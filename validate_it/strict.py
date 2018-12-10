import collections
from dataclasses import dataclass, field
from datetime import datetime
from inspect import isclass
from typing import Union, List, Callable, Tuple, Any, Type, Dict

from validate_it.base import Validator
from validate_it.utils import choices_from_enum


def update_definitions(instance, schema, definitions):
    if "definitions" in schema:
        definitions.update(schema["definitions"])
        del schema["definitions"]

    definitions_name = instance.jsonschema_options.get(
        "title",
    )

    if not definitions_name and hasattr(instance, "choices") and instance.choices:
        if isclass(instance.choices):
            definitions_name = instance.choices.__name__
        else:
            definitions_name = instance.choices.__class__.__name__

    if not definitions_name:
        definitions_name = instance.field_name

    if not definitions_name:
        definitions_name = instance.__class__.__name__

    if definitions_name not in definitions.keys():
        del schema["title"]
        definitions[definitions_name] = schema

    return {
        "title": definitions_name,
        "$ref": f"#/definitions/{definitions_name}"
    }


@dataclass
class StrictType(Validator):
    required: bool = False
    default: Union[object, None] = None
    only: Union[Callable, list] = field(default_factory=list)
    enum: Any = None
    choices: List[Tuple[Any, Any]] = None
    validators: List[Callable] = field(default_factory=list)

    def __post_init__(self):
        if self.enum and self.enum is not None:
            if self.choices:
                raise TypeError(
                    f"Field {self.field_name} improperly configured: "
                    f"`choices` parameter must be empty when `enum` defined"
                )
            if self.only:
                raise TypeError(
                    f"Field {self.field_name} improperly configured: "
                    f"`only` parameter must be empty when `enum` defined"
                )
            self.choices = choices_from_enum(self.enum)

        if self.choices:
            if self.only:
                raise TypeError(
                    f"Field {self.field_name} improperly configured: "
                    f"`only` parameter must be empty when `choices` defined"
                )
            self.only = [choice[0] for choice in self.choices]

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        _data["required"] = self.required

        if self.description:
            _data["description"] = self.description

        if self.only and callable(self.only):
            _data["only"] = {"type": "callable", "example": self.only()}
        elif self.only:
            _data["only"] = self.only

        if self.default and callable(self.default):
            _data["default"] = {"type": "callable", "example": self.default()}
        elif self.default:
            _data["default"] = self.default

        return _data

    def validate_it(self, value, **kwargs) -> Tuple[Any, Any]:
        """
        :param value:
        :param convert=False:
        :param strip_unknown=False:
        :param meta=None:
        :return:
        """
        _error, value = self.set_defaults(value, **kwargs)

        if not _error:
            _error, value = self.validate_required(value, **kwargs)

        if not _error and value is not None:
            _error, value = self.validate_type(value, **kwargs)

        if not _error and value is not None:
            _error, value = self.validate_only(value, **kwargs)

        if not _error and value is not None:
            _error, value = self.validate_other(value, **kwargs)

        if not _error and value is not None:
            _error, value = self.apply_validators(value, **kwargs)

        return _error, value

    def set_defaults(self, value, **kwargs) -> Tuple[str, Any]:
        if value is None and self.default is not None:
            if callable(self.default) and self.default not in [dict, list]:
                value = self.default(value, kwargs.get("meta", None))
            elif callable(self.default):
                value = self.default()
            else:
                value = self.default

        return "", value

    def validate_required(self, value, **kwargs) -> Tuple[str, Any]:
        if self.required and value is None:
            return "Value is required", value

        return "", value

    def validate_type(self, value, **kwargs) -> Tuple[Any, Any]:
        if not isinstance(value, self.base_type) and kwargs.get("convert", False):
            value = self.convert(value)

        if self.base_type is int and isinstance(value, bool) and kwargs.get("convert", False):
            value = self.convert(value)

        if isinstance(value, self.base_type):
            return "", value

        return "Wrong type", value

    def validate_only(self, value, **kwargs) -> Tuple[str, Any]:
        only = self.only

        if callable(self.only):
            only = self.only(value, kwargs.get("meta", None))

        if only and value not in only:
            return f"Value must belong to `{only}`", value
        else:
            return "", value

    def validate_other(self, value, **kwargs) -> Tuple[Any, Any]:
        return {}, value

    def apply_validators(self, value, **kwargs) -> Tuple[Any, Any]:
        _error = ""

        for validator in self.validators:
            _error, value = validator(value, **kwargs)

        return _error, value

    def convert(self, value, **kwargs):
        try:
            value = self.base_type(value)
        except Exception:
            pass

        return value

    def get_jsonschema_type(self):
        return super().get_jsonschema_type()

    def jsonschema(self, definitions=None, **kwargs):
        _schema = super().jsonschema(definitions, **kwargs)

        if self.only:
            _type = self.get_jsonschema_type()

            if self.choices:
                _map = {
                    _choice[0]: _choice[1]
                    for _choice in self.choices
                }
            else:
                _map = {
                    _value: _value
                    for _value in self.only
                }

            _items = list(_map.items())
            _items.sort(key=lambda x: x[0])

            _schema['anyOf'] = [
                {
                    "type": _type,
                    "enum": [
                        _key
                    ],
                    "title": _value
                } for _key, _value in _items
            ]

        return _schema


