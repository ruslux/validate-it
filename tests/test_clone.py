from unittest import TestCase

from validate_it import schema, Options, clone, to_dict


@schema(strip_unknown=True)
class First:
    a: int = 0
    b: int = 0


class TestClone(TestCase):
    def test_clone(self):
        data = {"a": 1, "b": 2}

        # Second = clone(First, strip_unknown=True, include=["a"])
        # Third = clone(First, strip_unknown=True, exclude=["a"])
        # # try replace
        # Fourth = clone(First, strip_unknown=True, add=[("a", str, Options(parser=str))])
        # add
        Fifth = clone(First, strip_unknown=True, add=[("_id", int, Options(default=1))])
        #
        # first = First(**data)
        # self.assertEquals(data, to_dict(first))

        # second = Second(**data)
        # self.assertEquals({"a": 1}, to_dict(second))
        #
        # third = Third(**data)
        # self.assertEquals({"b": 2}, to_dict(third))
        #
        # fourth = Fourth(**data)
        # self.assertEquals({"a": "1", "b": 2}, to_dict(fourth))

        fifth = Fifth(**data)
        self.assertEquals({"a": 1, "b": 2, "_id": 1}, to_dict(fifth))
