"""Tests for env_surgeon.validator."""
from __future__ import annotations

import pathlib
import textwrap

import pytest

from env_surgeon.parser import EnvFile
from env_surgeon.validator import (
    SchemaRule,
    ValidationError,
    ValidationResult,
    load_schema,
    validate_env_file,
)


def _make_env(tmp_path: pathlib.Path, content: str) -> EnvFile:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent(content))
    return EnvFile.parse(p)


# ---------------------------------------------------------------------------
# load_schema
# ---------------------------------------------------------------------------

def test_load_schema_builds_rules():
    raw = {
        "DATABASE_URL": {"required": True, "pattern": r"postgres://.+"},
        "DEBUG": {"required": False, "description": "Enable debug mode"},
    }
    rules = load_schema(raw)
    assert len(rules) == 2
    assert rules[0].key == "DATABASE_URL"
    assert rules[0].required is True
    assert rules[0].pattern == r"postgres://.+"
    assert rules[1].key == "DEBUG"
    assert rules[1].required is False


# ---------------------------------------------------------------------------
# validate_env_file — happy path
# ---------------------------------------------------------------------------

def test_valid_file_passes(tmp_path):
    env = _make_env(tmp_path, """
        DATABASE_URL=postgres://localhost/db
        PORT=8080
    """)
    rules = [
        SchemaRule(key="DATABASE_URL", required=True, pattern=r"postgres://.+"),
        SchemaRule(key="PORT", required=True, pattern=r"\d+"),
    ]
    result = validate_env_file(env, rules)
    assert result.is_valid
    assert str(result) == "All schema rules passed."


# ---------------------------------------------------------------------------
# validate_env_file — missing required key
# ---------------------------------------------------------------------------

def test_missing_required_key_is_error(tmp_path):
    env = _make_env(tmp_path, "PORT=8080\n")
    rules = [SchemaRule(key="DATABASE_URL", required=True)]
    result = validate_env_file(env, rules)
    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].is_missing is True
    assert "DATABASE_URL" in str(result.errors[0])


def test_missing_optional_key_is_not_error(tmp_path):
    env = _make_env(tmp_path, "PORT=8080\n")
    rules = [SchemaRule(key="DEBUG", required=False)]
    result = validate_env_file(env, rules)
    assert result.is_valid


# ---------------------------------------------------------------------------
# validate_env_file — pattern mismatch
# ---------------------------------------------------------------------------

def test_pattern_mismatch_is_error(tmp_path):
    env = _make_env(tmp_path, "PORT=not-a-number\n")
    rules = [SchemaRule(key="PORT", required=True, pattern=r"\d+")]
    result = validate_env_file(env, rules)
    assert not result.is_valid
    assert result.errors[0].is_missing is False
    assert "not-a-number" in str(result.errors[0])


def test_multiple_errors_reported(tmp_path):
    env = _make_env(tmp_path, "PORT=bad\n")
    rules = [
        SchemaRule(key="DATABASE_URL", required=True),
        SchemaRule(key="PORT", required=True, pattern=r"\d+"),
    ]
    result = validate_env_file(env, rules)
    assert len(result.errors) == 2
    summary = str(result)
    assert "MISSING" in summary
    assert "INVALID" in summary
