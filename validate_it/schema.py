import uuid
from inspect import getmembers, isroutine, isclass
from typing import Union, List, Tuple, Type, Dict, TypeVar, Any

from validate_it.options import Options


def _is_generic_alias(t, classes):
    if not isinstance(classes, (list, tuple)):
        classes = (classes,)
    return hasattr(t, '__origin__') and t.__origin__ in classes


class SchemaVar:
    def __init__(self, value=None, options=None) -> None:
        self._current_value = value
        self._confirmed_value = None

        self.options = options

    def __get__(self, instance, owner):
        return self._current_value

    def __set__(self, instance, value):
        self._current_value = value


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

    try:
        if issubclass(t, Schema):
            return value.to_dict()
    except TypeError:
        pass

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

    try:
        if issubclass(t, Schema) and _is_compatible(value, dict):
            return t.from_dict(value)
    except TypeError:
        pass

    return value


def _is_compatible(value, t):
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
        for k, o in self.__options__.items():
            if not _is_compatible(kwargs.get(k), o.get_type()) and o.parser:

                converted = o.parser(kwargs.get(k))

                if converted is not None:
                    kwargs[k] = converted

        return kwargs

    def _check_types(self, kwargs):
        for k, o in self.__options__.items():
            if not _is_compatible(kwargs.get(k), o.get_type()):
                raise TypeError(f"Field `{k}`: {o.get_type()} is not compatible with value `{kwargs.get(k)}`")

        return kwargs

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

    def _set_options(self):
        if not hasattr(self, '__options__'):
            self.__options__ = self.__class__._get_options()

    def _set_schema_vars(self):
        for key, options in self.__options__.items():
            if callable(options.default):
                value = options.default()
            else:
                value = options.default

            sv = SchemaVar(value, options)
            setattr(self, key, sv)

    def __init__(self, **kwargs) -> None:
        self._set_options()
        self._set_schema_vars()

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

        for k, o in self.__options__.items():
            v = kwargs.get(k)
            t = self.__options__[k].get_type()
            setattr(self, k, _wrap(v, t))

    @classmethod
    def representation(cls):
        _options = cls._get_options()

        return {
            'schema': {
                k: _repr(o.get_type(), o)
                for k, o in _options.items()
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

        for k, o in self.__options__.items():
            if o.required:
                value = getattr(self, k)

                _unwrapped = _unwrap(value, o.get_type())

                if _unwrapped is not None:
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

    def _validate_allowed(self, kwargs):
        for k, o in self.__options__.items():
            allowed = o.allowed

            if callable(o.allowed):
                allowed = o.allowed()

            if allowed and kwargs.get(k) not in allowed:
                raise ValueError(f"Field `{k}`: value `{kwargs.get(k)}` is not allowed. Allowed values: `{allowed}`")

        return kwargs

    def _validate_min_length(self, kwargs):
        for k, o in self.__options__.items():
            min_length = o.min_length

            if callable(min_length):
                min_length = min_length()

            if min_length is not None and len(kwargs.get(k)) < min_length:
                raise ValueError(f"Field `{k}`: len(`{kwargs.get(k)}`) is less than required")

        return kwargs

    def _validate_max_length(self, kwargs):
        for k, o in self.__options__.items():
            max_length = o.max_length

            if callable(max_length):
                max_length = max_length()

            if max_length is not None and len(kwargs.get(k)) > max_length:
                raise ValueError(f"Field `{k}`: len(`{kwargs.get(k)}`) is greater than required")

        return kwargs

    def _validate_min_value(self, kwargs):
        for k, o in self.__options__.items():
            min_value = o.min_value

            if callable(min_value):
                min_value = min_value()

            if min_value is not None and kwargs.get(k) < min_value:
                raise ValueError(f"Field `{k}`: value `{kwargs.get(k)}` is less than required")

        return kwargs

    def _validate_max_value(self, kwargs):
        for k, o in self.__options__.items():
            max_value = o.max_value

            if callable(max_value):
                max_value = max_value()

            if max_value is not None and kwargs.get(k) > max_value:
                raise ValueError(f"Field `{k}`: value `{kwargs.get(k)}` is greater than required")

        return kwargs

    def _validate_size(self, kwargs):
        for k, o in self.__options__.items():
            size = o.size

            if callable(size):
                size = size()

            if size is not None and size != len(kwargs.get(k)):
                raise ValueError(f"Field `{k}`: len(`{kwargs.get(k)}`) is not equal `{size}`")

        return kwargs

    def _walk_validators(self, kwargs):
        for k, o in self.__options__.items():
            validators = o.validators

            if validators:
                for validator in validators:
                    validator(kwargs.get(k))

        return kwargs
