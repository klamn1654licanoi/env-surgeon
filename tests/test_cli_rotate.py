"""CLI tests for the rotate command."""
from __future__ import annotations

import pathlib
import pytest
from click.testing import CliRunner
from env_surgeon.cli_rotate import rotate_command


@pytest.fixture()
def runner():
    return CliRunner()


def _write(tmp_path: pathlib.Path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_rotate_exits_0_on_success(tmp_path, runner):
    f = _write(tmp_path, "API_KEY=old\n")
    result = runner.invoke(rotate_command, [f, "-k", "API_KEY", "-r", "API_KEY=newval"])
    assert result.exit_code == 0
    assert "rotated" in result.output


def test_rotate_missing_key_warns(tmp_path, runner):
    f = _write(tmp_path, "A=1\n")
    result = runner.invoke(rotate_command, [f, "-k", "MISSING"])
    assert "not found" in result.output or result.exit_code == 0


def test_rotate_strict_exits_1_on_missing(tmp_path, runner):
    f = _write(tmp_path, "A=1\n")
    result = runner.invoke(rotate_command, [f, "-k", "MISSING", "--strict"])
    assert result.exit_code == 1


def test_rotate_writes_output_file(tmp_path, runner):
    f = _write(tmp_path, "SECRET=old\n")
    out = str(tmp_path / "out.env")
    runner.invoke(rotate_command, [f, "-k", "SECRET", "-r", "SECRET=rotated", "--output", out])
    assert "rotated" in pathlib.Path(out).read_text()


def test_rotate_in_place_overwrites(tmp_path, runner):
    f = _write(tmp_path, "TOKEN=old\n")
    runner.invoke(rotate_command, [f, "-k", "TOKEN", "-r", "TOKEN=fresh", "--in-place"])
    assert "fresh" in pathlib.Path(f).read_text()


def test_rotate_bad_replacement_format(tmp_path, runner):
    f = _write(tmp_path, "X=1\n")
    result = runner.invoke(rotate_command, [f, "-k", "X", "-r", "NOEQUALS"])
    assert result.exit_code != 0
