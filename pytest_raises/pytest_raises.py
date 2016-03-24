# -*- coding: utf-8 -*-
import sys

import pytest

class ExpectedException(Exception):
    pass

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    outcome = yield
    raises_marker = item.get_marker('raises')
    if raises_marker:
        exception = raises_marker.kwargs.get('exception')
        exception = exception or Exception

        raised_exception = outcome.excinfo[1] if outcome.excinfo else None
        traceback = outcome.excinfo[2] if outcome.excinfo else None
        if isinstance(raised_exception, exception):
            outcome.force_result(None)
        else:
            try:
                raise ExpectedException('Expected exception {}, but it did not raise'.format(exception))
            except(ExpectedException):
                excinfo = sys.exc_info()
                if traceback:
                    outcome.excinfo = excinfo[:2] + (traceback, )
                else:
                    outcome.excinfo = excinfo
