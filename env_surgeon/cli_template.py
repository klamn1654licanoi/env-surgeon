"""CLI command: env-surgeon template — produce a .env.example from a .env."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

import click

from env_surgeon.parser import EnvFile
from env_surgeon.templater import template_env_file
from env_surgeon.formatter import format_entries, write_env_file


@click.command("template")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--output", "-o",
    default=None,
    help="Destination file (default: <env_file>.example).",
)
@click.option(
    "--placeholder",
    default="",
    show_default=True,
    help="Value to use for stripped secrets.",
)
@click.option(
    "--pattern", "-p",
    multiple=True,
    help="Extra regex patterns to treat as secret keys.",
)
@click.option(
    "--no-comments",
    is_flag=True,
    default=False,
    help="Strip comment lines from the output.",
)
@click.option(
    "--list-stripped",
    is_flag=True,
    default=False,
    help="Print the list of stripped keys to stderr.",
)
def template_command(
    env_file: str,
    output: Optional[str],
    placeholder: str,
    pattern: List[str],
    no_comments: bool,
    list_stripped: bool,
) -> None:
    """Generate a .env.example by replacing secret values with a placeholder."""
    src = Path(env_file)
    parsed = EnvFile.parse(src)

    result = template_env_file(
        parsed,
        placeholder=placeholder,
        extra_secret_patterns=list(pattern) or None,
        keep_comments=not no_comments,
    )

    dest = Path(output) if output else src.with_suffix(".env.example") if src.suffix == ".env" else Path(str(src) + ".example")

    write_env_file(result.entries, dest)
    click.echo(f"Template written to {dest}")

    if list_stripped:
        if result.stripped_keys:
            click.echo("Stripped keys:", err=True)
            for key in result.stripped_keys:
                click.echo(f"  {key}", err=True)
        else:
            click.echo("No secret keys detected.", err=True)

    sys.exit(0)
