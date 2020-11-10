from collections import OrderedDict
from datetime import date, time
from unittest import TestCase

from bai2 import models, writers, constants


class TransactionDetailWriterTestCase(TestCase):
    def test_transaction_detail_with_no_availability_renders_correctly(self):
        transaction = models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=2599,
            text='BILLS',
        )

        output = writers.TransactionDetailWriter(transaction).write()
        self.assertEqual(output, ['16,399,2599,,,,BILLS'])

    def test_transaction_detail_with_unknown_availability_renders_correctly(self):
        transaction = models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=2599,
            funds_type=constants.FundsType.unknown_availability,
            text='BILLS',
        )

        output = writers.TransactionDetailWriter(transaction).write()
        self.assertEqual(output, ['16,399,2599,Z,,,BILLS'])

    def test_transaction_detail_with_text_on_new_line_renders_correctly(self):
        transaction = models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=2599,
            text='BILLS',
        )

        output = writers.TransactionDetailWriter(
            transaction, text_on_new_line=True
        ).write()
        self.assertEqual(output, ['16,399,2599,,,/', '88,BILLS'])

    def test_transaction_detail_with_immediate_availability_renders_correctly(self):
        transaction = models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=2599,
            funds_type=constants.FundsType.immediate_availability,
            text='BILLS',
        )

        output = writers.TransactionDetailWriter(transaction).write()
        self.assertEqual(output, ['16,399,2599,0,,,BILLS'])

    def test_transaction_detail_with_distributed_availability_simple_renders_correctly(self):
        transaction = models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=2599,
            funds_type=constants.FundsType.distributed_availability_simple,
            availability=OrderedDict([('0', 500), ('1', 599), ('>1', 2599)]),
            text='BILLS',
        )

        output = writers.TransactionDetailWriter(transaction).write()
        self.assertEqual(output, ['16,399,2599,S,500,599,2599,,,BILLS'])

    def test_transaction_detail_with_value_dated_availability_renders_correctly(self):
        transaction = models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=2599,
            funds_type=constants.FundsType.value_dated,
            availability=OrderedDict([('date', date(year=2015, month=10, day=1)),
                                      ('time', None)]),
            text='BILLS',
        )

        output = writers.TransactionDetailWriter(transaction).write()
        self.assertEqual(output, ['16,399,2599,V,151001,,,,BILLS'])

    def test_transaction_detail_with_distributed_availability_renders_correctly(self):
        transaction = models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=2599,
            funds_type=constants.FundsType.distributed_availability,
            availability=OrderedDict([('1', 500), ('2', 599), ('4', 2599)]),
            text='BILLS'
        )

        output = writers.TransactionDetailWriter(transaction).write()
        self.assertEqual(output, ['16,399,2599,D,3,1,500,2,599,4,2599,,,BILLS'])

    def test_transaction_detail_with_continuation_renders_correctly(self):
        transaction = models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=2599,
            text='BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
        )

        output = writers.TransactionDetailWriter(transaction).write()
        self.assertEqual(
            output,
            ['16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
             '88, BILLS'])


