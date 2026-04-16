"""CLI command: env-surgeon profile"""
from __future__ import annotations
import click
from env_surgeon.parser import EnvFile
from env_surgeon.profiler import profile_env_file


@click.command("profile")
@click.argument("envfile", type=click.Path(exists=True))
@click.option("--extra-pattern", "extra_patterns", multiple=True, help="Extra secret key patterns (regex).")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def profile_command(envfile: str, extra_patterns: tuple, as_json: bool) -> None:
    """Show a statistical profile of an .env file."""
    env = EnvFile.parse(envfile)
    result = profile_env_file(env, extra_patterns=list(extra_patterns) or None)

    if as_json:
        import json
        click.echo(json.dumps({
            "path": result.path,
            "key_count": result.key_count,
            "secret_count": result.secret_count,
            "empty_count": result.empty_count,
            "comment_lines": result.comment_lines,
            "blank_lines": result.blank_lines,
            "secret_keys": result.secret_keys,
            "empty_value_keys": result.empty_value_keys,
        }, indent=2))
        return

    click.echo(f"Profile: {result.path}")
    click.echo(f"  Keys          : {result.key_count}")
    click.echo(f"  Secret keys   : {result.secret_count}")
    click.echo(f"  Empty values  : {result.empty_count}")
    click.echo(f"  Comment lines : {result.comment_lines}")
    click.echo(f"  Blank lines   : {result.blank_lines}")
    if result.secret_keys:
        click.echo("  Secret key names: " + ", ".join(result.secret_keys))
    if result.empty_value_keys:
        click.echo("  Empty value keys: " + ", ".join(result.empty_value_keys))
