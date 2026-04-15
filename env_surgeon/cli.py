"""Entry point for the env-surgeon CLI."""
from __future__ import annotations

import click

from env_surgeon.cli_audit import audit_command
from env_surgeon.cli_diff import diff_command
from env_surgeon.cli_merge import merge_command
from env_surgeon.cli_mask import mask_command
from env_surgeon.cli_snapshot import snapshot_command, snapshot_diff_command
from env_surgeon.cli_report import report_command
from env_surgeon.cli_export import export_command
from env_surgeon.cli_interpolate import interpolate_command
from env_surgeon.cli_lint import lint_command


@click.group()
@click.version_option(package_name="env-surgeon")
def cli() -> None:
    """env-surgeon — audit, merge, and diff .env files safely."""


cli.add_command(audit_command)
cli.add_command(diff_command)
cli.add_command(merge_command)
cli.add_command(mask_command)
cli.add_command(snapshot_command, name="snapshot")
cli.add_command(snapshot_diff_command, name="snapshot-diff")
cli.add_command(report_command)
cli.add_command(export_command)
cli.add_command(interpolate_command)
cli.add_command(lint_command)
