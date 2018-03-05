import datetime
from unittest import TestCase
from collections import OrderedDict

from bai2.helpers import IteratorHelper
from bai2.parsers import TransactionDetailParser, AccountParser, \
    GroupParser, Bai2FileParser
from bai2.constants import TypeCodes, FundsType, GroupStatus, \
    AsOfDateModifier
from bai2.models import \
    Bai2File, Bai2FileHeader, Bai2FileTrailer, \
    Group, GroupHeader, GroupTrailer, \
    Account, AccountIdentifier, AccountTrailer, \
    TransactionDetail
from bai2.exceptions import ParsingException, \
    NotSupportedYetException, IntegrityException


class TransactionDetailParserTestCase(TestCase):
    def test_parse(self):
        lines = [
            '16,165,1500000,0,DD1620,,DEALER PAYMENTS',
        ]

        ii = IteratorHelper(lines)
        parser = TransactionDetailParser(ii)

        transaction = parser.parse()

        self.assertEqual(transaction.type_code, TypeCodes['165'])
        self.assertEqual(transaction.amount, 1500000)
        self.assertEqual(transaction.funds_type, FundsType.immediate_availability)
        self.assertEqual(transaction.bank_reference, 'DD1620')
        self.assertEqual(transaction.customer_reference, None)
        self.assertEqual(
            transaction.text,
            'DEALER PAYMENTS'
        )

    def test_continuation_record(self):
        lines = [
            '16,115,10000000,S,5000000,4000000,1000000/',
            '88,AX13612,B096132,AMALGAMATED CORP. LOCKBOX',
            '88,DEPOSIT-MISC. RECEIVABLES'
        ]

        parser = TransactionDetailParser(IteratorHelper(lines))

        transaction = parser.parse()

        self.assertEqual(transaction.type_code, TypeCodes['115'])
        self.assertEqual(transaction.amount, 10000000)
        self.assertEqual(transaction.funds_type, FundsType.distributed_availability_simple)
        self.assertEqual(
            transaction.availability,
            OrderedDict([('0', 5000000), ('1', 4000000), ('>1', 1000000)])
        )
        self.assertEqual(transaction.bank_reference, 'AX13612')
        self.assertEqual(transaction.customer_reference, 'B096132')
        self.assertEqual(
            transaction.text,
            'AMALGAMATED CORP. LOCKBOX DEPOSIT-MISC. RECEIVABLES'
        )

    def test_unknown_availability(self):
        lines = [
            '16,165,1500000,Z,DD1620,,DEALER PAYMENTS',
        ]

        ii = IteratorHelper(lines)
        parser = TransactionDetailParser(ii)

        transaction = parser.parse()

        self.assertEqual(transaction.type_code, TypeCodes['165'])
        self.assertEqual(transaction.amount, 1500000)
        self.assertEqual(transaction.funds_type, FundsType.unknown_availability)
        self.assertEqual(transaction.availability, None)
        self.assertEqual(transaction.bank_reference, 'DD1620')
        self.assertEqual(transaction.customer_reference, None)
        self.assertEqual(
            transaction.text,
            'DEALER PAYMENTS'
        )

    def test_value_dated_availability(self):
        lines = [
            '16,191,001,V,150715,2340,1234567890,RP12312312312312/',
            '88,FR:FP SIP INCOMING',
            '88,ENDT:20150715',
            '88,TRID:RP12312312312312',
            '88,PY:RP1231231231231200                 A1234BC 22/03/66',
            '88,BI:22222222',
            '88,OB:111111 BUCKINGHAM PALACE OB3:BARCLAYS BANK PLC',
            '88,BO:11111111 BO1:DOE JO',
        ]

        parser = TransactionDetailParser(IteratorHelper(lines))

        transaction = parser.parse()

        self.assertEqual(transaction.funds_type, FundsType.value_dated)
        self.assertEqual(
            transaction.availability['date'],
            datetime.date(day=15, month=7, year=2015)
        )
        self.assertEqual(
            transaction.availability['time'],
            datetime.time(hour=23, minute=40)
        )

    def test_distributed_availability_simple(self):
        lines = [
            '16,191,005,S,001,003,001,1234567890,RP12312312312312/',
            '88,FR:FP SIP INCOMING',
            '88,ENDT:20150715',
            '88,TRID:RP12312312312312',
            '88,PY:RP1231231231231200                 A1234BC 22/03/66',
            '88,BI:22222222',
            '88,OB:111111 BUCKINGHAM PALACE OB3:BARCLAYS BANK PLC',
            '88,BO:11111111 BO1:DOE JO',
        ]

        parser = TransactionDetailParser(IteratorHelper(lines))

        transaction = parser.parse()

        self.assertEqual(transaction.funds_type, FundsType.distributed_availability_simple)
        self.assertEqual(transaction.amount, 5)
        self.assertEqual(
            transaction.availability,
            OrderedDict([('0', 1), ('1', 3), ('>1', 1)])
        )

    def test_distributed_availability(self):
        lines = [
            '16,191,005,D,2,1,001,2,004,1234567890,RP12312312312312/',
            '88,FR:FP SIP INCOMING',
            '88,ENDT:20150715',
            '88,TRID:RP12312312312312',
            '88,PY:RP1231231231231200                 A1234BC 22/03/66',
            '88,BI:22222222',
            '88,OB:111111 BUCKINGHAM PALACE OB3:BARCLAYS BANK PLC',
            '88,BO:11111111 BO1:DOE JO',
        ]

        parser = TransactionDetailParser(IteratorHelper(lines))

        transaction = parser.parse()

        self.assertEqual(transaction.funds_type, FundsType.distributed_availability)
        self.assertEqual(transaction.amount, 5)

        self.assertEqual(
            transaction.availability,
            OrderedDict([('1', 1), ('2', 4)])
        )


