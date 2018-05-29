from datetime import datetime
from unittest import TestCase

from validate_it import *


class BoolFieldTestCase(TestCase):
    def test_required(self):
        error, value = BoolField(required=True).validate_it(None)
        assert error

        error, value = BoolField(required=True).validate_it(False)
        assert not error

    def test_default_not_required(self):
        error, value = BoolField(default=True).validate_it(None)
        assert value

        error, value = BoolField(default=False).validate_it(None)
        assert not value

        error, value = BoolField(default=True).validate_it(False)
        assert not value

    def test_default_required(self):
        error, value = BoolField(default=True, required=True).validate_it(None)
        assert not error

    def test_default_callable_not_required(self):
        error, value = BoolField(default=lambda: True).validate_it(None)
        assert value

        error, value = BoolField(default=lambda: False).validate_it(None)
        assert not value

        error, value = BoolField(default=lambda: True).validate_it(False)
        assert not value

    def test_default_callable_required(self):
        error, value = BoolField(default=lambda: True, required=True).validate_it(None)
        assert not error

    def test_wrong_type(self):
        error, value = BoolField().validate_it(1)
        assert error

    def test_only(self):
        error, value = BoolField(only=[False]).validate_it(True)
        assert error

        error, value = BoolField(only=[True]).validate_it(True)
        assert not error

    def test_only_callable(self):
        error, value = BoolField(only=lambda: [False]).validate_it(True)
        assert error

        error, value = BoolField(only=lambda: [True]).validate_it(True)
        assert not error

    def test_amount(self):
        pass

    def test_length(self):
        pass

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        error, value = BoolField().validate_it(1, convert=True)
        assert not error
        assert value is True


class IntFieldTestCase(TestCase):
    def test_required(self):
        error, value = IntField(required=True).validate_it(None)
        assert error

        error, value = IntField(required=True).validate_it(10)
        assert not error

    def test_default_not_required(self):
        error, value = IntField(default=3).validate_it(None)
        assert value is 3

        error, value = IntField(default=0).validate_it(None)
        assert value is 0

        error, value = IntField(default=3).validate_it(4)
        assert value is 4

    def test_default_required(self):
        error, value = IntField(default=3, required=True).validate_it(None)
        assert not error

    def test_default_callable_not_required(self):
        error, value = IntField(default=lambda: 3).validate_it(None)
        assert value is 3

        error, value = IntField(default=lambda: 0).validate_it(None)
        assert value is 0

        error, value = IntField(default=lambda: 3).validate_it(4)
        assert value is 4

    def test_default_callable_required(self):
        error, value = IntField(default=lambda: 3, required=True).validate_it(None)
        assert not error
        assert value is 3

    def test_wrong_type(self):
        error, value = IntField().validate_it(1.0)
        assert error

    def test_only(self):
        error, value = IntField(only=[1, 2, 3]).validate_it(4)
        assert error

        error, value = IntField(only=[1, 2, 3]).validate_it(1)
        assert not error

    def test_only_callable(self):
        error, value = IntField(only=lambda: [1, 2, 3]).validate_it(4)
        assert error

        error, value = IntField(only=lambda: [1, 2, 3]).validate_it(1)
        assert not error

    def test_amount(self):
        error, value = IntField(min_value=3).validate_it(2)
        assert error

        error, value = IntField(min_value=3).validate_it(4)
        assert not error

        error, value = IntField(max_value=3).validate_it(4)
        assert error

        error, value = IntField(max_value=3).validate_it(3)
        assert not error

    def test_length(self):
        pass

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        error, value = IntField().validate_it(3.0, convert=True)
        assert not error
        assert value is 3

        error, value = IntField().validate_it(True, convert=True)
        assert not error
        assert value is 1

        error, value = IntField().validate_it('4', convert=True)
        assert not error
        assert value is 4


