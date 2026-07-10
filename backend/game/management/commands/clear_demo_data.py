"""
Отдельная команда для ОЧИСТКИ демо-данных без повторной генерации.
Удаляет только то, что создаёт seed_demo_data.py (юзеры на домене
@example.com и их матчи/события) — реальные аккаунты и их данные
не трогает вообще, идентификация идёт строго по email-домену.

Запуск:
    docker-compose exec backend python manage.py clear_demo_data

По умолчанию спрашивает подтверждение (сколько юзеров/матчей будет
удалено). Для автоматического запуска без вопроса — флаг --yes:

    docker-compose exec backend python manage.py clear_demo_data --yes

Куда положить:
    backend/game/management/commands/clear_demo_data.py
(в той же папке management/commands/, что и seed_demo_data.py)
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from game.models import Match

User = get_user_model()

DEMO_EMAIL_SUFFIX = '@example.com'


class Command(BaseCommand):
    help = 'Удаляет демо-данные (юзеров на @example.com и их матчи/события), не трогая реальные аккаунты.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Не спрашивать подтверждение, удалить сразу.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        demo_users = User.objects.filter(email__iendswith=DEMO_EMAIL_SUFFIX)
        demo_matches = Match.objects.filter(
            Q(player1__in=demo_users) | Q(player2__in=demo_users)
        )

        users_count = demo_users.count()
        matches_count = demo_matches.count()

        if users_count == 0 and matches_count == 0:
            self.stdout.write(self.style.WARNING('Демо-данных не найдено — нечего чистить.'))
            return

        self.stdout.write(
            f'Будет удалено: {users_count} демо-юзеров '
            f'(email оканчивается на "{DEMO_EMAIL_SUFFIX}") и {matches_count} их матчей '
            f'(события удалятся каскадом вместе с матчами).'
        )

        if not options['yes']:
            answer = input('Продолжить? [y/N]: ').strip().lower()
            if answer != 'y':
                self.stdout.write(self.style.WARNING('Отменено, ничего не удалено.'))
                return

        # Match: player1/player2/winner — on_delete=SET_NULL, значит матчи
        # НЕ удалятся каскадом при удалении юзеров, их нужно снести явно
        # ДО удаления юзеров. MatchEvent удалится каскадом от Match сам
        # (там on_delete=CASCADE).
        demo_matches.delete()
        demo_users.delete()

        self.stdout.write(self.style.SUCCESS(
            f'Готово: удалено {users_count} демо-юзеров и {matches_count} матчей.'
        ))