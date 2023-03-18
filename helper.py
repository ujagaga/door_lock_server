import string
import random
from hashlib import sha256
import re
from datetime import datetime
import sys


DATE_FORMAT = "%Y-%m-%d"


def generate_token():
    return ''.join(random.choices(string.ascii_letters, k=32))


def hash_password(password: str):
    return sha256(password.encode('utf-8')).hexdigest()


def generate_random_string():
    return hash_password(generate_token())


def validate_email(email: str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        return False
    else:
        return True


def validate_password(password: str):
    if " " in password:
        # Password can not contain spaces.
        return 1
    if len(password) < 5:
        # Password can not be shorter than 5 characters.
        return 2

    return 0


def string_to_date(valid_until: str):
    result = None

    try:
        result = datetime.strptime(valid_until, DATE_FORMAT)
        # Setting to middle of the day for easier comparison.
        result = result.replace(hour=12, minute=0)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR converting string to date on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)

    return result


def date_to_string(valid_date: datetime) -> str:
    return valid_date.strftime(DATE_FORMAT)
