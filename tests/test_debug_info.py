from typing import Dict, List

import pytest

from validate_it import ValidationError, schema


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


def test_debug_info():
    with pytest.raises(ValidationError) as ve:
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

    assert ve.value.args == (
        "Field `Multiplier#value`: <class 'float'> is not compatible with value `ang`:<class 'str'>",
    )
