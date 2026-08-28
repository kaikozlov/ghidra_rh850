#!/usr/bin/env python3
"""Recover the original GTS+ PE bodies shipped beside the CP-protected copies.

Current GTS+ installs hollow selected PE .text sections and place the protected
payload in a sibling ``.dll._``/``.exe._`` file.  The Toyota installers carried
by the AgentLite distribution also contain an unprotected ``GTSPlus`` group
beside the installed ``GTSPlusCP`` group.  For every protected GTS+ executable
in the 2026.03.002.02 corpus, the same relative path exists in that unprotected
group.

This tool extracts those original binaries without executing Windows code or
emulating the protector.  It preserves the installed GTS+ relative paths and
writes a manifest tying each recovered PE to its CP stub/sidecar provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from techstream_paths import GTSPLUS_EXTERNAL_ROOT, resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_ARCHIVE = GTSPLUS_EXTERNAL_ROOT / "unpacked/gtsplus/gtsplus_msi.7z"
DEFAULT_OUTPUT = REPO / "build/out/gtsplus-unprotected"
INSTALLERS = ("Setup_PF.exe", "Setup_InfoCenter.exe")
CP_PREFIX = "GTSPlusCP\\"
PLAIN_PREFIX = "GTSPlus\\"
SIDECAR_SUFFIXES = (".dll._", ".exe._")


@dataclass(frozen=True)
class CabinetEntry:
    size: int
    path: str


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _require_tool(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise SystemExit(f"required host tool not found in PATH: {name}")
    return found


def _sevenzip() -> str:
    for name in ("7zz", "7z"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("required host tool not found in PATH: 7zz (or 7z)")


def _run(argv: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.PIPE if capture else subprocess.DEVNULL,
    )


def _archive_version(archive: Path, sevenzip: str) -> str:
    listing = _run([sevenzip, "l", "-ba", str(archive)], capture=True).stdout
    versions = {
        match.group(1)
        for line in listing.splitlines()
        if (match := re.search(r"(?:^|\s)([^/\\\s]+)/Setup_PF\.exe$", line))
    }
    if len(versions) != 1:
        raise SystemExit(f"expected exactly one GTS+ Setup_PF.exe release in {archive}, found {sorted(versions)}")
    return next(iter(versions))


def _extract_member(archive: Path, member: str, output: Path, sevenzip: str) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    _run([sevenzip, "e", "-y", str(archive), member, f"-o{output}"])
    path = output / Path(member).name
    if not path.is_file():
        raise RuntimeError(f"7-Zip did not materialize expected member: {member}")
    return path


def _extract_sfx_payload(exe: Path, output: Path, sevenzip: str) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    _run([sevenzip, "e", "-y", str(exe), "[0]", f"-o{output}"])
    path = output / "[0]"
    if not path.is_file():
        raise RuntimeError(f"7-Zip did not expose InstallShield payload [0] from {exe}")
    return path


def _parse_unshield_listing(text: str) -> list[CabinetEntry]:
    rows: list[CabinetEntry] = []
    for line in text.splitlines():
        match = re.match(r"^\s*(\d+)\s+(.+)$", line)
        if match:
            rows.append(CabinetEntry(size=int(match.group(1)), path=match.group(2)))
    return rows


def _carve_main_cabinet(payload: Path, output: Path, unshield: str) -> tuple[Path, list[CabinetEntry]]:
    """Locate the embedded cabinet containing GTSPlus/GTSPlusCP.

    InstallShield's SFX payload concatenates its cabinets with small metadata
    gaps.  Every cabinet starts with ``ISc(``.  unshield ignores trailing bytes,
    so carving each candidate up to the next signature is sufficient and avoids
    pinning release-specific offsets/sizes.
    """
    data = payload.read_bytes()
    positions: list[int] = []
    cursor = 0
    while True:
        cursor = data.find(b"ISc(", cursor)
        if cursor < 0:
            break
        positions.append(cursor)
        cursor += 4
    if len(positions) < 3:
        raise RuntimeError(f"not enough InstallShield cabinet signatures in {payload}: {len(positions)}")

    output.mkdir(parents=True, exist_ok=True)
    for index in range(len(positions) - 2):
        end3 = positions[index + 3] if index + 3 < len(positions) else len(data)
        candidate = output / f"candidate-{index}"
        candidate.mkdir(parents=True, exist_ok=True)
        slices = (
            ("data1.cab", positions[index], positions[index + 1]),
            ("data1.hdr", positions[index + 1], positions[index + 2]),
            ("data2.cab", positions[index + 2], end3),
        )
        for name, start, end in slices:
            (candidate / name).write_bytes(data[start:end])
        result = subprocess.run(
            [unshield, "l", str(candidate / "data1.cab")],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            continue
        entries = _parse_unshield_listing(result.stdout)
        paths = {entry.path.casefold() for entry in entries}
        if any(path.startswith(CP_PREFIX.casefold()) for path in paths) and any(
            path.startswith(PLAIN_PREFIX.casefold()) for path in paths
        ):
            return candidate / "data1.cab", entries
    raise RuntimeError(f"could not locate GTSPlus/GTSPlusCP InstallShield cabinet inside {payload}")


def _protected_twins(entries: list[CabinetEntry]) -> list[tuple[CabinetEntry, CabinetEntry, CabinetEntry]]:
    by_path = {entry.path.casefold(): entry for entry in entries}
    rows: list[tuple[CabinetEntry, CabinetEntry, CabinetEntry]] = []
    for sidecar in entries:
        folded = sidecar.path.casefold()
        if not folded.startswith(CP_PREFIX.casefold()) or not folded.endswith(SIDECAR_SUFFIXES):
            continue
        cp_stub_path = sidecar.path[:-2]
        relative = cp_stub_path[len(CP_PREFIX) :]
        plain_path = PLAIN_PREFIX + relative
        try:
            stub = by_path[cp_stub_path.casefold()]
            plain = by_path[plain_path.casefold()]
        except KeyError as exc:
            raise RuntimeError(f"protected installer entry lacks twin: {sidecar.path}") from exc
        rows.append((sidecar, stub, plain))
    return sorted(rows, key=lambda row: row[2].path.casefold())


def _extract_group(cab: Path, group: str, output: Path, unshield: str) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    _run([unshield, "-g", group, "-d", str(output), "x", str(cab)])
    root = output / group
    if not root.is_dir():
        raise RuntimeError(f"unshield did not materialize expected group {group} from {cab}")
    return root


def _text_shape(path: Path) -> dict[str, int] | None:
    data = path.read_bytes()
    if len(data) < 0x100 or data[:2] != b"MZ":
        return None
    peoff = struct.unpack_from("<I", data, 0x3C)[0]
    if peoff + 24 > len(data) or data[peoff : peoff + 4] != b"PE\0\0":
        return None
    count = struct.unpack_from("<H", data, peoff + 6)[0]
    optional_size = struct.unpack_from("<H", data, peoff + 20)[0]
    section = peoff + 24 + optional_size
    for index in range(count):
        off = section + 40 * index
        if off + 40 > len(data):
            return None
        name = data[off : off + 8].split(b"\0", 1)[0]
        if name == b".text":
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", data, off + 8)
            return {
                "virtual_size": virtual_size,
                "virtual_address": virtual_address,
                "raw_size": raw_size,
                "raw_offset": raw_offset,
            }
    return None


def _installed_sidecars(installed_root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in installed_root.rglob("*._"):
        if not path.is_file() or not path.name.casefold().endswith(SIDECAR_SUFFIXES):
            continue
        base = Path(str(path)[:-2])
        relative = base.relative_to(installed_root).as_posix()
        result[relative.casefold()] = path
    return result


def recover(
    archive: Path = DEFAULT_ARCHIVE,
    output: Path = DEFAULT_OUTPUT,
    installed_root: Path | None = None,
    *,
    keep_workspace: bool = False,
) -> dict:
    archive = archive.expanduser().resolve()
    output = output.expanduser().resolve()
    installed_root = (installed_root or resolve_gts_root()).expanduser().resolve()
    if not archive.is_file():
        raise SystemExit(f"missing GTS+ installer archive: {archive}")
    if not installed_root.is_dir():
        raise SystemExit(f"missing installed GTS+ root: {installed_root}")

    sevenzip = _sevenzip()
    unshield = _require_tool("unshield")
    version = _archive_version(archive, sevenzip)
    output.mkdir(parents=True, exist_ok=True)

    workspace_owner: tempfile.TemporaryDirectory[str] | None = None
    if keep_workspace:
        workspace = REPO / "build/tmp/gtsplus-body-recovery"
        shutil.rmtree(workspace, ignore_errors=True)
        workspace.mkdir(parents=True)
    else:
        workspace_owner = tempfile.TemporaryDirectory(prefix="gtsplus-body-recovery-")
        workspace = Path(workspace_owner.name)

    recovered: dict[str, dict] = {}
    installer_summaries: list[dict] = []
    try:
        for installer in INSTALLERS:
            installer_dir = workspace / installer.removesuffix(".exe")
            exe = _extract_member(archive, f"{version}/{installer}", installer_dir, sevenzip)
            payload = _extract_sfx_payload(exe, installer_dir / "sfx", sevenzip)
            cab, entries = _carve_main_cabinet(payload, installer_dir / "cabs", unshield)
            twins = _protected_twins(entries)
            if not twins:
                raise RuntimeError(f"{installer}: cabinet had no GTSPlusCP protected twins")
            plain_root = _extract_group(cab, "GTSPlus", installer_dir / "plain", unshield)
            cp_root = _extract_group(cab, "GTSPlusCP", installer_dir / "cp", unshield)

            installer_summaries.append(
                {
                    "installer": installer,
                    "protected_body_count": len(twins),
                    "all_have_plaintext_twins": True,
                }
            )
            for side_entry, stub_entry, plain_entry in twins:
                relative = plain_entry.path[len(PLAIN_PREFIX) :].replace("\\", "/")
                key = relative.casefold()
                source_plain = plain_root.joinpath(*relative.split("/"))
                source_stub = cp_root.joinpath(*relative.split("/"))
                source_side = Path(str(source_stub) + "._")
                if not source_plain.is_file() or not source_stub.is_file() or not source_side.is_file():
                    raise RuntimeError(f"{installer}: extracted protected/plain triplet incomplete for {relative}")
                destination = output.joinpath(*relative.split("/"))
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_plain, destination)

                installed_stub = installed_root.joinpath(*relative.split("/"))
                installed_side = Path(str(installed_stub) + "._")
                if not installed_stub.is_file() or not installed_side.is_file():
                    raise RuntimeError(f"installed protected GTS+ pair missing for {relative}")
                cp_stub_hash = _sha256(source_stub)
                cp_side_hash = _sha256(source_side)
                installed_stub_hash = _sha256(installed_stub)
                installed_side_hash = _sha256(installed_side)
                if cp_stub_hash != installed_stub_hash or cp_side_hash != installed_side_hash:
                    raise RuntimeError(f"installed protected pair differs from {installer} GTSPlusCP payload: {relative}")

                protected_text = _text_shape(installed_stub)
                recovered_text = _text_shape(destination)
                if recovered_text is None:
                    raise RuntimeError(f"recovered plaintext twin is not a parseable PE with .text: {relative}")
                # Native CP images are typically obvious hollow PEs (tiny raw
                # .text, huge virtual .text).  Managed assemblies can instead
                # gain a larger protector-loader .text than their original CLR
                # image, so section-size growth is evidence worth recording,
                # not a format-independent validity requirement.
                native_text_expanded = bool(
                    protected_text is not None
                    and recovered_text["raw_size"] > protected_text["raw_size"]
                )

                if key in recovered:
                    raise RuntimeError(f"duplicate recovered GTS+ relative path across installers: {relative}")
                recovered[key] = {
                    "path": relative,
                    "installer": installer,
                    "plaintext": {
                        "size": destination.stat().st_size,
                        "sha256": _sha256(destination),
                        "text": recovered_text,
                        "native_text_expanded_vs_cp": native_text_expanded,
                    },
                    "protected": {
                        "stub_size": installed_stub.stat().st_size,
                        "stub_sha256": installed_stub_hash,
                        "sidecar_size": installed_side.stat().st_size,
                        "sidecar_sha256": installed_side_hash,
                        "text": protected_text,
                    },
                    "package_identity": {
                        "cp_stub_matches_installed": True,
                        "cp_sidecar_matches_installed": True,
                        "listed_stub_size": stub_entry.size,
                        "listed_sidecar_size": side_entry.size,
                        "listed_plaintext_size": plain_entry.size,
                    },
                }

        installed = _installed_sidecars(installed_root)
        missing = sorted(path for path in installed if path not in recovered)
        extra = sorted(path for path in recovered if path not in installed)
        if missing or extra:
            raise RuntimeError(
                "recovery/install coverage mismatch: "
                f"missing={missing[:20]} extra={extra[:20]} "
                f"(installed={len(installed)} recovered={len(recovered)})"
            )

        rows = [recovered[key] for key in sorted(recovered)]
        manifest = {
            "schema": "gtsplus-unprotected-body-recovery-v1",
            "gtsplus_version": version,
            "source_archive": str(archive),
            "source_archive_sha256": _sha256(archive),
            "installed_root": str(installed_root),
            "output_root": str(output),
            "method": (
                "extract the Toyota installer GTSPlus group paired with GTSPlusCP; "
                "no runtime decryption/emulation is required"
            ),
            "installers": installer_summaries,
            "installed_protected_body_count": len(installed),
            "recovered_plaintext_body_count": len(rows),
            "coverage_complete": True,
            "binaries": rows,
        }
        manifest_path = output / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return manifest
    finally:
        if workspace_owner is not None:
            workspace_owner.cleanup()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE, help="gtsplus_msi.7z archive")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="recovered plaintext output root")
    parser.add_argument("--installed-root", type=Path, help="installed GTSPlus root used to prove CP identity/coverage")
    parser.add_argument("--keep-workspace", action="store_true", help="keep carved installer workspace under build/tmp")
    parser.add_argument("--json", action="store_true", help="print the recovery manifest JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = recover(args.archive, args.output, args.installed_root, keep_workspace=args.keep_workspace)
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"GTS+ {manifest['gtsplus_version']}: recovered {manifest['recovered_plaintext_body_count']} plaintext bodies")
        print(f"coverage: {manifest['recovered_plaintext_body_count']}/{manifest['installed_protected_body_count']} protected GTS+ files")
        print(f"output: {manifest['output_root']}")
        print(f"manifest: {Path(manifest['output_root']) / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
