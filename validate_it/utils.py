import uuid
from inspect import getmembers, isclass, isroutine
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union

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


def _repr(_type, options):
    _dict = {
        "required": options.required,
    }

    if options.default is not None:
        _dict["default"] = options.default if not callable(options.default) else "dynamic"

    if options.min_length is not None:
        _dict["min length"] = options.min_length if not callable(options.min_length) else "dynamic"

    if options.max_length is not None:
        _dict["max length"] = options.max_length if not callable(options.max_length) else "dynamic"

    if options.min_value is not None:
        _dict["min value"] = options.min_value if not callable(options.min_value) else "dynamic"

    if options.max_value is not None:
        _dict["max value"] = options.max_value if not callable(options.max_value) else "dynamic"

    if options.size is not None:
        _dict["size"] = options.size if not callable(options.size) else "dynamic"

    if options.allowed is not None:
        _dict["allowed values"] = options.allowed if not callable(options.allowed) else "dynamic"

    if options.alias is not None:
        _dict["search alias"] = options.alias if not callable(options.alias) else "dynamic"

    if options.rename is not None:
        _dict["rename to"] = options.rename if not callable(options.rename) else "dynamic"

    if is_generic_alias(_type, (Union,)):
        _dict.update(
            {
                "type": "union",
                "nested_types": [
                    _repr(arg, Options())
                    for arg in _type.__args__
                ]
            }
        )

    elif is_generic_alias(_type, (list, List)):
        _dict.update(
            {
                "type": "list",
                "nested_type": [
                    _repr(_type.__args__[0], Options())
                ]
            }
        )

    elif is_generic_alias(_type, (dict, Dict)):
        _dict.update(
            {
                "type": "dict",
                "key_type": _repr(_type.__args__[0], Options()),
                "value_type": _repr(_type.__args__[1], Options())
            }
        )

    elif hasattr(_type, '__validate_it__options__'):
        _dict.update(
            {
                "type": "validate_it.schema",
                "schema": representation(_type)
            }
        )

    elif isinstance(_type, list):
        _dict.update(
            {
                "type": "dict",
                "nested_type": "any"
            }
        )

    elif isinstance(_type, dict):
        _dict.update(
            {
                "type": "dict",
                "key_type": "any",
                "value_type": "any"
            }
        )

    else:
        _dict["type"] = _type.__name__

    return _dict