class AccountIdentifierWriterTestCase(TestCase):
    def test_account_identifier_renders_correctly(self):
        account_identifier = models.AccountIdentifier(
            customer_account_number='77777777',
            currency='GBP',
            summary_items=[
                models.Summary(type_code=constants.TypeCodes['010'], amount=10000),
                models.Summary(type_code=constants.TypeCodes['015'], amount=10000),
            ]
        )

        output = writers.AccountIdentifierWriter(account_identifier).write()
        self.assertEqual(
            output,
            ['03,77777777,GBP,010,10000,,,015,10000,,/']
        )

    def test_account_identifier_with_continuation_renders_correctly(self):
        account_identifier = models.AccountIdentifier(
            customer_account_number='77777777',
            currency='GBP',
            summary_items=[
                models.Summary(type_code=constants.TypeCodes['010'],
                               amount=10000),
                models.Summary(type_code=constants.TypeCodes['015'],
                               amount=10000),
                models.Summary(type_code=constants.TypeCodes['045'],
                               amount=10000),
                models.Summary(type_code=constants.TypeCodes['040'],
                               amount=10000),
                models.Summary(type_code=constants.TypeCodes['072'],
                               amount=10000),
                models.Summary(type_code=constants.TypeCodes['074'],
                               amount=10000),
                models.Summary(type_code=constants.TypeCodes['075'],
                               amount=10000),
                models.Summary(type_code=constants.TypeCodes['400'],
                               amount=10000, item_count=175),
                models.Summary(type_code=constants.TypeCodes['100'],
                               amount=10000, item_count=50),
            ]
        )

        output = writers.AccountIdentifierWriter(account_identifier).write()
        self.assertEqual(
            output,
            ['03,77777777,GBP,010,10000,,,015,10000,,,045,10000,,,040,10000,,,072,10000,,/',
             '88,074,10000,,,075,10000,,,400,10000,175,,100,10000,50,/']
        )

    def test_account_identifier_with_summary_availability_renders_correctly(self):
        account_identifier = models.AccountIdentifier(
            customer_account_number='77777777',
            currency='GBP',
            summary_items=[
                models.Summary(
                    type_code=constants.TypeCodes['010'],
                    amount=10000,
                    funds_type=constants.FundsType.distributed_availability_simple,
                    availability=OrderedDict([('0', 100), ('1', 200), ('>1', 300)])
                ),
                models.Summary(
                    type_code=constants.TypeCodes['015'],
                    amount=10000,
                    funds_type=constants.FundsType.distributed_availability_simple,
                    availability=OrderedDict([('0', 100), ('1', 200), ('>1', 300)])
                )
            ]
        )

        output = writers.AccountIdentifierWriter(account_identifier).write()
        self.assertEqual(
            output,
            ['03,77777777,GBP,010,10000,,S,100,200,300,015,10000,,S,100,200,300/']
        )


class AccountTrailerWriterTestCase(TestCase):
    def test_account_trailer_renders_correctly(self):
        account_trailer = models.AccountTrailer(
            account_control_total=100,
            number_of_records=4
        )

        output = writers.AccountTrailerWriter(account_trailer).write()
        self.assertEqual(
            output,
            ['49,100,4/']
        )


class GroupHeaderWriterTestTcase(TestCase):
    def test_group_header_renders_correctly(self):
        group_header = models.GroupHeader(
            ultimate_receiver_id='8888888',
            originator_id='CITIGB00',
            group_status=constants.GroupStatus.update,
            as_of_date=date(year=2015, month=7, day=15),
            as_of_time=time(hour=23, minute=40),
            currency='GBP',
            as_of_date_modifier=constants.AsOfDateModifier.final_previous_day
        )

        output = writers.GroupHeaderWriter(group_header).write()
        self.assertEqual(
            output,
            ['02,8888888,CITIGB00,1,150715,2340,GBP,2/']
        )


class GroupTrailerWriterTestCase(TestCase):
    def test_account_trailer_renders_correctly(self):
        group_trailer = models.GroupTrailer(
            group_control_total=100,
            number_of_accounts=1,
            number_of_records=6
        )

        output = writers.GroupTrailerWriter(group_trailer).write()
        self.assertEqual(
            output,
            ['98,100,1,6/']
        )


class Bai2FileHeaderWriterTestCase(TestCase):
    def test_file_header_renders_correctly(self):
        file_header = models.Bai2FileHeader(
            sender_id='CITIDIRECT',
            receiver_id='8888888',
            creation_date=date(year=2015, month=7, day=15),
            creation_time=time(hour=23, minute=40),
            file_id='00131100',
            physical_record_length=None,
            block_size=None,
            version_number=2
        )

        output = writers.Bai2FileHeaderWriter(file_header).write()
        self.assertEqual(
            output,
            ['01,CITIDIRECT,8888888,150715,2340,00131100,,,2/']
        )


class Bai2FileTrailerWriterTestCase(TestCase):
    def test_file_trailer_renders_correctly(self):
        file_trailer = models.Bai2FileTrailer(
            file_control_total=100,
            number_of_groups=1,
            number_of_records=8
        )

        output = writers.Bai2FileTrailerWriter(file_trailer).write()
        self.assertEqual(
            output,
            ['99,100,1,8/']
        )


