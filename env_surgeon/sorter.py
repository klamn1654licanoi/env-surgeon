"""Sort keys in an .env file alphabetically or by a custom key order."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from env_surgeon.parser import EnvEntry, EnvFile


@dataclass
class SortResult:
    entries: List[EnvEntry] = field(default_factory=list)
    original_order: List[str] = field(default_factory=list)
    sorted_order: List[str] = field(default_factory=list)

    def is_clean(self) -> bool:
        """Return True if the file was already in sorted order."""
        return self.original_order == self.sorted_order


def sort_env_file(
    env_file: EnvFile,
    *,
    key_order: Optional[List[str]] = None,
    reverse: bool = False,
    comments_first: bool = True,
) -> SortResult:
    """Sort entries in *env_file*.

    Parameters
    ----------
    env_file:
        Parsed :class:`EnvFile` to sort.
    key_order:
        Optional explicit ordering.  Keys listed here appear first (in the
        given order); remaining keys are sorted alphabetically.
    reverse:
        When *True*, alphabetical sort is reversed (Z→A).
    comments_first:
        When *True*, standalone comment / blank entries that precede a key
        are kept attached to that key during sorting.
    """
    # Separate comment-only / blank lines from key entries
    leading_comments: List[EnvEntry] = []
    keyed: List[EnvEntry] = []

    pending_comments: List[EnvEntry] = []
    for entry in env_file.entries:
        if entry.key is None:
            pending_comments.append(entry)
        else:
            if comments_first:
                # Attach pending comments to this key entry
                keyed.append(
                    EnvEntry(
                        key=entry.key,
                        value=entry.value,
                        comment=entry.comment,
                        preceding_comment=(
                            "\n".join(
                                c.raw_line.rstrip() for c in pending_comments
                            )
                            if pending_comments
                            else entry.preceding_comment
                        ),
                        raw_line=entry.raw_line,
                    )
                )
                pending_comments = []
            else:
                leading_comments.extend(pending_comments)
                pending_comments = []
                keyed.append(entry)

    # Any trailing comments with no following key
    trailing_comments = pending_comments

    original_order = [e.key for e in keyed if e.key]

    if key_order:
        order_index = {k: i for i, k in enumerate(key_order)}
        def _sort_key(e: EnvEntry) -> tuple:
            idx = order_index.get(e.key, len(key_order))
            alpha = e.key.lower() if e.key else ""
            return (idx, alpha)
        keyed.sort(key=_sort_key, reverse=False)
    else:
        keyed.sort(key=lambda e: (e.key or "").lower(), reverse=reverse)

    sorted_order = [e.key for e in keyed if e.key]

    final_entries = leading_comments + keyed + trailing_comments

    return SortResult(
        entries=final_entries,
        original_order=original_order,
        sorted_order=sorted_order,
    )