def representation(cls):
    return {
        "schema": {
            key: _repr(options.get_type(), options)
            for key, options in cls.__validate_it__options__.items()
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
        if "__args__" in box_type.__dict__ and box_type.__dict__["__args__"]:
            subtype = box_type.__args__[0]

            return [
                unpack_value(item, subtype)
                for item in value
            ]
        else:
            return value

    if is_generic_alias(box_type, (dict, Dict)) and isinstance(value, dict):
        if "__args__" in box_type.__dict__ and box_type.__dict__["__args__"]:
            subtype_0 = box_type.__args__[0]
            subtype_1 = box_type.__args__[1]

            return {
                unpack_value(key, subtype_0): unpack_value(value, subtype_1)
                for key, value in value.items()
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

    if is_generic_alias(box_type, (tuple, Tuple)) and isinstance(value, tuple):
        if len(value) != len(box_type.__args__):
            return False

        return all(
            map(
                lambda x: is_compatible(x[0], x[1]),
                zip(value, box_type.__args__)
            )
        )

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


def getattr_or_default(obj, key, default=None):
    if hasattr(obj, key):
        return getattr(obj, key)
    else:
        return default


def validate(name, options: Options, key, value):
    value = _set_default(options, key, value)
    value = _convert(options, key, value)
    value = _check_types(name, options, key, value)

    value = _validate_allowed(name, options, key, value)
    value = _validate_min_value(name, options, key, value)
    value = _validate_max_value(name, options, key, value)
    value = _validate_min_length(name, options, key, value)
    value = _validate_max_length(name, options, key, value)
    value = _validate_size(name, options, key, value)
    value = _walk_validators(name, options, key, value)

    return value


def _set_default(options: Options, key, value):
    if options.default is None:
        return value

    if value is None:
        value = options.default

        if value is not None:
            if callable(value):
                value = value()
    return value


def _convert(options: Options, key, value):
    if options.parser and not is_compatible(value, options.get_type()):
        converted = options.parser(value)

        if converted is not None:
            value = converted

    return value


def _check_types(name, options: Options, key, value):
    if not is_compatible(value, options.get_type()):
        raise ValidationError(
            f"Field `{name}#{key}`: {options.get_type()} is not compatible with value `{value}`:{type(value)}"
        )

    return value


def _validate_allowed(name, options: Options, key, value):
    if options.allowed is None:
        return value

    allowed = options.allowed

    if callable(options.allowed):
        allowed = options.allowed()

    if allowed and value not in allowed:
        raise ValidationError(
            f"Field `{name}#{key}`: value `{value}` is not allowed. Allowed vs: `{allowed}`"
        )

    return value


def _validate_min_length(name, options: Options, key, value):
    if options.min_length is None:
        return value

    min_length = options.min_length

    if callable(min_length):
        min_length = min_length()

    if min_length is not None and len(value) < min_length:
        raise ValidationError(f"Field `{name}#{key}`: len(`{value}`) is less than required")

    return value


def _validate_max_length(name, options: Options, key, value):
    if options.max_length is None:
        return value

    max_length = options.max_length

    if callable(max_length):
        max_length = max_length()

    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"Field `{name}#{key}`: len(`{value}`) is greater than required")

    return value


def _validate_min_value(name, options: Options, key, value):
    if options.min_value is None:
        return value

    min_value = options.min_value

    if callable(min_value):
        min_value = min_value()

    if min_value is not None and value < min_value:
        raise ValidationError(f"Field `{name}#{key}`: value `{value}` is less than required")

    return value


def _validate_max_value(name, options: Options, key, value):
    if options.max_value is None:
        return value

    max_value = options.max_value

    if callable(max_value):
        max_value = max_value()

    if max_value is not None and value > max_value:
        raise ValidationError(f"Field `{name}#{key}`: value `{value}` is greater than required")

    return value


def _validate_size(name, options: Options, key, value):
    if options.size is None:
        return value

    size = options.size

    if callable(size):
        size = size()

    if size is not None and size != len(value):
        raise ValidationError(f"Field `{name}#{key}`: len(`{value}`) is not equal `{size}`")

    return value


def _walk_validators(name, options: Options, key, value):
    if options.validators is None:
        return value

    validators = options.validators

    if validators:
        for validator in validators:
            value = validator(name, key, value)

    return value


def _replace_init(cls, strip_unknown=False):
    def __init__(self, **kwargs) -> None:
        mapped, unknown_fields = _map(cls, kwargs)
        _strip_unknown(cls, unknown_fields, strip_unknown=strip_unknown)

        get = mapped.get

        for key, options in self.__validate_it__options__.items():
            value = get(key)
            setattr(self, key, value)

        if hasattr(cls, '__validate_it__post_init__'):
            self.__validate_it__post_init__()

    cls.__init__ = __init__


def _replace_setattr(cls):
    origin = cls.__setattr__

    def __setattr__(self, key, value):
        options = self.__validate_it__options__[key]

        auto_pack = options.auto_pack

        if callable(auto_pack):
            auto_pack = auto_pack()

        if auto_pack:
            pack_function = options.packer
            value = pack_function(value, options.get_type())

        value = validate(self.__class__.__name__, options, key, value)

        origin(self, key, value)

    cls.__setattr__ = __setattr__


def _map(cls, data):
    enable_map = hasattr(cls, "__validate_it__enable_map__")

    def key_or_alias_value(key, alias):
        if not enable_map:
            to_check = [key]
        else:
            to_check = [key, alias]

        for key in to_check:
            try:
                item = data[key]
                del data[key]
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

    for key, options in instance.__validate_it__options__.items():
        if options.required and hasattr(instance, key):
            value = getattr(instance, key)

            _value = unpack_value(value, options.get_type())

            if _value is not None:
                if options.serializer:
                    _value = options.serializer(_value)

                _data[_expected_name(instance, key)] = _value

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

    for key, value in cls.__dict__.items():
        if key not in ["__validate_it__options__"] + list(cls.__validate_it__options__.keys()):
            _dict[key] = value

    if include:
        include = set(include)
        _all = set(cls.__validate_it__options__.keys())

        _drop = _all - include

    if exclude:
        _drop = set(exclude)

    for key, options in cls.__validate_it__options__.items():
        if key not in _drop:
            _dict["__validate_it__options__"][key] = options

    if add:
        for key, _type, options in add:
            options.set_type(_type)
            _dict["__validate_it__options__"][key] = options

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
