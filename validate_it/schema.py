import uuid
from inspect import getmembers, isroutine, isclass
from typing import Union, List, Tuple, Type, Any

from validate_it.options import Options
from validate_it.utils import _repr, _unwrap
from validate_it.variable import SchemaVar


class Schema:
    class Meta:
        strip_unknown = False

    def __init__(self, **kwargs) -> None:
        self.__init_kwargs__ = kwargs
        self.__post_init__()

    def __post_init__(self):
        self.__class__._set_schema()

        if hasattr(self, '__init_kwargs__'):
            kwargs = self.__init_kwargs__

            # use options alias
            kwargs = self._map(kwargs)
        else:
            kwargs = {}

            for k in self.__class__.__options__.keys():
                kwargs[k] = getattr(self, k)

            print(kwargs)

        # other checks placed into descriptors
        for k, o in self.__class__.__options__.items():
            v = kwargs.get(k)
            setattr(self, k, v)

    @classmethod
    def _get_options(cls):
        _options = {}

        _keys = set()

        attributes = getmembers(
            cls, lambda _field: not isroutine(_field) and not isclass(_field)
        )

        for key, value in attributes:
            if not key.startswith("__") and not key.endswith("__"):
                if isinstance(value, Options):
                    _options[key] = value
                else:
                    _options[key] = Options(default=value)

        for key, _type in cls.__annotations__.items():
            if key not in _options.keys():
                _options[key] = Options()

            _options[key].set_type(_type)

            if hasattr(_type, '__origin__') and _type.__origin__ == Union and None in _type.__args__:
                _options[key].required = False

        if hasattr(cls, '__cloned_options__'):
            for k, o in cls.__cloned_options__.items():
                _options[k] = o

        for key, options in _options.items():
            if not options.get_type():
                options.set_type(Any)

        return _options

    @classmethod
    def _set_schema(cls):
        if not hasattr(cls, '__options__'):
            cls.__options__ = cls._get_options()
            cls._set_schema_vars()

        if not hasattr(cls.Meta, 'strip_unknown'):
            cls.Meta.strip_unknown = False

    @classmethod
    def _set_schema_vars(cls):
        for key, options in cls.__options__.items():
            sv = SchemaVar(key, options)
            setattr(cls, key, sv)

    @classmethod
    def representation(cls):
        _options = cls._get_options()

        return {
            'schema': {
                k: _repr(o.get_type(), o)
                for k, o in _options.items()
            }
        }

    def _map(self, data):
        _new = {}
        _expected = []

        for key, value in self.__class__.__options__.items():
            try:
                _new[key] = data[key]
                _expected.append(key)
            except KeyError:
                if value.alias:
                    try:
                        _new[key] = data[value.alias]
                        _expected.append(value.alias)
                    except KeyError:
                        pass

        if not self.Meta.strip_unknown:
            _schema_keys = set(_expected)
            _kwargs_keys = set(data.keys())

            _unexpected = _kwargs_keys - _schema_keys

            if len(_unexpected):
                raise TypeError(f"__new__() got an unexpected keyword arguments {_unexpected}")

        return _new

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def _expected_name(self, name):
        if name in self.__class__.__options__.keys():
            rename = self.__class__.__options__[name].rename

            if rename:
                return rename

        return name

    def to_dict(self) -> dict:
        _data = {}

        for k, o in self.__class__.__options__.items():
            if o.required:
                value = getattr(self, k)

                _unwrapped = _unwrap(value, o.get_type())

                if _unwrapped is not None:
                    if o.serializer:
                        _unwrapped = o.serializer(_unwrapped)

                    _data[self._expected_name(k)] = _unwrapped

        return _data

    @classmethod
    def clone(cls, exclude=None, include=None, add: List[Tuple[str, Type, Options]] = None):
        if exclude and include:
            raise ValueError("cannot specify both exclude and include")

        _dict = {
            '__cloned_options__': {},
            '__annotations__': {}
        }

        _drop = set()

        _options = cls._get_options()

        for k, v in cls.__dict__.items():
            if k not in ['__annotations__', '__options__', '__cloned_options__'] + list(_options.keys()):
                _dict[k] = v

        if include:
            include = set(include)
            _all = set(_options.keys())

            _drop = _all - include

        if exclude:
            _drop = set(exclude)

        for k, o in _options.items():
            if k not in _drop:
                _dict['__cloned_options__'][k] = o

        if add:
            for k, t, o in add:
                o.set_type(t)
                _dict['__cloned_options__'][k] = o

        new_cls = type(
            f"DynamicCloneOf{cls.__name__}{uuid.uuid4().hex}", cls.__bases__, _dict
        )

        return new_cls


__all__ = [
    "Schema"
]
