# Validate-it

[![Build Status](https://travis-ci.org/ruslux/validate-it.svg?branch=master)](https://travis-ci.org/ruslux/validate-it) 
[![Coverage Status](https://coveralls.io/repos/github/ruslux/validate-it/badge.svg?branch=master)](https://coveralls.io/github/ruslux/validate-it)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ruslux/validate-it/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ruslux/validate-it)
[![PyPI version](https://badge.fury.io/py/validate-it.svg)](https://badge.fury.io/py/validate-it)

- [About](#about)
- [Installation](#installation)
- [Available fields](#fields)
- [Keyword arguments](#kwargs)
- [Validation example](#validation-example)
- [Simple mapping example](#simple-mapping-example)
- [Nested mapping example](#nested-mapping-example)
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
from validate_it import *


error, value = BoolField(default=True).validate_it(None)
assert value
```
* ``IntField``
```python
from validate_it import *


error, value = IntField().validate_it('10', convert=True)
assert value == 10
```
* ``FloatField``
```python
from validate_it import *


error, value = FloatField().validate_it(9, convert=True)
assert value == 9.0
```
* ``ListField``
```python
from validate_it import *


errors, value = ListField(
    nested=IntField()
).validate_it([1, 2, 3, 4])

assert value == [1, 2, 3, 4]
assert not errors
```
* ``TupleField``
```python
from validate_it import *


errors, value = TupleField(
    nested=(
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
from validate_it import *


errors, value = DictField(
    nested=IntField()
).validate_it({'a': 1, 'b': 2, 'c': 3})

assert value == {'a': 1, 'b': 2, 'c': 3}
assert not errors
```
* ``DatetimeField``
```python
from datetime import datetime

from validate_it import *


errors, value = DatetimeField().validate_it(datetime.now())
assert not errors
```

* ``Schema``
```python
from validate_it import *


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
        "author": {
            "first_name": "John",
            "last_name": "Smith"
        }
    }
)
assert not errors
```


### <a name="kwargs"/>Keyword arguments</a>
#### All fields:
* ``required`` - value is required (default is ``False``)
```python
from validate_it import *


a = IntField(required=True)
b = IntField(required=False)
```
* ``only`` - list of available values (can be callable, default allow any)
```python
from validate_it import *


a = IntField(only=[1, 2, 3])
b = IntField(only=lambda: range(0, 100))
```
* ``default`` - set default if value is ``None`` (can be callable, default is ``None``)
```python
from validate_it import *


a = IntField(default=1)
b = IntField(default=lambda: 1 + 1)
```
* ``validators`` - list of custom callable validators
```python
from validate_it import *


a = IntField(
    validators=[
        lambda value, *_: 0 < value < 10,
        lambda value, *_: value % 2,
    ]
)
```
#### StrField, ListField:
* ``min_length`` - minimal sequence length (default is ``None``)
```python
from validate_it import *


a = StrField(min_length=2)
```
* ``max_length`` - maximum sequence length (default is ``None``)
```python
from validate_it import *


a = ListField(max_length=2)
```
#### ListField, DictField:
* ``nested`` - required ``Validator`` subclass for value
```python
from validate_it import *


a = ListField(nested=IntField())
```

#### TupleField:
* ``nested`` - tuple of ``Validator`` subclasses
```python
from validate_it import *


a = TupleField(
    nested=(
        IntField(),
        IntField(),
        StrField(),
    )
)

# aliases
class HeaderSize(IntField):
    pass

class Header(StrField):
    pass

class Message(TupleField):
    pass

b = Message(
    nested=(
        HeaderSize(),
        Header()
    )
)
```

#### IntField, FloatField:
* ``min_value``
```python
from validate_it import *


a = IntField(min_value=2)
```
* ``max_value``
```python
from validate_it import *


a = IntField(max_value=2)
```


### <a name="validation-example"/>Validation example</a>
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
    owners = ListField(required=True, nested=Owner())
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

### <a name="simple-mapping-example"/>Simple mapping example</a>
```python
from validate_it import *


class CustomMapper(Schema):
    first_name = StrField(alias="lastname")
    last_name = StrField(alias="firstname")
    
_in_data = {
    "firstname": "Connor",
    "lastname": "John"
}

_errors, _out_data = CustomMapper().validate_it(_in_data)

assert _out_data == {"first_name": "John", "last_name": "Connor"}
```

### <a name="nested-mapping-example"/>Nested mapping example</a>
```python
from validate_it import *
from accordion import compress


class CustomMapper(Schema):
    nickname = StrField(alias="info.nickname")
    int = IntField(alias="characteristics/0")
    dex = IntField(alias="characteristics/1")
    str = IntField(alias="characteristics/2")
    vit = IntField(alias="characteristics/3")

_in_data = {
    "info": {
        "nickname": "Killer777",
    },
    "characteristics": [
        7,
        55,
        11,
        44
    ]
}

_errors, _out_data = CustomMapper().validate_it(compress(_in_data), strip_unknown=True)

assert _out_data == {
    "nickname": "Killer777", 
    "int": 7, 
    "dex": 55, 
    "str": 11, 
    "vit": 44
}
```

and back:
```python
from validate_it import *
from accordion import expand


class CustomMapper(Schema):
    nickname = StrField(rename="info.nickname")
    int = IntField(rename="characteristics/0")
    dex = IntField(rename="characteristics/1")
    str = IntField(rename="characteristics/2")
    vit = IntField(rename="characteristics/3")

_in_data = {
    "nickname": "Killer777", 
    "int": 7, 
    "dex": 55, 
    "str": 11, 
    "vit": 44
}

_errors, _out_data = CustomMapper().validate_it(_in_data, strip_unknown=True)


assert expand(_out_data) == {
    "info": {
        "nickname": "Killer777",
    },
    "characteristics": [
        7,
        55,
        11,
        44
    ]
}
```

### <a name="requirements"/>Requirements</a>
Tested with `python3.7`

### <a name="contribution"/>Contribution how-to</a>
###### Run tests:
* clone repo: `git clone <your-fork>`
* create and activate your virtualenv
* `pip install -r requirements.txt && pip install -r dev-requirements`
* `./run_tests.sh`
