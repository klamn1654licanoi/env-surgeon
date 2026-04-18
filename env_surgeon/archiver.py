"""Archive an EnvFile to a timestamped backup file."""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from env_surgeon.parser import EnvFile, parse_env_file


@dataclass
class ArchiveResult:
    source: Path
    archive_path: Path
    key_count: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def is_clean(result: ArchiveResult) -> bool:
    return result.archive_path.exists()


def _archive_name(source: Path, ts: datetime) -> str:
    stamp = ts.strftime("%Y%m%dT%H%M%S")
    return f"{source.stem}.{stamp}{source.suffix}"


def archive_env_file(
    source: Path,
    archive_dir: Path | None = None,
    *,
    timestamp: datetime | None = None,
) -> ArchiveResult:
    """Copy *source* to *archive_dir* (default: same directory) with a timestamp suffix."""
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    ts = timestamp or datetime.now(timezone.utc)
    dest_dir = archive_dir or source.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    archive_path = dest_dir / _archive_name(source, ts)
    shutil.copy2(source, archive_path)

    env: EnvFile = parse_env_file(source)
    key_count = sum(1 for e in env.entries if e.key is not None)

    return ArchiveResult(
        source=source,
        archive_path=archive_path,
        key_count=key_count,
        timestamp=ts,
    )
