import inspect
from pprint import pprint
from unittest import TestCase

from validate_it import *


class TestClone(TestCase):
    def test_representation(self):
        _field = IntField(required=True, min_value=1, max_value=10, only=lambda: [1, 2])
        assert _field.representation() == {
            "base_type": "int",
            "required": True,
            "min_value": 1,
            "max_value": 10,
            "extended_type": "IntField",
            "only": {"example": [1, 2], "type": "callable", "callable": _field.only},
        }

        assert FloatField(only=[0.1, 0.2], min_value=0.1, max_value=0.2).representation() == {
            "base_type": "float",
            "only": [0.1, 0.2],
            "required": False,
            "min_value": 0.1,
            "max_value": 0.2,
            "extended_type": "FloatField",
        }

        assert BoolField(default=True).representation() == {
            "base_type": "bool",
            "default": True,
            "required": False,
            "extended_type": "BoolField",
        }

        _field = StrField(default=lambda: "a", min_length=1, max_length=2)

        assert _field.representation() == {
            "base_type": "str",
            "default": {"example": "a", "type": "callable", "callable": _field.default},
            "required": False,
            "min_length": 1,
            "max_length": 2,
            "extended_type": "StrField",
        }

        assert ListField(nested=AnyType(), min_length=1, max_length=19).representation() == {
            "base_type": "list",
            "required": False,
            "nested": {"base_type": "object", "extended_type": "AnyType", "required": False},
            "min_length": 1,
            "max_length": 19,
            "extended_type": "ListField",
        }

        assert TupleField(nested=[IntField(), FloatField()]).representation() == {
            "base_type": "tuple",
            "required": False,
            "nested": [
                {"base_type": "int", "required": False, "extended_type": "IntField"},
                {"base_type": "float", "required": False, "extended_type": "FloatField"},
            ],
            "extended_type": "TupleField",
        }

        assert DictField(nested=AnyType()).representation() == {
            "base_type": "dict",
            "nested": {"base_type": "object", "extended_type": "AnyType", "required": False},
            "required": False,
            "extended_type": "DictField",
        }

        class SomeSchema(Schema):
            a = AnyType()
            b = AnyType()

        assert SomeSchema().representation(kwargs=True) == {
            "required": True,
            "base_type": "dict",
            "schema": {
                "a": {
                    "base_type": "object",
                    "extended_type": "AnyType",
                    "name": "a",
                    "required": False,
                    "kwargs": True,
                },
                "b": {
                    "base_type": "object",
                    "extended_type": "AnyType",
                    "name": "b",
                    "required": False,
                    "kwargs": True,
                },
            },
            "extended_type": "SomeSchema",
            "kwargs": True,
        }

        assert UnionType(alternatives=[IntField(), FloatField()], description="one of").representation(end=True) == {
            "base_type": "object",
            "description": "one of",
            "extended_type": "UnionType",
            "end": True,
            "one of": [
                {"base_type": "int", "required": False, "end": True, "extended_type": "IntField"},
                {"base_type": "float", "required": False, "end": True, "extended_type": "FloatField"},
            ],
            "required": False,
        }

    def test_mozilla_react_jsonschema_form(self):

        class Aspect:
            FIRE = 1
            WATER = 2
            EARTH = 3
            AIR = 4

        class Skill(Schema):
            title = StrField(min_length=3, max_length=32, required=True, jsonschema_options={"title": "Title"})
            power = FloatField(min_value=0.1, max_value=100.0, required=True, jsonschema_options={"title": "Power"})
            aspect = IntField(choices=Aspect, required=True, jsonschema_options={"title": "Aspect"})

        class Enchant(Schema):
            power = FloatField(min_value=0.1, max_value=100.0, required=True,
                               jsonschema_options={"title": "Power"})
            aspect = IntField(choices=Aspect, required=True, jsonschema_options={"title": "Aspect"})

        class PlayerItem(Schema):
            item_id = IntField(min_value=0, required=True, jsonschema_options={"title": "Item_id"})
            enchant = Enchant(required=False, jsonschema_options={"title": "Enchant"})

        class Player(Schema):
            id = IntField(min_value=0, required=True)
            _id = StrField(min_length=24, max_length=24, required=True)
            skills = ListField(nested=Skill(jsonschema_options={"title": "Skill"}),
                               min_length=4, max_length=10, required=True,
                               jsonschema_options={"title": "Skills"})
            items = ListField(nested=PlayerItem(jsonschema_options={"title": "PlayerItem"}),
                              min_length=4, max_length=20, required=True,
                              jsonschema_options={"title": "Items"})
            nickname = StrField(min_length=3, max_length=32, required=False,
                                jsonschema_options={"title": "Nickname"})
            is_active = BoolField(required=True, jsonschema_options={"title": "Is active"})

        _expected = {
            "definitions": {
                "Enchant": {
                    "type": "object",
                    "required": [
                        "power",
                        "aspect"
                    ],
                    "properties": {
                        "power": {
                            "title": "Power",
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 100.0
                        },
                        "aspect": {
                            "$ref": "#/definitions/Aspect",
                            "title": "Aspect"
                        }
                    }
                },
                "Aspect": {
                    "type": "integer",
                    "anyOf": [
                        {
                            "type": "integer",
                            "enum": [
                                1
                            ],
                            "title": "Fire"
                        },
                        {
                            "type": "integer",
                            "enum": [
                                2
                            ],
                            "title": "Water"
                        },
                        {
                            "type": "integer",
                            "enum": [
                                3
                            ],
                            "title": "Earth"
                        },
                        {
                            "type": "integer",
                            "enum": [
                                4
                            ],
                            "title": "Air"
                        }
                    ]
                },
                "PlayerItem": {
                    "type": "object",
                    "required": [
                        "item_id"
                    ],
                    "properties": {
                        "item_id": {
                            "title": "Item_id",
                            "type": "integer",
                            "minimum": 0
                        },
                        "enchant": {
                            "title": "Enchant",
                            "$ref": "#/definitions/Enchant"
                        }
                    }
                },
                "Skill": {
                    "type": "object",
                    "required": [
                        "title",
                        "power",
                        "aspect"
                    ],
                    "properties": {
                        "title": {
                            "title": "Title",
                            "type": "string",
                            "minLength": 3,
                            "maxLength": 32
                        },
                        "power": {
                            "title": "Power",
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 100.0
                        },
                        "aspect": {
                            "$ref": "#/definitions/Aspect",
                            "title": "Aspect"
                        }
                    }
                }
            },
            "title": "Player editor",
            "type": "object",
            "required": [
                "id",
                "_id",
                "skills",
                "items",
                "is_active"
            ],
            "properties": {
                "id": {
                    "title": "id",
                    "type": "integer",
                    "minimum": 0
                },
                "_id": {
                    "title": "_id",
                    "type": "string",
                    "minLength": 24,
                    "maxLength": 24
                },
                "skills": {
                    "title": "Skills",
                    "type": "array",
                    "items": {
                        "title": "Skill",
                        "$ref": "#/definitions/Skill"
                    },
                    "minItems": 4,
                    "maxItems": 10
                },
                "items": {
                    "title": "Items",
                    "type": "array",
                    "items": {
                        "title": "Item",
                        "$ref": "#/definitions/PlayerItem"
                    },
                    "minItems": 4,
                    "maxItems": 20
                },
                "nickname": {
                    "title": "Nickname",
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 32
                },
                "is_active": {
                    "title": "Is active",
                    "type": "boolean"
                }
            }
        }

        _jsonschema = Player(
            jsonschema_options={"title": "Player editor"}
        ).jsonschema(title="Player editor")

        self.maxDiff = None
        self.assertEqual(
            _expected["definitions"],
            _jsonschema["definitions"]
        )
