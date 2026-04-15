"""CLI command for auditing .env files."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from env_surgeon.auditor import AuditSeverity, audit_env_file
from env_surgeon.parser import EnvFile


_SEVERITY_COLORS: dict[str, str] = {
    "ERROR": "red",
    "WARNING": "yellow",
    "INFO": "cyan",
}


def _severity_label(severity: AuditSeverity, *, color: bool) -> str:
    label = severity.name
    if color:
        return click.style(label, fg=_SEVERITY_COLORS.get(label, "white"), bold=True)
    return label


@click.command("audit")
@click.argument("envfile", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable colored output.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any warnings are found (not just errors).",
)
def audit_command(envfile: str, no_color: bool, strict: bool) -> None:
    """Audit ENVFILE for common issues."""
    use_color = not no_color
    path = Path(envfile)

    try:
        env = EnvFile.parse(path)
    except OSError as exc:
        click.echo(f"Error reading file: {exc}", err=True)
        sys.exit(2)

    result = audit_env_file(env)

    if not result.issues:
        ok_msg = "No issues found."
        click.echo(click.style(ok_msg, fg="green") if use_color else ok_msg)
        sys.exit(0)

    for issue in result.issues:
        label = _severity_label(issue.severity, color=use_color)
        line_info = f" (line {issue.line})" if issue.line is not None else ""
        key_info = f" [{issue.key}]" if issue.key else ""
        click.echo(f"{label}{key_info}{line_info}: {issue.message}")

    if result.has_errors() or (strict and result.has_warnings()):
        sys.exit(1)

    sys.exit(0)
