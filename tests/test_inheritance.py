from unittest import TestCase

from validate_it import Schema, Options


class TestInheritance(TestCase):
    def test_inheritance(self):
        class A(Schema):
            a: int

        class B(Schema):
            b: int = Options(default=1)
            
        class C(A, B):
            c: str

        class D(C):
            d: str
            
        example = D(a=1, c="c", d="1")
        
        assert example.to_dict() == {"a": 1, "b": 1, "c": "c", "d": "1"}

