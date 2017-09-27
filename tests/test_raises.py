# -*- coding: utf-8 -*-

def _run_tests_test(testdir, code, expected_output, expcted_return_code):
    testdir.makepyfile(code)
    result = testdir.runpytest('-v')
    result.stdout.fnmatch_lines(expected_output)
    assert result.ret == expcted_return_code

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
            '*::test_mark_raises_expected_exception PASSED',
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
            '*::test_mark_raises_no_args PASSED',
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
            '*::test_unmarked_test FAILED',
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
            '*::test_pytest_mark_raises_no_exception FAILED',
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
            '*::test_pytest_mark_raises_unexpected_exception FAILED',
            '*AnotherException: the message',
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
                pytest.mark.raises(SomeException('the message'), exception=SomeException),
                pytest.mark.raises(AnotherException('the message'), exception=AnotherException),
                pytest.mark.raises(Exception('the message')),
                pytest.mark.raises(AnotherException('the message'), exception=SomeException),
                SomeException('the message'),
                pytest.mark.raises(None, exception=SomeException),
            ])
            def test_mark_raises(error):
                if error:
                    raise error
        """,
        [
            '*::test_mark_raises*None* PASSED',
            '*::test_mark_raises*error1* PASSED',
            '*::test_mark_raises*error2* PASSED',
            '*::test_mark_raises*error3* PASSED',
            '*::test_mark_raises*error4* FAILED',
            '*::test_mark_raises*error5* FAILED',
            '*::test_mark_raises*None* FAILED',
        ],
        1
    )