@dataclass
class BoolField(StrictType):
    """
    Поле для значений типа ``bool``
    """

    base_type: Type = bool
    default: Union[bool, None] = None

    def get_jsonschema_type(self):
        return "boolean"


@dataclass
class AmountMixin:
    min_value: Union[Any, None] = None
    max_value: Union[Any, None] = None

    def validate_amount(self, value, **kwargs) -> Tuple[Union[Any, str], Any]:
        if self.min_value is not None:
            if value < self.min_value:
                return f"Value must be greater than `{self.min_value}`", value

        if self.max_value is not None:
            if value > self.max_value:
                return f"Value must be lesser than `{self.max_value}`", value

        return {}, value


@dataclass
class __Number(AmountMixin, StrictType):
    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        if self.max_value is not None:
            _data["max_value"] = self.max_value

        if self.min_value is not None:
            _data["min_value"] = self.min_value

        return _data

    def validate_other(self, value, **kwargs) -> Tuple[Any, Any]:
        return self.validate_amount(value, **kwargs)

    def jsonschema(self, definitions=None, **kwargs):
        _schema = super().jsonschema(definitions, **kwargs)

        if self.min_value is not None:
            _schema["minimum"] = self.min_value

        if self.max_value is not None:
            _schema["maximum"] = self.max_value

        return _schema


@dataclass
class IntField(__Number):
    """
    Поле для значений типа ``int``
    """

    base_type: Type = int
    default: Union[int, None] = None
    min_value: Union[int, None] = None
    max_value: Union[int, None] = None

    def get_jsonschema_type(self):
        return "integer"


@dataclass
class FloatField(__Number):
    """
    Поле для значений типа ``float``
    """

    base_type: Type = float
    default: Union[float, None] = None
    min_value: Union[float, None] = None
    max_value: Union[float, None] = None

    def get_jsonschema_type(self):
        return "number"


@dataclass
class LengthMixin:
    min_length: Union[int, None] = None
    max_length: Union[int, None] = None

    def validate_length(self, value, **kwargs) -> Tuple[Union[Any, str], Any]:
        if self.min_length is not None:
            if len(value) < self.min_length:
                return f"Value length must be greater than `{self.min_length}`", value

        if self.max_length is not None:
            if len(value) > self.max_length:
                return f"[Value length must be lesser than `{self.max_length}`", value

        return {}, value


@dataclass
class StrField(LengthMixin, StrictType):
    """
    Поле для значений типа ``str``
    """

    base_type: Type = str
    default: Union[str, None] = None

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        if self.max_length is not None:
            _data["max_length"] = self.max_length

        if self.min_length is not None:
            _data["min_length"] = self.min_length

        return _data

    def validate_other(self, value, **kwargs) -> Tuple[Any, Any]:
        return self.validate_length(value, **kwargs)

    def get_jsonschema_type(self):
        return "string"

    def jsonschema(self, definitions=None, **kwargs):
        _schema = super().jsonschema(definitions, **kwargs)

        if self.min_length is not None:
            _schema["minLength"] = self.min_length

        if self.max_length is not None:
            _schema["maxLength"] = self.max_length

        return _schema


