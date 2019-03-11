from typing import Type

import attr

from validate_it.strict import StrictType


@attr.s(auto_attribs=True)
class AnyType(StrictType):
    """
    Поле, для которого любое значение считается правильным.
    """

    base_type: Type = object


__all__ = ["AnyType"]
