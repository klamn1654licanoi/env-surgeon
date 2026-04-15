"""Integration tests for the `template` CLI command."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from env_surgeon.cli_template import template_command


@pytest.fixture()
def runner():
    return CliRunner()


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_template_exits_0_on_clean_file(runner, tmp_path):
    src = _write(tmp_path, "app.env", "PORT=8080\nAPP_NAME=myapp\n")
    result = runner.invoke(template_command, [str(src)])
    assert result.exit_code == 0


def test_template_creates_example_file(runner, tmp_path):
    src = _write(tmp_path, "app.env", "PORT=8080\n")
    runner.invoke(template_command, [str(src)])
    example = tmp_path / "app.env.example"
    assert example.exists()


def test_template_strips_secret_values(runner, tmp_path):
    src = _write(tmp_path, "app.env", "API_KEY=topsecret\nPORT=8080\n")
    runner.invoke(template_command, [str(src)])
    example = tmp_path / "app.env.example"
    content = example.read_text()
    assert "topsecret" not in content
    assert "PORT" in content


def test_template_custom_placeholder(runner, tmp_path):
    src = _write(tmp_path, "app.env", "DB_PASSWORD=secret\n")
    runner.invoke(template_command, [str(src), "--placeholder", "CHANGEME"])
    example = tmp_path / "app.env.example"
    assert "CHANGEME" in example.read_text()


def test_template_custom_output_path(runner, tmp_path):
    src = _write(tmp_path, "app.env", "PORT=8080\n")
    out = tmp_path / "custom.example"
    result = runner.invoke(template_command, [str(src), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_template_list_stripped_writes_to_stderr(runner, tmp_path):
    src = _write(tmp_path, "app.env", "SECRET_TOKEN=abc\nPORT=8080\n")
    result = runner.invoke(template_command, [str(src), "--list-stripped"])
    assert "SECRET_TOKEN" in (result.output + (result.stderr if hasattr(result, 'stderr') else ""))


def test_template_extra_pattern(runner, tmp_path):
    src = _write(tmp_path, "app.env", "MY_CERT=certdata\nPORT=8080\n")
    runner.invoke(template_command, [str(src), "--pattern", "CERT"])
    example = tmp_path / "app.env.example"
    content = example.read_text()
    assert "certdata" not in content
    assert "PORT" in content
