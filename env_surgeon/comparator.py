"""Compare multiple .env files and produce a matrix of key presence/values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from env_surgeon.parser import EnvFile, parse


@dataclass
class CompareMatrix:
    """Matrix showing each key across all compared files."""
    files: List[str]
    # key -> {filename -> value or None}
    matrix: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)

    def all_keys(self) -> List[str]:
        return sorted(self.matrix.keys())

    def is_consistent(self, key: str) -> bool:
        """True when all files that have the key share the same value."""
        values = [v for v in self.matrix[key].values() if v is not None]
        return len(set(values)) <= 1

    def missing_in(self, key: str) -> List[str]:
        """Return filenames where the key is absent."""
        return [f for f, v in self.matrix[key].items() if v is None]

    def inconsistent_keys(self) -> List[str]:
        return [k for k in self.all_keys() if not self.is_consistent(k)]

    def missing_keys(self) -> List[str]:
        """Keys absent in at least one file."""
        return [k for k in self.all_keys() if self.missing_in(k)]


def compare_env_files(paths: List[str]) -> CompareMatrix:
    """Parse each path and build a CompareMatrix."""
    envs: List[EnvFile] = []
    for p in paths:
        with open(p) as fh:
            envs.append(parse(fh.read()))

    all_keys: set[str] = set()
    dicts = []
    for env in envs:
        d = {e.key: e.value for e in env.entries if e.key is not None}
        dicts.append(d)
        all_keys.update(d.keys())

    matrix: Dict[str, Dict[str, Optional[str]]] = {}
    for key in all_keys:
        matrix[key] = {p: dicts[i].get(key) for i, p in enumerate(paths)}

    return CompareMatrix(files=list(paths), matrix=matrix)


def format_matrix(cm: CompareMatrix, mask_secrets: bool = False) -> str:
    """Render a human-readable table of the comparison matrix."""
    from env_surgeon.masker import is_secret_key

    col_w = max((len(f) for f in cm.files), default=10)
    key_w = max((len(k) for k in cm.all_keys()), default=10)
    header = f"{'KEY':<{key_w}}  " + "  ".join(f"{f:<{col_w}}" for f in cm.files)
    lines = [header, "-" * len(header)]
    for key in cm.all_keys():
        row_vals = []
        for fname in cm.files:
            val = cm.matrix[key].get(fname)
            if val is None:
                row_vals.append(f"{'<missing>':<{col_w}}")
            elif mask_secrets and is_secret_key(key):
                row_vals.append(f"{'***':<{col_w}}")
            else:
                display = val if len(val) <= col_w else val[:col_w - 3] + "..."
                row_vals.append(f"{display:<{col_w}}")
        lines.append(f"{key:<{key_w}}  " + "  ".join(row_vals))
    return "\n".join(lines)
