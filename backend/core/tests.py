from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.conf import settings
from game.models import Match

class StaticFilesTest(SimpleTestCase):
    def test_collectstatic_is_configured(self):
        call_command('collectstatic', '--noinput', '--dry-run', stdout=StringIO())
        
class RedisSettingsTests(SimpleTestCase):
    def test_channel_layer_uses_redis_host_settings(self):
        host, port = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
        self.assertEqual(host, settings.REDIS_HOST)

class MigrationTests(TestCase):
    def test_no_missiing_migrations(self):
        call_command('makemigrations', '--check', '--dry-run',
        stdout=StringIO())

    def test_finished_status_label(self):
        self.assertEqual(Match.Status.FINISHED.label, 'Match finished')