from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from django.test.utils import CaptureQueriesContext
from django.db import connection
from rest_framework.test import APITestCase
from .serializers import MatchFinishSerializer
from .models import Match, MatchEvent
from unittest.mock import patch

User = get_user_model()

TEST_CHANNEL_LAYERS = {'default' : {'BACKEND': 'channels.layers.InMemoryChannelLayer'}} #change redis to channelk layer in memory

@override_settings(CHANNEL_LAYERS = TEST_CHANNEL_LAYERS)
class FinishMatchTests(APITestCase):
    def setUp(self):
        self.p1 = User.objects.create_user(email='p1@test.com', password='pass12345', nickname='p1')
        self.p2 = User.objects.create_user(email='p2@test.com', password='pass12345', nickname='p2')
        self.outsider = User.objects.create_user(email='out@test.com', password='pass12345', nickname='out')
        self.match = Match.objects.create(
            player1=self.p1, player2=self.p2,
            status=Match.Status.ACTIVE, mode=Match.Mode.LOCAL,
        )
        self.url = f'/api/game/matches/{self.match.id}/finish/'
        self.client.force_authenticate(self.p1)
    
    def finish(self, winner_id, s1=5, s2=3):
            return self.client.patch(
                self.url,
                {'winner': winner_id, 'score_player1': s1, 'score_player2': s2},
                format='json',
            )

    def test_finish_updates_match_and_stats(self):
        res = self.finish(self.p1.id)
        self.assertEqual(res.status_code, 200)

        self.match.refresh_from_db()
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()

        self.assertEqual(self.match.status, Match.Status.FINISHED)
        self.assertIsNotNone(self.match.ended_at)
        self.assertEqual((self.p1.wins, self.p1.losses), (1, 0))
        self.assertEqual((self.p2.wins, self.p2.losses), (0, 1))


    def test_cannot_finish_twice(self):
        self.finish(self.p1.id)
        res = self.finish(self.p1.id)
        self.assertEqual(res.status_code, 400)

        self.p1.refresh_from_db()
        self.assertEqual(self.p1.wins, 1) #check if after second attempt to finish is still right result

    def test_winner_must_be_participant(self):
        res = self.finish(self.outsider.id)
        self.assertEqual(res.status_code, 400)

        self.outsider.refresh_from_db()
        self.assertEqual(self.outsider.wins, 0)

    def test_missing_winner_returns_400(self):
        res = self.client.patch(self.url, {'score_player1': 2, 'score_player2': 2}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_outsider_cannot_finish(self):
        self.client.force_authenticate(self.outsider)
        res = self.finish(self.p1.id)
        self.assertEqual(res.status_code, 403)

    def test_finish_does_not_overwrite_concurrent_user_changes(self):
        original_save = MatchFinishSerializer.save
        def save_then_change_users(serializer, **kwargs):
            result = original_save(serializer, **kwargs)
            User.objects.filter(pk=self.p1.pk).update(is_online=True, wins=10)
            User.objects.filter(pk=self.p2.pk).update(losses=10)
            return result
        with patch.object(MatchFinishSerializer, 'save', save_then_change_users):
            res = self.finish(self.p1.id)
            self.assertEqual(res.status_code, 200)
            self.p1.refresh_from_db()
            self.p2.refresh_from_db()
            self.assertTrue(self.p1.is_online)
            self.assertEqual(self.p1.wins, 11)
            self.assertEqual(self.p2.losses, 11)





class BulkMatchEventTests(APITestCase):
    url = '/api/game/matches/events/bulk/'

    def setUp(self):
        self.p1 = User.objects.create_user(email='p1@test.com', password='pass12345', nickname='p1')
        self.p2 = User.objects.create_user(email='p2@test.com', password='pass12345', nickname='p2')
        self.outsider = User.objects.create_user(email='out@test.com', password='pass12345', nickname='out')
        self.match = Match.objects.create(
            player1=self.p1, player2=self.p2,
            status=Match.Status.ACTIVE, mode=Match.Mode.LOCAL,
        )
        self.client.force_authenticate(self.p1)

    def event(self, match_id, player_id, event_type='hit'):
        return {'match': match_id, 'event_type': event_type, 'player': player_id,
                'pos_x': 0.5, 'pos_y': 0.5, 'reaction_time_ms': None}
    
    def post(self, events):
        return self.client.post(self.url, events, format='json')

    def test_participant_can_log_events(self):
        res = self.post([self.event(self.match.id, self.p1.id), 
            self.event(self.match.id, self.p2.id, 'goal')])
        self.assertEqual(res.status_code, 201)
        self.assertEqual(MatchEvent.objects.filter(match=self.match).count(), 2)

    def test_outsider_cannot_log_events(self):
        self.client.force_authenticate(self.outsider)
        res = self.post([self.event(self.match.id, self.p1.id)])
        self.assertEqual(res.status_code, 403)
        self.assertEqual(MatchEvent.objects.count(), 0)

    def test_cannot_log_events_to_finished_match(self):
        self.match.status = Match.Status.FINISHED
        self.match.save(update_fields=['status'])
        res = self.post([self.event(self.match.id, self.p1.id)])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(MatchEvent.objects.count(), 0)

    def test_batch_with_one_foreign_match(self):
        other = Match.objects.create(player1=self.p2, player2=self.outsider,
            status=Match.Status.ACTIVE, mode=Match.Mode.LOCAL)
        res = self.post([self.event(self.match.id, self.p1.id),
                        self.event(other.id, self.p2.id)])
        self.assertEqual(res.status_code, 403)
        self.assertEqual(MatchEvent.objects.count(), 0)

    def test_event_player_must_be_participant(self):
        res = self.post([self.event(self.match.id, self.outsider.id)])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(MatchEvent.objects.count(), 0)

    def test_unknown_match_returns_400(self):
        res = self.post([self.event(999999, self.p1.id)])
        self.assertEqual(res.status_code, 400)

    def test_bulk_response_contains_created_events(self):
        res = self.post([self.event(self.match.id, self.p1.id)])
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data[0]['match'], self.match.id)
        self.assertIn('id', res.data[0])

    def test_query_count_does_not_grow_with_events(self):
        def count(n):
            with CaptureQueriesContext(connection) as ctx:
                self.post([self.event(self.match.id, self.p1.id) for _ in range(n)])
            return (len(ctx.captured_queries))
        self.assertEqual(count(2), count(20))


