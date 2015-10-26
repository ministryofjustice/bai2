import os


class Bai2Settings(object):
    def __init__(self):
        self._conf = {}

    def load(self):
        if not self._conf:
            self._conf = {
                'IGNORE_INTEGRITY_CHECKS': os.environ.get(
                    'BAI2_IGNORE_INTEGRITY_CHECKS', '0'
                ) == '1',
                'TEXT_ON_NEW_LINE': os.environ.get(
                    'BAI2_TEXT_ON_NEW_LINE', '0'
                ) == '1',
                'LINE_LENGTH': int(os.environ.get(
                    'BAI2_LINE_LENGTH', 80
                )),
                'USE_CLOCK_FORMAT_FOR_INTRA_DAY': os.environ.get(
                    'BAI2_USE_CLOCK_FORMAT_FOR_INTRA_DAY', '0'
                ) == '1'
            }

    def __getattr__(self, attr):
        self.load()
        return self._conf[attr]
settings = Bai2Settings()
