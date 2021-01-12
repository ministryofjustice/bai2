from .models import Record
from .constants import RecordCode


def _build_record(rows):
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
