# -*- coding: utf-8 -*-
import re
import sys

import pytest


class ExpectedException(Exception):       # pragma: no cover
    pass                                  # pragma: no cover


class ExpectedMessage(Exception):         # pragma: no cover
    pass                                  # pragma: no cover


class PytestRaisesUsageError(Exception):  # pragma: no cover
    pass                                  # pragma: no cover


def _pytest_fail_by_mark_or_set_excinfo(item, outcome, marker_name, ExceptionClass, failure_message, traceback):
    """
    Defer a test failure to a later stage, or set ``excinfo`` of ``outcome``, depending
    on ``marker_name``.  This function should only be called for test items that have
    failed -- the end result of calling this function for *any* ``item`` / ``outcome``
    is that the test will fail.

    .. warning::

        **This is a "private" function not intended to be called directly by external projects!**

    Depending on the stage at which this function is called, one of two actions will
    be performed:

    1. ``marker_name='setup_raises'``: a "secret" marker will be added to ``item``
       indicating that the test failed.  This marker is then checked at a later stage
       when it is safe to fail.  See documentation for :func:`_pytest_raises_validation`
       for more information.
    2. ``marker_name='raises'``: the ``outcome.excinfo`` will be populated with an
       exception traceback that will eventually (through ``pytest``) mark the test as
       failed.

    **Parameters**

    ``item``
        The ``pytest`` test item, e.g., what is supplied to
        ``pytest_runtest_setup(item)`` or ``pytest_runtest_call(item)``.

    ``outcome``
        The ``pytest`` test outcome for the ``@pytest.hookimpl(hookwrapper=True)`` hook
        wrappers, where ``outcome = yield``.

    ``marker_name``
        The string marker name.  Values are **assumed** to be ``'setup_raises'`` or
        ``'raises'`` **only**.

        - ``'setup_raises'``: call originates from ``pytest_runtest_setup`` hook wrapper.
        - ``'raises'``: call originates from ``pytest_runtest_call`` hook wrapper.

    ``ExceptionClass``
        The exception class to re-raise.  Expected to be :class:`ExpectedException` or
        :class:`ExpectedMessage`, but not strictly required.

    ``failure_message``
        The string failure message to mark with or re-raise, depending on the value
        of ``marker_name``.

    ``traceback``
        The traceback information if available, ``None`` otherwise.
    """
    # pylint: disable=unused-variable
    __tracebackhide__ = True
    if marker_name == 'setup_raises':
        # In the later stage when `fail` is called, it is nice to "simulate" an
        # exception by putting the expected exception class's name as a prefix.
        failure_message = '{}: {}'.format(ExceptionClass.__name__, failure_message)
        item.add_marker(pytest.mark.setup_raises_expected_exc_or_message_not_found(failure_message))
    else:  # marker_name == 'raises'
        # Avoid "while handling exception another exception occurred" scenarios.
        if issubclass(ExceptionClass, PytestRaisesUsageError):
            failure_message = '{}: {}'.format(ExceptionClass.__name__, failure_message)
            pytest.fail(failure_message, pytrace=False)
        else:
            try:
                raise ExceptionClass(failure_message)
            except(ExceptionClass):
                # 1. Try and set ``outcome.excinfo``.
                # 2. Sometimes (unknown when) ``outcome.excinfo`` will trigger an
                #    AttributeError even when the test raised.  So try and set the
                #    undocumented ``outcome._excinfo`` attribute instead.
                # 3. If setting ``outcome._excinfo`` fails, fallback on ``pytest.fail``.
                excinfo = sys.exc_info()
                if traceback:
                    excinfo = excinfo[:2] + (traceback, )
                try:
                    outcome.excinfo = excinfo
                # pylint: disable=bare-except
                except:
                    try:
                        # pylint: disable=protected-access
                        outcome._excinfo = excinfo
                    # pylint: disable=bare-except
                    except:  # pragma: no cover (no tests hit this, kept for safety).
                        pytest.fail(failure_message, pytrace=False)


