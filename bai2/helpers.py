from .models import Record
from .constants import RecordCode


def _build_account_identifier_record(rows):
    fields_str = ''
    for index, row in enumerate(rows):
        field_str = row[1]
        commas_count = field_str.count(',')
        # first row will have account identifier and currency (the common part of the account identifier)
        # and then a multiple of 4 commas (the rest of the account identifier, which are summary components)
        # the rest of the rows will have only the summary components
        summary_commas_count = commas_count - 2 if index == 0 else commas_count

        if field_str:
            if field_str[-1] == '/':
                fields_str += field_str[:-1]
                if summary_commas_count % 4 != 0:
                    # if the number of commas is not a multiple of 4, then we need to add a comma
                    # some banks emit this extra comma, some don't, so we need to normalize it
                    fields_str += ','
            else:
                fields_str += field_str

    fields = fields_str.split(',')
    return Record(code=rows[0][0], fields=fields, rows=rows)


def _build_generic_record(rows):
    fields_str = ''
    for row in rows:
        field_str = row[1]

        if field_str:
            if field_str[-1] == '/':
                fields_str += field_str[:-1] + ','
            else:
                fields_str += field_str + ' '

    fields = fields_str[:-1].split(',')
    return Record(code=rows[0][0], fields=fields, rows=rows)


RecordBuilderFactory = {
    RecordCode.file_header: _build_generic_record,
    RecordCode.group_header: _build_generic_record,
    RecordCode.account_identifier: _build_account_identifier_record,
    RecordCode.transaction_detail: _build_generic_record,
    RecordCode.account_trailer: _build_generic_record,
    RecordCode.group_trailer: _build_generic_record,
    RecordCode.file_trailer: _build_generic_record,
}


def _build_record(rows):
    record_code = rows[0][0]
    return RecordBuilderFactory[record_code](rows)


def record_generator(lines):
    rows = iter(
        [(RecordCode(line[:2]), line[3:]) for line in lines]
    )

    records = [next(rows)]
    while True:
        try:
            row = next(rows)
        except StopIteration:
            break

        if row[0] != RecordCode.continuation:
            yield _build_record(records)
            records = [row]
        else:
            records.append(row)

    yield _build_record(records)


class IteratorHelper:
    def __init__(self, lines):
        self._generator = record_generator(lines)
        self.current_record = None
        self.advance()

    def advance(self):
        self.current_record = next(self._generator)
