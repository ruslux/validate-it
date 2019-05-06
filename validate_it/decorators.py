from validate_it.utils import _init_schema


def schema(*args, **kwargs):
    def _wrapper(cls):
        _init_schema(cls, strip_unknown=kwargs.get('strip_unknown', False))
        return cls

    if args:
        return _wrapper(*args)
    else:
        return _wrapper
