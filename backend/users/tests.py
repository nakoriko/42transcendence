from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase
from io import StringIO
from unittest.mock import patch
from django.apps import apps
from django.core.management import call_command
from django.core.exceptions import ValidationError


from .models import FriendRelation
User = get_user_model()

TEST_CHANNEL_LAYERS = {'default' : {'BACKEND': 'channels.layers.InMemoryChannelLayer'}} 
#change redis to channelk layer in memory

@override_settings(CHANNEL_LAYERS = TEST_CHANNEL_LAYERS)
class FriendDetailTests(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(email='s@test.com', password='pass12345', nickname='sender')
        self.recipient = User.objects.create_user(email='r@test.com', password='pass12345', nickname='recipient')
        self.outsider = User.objects.create_user(email='o@test.com', password='pass12345', nickname='outsider')
        self.relation = FriendRelation.objects.create(
            from_user=self.sender, to_user=self.recipient,
            status='pending', 
        )
        self.url = f'/api/users/friends/{self.relation.id}/'

    def act(self, user, action):
        self.client.force_authenticate(user)
        return self.client.patch(self.url, {'action': action}, format='json')

    def test_recipient_can_accept(self):
        res=self.act(self.recipient, 'accept')
        self.assertEqual(res.status_code, 200)
        self.relation.refresh_from_db()
        self.assertEqual(self.relation.status, 'accepted')

    def test_recipient_can_reject(self):
        res=self.act(self.recipient, 'reject')
        self.assertEqual(res.status_code, 200)
        self.relation.refresh_from_db()
        self.assertEqual(self.relation.status, 'rejected')

    def test_sender_cannot_accept_own_request(self):
        res = self.act(self.sender, 'accept')
        self.assertEqual(res.status_code, 403)
        self.relation.refresh_from_db()
        self.assertEqual(self.relation.status, 'pending')

    def test_sender_cannot_reject_own_request(self):
        res = self.act(self.sender, 'reject')
        self.assertEqual(res.status_code, 403)
        self.relation.refresh_from_db()
        self.assertEqual(self.relation.status, 'pending')

    def test_outsider_gets_404(self):
        res=self.act(self.outsider, 'accept')
        self.assertEqual(res.status_code, 404)

    def test_sender_can_cancel_request(self):
        self.client.force_authenticate(self.sender)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, 204)
        self.assertFalse(FriendRelation.objects.filter(id=self.relation.id).exists())

    def test_cannot_accept_already_accepted(self):
        self.relation.status = 'accepted'
        self.relation.save()

        res = self.act(self.recipient, 'accept')
        self.assertEqual(res.status_code, 400)

    def test_cannot_accept_rejected(self):
        self.relation.status = 'rejected'
        self.relation.save()
        res = self.act(self.recipient, 'accept')
        self.assertEqual(res.status_code, 400)
        self.relation.refresh_from_db()
        self.assertEqual(self.relation.status, 'rejected')


    

    #Multiply request sending
@override_settings (CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
class FriendRequestTests(APITestCase):
    url = '/api/users/friends/request/'
    
    def setUp(self):
        self.sender = User.objects.create_user(email='s@test.com', password='pass12345', nickname='sender')
        self.recipient = User.objects.create_user(email='r@test.com', password='pass12345', nickname='recipient')

    def send(self, from_user, to_user):
        self.client.force_authenticate(from_user)
        return self.client.post(self.url, {'to_user_id': to_user.id}, format='json')

    def relations(self):
        return FriendRelation.objects.filter(
            from_user__in=[self.sender, self.recipient],
            to_user__in=[self.sender, self.recipient],
        )

    def test_can_send_request(self):
        res=self.send(self.sender, self.recipient)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.relations().get().status, 'pending')

    def test_cannot_duplicate_request(self):
        self.send(self.sender, self.recipient)
        res=self.send(self.sender, self.recipient)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(self.relations().count(), 1)

    def test_cannot_request_existing_friend(self):
        FriendRelation.objects.create(from_user=self.sender, to_user=self.recipient, status='accepted')
        res=self.send(self.recipient, self.sender)
        self.assertEqual(res.status_code, 400)


    def test_sender_can_resend_after_rejection(self):
        FriendRelation.objects.create(from_user=self.sender, to_user=self.recipient, status='rejected')
        res=self.send(self.sender, self.recipient)
        self.assertEqual(res.status_code, 201)

        relation = self.relations().get()
        self.assertEqual(relation.status, 'pending')

    def test_recipient_can_send_after_rejecting(self):
        FriendRelation.objects.create(from_user=self.sender, to_user=self.recipient, status='rejected')
        res=self.send(from_user=self.recipient, to_user=self.sender)
        self.assertEqual(res.status_code, 201)

        relation = self.relations().get()
        self.assertEqual(relation.from_user, self.recipient)
        self.assertEqual(relation.status, 'pending')

    def test_full_flow_request_reject_request_again(self):
        self.send(self.sender, self.recipient)
        relation = self.relations().get()
        self.client.force_authenticate(self.recipient)
        self.client.patch(f'/api/users/friends/{relation.id}/', {'action': 'reject'}, format='json')

        res=self.send(self.sender, self.recipient)
        self.assertEqual(res.status_code, 201)

