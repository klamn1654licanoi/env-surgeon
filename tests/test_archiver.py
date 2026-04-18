"""Tests for env_surgeon.archiver"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.archiver import ArchiveResult, archive_env_file, is_clean
from env_surgeon.cli_archive import archive_command


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


FIXED_TS = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_archive_creates_file(tmp_path: Path) -> None:
    src = _write(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    result = archive_env_file(src, timestamp=FIXED_TS)
    assert result.archive_path.exists()
    assert result.archive_path != src


def test_archive_filename_contains_timestamp(tmp_path: Path) -> None:
    src = _write(tmp_path, ".env", "FOO=bar\n")
    result = archive_env_file(src, timestamp=FIXED_TS)
    assert "20240601T120000" in result.archive_path.name


def test_archive_key_count(tmp_path: Path) -> None:
    src = _write(tmp_path, ".env", "A=1\nB=2\n# comment\n")
    result = archive_env_file(src, timestamp=FIXED_TS)
    assert result.key_count == 2


def test_archive_custom_dir(tmp_path: Path) -> None:
    src = _write(tmp_path, ".env", "X=1\n")
    dest_dir = tmp_path / "backups"
    result = archive_env_file(src, archive_dir=dest_dir, timestamp=FIXED_TS)
    assert result.archive_path.parent == dest_dir
    assert dest_dir.exists()


def test_is_clean_true(tmp_path: Path) -> None:
    src = _write(tmp_path, ".env", "K=v\n")
    result = archive_env_file(src, timestamp=FIXED_TS)
    assert is_clean(result)


def test_missing_source_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        archive_env_file(tmp_path / "missing.env", timestamp=FIXED_TS)


def test_cli_archive_exits_0(tmp_path: Path) -> None:
    src = _write(tmp_path, ".env", "FOO=1\n")
    runner = CliRunner()
    result = runner.invoke(archive_command, [str(src)])
    assert result.exit_code == 0
    assert "archived" in result.output


def test_cli_archive_custom_dir(tmp_path: Path) -> None:
    src = _write(tmp_path, ".env", "FOO=1\n")
    dest = tmp_path / "bkp"
    runner = CliRunner()
    result = runner.invoke(archive_command, [str(src), "--dir", str(dest)])
    assert result.exit_code == 0
    assert dest.exists()