@dataclass
class ListField(LengthMixin, StrictType):
    """
    Поле для значений типа ``list``, который хранит в себе значения типа указанного в ``nested``

    Например:

    .. code-block:: python

        class Good(Schema):
            price_range = List(
                required=True,
                nested=Float()
            )

        # prices for different user categories:
        _data = [140.0, 138.0, 130.0]

        _errors, _value = Good().validate_it(_data)
        assert not _errors

    """

    base_type: Type = list
    default: Union[List[Any], None] = None
    nested: Union[Validator, None] = None

    def validate_items(self, value, **kwargs) -> Tuple[Any, Any]:
        _errors = {}

        if value:
            for _index, _item in enumerate(value):
                _item_error, _item = self.nested.validate_it(_item, **kwargs)

                if _item_error:
                    _errors[_index] = _item_error
                else:
                    value[_index] = _item

        return _errors, value

    def validate_other(self, value, **kwargs) -> Tuple[Any, Any]:
        _error, value = self.validate_length(value, **kwargs)

        if not _error:
            _error, value = self.validate_items(value, **kwargs)

        return _error, value

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        if self.max_length:
            _data["max_length"] = self.max_length

        if self.min_length:
            _data["min_length"] = self.min_length

        if self.nested:
            _data["nested"] = self.nested.representation(**kwargs)

        return _data

    def convert(self, value, **kwargs):
        if not isinstance(value, collections.MutableSequence) and not isinstance(value, tuple):
            value = [value]

        return super().convert(value, **kwargs)

    def jsonschema(self, definitions=None, **kwargs):
        _schema = super().jsonschema(definitions, **kwargs)

        if self.min_length is not None:
            _schema["minItems"] = self.min_length

        if self.max_length is not None:
            _schema["maxItems"] = self.max_length

        _nested_schema = self.nested.jsonschema(definitions=definitions)

        if isinstance(self.nested, Schema) or "anyOf" in _nested_schema:
            _schema['item'] = update_definitions(self.nested, _nested_schema, definitions)
        else:
            _schema['item'] = _nested_schema

        return _schema

    def get_jsonschema_type(self):
        return "array"


