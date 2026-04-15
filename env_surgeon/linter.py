"""Lint .env files against common style and correctness rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from env_surgeon.parser import EnvFile


class LintSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintViolation:
    line: int
    key: str | None
    message: str
    severity: LintSeverity

    def __str__(self) -> str:
        loc = f"line {self.line}" + (f" [{self.key}]" if self.key else "")
        return f"{self.severity.value.upper()} {loc}: {self.message}"


@dataclass
class LintResult:
    path: str
    violations: List[LintViolation] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(v.severity == LintSeverity.ERROR for v in self.violations)

    @property
    def is_clean(self) -> bool:
        return len(self.violations) == 0


def lint_env_file(env_file: EnvFile) -> LintResult:
    """Run all lint rules against *env_file* and return a LintResult."""
    result = LintResult(path=env_file.path)
    seen_keys: dict[str, int] = {}

    for entry in env_file.entries:
        if entry.key is None:
            continue

        lineno = entry.lineno
        key = entry.key
        value = entry.value or ""

        # Rule: duplicate keys
        if key in seen_keys:
            result.violations.append(
                LintViolation(lineno, key, f"duplicate key (first at line {seen_keys[key]})", LintSeverity.ERROR)
            )
        else:
            seen_keys[key] = lineno

        # Rule: trailing whitespace in value
        if value != value.strip():
            result.violations.append(
                LintViolation(lineno, key, "value has leading or trailing whitespace", LintSeverity.WARNING)
            )

        # Rule: lowercase key
        if key != key.upper():
            result.violations.append(
                LintViolation(lineno, key, "key is not uppercase", LintSeverity.INFO)
            )

        # Rule: key contains spaces
        if " " in key:
            result.violations.append(
                LintViolation(lineno, key, "key contains spaces", LintSeverity.ERROR)
            )

        # Rule: empty value without explicit quote
        if value == "" and entry.raw and "=" in entry.raw and entry.raw.strip().endswith("="):
            result.violations.append(
                LintViolation(lineno, key, "empty value; consider using explicit empty quotes", LintSeverity.WARNING)
            )

    return result
