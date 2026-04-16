"""Deduplicate keys in an .env file, keeping first or last occurrence."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from env_surgeon.parser import EnvEntry, EnvFile


class KeepStrategy(str, Enum):
    FIRST = "first"
    LAST = "last"


@dataclass
class DeduplicateResult:
    entries: List[EnvEntry]
    removed: List[EnvEntry] = field(default_factory=list)

    def is_clean(self) -> bool:
        """Return True when no duplicates were found."""
        return len(self.removed) == 0


def deduplicate_env_file(
    env_file: EnvFile,
    strategy: KeepStrategy = KeepStrategy.FIRST,
) -> DeduplicateResult:
    """Return a DeduplicateResult with duplicate entries removed.

    Args:
        env_file: Parsed environment file.
        strategy: Which occurrence to keep — FIRST or LAST.

    Returns:
        DeduplicateResult containing the deduplicated entries and
        a list of the entries that were dropped.
    """
    seen: dict[str, int] = {}  # key -> index in `kept`
    kept: list[EnvEntry] = []
    removed: list[EnvEntry] = []

    for entry in env_file.entries:
        if entry.key is None:
            # comment or blank line — always keep
            kept.append(entry)
            continue

        if entry.key not in seen:
            seen[entry.key] = len(kept)
            kept.append(entry)
        else:
            if strategy is KeepStrategy.LAST:
                # Replace the previously kept entry
                old_index = seen[entry.key]
                removed.append(kept[old_index])
                kept[old_index] = entry
                seen[entry.key] = old_index
            else:
                # FIRST — discard the new duplicate
                removed.append(entry)

    return DeduplicateResult(entries=kept, removed=removed)
