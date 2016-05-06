from __future__ import absolute_import

from bai2.parsers import Bai2FileParser
from bai2.writers import Bai2FileWriter
from bai2.helpers import IteratorHelper


def parse_from_lines(lines, **kwargs):
    helper = IteratorHelper(lines)
    parser = Bai2FileParser(helper, **kwargs)
    return parser.parse()


def parse_from_string(s, **kwargs):
    return parse_from_lines(s.splitlines(), **kwargs)


def parse_from_file(f, **kwargs):
    return parse_from_string(f.read(), **kwargs)


def write(bai2_obj, **kwargs):
    return '\n'.join(Bai2FileWriter(bai2_obj, **kwargs).write())
