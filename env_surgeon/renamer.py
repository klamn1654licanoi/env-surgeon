"""Rename or alias keys across one or more EnvFile objects."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_surgeon.parser import EnvEntry, EnvFile


@dataclass
class RenameResult:
    """Outcome of a rename operation."""

    entries: List[EnvEntry] = field(default_factory=list)
    renamed: List[tuple[str, str]] = field(default_factory=list)  # (old, new)
    not_found: List[str] = field(default_factory=list)

    def is_clean(self) -> bool:
        """True when every requested key was found and renamed."""
        return len(self.not_found) == 0


def rename_keys(
    env_file: EnvFile,
    mapping: Dict[str, str],
    *,
    ignore_missing: bool = False,
) -> RenameResult:
    """Return a new list of entries with keys renamed according to *mapping*.

    Parameters
    ----------
    env_file:
        Parsed source file.
    mapping:
        ``{old_key: new_key}`` pairs to apply.
    ignore_missing:
        When *False* (default) keys absent from the file are recorded in
        ``RenameResult.not_found``.  When *True* they are silently skipped.

    Returns
    -------
    RenameResult
        Contains the updated entries and bookkeeping lists.
    """
    result = RenameResult()
    found_keys = {e.key for e in env_file.entries if e.key is not None}

    for old_key, new_key in mapping.items():
        if old_key not in found_keys:
            if not ignore_missing:
                result.not_found.append(old_key)
        else:
            result.renamed.append((old_key, new_key))

    rename_map: Dict[str, str] = dict(result.renamed)

    new_entries: List[EnvEntry] = []
    for entry in env_file.entries:
        if entry.key is not None and entry.key in rename_map:
            new_entries.append(
                EnvEntry(
                    key=rename_map[entry.key],
                    value=entry.value,
                    comment=entry.comment,
                    raw=entry.raw,
                )
            )
        else:
            new_entries.append(entry)

    result.entries = new_entries
    return result
