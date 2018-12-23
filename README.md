pytest-raises
===================================
[![Build Status](https://travis-ci.com/Lemmons/pytest-raises.svg?branch=master)](https://travis-ci.com/Lemmons/pytest-raises) [![codecov](https://codecov.io/gh/Lemmons/pytest-raises/branch/master/graph/badge.svg)](https://codecov.io/gh/Lemmons/pytest-raises)

A [pytest][] plugin implementation of pytest.raises as a pytest.mark fixture.

**Contents**

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
    - [Available Markers](#available-markers)
    - [Limitations on Markers](#limitations-on-markers)
    - [Available Parameters](#available-parameters)
    - [`@pytest.mark.raises` Examples](#pytestmarkraises-examples)
    - [`@pytest.mark.setup_raises` Examples](#pytestmarksetup_raises-examples)
- [License](#license)
- [Issues](#issues)

Features
--------

Adds functionality for marking tests with a `pytest.mark.raises` fixture, which
functions similarly to using `with pytest.raises`


Requirements
------------

- python 2.7 or above
- pytest 2.8.1 or above


Installation
------------

You can install "pytest-raises" via [pip][] from [PyPI][]

```
$ pip install pytest-raises
```

Usage
-----

Marking a test with the `@pytest.mark.raises()` or
`@pytest.mark.setup_raises` decorator will mark that the code the test
executes is **expected** to raise an error.  This is different from
`@pytest.mark.xfail()` as it does not mean the test itself might fail, but
instead that the "pass" for the test is that the code raises an error.

It will allow tests which raise errors to pass.  The main usage is to assert
that an error of a specific type is raise.

If a test is marked with `@pytest.mark.raises` or
`@pytest.mark.setup_raises` and it does **not** `raise` in the appropriate
testing phase, the test will be failed.

### Available Markers

This extension provides two markers for different phases of `pytest`:

- `@pytest.mark.raises`: for marking a function that should `raise` during
  the `pytest_runtest_call` phase.
    - This decorator can be used in place of the
      [`with pytest.raises(...)` context manager](https://docs.pytest.org/en/latest/assert.html#assertions-about-expected-exceptions).
- `@pytest.mark.setup_raises`: for marking a function that should `raise`
  during the `pytest_runtest_setup` phase.

### Limitations on Markers

1. Any test function decorated with `@pytest.mark.setup_raises` is assumed
   to have an empty function body

   ```python
   @pytest.mark.setup_raises()
   def test_something():
       pass
   ```

   This is because `pytest_runtest_call` may still be executed depending on
   what raised when.  So any code in the test function body may cause
   erroneous errors (particularly if you are using fixtures, since the
   fixture setup may be incomplete).

   See the [`@pytest.mark.setup_raises` Examples](#pytestmarksetup_raises-examples)
   for more information.

2. Since the function body of anything decorated with
   `@pytest.mark.setup_raises` is assumed to be empty, test functions that
   are decorated with both `@pytest.mark.raises`and
   `@pytest.mark.setup_raises` is **not** supported.

   The implementation details of this limitation are further documented in
   the `_pytest_raises_validation` function.

### Available Parameters

Both markers accept the following optional parameters:

- `exception=<Some Exception Class>`: the exact exception **class** that is
  expected to be raised.
- `message='some string'`: a verbatim message that is expected to be in the
  raised exception message.  Note that when `message` is supplied, the check
  performed is essentially `message in exception_message`.  So any substring
  can be used, but if the message is "too simple" you may get false
  positives.
- `match=r'some regular expression'`: a regular expression to be matched for
  in the raised exception message.  Note that
  [`re.match`](https://docs.python.org/3/library/re.html#re.match) is used
  (rather than `re.search`).  This behavior is identical to the
  `with pytest.raises` context manager.
- `match_flags=<regular expression flags>`: any regular expression _flags_
  desired to be used with the `match` argument.  For example,
  `match_flags=(re.IGNORECASE | re.DOTALL)`.  No validity checks are
  performed on the specified flags, but you will receive an error when the
  match is performed and invalid flags are provided (since the `re` module
  will not understand the flags).

**Note**: _the `message` and `match` arguments may **not** be supplied at the
same time.  Only one or the other may be provided._

### `@pytest.mark.raises` Examples

A very simple example is:

```python
import pytest

class SomeException(Exception):
    pass

class AnotherException(Exception):
    pass

@pytest.mark.raises(exception=SomeException)
def test_mark_raises_named():
    raise SomeException('the message')

@pytest.mark.raises()
def test_mark_raises_general():
    raise AnotherException('the message')

```

A more useful example using test parametrization is:

```python
import pytest

class SomeException(Exception):
    pass

class AnotherException(Exception):
    pass

@pytest.mark.parametrize('error', [
    None,
    pytest.param(
        SomeException('the message'),
        marks=pytest.mark.raises(exception=SomeException)
    ),
    pytest.param(
        AnotherException('the message'),
        marks=pytest.mark.raises(exception=AnotherException)
    ),
    pytest.param(
        Exception('the message'),
        marks=pytest.mark.raises()
    )
])
def test_mark_raises_demo(error):
    if error:
        raise error

```

All of these tests pass.  These examples are actual [tests for this plugin][]
(exact test case is in `test_pytest_raises_parametrize_demo` test).

### `@pytest.mark.setup_raises` Examples

Usage of the `@pytest.mark.setup_raises` decorator is likely to be uncommon,
but when it is needed there is no known alternative.  Consider the following
contrived example, where in a `conftest.py` we have the following check for
some custom marker we are concerned about:

```python
# in conftest.py
def pytest_runtest_setup(item):
    custom_marker = item.get_closest_marker('custom_marker')
    if custom_marker:
        valid = custom_marker.kwargs.get('valid', True)
        if not valid:
            raise ValueError('custom_marker.valid was False')
```

and two tests using this marker

```python
import pytest

@pytest.mark.custom_marker(valid=False)
@pytest.mark.setup_raises(
    exception=ValueError, match=r'.*was False$'
)
def test_mark_setup_raises_demo():
    pass

@pytest.mark.custom_marker(valid=True)
def test_all_good():
    pass
```

This example is in the [tests for this plugin][] in the
`test_pytest_mark_setup_raises_demo` test case.  This example is awkward, but
the idea is you can use `@pytest.mark.setup_raises` to catch expected errors
during the `pytest_runtest_setup` phase.  So when we used `custom_marker`
with `valid=False`, the `pytest_runtest_setup` will `raise` as expected, but
not when `valid=True`.

In the real world, the utility of `@pytest.mark.setup_raises` comes in when
you have potentially less control over the execution of fixtures or perhaps
want to stress-test custom markers or fixtures.  Consider writing a decorator
that auto-uses a fixture for a given test function, but deliberately provides
invalid arguments to the fixture.

In short: the chances are good that you will **not** need
`@pytest.mark.setup_raises` in the average testing framework.  However, if
you need to verify failures during the `pytest_runtest_setup` phase, it is
an invaluable tool.

**Reminder**: notice that when `@pytest.mark.setup_raises` is used, **the
function body should be exactly `pass`**.  The `pytest_runtest_setup` phase
has raised, meaning the setup for the test is incomplete.  Anything other
than an empty test function body of `pass` is **not** supported by this
extension.

License
-------

Distributed under the terms of the [MIT][] license, "pytest-raises" is free and
open source software.


Issues
------

If you encounter any problems, please [file an issue][] along with a detailed
description.

[MIT]: http://opensource.org/licenses/MIT
[file an issue]: https://github.com/Authentise/pytest-raises/issues
[pytest]: https://github.com/pytest-dev/pytest
[tests for this plugin]: https://github.com/Authentise/pytest-raises/blob/master/tests/test_raises.py
[pip]: https://pypi.python.org/pypi/pip/
[PyPI]: https://pypi.python.org/pypi
