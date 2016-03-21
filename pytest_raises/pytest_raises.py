# -*- coding: utf-8 -*-

import pytest

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    outcome = yield
    raises_marker = item.get_marker('raises')
    if raises_marker:
        exception = raises_marker.kwargs.get('exception')

        if exception:
            try:
                outcome.get_result()
            except (exception):
                pass

        outcome.force_result(True)
