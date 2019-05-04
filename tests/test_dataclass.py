
from typing import Optional, List, Dict, Tuple
from unittest import TestCase

from validate_it import Schema, Options


class DataclassTestCase(TestCase):
    def test_dataclass(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        @dataclass
        class Skill(Schema):
            level: int
            multiplier: float

        @dataclass
        class Item(Schema):
            title: str

        @dataclass
        class Player(Schema):
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
                    "multiplier": 2.0,
                },
                "ice": {
                    "level": 2,
                    "multiplier": 3.0,
                }
            }
        }

        p = Player.from_dict(_data)

        self.assertEqual(p.to_dict(), _data)
        self.assertEqual(p.name, "John")
        self.assertEqual(p.items[0].title, "Rose")
        self.assertEqual(p.skills["ice"].level, 2)

        p = Player(**_data)
        self.assertEqual(p.to_dict(), _data)

    def test_dataclass_with_options(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        @dataclass
        class Skill(Schema):
            level: int
            multiplier: float

        @dataclass
        class Item(Schema):
            title: str

        @dataclass
        class Player(Schema):
            name: str

            items: List[Item] = Options(default=list)

            skills: Dict[str, Skill] = Options(default=dict)

        _data = {
            "name": "John",
            "items": None,
            "skills": None
        }

        Player.from_dict(_data).to_dict()
        Player.from_dict(_data).to_dict()
        Player(**_data).to_dict()

        _data = {
            "name": "John",
            "items": [
                {"title": "Rose"}
            ],
            "skills": {
                "fire": {
                    "level": 1,
                    "multiplier": 2.0,
                },
                "ice": {
                    "level": 2,
                    "multiplier": 3.0,
                }
            }
        }

        p = Player.from_dict(_data)

        self.assertEqual(p.to_dict(), _data)
        self.assertEqual(p.name, "John")
        self.assertEqual(p.items[0].title, "Rose")
        self.assertEqual(p.skills["ice"].level, 2)

        p = Player(**_data)
        self.assertEqual(p.to_dict(), _data)
