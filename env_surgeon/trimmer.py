"""Trim leading/trailing whitespace from .env values and keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from env_surgeon.parser import EnvEntry, EnvFile


@dataclass
class TrimResult:
    entries: List[EnvEntry] = field(default_factory=list)
    trimmed_keys: List[str] = field(default_factory=list)
    trimmed_values: List[str] = field(default_factory=list)


def is_clean(result: TrimResult) -> bool:
    """Return True when no keys or values required trimming."""
    return not result.trimmed_keys and not result.trimmed_values


def trim_env_file(env_file: EnvFile) -> TrimResult:
    """Return a TrimResult with all key/value whitespace stripped.

    Comment-only and blank entries are passed through unchanged.
    """
    result = TrimResult()

    for entry in env_file.entries:
        if entry.key is None:
            # comment or blank line — pass through
            result.entries.append(entry)
            continue

        raw_key = entry.key
        raw_value = entry.value if entry.value is not None else ""

        trimmed_key = raw_key.strip()
        trimmed_value = raw_value.strip()

        if trimmed_key != raw_key:
            result.trimmed_keys.append(trimmed_key)

        if trimmed_value != raw_value:
            result.trimmed_values.append(trimmed_key)

        new_entry = EnvEntry(
            key=trimmed_key,
            value=trimmed_value,
            comment=entry.comment,
            raw=entry.raw,
        )
        result.entries.append(new_entry)

    return result
