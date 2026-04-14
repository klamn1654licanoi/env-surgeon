"""Audit .env files for common issues: missing keys, empty values, duplicates."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from env_surgeon.parser import EnvFile


@dataclass
class AuditIssue:
    key: Optional[str]
    message: str
    severity: str  # "error" | "warning" | "info"
    line: Optional[int] = None

    def __str__(self) -> str:
        location = f" (line {self.line})" if self.line is not None else ""
        key_part = f"[{self.key}]" if self.key else "[—]"
        return f"{self.severity.upper()} {key_part}{location}: {self.message}"


@dataclass
class AuditResult:
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def summary(self) -> str:
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        return f"{errors} error(s), {warnings} warning(s) found."


def audit_env_file(env_file: EnvFile) -> AuditResult:
    """Run all audit checks on a parsed EnvFile and return an AuditResult."""
    result = AuditResult()
    seen_keys: dict[str, int] = {}

    for entry in env_file.entries:
        if entry.key is None:
            continue  # comment or blank line

        line = entry.line

        # Duplicate key check
        if entry.key in seen_keys:
            result.issues.append(
                AuditIssue(
                    key=entry.key,
                    message=(
                        f"Duplicate key; first seen at line {seen_keys[entry.key]}"
                    ),
                    severity="error",
                    line=line,
                )
            )
        else:
            seen_keys[entry.key] = line if line is not None else -1

        # Empty value check
        if entry.value == "":
            result.issues.append(
                AuditIssue(
                    key=entry.key,
                    message="Key has an empty value.",
                    severity="warning",
                    line=line,
                )
            )

        # Key naming convention (should be UPPER_SNAKE_CASE)
        if not entry.key.isupper() and entry.key.replace("_", "").isalpha():
            result.issues.append(
                AuditIssue(
                    key=entry.key,
                    message="Key is not UPPER_SNAKE_CASE.",
                    severity="info",
                    line=line,
                )
            )

    return result
