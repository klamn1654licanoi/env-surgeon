"""CLI subcommand: audit — check a .env file for common issues."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from env_surgeon.parser import parse_env_file
from env_surgeon.auditor import audit_env_file


@click.command("audit")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with non-zero status if any warnings are found (not just errors).",
)
@click.option(
    "--min-severity",
    type=click.Choice(["info", "warning", "error"], case_sensitive=False),
    default="info",
    show_default=True,
    help="Minimum severity level to display.",
)
def audit_command(env_file: Path, strict: bool, min_severity: str) -> None:
    """Audit ENV_FILE for duplicate keys, empty values, and naming issues."""
    severity_rank = {"info": 0, "warning": 1, "error": 2}
    min_rank = severity_rank[min_severity.lower()]

    parsed = parse_env_file(env_file)
    result = audit_env_file(parsed)

    visible = [
        issue
        for issue in result.issues
        if severity_rank.get(issue.severity, 0) >= min_rank
    ]

    if not visible:
        click.secho(f"✔  No issues found in {env_file}", fg="green")
        sys.exit(0)

    click.echo(f"Audit results for {env_file}:")
    for issue in visible:
        color = {"error": "red", "warning": "yellow", "info": "cyan"}.get(
            issue.severity, "white"
        )
        click.secho(f"  {issue}", fg=color)

    click.echo()
    click.secho(result.summary(), bold=True)

    if result.has_errors or (strict and result.has_warnings):
        sys.exit(1)
