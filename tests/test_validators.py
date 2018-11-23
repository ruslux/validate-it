import re
from unittest import TestCase

from validate_it import StrField


def is_email(value, **kwargs):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        return "Invalid email", value

    return "", value


class TestValidators(TestCase):
    def test_validators(self):
        _error, _value = StrField(required=True, validators=[is_email]).validate_it("notEmail")

        assert _error
        self.assertEquals("Invalid email", _error)
