"""Tests for env_surgeon.cli_profile"""
import json
from pathlib import Path
from click.testing import CliRunner
from env_surgeon.cli_profile import profile_command


def _write(tmp_path: Path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


runner = CliRunner()


def test_profile_exits_0(tmp_path):
    p = _write(tmp_path, "FOO=bar\n")
    result = runner.invoke(profile_command, [p])
    assert result.exit_code == 0


def test_profile_shows_key_count(tmp_path):
    p = _write(tmp_path, "FOO=bar\nBAZ=qux\n")
    result = runner.invoke(profile_command, [p])
    assert "Keys" in result.output
    assert "2" in result.output


def test_profile_json_output(tmp_path):
    p = _write(tmp_path, "API_SECRET=abc\nHOST=localhost\n")
    result = runner.invoke(profile_command, [p, "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["key_count"] == 2
    assert "API_SECRET" in data["secret_keys"]


def test_profile_json_empty_values(tmp_path):
    p = _write(tmp_path, "FOO=\nBAR=val\n")
    result = runner.invoke(profile_command, [p, "--json"])
    data = json.loads(result.output)
    assert "FOO" in data["empty_value_keys"]


def test_profile_extra_pattern(tmp_path):
    p = _write(tmp_path, "MY_CRED=xyz\n")
    result = runner.invoke(profile_command, [p, "--json", "--extra-pattern", "CRED"])
    data = json.loads(result.output)
    assert "MY_CRED" in data["secret_keys"]


def test_profile_comment_lines_in_json(tmp_path):
    p = _write(tmp_path, "# hi\nFOO=bar\n")
    result = runner.invoke(profile_command, [p, "--json"])
    data = json.loads(result.output)
    assert data["comment_lines"] == 1
