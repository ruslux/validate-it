# dual core i5 7 gen
from timeit import timeit
from typing import Union

from benchmarks.config import NUMBER
from validate_it import schema

try:
    from dataclasses import dataclass

    @dataclass
    class A:
        a: Union[int, float]


    @schema
    @dataclass
    class B:
        a: Union[int, float]


    def test_dataclass():
        A(a=1.0)


    def test_dataclass_schema():
        B(a=1.0)


    print("union dataclass         ", timeit("test()", globals={"test": test_dataclass}, number=NUMBER))
    print("union dataclass + schema", timeit("test()", globals={"test": test_dataclass_schema}, number=NUMBER))


except ImportError:
    pass


@schema
class C:
    a: Union[int, float]


def test_schema():
    C(a=1.0)


print("union schema            ", timeit("test()", globals={"test": test_schema}, number=NUMBER))
