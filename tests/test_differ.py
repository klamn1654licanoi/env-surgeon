"""Tests for env_surgeon.differ."""

import textwrap
from pathlib import Path

import pytest

from env_surgeon.parser import parse_env_file
from env_surgeon.differ import DiffResult, diff_env_files, format_diff


def _write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content))
    return p


def test_identical_files_is_identical(tmp_path):
    content = "FOO=bar\nBAZ=qux\n"
    left = parse_env_file(_write_env(tmp_path, ".env.left", content))
    right = parse_env_file(_write_env(tmp_path, ".env.right", content))
    result = diff_env_files(left, right)
    assert result.is_identical


def test_missing_in_right(tmp_path):
    left = parse_env_file(_write_env(tmp_path, ".env.l", "FOO=1\nBAR=2\n"))
    right = parse_env_file(_write_env(tmp_path, ".env.r", "FOO=1\n"))
    result = diff_env_files(left, right)
    assert result.missing_in_right == ["BAR"]
    assert result.missing_in_left == []
    assert not result.changed


def test_missing_in_left(tmp_path):
    left = parse_env_file(_write_env(tmp_path, ".env.l", "FOO=1\n"))
    right = parse_env_file(_write_env(tmp_path, ".env.r", "FOO=1\nBAR=2\n"))
    result = diff_env_files(left, right)
    assert result.missing_in_left == ["BAR"]
    assert result.missing_in_right == []


def test_changed_values(tmp_path):
    left = parse_env_file(_write_env(tmp_path, ".env.l", "FOO=old\n"))
    right = parse_env_file(_write_env(tmp_path, ".env.r", "FOO=new\n"))
    result = diff_env_files(left, right)
    assert result.changed == {"FOO": ("old", "new")}
    assert result.is_identical is False


def test_mask_values(tmp_path):
    left = parse_env_file(_write_env(tmp_path, ".env.l", "SECRET=hunter2\n"))
    right = parse_env_file(_write_env(tmp_path, ".env.r", "SECRET=p@ssw0rd\n"))
    result = diff_env_files(left, right, mask_values=True)
    assert result.changed["SECRET"] == ("***", "***")


def test_format_diff_no_differences(tmp_path):
    content = "A=1\n"
    left = parse_env_file(_write_env(tmp_path, ".env.l", content))
    right = parse_env_file(_write_env(tmp_path, ".env.r", content))
    result = diff_env_files(left, right)
    assert format_diff(result) == "No differences found."


def test_format_diff_shows_all_sections(tmp_path):
    left = parse_env_file(_write_env(tmp_path, ".env.l", "ONLY_LEFT=1\nSHARED=old\n"))
    right = parse_env_file(_write_env(tmp_path, ".env.r", "ONLY_RIGHT=2\nSHARED=new\n"))
    result = diff_env_files(left, right)
    output = format_diff(result, left_label="dev", right_label="prod")
    assert "- [dev]" in output
    assert "+ [prod]" in output
    assert "SHARED" in output
    assert "old" in output
    assert "new" in output
