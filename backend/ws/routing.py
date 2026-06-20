from django.urls import path
from . import consumers

#nome convenzionale per channels quando imposta in asgi.py
websocket_urlpatterns = [
    path('ws/test/', consumers.PresenceConsumer.as_asgi()),
]