"""Tests for env_surgeon.interpolator."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from env_surgeon.parser import EnvFile
from env_surgeon.interpolator import interpolate_env_file, InterpolationResult


def _make_env(tmp_path: Path, content: str) -> EnvFile:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent(content))
    return EnvFile.parse(p)


def test_no_interpolation_passthrough(tmp_path):
    env = _make_env(tmp_path, """
        HOST=localhost
        PORT=5432
    """)
    result = interpolate_env_file(env)
    assert result.resolved["HOST"] == "localhost"
    assert result.resolved["PORT"] == "5432"
    assert result.is_clean


def test_simple_brace_interpolation(tmp_path):
    env = _make_env(tmp_path, """
        BASE=postgres
        URL=${BASE}://localhost
    """)
    result = interpolate_env_file(env)
    assert result.resolved["URL"] == "postgres://localhost"
    assert result.is_clean


def test_bare_dollar_interpolation(tmp_path):
    env = _make_env(tmp_path, """
        PROTO=https
        ENDPOINT=$PROTO/api
    """)
    result = interpolate_env_file(env)
    assert result.resolved["ENDPOINT"] == "https/api"
    assert result.is_clean


def test_unresolved_reference_reported(tmp_path):
    env = _make_env(tmp_path, """
        URL=${MISSING_VAR}/path
    """)
    result = interpolate_env_file(env)
    assert "URL" in result.unresolved_keys
    assert not result.is_clean


def test_base_dict_resolves_external_ref(tmp_path):
    env = _make_env(tmp_path, """
        FULL_URL=${EXTERNAL_HOST}/api
    """)
    result = interpolate_env_file(env, base={"EXTERNAL_HOST": "example.com"})
    assert result.resolved["FULL_URL"] == "example.com/api"
    assert result.is_clean


def test_chained_interpolation(tmp_path):
    env = _make_env(tmp_path, """
        A=hello
        B=${A}_world
        C=${B}!
    """)
    result = interpolate_env_file(env)
    assert result.resolved["C"] == "hello_world!"
    assert result.is_clean


def test_is_clean_false_on_unresolved(tmp_path):
    env = _make_env(tmp_path, """
        X=${NOPE}
    """)
    result = interpolate_env_file(env)
    assert not result.is_clean


def test_empty_file_gives_empty_result(tmp_path):
    env = _make_env(tmp_path, "")
    result = interpolate_env_file(env)
    assert result.resolved == {}
    assert result.is_clean
