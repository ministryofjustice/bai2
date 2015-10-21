from .constants import RecordCode


# ABSTRACTION


class Record(object):

    def __init__(self, code, fields, rows):
        self.code = code
        self.fields = fields
        self.rows = rows


class Bai2Model(object):
    code = None

    def as_string(self):
        return '\n'.join([
            "{0},{1}".format(row[0].value, row[1])
            for row in self.rows
        ])


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

    def update_totals(self):
        pass

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

    def update_totals(self):
        file_control_total = 0
        for group in self.children:
            file_control_total += group.group_control_total

        self.trailer.file_control_total = file_control_total
        self.trailer.number_of_groups = len(self.children)


class Bai2FileHeader(Bai2SingleModel):
    code = RecordCode.file_header


class Bai2FileTrailer(Bai2SingleModel):
    code = RecordCode.file_trailer


class Group(Bai2SectionModel):

    def update_totals(self):
        group_control_total = 0
        for account in self.children:
            group_control_total += account.account_control_total

        self.trailer.group_control_total = group_control_total
        self.trailer.number_of_groups = len(self.children)


class GroupHeader(Bai2SingleModel):
    code = RecordCode.group_header


class GroupTrailer(Bai2SingleModel):
    code = RecordCode.group_trailer


class Account(Bai2SectionModel):

    def update_totals(self):
        account_control_total = 0
        for transaction in self.children:
            account_control_total += transaction.amount

        self.trailer.account_control_total = account_control_total


class AccountIdentifier(Bai2SingleModel):
    code = RecordCode.account_identifier


class AccountTrailer(Bai2SingleModel):
    code = RecordCode.account_trailer


class TransactionDetail(Bai2SingleModel):
    code = RecordCode.transaction_detail
