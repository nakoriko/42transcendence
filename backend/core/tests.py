import os
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.conf import settings
from game.models import Match
from core.settings import env_list

class StaticFilesTest(SimpleTestCase):
    def test_collectstatic_is_configured(self):
        call_command('collectstatic', '--noinput', '--dry-run', stdout=StringIO())
        
class RedisSettingsTests(SimpleTestCase):
    def test_channel_layer_uses_redis_host_settings(self):
        host, port = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
        self.assertEqual(host, settings.REDIS_HOST)

class MigrationsTests(TestCase):
    def test_no_missing_migrations(self):
        call_command('makemigrations', '--check', '--dry-run',
        stdout=StringIO())

    def test_finished_status_label(self):
        self.assertEqual(Match.Status.FINISHED.label, 'Match finished')

class EnvListTests(SimpleTestCase):
    def test_returns_default_when_variable_is_not_set(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(env_list('HOSTS', ['localhost']), ['localhost'])

    def test_splits_comma_separated_values(self):
        with patch.dict(os.environ, {'HOSTS': 'example.com, api.example.com ,'}):
            self.assertEqual(env_list('HOSTS', ['localhost']), ['example.com', 'api.example.com'])
