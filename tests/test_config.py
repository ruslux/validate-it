from dataclasses import dataclass
from unittest import TestCase

from validate_it import Schema, IntField


class Enum:
    ONE = 1
    TWO = 2


class TestStrictTypeConfig(TestCase):
    def test_only(self):

        @dataclass
        class A(Schema):
            a = IntField(enum=Enum)

        self.assertEqual(A.a.choices, ((1, 'One'), (2, 'Two')))
        self.assertEqual(A.a.only, [1, 2])

        with self.assertRaises(TypeError):
            @dataclass
            class A(Schema):
                a = IntField(enum=Enum, choices=((1, 'One'), (2, 'Two')))


        with self.assertRaises(TypeError):
            @dataclass
            class A(Schema):
                a = IntField(enum=Enum, only=[1, 2])


        with self.assertRaises(TypeError):
            @dataclass
            class A(Schema):
                a = IntField(choices=((1, 'One'), (2, 'Two')), only=[1, 2])
