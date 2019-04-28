import re
from unittest import TestCase

from validate_it import Schema, Options


class IsNotEmailError(Exception):
    pass


def is_email(value):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise IsNotEmailError()


class TypeWithValidator(Schema):
    email: str = Options(validators=[is_email])


class TestValidators(TestCase):
    def test_validators(self):
        with self.assertRaises(IsNotEmailError):
            TypeWithValidator(email="notEmail")

        TypeWithValidator(email="it@is.email")
