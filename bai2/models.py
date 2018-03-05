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

    def __init__(self, header=None, trailer=None, children=None):
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
    def __init__(self, header=None, trailer=None, children=None):
        super(Bai2File, self).__init__(header=header or Bai2FileHeader([]),
                                       trailer=trailer or Bai2FileTrailer([]),
                                       children=children or [])

    def update_totals(self):
        file_control_total = 0
        for group in self.children:
            file_control_total += group.trailer.group_control_total

        self.trailer.file_control_total = file_control_total
        self.trailer.number_of_groups = len(self.children)


class Bai2FileHeader(Bai2SingleModel):
    code = RecordCode.file_header

    def __init__(
        self,
        rows,
        sender_id=None,
        receiver_id=None,
        creation_date=None,
        creation_time=None,
        file_id=None,
        physical_record_length=None,
        block_size=None,
        version_number=2
    ):
        super(Bai2FileHeader, self).__init__(
            rows, sender_id=sender_id, receiver_id=receiver_id,
            creation_date=creation_date, creation_time=creation_time,
            file_id=file_id, physical_record_length=physical_record_length,
            block_size=block_size, version_number=version_number
        )


class Bai2FileTrailer(Bai2SingleModel):
    code = RecordCode.file_trailer

    def __init__(
        self,
        rows,
        file_control_total=None,
        number_of_groups=None,
        number_of_records=None
    ):
        super(Bai2FileTrailer, self).__init__(
            rows, file_control_total=file_control_total,
            number_of_groups=number_of_groups, number_of_records=number_of_records
        )


class Group(Bai2SectionModel):
    def __init__(self, header=None, trailer=None, children=None):
        super(Group, self).__init__(header=header or GroupHeader([]),
                                    trailer=trailer or GroupTrailer([]),
                                    children=children or [])

    def update_totals(self):
        group_control_total = 0
        for account in self.children:
            group_control_total += account.trailer.account_control_total

        self.trailer.group_control_total = group_control_total
        self.trailer.number_of_accounts = len(self.children)


class GroupHeader(Bai2SingleModel):
    code = RecordCode.group_header

    def __init__(
        self,
        rows,
        ultimate_receiver_id=None,
        originator_id=None,
        group_status=None,
        as_of_date=None,
        as_of_time=None,
        currency=None,
        as_of_date_modifier=None
    ):
        super(GroupHeader, self).__init__(
            rows, ultimate_receiver_id=ultimate_receiver_id,
            originator_id=originator_id, group_status=group_status,
            as_of_date=as_of_date, as_of_time=as_of_time, currency=currency,
            as_of_date_modifier=as_of_date_modifier
        )


class GroupTrailer(Bai2SingleModel):
    code = RecordCode.group_trailer

    def __init__(
        self,
        rows,
        group_control_total=None,
        number_of_accounts=None,
        number_of_records=None
    ):
        super(GroupTrailer, self).__init__(
            rows, group_control_total=group_control_total,
            number_of_accounts=number_of_accounts,
            number_of_records=number_of_records
        )


class Account(Bai2SectionModel):

    def __init__(self, header=None, trailer=None, children=None):
        super(Account, self).__init__(header=header or AccountIdentifier([]),
                                      trailer=trailer or AccountTrailer([]),
                                      children=children or [])

    def update_totals(self):
        account_control_total = 0
        for transaction in self.children:
            account_control_total += transaction.amount
        for summary in self.header.summary_items:
            account_control_total += summary.amount

        self.trailer.account_control_total = account_control_total


class AccountIdentifier(Bai2SingleModel):
    code = RecordCode.account_identifier

    def __init__(
        self,
        rows,
        customer_account_number=None,
        currency=None,
        summary_items=[]
    ):
        super(AccountIdentifier, self).__init__(
            rows, customer_account_number=customer_account_number,
            currency=currency, summary_items=summary_items
        )


class Summary(object):

    def __init__(
        self,
        type_code=None,
        amount=0,
        item_count=None,
        funds_type=None,
        availability={}
    ):
        self.type_code = type_code
        self.amount = amount
        self.item_count = item_count
        self.funds_type = funds_type
        self.availability = availability


class AccountTrailer(Bai2SingleModel):
    code = RecordCode.account_trailer

    def __init__(
        self,
        rows,
        account_control_total=None,
        number_of_records=None
    ):
        super(AccountTrailer, self).__init__(
            rows, account_control_total=account_control_total,
            number_of_records=number_of_records
        )


class TransactionDetail(Bai2SingleModel):
    code = RecordCode.transaction_detail

    def __init__(
        self,
        rows,
        type_code=None,
        amount=None,
        funds_type=None,
        availability={},
        bank_reference=None,
        customer_reference=None,
        text=None
    ):
        super(TransactionDetail, self).__init__(
            rows, type_code=type_code, amount=amount, funds_type=funds_type,
            availability=availability, bank_reference=bank_reference,
            customer_reference=customer_reference, text=text
        )
