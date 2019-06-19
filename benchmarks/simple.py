# dual core i5 7 gen
from timeit import timeit

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


    print("simple dataclass         ", timeit("test()", globals={"test": test_dataclass}, number=100000))
    print("simple dataclass + schema", timeit("test()", globals={"test": test_dataclass_schema}, number=100000))

except ImportError:
    pass


@schema
class C:
    a: int


def test_schema():
    C(a=1)


print("simple schema            ", timeit("test()", globals={"test": test_schema}, number=100000))
