"""CLI command: env-surgeon scan."""
from __future__ import annotations

from pathlib import Path

import click

from .scanner import scan_directory


@click.command("scan")
@click.argument("root", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--max-depth", default=5, show_default=True, help="Directory recursion limit.")
@click.option("--include-hidden/--skip-hidden", default=False, show_default=True,
              help="Include hidden directories in the walk.")
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
def scan_command(root: str, max_depth: int, include_hidden: bool, as_json: bool) -> None:
    """Discover .env files under ROOT."""
    result = scan_directory(
        Path(root),
        max_depth=max_depth,
        skip_hidden_dirs=not include_hidden,
    )

    if as_json:
        import json
        data = {
            "root": str(result.root),
            "found": [str(p) for p in result.found],
            "skipped": [str(p) for p in result.skipped],
        }
        click.echo(json.dumps(data, indent=2))
        raise SystemExit(0 if not result.is_empty() else 1)

    if result.is_empty():
        click.echo(click.style("No .env files found.", fg="yellow"))
        raise SystemExit(1)

    click.echo(click.style(f"Found {result.file_count()} .env file(s) under {result.root}:", bold=True))
    for p in result.found:
        click.echo(f"  {click.style('+', fg='green')} {p}")
    if result.skipped:
        click.echo(click.style(f"  ({len(result.skipped)} empty file(s) skipped)", fg="yellow"))
    raise SystemExit(0)
