from validate_it import schema, Options, clone, to_dict


@schema(strip_unknown=True)
class First:
    a: int = 0
    b: int = 0


Second = clone(First, strip_unknown=True, include=["a"])
Third = clone(First, strip_unknown=True, exclude=["a"])
# Replace field definition
Fourth = clone(First, strip_unknown=True, add=[("a", str, Options(parser=str))])
# Add new field
Fifth = clone(First, strip_unknown=True, add=[("_id", int, Options(default=1))])


def test_clone():
    data = {"a": 1, "b": 2}

    first = First(**data)
    assert data == to_dict(first)

    second = Second(**data)
    assert {"a": 1} == to_dict(second)

    third = Third(**data)
    assert {"b": 2} == to_dict(third)

    fourth = Fourth(**data)
    assert {"a": "1", "b": 2} == to_dict(fourth)

    fifth = Fifth(**data)
    assert {"a": 1, "b": 2, "_id": 1} == to_dict(fifth)
