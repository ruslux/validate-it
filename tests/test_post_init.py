import pytest

from validate_it import ValidationError, schema


@schema
class A:
    a: int

    def __validate_it__post_init__(self):
        raise ValidationError


def test_post_init():
    with pytest.raises(ValidationError):
        A(a=1)
