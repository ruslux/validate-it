import uuid
from inspect import getmembers, isroutine, isclass
from typing import Union, List, Tuple, Type, Any

from validate_it.options import Options
from validate_it.utils import _repr, _unwrap, _wrap, _is_compatible


def validate(o: Options, k, v):
    v = _convert(o, k, v)
    v = _check_types(o, k, v)

    # use o other
    v = _validate_allowed(o, k, v)
    v = _validate_min_value(o, k, v)
    v = _validate_max_value(o, k, v)
    v = _validate_min_length(o, k, v)
    v = _validate_max_length(o, k, v)
    v = _validate_size(o, k, v)
    v = _walk_validators(o, k, v)

    return v


def _convert(o: Options, k, v):
    if not _is_compatible(v, o.get_type()) and o.parser:
        converted = o.parser(v)

        if converted is not None:
            v = converted

    return v


def _check_types(o: Options, k, v):
    if not _is_compatible(v, o.get_type()):
        raise TypeError(f"Field `{k}`: {o.get_type()} is not compatible with value `{v}`:{type(v)}")

    return v


def _validate_allowed(o: Options, k, v):
    allowed = o.allowed

    if callable(o.allowed):
        allowed = o.allowed()

    if allowed and v not in allowed:
        raise ValueError(f"Field `{k}`: value `{v}` is not allowed. Allowed vs: `{allowed}`")

    return v


def _validate_min_length(o: Options, k, v):
    min_length = o.min_length

    if callable(min_length):
        min_length = min_length()

    if min_length is not None and len(v) < min_length:
        raise ValueError(f"Field `{k}`: len(`{v}`) is less than required")

    return v


def _validate_max_length(o: Options, k, v):
    max_length = o.max_length

    if callable(max_length):
        max_length = max_length()

    if max_length is not None and len(v) > max_length:
        raise ValueError(f"Field `{k}`: len(`{v}`) is greater than required")

    return v


def _validate_min_value(o: Options, k, v):
    min_value = o.min_value

    if callable(min_value):
        min_value = min_value()

    if min_value is not None and v < min_value:
        raise ValueError(f"Field `{k}`: value `{v}` is less than required")

    return v


def _validate_max_value(o: Options, k, v):
    max_value = o.max_value

    if callable(max_value):
        max_value = max_value()

    if max_value is not None and v > max_value:
        raise ValueError(f"Field `{k}`: value `{v}` is greater than required")

    return v


def _validate_size(o: Options, k, v):
    size = o.size

    if callable(size):
        size = size()

    if size is not None and size != len(v):
        raise ValueError(f"Field `{k}`: len(`{v}`) is not equal `{size}`")

    return v


def _walk_validators(o: Options, k, v):
    validators = o.validators

    if validators:
        for validator in validators:
            v = validator(k, v)

    return v


def _replace_init(cls, strip_unknown=False):
    origin = cls.__init__

    def __init__(self, **kwargs) -> None:
        kwargs = _map(cls, kwargs, strip_unknown=strip_unknown)
        kwargs = _set_defaults(self, kwargs)

        for k, o in self.__options__.items():
            v = kwargs.get(k)
            v = _wrap(v, o.get_type())

            kwargs[k] = validate(o, k, v)
        try:
            origin(self, **kwargs)
            return
        except TypeError:
            pass

        origin(self)

        for k, o in self.__options__.items():
            v = kwargs.get(k)
            setattr(self, k, v)

    cls.__init__ = __init__


def _replace_setattr(cls):
    origin = cls.__setattr__

    def __setattr__(self, key, value):
        o = self.__options__.get(key)

        if o:
            value = validate(o, key, value)

        origin(self, key, value)

    cls.__setattr__ = __setattr__


def _replace_getattribute(cls):
    origin = cls.__getattribute__

    def __getattribute__(self, name: str) -> Any:
        # if name == "__options__":
        #     return self.__class__.__options__

        return origin(self, name)

    cls.__getattribute__ = __getattribute__


