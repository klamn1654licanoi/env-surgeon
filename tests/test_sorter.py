"""Tests for env_surgeon.sorter and the sort CLI command."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.parser import EnvFile
from env_surgeon.sorter import sort_env_file
from env_surgeon.cli_sort import sort_command


def _make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Unit tests for sorter.sort_env_file
# ---------------------------------------------------------------------------

def test_already_sorted_is_clean():
    env = _make_env("ALPHA=1\nBETA=2\nZETA=3\n")
    result = sort_env_file(env)
    assert result.is_clean()
    assert result.sorted_order == ["ALPHA", "BETA", "ZETA"]


def test_unsorted_is_not_clean():
    env = _make_env("ZETA=3\nALPHA=1\nBETA=2\n")
    result = sort_env_file(env)
    assert not result.is_clean()
    assert result.sorted_order == ["ALPHA", "BETA", "ZETA"]


def test_reverse_sort():
    env = _make_env("ALPHA=1\nBETA=2\nZETA=3\n")
    result = sort_env_file(env, reverse=True)
    assert result.sorted_order == ["ZETA", "BETA", "ALPHA"]


def test_custom_key_order_comes_first():
    env = _make_env("ZETA=3\nALPHA=1\nBETA=2\n")
    result = sort_env_file(env, key_order=["BETA"])
    assert result.sorted_order[0] == "BETA"
    # Remaining keys are alphabetical
    assert result.sorted_order[1:] == ["ALPHA", "ZETA"]


def test_values_are_preserved_after_sort():
    env = _make_env("ZETA=hello\nALPHA=world\n")
    result = sort_env_file(env)
    entries = {e.key: e.value for e in result.entries if e.key}
    assert entries["ALPHA"] == "world"
    assert entries["ZETA"] == "hello"


def test_comment_only_lines_kept():
    env = _make_env("# header\nZETA=3\nALPHA=1\n")
    result = sort_env_file(env, comments_first=False)
    # First entry should be the comment
    assert result.entries[0].key is None
    assert "header" in result.entries[0].raw_line


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture
def runner():
    return CliRunner()


def test_sort_stdout(runner, tmp_path):
    p = _write(tmp_path, "ZETA=3\nALPHA=1\nBETA=2\n")
    res = runner.invoke(sort_command, [str(p)])
    assert res.exit_code == 0
    lines = [l for l in res.output.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys)


def test_sort_in_place(runner, tmp_path):
    p = _write(tmp_path, "ZETA=3\nALPHA=1\n")
    res = runner.invoke(sort_command, [str(p), "--in-place"])
    assert res.exit_code == 0
    content = p.read_text()
    assert content.index("ALPHA") < content.index("ZETA")


def test_sort_check_already_sorted_exits_0(runner, tmp_path):
    p = _write(tmp_path, "ALPHA=1\nZETA=3\n")
    res = runner.invoke(sort_command, [str(p), "--check"])
    assert res.exit_code == 0


def test_sort_check_unsorted_exits_1(runner, tmp_path):
    p = _write(tmp_path, "ZETA=3\nALPHA=1\n")
    res = runner.invoke(sort_command, [str(p), "--check"])
    assert res.exit_code == 1


def test_sort_output_file(runner, tmp_path):
    p = _write(tmp_path, "ZETA=3\nALPHA=1\n")
    out = tmp_path / "sorted.env"
    res = runner.invoke(sort_command, [str(p), "--output", str(out)])
    assert res.exit_code == 0
    content = out.read_text()
    assert content.index("ALPHA") < content.index("ZETA")
