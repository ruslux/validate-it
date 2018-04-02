import re
from unittest import TestCase

from validate_it import StrField


def is_email(value, convert, strip_unknown):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        return False, "Invalid email", value

    return True, '', value


class TestValidators(TestCase):
    def test_validators(self):
        _is_valid, _error, _value = StrField(required=True, validators=[is_email]).is_valid("notEmail")

        self.assertEquals(False, _is_valid)
        self.assertEquals("Invalid email", _error)
