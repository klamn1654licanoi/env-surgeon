"""Profile an .env file: count keys, secrets, comments, empty values, etc."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from env_surgeon.parser import EnvFile
from env_surgeon.masker import is_secret_key


@dataclass
class ProfileResult:
    path: str
    total_entries: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    secret_keys: List[str] = field(default_factory=list)
    empty_value_keys: List[str] = field(default_factory=list)
    all_keys: List[str] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.all_keys)

    @property
    def secret_count(self) -> int:
        return len(self.secret_keys)

    @property
    def empty_count(self) -> int:
        return len(self.empty_value_keys)


def profile_env_file(env_file: EnvFile, extra_patterns: List[str] | None = None) -> ProfileResult:
    result = ProfileResult(path=env_file.path or "<unknown>")
    for entry in env_file.entries:
        if entry.is_comment:
            result.comment_lines += 1
            continue
        if entry.key is None:
            result.blank_lines += 1
            continue
        result.total_entries += 1
        result.all_keys.append(entry.key)
        if is_secret_key(entry.key, extra_patterns=extra_patterns):
            result.secret_keys.append(entry.key)
        if entry.value == "":
            result.empty_value_keys.append(entry.key)
    return result
