from unittest import TestCase

from validate_it import Schema, IntField, StrField


class First(Schema):
    a = IntField()
    b = IntField()


Second = First().only_fields('a')
Third = First().exclude_fields('a')


class Fourth(Schema):
    a = StrField()


class TestClone(TestCase):
    def test_clone_only(self):
        _data = {
            'a': 1,
            'b': 2
        }

        _error, _validated = First().validate_it(_data)

        assert not _error
        self.assertEquals(_data, _validated)

        _error, _validated = Second().validate_it(_data, strip_unknown=True)

        assert not _error
        self.assertEquals({'a': 1}, _validated)

        _error, _validated = Third().validate_it(_data, strip_unknown=True)

        assert not _error
        self.assertEquals({'b': 2}, _validated)

        _error, _validated = Fourth().validate_it(_data, convert=True, strip_unknown=True)

        assert not _error
        self.assertEquals({'a': '1'}, _validated)
