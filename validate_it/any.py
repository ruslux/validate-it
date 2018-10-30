from typing import Type

from validate_it.strict import StrictType


class AnyType(StrictType):
    """
    Поле, для которого любое значение считается правильным.
    """

    base_type: Type = object


__all__ = ["AnyType"]
