"""
Integration tests — WebSocket /ws/cost-stream consumer.
Run with: python manage.py test tests.test_websocket
Requires Django Channels and an in-memory channel layer (configured in test settings).
"""
from django.test import TestCase, override_settings
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from rest_framework_simplejwt.tokens import AccessToken

from eco_chain.asgi import application
from apps.authentication.models import User
from apps.build_assistant.models import Layout
from apps.cost_estimator.models import MaterialPrice, LabourRate

import json
import asyncio


@override_settings(
    CHANNEL_LAYERS={'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}
)
class CostStreamWebSocketTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='ws@eco.io', name='WS User', password='Pass1234!', status='ACTIVE',
        )
        self.layout = Layout.objects.create(
            user=self.user, bedrooms=2, climate_zone='equatorial', style='modern',
            orientation='south', total_area_sqm=70.0, eco_score=65,
            layout_json={'rooms': [
                {'type': 'bedroom', 'area_sqm': 12},
                {'type': 'living_room', 'area_sqm': 20},
                {'type': 'kitchen', 'area_sqm': 8},
            ]},
        )
        # Seed minimal pricing so cost calculator can return a result
        for cat in ('wall', 'foundation', 'roof', 'floor', 'finishing'):
            MaterialPrice.objects.create(
                name=f'WS Material {cat}', category=cat, unit='sqm',
                price_per_unit=1500, currency='KES', country='KE',
            )
        for skill in ('mason', 'carpenter', 'plumber'):
            LabourRate.objects.create(
                skill_type=skill, country='KE', rate_per_day=1800, currency='KES',
            )

    def _get_token(self):
        return str(AccessToken.for_user(self.user))

    async def _connect(self, token=None, layout_id=None):
        t = token or self._get_token()
        lid = layout_id or str(self.layout.id)
        communicator = WebsocketCommunicator(
            application,
            f'/ws/cost-stream?token={t}&layout_id={lid}',
        )
        connected, _ = await communicator.connect()
        return communicator, connected

    def test_connects_with_valid_token(self):
        async def run():
            comm, connected = await self._connect()
            self.assertTrue(connected)
            await comm.disconnect()
        asyncio.get_event_loop().run_until_complete(run())

    def test_rejects_without_token(self):
        async def run():
            communicator = WebsocketCommunicator(application, '/ws/cost-stream')
            connected, code = await communicator.connect()
            self.assertFalse(connected)
        asyncio.get_event_loop().run_until_complete(run())

    def test_rejects_invalid_token(self):
        async def run():
            comm, connected = await self._connect(token='bad-token')
            self.assertFalse(connected)
        asyncio.get_event_loop().run_until_complete(run())

    def test_cost_update_received_after_update_event(self):
        async def run():
            comm, connected = await self._connect()
            self.assertTrue(connected)

            await comm.send_json_to({
                'type': 'update',
                'country': 'KE',
                'city': '',
                'labour_zone': 'KE',
            })

            # Give the debounce + calculation time to complete
            await asyncio.sleep(0.6)

            response = await comm.receive_json_from(timeout=3)
            self.assertEqual(response['type'], 'cost_update')
            self.assertIn('data', response)
            self.assertIn('total_cost', response['data'])
            await comm.disconnect()

        asyncio.get_event_loop().run_until_complete(run())

    def test_debounce_fires_once_for_rapid_updates(self):
        async def run():
            comm, _ = await self._connect()

            # Fire 5 rapid updates — only 1 calculation should result
            for _ in range(5):
                await comm.send_json_to({'type': 'update', 'country': 'KE'})
                await asyncio.sleep(0.05)

            await asyncio.sleep(0.6)

            response = await comm.receive_json_from(timeout=3)
            self.assertEqual(response['type'], 'cost_update')

            # No second message should be queued
            self.assertTrue(await comm.receive_nothing(timeout=0.3))
            await comm.disconnect()

        asyncio.get_event_loop().run_until_complete(run())

    def test_error_returned_for_invalid_layout(self):
        async def run():
            comm, _ = await self._connect(layout_id='00000000-0000-0000-0000-000000000000')
            await comm.send_json_to({'type': 'update', 'country': 'KE'})
            await asyncio.sleep(0.6)
            response = await comm.receive_json_from(timeout=3)
            self.assertEqual(response['type'], 'error')
            await comm.disconnect()

        asyncio.get_event_loop().run_until_complete(run())
