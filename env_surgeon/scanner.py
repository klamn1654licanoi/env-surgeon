"""Scanner: detect .env files across a directory tree."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ScanResult:
    root: Path
    found: List[Path] = field(default_factory=list)
    skipped: List[Path] = field(default_factory=list)

    def file_count(self) -> int:
        return len(self.found)

    def is_empty(self) -> bool:
        return len(self.found) == 0


_DEFAULT_NAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.staging",
    ".env.production",
    ".env.test",
    ".env.example",
}


def scan_directory(
    root: Path,
    *,
    names: Optional[set] = None,
    max_depth: int = 5,
    skip_hidden_dirs: bool = True,
) -> ScanResult:
    """Walk *root* up to *max_depth* levels and collect .env files."""
    allowed = names if names is not None else _DEFAULT_NAMES
    result = ScanResult(root=root)

    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        depth = len(current.relative_to(root).parts)
        if depth >= max_depth:
            dirnames.clear()
            continue
        if skip_hidden_dirs:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for name in filenames:
            if name in allowed or name.startswith(".env."):
                p = current / name
                if p.stat().st_size == 0:
                    result.skipped.append(p)
                else:
                    result.found.append(p)

    result.found.sort()
    result.skipped.sort()
    return result
