import uuid

from inspect import getmembers, isroutine, isclass
from typing import Dict, TypeVar
from typing import Union, List, Tuple, Type, Any

from validate_it.errors import ValidationError
from validate_it.options import Options


def is_schema(box_type):
    return hasattr(box_type, '__validate_it__options__')


def is_generic_alias(box_type, classes):
    if box_type in classes:
        return True

    try:
        return box_type.__origin__ in classes
    except AttributeError:
        return False


def _repr(t, o):
    from validate_it import Options

    _d = {
        "required": o.required,
    }

    if o.default is not None:
        _d["default"] = o.default if not callable(o.default) else "dynamic"

    if o.min_length is not None:
        _d["min length"] = o.min_length if not callable(o.min_length) else "dynamic"

    if o.max_length is not None:
        _d["max length"] = o.max_length if not callable(o.max_length) else "dynamic"

    if o.min_value is not None:
        _d["min value"] = o.min_value if not callable(o.min_value) else "dynamic"

    if o.max_value is not None:
        _d["max value"] = o.max_value if not callable(o.max_value) else "dynamic"

    if o.size is not None:
        _d["size"] = o.size if not callable(o.size) else "dynamic"

    if o.allowed is not None:
        _d["allowed values"] = o.allowed if not callable(o.allowed) else "dynamic"

    if o.alias is not None:
        _d["search alias"] = o.alias if not callable(o.alias) else "dynamic"

    if o.rename is not None:
        _d["rename to"] = o.rename if not callable(o.rename) else "dynamic"

    if is_generic_alias(t, (Union,)):
        _d.update(
            {
                "type": "union",
                "nested_types": [
                    _repr(arg, Options())
                    for arg in t.__args__
                ]
            }
        )

    elif is_generic_alias(t, (list, List)):
        _d.update(
            {
                "type": "list",
                "nested_type": [
                    _repr(t.__args__[0], Options())
                ]
            }
        )

    elif is_generic_alias(t, (dict, Dict)):
        _d.update(
            {
                "type": "dict",
                "key_type": _repr(t.__args__[0], Options()),
                "value_type": _repr(t.__args__[1], Options())
            }
        )

    elif hasattr(t, '__validate_it__options__'):
        _d.update(
            {
                "type": "validate_it.schema",
                "schema": representation(t)
            }
        )

    elif isinstance(t, list):
        _d.update(
            {
                "type": "dict",
                "nested_type": "any"
            }
        )

    elif isinstance(t, dict):
        _d.update(
            {
                "type": "dict",
                "key_type": "any",
                "value_type": "any"
            }
        )

    else:
        _d["type"] = t.__name__

    return _d


def representation(cls):
    return {
        "schema": {
            k: _repr(o.get_type(), o)
            for k, o in cls.__validate_it__options__.items()
        }
    }


def unpack_value(value, box_type):
    """ Cast nested values types: List[NestedClass] -> List[Dict]"""
    if value is None:
        return value

    if box_type is dict and isinstance(value, dict):
        return value

    if box_type is list and isinstance(value, list):
        return value

    if is_generic_alias(box_type, (Union,)):
        for arg in box_type.__args__:
            try:
                return unpack_value(value, arg)
            except ValidationError:
                continue

    if is_generic_alias(box_type, (list, List)) and isinstance(value, list):
        if box_type.__args__:
            subtype = box_type.__args__[0]

            return [
                unpack_value(item, subtype)
                for item in value
            ]
        else:
            return value

    if is_generic_alias(box_type, (dict, Dict)) and isinstance(value, dict):
        if box_type.__args__:
            subtype_0 = box_type.__args__[0]
            subtype_1 = box_type.__args__[1]

            return {
                unpack_value(k, subtype_0): unpack_value(v, subtype_1)
                for k, v in value.items()
            }
        else:
            return value

    if is_schema(box_type):
        return to_dict(value)

    return value


def pack_value(value, box_type):
    """ Cast nested values types: List[Dict] -> List[NestedClass]"""
    if value is None:
        return None

    try:
        if isinstance(value, box_type):
            return value
    except TypeError:
        pass

    if box_type is dict and isinstance(value, dict):
        return value

    if box_type is list and isinstance(value, list):
        return value

    if hasattr(box_type, '__validate_it__options__') and is_compatible(value, dict):
        result = box_type(**value)
        return result

    if is_generic_alias(box_type, (Union,)):
        for arg in box_type.__args__:
            try:
                return pack_value(value, arg)
            except ValidationError:
                continue

    if is_generic_alias(box_type, (list, List)) and isinstance(value, list):
        subtype = box_type.__args__[0]

        return [
            pack_value(item, subtype)
            for item in value
        ]

    if is_generic_alias(box_type, (dict, Dict)) and isinstance(value, dict):
        subtype_0 = box_type.__args__[0]
        subtype_1 = box_type.__args__[1]

        return {
            pack_value(k, subtype_0): pack_value(v, subtype_1)
            for k, v in value.items()
        }

    return value


