"""CLI command: env-surgeon export — export a .env file to JSON/TOML/shell."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from env_surgeon.parser import EnvFile
from env_surgeon.exporter import ExportFormat, export_env


@click.command("export")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--format", "fmt",
    type=click.Choice([f.value for f in ExportFormat], case_sensitive=False),
    default=ExportFormat.JSON.value,
    show_default=True,
    help="Output format.",
)
@click.option(
    "--no-mask",
    is_flag=True,
    default=False,
    help="Do not mask secret values (use with caution).",
)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Write output to this file instead of stdout.",
)
def export_command(env_file: str, fmt: str, no_mask: bool, output: str | None) -> None:
    """Export ENV_FILE to the chosen format."""
    try:
        env = EnvFile.parse(Path(env_file))
    except OSError as exc:
        click.echo(f"Error reading file: {exc}", err=True)
        sys.exit(2)

    export_fmt = ExportFormat(fmt)
    mask = not no_mask

    if output:
        out_path = Path(output)
        with out_path.open("w", encoding="utf-8") as fh:
            export_env(env, export_fmt, mask=mask, output=fh)
        click.echo(f"Exported to {out_path}")
    else:
        rendered = export_env(env, export_fmt, mask=mask)
        click.echo(rendered)
