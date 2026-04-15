"""CLI sub-command: mask — print a .env file with secrets redacted."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from env_surgeon.masker import mask_env_file
from env_surgeon.parser import EnvFile
from env_surgeon.formatter import format_entries


@click.command("mask")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--extra-pattern",
    "extra_patterns",
    multiple=True,
    metavar="PATTERN",
    help="Additional regex patterns for keys to mask (can be repeated).",
)
@click.option(
    "--placeholder",
    default="***",
    show_default=True,
    help="Replacement text for masked values.",
)
@click.option(
    "--list-masked",
    is_flag=True,
    default=False,
    help="Print the list of masked keys to stderr after output.",
)
def mask_command(
    env_file: str,
    extra_patterns: tuple[str, ...],
    placeholder: str,
    list_masked: bool,
) -> None:
    """Print ENV_FILE with secret values replaced by PLACEHOLDER."""
    path = Path(env_file)
    try:
        parsed = EnvFile.parse(path)
    except OSError as exc:
        click.echo(f"Error reading {path}: {exc}", err=True)
        sys.exit(2)

    result = mask_env_file(
        parsed,
        extra_patterns=extra_patterns if extra_patterns else None,
        placeholder=placeholder,
    )

    click.echo(format_entries(result.entries), nl=False)

    if list_masked:
        if result.masked_keys:
            click.echo(
                f"Masked keys ({len(result.masked_keys)}): "
                + ", ".join(result.masked_keys),
                err=True,
            )
        else:
            click.echo("No keys were masked.", err=True)
