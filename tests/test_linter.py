"""Tests for env_surgeon.linter."""
from __future__ import annotations

import pytest

from env_surgeon.linter import LintSeverity, lint_env_file
from env_surgeon.parser import EnvFile


def _make_env(tmp_path, content: str) -> EnvFile:
    p = tmp_path / ".env"
    p.write_text(content)
    return EnvFile.parse(str(p))


def test_clean_file_has_no_violations(tmp_path):
    env = _make_env(tmp_path, "FOO=bar\nBAZ=qux\n")
    result = lint_env_file(env)
    assert result.is_clean
    assert not result.has_errors


def test_duplicate_key_is_error(tmp_path):
    env = _make_env(tmp_path, "FOO=bar\nFOO=baz\n")
    result = lint_env_file(env)
    errors = [v for v in result.violations if v.severity == LintSeverity.ERROR]
    assert len(errors) == 1
    assert "duplicate" in errors[0].message
    assert errors[0].key == "FOO"


def test_trailing_whitespace_is_warning(tmp_path):
    env = _make_env(tmp_path, "FOO= bar \n")
    result = lint_env_file(env)
    warnings = [v for v in result.violations if v.severity == LintSeverity.WARNING]
    assert any("whitespace" in w.message for w in warnings)


def test_lowercase_key_is_info(tmp_path):
    env = _make_env(tmp_path, "foo=bar\n")
    result = lint_env_file(env)
    infos = [v for v in result.violations if v.severity == LintSeverity.INFO]
    assert len(infos) == 1
    assert "uppercase" in infos[0].message


def test_empty_value_without_quotes_is_warning(tmp_path):
    env = _make_env(tmp_path, "FOO=\n")
    result = lint_env_file(env)
    warnings = [v for v in result.violations if v.severity == LintSeverity.WARNING]
    assert any("empty value" in w.message for w in warnings)


def test_violation_str_contains_severity_and_line(tmp_path):
    env = _make_env(tmp_path, "FOO=bar\nFOO=baz\n")
    result = lint_env_file(env)
    violation_str = str(result.violations[0])
    assert "ERROR" in violation_str
    assert "line" in violation_str


def test_has_errors_false_when_only_warnings(tmp_path):
    env = _make_env(tmp_path, "FOO=\n")
    result = lint_env_file(env)
    assert not result.has_errors


def test_comments_are_ignored(tmp_path):
    env = _make_env(tmp_path, "# this is a comment\nFOO=bar\n")
    result = lint_env_file(env)
    assert result.is_clean
