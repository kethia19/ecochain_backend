"""ASGI config — HTTP via Django, WebSocket via Channels."""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_chain.settings')

django_asgi_app = get_asgi_application()

from apps.cost_estimator.routing import websocket_urlpatterns  # noqa: E402 — import after setup

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        URLRouter(websocket_urlpatterns)
    ),
})
