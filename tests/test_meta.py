from unittest import TestCase

from validate_it import Schema, IntField


class MetaException(BaseException):
    pass


def raise_if_value(value, meta):
    if value:
        raise meta.exception(value)


def raise_if_not_value(value, meta):
    if not value:
        raise meta.exception(value)


class CheckOnly(Schema):
    value = IntField(only=raise_if_value)

    class Meta:
        exception = MetaException


class CheckDefault(Schema):
    value = IntField(default=raise_if_not_value)

    class Meta:
        exception = MetaException


class TestMetaConfig(TestCase):
    def test_meta(self):
        with self.assertRaises(MetaException):
            CheckOnly().validate_it({'value': 1})

        with self.assertRaises(MetaException):
            CheckDefault().validate_it({})
