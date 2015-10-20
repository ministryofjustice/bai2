from bai2.parsers import Bai2FileParser
from bai2.writers import Bai2FileWriter
from bai2.helpers import IteratorHelper


def parse_from_lines(lines):
    helper = IteratorHelper(lines)
    parser = Bai2FileParser(helper)
    return parser.parse()


def parse_from_string(s):
    return parse_from_lines(s.splitlines())


def parse_from_file(f):
    return parse_from_string(f.read())


def write_to_string(bai2_obj):
    return Bai2FileWriter(bai2_obj).write()
