from inspect import getmembers, isroutine


def choices_from_enum(cls):
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

    return tuple(choices)


__all__ = [
    'choices_from_enum',
]
