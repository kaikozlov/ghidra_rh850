#!/usr/bin/env python3
"""Optional checks against pinned public upstream repositories.

The core ``make verify`` target never imports this module and requires no
external checkout. Run this suite explicitly with ``make verify-external``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOCK_PATH = REPO / "external-references.lock.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repos-dir",
        type=Path,
        default=REPO.parent,
        help="directory containing checkouts named as in external-references.lock.json",
    )
    args = parser.parse_args()
    refs_dir = args.repos_dir.expanduser().resolve()
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))

    print("== pinned external repositories ==")
    roots: dict[str, Path] = {}
    for name, metadata in lock["repositories"].items():
        root = refs_dir / metadata["directory"]
        roots[name] = root
        check(f"{name} checkout exists", root.is_dir(), str(root))
        if root.is_dir():
            try:
                head = git_head(root)
            except (OSError, subprocess.CalledProcessError) as error:
                check(f"{name} is a Git checkout", False, str(error))
            else:
                check(f"{name} commit is pinned", head == metadata["commit"], head)

    if any(not root.is_dir() for root in roots.values()):
        print(f"\n== RESULT: {passed} passed, {failed} failed ==")
        return 1

    print("\n== pinned artifacts and local fixtures ==")
    for artifact in lock["artifacts"]:
        root = roots[artifact["repository"]]
        path = root / artifact["path"]
        label = f"{artifact['repository']}:{artifact['path']}"
        check(f"{label} exists", path.is_file(), str(path))
        if not path.is_file():
            continue
        if "size" in artifact:
            check(f"{label} size", path.stat().st_size == artifact["size"], str(path.stat().st_size))
        digest = sha256(path)
        check(f"{label} SHA-256", digest == artifact["sha256"], digest)
        fixture_name = artifact.get("fixture")
        if fixture_name:
            fixture = REPO / fixture_name
            check(f"{label} fixture exists", fixture.is_file(), str(fixture))
            if fixture.is_file():
                check(f"{label} equals committed fixture", path.read_bytes() == fixture.read_bytes())

    print("\n== original combined image reconstruction ==")
    combined = roots["rh850_p1me_original"] / "RH850_P1M-E_Firmware.bin"
    split = (
        (REPO / "firmware" / "RH850_P1M-E_DataFlash.bin").read_bytes()
        + (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
    )
    check("pinned original equals DataFlash || CodeFlash", combined.is_file() and combined.read_bytes() == split)

    print("\n== public tooling semantics ==")
    semantic_inputs = [
        roots["icanhack_secoc"] / "extract_keys.py",
        roots["icanhack_secoc"] / "shellcode/main.c",
        roots["toyota_dataflash_secoc_setup"] / "steps/step_dump_dataflash.py",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/car/uds.py",
        roots["opendbc"] / "opendbc/dbc/generator/toyota/_toyota_2017.dbc",
        roots["opendbc"] / "opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc",
    ]
    if any(not path.is_file() for path in semantic_inputs):
        print("source-level corroboration skipped because a pinned input is missing")
        print(f"\n== RESULT: {passed} passed, {failed} failed ==")
        return 1

    extract = (roots["icanhack_secoc"] / "extract_keys.py").read_text(encoding="utf-8")
    extract_lower = extract.lower()
    shellcode = (roots["icanhack_secoc"] / "shellcode/main.c").read_text(encoding="utf-8").lower()
    dump_step = (
        roots["toyota_dataflash_secoc_setup"] / "steps/step_dump_dataflash.py"
    ).read_text(encoding="utf-8").lower()
    uds = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/car/uds.py"
    ).read_text(encoding="utf-8")
    toyota_2017_dbc = (
        roots["opendbc"]
        / "opendbc/dbc/generator/toyota/_toyota_2017.dbc"
    ).read_text(encoding="utf-8")
    toyota_secoc_dbc = (
        roots["opendbc"]
        / "opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc"
    ).read_text(encoding="utf-8")

    p203 = extract.find("write_data_by_identifier(0x203")
    p201 = extract.find("write_data_by_identifier(0x201")
    p202 = extract.find("write_data_by_identifier(0x202")
    check("Willem tooling writes 0203 -> 0201 -> 0202", -1 < p203 < p201 < p202)
    check("Willem tooling uses exactly five bytes for 0203", '0x203, b"\\x00" * 5' in extract)
    check("Willem tooling transmits to CAN 0x7A1", "addr = 0x7a1" in extract_lower)
    check("DataFlash tooling uses TX 0x7A1", "tx_addr = 0x7a1" in dump_step)
    check("DataFlash tooling expects RX 0x7A9", "rx_addr = 0x7a9" in dump_step)
    check("dump shellcode transmits CAN 0x7A9", "= 0x7a9;" in shellcode)
    for address in (
        "0xffd20250", "0xffd202d0", "0xffd24000", "0xffd24004",
        "0xffd24008", "0xffd2400c", "0xffd24010",
    ):
        check(f"dump shellcode independently uses RSCFD {address}", address in shellcode)
    check(
        "public extraction tooling does not name functional 0x777",
        "0x777" not in extract_lower and "0x777" not in dump_step and "0x777" not in shellcode,
    )
    check(
        "public UDS enum identifies F181 as application software ID",
        "APPLICATION_SOFTWARE_IDENTIFICATION = 0xF181" in uds,
    )
    check(
        "pinned Toyota DBC names CAN 0x260 STEER_TORQUE_SENSOR",
        "BO_ 608 STEER_TORQUE_SENSOR: 8" in toyota_2017_dbc,
    )
    for signal in (
        "STEER_OVERRIDE", "STEER_ANGLE_INITIALIZING", "STEER_TORQUE_DRIVER",
        "STEER_ANGLE", "STEER_TORQUE_EPS", "CHECKSUM",
    ):
        check(f"pinned CAN 0x260 DBC contains {signal}", signal in toyota_2017_dbc)
    check(
        "pinned Toyota DBC names CAN 0x262 EPS_STATUS",
        "BO_ 610 EPS_STATUS: 8 EPS" in toyota_secoc_dbc,
    )
    check(
        "pinned CAN 0x262 DBC places checksum in final byte",
        "SG_ CHECKSUM : 63|8@0+" in toyota_secoc_dbc,
    )

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
