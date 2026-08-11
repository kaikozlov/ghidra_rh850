#!/usr/bin/env python3
"""Optional checks against pinned public upstream repositories.

The core ``make verify`` target never imports this module and requires no
external checkout. Run this suite explicitly with ``make verify-external``.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import io
import json
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

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

    print("\n== pinned Stage-8 optskug evidence ==")
    optskug_readme = (roots["optskug_docs"] / "README.md").read_text(encoding="utf-8")
    check(
        "optskug records MCU ID + VIN as required official rekey inputs",
        "requires uploading both the MCU ID and VIN" in optskug_readme
        and "refuses to provide a key update when only the VIN is supplied" in optskug_readme,
    )
    check(
        "optskug keeps MCU-ID cryptographic role bounded",
        "does not yet establish the exact calculation" in optskug_readme,
    )
    check(
        "optskug records physical Toyota-B CAN0/CAN1 swap anomaly",
        "after physically swapping CAN 0 and CAN 1 at the harness, they were able to dump the firmware" in optskug_readme,
    )
    check(
        "optskug records the first 2023-US-Corolla public route",
        "a74eba85c97eaf67/00000004--555953f500/0" in optskug_readme,
    )
    check(
        "optskug records failed 2024 RAV4 Prime persistent-patch field test",
        "Techstream reported EPMS code `U023A87`" in optskug_readme,
    )
    check(
        "optskug records Toyota-B physical bus assignment can move the relay onto bus 1",
        "the relay ends up on bus 1 instead of bus 0/2" in optskug_readme.lower(),
    )

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
        roots["toyota_dataflash_secoc_setup"] / "steps/step_collect_can.py",
        roots["toyota_dataflash_secoc_setup"] / "steps/step_extract_verify_key.py",
        roots["toyota_dataflash_secoc_setup"] / "steps/step_eps_probe.py",
        roots["toyota_dataflash_secoc_setup"]
        / "payload_source/shellcode/main_ff1ff000_ff209000.c",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/car/uds.py",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/car/panda_runner.py",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/safety/modes/defaults.h",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/safety/modes/elm327.h",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/safety/modes/toyota.h",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/safety/safety.h",
        roots["calvinpark_openpilot"] / "panda/board/can_comms.h",
        roots["calvinpark_openpilot"] / "panda/board/main.c",
        roots["calvinpark_openpilot"] / "panda/board/main_comms.h",
        roots["calvinpark_openpilot"] / "panda/board/boards/tres.h",
        roots["calvinpark_openpilot"] / "panda/board/boards/cuatro.h",
        roots["calvinpark_openpilot"] / "panda/board/drivers/can_common.h",
        roots["calvinpark_openpilot"] / "panda/board/drivers/fdcan.h",
        roots["calvinpark_openpilot"] / "panda/board/drivers/harness.h",
        roots["calvinpark_openpilot"] / "panda/python/__init__.py",
        roots["calvinpark_openpilot"] / "panda/examples/query_fw_versions.py",
        roots["calvinpark_openpilot"] / "panda/scripts/can_printer.py",
        roots["calvinpark_openpilot"] / "openpilot/selfdrive/pandad/panda.h",
        roots["calvinpark_openpilot"] / "openpilot/selfdrive/pandad/panda.cc",
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
    collect_step = (
        roots["toyota_dataflash_secoc_setup"] / "steps/step_collect_can.py"
    ).read_text(encoding="utf-8").lower()
    verify_key_step = (
        roots["toyota_dataflash_secoc_setup"] / "steps/step_extract_verify_key.py"
    ).read_text(encoding="utf-8").lower()
    eps_probe_step = (
        roots["toyota_dataflash_secoc_setup"] / "steps/step_eps_probe.py"
    ).read_text(encoding="utf-8").lower()
    dump_shellcode_source = (
        roots["toyota_dataflash_secoc_setup"]
        / "payload_source/shellcode/main_ff1ff000_ff209000.c"
    ).read_text(encoding="utf-8").lower()
    uds = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/car/uds.py"
    ).read_text(encoding="utf-8")
    panda_runner = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/car/panda_runner.py"
    ).read_text(encoding="utf-8")
    default_safety = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/safety/modes/defaults.h"
    ).read_text(encoding="utf-8")
    elm327_safety = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/safety/modes/elm327.h"
    ).read_text(encoding="utf-8")
    calvin_toyota_safety = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/safety/modes/toyota.h"
    ).read_text(encoding="utf-8")
    calvin_safety_core = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/safety/safety.h"
    ).read_text(encoding="utf-8")
    panda_can_comms = (
        roots["calvinpark_openpilot"] / "panda/board/can_comms.h"
    ).read_text(encoding="utf-8")
    panda_main = (
        roots["calvinpark_openpilot"] / "panda/board/main.c"
    ).read_text(encoding="utf-8")
    panda_main_comms = (
        roots["calvinpark_openpilot"] / "panda/board/main_comms.h"
    ).read_text(encoding="utf-8")
    panda_tres = (
        roots["calvinpark_openpilot"] / "panda/board/boards/tres.h"
    ).read_text(encoding="utf-8")
    panda_cuatro = (
        roots["calvinpark_openpilot"] / "panda/board/boards/cuatro.h"
    ).read_text(encoding="utf-8")
    panda_can_common = (
        roots["calvinpark_openpilot"] / "panda/board/drivers/can_common.h"
    ).read_text(encoding="utf-8")
    panda_fdcan = (
        roots["calvinpark_openpilot"] / "panda/board/drivers/fdcan.h"
    ).read_text(encoding="utf-8")
    panda_harness = (
        roots["calvinpark_openpilot"] / "panda/board/drivers/harness.h"
    ).read_text(encoding="utf-8")
    panda_python = (
        roots["calvinpark_openpilot"] / "panda/python/__init__.py"
    ).read_text(encoding="utf-8")
    panda_query_fw = (
        roots["calvinpark_openpilot"] / "panda/examples/query_fw_versions.py"
    ).read_text(encoding="utf-8")
    panda_can_printer = (
        roots["calvinpark_openpilot"] / "panda/scripts/can_printer.py"
    ).read_text(encoding="utf-8")
    pandad_header = (
        roots["calvinpark_openpilot"] / "openpilot/selfdrive/pandad/panda.h"
    ).read_text(encoding="utf-8")
    pandad_source = (
        roots["calvinpark_openpilot"] / "openpilot/selfdrive/pandad/panda.cc"
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
    check("DataFlash tooling hardcodes Panda bus 0", "bus = 0" in dump_step)
    check("EPS probe independently hardcodes Panda bus 0", "bus = 0" in eps_probe_step)
    check(
        "current CAN collector restricts oracle buses to 0 and 2",
        "oracle_buses = {0, 2}" in collect_step,
    )
    check(
        "current CAN collector recognizes only sync plus Sienna protected IDs",
        "oracle_addrs = {0x0f, 0x131, 0x2e4, 0x344}" in collect_step,
    )
    check(
        "current key verifier likewise restricts protected IDs",
        "protected_addrs = {0x131, 0x2e4, 0x344}" in verify_key_step,
    )
    check(
        "current key verifier likewise restricts buses to 0 and 2",
        "buses = {0, 2}" in verify_key_step,
    )
    check(
        "DataFlash tooling selects ELM327 without an explicit nonzero routing parameter",
        "panda.set_safety_mode(3)" in dump_step,
    )
    check(
        "EPS probe also selects implicit ELM327 param 0",
        "panda.set_safety_mode(3)" in eps_probe_step,
    )
    check(
        "CAN collector also selects implicit ELM327 param 0",
        "panda.set_safety_mode(3)" in collect_step,
    )

    print("\n== pinned Panda ELM327 and harness routing ==")
    check(
        "ELM327 safety source documents param 0 bus-1 OBD multiplexing",
        "if safety_param == 0, bus 1 is multiplexed to the obd-ii port" in elm327_safety.lower(),
    )
    check(
        "Panda firmware selects OBD CAN2 mode when ELM327 param is zero",
        "if (param == 0u)" in panda_main.lower()
        and "set_can_mode(can_mode_obd_can2)" in panda_main.lower(),
    )
    check(
        "Panda firmware selects normal CAN mode for nonzero ELM327 param",
        "else" in panda_main.lower()
        and "set_can_mode(can_mode_normal)" in panda_main.lower(),
    )
    check(
        "Panda query_fw_versions exposes the same no-OBD routing switch",
        "set_safety_mode(carparams.safetymodel.elm327, 1 if args.no_obd else 0)"
        in panda_query_fw.lower(),
    )
    check(
        "Panda can_printer's pseudo bus 3 is actually OBD-muxed logical bus 1",
        'if canbus == "3":' in panda_can_printer
        and "p.set_obd(True)" in panda_can_printer
        and 'canbus = "1"' in panda_can_printer,
    )
    check(
        "normal openpilot PandaRunner establishes ELM param 1 before fingerprinting",
        "self.p.set_safety_mode(carparams.safetymodel.elm327, 1)" in panda_runner.lower()
        and "self.p.set_obd" in panda_runner.lower(),
    )
    check(
        "ELM safety-policy init ignores the routing parameter",
        ".init = nooutput_init" in elm327_safety
        and "SAFETY_UNUSED(param);" in default_safety,
    )
    elm_tx_body = elm327_safety.split("static bool elm327_tx_hook", 1)[1].split("// If safety_param", 1)[0]
    check("ELM transmit policy itself has no safety-param branch", "param" not in elm_tx_body.lower())
    check(
        "ELM diagnostic whitelist admits EPS request 0x7A1",
        "((msg->addr & 0x1FFFFF00U) != 0x700U)" in elm327_safety
        and (0x7A1 & 0x1FFFFF00) == 0x700,
    )
    check(
        "ELM mode disables software forwarding while leaving the harness relay unintercepted",
        "return (safety_config){NULL, 0, NULL, 0, true}" in default_safety
        and "case SAFETY_ELM327:" in panda_main
        and "set_intercept_relay(false, false);" in panda_main,
    )
    check(
        "Panda logical bus orientation swaps buses 0 and 2 only",
        "bus_config[0].bus_lookup = flipped ? 2u : 0u" in panda_can_common.lower()
        and "bus_config[2].bus_lookup = flipped ? 0u : 2u" in panda_can_common.lower(),
    )
    check(
        "Panda generic harness forwarding is a bus-0/bus-2 pair and excludes bus 1",
        "if (bus_num == 0)" in calvin_safety_core.lower()
        and "destination_bus = 2" in calvin_safety_core.lower()
        and "else if (bus_num == 2)" in calvin_safety_core.lower()
        and "destination_bus = 0" in calvin_safety_core.lower()
        and "destination_bus = -1" in calvin_safety_core.lower(),
    )
    check(
        "harness default and ELM both keep the physical intercept relay closed/pass-through",
        "set_intercept_relay(false, false);" in panda_harness
        and panda_main.count("set_intercept_relay(false, false);") >= 3,
    )
    check(
        "harness orientation changes reapply the remembered safety mode and parameter",
        "can_set_orientation(harness.status == HARNESS_STATUS_FLIPPED);" in panda_main
        and "set_safety_mode(current_safety_mode, current_safety_param);" in panda_main,
    )
    obd_handler = panda_main_comms.split("// **** 0xdb: set OBD CAN multiplexing mode", 1)[1].split("// **** 0xdc: set safety mode", 1)[0]
    safety_handler = panda_main_comms.split("// **** 0xdc: set safety mode", 1)[1].split("// **** 0xdd:", 1)[0]
    check(
        "Panda set_obd USB request changes board CAN mode without updating remembered safety param",
        "current_board->set_can_mode" in obd_handler and "current_safety_param" not in obd_handler,
    )
    check(
        "Panda set_safety_mode USB request updates the persistent safety state through set_safety_mode",
        "set_safety_mode(req->param1, (uint16_t)req->param2);" in safety_handler
        and "current_safety_param = param;" in calvin_safety_core,
    )
    check(
        "Python set_obd and set_safety_mode are distinct USB controls",
        "controlWrite(Panda.REQUEST_OUT, 0xdb, int(obd), 0, b'')" in panda_python
        and "controlWrite(Panda.REQUEST_OUT, 0xdc, mode, param, b'')" in panda_python,
    )
    check(
        "Panda constructor defaults to disabling heartbeat checks for standalone scripts",
        "disable_checks: bool = True" in panda_python
        and "self.set_heartbeat_disabled()" in panda_python,
    )
    check(
        "pandad marks returned CAN with source offset 0x80",
        "#define CAN_RETURNED_BUS_OFFSET 0x80U" in pandad_header
        and "canData.src += CAN_RETURNED_BUS_OFFSET" in pandad_source,
    )
    check(
        "pandad marks rejected CAN with source offset 0xC0",
        "#define CAN_REJECTED_BUS_OFFSET   0xC0U" in pandad_header
        and "canData.src += CAN_REJECTED_BUS_OFFSET" in pandad_source,
    )
    check(
        "Tres OBD mode changes the FDCAN2 physical pin/transceiver selection",
        "case can_mode_obd_can2:" in panda_tres.lower()
        and "gpio_af9_fdcan2" in panda_tres.lower()
        and "enable_can_transceiver(2u, true)" in panda_tres.lower()
        and "enable_can_transceiver(4u, true)" in panda_tres.lower(),
    )
    check(
        "Tres normal/OBD selection is explicitly coupled to harness orientation",
        "(bool)(mode == CAN_MODE_NORMAL) != (bool)(harness.status == HARNESS_STATUS_FLIPPED)"
        in panda_tres,
    )
    check(
        "comma 4 Cuatro inherits the Tres FDCAN2 physical-routing implementation",
        ".set_can_mode = tres_set_can_mode" in panda_cuatro.lower(),
    )
    check(
        "UdsClient bus selection only feeds CAN send and receive-bus filtering",
        "self.tx(self.tx_addr, msg, self.bus)" in uds
        and "return bus == self.bus and addr == self.rx_addr" in uds,
    )
    check(
        "Panda CAN send path maps the UDS logical bus through bus_config into an MCU CAN controller",
        "can_send(&to_push, to_push.bus, false);" in panda_can_comms
        and "process_can(CAN_NUM_FROM_BUS_NUM(bus_number));" in panda_can_common
        and "uint8_t bus_number = BUS_NUM_FROM_CAN_NUM(can_number);" in panda_fdcan,
    )
    check(
        "FDCAN2 mux error recovery explicitly accounts for ACK errors while switching physical paths",
        "while multiplexing between buses 1 and 3 we are getting ACK errors" in panda_fdcan
        and "can_clear_send(FDCANx, can_number);" in panda_fdcan,
    )
    check("dump shellcode transmits CAN 0x7A9", "= 0x7a9;" in shellcode)
    for address in (
        "0xffd20250", "0xffd202d0", "0xffd24000", "0xffd24004",
        "0xffd24008", "0xffd2400c", "0xffd24010",
    ):
        check(f"dump shellcode independently uses RSCFD {address}", address in shellcode)
        check(
            f"DataFlash source independently uses RSCFD {address}",
            address in dump_shellcode_source,
        )
    check(
        "DataFlash source uses the candidate's CAN 0x7A9 word-frame expression",
        "((int)addr << 8) | 0x07" in dump_shellcode_source
        and "= *addr;" in dump_shellcode_source
        and "= 0x7a9;" in dump_shellcode_source,
    )
    check(
        "DataFlash source carries the candidate's boot-reset target",
        "0x0000157e" in dump_shellcode_source and "bl_reset();" in dump_shellcode_source,
    )
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
        "pinned Toyota checksum source matches recovered additive algorithm",
        "def toyota_checksum(address: int, sig, d: bytearray) -> int:" in opendbc_toyotacan
        and "s = len(d)" in opendbc_toyotacan
        and "while addr:" in opendbc_toyotacan
        and "s += addr & 0xFF" in opendbc_toyotacan
        and "for i in range(len(d) - 1):" in opendbc_toyotacan
        and "s += d[i]" in opendbc_toyotacan
        and "return s & 0xFF" in opendbc_toyotacan,
    )
    check(
        "pinned Toyota SecOC DBC names CAN 0x2E4 STEERING_LKA",
        "BO_ 740 STEERING_LKA: 8" in toyota_secoc_dbc,
    )
    check(
        "pinned CAN 0x2E4 DBC identifies signed B1..B2 torque command",
        "SG_ STEER_TORQUE_CMD : 15|16@0-" in toyota_secoc_dbc,
    )
    for can_id, message_name in (
        (278, "GAS_PEDAL"),
        (305, "STEERING_LTA_2"),
        (375, "PCM_CRUISE_3"),
        (387, "ACC_CONTROL_2"),
        (589, "PCM_CRUISE_4"),
        (643, "PRE_COLLISION"),
        (740, "STEERING_LKA"),
        (836, "PRE_COLLISION_2"),
    ):
        block = dbc_message(toyota_secoc_dbc, can_id, message_name)
        check(
            f"classic SecOC profile contains {message_name} at CAN {can_id:#x}",
            bool(block),
        )
        for signal in ("AUTHENTICATOR", "RESET_FLAG", "MSG_CNT_LOWER"):
            check(
                f"CAN {can_id:#x} {message_name} carries {signal}",
                signal in block,
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
    check(
        "opendbc marks 2021-23 RAV4 Prime as a SecOC platform",
        "TOYOTA_RAV4_PRIME = ToyotaSecOCPlatformConfig(" in opendbc_toyota_values
        and 'ToyotaSecOcCarDocs("Toyota RAV4 Prime 2021-23"' in opendbc_toyota_values,
    )
    check(
        "Toyota SecOC controller derives outbound freshness from live synchronization",
        "CS.secoc_synchronization['TRIP_CNT']" in opendbc_toyota_controller
        and "CS.secoc_synchronization['RESET_CNT']" in opendbc_toyota_controller,
    )
    check(
        "wrong sync MAC is logged but does not directly abort controller update",
        'carlog.error("SecOC synchronization MAC mismatch, wrong key?")' in opendbc_toyota_controller,
    )
    check(
        "ACC_CONTROL_2 signing is gated by openpilot longitudinal control",
        "if self.CP.openpilotLongitudinalControl:" in opendbc_toyota_controller
        and "acc_cmd_2 = add_mac(self.secoc_key" in opendbc_toyota_controller,
    )

    print("\n== pinned forced RAV4 Prime SecOC safety substitution ==")
    check(
        "stock-longitudinal SecOC safety whitelist includes camera replacement 0x2E4 and 0x131",
        "TOYOTA_COMMON_SECOC_TX_MSGS" in calvin_toyota_safety
        and "{0x2E4, 0, 8, .check_relay = true}" in calvin_toyota_safety
        and "{0x131, 0, 8, .check_relay = true}" in calvin_toyota_safety,
    )
    check(
        "base Toyota safety whitelist also replaces 0x191 and 0x412",
        "{0x191, 0, 8, .check_relay = true}" in calvin_toyota_safety
        and "{0x412, 0, 8, .check_relay = true}" in calvin_toyota_safety,
    )
    check(
        "SecOC openpilot-long whitelist adds authenticated 0x183",
        "{0x183, 0, 8, .check_relay = true}" in calvin_toyota_safety,
    )
    check(
        "stock-longitudinal SecOC selects the whitelist without 0x183",
        "if (toyota_secoc)" in calvin_toyota_safety
        and "if (toyota_stock_longitudinal)" in calvin_toyota_safety
        and "SET_TX_MSGS(TOYOTA_SECOC_TX_MSGS, ret);" in calvin_toyota_safety
        and "SET_TX_MSGS(TOYOTA_SECOC_LONG_TX_MSGS, ret);" in calvin_toyota_safety,
    )
    check(
        "generic Panda safety forwarding is bus 0<->2",
        "if (bus_num == 0)" in calvin_safety_core
        and "destination_bus = 2;" in calvin_safety_core
        and "else if (bus_num == 2)" in calvin_safety_core
        and "destination_bus = 0;" in calvin_safety_core,
    )
    check(
        "generic forwarding blocks stock frames matching destination check_relay TX entries",
        "m->check_relay" in calvin_safety_core
        and "m->addr == addr" in calvin_safety_core
        and "m->bus == (unsigned int)destination_bus" in calvin_safety_core
        and "blocked = true;" in calvin_safety_core,
    )
    check(
        "Toyota safety has no custom forward hook overriding the generic substitution",
        ".fwd =" not in calvin_toyota_safety,
    )
    check(
        "RAV4 Prime SecOC platform flags do not include UNSUPPORTED_DSU",
        "TOYOTA_RAV4_PRIME = ToyotaSecOCPlatformConfig(" in opendbc_toyota_values
        and "flags=ToyotaFlags.UNSUPPORTED_DSU" not in opendbc_toyota_values[opendbc_toyota_values.index("TOYOTA_RAV4_PRIME = ToyotaSecOCPlatformConfig("):opendbc_toyota_values.index("TOYOTA_YARIS =", opendbc_toyota_values.index("TOYOTA_RAV4_PRIME = ToyotaSecOCPlatformConfig("))],
    )
    check(
        "SecOC platform base flags are TSS2 NO_DSU SECOC",
        "self.flags |= ToyotaFlags.TSS2 | ToyotaFlags.NO_DSU | ToyotaFlags.SECOC" in opendbc_toyota_values,
    )
    check(
        "STEERING_LKA is always generated and SecOC-signed when the platform flag is set",
        "steer_command = toyotacan.create_steer_command" in opendbc_toyota_controller
        and "steer_command = add_mac(self.secoc_key" in opendbc_toyota_controller,
    )
    check(
        "STEERING_LTA and LTA_2 are generated on frame mod 2",
        "if self.frame % 2 == 0 and self.CP.carFingerprint in TSS2_CAR:" in opendbc_toyota_controller
        and "create_lta_steer_command_2" in opendbc_toyota_controller,
    )
    check(
        "LKAS HUD is generated on frame mod 20 or UI edge",
        "if self.frame % 20 == 0 or send_ui:" in opendbc_toyota_controller
        and "create_ui_command" in opendbc_toyota_controller,
    )
    check(
        "stock-long cancel chooses ACC_CONTROL unless UNSUPPORTED_DSU",
        "if self.CP.carFingerprint in UNSUPPORTED_DSU_CAR:" in opendbc_toyota_controller
        and "create_acc_cancel_command" in opendbc_toyota_controller
        and "create_accel_command(self.packer, 0, pcm_cancel_cmd" in opendbc_toyota_controller,
    )
    check(
        "ACC_CONTROL_2 is generated only inside openpilot longitudinal branch",
        "if self.CP.openpilotLongitudinalControl:" in opendbc_toyota_controller
        and "acc_cmd_2 = toyotacan.create_accel_command_2" in opendbc_toyota_controller,
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

    print("\n== pinned Vance deployment-bundle payloads ==")
    bundle_v3 = (
        roots["vance_sienna_2024"]
        / "scripts/secoc/20260531_othersienna_secoc_bundle_v3.zip"
    )
    with zipfile.ZipFile(bundle_v3) as archive:
        member_names = set(archive.namelist())
        standard_ciphertext = archive.read("payload_dataflash_ff200000_ff208000.bin")
        candidate_ciphertext = archive.read(
            "payload_candidate_f05_dataflash_ff200000_ff208000.bin"
        )
        bundle_readme = archive.read(
            "README_other_sienna_secoc_bundle_zh.md"
        ).decode("utf-8")

    check(
        "bundle standard payload matches committed DataFlash fixture",
        standard_ciphertext
        == (REPO / "tests/fixtures/payloads/dataflash_dump_payload.bin").read_bytes(),
    )
    check(
        "bundle candidate-f05 ciphertext SHA-256",
        hashlib.sha256(candidate_ciphertext).hexdigest()
        == "296d87d2e89b9c7e800122e4c7f6d3b9c876362e52586530cdd53c86ba1116f5",
    )
    check(
        "bundle candidate-f05 matches committed fixture",
        candidate_ciphertext
        == (REPO / "tests/fixtures/payloads/candidate_f05_dataflash_payload.bin").read_bytes(),
    )
    candidate_bundle_members = []
    for bundle_name in (
        "20260531_othersienna_secoc_bundle.zip",
        "20260531_othersienna_secoc_bundle_v2.zip",
        "20260531_othersienna_secoc_bundle_v3.zip",
    ):
        with zipfile.ZipFile(
            roots["vance_sienna_2024"] / "scripts/secoc" / bundle_name
        ) as candidate_bundle:
            candidate_bundle_members.append(
                candidate_bundle.read(
                    "payload_candidate_f05_dataflash_ff200000_ff208000.bin"
                )
            )
    check(
        "all three Vance deployment bundles carry the identical candidate-f05",
        all(payload == candidate_ciphertext for payload in candidate_bundle_members),
    )

    print("\n== candidate-f05 historical provenance ==")
    vance_root = roots["vance_sienna_2024"]
    earliest_commit = "97ba3d1d9e77a6e047887da04767538fe81fc674"
    earliest_meta = subprocess.run(
        ["git", "-C", str(vance_root), "show", "-s", "--format=%H|%ai|%an", earliest_commit],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    check(
        "earliest public Vance bundle commit metadata",
        earliest_meta
        == f"{earliest_commit}|2026-05-31 20:26:27 +0800|Vance425",
        earliest_meta,
    )
    earliest_zip = subprocess.run(
        ["git", "-C", str(vance_root), "show",
         f"{earliest_commit}:scripts/secoc/20260531_othersienna_secoc_bundle.zip"],
        check=True, capture_output=True,
    ).stdout
    with zipfile.ZipFile(io.BytesIO(earliest_zip)) as archive:
        earliest_candidate = archive.read("payload_candidate_f05_dataflash_ff200000_ff208000.bin")
        earliest_manifest = json.loads(archive.read("manifest_sha256.json").decode("utf-8-sig"))
        earliest_readme = archive.read("README_other_sienna_secoc_bundle_zh.md").decode("utf-8")
    check("earliest public bundle already contains identical candidate-f05",
          earliest_candidate == candidate_ciphertext)
    check("earliest public bundle README gives candidate-only bounded description",
          "保留候選 payload，預設不使用" in earliest_readme)
    manifest_text = json.dumps(earliest_manifest, ensure_ascii=False)
    check("earliest public manifest pins candidate ciphertext SHA",
          "296d87d2e89b9c7e800122e4c7f6d3b9c876362e52586530cdd53c86ba1116f5" in manifest_text)

    patch_commit = "abc871308b0933c13a2551852857c350ea0f5386"
    patch_source = subprocess.run(
        ["git", "-C", str(vance_root), "show",
         f"{patch_commit}:scripts/secoc/patch_secoc_payload_dump_range.py"],
        check=True, capture_output=True, text=True,
    ).stdout
    check("May-28 Vance helper is range-patch/reseal, not shellcode compiler",
          "replace_exact" in patch_source and "old_start" in patch_source
          and "old_end" in patch_source and "v850-elf-gcc" not in patch_source)

    bk_root = roots["toyota_dataflash_secoc_setup"]
    bk_first = subprocess.run(
        ["git", "-C", str(bk_root), "log", "--diff-filter=A", "--format=%H|%ai",
         "--", "payload_source/shellcode/main_ff1ff000_ff209000.c"],
        check=True, capture_output=True, text=True,
    ).stdout.strip().splitlines()
    check("Bk2ol public source first appears after Vance candidate",
          bk_first == ["db453752beeb7cdd024a1a9c38c6711c981e75ad|2026-07-11 18:29:18 -0500"],
          repr(bk_first))
    bk_build = (bk_root / "payload_source/shellcode/build.sh").read_text(encoding="utf-8")
    check("later Bk2ol source family uses v850 gcc plus objcopy",
          "v850-elf-gcc" in bk_build and "v850-elf-objcopy" in bk_build)

    codeflash = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
    zero = bytes(16)

    def decode_payload(ciphertext: bytes, build_secret: bytes) -> tuple[bytes, bool, bool]:
        derived = AES.new(build_secret, AES.MODE_ECB).encrypt(zero)
        plaintext = AES.new(derived, AES.MODE_CBC, zero).decrypt(ciphertext)
        cmac = CMAC.new(derived, ciphermod=AES)
        cmac.update(zero + plaintext[:0xFF0])
        cmac_ok = cmac.digest() == plaintext[0xFF0:]
        crc_ok = binascii.crc32(plaintext[:0xFF0]) % (1 << 32) == 0xFFFFFFFF
        return plaintext, cmac_ok, crc_ok

    standard_plain, standard_cmac, standard_crc = decode_payload(
        standard_ciphertext, codeflash[0xBFD8:0xBFE8]
    )
    candidate_normal_plain, candidate_normal_cmac, candidate_normal_crc = decode_payload(
        candidate_ciphertext, codeflash[0xBFD8:0xBFE8]
    )
    candidate_f05_plain, candidate_f05_cmac, candidate_f05_crc = decode_payload(
        candidate_ciphertext, codeflash[0xBFE8:0xBFF8]
    )
    check("bundle standard payload authenticates with payload-build secret",
          standard_cmac and standard_crc)
    check("candidate-f05 does not authenticate with payload-build secret",
          not candidate_normal_cmac and not candidate_normal_crc)
    check("candidate-f05 authenticates with SecurityAccess secret as build secret",
          candidate_f05_cmac and candidate_f05_crc)
    check(
        "candidate-f05 has valid callback and CRC descriptor",
        struct.unpack_from("<I", candidate_f05_plain, 0xFD0)[0] == 0xFEBF0000
        and struct.unpack_from("<II", candidate_f05_plain, 0xFE0)
        == (0xFEBF0000, 0xFF0),
    )
    check(
        "candidate-f05 plaintext materially differs from standard payload",
        sum(a != b for a, b in zip(standard_plain, candidate_f05_plain)) == 380
        and sum(a != b for a, b in zip(standard_plain[:0xFD0], candidate_f05_plain[:0xFD0]))
        == 360,
    )
    check(
        "bundle README labels candidate-f05 retained and not default",
        "保留候選 payload，預設不使用" in bundle_readme,
    )
    completed_outputs = {
        "metadata.json", "transcript.jsonl", "frames.csv", "frames.jsonl",
        "protected_frames.jsonl", "sync_frames.jsonl",
        "secoc_key_probe_results.json", "secoc_key_probe_results.csv",
    }
    check(
        "bundle contains no completed partner dump/capture outputs",
        not any(
            Path(name).name in completed_outputs
            or Path(name).name.startswith("dump_")
            for name in member_names
        ),
    )
    check(
        "wrong-key candidate plaintext is structurally invalid",
        struct.unpack_from("<I", candidate_normal_plain, 0xFD0)[0] != 0xFEBF0000,
    )

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
