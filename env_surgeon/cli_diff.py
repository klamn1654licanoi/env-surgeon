"""CLI command for diffing two .env files."""
from __future__ import annotations

import sys
from pathlib import Path

from env_surgeon.differ import diff_env_files, format_diff, is_identical
from env_surgeon.parser import parse_env_file


def diff_command(left: str, right: str, no_color: bool = False) -> int:
    """Compare two .env files and print a human-readable diff.

    Returns:
        0  – files are identical
        1  – files differ
        2  – a file was not found or could not be parsed
    """
    left_path = Path(left)
    right_path = Path(right)

    for path in (left_path, right_path):
        if not path.exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2

    try:
        left_env = parse_env_file(left_path)
        right_env = parse_env_file(right_path)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = diff_env_files(left_env, right_env)

    if is_identical(result):
        print("Files are identical.")
        return 0

    output = format_diff(result, left_label=left, right_label=right)

    if no_color:
        # Strip ANSI escape codes when colour output is disabled.
        import re
        output = re.sub(r"\x1b\[[0-9;]*m", "", output)

    print(output)
    return 1
