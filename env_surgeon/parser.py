"""Parser for .env files — handles reading and tokenizing key-value pairs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


_LINE_RE = re.compile(
    r"^\s*"
    r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*=\s*"
    r"(?P<value>.*?)\s*$"
)


@dataclass
class EnvEntry:
    key: str
    value: str
    comment: Optional[str] = None  # inline or preceding comment
    line_number: int = 0


@dataclass
class EnvFile:
    path: Path
    entries: List[EnvEntry] = field(default_factory=list)

    def as_dict(self) -> Dict[str, str]:
        """Return a plain key→value mapping (last value wins for duplicates)."""
        return {e.key: e.value for e in self.entries}

    def get(self, key: str) -> Optional[EnvEntry]:
        """Return the last :class:`EnvEntry` matching *key*, or ``None``."""
        for entry in reversed(self.entries):
            if entry.key == key:
                return entry
        return None


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    for quote in ('"', "'"):
        if value.startswith(quote) and value.endswith(quote) and len(value) >= 2:
            return value[1:-1]
    return value


def parse_env_file(path: Path) -> EnvFile:
    """Parse a .env file and return an :class:`EnvFile` instance.

    Lines starting with ``#`` are treated as comments and attached to the
    *next* key-value pair found.  Blank lines reset the pending comment.
    """
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    env_file = EnvFile(path=path)
    pending_comment: Optional[str] = None

    with path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n")

            if not line.strip():
                pending_comment = None
                continue

            if line.strip().startswith("#"):
                pending_comment = line.strip().lstrip("# ").strip()
                continue

            # Strip inline comment (value # comment)
            inline_comment: Optional[str] = None
            if " #" in line:
                value_part, _, inline_comment_raw = line.partition(" #")
                inline_comment = inline_comment_raw.strip()
                line = value_part

            match = _LINE_RE.match(line)
            if match:
                raw_value = match.group("value")
                entry = EnvEntry(
                    key=match.group("key"),
                    value=_strip_quotes(raw_value),
                    comment=pending_comment or inline_comment,
                    line_number=lineno,
                )
                env_file.entries.append(entry)
                pending_comment = None

    return env_file
