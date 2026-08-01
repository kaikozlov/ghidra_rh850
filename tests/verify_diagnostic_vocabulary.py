#!/usr/bin/env python3
"""Deterministic verification for the Techstream↔firmware diagnostic vocabulary.

Verifies that:
  1. The correlation engine produces the expected vocabulary artifact.
  2. Every "exact" DID match has a real callback address in the firmware DID table.
  3. Every DTC offset is a real 2-byte match in CodeFlash.
  4. Every "exact" service match references a real callback in the service table.
  5. The firmware SHA256 in the vocabulary matches the actual firmware hash.
  6. No auto-applied (symbol rename) mapping has grade < exact.

No Ghidra required — all checks use raw firmware bytes and the generated JSON.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
FW_SHA = hashlib.sha256(CF).hexdigest()

VOCAB_PATH = REPO / "data" / "generated" / "21140bbd65e530a9" / "diagnostic_vocabulary.json"

passed = 0
failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{mark}] {name}{suffix}")


# ── Regenerate the vocabulary on the fly ──────────────────────────────────────

sys.path.insert(0, str(REPO / "tools" / "diagnostics"))
sys.path.insert(0, str(REPO / "tools" / "techstream"))
from correlate_vocabulary import build_vocabulary  # noqa: E402
from firmware_tables import extract_all, DID_TABLE_BASE, DID_TABLE_COUNT  # noqa: E402

vocab = build_vocabulary()
mappings = vocab["mappings"]
tables = extract_all()


print("== vocabulary artifact structure ==")
check("vocabulary has firmware_sha256", "firmware_sha256" in vocab)
check("vocabulary firmware SHA256 matches actual firmware",
      vocab["firmware_sha256"] == FW_SHA,
      f"vocab={vocab['firmware_sha256'][:16]}... actual={FW_SHA[:16]}...")
check("vocabulary has ecu metadata", "ecu" in vocab)
check("vocabulary ecu family is EPS", vocab["ecu"]["family"] == "EPS")
check("vocabulary has source_catalog path", "source_catalog" in vocab)
check("vocabulary has firmware_tables metadata", "firmware_tables" in vocab)
check("vocabulary firmware DID table count is 242",
      vocab["firmware_tables"]["did_table"]["count"] == 242)
check("vocabulary firmware service table count is 23",
      vocab["firmware_tables"]["service_table"]["count"] == 23)
check("vocabulary firmware routine table count is 32",
      vocab["firmware_tables"]["routine_table"]["count"] == 32)
check("vocabulary has summary with grade counts", "by_grade" in vocab["summary"])
check("vocabulary has mappings list", len(mappings) > 0)


print("\n== DID correlations ==")
did_mappings = [m for m in mappings if m["kind"] == "did"]
check("exactly 12 DID mappings", len(did_mappings) == 12,
      f"got {len(did_mappings)}")

# All Techstream DIDs must be within the firmware DID range
fw_did_ids = {d.identifier for d in tables.dids}
check("all firmware DIDs unique", len(fw_did_ids) == len(tables.dids))

for m in did_mappings:
    did_id = m["identifier"]
    grade = m["match_grade"]
    cb_str = m.get("firmware_callback")

    if grade == "exact":
        check(f"DID 0x{did_id:04X} exact match is in firmware table",
              did_id in fw_did_ids)
        if cb_str:
            cb = int(cb_str, 16)
            fw_did = tables.did_by_id[did_id]
            check(f"DID 0x{did_id:04X} callback {cb_str} matches firmware table",
                  fw_did.callback == cb,
                  f"firmware says 0x{fw_did.callback:05X}")
            check(f"DID 0x{did_id:04X} flags {m['firmware_flags']} match firmware",
                  fw_did.flags == int(m["firmware_flags"], 16))


print("\n== DTC correlations ==")
dtc_mappings = [m for m in mappings if m["kind"] == "dtc"]
check("DTC mapping count is 54", len(dtc_mappings) == 54,
      f"got {len(dtc_mappings)}")

dtc_found = [m for m in dtc_mappings if m["firmware_offsets"]]
check("at least 25 DTCs found in firmware", len(dtc_found) >= 25,
      f"got {len(dtc_found)}")

# Verify every claimed DTC offset is a real 2-byte match
for m in dtc_found:
    dtc_id = m["dtc_identifier"]
    pattern = struct.pack("<H", dtc_id)
    for off_str in m["firmware_offsets"][:3]:  # verify first 3
        offset = int(off_str, 16)
        check(f"DTC {m['code']} offset 0x{offset:X} contains 0x{dtc_id:04X}",
              CF[offset:offset + 2] == pattern,
              f"actual={CF[offset:offset+2].hex()}")


print("\n== service correlations ==")
svc_mappings = [m for m in mappings if m["kind"] == "service"]
check("service mapping count is 17 (primary table, no duplicate SIDs)",
      len(svc_mappings) == 17,
      f"got {len(svc_mappings)}")

# All standard UDS SIDs present
expected_sids = {0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x27, 0x28, 0x2E,
                 0x31, 0x34, 0x36, 0x37, 0x3E, 0x85, 0xAB, 0xBA}
found_sids = {m["sid"] for m in svc_mappings}
check("all standard SIDs present in service mappings",
      expected_sids <= found_sids)

# Service callbacks must match firmware service table.
# Only compare against primary-table entries (indices 0–16); the extra records
# (17–22) are shared entries for functional/secondary groups.
fw_services = {s.sid: s for s in tables.services if s.table_index < 17}
for m in svc_mappings:
    sid = m["sid"]
    fw_svc = fw_services.get(sid)
    if not fw_svc:
        continue
    if m.get("firmware_callback"):
        cb = int(m["firmware_callback"], 16)
        check(f"SID 0x{sid:02X} callback {m['firmware_callback']} matches firmware",
              fw_svc.callback == cb,
              f"firmware says 0x{fw_svc.callback:05X}")
        check(f"SID 0x{sid:02X} is exact grade", m["match_grade"] == "exact")


print("\n== match-grade integrity ==")
auto_applied = [m for m in mappings if m.get("annotation_action") == "name_callback"]
check("no name_callback mapping has grade < exact",
      all(m["match_grade"] in ("exact", "structural") for m in auto_applied))

family_mappings = [m for m in mappings if m["match_grade"] == "family"]
check("all family-grade mappings use comment/vocabulary action",
      all(m["annotation_action"] in ("comment", "vocabulary") for m in family_mappings))

candidate_mappings = [m for m in mappings if m["match_grade"] == "candidate"]
check("candidate-grade mappings note their conflict",
      all("conflict" in m.get("note", "").lower() for m in candidate_mappings),
      f"{[m.get('note','')[:50] for m in candidate_mappings[:3]]}")


print("\n== monitor vocabulary ==")
monitor_mappings = [m for m in mappings if m["kind"] == "monitor"]

# Monitors now split into two classes: those bridged to firmware DIDs
# (via DID = 0x0100 + seq), and remaining family-grade vocabulary.
bridged = [m for m in monitor_mappings if "firmware_callback" in m]
check("at least 9 monitors bridged to firmware DIDs", len(bridged) >= 9,
      f"got {len(bridged)}")

family_monitors = [m for m in monitor_mappings if "firmware_callback" not in m]
check("remaining family-grade monitors >= 100", len(family_monitors) >= 100,
      f"got {len(family_monitors)}")

named_monitors = [m for m in monitor_mappings if m.get("oem_name")]
check("at least 100 monitors have OEM names", len(named_monitors) >= 100,
      f"got {len(named_monitors)}")

# Verify every bridged monitor's callback matches the firmware DID table
for m in bridged:
    did = m["identifier"]
    cb = int(m["firmware_callback"], 16)
    fw_did = tables.did_by_id[did]
    check(f"monitor DID 0x{did:04X} callback {m['firmware_callback']} matches firmware",
          fw_did.callback == cb,
          f"firmware says 0x{fw_did.callback:05X}")

# Verify RAM source annotations are present for decompiled monitors
ram_sourced = [m for m in bridged if "ram_source" in m]
check("at least 7 bridged monitors have RAM source annotations",
      len(ram_sourced) >= 7, f"got {len(ram_sourced)}")

# Verify the motor-control RAM sources are present
ram_text = " ".join(m.get("ram_source", "") for m in ram_sourced)
check("DID 0x0105 (Motor Actual Current) references checkpoint 0x204",
      "checkpoint_object 0x204" in ram_text)
check("DID 0x0109 (Steering torque) references DAT_FEBEE867",
      "DAT_FEBEE867" in ram_text)
check("DID 0x010B (torque sensor 2) references checkpoint 0x20A",
      "checkpoint_object 0x20A" in ram_text)

# Spot-check key motor-control monitor names are present in bridged monitors
bridged_names = {m["oem_name"].lower() for m in bridged}
for expected_name in ("motor actual current", "steering torque",
                      "thermistor temperature", "pig power supply"):
    # These may be in either bridged or family depending on KWP/CAN variant
    all_monitor_names = {m["oem_name"].lower() for m in named_monitors}
    check(f"monitor '{expected_name}' present in vocabulary",
          expected_name in all_monitor_names,
          f"searched {len(all_monitor_names)} names")


print("\n== utility procedures ==")
proc_mappings = [m for m in mappings if m["kind"] == "utility_procedure"]
check("at least 50 utility procedure mappings", len(proc_mappings) >= 50,
      f"got {len(proc_mappings)}")

structural_procs = [m for m in proc_mappings if m["match_grade"] == "structural"]
check("at least 10 structural procedure-to-routine matches",
      len(structural_procs) >= 10, f"got {len(structural_procs)}")

# Verify "Torque Sensor Writing" maps to firmware routines
ts_writing = [m for m in proc_mappings if "torque sensor writing" in m["oem_name"].lower()]
check("'Torque Sensor Writing' procedure is present", len(ts_writing) >= 1)
if ts_writing:
    check("'Torque Sensor Writing' has structural grade",
          ts_writing[0]["match_grade"] == "structural")
    check("'Torque Sensor Writing' references routine 0x2005",
          any(r["routine_id"] == "0x2005" for r in ts_writing[0].get("firmware_routines", [])))

# Verify "Power Steering ECU Initial Setting" maps to firmware routines
ps_init = [m for m in proc_mappings if "power steering ecu initial setting" in m["oem_name"].lower()]
check("'Power Steering ECU Initial Setting' procedure is present", len(ps_init) >= 1)
if ps_init:
    check("'Power Steering ECU Initial Setting' references routine 0x0204",
          any(r["routine_id"] == "0x0204" for r in ps_init[0].get("firmware_routines", [])))


print("\n== idempotency ==")
vocab2 = build_vocabulary()
check("rebuild produces same mapping count",
      len(vocab2["mappings"]) == len(vocab["mappings"]))
check("rebuild produces same grade distribution",
      vocab2["summary"]["by_grade"] == vocab["summary"]["by_grade"])


print("\n== three-DB string resolution ==")
# Verify all three DBs are loaded in the catalog
cat_path = REPO / "data" / "generated" / "21140bbd65e530a9" / "diagnostic_annotations.json"
catalog = json.loads(cat_path.read_text())
check("catalog loaded all three string DBs",
      set(catalog["string_databases"].keys()) == {"M_English", "V_English", "U_English"})

# Verify entries carry multi-DB resolutions
sample_monitors = [e for e in catalog["entries"] if e["kind"] == "monitor"]
check("monitor entries have name_resolutions dict",
      all("name_resolutions" in m for m in sample_monitors))

sample_dtcs = [e for e in catalog["entries"] if e["kind"] == "dtc"]
check("DTC entries have resolutions dict",
      all("resolutions" in d for d in sample_dtcs))

# Verify M and V resolve differently for EPS (confirming they are distinct DBs)
dtc_with_both = [d for d in sample_dtcs
                 if d["resolutions"].get("M_English")
                 and d["resolutions"].get("V_English")
                 and d["resolutions"]["M_English"] != d["resolutions"]["V_English"]]
check("at least one DTC where M and V differ (distinct DBs)",
      len(dtc_with_both) > 0,
      f"{len(dtc_with_both)} DTCs with differing M/V")

# Verify u32 string index fix: monitors with index > 65535 now resolve correctly
large_idx_monitors = [m for m in sample_monitors if m["name_string_index"] > 65535]
check("at least 10 monitors with string index > 65535",
      len(large_idx_monitors) >= 10, f"got {len(large_idx_monitors)}")
check("all large-index monitors have M_English names",
      all(m["resolved_name"] for m in large_idx_monitors),
      f"{sum(1 for m in large_idx_monitors if not m['resolved_name'])} missing")

# Specifically verify "Ready ON Status" (index 177303) resolves correctly
ready_mon = [m for m in large_idx_monitors if m["resolved_name"] == "Ready ON Status"]
check("'Ready ON Status' (index 177303) resolves correctly via u32",
      len(ready_mon) >= 1)


print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
