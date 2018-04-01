from datetime import datetime
from unittest import TestCase

from validate_it import *

SIMPLE_FIELDS = [BoolField, IntField, FloatField, StrField, DatetimeField]
FIELDS_WITH_CHILDREN = [ListField, DictField]
SCHEMA_FIELDS = [SchemaField]
FIELDS_FIELDS = [TupleField]

ALL_FIELDS = SIMPLE_FIELDS + FIELDS_WITH_CHILDREN + SCHEMA_FIELDS + FIELDS_FIELDS

AMOUNT_FIELDS = [IntField, FloatField]
LENGTH_FIELDS = [StrField, ListField]


class SimpleSchema(Schema):
    field = IntField()


_now = datetime.now()


REQUIRED = {
    'value': {
        BoolField: True,
        IntField: 0,
        FloatField: 0.0,
        StrField: '',
        ListField: [1, 2, 3],
        TupleField: (1, 2, 3),
        DictField: {'field': 1},
        SchemaField: {'field': 1},
        DatetimeField: _now,
    },
    'callable': {
        BoolField: lambda: True,
        IntField: lambda: 0,
        FloatField: lambda: 0.0,
        StrField: lambda: '',
        ListField: lambda: [1, 2, 3],
        TupleField: lambda: (1, 2, 3),
        DictField: lambda: {'field': 1},
        SchemaField: lambda: {'field': 1},
        DatetimeField: lambda: _now,
    }
}

ONLY = {
    'value': {
        BoolField: True,
        IntField: 0,
        FloatField: 0.0,
        StrField: 'yes',
        ListField: [1, 2, 3],
        TupleField: (1, 2, 3),
        DictField: {'field': 1},
        SchemaField: {'field': 1},
        DatetimeField: _now,
    },
    'right': {
        BoolField: [True, False],
        IntField: [0, 1, 2],
        FloatField: [0.0, 0.1, 0.2],
        StrField: ['yes', 'no'],
        ListField: [[1, 2, 3], [], [3, 2, 1]],
        TupleField: [(1, 2, 3), (), (3, 2, 1)],
        DictField: [{'field': 1}, {'field': 2}],
        SchemaField: [{'field': 1}, {'field': 2}],
        DatetimeField: [_now, datetime.now()],
    },
    'wrong': {
        BoolField: [False],
        IntField: [1, 2],
        FloatField: [0.1, 0.2],
        StrField: ['no'],
        ListField: [[], [3, 2, 1]],
        TupleField: [(), (3, 2, 1)],
        DictField: [{'field': 2}],
        SchemaField: [{'field': 2}],
        DatetimeField: [datetime.now()],
    }
}

AMOUNT_VALUE = {
    IntField: 0,
    FloatField: 0.0,
}

AMOUNT_RIGHT = {
    'min': {
        IntField: 0,
        FloatField: 0.0,
    },
    'max': {
        IntField: 0,
        FloatField: 0.0,
    }
}

AMOUNT_WRONG = {
    'min': {
        IntField: 1,
        FloatField: 1.0,
    },
    'max': {
        IntField: -1,
        FloatField: -1.0,
    }
}

LENGTH_VALUE = {
    StrField: '12345',
    ListField: [1, 2, 3, 4, 5]
}

LENGTH_RIGHT = {
    'min': {
        StrField: 5,
        ListField: 5
    },
    'max': {
        StrField: 5,
        ListField: 5
    }
}

LENGTH_WRONG = {
    'min': {
        StrField: 6,
        ListField: 6
    },
    'max': {
        StrField: 4,
        ListField: 4
    }
}

CONVERT = {
    'wrong': {
        BoolField: ['', 1, 0],
        IntField: ['0', '1', 2.0],
        FloatField: [0, '0.1'],
        StrField: [1, 2.0],
        ListField: [()],
        TupleField: [[]],
        DictField: [],
        SchemaField: [],
        DatetimeField: ['2018-01-30'],
    },
    'expected': {
        BoolField: [False, True, False],
        IntField: [0, 1, 2],
        FloatField: [0.0, 0.1],
        StrField: ['1', '2.0'],
        ListField: [[]],
        TupleField: [()],
        DictField: [],
        SchemaField: [],
        DatetimeField: [],
    }
}


