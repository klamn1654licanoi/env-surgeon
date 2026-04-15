"""Tests for env_surgeon.exporter and cli_export."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.parser import EnvFile
from env_surgeon.exporter import ExportFormat, export_env
from env_surgeon.cli_export import export_command


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return p


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_export_json_contains_keys(tmp_path: Path) -> None:
    p = _write(tmp_path, "APP_NAME=myapp\nDB_PASSWORD=secret\n")
    env = EnvFile.parse(p)
    rendered = export_env(env, ExportFormat.JSON, mask=False)
    data = json.loads(rendered)
    assert data["APP_NAME"] == "myapp"
    assert data["DB_PASSWORD"] == "secret"


def test_export_json_masks_secrets(tmp_path: Path) -> None:
    p = _write(tmp_path, "APP_NAME=myapp\nDB_PASSWORD=secret\n")
    env = EnvFile.parse(p)
    rendered = export_env(env, ExportFormat.JSON, mask=True)
    data = json.loads(rendered)
    assert data["APP_NAME"] == "myapp"
    assert data["DB_PASSWORD"] == "***"


def test_export_shell_contains_export(tmp_path: Path) -> None:
    p = _write(tmp_path, "FOO=bar\n")
    env = EnvFile.parse(p)
    rendered = export_env(env, ExportFormat.SHELL, mask=False)
    assert 'export FOO="bar"' in rendered
    assert rendered.startswith("#!/usr/bin/env sh")


def test_export_toml_section_header(tmp_path: Path) -> None:
    p = _write(tmp_path, "FOO=bar\nBAZ=qux\n")
    env = EnvFile.parse(p)
    rendered = export_env(env, ExportFormat.TOML, mask=False)
    assert "[env]" in rendered
    assert 'FOO = "bar"' in rendered
    assert 'BAZ = "qux"' in rendered


def test_export_to_output_file(tmp_path: Path) -> None:
    p = _write(tmp_path, "KEY=value\n")
    env = EnvFile.parse(p)
    out = tmp_path / "out.json"
    with out.open("w") as fh:
        export_env(env, ExportFormat.JSON, mask=False, output=fh)
    data = json.loads(out.read_text())
    assert data["KEY"] == "value"


def test_cli_export_json_stdout(tmp_path: Path, runner: CliRunner) -> None:
    p = _write(tmp_path, "APP=test\nAPI_SECRET=topsecret\n")
    result = runner.invoke(export_command, [str(p), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["APP"] == "test"
    assert data["API_SECRET"] == "***"


def test_cli_export_no_mask_flag(tmp_path: Path, runner: CliRunner) -> None:
    p = _write(tmp_path, "API_SECRET=topsecret\n")
    result = runner.invoke(export_command, [str(p), "--format", "json", "--no-mask"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["API_SECRET"] == "topsecret"


def test_cli_export_to_file(tmp_path: Path, runner: CliRunner) -> None:
    p = _write(tmp_path, "X=1\n")
    out = tmp_path / "result.json"
    result = runner.invoke(export_command, [str(p), "--format", "json", "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["X"] == "1"
