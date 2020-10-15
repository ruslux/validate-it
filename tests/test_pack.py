from typing import Optional

import pytest

from validate_it import Options, ValidationError, pack_value, schema, to_dict


@schema
class A:
    a: int


@schema
class OptionalAutoPackDisabled:
    a: Optional[A]


@schema
class OptionalAutoPackEnabled:
    a: Optional[A] = Options(auto_pack=True, packer=pack_value)


def test_pack():
    with pytest.raises(ValidationError):
        OptionalAutoPackDisabled(a={'a': 1})

    OptionalAutoPackDisabled(a=A(a=1))
    OptionalAutoPackDisabled(a=None)
    OptionalAutoPackDisabled()

    OptionalAutoPackEnabled(a={'a': 1})
    OptionalAutoPackEnabled(a=None)
    OptionalAutoPackEnabled()


def test_unpack():
    assert {'a': {'a': 1}} == to_dict(OptionalAutoPackDisabled(a=A(a=1)))
    assert {'a': {'a': 1}} == to_dict(OptionalAutoPackEnabled(a={'a': 1}))

    assert {} == to_dict(OptionalAutoPackEnabled(a=None))
    assert {} == to_dict(OptionalAutoPackEnabled())
