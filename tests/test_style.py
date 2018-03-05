import pkg_resources
import unittest


class CodeStyleTestCase(unittest.TestCase):
    def test_code_style(self):
        flake8 = pkg_resources.load_entry_point('flake8', 'console_scripts', 'flake8')
        try:
            flake8([])
        except SystemExit as e:
            if e.code != 0:
                self.fail('Code style checks failed')
