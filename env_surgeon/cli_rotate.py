"""CLI command: env-surgeon rotate"""
from __future__ import annotations

import click

from env_surgeon.parser import parse_env_file
from env_surgeon.rotator import rotate_env_file, is_clean
from env_surgeon.formatter import write_env_file


@click.command("rotate")
@click.argument("envfile", type=click.Path(exists=True))
@click.option("-k", "--key", "keys", multiple=True, required=True, help="Key(s) to rotate.")
@click.option("-r", "--replace", "replacements", multiple=True, metavar="KEY=VALUE",
              help="Explicit replacement in KEY=VALUE form.")
@click.option("--length", default=32, show_default=True, help="Generated secret length.")
@click.option("--in-place", is_flag=True, help="Overwrite the source file.")
@click.option("--output", "output", default=None, type=click.Path(), help="Write result here.")
@click.option("--strict", is_flag=True, help="Exit 1 if any key was not found.")
def rotate_command(
    envfile: str,
    keys: tuple,
    replacements: tuple,
    length: int,
    in_place: bool,
    output: str | None,
    strict: bool,
) -> None:
    """Rotate secret values for KEY(s) in ENVFILE."""
    parsed_replacements: dict[str, str] = {}
    for item in replacements:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item}")
        k, v = item.split("=", 1)
        parsed_replacements[k.strip()] = v.strip()

    env = parse_env_file(envfile)
    result = rotate_env_file(env, list(keys), parsed_replacements, length)

    if result.not_found:
        click.echo(f"[warn] keys not found: {', '.join(result.not_found)}", err=True)

    if result.rotated:
        click.echo(f"[info] rotated: {', '.join(result.rotated)}")

    dest = envfile if in_place else output
    if dest:
        write_env_file(result.entries, dest)
        click.echo(f"[info] written to {dest}")
    else:
        for entry in result.entries:
            click.echo(entry.raw)

    if strict and not is_clean(result):
        raise SystemExit(1)
