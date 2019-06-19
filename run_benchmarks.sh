#!/usr/bin/env bash

export PYTHONPATH="$(pwd)"/validate_it:$PYTHONPATH
python ./benchmarks/simple.py
python ./benchmarks/union.py
python ./benchmarks/nested_union.py
python ./benchmarks/_list.py
python ./benchmarks/_dict.py
