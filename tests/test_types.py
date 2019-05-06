from typing import Optional, List, Dict, Tuple
from unittest import TestCase

from validate_it import Options, schema, to_dict, ValidationError


@schema
class Skill:
    level: int
    multiplier: float


@schema
class Item:
    title: str


@schema
class Player:
    name: str

    items: List[Item]

    skills: Dict[str, Skill]


class TypesTestCase(TestCase):
    def test_required(self):
        @schema
        class A:
            _int: int
            _float: float
            _bool: bool
            _str: str
            _dict: dict
            _list: list

        with self.assertRaises(ValidationError):
            A()

        _data = {
            "_int": 1,
            "_float": 1.0,
            "_bool": True,
            "_str": "str",
            "_dict": dict(),
            "_list": list()
        }

        assert to_dict(A(**_data)) == _data

    def test_required_default(self):
        @schema
        class A:
            _int: int = Options(default=1)
            _float: float = Options(default=1.0)
            _bool: bool = Options(default=True)
            _str: str = Options(default="x")
            _dict: dict = Options(default={"x": 1})
            _list: List[int] = Options(default=[1, 2])

        _data = {
            "_int": 1,
            "_float": 1.0,
            "_bool": True,
            "_str": "x",
            "_dict": {"x": 1},
            "_list": [1, 2]
        }

        self.assertEqual(to_dict(A()), _data)

    def test_required_default_callable(self):
        @schema
        class A:
            _int: int = Options(default=lambda: 1)
            _float: float = Options(default=lambda: 1.0)
            _bool: bool = Options(default=lambda: True)
            _str: str = Options(default=lambda: "x")
            _dict: dict = Options(default=lambda: {"x": 1})
            _list: list = Options(default=lambda: [1, 2])

        _data = {
            "_int": 1,
            "_float": 1.0,
            "_bool": True,
            "_str": "x",
            "_dict": {"x": 1},
            "_list": [1, 2]
        }

        self.assertEqual(to_dict(A()), _data)

    def test_not_required(self):
        @schema
        class A:
            _optional: Optional[int]
            _required: int

        _data = {
            "_required": 1
        }

        self.assertEqual(to_dict(A(**_data)), _data)

        _data = {
            "_required": 1,
            "_optional": 1
        }

        self.assertEqual(to_dict(A(**_data)), _data)

        _data = {}

        with self.assertRaises(ValidationError):
            to_dict(A(**_data))

    def test_not_required_default(self):
        @schema
        class A:
            _optional: Optional[int] = 0
            _optional_with_options: Optional[int] = Options(default=1)
            _required: int = 0

        _data = {
            "_required": 0,
            "_optional": 0,
            "_optional_with_options": 1
        }

        self.assertEqual(to_dict(A(**_data)), _data)

    def test_not_required_default_callable(self):
        @schema
        class A:
            _optional: Optional[int] = lambda: 0
            _optional_with_options: Optional[int] = Options(default=lambda: 0)
            _required: int = lambda: 0

        _data = {
            "_required": 0,
            "_optional": 0,
            "_optional_with_options": 1
        }

        self.assertEqual(to_dict(A(**_data)), _data)

    def empty(self):
        @schema
        class A:
            _optional: Optional[int]
            _required: int

        _data = {
            "_required": 0,
            "_optional": None
        }

        _expected = {
            "_required": 0
        }

        self.assertEqual(to_dict(A(**_data)), _expected)

    def test_allowed(self):
        @schema
        class A:
            a: int = Options(allowed=[1, 2])

        with self.assertRaises(ValidationError):
            A(a=3)

        A(a=1)

    def test_allowed_callable(self):
        @schema
        class A:
            a: int = Options(allowed=lambda: [1, 2])

        with self.assertRaises(ValidationError):
            A(a=3)

        A(a=1)

    def test_amount(self):
        @schema
        class A:
            a: int = Options(min_value=10)
            b: int = Options(max_value=20)

        A(a=10, b=20)

        with self.assertRaises(ValidationError):
            to_dict(A(a=9, b=20))

        with self.assertRaises(ValidationError):
            to_dict(A(a=10, b=21))

    def test_length(self):
        @schema
        class A:
            a: str = Options(min_length=2)
            b: str = Options(max_length=5)

        A(a="12", b="12345")

        with self.assertRaises(ValidationError):
            A(a="1", b="12345")

        with self.assertRaises(ValidationError):
            A(a="12", b="123456")

    def test_convert(self):
        @schema
        class A:
            a: str = Options(parser=str)

        self.assertEqual(to_dict(A(a=1)), {"a": "1"})

    def test_nested_validation_and_members_access(self):
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

    def test_not_specified(self):
        @schema
        class A:
            a: list
            b: dict

        with self.assertRaises(ValidationError):
            A(a={1: 1}, b={1: 1})

        with self.assertRaises(ValidationError):
            A(a=[1, 1], b=[1, 1])

        self.assertEqual(
            to_dict(A(a=[1, 1], b={1: 1})),
            {
                "a": [1, 1],
                "b": {1: 1}
            }
        )

    def test_tuple(self):
        @schema
        class A:
            a: tuple
            b: Tuple[int, int, float]

        with self.assertRaises(ValidationError):
            A(a=[1, 2, 3], b={1, 2, 3.0})

        with self.assertRaises(ValidationError):
            A(a={1, 2, 3}, b={1, 2, 3})

    def test_typevar(self):
        @schema
        class A:
            a: Optional[List]
            b: Optional[List[int]]
            c: Optional[Dict]
            d: Optional[Dict[int, int]]

        data = {"a": [], "b": [1], "c": {"a": "b"}, "d": {1: 2}}

        assert to_dict(A(**data)) == data

    def test_descriptor(self):
        @schema
        class A:
            a: Optional[List]
            b: Optional[List[int]]
            c: Optional[Dict]
            d: Optional[Dict[int, int]]

        a = A(a=[], b=[1], c={"a": "b"}, d={1: 2})

        assert to_dict(a) == {"a": [], "b": [1], "c": {"a": "b"}, "d": {1: 2}}

        with self.assertRaises(ValidationError):
            a.a = {}

        a.a = [100]

        assert a.a == [100]

    def test_serializer(self):
        @schema
        class A:
            a: float = Options(parser=float, serializer=int)

        a = A(a="1.1")
        assert a.a == 1.1
        assert to_dict(a) == {"a": 1}

    def test_unexpected(self):
        @schema(strip_unknown=True)
        class A:
            a: float = Options(parser=float, serializer=int)

        a = A(a="1.1", b="1.1")
        assert a.a == 1.1
        assert to_dict(a) == {"a": 1}

        @schema
        class A:
            a: float = Options(parser=float, serializer=int)

        with self.assertRaises(ValidationError):
            A(a="1.1", b="1.1")

        @schema
        class A:
            a: float = Options(parser=float, serializer=int)

            class Meta:
                some_field = 3

        with self.assertRaises(ValidationError):
            A(a="1.1", b="1.1")
