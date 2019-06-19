# Validate-it

[![Build Status](https://travis-ci.org/ruslux/validate-it.svg?branch=master)](https://travis-ci.org/ruslux/validate-it) 
[![Coverage Status](https://coveralls.io/repos/github/ruslux/validate-it/badge.svg?branch=master)](https://coveralls.io/github/ruslux/validate-it)
[![PyPI version](https://badge.fury.io/py/validate-it.svg)](https://badge.fury.io/py/validate-it)

- [About](#about)
- [Installation](#installation)
- [Supported fields](#fields)
- [Validation example](#validation-example)
- [Dataclass example](#dataclass-example)
- [Simple mapping example](#simple-mapping-example)
- [Nested mapping example](#nested-mapping-example)
- [Requirements](#requirements)

### <a name="about"/>About</a>
Schema validator built on top of the typing module


### <a name="installation"/>Installation</a>
With pip:
```bash
pip install validate-it
```

### <a name="fields"/>Supported fields</a>
```python
import re
from datetime import datetime
from typing import Dict, List, Union, Optional
from validate_it import schema, Options


class IsNotEmailError(Exception):
    pass


def is_email(key, value):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise IsNotEmailError(f"{key}: is not email")

    return value

@schema
class Example:
    # required fields
    field_a: datetime
    field_b: float
    
    # required fields with defaults
    field_c: str = "unknown"
    field_d: int = 9
    
    # required fields with nested types
    field_e: Dict[int, str]
    field_f: List[int]
    
    # optional fields
    field_g: Optional[int]
    field_h: Union[int, None] # equivalent of Optional[int]
    
    # with some validators:
    fields_i: int = Options(default=0, max_value=100, min_value=100)
    fields_j: str = Options(size=10)
    fields_k: str = Options(min_length=10, max_length=20)
    fields_l: List[str] = Options(size=5)
    fields_m: str = Options(validators=[is_email])
    fields_n: int = Options(allowed=[1, 2, 3])
    
    # with search (input) alias:
    fields_o: int = Options(alias="field_n")
    
    # with rename (output) alias:
    fields_p: int = Options(rename="field_q")
    
    # with serializer used in #to_dict(), outgoing value is str type
    fields_q: int = Options(serializer=str)
    
    # with parser used in #from_dict() or direct setattr, incoming value will be parsed as int
    fields_r: int = Options(parser=int)
```

### <a name="validation-example"/>Validation example</a>
```python
from typing import List
from validate_it import *


@schema
class Simple:
    a: int
    b: int


simple = Simple(a=1, b=2)
simple.a = 2
simple.b = 3

try:
    simple.a = 'not int'
except TypeError:
    print("Wrong type")

@schema
class Owner:
    first_name: str
    last_name: str


@schema
class Characteristics:
    cc: float = Options(min_value=0.0)
    hp: int = Options(min_value=0)


@schema
class Car:
    name: str = Options(min_length=2, max_length=20)
    owners: List[Owner] = Options(auto_pack=True, packer=pack_value)
    characteristics: Characteristics = Options(default=lambda: {"cc": 0.0, "hp": 0}, auto_pack=True, packer=pack_value)
    convert: bool = Options(parser=bool)


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

_expected = {
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
    "convert": "1"
}

car = Car(**_data)
assert to_dict(car) == _expected
```
### <a name="dataclass-example"/>Dataclass example</a>
```python
from validate_it import *
from dataclasses import dataclass


@schema
@dataclass
class Simple:
    a: int
    b: int


simple = Simple(a=1, b=2)
simple.a = 2
simple.b = 3

try:
    simple.a = 'not int'
except TypeError:
    print("Wrong type")
```

### <a name="simple-mapping-example"/>Simple mapping example</a>
```python
from validate_it import *


@schema
class User:
    first_name: str = Options(alias="f")
    last_name: str = Options(alias="l")

_in_data = {
    "f": "John",
    "l": "Connor"
}

user = User(**_in_data)

assert to_dict(user) == {"first_name": "John", "last_name": "Connor"}
```

### <a name="nested-mapping-example"/>Nested mapping example</a>
```python
from validate_it import *
from accordion import compress


@schema
class Player:
    nickname: str = Options(alias="info.nickname")
    intelligence: int = Options(alias="characteristics/0")
    dexterity: int = Options(alias="characteristics/1")
    strength: int = Options(alias="characteristics/2")
    vitality: int = Options(alias="characteristics/3")

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

player = Player(**compress(_in_data))

assert to_dict(player) == {
    "nickname": "Killer777", 
    "intelligence": 7, 
    "dexterity": 55, 
    "strength": 11, 
    "vitality": 44
}
```

and back:
```python
from validate_it import *
from accordion import expand


@schema
class Player:
    nickname: str = Options(rename="info.nickname")
    intelligence: int = Options(rename="characteristics/0")
    dexterity: int = Options(rename="characteristics/1")
    strength: int = Options(rename="characteristics/2")
    vitality: int = Options(rename="characteristics/3")

_in_data = {
    "nickname": "Killer777", 
    "intelligence": 7, 
    "dexterity": 55, 
    "strength": 11, 
    "vitality": 44
}

player = Player(**_in_data)

assert expand(to_dict(player)) == {
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
Tested with `python3.6`, `python3.7`, `pypy3.6-7.0.0`

### <a name="contribution"/>Contribution how-to</a>
###### Run tests:
* clone repo: `git clone <your-fork>`
* create and activate your virtualenv
* `pip install -r requirements.txt && pip install -r dev-requirements`
* `./run_tests.sh`
