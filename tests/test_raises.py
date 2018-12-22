# -*- coding: utf-8 -*-

def _run_tests_test(testdir, code, expected_output, expcted_return_code, conftest=None):
    if conftest:
        testdir.makeconftest(conftest)
    testdir.makepyfile(code)
    result = testdir.runpytest('-v')
    result.stdout.fnmatch_lines(expected_output)
    assert result.ret == expcted_return_code

####################################################################################################
# @pytest.mark.raises tests                                                                        #
####################################################################################################
def test_pytest_mark_raises_expected_exception(testdir):
    _run_tests_test(testdir, """
            import pytest

            class SomeException(Exception):
                pass

            @pytest.mark.raises(exception = SomeException)
            def test_mark_raises_expected_exception():
                raise SomeException('the message')
        """,
        [
            '*::test_mark_raises_expected_exception PASSED*',
        ],
        0
    )

def test_mark_raises_no_args(testdir):
    _run_tests_test(testdir, """
            import pytest

            class AnotherException(Exception):
                pass

            @pytest.mark.raises()
            def test_mark_raises_no_args():
                raise AnotherException('the message')
        """,
        [
            '*::test_mark_raises_no_args PASSED*',
        ],
        0
    )

def test_unmarked_test(testdir):
    _run_tests_test(testdir, """
            import pytest

            class SomeException(Exception):
                pass

            def test_unmarked_test():
                raise SomeException('the message')
        """,
        [
            '*::test_unmarked_test FAILED*',
        ],
        1
    )

def test_pytest_mark_raises_no_exception(testdir):
    _run_tests_test(testdir, """
            import pytest

            class SomeException(Exception):
                pass

            @pytest.mark.raises(exception = SomeException)
            def test_pytest_mark_raises_no_exception():
                pass
        """,
        [
            '*::test_pytest_mark_raises_no_exception FAILED*',
            "*Expected exception <class '*.SomeException'>, but it did not raise",
        ],
        1
    )

def test_pytest_mark_raises_unexpected_exception(testdir):
    _run_tests_test(testdir, """
            import pytest

            class SomeException(Exception):
                pass

            class AnotherException(Exception):
                pass

            @pytest.mark.raises(exception = SomeException)
            def test_pytest_mark_raises_unexpected_exception():
                raise AnotherException('the message')
        """,
        [
            '*::test_pytest_mark_raises_unexpected_exception FAILED*',
            # pylint: disable=line-too-long
            "*ExpectedException: Expected exception of type <class '*SomeException'>, but got exception of type <class '*AnotherException'> with message: the message",
        ],
        1
    )

def test_pytest_mark_raises_not_an_exception(testdir):
    _run_tests_test(testdir, """
            import pytest

            class NotAnException(object):
                pass

            @pytest.mark.raises(exception=NotAnException)
            def test_pytest_mark_raises_not_an_exception():
                pass
        """,
        [
            '*::test_pytest_mark_raises_not_an_exception FAILED*',
            # pylint: disable=line-too-long
            "PytestRaisesUsageError: @pytest.mark.raises: supplied `exception=<class '*NotAnException'>` is not a subclass of `BaseException`."

        ],
        1
    )

def test_pytest_mark_raises_not_an_exception_class(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.raises(exception=RuntimeError('bad'))
            def test_pytest_mark_raises_not_an_exception_class():
                pass
        """,
        [
            '*::test_pytest_mark_raises_not_an_exception_class FAILED*',
            'PytestRaisesUsageError: @pytest.mark.raises: supplied `exception` argument must be a Class, e.g., `exception=RuntimeError`.'
        ],
        1
    )

def test_pytest_mark_raises_expected_message(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.raises(message='the message')
            def test_pytest_mark_raises_expected_message():
                raise RuntimeError('the message')
        """,
        [
            '*::test_pytest_mark_raises_expected_message PASSED*'
        ],
        0
    )

def test_pytest_mark_raises_unexpected_message(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.raises(message='the message')
            def test_pytest_mark_raises_unexpected_message():
                raise RuntimeError('a different message')
        """,
        [
            '*::test_pytest_mark_raises_unexpected_message FAILED*',
            '*"the message" not in "a different message"*'
        ],
        1
    )

def test_pytest_mark_raises_expected_match(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.raises(match=r'.*Middle.*Road.*')
            def test_pytest_mark_raises_expected_match():
                raise RuntimeError('In The Middle Of The Road')
        """,
        [
            '*::test_pytest_mark_raises_expected_match PASSED*',
        ],
        0
    )

