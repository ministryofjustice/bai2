import logging
import pkg_resources
import unittest


class CodeStyleTestCase(unittest.TestCase):
    def test_code_style(self):
        logger = logging.getLogger('flake8')
        logger.setLevel(logging.ERROR)
        flake8 = pkg_resources.load_entry_point('flake8', 'console_scripts', 'flake8')
        if flake8(['--jobs', '0']):
            self.fail('Code style checks failed')
