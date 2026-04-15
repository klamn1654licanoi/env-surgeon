"""Tests for env_surgeon.renamer."""
from __future__ import annotations

import pytest

from env_surgeon.parser import EnvEntry, EnvFile
from env_surgeon.renamer import RenameResult, rename_keys


def _make_env(*pairs: tuple[str, str]) -> EnvFile:
    entries = [
        EnvEntry(key=k, value=v, comment=None, raw=f"{k}={v}")
        for k, v in pairs
    ]
    return EnvFile(path="test.env", entries=entries)


def test_rename_single_key():
    env = _make_env(("OLD_KEY", "value"))
    result = rename_keys(env, {"OLD_KEY": "NEW_KEY"})
    assert result.is_clean()
    assert result.renamed == [("OLD_KEY", "NEW_KEY")]
    keys = [e.key for e in result.entries]
    assert "NEW_KEY" in keys
    assert "OLD_KEY" not in keys


def test_rename_preserves_value():
    env = _make_env(("TOKEN", "abc123"))
    result = rename_keys(env, {"TOKEN": "API_TOKEN"})
    renamed_entry = next(e for e in result.entries if e.key == "API_TOKEN")
    assert renamed_entry.value == "abc123"


def test_rename_multiple_keys():
    env = _make_env(("A", "1"), ("B", "2"), ("C", "3"))
    result = rename_keys(env, {"A": "X", "C": "Z"})
    assert result.is_clean()
    keys = [e.key for e in result.entries]
    assert keys == ["X", "B", "Z"]


def test_missing_key_recorded_in_not_found():
    env = _make_env(("PRESENT", "yes"))
    result = rename_keys(env, {"MISSING": "OTHER"})
    assert not result.is_clean()
    assert "MISSING" in result.not_found


def test_ignore_missing_flag_skips_silently():
    env = _make_env(("PRESENT", "yes"))
    result = rename_keys(env, {"MISSING": "OTHER"}, ignore_missing=True)
    assert result.is_clean()
    assert result.not_found == []


def test_comment_entries_passed_through_unchanged():
    comment_entry = EnvEntry(key=None, value=None, comment="# section", raw="# section")
    env = EnvFile(
        path="test.env",
        entries=[comment_entry, EnvEntry(key="FOO", value="bar", comment=None, raw="FOO=bar")],
    )
    result = rename_keys(env, {"FOO": "BAZ"})
    assert result.entries[0].comment == "# section"
    assert result.entries[1].key == "BAZ"


def test_untouched_keys_remain_unchanged():
    env = _make_env(("KEEP", "same"), ("RENAME_ME", "val"))
    result = rename_keys(env, {"RENAME_ME": "RENAMED"})
    keep_entry = next(e for e in result.entries if e.key == "KEEP")
    assert keep_entry.value == "same"
