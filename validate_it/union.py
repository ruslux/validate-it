from typing import Tuple

import attr

from validate_it.base import Validator
from validate_it.utils import list_of, not_empty


@attr.s(slots=True)
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

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        _data['one of'] = [x.representation(**kwargs) for x in self._alternatives]

        return _data

    def validate_it(self, value, convert=False, strip_unknown=False) -> Tuple[dict, dict]:
        _errors = {}

        for _alternative in self._alternatives:
            _error, _value = _alternative.validate_it(value, convert, strip_unknown)

            if not _error:
                return _error, _value
            else:
                _errors[_alternative.__class__.__name__] = _error

        return _errors, value


__all__ = [
    'UnionType'
]
