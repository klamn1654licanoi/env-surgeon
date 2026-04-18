"""Tests for env_surgeon.freezer."""
from __future__ import annotations

import pytest

from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.freezer import freeze_env_file, is_clean


def _make_env(*pairs: tuple) -> EnvFile:
    entries = [
        EnvEntry(key=k, value=v, comment=None, raw_line=None)
        for k, v in pairs
    ]
    return EnvFile(path="test.env", entries=entries)


def test_no_interpolation_is_clean():
    env = _make_env(("HOST", "localhost"), ("PORT", "5432"))
    result = freeze_env_file(env)
    assert is_clean(result)
    assert result.frozen_keys == []
    assert len(result.entries) == 2


def test_interpolated_value_is_frozen():
    env = _make_env(("BASE", "http://example.com"), ("URL", "${BASE}/api"))
    result = freeze_env_file(env)
    assert is_clean(result)
    assert "URL" in result.frozen_keys
    url_entry = next(e for e in result.entries if e.key == "URL")
    assert url_entry.value == "http://example.com/api"


def test_original_reference_key_unchanged():
    env = _make_env(("BASE", "http://example.com"), ("URL", "${BASE}/api"))
    result = freeze_env_file(env)
    base_entry = next(e for e in result.entries if e.key == "BASE")
    assert base_entry.value == "http://example.com"
    assert "BASE" not in result.frozen_keys


def test_unresolved_reference_recorded():
    env = _make_env(("URL", "${MISSING}/path"))
    result = freeze_env_file(env)
    assert not is_clean(result)
    assert "URL" in result.unresolved_keys
    # value left unchanged
    url_entry = next(e for e in result.entries if e.key == "URL")
    assert "${MISSING}" in url_entry.value


def test_comment_entries_passed_through():
    comment = EnvEntry(key=None, value=None, comment="# section", raw_line="# section\n")
    kv = EnvEntry(key="FOO", value="bar", comment=None, raw_line=None)
    env = EnvFile(path="test.env", entries=[comment, kv])
    result = freeze_env_file(env)
    assert result.entries[0].key is None
    assert result.entries[0].comment == "# section"


def test_multiple_interpolations_in_one_value():
    env = _make_env(
        ("SCHEME", "https"),
        ("HOST", "example.com"),
        ("URL", "${SCHEME}://${HOST}"),
    )
    result = freeze_env_file(env)
    assert is_clean(result)
    url_entry = next(e for e in result.entries if e.key == "URL")
    assert url_entry.value == "https://example.com"
