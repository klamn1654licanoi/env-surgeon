"""Entry-point for the env-surgeon CLI."""
import click

from env_surgeon.cli_audit import audit_command
from env_surgeon.cli_diff import diff_command
from env_surgeon.cli_mask import mask_command
from env_surgeon.cli_merge import merge_command
from env_surgeon.cli_snapshot import snapshot_command, snapshot_diff_command


@click.group()
@click.version_option(package_name="env-surgeon")
def cli() -> None:
    """env-surgeon — audit, merge, diff, and snapshot .env files."""


cli.add_command(audit_command, name="audit")
cli.add_command(diff_command, name="diff")
cli.add_command(merge_command, name="merge")
cli.add_command(mask_command, name="mask")
cli.add_command(snapshot_command, name="snapshot")
cli.add_command(snapshot_diff_command, name="snapshot-diff")
