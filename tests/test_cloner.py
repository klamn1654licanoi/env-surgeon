"""Tests for env_surgeon.cloner."""
from __future__ import annotations

from pathlib import Path

import pytest

from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.cloner import clone_env_file, is_clean, CloneResult


def _make_env(tmp_path: Path, content: str) -> EnvFile:
    p = tmp_path / ".env"
    p.write_text(content)
    return EnvFile.parse(p)


def test_clone_all_keys(tmp_path: Path) -> None:
    src = _make_env(tmp_path, "FOO=1\nBAR=2\n")
    target = tmp_path / ".env.copy"
    result = clone_env_file(src, target)
    keys = [e.key for e in result.entries if e.key]
    assert "FOO" in keys
    assert "BAR" in keys
    assert result.skipped_keys == []
    assert is_clean(result)


def test_clone_prefix_filter(tmp_path: Path) -> None:
    src = _make_env(tmp_path, "APP_HOST=localhost\nAPP_PORT=5432\nDB_URL=postgres\n")
    target = tmp_path / ".env.app"
    result = clone_env_file(src, target, prefix="APP_")
    keys = [e.key for e in result.entries if e.key]
    assert "APP_HOST" in keys
    assert "APP_PORT" in keys
    assert "DB_URL" not in keys
    assert "DB_URL" in result.skipped_keys


def test_clone_explicit_keys(tmp_path: Path) -> None:
    src = _make_env(tmp_path, "FOO=1\nBAR=2\nBAZ=3\n")
    target = tmp_path / ".env.sub"
    result = clone_env_file(src, target, keys=["FOO", "BAZ"])
    keys = [e.key for e in result.entries if e.key]
    assert "FOO" in keys
    assert "BAZ" in keys
    assert "BAR" not in keys
    assert "BAR" in result.skipped_keys


def test_clone_no_overwrite_skips_existing(tmp_path: Path) -> None:
    src = _make_env(tmp_path, "FOO=new\nBAR=2\n")
    target = tmp_path / ".env.target"
    target.write_text("FOO=old\n")
    result = clone_env_file(src, target, overwrite=False)
    assert "FOO" in result.skipped_keys
    keys = [e.key for e in result.entries if e.key]
    assert "BAR" in keys
    assert not is_clean(result)


def test_clone_preserves_comments(tmp_path: Path) -> None:
    src = _make_env(tmp_path, "# header\nFOO=1\n")
    target = tmp_path / ".env.out"
    result = clone_env_file(src, target)
    comment_entries = [e for e in result.entries if e.key is None]
    assert len(comment_entries) >= 1
