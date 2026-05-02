"""ASGI config for eco_chain project."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_chain.settings')

application = get_asgi_application()
