import inspect

import attr


@attr.s(repr=False, slots=True, hash=True)
class NullableValidator(object):
    _type = attr.ib()

    def __call__(self, instance, attribute, value):

        if not isinstance(value, self._type) and value is not None and not inspect.isfunction(value):
            raise TypeError(
                f"'{attribute.name}' must be {self._type} or None (got {value} that is a {value.__class__})."
            )


def is_none_or_instance_of(_type):
    return NullableValidator(type=_type)


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


def validate_amount(value, min_value, max_value):
    if min_value is not None:
        if value < min_value:
            return False, f"Value must be greater than `{min_value}`", value

    if max_value is not None:
        if value > max_value:
            return False, f"Value must be lesser than `{max_value}`", value

    return True, {}, value


def validate_length(value, min_length, max_length):
    if min_length is not None:
        if len(value) < min_length:
            return False, f"Value length must be greater than `{min_length}`", value

    if max_length is not None:
        if len(value) > max_length:
            return False, f"[Value length must be lesser than `{max_length}`", value

    return True, {}, value


def validate_belonging(value, only):
    if only and value not in only:
        return False, f"Value must belong to `{only}`", value
    else:
        return True, "", value
