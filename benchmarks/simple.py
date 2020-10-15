from timeit import timeit

from benchmarks.config import NUMBER
from validate_it import schema

try:
    from dataclasses import dataclass

    def test_dataclass():
        A(a=1)


    def test_dataclass_schema():
        B(a=1)


    @dataclass
    class A:
        a: int

    @schema
    @dataclass
    class B:
        a: int


    print("simple dataclass         ", timeit("test()", globals={"test": test_dataclass}, number=NUMBER))
    print("simple dataclass + schema", timeit("test()", globals={"test": test_dataclass_schema}, number=NUMBER))

except ImportError:
    pass


@schema
class C:
    a: int


def test_schema():
    C(a=1)


print("simple schema            ", timeit("test()", globals={"test": test_schema}, number=NUMBER))
