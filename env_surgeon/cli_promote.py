"""CLI command for promoting env keys from one file to another."""
from __future__ import annotations
import click
from pathlib import Path
from env_surgeon.parser import parse_env_file
from env_surgeon.promoter import promote_env_file, is_clean
from env_surgeon.formatter import write_env_file


@click.command("promote")
@click.argument("source", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(exists=True, dir_okay=False))
@click.option("--key", "keys", multiple=True, help="Keys to promote (default: all).")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys already in target.")
@click.option("--dry-run", is_flag=True, default=False, help="Print result without writing.")
@click.option("--output", type=click.Path(dir_okay=False), default=None, help="Write result here instead of target.")
def promote_command(
    source: str,
    target: str,
    keys: tuple,
    no_overwrite: bool,
    dry_run: bool,
    output: str | None,
) -> None:
    """Promote keys from SOURCE into TARGET."""
    src = parse_env_file(Path(source))
    tgt = parse_env_file(Path(target))

    result = promote_env_file(
        src,
        tgt,
        keys=list(keys) if keys else None,
        overwrite=not no_overwrite,
    )

    if result.promoted:
        click.echo(f"Promoted: {', '.join(result.promoted)}")
    if result.overwritten:
        click.echo(f"Overwritten: {', '.join(result.overwritten)}")
    if result.skipped:
        click.echo(f"Skipped: {', '.join(result.skipped)}", err=True)

    if dry_run:
        for entry in result.entries:
            click.echo(entry.raw)
        raise SystemExit(0)

    dest = Path(output) if output else Path(target)
    from env_surgeon.parser import EnvFile
    write_env_file(EnvFile(path=dest, entries=result.entries), dest)

    if not is_clean(result):
        raise SystemExit(1)
