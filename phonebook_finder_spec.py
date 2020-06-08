import unittest
from unittest.mock import patch

from phonebook.main import (
    phone,
    separate_line,
    PhoneBookExtractor,
    PhoneBookObject,
    PhoneBookCleanser
)


class RequireTestCase(unittest.TestCase):
    dr = "/+1-541-754-3010 156 Alphand_St. <J Steeve>\n 133, Green, Rd. <E Kustur> NY-56423 ;+1-541-914-3010\n" \
         + "+1-541-984-3012 <P Reed> /PO Box 530; Pollocksville, NC-28573\n :+1-321-512-2222 <Paul Dive> Sequoia " \
           "Alley PQ-67209\n" \
         + "+1-741-984-3090 <Peter Reedgrave> _Chicago\n :+1-921-333-2222 <Anna Stevens> Haramburu_Street AA-67209\n" \
         + "+1-111-544-8973 <Peter Pan> LA\n +1-921-512-2222 <Wilfrid Stevens> Wild Street AA-67209\n" \
         + "<Peter Gone> LA ?+1-121-544-8974 \n <R Steell> Quora Street AB-47209 +1-481-512-2222\n" \
         + "<Arthur Clarke> San Antonio $+1-121-504-8974 TT-45120\n <Ray Chandler> Teliman Pk. !+1-681-512-2222! " \
           "AB-47209,\n" \
         + "<Sophia Loren> +1-421-674-8974 Bern TP-46017\n <Peter O'Brien> High Street +1-908-512-2222; CC-47209\n" \
         + "<Anastasia> +48-421-674-8974 Via Quirinal Roma\n <P Salinger> Main Street, +1-098-512-2222, Denver\n" \
         + "<C Powel> *+19-421-674-8974 Chateau des Fosses Strasbourg F-68000\n <Bernard Deltheil> +1-498-512-2222; " \
           "Mount Av. Eldorado\n" \
         + "+1-099-500-8000 <Peter Crush> Labrador Bd.\n +1-931-512-4855 <William Saurin> Bison Street CQ-23071\n" \
         + "<P Salinge> Main Street, +1-098-512-2222, Denve\n"

    def test_tc_001(self):
        self.assertEqual(
            phone(self.dr, "48-421-674-8974"),
            "Phone => 48-421-674-8974, Name => Anastasia, Address => Via Quirinal Roma"
        )

    def test_tc_002(self):
        self.assertEqual(
            phone(self.dr, "1-921-512-2222"),
            "Phone => 1-921-512-2222, Name => Wilfrid Stevens, Address => Wild Street AA-67209"
        )

    def test_tc_003(self):
        self.assertEqual(
            phone(self.dr, "1-908-512-2222"),
            "Phone => 1-908-512-2222, Name => Peter O'Brien, Address => High Street CC-47209"
        )

    def test_tc_004(self):
        self.assertEqual(
            phone(self.dr, "1-541-754-3010"),
            "Phone => 1-541-754-3010, Name => J Steeve, Address => 156 Alphand St."
        )

    def test_tc_005(self):
        self.assertEqual(
            phone(self.dr, "1-121-504-8974"),
            "Phone => 1-121-504-8974, Name => Arthur Clarke, Address => San Antonio TT-45120"
        )

    def test_tc_006(self):
        self.assertEqual(
            phone(self.dr, "1-498-512-2222"),
            "Phone => 1-498-512-2222, Name => Bernard Deltheil, Address => Mount Av. Eldorado"
        )

    def test_tc_007(self):
        self.assertEqual(
            phone(self.dr, "1-098-512-2222"),
            "Error => Too many people: 1-098-512-2222"
        )

    def test_tc_008(self):
        self.assertEqual(
            phone(self.dr, "5-555-555-5555"),
            "Error => Not found: 5-555-555-5555"
        )


class LineSeparateTestCase(unittest.TestCase):
    def test_string_should_split_by_line_feed(self):
        self.assertEqual(separate_line("A\nB"), ["A", "B"])

    def test_string_should_split_by_line_feed_with_multiple_linefeed_contiguously(self):
        self.assertEqual(separate_line("A\n\nB"), ["A", "B"])


