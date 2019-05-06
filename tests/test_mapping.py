from unittest import TestCase

from accordion import compress, expand

from validate_it import *


class TestMapping(TestCase):
    def test_simple_mapping(self):
        @schema(strip_unknown=True)
        class CustomMapper:
            first_name: str = Options(alias="f")
            last_name: str = Options(alias="l")

        _in_data = {
            "f": "John",
            "l": "Connor"
        }

        mapper = CustomMapper(**_in_data)

        assert to_dict(mapper) == {"first_name": "John", "last_name": "Connor"}

    def test_nested_mapping(self):
        @schema(strip_unknown=True)
        class CustomMapper:
            nickname: str = Options(alias="info.nickname")
            _int: int = Options(alias="characteristics/0", rename="int")
            _dex: int = Options(alias="characteristics/1", rename="dex")
            _str: int = Options(alias="characteristics/2", rename="str")
            _vit: int = Options(alias="characteristics/3", rename="vit")

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

        mapper = CustomMapper(**compress(_in_data))

        assert to_dict(mapper) == {"nickname": "Killer777", "int": 7, "dex": 55, "str": 11, "vit": 44}

    def test_back_nested_mapping(self):
        @schema(strip_unknown=True)
        class CustomMapper:
            nickname: str = Options(rename="info.nickname")
            _int: int = Options(alias="int", rename="characteristics/0")
            _dex: int = Options(alias="dex", rename="characteristics/1")
            _str: int = Options(alias="str", rename="characteristics/2")
            _vit: int = Options(alias="vit", rename="characteristics/3")

        _in_data = {
            "nickname": "Killer777",
            "int": 7,
            "dex": 55,
            "str": 11,
            "vit": 44
        }

        mapper = CustomMapper(**_in_data)

        assert expand(to_dict(mapper)) == {
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
