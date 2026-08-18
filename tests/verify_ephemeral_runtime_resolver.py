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
COROLLA_GATE_PATH = REPO / "data/generated/secoc_gate_resolution_8965H1202000_minimal.json"
COROLLA_MANIFEST_PATH = REPO / "data/generated/ephemeral_runtime_target_manifest_8965H1202000.json"
JAVA = REPO / "ghidra/scripts/investigate/ResolveEphemeralRuntime.java"
BUILDER = REPO / "tools/build_ephemeral_runtime_manifest.py"
WRAPPER = REPO / "tools/resolve_ephemeral_runtime_image.sh"
GEOMETRY_DB = REPO / "data/variant_ram_exec_requirements.json"
BOOTSTRAP_DB = REPO / "data/variant_bootstrap_profiles.json"
COMMUNITY_PATCHER = REPO / "community/blurbdust_secoc_flash_patcher/flash_patcher.py"
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


print("== committed fresh-import semantic result ==")
sem = json.loads(SEM_PATH.read_text(encoding="utf-8"))
check("bare import resolves one control skeleton", sem["status"] == "control-resolved" and sem["candidate_count"] == 1)
check("bare import Gate-2 owner is exact", int(sem["gate_entry"], 0) == 0x8E67A)
a = sem["anchors"]
check("startup/context anchors are exact", a["startup_coordinator"] == "0x62758" and a["application_context_init"] == "0x70524")
check("startup JARL span/count are exact", a["startup_jarl_first"] == "0x62760" and a["startup_jarl_after"] == "0x627B4" and a["startup_jarl_count"] == 21)
check("startup final init is exact", a["startup_final_init"] == "0x6F15A")
check("foreground loop/tick primitive are exact", a["foreground_loop"] == "0x64FCC" and a["tick_bit"] == 4 and a["tick_displacement"] == -20207)
check("foreground call list is exact", a["foreground_call_targets"] == [
    "0x63E7C", "0x643AC", "0x702E8", "0x65F5C", "0x70308",
    "0x65750", "0x702E8", "0x65C60", "0x70308", "0x64080",
])
check("aggregate index and six-call list are exact",
      a["foreground_aggregate_call_index"] == 5 and a["aggregate"] == "0x65750" and
      a["aggregate_call_targets"] == ["0x68C0C", "0x791C4", "0x96BAC", "0x68DE6", "0x57AC2", "0x6547C"])
check("bare import intentionally leaves pointer-table/RAM anchors unresolved",
      a["com_rx_indication"] == "" and a["secoc_queue_storage_helper"] == "" and a["foreground_tick_counter"] == "null")

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

print("\n== committed joined target manifest ==")
m = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
check("manifest is SHA-bound to exact Sienna CodeFlash", m["image"]["sha256"] == hashlib.sha256(CF).hexdigest() and m["image"]["size"] == 0x100000)
check("manifest extracts Sienna software ID from raw CodeFlash", "8965B4512000" in m["image"].get("software_ids", []))
bootstrap = m.get("authenticated_bootstrap_profile")
check("manifest binds shared authenticated-RAM bootstrap profile",
      bootstrap is not None and bootstrap["id"] == "denso-p1me-f05f-zero-did-febf-v1")
check("bootstrap profile pins recovered shared f05f SecurityAccess secret",
      bootstrap["security_access_secret"] == "f05f36b7d78c03e24ab4faef2a57d044")
check("bootstrap profile keeps exact Sienna fixture identity separate",
      bootstrap["matched_evidence"][0].get("exact_fixture_sha256") == "d972d4bf432685217591768600a9abd7820d35b04a72270edc87074365356be2" and
      "Exact byte-for-byte acceptance" in bootstrap["boundary"])
check("manifest is runtime-build-ready only with verified geometry and steering profiles",
      m["status"] == "runtime-build-ready" and m["runtime_build_ready"] is True and
      m["ram_execution_geometry"]["status"] == "verified" and m["secoc_records"]["steering_bridge_applicable"] is True)
check("retained geometry is exact", m["ram_execution_geometry"]["retained_application_rwx_base"] == "0xFEBF0000" and m["ram_execution_geometry"]["retained_application_rwx_end_exclusive"] == "0xFEBF0308")
profiles = m["secoc_records"]["steering_bridge_profiles"]
check("manifest derives 2E4 bridge addresses", profiles[0]["can_id"] == "0x2E4" and profiles[0]["raw_buffer_address"] == "0xFEBE5490" and profiles[0]["descriptor_address"] == "0xFEBE545A" and profiles[0]["update_counter_address"] == "0xFEBE5332")
check("manifest derives 131 bridge addresses", profiles[1]["can_id"] == "0x131" and profiles[1]["raw_buffer_address"] == "0xFEBE5498" and profiles[1]["descriptor_address"] == "0xFEBE5462" and profiles[1]["update_counter_address"] == "0xFEBE5346")
check("manifest carries target-specific canary observation evidence",
      m["ram_execution_geometry"]["canary_observation_address"] == "0xFEBFFBF0" and
      m["ram_execution_geometry"]["canary_observation_method"] == "application-rmba-or-xcp-read")

