"""CLI command: env-surgeon rename — rename keys in a .env file."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from env_surgeon.formatter import format_entries, write_env_file
from env_surgeon.parser import parse_env_file
from env_surgeon.renamer import rename_keys


@click.command("rename")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-r",
    "--rename",
    "renames",
    multiple=True,
    metavar="OLD=NEW",
    required=True,
    help="Key rename pair, e.g. OLD_KEY=NEW_KEY.  Repeatable.",
)
@click.option(
    "--in-place",
    is_flag=True,
    default=False,
    help="Overwrite the source file instead of printing to stdout.",
)
@click.option(
    "--ignore-missing",
    is_flag=True,
    default=False,
    help="Do not error when a key to rename is absent.",
)
def rename_command(
    env_file: str,
    renames: tuple[str, ...],
    in_place: bool,
    ignore_missing: bool,
) -> None:
    """Rename one or more keys inside ENV_FILE.

    \b
    Example:
        env-surgeon rename .env -r OLD_TOKEN=API_TOKEN -r DB_PASS=DATABASE_PASSWORD
    """
    mapping: dict[str, str] = {}
    for pair in renames:
        if "=" not in pair:
            click.echo(f"[error] Invalid rename pair (expected OLD=NEW): {pair!r}", err=True)
            sys.exit(2)
        old, _, new = pair.partition("=")
        mapping[old.strip()] = new.strip()

    parsed = parse_env_file(Path(env_file))
    result = rename_keys(parsed, mapping, ignore_missing=ignore_missing)

    if result.not_found:
        for key in result.not_found:
            click.echo(f"[error] Key not found in file: {key}", err=True)
        sys.exit(1)

    output = format_entries(result.entries)

    if in_place:
        write_env_file(Path(env_file), result.entries)
        click.echo(f"[ok] Renamed {len(result.renamed)} key(s) in {env_file}")
    else:
        click.echo(output, nl=False)
