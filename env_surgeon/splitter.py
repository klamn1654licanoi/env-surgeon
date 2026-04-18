"""Split an EnvFile into multiple files based on key prefix."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_surgeon.parser import EnvFile, EnvEntry


@dataclass
class SplitResult:
    buckets: Dict[str, List[EnvEntry]] = field(default_factory=dict)
    unmatched: List[EnvEntry] = field(default_factory=list)

    def is_clean(self) -> bool:
        """True when every entry was assigned to a named bucket."""
        return len(self.unmatched) == 0


def _prefix(key: str) -> Optional[str]:
    """Return the portion before the first '_', or None if no underscore."""
    idx = key.find("_")
    if idx <= 0:
        return None
    return key[:idx].upper()


def split_env_file(
    env: EnvFile,
    prefixes: Optional[List[str]] = None,
    *,
    include_comments: bool = True,
) -> SplitResult:
    """Partition entries by key prefix.

    Parameters
    ----------
    env:
        Parsed source file.
    prefixes:
        Explicit list of prefixes to extract (upper-cased automatically).
        When *None* every detected prefix is used.
    include_comments:
        If True, comment/blank entries are placed into the bucket of the
        immediately following key entry, or into *unmatched* if none follows.
    """
    result = SplitResult()
    canonical = {p.upper() for p in prefixes} if prefixes is not None else None

    pending_comments: List[EnvEntry] = []

    for entry in env.entries:
        if entry.key is None:
            # comment or blank line — hold until we know the next bucket
            if include_comments:
                pending_comments.append(entry)
            continue

        pfx = _prefix(entry.key)
        if pfx is None or (canonical is not None and pfx not in canonical):
            result.unmatched.extend(pending_comments)
            result.unmatched.append(entry)
            pending_comments = []
            continue

        bucket = result.buckets.setdefault(pfx, [])
        bucket.extend(pending_comments)
        bucket.append(entry)
        pending_comments = []

    # flush any trailing comments
    result.unmatched.extend(pending_comments)
    return result