def is_compatible(value, box_type):
    try:
        return isinstance(value, box_type)
    except TypeError:
        pass

    if box_type is Any:
        return True

    if isinstance(box_type, TypeVar):
        return True

    if is_generic_alias(box_type, (Union,)) and any(
        map(
            lambda arg: is_compatible(value, arg),
            box_type.__args__
        )
    ):
        return True

    if is_generic_alias(box_type, (list, List)) and isinstance(value, list):
        subtype = box_type.__args__[0]

        return all(
            map(
                lambda x: is_compatible(x, subtype),
                value
            )
        )

    if is_generic_alias(box_type, (dict, Dict)) and isinstance(value, dict):
        subtype_0 = box_type.__args__[0]
        subtype_1 = box_type.__args__[1]

        return all(
            map(
                lambda pair: is_compatible(pair[0], subtype_0) and is_compatible(pair[1], subtype_1),
                value.items()
            )
        )

    return False


def getattr_or_default(obj, k, default=None):
    if hasattr(obj, k):
        return getattr(obj, k)
    else:
        return default



def validate(name, o: Options, k, v):
    v = _set_default(o, k, v)
    v = _convert(o, k, v)
    v = _check_types(name, o, k, v)

    v = _validate_allowed(name, o, k, v)
    v = _validate_min_value(name, o, k, v)
    v = _validate_max_value(name, o, k, v)
    v = _validate_min_length(name, o, k, v)
    v = _validate_max_length(name, o, k, v)
    v = _validate_size(name, o, k, v)
    v = _walk_validators(name, o, k, v)

    return v


def _set_default(o: Options, k, v):
    if o.default is None:
        return v

    if v is None:
        v = o.default

        if v is not None:
            if callable(v):
                v = v()
    return v


def _convert(o: Options, k, v):
    if o.parser and not is_compatible(v, o.get_type()):
        converted = o.parser(v)

        if converted is not None:
            v = converted

    return v


def _check_types(name, o: Options, k, v):
    if not is_compatible(v, o.get_type()):
        raise ValidationError(f"Field `{name}#{k}`: {o.get_type()} is not compatible with value `{v}`:{type(v)}")

    return v


def _validate_allowed(name, o: Options, k, v):
    if o.allowed is None:
        return v

    allowed = o.allowed

    if callable(o.allowed):
        allowed = o.allowed()

    if allowed and v not in allowed:
        raise ValidationError(f"Field `{name}#{k}`: value `{v}` is not allowed. Allowed vs: `{allowed}`")

    return v


def _validate_min_length(name, o: Options, k, v):
    if o.min_length is None:
        return v

    min_length = o.min_length

    if callable(min_length):
        min_length = min_length()

    if min_length is not None and len(v) < min_length:
        raise ValidationError(f"Field `{name}#{k}`: len(`{v}`) is less than required")

    return v


def _validate_max_length(name, o: Options, k, v):
    if o.max_length is None:
        return v

    max_length = o.max_length

    if callable(max_length):
        max_length = max_length()

    if max_length is not None and len(v) > max_length:
        raise ValidationError(f"Field `{name}#{k}`: len(`{v}`) is greater than required")

    return v


def _validate_min_value(name, o: Options, k, v):
    if o.min_value is None:
        return v

    min_value = o.min_value

    if callable(min_value):
        min_value = min_value()

    if min_value is not None and v < min_value:
        raise ValidationError(f"Field `{name}#{k}`: value `{v}` is less than required")

    return v


def _validate_max_value(name, o: Options, k, v):
    if o.max_value is None:
        return v

    max_value = o.max_value

    if callable(max_value):
        max_value = max_value()

    if max_value is not None and v > max_value:
        raise ValidationError(f"Field `{name}#{k}`: value `{v}` is greater than required")

    return v


def _validate_size(name, o: Options, k, v):
    if o.size is None:
        return v

    size = o.size

    if callable(size):
        size = size()

    if size is not None and size != len(v):
        raise ValidationError(f"Field `{name}#{k}`: len(`{v}`) is not equal `{size}`")

    return v


def _walk_validators(name, o: Options, k, v):
    if o.validators is None:
        return v

    validators = o.validators

    if validators:
        for validator in validators:
            v = validator(name, k, v)

    return v


def _replace_init(cls, strip_unknown=False):
    def __init__(self, **kwargs) -> None:
        mapped, unknown_fields = _map(cls, kwargs)
        _strip_unknown(cls, unknown_fields, strip_unknown=strip_unknown)

        get = mapped.get

        for k, o in self.__validate_it__options__.items():
            v = get(k)
            setattr(self, k, v)

    cls.__init__ = __init__


