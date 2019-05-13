from typing import List, Dict
from unittest import TestCase

from validate_it import schema, ValidationError


@schema
class Multiplier:
    value: float


@schema
class Skill:
    level: int
    multipliers: Dict[int, Multiplier]


@schema
class Item:
    title: str


@schema
class Player:
    name: str

    items: List[Item]

    skills: Dict[str, Skill]


_data = {
    "name": "John",
    "items": [
        {"title": "Rose"}
    ],
    "skills": {
        "fire": {
            "level": 1,
            "multipliers": {
                1: {"value": 1.0},
                2: {"value": 'ang'},
            },
        },
        "ice": {
            "level": 2,
            "multipliers": {
                1: {"value": 1.0},
                2: {"value": 'ang'},
            },
        }
    }
}


class DebugInfoTestCase(TestCase):
    def test_debug_info(self):

        with self.assertRaises(ValidationError) as ve:
            Player(**_data)

        assert ve.exception.args == (
            "Field `Multiplier#value`: <class 'float'> is not compatible with value `ang`:<class 'str'>",
        )
