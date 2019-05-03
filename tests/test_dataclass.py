
from typing import Optional, List, Dict, Tuple
from unittest import TestCase

from validate_it import Schema, Options


class DataclassTestCase(TestCase):
    def test_dataclass(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        @dataclass(repr=False)
        class Skill(Schema):
            level: int
            multiplier: float

        @dataclass(repr=False)
        class Item(Schema):
            title: str

        @dataclass(repr=False)
        class Player(Schema):
            name: str

            items: List[Item]

            skills: Dict[str, Skill]

        _data = {
            'name': 'John',
            'items': [
                {'title': 'Rose'}
            ],
            'skills': {
                'fire': {
                    'level': 1,
                    'multiplier': 2.0,
                },
                'ice': {
                    'level': 2,
                    'multiplier': 3.0,
                }
            }
        }

        p = Player.from_dict(_data)

        self.assertEqual(p.to_dict(), _data)
        self.assertEqual(p.name, "John")
        self.assertEqual(p.items[0].title, "Rose")
        self.assertEqual(p.skills['ice'].level, 2)

        p = Player(**_data)
        self.assertEqual(p.to_dict(), _data)
