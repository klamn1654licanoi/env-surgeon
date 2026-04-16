"""Tests for env_surgeon.promoter."""
import pytest
from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.promoter import promote_env_file, is_clean


def _make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(path="dummy.env", entries=entries)


def test_promote_new_key():
    source = _make_env({"NEW_KEY": "hello"})
    target = _make_env({"EXISTING": "world"})
    result = promote_env_file(source, target)
    keys = [e.key for e in result.entries if e.key]
    assert "NEW_KEY" in keys
    assert "EXISTING" in keys
    assert "NEW_KEY" in result.promoted


def test_promote_overwrite_existing():
    source = _make_env({"KEY": "new_val"})
    target = _make_env({"KEY": "old_val"})
    result = promote_env_file(source, target, overwrite=True)
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.value == "new_val"
    assert "KEY" in result.overwritten


def test_promote_no_overwrite_skips():
    source = _make_env({"KEY": "new_val"})
    target = _make_env({"KEY": "old_val"})
    result = promote_env_file(source, target, overwrite=False)
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.value == "old_val"
    assert "KEY" in result.skipped
    assert not is_clean(result)


def test_promote_specific_keys_only():
    source = _make_env({"A": "1", "B": "2", "C": "3"})
    target = _make_env({})
    result = promote_env_file(source, target, keys=["A", "C"])
    keys = [e.key for e in result.entries if e.key]
    assert "A" in keys
    assert "C" in keys
    assert "B" not in keys


def test_promote_missing_source_key_skipped():
    source = _make_env({"A": "1"})
    target = _make_env({})
    result = promote_env_file(source, target, keys=["A", "MISSING"])
    assert "MISSING" in result.skipped
    assert not is_clean(result)


def test_is_clean_when_all_promoted():
    source = _make_env({"X": "val"})
    target = _make_env({})
    result = promote_env_file(source, target)
    assert is_clean(result)
