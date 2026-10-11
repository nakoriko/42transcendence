from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase
from django.conf import settings

class StaticFilesTest(SimpleTestCase):
    def test_coollectstatic_is_configured(self):
        call_command('collectstatic', '--noinput', '--dry-run', stdout=StringIO())
        
class RedisSettingsTests(SimpleTestCase):
    def test_channel_layer_uses_redis_host_settings(self):
        host, port = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
        self.assertEqual(host, settings.REDIS_HOST)