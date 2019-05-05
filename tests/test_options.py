import warnings
from typing import Optional, List
from unittest import TestCase

from validate_it import Schema, Options


class Example(Schema):
    a = 0
    b: int = 0
    c: int
    d: Optional[List]
    e: Optional[int] = 1
    f: int = Options(rename="g")


class TestAnnotations(TestCase):
    def test_annotations(self):
        assert sorted(list(Example.__annotations__.keys())) == ["b", "c", "d", "e", "f"]

    def test_warning(self):
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter('always')

            class A(Schema):
                pass

            self.assertTrue(any(item.category == RuntimeWarning for item in warning_list))

    def test_options(self):
        assert sorted(list(Example.__options__.keys())) == ["a", "b", "c", "d", "e", "f"]