class AccountParserTestCase(TestCase):

    def test_parse(self):
        lines = [
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/'
        ]

        parser = AccountParser(IteratorHelper(lines))

        account = parser.parse()

        header = account.header
        self.assertEqual(header.customer_account_number, '0975312468')
        self.assertEqual(header.currency, 'GBP')

        trailer = account.trailer
        self.assertEqual(trailer.account_control_total, 72000000)
        self.assertEqual(trailer.number_of_records, 3)

        self.assertEqual(len(account.children), 1)

    def test_parse_without_transactions(self):
        lines = [
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '49,70500000,2/'
        ]

        parser = AccountParser(IteratorHelper(lines))

        account = parser.parse()

        self.assertEqual(len(account.children), 0)

    def test_parse_with_multiple_transactions(self):
        lines = [
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '16,115,10000000,S,5000000,4000000,1000000/',
            '88,AX13612,B096132,AMALGAMATED CORP. LOCKBOX',
            '88,DEPOSIT-MISC. RECEIVABLES',
            '49,82000000,6/'
        ]

        parser = AccountParser(IteratorHelper(lines))

        account = parser.parse()

        self.assertEqual(len(account.children), 2)

    def test_fails_without_trailer(self):
        lines = [
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
        ]

        parser = AccountParser(IteratorHelper(lines))
        self.assertRaises(ParsingException, parser.parse)

    def test_fails_integrity_on_numbers_of_records(self):
        """
        Number of records == 4 when it should be 3.
        """
        lines = [
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,4/'
        ]

        parser = AccountParser(IteratorHelper(lines))
        self.assertRaises(IntegrityException, parser.parse)

    def test_fails_integrity_on_account_control_total(self):
        """
        Account Control Total == 72000001 when it should be 72000000.
        """
        lines = [
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000001,3/'
        ]

        parser = AccountParser(IteratorHelper(lines))
        self.assertRaises(IntegrityException, parser.parse)

    def test_ignore_integrity_checks(self):
        """
        Checks that if IGNORE_INTEGRITY_CHECKS is set, integrity checks
        are not performed.
        """
        lines = [
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000001,3/'
        ]

        parser = AccountParser(IteratorHelper(lines), check_integrity=False)
        account = parser.parse()
        self.assertTrue(isinstance(account, Account))