def test_pytest_mark_raises_expected_match_with_flags(testdir):
    _run_tests_test(testdir, """
            import pytest
            import re

            @pytest.mark.raises(match=r'.*middle.*road.*', match_flags=re.IGNORECASE)
            def test_pytest_mark_raises_expected_match_with_flags():
                raise RuntimeError('In The Middle Of The Road')
        """,
        [
            '*::test_pytest_mark_raises_expected_match_with_flags PASSED*',
        ],
        0
    )

def test_pytest_mark_raises_unexpected_match(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.raises(match='^middle$')
            def test_pytest_mark_raises_unexpected_match():
                raise RuntimeError('In The Middle Of The Road')
        """,
        [
            '*::test_pytest_mark_raises_unexpected_match FAILED*',
            '*ExpectedMessage: "^middle$" does not match raised message "In The Middle Of The Road"'
        ],
        1
    )

def test_pytest_mark_raises_message_and_match_fails(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.raises(message='some message', match=r'stuff')
            def test_pytest_mark_raises_message_and_match_fails():
                pass
        """,
        [
            '*::test_pytest_mark_raises_message_and_match_fails FAILED*',
            'PytestRaisesUsageError: @pytest.mark.raises: only `message="some message"` *OR* `match="stuff"` allowed, not both.'
        ],
        1
    )

def test_pytest_mark_raises_parametrize(testdir):
    _run_tests_test(testdir, """
            import pytest

            class SomeException(Exception):
                pass

            class AnotherException(Exception):
                pass

            @pytest.mark.parametrize('error', [
                None,
                pytest.param(
                    SomeException('the message'), marks=pytest.mark.raises(exception=SomeException)
                ),
                pytest.param(
                    AnotherException('the message'), marks=pytest.mark.raises(exception=AnotherException)
                ),
                pytest.param(
                    Exception('the message'), marks=pytest.mark.raises()
                ),
                pytest.param(
                    AnotherException('the message'), marks=pytest.mark.raises(exception=SomeException)
                ),
                SomeException('the message'),
                pytest.param(
                    None, marks=pytest.mark.raises(exception=SomeException)
                ),
                pytest.param(
                    SomeException('the message'), marks=pytest.mark.raises(exception=SomeException, message='the message')
                ),
                pytest.param(
                    SomeException('the message'),
                    marks=pytest.mark.raises(exception=SomeException, message='other message')
                ),
            ])
            def test_mark_raises(error):
                if error:
                    raise error
        """,
        [
            '*::test_mark_raises*None0* PASSED*',
            '*::test_mark_raises*error1* PASSED*',
            '*::test_mark_raises*error2* PASSED*',
            '*::test_mark_raises*error3* PASSED*',
            '*::test_mark_raises*error4* FAILED*',
            '*::test_mark_raises*error5* FAILED*',
            '*::test_mark_raises*None1* FAILED*',
            '*::test_mark_raises*error7* PASSED*',
            '*::test_mark_raises*error8* FAILED*',
            '*ExpectedMessage: "other message" not in "the message"',
        ],
        1
    )

####################################################################################################
# @pytest.mark.setup_raises tests                                                                  #
####################################################################################################
def test_pytest_mark_setup_raises_expected_exception(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.setup_raises(exception = ValueError)
            def test_mark_setup_raises_expected_exception():
                pass
        """,
        [
            '*::test_mark_setup_raises_expected_exception PASSED*',
        ],
        0,
        conftest="""
            def pytest_runtest_setup(item):
                raise ValueError('the message')
        """
    )

def test_pytest_mark_setup_raises_no_args(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.setup_raises()
            def test_mark_setup_raises_no_args():
                pass
        """,
        [
            '*::test_mark_setup_raises_no_args PASSED*',
        ],
        0,
        conftest="""
            def pytest_runtest_setup(item):
                raise RuntimeError()
        """
    )

def test_unmarked_test_setup(testdir):
    _run_tests_test(testdir, """
            def test_unmarked_test_setup():
                pass
        """,
        [
            '*::test_unmarked_test_setup ERROR*',
        ],
        1,
        conftest="""
            def pytest_runtest_setup(item):
                raise RuntimeError()
        """
    )

