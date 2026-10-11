import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from users.models import FriendRelation
import redis.asyncio as redis
from django.conf import settings


User = get_user_model()

redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379)

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
            await self.channel_layer.group_discard("global_presence", self.channel_name)
            await self.channel_layer.group_discard("dashboard_updates", self.channel_name)
            
            conn_count = await redis_client.decr(f"ws_conn_count:{self.user.id}")

            if conn_count <= 0:
                self.user.is_online = False
                await self.user.asave(update_fields=['is_online']) #NAT: added to fix error with profile update after F5 
                # await self.user.asave()
                await self.broadcast_presence_update(False) # ← era notify_friends_status(False)
                await self.broadcast_online_count()

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
            "player_input": self.handle_player_input,
            'chat_message': self.handle_chat_message,
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

             # iscrizione a gruppo personale
            await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)
            await self.channel_layer.group_add("global_presence", self.channel_name)
            await self.channel_layer.group_add("dashboard_updates", self.channel_name)

            conn_count = await redis_client.incr(f"ws_conn_count:{self.user.id}")

            if conn_count == 1:
                self.user.is_online = True
                await self.user.asave(update_fields=['is_online']) #NAT: added to fix error: ws rewrited all fields. Cioe: se utente cambia il suo profilo, ws li rescrive tutti dentro DB (bug), acnhe se non sono piu attuali         # await self.user.asave()
                await self.broadcast_presence_update(True)  # ← era notify_friends_status(True)
                await self.broadcast_online_count()

           

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

        self.match_id = match_id

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

    async def handle_player_input(self, data):
        direction = data["direction"]

        await self.channel_layer.group_send(
            f"match_{self.match_id}",
            {
                "type": "player_input_event",
                "player": self.user.nickname,
                "direction": direction,
            }
        )

    async def handle_chat_message(self, data):
        to_user_id = data.get('to_user_id')
        content = (data.get('content') or '').strip()

        if not to_user_id or not content:
            await self.send(json.dumps({
                "type": "chat_error",
                "reason": "invalid_message",
                "to_user_id": to_user_id
            }))
            return

        try:
            to_user = await User.objects.aget(id=to_user_id)
        except User.DoesNotExist:
            await self.send(json.dumps({
                "type": "chat_error",
                "reason": "user_not_found",
                "to_user_id": to_user_id
            }))
            return

        # nuovo controllo: sono amici?
        are_friends = await FriendRelation.objects.filter(
            Q(from_user=self.user, to_user=to_user) |
            Q(from_user=to_user, to_user=self.user),
            status='accepted'
        ).aexists()

        if not are_friends:
            await self.send(json.dumps({
                "type": "chat_error",
                "reason": "not_friends",
                "to_user_id": to_user_id
            }))
            return

        if not to_user.is_online:
            await self.send(json.dumps({
                "type": "chat_error",
                "reason": "user_offline",
                "to_user_id": to_user_id
            }))
            return

        await self.channel_layer.group_send(f"user_{to_user_id}", {
            "type": "chat_message_event",
            "from_user_id": self.user.id,
            "from_user_nickname": self.user.nickname,
            "content": content,
        })

    async def chat_message_event(self, event):
        await self.send(json.dumps({
            "type": "chat_message",
            "from_user": {
                "id": event["from_user_id"],
                "nickname": event["from_user_nickname"],
            },
            "content": event["content"],
        }))

    #SAB: sostituito da broadcast_presence_update per aggiornare stato di tutti, non solo amici
    # async def notify_friends_status(self, is_online):
    #     friends = FriendRelation.objects.filter(
    #         Q(from_user=self.user) | Q(to_user=self.user),
    #         status='accepted'
    #     )
    #     async for relation in friends:
    #         friend_id = relation.to_user_id if relation.from_user_id == self.user.id else relation.from_user_id
    #         await self.channel_layer.group_send(f"user_{friend_id}", {
    #             "type": "friend_status_event",
    #             "user_id": self.user.id,
    #             "is_online": is_online,
    #         })

    async def broadcast_presence_update(self, is_online):
        await self.channel_layer.group_send("global_presence", {
            "type": "friend_status_event",
            "user_id": self.user.id,
            "is_online": is_online,
        })

    async def friend_status_event(self, event):
        await self.send(json.dumps({
            "type": "presence_update",
            "user_id": event["user_id"],
            "is_online": event["is_online"],
        }))

    async def broadcast_online_count(self):
        count = await User.objects.filter(is_online=True).acount()
        await self.channel_layer.group_send("global_presence", {
            "type": "online_count_event",
            "count": count,
        })

    async def online_count_event(self, event):
        await self.send(json.dumps({
            "type": "online_count",
            "count": event["count"],
        }))

    async def friend_request_event(self, event):
        await self.send(json.dumps({
            "type": "friend_request_received",
            "from_user": {
                "id": event["from_user_id"],
                "nickname": event["from_user_nickname"],
            },
            "relation_id": event["relation_id"],
        }))

    async def friend_request_accepted_event(self, event):
        await self.send(json.dumps({
            "type": "friend_request_accepted",
            "user_id": event["user_id"],
            "nickname": event["nickname"],
        }))

    async def match_finished_event(self, event):
        await self.send(json.dumps({
            "type": "match_finished",
            "match_id": event["match_id"],
            "player1_id": event["player1_id"],
            "player2_id": event["player2_id"],
            "winner_id": event["winner_id"],
            "score_player1": event["score_player1"],
            "score_player2": event["score_player2"],
        }))