class PublicProfileTests(APITestCase):
    def setUp(self):
        self.me =User.objects.create_user(email='me@test.com', password='pass12345', nickname='me')
        self.other =User.objects.create_user(email='other@test.com', password='pass12345', nickname='other')
        self.url= f'/api/users/{self.other.id}/'
        self.client.force_authenticate(self.me)

    def test_public_profile_hides_email(self):
        res=self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('email', res.data)

    def test_public_profile_returns_public_fields(self):
        res=self.client.get(self.url)
        self.assertEqual(res.data['id'], self.other.id)
        self.assertEqual(res.data['nickname'], 'other')
        for filed in('wins', 'losses', 'avatar'):
                self.assertIn(filed, res.data)

    def test_own_profile_still_has_email(self):
        res=self.client.get('/api/users/profile/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['email'], 'me@test.com')

    def test_unknown_user_returns_404(self):
        res = self.client.get('/api/users/999999/')
        self.assertEqual(res.status_code, 404)

    def test_anonymous_cannot_view_profile(self):
        self.client.force_authenticate(None)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 401)


class PresenceResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='on@test.com', password='pass12345', nickname='online', is_online=True,
        )
    
    @patch('redis.Redis')
    def test_app_startup_does_not_reset_presence(self, mock_redis):
        apps.get_app_config('users').ready()

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_online)
        mock_redis.assert_not_called()

    @patch('redis.Redis')
    def test_reset_presence_command(self, mock_redis):
        r = mock_redis.return_value
        r.scan_iter.return_value = [b'ws_conn_count:1', b'ws_conn_count:2']

        call_command('reset_presence', stdout=StringIO())
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_online)
        r.scan_iter.assert_called_once_with('ws_conn_count:*')
        self.assertEqual(r.delete.call_count, 2)

    @override_settings(REDIS_HOST='redis-test')
    @patch('redis.Redis')
    def test_reset_presence_uses_configured_redis_host(self, mock_redis):
        call_command('reset_presence', stdout=StringIO())
        mock_redis.assert_called_once_with(host='redis-test', port=6379)

class RegisterTests(APITestCase):
    url = '/api/users/register/'

    def register(self, password):
        return self.client.post(self.url, {
            'email': 'new@test.com', 'password': password, 'nickname': 'newbie',
        }, format='json')

    def test_too_short_password_is_rejected(self):
        res = self.register('1')
        self.assertEqual(res.status_code, 400)
        self.assertIn('password', res.data)
        self.assertFalse(User.objects.filter(email='new@test.com').exists())

    def test_numeric_password_rejected(self):
        res = self.register('12345678')
        self.assertEqual(res.status_code, 400)
        self.assertIn('password', res.data)

    def test_strong_password_register(self):
        res = self.register('Pong-Ultra-2026')
        self.assertEqual(res.status_code, 201)
        user = User.objects.get(email='new@test.com')
        self.assertTrue(user.check_password('Pong-Ultra-2026'))
        self.assertNotIn('password', res.data)

