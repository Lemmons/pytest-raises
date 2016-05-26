# -*- coding: utf-8 -*-


def test_pytest_mark_raises_expected_exception(testdir):
    testdir.makepyfile("""
        import pytest

        class SomeException(Exception):
            pass

        @pytest.mark.raises(exception = SomeException)
        def test_mark_raises_expected_exception():
            raise SomeException('the message')
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_mark_raises_expected_exception PASSED',
    ])

    assert result.ret == 0

def test_mark_raises_no_args(testdir):
    testdir.makepyfile("""
        import pytest

        class AnotherException(Exception):
            pass

        @pytest.mark.raises()
        def test_mark_raises_no_args():
            raise AnotherException('the message')
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_mark_raises_no_args PASSED',
    ])

    assert result.ret == 0

def test_unmarked_test(testdir):
    testdir.makepyfile("""
        import pytest

        class SomeException(Exception):
            pass

        def test_unmarked_test():
            raise SomeException('the message')
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_unmarked_test FAILED',
    ])

    assert result.ret == 1

def test_pytest_mark_raises_no_exception(testdir):
    testdir.makepyfile("""
        import pytest

        class SomeException(Exception):
            pass

        @pytest.mark.raises(exception = SomeException)
        def test_pytest_mark_raises_no_exception():
            pass
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_pytest_mark_raises_no_exception FAILED',
        "*Expected exception <class '*.SomeException'>, but it did not raise",
    ])

    assert result.ret == 1

def test_pytest_mark_raises_pass_through_unexpected_exception(testdir):
    testdir.makepyfile("""
        import pytest

        class SomeException(Exception):
            pass

        class AnotherException(Exception):
            pass

        @pytest.mark.raises(exception = SomeException)
        def test_pytest_mark_raises_pass_through_unexpected_exception():
            raise AnotherException('the message')

    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_pytest_mark_raises_pass_through_unexpected_exception FAILED',
        '*test_pytest_mark_raises_pass_through_unexpected_exception.AnotherException: the message',
    ])

    assert result.ret == 1

def test_pytest_mark_raises_parametrize(testdir):
    testdir.makepyfile("""
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
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_mark_raises*None* PASSED',
        '*::test_mark_raises*error1* PASSED',
        '*::test_mark_raises*error2* PASSED',
        '*::test_mark_raises*error3* PASSED',
        '*::test_mark_raises*error4* FAILED',
        '*::test_mark_raises*error5* FAILED',
        '*::test_mark_raises*6None* FAILED',
    ])

    assert result.ret == 1
