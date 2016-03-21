#!/bin/bash -vx
set -e
rm -f dist/*

echo "Building the python package"
rm -Rf ./dist
mkdir dist
./pylint.sh
py.test --cov-report xml --cov vision --junitxml dist/results.xml tests
python setup.py sdist
