# dual core i5 7 gen
from timeit import timeit
from typing import List

from benchmarks.config import NUMBER
from validate_it import schema

try:
    from dataclasses import dataclass

    @dataclass
    class A:
        a: List[int]


    @schema
    @dataclass
    class B:
        a: List[int]


    def test_dataclass():
        A(a=[1] * 10)


    def test_dataclass_schema():
        B(a=[1] * 10)


    print("list dataclass         ", timeit("test()", globals={"test": test_dataclass}, number=NUMBER))
    print("list dataclass + schema", timeit("test()", globals={"test": test_dataclass_schema}, number=NUMBER))

except ImportError:
    pass


@schema
class C:
    a: List[int]


def test_schema():
    C(a=[1] * 10)


print("list schema            ", timeit("test()", globals={"test": test_schema}, number=NUMBER))
