# -*- coding: utf-8 -*-
import sys

import pytest


class ExpectedException(Exception):
    pass


class ExpectedMessage(Exception):
    pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    outcome = yield

    # Pytest 3.5+ has a new function for getting a maker from a node
    # In order to maintain compatability, prefer the newer function
    # (get_closest_marker) but use the old function (get_marker) if it
    # doesn't exist.
    marker_get_func = item.get_closest_marker if hasattr(item, 'get_closest_marker') else item.get_marker

    raises_marker = marker_get_func('raises')
    if raises_marker:
        exception = raises_marker.kwargs.get('exception')
        exception = exception or Exception
        message = raises_marker.kwargs.get('message')

        raised_exception = outcome.excinfo[1] if outcome.excinfo else None
        traceback = outcome.excinfo[2] if outcome.excinfo else None
        if isinstance(raised_exception, exception):
            outcome.force_result(None)
            if message is not None:
                try:
                    raised_message = str(raised_exception)
                    if message not in raised_message:
                        raise ExpectedMessage('"{}" not in "{}"'.format(message, raised_message))
                except(ExpectedMessage):
                    excinfo = sys.exc_info()
                    if traceback:
                        outcome.excinfo = excinfo[:2] + (traceback, )
                    else:
                        outcome.excinfo = excinfo
        else:
            try:
                raise raised_exception or ExpectedException('Expected exception {}, but it did not raise'.format(exception))
            except(ExpectedException):
                excinfo = sys.exc_info()
                if traceback:
                    outcome.excinfo = excinfo[:2] + (traceback, )
                else:
                    outcome.excinfo = excinfo
