"""CLI integration tests for snapshot and snapshot-diff commands."""
from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from env_surgeon.cli_snapshot import snapshot_command, snapshot_diff_command


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


def test_snapshot_exits_0(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "HOST=localhost\nPASSWORD=secret\n")
    snap_dir = tmp_path / "snaps"
    r = CliRunner().invoke(
        snapshot_command,
        [str(env), "--snapshot-dir", str(snap_dir)],
    )
    assert r.exit_code == 0
    assert "Snapshot saved" in r.output
    assert list(snap_dir.glob("*.json")), "snapshot file should exist"


def test_snapshot_no_mask_flag(tmp_path: Path) -> None:
    import json

    env = _write(tmp_path, ".env", "API_TOKEN=raw_value\n")
    snap_dir = tmp_path / "snaps"
    CliRunner().invoke(
        snapshot_command,
        [str(env), "--snapshot-dir", str(snap_dir), "--no-mask"],
    )
    snap_file = next(snap_dir.glob("*.json"))
    data = json.loads(snap_file.read_text())
    assert data["entries"]["API_TOKEN"] == "raw_value"


def test_snapshot_diff_clean_exits_0(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "FOO=bar\n")
    snap_dir = tmp_path / "snaps"
    CliRunner().invoke(
        snapshot_command,
        [str(env), "--snapshot-dir", str(snap_dir), "--no-mask"],
    )
    snap_file = next(snap_dir.glob("*.json"))
    r = CliRunner().invoke(snapshot_diff_command, [str(env), str(snap_file)])
    assert r.exit_code == 0
    assert "No changes" in r.output


def test_snapshot_diff_changed_exits_1(tmp_path: Path) -> None:
    env = _write(tmp_path, ".env", "FOO=old\n")
    snap_dir = tmp_path / "snaps"
    CliRunner().invoke(
        snapshot_command,
        [str(env), "--snapshot-dir", str(snap_dir), "--no-mask"],
    )
    snap_file = next(snap_dir.glob("*.json"))
    env.write_text("FOO=new\n")
    r = CliRunner().invoke(snapshot_diff_command, [str(env), str(snap_file)])
    assert r.exit_code == 1
    assert "FOO" in r.output


def test_snapshot_diff_no_color(tmp_path: Path) -> None:
    import re

    env = _write(tmp_path, ".env", "FOO=old\n")
    snap_dir = tmp_path / "snaps"
    CliRunner().invoke(
        snapshot_command,
        [str(env), "--snapshot-dir", str(snap_dir), "--no-mask"],
    )
    snap_file = next(snap_dir.glob("*.json"))
    env.write_text("FOO=new\n")
    r = CliRunner().invoke(
        snapshot_diff_command, [str(env), str(snap_file), "--no-color"]
    )
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    assert not ansi_escape.search(r.output)
