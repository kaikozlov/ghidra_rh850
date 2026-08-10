#!/usr/bin/env python3
"""Convert between committed snapshot names and a live Ghidra project layout.

Committed snapshots deliberately use ``.gpr.snapshot`` / ``.rep.snapshot`` so
raw Ghidra cannot open and compact ``project/``. Working copies use normal
``.gpr`` / ``.rep`` names under ``build/project``.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

DEFAULT_PROJECT_NAME = "rh850_p1me_mapped"
TRANSIENT_SUFFIXES = (".lock", ".lock~")


def resolved(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def require_distinct(source: Path, destination: Path) -> None:
    source_resolved = resolved(source)
    destination_resolved = resolved(destination)
    if source_resolved == destination_resolved:
        raise ValueError(f"source and destination must differ: {source}")
    if source_resolved in destination_resolved.parents or destination_resolved in source_resolved.parents:
        raise ValueError(
            f"source and destination must not be nested: {source_resolved} / {destination_resolved}"
        )


def transient(path: Path) -> bool:
    name = path.name
    return (
        name == ".git"
        or name == "checkout.dat"
        or name.startswith("tmp")
        or "~journal" in name
        or name.endswith(TRANSIENT_SUFFIXES)
    )


def reject_symlinks(root: Path) -> None:
    if root.is_symlink():
        raise ValueError(f"project layout root must not be a symlink: {root}")
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"project layout must not contain symlinks: {path}")


def copy_tree(source: Path, destination: Path, renames: dict[str, str]) -> None:
    reject_symlinks(source)
    if destination.exists() or destination.is_symlink():
        reject_symlinks(destination)
        if any(destination.iterdir()):
            raise ValueError(f"destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    for item in sorted(source.iterdir(), key=lambda p: p.name):
        if transient(item):
            continue
        target = destination / renames.get(item.name, item.name)
        if item.is_dir():
            shutil.copytree(
                item,
                target,
                symlinks=False,
                ignore=lambda _dir, names: [name for name in names if transient(Path(name))],
            )
        else:
            shutil.copy2(item, target, follow_symlinks=False)


def validate_snapshot(snapshot_dir: Path, project_name: str) -> None:
    reject_symlinks(snapshot_dir)
    gpr_snapshot = snapshot_dir / f"{project_name}.gpr.snapshot"
    rep_snapshot = snapshot_dir / f"{project_name}.rep.snapshot"
    live_gpr = snapshot_dir / f"{project_name}.gpr"
    live_rep = snapshot_dir / f"{project_name}.rep"

    if live_gpr.exists() or live_rep.exists():
        raise ValueError(
            f"committed snapshot contains live Ghidra project names: "
            f"{live_gpr.name} / {live_rep.name}"
        )
    if not gpr_snapshot.is_file():
        raise ValueError(f"missing snapshot project file: {gpr_snapshot}")
    if not rep_snapshot.is_dir():
        raise ValueError(f"missing snapshot repository: {rep_snapshot}")


def materialize(snapshot_dir: Path, project_dir: Path, project_name: str) -> None:
    require_distinct(snapshot_dir, project_dir)
    validate_snapshot(snapshot_dir, project_name)
    copy_tree(
        snapshot_dir,
        project_dir,
        {
            f"{project_name}.gpr.snapshot": f"{project_name}.gpr",
            f"{project_name}.rep.snapshot": f"{project_name}.rep",
        },
    )


def pack(project_dir: Path, snapshot_dir: Path, project_name: str) -> None:
    require_distinct(project_dir, snapshot_dir)
    live_gpr = project_dir / f"{project_name}.gpr"
    live_rep = project_dir / f"{project_name}.rep"
    if not live_gpr.is_file():
        raise ValueError(f"missing live project file: {live_gpr}")
    if not live_rep.is_dir():
        raise ValueError(f"missing live project repository: {live_rep}")
    copy_tree(
        project_dir,
        snapshot_dir,
        {
            f"{project_name}.gpr": f"{project_name}.gpr.snapshot",
            f"{project_name}.rep": f"{project_name}.rep.snapshot",
        },
    )
    validate_snapshot(snapshot_dir, project_name)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)

    materialize_parser = sub.add_parser("materialize")
    materialize_parser.add_argument("--snapshot-dir", type=Path, required=True)
    materialize_parser.add_argument("--project-dir", type=Path, required=True)
    materialize_parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)

    pack_parser = sub.add_parser("pack")
    pack_parser.add_argument("--project-dir", type=Path, required=True)
    pack_parser.add_argument("--snapshot-dir", type=Path, required=True)
    pack_parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)

    validate_parser = sub.add_parser("validate-snapshot")
    validate_parser.add_argument("--snapshot-dir", type=Path, required=True)
    validate_parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "materialize":
            materialize(args.snapshot_dir, args.project_dir, args.project_name)
        elif args.command == "pack":
            pack(args.project_dir, args.snapshot_dir, args.project_name)
        else:
            validate_snapshot(args.snapshot_dir, args.project_name)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
