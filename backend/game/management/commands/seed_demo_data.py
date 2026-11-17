"""
Demo data for the analytics dashboard.

    docker-compose exec backend python manage.py seed_demo_data

Peer_42 is recreated on every run: log out and log in again afterwards.

100 demo users (all with an @example.com email):
    - 8 main clusters (A-H): Peer_42 plays a few members of each. Clusters have
      different shapes and no bridges between them, so on his Player Network
      every cluster is a separate "petal" around him.
    - 8 satellite clusters (I-P): never play Peer_42, visible only in Pong Universe.
    - 3 lone players who only ever played Peer_42.
Peer_42: 12 weeks of matches with a smooth weekly volume and a win rate trend
shaped for Player Stats, 10 friends and 2 incoming friend requests.
"""
import math
import random
from collections import defaultdict
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from game.management.commands.clear_demo_data import DEMO_EMAIL_SUFFIX
from game.models import Match, MatchEvent
from users.models import FriendRelation

User = get_user_model()

# --- key user ------------------------------------------------------------

KEY_EMAIL = f'Peer42{DEMO_EMAIL_SUFFIX}'
KEY_NICKNAME = 'Peer_42'
KEY_PASSWORD = '123'

# --- main clusters (on Peer_42's Player Network) -------------------------

CLUSTERS = {
    'A': ['NeonServe', 'ViperSpin', 'QuantumPaddle', 'GhostRally', 'AceVortex', 'SolarSmash'],
    'B': ['CrimsonAce', 'ZenBounce', 'TurboTopspin', 'LunarDrift', 'ObsidianEdge', 'EchoStrike'],
    'C': ['PixelPunch', 'VelvetVolley', 'ThunderPad', 'SilentSpin', 'BlazeCourt', 'FrostyServe'],
    'D': ['IronRicochet', 'VoltDrive', 'ShadowSmash', 'AmberSpike', 'CobaltCurve', 'MysticVolley'],
    'E': ['RapidFuse', 'GoldenPaddle', 'NovaStrike', 'DriftKing', 'PulseServe', 'CrypticSpin'],
    'F': ['SteelSpin', 'VenomServe', 'ArcticSmash', 'RogueVolley', 'PhantomPaddle', 'StormEdge'],
    'G': ['CopperCurve', 'WildfireSpin', 'GlacierBounce', 'EmberStrike', 'TitanServe', 'WhisperSpin'],
    'H': ['RadiantVolley', 'OnyxDrive', 'SapphireSmash', 'VelocitySpin', 'MidnightVolley', 'CoralStrike'],
}

# --- satellite clusters (only in Pong Universe) --------------------------
# They never play Peer_42 or the main clusters, so they are not on his graph,
# but they add players and spikes to Pong Universe.

SATELLITE_CLUSTERS = {
    'I': ['ZephyrPaddle', 'InfernoServe', 'CyberSmash', 'MysticEdge', 'ThunderRally', 'VoidServe'],
    'J': ['CrystalSpin', 'RustPulse', 'HyperStrike', 'LotusVolley', 'ChaosPaddle', 'QuasarDrift'],
    'K': ['QuartzBurst', 'PrismFlux', 'TideGlide', 'WraithRush', 'SpectralFuse', 'LunarBlast'],
    'L': ['SolarThrust', 'IvoryVolley', 'FlameSpin', 'DuskServe', 'DawnEdge', 'JadePaddle'],
    'M': ['CarbonSmash', 'PlatinumRally', 'ArgonStrike', 'CosmicPulse', 'CometDrift', 'OrbitSpin'],
    'N': ['NebulaFlux', 'GalaxyBurst', 'StellarEdge', 'MarbleSmash', 'NightShade', 'GhostStrike'],
    'O': ['RavenServe', 'CipherRally', 'FrostFire', 'OceanDrift', 'HavocSpin', 'PhoenixDart'],
    'P': ['VanguardSlash', 'StarlightEdge', 'BlitzSmash', 'TwilightSpin', 'EclipseServe', 'AuroraPulse'],
}

# Players who only ever played Peer_42: single leaves on his graph.
LONE_PLAYERS = {'Q': ['RookieRay', 'LoneLobber', 'QuietQuasar']}

