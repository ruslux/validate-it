# Validate-it

[![Build Status](https://travis-ci.org/ruslux/validate-it.svg?branch=master)](https://travis-ci.org/ruslux/validate-it) 
[![Coverage Status](https://coveralls.io/repos/github/ruslux/validate-it/badge.svg?branch=master)](https://coveralls.io/github/ruslux/validate-it)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ruslux/validate-it/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ruslux/validate-it)
[![PyPI version](https://badge.fury.io/py/validate-it.svg)](https://badge.fury.io/py/validate-it)

- [About](#about)
- [Installation](#installation)
- [Example](#example)
- [Requirements](#requirements)

### <a name="about"/>About</a>
Yet another schema validator.


### <a name="installation"/>Installation</a>
With pip:
```bash
pip install validate-it
```

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