class AccountWriterTestCase(TestCase):
    @staticmethod
    def create_account_section():
        transactions = []
        transactions.append(models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=2599,
            text='BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
        ))
        transactions.append(models.TransactionDetail(
            type_code=constants.TypeCodes['399'],
            amount=1000,
            funds_type=constants.FundsType.immediate_availability,
            text='OTHER',
        ))

        account_identifier = models.AccountIdentifier(
            customer_account_number='77777777',
            currency='GBP',
            summary_items=[
                models.Summary(type_code=constants.TypeCodes['010'], amount=10000),
                models.Summary(type_code=constants.TypeCodes['015'], amount=10000),
            ]
        )

        return models.Account(header=account_identifier, children=transactions)

    def test_account_renders_correctly(self):
        account = AccountWriterTestCase.create_account_section()

        output = writers.AccountWriter(account).write()
        self.assertEqual(
            output,
            [
                '03,77777777,GBP,010,10000,,,015,10000,,/',
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
                '88, BILLS',
                '16,399,1000,0,,,OTHER',
                '49,23599,5/',
            ]
        )


class GroupWriterTestCase(TestCase):
    @staticmethod
    def create_group_section():
        accounts = []
        accounts.append(AccountWriterTestCase.create_account_section())
        accounts.append(AccountWriterTestCase.create_account_section())

        group_header = models.GroupHeader(
            ultimate_receiver_id='8888888',
            originator_id='CITIGB00',
            group_status=constants.GroupStatus.update,
            as_of_date=date(year=2015, month=7, day=15),
            as_of_time=time(hour=23, minute=40),
            currency='GBP',
            as_of_date_modifier=constants.AsOfDateModifier.final_previous_day
        )

        return models.Group(header=group_header, children=accounts)

    def test_group_renders_correctly(self):
        group = GroupWriterTestCase.create_group_section()

        output = writers.GroupWriter(group).write()
        self.assertEqual(
            output,
            [
                '02,8888888,CITIGB00,1,150715,2340,GBP,2/',
                '03,77777777,GBP,010,10000,,,015,10000,,/',
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
                '88, BILLS',
                '16,399,1000,0,,,OTHER',
                '49,23599,5/',
                '03,77777777,GBP,010,10000,,,015,10000,,/',
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
                '88, BILLS',
                '16,399,1000,0,,,OTHER',
                '49,23599,5/',
                '98,47198,2,12/',
            ]
        )


class Bai2FileWriterTestCase(TestCase):
    @staticmethod
    def create_bai2_file():
        groups = []
        groups.append(GroupWriterTestCase.create_group_section())
        groups.append(GroupWriterTestCase.create_group_section())

        file_header = models.Bai2FileHeader(
            sender_id='CITIDIRECT',
            receiver_id='8888888',
            creation_date=date(year=2015, month=7, day=15),
            creation_time=time(hour=23, minute=40),
            file_id='00131100',
            physical_record_length=None,
            block_size=None,
            version_number=2
        )

        return models.Bai2File(header=file_header, children=groups)

    def test_bai2_file_renders_correctly(self):
        bai2_file = Bai2FileWriterTestCase.create_bai2_file()

        output = writers.Bai2FileWriter(bai2_file).write()
        self.assertEqual(
            output,
            [
                '01,CITIDIRECT,8888888,150715,2340,00131100,,,2/',
                '02,8888888,CITIGB00,1,150715,2340,GBP,2/',
                '03,77777777,GBP,010,10000,,,015,10000,,/',
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
                '88, BILLS',
                '16,399,1000,0,,,OTHER',
                '49,23599,5/',
                '03,77777777,GBP,010,10000,,,015,10000,,/',
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
                '88, BILLS',
                '16,399,1000,0,,,OTHER',
                '49,23599,5/',
                '98,47198,2,12/',
                '02,8888888,CITIGB00,1,150715,2340,GBP,2/',
                '03,77777777,GBP,010,10000,,,015,10000,,/',
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
                '88, BILLS',
                '16,399,1000,0,,,OTHER',
                '49,23599,5/',
                '03,77777777,GBP,010,10000,,,015,10000,,/',
                '16,399,2599,,,,BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS BILLS',
                '88, BILLS',
                '16,399,1000,0,,,OTHER',
                '49,23599,5/',
                '98,47198,2,12/',
                '99,94396,2,26/',
            ]
        )
