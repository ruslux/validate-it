from typing import Tuple, List

import attr

from validate_it.strict import StrictType
from validate_it.base import Validator


@attr.s(auto_attribs=True)
class UnionType(StrictType):
    """
    Схема для которой можно задать несколько допустимых типов.

    Например:

    .. code-block:: python

        class MySchema(UnionSchema):
            alternatives=[
                FirstSchema(),
                SecondSchema()
            ]

    """

    alternatives: List[Validator] = attr.Factory(list)

    def __attrs_post_init__(self):
        if not len(self.alternatives):
            raise ValueError(f"UnionType `alternatives` must be not empty")

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        _data["one of"] = [x.representation(**kwargs) for x in self.alternatives]

        return _data

    def validate_it(self, value, **kwargs) -> Tuple[dict, dict]:
        _errors = {}

        for _alternative in self.alternatives:
            _error, _value = _alternative.validate_it(value, **kwargs)

            if not _error:
                return _error, _value
            else:
                _errors[_alternative.__class__.__name__] = _error

        return _errors, value


__all__ = ["UnionType"]