# All groups are generated the same way, only the edge pattern differs.
ALL_CLUSTERS = {**CLUSTERS, **SATELLITE_CLUSTERS, **LONE_PLAYERS}

# Default pattern: who plays whom inside a cluster (indices in the cluster list).
INTRA_CLUSTER_EDGE_INDICES = [
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),
    (0, 3), (1, 4),
]

# Clusters on Peer_42's graph get different shapes, so his "petals" don't look alike.
# Clusters not listed here use INTRA_CLUSTER_EDGE_INDICES.
CLUSTER_EDGE_PATTERNS = {
    'A': [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),   # dense group
          (0, 3), (1, 4), (2, 5), (0, 2), (3, 5)],
    'B': [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],           # chain
    'C': [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)],   # ring
    'D': [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2)],   # star around index 0
    'F': [(0, 1), (1, 2), (2, 3), (4, 5)],                   # sparse
    'H': [(2, 0), (2, 1), (2, 3), (2, 4), (2, 5), (4, 5)],   # star around index 2
    'Q': [],                                                 # lone players
}

# Peer_42's opponents and how often he picks each of them (relative weight).
# A different number per cluster and different cluster shapes (CLUSTER_EDGE_PATTERNS),
# so the petals around him differ in size and density.
PEER42_OPPONENTS = {
    'QuantumPaddle': 3, 'GhostRally': 2, 'SolarSmash': 1,   # A: big dense petal
    'LunarDrift': 2, 'CrimsonAce': 1,                      # B: long chain
    'ThunderPad': 3, 'SilentSpin': 1,                      # C: arc of the ring
    'IronRicochet': 3,                                     # D: fan around one hub
    'DriftKing': 2, 'PulseServe': 1,                       # E: default shape
    'ArcticSmash': 2, 'PhantomPaddle': 1,                  # F: tail + separate pair
    'GlacierBounce': 2, 'EmberStrike': 1,                  # G: default shape
    'SapphireSmash': 2,                                    # H: fan around one hub
    'RookieRay': 1, 'LoneLobber': 1, 'QuietQuasar': 1,     # Q: single leaves
}
PEER42_FRIENDS = [
    'QuantumPaddle', 'GhostRally', 'SolarSmash', 'LunarDrift', 'ThunderPad',
    'IronRicochet', 'DriftKing', 'PulseServe', 'ArcticSmash', 'RookieRay',
]
PEER42_INCOMING_REQUESTS = ['EchoStrike', 'FrostyServe']

# --- activity tiers of demo users ---------------------------------------
# weight: scales the number of matches inside the cluster,
# share: part of all demo users, bonus: extra matches with existing partners.
ACTIVITY_TIERS = {
    'rookie':  {'weight': (1, 1),   'share': 0.15, 'bonus': (0, 0)},
    'casual':  {'weight': (2, 3),   'share': 0.25, 'bonus': (0, 0)},
    'regular': {'weight': (4, 5),   'share': 0.30, 'bonus': (3, 8)},
    'veteran': {'weight': (6, 8),   'share': 0.20, 'bonus': (15, 30)},
    'legend':  {'weight': (9, 12),  'share': 0.10, 'bonus': (40, 60)},
}

JOINED_DAYS_RANGE = (3, 180)
LEGEND_MIN_DAYS = 60

INTRA_CLUSTER_BASE_RANGE = (3, 6)

