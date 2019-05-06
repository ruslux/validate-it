from unittest import TestCase

from validate_it import Options, schema, to_dict


class TestInheritance(TestCase):
    def test_inheritance(self):
        @schema
        class A:
            a: int

        @schema
        class B:
            b: int = Options(default=1)

        @schema
        class C(A, B):
            c: str

        @schema
        class D(C):
            d: str

        example = D(a=1, c="c", d="1")
        
        assert to_dict(example) == {"a": 1, "b": 1, "c": "c", "d": "1"}