def _map(cls, data, strip_unknown=False):
    _new = {}
    _expected = []

    for key, value in cls.__options__.items():
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

    if not strip_unknown:
        _schema_keys = set(_expected)
        _kwargs_keys = set(data.keys())

        _unexpected = _kwargs_keys - _schema_keys

        if len(_unexpected):
            raise TypeError(f"__new__() got an unexpected keyword arguments {_unexpected}")

    return _new


def _set_defaults(instance, data):
    for key, options in instance.__options__.items():
        value = data.get(key)

        if value is None and options.default is not None:
            if callable(options.default):
                value = options.default()
            else:
                value = options.default

            data[key] = value

    return data


def _set_options(cls):
    if not hasattr(cls, "__options__"):
        cls.__options__ = {}

    _keys = set()

    attributes = getmembers(
        cls, lambda _field: not isroutine(_field) and not isclass(_field)
    )

    for key, value in attributes:
        if not key.startswith("__") and not key.endswith("__"):
            if isinstance(value, Options):
                cls.__options__[key] = value
            else:
                cls.__options__[key] = Options(default=value)

    if hasattr(cls, '__annotations__'):
        for key, _type in cls.__annotations__.items():
            if key not in cls.__options__.keys():
                cls.__options__[key] = Options()


def _set_options_type(cls):
    if hasattr(cls, '__annotations__'):
        for key, _type in cls.__annotations__.items():
            cls.__options__[key].set_type(_type)


def _set_options_required(cls):
    if hasattr(cls, '__annotations__'):
        for key, _type in cls.__annotations__.items():

            if hasattr(_type, "__origin__") and _type.__origin__ == Union and None in _type.__args__:
                cls.__options__[key].required = False


def _set_options_type_any(cls):
    for key, options in cls.__options__.items():
        if not options.get_type():
            options.set_type(Any)


def _init_schema(cls, strip_unknown=False):
    _set_options(cls)
    _set_options_type(cls)
    _set_options_required(cls)
    _set_options_type_any(cls)

    _replace_init(cls, strip_unknown)
    _replace_setattr(cls)


def schema(*args, **kwargs):
    def _wrapper(cls):
        _init_schema(cls, strip_unknown=kwargs.get('strip_unknown', False))
        return cls

    if args:
        return _wrapper(*args)
    else:
        return _wrapper


def representation(cls):
    return {
        "schema": {
            k: _repr(o.get_type(), o)
            for k, o in cls.__options__.items()
        }
    }


def _expected_name(instance, name):
    if name in instance.__options__.keys():
        rename = instance.__options__[name].rename

        if rename:
            return rename

    return name


def to_dict(instance) -> dict:
    _data = {}

    for k, o in instance.__options__.items():
        if o.required:
            value = getattr(instance, k)

            _unwrapped = _unwrap(value, o.get_type())

            if _unwrapped is not None:
                if o.serializer:
                    _unwrapped = o.serializer(_unwrapped)

                _data[_expected_name(instance, k)] = _unwrapped

    return _data


def clone(cls, strip_unknown=False, exclude=None, include=None, add: List[Tuple[str, Type, Options]] = None):
    if exclude and include:
        raise ValueError("cannot specify both exclude and include")

    _dict = {
        "__options__": {}
    }

    _drop = set()

    if not hasattr(cls, "__options__"):
        raise TypeError("Cloned class must be schema")

    for k, v in cls.__dict__.items():
        if k not in ["__options__"] + list(cls.__options__.keys()):
            _dict[k] = v

    if include:
        include = set(include)
        _all = set(cls.__options__.keys())

        _drop = _all - include

    if exclude:
        _drop = set(exclude)

    for k, o in cls.__options__.items():
        if k not in _drop:
            _dict["__options__"][k] = o

    if add:
        for k, t, o in add:
            o.set_type(t)
            _dict["__options__"][k] = o

    print(_dict["__options__"])

    new_cls = type(
        f"DynamicCloneOf{cls.__name__}_{uuid.uuid4().hex}", cls.__bases__, _dict
    )

    return new_cls


__all__ = [
    "schema",
    "to_dict",
    "representation",
    "clone"
]
