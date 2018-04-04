import collections
import typing
from datetime import datetime

import attr

from validate_it.base import Validator
from validate_it.utils import is_none_or_instance_of, validate_belonging, validate_length, validate_amount


@attr.s(slots=True)
class StrictType(Validator):
    _base_type = object
    _description = attr.ib(default='', validator=[attr.validators.instance_of(str)])
    _required = attr.ib(default=False, validator=[attr.validators.instance_of(bool)])
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(object)])
    _only = attr.ib(default=attr.Factory(list), validator=[attr.validators.instance_of(collections.Iterable)])
    _validators = attr.ib(default=attr.Factory(list), validator=[attr.validators.instance_of(collections.Iterable)])

    @property
    def extended_type(self):
        if self.__class__.__name__.lower() == self._base_type.__name__ + 'field':
            return None
        return self.__class__.__name__

    def __attrs_post_init__(self):
        if self._only and self._default is not None:
            if callable(self._default):
                raise TypeError(
                    f"Field {self._field_name} improperly configured: `default` parameter does not allow `callable` "
                    f"when `only` defined"
                )
            if self._default not in self._only:
                raise ValueError(
                    f"Field {self._field_name} improperly configured: `default` parameter not in `only` "
                )

        for _validator in self._validators:
            for _item in self._only:
                _is_valid, _error, _value = _validator(_item, False, False)
                if _error:
                    raise ValueError(
                        f"Field {self._field_name} improperly configured: `only` value {_item} does not pass defined "
                        f"`validator` {_validator}"
                    )

            if self._default is not None:
                _default = self._default() if callable(self._default) else self._default
                raise ValueError(
                    f"Field {self._field_name} improperly configured: `default` value {_default} does not pass defined "
                    f"`validator` {_validator}"
                )

    def representation(self):
        _data = {
            'base_type': self._base_type.__name__,
            'required': self._required
        }

        if self.extended_type:
            _data['extended_type'] = self.extended_type

        if self._description:
            _data['description'] = self._description

        if self._only:
            _data['only'] = self._only

        if self._default and callable(self._default):
            _data['default'] = {
                'type': 'callable',
                'example': self._default()
            }
        elif self._default:
            _data['default'] = self._default

        return _data

    def is_valid(self, value, convert=False, strip_unknown=False):
        _is_valid, _error, value = self.set_defaults(value, convert, strip_unknown)

        if _is_valid:
            _is_valid, _error, value = self.validate_required(value, convert, strip_unknown)

        if _is_valid and value is not None:
            _is_valid, _error, value = self.validate_type(value, convert, strip_unknown)

        if _is_valid and value is not None:
            _is_valid, _error, value = self.validate_only(value, convert, strip_unknown)

        if _is_valid and value is not None:
            _is_valid, _error, value = self.validate_other(value, convert, strip_unknown)

        if _is_valid and value is not None:
            _is_valid, _error, value = self.apply_validators(value, convert, strip_unknown)

        return _is_valid, _error, value

    def set_defaults(self, value, convert, strip_unknown):
        if value is None and self._default is not None:
            if callable(self._default):
                value = self._default()
            else:
                value = self._default

        return True, '', value

    def validate_required(self, value, convert, strip_unknown):
        if self._required and value is None:
            return False, "Value is required", value

        return True, '', value

    def validate_type(self, value, convert, strip_unknown):
        if not isinstance(value, self._base_type) and convert:
            value = self.convert(value)

        if isinstance(value, self._base_type):
            return True, '', value

        return False, "Wrong type", value

    def validate_only(self, value, convert, strip_unknown):
        return validate_belonging(value, self._only)

    def validate_other(self, value, convert, strip_unknown):
        return True, {}, value

    def apply_validators(self, value, convert, strip_unknown):
        for validator in self._validators:
            _is_valid, _error, value = validator(value, convert, strip_unknown)

            if not _is_valid:
                return _is_valid, _error, value

        return True, '', value

    def convert(self, value):
        try:
            value = self._base_type(value)
        except Exception:
            pass

        return value


@attr.s(slots=True)
class BoolField(StrictType):
    """
    Поле для значений типа ``bool``
    """

    _base_type = bool
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(bool)])


@attr.s(slots=True)
class __Number(StrictType):
    def representation(self):
        _data = super().representation()

        if self._max_value:
            _data['max_value'] = self._max_value

        if self._min_value:
            _data['min_value'] = self._min_value

        return _data

    def validate_other(self, value, convert, strip_unknown):
        return validate_amount(value, self._min_value, self._max_value)


@attr.s(slots=True)
class IntField(__Number):
    """
    Поле для значений типа ``int``
    """

    _base_type = int
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(int)])
    _min_value = attr.ib(default=None, validator=[is_none_or_instance_of(int)])
    _max_value = attr.ib(default=None, validator=[is_none_or_instance_of(int)])


