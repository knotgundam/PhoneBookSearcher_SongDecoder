import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Type, Mapping, Sequence


class PhoneBookCleanser:
    @staticmethod
    def cleanse_person_name(person_name: str) -> str:
        return person_name.replace("<", "").replace(">", "")

    @staticmethod
    def cleanse_phone_number(phone_num: str) -> str:
        return phone_num.replace("+", "")

    @staticmethod
    def cleanse_address(address: str) -> str:
        def remove_redundant_space(text: str) -> str:
            space_re = re.compile(r"( {2,})")
            return space_re.sub(" ", text)
        unwanted_special_chars = list("~!@#$%^&*()+`/\\=;_")
        for c in unwanted_special_chars:
            address = address.replace(c, " ")
        return remove_redundant_space(address.strip())


@dataclass()
class PhoneBookObject:
    Person: str
    PhoneNumber: str
    Address: str

    def cleanse(self, phonebook_cleanser: Type[PhoneBookCleanser]):
        self.Person = phonebook_cleanser.cleanse_person_name(self.Person)
        self.PhoneNumber = phonebook_cleanser.cleanse_phone_number(self.PhoneNumber)
        self.Address = phonebook_cleanser.cleanse_address(self.Address)


class PhoneBookExtractor:
    @staticmethod
    def extract_raw_address(phonebook_line: str, raw_phone_num: str, raw_person_name: str) -> str:
        return phonebook_line.replace(raw_phone_num, "").replace(raw_person_name, "")

    @staticmethod
    def get_raw_person_name(phonebook_line: str) -> str:
        person_regex = re.compile(r"<.+>")
        match_object = person_regex.search(phonebook_line)
        return match_object.group() if match_object else ""

    @staticmethod
    def get_raw_phone_number(phonebook_line: str) -> str:
        phone_regex = re.compile(r"(\+[0-9]{1,2}-[0-9]{3}-[0-9]{3}-[0-9]{4})")
        match_object = phone_regex.search(phonebook_line)
        return match_object.group() if match_object else ""

    @staticmethod
    def extract(phonebook_line) -> PhoneBookObject:
        person_name = PhoneBookExtractor.get_raw_person_name(phonebook_line)
        phone_number = PhoneBookExtractor.get_raw_phone_number(phonebook_line)
        address = PhoneBookExtractor.extract_raw_address(phonebook_line, phone_number, person_name)
        return PhoneBookObject(person_name, phone_number, address)


def separate_line(raw_str: str):
    return [i for i in raw_str.split("\n") if i]


def get_phonebook_dict(phonebook_line):
    phonebook_obj = PhoneBookExtractor.extract(phonebook_line)
    phonebook_obj.cleanse(PhoneBookCleanser)
    return phonebook_obj


def refine_phone_book(phonebook_raw: str) -> Mapping[str, Sequence[PhoneBookObject]]:
    phonebook_dicts = defaultdict(list)
    for line in separate_line(phonebook_raw):
        pb_dict = get_phonebook_dict(line)
        phonebook_dicts[pb_dict.PhoneNumber].append(pb_dict)
    return phonebook_dicts


def phone(phonebook_raw: str, phonenum: str):
    phonebook = refine_phone_book(phonebook_raw)
    search_result = phonebook.get(phonenum, [])
    if len(search_result) == 0:
        return f"Error => Not found: {phonenum}"
    elif len(search_result) > 1:
        return f"Error => Too many people: {phonenum}"
    return f"Phone => {search_result[0].PhoneNumber}, " \
           f"Name => {search_result[0].Person}, " \
           f"Address => {search_result[0].Address}"
