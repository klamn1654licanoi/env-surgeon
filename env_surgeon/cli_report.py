"""CLI command to generate a combined HTML or text report of audit + diff results."""
from __future__ import annotations

import datetime
from pathlib import Path

import click

from env_surgeon.parser import EnvFile
from env_surgeon.auditor import audit_env_file
from env_surgeon.differ import diff_env_files, format_diff
from env_surgeon.masker import mask_env_file


def _severity_icon(severity: str) -> str:
    return {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(severity, "•")


def _render_text_report(
    paths: list[Path],
    audit_results: list,
    diff_blocks: list[str],
    mask: bool,
) -> str:
    lines: list[str] = []
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines.append(f"env-surgeon report  [{ts}]")
    lines.append("=" * 60)

    lines.append("\n── AUDIT ──")
    for path, result in zip(paths, audit_results):
        lines.append(f"\n  {path}")
        if not result.issues:
            lines.append("    ✅  No issues found.")
        for issue in result.issues:
            icon = _severity_icon(issue.severity)
            lines.append(f"    {icon}  [{issue.severity.upper()}] {issue.key}: {issue.message}")

    if diff_blocks:
        lines.append("\n── DIFF ──")
        for block in diff_blocks:
            lines.append(block)

    if mask:
        lines.append("\n  (secret values were masked in this report)")

    return "\n".join(lines)


@click.command("report")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Write report to this file instead of stdout.")
@click.option("--mask/--no-mask", default=True, show_default=True, help="Mask secret values.")
@click.option("--no-color", is_flag=True, default=False, help="Strip ANSI colour codes.")
def report_command(files: tuple[str, ...], output: str | None, mask: bool, no_color: bool) -> None:
    """Audit every FILE and diff consecutive pairs, then emit a combined report."""
    paths = [Path(f) for f in files]
    env_files: list[EnvFile] = []
    for p in paths:
        ef = EnvFile.parse(p)
        if mask:
            ef = mask_env_file(ef).masked_file
        env_files.append(ef)

    audit_results = [audit_env_file(ef) for ef in env_files]

    diff_blocks: list[str] = []
    for left, right in zip(env_files, env_files[1:]):
        result = diff_env_files(left, right)
        block = format_diff(result, use_color=not no_color)
        diff_blocks.append(f"  {left.path}  ↔  {right.path}\n{block}")

    report = _render_text_report(paths, audit_results, diff_blocks, mask)

    if output:
        Path(output).write_text(report, encoding="utf-8")
        click.echo(f"Report written to {output}")
    else:
        click.echo(report)

    has_errors = any(r.has_errors() for r in audit_results)
    raise SystemExit(1 if has_errors else 0)
