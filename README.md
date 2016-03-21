pytest-raises
===================================

[![Current Build Status](https://travis-ci.org/Authentise/pytest-raises.svg?branch=master)](https://travis-ci.org/Authentise/pytest-raises)

A [pytest][] plugin implementation of pytest.raises as a pytest.mark fixture

Features
--------

Adds functionality for marking tests with a `pytest.mark.raises` fixture, which functions similarly to using `with pytest.raises`


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

Marking a test with the `@pytest.mark.raises()` decorator will mark that the code the test executes is expected to raise an error.  This is different from `@pytest.mark.xfail()` as it does not mean the test itself might fail, but instead that the "pass" for the test is that the code raises an error.

It accepts an `exception` keyword argument, which is the class of error expected to be raised.

It will allow tests which raise errors to pass.  The main usage is to assert that an error of a specific type is raise.

A very simple example is:

```python
import pytest

class SomeException(Exception):
    pass

class AnotherException(Exception):
    pass

@pytest.mark.raises(exception = SomeException)
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
    pytest.mark.raises(SomeException('the message'), exception=SomeException),
    pytest.mark.raises(AnotherException('the message'), exception=AnotherException),
    pytest.mark.raises(Exception('the message')),
])
def test_mark_raises(error):
    if error:
        raise error

```

All of these tests pass.  These examples are actual [tests for this plugin][].

License
-------

Distributed under the terms of the [MIT][] license, "pytest-raises" is free and open source software


Issues
------

If you encounter any problems, please [file an issue][] along with a detailed description.

[MIT]: http://opensource.org/licenses/MIT
[file an issue]: https://github.com/Authentise/pytest-raises/issues
[pytest]: https://github.com/pytest-dev/pytest
[tests for this plugin]: https://github.com/Authentise/pytest-raises/blob/master/tests/test_raises.py
[pip]: https://pypi.python.org/pypi/pip/
[PyPI]: https://pypi.python.org/pypi
