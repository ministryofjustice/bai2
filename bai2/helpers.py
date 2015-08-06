from .models import Record
from .constants import RecordCode
from .exceptions import ParsingException


class IteratorHelper(object):

    def __init__(self, lines):
        self._records = self._build_records(lines)
        self.index = 0

    def _build_records(self, lines):
        rows = [
            (RecordCode(line[:2]), line[3:]) for line in lines
        ]

        i = 0
        records = []

        finished_parsing = False
        while not finished_parsing:
            sub_rows = []
            stop = False
            while not stop:
                sub_rows.append(rows[i])
                i += 1  # 1 step down
                next_code = rows[i][0] if i < len(lines) else None

                finished_parsing = not next_code
                stop = next_code != RecordCode.continuation

            records.append(
                self._build_record(sub_rows)
            )

        return records

    def _build_record(self, rows):
        code = rows[0][0]
        fields_str = ''
        for index, row in enumerate(rows):
            field_str = row[1]
            if field_str[-1] == '/':
                field_str = field_str[:-1] + (',' if len(rows) > 1 else '')
            else:
                field_str += (' ' if index < len(rows)-1 else '')
            fields_str += field_str

        fields = fields_str.split(',')
        return Record(code=code, fields=fields, rows=rows)

    @property
    def current_record(self):
        try:
            return self._records[self.index]
        except IndexError:
            raise ParsingException('Unexpected EOF')

    def advance(self):
        self.index += 1
