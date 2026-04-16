"""CLI command: env-surgeon patch."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from env_surgeon.formatter import write_env_file
from env_surgeon.parser import EnvFile
from env_surgeon.patcher import patch_env_file


@click.command("patch")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option("-s", "--set", "set_pairs", multiple=True, metavar="KEY=VALUE",
              help="Set or update a key (may be repeated).")
@click.option("-r", "--remove", "remove_keys", multiple=True, metavar="KEY",
              help="Remove a key (may be repeated).")
@click.option("--no-overwrite", is_flag=True, default=False,
              help="Skip keys that already exist.")
@click.option("--in-place", is_flag=True, default=False,
              help="Write changes back to the source file.")
@click.option("--output", "-o", type=click.Path(dir_okay=False), default=None,
              help="Write patched file to this path instead of stdout.")
def patch_command(
    env_file: str,
    set_pairs: tuple[str, ...],
    remove_keys: tuple[str, ...],
    no_overwrite: bool,
    in_place: bool,
    output: str | None,
) -> None:
    """Patch KEY=VALUE pairs in an .env file."""
    parsed_pairs: dict[str, str] = {}
    for pair in set_pairs:
        if "=" not in pair:
            click.echo(f"ERROR: --set value must be KEY=VALUE, got: {pair!r}", err=True)
            sys.exit(2)
        k, v = pair.split("=", 1)
        parsed_pairs[k.strip()] = v

    env = EnvFile.parse(Path(env_file))
    result = patch_env_file(
        env,
        set_pairs=parsed_pairs,
        remove_keys=list(remove_keys),
        no_overwrite=no_overwrite,
    )

    dest: Path | None = None
    if in_place:
        dest = Path(env_file)
    elif output:
        dest = Path(output)

    if dest:
        write_env_file(result.entries, dest)
    else:
        for entry in result.entries:
            if entry.raw_line is not None and entry.key is None:
                click.echo(entry.raw_line, nl=False)
            else:
                from env_surgeon.formatter import format_entry
                click.echo(format_entry(entry))

    if result.set_keys:
        click.echo(f"Added: {', '.join(result.set_keys)}", err=True)
    if result.updated_keys:
        click.echo(f"Updated: {', '.join(result.updated_keys)}", err=True)
    if result.removed_keys:
        click.echo(f"Removed: {', '.join(result.removed_keys)}", err=True)
    if result.skipped_keys:
        click.echo(f"Skipped: {', '.join(result.skipped_keys)}", err=True)