class FloatFieldTestCase(TestCase):
    def test_required(self):
        error, value = FloatField(required=True).validate_it(None)
        assert error

        error, value = FloatField(required=True).validate_it(10.0)
        assert not error

    def test_default_not_required(self):
        error, value = FloatField(default=3.0).validate_it(None)
        assert value == 3.0

        error, value = FloatField(default=0.0).validate_it(None)
        assert value == 0.0

        error, value = FloatField(default=3.0).validate_it(4.0)
        assert value == 4.0

    def test_default_required(self):
        error, value = FloatField(default=3.0, required=True).validate_it(None)
        assert not error

    def test_default_callable_not_required(self):
        error, value = FloatField(default=lambda: 3.0).validate_it(None)
        assert value == 3.0

        error, value = FloatField(default=lambda: 0.0).validate_it(None)
        assert value == 0.0

        error, value = FloatField(default=lambda: 3.0).validate_it(4.0)
        assert value == 4.0

    def test_default_callable_required(self):
        error, value = FloatField(default=lambda: 3.0, required=True).validate_it(None)
        assert not error
        assert value == 3.0

    def test_wrong_type(self):
        error, value = FloatField().validate_it(1)
        assert error

    def test_only(self):
        error, value = FloatField(only=[1.0, 2.0, 3.0]).validate_it(4.0)
        assert error

        error, value = FloatField(only=[1.0, 2.0, 3.0]).validate_it(1.0)
        assert not error

    def test_only_callable(self):
        error, value = FloatField(only=lambda: [1.0, 2.0, 3.0]).validate_it(4.0)
        assert error

        error, value = FloatField(only=lambda: [1.0, 2.0, 3.0]).validate_it(1.0)
        assert not error

    def test_amount(self):
        error, value = FloatField(min_value=3.0).validate_it(2.0)
        assert error

        error, value = FloatField(min_value=3.0).validate_it(4.0)
        assert not error

        error, value = FloatField(max_value=3.0).validate_it(4.0)
        assert error

        error, value = FloatField(max_value=3.0).validate_it(3.0)
        assert not error

    def test_length(self):
        pass

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        error, value = FloatField().validate_it(3, convert=True)
        assert not error
        assert value == 3.0

        error, value = FloatField().validate_it(True, convert=True)
        assert not error
        assert value == 1.0

        error, value = FloatField().validate_it('4.0', convert=True)
        assert not error
        assert value == 4.0


class StrFieldTestCase(TestCase):
    def test_required(self):
        error, value = StrField(required=True).validate_it(None)
        assert error

        error, value = StrField(required=True).validate_it('')
        assert not error

    def test_default_not_required(self):
        error, value = StrField(default='a').validate_it(None)
        assert value == 'a'

        error, value = StrField(default='').validate_it(None)
        assert value == ''

        error, value = StrField(default='a').validate_it('b')
        assert value == 'b'

    def test_default_required(self):
        error, value = StrField(default='a', required=True).validate_it(None)
        assert not error
        assert value == 'a'

    def test_default_callable_not_required(self):
        error, value = StrField(default=lambda: 'a').validate_it(None)
        assert value == 'a'

        error, value = StrField(default=lambda: '').validate_it(None)
        assert value == ''

        error, value = StrField(default=lambda: 'a').validate_it('b')
        assert value == 'b'

    def test_default_callable_required(self):
        error, value = StrField(default=lambda: 'a', required=True).validate_it(None)
        assert not error
        assert value == 'a'

    def test_wrong_type(self):
        error, value = StrField().validate_it(1)
        assert error

    def test_only(self):
        error, value = StrField(only=['a', 'b', 'c']).validate_it('d')
        assert error

        error, value = StrField(only=['a', 'b', 'c']).validate_it('a')
        assert not error

    def test_only_callable(self):
        error, value = StrField(only=lambda: ['a', 'b', 'c']).validate_it('d')
        assert error

        error, value = StrField(only=lambda: ['a', 'b', 'c']).validate_it('a')
        assert not error

    def test_amount(self):
        pass

    def test_length(self):
        error, value = StrField(min_length=3).validate_it('a')
        assert error

        error, value = StrField(min_length=3).validate_it('abc')
        assert not error

        error, value = StrField(max_length=3).validate_it('abcd')
        assert error

        error, value = StrField(max_length=3).validate_it('abc')
        assert not error

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        error, value = StrField().validate_it(3.0, convert=True)
        assert not error
        assert value == '3.0'

        error, value = StrField().validate_it(True, convert=True)
        assert not error
        assert value == 'True'

        error, value = StrField().validate_it(4, convert=True)
        assert not error
        assert value == '4'


