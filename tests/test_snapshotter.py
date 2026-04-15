"""Tests for env_surgeon.snapshotter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from env_surgeon.snapshotter import (
    Snapshot,
    SnapshotDiff,
    diff_against_snapshot,
    load_snapshot,
    take_snapshot,
)


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_take_snapshot_creates_file(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "DB_HOST=localhost\nDB_PASS=secret\n")
    snap_dir = tmp_path / "snaps"
    snap = take_snapshot(env, snapshot_dir=snap_dir, mask_secrets=True)

    assert snap_dir.exists()
    files = list(snap_dir.glob("*.json"))
    assert len(files) == 1
    assert snap.snapshot_id in files[0].name


def test_snapshot_masks_secrets(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "API_KEY=supersecret\nHOST=example.com\n")
    snap = take_snapshot(env, snapshot_dir=tmp_path / "snaps", mask_secrets=True)

    assert snap.entries["API_KEY"] == "***"
    assert snap.entries["HOST"] == "example.com"


def test_snapshot_no_mask_stores_raw(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "API_KEY=supersecret\n")
    snap = take_snapshot(env, snapshot_dir=tmp_path / "snaps", mask_secrets=False)

    assert snap.entries["API_KEY"] == "supersecret"


def test_load_snapshot_roundtrip(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    snap_dir = tmp_path / "snaps"
    original = take_snapshot(env, snapshot_dir=snap_dir, mask_secrets=False)

    snap_file = next(snap_dir.glob("*.json"))
    loaded = load_snapshot(snap_file)

    assert loaded.snapshot_id == original.snapshot_id
    assert loaded.entries == original.entries
    assert loaded.source_path == original.source_path


def test_diff_against_snapshot_clean(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "FOO=bar\n")
    snap = take_snapshot(env, snapshot_dir=tmp_path / "snaps", mask_secrets=False)
    result = diff_against_snapshot(env, snap)
    assert result.is_clean


def test_diff_detects_added_key(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "FOO=bar\n")
    snap = take_snapshot(env, snapshot_dir=tmp_path / "snaps", mask_secrets=False)
    env.write_text("FOO=bar\nNEW_KEY=value\n")
    result = diff_against_snapshot(env, snap)
    assert "NEW_KEY" in result.added
    assert not result.removed
    assert not result.changed


def test_diff_detects_removed_key(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "FOO=bar\nOLD=gone\n")
    snap = take_snapshot(env, snapshot_dir=tmp_path / "snaps", mask_secrets=False)
    env.write_text("FOO=bar\n")
    result = diff_against_snapshot(env, snap)
    assert "OLD" in result.removed


def test_diff_detects_changed_value(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "FOO=old\n")
    snap = take_snapshot(env, snapshot_dir=tmp_path / "snaps", mask_secrets=False)
    env.write_text("FOO=new\n")
    result = diff_against_snapshot(env, snap)
    assert "FOO" in result.changed
    assert not result.is_clean
