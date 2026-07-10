"""
Демонстрационный сид-скрипт для аналитического дашборда
(Pong Universe / Player Stats / Rally Timeline).

НЕ часть обычного workflow приложения — не пушим как рабочую фичу,
запускаем вручную перед демонстрацией:

    docker-compose exec backend python manage.py seed_demo_data

Безопасен для повторного запуска: сначала удаляет данные предыдущего
запуска (по email-домену @example.com — все демо-юзеры используют его),
затем создаёт всё заново.

⚠️ После КАЖДОГО перезапуска скрипта юзер Peer_42 пересоздаётся с новым id
— старые JWT-токены в браузере станут невалидными (см. разбор бесконечных
401 в истории чата). Разлогинься/залогинься заново (или чисти localStorage)
после каждого прогона.

Куда положить этот файл:
    backend/game/management/commands/seed_demo_data.py

Нужны ещё два (пустых) файла, если их ещё нет:
    backend/game/management/__init__.py
    backend/game/management/commands/__init__.py
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from game.models import Match, MatchEvent

User = get_user_model()

# --- конфигурация ------------------------------------------------------

KEY_EMAIL = 'Peer42@example.com'
KEY_NICKNAME = 'Peer_42'
KEY_PASSWORD = '123'
KEY_WIN_PROBABILITY = 0.65  # шанс, что в матче победит именно Peer_42

# 50 фоновых игроков для "Pong Universe". У каждого случайный "вес
# активности" (1-10) — при выборе оппонентов для фоновых матчей юзеры
# с большим весом встречаются чаще → на графике естественно появляются
# и "новички" с несколькими матчами, и явные "ветераны" с полусотней.
BACKGROUND_NICKNAMES = [
    'NeonServe', 'ViperSpin', 'QuantumPaddle', 'GhostRally', 'AceVortex',
    'SolarSmash', 'CrimsonAce', 'ZenBounce', 'TurboTopspin', 'LunarDrift',
    'ObsidianEdge', 'EchoStrike', 'PixelPunch', 'VelvetVolley', 'ThunderPad',
    'SilentSpin', 'BlazeCourt', 'FrostyServe', 'IronRicochet', 'VoltDrive',
    'ShadowSmash', 'AmberSpike', 'CobaltCurve', 'MysticVolley', 'RapidFuse',
    'GoldenPaddle', 'NovaStrike', 'DriftKing', 'PulseServe', 'CrypticSpin',
    'SteelSpin', 'VenomServe', 'ArcticSmash', 'RogueVolley', 'PhantomPaddle',
    'StormEdge', 'CopperCurve', 'WildfireSpin', 'GlacierBounce', 'EmberStrike',
    'TitanServe', 'WhisperSpin', 'RadiantVolley', 'OnyxDrive', 'SapphireSmash',
    'VelocitySpin', 'MidnightVolley', 'CoralStrike', 'ZephyrPaddle', 'InfernoServe',
]

BACKGROUND_MATCHES_COUNT = 450   # суммарно между всеми фоновыми юзерами

# DashRallyTimeline фильтрует ралли с hits <= 1 (не показывает их вообще —
# см. `.filter(r => r.hits > 1)` в компоненте). Чтобы на графике было
# МЕНЬШЕ видимых ралли, но каждое видимое было эффектнее (длиннее) —
# генерируем цепочку ударов бимодально: с вероятностью
# HIT_CHAIN_VISIBLE_PROBABILITY берём длинную цепочку (она попадёт
# на график), иначе — короткую 0-1 удар (отфильтруется, просто не
# попадёт в Rally Timeline и почти не будет видна в MatchEchoViz).
HIT_CHAIN_SHORT_RANGE = (0, 1)
HIT_CHAIN_LONG_RANGE = (4, 16)
HIT_CHAIN_VISIBLE_PROBABILITY = 0.4

# (мин.активных дней, макс.активных дней, дней назад от, дней назад до).
# "Активный день" — календарный день, в который сыгран хотя бы 1 матч
# ключевого юзера; на каждый активный день приходится 1-3 матча.
# Диапазон активных дней (а не фиксированное число) — при каждом
# запуске получается чуть другая картина, естественнее.
KEY_USER_MATCH_BUCKETS = [
    (2, 4, 0, 7),
    (3, 5, 8, 30),
    (3, 5, 31, 90),
]
KEY_USER_DAY_MATCHES_RANGE = (1, 4)  # матчей на один активный день
MIXED_DAY_PROBABILITY = 0.75  # шанс, что день НЕ будет "чисто победным/проигрышным"


class Command(BaseCommand):
    help = 'Наполняет БД демо-данными для аналитического дашборда (Pong Universe / Player Stats / Rally Timeline).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Очищаю данные предыдущего запуска...')
        self._clear_previous_demo_data()

        self.stdout.write('Создаю фоновых пользователей...')
        background_users = self._create_background_users()
        weights = {u.id: random.randint(1, 10) for u in background_users}

        self.stdout.write('Создаю ключевого пользователя...')
        key_user = self._create_key_user()

        self.stdout.write(f'Генерирую {BACKGROUND_MATCHES_COUNT} фоновых матчей...')
        self._generate_background_matches(background_users, weights)

        self.stdout.write('Генерирую матчи ключевого пользователя...')
        self._generate_key_user_matches(key_user, background_users)

        self.stdout.write('Пересчитываю wins/losses...')
        self._recalculate_wins_losses(background_users + [key_user])

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Логин для демонстрации: {KEY_EMAIL} / {KEY_PASSWORD}'
        ))

    # --- очистка -----------------------------------------------------

    def _clear_previous_demo_data(self):
        demo_users = User.objects.filter(email__iendswith='@example.com')
        # Match: player1/player2/winner — on_delete=SET_NULL, значит матчи
        # НЕ удалятся каскадом при удалении юзеров, их нужно снести явно
        # ДО удаления юзеров. MatchEvent удалится каскадом от Match сам.
        Match.objects.filter(
            Q(player1__in=demo_users) | Q(player2__in=demo_users)
        ).delete()
        demo_users.delete()

    # --- пользователи --------------------------------------------------

    def _create_background_users(self):
        users = []
        for nickname in BACKGROUND_NICKNAMES:
            user = User.objects.create_user(
                email=f'{nickname.lower()}@example.com',
                password='demopass123',
                nickname=nickname,
                is_online=random.random() < 0.3,
            )
            # date_joined — auto_now_add=True. create_user() идёт через
            # save(), который запускает pre_save() и подставляет "сейчас",
            # игнорируя переданное значение. Поэтому фиксируем дату
            # отдельным .update() СРАЗУ после создания — обычный SQL
            # UPDATE, auto_now_add тут уже не участвует.
            joined_days_ago = random.randint(1, 120)
            User.objects.filter(pk=user.pk).update(
                date_joined=timezone.now() - timedelta(days=joined_days_ago)
            )
            users.append(user)
        return users

    def _create_key_user(self):
        user = User.objects.create_user(
            email=KEY_EMAIL,
            password=KEY_PASSWORD,
            nickname=KEY_NICKNAME,
            is_online=True,
        )
        joined_days_ago = random.randint(60, 90)
        User.objects.filter(pk=user.pk).update(
            date_joined=timezone.now() - timedelta(days=joined_days_ago)
        )
        return user

    # --- построение одного матча + его событий ------------------------

    def _pick_weighted_pair(self, pool, weights):
        """Выбирает двух РАЗНЫХ юзеров, с вероятностью пропорциональной весу."""
        pool_weights = [weights[u.id] for u in pool]
        p1 = random.choices(pool, weights=pool_weights, k=1)[0]
        p2 = p1
        while p2 is p1:
            p2 = random.choices(pool, weights=pool_weights, k=1)[0]
        return p1, p2

    def _build_match_shell(self, player1, player2, ended_at,
                            favor_p1_prob=0.5, forced_p1_wins=None):
        """
        Создаёт (пока НЕ сохранённый) Match. Правило игры — "до 5 очков":
        победитель ВСЕГДА получает ровно 5, проигравший — случайно 0..4
        (иначе физически невозможно: игра обязана закончиться, как только
        кто-то первым доходит до 5).

        favor_p1_prob — шанс, что в этом матче выиграет именно player1
        (используется, когда исход разыгрывается монеткой).

        forced_p1_wins — если задан (True/False), исход НЕ разыгрывается,
        а прибивается жёстко (используем для ключевого юзера — там нужно
        точно контролировать, сколько побед/поражений выпадет на
        конкретный день, чтобы дни не повторялись подряд).

        started_at/ended_at выставляем сразу в конструкторе: bulk_create()
        (в отличие от save()) НЕ запускает pre_save(), auto_now_add не
        трогает эти значения — они дойдут до БД как есть.
        """
        duration = timedelta(minutes=random.randint(2, 12))
        loser_score = random.randint(0, 4)

        if forced_p1_wins is not None:
            p1_wins = forced_p1_wins
        else:
            p1_wins = random.random() < favor_p1_prob

        if p1_wins:
            score1, score2 = 5, loser_score
            winner = player1
        else:
            score2, score1 = 5, loser_score
            winner = player2

        return Match(
            status=Match.Status.FINISHED,
            mode=Match.Mode.LOCAL,
            player1=player1,
            player2=player2,
            score_player1=score1,
            score_player2=score2,
            started_at=ended_at - duration,
            ended_at=ended_at,
            winner=winner,
        )

    def _build_events_for_match(self, match):
        """
        Строит события (ралли) для УЖЕ сохранённого матча (с pk).
        При правиле "до 5" счёт 0-0 невозможен — эта ветка не
        обязательна, но оставлена как защита на случай будущих правок.
        Один розыгрыш = N x hit -> goal (у того, кто забил) + miss (у того,
        кто прозевал) с одинаковым таймстампом — повторяет существующий
        паттерн записи событий из GameView.vue.
        """
        if match.score_player1 == 0 and match.score_player2 == 0:
            return []

        player1, player2 = match.player1, match.player2
        point_owners = [player1] * match.score_player1 + [player2] * match.score_player2
        random.shuffle(point_owners)

        duration = match.ended_at - match.started_at
        n_points = len(point_owners)
        point_times = sorted(
            match.started_at + duration * (i + 1) / (n_points + 1)
            for i in range(n_points)
        )

        events = []
        for point_index, scorer in enumerate(point_owners):
            other = player2 if scorer is player1 else player1
            point_end = point_times[point_index]
            point_start = point_times[point_index - 1] if point_index > 0 else match.started_at

            if random.random() < HIT_CHAIN_VISIBLE_PROBABILITY:
                n_hits = random.randint(*HIT_CHAIN_LONG_RANGE)
            else:
                n_hits = random.randint(*HIT_CHAIN_SHORT_RANGE)
            hit_gap = (point_end - point_start) / (n_hits + 1)

            for h in range(n_hits):
                hitter = random.choice([player1, player2])
                events.append(MatchEvent(
                    match=match,
                    event_type=MatchEvent.EventType.HIT,
                    player=hitter,
                    timestamp=point_start + hit_gap * (h + 1),
                    pos_x=round(random.random(), 3),
                    pos_y=round(random.random(), 3),
                    # reaction_time_ms не заполняем — больше не используется
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

    # --- генерация матчей пачками --------------------------------------

    def _generate_background_matches(self, pool, weights):
        matches = []
        for _ in range(BACKGROUND_MATCHES_COUNT):
            player1, player2 = self._pick_weighted_pair(pool, weights)
            days_ago = random.uniform(1, 90)
            ended_at = timezone.now() - timedelta(days=days_ago)
            matches.append(self._build_match_shell(player1, player2, ended_at))

        # На Postgres bulk_create сам проставляет pk на переданные объекты
        # (RETURNING id) — дальше matches уже с валидными id.
        Match.objects.bulk_create(matches)

        events = []
        for match in matches:
            events.extend(self._build_events_for_match(match))
        MatchEvent.objects.bulk_create(events)

    def _generate_key_user_matches(self, key_user, opponents):
        """
        PlayerStatsView строит по одной точке на каждый календарный день,
        где у ключевого юзера был хотя бы 1 матч. Чтобы линии total/wins/
        losses не превращались в плоские отрезки, идём СТРОГО по дням в
        хронологическом порядке (от старых к новым) и для каждого дня
        рандомим (total, wins, losses), пока получившаяся тройка не будет
        отличаться от вчерашней СРАЗУ по всем трём числам. Вариантов мало
        (total 1-3), поэтому это быстро — обычно 1-2 попытки.
        """
        matches = []

        # Шаг 1: собираем активные дни СО ВСЕХ корзин в один список.
        # Важно делать это до анти-повторной проверки — иначе последний
        # день одной корзины (например 7d) не сравнивается с первым днём
        # следующей (30d), хотя на итоговом графике они окажутся соседними.
        chosen_days = []
        for min_active_days, max_active_days, min_days_ago, max_days_ago in KEY_USER_MATCH_BUCKETS:
            available_days = list(range(min_days_ago, max_days_ago + 1))
            active_days_count = random.randint(
                min_active_days, min(max_active_days, len(available_days))
            )
            chosen_days.extend(random.sample(available_days, k=active_days_count))

        # По убыванию days_ago = от старых дат к новым (хронологический
        # порядок слева направо, как рисует его PlayerStatsView)
        chosen_days.sort(reverse=True)

        # Шаг 2: идём по ЕДИНОМУ отсортированному списку дней и для каждого
        # дня рандомим (total, wins, losses), пока тройка не станет
        # отличаться от ПРЕДЫДУЩЕГО дня сразу по всем трём числам.
        prev_stats = None
        for days_ago in chosen_days:
            for _ in range(50):  # запас попыток, на случай неудачного рандома
                day_total = random.randint(*KEY_USER_DAY_MATCHES_RANGE)
                # По умолчанию day_wins мог случайно выпасть 0 или day_total
                # ("чисто победный"/"чисто проигрышный" день) - при малом
                # total это происходит СЛИШКОМ часто и даёт неестественно
                # ритмичный, "нарисованный по лекалу" график (см. скрин).
                # Поэтому явно смещаем в сторону смешанных дней - оставляем
                # чистые исходы только как редкое исключение.
                if day_total >= 2 and random.random() < MIXED_DAY_PROBABILITY:
                    day_wins = random.randint(1, day_total - 1)
                else:
                    day_wins = random.randint(0, day_total)
                day_losses = day_total - day_wins
                if prev_stats is None or (
                    day_total != prev_stats[0]
                    and day_wins != prev_stats[1]
                    and day_losses != prev_stats[2]
                ):
                    break
            prev_stats = (day_total, day_wins, day_losses)

            outcomes = [True] * day_wins + [False] * day_losses  # True = победа key_user
            random.shuffle(outcomes)

            for is_win in outcomes:
                opponent = random.choice(opponents)
                # время суток внутри дня — разное, чтобы у матчей
                # одного дня были разные (не идентичные) timestamp
                ended_at = timezone.now() - timedelta(
                    days=days_ago,
                    hours=random.uniform(0, 3),
                    minutes=random.uniform(0, 59),
                )
                # чередуем, кто из двоих player1/player2 — но исход
                # (forced_p1_wins) всегда считаем ОТНОСИТЕЛЬНО key_user
                if random.random() < 0.5:
                    match = self._build_match_shell(
                        key_user, opponent, ended_at, forced_p1_wins=is_win,
                    )
                else:
                    match = self._build_match_shell(
                        opponent, key_user, ended_at, forced_p1_wins=not is_win,
                    )
                matches.append(match)

        Match.objects.bulk_create(matches)

        events = []
        for match in matches:
            events.extend(self._build_events_for_match(match))
        MatchEvent.objects.bulk_create(events)

    # --- пересчёт денормализованных счётчиков ---------------------------

    def _recalculate_wins_losses(self, users):
        """
        User.wins/losses — денормализованные счётчики. Важно: теперь
        матчи могут заканчиваться без победителя (0-0 форфит), поэтому
        losses считаем ТОЛЬКО среди матчей с явным winner — иначе 0-0
        матч ошибочно засчитался бы поражением обоим игрокам сразу.
        """
        for user in users:
            user.wins = Match.objects.filter(winner=user).count()
            user.losses = Match.objects.filter(
                Q(player1=user) | Q(player2=user),
                status=Match.Status.FINISHED,
                winner__isnull=False,
            ).exclude(winner=user).count()

        User.objects.bulk_update(users, ['wins', 'losses'])