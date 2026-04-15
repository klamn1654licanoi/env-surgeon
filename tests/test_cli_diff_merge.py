"""Integration tests for cli_diff and cli_merge commands."""
from __future__ import annotations

from pathlib import Path

import pytest

from env_surgeon.cli_diff import diff_command
from env_surgeon.cli_merge import merge_command


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


# ---------------------------------------------------------------------------
# diff_command
# ---------------------------------------------------------------------------

def test_diff_identical_returns_0(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\nBAZ=qux\n")
    b = _write(tmp_path, "b.env", "FOO=bar\nBAZ=qux\n")
    assert diff_command(a, b) == 0


def test_diff_different_returns_1(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\n")
    b = _write(tmp_path, "b.env", "FOO=changed\n")
    assert diff_command(a, b) == 1


def test_diff_missing_file_returns_2(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\n")
    assert diff_command(a, str(tmp_path / "missing.env")) == 2


def test_diff_no_color_strips_ansi(tmp_path, capsys):
    a = _write(tmp_path, "a.env", "FOO=bar\n")
    b = _write(tmp_path, "b.env", "FOO=baz\n")
    diff_command(a, b, no_color=True)
    captured = capsys.readouterr()
    assert "\x1b[" not in captured.out


# ---------------------------------------------------------------------------
# merge_command
# ---------------------------------------------------------------------------

def test_merge_no_conflict_writes_output(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "BAR=2\n")
    out = str(tmp_path / "merged.env")
    rc = merge_command([a, b], output=out)
    assert rc == 0
    merged = Path(out).read_text()
    assert "FOO=1" in merged
    assert "BAR=2" in merged


def test_merge_conflict_error_strategy_returns_1(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "FOO=2\n")
    rc = merge_command([a, b], strategy="error")
    assert rc == 1


def test_merge_last_wins_strategy(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=first\n")
    b = _write(tmp_path, "b.env", "FOO=last\n")
    out = str(tmp_path / "merged.env")
    rc = merge_command([a, b], output=out, strategy="last_wins")
    assert rc == 0
    assert "FOO=last" in Path(out).read_text()


def test_merge_invalid_strategy_returns_2(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    rc = merge_command([a], strategy="unknown")
    assert rc == 2


def test_merge_missing_source_returns_2(tmp_path):
    rc = merge_command([str(tmp_path / "ghost.env")])
    assert rc == 2


def test_merge_stdout_when_no_output(tmp_path, capsys):
    a = _write(tmp_path, "a.env", "KEY=value\n")
    rc = merge_command([a])
    assert rc == 0
    captured = capsys.readouterr()
    assert "KEY=value" in captured.out
