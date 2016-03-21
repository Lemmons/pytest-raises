PYTHON36=$(python -c 'import sys; print(sys.version_info[0] == 3 and sys.version_info[1] > 5 )')
if [ "$PYTHON36" == "True" ]; then
    exit 0
fi

set -x
PROJECT=pytest_raises
if [ -z "$1" ]; then
    FILES="setup.py $(find $PROJECT -maxdepth 3 -name "*.py" -print) $(find tests -maxdepth 3 -name "*.py" -print)"
else
    FILES="$1"
    echo "linting $FILES"
fi
pylint $FILES --reports=no
