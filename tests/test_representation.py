from unittest import TestCase

from validate_it import *


class TestClone(TestCase):
    def test_representation(self):
        _field = IntField(required=True, min_value=1, max_value=10, only=lambda: [1, 2])
        assert _field.representation() == {
            'base_type': 'int', 'required': True, 'min_value': 1, 'max_value': 10, 'extended_type': 'IntField',
            'only': {'example': [1, 2], 'type': 'callable', 'callable': _field._only},
        }

        assert FloatField(only=[0.1, 0.2], min_value=0.1, max_value=0.2).representation() == {
            'base_type': 'float', 'only': [0.1, 0.2], 'required': False, 'min_value': 0.1, 'max_value': 0.2,
            'extended_type': 'FloatField'
        }

        assert BoolField(default=True).representation() == {
            'base_type': 'bool', 'default': True, 'required': False, 'extended_type': 'BoolField'
        }

        _field = StrField(default=lambda: 'a', min_length=1, max_length=2)

        assert _field.representation() == {
            'base_type': 'str', 'default': {'example': 'a', 'type': 'callable', 'callable': _field._default},
            'required': False, 'min_length': 1, 'max_length': 2, 'extended_type': 'StrField',
        }

        assert ListField(children_field=AnyType(), min_length=1, max_length=19).representation() == {
            'base_type': 'list', 'required': False, 'children_field': {
                'base_type': 'object', 'extended_type': 'AnyType', 'required': False
            }, 'min_length': 1, 'max_length': 19, 'extended_type': 'ListField'
        }

        assert TupleField(elements=[IntField(), FloatField()]).representation() == {
            'base_type': 'tuple', 'required': False, 'elements': [
                {'base_type': 'int', 'required': False, 'extended_type': 'IntField'},
                {'base_type': 'float', 'required': False, 'extended_type': 'FloatField'}
            ], 'extended_type': 'TupleField'
        }

        assert DictField(children_field=AnyType()).representation() == {
            'base_type': 'dict', 'children_field': {
                'base_type': 'object', 'extended_type': 'AnyType', 'required': False
            }, 'required': False, 'extended_type': 'DictField'
        }

        class SomeSchema(Schema):
            a = AnyType()
            b = AnyType()

        assert SomeSchema().representation(kwargs=True) == {
            'required': True, 'base_type': 'dict', 'schema': {
                'a': {
                    'base_type': 'object', 'extended_type': 'AnyType', 'name': 'a', 'required': False, 'kwargs': True
                },
                'b': {
                    'base_type': 'object', 'extended_type': 'AnyType', 'name': 'b', 'required': False, 'kwargs': True
                }
            }, 'extended_type': 'SomeSchema', 'kwargs': True
        }

        assert UnionType(alternatives=[IntField(), FloatField()], description="one of").representation(end=True) == {
            'base_type': 'object', 'description': 'one of', 'extended_type': 'UnionType', 'end': True,
            'one of': [
                {'base_type': 'int', 'required': False, 'end': True, 'extended_type': 'IntField'},
                {'base_type': 'float', 'required': False, 'end': True, 'extended_type': 'FloatField'}
            ]
        }
