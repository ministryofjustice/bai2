from collections import OrderedDict

from .constants import GroupStatus, AsOfDateModifier, FundsType
from .exceptions import ParsingException, NotSupportedYetException, \
    IntegrityException
from .models import \
    Bai2File, Bai2FileHeader, Bai2FileTrailer, \
    Group, GroupHeader, GroupTrailer, \
    AccountIdentifier, AccountTrailer, Account, \
    TransactionDetail, Summary
from .utils import parse_date, parse_time, parse_type_code


# ABSTRACTION

class BaseParser:
    model = None
    child_parser_class = None

    def __init__(self, iterator, check_integrity=True):
        """
        Keyword arguments:
        check_integrity -- checks the data integrity of the parsed file (default True)
        """
        super().__init__()
        self._iter = iterator
        self.check_integrity = check_integrity

        self.child_parser = self._get_parser('child')

    def _check_record_code(self, expected_code):
        if self._iter.current_record.code != expected_code:
            raise ParsingException(
                'Expected {expected}, got {found} instead'.format(
                    expected=expected_code,
                    found=self._iter.current_record.code
                )
            )

    def _get_parser(self, parser_type):
        name = '{name}_parser_class'.format(name=parser_type.lower())
        parser_clazz = getattr(self, name)
        if parser_clazz:
            return parser_clazz(
                self._iter,
                check_integrity=self.check_integrity,
            )
        return None

    def validate(self, obj):
        pass

    def can_parse(self):
        raise NotImplementedError()

    def parse(self):
        raise NotImplementedError()


class BaseSectionParser(BaseParser):
    header_parser_class = None
    trailer_parser_class = None

    def __init__(self, iterator, **kwargs):
        super().__init__(iterator, **kwargs)

        self.header_parser = self._get_parser('header')
        self.trailer_parser = self._get_parser('trailer')

    def _parse_header(self):
        return self.header_parser.parse()

    def _parse_trailer(self):
        return self.trailer_parser.parse()

    def _parse_children(self):
        if not self.child_parser:
            return []

        children = []
        while self.child_parser.can_parse():
            children.append(self.child_parser.parse())

        return children

    def can_parse(self):
        return \
            self.header_parser.can_parse() or \
            self.trailer_parser.can_parse() or \
            (self.child_parser and self.child_parser.can_parse())

    def validate_number_of_records(self, obj):
        if self.check_integrity:
            number_of_records = len(obj.header.rows) + len(obj.trailer.rows)
            for child in obj.children:
                number_of_records += len(child.rows)

            if number_of_records != obj.trailer.number_of_records:
                raise IntegrityException(
                    'Invalid number of records for {clazz}. '
                    'expected {expected}, found {found}'.format(
                        clazz=obj.__class__.__name__,
                        expected=obj.trailer.number_of_records,
                        found=number_of_records
                    )
                )

    def validate(self, obj):
        super().validate(obj)

        self.validate_number_of_records(obj)

    def parse(self):
        header = self._parse_header()
        children = self._parse_children()
        trailer = self._parse_trailer()

        obj = self.build_model(header, children, trailer)

        self.validate(obj)

        return obj

    def build_model(self, header, children, trailer):
        return self.model(header, trailer, children)


