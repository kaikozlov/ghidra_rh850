#!/usr/bin/env python3
"""Verify exact-F33 non-bypassing B6 transaction observer design and installer."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.common.payload_package import inspect_payload, package_shellcode
from exploit.ephemeral_runtime.camry_f33_b6_transaction_observer import (
    TELEMETRY_BASE,
    TELEMETRY_FIELDS,
    TELEMETRY_SIZE,
    decode_telemetry,
)

AUDITED_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_transaction_observer.bin"
AUDIT = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_b6_transaction_observer_build.json"
SOURCE = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_transaction_observer.c"
BUILDER = ROOT / "exploit/ephemeral_runtime/build_camry_f33_b6_transaction_observer.py"
INSTALLER = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_transaction_observer_install.py"
BRIDGE_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_bridge.bin"
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


audit = json.loads(AUDIT.read_text())
blob = AUDITED_BIN.read_bytes()
image = IMAGE.read_bytes()
print("== audited observer / retained-tail contract ==")
check("observer binary identity exact", len(blob) == audit["shellcode"]["size"] == 594 and
      sha(blob) == audit["shellcode"]["sha256"] == "42af3133034ab9a95858e6dd189bb847f2b3ac7d57df4dc4c02652beb1e7aa3f")
check("observer source and builder are hash-bound", audit["source"]["sha256"] == sha(SOURCE.read_bytes()) and
      audit["builder"]["sha256"] == sha(BUILDER.read_bytes()))
c = audit["compile_contract"]
check("code plus telemetry stays inside exact 524-byte live-proven tail",
      c["resident_base"] == "0xFEBFF9F0" and c["resident_size_incl_marker_slack"] == 494 and
      c["resident_limit"] == 496 and c["resident_telemetry_base"] == "0xFEBFFBE0" and
      c["resident_telemetry_size"] == 28 and c["resident_end_exclusive"] == "0xFEBFFBFC" and
      494 + 28 <= 524)
check("observer is position-independent and relocation-free", c["entry_offset"] == 0 and c["relocations"] == 0)
check("shared telemetry schema matches audited build", audit["telemetry_layout"]["size"] == TELEMETRY_SIZE == 28 and
      int(c["resident_telemetry_base"], 16) == TELEMETRY_BASE and audit["telemetry_layout"]["fields"] == list(TELEMETRY_FIELDS))

print("\n== exact F33 transaction pins ==")
pins = {k: int(v, 16) for k, v in audit["static_pins"].items()}
check("queue/buffer/result/publication cells exact", pins["B6_QUEUE_RECORD"] == 0xFEBE547A and
      pins["B6_SECURED_BUFFER"] == 0xFEBE54D4 and pins["B6_SECOC_RESULT"] == 0xFEBE5564 and
      pins["B6_IPDU_FLAG"] == 0xFEBE5364)
check("ICU-S done/status bytes exact and byte-pinned", pins["ICUS_DONE"] == 0xFEBF13BE and
      pins["ICUS_STATUS"] == 0xFEBF13BF and image[0x89CB4:0x89CBC] == bytes.fromhex("4407be5b448fbf5b"))
check("SecOC result-byte consumer exact", image[0x8F92A:0x8F932] == bytes.fromhex("840f659de009e10f"))
record = 0x25848 + 2 * 0x50
check("B6 profile callbacks exact", int.from_bytes(image[record+0x30:record+0x34], "little") == 0x90448 and
      int.from_bytes(image[record+0x48:record+0x4C], "little") == 0x903A0)

print("\n== non-bypass semantics ==")
src = SOURCE.read_text()
check("observer executes stock aggregate exactly once and never calls route44 itself",
      src.count("call0(TARGET_FG_AGGREGATE);") == 1 and "TARGET_B6_COM_RX_CALLBACK" not in src and "B6_PDUR_ROUTE" not in src)
check("observer latches security state only on queued-B6 cycles", "if (queued_b6 != 0u)" in src and src.count("if (queued_b6 != 0u)") == 2)
check("observer binary has stock aggregate immediate but no route44 callback immediate",
      bytes.fromhex("e6670600") in blob and bytes.fromhex("2cd70700") not in blob and bytes.fromhex("2cd70700") in BRIDGE_BIN.read_bytes())
check("observer contains exact protected ICU-S address material", bytes.fromhex("be13bffe") in blob)

print("\n== telemetry decode contract ==")
raw = bytearray(TELEMETRY_SIZE)
raw[0:4] = (0x4F364260).to_bytes(4, "little")
raw[4] = 1
raw[8] = 7; raw[9] = 10
raw[10:12] = (0).to_bytes(2, "little")
raw[12] = 1; raw[13] = 10; raw[14] = 1; raw[15] = 1
raw[16:21] = bytes((0x0B, 0xFF, 0xF0, 0x00, 0x3E))
raw[24:28] = bytes.fromhex("d1234567")
d = decode_telemetry(bytes(raw))
check("decoder recovers B6 identity and signed target", d["queue_seen"] is True and d["b6_target_id"] == 11 and
      d["b6_target_raw"] == -16 and d["b6_companion"] == 0 and d["b6_sequence"] == 62)
check("decoder recovers FV4/MAC28 and security result", d["b6_fv4"] == 13 and d["b6_mac28"] == 0x1234567 and
      d["pre_secoc_result"] == 7 and d["post_secoc_result"] == 1 and d["icus_done"] == 1 and d["icus_status"] == 1)
blank = decode_telemetry(bytes(TELEMETRY_SIZE))
check("decoder fails closed on never-seen transaction fields", blank["queue_seen"] is False and blank["b6_target_id"] is None and blank["icus_status"] is None)

print("\n== deterministic authenticated payload / installer ==")
secret = image[0xBFD8:0xBFE8]
payload = package_shellcode(blob, secret=secret)
inspection = inspect_payload(payload, secret=secret)
check("authenticated payload is deterministic and valid", len(payload) == 0x1000 and
      sha(payload) == "29841b4965c7a690d76e641efd2d950ab291cfb6332a8d806fa6930fdaecbbbb" and
      inspection.cmac_valid and inspection.crc_residue == 0xFFFFFFFF and inspection.callback_address == 0xFEBF0000)
spec = importlib.util.spec_from_file_location("camry_f33_b6_transaction_observer_install", INSTALLER)
assert spec and spec.loader
installer = importlib.util.module_from_spec(spec); sys.modules[spec.name] = installer; spec.loader.exec_module(installer)
check("installer pins payload/shellcode and exact current route", installer.EXPECTED_PAYLOAD_SHA256 == sha(payload) and
      installer.OBSERVER_SHELLCODE_SHA256 == sha(blob) and installer.ROUTE.bus == 0 and installer.ROUTE.elm327_param == 1)
plan = installer.plan(Path("/nonexistent/observer.bin"))
check("installer plan is RAM-only, non-bypassing, and uses the built-in P1M-E root",
      plan["ram"]["persistent_flash_writes"] is False and plan["telemetry"]["bypass"] is False and
      "built-in Toyota P1M-E boot SecurityAccess root" in plan["live_requirements"] and
      "NRTD->READY directly" in plan["next_state"])
installer_src = INSTALLER.read_text()
check("installer uses authenticated RAM executor only", "execute_ram_payload(" in installer_src and
      all(x not in installer_src for x in ("flash_program", "erase_codeflash", "RequestDownload(")))
check("installer requires no temporary boot-secret file", "--boot-secret-file" not in installer_src)
check("installer never records the secret value", '"secret_value_recorded": False' in installer_src)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
