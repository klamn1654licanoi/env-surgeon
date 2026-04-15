"""Snapshot and restore .env files — save a timestamped copy and compare against it."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from env_surgeon.parser import EnvFile, parse
from env_surgeon.masker import mask_env_file

DEFAULT_SNAPSHOT_DIR = Path(".env_snapshots")


@dataclass
class Snapshot:
    source_path: str
    taken_at: str  # ISO-8601
    entries: Dict[str, Optional[str]]  # key -> raw value (secrets already masked)
    snapshot_id: str = ""

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "source_path": self.source_path,
            "taken_at": self.taken_at,
            "entries": self.entries,
        }

    @staticmethod
    def from_dict(data: dict) -> "Snapshot":
        return Snapshot(
            source_path=data["source_path"],
            taken_at=data["taken_at"],
            entries=data["entries"],
            snapshot_id=data.get("snapshot_id", ""),
        )


@dataclass
class SnapshotDiff:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not (self.added or self.removed or self.changed)


def take_snapshot(
    env_path: Path,
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
    mask_secrets: bool = True,
) -> Snapshot:
    """Parse *env_path*, optionally mask secrets, and persist a JSON snapshot."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    env_file: EnvFile = parse(env_path)

    if mask_secrets:
        mask_result = mask_env_file(env_file)
        entries = {k: v for k, v in mask_result.as_dict().items()}
    else:
        entries = {e.key: e.value for e in env_file.entries if e.key}

    now = datetime.now(timezone.utc)
    snapshot_id = f"{env_path.stem}_{now.strftime('%Y%m%dT%H%M%SZ')}"
    snap = Snapshot(
        source_path=str(env_path),
        taken_at=now.isoformat(),
        entries=entries,
        snapshot_id=snapshot_id,
    )

    out_file = snapshot_dir / f"{snapshot_id}.json"
    out_file.write_text(json.dumps(snap.to_dict(), indent=2))
    return snap


def load_snapshot(snapshot_file: Path) -> Snapshot:
    data = json.loads(snapshot_file.read_text())
    return Snapshot.from_dict(data)


def diff_against_snapshot(env_path: Path, snapshot: Snapshot) -> SnapshotDiff:
    """Compare the current state of *env_path* against a previously saved snapshot."""
    env_file: EnvFile = parse(env_path)
    current: Dict[str, Optional[str]] = {e.key: e.value for e in env_file.entries if e.key}
    old = snapshot.entries

    result = SnapshotDiff()
    for key in set(current) - set(old):
        result.added.append(key)
    for key in set(old) - set(current):
        result.removed.append(key)
    for key in set(current) & set(old):
        if current[key] != old[key]:
            result.changed.append(key)
    return result