class BaseSingleParser(BaseParser):
    fields_config = {}

    def can_parse(self):
        try:
            self._check_record_code(self.model.code)
        except ParsingException:
            return False
        return True

    def _parse_field_from_config(self, field_config, raw_value):
        if isinstance(field_config, str):
            field_config = (field_config, lambda x: x)

        field_name, parser = field_config

        # Integer check
        if parser == int and 'total' in field_name:
            field_value = parser(raw_value) if raw_value else 0
        else:
            field_value = parser(raw_value) if raw_value else None
        return field_name, field_value

    def _parse_fields_from_config(self, values, fields_config):
        fields = {}

        index = 0
        for field_config in fields_config:
            field_name, field_value = self._parse_field_from_config(
                field_config, values[index]
            )
            fields[field_name] = field_value
            index += 1
        return fields

    def _parse_fields(self, record):
        return self._parse_fields_from_config(
            record.fields, self.fields_config
        )

    def _parse_availability(self, funds_type, rest):
        availability = None
        if funds_type == FundsType.distributed_availability_simple:
            availability = OrderedDict()
            for day in ['0', '1', '>1']:
                availability[day] = int(rest.pop(0))
        elif funds_type == FundsType.value_dated:
            date = rest.pop(0)
            time = rest.pop(0)
            availability = OrderedDict()
            availability['date'] = parse_date(date) if date else None
            availability['time'] = parse_time(time) if time else None
        elif funds_type == FundsType.distributed_availability:
            num_distributions = int(rest.pop(0))
            availability = OrderedDict()
            for _ in range(num_distributions):
                day = rest.pop(0)
                amount = int(rest.pop(0))
                availability[day] = amount

        return availability, rest

    def parse(self):
        self._check_record_code(self.model.code)
        obj = self.model(
            self._iter.current_record.rows,
            **self._parse_fields(self._iter.current_record)
        )

        self.validate(obj)

        try:
            self._iter.advance()
        except StopIteration:
            pass

        return obj


# IMPLEMENTATION

class TransactionDetailParser(BaseSingleParser):
    model = TransactionDetail

    head_fields_config = [
        ('type_code', parse_type_code),
        ('amount', int),
        ('funds_type', FundsType),
    ]

    tail_fields_config = [
        'bank_reference',
        'customer_reference',
        'text',
    ]

    def _parse_fields(self, record):
        # fields at the start
        rest = record.fields
        fields = self._parse_fields_from_config(
            rest[:len(self.head_fields_config)],
            self.head_fields_config
        )

        rest = rest[len(self.head_fields_config):]
        # availability fields:
        availability, rest = self._parse_availability(
            fields['funds_type'], rest
        )
        fields['availability'] = availability

        # fields at the end
        fields.update(
            self._parse_fields_from_config(
                rest[:2] + [','.join(rest[2:])],
                self.tail_fields_config
            )
        )

        return fields


class AccountIdentifierParser(BaseSingleParser):
    model = AccountIdentifier

    common_fields_config = [
        'customer_account_number',
        'currency',
    ]
    summary_fields_config = [
        ('type_code', parse_type_code),
        ('amount', int),
        ('item_count', int),
        ('funds_type', FundsType),
    ]

    def _parse_fields(self, record):
        model_fields = self._parse_fields_from_config(
            record.fields[:len(self.common_fields_config)],
            self.common_fields_config
        )

        summary_items = []
        rest = record.fields[len(self.common_fields_config):]
        while rest:
            # there's currently a bug in some exports so we need to ignore
            # the last empty item if it's the only one left.
            if len(rest) == 1 and not rest[0]:
                break

            summary = self._parse_fields_from_config(
                rest, self.summary_fields_config
            )
            rest = rest[len(self.summary_fields_config):]
            availability, rest = self._parse_availability(
                summary['funds_type'], rest
            )
            if availability:
                summary['availability'] = availability
            summary_items.append(Summary(**summary))
        model_fields['summary_items'] = summary_items

        return model_fields


class AccountTrailerParser(BaseSingleParser):
    model = AccountTrailer

    fields_config = [
        ('account_control_total', int),
        ('number_of_records', int),
    ]


class AccountParser(BaseSectionParser):
    model = Account
    header_parser_class = AccountIdentifierParser
    trailer_parser_class = AccountTrailerParser
    child_parser_class = TransactionDetailParser

    def validate(self, obj):
        super().validate(obj)

        if self.check_integrity:
            transaction_sum = sum([child.amount or 0 for child in obj.children])
            account_sum = sum([summary.amount or 0 for summary in obj.header.summary_items])

            control_total = transaction_sum + account_sum
            if control_total != obj.trailer.account_control_total:
                raise IntegrityException(
                    'Invalid account control total for {clazz}. '
                    'expected {expected}, found {found}'.format(
                        clazz=obj.__class__.__name__,
                        expected=obj.trailer.account_control_total,
                        found=control_total
                    )
                )


