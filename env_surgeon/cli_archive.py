"""CLI command: env-surgeon archive"""
from __future__ import annotations

from pathlib import Path

import click

from env_surgeon.archiver import archive_env_file, is_clean


@click.command("archive")
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--dir",
    "archive_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Directory to store the archive (default: same as SOURCE).",
)
def archive_command(source: Path, archive_dir: Path | None) -> None:
    """Create a timestamped backup of a .env file."""
    try:
        result = archive_env_file(source, archive_dir)
    except FileNotFoundError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(2) from exc

    if is_clean(result):
        click.echo(
            f"archived {result.key_count} key(s) → {result.archive_path}"
        )
    else:
        click.echo("error: archive was not created", err=True)
        raise SystemExit(1)
