from typing import Tuple

import attr

from validate_it.base import Validator
from validate_it.utils import list_of, not_empty


@attr.s
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
    _alternatives = attr.ib(
        default=attr.Factory(list), validator=[attr.validators.instance_of(list), list_of(Validator), not_empty]
    )

    def representation(self):
        return {'one of': [x.representation() for x in self._alternatives]}

    def is_valid(self, value, convert=False, strip_unknown=False) -> Tuple[bool, dict, dict]:
        _errors = {}

        for _alternative in self._alternatives:
            _is_valid, _error, _value = _alternative.is_valid(value, convert, strip_unknown)

            if _is_valid:
                return _is_valid, _error, _value
            else:
                _errors[_alternative.__class__.__name__] = _error

        return False, _errors, value


__all__ = [
    'UnionType'
]
