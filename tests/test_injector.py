"""Tests for env_surgeon.injector."""
from __future__ import annotations

import pytest

from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.injector import inject_env_file, is_clean


def _make_env(*pairs: tuple) -> EnvFile:
    entries = [
        EnvEntry(key=k, value=v, comment=None, raw=f"{k}={v}")
        for k, v in pairs
    ]
    return EnvFile(path="test.env", entries=entries)


def test_inject_new_key():
    env = _make_env(("HOST", "localhost"))
    result = inject_env_file(env, {"PORT": "5432"})
    keys = [e.key for e in result.entries if e.key]
    assert "PORT" in keys
    assert "PORT" in result.injected
    assert is_clean(result)


def test_inject_overwrites_existing_by_default():
    env = _make_env(("HOST", "localhost"))
    result = inject_env_file(env, {"HOST": "remotehost"})
    entry = next(e for e in result.entries if e.key == "HOST")
    assert entry.value == "remotehost"
    assert "HOST" in result.overwritten
    assert result.injected == []


def test_inject_no_overwrite_skips_existing():
    env = _make_env(("HOST", "localhost"))
    result = inject_env_file(env, {"HOST": "remotehost"}, overwrite=False)
    entry = next(e for e in result.entries if e.key == "HOST")
    assert entry.value == "localhost"
    assert "HOST" in result.skipped
    assert not is_clean(result)


def test_inject_multiple_pairs():
    env = _make_env(("A", "1"))
    result = inject_env_file(env, {"B": "2", "C": "3"})
    keys = [e.key for e in result.entries if e.key]
    assert "B" in keys
    assert "C" in keys
    assert len(result.injected) == 2


def test_inject_with_comment():
    env = _make_env(("A", "1"))
    result = inject_env_file(env, {"B": "2"}, comment="added by CI")
    entry = next(e for e in result.entries if e.key == "B")
    assert entry.comment == "added by CI"


def test_inject_preserves_original_order():
    env = _make_env(("A", "1"), ("B", "2"), ("C", "3"))
    result = inject_env_file(env, {"D": "4"})
    keys = [e.key for e in result.entries if e.key]
    assert keys == ["A", "B", "C", "D"]


def test_inject_empty_pairs_is_clean():
    env = _make_env(("A", "1"))
    result = inject_env_file(env, {})
    assert is_clean(result)
    assert result.injected == []
    assert result.overwritten == []
