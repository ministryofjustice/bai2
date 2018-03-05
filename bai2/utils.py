import datetime
import re

from .constants import TypeCodes


def parse_date(value):
    """
    YYMMDD Format.
    """
    return datetime.datetime.strptime(value, '%y%m%d').date()


def write_date(date):
    return date.strftime('%y%m%d')


def parse_time(value):
    clock_pattern = re.compile('\d\d:\d\d:\d\d')

    if clock_pattern.match(value):
        return parse_clock_time(value)
    else:
        return parse_military_time(value)


def parse_clock_time(value):
    return datetime.datetime.strptime(value, '%H:%M:%S').time()


def parse_military_time(value):
    """
    Military Format, 24 hours. 0001 through 2400.
    Times are stated in military format (0000 through 2400).
    0000 indicates the beginning of the day and 2400 indicates the end of the day
    for the date indicated.
    Some processors use 9999 to indicate the end of the day.
    Be prepared to recognize 9999 as end-of-day when receiving transmissions.
    """
    # 9999 indicates end of the day
    # 2400 indicates end of the day but 24:00 not allowed so
    # it's really 23:59
    if value == '9999' or value == '2400':
        return datetime.time.max
    return datetime.datetime.strptime(value, '%H%M').time()


def write_time(time, clock_format_for_intra_day=False):
    if clock_format_for_intra_day and time != datetime.time.max:
        return write_clock_time(time)
    else:
        return write_military_time(time)


def write_clock_time(time):
    date = datetime.datetime.now().replace(hour=time.hour,
                                           minute=time.minute,
                                           second=time.second)
    return datetime.datetime.strftime(date, '%H:%M:%S')


def write_military_time(time):
    if time == datetime.time.max:
        return '2400'
    else:
        date = datetime.datetime.now().replace(hour=time.hour, minute=time.minute)
        return datetime.datetime.strftime(date, '%H%M')


def parse_type_code(value):
    return TypeCodes[value]


def convert_to_string(value):
    if value is None:
        return ''
    else:
        return str(value)