class GroupParserTestCase(TestCase):

    def test_parse(self):
        lines = [
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000000,1,5/'
        ]

        parser = GroupParser(IteratorHelper(lines))

        group = parser.parse()

        header = group.header
        self.assertEqual(header.ultimate_receiver_id, '031001234')
        self.assertEqual(header.originator_id, '122099999')
        self.assertEqual(header.group_status, GroupStatus.update)
        self.assertEqual(header.as_of_date, datetime.date(year=2004, month=6, day=20))
        self.assertEqual(header.as_of_time, datetime.time(hour=23, minute=59))
        self.assertEqual(header.currency, 'GBP')
        self.assertEqual(header.as_of_date_modifier, AsOfDateModifier.final_previous_day)

        trailer = group.trailer
        self.assertEqual(trailer.group_control_total, 72000000)
        self.assertEqual(trailer.number_of_accounts, 1)
        self.assertEqual(trailer.number_of_records, 5)

        self.assertEqual(len(group.children), 1)

    def test_default_currency(self):
        """
        If currency field is blank in group header => default to USD
        """

        lines = [
            '02,031001234,122099999,1,040620,2359,,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000000,1,5/'
        ]

        parser = GroupParser(IteratorHelper(lines))

        group = parser.parse()

        header = group.header
        self.assertEqual(header.currency, 'USD')

    def test_multiple_accounts(self):
        lines = [
            '02,031001234,122099999,1,040620,2359,,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '03,0975312469,GBP,010,100,,/',
            '49,100,2/',
            '98,72000100,2,7/'
        ]

        parser = GroupParser(IteratorHelper(lines))

        group = parser.parse()

        trailer = group.trailer
        self.assertEqual(trailer.group_control_total, 72000100)
        self.assertEqual(trailer.number_of_accounts, 2)
        self.assertEqual(trailer.number_of_records, 7)

        self.assertEqual(len(group.children), 2)

    def test_fails_if_no_accounts_found(self):
        lines = [
            '02,031001234,122099999,1,040620,2359,,2/',
            '98,11800000,0,2/'
        ]

        parser = GroupParser(IteratorHelper(lines))
        self.assertRaises(ParsingException, parser.parse)

    def test_fails_without_trailer(self):
        lines = [
            '02,031001234,122099999,1,040620,2359,,2/',
        ]

        parser = GroupParser(IteratorHelper(lines))
        self.assertRaises(ParsingException, parser.parse)

    def test_fails_integrity_on_numbers_of_records(self):
        """
        Number of records == 6 when it should be 5.
        """
        lines = [
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000000,1,6/'
        ]

        parser = GroupParser(IteratorHelper(lines))
        self.assertRaises(IntegrityException, parser.parse)

    def test_fails_integrity_on_numbers_of_accounts(self):
        """
        Number of accounts == 4 when it should be 3.
        """
        lines = [
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,4/',
            '98,72000000,1,5/'
        ]

        parser = GroupParser(IteratorHelper(lines))
        self.assertRaises(IntegrityException, parser.parse)

    def test_fails_integrity_on_group_control_total(self):
        """
        Group Control Total == 72000001 when it should be 72000000.
        """
        lines = [
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000001,1,5/'
        ]

        parser = GroupParser(IteratorHelper(lines))
        self.assertRaises(IntegrityException, parser.parse)

    def test_ignore_integrity_checks(self):
        """
        Checks that if IGNORE_INTEGRITY_CHECKS is set, integrity checks
        are not performed.
        """
        lines = [
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000001,2,6/'
        ]

        parser = GroupParser(IteratorHelper(lines), check_integrity=False)
        group = parser.parse()
        self.assertTrue(isinstance(group, Group))


