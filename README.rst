pytest-raises
===================================

.. image:: https://travis-ci.org/Authentise/pytest-raises.svg?branch=master
    :target: https://travis-ci.org/Authentise/pytest-raises
    :alt: See Build Status on Travis CI

An implementation of pytest.raises as a pytest.mark fixture

----

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.


Features
--------

Adds functionality for marking tests with a `pytest.mark.raises` fixture, which functions similarly to using `with pytest.raises`


Requirements
------------

- python 2.7 or above
- pytest 2.8.1 or above


Installation
------------

You can install "pytest-raises" via `pip`_ from `PyPI`_::

    $ pip install pytest-raises


Usage
-----

Marking a test with the `@pytest.mark.raises()` decorator will mark that the code the test executes is expected to raise an error.  This is different from `@pytest.mark.xfail()` as it does not mean the test itself might fail, but instead that the "pass" for the test is that the code raises an error.

It accepts an `exception` keyword argument, which is the class of error expected to be raised.

It will allow tests which raise errors to pass.  The main usage is to assert that an error of a specific type is raise.

A very simple example is:
```
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
```
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

All of these tests pass.  These examples are actual tests for this plugin.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-raises" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/Lemmons/pytest-raises/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.org/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi
