from unittest import TestCase

from validate_it import Schema, IntField


class TestStrictTypeConfig(TestCase):
    def test_only(self):
        class A(Schema):
            a = IntField(default=lambda: 10)
            b = IntField(default=10)

        with self.assertRaises(TypeError):
            class B(Schema):
                a = IntField(default=lambda: 10, only=[1, 2])

        with self.assertRaises(ValueError):
            class C(Schema):
                a = IntField(default=10, only=[1, 2])

        def false_validator(value, convert, strip_unknown):
            return False, 'Wrong', value

        with self.assertRaises(ValueError):
            class D(Schema):
                a = IntField(only=[1, 2], validators=[false_validator])

        with self.assertRaises(ValueError):
            class E(Schema):
                a = IntField(default=1, validators=[false_validator])

        with self.assertRaises(ValueError):
            class F(Schema):
                a = IntField(default=lambda: 1, validators=[false_validator])
