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
            await self.channel_layer.group_discard(f"user_{self.user.id}", self.channel_name)
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

                    # iscrizione a gruppo personale
                    await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)

                    await self.send(json.dumps({'type': 'auth_success'}))
                # except da mettere in versione finale
                # except Exception:
                #     await self.close()

                #except per debug
                except Exception as e:
                    print("AUTH ERROR:", e)
                    await self.close()
            else:
                await self.close()
            return

        elif data.get('type') == 'game_invite':
            match_id = data.get('match_id')
            to_user_id = data.get('to_user_id')

            await self.channel_layer.group_send(f"user_{to_user_id}", {
                "type": "game_invite_event",
                "match_id": match_id,
                "from_user_id": self.user.id,
                "from_user_nickname": self.user.nickname,
            })

    # --- handler chiamati da Channels quando arriva un messaggio dal Group ---

    async def game_invite_event(self, event):
        await self.send(json.dumps({
            "type": "game_invite",
            "match_id": event["match_id"],
            "from_user": {
                "id": event["from_user_id"],
                "nickname": event["from_user_nickname"],
            }
        }))