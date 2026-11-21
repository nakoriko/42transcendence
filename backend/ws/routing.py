from django.urls import path
from . import consumers

# imported by core/asgi.py
websocket_urlpatterns = [
    path('ws/game/', consumers.PresenceConsumer.as_asgi()),
]