from unittest import TestCase
from validate_it import *
from accordion import compress, expand


class TestMapping(TestCase):
    def test_simple_mapping(self):

        class CustomMapper(Schema):
            first_name = StrField(alias="f")
            last_name = StrField(alias="l")

        _in_data = {
            "f": "John",
            "l": "Connor"
        }

        _errors, _out_data = CustomMapper().validate_it(_in_data, strip_unknown=True)

        assert _out_data == {"first_name": "John", "last_name": "Connor"}

    def test_nested_mapping(self):
        class CustomMapper(Schema):
            nickname = StrField(alias="info.nickname")
            int = IntField(alias="characteristics/0")
            dex = IntField(alias="characteristics/1")
            str = IntField(alias="characteristics/2")
            vit = IntField(alias="characteristics/3")

        _in_data = {
            "info": {
                "nickname": "Killer777",
            },
            "characteristics": [
                7,
                55,
                11,
                44
            ]
        }

        _errors, _out_data = CustomMapper().validate_it(compress(_in_data), strip_unknown=True)

        assert _out_data == {"nickname": "Killer777", "int": 7, "dex": 55, "str": 11, "vit": 44}

    def test_back_nested_mapping(self):
        class CustomMapper(Schema):
            nickname = StrField(rename="info.nickname")
            int = IntField(rename="characteristics/0")
            dex = IntField(rename="characteristics/1")
            str = IntField(rename="characteristics/2")
            vit = IntField(rename="characteristics/3")

        _in_data = {
            "nickname": "Killer777",
            "int": 7,
            "dex": 55,
            "str": 11,
            "vit": 44
        }

        _errors, _out_data = CustomMapper().validate_it(_in_data, strip_unknown=True)

        assert expand(_out_data) == {
            "info": {
                "nickname": "Killer777",
            },
            "characteristics": [
                7,
                55,
                11,
                44
            ]
        }
