import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.authenticated = False
        await self.accept()
        self.auth_timeout = asyncio.create_task(self.close_if_not_authenticated())

    async def close_if_not_authenticated(self):
        await asyncio.sleep(5)
        if not self.authenticated:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'auth_timeout'):
            self.auth_timeout.cancel()

        if self.authenticated:
            self.user.is_online = False
            await self.user.asave()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if not self.authenticated:
            if data.get('type') == 'auth':
                token_string = data.get('token')
                try:
                    token = AccessToken(token_string)
                    self.user = await User.objects.aget(id=token['user_id'])
                    self.authenticated = True
                    self.auth_timeout.cancel()

                    self.user.is_online = True
                    await self.user.asave()

                    await self.send(json.dumps({'type': 'auth_success'}))
                except Exception:
                    await self.close()
            else:
                await self.close()
            return

        await self.send(text_data=text_data)

