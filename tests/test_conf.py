import mock
from unittest import TestCase

from bai2.conf import Bai2Settings


class Bai2SettingsTestCase(TestCase):
    def test_defaults(self):
        """
        Tests that if no settings are set, use defaults.
        """
        settings = Bai2Settings()
        self.assertFalse(settings.IGNORE_INTEGRITY_CHECKS)

    def test_ignore_integrity_checks_true(self):
        with mock.patch.dict(
            'os.environ', {'BAI2_IGNORE_INTEGRITY_CHECKS': '1'}
        ):
            settings = Bai2Settings()
            self.assertTrue(settings.IGNORE_INTEGRITY_CHECKS)

    def test_ignore_integrity_checks_invalid_value(self):
        """
        Tests that if the value is != '1', the module ignores it.
        """
        with mock.patch.dict(
            'os.environ', {'BAI2_IGNORE_INTEGRITY_CHECKS': 'invalid'}
        ):
            settings = Bai2Settings()
            self.assertFalse(settings.IGNORE_INTEGRITY_CHECKS)
