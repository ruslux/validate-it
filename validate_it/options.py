from datetime import datetime
from typing import Any, Callable, Iterable, List, Optional, Union

Amount = Union[
    int,
    float,
    datetime
]


class Options:
    required: bool
    default: Optional[Union[Any, Callable]]

    auto_pack: Optional[Union[bool, Callable]]
    packer: Optional[Callable]

    allowed: Optional[Union[Iterable[Any], Callable]]

    min_value: Optional[Union[Amount, Callable]]
    max_value: Optional[Union[Amount, Callable]]

    size: Optional[Union[int, Callable]]

    min_length: Optional[Union[int, Callable]]
    max_length: Optional[Union[int, Callable]]

    alias: Optional[Union[str, Callable]]
    rename: Optional[Union[str, Callable]]

    validators: Optional[List[Callable]]

    parser: Optional[Callable]

    def __init__(
        self,
        required: bool = True,
        default: Optional[Union[Any, Callable]] = None,
        auto_pack: Optional[Union[bool, Callable]] = None,
        packer: Optional[Callable] = None,
        allowed: Optional[Union[Iterable[Any], Callable]] = None,
        min_value: Optional[Union[Amount, Callable]] = None,
        max_value: Optional[Union[Amount, Callable]] = None,
        size: Optional[Union[int, Callable]] = None,
        min_length: Optional[Union[int, Callable]] = None,
        max_length: Optional[Union[int, Callable]] = None,
        alias: Optional[Union[str, Callable]] = None,
        rename: Optional[Union[str, Callable]] = None,
        validators: Optional[Iterable[Callable]] = None,
        parser: Optional[Callable] = None,
        serializer: Optional[Callable] = None
    ):

        self.required = required
        self.default = default
        self.auto_pack = auto_pack
        self.packer = packer
        self.allowed = allowed
        self.min_value = min_value
        self.max_value = max_value
        self.size = size
        self.min_length = min_length
        self.max_length = max_length
        self.alias = alias
        self.rename = rename
        self.validators = validators
        self.parser = parser
        self.serializer = serializer

        self.__type__ = None

    def set_type(self, t):
        self.__type__ = t

    def get_type(self):
        return self.__type__


__all__ = [
    "Options"
]
