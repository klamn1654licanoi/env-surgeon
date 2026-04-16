"""Tests for env_surgeon.deduplicator."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.deduplicator import KeepStrategy, deduplicate_env_file
from env_surgeon.parser import EnvFile
from env_surgeon.cli_dedup import dedup_command


def _make_env(entries: list[tuple[str | None, str | None]]) -> EnvFile:
    """Build a minimal EnvFile from (key, value) pairs; key=None means comment."""
    from env_surgeon.parser import EnvEntry

    env = EnvFile(path="test.env", entries=[])
    for lineno, (key, value) in enumerate(entries, start=1):
        env.entries.append(
            EnvEntry(
                key=key,
                value=value,
                raw=f"{key}={value}" if key else (value or ""),
                line_number=lineno,
                comment=None,
            )
        )
    return env


def test_no_duplicates_is_clean():
    env = _make_env([("A", "1"), ("B", "2"), ("C", "3")])
    result = deduplicate_env_file(env)
    assert result.is_clean()
    assert len(result.entries) == 3
    assert len(result.removed) == 0


def test_duplicate_keep_first():
    env = _make_env([("A", "1"), ("B", "2"), ("A", "99")])
    result = deduplicate_env_file(env, strategy=KeepStrategy.FIRST)
    assert not result.is_clean()
    keys = [e.key for e in result.entries if e.key]
    assert keys == ["A", "B"]
    kept_value = next(e.value for e in result.entries if e.key == "A")
    assert kept_value == "1"
    assert len(result.removed) == 1
    assert result.removed[0].value == "99"


def test_duplicate_keep_last():
    env = _make_env([("A", "1"), ("B", "2"), ("A", "99")])
    result = deduplicate_env_file(env, strategy=KeepStrategy.LAST)
    assert not result.is_clean()
    keys = [e.key for e in result.entries if e.key]
    assert keys == ["A", "B"]
    kept_value = next(e.value for e in result.entries if e.key == "A")
    assert kept_value == "99"
    assert result.removed[0].value == "1"


def test_comments_preserved():
    env = _make_env([(None, "# header"), ("A", "1"), ("A", "2")])
    result = deduplicate_env_file(env)
    comment_entries = [e for e in result.entries if e.key is None]
    assert len(comment_entries) == 1


def test_cli_dedup_stdout(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text("A=1\nB=2\nA=99\n")
    runner = CliRunner()
    res = runner.invoke(dedup_command, [str(env_path)])
    assert res.exit_code == 1  # duplicates found
    assert "A=1" in res.output
    assert "A=99" not in res.output


def test_cli_dedup_in_place(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text("X=hello\nY=world\nX=bye\n")
    runner = CliRunner()
    res = runner.invoke(dedup_command, ["--in-place", str(env_path)])
    assert res.exit_code == 1
    content = env_path.read_text()
    assert "X=hello" in content
    assert "X=bye" not in content


def test_cli_dedup_clean_exits_0(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text("A=1\nB=2\n")
    runner = CliRunner()
    res = runner.invoke(dedup_command, [str(env_path)])
    assert res.exit_code == 0
