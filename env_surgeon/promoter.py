"""Promote keys from one environment to another, with optional overwrite control."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from env_surgeon.parser import EnvFile, EnvEntry


@dataclass
class PromoteResult:
    entries: List[EnvEntry]
    promoted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)


def is_clean(result: PromoteResult) -> bool:
    return len(result.skipped) == 0


def promote_env_file(
    source: EnvFile,
    target: EnvFile,
    keys: List[str] | None = None,
    overwrite: bool = True,
) -> PromoteResult:
    """Promote keys from source into target.

    Args:
        source: The environment to pull values from.
        target: The environment to promote values into.
        keys: Specific keys to promote; if None, promote all source keys.
        overwrite: Whether to overwrite existing keys in target.
    """
    source_dict: Dict[str, EnvEntry] = {}
    for e in source.entries:
        if e.key is not None:
            source_dict[e.key] = e

    target_dict: Dict[str, EnvEntry] = {}
    for e in target.entries:
        if e.key is not None:
            target_dict[e.key] = e

    promote_keys = keys if keys is not None else list(source_dict.keys())

    result_entries = list(target.entries)
    promoted: List[str] = []
    skipped: List[str] = []
    overwritten: List[str] = []

    for key in promote_keys:
        if key not in source_dict:
            skipped.append(key)
            continue
        if key in target_dict:
            if not overwrite:
                skipped.append(key)
                continue
            # Replace in-place
            result_entries = [
                source_dict[key] if (e.key == key) else e
                for e in result_entries
            ]
            overwritten.append(key)
        else:
            result_entries.append(source_dict[key])
            promoted.append(key)

    return PromoteResult(
        entries=result_entries,
        promoted=promoted,
        skipped=skipped,
        overwritten=overwritten,
    )