class FieldTestCase(TestCase):
    def test_convert(self):
        for _field in SIMPLE_FIELDS:
            _expected_list = CONVERT['expected'][_field]
            for _index, _expected in enumerate(_expected_list):
                _value = CONVERT['wrong'][_field][_index]
                _is_valid, _error, _data = _field(field_name=_field).is_valid(_value, True, False)
                self.assertEqual(_expected, _data)

    def test_not_required(self):
        _is_valid, _error, _data = StrictType(field_name='StrictType').is_valid(None, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)

    def test_required_right(self):
        _is_valid, _error, _data = StrictType(field_name='StrictType', required=True)\
            .is_valid(1, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)

    def test_required_wrong(self):
        _is_valid, _error, _data = StrictType(field_name='StrictType', required=True)\
            .is_valid(None, False, False)
        self.assertEqual(False, _is_valid)

    def test_default_value_required(self):
        _is_valid, _error, _data = StrictType(field_name='StrictType', required=True, default=1) \
            .is_valid(None, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(1, _data)

    def test_default_value_not_required(self):
        _is_valid, _error, _data = StrictType(field_name='StrictType', default=1) \
            .is_valid(None, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(1, _data)

    def test_default_callable_required(self):
        for _field in SIMPLE_FIELDS:
            _default = REQUIRED['callable'][_field]
            _is_valid, _error, _data = _field(field_name=_field, required=True, default=_default)\
                .is_valid(None, False, False)
            self.assertEqual({}, _error)
            self.assertEqual(True, _is_valid)
            self.assertEqual(_default(), _data)

        _default = REQUIRED['callable'][Schema]
        _is_valid, _error, _data = SimpleSchema(
            field_name=Schema, required=True, default=_default
        ).is_valid(None, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(_default(), _data)

    def test_default_callable_not_required(self):
        for _field in SIMPLE_FIELDS:
            _default = REQUIRED['callable'][_field]
            _is_valid, _error, _data = _field(field_name=_field, default=_default).is_valid(None, False, False)
            self.assertEqual({}, _error)
            self.assertEqual(True, _is_valid)
            self.assertEqual(_default(), _data)

        _default = REQUIRED['callable'][Schema]
        _is_valid, _error, _data = SimpleSchema(
            field_name=Schema, default=_default
        ).is_valid(None, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(_default(), _data)

    def test_amount_min_right(self):
        for _field in AMOUNT_FIELDS:
            _value = AMOUNT_VALUE[_field]
            _min = AMOUNT_RIGHT['min'][_field]

            _is_valid, _error, _data = _field(field_name=_field, min_value=_min).is_valid(_value, False, False)
            self.assertEqual({}, _error)
            self.assertEqual(True, _is_valid)
            self.assertEqual(_value, _data)

    def test_amount_max_right(self):
        for _field in AMOUNT_FIELDS:
            _value = AMOUNT_VALUE[_field]
            _max = AMOUNT_RIGHT['max'][_field]

            _is_valid, _error, _data = _field(field_name=_field, max_value=_max).is_valid(_value, False, False)
            self.assertEqual({}, _error)
            self.assertEqual(True, _is_valid)
            self.assertEqual(_value, _data)

    def test_amount_both_right(self):
        for _field in AMOUNT_FIELDS:
            _value = AMOUNT_VALUE[_field]
            _min = AMOUNT_RIGHT['min'][_field]
            _max = AMOUNT_RIGHT['max'][_field]

            _is_valid, _error, _data = _field(field_name=_field, min_value=_min, max_value=_max)\
                .is_valid(_value, False, False)
            self.assertEqual({}, _error)
            self.assertEqual(True, _is_valid)
            self.assertEqual(_value, _data)

    def test_amount_min_wrong(self):
        for _field in AMOUNT_FIELDS:
            _value = AMOUNT_VALUE[_field]
            _min = AMOUNT_WRONG['min'][_field]

            _is_valid, _error, _data = _field(field_name=_field, min_value=_min).is_valid(_value, False, False)
            self.assertEqual(False, _is_valid)
            self.assertEqual(_value, _data)

    def test_amount_max_wrong(self):
        for _field in AMOUNT_FIELDS:
            _value = AMOUNT_VALUE[_field]
            _max = AMOUNT_WRONG['max'][_field]

            _is_valid, _error, _data = _field(field_name=_field, max_value=_max).is_valid(_value, False, False)
            self.assertEqual(False, _is_valid)
            self.assertEqual(_value, _data)

    def test_amount_both_wrong(self):
        for _field in AMOUNT_FIELDS:
            _value = AMOUNT_VALUE[_field]
            _min = AMOUNT_WRONG['min'][_field]
            _max = AMOUNT_WRONG['max'][_field]

            _is_valid, _error, _data = _field(field_name=_field, min_value=_min, max_value=_max)\
                .is_valid(_value, False, False)
            self.assertEqual(False, _is_valid)
            self.assertEqual(_value, _data)

    def test_length_min_right(self):
        # list
        _value = LENGTH_VALUE[ListField]
        _min = LENGTH_RIGHT['min'][ListField]

        _is_valid, _error, _data = ListField(
            field_name='ListField', min_length=_min, children_field=AnyType()
        ).is_valid(_value, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(_value, _data)

        # string
        _value = LENGTH_VALUE[StrField]
        _min = LENGTH_RIGHT['min'][StrField]

        _is_valid, _error, _data = StrField(
            field_name='StrField', min_length=_min
        ).is_valid(_value, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(_value, _data)

    def test_length_max_right(self):
        # list
        _value = LENGTH_VALUE[ListField]
        _max = LENGTH_RIGHT['max'][ListField]

        _is_valid, _error, _data = ListField(
            field_name='ListField', max_length=_max, children_field=AnyType()
        ).is_valid(_value, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(_value, _data)

        # string
        _value = LENGTH_VALUE[StrField]
        _max = LENGTH_RIGHT['max'][StrField]

        _is_valid, _error, _data = StrField(
            field_name='StrField', max_length=_max
        ).is_valid(_value, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(_value, _data)

    def test_length_both_right(self):
        # list
        _value = LENGTH_VALUE[ListField]
        _min = LENGTH_RIGHT['min'][ListField]
        _max = LENGTH_RIGHT['max'][ListField]

        _is_valid, _error, _data = ListField(
            field_name='ListField', min_length=_min, max_length=_max, children_field=AnyType()
        ).is_valid(_value, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(_value, _data)

        # string
        _value = LENGTH_VALUE[StrField]
        _min = LENGTH_RIGHT['min'][StrField]
        _max = LENGTH_RIGHT['max'][StrField]

        _is_valid, _error, _data = StrField(
            field_name='StrField', min_length=_min, max_length=_max
        ).is_valid(_value, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)
        self.assertEqual(_value, _data)

    def test_length_min_wrong(self):
        # list
        _value = LENGTH_VALUE[ListField]
        _min = LENGTH_WRONG['min'][ListField]

        _is_valid, _error, _data = ListField(
            field_name='ListField', min_length=_min, children_field=AnyType()
        ).is_valid(_value, False, False)
        self.assertEqual(False, _is_valid)
        self.assertEqual(_value, _data)

        # string
        _value = LENGTH_VALUE[StrField]
        _min = LENGTH_WRONG['min'][StrField]

        _is_valid, _error, _data = StrField(
            field_name='StrField', min_length=_min
        ).is_valid(_value, False, False)
        self.assertEqual(False, _is_valid)
        self.assertEqual(_value, _data)

    def test_length_max_wrong(self):
        # list
        _value = LENGTH_VALUE[ListField]
        _max = LENGTH_WRONG['max'][ListField]

        _is_valid, _error, _data = ListField(
            field_name='ListField', max_length=_max, children_field=AnyType()
        ).is_valid(_value, False, False)
        self.assertEqual(False, _is_valid)
        self.assertEqual(_value, _data)

        # string
        _value = LENGTH_VALUE[StrField]
        _max = LENGTH_WRONG['max'][StrField]

        _is_valid, _error, _data = StrField(
            field_name='StrField', max_length=_max
        ).is_valid(_value, False, False)
        self.assertEqual(False, _is_valid)
        self.assertEqual(_value, _data)

    def test_length_both_wrong(self):
        # list
        _value = LENGTH_VALUE[ListField]
        _min = LENGTH_WRONG['min'][ListField]
        _max = LENGTH_WRONG['max'][ListField]

        _is_valid, _error, _data = ListField(
            field_name='ListField', min_length=_min, max_length=_max, children_field=AnyType()
        ).is_valid(_value, False, False)
        self.assertEqual(False, _is_valid)
        self.assertEqual(_value, _data)

        # string
        _value = LENGTH_VALUE[StrField]
        _min = LENGTH_WRONG['min'][StrField]
        _max = LENGTH_WRONG['max'][StrField]

        _is_valid, _error, _data = StrField(
            field_name='StrField', min_length=_min, max_length=_max
        ).is_valid(_value, False, False)
        self.assertEqual(False, _is_valid)
        self.assertEqual(_value, _data)

    def test_only_right(self):
        for _field in SIMPLE_FIELDS:
            _value = ONLY['value'][_field]
            _only = ONLY['right'][_field]
            _is_valid, _error, _data = _field(field_name=_field, required=True, only=_only)\
                .is_valid(_value, False, False)

            self.assertEqual({}, _error)
            self.assertEqual(True, _is_valid)

        for _field in FIELDS_WITH_CHILDREN:
            _value = ONLY['value'][_field]
            _only = ONLY['right'][_field]
            _is_valid, _error, _data = _field(
                field_name=_field, required=True, only=_only, children_field=AnyType()
            ).is_valid(_value, False, False)

            self.assertEqual(_value, _data)
            self.assertEqual({}, _error)
            self.assertEqual(True, _is_valid)

        _value = ONLY['value'][Schema]
        _only = ONLY['right'][Schema]
        _is_valid, _error, _data = AnyType(
            field_name=Schema, required=True, only=_only
        ).is_valid(_value, False, False)
        self.assertEqual({}, _error)
        self.assertEqual(True, _is_valid)

    def test_only_wrong(self):
        for _field in SIMPLE_FIELDS:
            _value = ONLY['value'][_field]
            _only = ONLY['wrong'][_field]
            _is_valid, _error, _data = _field(
                field_name=_field, required=True, only=_only
            ).is_valid(_value, False, False)

            self.assertEqual(False, _is_valid)

        for _field in FIELDS_WITH_CHILDREN:
            _value = ONLY['value'][_field]
            _only = ONLY['wrong'][_field]
            _is_valid, _error, _data = _field(
                field_name=_field, required=True, only=_only, children_field=AnyType()
            ).is_valid(_value, False, False)

            self.assertEqual(False, _is_valid)

        _value = ONLY['value'][Schema]
        _only = ONLY['wrong'][Schema]
        _is_valid, _error, _data = SimpleSchema(
            field_name=Schema, required=True, only=_only
        ).is_valid(_value, False, False)

        self.assertEqual(False, _is_valid)


class UnionTestCase(TestCase):
    def test_no_alternatives(self):
        with self.assertRaises(ValueError):
            UnionType(alternatives=[])

    def test_first_coincidence(self):
        _field = UnionType(field_name='union', alternatives=[
            IntField(),
            FloatField()
        ])

        _is_valid, _error, _value = _field.is_valid(0.1, False, False)
        self.assertEqual(True, _is_valid)
        self.assertEqual(0.1, _value)

    def test_wrong_alternatives(self):
        _field = UnionType(field_name='union', alternatives=[
            IntField(),
            FloatField()
        ])

        _is_valid, _error, _value = _field.is_valid('0.1', False, False)
        self.assertEqual(False, _is_valid)
        self.assertEqual('0.1', _value)


class SchemaTestCase(TestCase):
    def test_strip_unknown(self):
        class Original(Schema):
            a = IntField()
            b = IntField()

        _value = {'a': 1, 'b': 1, 'c': 1}
        _is_valid, _error, value = Original().is_valid(_value, strip_unknown=True)
        self.assertEqual(True, _is_valid)
        self.assertEqual({'a': 1, 'b': 1}, value)

    def test_not_strip_unknown(self):
        class Original(Schema):
            a = IntField()
            b = IntField()

        _value = {'a': 1, 'b': 1, 'c': 1}
        _is_valid, _error, value = Original().is_valid(_value)
        self.assertEqual(False, _is_valid)
        self.assertEqual(_value, value)

    def test_clone(self):
        class Original(Schema):
            a = IntField()
            b = IntField()
            c = IntField()
            d = IntField()

        clone = Original().only_fields('a')
        self.assertEqual(list(clone.get_fields().keys()), ['a'])

        clone = Original().exclude_fields('b', 'd')
        self.assertEqual(list(clone.get_fields().keys()), ['a', 'c'])
