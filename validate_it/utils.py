from inspect import getmembers, isroutine
from typing import Dict, List, Union, TypeVar, Any


def _is_generic_alias(t, classes):
    if not isinstance(classes, (list, tuple)):
        classes = (classes,)
    return hasattr(t, '__origin__') and t.__origin__ in classes


def _repr(t, o):
    from validate_it import Schema, Options

    _d = {
        'required': o.required,
    }

    if o.default is not None:
        _d['default'] = o.default if not callable(o.default) else 'dynamic'

    if o.min_length is not None:
        _d['min length'] = o.min_length if not callable(o.min_length) else 'dynamic'

    if o.max_length is not None:
        _d['max length'] = o.max_length if not callable(o.max_length) else 'dynamic'

    if o.min_value is not None:
        _d['min value'] = o.min_value if not callable(o.min_value) else 'dynamic'

    if o.max_value is not None:
        _d['max value'] = o.max_value if not callable(o.max_value) else 'dynamic'

    if o.size is not None:
        _d['size'] = o.size if not callable(o.size) else 'dynamic'

    if o.allowed is not None:
        _d['allowed values'] = o.allowed if not callable(o.allowed) else 'dynamic'

    if o.alias is not None:
        _d['search alias'] = o.alias if not callable(o.alias) else 'dynamic'

    if o.rename is not None:
        _d['rename to'] = o.rename if not callable(o.rename) else 'dynamic'

    if _is_generic_alias(t, Union):
        _d.update(
            {
                'type': 'union',
                'nested_types': [
                    _repr(arg, Options())
                    for arg in t.__args__
                ]
            }
        )

    elif _is_generic_alias(t, (list, List)):
        _d.update(
            {
                'type': 'list',
                'nested_type': [
                    _repr(t.__args__[0], Options())
                ]
            }
        )

    elif _is_generic_alias(t, (dict, Dict)):
        _d.update(
            {
                'type': 'dict',
                'key_type': _repr(t.__args__[0], Options()),
                'value_type': _repr(t.__args__[1], Options())
            }
        )

    elif issubclass(t, Schema):
        _d.update(
            {
                'type': 'validate_it.Schema',
                'schema': t.representation()
            }
        )

    elif isinstance(t, list):
        _d.update(
            {
                'type': 'dict',
                'nested_type': 'any'
            }
        )

    elif isinstance(t, dict):
        _d.update(
            {
                'type': 'dict',
                'key_type': 'any',
                'value_type': 'any'
            }
        )

    else:
        _d['type'] = t.__name__

    return _d


def _unwrap(value, t):
    from validate_it import Schema

    if _is_generic_alias(t, Union):
        for arg in t.__args__:
            if _is_compatible(value, arg):
                return _unwrap(value, arg)

    if _is_generic_alias(t, (list, List)) and _is_compatible(value, list):
        return [
            _unwrap(item, t.__args__[0])
            for item in value
        ]

    if _is_generic_alias(t, (dict, Dict)):
        return {
            _unwrap(k, t.__args__[0]): _unwrap(v, t.__args__[1])
            for k, v in value.items()
        }

    try:
        if issubclass(t, Schema):
            return value.to_dict()
    except TypeError:
        pass

    return value


def _wrap(value, t):
    from validate_it import Schema

    if _is_generic_alias(t, Union):
        for arg in t.__args__:
            if _is_compatible(value, arg):
                return _wrap(value, arg)

    if _is_generic_alias(t, (list, List)) and _is_compatible(value, list):
        return [
            _wrap(item, t.__args__[0])
            for item in value
        ]

    if _is_generic_alias(t, (dict, Dict)):
        return {
            _wrap(k, t.__args__[0]): _wrap(v, t.__args__[1])
            for k, v in value.items()
        }

    try:
        if issubclass(t, Schema) and _is_compatible(value, dict):
            result = t.from_dict(value)
            return result
    except TypeError:
        pass

    return value


def _is_compatible(value, t):
    from validate_it import Schema

    if t is Any:
        return True

    if isinstance(t, TypeVar):
        return True

    if _is_generic_alias(t, Union):
        for arg in t.__args__:
            if _is_compatible(value, arg):
                return True

    if _is_generic_alias(t, (list, List)) and _is_compatible(value, list):
        for item in value:
            if not _is_compatible(item, t.__args__[0]):
                return False
        else:
            return True

    if _is_generic_alias(t, (dict, Dict)):
        for k, v in value.items():
            if not _is_compatible(k, t.__args__[0]) or not _is_compatible(v, t.__args__[1]):
                return False
        return True

    try:
        if issubclass(t, Schema) and _is_compatible(value, dict):
            return True
    except TypeError:
        pass

    try:
        return isinstance(value, t)
    except TypeError:
        return False


def getattr_or_default(obj, k, default=None):
    if hasattr(obj, k):
        return getattr(obj, k)
    else:
        return default


def choices_from_enum(cls):
    attributes = getmembers(
        cls,
        lambda _field: not isroutine(_field)
    )

    choices = [
        (value, name.replace("_", " ").lower().capitalize())
        for name, value in attributes
        if not name.startswith("__") and not name.endswith("__")
    ]

    choices.sort(key=lambda x: x[1])

    return tuple(choices)


__all__ = [
    "choices_from_enum"
]
