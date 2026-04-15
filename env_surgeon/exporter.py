"""Export EnvFile data to multiple formats: JSON, TOML, shell script."""
from __future__ import annotations

import json
from enum import Enum
from typing import IO

from env_surgeon.parser import EnvFile
from env_surgeon.masker import mask_env_file


class ExportFormat(str, Enum):
    JSON = "json"
    SHELL = "shell"
    TOML = "toml"


def _to_json(env: EnvFile, mask: bool) -> str:
    source = mask_env_file(env).masked if mask else env
    data = {entry.key: entry.value for entry in source.entries if entry.key}
    return json.dumps(data, indent=2)


def _to_shell(env: EnvFile, mask: bool) -> str:
    source = mask_env_file(env).masked if mask else env
    lines: list[str] = ["#!/usr/bin/env sh"]
    for entry in source.entries:
        if entry.key is None:
            # blank line or comment passthrough
            lines.append(entry.raw_line.rstrip("\n"))
        else:
            value = entry.value or ""
            escaped = value.replace('"', '\\"')
            lines.append(f'export {entry.key}="{escaped}"')
    return "\n".join(lines)


def _to_toml(env: EnvFile, mask: bool) -> str:
    source = mask_env_file(env).masked if mask else env
    lines: list[str] = ["[env]"]
    for entry in source.entries:
        if entry.key is None:
            continue
        value = entry.value or ""
        escaped = value.replace('"', '\\"')
        lines.append(f'{entry.key} = "{escaped}"')
    return "\n".join(lines)


def export_env(
    env: EnvFile,
    fmt: ExportFormat,
    *,
    mask: bool = True,
    output: IO[str] | None = None,
) -> str:
    """Render *env* in the requested format and optionally write to *output*."""
    renderers = {
        ExportFormat.JSON: _to_json,
        ExportFormat.SHELL: _to_shell,
        ExportFormat.TOML: _to_toml,
    }
    rendered = renderers[fmt](env, mask)
    if output is not None:
        output.write(rendered)
        if not rendered.endswith("\n"):
            output.write("\n")
    return rendered
