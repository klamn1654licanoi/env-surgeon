"""CLI command: env-surgeon sort"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

import click

from env_surgeon.parser import EnvFile
from env_surgeon.sorter import sort_env_file
from env_surgeon.formatter import write_env_file


@click.command("sort")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--key-order",
    default=None,
    help="Comma-separated list of keys that should appear first.",
)
@click.option(
    "--reverse",
    is_flag=True,
    default=False,
    help="Sort alphabetically in reverse (Z→A).",
)
@click.option(
    "--in-place",
    is_flag=True,
    default=False,
    help="Overwrite the input file with the sorted output.",
)
@click.option(
    "--check",
    is_flag=True,
    default=False,
    help="Exit with code 1 if the file is not already sorted (dry-run).",
)
@click.option(
    "--output",
    default=None,
    type=click.Path(dir_okay=False),
    help="Write sorted output to this path instead of stdout.",
)
def sort_command(
    env_file: str,
    key_order: Optional[str],
    reverse: bool,
    in_place: bool,
    check: bool,
    output: Optional[str],
) -> None:
    """Sort keys in ENV_FILE alphabetically (or by a custom order)."""
    path = Path(env_file)
    parsed = EnvFile.parse(path.read_text(encoding="utf-8"))

    order: Optional[List[str]] = (
        [k.strip() for k in key_order.split(",") if k.strip()]
        if key_order
        else None
    )

    result = sort_env_file(parsed, key_order=order, reverse=reverse)

    if check:
        if result.is_clean():
            click.echo(f"{env_file} is already sorted.")
            sys.exit(0)
        else:
            click.echo(f"{env_file} is NOT sorted.", err=True)
            sys.exit(1)

    # Produce sorted text
    sorted_env = EnvFile(entries=result.entries)
    sorted_text = write_env_file(sorted_env)

    if in_place:
        path.write_text(sorted_text, encoding="utf-8")
        click.echo(f"Sorted {env_file} in place.")
    elif output:
        Path(output).write_text(sorted_text, encoding="utf-8")
        click.echo(f"Sorted output written to {output}.")
    else:
        click.echo(sorted_text, nl=False)
