from bai2.parsers import Bai2FileParser
from bai2.helpers import IteratorHelper


def parse(lines):
    helper = IteratorHelper(lines)
    parser = Bai2FileParser(helper)
    return parser.parse()
