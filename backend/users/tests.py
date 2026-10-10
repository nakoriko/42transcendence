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


    