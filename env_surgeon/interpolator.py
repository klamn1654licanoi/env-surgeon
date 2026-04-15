"""Variable interpolation for .env files.

Supports ${VAR} and $VAR syntax, resolving references within the same file
or against an optional base dictionary of values.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_surgeon.parser import EnvFile

_INTERPOLATION_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved_keys: List[str] = field(default_factory=list)
    cycles: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.unresolved_keys and not self.cycles


def _resolve_value(
    key: str,
    raw: str,
    env_dict: Dict[str, str],
    base: Dict[str, str],
    visiting: set,
) -> Optional[str]:
    """Recursively resolve a single value, detecting cycles."""
    if key in visiting:
        return None  # cycle detected
    visiting = visiting | {key}

    def _replace(match: re.Match) -> str:
        ref = match.group(1) or match.group(2)
        if ref in visiting:
            return match.group(0)  # leave unresolved to signal cycle
        if ref in env_dict:
            resolved = _resolve_value(ref, env_dict[ref], env_dict, base, visiting)
            return resolved if resolved is not None else match.group(0)
        if ref in base:
            return base[ref]
        return match.group(0)

    return _INTERPOLATION_RE.sub(_replace, raw)


def interpolate_env_file(
    env_file: EnvFile,
    base: Optional[Dict[str, str]] = None,
) -> InterpolationResult:
    """Resolve variable references in *env_file*.

    Args:
        env_file: Parsed .env file whose values may contain ``${VAR}`` refs.
        base: Optional external mapping (e.g. OS environment) used as fallback.

    Returns:
        :class:`InterpolationResult` with fully resolved values and diagnostics.
    """
    base = base or {}
    raw_dict: Dict[str, str] = {}
    for entry in env_file.entries:
        if entry.key is not None:
            raw_dict[entry.key] = entry.value or ""

    result = InterpolationResult()
    for key, raw in raw_dict.items():
        resolved = _resolve_value(key, raw, raw_dict, base, set())
        if resolved is None:
            result.cycles.append(key)
            result.resolved[key] = raw
        elif _INTERPOLATION_RE.search(resolved):
            result.unresolved_keys.append(key)
            result.resolved[key] = resolved
        else:
            result.resolved[key] = resolved

    return result
