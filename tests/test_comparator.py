"""Tests for env_surgeon.comparator."""
import pytest
from pathlib import Path
from env_surgeon.comparator import compare_env_files, format_matrix


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_all_keys_present_in_both(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\nBAZ=qux\n")
    b = _write(tmp_path, "b.env", "FOO=bar\nBAZ=qux\n")
    cm = compare_env_files([a, b])
    assert set(cm.all_keys()) == {"FOO", "BAZ"}


def test_missing_key_detected(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\nONLY_A=1\n")
    b = _write(tmp_path, "b.env", "FOO=bar\n")
    cm = compare_env_files([a, b])
    assert b in cm.missing_in("ONLY_A")
    assert a not in cm.missing_in("ONLY_A")


def test_consistent_same_value(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=same\n")
    b = _write(tmp_path, "b.env", "FOO=same\n")
    cm = compare_env_files([a, b])
    assert cm.is_consistent("FOO")


def test_inconsistent_different_values(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=one\n")
    b = _write(tmp_path, "b.env", "FOO=two\n")
    cm = compare_env_files([a, b])
    assert not cm.is_consistent("FOO")
    assert "FOO" in cm.inconsistent_keys()


def test_missing_keys_list(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=1\n")
    cm = compare_env_files([a, b])
    assert "BAR" in cm.missing_keys()
    assert "FOO" not in cm.missing_keys()


def test_format_matrix_contains_keys(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=hello\n")
    b = _write(tmp_path, "b.env", "FOO=world\n")
    cm = compare_env_files([a, b])
    out = format_matrix(cm)
    assert "FOO" in out
    assert "hello" in out
    assert "world" in out


def test_format_matrix_masks_secrets(tmp_path):
    a = _write(tmp_path, "a.env", "API_SECRET=supersecret\n")
    b = _write(tmp_path, "b.env", "API_SECRET=anothersecret\n")
    cm = compare_env_files([a, b])
    out = format_matrix(cm, mask_secrets=True)
    assert "supersecret" not in out
    assert "***" in out


def test_three_files(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "X=1\nY=2\n")
    c = _write(tmp_path, "c.env", "X=1\nY=2\nZ=3\n")
    cm = compare_env_files([a, b, c])
    assert set(cm.all_keys()) == {"X", "Y", "Z"}
    assert a in cm.missing_in("Y")
    assert a in cm.missing_in("Z")
    assert b in cm.missing_in("Z")
