"""
Remove demo data without generating it again.

Deletes only what seed_demo_data creates: users with an @example.com email
and their matches/events. Real accounts and their data are never touched,
demo users are identified strictly by the email domain.

Usage:
    docker-compose exec backend python manage.py clear_demo_data
    docker-compose exec backend python manage.py clear_demo_data --yes   # no confirmation prompt
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from game.models import Match

User = get_user_model()

DEMO_EMAIL_SUFFIX = '@example.com'


class Command(BaseCommand):
    help = 'Delete demo data (@example.com users and their matches/events), real accounts are kept.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Delete without asking for confirmation.',
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
            self.stdout.write(self.style.WARNING('No demo data found, nothing to delete.'))
            return

        self.stdout.write(
            f'Will delete {users_count} demo users '
            f'(email ends with "{DEMO_EMAIL_SUFFIX}") and {matches_count} of their matches '
            f'(events are deleted together with the matches).'
        )

        if not options['yes']:
            answer = input('Continue? [y/N]: ').strip().lower()
            if answer != 'y':
                self.stdout.write(self.style.WARNING('Cancelled, nothing was deleted.'))
                return

        # Match.player1/player2/winner use on_delete=SET_NULL, so matches are NOT
        # deleted together with users and must be removed first.
        # MatchEvent is deleted by CASCADE from Match.
        demo_matches.delete()
        demo_users.delete()

        self.stdout.write(self.style.SUCCESS(
            f'Done: deleted {users_count} demo users and {matches_count} matches.'
        ))