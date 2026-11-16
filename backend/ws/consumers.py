import asyncio
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from users.models import FriendRelation
import redis.asyncio as redis
from django.conf import settings


User = get_user_model()
logger = logging.getLogger(__name__)

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
                await self.broadcast_presence_update(False) # ← era notify_friends_status(False)
                await self.broadcast_online_count()

    #nuova versione di receive
    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if not isinstance(data, dict):
            return

        if not self.authenticated:
            if data.get('type') == 'auth':
                await self.handle_auth(data)
            else:
                await self.close()
            return

        # Dispatcher per messaggi autenticati
        message_type = data.get('type')
        handlers = {
            'chat_message': self.handle_chat_message,
            # altri handler qui quando ne aggiungiamo
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(data)
        else:
            logger.warning("Unknown WS message type: %s", message_type)

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
                await self.user.asave(update_fields=['is_online']) #NAT: added to fix error: ws rewrited all fields. Cioe: se utente cambia il suo profilo, ws li rescrive tutti dentro DB (bug), acnhe se non sono piu attuali
                await self.broadcast_presence_update(True)  # ← era notify_friends_status(True)
                await self.broadcast_online_count()

           

            await self.send(json.dumps({'type': 'auth_success'}))
        except Exception as e:
            logger.warning("WS auth failed: %s", e)
            await self.close()

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