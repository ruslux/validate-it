import sys
import uuid
from typing import Union, List, Tuple, Type, Dict

from validate_it.options import Options


def _is_generic_alias(t, classes):
    if not isinstance(classes, (list, tuple)):
        classes = (classes,)
    return hasattr(t, '__origin__') and t.__origin__ in classes


def _repr(t, o):
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

    if issubclass(t, Schema):
        return value.to_dict()

    return value


def _wrap(value, t):
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

    if issubclass(t, Schema) and _is_compatible(value, dict):
        return t.from_dict(value)

    return value


def _is_compatible(value, t):
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

    if issubclass(t, Schema) and _is_compatible(value, dict):
        return True

    return isinstance(value, t)


def getattr_or_default(obj, k, default=None):
    if hasattr(obj, k):
        return getattr(obj, k)
    else:
        return default


class Schema:
    def _set_defaults(self, kwargs):
        for k, o in self.__options__.items():
            if kwargs.get(k) is None and o.default is not None:
                if callable(o.default):
                    kwargs[k] = o.default()
                else:
                    kwargs[k] = o.default

        return kwargs

    def _convert(self, kwargs):
        for k, t in self.__annotations__.items():
            if not _is_compatible(kwargs.get(k), t) and self.__options__[k].parser:

                converted = self.__options__[k].parser(kwargs.get(k))

                if converted is not None:
                    kwargs[k] = converted

        return kwargs

    def _check_types(self, kwargs):
        for k, t in self.__annotations__.items():
            if not _is_compatible(kwargs.get(k), t):
                raise TypeError(f"Field `{k}`: {t} is not compatible with value `{kwargs.get(k)}`")

        return kwargs

    @classmethod
    def _get_options(cls):
        _options = {}

        for k, t in cls.__annotations__.items():
            value = getattr_or_default(cls, k)

            if isinstance(value, Options):
                _options[k] = value
            else:
                _options[k] = Options(default=value)

            if hasattr(t, '__origin__') and t.__origin__ == Union and None in t.__args__:
                _options[k].required = False

        if hasattr(cls, '__cloned_options__'):
            for k, o in cls.__cloned_options__.items():
                _options[k] = o

        return _options

    def _set_options(self):
        if not hasattr(self, '__options__'):
            self.__options__ = self.__class__._get_options()

    def _clear_options(self):
        for k, v in self.__annotations__.items():
            value = getattr_or_default(self, k)

            if isinstance(value, Options):
                setattr(self, k, value.default)

    def __init__(self, **kwargs) -> None:
        self._set_options()
        self._clear_options()

        try:
            assert self.__annotations__.keys() == self.__options__.keys()
        except AssertionError:
            print(self.__annotations__, self.__options__)

        # use options alias
        kwargs = self._map(kwargs)

        # use options default
        kwargs = self._set_defaults(kwargs)

        # use options parser
        kwargs = self._convert(kwargs)

        kwargs = self._check_types(kwargs)

        # use options other
        kwargs = self._validate_allowed(kwargs)
        kwargs = self._validate_min_value(kwargs)
        kwargs = self._validate_max_value(kwargs)
        kwargs = self._validate_min_length(kwargs)
        kwargs = self._validate_max_length(kwargs)
        kwargs = self._validate_size(kwargs)
        kwargs = self._walk_validators(kwargs)

        for k, v in kwargs.items():
            if k in self.__annotations__.keys():
                t = self.__annotations__[k]
                setattr(self, k, _wrap(v, t))

    @classmethod
    def representation(cls):
        _options = cls._get_options()

        return {
            'schema': {
                k: _repr(t, _options[k])
                for k, t in cls.__annotations__.items()
            }
        }

    class Meta:
        strip_unknown = False

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
    def from_dict(cls, data: dict):
        return cls(**data)

    def _expected_name(self, name):
        if name in self.__options__.keys():
            rename = self.__options__[name].rename

            if rename:
                return rename

        return name

    def to_dict(self) -> dict:
        _data = {}

        for k in self.__annotations__.keys():
            if self.__options__[k].required and hasattr(self, k):
                t = self.__annotations__[k]
                value = getattr(self, k)

                _data[self._expected_name(k)] = _unwrap(value, t)

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

        for k, v in cls.__dict__.items():
            if k not in ['__annotations__', '__options__']:
                _dict[k] = v

        if include:
            include = set(include)
            _all = set(cls.__annotations__.keys())

            _drop = _all - include

        if exclude:
            _drop = set(exclude)

        for k in cls.__annotations__.keys():
            if k not in _drop:
                _dict['__annotations__'][k] = cls.__annotations__[k]

        if add:
            for k, t, o in add:
                _dict['__annotations__'][k] = t
                _dict['__cloned_options__'][k] = o
                _dict[k] = o.default

        new_cls = type(
            f"DynamicCloneOf{cls.__name__}{uuid.uuid4().hex}", cls.__bases__, _dict
        )

        return new_cls

    def _validate_allowed(self, kwargs):
        for k, v in self.__annotations__.items():
            allowed = self.__options__[k].allowed

            if callable(allowed):
                allowed = allowed()

            if allowed and kwargs.get(k) not in allowed:
                raise ValueError(f"Field `{k}`: value `{kwargs.get(k)}` is not allowed. Allowed values: `{allowed}`")

        return kwargs

    def _validate_min_length(self, kwargs):
        for k, v in self.__annotations__.items():
            min_length = self.__options__[k].min_length

            if callable(min_length):
                min_length = min_length()

            if min_length is not None and len(kwargs.get(k)) < min_length:
                raise ValueError(f"Field `{k}`: len(`{kwargs.get(k)}`) is less than required")

        return kwargs

    def _validate_max_length(self, kwargs):
        for k, v in self.__annotations__.items():
            max_length = self.__options__[k].max_length

            if callable(max_length):
                max_length = max_length()

            if max_length is not None and len(kwargs.get(k)) > max_length:
                raise ValueError(f"Field `{k}`: len(`{kwargs.get(k)}`) is greater than required")

        return kwargs

    def _validate_min_value(self, kwargs):
        for k, v in self.__annotations__.items():
            min_value = self.__options__[k].min_value

            if callable(min_value):
                min_value = min_value()

            if min_value is not None and kwargs.get(k) < min_value:
                raise ValueError(f"Field `{k}`: value `{kwargs.get(k)}` is less than required")

        return kwargs

    def _validate_max_value(self, kwargs):
        for k, v in self.__annotations__.items():
            max_value = self.__options__[k].max_value

            if callable(max_value):
                max_value = max_value()

            if max_value is not None and kwargs.get(k) > max_value:
                raise ValueError(f"Field `{k}`: value `{kwargs.get(k)}` is greater than required")

        return kwargs

    def _validate_size(self, kwargs):
        for k, v in self.__annotations__.items():
            size = self.__options__[k].size

            if callable(size):
                size = size()

            if size is not None and size != len(kwargs.get(k)):
                raise ValueError(f"Field `{k}`: len(`{kwargs.get(k)}`) is not equal `{size}`")

        return kwargs

    def _walk_validators(self, kwargs):
        for k, v in self.__annotations__.items():
            validators = self.__options__[k].validators

            if validators:
                for validator in validators:
                    validator(kwargs.get(k))

        return kwargs
