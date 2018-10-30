from dataclasses import field, dataclass
from typing import Tuple, List

from validate_it.base import Validator


@dataclass
class UnionType(Validator):
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

    alternatives: List[Validator] = field(default_factory=list)

    def __post_init__(self):
        if not len(self.alternatives):
            raise ValueError(f"UnionType `alternatives` must be not empty")

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        _data["one of"] = [x.representation(**kwargs) for x in self.alternatives]

        return _data

    def validate_it(self, value, convert=False, strip_unknown=False) -> Tuple[dict, dict]:
        _errors = {}

        for _alternative in self.alternatives:
            _error, _value = _alternative.validate_it(value, convert, strip_unknown)

            if not _error:
                return _error, _value
            else:
                _errors[_alternative.__class__.__name__] = _error

        return _errors, value


__all__ = ["UnionType"]
