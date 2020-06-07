import re
def get_phone_number(phone_line: str):
    phone_regex = re.compile(r"([0-9]{1,2}-[0-9]{3}-[0-9]{3}-[0-9]{4})")
    return phone_regex.search(phone_line)

def separate_line(raw_str: str):
    return [i for i in raw_str.split("\n") if i]

def phone(phonebook_raw: str, phonenum: str):
    return