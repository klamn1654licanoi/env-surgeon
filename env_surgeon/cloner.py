"""Clone an env file to a new target, optionally filtering keys by prefix or list."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from env_surgeon.parser import EnvFile, EnvEntry


@dataclass
class CloneResult:
    source: Path
    target: Path
    entries: List[EnvEntry] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)


def is_clean(result: CloneResult) -> bool:
    return len(result.skipped_keys) == 0


def clone_env_file(
    source: EnvFile,
    target: Path,
    *,
    prefix: Optional[str] = None,
    keys: Optional[List[str]] = None,
    overwrite: bool = True,
) -> CloneResult:
    """Copy entries from *source* into *target*, with optional key filtering."""
    kept: List[EnvEntry] = []
    skipped: List[str] = []

    existing_keys: set[str] = set()
    if not overwrite and target.exists():
        from env_surgeon.parser import EnvFile as _EF
        existing = _EF.parse(target)
        existing_keys = {e.key for e in existing.entries if e.key}

    for entry in source.entries:
        if entry.key is None:
            kept.append(entry)
            continue

        if prefix and not entry.key.startswith(prefix):
            skipped.append(entry.key)
            continue

        if keys and entry.key not in keys:
            skipped.append(entry.key)
            continue

        if not overwrite and entry.key in existing_keys:
            skipped.append(entry.key)
            continue

        kept.append(entry)

    return CloneResult(
        source=source.path,
        target=target,
        entries=kept,
        skipped_keys=skipped,
    )
