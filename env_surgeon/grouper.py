"""Group .env entries by prefix (e.g. DB_, AWS_, APP_)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from env_surgeon.parser import EnvFile, EnvEntry


@dataclass
class GroupResult:
    groups: Dict[str, List[EnvEntry]] = field(default_factory=dict)
    ungrouped: List[EnvEntry] = field(default_factory=list)

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def is_clean(self) -> bool:
        """True when every entry belongs to a named group."""
        return len(self.ungrouped) == 0


def _prefix(key: str, sep: str = "_") -> Optional[str]:
    idx = key.find(sep)
    if idx <= 0:
        return None
    return key[:idx].upper()


def group_env_file(
    env: EnvFile,
    prefixes: Optional[List[str]] = None,
    sep: str = "_",
) -> GroupResult:
    """Group entries by key prefix.

    If *prefixes* is given only those prefixes are recognised;
    otherwise every distinct prefix is used.
    """
    result = GroupResult()
    for entry in env.entries:
        if entry.key is None:
            # comment / blank line — attach to ungrouped
            result.ungrouped.append(entry)
            continue
        p = _prefix(entry.key, sep)
        if p is None:
            result.ungrouped.append(entry)
            continue
        if prefixes is not None and p not in [x.upper() for x in prefixes]:
            result.ungrouped.append(entry)
            continue
        result.groups.setdefault(p, []).append(entry)
    return result
