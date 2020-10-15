from typing import Optional, List, Dict, Tuple, Union

import pytest

from validate_it import Options, schema, to_dict, ValidationError


@schema
class Skill:
    level: int
    multiplier: float


@schema
class Item:
    title: str


@schema
class Player:
    name: str

    items: List[Item]

    skills: Dict[str, Skill]


@schema
class Required:
    _int: int
    _float: float
    _bool: bool
    _str: str
    _dict: dict
    _list: list


@schema
class RequiredDefault:
    _int: int = Options(default=1)
    _float: float = Options(default=1.0)
    _bool: bool = Options(default=True)
    _str: str = Options(default="x")
    _dict: dict = Options(default={"x": 1})
    _list: List[int] = Options(default=[1, 2])


@schema
class RequiredDefaultCallable:
    _int: int = Options(default=lambda: 1)
    _float: float = Options(default=lambda: 1.0)
    _bool: bool = Options(default=lambda: True)
    _str: str = Options(default=lambda: "x")
    _dict: dict = Options(default=lambda: {"x": 1})
    _list: list = Options(default=lambda: [1, 2])


@schema
class NotRequired:
    _optional: Optional[int]
    _required: int


@schema
class NotRequiredDefault:
    _optional: Optional[int] = 0
    _optional_with_options: Optional[int] = Options(default=1)
    _required: int = 0


@schema
class NotRequiredDefaultCallable:
    _optional: Optional[int] = lambda: 0
    _optional_with_options: Optional[int] = Options(default=lambda: 0)
    _required: int = lambda: 0


@schema
class Empty:
    _optional: Optional[int]
    _required: int


@schema
class Allowed:
    a: int = Options(allowed=[1, 2])


@schema
class AllowedCallable:
    a: int = Options(allowed=lambda: [1, 2])


@schema
class Amount:
    a: int = Options(min_value=10)
    b: int = Options(max_value=20)


@schema
class Length:
    a: str = Options(min_length=2)
    b: str = Options(max_length=5)


@schema
class Convert:
    a: str = Options(parser=str)


@schema
class NotSpecified:
    a: list
    b: dict


@schema
class TupleType:
    a: tuple
    b: Tuple[int, int, float]


@schema
class TypeVarType:
    a: Optional[List]
    b: Optional[List[int]]
    c: Optional[Dict]
    d: Optional[Dict[int, int]]


@schema
class DescriptorType:
    a: Optional[List]
    b: Optional[List[int]]
    c: Optional[Dict]
    d: Optional[Dict[int, int]]


@schema
class SerializerType:
    a: float = Options(parser=float, serializer=int)


@schema(strip_unknown=True)
class Unexpected:
    a: float = Options(parser=float, serializer=int)


@schema
class UnexpectedNotStrip:
    a: float = Options(parser=float, serializer=int)


@schema
class UnionA:
    a: int


@schema
class UnionB:
    b: float


@schema
class UnionC:
    c: Union[UnionA, UnionB]


@schema
class OptionalDictA:
    i: int


@schema
class OptionalDictB:
    s: str
    nested_with_elements: Optional[Dict[int, OptionalDictA]]
    nested_empty: Optional[Dict[int, OptionalDictA]]


@schema
class OptionalDictWithDefaultA:
    i: int


@schema
class OptionalDictWithDefaultB:
    nested: OptionalDictWithDefaultA


@schema
class OptionalDictWithDefaultC:
    s: str
    nested_with_elements: Optional[Dict[int, OptionalDictWithDefaultB]] = Options()
    nested_empty: Optional[Dict[int, OptionalDictWithDefaultB]] = Options()


def test_required():
    with pytest.raises(ValidationError):
        Required()

    _data = {
        "_int": 1,
        "_float": 1.0,
        "_bool": True,
        "_str": "str",
        "_dict": dict(),
        "_list": list()
    }

    assert to_dict(Required(**_data)) == _data


def test_required_default():
    _data = {
        "_int": 1,
        "_float": 1.0,
        "_bool": True,
        "_str": "x",
        "_dict": {"x": 1},
        "_list": [1, 2]
    }

    assert to_dict(RequiredDefault()) == _data


def test_required_default_callable():
    _data = {
        "_int": 1,
        "_float": 1.0,
        "_bool": True,
        "_str": "x",
        "_dict": {"x": 1},
        "_list": [1, 2]
    }

    assert to_dict(RequiredDefaultCallable()) == _data


def test_not_required():
    _data = {
        "_required": 1
    }

    assert to_dict(NotRequired(**_data)) == _data

    _data = {
        "_required": 1,
        "_optional": 1
    }

    assert to_dict(NotRequired(**_data)) == _data

    _data = {}

    with pytest.raises(ValidationError):
        to_dict(NotRequired(**_data))


