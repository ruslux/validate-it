import collections

from dataclasses import dataclass, field
from datetime import datetime
from inspect import getmembers, isroutine, isclass
from typing import Union, List, Callable, Tuple, Any, Type, Dict

from validate_it.base import Validator


def choices_from_type(cls):
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

    return choices


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
    choices: Any = None
    validators: List[Callable] = field(default_factory=list)

    def __post_init__(self):
        if self.choices and self.only:
            raise TypeError(
                f"Field {self.field_name} improperly configured: `only` parameter must be empty when `choices` defined"
            )

        if self.choices:
            self.only = [choice[0] for choice in choices_from_type(self.choices)]

        if self.only and self.default is not None:
            if callable(self.default):
                raise TypeError(
                    f"Field {self.field_name} improperly configured: `default` parameter does not allow `callable` "
                    f"when `only` or `choices` defined"
                )
            if self.default not in self.only:
                raise ValueError(f"Field {self.field_name} improperly configured: `default` parameter not in `only` ")

        for _validator in self.validators:
            for _item in self.only:
                _validate_it, _error, _value = _validator(_item, False, False)
                if _error:
                    raise ValueError(
                        f"Field {self.field_name} improperly configured: `only` value {_item} does not pass defined "
                        f"`validator` {_validator}"
                    )

            if self.default is not None:
                _default = self.default() if callable(self.default) else self.default
                raise ValueError(
                    f"Field {self.field_name} improperly configured: `default` value {_default} does not pass defined "
                    f"`validator` {_validator}"
                )

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        _data["required"] = self.required

        if self.description:
            _data["description"] = self.description

        if self.only and callable(self.only):
            _data["only"] = {"type": "callable", "example": self.only(), "callable": self.only}
        elif self.only:
            _data["only"] = self.only

        if self.default and callable(self.default):
            _data["default"] = {"type": "callable", "example": self.default(), "callable": self.default}
        elif self.default:
            _data["default"] = self.default

        return _data

    def validate_it(self, value, convert=False, strip_unknown=False) -> Tuple[Any, Any]:
        _error, value = self.set_defaults(value, convert, strip_unknown)

        if not _error:
            _error, value = self.validate_required(value, convert, strip_unknown)

        if not _error and value is not None:
            _error, value = self.validate_type(value, convert, strip_unknown)

        if not _error and value is not None:
            _error, value = self.validate_only(value)

        if not _error and value is not None:
            _error, value = self.validate_other(value, convert, strip_unknown)

        if not _error and value is not None:
            _error, value = self.apply_validators(value, convert, strip_unknown)

        return _error, value

    def set_defaults(self, value, convert, strip_unknown) -> Tuple[str, Any]:
        if value is None and self.default is not None:
            if callable(self.default):
                value = self.default()
            else:
                value = self.default

        return "", value

    def validate_required(self, value, convert, strip_unknown) -> Tuple[str, Any]:
        if self.required and value is None:
            return "Value is required", value

        return "", value

    def validate_type(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        if not isinstance(value, self.base_type) and convert:
            value = self.convert(value)

        if self.base_type is int and isinstance(value, bool) and convert:
            value = self.convert(value)

        if isinstance(value, self.base_type):
            return "", value

        return "Wrong type", value

    def validate_only(self, value) -> Tuple[str, Any]:
        only = self.only

        if callable(self.only):
            only = self.only()

        if only and value not in only:
            return f"Value must belong to `{only}`", value
        else:
            return "", value

    def validate_other(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        return {}, value

    def apply_validators(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        _error = ""

        for validator in self.validators:
            _error, value = validator(value, convert, strip_unknown)

        return _error, value

    def convert(self, value):
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
                    for _choice in choices_from_type(self.choices)
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

    def validate_amount(self, value) -> Tuple[Union[Any, str], Any]:
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

    def validate_other(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        return self.validate_amount(value)

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

    def validate_length(self, value) -> Tuple[Union[Any, str], Any]:
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

    def validate_other(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        return self.validate_length(value)

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

        _errors, _value = Good().validate_it(_data)
        assert not _errors

    """

    base_type: Type = list
    default: Union[List[Any], None] = None
    nested: Union[Validator, None] = None

    def validate_items(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        _errors = {}

        if value:
            for _index, _item in enumerate(value):
                _item_error, _item = self.nested.validate_it(_item, convert, strip_unknown)

                if _item_error:
                    _errors[_index] = _item_error
                else:
                    value[_index] = _item

        return _errors, value

    def validate_other(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        _error, value = self.validate_length(value)

        if not _error:
            _error, value = self.validate_items(value, convert, strip_unknown)

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

    def convert(self, value):
        if not isinstance(value, collections.MutableSequence) and not isinstance(value, tuple):
            value = [value]

        return super().convert(value)

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

    def validate_length(self, value, convert, strip_unknown) -> Tuple[str, Any]:
        if len(value) == len(self.nested):
            return "", value
        else:
            return "Tuple length does not match with value length", value

    def validate_items(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        _errors = {}

        value = list(value)

        if value:
            for _index, _field in enumerate(self.nested):
                _item = value[_index]
                _item_error, _item = _field.validate_it(_item, convert, strip_unknown)

                if _item_error:
                    _errors[_index] = _item_error
                else:
                    value[_index] = _item

        return _errors, tuple(value)

    def validate_other(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        if not self.nested:
            return {}, value

        _error, value = self.validate_length(value, convert, strip_unknown)

        if not _error:
            _error, value = self.validate_items(value, convert, strip_unknown)

        return _error, value

    def get_jsonschema_type(self):
        return "array"


@dataclass
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

        _errors, _value = Character().validate_it(_data)
        assert not _errors

    """

    base_type: Type = dict
    default: Union[Callable, Dict[str, Validator], None] = None
    nested: Union[Validator, None] = None

    def representation(self, **kwargs):
        _data = super().representation(**kwargs)

        if self.nested:
            _data["nested"] = self.nested.representation(**kwargs)

        return _data

    def validate_other(self, value, convert, strip_unknown) -> Tuple[Any, Any]:
        _errors = {}

        if value:
            for _key, _value in value.items():
                self.nested.field_name = self.field_name
                _item_error, _value = self.nested.validate_it(_value, convert, strip_unknown)

                if _item_error:
                    _errors[_key] = _item_error
                else:
                    value[_key] = _value

        return _errors, value


@dataclass
class DatetimeField(StrictType):
    """
    Поле для значений типа ``datetime``
    """

    base_type: Type = datetime
    default: Union[datetime, None] = None

    def get_jsonschema_type(self):
        return "string"

    def get_jsonschema_format(self):
        return self.jsonschema_options.get("format", "date-time")


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
    def only_fields(cls, *args: str):
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

    def validate_other(self, value, convert=False, strip_unknown=False) -> Tuple[Any, Any]:
        _errors = {}

        _value_keys = set(value.keys())
        _schema_keys = set()

        _copy = value.__class__()

        for _name, _field in self.get_fields().items():
            _check = value.get(_field.alias) if _field.alias else value.get(_name)

            _error, _value = _field.validate_it(_check, convert, strip_unknown)

            if _error:
                _errors[_name] = _error
            elif _value is None:
                continue

            if _field.rename:
                _copy[_field.rename] = _value
            else:
                _copy[_name] = _value

            _schema_keys.add(_name)

        for _unknown_item in _value_keys - _schema_keys:
            if not strip_unknown:
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