# --- Peer_42's matches ----------------------------------------------------
# Schedule: KEY_USER_WEEKS weeks up to yesterday. Matches per week follow
# a smooth curve (slow growth + gentle wave). He plays most days, 1-2 matches an evening:
# Player Stats puts a point on every match, so points of one evening stand on one x.
KEY_USER_WEEKS = 12
KEY_USER_JOINED_DAYS_AGO = KEY_USER_WEEKS * 7 + 4
KEY_USER_WEEKLY_BASE = 7
KEY_USER_WEEKLY_GROWTH = 3             # extra matches per week by the last week
KEY_USER_WEEKLY_WAVE = 1.5             # amplitude of the wave
KEY_USER_WEEKLY_WAVE_PERIOD = 6        # in weeks
KEY_USER_WEEKLY_MIN = 4
KEY_USER_MATCHES_PER_DAY = 1.4         # average, defines how many days a week he plays
KEY_USER_MIN_DAYS_PER_WEEK = 3
KEY_USER_SESSION_START_HOURS = (17, 22)
KEY_USER_BREAK_MINUTES = (1, 6)        # pause between matches in one evening
# Win rate trend (progress 0 = first match, 1 = last): grows from start to end,
# with a gentle wave and a slump, so the line tells a story: up, slump, strong climb.
KEY_USER_WIN_RATE_START = 0.30
KEY_USER_WIN_RATE_END = 0.70
KEY_USER_WAVE_DEPTH = 0.12
KEY_USER_WAVE_CYCLES = 1.5
KEY_USER_SLUMP_AT = 0.6
KEY_USER_SLUMP_DEPTH = 0.15
KEY_USER_SLUMP_WIDTH = 0.1
# Rolling window of Player Stats (WINDOW in DashPlayerStats.vue)
STATS_WINDOW = 10
# Rolling win rate moves only when the trend is this far from it (0.05 = half a step)
KEY_USER_TREND_TOLERANCE = 0.05
# Peer_42's opponents must exist before his first match
PEER42_OPPONENT_JOINED_DAYS_AGO = (KEY_USER_JOINED_DAYS_AGO + 5, 180)

# --- match events (Rally timeline) ---------------------------------------
HIT_CHAIN_SHORT_RANGE = (0, 1)
HIT_CHAIN_LONG_RANGE = (4, 16)
HIT_CHAIN_VISIBLE_PROBABILITY = 0.4


