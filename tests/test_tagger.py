"""Tests for env_surgeon.tagger."""
from __future__ import annotations

from env_surgeon.parser import EnvEntry, EnvFile
from env_surgeon.tagger import tag_env_file


def _make_env(*pairs: tuple[str, str]) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs]
    return EnvFile(path=".env", entries=entries)


def test_tagged_keys_appear_in_tagged():
    env = _make_env(("DB_HOST", "localhost"), ("APP_PORT", "8080"), ("SECRET_KEY", "abc"))
    result = tag_env_file(env, tags={"database": ["DB_HOST"], "app": ["APP_PORT"]})
    tagged_keys = [e.key for e in result.tagged]
    assert "DB_HOST" in tagged_keys
    assert "APP_PORT" in tagged_keys


def test_untagged_keys_appear_in_untagged():
    env = _make_env(("DB_HOST", "localhost"), ("SECRET_KEY", "abc"))
    result = tag_env_file(env, tags={"database": ["DB_HOST"]})
    untagged_keys = [e.key for e in result.untagged]
    assert "SECRET_KEY" in untagged_keys
    assert "DB_HOST" not in untagged_keys


def test_filter_tag_returns_only_matching():
    env = _make_env(("DB_HOST", "localhost"), ("APP_PORT", "8080"), ("SECRET_KEY", "abc"))
    result = tag_env_file(
        env,
        tags={"database": ["DB_HOST", "SECRET_KEY"], "app": ["APP_PORT"]},
        filter_tag="database",
    )
    tagged_keys = [e.key for e in result.tagged]
    assert "DB_HOST" in tagged_keys
    assert "SECRET_KEY" in tagged_keys
    assert "APP_PORT" not in tagged_keys


def test_tag_map_only_includes_existing_keys():
    env = _make_env(("DB_HOST", "localhost"))
    result = tag_env_file(env, tags={"database": ["DB_HOST", "DB_PORT"]})
    assert result.tag_map["database"] == ["DB_HOST"]


def test_is_clean_when_all_tagged():
    env = _make_env(("DB_HOST", "localhost"))
    result = tag_env_file(env, tags={"database": ["DB_HOST"]})
    # no real untagged kv entries
    assert result.is_clean()


def test_is_not_clean_when_untagged_keys_exist():
    env = _make_env(("DB_HOST", "localhost"), ("ORPHAN", "value"))
    result = tag_env_file(env, tags={"database": ["DB_HOST"]})
    assert not result.is_clean()


def test_comment_entries_go_to_untagged():
    comment = EnvEntry(key=None, value=None, raw="# a comment")
    env = EnvFile(path=".env", entries=[comment])
    result = tag_env_file(env, tags={})
    assert comment in result.untagged
    assert result.tagged == []
