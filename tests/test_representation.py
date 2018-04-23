from unittest import TestCase

from validate_it import *


class TestClone(TestCase):
    def test_representation(self):
        assert IntField(required=True, min_value=1, max_value=10).representation() == {
            'name': 'undefined', 'base_type': 'int', 'required': True, 'min_value': 1, 'max_value': 10,
            'extended_type': 'IntField'
        }

        assert FloatField(only=[0.1, 0.2], min_value=0.1, max_value=0.2).representation() == {
            'name': 'undefined', 'base_type': 'float', 'only': [0.1, 0.2], 'required': False, 'min_value': 0.1,
            'max_value': 0.2, 'extended_type': 'FloatField'
        }

        assert BoolField(default=True).representation() == {
            'name': 'undefined', 'base_type': 'bool', 'default': True, 'required': False, 'extended_type': 'BoolField'
        }

        assert StrField(default=lambda: 'a', min_length=1, max_length=2).representation() == {
            'name': 'undefined', 'base_type': 'str', 'default': {'example': 'a', 'type': 'callable'}, 'required': False,
            'min_length': 1, 'max_length': 2, 'extended_type': 'StrField'
        }

        assert ListField(children_field=AnyType(), min_length=1, max_length=19).representation() == {
            'name': 'undefined', 'base_type': 'list', 'required': False, 'children_field': {
                'base_type': 'object', 'extended_type': 'AnyType', 'name': 'undefined', 'required': False
            }, 'min_length': 1, 'max_length': 19, 'extended_type': 'ListField'
        }

        assert TupleField(elements=[IntField(), FloatField()]).representation() == {
            'name': 'undefined', 'base_type': 'tuple', 'required': False, 'elements': [
                {'name': 'undefined', 'base_type': 'int', 'required': False, 'extended_type': 'IntField'},
                {'name': 'undefined', 'base_type': 'float', 'required': False, 'extended_type': 'FloatField'}
            ], 'extended_type': 'TupleField'
        }

        assert DictField(children_field=AnyType()).representation() == {
            'name': 'undefined', 'base_type': 'dict', 'children_field': {
                'base_type': 'object', 'extended_type': 'AnyType', 'name': 'undefined', 'required': False
            }, 'required': False, 'extended_type': 'DictField'
        }

        class SomeSchema(Schema):
            a = AnyType()
            b = AnyType()

        assert SomeSchema().representation() == {
            'name': 'undefined', 'required': True, 'base_type': 'dict', 'schema': {
                'a': {
                    'base_type': 'object', 'extended_type': 'AnyType', 'name': 'a', 'required': False
                },
                'b': {
                    'base_type': 'object', 'extended_type': 'AnyType', 'name': 'b', 'required': False
                }
            }, 'extended_type': 'SomeSchema'
        }

        assert UnionType(alternatives=[IntField(), FloatField()]).representation() == {
            'one of': [
                {'name': 'undefined', 'base_type': 'int', 'required': False, 'extended_type': 'IntField'},
                {'name': 'undefined', 'base_type': 'float', 'required': False, 'extended_type': 'FloatField'}
            ]
        }
