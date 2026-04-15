"""Unit tests for env_surgeon.templater."""
from __future__ import annotations

from pathlib import Path

import pytest

from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.templater import template_env_file, TemplateResult


def _make_env(entries):
    """Build an EnvFile from a list of (key, value) or (None, raw_line) tuples."""
    parsed_entries = []
    for item in entries:
        if item[0] is None:
            parsed_entries.append(EnvEntry(key=None, value=None, comment=item[1], raw_line=item[1]))
        else:
            parsed_entries.append(EnvEntry(key=item[0], value=item[1], comment=None, raw_line=None))
    return EnvFile(entries=parsed_entries, path=Path("test.env"))


def test_non_secret_values_preserved():
    env = _make_env([("APP_NAME", "myapp"), ("PORT", "8080")])
    result = template_env_file(env)
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["APP_NAME"] == "myapp"
    assert values["PORT"] == "8080"
    assert result.is_clean()


def test_secret_values_replaced_with_placeholder():
    env = _make_env([("API_KEY", "super-secret"), ("APP_NAME", "myapp")])
    result = template_env_file(env, placeholder="<REPLACE_ME>")
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["API_KEY"] == "<REPLACE_ME>"
    assert values["APP_NAME"] == "myapp"
    assert "API_KEY" in result.stripped_keys
    assert not result.is_clean()


def test_password_key_is_stripped():
    env = _make_env([("DB_PASSWORD", "hunter2")])
    result = template_env_file(env)
    assert "DB_PASSWORD" in result.stripped_keys
    assert result.entries[0].value == ""


def test_comments_kept_by_default():
    env = _make_env([(None, "# section header"), ("PORT", "8080")])
    result = template_env_file(env)
    comment_entries = [e for e in result.entries if e.key is None]
    assert len(comment_entries) == 1


def test_comments_stripped_when_requested():
    env = _make_env([(None, "# section header"), ("PORT", "8080")])
    result = template_env_file(env, keep_comments=False)
    comment_entries = [e for e in result.entries if e.key is None]
    assert len(comment_entries) == 0


def test_extra_pattern_treated_as_secret():
    env = _make_env([("MY_INTERNAL_CERT", "cert-data"), ("PORT", "8080")])
    result = template_env_file(env, extra_secret_patterns=[r"CERT"])
    assert "MY_INTERNAL_CERT" in result.stripped_keys
    assert "PORT" not in result.stripped_keys


def test_empty_placeholder_default():
    env = _make_env([("SECRET_KEY", "abc123")])
    result = template_env_file(env)
    assert result.entries[0].value == ""
