"""CLI commands: snapshot and snapshot-diff."""
from __future__ import annotations

from pathlib import Path

import click

from env_surgeon.snapshotter import (
    DEFAULT_SNAPSHOT_DIR,
    diff_against_snapshot,
    load_snapshot,
    take_snapshot,
)


@click.command("snapshot")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--snapshot-dir",
    default=str(DEFAULT_SNAPSHOT_DIR),
    show_default=True,
    help="Directory where snapshots are stored.",
    type=click.Path(path_type=Path),
)
@click.option(
    "--no-mask",
    is_flag=True,
    default=False,
    help="Store raw values without masking secrets (use with care).",
)
def snapshot_command(env_file: Path, snapshot_dir: Path, no_mask: bool) -> None:
    """Take a timestamped snapshot of ENV_FILE."""
    snap = take_snapshot(env_file, snapshot_dir=snapshot_dir, mask_secrets=not no_mask)
    click.echo(f"Snapshot saved: {snap.snapshot_id}  ({len(snap.entries)} keys)")


@click.command("snapshot-diff")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("snapshot_file", type=click.Path(exists=True, path_type=Path))
@click.option("--no-color", is_flag=True, default=False, help="Disable ANSI colours.")
def snapshot_diff_command(
    env_file: Path, snapshot_file: Path, no_color: bool
) -> None:
    """Compare ENV_FILE against a previously saved SNAPSHOT_FILE."""
    try:
        snap = load_snapshot(snapshot_file)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Failed to load snapshot: {exc}") from exc

    result = diff_against_snapshot(env_file, snap)

    if result.is_clean:
        click.echo("No changes since snapshot.")
        raise SystemExit(0)

    green = lambda s: s if no_color else click.style(s, fg="green")
    red = lambda s: s if no_color else click.style(s, fg="red")
    yellow = lambda s: s if no_color else click.style(s, fg="yellow")

    for key in sorted(result.added):
        click.echo(green(f"+ {key}"))
    for key in sorted(result.removed):
        click.echo(red(f"- {key}"))
    for key in sorted(result.changed):
        click.echo(yellow(f"~ {key}"))

    raise SystemExit(1)
