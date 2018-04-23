import inspect
import typing

import attr


@attr.s(repr=False, slots=True, hash=True)
class NullableValidator(object):
    _type = attr.ib()

    def __call__(self, instance, attribute, value):
        if inspect.isfunction(value):
            value = value()

        if not isinstance(value, self._type) and value is not None:
            raise TypeError(
                f"'{attribute.name}' must be {self._type} or None (got {value} that is a {value.__class__})."
            )


def is_none_or_instance_of(_type):
    return NullableValidator(type=_type)


@attr.s(repr=False, slots=True, hash=True)
class CallableValidator(object):
    _type = attr.ib()

    def __call__(self, instance, attribute, value):
        if inspect.isfunction(value):
            value = value()

        if not isinstance(value, self._type):
            raise TypeError(
                f"'{attribute.name}' must be {self._type} or callable (got {value} that is a {value.__class__})."
            )


def is_callable_or_instance_of(_type):
    return CallableValidator(type=_type)


def is_class(instance, attribute, value):
    if not inspect.isclass(value):
        raise ValueError(f"`{attribute.name}` must be `class` type, not `{type(value)}`")


def not_empty(instance, attribute, value):
    if not len(value):
        raise ValueError(f"`{attribute.name}` must be not empty")


@attr.s(repr=False, slots=True, hash=True)
class _ListOfValidator(object):
    type = attr.ib()

    def __call__(self, inst, attr, value):
        for _item in value:
            if not isinstance(_item, self.type):
                raise TypeError(f"{attr.name} must be list instances of `{self.type}`")

    def __repr__(self):
        return f"<list_of validator for type `{self.type}`>"


def list_of(_type):
    return _ListOfValidator(_type)


@attr.s(repr=False, slots=True, hash=True)
class _OneOfValidator(object):
    list = attr.ib()

    def __call__(self, inst, attr, value):
        if value not in self.list:
            raise ValueError(f"{attr.name} must be one of {self.list}")

    def __repr__(self):
        return f"<one_of validator for list {self.list}>"


def one_of(_list):
    return _OneOfValidator(_list)

