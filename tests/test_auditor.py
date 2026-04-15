"""Tests for env_surgeon.auditor."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from env_surgeon.parser import parse_env_file
from env_surgeon.auditor import audit_env_file, AuditIssue


def _write_env(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent(content))
    return p


def test_no_issues_clean_file(tmp_path):
    path = _write_env(tmp_path, """
        HOST=localhost
        PORT=5432
        DEBUG=false
    """)
    env_file = parse_env_file(path)
    result = audit_env_file(env_file)
    assert result.issues == []
    assert not result.has_errors
    assert not result.has_warnings


def test_duplicate_key_is_error(tmp_path):
    path = _write_env(tmp_path, """
        HOST=localhost
        HOST=remotehost
    """)
    env_file = parse_env_file(path)
    result = audit_env_file(env_file)
    errors = [i for i in result.issues if i.severity == "error"]
    assert len(errors) == 1
    assert errors[0].key == "HOST"
    assert "Duplicate" in errors[0].message


def test_empty_value_is_warning(tmp_path):
    path = _write_env(tmp_path, """
        API_KEY=
        HOST=localhost
    """)
    env_file = parse_env_file(path)
    result = audit_env_file(env_file)
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert len(warnings) == 1
    assert warnings[0].key == "API_KEY"


def test_lowercase_key_is_info(tmp_path):
    path = _write_env(tmp_path, """
        host=localhost
    """)
    env_file = parse_env_file(path)
    result = audit_env_file(env_file)
    infos = [i for i in result.issues if i.severity == "info"]
    assert len(infos) == 1
    assert infos[0].key == "host"


def test_summary_counts(tmp_path):
    path = _write_env(tmp_path, """
        HOST=localhost
        HOST=other
        API_KEY=
    """)
    env_file = parse_env_file(path)
    result = audit_env_file(env_file)
    assert result.has_errors
    assert result.has_warnings
    assert "1 error(s)" in result.summary()
    assert "1 warning(s)" in result.summary()


def test_audit_issue_str():
    issue = AuditIssue(key="FOO", message="Something wrong.", severity="error", line=3)
    text = str(issue)
    assert "ERROR" in text
    assert "[FOO]" in text
    assert "line 3" in text


def test_comments_and_blanks_ignored(tmp_path):
    path = _write_env(tmp_path, """
        # This is a comment
        HOST=localhost

        PORT=8080
    """)
    env_file = parse_env_file(path)
    result = audit_env_file(env_file)
    assert result.issues == []


def test_multiple_empty_values_all_warned(tmp_path):
    """Each key with an empty value should produce its own warning."""
    path = _write_env(tmp_path, """
        API_KEY=
        SECRET=
        HOST=localhost
    """)
    env_file = parse_env_file(path)
    result = audit_env_file(env_file)
    warnings = [i for i in result.issues if i.severity == "warning"]
    warned_keys = {w.key for w in warnings}
    assert len(warnings) == 2
    assert warned_keys == {"API_KEY", "SECRET"}
