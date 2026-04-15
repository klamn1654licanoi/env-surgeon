"""Tests for the audit CLI command."""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.cli_audit import audit_command


def _write(tmp_path: Path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_audit_clean_file_exits_0(runner: CliRunner, tmp_path: Path) -> None:
    path = _write(tmp_path, "API_KEY=abc123\nDATABASE_URL=postgres://localhost/db\n")
    result = runner.invoke(audit_command, [path, "--no-color"])
    assert result.exit_code == 0
    assert "No issues found" in result.output


def test_audit_duplicate_key_exits_1(runner: CliRunner, tmp_path: Path) -> None:
    path = _write(tmp_path, "FOO=bar\nFOO=baz\n")
    result = runner.invoke(audit_command, [path, "--no-color"])
    assert result.exit_code == 1
    assert "ERROR" in result.output
    assert "FOO" in result.output


def test_audit_empty_value_exits_0_without_strict(runner: CliRunner, tmp_path: Path) -> None:
    path = _write(tmp_path, "FOO=\n")
    result = runner.invoke(audit_command, [path, "--no-color"])
    assert result.exit_code == 0
    assert "WARNING" in result.output


def test_audit_empty_value_exits_1_with_strict(runner: CliRunner, tmp_path: Path) -> None:
    path = _write(tmp_path, "FOO=\n")
    result = runner.invoke(audit_command, [path, "--no-color", "--strict"])
    assert result.exit_code == 1
    assert "WARNING" in result.output


def test_audit_no_color_strips_ansi(runner: CliRunner, tmp_path: Path) -> None:
    path = _write(tmp_path, "foo=bar\n")
    result = runner.invoke(audit_command, [path, "--no-color"])
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    assert not ansi_escape.search(result.output)


def test_audit_missing_file_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    missing = str(tmp_path / "nonexistent.env")
    result = runner.invoke(audit_command, [missing, "--no-color"])
    assert result.exit_code != 0


def test_audit_info_issue_present(runner: CliRunner, tmp_path: Path) -> None:
    path = _write(tmp_path, "lowercase_key=value\n")
    result = runner.invoke(audit_command, [path, "--no-color"])
    assert "INFO" in result.output
    assert result.exit_code == 0
