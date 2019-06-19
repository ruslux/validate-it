from time import time
from typing import List, Dict, Union
from unittest import TestCase

from validate_it import Options, schema, to_dict, ValidationError

try:
    from dataclasses import dataclass

    @schema
    @dataclass
    class SkillA:
        level: int
        multiplier: float


    @schema
    @dataclass
    class ItemA:
        title: str


    @schema
    @dataclass
    class PlayerA:
        name: str

        items: List[ItemA]

        skills: Dict[str, SkillA]


    @schema
    @dataclass
    class SkillB:
        level: int
        multiplier: float


    @schema
    @dataclass
    class ItemB:
        title: str


    @schema
    @dataclass
    class PlayerB:
        name: str = Options(default="")

        items: List[ItemB] = Options(default=list)

        skills: Dict[str, SkillB] = Options(default=dict)


    @schema
    class A:
        a: str = Options(default="a")
        b: str = Options(default="b")


    @schema
    @dataclass
    class B:
        a: int = Options(alias="_a")
        b: int = Options(alias="_b")


    @schema
    @dataclass
    class Nested:
        nested: int


    @schema
    @dataclass
    class NestedA:
        a: int
        nested: Nested


    @schema
    @dataclass
    class NestedB:
        b: float


    @schema
    @dataclass
    class NestedC:
        c: Union[NestedA, NestedB]

except ImportError:
    pass


class DataclassTestCase(TestCase):
    def test_dataclass(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

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

        p = PlayerA(
            name="John",
            items=[
                ItemA(title="Rose"),
            ],
            skills={
                "fire": SkillA(level=1, multiplier=2.0),
                "ice": SkillA(level=2, multiplier=3.0),
            }
        )

        self.assertEqual(to_dict(p), _data)
        self.assertEqual(p.name, "John")
        self.assertEqual(p.items[0].title, "Rose")
        self.assertEqual(p.skills["ice"].level, 2)

        self.assertEqual(to_dict(p), _data)

    def test_dataclass_with_options(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        _data = {
            "name": "John",
            "items": None,
            "skills": None
        }

        PlayerB()
        PlayerB(
            name="John"
        )
        PlayerB(
            name="John"
        )

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

        p = PlayerB(
            name="John",
            items=[
                ItemB(title="Rose"),
            ],
            skills={
                "fire": SkillB(level=1, multiplier=2.0),
                "ice": SkillB(level=2, multiplier=3.0),
            }
        )

        self.assertEqual(to_dict(p), _data)
        self.assertEqual(p.name, "John")
        self.assertEqual(p.items[0].title, "Rose")
        self.assertEqual(p.skills["ice"].level, 2)

        self.assertEqual(to_dict(p), _data)

    def test_missing_arguments(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        A(a="c")

    def test_map(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        B(_a=1, _b=2)

    def test_union(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        NestedC(
            c=NestedA(
                a=1,
                nested=Nested(
                    nested=2
                )
            )
        )
        NestedC(
            c=NestedB(
                b=0.1
            )
        )

        with self.assertRaises(ValidationError):
            NestedC(
                c=NestedA(
                    a=0.1
                )
            )
