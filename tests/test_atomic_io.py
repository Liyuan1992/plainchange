import pytest

from plainchange import atomic_io


@pytest.mark.parametrize("failures,winerror,success,attempts", [(2, 32, True, 3), (9, 5, False, 6), (1, None, False, 1)])
def test_replace_retries_only_bounded_windows_contention(tmp_path, monkeypatch, failures, winerror, success, attempts):
    source, target = tmp_path/'new', tmp_path/'current'
    source.write_text('new'); target.write_text('old')
    original = atomic_io.os.replace
    calls = []
    def replace(a, b):
        calls.append(1)
        if len(calls) <= failures:
            error = PermissionError('locked')
            if winerror is not None:
                error.winerror = winerror
            raise error
        original(a, b)
    monkeypatch.setattr(atomic_io.os, 'replace', replace)
    monkeypatch.setattr(atomic_io.time, 'sleep', lambda _: None)
    if success:
        atomic_io.replace_with_retry(source, target)
        assert target.read_text() == 'new'
    else:
        with pytest.raises(PermissionError):
            atomic_io.replace_with_retry(source, target)
        assert target.read_text() == 'old' and source.read_text() == 'new'
    assert len(calls) == attempts