class Bai2FileParserTestCase(TestCase):

    def test_parse(self):
        lines = [
            '01,CITIDIRECT,8888888,150716,0713,00131100,,,2/',
            '02,8888888,CITIGB00,1,150715,2340,GBP,2/',
            '03,77777777,GBP,010,10000,,,015,10000,,,/',
            '16,191,001,V,150715,,1234567890,RP12312312312312/',
            '88,FR:FP SIP INCOMING',
            '88,ENDT:20150715',
            '88,TRID:RP12312312312312',
            '88,PY:RP1231231231231200                 A1234BC 22/03/66',
            '88,BI:22222222',
            '88,OB:111111 BUCKINGHAM PALACE OB3:BARCLAYS BANK PLC',
            '88,BO:11111111 BO1:DOE JO',
            '49,20001,10/',
            '98,20001,1,12/',
            '99,20001,1,14/'
        ]

        parser = Bai2FileParser(IteratorHelper(lines))
        bai2_file = parser.parse()

        july_15_2015 = datetime.date(day=15, month=7, year=2015)
        july_16_2015 = datetime.date(day=16, month=7, year=2015)

        # BAI2 file
        self.assertTrue(isinstance(bai2_file, Bai2File))

        # BAI2 file header
        bai2_header = bai2_file.header
        self.assertTrue(isinstance(bai2_header, Bai2FileHeader))
        self.assertEqual(bai2_header.sender_id, 'CITIDIRECT')
        self.assertEqual(bai2_header.receiver_id, '8888888')
        self.assertEqual(bai2_header.creation_date, july_16_2015)
        self.assertEqual(bai2_header.creation_time, datetime.time(hour=7, minute=13))
        self.assertEqual(bai2_header.file_id, '00131100')
        self.assertEqual(bai2_header.physical_record_length, None)
        self.assertEqual(bai2_header.block_size, None)
        self.assertEqual(bai2_header.version_number, 2)

        # BAI2 file trailer
        bai2_trailer = bai2_file.trailer
        self.assertTrue(isinstance(bai2_trailer, Bai2FileTrailer))
        self.assertEqual(bai2_trailer.file_control_total, 20001)
        self.assertEqual(bai2_trailer.number_of_groups, 1)
        self.assertEqual(bai2_trailer.number_of_records, 14)

        # GROUP

        self.assertEqual(len(bai2_file.children), 1)
        group = bai2_file.children[0]
        self.assertTrue(isinstance(group, Group))

        # Group Header

        group_header = group.header
        self.assertTrue(isinstance(group_header, GroupHeader))
        self.assertEqual(group_header.ultimate_receiver_id, '8888888')
        self.assertEqual(group_header.originator_id, 'CITIGB00')
        self.assertEqual(group_header.group_status, GroupStatus.update)
        self.assertEqual(group_header.as_of_date, july_15_2015)
        self.assertEqual(group_header.as_of_time, datetime.time(hour=23, minute=40))
        self.assertEqual(group_header.currency, 'GBP')
        self.assertEqual(
            group_header.as_of_date_modifier, AsOfDateModifier.final_previous_day
        )

        # Group Trailer

        group_trailer = group.trailer
        self.assertTrue(isinstance(group_trailer, GroupTrailer))
        self.assertEqual(group_trailer.group_control_total, 20001)
        self.assertEqual(group_trailer.number_of_accounts, 1)
        self.assertEqual(group_trailer.number_of_records, 12)

        # ACCOUNT

        self.assertEqual(len(group.children), 1)
        account = group.children[0]
        self.assertTrue(isinstance(account, Account))

        # Account Identifier

        account_identifier = account.header
        self.assertTrue(isinstance(account_identifier, AccountIdentifier))
        self.assertEqual(account_identifier.customer_account_number, '77777777')
        self.assertEqual(account_identifier.currency, 'GBP')

        # Account Trailer

        account_trailer = account.trailer
        self.assertTrue(isinstance(account_trailer, AccountTrailer))
        self.assertEqual(account_trailer.account_control_total, 20001)
        self.assertEqual(account_trailer.number_of_records, 10)

        # Transaction Detail

        self.assertEqual(len(account.children), 1)
        transaction = account.children[0]
        self.assertTrue(isinstance(transaction, TransactionDetail))
        self.assertEqual(transaction.type_code, TypeCodes['191'])
        self.assertEqual(transaction.amount, 1)
        self.assertEqual(transaction.funds_type, FundsType.value_dated)
        self.assertEqual(transaction.availability['date'], july_15_2015)
        self.assertEqual(transaction.availability['time'], None)
        self.assertEqual(transaction.bank_reference, '1234567890')
        self.assertEqual(transaction.customer_reference, 'RP12312312312312')
        self.assertEqual(
            transaction.text,
            'FR:FP SIP INCOMING '
            'ENDT:20150715 '
            'TRID:RP12312312312312 '
            'PY:RP1231231231231200                 A1234BC 22/03/66 '
            'BI:22222222 '
            'OB:111111 BUCKINGHAM PALACE OB3:BARCLAYS BANK PLC '
            'BO:11111111 BO1:DOE JO'
        )

    def test_only_version_2_supported(self):
        """
        Checks that BAI version 2 is supported.
        """
        lines = [
            '01,122099999,123456789,040621,0200,1,,,1/',
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,18650000,3/',
            '98,18650000,1,5/',
            '99,18650000,1,7/'
        ]

        parser = Bai2FileParser(IteratorHelper(lines))

        self.assertRaises(NotSupportedYetException, parser.parse)

    def test_multiple_groups(self):
        lines = [
            '01,122099999,123456789,040621,0200,1,,,2/',
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000000,1,5/',
            '02,031001233,122099998,1,040620,2359,GBP,2/',
            '03,0975312469,GBP,010,100,,/',
            '49,100,2/',
            '98,100,1,4/',
            '99,72000100,2,11/'
        ]

        parser = Bai2FileParser(IteratorHelper(lines))
        bai2_file = parser.parse()

        trailer = bai2_file.trailer
        self.assertEqual(trailer.file_control_total, 72000100)
        self.assertEqual(trailer.number_of_groups, 2)
        self.assertEqual(trailer.number_of_records, 11)

        self.assertEqual(len(bai2_file.children), 2)

    def test_fails_if_no_groups_found(self):
        lines = [
            '01,122099999,123456789,040621,0200,1,,,2/',
            '99,1215450000,0,2/'
        ]

        parser = Bai2FileParser(IteratorHelper(lines))
        self.assertRaises(ParsingException, parser.parse)

    def test_fails_without_trailer(self):
        lines = [
            '01,122099999,123456789,040621,0200,1,,,2/',
        ]

        parser = Bai2FileParser(IteratorHelper(lines))
        self.assertRaises(ParsingException, parser.parse)

    def test_fails_integrity_on_numbers_of_records(self):
        """
        Number of records == 8 when it should be 7.
        """
        lines = [
            '01,122099999,123456789,040621,0200,1,,,2/',
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000000,1,5/',
            '99,72000000,1,8/'
        ]

        parser = Bai2FileParser(IteratorHelper(lines))
        self.assertRaises(IntegrityException, parser.parse)

    def test_fails_integrity_on_numbers_of_groups(self):
        """
        Number of groups == 2 when it should be 1.
        """
        lines = [
            '01,122099999,123456789,040621,0200,1,,,2/',
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000000,1,5/',
            '99,72000000,2,7/'
        ]

        parser = Bai2FileParser(IteratorHelper(lines))
        self.assertRaises(IntegrityException, parser.parse)

    def test_fails_integrity_on_file_control_total(self):
        """
        File Control Total == 72000001 when it should be 72000000.
        """
        lines = [
            '01,122099999,123456789,040621,0200,1,,,2/',
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000000,1,5/',
            '99,72000001,1,7/'
        ]

        parser = Bai2FileParser(IteratorHelper(lines))
        self.assertRaises(IntegrityException, parser.parse)

    def test_ignore_integrity_checks(self):
        """
        Checks that if IGNORE_INTEGRITY_CHECKS is set, integrity checks
        are not performed.
        """
        lines = [
            '01,122099999,123456789,040621,0200,1,,,2/',
            '02,031001234,122099999,1,040620,2359,GBP,2/',
            '03,0975312468,GBP,010,500000,,,190,70000000,4,0/',
            '16,165,1500000,1,DD1620,, DEALER PAYMENTS',
            '49,72000000,3/',
            '98,72000000,1,5/',
            '99,72000001,2,8/'
        ]

        parser = Bai2FileParser(IteratorHelper(lines), check_integrity=False)
        bai2_file = parser.parse()
        self.assertTrue(isinstance(bai2_file, Bai2File))