class ListFieldTestCase(TestCase):
    def test_required(self):
        error, value = ListField(children_field=IntField(), required=True).validate_it(None)
        assert error

        error, value = ListField(children_field=IntField(), required=True).validate_it([])
        assert not error

    def test_default_not_required(self):
        error, value = ListField(children_field=IntField(), default=[1]).validate_it(None)
        assert value == [1]

        error, value = ListField(children_field=IntField(), default=[]).validate_it(None)
        assert value == []

        error, value = ListField(children_field=IntField(), default=[1]).validate_it([2])
        assert value == [2]

    def test_default_required(self):
        error, value = ListField(children_field=IntField(), default=[1], required=True).validate_it(None)
        assert not error
        assert value == [1]

    def test_default_callable_not_required(self):
        error, value = ListField(children_field=IntField(), default=lambda: [1]).validate_it(None)
        assert value == [1]

        error, value = ListField(children_field=IntField(), default=lambda: []).validate_it(None)
        assert value == []

        error, value = ListField(children_field=IntField(), default=lambda: [1]).validate_it([2])
        assert value == [2]

    def test_default_callable_required(self):
        error, value = ListField(children_field=IntField(), default=lambda: [1], required=True).validate_it(None)
        assert not error
        assert value == [1]

    def test_wrong_type(self):
        error, value = ListField(children_field=IntField()).validate_it((1,))
        assert error

    def test_only(self):
        error, value = ListField(children_field=IntField(), only=[[1], [2, 3], [3, 4]]).validate_it([4, 5])
        assert error

        error, value = ListField(children_field=IntField(), only=[[1], [2, 3], [3, 4]]).validate_it([3, 4])
        assert not error

    def test_only_callable(self):
        error, value = ListField(children_field=IntField(), only=lambda: [[1], [2, 3], [3, 4]]).validate_it([4, 5])
        assert error

        error, value = ListField(children_field=IntField(), only=lambda: [[1], [2, 3], [3, 4]]).validate_it([3, 4])
        assert not error

    def test_amount(self):
        pass

    def test_length(self):
        error, value = ListField(children_field=IntField(), min_length=3).validate_it([1])
        assert error

        error, value = ListField(children_field=IntField(), min_length=3).validate_it([1, 2, 3])
        assert not error

        error, value = ListField(children_field=IntField(), max_length=3).validate_it([1, 2, 3, 4])
        assert error

        error, value = ListField(children_field=IntField(), max_length=3).validate_it([1, 2, 3])
        assert not error

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        error, value = ListField(children_field=IntField()).validate_it((1, 2.0, '3'), convert=True)
        assert not error
        assert value == [1, 2, 3]

        error, value = ListField(children_field=IntField()).validate_it(10, convert=True)
        assert not error
        assert value == [10]

        error, value = ListField(children_field=StrField()).validate_it('abc', convert=True)
        assert not error
        assert value == ['abc']