class StartMatchTests(APITestCase):
    url='/api/game/matches/start/'

    def setUp(self):
        self.p1 = User.objects.create_user(email='p1@test.com', password='pass12345', nickname='p1')
        self.p2 = User.objects.create_user(email='p2@test.com', password='pass12345', nickname='p2')
        self.outsider = User.objects.create_user(email='out@test.com', password='pass12345', nickname='out')
        self.client.force_authenticate(self.p1)

    def start(self, payload):
        return self.client.post(self.url, payload, format='json')

    def test_start_match_as_frontend_does(self):
        res = self.start({'player1': self.p1.id, 'player2': self.p2.id})
        self.assertEqual(res.status_code, 201)

        match = Match.objects.get(id=res.data['id'])
        self.assertEqual(match.player1, self.p1)
        self.assertEqual(match.player2, self.p2)
        self.assertEqual(match.status, Match.Status.ACTIVE)
        self.assertEqual(match.mode, Match.Mode.LOCAL)

    def test_player1_from_body_is_ignored(self):
        res = self.start({'player1': self.outsider.id, 'player2': self.p2.id})
        self.assertEqual(res.status_code, 201)

        match = Match.objects.get(id=res.data['id'])
        self.assertEqual(match.player1, self.p1)

    def test_player1_is_set_even_when_omitted(self):
        res = self.start({'player2': self.p2.id})
        self.assertEqual(res.status_code, 201)

        match = Match.objects.get(id=res.data['id'])
        self.assertEqual(match.player1, self.p1)

    def test_player2_is_required(self):
        res =self.start({})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Match.objects.count(), 0)

    def test_cannot_play_against_yourself(self):
        res = self.start({'player2': self.p1.id})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Match.objects.count(), 0)

class MatchHistoryTests(APITestCase):
    url = '/api/game/matches/'

    def setUp(self):
        self.p1 = User.objects.create_user(email='p1@test.com', password='pass12345', nickname='p1')
        self.p2 = User.objects.create_user(email='p2@test.com', password='pass12345', nickname='p2')

        now = timezone.now()
        Match.objects.bulk_create([
            Match(player1=self.p1, player2=self.p2, winner=self.p1,
                    status=Match.Status.FINISHED, ended_at=now)
            for _ in range(12)
        ])
        self.client.force_authenticate(self.p1)

    def test_default_limit_is_10(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 10)

    def test_limit_param_is_respected(self):
        res = self.client.get(self.url, {'limit': 5})
        self.assertEqual(len(res.data), 5)


    def test_non_numeric_limit_returns_400(self):
        res=self.client.get(self.url, {'limit': 'abc'})
        self.assertEqual(res.status_code, 400)

    def test_negative_limit_is_clamped(self):
        res=self.client.get(self.url, {'limit': -1})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_match_without_winner_is_draw(self):
        Match.objects.create(player1=self.p1, player2=self.p2, status=Match.Status.FINISHED,
            mode=Match.Mode.LOCAL, ended_at=timezone.now(), winner=None)
        res = self.client.get(f'{self.url}?limit=1')
        self.assertEqual(res.data[0]['result'], 'draw')


    
    








async def broken_group_send(*args, **kwargs):
    raise ConnectionError('channel layer is down')


@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
@patch('channels.layers.InMemoryChannelLayer.group_send', broken_group_send)
class FinishMatchNotificationFailureTests(APITestCase):
    def test_match_is_finished_when_notification_fails(self):
        p1 = User.objects.create_user(email='p1@test.com', password='pass12345', nickname='p1')
        p2 = User.objects.create_user(email='p2@test.com', password='pass12345', nickname='p2')
        match = Match.objects.create(player1=p1, player2=p2, status=Match.Status.ACTIVE, mode=Match.Mode.LOCAL)
        self.client.force_authenticate(p1)
        with self.assertLogs('ws', level='ERROR'):
            res = self.client.patch(
                f'/api/game/matches/{match.id}/finish/',
                {'winner': p1.id, 'score_player1': 5, 'score_player2': 3},
                format='json',
            )
        self.assertEqual(res.status_code, 200)
        match.refresh_from_db()
        p1.refresh_from_db()
        self.assertEqual(match.status, Match.Status.FINISHED)
        self.assertEqual(p1.wins, 1)
