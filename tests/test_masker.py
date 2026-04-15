"""Tests for env_surgeon.masker."""

from __future__ import annotations

import pytest

from env_surgeon.masker import (
    MASK_PLACEHOLDER,
    MaskResult,
    is_secret_key,
    mask_env_file,
    _compile_patterns,
    DEFAULT_SECRET_PATTERNS,
)
from env_surgeon.parser import EnvEntry, EnvFile


def _make_env(*pairs: tuple[str, str]) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, comment=None, raw=f"{k}={v}") for k, v in pairs]
    return EnvFile(path="test.env", entries=entries)


# ---------------------------------------------------------------------------
# is_secret_key
# ---------------------------------------------------------------------------

def test_is_secret_key_matches_token():
    compiled = _compile_patterns(DEFAULT_SECRET_PATTERNS)
    assert is_secret_key("GITHUB_TOKEN", compiled) is True


def test_is_secret_key_matches_password():
    compiled = _compile_patterns(DEFAULT_SECRET_PATTERNS)
    assert is_secret_key("DB_PASSWORD", compiled) is True


def test_is_secret_key_does_not_match_plain_key():
    compiled = _compile_patterns(DEFAULT_SECRET_PATTERNS)
    assert is_secret_key("APP_NAME", compiled) is False


def test_is_secret_key_case_insensitive():
    compiled = _compile_patterns(DEFAULT_SECRET_PATTERNS)
    assert is_secret_key("db_secret", compiled) is True


# ---------------------------------------------------------------------------
# mask_env_file
# ---------------------------------------------------------------------------

def test_mask_replaces_secret_values():
    env = _make_env(("APP_NAME", "myapp"), ("API_KEY", "super-secret"))
    result = mask_env_file(env)
    d = result.as_dict()
    assert d["APP_NAME"] == "myapp"
    assert d["API_KEY"] == MASK_PLACEHOLDER


def test_mask_records_masked_keys():
    env = _make_env(("DB_PASSWORD", "s3cr3t"), ("HOST", "localhost"))
    result = mask_env_file(env)
    assert "DB_PASSWORD" in result.masked_keys
    assert "HOST" not in result.masked_keys


def test_mask_custom_placeholder():
    env = _make_env(("SECRET_KEY", "abc123"))
    result = mask_env_file(env, placeholder="[REDACTED]")
    assert result.as_dict()["SECRET_KEY"] == "[REDACTED]"


def test_mask_extra_patterns():
    env = _make_env(("MY_INTERNAL_CERT", "cert-data"), ("NORMAL", "value"))
    result = mask_env_file(env, extra_patterns=[r".*CERT.*"])
    assert result.as_dict()["MY_INTERNAL_CERT"] == MASK_PLACEHOLDER
    assert result.as_dict()["NORMAL"] == "value"


def test_mask_preserves_comment_entries():
    comment_entry = EnvEntry(key=None, value=None, comment="# section", raw="# section")
    env = EnvFile(
        path="test.env",
        entries=[comment_entry, EnvEntry(key="API_KEY", value="x", comment=None, raw="API_KEY=x")],
    )
    result = mask_env_file(env)
    assert result.entries[0].comment == "# section"
    assert result.entries[1].value == MASK_PLACEHOLDER


def test_mask_empty_file_returns_empty_result():
    env = EnvFile(path="empty.env", entries=[])
    result = mask_env_file(env)
    assert result.entries == []
    assert result.masked_keys == []
