# dual core i5 7 gen
from timeit import timeit
from typing import Union

from benchmarks.config import NUMBER
from validate_it import schema, Options, pack_value


try:
    from dataclasses import dataclass


    @dataclass
    class A:
        a: int


    @dataclass
    class B:
        b: float


    @dataclass
    class C:
        c: Union[A, B] = Options(auto_pack=True, packer=pack_value)


    @schema
    @dataclass
    class E:
        a: int


    @schema
    @dataclass
    class F:
        b: float


    @schema
    @dataclass
    class G:
        c: Union[E, F] = Options(auto_pack=True, packer=pack_value)


    def test_dataclass():
        a = {'a': 1}
        C(c=a)


    def test_dataclass_schema():
        a = {'a': 1}
        G(c=a)

    print("nested union dataclass         ", timeit("test()", globals={"test": test_dataclass}, number=NUMBER))
    print("nested union dataclass + schema", timeit("test()", globals={"test": test_dataclass_schema}, number=NUMBER))

except ImportError:
    pass


@schema
class H:
    a: int


@schema
class I:
    b: float


@schema
class J:
    c: Union[H, I] = Options(auto_pack=True, packer=pack_value)


def test_schema():
    a = {'a': 1}
    J(c=a)


print("nested union schema            ", timeit("test()", globals={"test": test_schema}, number=NUMBER))
