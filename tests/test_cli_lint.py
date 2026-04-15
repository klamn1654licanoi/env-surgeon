"""Integration tests for the lint CLI command."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from env_surgeon.cli_lint import lint_command


@pytest.fixture()
def runner():
    return CliRunner()


def _write(tmp_path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_lint_clean_file_exits_0(runner, tmp_path):
    path = _write(tmp_path, "FOO=bar\nBAZ=qux\n")
    result = runner.invoke(lint_command, [path])
    assert result.exit_code == 0
    assert "ok" in result.output


def test_lint_duplicate_key_exits_1(runner, tmp_path):
    path = _write(tmp_path, "FOO=bar\nFOO=baz\n")
    result = runner.invoke(lint_command, [path])
    assert result.exit_code == 1
    assert "duplicate" in result.output


def test_lint_warning_exits_0_without_strict(runner, tmp_path):
    path = _write(tmp_path, "FOO=\n")
    result = runner.invoke(lint_command, [path])
    assert result.exit_code == 0


def test_lint_warning_exits_1_with_strict(runner, tmp_path):
    path = _write(tmp_path, "FOO=\n")
    result = runner.invoke(lint_command, ["--strict", path])
    assert result.exit_code == 1


def test_lint_no_color_strips_ansi(runner, tmp_path):
    path = _write(tmp_path, "FOO=bar\nFOO=baz\n")
    result = runner.invoke(lint_command, ["--no-color", path])
    assert "\x1b[" not in result.output
    assert "duplicate" in result.output


def test_lint_multiple_files(runner, tmp_path):
    p1 = tmp_path / "a.env"
    p2 = tmp_path / "b.env"
    p1.write_text("FOO=bar\n")
    p2.write_text("BAZ=qux\n")
    result = runner.invoke(lint_command, [str(p1), str(p2)])
    assert result.exit_code == 0
    assert result.output.count("ok") == 2
