from dataclasses import dataclass, field
from typing import Tuple, Any, Type


@dataclass
class Validator:
    base_type: Type = object
    field_name: str = ""
    alias: str = ""
    rename: str = ""
    description: str = ""
    jsonschema_options: dict = field(default_factory=dict)

    def __set_name__(self, owner, name):
        self.field_name = name

    @property
    def extended_type(self):
        return self.__class__.__name__

    @classmethod
    def get_singleton_name(cls, *args, **kwargs):
        return cls.__name__ + str(kwargs)

    def representation(self, **kwargs):
        _data = {"base_type": self.base_type.__name__, "extended_type": self.extended_type}

        _data.update(**kwargs)

        if self.field_name:
            _data["name"] = self.field_name

        if self.description:
            _data["description"] = self.description

        return _data

    def validate_it(self, value, convert=False, strip_unknown=False) -> Tuple[Any, Any]:
        raise NotImplementedError

    def get_jsonschema_type(self):
        return "object"

    def get_jsonschema_format(self):
        return ""

    def jsonschema(self, definitions=None, **kwargs):
        _title = self.jsonschema_options.get("title", self.field_name)

        _schema = {
            "title": _title,
            "type": self.get_jsonschema_type()
        }

        _format = self.get_jsonschema_format()

        if _format:
            _schema["format"] = _format

        return _schema


__all__ = ["Validator"]