class TupleFieldTestCase(TestCase):
    def test_required(self):
        error, value = TupleField(elements=[IntField(), FloatField(), StrField()], required=True).validate_it(None)
        assert error

        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], required=True
        ).validate_it((1, 2.0, '3'))
        assert not error

    def test_default_not_required(self):
        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], default=(1, 2.0, '3.0')
        ).validate_it(None)
        assert value == (1, 2.0, '3.0')

        error, value = TupleField(default=tuple()).validate_it(None)
        assert value == tuple()

        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], default=(1, 2.0, '3')
        ).validate_it((2, 3.0, '4.0'))
        assert value == (2, 3.0, '4.0')

    def test_default_required(self):
        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], default=(1, 2.0, '3'), required=True
        ).validate_it(None)
        assert not error
        assert value == (1, 2.0, '3')

    def test_default_callable_not_required(self):
        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], default=lambda: (1, 2.0, '3')
        ).validate_it(None)
        assert value == (1, 2.0, '3')

        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], default=lambda: tuple()
        ).validate_it(None)
        assert value == tuple()

        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], default=lambda: (1, 2.0, '3')
        ).validate_it((2, 3.0, '4.0'))
        assert value == (2, 3.0, '4.0')

    def test_default_callable_required(self):
        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], default=lambda: (1, 2.0, '3'), required=True
        ).validate_it(None)
        assert not error
        assert value == (1, 2.0, '3')

    def test_wrong_type(self):
        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()]
        ).validate_it([1])
        assert error

    def test_only(self):
        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], only=[(1, 2.0, '3'), (2, 3.0, '4'), (3, 4.0, '5')]
        ).validate_it((4, 5.0, '6'))
        assert error

        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], only=[(1, 2.0, '3'), (2, 3.0, '4'), (3, 4.0, '5')]
        ).validate_it((1, 2.0, '3'))
        assert not error

    def test_only_callable(self):
        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], only=lambda: [(1, 2.0, '3'), (2, 3.0, '4'), (3, 4.0, '5')]
        ).validate_it((4, 5.0, '6'))
        assert error

        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()], only=lambda: [(1, 2.0, '3'), (2, 3.0, '4'), (3, 4.0, '5')]
        ).validate_it((1, 2.0, '3'))
        assert not error

    def test_amount(self):
        pass

    def test_length(self):
        error, value = TupleField(elements=[IntField(), FloatField(), StrField()]).validate_it((1, 2.0, '3'))
        assert not error

        error, value = TupleField(elements=[IntField(), FloatField(), StrField()]).validate_it((1, 2.0))
        assert error

        error, value = TupleField(elements=[IntField(), FloatField(), StrField()]).validate_it((1, 2.0, '3', []))
        assert error

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()]
        ).validate_it([1, 2.0, '3'], convert=True)
        assert not error
        assert value == (1, 2.0, '3')

        error, value = TupleField(
            elements=[IntField(), FloatField(), StrField()]
        ).validate_it([1, 2, 3], convert=True)
        assert not error
        assert value == (1, 2.0, '3')


