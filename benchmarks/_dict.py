# dual core i5 7 gen
from timeit import timeit
from typing import Dict, List

from benchmarks.config import NUMBER
from validate_it import schema

try:
    from dataclasses import dataclass

    @dataclass
    class A:
        a: Dict[int, int]

    @schema
    @dataclass
    class B:
        a: Dict[int, int]


    def test_dataclass():
        A(a={1: 1, 2: 2})


    def test_dataclass_schema():
        B(a={1: 1, 2: 2})

    print("dict dataclass         ", timeit("test()", globals={"test": test_dataclass}, number=NUMBER))
    print("dict dataclass + schema", timeit("test()", globals={"test": test_dataclass_schema}, number=NUMBER))
except ImportError:
    pass


@schema
class C:
    a: Dict[int, int]


def test_schema():
    C(a={1: 1, 2: 2})


print("dict schema            ", timeit("test()", globals={"test": test_schema}, number=NUMBER))