def test_not_required_default():
    _data = {
        "_required": 0,
        "_optional": 0,
        "_optional_with_options": 1
    }

    assert to_dict(NotRequiredDefault(**_data)) == _data


def test_not_required_default_callable():
    _data = {
        "_required": 0,
        "_optional": 0,
        "_optional_with_options": 1
    }

    assert to_dict(NotRequiredDefaultCallable(**_data)) == _data


def empty():
    _data = {
        "_required": 0,
        "_optional": None
    }

    _expected = {
        "_required": 0
    }

    assert to_dict(Empty(**_data)) == _expected


def test_allowed():
    with pytest.raises(ValidationError):
        Allowed(a=3)

    Allowed(a=1)


def test_allowed_callable():
    with pytest.raises(ValidationError):
        AllowedCallable(a=3)

    AllowedCallable(a=1)


def test_amount():
    Amount(a=10, b=20)

    with pytest.raises(ValidationError):
        to_dict(Amount(a=9, b=20))

    with pytest.raises(ValidationError):
        to_dict(Amount(a=10, b=21))


def test_length():
    Length(a="12", b="12345")

    with pytest.raises(ValidationError):
        Length(a="1", b="12345")

    with pytest.raises(ValidationError):
        Length(a="12", b="123456")


def test_convert():
    assert to_dict(Convert(a=1)) == {"a": "1"}


def test_nested_validation_and_members_access():
    _data = {
        "name": "John",
        "items": [
            {"title": "Rose"}
        ],
        "skills": {
            "fire": {
                "level": 1,
                "multiplier": 2.0,
            },
            "ice": {
                "level": 2,
                "multiplier": 3.0,
            }
        }
    }

    p = Player(
        name="John",
        items=[
            Item(title="Rose"),
        ],
        skills={
            "fire": Skill(level=1, multiplier=2.0),
            "ice": Skill(level=2, multiplier=3.0),
        }
    )

    assert to_dict(p) == _data
    assert p.name == "John"
    assert p.items[0].title == "Rose"
    assert p.skills["ice"].level == 2


def test_not_specified():
    with pytest.raises(ValidationError):
        NotSpecified(a={1: 1}, b={1: 1})

    with pytest.raises(ValidationError):
        NotSpecified(a=[1, 1], b=[1, 1])

    assert to_dict(NotSpecified(a=[1, 1], b={1: 1})) == {
        "a": [1, 1],
        "b": {1: 1}
    }


def test_tuple():
    TupleType(a=(1, 2), b=(1, 2, 3.0))

    with pytest.raises(ValidationError):
        TupleType(a=[1, 2, 3], b={1, 2, 3.0})

    with pytest.raises(ValidationError):
        TupleType(a={1, 2, 3}, b={1, 2, 3})


def test_typevar():
    data = {"a": [], "b": [1], "c": {"a": "b"}, "d": {1: 2}}

    assert to_dict(TypeVarType(**data)) == data


def test_descriptor():
    a = DescriptorType(a=[], b=[1], c={"a": "b"}, d={1: 2})

    assert to_dict(a) == {"a": [], "b": [1], "c": {"a": "b"}, "d": {1: 2}}

    with pytest.raises(ValidationError):
        a.a = {}

    a.a = [100]

    assert a.a == [100]


def test_serializer():
    a = SerializerType(a="1.1")
    assert a.a == 1.1
    assert to_dict(a) == {"a": 1}


def test_unexpected():
    a = Unexpected(a="1.1", b="1.1")
    assert a.a == 1.1
    assert to_dict(a) == {"a": 1}

    with pytest.raises(ValidationError):
        UnexpectedNotStrip(a="1.1", b="1.1")


def test_union():
    UnionC(c=UnionA(a=1))
    UnionC(c=UnionB(b=0.1))

    with pytest.raises(ValidationError):
        UnionC(c=UnionA(a=0.1))


def test_optional_dict():
    b = OptionalDictB(
        s="s",
        nested_with_elements={1: OptionalDictA(i=2)}
    )

    assert to_dict(b) == {"s": "s", "nested_with_elements": {1: {"i": 2}}}


def test_optional_dict_with_default():
    c = OptionalDictWithDefaultC(
        s="s",
        nested_with_elements={
            1: OptionalDictWithDefaultB(nested=OptionalDictWithDefaultA(i=2))
        }
    )

    assert c.s == "s"

    assert to_dict(c) == {"s": "s", "nested_with_elements": {1: {"nested": {"i": 2}}}}
    c.nested_with_elements[1].nested = OptionalDictWithDefaultA(i=10)
    to_dict(c)
