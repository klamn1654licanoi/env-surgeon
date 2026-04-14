"""Tests for env_surgeon.formatter."""

from pathlib import Path

from env_surgeon.parser import EnvEntry, parse_env_file
from env_surgeon.merger import merge_env_files, ConflictStrategy
from env_surgeon.formatter import (
    format_entries,
    format_entry,
    format_merge_result,
    write_env_file,
)


def test_format_simple_entry():
    e = EnvEntry(key="FOO", value="bar")
    assert format_entry(e) == "FOO=bar"


def test_format_entry_with_spaces_quotes_value():
    e = EnvEntry(key="MSG", value="hello world")
    assert format_entry(e) == 'MSG="hello world"'


def test_format_entry_force_quote():
    e = EnvEntry(key="X", value="plain")
    assert format_entry(e, quote_values=True) == 'X="plain"'


def test_format_entry_comment_passthrough():
    e = EnvEntry(key="", value="", is_comment=True, raw_line="# hello")
    assert format_entry(e) == "# hello"


def test_format_entries_roundtrip(tmp_path):
    p = tmp_path / "sample.env"
    p.write_text("A=1\nB=2\nC=3\n")
    env = parse_env_file(str(p))
    output = format_entries(env.entries)
    assert "A=1" in output
    assert "B=2" in output
    assert "C=3" in output


def test_format_merge_result_no_conflicts(tmp_path):
    a_path = tmp_path / "a.env"
    b_path = tmp_path / "b.env"
    a_path.write_text("FOO=1\n")
    b_path.write_text("BAR=2\n")
    a = parse_env_file(str(a_path))
    b = parse_env_file(str(b_path))
    result = merge_env_files([a, b])
    text = format_merge_result(result)
    assert "FOO=1" in text
    assert "BAR=2" in text
    assert "CONFLICT" not in text


def test_format_merge_result_with_conflict_comments(tmp_path):
    a_path = tmp_path / "a.env"
    b_path = tmp_path / "b.env"
    a_path.write_text("KEY=alpha\n")
    b_path.write_text("KEY=beta\n")
    a = parse_env_file(str(a_path))
    b = parse_env_file(str(b_path))
    result = merge_env_files([a, b], strategy=ConflictStrategy.LAST)
    text = format_merge_result(result, include_conflict_comments=True)
    assert "# CONFLICT" in text
    assert "KEY=beta" in text


def test_write_env_file(tmp_path):
    entries = [EnvEntry(key="X", value="42"), EnvEntry(key="Y", value="hello world")]
    out = tmp_path / "out.env"
    write_env_file(entries, str(out))
    content = out.read_text()
    assert "X=42" in content
    assert 'Y="hello world"' in content
