"""Tests for the `report` CLI command."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.cli_report import report_command


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_report_single_clean_file_exits_0(tmp_path: Path, runner: CliRunner) -> None:
    f = _write(tmp_path, ".env", "APP_NAME=myapp\nDEBUG=false\n")
    result = runner.invoke(report_command, [str(f), "--no-mask"])
    assert result.exit_code == 0
    assert "AUDIT" in result.output
    assert "No issues found" in result.output


def test_report_duplicate_key_exits_1(tmp_path: Path, runner: CliRunner) -> None:
    f = _write(tmp_path, ".env", "FOO=1\nFOO=2\n")
    result = runner.invoke(report_command, [str(f), "--no-mask"])
    assert result.exit_code == 1
    assert "ERROR" in result.output


def test_report_two_files_shows_diff(tmp_path: Path, runner: CliRunner) -> None:
    a = _write(tmp_path, ".env.a", "KEY=alpha\nONLY_A=yes\n")
    b = _write(tmp_path, ".env.b", "KEY=beta\nONLY_B=yes\n")
    result = runner.invoke(report_command, [str(a), str(b), "--no-mask", "--no-color"])
    assert "DIFF" in result.output
    assert "KEY" in result.output


def test_report_mask_flag_hides_secrets(tmp_path: Path, runner: CliRunner) -> None:
    f = _write(tmp_path, ".env", "API_SECRET=supersecret\nNAME=public\n")
    result = runner.invoke(report_command, [str(f), "--mask"])
    assert "supersecret" not in result.output
    assert "masked" in result.output.lower()


def test_report_output_file(tmp_path: Path, runner: CliRunner) -> None:
    f = _write(tmp_path, ".env", "X=1\n")
    out = tmp_path / "report.txt"
    result = runner.invoke(report_command, [str(f), "--no-mask", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "AUDIT" in content


def test_report_no_color_strips_ansi(tmp_path: Path, runner: CliRunner) -> None:
    a = _write(tmp_path, ".env.a", "K=1\n")
    b = _write(tmp_path, ".env.b", "K=2\n")
    result = runner.invoke(report_command, [str(a), str(b), "--no-mask", "--no-color"])
    assert "\x1b[" not in result.output