class NicknameLengthTests(APITestCase):
    def test_model_rejects_nickname_longer_than_15(self):
        user = User(email='long@example.com',
        username='long',
        nickname='a' * 16)
        user.set_password('Str0ng-pass-42')
        with self.assertRaises(ValidationError) as cm:
            user.full_clean()
        self.assertIn('nickname', cm.exception.message_dict)

    def test_model_accepts_nickname_of_15(self):
        user = User(email='ok@example.com', username='ok', nickname='a' * 15)
        user.set_password('Str0ng-pass-42')
        user.full_clean()

@override_settings(CHANNEL_LAYERS = TEST_CHANNEL_LAYERS)
class UserListTests(APITestCase):
    def setUp(self):
        self.me = User.objects.create_user(email='me@test.com', password='pass12345', nickname='me')
        self.other = User.objects.create_user(email='other@test.com', password='pass12345', nickname='other')
        self.other.wins = 3
        self.other.losses = 2
        self.other.save()
        self.client.force_authenticate(self.me)

    def test_list_returns_wins_and_losses(self):
        res = self.client.get('/api/users/list/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data[0]['wins'], 3)
        self.assertEqual(res.data[0]['losses'], 2)

    def test_list_excludes_current_user(self):
        res = self.client.get('/api/users/list/')
        self.assertEqual([u['id'] for u in res.data], [self.other.id])

    def test_list_returns_relative_avatar_url(self):
        self.other.avatar = 'avatars/pic.jpg'
        self.other.save()
        res = self.client.get('/api/users/list/')
        self.assertEqual(res.data[0]['avatar'], '/media/avatars/pic.jpg')

    def test_profile_returns_date_joined(self):
        res = self.client.get('/api/users/profile/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['date_joined'], self.me.date_joined)



    

    


class LogoutTests(APITestCase):
    def setUp(self):
        User.objects.create_user(email='u@test.com', password='pass12345', nickname='user')
        res = self.client.post('/api/users/login/', {'email': 'u@test.com', 'password': 'pass12345'}, format='json')
        self.refresh = res.data['refresh']

    def logout(self, data):
        return self.client.post('/api/users/logout/', data, format='json')

    def use_refresh(self):
        return self.client.post('/api/users/token/refresh/', {'refresh': self.refresh}, format='json')

    def test_refresh_works_before_logout(self):
        self.assertEqual(self.use_refresh().status_code, 200)

    def test_refresh_is_rejected_after_logout(self):
        res = self.logout({'refresh': self.refresh})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.use_refresh().status_code, 401)

    def test_logout_twice_is_ok(self):
        self.logout({'refresh': self.refresh})
        self.assertEqual(self.logout({'refresh': self.refresh}).status_code, 200)

    def test_logout_with_invalid_token_is_ok(self):
        self.assertEqual(self.logout({'refresh': 'garbage'}).status_code, 200)

    def test_logout_without_token_is_rejected(self):
        self.assertEqual(self.logout({}).status_code, 400)


async def broken_group_send(*args, **kwargs):
    raise ConnectionError('channel layer is down')


@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
@patch('channels.layers.InMemoryChannelLayer.group_send', broken_group_send)
class FriendNotificationFailureTests(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(email='s@test.com', password='pass12345', nickname='sender')
        self.recipient = User.objects.create_user(email='r@test.com', password='pass12345', nickname='recipient')

    def test_friend_request_is_saved_when_notification_fails(self):
        self.client.force_authenticate(self.sender)
        with self.assertLogs('ws', level='ERROR'):
            res = self.client.post('/api/users/friends/request/', {'to_user_id': self.recipient.id}, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertTrue(FriendRelation.objects.filter(from_user=self.sender, to_user=self.recipient).exists())

    def test_accept_is_saved_when_notification_fails(self):
        relation = FriendRelation.objects.create(from_user=self.sender, to_user=self.recipient, status='pending')
        self.client.force_authenticate(self.recipient)
        with self.assertLogs('ws', level='ERROR'):
            res = self.client.patch(f'/api/users/friends/{relation.id}/', {'action': 'accept'}, format='json')
        self.assertEqual(res.status_code, 200)
        relation.refresh_from_db()
        self.assertEqual(relation.status, 'accepted')
