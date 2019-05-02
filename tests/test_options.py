from typing import Optional, List
from unittest import TestCase

from validate_it import Schema, Options


class Example(Schema):
    a = 0
    b: int = 0
    c: int
    d: Optional[List]
    e: Optional[int] = 1
    f: int = Options(rename='g')


class TestAnnotations(TestCase):
    def test_annotations(self):
        assert sorted(list(Example.__annotations__.keys())) == ['b', 'c', 'd', 'e', 'f']

    def test_options(self):
        assert sorted(list(Example._get_options().keys())) == ['a', 'b', 'c', 'd', 'e', 'f']
