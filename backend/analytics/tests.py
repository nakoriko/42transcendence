from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from game.models import Match

User = get_user_model()

class AnalyticsEmailLeakTests(APITestCase):
    def setUp(self):
        self.me = User.objects.create_user(email='me@test.com', password='pass12345', nickname='me')
        self.other = User.objects.create_user(email='other@test.com', password='pass12345', nickname='')
        Match.objects.create(
            player1=self.me, player2=self.other, mode='local',
            status=Match.Status.FINISHED, winner=self.me,
            score_player1=3, score_player2=2, ended_at=timezone.now()
        )
        self.client.force_authenticate(self.me)

    def test_universe_does_not_leak_email(self):
        res = self.client.get('/api/analytics/universe/')
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('other@test.com', res.content.decode())

    def test_player_graph_does_not_leak_email(self):
        res =self.client.get('/api/analytics/player-graph/')
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('other@test.com', res.content.decode())

