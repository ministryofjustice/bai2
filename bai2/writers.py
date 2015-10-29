from collections import OrderedDict

from .models import \
    Bai2File, Bai2FileHeader, Bai2FileTrailer, \
    Group, GroupHeader, GroupTrailer, \
    AccountIdentifier, AccountTrailer, Account, \
    TransactionDetail
from .utils import write_date, write_time, convert_to_string
from .constants import CONTINUATION_CODE


class BaseWriter(object):

    def __init__(self, obj,
                 line_length=80,
                 text_on_new_line=False,
                 clock_format_for_intra_day=False):
        """
        Keyword arguments:
        line_length -- number of characters per record (default 80)
        text_on_new_line -- whether to begin a text field in a new record (default False)
        clock_format_for_intra_day -- use HH:MM:SS instead of HHMM for intra-day times (default False)
        """
        self.obj = obj
        self.line_length = line_length
        self.text_on_new_line = text_on_new_line
        self.clock_format_for_intra_day = clock_format_for_intra_day

    def write(self):
        raise NotImplementedError()


class BaseSectionWriter(BaseWriter):
    model = None
    header_writer_class = None
    child_writer_class = None
    trailer_writer_class = None

    def write(self):
        header = self.header_writer_class(self.obj.header).write()

        children = []
        for child in self.obj.children:
            children += self.child_writer_class(child).write()

        self.obj.update_totals()
        self.obj.trailer.number_of_records = len(header) + len(children) + 1
        trailer = self.trailer_writer_class(self.obj.trailer).write()

        return header + children + trailer


class BaseSingleWriter(BaseWriter):
    model = None

    def _write_field_from_config(self, field_config):
        if isinstance(field_config, str):
            field_config = (field_config, lambda w, x: x)

        field_name, write_func = field_config
        field_value = getattr(self.obj, field_name, None)
        output = write_func(self, field_value) if field_value is not None else None

        if isinstance(output, dict):
            return output
        else:
            return {field_name: convert_to_string(output)}

    def _write_fields_from_config(self, fields_config):
        fields = OrderedDict()
        for field_config in fields_config:
            fields.update(self._write_field_from_config(field_config))
        return fields

    def write(self):
        record = ''
        fields = self._write_fields_from_config(self.fields_config)

        record += self.model.code.value
        for field_name in fields:
            record += ',' + fields[field_name]
        record += '/'

        return [record]


def expand_availability(writer, availability):
    fields = OrderedDict()
    if len(availability) == 0:
        pass
    elif list(availability.keys()) in [['0', '1', '>1'], ['date', 'time']]:
        for field, value in availability.items():
            if field == 'date':
                value = write_date(value) if value else None
            elif field == 'time':
                value = (write_time(value, writer.clock_format_for_intra_day)
                         if value else None)
            fields[field] = convert_to_string(value)
    else:
        fields['distribution_length'] = str(len(availability))
        for field, value in availability.items():
            fields['day_%s' % str(field)] = convert_to_string(field)
            fields['amount_%s' % str(field)] = convert_to_string(value)
    return fields


class TransactionDetailWriter(BaseSingleWriter):
    model = TransactionDetail

    fields_config = [
        ('type_code', lambda w, tc: tc.code),
        'amount',
        ('funds_type', lambda w, ft: ft.value),
        ('availability', expand_availability),
        'bank_reference',
        'customer_reference',
        'text'
    ]

    def write(self):
        records = ['']
        fields = self._write_fields_from_config(self.fields_config)

        i = 0
        records[i] += self.model.code.value
        for field_name in fields:
            if field_name == 'text' and self.obj.text:
                text_cursor = 0
                if self.text_on_new_line:
                    records[i] += '/'
                    records.append(CONTINUATION_CODE)
                    i += 1

                while text_cursor < len(self.obj.text):
                    # -1 for comma after preceding field
                    remaining_line_length = (self.line_length - len(records[i])) - 1

                    if remaining_line_length > 0:
                        end_index = text_cursor + remaining_line_length
                        records[i] += ',' + self.obj.text[text_cursor:end_index]
                        text_cursor = end_index
                    else:
                        records.append(CONTINUATION_CODE)
                        i += 1
            else:
                records[i] += ',' + fields[field_name]

        return records


