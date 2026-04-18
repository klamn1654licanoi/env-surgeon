"""Tests for env_surgeon.splitter."""
import pytest
from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.splitter import split_env_file, SplitResult


def _make_env(pairs: list) -> EnvFile:
    entries = []
    for item in pairs:
        if isinstance(item, str):
            entries.append(EnvEntry(key=None, value=None, comment=item, raw=item))
        else:
            k, v = item
            entries.append(EnvEntry(key=k, value=v, comment=None, raw=f"{k}={v}"))
    return EnvFile(path=None, entries=entries)


def test_split_by_detected_prefix():
    env = _make_env([("DB_HOST", "localhost"), ("DB_PORT", "5432"), ("APP_NAME", "myapp")])
    result = split_env_file(env)
    assert "DB" in result.buckets
    assert "APP" in result.buckets
    assert len(result.buckets["DB"]) == 2
    assert len(result.buckets["APP"]) == 1


def test_split_explicit_prefix_filters_others():
    env = _make_env([("DB_HOST", "localhost"), ("APP_NAME", "myapp"), ("CACHE_TTL", "300")])
    result = split_env_file(env, prefixes=["DB"])
    assert "DB" in result.buckets
    assert "APP" not in result.buckets
    assert any(e.key == "APP_NAME" for e in result.unmatched)
    assert any(e.key == "CACHE_TTL" for e in result.unmatched)


def test_no_underscore_goes_to_unmatched():
    env = _make_env([("PORT", "8080"), ("DB_URL", "postgres://")])
    result = split_env_file(env)
    assert any(e.key == "PORT" for e in result.unmatched)
    assert "DB" in result.buckets


def test_is_clean_when_all_assigned():
    env = _make_env([("DB_HOST", "localhost"), ("DB_PORT", "5432")])
    result = split_env_file(env)
    assert result.is_clean()


def test_is_not_clean_with_unmatched():
    env = _make_env([("PORT", "8080"), ("DB_HOST", "localhost")])
    result = split_env_file(env)
    assert not result.is_clean()


def test_comments_follow_next_key():
    env = _make_env(["# database settings", ("DB_HOST", "localhost")])
    result = split_env_file(env, include_comments=True)
    bucket = result.buckets.get("DB", [])
    assert any(e.key is None for e in bucket), "comment should be in DB bucket"


def test_trailing_comments_go_to_unmatched():
    env = _make_env([("DB_HOST", "localhost"), "# trailing comment"])
    result = split_env_file(env, include_comments=True)
    assert any(e.key is None for e in result.unmatched)


def test_prefix_case_insensitive_explicit():
    env = _make_env([("DB_HOST", "localhost")])
    result = split_env_file(env, prefixes=["db"])
    assert "DB" in result.buckets