class Command(BaseCommand):
    help = 'Demo data for the dashboard (100 users in clusters, Peer_42 as the main account).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Deleting data of the previous run...')
        self._clear_previous_demo_data()

        n_users = sum(len(nicks) for nicks in ALL_CLUSTERS.values())
        self.stdout.write(f'Creating {n_users} demo users...')
        users_by_nickname, weights, tiers = self._create_background_users()

        self.stdout.write('Creating Peer_42...')
        key_user = self._create_key_user()
        self._backdate_key_user_opponents(users_by_nickname)
        users_by_nickname[KEY_NICKNAME] = key_user

        partner_map = defaultdict(set)

        self.stdout.write('Generating matches inside clusters...')
        self._generate_intra_cluster_matches(users_by_nickname, weights, partner_map)

        self.stdout.write('Generating bonus matches of regulars, veterans and legends...')
        self._generate_bonus_matches(users_by_nickname, tiers, partner_map)

        self.stdout.write('Generating Peer_42 matches...')
        self._generate_key_user_matches(key_user, users_by_nickname)

        self.stdout.write('Creating Peer_42 friends and friend requests...')
        self._create_key_user_friends(key_user, users_by_nickname)

        self.stdout.write('Recalculating wins/losses...')
        all_users = list(users_by_nickname.values())
        self._recalculate_wins_losses(all_users)

        peer42_matches = Match.objects.filter(Q(player1=key_user) | Q(player2=key_user)).count()
        self.stdout.write(self.style.SUCCESS(
            f'Done: {len(all_users)} users, {Match.objects.count()} matches '
            f'({peer42_matches} of them with Peer_42). '
            f'Login: {KEY_EMAIL} / {KEY_PASSWORD}'
        ))

    # --- cleanup ------------------------------------------------------------

    def _clear_previous_demo_data(self):
        demo_users = User.objects.filter(email__iendswith=DEMO_EMAIL_SUFFIX)
        # matches are not deleted together with users (SET_NULL), so they go first
        Match.objects.filter(
            Q(player1__in=demo_users) | Q(player2__in=demo_users)
        ).delete()
        demo_users.delete()

    # --- users --------------------------------------------------------------

    def _assign_tiers(self, nicknames):
        total = len(nicknames)
        counts = {
            tier: max(1, round(total * cfg['share']))
            for tier, cfg in ACTIVITY_TIERS.items()
        }
        counts['regular'] += total - sum(counts.values())

        tier_pool = []
        for tier, count in counts.items():
            tier_pool.extend([tier] * count)
        random.shuffle(tier_pool)
        return dict(zip(nicknames, tier_pool))

    def _pick_joined_days(self, tier_name):
        low, high = JOINED_DAYS_RANGE
        if tier_name == 'legend':
            low = max(low, LEGEND_MIN_DAYS)
        return random.randint(low, high)

    def _set_date_joined(self, user, days_ago):
        # date_joined is set on create, so it is changed with update()
        user.date_joined = timezone.now() - timedelta(days=days_ago)
        User.objects.filter(pk=user.pk).update(date_joined=user.date_joined)

    def _create_background_users(self):
        all_nicknames = [n for nicks in ALL_CLUSTERS.values() for n in nicks]
        tiers = self._assign_tiers(all_nicknames)

        users_by_nickname = {}
        weights = {}

        for nickname in all_nicknames:
            tier_name = tiers[nickname]
            user = User.objects.create_user(
                email=f'{nickname.lower()}{DEMO_EMAIL_SUFFIX}',
                password='demopass123',
                nickname=nickname,
                is_online=random.random() < 0.3,
            )
            self._set_date_joined(user, self._pick_joined_days(tier_name))
            users_by_nickname[nickname] = user
            weights[user.id] = random.randint(*ACTIVITY_TIERS[tier_name]['weight'])

        return users_by_nickname, weights, tiers

    def _create_key_user(self):
        user = User.objects.create_user(
            email=KEY_EMAIL,
            password=KEY_PASSWORD,
            nickname=KEY_NICKNAME,
            is_online=True,
        )
        self._set_date_joined(user, KEY_USER_JOINED_DAYS_AGO)
        return user

    def _backdate_key_user_opponents(self, users_by_nickname):
        """Peer_42's opponents must exist before his first match."""
        for nickname in PEER42_OPPONENTS:
            user = users_by_nickname[nickname]
            if (timezone.now() - user.date_joined).days < PEER42_OPPONENT_JOINED_DAYS_AGO[0]:
                self._set_date_joined(user, random.randint(*PEER42_OPPONENT_JOINED_DAYS_AGO))

    def _scale_match_count(self, base_range, user1, user2, weights):
        multiplier = (weights[user1.id] + weights[user2.id]) / 2 / 5.0
        low, high = base_range
        scaled_low = max(1, round(low * multiplier))
        scaled_high = max(scaled_low, round(high * multiplier))
        return random.randint(scaled_low, scaled_high)

    def _max_days_for_pair(self, u1, u2):
        """A pair can only play after both have joined."""
        d1 = (timezone.now() - u1.date_joined).days
        d2 = (timezone.now() - u2.date_joined).days
        return max(1, min(d1, d2))

    # --- Match / MatchEvent ---------------------------------------------------

    def _build_match_shell(self, player1, player2, ended_at, p1_wins=None):
        """Finished match 5:x. p1_wins=None means a random winner."""
        if p1_wins is None:
            p1_wins = random.random() < 0.5
        loser_score = random.randint(0, 4)
        score1, score2 = (5, loser_score) if p1_wins else (loser_score, 5)

        return Match(
            status=Match.Status.FINISHED,
            mode=Match.Mode.LOCAL,
            player1=player1,
            player2=player2,
            score_player1=score1,
            score_player2=score2,
            started_at=ended_at - timedelta(minutes=random.randint(2, 12)),
            ended_at=ended_at,
            winner=player1 if p1_wins else player2,
        )

    def _build_events_for_match(self, match):
        player1, player2 = match.player1, match.player2
        point_owners = [player1] * match.score_player1 + [player2] * match.score_player2
        random.shuffle(point_owners)

        duration = match.ended_at - match.started_at
        n_points = len(point_owners)
        point_times = [
            match.started_at + duration * (i + 1) / (n_points + 1)
            for i in range(n_points)
        ]

        events = []
        for point_index, scorer in enumerate(point_owners):
            other = player2 if scorer is player1 else player1
            point_end = point_times[point_index]
            point_start = point_times[point_index - 1] if point_index > 0 else match.started_at

            # most rallies are short, some are long and visible on the Rally timeline
            if random.random() < HIT_CHAIN_VISIBLE_PROBABILITY:
                n_hits = random.randint(*HIT_CHAIN_LONG_RANGE)
            else:
                n_hits = random.randint(*HIT_CHAIN_SHORT_RANGE)
            hit_gap = (point_end - point_start) / (n_hits + 1)

            for h in range(n_hits):
                events.append(MatchEvent(
                    match=match,
                    event_type=MatchEvent.EventType.HIT,
                    player=random.choice([player1, player2]),
                    timestamp=point_start + hit_gap * (h + 1),
                    pos_x=round(random.random(), 3),
                    pos_y=round(random.random(), 3),
                ))

            events.append(MatchEvent(
                match=match, event_type=MatchEvent.EventType.GOAL,
                player=scorer, timestamp=point_end,
                pos_x=round(random.random(), 3), pos_y=round(random.random(), 3),
            ))
            events.append(MatchEvent(
                match=match, event_type=MatchEvent.EventType.MISS,
                player=other, timestamp=point_end,
                pos_x=round(random.random(), 3), pos_y=round(random.random(), 3),
            ))

        return events

    def _random_ended_at(self, max_days_ago):
        """Random moment between max_days_ago and 1 day ago."""
        days_ago = random.uniform(1, max(max_days_ago, 1.5))
        return timezone.now() - timedelta(days=days_ago)

    def _bulk_create_matches_and_events(self, matches):
        Match.objects.bulk_create(matches)
        events = []
        for match in matches:
            events.extend(self._build_events_for_match(match))
        MatchEvent.objects.bulk_create(events)

    # --- matches of demo users --------------------------------------------------

    def _generate_intra_cluster_matches(self, users_by_nickname, weights, partner_map):
        matches = []
        for cluster, nicknames in ALL_CLUSTERS.items():
            cluster_users = [users_by_nickname[n] for n in nicknames]
            for i, j in CLUSTER_EDGE_PATTERNS.get(cluster, INTRA_CLUSTER_EDGE_INDICES):
                p1, p2 = cluster_users[i], cluster_users[j]
                partner_map[p1.id].add(p2)
                partner_map[p2.id].add(p1)
                n = self._scale_match_count(INTRA_CLUSTER_BASE_RANGE, p1, p2, weights)
                max_days = self._max_days_for_pair(p1, p2)
                for _ in range(n):
                    matches.append(self._build_match_shell(
                        p1, p2, self._random_ended_at(max_days)
                    ))
        self._bulk_create_matches_and_events(matches)

    def _generate_bonus_matches(self, users_by_nickname, tiers, partner_map):
        """Extra matches with existing partners only, so no new links appear on the graph."""
        matches = []
        for user in users_by_nickname.values():
            tier_name = tiers.get(user.nickname)
            if not tier_name:  # Peer_42 has no tier, his matches are generated separately
                continue
            bonus_range = ACTIVITY_TIERS[tier_name]['bonus']
            existing_partners = list(partner_map[user.id])
            if bonus_range[1] == 0 or not existing_partners:
                continue
            for _ in range(random.randint(*bonus_range)):
                opponent = random.choice(existing_partners)
                ended_at = self._random_ended_at(self._max_days_for_pair(user, opponent))
                matches.append(self._build_match_shell(user, opponent, ended_at))
        self._bulk_create_matches_and_events(matches)

    # --- Peer_42 --------------------------------------------------------------

    def _key_user_weekly_matches(self, week):
        progress = week / (KEY_USER_WEEKS - 1)
        target = (
            KEY_USER_WEEKLY_BASE
            + KEY_USER_WEEKLY_GROWTH * progress
            + KEY_USER_WEEKLY_WAVE * math.sin(2 * math.pi * week / KEY_USER_WEEKLY_WAVE_PERIOD)
            + random.randint(-1, 1)
        )
        return max(KEY_USER_WEEKLY_MIN, round(target))

    def _key_user_schedule(self):
        """Playing days as (days_ago, matches), oldest first. Every week has matches."""
        days = []
        for week in range(KEY_USER_WEEKS):
            # days_ago of the week's days, oldest week first; the last day is yesterday
            week_days = [KEY_USER_WEEKS * 7 - week * 7 - d for d in range(7)]
            n_matches = self._key_user_weekly_matches(week)
            n_days = min(7, n_matches, max(KEY_USER_MIN_DAYS_PER_WEEK,
                                           round(n_matches / KEY_USER_MATCHES_PER_DAY)))
            play_days = sorted(random.sample(week_days, k=n_days), reverse=True)
            # every day gets one match, the rest are spread randomly
            counts = [1] * n_days
            for _ in range(n_matches - n_days):
                counts[random.randrange(n_days)] += 1
            days.extend(zip(play_days, counts))
        return days

    def _key_user_win_probability(self, progress):
        """Target win rate; progress: 0 at the first match, 1 at the last one."""
        trend = KEY_USER_WIN_RATE_START + (KEY_USER_WIN_RATE_END - KEY_USER_WIN_RATE_START) * progress
        wave = KEY_USER_WAVE_DEPTH * math.sin(2 * math.pi * KEY_USER_WAVE_CYCLES * progress)
        slump = KEY_USER_SLUMP_DEPTH * math.exp(
            -((progress - KEY_USER_SLUMP_AT) / KEY_USER_SLUMP_WIDTH) ** 2
        )
        return trend + wave - slump

    def _key_user_outcomes(self, days):
        """Wins/losses for every match, in order, shaped for the rolling win rate.

        Repeating the result that leaves the window keeps the rate unchanged.
        The rate moves one step (1/STATS_WINDOW) towards the trend only on the
        first match of a day, so it never jumps up and down within one evening.
        """
        n_total = sum(n for _, n in days)
        outcomes = []
        for _, n_matches in days:
            for match_of_day in range(n_matches):
                i = len(outcomes)
                target = self._key_user_win_probability(i / max(1, n_total - 1))
                if i < STATS_WINDOW:
                    # window not full yet: pick the result that keeps the rate closest to the trend
                    wins = sum(outcomes)
                    is_win = abs((wins + 1) / (i + 1) - target) <= abs(wins / (i + 1) - target)
                else:
                    leaving = outcomes[i - STATS_WINDOW]
                    rate = sum(outcomes[i - STATS_WINDOW:i]) / STATS_WINDOW
                    is_win = leaving
                    if match_of_day == 0:
                        if target >= rate + KEY_USER_TREND_TOLERANCE and not leaving:
                            is_win = True
                        elif target <= rate - KEY_USER_TREND_TOLERANCE and leaving:
                            is_win = False
                outcomes.append(is_win)
        return outcomes

    def _generate_key_user_matches(self, key_user, users_by_nickname):
        opponents = [users_by_nickname[n] for n in PEER42_OPPONENTS]
        opponent_weights = list(PEER42_OPPONENTS.values())
        days = self._key_user_schedule()
        outcomes = iter(self._key_user_outcomes(days))

        matches = []
        for days_ago, n_matches in days:
            day = timezone.localtime() - timedelta(days=days_ago)
            ended_at = day.replace(
                hour=random.randint(*KEY_USER_SESSION_START_HOURS),
                minute=random.randint(0, 59), second=0, microsecond=0,
            )
            for _ in range(n_matches):
                if ended_at > timezone.now():  # yesterday's late evening ran past midnight
                    break
                opponent = random.choices(opponents, weights=opponent_weights)[0]
                is_win = next(outcomes)
                # Peer_42 is player1 or player2 at random, like in real matches
                if random.random() < 0.5:
                    match = self._build_match_shell(key_user, opponent, ended_at, p1_wins=is_win)
                else:
                    match = self._build_match_shell(opponent, key_user, ended_at, p1_wins=not is_win)
                matches.append(match)
                # the next match ends after this one's length plus a short break
                ended_at += (match.ended_at - match.started_at) + timedelta(
                    minutes=random.randint(*KEY_USER_BREAK_MINUTES))
        self._bulk_create_matches_and_events(matches)

    def _create_key_user_friends(self, key_user, users_by_nickname):
        relations = []
        for nickname in PEER42_FRIENDS:
            friend = users_by_nickname[nickname]
            from_user, to_user = random.choice([(key_user, friend), (friend, key_user)])
            relations.append(FriendRelation(
                from_user=from_user, to_user=to_user, status='accepted'))
        for nickname in PEER42_INCOMING_REQUESTS:
            relations.append(FriendRelation(
                from_user=users_by_nickname[nickname], to_user=key_user, status='pending'))
        FriendRelation.objects.bulk_create(relations)

    # --- denormalized counters ------------------------------------------------

    def _recalculate_wins_losses(self, users):
        for user in users:
            user.wins = Match.objects.filter(winner=user).count()
            user.losses = Match.objects.filter(
                Q(player1=user) | Q(player2=user),
                status=Match.Status.FINISHED,
                winner__isnull=False,
            ).exclude(winner=user).count()
        User.objects.bulk_update(users, ['wins', 'losses'])
