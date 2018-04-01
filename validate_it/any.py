import attr

from validate_it.strict import StrictType


@attr.s
class AnyType(StrictType):
    """
    Поле, для которого любое значение считается правильным.
    """
    _type = object

    def representation(self):
        return 'any type'


__all__ = [
    'AnyType'
]
