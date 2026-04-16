"""Patch specific keys in an .env file (set, unset, or update)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_surgeon.parser import EnvEntry, EnvFile


@dataclass
class PatchResult:
    entries: List[EnvEntry]
    set_keys: List[str] = field(default_factory=list)
    updated_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)

    def is_clean(self) -> bool:
        return not (self.set_keys or self.updated_keys or self.removed_keys)


def patch_env_file(
    env_file: EnvFile,
    set_pairs: Optional[Dict[str, str]] = None,
    remove_keys: Optional[List[str]] = None,
    no_overwrite: bool = False,
) -> PatchResult:
    """Apply a patch to an EnvFile.

    Args:
        env_file: Parsed source file.
        set_pairs: Keys to add or update.
        remove_keys: Keys to remove entirely.
        no_overwrite: When True, existing keys are not overwritten.
    """
    set_pairs = set_pairs or {}
    remove_keys_set = set(remove_keys or [])

    result_entries: List[EnvEntry] = []
    seen: set[str] = set()
    set_keys: List[str] = []
    updated_keys: List[str] = []
    removed_keys: List[str] = []
    skipped_keys: List[str] = []

    for entry in env_file.entries:
        if entry.key is None:
            result_entries.append(entry)
            continue

        if entry.key in remove_keys_set:
            removed_keys.append(entry.key)
            seen.add(entry.key)
            continue

        if entry.key in set_pairs:
            if no_overwrite:
                skipped_keys.append(entry.key)
                result_entries.append(entry)
            else:
                updated_keys.append(entry.key)
                result_entries.append(
                    EnvEntry(
                        key=entry.key,
                        value=set_pairs[entry.key],
                        comment=entry.comment,
                        raw_line=None,
                    )
                )
            seen.add(entry.key)
        else:
            result_entries.append(entry)

    for key, value in set_pairs.items():
        if key not in seen:
            result_entries.append(EnvEntry(key=key, value=value, comment=None, raw_line=None))
            set_keys.append(key)

    for key in remove_keys_set:
        if key not in seen:
            skipped_keys.append(key)

    return PatchResult(
        entries=result_entries,
        set_keys=set_keys,
        updated_keys=updated_keys,
        removed_keys=removed_keys,
        skipped_keys=skipped_keys,
    )
