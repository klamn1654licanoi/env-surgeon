"""CLI sub-command: interpolate — resolve variable references in a .env file."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import click

from env_surgeon.parser import EnvFile
from env_surgeon.interpolator import interpolate_env_file


@click.command("interpolate")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--base",
    "base_pairs",
    multiple=True,
    metavar="KEY=VALUE",
    help="Extra KEY=VALUE pairs available as interpolation sources.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any references remain unresolved.",
)
@click.option("--no-color", is_flag=True, default=False, help="Disable ANSI colours.")
def interpolate_command(
    env_file: Path,
    base_pairs: List[str],
    strict: bool,
    no_color: bool,
) -> None:
    """Resolve \${VAR} / $VAR references inside ENV_FILE and print the result."""
    parsed = EnvFile.parse(env_file)

    base: dict[str, str] = {}
    for pair in base_pairs:
        if "=" not in pair:
            click.echo(f"Invalid --base value (expected KEY=VALUE): {pair}", err=True)
            sys.exit(2)
        k, _, v = pair.partition("=")
        base[k.strip()] = v.strip()

    result = interpolate_env_file(parsed, base=base)

    green = "" if no_color else "\033[32m"
    yellow = "" if no_color else "\033[33m"
    reset = "" if no_color else "\033[0m"

    for key, value in result.resolved.items():
        if key in result.unresolved_keys:
            click.echo(f"{yellow}{key}={value}{reset}  # unresolved")
        elif key in result.cycles:
            click.echo(f"{yellow}{key}={value}{reset}  # cycle")
        else:
            click.echo(f"{green}{key}={value}{reset}")

    if result.unresolved_keys:
        click.echo(
            f"\n{yellow}Warning:{reset} {len(result.unresolved_keys)} unresolved "
            "reference(s): " + ", ".join(result.unresolved_keys),
            err=True,
        )

    if result.cycles:
        click.echo(
            f"\n{yellow}Warning:{reset} {len(result.cycles)} cycle(s) detected: "
            + ", ".join(result.cycles),
            err=True,
        )

    if strict and not result.is_clean:
        sys.exit(1)