class DictFieldTestCase(TestCase):
    _first = {
        'a': 1,
        'b': 2,
        'c': 3
    }

    _as_first = {
        'a': 1,
        'b': 2,
        'c': 3
    }

    _second = {
        'a': 2,
        'b': 3,
        'c': 4
    }

    _as_second = {
        'a': 2,
        'b': 3,
        'c': 4
    }

    _third = {
        'a': 3,
        'b': 4,
        'c': 5
    }

    def test_required(self):
        error, value = DictField(children_field=IntField(), required=True).validate_it(None)
        assert error

        error, value = DictField(children_field=IntField(), required=True).validate_it(self._first)
        assert not error

    def test_default_not_required(self):
        error, value = DictField(children_field=IntField(), default=self._first).validate_it(None)
        assert value == self._as_first

        error, value = DictField(children_field=IntField(), default={}).validate_it(None)
        assert value == {}

        value['a'] = 1

        error, value = DictField(children_field=IntField(), default={}).validate_it(None)
        assert value == {}

        error, value = DictField(children_field=IntField(), default=self._first).validate_it(self._second)
        assert value == self._as_second

    def test_default_required(self):
        error, value = DictField(children_field=IntField(), default=self._first, required=True).validate_it(None)
        assert not error
        assert value == self._as_first

    def test_default_callable_not_required(self):
        error, value = DictField(children_field=IntField(), default=lambda: self._first).validate_it(None)
        assert value == self._as_first

        error, value = DictField(children_field=IntField(), default=lambda: {}).validate_it(None)
        assert value == {}

        value['a'] = 1

        error, value = DictField(children_field=IntField(), default=lambda: {}).validate_it(None)
        assert value == {}

        error, value = DictField(children_field=IntField(), default=lambda: self._first).validate_it(self._second)
        assert value == self._as_second

    def test_default_callable_required(self):
        error, value = DictField(
            children_field=IntField(), default=lambda: self._first, required=True
        ).validate_it(None)
        assert not error
        assert value == self._as_first

    def test_wrong_type(self):
        error, value = DictField(children_field=IntField()).validate_it(1.0)
        assert error

    def test_only(self):
        error, value = DictField(children_field=IntField(), only=[self._first, self._second]).validate_it(self._third)
        assert error

        error, value = DictField(
            children_field=IntField(), only=[self._first, self._second]
        ).validate_it(self._as_first)
        assert not error

    def test_only_callable(self):
        error, value = DictField(
            children_field=IntField(), only=lambda: [self._first, self._second]
        ).validate_it(self._third)
        assert error

        error, value = DictField(
            children_field=IntField(), only=lambda: [self._first, self._second]
        ).validate_it(self._as_first)
        assert not error

    def test_amount(self):
        pass

    def test_length(self):
        pass

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        error, value = DictField(children_field=IntField()).validate_it({'a': '1', 'b': 2.0}, convert=True)
        assert not error
        assert value == {'a': 1, 'b': 2}


class DatetimeFieldTestCase(TestCase):
    _first = datetime.now()

    _as_first = datetime(
        year=_first.year,
        month=_first.month,
        day=_first.day,
        hour=_first.hour,
        minute=_first.minute,
        second=_first.second,
        microsecond=_first.microsecond
    )

    _second = datetime.now()

    _as_second = datetime(
        year=_second.year,
        month=_second.month,
        day=_second.day,
        hour=_second.hour,
        minute=_second.minute,
        second=_second.second,
        microsecond=_second.microsecond
    )

    _third = datetime.now()

    def test_required(self):
        error, value = DatetimeField(required=True).validate_it(None)
        assert error

        error, value = DatetimeField(required=True).validate_it(self._first)
        assert not error

    def test_default_not_required(self):
        error, value = DatetimeField(default=self._first).validate_it(None)
        assert value == self._as_first

        error, value = DatetimeField(default=self._first).validate_it(self._second)
        assert value == self._as_second

    def test_default_required(self):
        error, value = DatetimeField(default=self._first, required=True).validate_it(None)
        assert not error
        assert value == self._as_first

    def test_default_callable_not_required(self):
        error, value = DatetimeField(default=lambda: self._first).validate_it(None)
        assert value == self._as_first

        error, value = DatetimeField(default=lambda: self._first).validate_it(self._second)
        assert value == self._as_second

    def test_default_callable_required(self):
        error, value = DatetimeField(default=lambda: self._first, required=True).validate_it(None)
        assert not error
        assert value == self._as_first

    def test_wrong_type(self):
        error, value = DatetimeField().validate_it(1.0)
        assert error

    def test_only(self):
        error, value = DatetimeField(only=[self._first, self._second]).validate_it(self._third)
        assert error

        error, value = DatetimeField(only=[self._first, self._second]).validate_it(self._as_first)
        assert not error

    def test_only_callable(self):
        error, value = DatetimeField(only=lambda: [self._first, self._second]).validate_it(self._third)
        assert error

        error, value = DatetimeField(only=lambda: [self._first, self._second]).validate_it(self._as_first)
        assert not error

    def test_amount(self):
        pass

    def test_length(self):
        pass

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        pass


