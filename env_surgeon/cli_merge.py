"""CLI command for merging two or more .env files."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from env_surgeon.formatter import write_env_file
from env_surgeon.merger import ConflictStrategy, MergeConflictError, merge_env_files
from env_surgeon.parser import parse_env_file


def merge_command(
    sources: List[str],
    output: Optional[str] = None,
    strategy: str = "last_wins",
) -> int:
    """Merge *sources* .env files into one and write the result.

    Returns:
        0 – success
        1 – unresolvable conflict (strategy=error)
        2 – file not found or parse error
    """
    try:
        conflict_strategy = ConflictStrategy[strategy.upper()]
    except KeyError:
        valid = ", ".join(s.name.lower() for s in ConflictStrategy)
        print(f"error: unknown strategy '{strategy}'. Choose from: {valid}", file=sys.stderr)
        return 2

    env_files = []
    for src in sources:
        path = Path(src)
        if not path.exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2
        try:
            env_files.append(parse_env_file(path))
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    try:
        result = merge_env_files(env_files, strategy=conflict_strategy)
    except MergeConflictError as exc:
        print(f"conflict: {exc}", file=sys.stderr)
        return 1

    if output:
        dest = Path(output)
        write_env_file(result, dest)
        print(f"Merged {len(sources)} file(s) → {dest}")
    else:
        # Print merged content to stdout.
        from env_surgeon.formatter import format_merge_result
        print(format_merge_result(result), end="")

    if result.conflicts:
        print(
            f"warning: {len(result.conflicts)} conflict(s) resolved via '{strategy}'.",
            file=sys.stderr,
        )

    return 0
