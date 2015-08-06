import datetime

from unittest import TestCase

from bai2.utils import parse_date, parse_military_time


class ParseDateTestCase(TestCase):

    def test_parse(self):
        parsed = parse_date('150330')
        self.assertEqual(
            datetime.date(year=2015, month=3, day=30),
            parsed
        )


class ParseMilitaryTime(TestCase):

    def test_parse(self):
        parsed_value = parse_military_time('2145')

        self.assertEqual(
            datetime.time(hour=21, minute=45),
            parsed_value
        )

    def test_parse_end_of_day_as_9999(self):
        parsed_value = parse_military_time('9999')

        self.assertEqual(
            datetime.time(hour=23, minute=59),
            parsed_value
        )

    def test_parse_end_of_day_as_2400(self):
        parsed_value = parse_military_time('2400')

        self.assertEqual(
            datetime.time(hour=23, minute=59),
            parsed_value
        )

    def test_parse_beginning_of_day(self):
        parsed_value = parse_military_time('0000')

        self.assertEqual(
            datetime.time(hour=0, minute=0),
            parsed_value
        )
