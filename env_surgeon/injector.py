"""Inject key=value pairs into an existing EnvFile, optionally overwriting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_surgeon.parser import EnvEntry, EnvFile


@dataclass
class InjectResult:
    entries: List[EnvEntry]
    injected: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def is_clean(result: InjectResult) -> bool:
    """True when nothing was skipped (all requested keys were applied)."""
    return len(result.skipped) == 0


def inject_env_file(
    env: EnvFile,
    pairs: Dict[str, str],
    *,
    overwrite: bool = True,
    comment: Optional[str] = None,
) -> InjectResult:
    """Return a new entry list with *pairs* injected.

    Args:
        env: Parsed source file.
        pairs: Mapping of key -> value to inject.
        overwrite: If False, existing keys are skipped instead of updated.
        comment: Optional inline comment appended to each injected entry.
    """
    existing: Dict[str, int] = {}
    entries: List[EnvEntry] = list(env.entries)

    for idx, entry in enumerate(entries):
        if entry.key is not None:
            existing[entry.key] = idx

    injected: List[str] = []
    overwritten: List[str] = []
    skipped: List[str] = []

    for key, value in pairs.items():
        if key in existing:
            if overwrite:
                old = entries[existing[key]]
                entries[existing[key]] = EnvEntry(
                    key=key,
                    value=value,
                    comment=comment if comment is not None else old.comment,
                    raw=f"{key}={value}",
                )
                overwritten.append(key)
            else:
                skipped.append(key)
        else:
            entries.append(
                EnvEntry(
                    key=key,
                    value=value,
                    comment=comment,
                    raw=f"{key}={value}",
                )
            )
            injected.append(key)

    return InjectResult(
        entries=entries,
        injected=injected,
        overwritten=overwritten,
        skipped=skipped,
    )
