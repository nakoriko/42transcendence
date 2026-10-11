import redis
from django.core.management.base import BaseCommand
from django.conf import settings

from users.models import User

class Command(BaseCommand):
    help = 'Mark all users offline and clear WS connection counters. Run once before starting workers'

    def handle(self, *args, **options):
        updated = User.objects.filter(is_online=True).update(is_online=False)

        r = redis.Redis(host=settings.REDIS_HOST, port=6379)
        deleted = 0
        for key in r.scan_iter('ws_conn_count:*'):
            r.delete(key)
            deleted +=1
        
        self.stdout.write(f'Presence reset: {updated} users set offline, {deleted} counters cleared')
