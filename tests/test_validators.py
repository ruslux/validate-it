import re

import pytest

from validate_it import Options, schema


class IsNotEmailError(Exception):
    pass


def is_email(name, key, value, root):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise IsNotEmailError()

    return value


def neighbor_is_alan(name, key, value, root):
    assert root["neighbor"] == "Alan"
    return value


@schema
class TypeWithValidator:
    email: str = Options(validators=[is_email])



@schema
class TypeWithRootAccess:
    neighbor: str
    user: str = Options(validators=[neighbor_is_alan])



def test_validators():
    with pytest.raises(IsNotEmailError):
        TypeWithValidator(email="notEmail")

    TypeWithValidator(email="it@is.email")


def test_root_access():
    TypeWithRootAccess(user="John", neighbor="Alan")

    with pytest.raises(AssertionError):
        TypeWithRootAccess(user="John", neighbor="Keira")
