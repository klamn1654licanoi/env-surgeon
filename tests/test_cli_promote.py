"""Tests for the promote CLI command."""
import pytest
from pathlib import Path
from click.testing import CliRunner
from env_surgeon.cli_promote import promote_command


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


@pytest.fixture
def runner():
    return CliRunner()


def test_promote_exits_0_on_success(runner, tmp_path):
    src = _write(tmp_path, "staging.env", "NEW=value\n")
    tgt = _write(tmp_path, "prod.env", "EXISTING=old\n")
    result = runner.invoke(promote_command, [str(src), str(tgt)])
    assert result.exit_code == 0


def test_promote_writes_key_to_target(runner, tmp_path):
    src = _write(tmp_path, "staging.env", "FEATURE_FLAG=true\n")
    tgt = _write(tmp_path, "prod.env", "OTHER=1\n")
    runner.invoke(promote_command, [str(src), str(tgt)])
    content = tgt.read_text()
    assert "FEATURE_FLAG" in content


def test_promote_no_overwrite_exits_1_when_skipped(runner, tmp_path):
    src = _write(tmp_path, "staging.env", "KEY=new\n")
    tgt = _write(tmp_path, "prod.env", "KEY=old\n")
    result = runner.invoke(promote_command, [str(src), str(tgt), "--no-overwrite"])
    assert result.exit_code == 1


def test_promote_dry_run_does_not_write(runner, tmp_path):
    src = _write(tmp_path, "staging.env", "X=1\n")
    tgt = _write(tmp_path, "prod.env", "Y=2\n")
    original = tgt.read_text()
    runner.invoke(promote_command, [str(src), str(tgt), "--dry-run"])
    assert tgt.read_text() == original


def test_promote_specific_key_only(runner, tmp_path):
    src = _write(tmp_path, "staging.env", "A=1\nB=2\n")
    tgt = _write(tmp_path, "prod.env", "")
    runner.invoke(promote_command, [str(src), str(tgt), "--key", "A"])
    content = tgt.read_text()
    assert "A" in content
    assert "B" not in content


def test_promote_output_flag_writes_to_new_file(runner, tmp_path):
    src = _write(tmp_path, "staging.env", "Z=99\n")
    tgt = _write(tmp_path, "prod.env", "")
    out = tmp_path / "result.env"
    runner.invoke(promote_command, [str(src), str(tgt), "--output", str(out)])
    assert out.exists()
    assert "Z" in out.read_text()
