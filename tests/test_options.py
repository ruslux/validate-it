from typing import Optional, List

from validate_it import Options, schema


@schema
class Example:
    a = 0
    b: int = 0
    c: int
    d: Optional[List]
    e: Optional[int] = 1
    f: int = Options(rename="g")


def test_annotations():
    assert sorted(list(Example.__annotations__.keys())) == ["b", "c", "d", "e", "f"]


def test_options():
    assert sorted(list(Example.__validate_it__options__.keys())) == ["a", "b", "c", "d", "e", "f"]
