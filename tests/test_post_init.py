from unittest import TestCase

from validate_it import schema, ValidationError


@schema
class A:
    a: int

    def __validate_it__post_init__(self):
        raise ValidationError


class PostInitTestCase(TestCase):
    def test_post_init(self):
        with self.assertRaises(ValidationError):
            A(a=1)