@attr.s(slots=True)
class FloatField(__Number):
    """
    Поле для значений типа ``float``
    """

    _base_type = float
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(float)])
    _min_value = attr.ib(default=None, validator=[is_none_or_instance_of(float)])
    _max_value = attr.ib(default=None, validator=[is_none_or_instance_of(float)])


@attr.s(slots=True)
class StrField(StrictType):
    """
    Поле для значений типа ``str``
    """

    _base_type = str
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(str)])
    _min_length = attr.ib(default=None, validator=[is_none_or_instance_of(int)])
    _max_length = attr.ib(default=None, validator=[is_none_or_instance_of(int)])

    def representation(self):
        _data = super().representation()

        if self._max_length:
            _data['max_length'] = self._max_length

        if self._min_length:
            _data['min_length'] = self._min_length

        return _data

    def validate_other(self, value, convert, strip_unknown):
        return validate_length(value, self._min_length, self._max_length)


@attr.s(slots=True)
class ListField(StrictType):
    """
    Поле для значений типа ``list``, который хранит в себе значения типа указанного в ``children_type``

    Например:

    .. code-block:: python

        class Good(Schema):
            price_range = List(
                required=True,
                children_type=Float()
            )

        # prices for different user categories:
        _data = [140.0, 138.0, 130.0]

        _is_valid, _error, _value = Good().is_valid(_data)
        assert _is_valid

    """

    _base_type = list
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(list)])
    _min_length = attr.ib(default=None, validator=[is_none_or_instance_of(int)])
    _max_length = attr.ib(default=None, validator=[is_none_or_instance_of(int)])
    _children_field = attr.ib(default=None, validator=[is_none_or_instance_of(Validator)])

    def validate_length(self, value, convert, strip_unknown):
        return validate_length(value, self._min_length, self._max_length)

    def validate_items(self, value, convert, strip_unknown):
        _errors = {}

        if value:
            for _index, _item in enumerate(value):
                _item_is_valid, _item_error, _item = self._children_field.is_valid(_item, convert, strip_unknown)

                if not _item_is_valid:
                    _errors[_index] = _item_error
                else:
                    value[_index] = _item

        return not bool(_errors), _errors, value

    def validate_other(self, value, convert, strip_unknown):
        _is_valid, _error, value = self.validate_length(value, convert, strip_unknown)

        if _is_valid:
            _is_valid, _error, value = self.validate_items(value, convert, strip_unknown)

        return _is_valid, _error, value

    def representation(self):
        _data = super().representation()

        if self._max_length:
            _data['max_length'] = self._max_length

        if self._min_length:
            _data['min_length'] = self._min_length

        if self._children_field:
            _data['children_field'] = self._children_field.representation()

        return _data


@attr.s(slots=True)
class TupleField(StrictType):
    """
    Поле для значений типа ``tuple``, который хранит в себе значения, которые строго соответсвуют порядку полей,
    указанных в ``fields``.

    Например:

    .. code-block:: python

        HTTP_STATUS_CODES = [200, 201, 404 ..... ]

        class Log(Schema):
            response = Tuple(
                status_code=Int(only=HTTP_STATUS_CODES),
                message=Str()
            )

        _data = {
            'status_code': 200,
            'message': '{"authorized": true}'
        }

        _is_valid, _error, _value = Log().is_valid(_data)
        assert _is_valid

    """

    _base_type = tuple
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(tuple)])
    _elements = attr.ib(default=attr.Factory(list), validator=[attr.validators.instance_of(list)])

    def __attrs_post_init__(self):
        if not self._elements:
            raise TypeError(f"`elements` list must be not empty")

        for _element in self._elements:
            if not isinstance(_element, Validator):
                raise TypeError(f"`elements` element must be `field.Validator` instance")

    def representation(self):
        _data = super().representation()
        _data['elements'] = [_field.representation() for _field in self._elements]

        return _data

    def validate_length(self, value, convert, strip_unknown):
        if len(value) == len(self._elements):
            return True, '', value
        else:
            return False, "Tuple length does not match with value length", value

    def validate_items(self, value, convert, strip_unknown):
        _errors = {}

        value = list(value)

        if value:
            for _index, _field in enumerate(self._elements):
                _item = value[_index]
                _item_is_valid, _item_error, _item = _field.is_valid(_item, convert, strip_unknown)

                if not _item_is_valid:
                    _errors[_index] = _item_error
                else:
                    value[_index] = _item

        return not bool(_errors), _errors, tuple(value)

    def validate_other(self, value, convert, strip_unknown):
        _is_valid, _error, value = self.validate_length(value, convert, strip_unknown)

        if _is_valid:
            _is_valid, _error, value = self.validate_items(value, convert, strip_unknown)

        return _is_valid, _error, value


