from unittest import TestCase

from validate_it import Options, schema, representation


class TestClone(TestCase):
    def test_representation(self):
        @schema
        class R:
            a: int = 0
            b: str = Options(min_length=3, max_length=10)

        assert representation(R) == {
            "schema": {
                "a": {
                    "default": 0,
                    "required": True,
                    "type": "int",
                },
                "b": {
                    "min length": 3,
                    "max length": 10,
                    "required": True,
                    "type": "str"
                }
            }
        }
