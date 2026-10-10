from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

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


    