"""CLI command: strip comments and blank lines from a .env file."""
from __future__ import annotations
import click
from env_surgeon.parser import parse_env_file
from env_surgeon.stripper import strip_env_file, is_clean
from env_surgeon.formatter import format_entries, write_env_file


@click.command("strip")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--no-comments", "strip_comments", is_flag=True, default=True, show_default=True, help="Remove comment lines.")
@click.option("--no-blanks", "strip_blanks", is_flag=True, default=True, show_default=True, help="Remove blank lines.")
@click.option("--in-place", is_flag=True, default=False, help="Overwrite the input file.")
@click.option("--check", is_flag=True, default=False, help="Exit 1 if file would change.")
def strip_command(
    env_file: str,
    strip_comments: bool,
    strip_blanks: bool,
    in_place: bool,
    check: bool,
) -> None:
    """Strip comments and/or blank lines from ENV_FILE."""
    parsed = parse_env_file(env_file)
    result = strip_env_file(parsed, strip_comments=strip_comments, strip_blanks=strip_blanks)

    if check:
        if not is_clean(result):
            click.echo(
                f"{env_file}: would remove {result.removed_comments} comment(s) "
                f"and {result.removed_blanks} blank line(s)."
            )
            raise SystemExit(1)
        click.echo(f"{env_file}: already clean.")
        return

    output = format_entries(result.entries)

    if in_place:
        write_env_file(env_file, result.entries)
        click.echo(
            f"{env_file}: removed {result.removed_comments} comment(s) "
            f"and {result.removed_blanks} blank line(s)."
        )
    else:
        click.echo(output, nl=False)
