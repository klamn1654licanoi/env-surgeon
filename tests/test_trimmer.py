"""Tests for env_surgeon.trimmer."""

from __future__ import annotations

import pytest

from env_surgeon.parser import EnvEntry, EnvFile
from env_surgeon.trimmer import TrimResult, is_clean, trim_env_file


def _make_env(*entries: EnvEntry) -> EnvFile:
    return EnvFile(entries=list(entries), path=None)


def _entry(key, value, comment=None, raw=""):
    return EnvEntry(key=key, value=value, comment=comment, raw=raw)


def _comment_entry(text):
    return EnvEntry(key=None, value=None, comment=text, raw=text)


# ---------------------------------------------------------------------------
# is_clean
# ---------------------------------------------------------------------------

def test_clean_file_has_no_trimmed_entries():
    env = _make_env(_entry("FOO", "bar"), _entry("BAZ", "qux"))
    result = trim_env_file(env)
    assert is_clean(result)


def test_value_with_trailing_space_is_not_clean():
    env = _make_env(_entry("FOO", "bar   "))
    result = trim_env_file(env)
    assert not is_clean(result)
    assert "FOO" in result.trimmed_values


def test_value_with_leading_space_is_not_clean():
    env = _make_env(_entry("FOO", "  bar"))
    result = trim_env_file(env)
    assert not is_clean(result)
    assert "FOO" in result.trimmed_values


def test_key_with_trailing_space_is_not_clean():
    env = _make_env(_entry("FOO  ", "bar"))
    result = trim_env_file(env)
    assert not is_clean(result)
    assert "FOO" in result.trimmed_keys


def test_trimmed_value_is_correct():
    env = _make_env(_entry("DB_URL", "  postgres://localhost  "))
    result = trim_env_file(env)
    assert result.entries[0].value == "postgres://localhost"


def test_trimmed_key_is_correct():
    env = _make_env(_entry(" API_KEY ", "abc123"))
    result = trim_env_file(env)
    assert result.entries[0].key == "API_KEY"


def test_comment_entry_passes_through_unchanged():
    comment = _comment_entry("# this is a comment")
    env = _make_env(comment, _entry("FOO", "bar"))
    result = trim_env_file(env)
    assert result.entries[0].key is None
    assert result.entries[0].comment == "# this is a comment"


def test_none_value_treated_as_empty_string():
    env = _make_env(_entry("EMPTY", None))
    result = trim_env_file(env)
    assert result.entries[0].value == ""
    assert is_clean(result)


def test_multiple_dirty_entries_all_reported():
    env = _make_env(
        _entry("FOO", "  val1  "),
        _entry("BAR", "val2  "),
        _entry("BAZ", "val3"),
    )
    result = trim_env_file(env)
    assert "FOO" in result.trimmed_values
    assert "BAR" in result.trimmed_values
    assert "BAZ" not in result.trimmed_values
