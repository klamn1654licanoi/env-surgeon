"""CLI command: env-surgeon dedup — remove duplicate keys from a .env file."""

from __future__ import annotations

import sys

import click

from env_surgeon.deduplicator import KeepStrategy, deduplicate_env_file
from env_surgeon.formatter import format_entries, write_env_file
from env_surgeon.parser import EnvFile


@click.command("dedup")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--keep",
    type=click.Choice(["first", "last"], case_sensitive=False),
    default="first",
    show_default=True,
    help="Which occurrence of a duplicate key to keep.",
)
@click.option(
    "--in-place", "-i",
    is_flag=True,
    default=False,
    help="Overwrite the input file with the deduplicated output.",
)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False),
    default=None,
    help="Write deduplicated output to this file instead of stdout.",
)
def dedup_command(env_file: str, keep: str, in_place: bool, output: str | None) -> None:
    """Remove duplicate keys from ENV_FILE.

    By default the first occurrence of each key is kept and the result
    is printed to stdout.  Use --in-place to overwrite the source file.
    """
    parsed = EnvFile.parse(env_file)
    strategy = KeepStrategy(keep.lower())
    result = deduplicate_env_file(parsed, strategy=strategy)

    if result.removed:
        for entry in result.removed:
            click.echo(
                click.style(
                    f"  removed duplicate: {entry.key} (line {entry.line_number})",
                    fg="yellow",
                ),
                err=True,
            )

    formatted = format_entries(result.entries)

    dest = env_file if in_place else output
    if dest:
        write_env_file(dest, result.entries)
        click.echo(click.style(f"Written to {dest}", fg="green"), err=True)
    else:
        click.echo(formatted, nl=False)

    sys.exit(1 if result.removed else 0)
