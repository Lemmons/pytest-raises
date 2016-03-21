# -*- coding: utf-8 -*-


def test_pytest_mark_raises(testdir):
    testdir.makepyfile("""
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

        def test_exception():
            raise SomeException('the message')
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_mark_raises_named PASSED',
        '*::test_mark_raises_general PASSED',
        '*::test_exception FAILED',
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
    ])

    assert result.ret == 1
