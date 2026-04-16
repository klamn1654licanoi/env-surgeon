"""Tests for env_surgeon.profiler"""
import pytest
from pathlib import Path
from env_surgeon.parser import EnvFile
from env_surgeon.profiler import profile_env_file, ProfileResult


def _write(tmp_path: Path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def _make_env(entries):
    from env_surgeon.parser import EnvEntry
    ef = EnvFile(path="test.env", entries=[])
    for e in entries:
        ef.entries.append(e)
    return ef


def test_key_count(tmp_path):
    p = _write(tmp_path, "FOO=bar\nBAZ=qux\n")
    env = EnvFile.parse(p)
    result = profile_env_file(env)
    assert result.key_count == 2


def test_secret_keys_detected(tmp_path):
    p = _write(tmp_path, "API_TOKEN=abc\nNAME=hello\n")
    env = EnvFile.parse(p)
    result = profile_env_file(env)
    assert "API_TOKEN" in result.secret_keys
    assert "NAME" not in result.secret_keys


def test_empty_value_detected(tmp_path):
    p = _write(tmp_path, "FOO=\nBAR=val\n")
    env = EnvFile.parse(p)
    result = profile_env_file(env)
    assert "FOO" in result.empty_value_keys
    assert "BAR" not in result.empty_value_keys


def test_comment_lines_counted(tmp_path):
    p = _write(tmp_path, "# comment\nFOO=bar\n")
    env = EnvFile.parse(p)
    result = profile_env_file(env)
    assert result.comment_lines == 1
    assert result.key_count == 1


def test_blank_lines_counted(tmp_path):
    p = _write(tmp_path, "FOO=bar\n\nBAZ=qux\n")
    env = EnvFile.parse(p)
    result = profile_env_file(env)
    assert result.blank_lines >= 1


def test_extra_pattern(tmp_path):
    p = _write(tmp_path, "MY_CUSTOM_CRED=xyz\nNAME=hello\n")
    env = EnvFile.parse(p)
    result = profile_env_file(env, extra_patterns=["CRED"])
    assert "MY_CUSTOM_CRED" in result.secret_keys


def test_secret_count_property(tmp_path):
    p = _write(tmp_path, "PASSWORD=s3cr3t\nHOST=localhost\n")
    env = EnvFile.parse(p)
    result = profile_env_file(env)
    assert result.secret_count == 1
    assert result.empty_count == 0
