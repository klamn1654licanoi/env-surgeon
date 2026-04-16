"""Redactor: permanently remove keys from an .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set

from env_surgeon.parser import EnvFile, EnvEntry


@dataclass
class RedactResult:
    entries: List[EnvEntry] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)
    not_found_keys: List[str] = field(default_factory=list)


def is_clean(result: RedactResult) -> bool:
    """Return True when every requested key was found and removed."""
    return len(result.not_found_keys) == 0


def redact_keys(
    env_file: EnvFile,
    keys: List[str],
    *,
    ignore_missing: bool = False,
) -> RedactResult:
    """Remove *keys* from *env_file*.

    Parameters
    ----------
    env_file:
        Parsed environment file to operate on.
    keys:
        Key names to remove (case-sensitive).
    ignore_missing:
        When *False* (default) keys that do not exist in the file are
        recorded in ``RedactResult.not_found_keys``.  When *True* they
        are silently skipped.

    Returns
    -------
    RedactResult
        Contains the surviving entries plus bookkeeping lists.
    """
    target: Set[str] = set(keys)
    found: Set[str] = set()
    surviving: List[EnvEntry] = []

    for entry in env_file.entries:
        if entry.key is not None and entry.key in target:
            found.add(entry.key)
            # Drop the entry — do not append to surviving
        else:
            surviving.append(entry)

    not_found: List[str] = [
        k for k in keys if k not in found
    ] if not ignore_missing else []

    return RedactResult(
        entries=surviving,
        removed_keys=sorted(found),
        not_found_keys=not_found,
    )
