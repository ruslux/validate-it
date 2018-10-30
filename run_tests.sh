#!/bin/bash

export PYTHONPATH="$(pwd)"/validate_it:$PYTHONPATH
coverage run --source='./validate_it/' -m pytest tests -vv && coverage combine && coverage report