class GroupHeaderParser(BaseSingleParser):
    model = GroupHeader

    fields_config = [
        'ultimate_receiver_id',
        'originator_id',
        ('group_status', GroupStatus),
        ('as_of_date', parse_date),
        ('as_of_time', parse_time),
        'currency',
        ('as_of_date_modifier', AsOfDateModifier),
    ]

    def _parse_fields(self, record):
        fields = super()._parse_fields(record)

        # if currency not defined => default to USD
        if not fields['currency']:
            fields['currency'] = 'USD'

        return fields


class GroupTrailerParser(BaseSingleParser):
    model = GroupTrailer

    fields_config = [
        ('group_control_total', int),
        ('number_of_accounts', int),
        ('number_of_records', int),
    ]


class GroupParser(BaseSectionParser):
    model = Group
    header_parser_class = GroupHeaderParser
    trailer_parser_class = GroupTrailerParser
    child_parser_class = AccountParser

    def validate(self, obj):
        super().validate(obj)

        if not obj.children:
            raise ParsingException('Group without accounts not allowed')

        if self.check_integrity:
            if obj.trailer.number_of_accounts != len(obj.children):
                raise IntegrityException(
                    'Invalid number of accounts for {clazz}. '
                    'expected {expected}, found {found}'.format(
                        clazz=obj.__class__.__name__,
                        expected=obj.trailer.number_of_accounts,
                        found=len(obj.children)
                    )
                )

            control_total = sum([
                account.trailer.account_control_total
                for account in obj.children
            ])

            if control_total != obj.trailer.group_control_total:
                raise IntegrityException(
                    'Invalid group control total for {clazz}. '
                    'expected {expected}, found {found}'.format(
                        clazz=obj.__class__.__name__,
                        expected=obj.trailer.group_control_total,
                        found=control_total
                    )
                )


class Bai2FileHeaderParser(BaseSingleParser):
    model = Bai2FileHeader

    fields_config = (
        'sender_id',
        'receiver_id',
        ('creation_date', parse_date),
        ('creation_time', parse_time),
        'file_id',
        ('physical_record_length', int),
        ('block_size', int),
        ('version_number', int),
    )

    def validate(self, obj):
        super().validate(obj)

        if obj.version_number != 2:
            raise NotSupportedYetException(
                'Only BAI version 2 supported'
            )


class Bai2FileTrailerParser(BaseSingleParser):
    model = Bai2FileTrailer

    fields_config = (
        ('file_control_total', int),
        ('number_of_groups', int),
        ('number_of_records', int),
    )


class Bai2FileParser(BaseSectionParser):
    model = Bai2File
    header_parser_class = Bai2FileHeaderParser
    trailer_parser_class = Bai2FileTrailerParser
    child_parser_class = GroupParser

    def validate(self, obj):
        super().validate(obj)

        if not obj.children:
            raise ParsingException('File without groups not allowed')

        if self.check_integrity:
            if obj.trailer.number_of_groups != len(obj.children):
                raise IntegrityException(
                    'Invalid number of groups for {clazz}. '
                    'expected {expected}, found {found}'.format(
                        clazz=obj.__class__.__name__,
                        expected=obj.trailer.number_of_groups,
                        found=len(obj.children)
                    )
                )

            control_total = sum([
                account.trailer.group_control_total
                for account in obj.children
            ])

            if control_total != obj.trailer.file_control_total:
                raise IntegrityException(
                    'Invalid file control total for {clazz}. '
                    'expected {expected}, found {found}'.format(
                        clazz=obj.__class__.__name__,
                        expected=obj.trailer.file_control_total,
                        found=control_total
                    )
                )
