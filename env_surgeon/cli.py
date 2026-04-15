"""Entry-point that groups all env-surgeon sub-commands."""

from __future__ import annotations

import click

from env_surgeon.cli_audit import audit_command
from env_surgeon.cli_diff import diff_command
from env_surgeon.cli_merge import merge_command
from env_surgeon.cli_mask import mask_command


@click.group()
@click.version_option(package_name="env-surgeon")
def cli() -> None:
    """env-surgeon — audit, merge, diff, and mask .env files."""


cli.add_command(audit_command)
cli.add_command(diff_command)
cli.add_command(merge_command)
cli.add_command(mask_command)


if __name__ == "__main__":
    cli()
