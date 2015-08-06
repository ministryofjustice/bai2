from .constants import RecordCode


# ABSTRACTION


class Record(object):

    def __init__(self, code, fields, rows):
        self.code = code
        self.fields = fields
        self.rows = rows


class Bai2Model(object):
    code = None


class Bai2SingleModel(Bai2Model):

    def __init__(self, rows, **fields):
        self.rows = rows
        for name, value in fields.items():
            setattr(self, name, value)


class Bai2SectionModel(Bai2Model):

    def __init__(self, header, trailer, children):
        self.header = header
        self.trailer = trailer
        self.children = children

    @property
    def rows(self):
        if not hasattr(self, '_rows'):
            rows = self.header.rows
            for child in self.children:
                rows += child.rows
            rows += self.trailer.rows
            self._rows = rows
        return self._rows


# IMPLEMENTATION

class Bai2File(Bai2SectionModel):
    pass


class Bai2FileHeader(Bai2SingleModel):
    code = RecordCode.file_header


class Bai2FileTrailer(Bai2SingleModel):
    code = RecordCode.file_trailer


class Group(Bai2SectionModel):
    pass


class GroupHeader(Bai2SingleModel):
    code = RecordCode.group_header


class GroupTrailer(Bai2SingleModel):
    code = RecordCode.group_trailer


class Account(Bai2SectionModel):
    pass


class AccountIdentifier(Bai2SingleModel):
    code = RecordCode.account_identifier


class AccountTrailer(Bai2SingleModel):
    code = RecordCode.account_trailer


class TransactionDetail(Bai2SingleModel):
    code = RecordCode.transaction_detail
