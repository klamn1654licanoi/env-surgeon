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
from env_surgeon.cli_group import group_command
from env_surgeon.cli_promote import promote_command
from env_surgeon.cli_scan import scan_command
from env_surgeon.cli_strip import strip_command
from env_surgeon.cli_rotate import rotate_command


@click.group()
@click.version_option()
def cli() -> None:
    """env-surgeon: audit, merge, and diff .env files."""


cli.add_command(audit_command, "audit")
cli.add_command(diff_command, "diff")
cli.add_command(merge_command, "merge")
cli.add_command(mask_command, "mask")
cli.add_command(snapshot_command, "snapshot")
cli.add_command(snapshot_diff_command, "snapshot-diff")
cli.add_command(report_command, "report")
cli.add_command(export_command, "export")
cli.add_command(interpolate_command, "interpolate")
cli.add_command(lint_command, "lint")
cli.add_command(template_command, "template")
cli.add_command(rename_command, "rename")
cli.add_command(sort_command, "sort")
cli.add_command(dedup_command, "dedup")
cli.add_command(patch_command, "patch")
cli.add_command(profile_command, "profile")
cli.add_command(group_command, "group")
cli.add_command(promote_command, "promote")
cli.add_command(scan_command, "scan")
cli.add_command(strip_command, "strip")
cli.add_command(rotate_command, "rotate")
