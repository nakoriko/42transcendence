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

    #nuova versione di receive
    async def receive(self, text_data):
        data = json.loads(text_data)

        if not self.authenticated:
            if data.get('type') == 'auth':
                await self.handle_auth(data)
            else:
                await self.close()
            return

        # Dispatcher per messaggi autenticati
        message_type = data.get('type')
        handlers = {
            'game_invite': self.handle_game_invite,
            'game_accept': self.handle_game_accept,
            'join_match': self.handle_join_match,
            'ping_match': self.handle_ping_match,
            # altri handler qui quando ne aggiungiamo
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(data)
        else:
            print(f"Unknown message type: {message_type}")

    # --- handler chiamati da Channels quando arriva un messaggio dal Group ---
    async def handle_auth(self, data):
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

    async def handle_game_invite(self, data):
        match_id = data.get('match_id')
        to_user_id = data.get('to_user_id')

        await self.channel_layer.group_send(f"user_{to_user_id}", {
            "type": "game_invite_event",
            "match_id": match_id,
            "from_user_id": self.user.id,
            "from_user_nickname": self.user.nickname,
        })
    
    async def game_invite_event(self, event):
        await self.send(json.dumps({
            "type": "game_invite",
            "match_id": event["match_id"],
            "from_user": {
                "id": event["from_user_id"],
                "nickname": event["from_user_nickname"],
            }
        }))

    async def handle_game_accept(self, data):
        match_id = data.get('match_id')
            
        try:
            from game.models import Match
            match = await Match.objects.aget(id=match_id)
            
            match.status = 'active'
            await match.asave()

            for player_id, role in [(match.player1_id, 'player1'), (match.player2_id, 'player2')]:
                await self.channel_layer.group_send(f"user_{player_id}", {
                    "type": "game_start_event",
                    "match_id": match_id,
                    "your_role": role,
                })
        except Exception as e:
            print(f"GAME_ACCEPT ERROR: {e}")
            await self.send(json.dumps({
                "type": "error",
                "message": "Match not found or error processing accept"
            }))
            return

    async def game_start_event(self, event):
        await self.send(json.dumps({
            "type": "game_start",
            "match_id": event["match_id"],
            "your_role": event["your_role"],
        }))

    async def handle_join_match(self, data):
        match_id = data.get("match_id")

        await self.channel_layer.group_add(
            f"match_{match_id}",
            self.channel_name
        )

        await self.send(json.dumps({
            "type": "joined_match",
            "match_id": match_id
        }))

    async def handle_ping_match(self, data):
        match_id = data.get("match_id")

        print(f"PING inviato al gruppo match_{match_id}")

        await self.channel_layer.group_send(
            f"match_{match_id}",
            {
                "type": "ping_event",
                "from_user": self.user.nickname,
            }
        )

    async def ping_event(self, event):
        print(f"PING ricevuto da {self.user.nickname}")
        
        await self.send(json.dumps({
            "type": "ping",
            "from": event["from_user"],
        }))