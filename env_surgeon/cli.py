"""Entry-point for the env-surgeon CLI."""
import click

from env_surgeon.cli_audit import audit_command
from env_surgeon.cli_diff import diff_command
from env_surgeon.cli_merge import merge_command
from env_surgeon.cli_mask import mask_command
from env_surgeon.cli_snapshot import snapshot_command, snapshot_diff_command
from env_surgeon.cli_report import report_command
from env_surgeon.cli_export import export_command
from env_surgeon.cli_interpolate import interpolate_command


@click.group()
@click.version_option()
def cli() -> None:
    """env-surgeon — audit, merge, diff and manage .env files safely."""


cli.add_command(audit_command, "audit")
cli.add_command(diff_command, "diff")
cli.add_command(merge_command, "merge")
cli.add_command(mask_command, "mask")
cli.add_command(snapshot_command, "snapshot")
cli.add_command(snapshot_diff_command, "snapshot-diff")
cli.add_command(report_command, "report")
cli.add_command(export_command, "export")
cli.add_command(interpolate_command, "interpolate")
