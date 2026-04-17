"""Tests for env_surgeon.scanner and cli_scan."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.scanner import scan_directory, ScanResult
from env_surgeon.cli_scan import scan_command


def _write(path: Path, content: str = "KEY=val\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_finds_dotenv_file(tmp_path):
    _write(tmp_path / ".env")
    result = scan_directory(tmp_path)
    assert any(p.name == ".env" for p in result.found)
    assert result.file_count() == 1
    assert not result.is_empty()


def test_finds_named_variants(tmp_path):
    for name in (".env.local", ".env.production", ".env.test"):
        _write(tmp_path / name)
    result = scan_directory(tmp_path)
    assert result.file_count() == 3


def test_empty_file_is_skipped(tmp_path):
    _write(tmp_path / ".env", "")
    result = scan_directory(tmp_path)
    assert result.file_count() == 0
    assert len(result.skipped) == 1


def test_max_depth_limits_recursion(tmp_path):
    deep = tmp_path / "a" / "b" / "c"
    _write(deep / ".env")
    result = scan_directory(tmp_path, max_depth=2)
    assert result.file_count() == 0


def test_hidden_dirs_skipped_by_default(tmp_path):
    _write(tmp_path / ".hidden" / ".env")
    result = scan_directory(tmp_path, skip_hidden_dirs=True)
    assert result.file_count() == 0


def test_hidden_dirs_included_when_flag_off(tmp_path):
    _write(tmp_path / ".hidden" / ".env")
    result = scan_directory(tmp_path, skip_hidden_dirs=False)
    assert result.file_count() == 1


def test_cli_scan_exits_0(tmp_path):
    _write(tmp_path / ".env")
    runner = CliRunner()
    r = runner.invoke(scan_command, [str(tmp_path)])
    assert r.exit_code == 0
    assert ".env" in r.output


def test_cli_scan_no_files_exits_1(tmp_path):
    runner = CliRunner()
    r = runner.invoke(scan_command, [str(tmp_path)])
    assert r.exit_code == 1


def test_cli_scan_json_output(tmp_path):
    import json
    _write(tmp_path / ".env.local")
    runner = CliRunner()
    r = runner.invoke(scan_command, [str(tmp_path), "--json"])
    data = json.loads(r.output)
    assert "found" in data
    assert any(".env.local" in p for p in data["found"])
