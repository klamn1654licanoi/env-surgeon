"""Validate .env files against a schema (required keys, value patterns)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_surgeon.parser import EnvFile


@dataclass
class SchemaRule:
    key: str
    required: bool = True
    pattern: Optional[str] = None  # regex the value must match
    description: str = ""


@dataclass
class ValidationError:
    key: str
    message: str
    is_missing: bool = False

    def __str__(self) -> str:
        tag = "MISSING" if self.is_missing else "INVALID"
        return f"[{tag}] {self.key}: {self.message}"


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def __str__(self) -> str:
        if self.is_valid:
            return "All schema rules passed."
        lines = [str(e) for e in self.errors]
        return "\n".join(lines)


def load_schema(raw: Dict[str, dict]) -> List[SchemaRule]:
    """Build a list of SchemaRule objects from a plain dict (e.g. loaded from JSON/YAML)."""
    rules: List[SchemaRule] = []
    for key, opts in raw.items():
        rules.append(
            SchemaRule(
                key=key,
                required=opts.get("required", True),
                pattern=opts.get("pattern"),
                description=opts.get("description", ""),
            )
        )
    return rules


def validate_env_file(env: EnvFile, rules: List[SchemaRule]) -> ValidationResult:
    """Validate *env* against *rules*, returning a ValidationResult."""
    result = ValidationResult()
    values: Dict[str, str] = {}
    for entry in env.entries:
        if entry.key is not None:
            values[entry.key] = entry.value or ""

    for rule in rules:
        if rule.key not in values:
            if rule.required:
                result.errors.append(
                    ValidationError(
                        key=rule.key,
                        message=f"Required key '{rule.key}' is missing.",
                        is_missing=True,
                    )
                )
            continue

        value = values[rule.key]
        if rule.pattern and not re.fullmatch(rule.pattern, value):
            result.errors.append(
                ValidationError(
                    key=rule.key,
                    message=(
                        f"Value '{value}' does not match required pattern '{rule.pattern}'."
                    ),
                )
            )

    return result
