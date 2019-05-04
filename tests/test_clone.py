from unittest import TestCase

from validate_it import Schema, Options


class First(Schema):
    a: int = 0
    b: int = 0

    class Meta:
        strip_unknown = True


Second = First.clone(include=["a"])
Third = First.clone(exclude=["a"])
# try replace
Fourth = First.clone(add=[("a", str, Options(parser=str))])
# add
Fifth = First.clone(add=[("_id", int, Options(default=1))])


class TestClone(TestCase):
    def test_clone(self):
        data = {"a": 1, "b": 2}

        first = First(**data)
        self.assertEquals(data, first.to_dict())

        second = Second(**data)
        self.assertEquals({"a": 1}, second.to_dict())

        third = Third(**data)
        self.assertEquals({"b": 2}, third.to_dict())

        fourth = Fourth(**data)
        self.assertEquals({"a": "1", "b": 2}, fourth.to_dict())

        fifth = Fifth(**data)
        self.assertEquals({"a": 1, "b": 2, "_id": 1}, fifth.to_dict())
