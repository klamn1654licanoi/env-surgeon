"""Tests for the `interpolate` CLI sub-command."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.cli_interpolate import interpolate_command


@pytest.fixture()
def runner():
    return CliRunner()


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def test_interpolate_clean_file_exits_0(tmp_path, runner):
    p = _write(tmp_path, "HOST=localhost\nPORT=5432\n")
    result = runner.invoke(interpolate_command, [str(p), "--no-color"])
    assert result.exit_code == 0
    assert "HOST=localhost" in result.output
    assert "PORT=5432" in result.output


def test_interpolate_resolves_reference(tmp_path, runner):
    p = _write(tmp_path, "BASE=postgres\nURL=${BASE}://localhost\n")
    result = runner.invoke(interpolate_command, [str(p), "--no-color"])
    assert result.exit_code == 0
    assert "URL=postgres://localhost" in result.output


def test_interpolate_unresolved_shows_warning(tmp_path, runner):
    p = _write(tmp_path, "URL=${MISSING}/path\n")
    result = runner.invoke(interpolate_command, [str(p), "--no-color"])
    assert result.exit_code == 0
    assert "unresolved" in result.output.lower() or "unresolved" in (result.output + "").lower()


def test_interpolate_strict_exits_1_on_unresolved(tmp_path, runner):
    p = _write(tmp_path, "URL=${MISSING}/path\n")
    result = runner.invoke(interpolate_command, [str(p), "--no-color", "--strict"])
    assert result.exit_code == 1


def test_interpolate_strict_exits_0_when_clean(tmp_path, runner):
    p = _write(tmp_path, "HOST=localhost\n")
    result = runner.invoke(interpolate_command, [str(p), "--no-color", "--strict"])
    assert result.exit_code == 0


def test_interpolate_base_flag_resolves_external(tmp_path, runner):
    p = _write(tmp_path, "URL=${EXT_HOST}/api\n")
    result = runner.invoke(
        interpolate_command,
        [str(p), "--no-color", "--base", "EXT_HOST=example.com"],
    )
    assert result.exit_code == 0
    assert "URL=example.com/api" in result.output


def test_interpolate_invalid_base_pair_exits_2(tmp_path, runner):
    p = _write(tmp_path, "X=1\n")
    result = runner.invoke(interpolate_command, [str(p), "--base", "NOEQUALS"])
    assert result.exit_code == 2
