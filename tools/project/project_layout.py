#!/usr/bin/env python3
"""Convert between committed snapshot names and a live Ghidra project layout.

Committed snapshots deliberately use ``.gpr.snapshot`` / ``.rep.snapshot`` so
raw Ghidra cannot open and compact ``project/``. Working copies use normal
``.gpr`` / ``.rep`` names under ``build/work/project``.
"""
from __future__ import annotations

import argparse
import getpass
import shutil
import socket
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_PROJECT_NAME = "rh850_p1me_mapped"
TRANSIENT_SUFFIXES = (".lock", ".lock~")
CHECKOUT_FILE = "checkout.dat"
PORTABLE_CHECKOUT_FILE = "checkout.dat.snapshot"


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




def _read_checkout_xml(path: Path) -> ET.Element:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as error:
        raise ValueError(f"invalid Ghidra checkout metadata {path}: {error}") from error
    if root.tag != "CHECKOUT_LIST":
        raise ValueError(f"unexpected checkout metadata root in {path}: {root.tag}")
    for entry in root:
        if entry.tag != "CHECKOUT":
            raise ValueError(f"unexpected checkout metadata entry in {path}: {entry.tag}")
        for required in ("ID", "VERSION", "EXCLUSIVE"):
            if required not in entry.attrib:
                raise ValueError(f"checkout metadata {path} missing {required}")
    return root


def _write_checkout_xml(path: Path, root: ET.Element) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n")


def _portable_checkout(root: ET.Element) -> ET.Element:
    portable = ET.Element("CHECKOUT_LIST")
    if "NEXT_ID" in root.attrib:
        portable.set("NEXT_ID", root.attrib["NEXT_ID"])
    for entry in root.findall("CHECKOUT"):
        out = ET.SubElement(portable, "CHECKOUT")
        for key in ("ID", "VERSION", "EXCLUSIVE"):
            out.set(key, entry.attrib[key])
    return portable


def _materialized_checkout(root: ET.Element, project_dir: Path, project_name: str) -> ET.Element:
    live = ET.Element("CHECKOUT_LIST")
    if "NEXT_ID" in root.attrib:
        live.set("NEXT_ID", root.attrib["NEXT_ID"])
    identity = f"{socket.gethostname()}::{project_dir / project_name}"
    now = str(int(time.time() * 1000))
    user = getpass.getuser()
    for entry in root.findall("CHECKOUT"):
        out = ET.SubElement(live, "CHECKOUT")
        out.set("ID", entry.attrib["ID"])
        out.set("USER", user)
        out.set("VERSION", entry.attrib["VERSION"])
        out.set("TIME", now)
        out.set("PROJECT", identity)
        out.set("EXCLUSIVE", entry.attrib["EXCLUSIVE"])
    return live


def _snapshot_checkout_metadata(project_dir: Path, snapshot_dir: Path, project_name: str) -> None:
    live_rep = project_dir / f"{project_name}.rep"
    packed_rep = snapshot_dir / f"{project_name}.rep.snapshot"
    for source in live_rep.rglob(CHECKOUT_FILE):
        relative = source.relative_to(live_rep)
        target = packed_rep / relative.parent / PORTABLE_CHECKOUT_FILE
        _write_checkout_xml(target, _portable_checkout(_read_checkout_xml(source)))


def _restore_checkout_metadata(project_dir: Path, project_name: str) -> None:
    live_rep = project_dir / f"{project_name}.rep"
    for portable in list(live_rep.rglob(PORTABLE_CHECKOUT_FILE)):
        root = _read_checkout_xml(portable)
        checkout = portable.with_name(CHECKOUT_FILE)
        _write_checkout_xml(checkout, _materialized_checkout(root, project_dir, project_name))
        portable.unlink()


def _validate_portable_checkouts(snapshot_dir: Path, project_name: str) -> None:
    rep = snapshot_dir / f"{project_name}.rep.snapshot"
    live = list(rep.rglob(CHECKOUT_FILE))
    if live:
        raise ValueError(f"snapshot contains machine-specific Ghidra checkout metadata: {live[0]}")
    for portable in rep.rglob(PORTABLE_CHECKOUT_FILE):
        root = _read_checkout_xml(portable)
        for entry in root.findall("CHECKOUT"):
            forbidden = {"USER", "TIME", "PROJECT"} & set(entry.attrib)
            if forbidden:
                raise ValueError(
                    f"portable checkout metadata contains machine-specific fields {sorted(forbidden)}: {portable}"
                )

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
    _validate_portable_checkouts(snapshot_dir, project_name)


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
    _restore_checkout_metadata(project_dir, project_name)


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
    _snapshot_checkout_metadata(project_dir, snapshot_dir, project_name)
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
