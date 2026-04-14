"""Diff two .env files and report missing, extra, and changed keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_surgeon.parser import EnvFile, as_dict


@dataclass
class DiffResult:
    """Result of diffing two EnvFile objects."""

    missing_in_right: List[str] = field(default_factory=list)
    """Keys present in left but absent in right."""

    missing_in_left: List[str] = field(default_factory=list)
    """Keys present in right but absent in left."""

    changed: Dict[str, tuple] = field(default_factory=dict)
    """Keys present in both but with different values: {key: (left_val, right_val)}."""

    @property
    def is_identical(self) -> bool:
        """Return True when the two files are semantically identical."""
        return (
            not self.missing_in_right
            and not self.missing_in_left
            and not self.changed
        )


def diff_env_files(
    left: EnvFile,
    right: EnvFile,
    *,
    mask_values: bool = False,
) -> DiffResult:
    """Compare *left* against *right* and return a :class:`DiffResult`.

    Parameters
    ----------
    left:
        The baseline :class:`~env_surgeon.parser.EnvFile`.
    right:
        The file to compare against the baseline.
    mask_values:
        When *True*, changed values are replaced with ``"***"`` so that
        secrets are not exposed in output or logs.
    """
    left_dict: Dict[str, Optional[str]] = as_dict(left)
    right_dict: Dict[str, Optional[str]] = as_dict(right)

    left_keys = set(left_dict.keys())
    right_keys = set(right_dict.keys())

    result = DiffResult()
    result.missing_in_right = sorted(left_keys - right_keys)
    result.missing_in_left = sorted(right_keys - left_keys)

    for key in sorted(left_keys & right_keys):
        lv = left_dict[key]
        rv = right_dict[key]
        if lv != rv:
            if mask_values:
                result.changed[key] = ("***", "***")
            else:
                result.changed[key] = (lv, rv)

    return result


def format_diff(result: DiffResult, left_label: str = "left", right_label: str = "right") -> str:
    """Render a :class:`DiffResult` as a human-readable string."""
    lines: List[str] = []

    for key in result.missing_in_right:
        lines.append(f"- [{left_label}]  {key}")

    for key in result.missing_in_left:
        lines.append(f"+ [{right_label}] {key}")

    for key, (lv, rv) in result.changed.items():
        lines.append(f"~ {key}: {left_label}={lv!r}  {right_label}={rv!r}")

    if not lines:
        return "No differences found."

    return "\n".join(lines)
