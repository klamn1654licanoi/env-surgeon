"""Tests for env_surgeon.parser."""

from pathlib import Path

import pytest

from env_surgeon.parser import EnvEntry, EnvFile, parse_env_file, _strip_quotes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_env(tmp_path: Path, content: str) -> Path:
    env_file = tmp_path / ".env"
    env_file.write_text(content, encoding="utf-8")
    return env_file


# ---------------------------------------------------------------------------
# Unit tests for _strip_quotes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ('"hello"', 'hello'),
    ("'world'", 'world'),
    ('no_quotes', 'no_quotes'),
    ('"single', '"single'),
    ('""', ''),
])
def test_strip_quotes(raw, expected):
    assert _strip_quotes(raw) == expected


# ---------------------------------------------------------------------------
# Integration tests for parse_env_file
# ---------------------------------------------------------------------------

def test_parse_simple_pairs(tmp_path):
    path = _write_env(tmp_path, "FOO=bar\nBAZ=qux\n")
    result = parse_env_file(path)
    assert isinstance(result, EnvFile)
    assert len(result.entries) == 2
    assert result.entries[0] == EnvEntry(key="FOO", value="bar", comment=None, line_number=1)
    assert result.entries[1].key == "BAZ"


def test_parse_quoted_values(tmp_path):
    path = _write_env(tmp_path, 'SECRET="my secret value"\nTOKEN=\'abc123\'\n')
    result = parse_env_file(path)
    assert result.entries[0].value == "my secret value"
    assert result.entries[1].value == "abc123"


def test_parse_preceding_comment(tmp_path):
    path = _write_env(tmp_path, "# database url\nDB_URL=postgres://localhost/db\n")
    result = parse_env_file(path)
    assert result.entries[0].comment == "database url"


def test_blank_line_resets_comment(tmp_path):
    path = _write_env(tmp_path, "# orphan comment\n\nFOO=bar\n")
    result = parse_env_file(path)
    assert result.entries[0].comment is None


def test_inline_comment(tmp_path):
    path = _write_env(tmp_path, "PORT=8080 # default port\n")
    result = parse_env_file(path)
    assert result.entries[0].value == "8080"
    assert result.entries[0].comment == "default port"


def test_as_dict(tmp_path):
    path = _write_env(tmp_path, "A=1\nB=2\nA=3\n")
    result = parse_env_file(path)
    d = result.as_dict()
    assert d == {"A": "3", "B": "2"}  # last value wins


def test_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "nonexistent.env")


def test_skips_comment_only_lines(tmp_path):
    path = _write_env(tmp_path, "# just a comment\n# another comment\n")
    result = parse_env_file(path)
    assert result.entries == []


def test_line_numbers_are_correct(tmp_path):
    """Verify that line_number reflects the actual line in the file."""
    path = _write_env(tmp_path, "# comment\nFIRST=1\n\nSECOND=2\n")
    result = parse_env_file(path)
    assert result.entries[0].line_number == 2
    assert result.entries[1].line_number == 4
