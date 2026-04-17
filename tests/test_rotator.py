"""Tests for env_surgeon.rotator"""
from __future__ import annotations

import pytest
from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.rotator import rotate_env_file, is_clean, _generate_secret


def _make_env(*pairs: tuple[str, str]) -> EnvFile:
    entries = [
        EnvEntry(key=k, value=v, comment=None, raw=f"{k}={v}")
        for k, v in pairs
    ]
    return EnvFile(path=".env", entries=entries)


def test_generate_secret_default_length():
    s = _generate_secret()
    assert len(s) == 32


def test_generate_secret_custom_length():
    s = _generate_secret(16)
    assert len(s) == 16


def test_rotate_replaces_value_with_provided_replacement():
    env = _make_env(("DB_PASS", "old"))
    result = rotate_env_file(env, ["DB_PASS"], {"DB_PASS": "newpass"})
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["DB_PASS"] == "newpass"
    assert "DB_PASS" in result.rotated


def test_rotate_generates_random_when_no_replacement():
    env = _make_env(("API_KEY", "old_secret"))
    result = rotate_env_file(env, ["API_KEY"])
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["API_KEY"] != "old_secret"
    assert len(values["API_KEY"]) == 32


def test_rotate_unaffected_keys_unchanged():
    env = _make_env(("SAFE", "keep"), ("SECRET", "old"))
    result = rotate_env_file(env, ["SECRET"], {"SECRET": "new"})
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["SAFE"] == "keep"


def test_missing_key_recorded_in_not_found():
    env = _make_env(("A", "1"))
    result = rotate_env_file(env, ["MISSING"])
    assert "MISSING" in result.not_found
    assert not is_clean(result)


def test_is_clean_when_all_keys_found():
    env = _make_env(("TOKEN", "abc"))
    result = rotate_env_file(env, ["TOKEN"], {"TOKEN": "xyz"})
    assert is_clean(result)


def test_rotate_multiple_keys():
    env = _make_env(("A", "1"), ("B", "2"), ("C", "3"))
    result = rotate_env_file(env, ["A", "C"], {"A": "aa", "C": "cc"})
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["A"] == "aa"
    assert values["B"] == "2"
    assert values["C"] == "cc"
    assert sorted(result.rotated) == ["A", "C"]
