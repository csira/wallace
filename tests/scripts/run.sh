#!/bin/bash

. env/bin/activate
PYTHONPATH=./ python tests/scripts/_run_tests.py
deactivate
