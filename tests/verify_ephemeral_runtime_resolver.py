#!/usr/bin/env python3
"""Verify the fail-closed ephemeral-runtime target resolver and manifest join."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF_PATH = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
CF = CF_PATH.read_bytes()
SEM_PATH = REPO / "data/generated/ephemeral_runtime_resolution_4512000_minimal.json"
MANIFEST_PATH = REPO / "data/generated/ephemeral_runtime_target_manifest_4512000.json"
COROLLA_RANGE_PATH = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
COROLLA_SEM_PATH = REPO / "data/generated/ephemeral_runtime_resolution_8965H1202000_minimal.json"
JAVA = REPO / "ghidra/scripts/investigate/ResolveEphemeralRuntime.java"
BUILDER = REPO / "tools/security/build_ephemeral_runtime_manifest.py"
GEOMETRY_DB = REPO / "data/variant_ram_exec_requirements.json"
BOOTSTRAP_DB = REPO / "data/variant_bootstrap_profiles.json"
TARGET_CONFIG = REPO / "exploit/ephemeral_runtime/target_config.py"
BRIDGE_SOURCE = REPO / "exploit/ephemeral_runtime/main.c"
CANARY_SOURCE = REPO / "exploit/ephemeral_runtime/canary.c"
passed = failed = 0

spec = importlib.util.spec_from_file_location("ephemeral_manifest", BUILDER)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)
COROLLA_CF, COROLLA_SOURCE = mod.load_codeflash(COROLLA_RANGE_PATH)
config_spec = importlib.util.spec_from_file_location("ephemeral_target_config", TARGET_CONFIG)
config = importlib.util.module_from_spec(config_spec)
assert config_spec.loader is not None
config_spec.loader.exec_module(config)


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def rejects(fn) -> bool:
    try:
        fn()
    except mod.ManifestError:
        return True
    return False


sem = json.loads(SEM_PATH.read_text(encoding="utf-8"))

print("\n== raw completion from bare CodeFlash ==")
completed = mod.complete_raw_anchors(CF, sem)
ca = completed["anchors"]
expected = {
    "application_gp": "0xFEBEB800",
    "application_tp": "0x23EE4",
    "boot_application_handoff": "0x13B0",
    "foreground_tick_counter": "0xFEBE39DB",
    "com_rx_indication": "0x7C640",
    "com_timeout_helper": "0x8D682",
    "com_validity_base": "0xFEBE52CC",
    "com_update_counter_base": "0xFEBE532C",
    "secoc_queue_storage_helper": "0x8D74C",
    "secoc_queue1_case": "0x8D74E",
    "secoc_descriptor_base": "0xFEBE5452",
    "secoc_queue_head_base": "0xFEBE544C",
    "secoc_raw_buffer_base": "0xFEBE5488",
    "secoc_record_count": 6,
    "secoc_record_table": "0x25970",
}
check("raw completion status is exact", completed["status"] == "resolved" and completed["raw_completion"]["status"] == "complete")
check("all raw-completed anchors are exact", all(ca[k] == v for k, v in expected.items()), repr({k: ca.get(k) for k in expected}))
check("boot transition call targets are exact", ca["boot_transition_call_targets"] == ["0xC9A", "0xE54", "0xF80", "0x10C6", "0x119E"])

print("\n== raw SecOC table / derived steering profiles ==")
table = int(ca["secoc_record_table"], 0)
records = [mod.parse_record(CF, table, i) for i in range(ca["secoc_record_count"])]
check("raw Gate-2 SecOC table/count are exact", table == 0x25970 and ca["secoc_record_count"] == 6)
check("every recovered Sienna queue-1 record has Level-1 shape", all(mod.secoc_record_shape(CF, int(r["record_address"], 0)) for r in records))
check("raw SecOC IDs are exact", [int(r["can_id"], 0) for r in records] == [0x00F, 0x2E4, 0x131, 0x132, 0x090, 0x0D7])
rec_2e4, rec_131 = records[1], records[2]
check("2E4 record geometry is exact", rec_2e4["pdu_id"] == 6 and rec_2e4["raw_offset"] == "0x8" and rec_2e4["secured_length"] == 8)
check("131 record geometry is exact", rec_131["pdu_id"] == 26 and rec_131["raw_offset"] == "0x10" and rec_131["secured_length"] == 8)

m = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

print("\n== 8965H1202000 foreign-image regression ==")
check("2 MiB range dump normalizes to exact 1 MiB CodeFlash",
      len(COROLLA_CF) == 0x100000 and COROLLA_SOURCE["size"] == 0x200000 and
      COROLLA_SOURCE["normalization"] == "trim-all-ff-upper-1mib-from-2mib-range-dump" and
      hashlib.sha256(COROLLA_CF).hexdigest() == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
corolla_sem = json.loads(COROLLA_SEM_PATH.read_text(encoding="utf-8"))
corolla_completed = mod.complete_raw_anchors(COROLLA_CF, corolla_sem)
cca = corolla_completed["anchors"]
corolla_expected = {
    "application_gp": "0xFEBEB800", "application_tp": "0x23D6C",
    "boot_application_handoff": "0x1394", "foreground_tick_counter": "0xFEBE38EF",
    "com_rx_indication": "0x76A3C", "com_timeout_helper": "0x87A82",
    "com_validity_base": "0xFEBE51C4", "com_update_counter_base": "0xFEBE5224",
    "secoc_queue_storage_helper": "0x87B72", "secoc_queue1_case": "0x87B92",
    "secoc_descriptor_base": "0xFEBE5356", "secoc_queue_head_base": "0xFEBE5350",
    "secoc_raw_buffer_base": "0xFEBE5398", "secoc_record_count": 3, "secoc_record_table": "0x2572C",
}
check("foreign raw completion recovers target-specific queue/table geometry",
      all(cca[k] == v for k, v in corolla_expected.items()), repr({k: cca.get(k) for k in corolla_expected}))
corolla_records = [mod.parse_record(COROLLA_CF, int(cca["secoc_record_table"], 0), i) for i in range(cca["secoc_record_count"])]
check("foreign queue-1 record IDs are target-derived, not Sienna-assumed",
      [int(r["can_id"], 0) for r in corolla_records] == [0x00F, 0x0D7, 0x0B6] and
      all(mod.secoc_record_shape(COROLLA_CF, int(r["record_address"], 0)) for r in corolla_records))
check("software-ID extraction rejects the longer ECU-serial prefix",
      mod.extract_software_ids(COROLLA_CF) == ["8965F1208000", "8965H1202000"])

print("\n== target-driven source/build contract ==")
values = config.target_values(m)
check("target config reconstructs original Sienna boot/COM/bridge anchors",
      values["BOOT_INIT_0"] == 0xC9A and values["APP_CPU_CONTEXT_INIT"] == 0x70524 and
      values["APPLICATION_COM_RX"] == 0x7C640 and values["BRIDGE_RAW_BASE"] == 0xFEBE5490 and
      values["BRIDGE_DESC_BASE"] == 0xFEBE545A and values["BRIDGE_COUNTER_BASE"] == 0xFEBE5332)
check("target config derives Sienna canary observation from manifest evidence",
      values["CANARY_HEARTBEAT"] == 0xFEBFFBF0)
check("target config derives command-5 record/slot/mailbox from manifest evidence",
      values["COMMAND5_DISPATCH"] == 0x88350 and values["COMMAND5_DRIVER_RECORD"] == 0 and
      values["COMMAND5_KEY_SELECTOR"] == 4 and values["COMMAND5_DONE_FLAG"] == 0xFEBF13BC and
      values["COMMAND5_STATUS_FLAG"] == 0xFEBF13BD and values["COMMAND5_MAILBOX"] == 0xFEBFFB80 and
      values["COMMAND5_MAILBOX_SIZE"] == 0x80)
header = config.render_header(m)
check("generated target header carries manifest-derived anchors",
      "#define TARGET_BOOT_INIT_0 0xC9A" in header and
      "#define TARGET_APPLICATION_COM_RX 0x7C640" in header and
      "#define TARGET_CANARY_HEARTBEAT 0xFEBFFBF0" in header and
      "#define TARGET_COMMAND5_DISPATCH 0x88350" in header and
      "#define TARGET_COMMAND5_MAILBOX 0xFEBFFB80" in header)
bridge_source = BRIDGE_SOURCE.read_text(encoding="utf-8").lower()
canary_source = CANARY_SOURCE.read_text(encoding="utf-8").lower()
source_forbidden = ["0x00000c9a", "0x00070524", "0x00062760", "0x00064fcc", "0x0007c640", "0xfebe5490", "0xfebe545a", "0xfebe5332", "0xfebffbf0"]
check("bridge source contains no Sienna address constants", not any(x in bridge_source for x in source_forbidden), repr([x for x in source_forbidden if x in bridge_source]))
check("canary source contains no Sienna address constants", not any(x in canary_source for x in source_forbidden), repr([x for x in source_forbidden if x in canary_source]))
blocked = copy.deepcopy(m)
blocked["runtime_build_ready"] = False
blocked["status"] = "semantic-resolved-geometry-unresolved"
with tempfile.TemporaryDirectory(prefix="ephemeral-target-config-") as td:
    blocked_path = Path(td) / "blocked.json"
    blocked_path.write_text(json.dumps(blocked), encoding="utf-8")
    try:
        config.load_manifest(blocked_path)
        blocked_rejected = False
    except config.TargetConfigError:
        blocked_rejected = True
check("non-build-ready target is rejected before code generation", blocked_rejected)

print("\n== fail-closed mutation behavior ==")
mut = bytearray(CF); mut[0x13C8] ^= 0x01
check("boot-handoff signature mutation is rejected", rejects(lambda: mod.recover_boot_handoff(bytes(mut))))
mut = bytearray(CF); mut[0x7C640] ^= 0x01
check("Com_RxIndication signature mutation is rejected", rejects(lambda: mod.recover_com_rx(bytes(mut))))
mut = bytearray(CF); mut[0x8D754] ^= 0x01
check("SecOC queue-1 storage-case mutation is rejected", rejects(lambda: mod.recover_queue_helper(bytes(mut), 0xFEBEB800)))
mut = bytearray(CF); mut[0x8D682] ^= 0x01
check("COM timeout-helper signature mutation is rejected", rejects(lambda: mod.recover_timeout_helper(bytes(mut), 0x7C640, 0xFEBEB800)))
mut = bytearray(CF); mut[0x25970 + 0x50 + mod.PDU_ID_OFFSET + 2] ^= 0x01
check("SecOC record-shape mutation is rejected", not mod.secoc_record_shape(bytes(mut), 0x25970 + 0x50))
geometry_db = json.loads(GEOMETRY_DB.read_text(encoding="utf-8"))
check("foreign SHA cannot select Sienna geometry by variant id",
      rejects(lambda: mod.choose_geometry(geometry_db, "00" * 32, "sienna-8965b4512000")))
external = next(v for v in geometry_db["variants"] if v["id"] == "yc-newer-toyota-field-report-2026-08-16")
check("external-only geometry remains non-buildable", mod.geometry_contract(external, "variant-evidence-not-image-bound")["status"] == "unresolved")

print("\n== resolver source discipline ==")
java = JAVA.read_text(encoding="utf-8").lower()
forbidden = ["0x13b0", "0x62758", "0x70524", "0x64fcc", "0x65750", "0x7c640", "0x8d682", "0x8d74c", "0xfebe532c", "0xfebe5452", "0xfebe5488"]
check("Ghidra semantic resolver embeds no Sienna target addresses", not any(x in java for x in forbidden), repr([x for x in forbidden if x in java]))
bootstrap_db = json.loads(BOOTSTRAP_DB.read_text(encoding="utf-8"))
profile = bootstrap_db["profiles"][0]
check("bootstrap selector joins known software IDs without using CodeFlash SHA",
      mod.choose_bootstrap_profile(bootstrap_db, ["8965F4201000"])["id"] == profile["id"] and
      mod.choose_bootstrap_profile(bootstrap_db, ["8965Z9999999"]) is None)

print(f"\nResults: {passed} passed, {failed} failed")
if failed:
    raise SystemExit(1)
