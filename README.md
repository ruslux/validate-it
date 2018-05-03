# Validate-it

[![Build Status](https://travis-ci.org/ruslux/validate-it.svg?branch=master)](https://travis-ci.org/ruslux/validate-it) 
[![Coverage Status](https://coveralls.io/repos/github/ruslux/validate-it/badge.svg?branch=master)](https://coveralls.io/github/ruslux/validate-it)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ruslux/validate-it/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ruslux/validate-it)
[![PyPI version](https://badge.fury.io/py/validate-it.svg)](https://badge.fury.io/py/validate-it)

- [About](#about)
- [Installation](#installation)
- [Available fields](#fields)
- [Keyword arguments](#kwargs)
- [Example](#example)
- [Requirements](#requirements)

### <a name="about"/>About</a>
Yet another schema validator.


### <a name="installation"/>Installation</a>
With pip:
```bash
pip install validate-it
```

### <a name="fields"/>Available fields</a>
* ``BoolField``
  ```python
  error, value = BoolField(default=True).validate_it(None)
  assert value
  ```
* ``IntField``
    ```python
    error, value = IntField().validate_it('10', convert=True)
    assert value == 10
    ```
* ``FloatField``
    ```python
    error, value = FloatField().validate_it(9, convert=True)
    assert value == 9.0
    ```
* ``ListField``
    ```python
    errors, value = ListField(
        children_field=IntField()
    ).validate_it([1, 2, 3, 4])

    assert value == [1, 2, 3, 4]
    assert not errors
    ```
* ``TupleField``
    ```python
    errors, value = TupleField(
        elemetns=(
            IntField(),
            FloatField(),
            StrField()
        )
    ).validate_it((1, 2.0, '3'))

    assert value == (1, 2.0, '3')
    assert not errors
    ```
* ``DictField``
    ```python
    errors, value = DictField(
        children_field=IntField()
    ).validate_it({'a': 1, 'b': 2, 'c': 3})

    assert value == {'a': 1, 'b': 2, 'c': 3}
    assert not errors
    ```
* ``DatetimeField``
    ```python
    errors, value = DatetimeField().validate_it(datetime.now())
    assert not errors
    ```

* ``Schema``
    ```python
    class Author(Schema):
        first_name = StrField()
        last_name = StrField()

    class Post(Schema):
        title = StrField()
        text = StrField()
        author = Author()

    errors, value = Post().validate_it(
        {
            "title": "Hello",
            "text": "World",
            "author" {
                "first_name": "John",
                "last_name": "Smith"
            }
        }
    )
    assert not errors
    ```


### <a name="kwargs"/>Keyword arguments</a>
All fields:
* ``required`` - value is required (default is ``False``)
* ``only`` - list of available values (can be callable, default allow any)
* ``default`` - set default if value is ``None`` (can be callable, default is ``None``)
* ``validators`` - list of custom callable validators

StrField, ListField:
* ``min_length`` - minimal sequence length (default is ``None``)
* ``max_length`` - maximum sequence length (default is ``None``)

ListField, DictField:
* ``children_field`` - required ``Validator`` subclass for value

TupleField:
* ``elements`` - tuple of ``Validator`` subclasses

IntField, FloatField:
* ``min_value``
* ``max_value``



### <a name="example"/>Example</a>
```python
from validate_it import *


class Owner(Schema):
    first_name = StrField(required=True)
    last_name = StrField(required=True)
    
    
class Characteristics(Schema):
    cc = FloatField(required=True, min_value=0.0)
    hp = IntField(required=True, min_value=0)


class Car(Schema):
    name = StrField(required=True, min_length=2, max_length=20)
    owners = ListField(required=True, children_field=Owner())
    characteristics = Characteristics(required=True, default={"cc": 0.0, "hp": 0})
    convert = BoolField(required=True)

    
_data = {
    "name": "Shelby GT500",
    "owners": [
        {
            "first_name": "Randall",
            "last_name": "Raines",
        }
    ],
    "characteristics": {
        "cc": 4.7,
        "hp": 306
    },
    "unknown_field": 10,
    "convert": 1 
}

_errors, _data = Car().validate_it(_data, convert=True, strip_unknown=True)
assert not _errors
```

### <a name="requirements"/>Requirements</a>
Tested with `python3.6`

### <a name="contribution"/>Contribution how-to</a>
###### Run tests:
* clone repo: `git clone <your-fork>`
* create and activate your virtualenv
* `pip install -r requirements.txt && pip install -r dev-requirements`
* `./run_tests.sh`
