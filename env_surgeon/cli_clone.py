"""CLI command: env-surgeon clone."""
from __future__ import annotations

import click

from env_surgeon.parser import EnvFile
from env_surgeon.cloner import clone_env_file, is_clean
from env_surgeon.formatter import write_env_file


@click.command("clone")
@click.argument("source", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(dir_okay=False))
@click.option("--prefix", default=None, help="Only copy keys that start with PREFIX.")
@click.option("--key", "keys", multiple=True, help="Explicit key(s) to copy (repeatable).")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys already present in target.")
@click.option("--dry-run", is_flag=True, default=False, help="Print what would be written without writing.")
def clone_command(
    source: str,
    target: str,
    prefix: str | None,
    keys: tuple[str, ...],
    no_overwrite: bool,
    dry_run: bool,
) -> None:
    """Clone SOURCE env file into TARGET with optional filtering."""
    from pathlib import Path

    src_path = Path(source)
    tgt_path = Path(target)

    env = EnvFile.parse(src_path)
    result = clone_env_file(
        env,
        tgt_path,
        prefix=prefix or None,
        keys=list(keys) if keys else None,
        overwrite=not no_overwrite,
    )

    if result.skipped_keys:
        click.echo(f"Skipped {len(result.skipped_keys)} key(s): {', '.join(result.skipped_keys)}")

    if dry_run:
        for entry in result.entries:
            if entry.key:
                click.echo(f"  {entry.key}={entry.value}")
        click.echo("(dry-run: nothing written)")
        raise SystemExit(0)

    write_env_file(tgt_path, result.entries)
    click.echo(f"Cloned {len([e for e in result.entries if e.key])} key(s) → {tgt_path}")
    raise SystemExit(0 if is_clean(result) else 1)
