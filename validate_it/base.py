from typing import Tuple, Any

import attr


@attr.s(slots=True)
class Validator:
    _singletons = {}
    _field_name = attr.ib(default=None, type=str)

    def __set_name__(self, owner, name):
        self._field_name = name

    # CONFLICT: _field_name representation for two different fields represent as first defined with same signature
    # def __new__(cls, *args, **kwargs):
    #     _name = cls.get_singleton_name(*args, **kwargs)
    #
    #     if _name not in cls._singletons:
    #         _instance = object.__new__(cls)
    #         _instance.__init__(*args, **kwargs)
    #         cls._singletons[_name] = _instance
    #     return cls._singletons[_name]

    @property
    def extended_type(self):
        return self.__class__.__name__

    @classmethod
    def get_singleton_name(cls, *args, **kwargs):
        return cls.__name__ + str(kwargs)

    def representation(self):
        return {
            'name': self._field_name or 'undefined',
            'base_type': self._base_type.__name__,
            'extended_type': self.extended_type
        }

    def validate_it(self, value, convert=False, strip_unknown=False) -> Tuple[Any, Any]:
        raise NotImplementedError


__all__ = [
    'Validator'
]