def test_pytest_mark_setup_raises_no_exception(testdir):
    _run_tests_test(testdir, """
            import pytest

            class DifferentException(Exception):
                pass

            @pytest.mark.setup_raises(exception = DifferentException)
            def test_pytest_mark_setup_raises_no_exception():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_no_exception FAILED*',
            "*Expected exception <class '*.DifferentException'>, but it did not raise",
        ],
        1
    )

def test_pytest_mark_setup_raises_unexpected_exception(testdir):
    _run_tests_test(testdir, """
            import pytest

            class SomeException(Exception):
                pass

            @pytest.mark.setup_raises(exception = SomeException)
            def test_pytest_mark_setup_raises_unexpected_exception():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_unexpected_exception FAILED*',
            # pylint: disable=line-too-long
            "*ExpectedException: Expected exception of type <class '*SomeException'>, but got exception of type <class '*AnotherException'> with message: the message",
        ],
        1,
        conftest="""
            class AnotherException(Exception):
                pass

            def pytest_runtest_setup(item):
                raise AnotherException('the message')
        """
    )

def test_pytest_mark_setup_raises_not_an_exception(testdir):
    _run_tests_test(testdir, """
            import pytest

            class NotAnException(object):
                pass

            @pytest.mark.setup_raises(exception=NotAnException)
            def test_pytest_mark_setup_raises_not_an_exception():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_not_an_exception FAILED*',
            # pylint: disable=line-too-long
            "PytestRaisesUsageError: @pytest.mark.setup_raises: supplied `exception=<class '*NotAnException'>` is not a subclass of `BaseException`."

        ],
        1
    )

def test_pytest_mark_setup_raises_not_an_exception_class(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.setup_raises(exception=RuntimeError('bad'))
            def test_pytest_mark_setup_raises_not_an_exception_class():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_not_an_exception_class FAILED*',
            # pylint: disable=line-too-long
            'PytestRaisesUsageError: @pytest.mark.setup_raises: supplied `exception` argument must be a Class, e.g., `exception=RuntimeError`.'
        ],
        1
    )

def test_pytest_mark_setup_raises_unexpected_exception_fixture(testdir):
    _run_tests_test(testdir, """
            import pytest

            class SomeException(Exception):
                pass

            class AnotherException(Exception):
                pass

            @pytest.fixture
            def raise_me():
                raise AnotherException('the message')

            @pytest.mark.setup_raises(exception = SomeException)
            def test_pytest_mark_setup_raises_unexpected_exception_fixture(raise_me):
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_unexpected_exception_fixture FAILED*',
            '*AnotherException*with message: the message',
        ],
        1
    )

def test_pytest_mark_setup_raises_expected_message(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.setup_raises(message='the message')
            def test_pytest_mark_setup_raises_expected_message():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_expected_message PASSED*'
        ],
        0,
        conftest="""
            def pytest_runtest_setup(item):
                raise RuntimeError('the message')
        """
    )

def test_pytest_mark_setup_raises_unexpected_message(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.setup_raises(message='the message')
            def test_pytest_mark_setup_raises_unexpected_message():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_unexpected_message FAILED*',
            '*"the message" not in "a different message"*'
        ],
        1,
        conftest="""
            def pytest_runtest_setup(item):
                raise RuntimeError('a different message')
        """
    )

def test_pytest_mark_setup_raises_expected_match(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.setup_raises(match=r'.*Middle.*Road.*')
            def test_pytest_mark_setup_raises_expected_match():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_expected_match PASSED*',
        ],
        0,
        conftest="""
            def pytest_runtest_setup(item):
                raise RuntimeError('In The Middle Of The Road')
        """
    )

def test_pytest_mark_setup_raises_expected_match_with_flags(testdir):
    _run_tests_test(testdir, """
            import pytest
            import re

            @pytest.mark.setup_raises(match=r'.*middle.*road.*', match_flags=re.IGNORECASE)
            def test_pytest_mark_setup_raises_expected_match_with_flags():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_expected_match_with_flags PASSED*',
        ],
        0,
        conftest="""
            def pytest_runtest_setup(item):
                raise RuntimeError('In The Middle Of The Road')
        """
    )

def test_pytest_mark_setup_raises_unexpected_match(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.setup_raises(match='^middle$')
            def test_pytest_mark_setup_raises_unexpected_match():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_unexpected_match FAILED*',
            '*ExpectedMessage: "^middle$" does not match raised message "In The Middle Of The Road"'
        ],
        1,
        conftest="""
            def pytest_runtest_setup(item):
                raise RuntimeError('In The Middle Of The Road')
        """
    )

def test_pytest_mark_setup_raises_message_and_match_fails(testdir):
    _run_tests_test(testdir, """
            import pytest

            @pytest.mark.setup_raises(message='some message', match=r'stuff')
            def test_pytest_mark_setup_raises_message_and_match_fails():
                pass
        """,
        [
            '*::test_pytest_mark_setup_raises_message_and_match_fails FAILED*',
            'PytestRaisesUsageError: @pytest.mark.setup_raises: only `message="some message"` *OR* `match="stuff"` allowed, not both.'
        ],
        1
    )
