from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase

class StaticFilesTest(SimpleTestCase):
    def test_coollectstatic_is_configured(self):
        call_command('collectstatic', '--noinput', '--dry-run', stdout=StringIO())
        