class AnyTestCase(TestCase):
    def test_required(self):
        error, value = AnyType(required=True).validate_it(None)
        assert error

        error, value = AnyType(required=True).validate_it(1)
        assert not error

        error, value = AnyType(required=True).validate_it('1')
        assert not error

    def test_default_not_required(self):
        error, value = AnyType(default=1).validate_it(None)
        assert not error
        assert value == 1

    def test_default_required(self):
        error, value = AnyType(default=1, required=True).validate_it(None)
        assert not error
        assert value == 1

    def test_default_callable_not_required(self):
        error, value = AnyType(default=lambda: 1).validate_it(None)
        assert not error
        assert value == 1

    def test_default_callable_required(self):
        error, value = AnyType(default=lambda: 1, required=True).validate_it(None)
        assert not error
        assert value == 1

    def test_wrong_type(self):
        pass

    def test_only(self):
        error, value = AnyType(only=[1, 'a', 3.0]).validate_it(4)
        assert error
        assert value == 4

        error, value = AnyType(only=[1, 'a', 3.0]).validate_it(1)
        assert not error
        assert value == 1

    def test_only_callable(self):
        error, value = AnyType(only=lambda: [1, 'a', 3.0]).validate_it(4)
        assert error
        assert value == 4

        error, value = AnyType(only=lambda: [1, 'a', 3.0]).validate_it(1)
        assert not error
        assert value == 1

    def test_amount(self):
        pass

    def test_length(self):
        pass

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        pass


class UnionTestCase(TestCase):
    def test_required(self):
        error, value = UnionType(
            alternatives=[
                IntField(required=True),
                FloatField(required=True)
            ]
        ).validate_it(None)

        assert error

        error, value = UnionType(
            alternatives=[
                IntField(),
                FloatField(required=True)
            ]
        ).validate_it(None)

        assert not error

        error, value = UnionType(
            alternatives=[
                IntField(required=True),
                FloatField(required=True)
            ]
        ).validate_it(1)

        assert not error

        error, value = UnionType(
            alternatives=[
                IntField(required=True),
                FloatField(required=True)
            ]
        ).validate_it(1.0)

        assert not error

    def test_default_not_required(self):
        error, value = UnionType(
            alternatives=[
                IntField(required=True),
                FloatField(required=True)
            ]
        ).validate_it(None)

    def test_default_required(self):
        pass

    def test_default_callable_not_required(self):
        pass

    def test_default_callable_required(self):
        pass

    def test_wrong_type(self):
        pass

    def test_only(self):
        pass

    def test_only_callable(self):
        pass

    def test_amount(self):
        pass

    def test_length(self):
        pass

    def test_strip_unknown(self):

        class A(Schema):
            a = IntField(required=True)

        class B(Schema):
            b = IntField(required=True)

        error, value = UnionType(
            alternatives=[
                A(),
                B()
            ]
        ).validate_it({'b': 1}, strip_unknown=True)

        assert not error
        assert value == {'b': 1}

    def test_convert(self):
        pass


class SchemaTestCase(TestCase):
    def test_required(self):
        pass

    def test_default_not_required(self):
        pass

    def test_default_required(self):
        pass

    def test_default_callable_not_required(self):
        pass

    def test_default_callable_required(self):
        pass

    def test_wrong_type(self):
        pass

    def test_only(self):
        pass

    def test_only_callable(self):
        pass

    def test_amount(self):
        pass

    def test_length(self):
        pass

    def test_strip_unknown(self):
        pass

    def test_convert(self):
        pass

    def test_alias(self):
        class A(Schema):
            a = IntField(required=True, alias='b', rename='c')

        error, value = A().validate_it({'b': 1}, strip_unknown=True)
        assert not error
        assert value == {'c': 1}