def expand_summary_items(writer, summary_items):
    items = OrderedDict()

    for n, summary_item in enumerate(summary_items):
        for summary_field_config in AccountIdentifierWriter.summary_fields_config:
            if isinstance(summary_field_config, str):
                summary_field_config = (summary_field_config, lambda w, x: x)

            summary_field_name, write_func = summary_field_config
            field_value = getattr(summary_item, summary_field_name, None)
            output = (write_func(writer, field_value)
                      if field_value is not None else None)

            if isinstance(output, dict):
                items.update(OrderedDict(
                    [('%s_%s' % (k, n), v) for k, v in output.items()]
                ))
            else:
                items['%s_%s' % (summary_field_name, n)] = convert_to_string(output)
    return items


class AccountIdentifierWriter(BaseSingleWriter):
    model = AccountIdentifier

    fields_config = [
        'customer_account_number',
        'currency',
        ('summary_items', expand_summary_items)
    ]

    summary_fields_config = [
        ('type_code', lambda w, tc: tc.code),
        'amount',
        'item_count',
        ('funds_type', lambda w, ft: ft.value),
        ('availability', expand_availability)
    ]

    def write(self):
        records = ['']
        fields = self._write_fields_from_config(self.fields_config)

        i = 0
        records[i] += self.model.code.value
        for field_name in fields:
            field_length = len(fields[field_name]) + 2
            if (len(records[i]) + field_length) >= self.line_length:
                records[i] += '/'
                records.append(CONTINUATION_CODE)
                i += 1
            records[i] += ',' + fields[field_name]
        records[i] += '/'
        return records


class AccountTrailerWriter(BaseSingleWriter):
    model = AccountTrailer

    fields_config = [
        'account_control_total',
        'number_of_records'
    ]


class AccountWriter(BaseSectionWriter):
    model = Account
    header_writer_class = AccountIdentifierWriter
    trailer_writer_class = AccountTrailerWriter
    child_writer_class = TransactionDetailWriter


class GroupHeaderWriter(BaseSingleWriter):
    model = GroupHeader

    fields_config = [
        'ultimate_receiver_id',
        'originator_id',
        ('group_status', lambda w, gs: gs.value),
        ('as_of_date', lambda w, d: write_date(d)),
        ('as_of_time', lambda w, t: write_time(t, w.clock_format_for_intra_day)),
        'currency',
        ('as_of_date_modifier', lambda w, aodm: aodm.value)
    ]


class GroupTrailerWriter(BaseSingleWriter):
    model = GroupTrailer

    fields_config = [
        'group_control_total',
        'number_of_accounts',
        'number_of_records'
    ]


class GroupWriter(BaseSectionWriter):
    model = Group
    header_writer_class = GroupHeaderWriter
    trailer_writer_class = GroupTrailerWriter
    child_writer_class = AccountWriter


class Bai2FileHeaderWriter(BaseSingleWriter):
    model = Bai2FileHeader

    fields_config = (
        'sender_id',
        'receiver_id',
        ('creation_date', lambda w, d: write_date(d)),
        ('creation_time', lambda w, t: write_time(t, w.clock_format_for_intra_day)),
        'file_id',
        'physical_record_length',
        'block_size',
        'version_number'
    )


class Bai2FileTrailerWriter(BaseSingleWriter):
    model = Bai2FileTrailer

    fields_config = (
        'file_control_total',
        'number_of_groups',
        'number_of_records',
    )


class Bai2FileWriter(BaseSectionWriter):
    model = Bai2File
    header_writer_class = Bai2FileHeaderWriter
    trailer_writer_class = Bai2FileTrailerWriter
    child_writer_class = GroupWriter
