from unittest import TestCase

from validate_it import Schema, IntField, StrField


class First(Schema):
    a = IntField()
    b = IntField()


Second = First().only_fields('a')
Third = First().exclude_fields('a')


class Fourth(Schema):
    a = StrField()


class TestComplex(TestCase):
    def test_clone_only(self):
        _data = {
            'a': 1,
            'b': 2
        }

        _is_valid, _error, _validated = First().is_valid(_data)

        self.assertEquals(True, _is_valid)
        self.assertEquals({}, _error)
        self.assertEquals(_data, _validated)

        _is_valid, _error, _validated = Second().is_valid(_data, strip_unknown=True)

        self.assertEquals(True, _is_valid)
        self.assertEquals({}, _error)
        self.assertEquals({'a': 1}, _validated)

        _is_valid, _error, _validated = Third().is_valid(_data, strip_unknown=True)

        self.assertEquals(True, _is_valid)
        self.assertEquals({}, _error)
        self.assertEquals({'b': 2}, _validated)

        _is_valid, _error, _validated = Fourth().is_valid(_data, convert=True, strip_unknown=True)

        self.assertEquals(True, _is_valid)
        self.assertEquals({}, _error)
        self.assertEquals({'a': '1'}, _validated)
