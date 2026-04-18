"""Tag env entries with arbitrary labels and filter by tag."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_surgeon.parser import EnvEntry, EnvFile


@dataclass
class TagResult:
    tagged: List[EnvEntry] = field(default_factory=list)
    untagged: List[EnvEntry] = field(default_factory=list)
    tag_map: Dict[str, List[str]] = field(default_factory=dict)  # tag -> [key]

    def is_clean(self) -> bool:
        return len(self.untagged) == 0


def tag_env_file(
    env: EnvFile,
    tags: Dict[str, List[str]],
    filter_tag: Optional[str] = None,
) -> TagResult:
    """Associate keys with tags and optionally filter entries by tag.

    Args:
        env: Parsed env file.
        tags: Mapping of tag name -> list of key names.
        filter_tag: If given, only entries with this tag are included in
                    ``tagged``; all others go to ``untagged``.
    """
    # Build reverse map: key -> set of tags
    key_to_tags: Dict[str, List[str]] = {}
    for tag, keys in tags.items():
        for k in keys:
            key_to_tags.setdefault(k, []).append(tag)

    # Build tag_map (tag -> keys that actually exist in the file)
    existing_keys = {e.key for e in env.entries if e.key is not None}
    tag_map: Dict[str, List[str]] = {}
    for tag, keys in tags.items():
        matched = [k for k in keys if k in existing_keys]
        if matched:
            tag_map[tag] = matched

    result = TagResult(tag_map=tag_map)

    for entry in env.entries:
        if entry.key is None:
            # comment / blank — pass through to untagged
            result.untagged.append(entry)
            continue

        entry_tags = key_to_tags.get(entry.key, [])
        if filter_tag is None:
            if entry_tags:
                result.tagged.append(entry)
            else:
                result.untagged.append(entry)
        else:
            if filter_tag in entry_tags:
                result.tagged.append(entry)
            else:
                result.untagged.append(entry)

    return result
