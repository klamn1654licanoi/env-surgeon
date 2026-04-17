"""Key rotation: replace values for specified keys with new generated or provided secrets."""
from __future__ import annotations

import secrets
import string
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_surgeon.parser import EnvFile, EnvEntry

_ALPHABET = string.ascii_letters + string.digits


def _generate_secret(length: int = 32) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


@dataclass
class RotateResult:
    entries: List[EnvEntry]
    rotated: List[str] = field(default_factory=list)
    not_found: List[str] = field(default_factory=list)


def is_clean(result: RotateResult) -> bool:
    return len(result.not_found) == 0


def rotate_env_file(
    env: EnvFile,
    keys: List[str],
    replacements: Optional[Dict[str, str]] = None,
    length: int = 32,
) -> RotateResult:
    """Rotate values for *keys* in *env*.

    If *replacements* supplies a value for a key it is used verbatim;
    otherwise a random secret of *length* characters is generated.
    """
    replacements = replacements or {}
    key_set = set(keys)
    rotated: List[str] = []
    not_found: List[str] = list(keys)
    new_entries: List[EnvEntry] = []

    for entry in env.entries:
        if entry.key and entry.key in key_set:
            new_value = replacements.get(entry.key, _generate_secret(length))
            new_entries.append(
                EnvEntry(
                    key=entry.key,
                    value=new_value,
                    comment=entry.comment,
                    raw=f"{entry.key}={new_value}",
                )
            )
            rotated.append(entry.key)
            if entry.key in not_found:
                not_found.remove(entry.key)
        else:
            new_entries.append(entry)

    return RotateResult(entries=new_entries, rotated=rotated, not_found=not_found)