def _replace_setattr(cls):
    origin = cls.__setattr__

    def __setattr__(self, key, value):
        o = self.__validate_it__options__[key]

        auto_pack = o.auto_pack

        if callable(auto_pack):
            auto_pack = auto_pack()

        if auto_pack:
            pack_function = o.packer
            value = pack_function(value, o.get_type())

        value = validate(self.__class__.__name__, o, key, value)

        origin(self, key, value)

    cls.__setattr__ = __setattr__


def _map(cls, data):
    enable_map = hasattr(cls, "__validate_it__enable_map__")

    def key_or_alias_value(key, alias):
        if not enable_map:
            to_check = [key]
        else:
            to_check = [key, alias]

        for k in to_check:
            try:
                item = data[k]
                del data[k]
                return item
            except KeyError:
                continue
        else:
            return None

    return {
        key: key_or_alias_value(key, value.alias)
        for key, value in cls.__validate_it__options__.items()
    }, data


def _strip_unknown(cls, unknown, strip_unknown=False):
    if not strip_unknown and len(unknown):
        raise ValidationError(f"{cls}.__new__() got an unexpected keyword arguments {unknown.keys()}")


def _set_options(cls):
    if not hasattr(cls, "__validate_it__options__"):
        cls.__validate_it__options__ = {}

    _keys = set()

    attributes = getmembers(
        cls, lambda _field: not isroutine(_field) and not isclass(_field)
    )

    for key, value in attributes:
        if not key.startswith("__") and not key.endswith("__"):
            if isinstance(value, Options):
                cls.__validate_it__options__[key] = value
            else:
                cls.__validate_it__options__[key] = Options(default=value)

    if hasattr(cls, '__annotations__'):
        for key, _type in cls.__annotations__.items():
            if key not in cls.__validate_it__options__.keys():
                cls.__validate_it__options__[key] = Options()

    if any(
        map(
            lambda x: x.alias,
            cls.__validate_it__options__.values()
        )
    ):
        setattr(cls, "__validate_it__enable_map__", True)


def _set_options_type(cls):
    if hasattr(cls, '__annotations__'):
        for key, _type in cls.__annotations__.items():
            cls.__validate_it__options__[key].set_type(_type)


def _set_options_required(cls):
    if hasattr(cls, '__annotations__'):
        for key, _type in cls.__annotations__.items():

            if hasattr(_type, "__origin__") and _type.__origin__ == Union and None in _type.__args__:
                cls.__validate_it__options__[key].required = False


def _set_options_type_any(cls):
    for key, options in cls.__validate_it__options__.items():
        if not options.get_type():
            options.set_type(Any)


def _init_schema(cls, strip_unknown=False):
    _set_options(cls)
    _set_options_type(cls)
    _set_options_required(cls)
    _set_options_type_any(cls)

    if not hasattr(cls, '__validate_it__init_replaced__'):
        _replace_init(cls, strip_unknown)
        _replace_setattr(cls)


def _expected_name(instance, name):
    if name in instance.__validate_it__options__.keys():
        rename = instance.__validate_it__options__[name].rename

        if rename:
            return rename

    return name


def to_dict(instance) -> dict:
    _data = {}

    for k, o in instance.__validate_it__options__.items():
        if o.required and hasattr(instance, k):
            value = getattr(instance, k)

            _value = unpack_value(value, o.get_type())

            if _value is not None:
                if o.serializer:
                    _value = o.serializer(_value)

                _data[_expected_name(instance, k)] = _value

    return _data


def clone(cls, strip_unknown=False, exclude=None, include=None, add: List[Tuple[str, Type, Options]] = None):
    if exclude and include:
        raise ValueError(f"{cls}: Cannot specify both exclude and include")

    _dict = {
        "__validate_it__options__": {}
    }

    _drop = set()

    if not hasattr(cls, "__validate_it__options__"):
        raise TypeError(f"Cloned class {cls} must be schema")

    for k, v in cls.__dict__.items():
        if k not in ["__validate_it__options__"] + list(cls.__validate_it__options__.keys()):
            _dict[k] = v

    if include:
        include = set(include)
        _all = set(cls.__validate_it__options__.keys())

        _drop = _all - include

    if exclude:
        _drop = set(exclude)

    for k, o in cls.__validate_it__options__.items():
        if k not in _drop:
            _dict["__validate_it__options__"][k] = o

    if add:
        for k, t, o in add:
            o.set_type(t)
            _dict["__validate_it__options__"][k] = o

    new_cls = type(
        f"DynamicCloneOf{cls.__name__}_{uuid.uuid4().hex}", cls.__bases__, _dict
    )

    return new_cls


__all__ = [
    "to_dict",
    "representation",
    "clone",
    "pack_value"
]