def _pytest_raises_validation(item, outcome, marker_name):
    """
    Validate that the test ``item`` and corresponding ``outcome`` raised an exception
    of the correct class, and if supplied the exception message was as expected.  A
    given test that has been marked with either ``@pytest.mark.setup_raises`` or
    ``@pytest.mark.raises`` can fail in one of three ways:

    1. The test raised an exception of the correct exception class, but the exception
       message did not match what was specified using either ``message`` or ``match``
       parameters.
    2. The test raised an exception of the incorrect exception class (as specified by
       the ``exception`` argument).
    3. The test was marked with either ``@pytest.mark.setup_raises`` or
       ``@pytest.mark.raises``, but no exception was raised.

    In order to support hook wrappers for both ``pytest_runtest_setup`` and
    ``pytest_runtest_call``, a "handshake" must be performed using a "secret" marker.
    This handshake is only possible because this extension implements a hook wrapper
    for both ``pytest_runtest_setup`` and ``pytest_runtest_call``.  To better explain
    the handshake, we first examine the ``pytest_runtest_call`` hook wrapper.

    ``@pytest.mark.raises(...)`` execution:

        1. The test is run (``outcome = yield``).
        2. This method is called.  If any of the three cases above that indicate failure
           happen, the test is failed.
        3. The test is failed by calling :func:`_pytest_fail_by_mark_or_set_excinfo`,
           which in this case will set ``outcome.excinfo``.
        4. By setting ``outcome.excinfo``, ``pytest`` will take over at a later stage
           and report the test as failed with our message.

    ``@pytest.mark.setup_raises(...)`` execution:

        1. The test *setup* is run (``outcome = yield``).
        2. This method is called, If any of the three cases above that indicate failure
           happen, the test is *marked* for failure.
        3. The test is failed by calling :func:`_pytest_fail_by_mark_or_set_excinfo`,
           which adds a "secret" marker that includes the failure message.
        4. Officially, the entire ``pytest_runtest_setup`` phase is completed without
           any formal failure by this extension.
        5. The ``pytest_runtest_call`` is triggered by ``pytest``, and this method is
           called again.
        6. The "secret" marker is detected, and an explicit invocation of
           ``pytest.fail`` is issued, ultimately failing the test.

    This process is unfortunately a little contrived.  However, it is done this way
    because this extension needs to be able to mark tests as failed, not error.  For
    reasons unknown to the author, any of the following issued during the
    ``pytest_runtest_setup`` hook wrapper will cause the test to **ERROR** rather than
    **FAIL**:

    - Setting ``outcome.excinfo``: during the setup phase this is a write protected
      attribute.
    - Issuing ``pytest.fail(...)``: a call to ``pytest.fail(...)`` during the setup
      phase will trigger a test **error** rather than a failure.

    .. note::

        The use of this handshake has an important implication!  Since the "secret"
        marker must be checked for first in order to fail out early, this means that
        marking a test case with **both** ``@pytest.mark.setup_raises`` and
        ``@pytest.mark.raises`` **cannot** be supported.  In practice, this should not
        be done (it does not make sense, if your setup fails you cannot run the test
        reliably).

    **Parameters**

    ``item``
        The ``pytest`` test item, e.g., what is supplied to
        ``pytest_runtest_setup(item)`` or ``pytest_runtest_call(item)``.

    ``outcome``
        The ``pytest`` test outcome for the ``@pytest.hookimpl(hookwrapper=True)`` hook
        wrappers, where ``outcome = yield``.

    ``marker_name``
        The string marker name.  Values are **assumed** to be ``'setup_raises'`` or
        ``'raises'`` **only**.

        - ``'setup_raises'``: call originates from ``pytest_runtest_setup`` hook wrapper.
        - ``'raises'``: call originates from ``pytest_runtest_call`` hook wrapper.
    """
    # pylint: disable=unused-variable
    __tracebackhide__ = True
    # Pytest 3.5+ has a new function for getting a maker from a node
    # In order to maintain compatability, prefer the newer function
    # (get_closest_marker) but use the old function (get_marker) if it
    # doesn't exist.
    marker_get_func = item.get_closest_marker if hasattr(item, 'get_closest_marker') else item.get_marker

    # Short-circuit: if the "secret" marker is found, then this test failed during setup
    # and it is now safe to ``pytest.fail`` without causing an ERROR.
    secret_marker = marker_get_func('setup_raises_expected_exc_or_message_not_found')
    if secret_marker:
        # NOTE: pytrace=False because the existing call stack is unrelated to the
        # original failure processed during `pytest_runtest_setup` hook wrapper.
        pytest.fail(secret_marker.args[0], pytrace=False)

    raises_marker = marker_get_func(marker_name)
    if raises_marker:
        exception = raises_marker.kwargs.get('exception', Exception)
        try:
            if not issubclass(exception, BaseException):
                failure_message = '@pytest.mark.{0}: supplied `exception={1}` is not a subclass of `BaseException`.'.format(
                    marker_name, exception
                )
                _pytest_fail_by_mark_or_set_excinfo(
                    item, outcome, marker_name, PytestRaisesUsageError, failure_message, None
                )
                return
        except TypeError:
            failure_message = '@pytest.mark.{}: supplied `exception` argument must be a Class, e.g., `exception=RuntimeError`.'.format(
                marker_name
            )
            _pytest_fail_by_mark_or_set_excinfo(
                item, outcome, marker_name, PytestRaisesUsageError, failure_message, None
            )
            return

        message = raises_marker.kwargs.get('message', None)
        match_pattern = raises_marker.kwargs.get('match', None)
        match_flags = raises_marker.kwargs.get('match_flags', 0)  # 0 means no flags for `re.match`

        # Only `message` or `match` should be supplied at a time, not both.
        if message and match_pattern:
            failure_message = '@pytest.mark.{}: only `message="{}"` *OR* `match="{}"` allowed, not both.'.format(
                marker_name, message, match_pattern
            )
            _pytest_fail_by_mark_or_set_excinfo(
                item, outcome, marker_name, PytestRaisesUsageError, failure_message, None
            )
            return

        raised_exception = outcome.excinfo[1] if outcome.excinfo else None
        traceback = outcome.excinfo[2] if outcome.excinfo else None

        # This plugin needs to work around the other hooks, see:
        # https://docs.pytest.org/en/latest/writing_plugins.html#hookwrapper-executing-around-other-hooks
        outcome.force_result(None)

        # Case 1: test raised exception is correct class (or derived type), check
        # message if provided by user.
        if isinstance(raised_exception, exception):
            raised_message = str(raised_exception)
            failure_message = None
            if message is not None:
                if message not in raised_message:
                    failure_message = '"{}" not in "{}"'.format(message, raised_message)
            elif match_pattern is not None:
                if not re.match(match_pattern, raised_message, match_flags):
                    failure_message = '"{}" does not match raised message "{}"'.format(match_pattern, raised_message)
            if failure_message:
                _pytest_fail_by_mark_or_set_excinfo(
                    item, outcome, marker_name, ExpectedMessage, failure_message, traceback
                )
        # Case 2: test raised exception, but it was of an unexpected type.
        elif raised_exception:
            failure_message = 'Expected exception of type {}, but got exception of type {} with message: {}'.format(
                exception, type(raised_exception), str(raised_exception)
            )
            _pytest_fail_by_mark_or_set_excinfo(
                item, outcome, marker_name, ExpectedException, failure_message, traceback
            )
        # Case 3: test did _not_ raise exception, but was expected to.
        else:
            failure_message = 'Expected exception {}, but it did not raise'.format(exception)
            _pytest_fail_by_mark_or_set_excinfo(
                item, outcome, marker_name, ExpectedException, failure_message, traceback
            )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    # pylint: disable=unused-variable
    __tracebackhide__ = True
    outcome = yield
    _pytest_raises_validation(item, outcome, 'setup_raises')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    # pylint: disable=unused-variable
    __tracebackhide__ = True
    outcome = yield
    _pytest_raises_validation(item, outcome, 'raises')


# NOTE: this gets evaluated by consuming packages only.
def pytest_configure(config):  # pragma: no cover
    """
    Register the markers with pytest.

    See: https://docs.pytest.org/en/latest/writing_plugins.html#registering-markers
    """
    config.addinivalue_line(
        'markers',
        'setup_raises: expect pytest_runtest_setup phase to raise.'
    )
    config.addinivalue_line(
        'markers',
        'raises: expect pytest_runtest_call phase to raise.'
    )
