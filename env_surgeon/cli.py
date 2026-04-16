"""env-surgeon CLI entry point."""
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
from env_surgeon.cli_template import template_command
from env_surgeon.cli_rename import rename_command
from env_surgeon.cli_sort import sort_command
from env_surgeon.cli_dedup import dedup_command
from env_surgeon.cli_patch import patch_command
from env_surgeon.cli_profile import profile_command


@click.group()
def cli() -> None:
    """env-surgeon: audit, merge, and diff .env files."""


cli.add_command(audit_command)
cli.add_command(diff_command)
cli.add_command(merge_command)
cli.add_command(mask_command)
cli.add_command(snapshot_command)
cli.add_command(snapshot_diff_command)
cli.add_command(report_command)
cli.add_command(export_command)
cli.add_command(interpolate_command)
cli.add_command(lint_command)
cli.add_command(template_command)
cli.add_command(rename_command)
cli.add_command(sort_command)
cli.add_command(dedup_command)
cli.add_command(patch_command)
cli.add_command(profile_command)
