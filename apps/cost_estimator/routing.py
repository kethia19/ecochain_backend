from django.urls import re_path
from .consumers import CostStreamConsumer

websocket_urlpatterns = [
    re_path(r'^ws/cost-stream$', CostStreamConsumer.as_asgi()),
]
