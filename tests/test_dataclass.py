
from typing import List, Dict
from unittest import TestCase

from validate_it import Options, schema, to_dict


class DataclassTestCase(TestCase):
    def test_dataclass(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        @schema
        @dataclass
        class Skill:
            level: int
            multiplier: float

        @schema
        @dataclass
        class Item:
            title: str

        @schema
        @dataclass
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
                    "multiplier": 2.0,
                },
                "ice": {
                    "level": 2,
                    "multiplier": 3.0,
                }
            }
        }

        p = Player(**_data)

        self.assertEqual(to_dict(p), _data)
        self.assertEqual(p.name, "John")
        self.assertEqual(p.items[0].title, "Rose")
        self.assertEqual(p.skills["ice"].level, 2)

        p = Player(**_data)
        self.assertEqual(to_dict(p), _data)

    def test_dataclass_with_options(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        @schema
        @dataclass
        class Skill:
            level: int
            multiplier: float

        @schema
        @dataclass
        class Item:
            title: str

        @schema
        @dataclass
        class Player:
            name: str

            items: List[Item] = Options(default=list)

            skills: Dict[str, Skill] = Options(default=dict)

        _data = {
            "name": "John",
            "items": None,
            "skills": None
        }

        to_dict(Player(**_data))
        to_dict(Player(**_data))

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

        p = Player(**_data)

        self.assertEqual(to_dict(p), _data)
        self.assertEqual(p.name, "John")
        self.assertEqual(p.items[0].title, "Rose")
        self.assertEqual(p.skills["ice"].level, 2)

        p = Player(**_data)
        self.assertEqual(to_dict(p), _data)

    def test_missing_arguments(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        @schema
        class A:
            a: str = Options(default="a")
            b: str = Options(default="b")

        A(a="c")

        @schema
        @dataclass
        class A:
            a: str = Options(default="a")
            b: str = Options(default="b")

        A(a="c")

    def test_map(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        @schema
        @dataclass
        class A:
            a: int = Options(alias="_a")
            b: int = Options(alias="_b")

        A(_a=1, _b=2)
