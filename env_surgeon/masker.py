"""Masking utilities to redact secret values before display or export."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from env_surgeon.parser import EnvEntry, EnvFile

# Keys whose values should always be masked
DEFAULT_SECRET_PATTERNS: list[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE_KEY.*",
    r".*CREDENTIALS.*",
]

MASK_PLACEHOLDER = "***"


@dataclass
class MaskResult:
    """Holds the masked copy of an EnvFile and metadata about what was masked."""

    entries: list[EnvEntry]
    masked_keys: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, str | None]:
        return {
            e.key: e.value
            for e in self.entries
            if e.key is not None
        }


def _compile_patterns(patterns: Iterable[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def is_secret_key(
    key: str,
    compiled: list[re.Pattern[str]],
) -> bool:
    """Return True if *key* matches any secret pattern."""
    return any(p.fullmatch(key) for p in compiled)


def mask_env_file(
    env_file: EnvFile,
    extra_patterns: Iterable[str] | None = None,
    placeholder: str = MASK_PLACEHOLDER,
) -> MaskResult:
    """Return a MaskResult with secret values replaced by *placeholder*."""
    patterns = list(DEFAULT_SECRET_PATTERNS)
    if extra_patterns:
        patterns.extend(extra_patterns)
    compiled = _compile_patterns(patterns)

    masked_entries: list[EnvEntry] = []
    masked_keys: list[str] = []

    for entry in env_file.entries:
        if entry.key is not None and is_secret_key(entry.key, compiled):
            masked_entries.append(
                EnvEntry(
                    key=entry.key,
                    value=placeholder,
                    comment=entry.comment,
                    raw=entry.raw,
                )
            )
            masked_keys.append(entry.key)
        else:
            masked_entries.append(entry)

    return MaskResult(entries=masked_entries, masked_keys=masked_keys)
