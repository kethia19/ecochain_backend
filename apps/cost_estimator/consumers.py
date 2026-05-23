"""
WebSocket consumer — /ws/cost-stream

Connection URL: ws://<host>/ws/cost-stream?token=<JWT>&layout_id=<UUID>

Protocol:
  Client → Server:
    {"type": "update", "country": "NG", "city": "Lagos", "labour_zone": "NG"}

  Server → Client:
    {"type": "cost_update", "data": { ...CostEstimate fields... }}
    {"type": "error", "message": "..."}

The 400 ms debounce absorbs rapid material-swap events from the canvas so
the DB is not hammered on every keystroke.
"""
import asyncio
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

from .services.cost_calculator import calculate_cost

User = get_user_model()
DEBOUNCE_SECONDS = 0.4


class CostStreamConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        token = self._query_param('token')
        if not token:
            await self.close(code=4001)
            return

        self.user = await self._authenticate(token)
        if not self.user:
            await self.close(code=4001)
            return

        self.layout_id = self._query_param('layout_id', '')
        self._debounce_task: asyncio.Task | None = None
        await self.accept()

    async def disconnect(self, code):
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or '{}')
        except json.JSONDecodeError:
            await self._send_error('Invalid JSON payload.')
            return

        if data.get('type') != 'update':
            return

        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()

        self._debounce_task = asyncio.create_task(
            self._debounced_calculate(data)
        )

    async def _debounced_calculate(self, data: dict):
        await asyncio.sleep(DEBOUNCE_SECONDS)

        layout_id = data.get('layout_id') or self.layout_id
        country = data.get('country', 'NG')
        city = data.get('city', '')
        labour_zone = data.get('labour_zone') or country

        if not layout_id:
            await self._send_error('layout_id is required.')
            return

        try:
            result = await database_sync_to_async(calculate_cost)(
                layout_id, country, city, labour_zone,
            )
            await self.send(json.dumps({'type': 'cost_update', 'data': result}))
        except ValueError as e:
            await self._send_error(str(e))
        except Exception:
            await self._send_error('Cost calculation failed. Please retry.')

    async def _send_error(self, message: str):
        await self.send(json.dumps({'type': 'error', 'message': message}))

    def _query_param(self, key: str, default: str = '') -> str:
        qs = self.scope.get('query_string', b'').decode()
        for part in qs.split('&'):
            if '=' in part:
                k, _, v = part.partition('=')
                if k == key:
                    return v
        return default

    @database_sync_to_async
    def _authenticate(self, token: str):
        try:
            access_token = AccessToken(token)
            return User.objects.get(id=access_token['user_id'])
        except Exception:
            return None
