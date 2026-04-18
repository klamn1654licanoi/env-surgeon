"""Freeze an env file by pinning all interpolated values in-place."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.interpolator import interpolate_env_file


@dataclass
class FreezeResult:
    entries: List[EnvEntry]
    frozen_keys: List[str] = field(default_factory=list)
    unresolved_keys: List[str] = field(default_factory=list)


def is_clean(result: FreezeResult) -> bool:
    """True when every key was successfully resolved and frozen."""
    return len(result.unresolved_keys) == 0


def freeze_env_file(env: EnvFile) -> FreezeResult:
    """Return a new EnvFile whose interpolation references are replaced
    with their resolved literal values.

    Keys that cannot be resolved are left unchanged and recorded in
    *unresolved_keys*.
    """
    interp = interpolate_env_file(env)

    resolved_map = {e.key: e.value for e in interp.entries if e.key}
    unresolved = list(interp.unresolved_keys)

    frozen_entries: List[EnvEntry] = []
    frozen_keys: List[str] = []

    for entry in env.entries:
        if entry.key is None:
            # comment / blank line — pass through
            frozen_entries.append(entry)
            continue

        original_value = entry.value or ""
        resolved_value = resolved_map.get(entry.key, original_value)

        if entry.key in unresolved:
            frozen_entries.append(entry)
        elif resolved_value != original_value:
            frozen_entries.append(
                EnvEntry(
                    key=entry.key,
                    value=resolved_value,
                    comment=entry.comment,
                    raw_line=None,
                )
            )
            frozen_keys.append(entry.key)
        else:
            frozen_entries.append(entry)

    return FreezeResult(
        entries=frozen_entries,
        frozen_keys=frozen_keys,
        unresolved_keys=unresolved,
    )
