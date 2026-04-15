"""Integration tests for the `rename` CLI command."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.cli_rename import rename_command


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def test_rename_exits_0_on_success(tmp_path, runner):
    env = _write(tmp_path, "OLD_KEY=hello\nOTHER=world\n")
    result = runner.invoke(rename_command, [str(env), "-r", "OLD_KEY=NEW_KEY"])
    assert result.exit_code == 0
    assert "NEW_KEY=hello" in result.output


def test_rename_missing_key_exits_1(tmp_path, runner):
    env = _write(tmp_path, "PRESENT=yes\n")
    result = runner.invoke(rename_command, [str(env), "-r", "GHOST=OTHER"])
    assert result.exit_code == 1


def test_rename_ignore_missing_exits_0(tmp_path, runner):
    env = _write(tmp_path, "PRESENT=yes\n")
    result = runner.invoke(
        rename_command, [str(env), "-r", "GHOST=OTHER", "--ignore-missing"]
    )
    assert result.exit_code == 0


def test_rename_in_place_modifies_file(tmp_path, runner):
    env = _write(tmp_path, "TOKEN=secret\n")
    result = runner.invoke(
        rename_command, [str(env), "-r", "TOKEN=API_TOKEN", "--in-place"]
    )
    assert result.exit_code == 0
    contents = env.read_text()
    assert "API_TOKEN=secret" in contents
    assert "TOKEN=secret" not in contents


def test_rename_invalid_pair_exits_2(tmp_path, runner):
    env = _write(tmp_path, "FOO=bar\n")
    result = runner.invoke(rename_command, [str(env), "-r", "NODIVIDER"])
    assert result.exit_code == 2


def test_rename_multiple_keys(tmp_path, runner):
    env = _write(tmp_path, "A=1\nB=2\nC=3\n")
    result = runner.invoke(
        rename_command, [str(env), "-r", "A=X", "-r", "C=Z"]
    )
    assert result.exit_code == 0
    assert "X=1" in result.output
    assert "B=2" in result.output
    assert "Z=3" in result.output
