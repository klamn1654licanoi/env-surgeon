"""Tests for env_surgeon.stripper."""
from __future__ import annotations
import pytest
from env_surgeon.parser import EnvFile
from env_surgeon.stripper import strip_env_file, is_clean
from env_surgeon.parser import EnvEntry


def _make_env(entries: list[EnvEntry]) -> EnvFile:
    return EnvFile(path="test.env", entries=entries)


def _kv(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


def _comment(text: str = "# comment") -> EnvEntry:
    return EnvEntry(key=None, value=None, raw=text)


def _blank() -> EnvEntry:
    return EnvEntry(key=None, value=None, raw="")


def test_clean_file_is_clean():
    env = _make_env([_kv("A", "1"), _kv("B", "2")])
    result = strip_env_file(env)
    assert is_clean(result)
    assert len(result.entries) == 2


def test_removes_comments():
    env = _make_env([_comment(), _kv("A", "1")])
    result = strip_env_file(env, strip_comments=True, strip_blanks=False)
    assert result.removed_comments == 1
    assert result.removed_blanks == 0
    assert len(result.entries) == 1
    assert result.entries[0].key == "A"


def test_removes_blanks():
    env = _make_env([_blank(), _kv("A", "1"), _blank()])
    result = strip_env_file(env, strip_comments=False, strip_blanks=True)
    assert result.removed_blanks == 2
    assert result.removed_comments == 0
    assert len(result.entries) == 1


def test_keeps_comments_when_flag_off():
    env = _make_env([_comment(), _kv("X", "y")])
    result = strip_env_file(env, strip_comments=False, strip_blanks=True)
    assert result.removed_comments == 0
    assert len(result.entries) == 2


def test_keeps_blanks_when_flag_off():
    env = _make_env([_blank(), _kv("X", "y")])
    result = strip_env_file(env, strip_comments=True, strip_blanks=False)
    assert result.removed_blanks == 0
    assert len(result.entries) == 2


def test_is_clean_false_when_removed():
    env = _make_env([_comment(), _kv("A", "1")])
    result = strip_env_file(env)
    assert not is_clean(result)


def test_mixed_removal():
    env = _make_env([_comment("# top"), _blank(), _kv("A", "1"), _comment("# end")])
    result = strip_env_file(env)
    assert result.removed_comments == 2
    assert result.removed_blanks == 1
    assert len(result.entries) == 1