@dataclass
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

        _errors, _value = Log().validate_it(_data)
        assert not _errors

    """

    base_type: Type = tuple
    default: Union[tuple, None] = None
    nested: List[Validator] = field(default_factory=list)

    def __post_init__(self):
        for _element in self.nested:
            if not isinstance(_element, Validator):
                raise TypeError(f"`nested` element must be `field.Validator` instance")

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)
        _data["nested"] = [_field.representation(**kwargs) for _field in self.nested]

        return _data

    def validate_length(self, value, **kwargs) -> Tuple[str, Any]:
        if len(value) == len(self.nested):
            return "", value
        else:
            return "Tuple length does not match with value length", value

    def validate_items(self, value, **kwargs) -> Tuple[Any, Any]:
        _errors = {}

        value = list(value)

        if value:
            for _index, _field in enumerate(self.nested):
                _item = value[_index]
                _item_error, _item = _field.validate_it(_item, **kwargs)

                if _item_error:
                    _errors[_index] = _item_error
                else:
                    value[_index] = _item

        return _errors, tuple(value)

    def validate_other(self, value, **kwargs) -> Tuple[Any, Any]:
        if not self.nested:
            return {}, value

        _error, value = self.validate_length(value, **kwargs)

        if not _error:
            _error, value = self.validate_items(value, **kwargs)

        return _error, value

    def get_jsonschema_type(self):
        return "array"


@dataclass
class DictField(StrictType):
    """
    Поле для значений типа ``dict``, который хранит в себе значения типа указанного в ``nested``.

    Например:

    .. code-block:: python

        class Character(Schema):
            skills = Dict(
                nested=Float()
            )

        _data = {
            'str': 1.0,
            'dex': 15.0,
            'int': 2.7
        }

        _errors, _value = Character().validate_it(_data)
        assert not _errors

    """

    base_type: Type = dict
    default: Union[Callable, Dict[str, Validator], None] = None
    key: Union[Validator, None] = None
    nested: Union[Validator, None] = None

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        if self.nested:
            _data["nested"] = self.nested.representation(**kwargs)

        return _data

    def validate_key(self, key, **kwargs):
        return self.key.validate_it(key, **kwargs)

    def validate_nested(self, value, **kwargs):
        return self.nested.validate_it(value, **kwargs)

    def validate_other(self, value, **kwargs) -> Tuple[Any, Any]:
        _errors = {}
        _new_value = {}
        if value:
            for _key, _value in value.items():
                if self.key:
                    self.key.field_name = self.field_name
                    _key_error, _key = self.validate_key(_key, **kwargs)

                    if _key_error:
                        _errors[_key] = _errors.get(_key, {})
                        _errors[_key]['key'] = _key_error

                if self.nested:
                    self.nested.field_name = self.field_name
                    _value_error, _value = self.validate_nested(_value, **kwargs)

                    if _value_error:
                        _errors[_key] = _errors.get(_key, {})
                        _errors[_key]['value'] = _value_error

                if not _errors:
                    _new_value[_key] = _value

        return _errors, _new_value


@dataclass
class DatetimeField(StrictType):
    """
    Поле для значений типа ``datetime``
    """

    base_type: Type = datetime
    default: Union[datetime, None] = None
    parser: Union[Callable, None] = None

    def get_jsonschema_type(self):
        return "string"

    def get_jsonschema_format(self):
        return self.jsonschema_options.get("format", "date-time")

    def convert(self, value, **kwargs):
        value = super().convert(value, **kwargs)

        if self.parser:
            value = self.parser(value)

        return value


@dataclass
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

        _errors, _document = User().validate_it(_document, convert=True, strip_unknown=False)
        assert not _errors

    Все доступные поля описаны в модуле ``validation.field`` и несколько полей в ``api.field``
    """

    base_type: Type = dict
    default: Union[Callable, dict, None] = None
    required: bool = True

    def validate_it(self, value, **kwargs) -> Tuple[Any, Any]:
        kwargs["meta"] = self.Meta
        return super().validate_it(value, **kwargs)

    @classmethod
    def get_singleton_name(cls, *args, **kwargs):
        return cls.__name__ + "_" + str(cls.get_fields()) + "_" + str(kwargs)

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)
        _data["schema"] = {x: y.representation(**kwargs) for x, y in self.get_fields().items()}
        return _data

    @classmethod
    def get_fields(cls):
        return {k: v for k, v in cls.__dict__.items() if isinstance(v, Validator)}

    @classmethod
    def filter_fields(cls, *args: str):
        """
        Clone schema with only fields described in ``*args``

        :param args: List[str]
        :return: cls
        """
        _new = {k: v for k, v in cls.get_fields().items() if k in args}

        return type(cls.__name__, cls.__bases__, _new)

    @classmethod
    def exclude_fields(cls, *args: str):
        """
        Clone schema with excluding fields described in ``*args``

        :param args: List[str]
        :return: cls
        """
        _new = {k: v for k, v in cls.get_fields().items() if k not in args}

        return type(cls.__name__, cls.__bases__, _new)

    @classmethod
    def add_fields(cls, **kwargs):
        """
        Add some fields to schema
        :param kwargs: Dict[Validator]
        :return:
        """
        _new = {k: v for k, v in cls.get_fields().items()}

        _new.update(kwargs)

        return type(cls.__name__, cls.__bases__, _new)

    def validate_other(self, value, **kwargs) -> Tuple[Any, Any]:
        _errors = {}

        _value_keys = set(value.keys())
        _schema_keys = set()

        _copy = value.__class__()

        for _origin_name, _field in self.get_fields().items():
            _search_name = _field.alias if _field.alias else _origin_name
            _schema_keys.add(_search_name)

            _raw_value = value.get(_search_name)
            _error, _nested_value = _field.validate_it(_raw_value, **kwargs)

            if _error:
                _errors[_search_name] = _error

            # {} -> {} instead {} -> {'a': None}, if schema has not required field 'a'
            # but
            # {'a': None} -> {'a': None}, if origin value has not required field 'a'
            if _search_name not in value.keys() and value.get(_search_name) is None and _nested_value is None:
                continue

            if _field.rename:
                _copy[_field.rename] = _nested_value
            else:
                _copy[_origin_name] = _nested_value

        for _unknown_item in _value_keys - _schema_keys:
            if not kwargs.get("strip_unknown", False):
                _errors[_unknown_item] = "Unknown field"

        return _errors, value if _errors else _copy

    def jsonschema(self, definitions=None, **kwargs):
        _schema = super().jsonschema(definitions=None, **kwargs)

        _is_root = definitions is None

        if _is_root:
            definitions = {}

        required = []
        properties = {}

        for _key, _value in self.get_fields().items():
            if _value.required:
                required.append(_key)

            _value_schema = _value.jsonschema(definitions=definitions)

            if isinstance(_value, Schema) or "anyOf" in _value_schema:
                properties[_key] = update_definitions(_value, _value_schema, definitions)
            else:
                properties[_key] = _value_schema

        _schema["required"] = required
        _schema["properties"] = properties

        # if root
        _schema["definitions"] = definitions

        return _schema


SchemaField = Schema


__all__ = [
    "StrictType",
    "BoolField",
    "IntField",
    "FloatField",
    "StrField",
    "ListField",
    "TupleField",
    "DictField",
    "DatetimeField",
    "Schema",
    "SchemaField",
]
