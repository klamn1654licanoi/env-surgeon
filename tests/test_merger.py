"""Tests for env_surgeon.merger."""

import pytest
from pathlib import Path

from env_surgeon.parser import parse_env_file
from env_surgeon.merger import (
    ConflictStrategy,
    MergeConflictError,
    merge_env_files,
)


def _make_env(tmp_path: Path, name: str, content: str):
    p = tmp_path / name
    p.write_text(content)
    return parse_env_file(str(p))


def test_merge_no_overlap(tmp_path):
    a = _make_env(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _make_env(tmp_path, "b.env", "BAZ=3\n")
    result = merge_env_files([a, b])
    d = result.as_dict()
    assert d == {"FOO": "1", "BAR": "2", "BAZ": "3"}
    assert result.conflicts == []


def test_merge_conflict_last_wins(tmp_path):
    a = _make_env(tmp_path, "a.env", "KEY=alpha\n")
    b = _make_env(tmp_path, "b.env", "KEY=beta\n")
    result = merge_env_files([a, b], strategy=ConflictStrategy.LAST)
    assert result.as_dict()["KEY"] == "beta"
    assert len(result.conflicts) == 1
    assert result.conflicts[0].key == "KEY"


def test_merge_conflict_first_wins(tmp_path):
    a = _make_env(tmp_path, "a.env", "KEY=alpha\n")
    b = _make_env(tmp_path, "b.env", "KEY=beta\n")
    result = merge_env_files([a, b], strategy=ConflictStrategy.FIRST)
    assert result.as_dict()["KEY"] == "alpha"
    assert len(result.conflicts) == 1


def test_merge_conflict_error_strategy(tmp_path):
    a = _make_env(tmp_path, "a.env", "KEY=alpha\n")
    b = _make_env(tmp_path, "b.env", "KEY=beta\n")
    with pytest.raises(MergeConflictError, match="KEY"):
        merge_env_files([a, b], strategy=ConflictStrategy.ERROR)


def test_merge_same_value_no_conflict(tmp_path):
    a = _make_env(tmp_path, "a.env", "KEY=same\n")
    b = _make_env(tmp_path, "b.env", "KEY=same\n")
    result = merge_env_files([a, b])
    assert result.conflicts == []
    assert result.as_dict()["KEY"] == "same"


def test_merge_labels_mismatch_raises(tmp_path):
    a = _make_env(tmp_path, "a.env", "X=1\n")
    with pytest.raises(ValueError):
        merge_env_files([a], labels=["l1", "l2"])


def test_merge_three_files(tmp_path):
    a = _make_env(tmp_path, "a.env", "A=1\nSHARED=first\n")
    b = _make_env(tmp_path, "b.env", "B=2\nSHARED=second\n")
    c = _make_env(tmp_path, "c.env", "C=3\nSHARED=third\n")
    result = merge_env_files([a, b, c], strategy=ConflictStrategy.LAST)
    d = result.as_dict()
    assert d["A"] == "1"
    assert d["B"] == "2"
    assert d["C"] == "3"
    assert d["SHARED"] == "third"
    assert len(result.conflicts) == 1
    assert set(result.conflicts[0].values.values()) == {"first", "second", "third"}
