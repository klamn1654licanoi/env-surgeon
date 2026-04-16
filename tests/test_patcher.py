"""Tests for env_surgeon.patcher."""
from __future__ import annotations

from pathlib import Path

import pytest

from env_surgeon.parser import EnvEntry, EnvFile
from env_surgeon.patcher import patch_env_file


def _make_env(pairs: dict[str, str]) -> EnvFile:
    entries = [
        EnvEntry(key=k, value=v, comment=None, raw_line=None)
        for k, v in pairs.items()
    ]
    return EnvFile(entries=entries, path=Path("test.env"))


def test_set_new_key():
    env = _make_env({"FOO": "bar"})
    result = patch_env_file(env, set_pairs={"NEW_KEY": "hello"})
    keys = [e.key for e in result.entries if e.key]
    assert "NEW_KEY" in keys
    assert "NEW_KEY" in result.set_keys


def test_update_existing_key():
    env = _make_env({"FOO": "old"})
    result = patch_env_file(env, set_pairs={"FOO": "new"})
    entry = next(e for e in result.entries if e.key == "FOO")
    assert entry.value == "new"
    assert "FOO" in result.updated_keys


def test_remove_key():
    env = _make_env({"FOO": "bar", "BAZ": "qux"})
    result = patch_env_file(env, remove_keys=["FOO"])
    keys = [e.key for e in result.entries if e.key]
    assert "FOO" not in keys
    assert "FOO" in result.removed_keys


def test_no_overwrite_skips_existing():
    env = _make_env({"FOO": "original"})
    result = patch_env_file(env, set_pairs={"FOO": "changed"}, no_overwrite=True)
    entry = next(e for e in result.entries if e.key == "FOO")
    assert entry.value == "original"
    assert "FOO" in result.skipped_keys
    assert "FOO" not in result.updated_keys


def test_remove_missing_key_goes_to_skipped():
    env = _make_env({"FOO": "bar"})
    result = patch_env_file(env, remove_keys=["MISSING"])
    assert "MISSING" in result.skipped_keys
    assert "MISSING" not in result.removed_keys


def test_is_clean_when_no_changes():
    env = _make_env({"FOO": "bar"})
    result = patch_env_file(env)
    assert result.is_clean()


def test_is_not_clean_when_updated():
    env = _make_env({"FOO": "bar"})
    result = patch_env_file(env, set_pairs={"FOO": "baz"})
    assert not result.is_clean()


def test_multiple_operations():
    env = _make_env({"A": "1", "B": "2", "C": "3"})
    result = patch_env_file(env, set_pairs={"B": "99", "D": "4"}, remove_keys=["C"])
    keys = [e.key for e in result.entries if e.key]
    assert "A" in keys
    assert "B" in keys
    assert "C" not in keys
    assert "D" in keys
    assert result.updated_keys == ["B"]
    assert result.removed_keys == ["C"]
    assert result.set_keys == ["D"]
