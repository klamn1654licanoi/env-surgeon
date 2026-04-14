"""Merge multiple .env files with configurable conflict resolution strategies."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from env_surgeon.parser import EnvEntry, EnvFile


class ConflictStrategy(Enum):
    """Strategy to use when a key exists in multiple sources."""
    FIRST = "first"    # Keep value from the first file that defines it
    LAST = "last"      # Keep value from the last file that defines it
    ERROR = "error"    # Raise an error on conflict


@dataclass
class MergeConflict:
    key: str
    values: Dict[str, str]  # source_label -> value


@dataclass
class MergeResult:
    entries: List[EnvEntry] = field(default_factory=list)
    conflicts: List[MergeConflict] = field(default_factory=list)
    source_labels: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries if not e.is_comment and e.key}


class MergeConflictError(Exception):
    """Raised when ConflictStrategy.ERROR is used and a conflict is detected."""


def merge_env_files(
    files: List[EnvFile],
    labels: Optional[List[str]] = None,
    strategy: ConflictStrategy = ConflictStrategy.LAST,
) -> MergeResult:
    """Merge a list of EnvFile objects into a single MergeResult."""
    if labels is None:
        labels = [f.path or f"file_{i}" for i, f in enumerate(files)]

    if len(labels) != len(files):
        raise ValueError("Length of labels must match length of files.")

    seen: Dict[str, tuple] = {}  # key -> (value, label)
    conflicts: List[MergeConflict] = []
    merged_entries: List[EnvEntry] = []
    conflict_keys: Dict[str, MergeConflict] = {}

    for env_file, label in zip(files, labels):
        for entry in env_file.entries:
            if entry.is_comment or not entry.key:
                continue

            if entry.key in seen:
                existing_value, existing_label = seen[entry.key]
                if existing_value != entry.value:
                    if strategy == ConflictStrategy.ERROR:
                        raise MergeConflictError(
                            f"Conflict on key '{entry.key}': "
                            f"'{existing_label}'={existing_value!r} vs "
                            f"'{label}'={entry.value!r}"
                        )
                    if entry.key not in conflict_keys:
                        mc = MergeConflict(
                            key=entry.key,
                            values={existing_label: existing_value},
                        )
                        conflict_keys[entry.key] = mc
                        conflicts.append(mc)
                    conflict_keys[entry.key].values[label] = entry.value

                    if strategy == ConflictStrategy.LAST:
                        seen[entry.key] = (entry.value, label)
                # FIRST: do nothing, keep existing
            else:
                seen[entry.key] = (entry.value, label)

    for key, (value, _) in seen.items():
        merged_entries.append(EnvEntry(key=key, value=value))

    return MergeResult(
        entries=merged_entries,
        conflicts=conflicts,
        source_labels=labels,
    )