# PhoneBookExtractor test cases
class GetRawPhoneNumberTestCase(unittest.TestCase):
    def test_get_phone_number_from_phonebook_line(self):
        self.assertEqual(PhoneBookExtractor.get_raw_phone_number("+1-111-544-8973 <Peter Pan> LA"), "+1-111-544-8973")

    def test_get_phone_number_from_phonebook_line_with_2_digit_prefix(self):
        self.assertEqual(PhoneBookExtractor.get_raw_phone_number("+12-111-544-8973 <Peter Pan> LA"), "+12-111-544-8973")

    def test_get_phone_number_from_phonebook_line_with_no_phone_num(self):
        self.assertEqual(PhoneBookExtractor.get_raw_phone_number("+1x2-1x1-5x4-8xx3 <Peter Pan> LA"), "")

    def test_get_phone_number_from_phonebook_line_with_incorrect_prefix(self):
        self.assertEqual(PhoneBookExtractor.get_raw_phone_number("-12-111-544-8973 <Peter Pan> LA"), "")


class GetRawPersonTestCase(unittest.TestCase):
    def test_get_person_from_phonebook_line(self):
        self.assertEqual(PhoneBookExtractor.get_raw_person_name("+1-111-544-8973 <Peter Pan> LA"), "<Peter Pan>")

    def test_get_person_from_phonebook_line__with_person_come_first(self):
        self.assertEqual(PhoneBookExtractor.get_raw_person_name("<R Steell> Quora Street AB-47209 +1-481-512-2222"),
                         "<R Steell>")

    def test_should_not_get_person_from_phonebook_line__with_unmatch_pattern(self):
        self.assertEqual(PhoneBookExtractor.get_raw_person_name(">R Steell< Quora Street AB-47209 +1-481-512-2222"), "")


class ExtractRawAddressTestCase(unittest.TestCase):
    def test_extract_raw_address(self):
        self.assertEqual(
            PhoneBookExtractor.extract_raw_address("+1-111-544-8973 <Peter Pan> LA", "+1-111-544-8973", "<Peter Pan>"),
            "  LA"
        )


class GetPhonebookDictTestCase(unittest.TestCase):

    @patch.object(PhoneBookExtractor, "extract_raw_address")
    @patch.object(PhoneBookExtractor, "get_raw_person_name")
    @patch.object(PhoneBookExtractor, "get_raw_phone_number")
    def test_extract_phoneline(self, mock_phone_no, mock_person, mock_address):
        mock_phone_no.return_value = "MYPHONE"
        mock_person.return_value = "MYPERSON"
        mock_address.return_value = "MYADDRESS"

        expected_result = PhoneBookObject("MYPERSON", "MYPHONE", "MYADDRESS")
        self.assertEqual(
            PhoneBookExtractor.extract("+1-111-544-8973 <Peter Pan> LA"),
            expected_result
        )


# PhoneBookObject test cases
class PhoneBookObjectTestCase(unittest.TestCase):
    class MockCleanser(PhoneBookCleanser):
        @staticmethod
        def cleanse_person_name(person_name: str):
            return "CLEAN_PERSON_NAME"

        @staticmethod
        def cleanse_address(address: str):
            return "CLEAN_ADDRESS"

        @staticmethod
        def cleanse_phone_number(phone_num: str):
            return "CLEAN_PHONE_NO"

    def test_clease_attribute(self):
        my_phonebook_obj = PhoneBookObject("a", "b", "c")
        my_phonebook_obj.cleanse(self.MockCleanser)
        self.assertEqual(my_phonebook_obj.PhoneNumber, "CLEAN_PHONE_NO")
        self.assertEqual(my_phonebook_obj.Person, "CLEAN_PERSON_NAME")
        self.assertEqual(my_phonebook_obj.Address, "CLEAN_ADDRESS")


# PhoneBookCleanser test cases
class PhoneBookCleanserTestCase(unittest.TestCase):
    def test_cleanse_phone_number(self):
        self.assertEqual(PhoneBookCleanser.cleanse_phone_number("+11-111-111-1111"), "11-111-111-1111")

    def test_cleanse_address(self):
        self.assertEqual(PhoneBookCleanser.cleanse_address(" !@# THIS IS MY HOMETOWN"), "THIS IS MY HOMETOWN")

    def test_cleanse_address_with_redundant_space_infix(self):
        self.assertEqual(PhoneBookCleanser.cleanse_address(" !@# THIS IS MY__HOMETOWN"), "THIS IS MY HOMETOWN")

    def test_cleanse_address_with_hyphens_in_address(self):
        self.assertEqual(PhoneBookCleanser.cleanse_address(" !@# THIS IS MY-HOMETOWN"), "THIS IS MY-HOMETOWN")

    def test_cleanse_person_name(self):
        self.assertEqual(PhoneBookCleanser.cleanse_person_name("<Person Name>"), "Person Name")


if __name__ == '__main__':
    unittest.main()
