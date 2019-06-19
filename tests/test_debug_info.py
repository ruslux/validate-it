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
            Player(
                name="John",
                items=[
                    Item(title="Rose")
                ],
                skills={
                    "fire": Skill(
                        level=1,
                        multipliers=[
                            Multiplier(value=1.0),
                            Multiplier(value="ang")
                        ]
                    ),
                    "ice": Skill(
                        level=2,
                        multipliers=[
                            Multiplier(value=1.0),
                            Multiplier(value="ang")
                        ]
                    )
                }
            )

        assert ve.exception.args == (
            "Field `Multiplier#value`: <class 'float'> is not compatible with value `ang`:<class 'str'>",
        )