print("\n== 8965H1202000 foreign-image regression ==")
check("2 MiB range dump normalizes to exact 1 MiB CodeFlash",
      len(COROLLA_CF) == 0x100000 and COROLLA_SOURCE["size"] == 0x200000 and
      COROLLA_SOURCE["normalization"] == "trim-all-ff-upper-1mib-from-2mib-range-dump" and
      hashlib.sha256(COROLLA_CF).hexdigest() == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
corolla_sem = json.loads(COROLLA_SEM_PATH.read_text(encoding="utf-8"))
check("foreign bare import independently resolves one control skeleton",
      corolla_sem["status"] == "control-resolved" and corolla_sem["candidate_count"] == 1 and
      int(corolla_sem["gate_entry"], 0) == 0x88C16)
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
corolla_gate = json.loads(COROLLA_GATE_PATH.read_text(encoding="utf-8"))
check("foreign Gate-2 patch resolves uniquely at 0x88C62",
      corolla_gate["resolution"] == "unique" and corolla_gate["patch"] == {
          "address": "0x00088c62", "original": "e0d1", "replacement": "e001",
          "operation": "cmp-second-register-to-first-force-fallthrough"})
cm = json.loads(COROLLA_MANIFEST_PATH.read_text(encoding="utf-8"))
check("foreign manifest is a successful non-steering capability result, not a resolver error",
      cm["status"] == "semantic-resolved-steering-unsupported" and cm["runtime_build_ready"] is False and
      cm["secoc_records"]["steering_bridge_applicable"] is False and
      cm["secoc_records"]["steering_bridge_missing_ids"] == ["0x2E4", "0x131"] and
      cm["secoc_records"]["steering_bridge_profiles"] == [])
check("foreign manifest binds observed authenticated-RAM bootstrap evidence",
      cm["authenticated_bootstrap_profile"]["matched_evidence"] == [next(
          row for row in json.loads(BOOTSTRAP_DB.read_text(encoding="utf-8"))["profiles"][0]["evidence"]
          if row.get("software_id") == "8965H1202000")])

print("\n== target-driven source/build contract ==")
values = config.target_values(m)
check("target config reconstructs original Sienna boot/COM/bridge anchors",
      values["BOOT_INIT_0"] == 0xC9A and values["APP_CPU_CONTEXT_INIT"] == 0x70524 and
      values["APPLICATION_COM_RX"] == 0x7C640 and values["BRIDGE_RAW_BASE"] == 0xFEBE5490 and
      values["BRIDGE_DESC_BASE"] == 0xFEBE545A and values["BRIDGE_COUNTER_BASE"] == 0xFEBE5332)
check("target config derives Sienna canary observation from manifest evidence",
      values["CANARY_HEARTBEAT"] == 0xFEBFFBF0)
header = config.render_header(m)
check("generated target header carries manifest-derived anchors",
      "#define TARGET_BOOT_INIT_0 0xC9A" in header and
      "#define TARGET_APPLICATION_COM_RX 0x7C640" in header and
      "#define TARGET_CANARY_HEARTBEAT 0xFEBFFBF0" in header)
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
wrapper = WRAPPER.read_text(encoding="utf-8")
check("wrapper uses disposable build project, not committed project", "build/ephemeral-runtime-targets" in wrapper and 'ResolveSecocAcceptanceGate.java' in wrapper and 'ResolveEphemeralRuntime.java' in wrapper and "project/" not in wrapper)
check("wrapper runs Gate-2 before runtime semantic resolver", wrapper.index("ResolveSecocAcceptanceGate.java") < wrapper.index("ResolveEphemeralRuntime.java"))
check("wrapper normalizes tracked 2 MiB trailing-FF range dumps without modifying source",
      "load_codeflash" in wrapper and "normalized-CodeFlash.bin" in wrapper and "IMPORT_IMAGE" in wrapper)
check("manifest builder never defaults a foreign image to Sienna geometry", "no-image-bound-geometry" in BUILDER.read_text(encoding="utf-8"))
bootstrap_db = json.loads(BOOTSTRAP_DB.read_text(encoding="utf-8"))
profile = bootstrap_db["profiles"][0]
evidence_ids = {row.get("software_id") for row in profile["evidence"]}
check("bootstrap evidence covers established B4 and published F3/F4 targets",
      {"8965B4514000", "8965B4209000", "8965B4233100", "8965B4509100",
       "8965F3401200", "8965F4207000", "8965F4201000"} <= evidence_ids)
check("bootstrap evidence keeps exact-local fixture proof distinct from foreign evidence",
      all(row["grade"] in {"observed", "external-source"} for row in profile["evidence"] if row.get("software_id") != "8965B4512000") and
      next(row for row in profile["evidence"] if row.get("software_id") == "8965H1202000")["grade"] == "observed")
patcher = COMMUNITY_PATCHER.read_text(encoding="utf-8").lower()
check("published F3/F4 patcher uses shared f05f/zero-DID/FEBF/10F0 bootstrap",
      "f05f36b7d78c03e24ab4faef2a57d044" in patcher.replace("\\x", "") or
      ("\\xf0\\x5f\\x36\\xb7" in patcher and "0xfebf0000" in patcher and "0x10f0" in patcher))
for software_id in ("8965F3401200", "8965F4207000", "8965F4201000"):
    check(f"published patcher lists {software_id}", software_id.lower() in patcher)
check("bootstrap selector joins known software IDs without using CodeFlash SHA",
      mod.choose_bootstrap_profile(bootstrap_db, ["8965F4201000"])["id"] == profile["id"] and
      mod.choose_bootstrap_profile(bootstrap_db, ["8965Z9999999"]) is None)

print(f"\nResults: {passed} passed, {failed} failed")
if failed:
    raise SystemExit(1)
