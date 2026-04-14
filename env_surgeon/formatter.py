"""Serialize EnvEntry lists and MergeResult back to .env file text."""

from typing import List, Optional

from env_surgeon.parser import EnvEntry
from env_surgeon.merger import MergeResult


def _needs_quoting(value: str) -> bool:
    """Return True if the value should be wrapped in double quotes."""
    return any(c in value for c in (" ", "\t", "#", "'", '"', "\n"))


def format_entry(entry: EnvEntry, quote_values: bool = False) -> str:
    """Render a single EnvEntry as a line suitable for a .env file."""
    if entry.is_comment:
        return entry.raw_line
    if not entry.key:
        return ""
    value = entry.value
    if quote_values or _needs_quoting(value):
        escaped = value.replace('"', '\\"')
        value = f'"{escaped}"'
    return f"{entry.key}={value}"


def format_entries(entries: List[EnvEntry], quote_values: bool = False) -> str:
    """Render a list of EnvEntry objects into .env file text."""
    lines = [format_entry(e, quote_values=quote_values) for e in entries]
    return "\n".join(lines) + "\n" if lines else ""


def format_merge_result(
    result: MergeResult,
    quote_values: bool = False,
    include_conflict_comments: bool = True,
) -> str:
    """Render a MergeResult to .env text, optionally annotating conflicts."""
    conflict_keys = {mc.key for mc in result.conflicts}
    lines: List[str] = []

    for entry in result.entries:
        if include_conflict_comments and entry.key in conflict_keys:
            mc = next(mc for mc in result.conflicts if mc.key == entry.key)
            lines.append(f"# CONFLICT on '{entry.key}':")
            for src, val in mc.values.items():
                lines.append(f"#   {src}={val!r}")
        lines.append(format_entry(entry, quote_values=quote_values))

    return "\n".join(lines) + "\n" if lines else ""


def write_env_file(
    entries: List[EnvEntry],
    path: str,
    quote_values: bool = False,
) -> None:
    """Write entries to a .env file at the given path."""
    content = format_entries(entries, quote_values=quote_values)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
