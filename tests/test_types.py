from typing import Optional, List, Dict, Tuple, Iterable
from unittest import TestCase

from validate_it import Schema, Options


class Skill(Schema):
    level: int
    multiplier: float


class Item(Schema):
    title: str


class Player(Schema):
    name: str

    items: List[Item]

    skills: Dict[str, Skill]


class TypesTestCase(TestCase):
    def test_required(self):
        class A(Schema):
            _int: int
            _float: float
            _bool: bool
            _str: str
            _dict: dict
            _list: list

        with self.assertRaises(TypeError):
            A.from_dict({})

        _data = {
            '_int': 1,
            '_float': 1.0,
            '_bool': True,
            '_str': 'str',
            '_dict': dict(),
            '_list': list()
        }

        assert A.from_dict(_data).to_dict() == _data

    def test_required_default(self):
        class A(Schema):
            _int: int = Options(default=1)
            _float: float = Options(default=1.0)
            _bool: bool = Options(default=True)
            _str: str = Options(default="x")
            _dict: dict = Options(default={"x": 1})
            _list: List[int] = Options(default=[1, 2])

        _data = {
            '_int': 1,
            '_float': 1.0,
            '_bool': True,
            '_str': 'x',
            '_dict': {'x': 1},
            '_list': [1, 2]
        }

        self.assertEqual(A.from_dict({}).to_dict(), _data)

    def test_required_default_callable(self):
        class A(Schema):
            _int: int = Options(default=lambda: 1)
            _float: float = Options(default=lambda: 1.0)
            _bool: bool = Options(default=lambda: True)
            _str: str = Options(default=lambda: "x")
            _dict: dict = Options(default=lambda: {"x": 1})
            _list: list = Options(default=lambda: [1, 2])

        _data = {
            '_int': 1,
            '_float': 1.0,
            '_bool': True,
            '_str': 'x',
            '_dict': {'x': 1},
            '_list': [1, 2]
        }

        self.assertEqual(A.from_dict({}).to_dict(), _data)

    def test_not_required(self):
        class A(Schema):
            _optional: Optional[int]
            _required: int

        _data = {
            "_required": 1
        }

        self.assertEqual(A.from_dict(_data).to_dict(), _data)

        _data = {
            "_required": 1,
            "_optional": 1
        }

        self.assertEqual(A.from_dict(_data).to_dict(), _data)

        _data = {}

        with self.assertRaises(TypeError):
            A.from_dict(_data)

    def test_not_required_default(self):
        class A(Schema):
            _optional: Optional[int] = 0
            _optional_with_options: Optional[int] = Options(default=1)
            _required: int = 0

        _data = {
            "_required": 0,
            "_optional": 0,
            "_optional_with_options": 1
        }

        self.assertEqual(A.from_dict(_data).to_dict(), _data)

    def test_not_required_default_callable(self):
        class A(Schema):
            _optional: Optional[int] = lambda: 0
            _optional_with_options: Optional[int] = Options(default=lambda: 0)
            _required: int = lambda: 0

        _data = {
            "_required": 0,
            "_optional": 0,
            "_optional_with_options": 1
        }

        self.assertEqual(A.from_dict(_data).to_dict(), _data)

    def empty(self):
        class A(Schema):
            _optional: Optional[int]
            _required: int

        _data = {
            "_required": 0,
            "_optional": None
        }

        _expected = {
            "_required": 0
        }

        self.assertEqual(A.from_dict(_data).to_dict(), _expected)

    def test_allowed(self):
        class A(Schema):
            a: int = Options(allowed=[1, 2])

        with self.assertRaises(ValueError):
            A(a=3)

        A(a=1)

    def test_allowed_callable(self):
        class A(Schema):
            a: int = Options(allowed=lambda: [1, 2])

        with self.assertRaises(ValueError):
            A(a=3)

        A(a=1)

    def test_amount(self):
        class A(Schema):
            a: int = Options(min_value=10)
            b: int = Options(max_value=20)

        A.from_dict({'a': 10, 'b': 20})

        with self.assertRaises(ValueError):
            A.from_dict({'a': 9, 'b': 20})

        with self.assertRaises(ValueError):
            A.from_dict({'a': 10, 'b': 21})

    def test_length(self):
        class A(Schema):
            a: str = Options(min_length=2)
            b: str = Options(max_length=5)

        A.from_dict({'a': '12', 'b': '12345'})

        with self.assertRaises(ValueError):
            A.from_dict({'a': '1', 'b': '12345'})

        with self.assertRaises(ValueError):
            A.from_dict({'a': '12', 'b': '123456'})

    def test_convert(self):
        class A(Schema):
            a: str = Options(parser=str)

        self.assertEqual(A.from_dict({'a': 1}).to_dict(), {'a': '1'})

    def test_nested_validation_and_members_access(self):
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

    def test_not_specified(self):
        class A(Schema):
            a: list
            b: dict

        with self.assertRaises(TypeError):
            A.from_dict({'a': {1: 1}, 'b': {1: 1}})

        with self.assertRaises(TypeError):
            A.from_dict({'a': [1, 1], 'b': [1, 1]})

        self.assertEqual(
            A.from_dict({'a': [1, 1], 'b': {1: 1}}).to_dict(),
            {
                'a': [1, 1],
                'b': {1: 1}
            }
        )

    def test_tuple(self):
        class A(Schema):
            a: tuple
            b: Tuple[int, int, float]

        with self.assertRaises(TypeError):
            A.from_dict({"a": [1, 2, 3], 'b': {1, 2, 3.0}})

        with self.assertRaises(TypeError):
            A.from_dict({"a": {1, 2, 3}, 'b': {1, 2, 3}})

    def test_iterable(self):
        class A(Schema):
            a: Iterable

        with self.assertRaises(TypeError):
            A.from_dict({'a': 1})

        self.assertEqual(
            A.from_dict({'a': 'abc'}).to_dict(),
            {'a': 'abc'}
        )

        self.assertEqual(
            A.from_dict({'a': [1, 2, 3]}).to_dict(),
            {'a': [1, 2, 3]}
        )

        self.assertEqual(
            A.from_dict({'a': {1: 1, 2: 2}}).to_dict(),
            {'a': {1: 1, 2: 2}}
        )
