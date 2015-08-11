import datetime

from .constants import TypeCodes


def parse_date(value):
    """
    YYMMDD Format.
    """
    return datetime.datetime.strptime(value, "%y%m%d").date()


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
    if value == '9999':
        value = '2400'

    # 2400 indicates end of the day but 24:00 not allowed so
    # it's really 23:59
    if value == '2400':
        value = '2359'
    return datetime.datetime.strptime(value, "%H%M").time()


def parse_type_code(value):
    return TypeCodes[value]
