"""Generate a .env.example file from an existing .env, stripping secret values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.masker import is_secret_key


@dataclass
class TemplateResult:
    """Outcome of templating an EnvFile."""

    entries: List[EnvEntry] = field(default_factory=list)
    stripped_keys: List[str] = field(default_factory=list)

    def is_clean(self) -> bool:
        """True when no keys were stripped (no secrets detected)."""
        return len(self.stripped_keys) == 0


def template_env_file(
    env_file: EnvFile,
    placeholder: str = "",
    extra_secret_patterns: Optional[List[str]] = None,
    keep_comments: bool = True,
) -> TemplateResult:
    """Return a TemplateResult whose entries are safe for committing.

    Secret values are replaced with *placeholder* (default: empty string).
    Non-secret values are preserved verbatim so the template remains useful.
    Comment-only lines are kept when *keep_comments* is True.
    """
    result_entries: List[EnvEntry] = []
    stripped_keys: List[str] = []

    for entry in env_file.entries:
        # Blank / comment-only lines
        if entry.key is None:
            if keep_comments:
                result_entries.append(entry)
            continue

        if is_secret_key(entry.key, extra_patterns=extra_secret_patterns):
            stripped_keys.append(entry.key)
            result_entries.append(
                EnvEntry(
                    key=entry.key,
                    value=placeholder,
                    comment=entry.comment,
                    raw_line=None,
                )
            )
        else:
            result_entries.append(entry)

    return TemplateResult(entries=result_entries, stripped_keys=stripped_keys)
