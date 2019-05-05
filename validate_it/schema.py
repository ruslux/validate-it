import uuid
from inspect import getmembers, isroutine, isclass
from typing import Union, List, Tuple, Type, Any
from warnings import warn

from validate_it.options import Options
from validate_it.utils import _repr, _unwrap
from validate_it.variable import SchemaVar


class Schema:
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if not hasattr(cls, '__annotations__'):
            warn("Schema without __annotations__ must be abstract. Do not instantiate it", RuntimeWarning)
        else:
            cls._init_schema()

    def __getattribute__(self, name: str) -> Any:
        if name == "__options__":
            return self.__class__.__options__

        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """ Dataclass support: prevent dataclass setattr to initialized SchemaVar"""
        if isinstance(value, Options):
            return

        super().__setattr__(name, value)

    class Meta:
        strip_unknown = False

    def __new__(cls, **kwargs) -> Any:
        """ Create container for validated values """

        if not hasattr(cls, '__annotations__'):
            raise RuntimeWarning("Schema without __annotations__ must be abstract. Do not instantiate it")
        else:
            instance = super().__new__(cls)
            instance.__current_values__ = {}
            return instance

    def __init__(self, **kwargs) -> None:
        """ Regular way to initialize Schema instance """
        kwargs = self._map(kwargs)

        for k, o in self.__options__.items():
            v = kwargs.get(k)
            setattr(self, k, v)

    def __post_init__(self):
        """ Dataclass way to initialize Schema instance """
        kwargs = {}

        for k in self.__options__.keys():
            kwargs[k] = getattr(self, k)

        for k, o in self.__options__.items():
            v = kwargs.get(k)
            setattr(self, k, v)

    @classmethod
    def _set_options(cls):
        cls.__options__ = {}

        _keys = set()

        attributes = getmembers(
            cls, lambda _field: not isroutine(_field) and not isclass(_field)
        )

        for key, value in attributes:
            if not key.startswith("__") and not key.endswith("__"):
                if isinstance(value, Options):
                    cls.__options__[key] = value
                elif isinstance(value, SchemaVar):
                    cls.__options__[key] = value.options
                else:
                    cls.__options__[key] = Options(default=value)

        for key, _type in cls.__annotations__.items():
            if key not in cls.__options__.keys():
                cls.__options__[key] = Options()

    @classmethod
    def _set_options_type(cls):
        for key, _type in cls.__annotations__.items():
            cls.__options__[key].set_type(_type)

    @classmethod
    def _set_options_required(cls):
        for key, _type in cls.__annotations__.items():

            if hasattr(_type, "__origin__") and _type.__origin__ == Union and None in _type.__args__:
                cls.__options__[key].required = False

    @classmethod
    def _add_cloned_options(cls):
        if hasattr(cls, "__cloned_options__"):
            for k, o in cls.__cloned_options__.items():
                cls.__options__[k] = o

    @classmethod
    def _set_options_type_any(cls):
        for key, options in cls.__options__.items():
            if not options.get_type():
                options.set_type(Any)

    @classmethod
    def _init_schema(cls):
        # if not hasattr(cls, "__options__"):
        cls._set_options()
        cls._set_options_type()
        cls._set_options_required()
        cls._add_cloned_options()
        cls._set_options_type_any()
        cls._set_schema_vars()

        if not hasattr(cls.Meta, "strip_unknown"):
            cls.Meta.strip_unknown = False

    @classmethod
    def _set_schema_vars(cls):
        for key, options in cls.__options__.items():
            sv = SchemaVar(key, options)
            setattr(cls, key, sv)

    @classmethod
    def representation(cls):
        return {
            "schema": {
                k: _repr(o.get_type(), o)
                for k, o in cls.__options__.items()
            }
        }

    def _map(self, data):
        _new = {}
        _expected = []

        for key, value in self.__options__.items():
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
    def _set_defaults(cls, data):
        """ Set defaults for silence @dataclass __init__()  missing required positional arguments TypeError"""
        for key, options in cls.__options__.items():
            value = data.get(key)

            if value is None and options.default is not None:
                if callable(options.default):
                    value = options.default()
                else:
                    value = options.default

                data[key] = value

        return data

    @classmethod
    def from_dict(cls, data: dict):
        data = cls._set_defaults(data)

        return cls(**data)

    def _expected_name(self, name):
        if name in self.__options__.keys():
            rename = self.__options__[name].rename

            if rename:
                return rename

        return name

    def to_dict(self) -> dict:
        _data = {}

        for k, o in self.__options__.items():
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
        if "__options__" not in cls.__dict__.keys():
            cls._init_schema()

        if exclude and include:
            raise ValueError("cannot specify both exclude and include")

        _dict = {
            "__cloned_options__": {},
            "__annotations__": {}
        }

        _drop = set()

        for k, v in cls.__dict__.items():
            if k not in ["__annotations__", "__options__", "__cloned_options__"] + list(cls.__options__.keys()):
                _dict[k] = v

        if include:
            include = set(include)
            _all = set(cls.__options__.keys())

            _drop = _all - include

        if exclude:
            _drop = set(exclude)

        for k, o in cls.__options__.items():
            if k not in _drop:
                _dict["__cloned_options__"][k] = o

        if add:
            for k, t, o in add:
                o.set_type(t)
                _dict["__cloned_options__"][k] = o

        new_cls = type(
            f"DynamicCloneOf{cls.__name__}{uuid.uuid4().hex}", cls.__bases__, _dict
        )

        return new_cls


__all__ = [
    "Schema"
]