@attr.s(slots=True)
class DictField(StrictType):
    """
    Поле для значений типа ``dict``, который хранит в себе значения типа указанного в ``children_type``.

    Например:

    .. code-block:: python

        class Character(Schema):
            skills = Dict(
                children_type=Float()
            )

        _data = {
            'str': 1.0,
            'dex': 15.0,
            'int': 2.7
        }

        _is_valid, _error, _value = Character().is_valid(_data)
        assert _is_valid

    """

    _base_type = dict
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(dict)])
    _children_field = attr.ib(default=None, validator=[is_none_or_instance_of(Validator)])

    def representation(self):
        _data = super().representation()

        if self._children_field:
            _data['children_field'] = self._children_field.representation()

        return _data

    def validate_other(self, value, convert, strip_unknown):
        _errors = {}

        if value:
            for _key, _value in value.items():
                self._children_field._field_name = self._field_name
                _item_is_valid, _item_error, _value = self._children_field.is_valid(_value, convert, strip_unknown)

                if not _item_is_valid:
                    _errors[_key] = _item_error
                else:
                    value[_key] = _value

        return not bool(_errors), _errors, value


@attr.s(slots=True)
class DatetimeField(StrictType):
    """
    Поле для значений типа ``datetime``
    """

    _base_type = datetime
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(datetime)])


@attr.s(slots=True)
class Schema(StrictType):
    """
    Наряду с ``AnySchema`` класс ``Schema`` является основным инструментом для валидации документов.

    Для валидации необходимо описать класс-наследник и описать поля документа.

    .. code-block:: python

        class User(Schema):
            username = StrField(required=True)
            password = StrField(required=True)
            books = IntField(required=True)

    и затем проверить документ:

    .. code-block:: python

        _document = {'username': 'Mark Lutz', 'password': 'AwEsOmEpAsSwOrDhAsH', 'books': '14'}

        _is_valid, _error, _document = User().is_valid(_document, convert=True, strip_unknown=False)
        assert _is_valid

    Все доступные поля описаны в модуле ``validation.field`` и несколько полей в ``api.field``
    """
    _base_type = dict
    _cached_fields = {}
    _default = attr.ib(default=None, validator=[is_none_or_instance_of(dict)])
    _required = attr.ib(default=True, validator=[attr.validators.instance_of(bool)])

    @classmethod
    def get_singleton_name(cls, *args, **kwargs):
        return cls.__name__ + '_' + str(cls.get_fields()) + '_' + str(kwargs)

    def representation(self):
        _data = super().representation()
        _data['schema'] = {x: y.representation() for x, y in self.get_fields().items()}
        return _data

    @classmethod
    def get_fields(cls):
        return {k: v for k, v in cls.__dict__.items() if isinstance(v, Validator)}

    @classmethod
    def only_fields(cls, *args: typing.List[str]):
        """
        Создает копию схемы, в которую включены только поля перечисленные в ``*args``

        :param args: List[str]
        :return: cls
        """
        _new = {k: v for k, v in cls.get_fields().items() if k in args}

        return type(cls.__name__, cls.__bases__, _new)

    @classmethod
    def exclude_fields(cls, *args: typing.List[str]):
        """
        Создает копию схемы без полей перечисленных в ``*args``

        :param args: List[str]
        :return: cls
        """
        _new = {k: v for k, v in cls.get_fields().items() if k not in args}

        return type(cls.__name__, cls.__bases__, _new)

    def validate_other(self, value, convert=False, strip_unknown=False):
        _is_valid = True
        _errors = {}

        _value_keys = set(value.keys())
        _schema_keys = set()
        _copy = {}

        for _name, _field in self.get_fields().items():
            _field_is_valid, _error, _value = _field.is_valid(value.get(_name), convert, strip_unknown)

            if not _field_is_valid:
                _errors[_name] = _error
            elif _value is None:
                continue

            _is_valid &= _field_is_valid
            _copy[_name] = _value

            _schema_keys.add(_name)

        if _is_valid:
            if _schema_keys == _value_keys or \
                    (_schema_keys.issubset(_value_keys) and strip_unknown) or \
                    _value_keys.issubset(_schema_keys):
                return _is_valid, {}, _copy
            else:
                for _unknown_item in _value_keys - _schema_keys:
                    _errors[_unknown_item] = "Unknown field"

        return False, _errors, value


SchemaField = Schema


__all__ = [
    'StrictType',
    'BoolField',
    'IntField',
    'FloatField',
    'StrField',
    'ListField',
    'TupleField',
    'DictField',
    'DatetimeField',
    'Schema',
    'SchemaField',
]
