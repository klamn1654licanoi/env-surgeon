"""Integration tests for the `mask` CLI sub-command."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.cli_mask import mask_command


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_mask_hides_secret_values(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "APP_NAME=myapp\nAPI_KEY=super-secret\n")
    runner = CliRunner()
    result = runner.invoke(mask_command, [str(env)])
    assert result.exit_code == 0
    assert "myapp" in result.output
    assert "super-secret" not in result.output
    assert "***" in result.output


def test_mask_custom_placeholder(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "DB_PASSWORD=hunter2\n")
    runner = CliRunner()
    result = runner.invoke(mask_command, [str(env), "--placeholder", "[HIDDEN]"])
    assert result.exit_code == 0
    assert "[HIDDEN]" in result.output
    assert "hunter2" not in result.output


def test_mask_extra_pattern(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "MY_CERT=cert-data\nHOST=localhost\n")
    runner = CliRunner()
    result = runner.invoke(mask_command, [str(env), "--extra-pattern", r".*CERT.*"])
    assert result.exit_code == 0
    assert "cert-data" not in result.output
    assert "localhost" in result.output


def test_mask_list_masked_flag(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "SECRET_KEY=abc\nNAME=app\n")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(mask_command, [str(env), "--list-masked"])
    assert result.exit_code == 0
    assert "SECRET_KEY" in result.stderr


def test_mask_no_secrets_list_masked(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "HOST=localhost\nPORT=5432\n")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(mask_command, [str(env), "--list-masked"])
    assert result.exit_code == 0
    assert "No keys were masked" in result.stderr


def test_mask_missing_file_returns_nonzero(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(mask_command, [str(tmp_path / "missing.env")])
    assert result.exit_code != 0
