import attr

from validate_it.strict import StrictType


@attr.s(slots=True)
class AnyType(StrictType):
    """
    Поле, для которого любое значение считается правильным.
    """
    _base_type = object


__all__ = [
    'AnyType'
]
