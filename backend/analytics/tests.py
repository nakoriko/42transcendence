from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test.utils import CaptureQueriesContext
from django.db import connection
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

class PlayerGraphTests(APITestCase):
    def setUp(self):
        self.users = {
            name: User.objects.create_user(email=f'{name}@test.com',
            password='pass12345', nickname=name)
            for name in ['me', 'A', 'B', 'C', 'F', 'G', 'H' , 'I', 'J', 'K']
        }
        self.play('me', 'A')
        self.play('me', 'B')
        self.play('A', 'C')
        for name, times in [('F', 6), ('G', 5), ('H', 4), ('I', 3), ('J', 2), ('K', 1)]:
            for _ in range(times):
                self.play('B', name)
        self.client.force_authenticate(self.users['me'])

    def play(self, a, b):
        Match.objects.create(
            player1=self.users[a], player2=self.users[b],
            mode='local',
            status=Match.Status.FINISHED, winner=self.users[a], ended_at=timezone.now()
        )

    def get_graph(self):
        res= self.client.get('/api/analytics/player-graph/')
        self.assertEqual(res.status_code, 200)
        return res.data

    def test_graph_contains_two_circles_with_top5_cap(self):
        names = {n['nickname'] for n in self.get_graph()['nodes']}
        self.assertEqual(names, {'me', 'A', 'B', 'C', 'F', 'G', 'H', 'I', 'J'})

    def test_query_count_does_not_grow_with_opponents(self):
        def count():
            with CaptureQueriesContext(connection) as ctx:
                self.get_graph()
            return len(ctx.captured_queries)
        before = count()
        for i in range(5):
            extra = User.objects.create_user(email=f'x{i}@test.com',
            password='pass12345', nickname=f'x{i}')
            Match.objects.create(
                player1=self.users['me'], player2=extra, mode='local',
                status=Match.Status.FINISHED, winner=extra, ended_at=timezone.now()
            )
        self.assertEqual(before, count())