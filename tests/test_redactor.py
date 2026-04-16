"""Tests for env_surgeon.redactor."""
from __future__ import annotations

import pytest

from env_surgeon.parser import EnvEntry, EnvFile
from env_surgeon.redactor import RedactResult, is_clean, redact_keys


def _make_env(*pairs: tuple[str, str]) -> EnvFile:
    entries = [
        EnvEntry(key=k, value=v, raw=f"{k}={v}", comment=None)
        for k, v in pairs
    ]
    return EnvFile(entries=entries, path=None)


# ---------------------------------------------------------------------------
# is_clean
# ---------------------------------------------------------------------------

def test_is_clean_all_found():
    env = _make_env(("A", "1"), ("B", "2"))
    result = redact_keys(env, ["A"])
    assert is_clean(result)


def test_is_clean_missing_key_not_clean():
    env = _make_env(("A", "1"))
    result = redact_keys(env, ["MISSING"])
    assert not is_clean(result)


# ---------------------------------------------------------------------------
# Removal behaviour
# ---------------------------------------------------------------------------

def test_redact_single_key_removes_entry():
    env = _make_env(("SECRET", "hunter2"), ("PORT", "8080"))
    result = redact_keys(env, ["SECRET"])
    keys = [e.key for e in result.entries]
    assert "SECRET" not in keys
    assert "PORT" in keys


def test_redact_records_removed_keys():
    env = _make_env(("A", "1"), ("B", "2"), ("C", "3"))
    result = redact_keys(env, ["A", "C"])
    assert sorted(result.removed_keys) == ["A", "C"]


def test_redact_multiple_keys():
    env = _make_env(("X", "x"), ("Y", "y"), ("Z", "z"))
    result = redact_keys(env, ["X", "Z"])
    remaining = [e.key for e in result.entries]
    assert remaining == ["Y"]


def test_redact_preserves_comment_entries():
    comment_entry = EnvEntry(key=None, value=None, raw="# a comment", comment="# a comment")
    env = EnvFile(
        entries=[comment_entry, EnvEntry(key="A", value="1", raw="A=1", comment=None)],
        path=None,
    )
    result = redact_keys(env, ["A"])
    assert any(e.comment is not None for e in result.entries)


# ---------------------------------------------------------------------------
# Missing key handling
# ---------------------------------------------------------------------------

def test_missing_key_recorded_in_not_found():
    env = _make_env(("A", "1"))
    result = redact_keys(env, ["GHOST"])
    assert "GHOST" in result.not_found_keys


def test_ignore_missing_suppresses_not_found():
    env = _make_env(("A", "1"))
    result = redact_keys(env, ["GHOST"], ignore_missing=True)
    assert result.not_found_keys == []
    assert is_clean(result)


def test_empty_key_list_returns_all_entries():
    env = _make_env(("A", "1"), ("B", "2"))
    result = redact_keys(env, [])
    assert len(result.entries) == 2
    assert result.removed_keys == []
