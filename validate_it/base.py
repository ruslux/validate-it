from typing import Tuple, Any

import attr


@attr.s
class Validator:
    _singletons = {}
    _field_name = attr.ib(default=None, type=str)

    def __set_name__(self, owner, name):
        self._field_name = name

    def __new__(cls, *args, **kwargs):
        _name = cls.get_singleton_name(*args, **kwargs)

        if _name not in cls._singletons:
            _instance = object.__new__(cls)
            _instance.__init__(*args, **kwargs)
            cls._singletons[_name] = _instance
        return cls._singletons[_name]

    @classmethod
    def get_singleton_name(cls, *args, **kwargs):
        return cls.__name__ + str(kwargs)

    def representation(self):
        raise NotImplementedError()

    def is_valid(self, value, convert=False, strip_unknown=False) -> Tuple[bool, Any, Any]:
        raise NotImplementedError


__all__ = [
    'Validator'
]
