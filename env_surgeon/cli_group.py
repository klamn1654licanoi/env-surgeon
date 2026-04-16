"""CLI command: group — display .env entries organised by key prefix."""
from __future__ import annotations
import click
from env_surgeon.parser import parse_env_file
from env_surgeon.grouper import group_env_file


@click.command("group")
@click.argument("envfile", type=click.Path(exists=True))
@click.option(
    "--prefix", "-p", multiple=True,
    help="Only show these prefixes (repeatable). Default: all.",
)
@click.option(
    "--sep", default="_", show_default=True,
    help="Separator used to detect prefixes.",
)
@click.option(
    "--show-ungrouped", is_flag=True, default=False,
    help="Also print entries that have no matching prefix.",
)
def group_command(envfile: str, prefix: tuple, sep: str, show_ungrouped: bool) -> None:
    """Show .env keys organised by prefix."""
    env = parse_env_file(envfile)
    prefixes = list(prefix) if prefix else None
    result = group_env_file(env, prefixes=prefixes, sep=sep)

    if not result.groups and not result.ungrouped:
        click.echo("No entries found.")
        raise SystemExit(0)

    for name in result.group_names():
        click.echo(click.style(f"[{name}]", fg="cyan", bold=True))
        for entry in result.groups[name]:
            click.echo(f"  {entry.key}={entry.value}")
        click.echo()

    if show_ungrouped and result.ungrouped:
        click.echo(click.style("[ungrouped]", fg="yellow", bold=True))
        for entry in result.ungrouped:
            if entry.key is not None:
                click.echo(f"  {entry.key}={entry.value}")
            else:
                click.echo(f"  {entry.raw}")
        click.echo()

    if not result.is_clean():
        ungrouped_count = len(result.ungrouped)
        hint = " Use --show-ungrouped to display them." if not show_ungrouped else ""
        click.echo(
            click.style(
                f"{ungrouped_count} ungrouped entry/entries.{hint}",
                fg="yellow",
            ),
            err=True,
        )
    raise SystemExit(0)
