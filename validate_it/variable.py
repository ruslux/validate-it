from validate_it.utils import _is_compatible, _wrap


class SchemaVar:
    def __init__(self, name, options=None) -> None:
        self._name = name

        self.options = options

    def __get__(self, instance, owner):
        if not hasattr(instance, '__current_values__'):
            return instance.__dict__[self._name]

        return instance.__current_values__.get(self._name)

    def __set__(self, instance, value):
        if not hasattr(instance, '__current_values__'):
            setattr(instance, '__current_values__', {})

        value = _wrap(value, self.options.__type__)
        value = self._validate(value)
        instance.__current_values__[self._name] = value

    def _validate(self, value):
        value = self._set_default(value)
        # use options parser
        value = self._convert(value)

        value = self._check_types(value)

        # use options other
        value = self._validate_allowed(value)
        value = self._validate_min_value(value)
        value = self._validate_max_value(value)
        value = self._validate_min_length(value)
        value = self._validate_max_length(value)
        value = self._validate_size(value)
        value = self._walk_validators(value)

        return value

    def _set_default(self, value):
        if value is None and self.options.default is not None:
            if callable(self.options.default):
                value = self.options.default()
            else:
                value = self.options.default

        return value

    def _convert(self, value):
        if not _is_compatible(value, self.options.get_type()) and self.options.parser:

            converted = self.options.parser(value)

            if converted is not None:
                value = converted

        return value

    def _check_types(self, value):
        if not _is_compatible(value, self.options.get_type()):
            raise TypeError(f"Field `{self._name}`: {self.options.get_type()} is not compatible with value `{value}`")

        return value

    def _validate_allowed(self, value):
        allowed = self.options.allowed

        if callable(self.options.allowed):
            allowed = self.options.allowed()

        if allowed and value not in allowed:
            raise ValueError(f"Field `{self._name}`: value `{value}` is not allowed. Allowed values: `{allowed}`")

        return value

    def _validate_min_length(self, value):
        min_length = self.options.min_length

        if callable(min_length):
            min_length = min_length()

        if min_length is not None and len(value) < min_length:
            raise ValueError(f"Field `{self._name}`: len(`{value}`) is less than required")

        return value

    def _validate_max_length(self, value):
        max_length = self.options.max_length

        if callable(max_length):
            max_length = max_length()

        if max_length is not None and len(value) > max_length:
            raise ValueError(f"Field `{self._name}`: len(`{value}`) is greater than required")

        return value

    def _validate_min_value(self, value):
        min_value = self.options.min_value

        if callable(min_value):
            min_value = min_value()

        if min_value is not None and value < min_value:
            raise ValueError(f"Field `{self._name}`: value `{value}` is less than required")

        return value

    def _validate_max_value(self, value):
        max_value = self.options.max_value

        if callable(max_value):
            max_value = max_value()

        if max_value is not None and value > max_value:
            raise ValueError(f"Field `{self._name}`: value `{value}` is greater than required")

        return value

    def _validate_size(self, value):
        size = self.options.size

        if callable(size):
            size = size()

        if size is not None and size != len(value):
            raise ValueError(f"Field `{self._name}`: len(`{value}`) is not equal `{size}`")

        return value

    def _walk_validators(self, value):
        validators = self.options.validators

        if validators:
            for validator in validators:
                validator(value)

        return value


__all__ = [
    "SchemaVar"
]