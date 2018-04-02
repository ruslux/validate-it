from unittest import TestCase

from validate_it import *


class TestClone(TestCase):
    def test_representation(self):
        assert IntField(required=True, min_value=1, max_value=10).representation() == {
            'type': 'int', 'required': True, 'min_value': 1, 'max_value': 10
        }

        assert FloatField(only=[0.1, 0.2], min_value=0.1, max_value=0.2).representation() == {
            'type': 'float', 'only': [0.1, 0.2], 'required': False, 'min_value': 0.1, 'max_value': 0.2
        }

        assert BoolField(default=True).representation() == {'type': 'bool', 'default': True, 'required': False}

        assert StrField(default=lambda: 'a', min_length=1, max_length=2).representation() == {
            'type': 'str', 'default': {'example': 'a', 'type': 'callable'}, 'required': False, 'min_length': 1,
            'max_length': 2
        }

        assert ListField(children_field=AnyType(), min_length=1, max_length=19).representation() == {
            'type': 'list', 'required': False, 'children_field': 'any type', 'min_length': 1, 'max_length': 19
        }

        assert TupleField(elements=[IntField(), FloatField()]).representation() == {
            'type': 'tuple', 'required': False, 'elements': [
                {'type': 'int', 'required': False}, {'type': 'float', 'required': False}
            ]
        }

        assert DictField(children_field=AnyType()).representation() == {
            'type': 'dict', 'children_field': 'any type', 'required': False
        }

        class SomeSchema(Schema):
            a = AnyType()
            b = AnyType()

        assert SomeSchema().representation() == {
            'required': True, 'type': 'dict', 'schema': {'a': 'any type', 'b': 'any type'}
        }

        assert UnionType(alternatives=[IntField(), FloatField()]).representation() == {
            'one of': [
                {'type': 'int', 'required': False},
                {'type': 'float', 'required': False}
            ]
        }
