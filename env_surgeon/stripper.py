"""Remove comments and blank lines from .env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from env_surgeon.parser import EnvFile, EnvEntry


@dataclass
class StripResult:
    entries: list[EnvEntry] = field(default_factory=list)
    removed_comments: int = 0
    removed_blanks: int = 0


def is_clean(result: StripResult) -> bool:
    return result.removed_comments == 0 and result.removed_blanks == 0


def strip_env_file(
    env_file: EnvFile,
    *,
    strip_comments: bool = True,
    strip_blanks: bool = True,
) -> StripResult:
    result = StripResult()
    for entry in env_file.entries:
        if entry.key is None:
            # blank line: raw == "" or whitespace-only
            if entry.raw.strip() == "":
                if strip_blanks:
                    result.removed_blanks += 1
                    continue
            else:
                # comment line
                if strip_comments:
                    result.removed_comments += 1
                    continue
        result.entries.append(entry)
    return result
