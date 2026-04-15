"""CLI command: env-surgeon lint — report style and correctness issues."""
from __future__ import annotations

import sys
import click

from env_surgeon.linter import LintSeverity, lint_env_file
from env_surgeon.parser import EnvFile

_COLORS = {
    LintSeverity.ERROR: "red",
    LintSeverity.WARNING: "yellow",
    LintSeverity.INFO: "cyan",
}


def _severity_label(severity: LintSeverity, no_color: bool) -> str:
    label = severity.value.upper().ljust(7)
    if no_color:
        return label
    return click.style(label, fg=_COLORS[severity], bold=severity == LintSeverity.ERROR)


@click.command("lint")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--no-color", is_flag=True, default=False, help="Disable coloured output.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on warnings too.")
def lint_command(files: tuple[str, ...], no_color: bool, strict: bool) -> None:
    """Lint one or more .env FILES for style and correctness issues."""
    any_error = False
    any_warning = False

    for path in files:
        try:
            env_file = EnvFile.parse(path)
        except OSError as exc:
            click.echo(f"ERROR  could not read {path}: {exc}", err=True)
            sys.exit(2)

        result = lint_env_file(env_file)

        if result.is_clean:
            click.echo(f"{path}: {click.style('ok', fg='green') if not no_color else 'ok'}")
            continue

        click.echo(f"{path}:")
        for v in result.violations:
            label = _severity_label(v.severity, no_color)
            loc = f"line {v.line}" + (f" [{v.key}]" if v.key else "")
            click.echo(f"  {label} {loc}: {v.message}")

        if result.has_errors:
            any_error = True
        if any(v.severity == LintSeverity.WARNING for v in result.violations):
            any_warning = True

    if any_error:
        sys.exit(1)
    if strict and any_warning:
        sys.exit(1)
