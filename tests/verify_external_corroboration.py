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


def dbc_message(dbc: str, can_id: int, name: str) -> str:
    """Return one DBC message block, excluding following BO_ definitions."""
    marker = f"BO_ {can_id} {name}:"
    start = dbc.find(marker)
    if start < 0:
        return ""
    end = dbc.find("\nBO_ ", start + len(marker))
    return dbc[start:] if end < 0 else dbc[start:end]


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
        roots["calvinpark_openpilot"] / "tsk/COROLLA_INVESTIGATION.md",
        roots["opendbc"] / "opendbc/dbc/generator/toyota/_toyota_2017.dbc",
        roots["opendbc"] / "opendbc/dbc/generator/toyota/_toyota_adas_standard.dbc",
        roots["opendbc"] / "opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc",
        roots["opendbc"] / "opendbc/car/secoc.py",
        roots["opendbc"] / "opendbc/car/toyota/carcontroller.py",
        roots["opendbc"] / "opendbc/car/toyota/toyotacan.py",
        roots["opendbc"] / "opendbc/car/toyota/values.py",
        roots["vance_sienna_2024"] / "docs/tss3-secoc-key-recovery-20260608-zh.md",
        roots["vance_sienna_2024"] / "docs/secoc-20260522-steering-lka-key-validation-full-zh.md",
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
    toyota_adas_dbc = (
        roots["opendbc"]
        / "opendbc/dbc/generator/toyota/_toyota_adas_standard.dbc"
    ).read_text(encoding="utf-8")
    toyota_secoc_dbc = (
        roots["opendbc"]
        / "opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc"
    ).read_text(encoding="utf-8")
    opendbc_secoc = (
        roots["opendbc"] / "opendbc/car/secoc.py"
    ).read_text(encoding="utf-8")
    opendbc_toyota_controller = (
        roots["opendbc"] / "opendbc/car/toyota/carcontroller.py"
    ).read_text(encoding="utf-8")
    opendbc_toyotacan = (
        roots["opendbc"] / "opendbc/car/toyota/toyotacan.py"
    ).read_text(encoding="utf-8")
    opendbc_toyota_values = (
        roots["opendbc"] / "opendbc/car/toyota/values.py"
    ).read_text(encoding="utf-8")
    vance_final = (
        roots["vance_sienna_2024"]
        / "docs/tss3-secoc-key-recovery-20260608-zh.md"
    ).read_text(encoding="utf-8").lower()
    vance_may = (
        roots["vance_sienna_2024"]
        / "docs/secoc-20260522-steering-lka-key-validation-full-zh.md"
    ).read_text(encoding="utf-8").lower()
    variant_page = (
        REPO / "docs/variants/sienna-8965B4514000.md"
    ).read_text(encoding="utf-8").lower()

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
    check(
        "pinned Toyota SecOC DBC names CAN 0x2E4 STEERING_LKA",
        "BO_ 740 STEERING_LKA: 8" in toyota_secoc_dbc,
    )
    check(
        "pinned CAN 0x2E4 DBC identifies signed B1..B2 torque command",
        "SG_ STEER_TORQUE_CMD : 15|16@0-" in toyota_secoc_dbc,
    )

    print("\n== pinned opendbc SecOC sender ==")
    check(
        "opendbc authenticates DataID_be16 plus payload4 plus freshness48",
        "struct.pack('>H', addr) + payload + freshness_value" in opendbc_secoc,
    )
    check(
        "opendbc packs trip16/reset20/message8/reset-low2 freshness",
        "(reset_cnt << 12) | ((msg_cnt & 0xff) << 4) | (reset_flag << 2)"
        in opendbc_secoc,
    )
    check(
        "opendbc transmits the first 28 CMAC bits",
        "cmac.digest().hex()[:7]" in opendbc_secoc,
    )
    check(
        "opendbc synchronization authenticator defaults to DataID 0x00F",
        "def build_sync_mac(key, trip_cnt, reset_cnt, id_=0xf):" in opendbc_secoc,
    )
    check(
        "Toyota controller signs three independent output streams",
        opendbc_toyota_controller.count("add_mac(self.secoc_key") == 3,
    )
    for counter in (
        "secoc_lka_message_counter",
        "secoc_lta_message_counter",
        "secoc_acc_message_counter",
    ):
        check(f"Toyota controller tracks {counter}", counter in opendbc_toyota_controller)
    check(
        "Toyota controller checks the synchronization authenticator",
        "expected_mac = build_sync_mac(" in opendbc_toyota_controller,
    )
    for message_name in ("STEERING_LKA", "STEERING_LTA_2", "ACC_CONTROL_2"):
        check(
            f"Toyota CAN builder constructs {message_name}",
            f'make_can_msg("{message_name}"' in opendbc_toyotacan,
        )
    for can_id, message_name in (
        (740, "STEERING_LKA"),
        (305, "STEERING_LTA_2"),
        (387, "ACC_CONTROL_2"),
    ):
        check(
            f"SecOC DBC binds {message_name} to CAN {can_id:#x}",
            f"BO_ {can_id} {message_name}: 8" in toyota_secoc_dbc,
        )
    check(
        "opendbc marks fourth-generation Sienna as a SecOC platform",
        "TOYOTA_SIENNA_4TH_GEN = ToyotaSecOCPlatformConfig(" in opendbc_toyota_values,
    )

    print("\n== pinned opendbc CAN 0x344 provenance ==")
    secoc_344 = dbc_message(toyota_secoc_dbc, 836, "PRE_COLLISION_2")
    check(
        "pinned Toyota SecOC DBC names CAN 0x344 PRE_COLLISION_2 with logical DSU node",
        "BO_ 836 PRE_COLLISION_2: 8 DSU" in secoc_344,
    )
    for signal in ("AUTHENTICATOR", "RESET_FLAG", "MSG_CNT_LOWER"):
        check(f"pinned CAN 0x344 SecOC block contains {signal}", signal in secoc_344)
    legacy_344 = dbc_message(toyota_adas_dbc, 836, "PRE_COLLISION_2")
    check(
        "pinned legacy CAN 0x344 DBC preserves logical DSU node",
        "BO_ 836 PRE_COLLISION_2: 8 DSU" in legacy_344,
    )
    for signal in ("DSS1GDRV", "PCSALM", "IBTRGR", "PBATRGR", "PREFILL", "AVSTRGR"):
        check(f"pinned legacy CAN 0x344 block contains PCS signal {signal}", signal in legacy_344)

    print("\n== pinned Vance 8965B4514000 field report ==")
    for token, label in (
        ("8965b4514000", "application software ID"),
        ("0xff200000 - 0xff208000", "32 KiB DataFlash range"),
        ("0xff206e14", "candidate absolute address"),
        ("`28180`", "candidate offset"),
        ("1d1c53a6d634016a", "public key SHA-256 prefix"),
        ("`0x7a1`", "physical diagnostic TX"),
        ("`0x7a9`", "physical diagnostic RX"),
        ("`1024/1024`", "corrected synchronization result"),
        ("`226/226`", "CAN 0x131 validation count"),
        ("`225/225`", "CAN 0x2E4 validation count"),
        ("`112/113`", "CAN 0x344 validation count"),
        ("`563/564`", "protected-frame aggregate"),
        ("`730/750`", "later end-to-end protected result"),
    ):
        check(f"Vance final report contains {label}", token in vance_final)
    check(
        "Vance May report records the superseded sync mismatch",
        "0x0f sync mac match = 0/512" in vance_may,
    )
    check(
        "local variant page marks the May sync conclusion superseded",
        "may" in variant_page and "superseded" in variant_page
        and "1024/1024" in variant_page,
    )
    check(
        "local variant page keeps 4514000 runtime architecture unresolved",
        "bounded but unresolved" in variant_page
        and "missing codeflash/runtime access" in variant_page,
    )

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
