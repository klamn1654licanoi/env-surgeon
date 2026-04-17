"""Tests for the clone CLI command."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.cli_clone import clone_command


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_clone_exits_0_on_success(tmp_path: Path, runner: CliRunner) -> None:
    src = _write(tmp_path, ".env", "FOO=1\nBAR=2\n")
    tgt = tmp_path / ".env.copy"
    result = runner.invoke(clone_command, [str(src), str(tgt)])
    assert result.exit_code == 0
    assert tgt.exists()


def test_clone_writes_keys_to_target(tmp_path: Path, runner: CliRunner) -> None:
    src = _write(tmp_path, ".env", "FOO=hello\n")
    tgt = tmp_path / ".env.out"
    runner.invoke(clone_command, [str(src), str(tgt)])
    assert "FOO" in tgt.read_text()


def test_clone_prefix_filters_keys(tmp_path: Path, runner: CliRunner) -> None:
    src = _write(tmp_path, ".env", "APP_X=1\nDB_Y=2\n")
    tgt = tmp_path / ".env.app"
    result = runner.invoke(clone_command, [str(src), str(tgt), "--prefix", "APP_"])
    assert result.exit_code == 0
    text = tgt.read_text()
    assert "APP_X" in text
    assert "DB_Y" not in text


def test_clone_dry_run_does_not_write(tmp_path: Path, runner: CliRunner) -> None:
    src = _write(tmp_path, ".env", "FOO=1\n")
    tgt = tmp_path / ".env.dry"
    result = runner.invoke(clone_command, [str(src), str(tgt), "--dry-run"])
    assert result.exit_code == 0
    assert not tgt.exists()
    assert "dry-run" in result.output


def test_clone_no_overwrite_reports_skipped(tmp_path: Path, runner: CliRunner) -> None:
    src = _write(tmp_path, ".env", "FOO=new\nBAR=2\n")
    tgt = _write(tmp_path, ".env.target", "FOO=old\n")
    result = runner.invoke(clone_command, [str(src), str(tgt), "--no-overwrite"])
    assert "Skipped" in result.output
    assert "FOO" in result.output
