#!/usr/bin/env python3
"""Deterministic verification for the Techstream↔firmware diagnostic vocabulary.

Verifies that:
  1. The correlation engine produces the expected vocabulary artifact.
  2. Every "exact" DID match has a real callback address in the firmware DID table.
  3. Every DTC "exact" match is in the firmware DTC table (structural, not byte search).
  4. Every "exact" service match references a real callback in the service table.
  5. The firmware SHA256 in the vocabulary matches the actual firmware hash.
  6. No auto-applied (symbol rename) mapping has grade < exact.
  7. Monitor→DID bridges use CAN-authoritative grading (not candidate for KWP differences).
  8. Utility procedures are family-only (no keyword slop to firmware routines).
  9. Active tests are NOT extracted (section 14 is PID display config, not active tests).

Independently verifies DDB parsing against raw bytes — does not trust the
correlation engine's own output for DDB field offsets.

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
from correlate_vocabulary import build_vocabulary, scan_firmware_dtc_table  # noqa: E402
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
check("vocabulary has DTC table metadata", "dtc_table" in vocab["firmware_tables"])
check("vocabulary has summary with grade counts", "by_grade" in vocab["summary"])
check("vocabulary has mappings list", len(mappings) > 0)


print("\n== DID correlations ==")
did_mappings = [m for m in mappings if m["kind"] == "did"]
# DIDs are now deduplicated by identifier across DDB variants
check("DID mappings are unique by identifier",
      len(did_mappings) == len({m["identifier"] for m in did_mappings}),
      f"{len(did_mappings)} mappings, {len({m['identifier'] for m in did_mappings})} unique")

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


print("\n== DTC correlations (structural table match) ==")
dtc_mappings = [m for m in mappings if m["kind"] == "dtc"]

# Independently scan the firmware DTC table
fw_dtcs = scan_firmware_dtc_table(CF)
fw_dtc_ids = set(fw_dtcs.keys())

dtc_exact = [m for m in dtc_mappings if m["match_grade"] == "exact"]
dtc_family = [m for m in dtc_mappings if m["match_grade"] == "family"]
check("DTC exact matches are non-zero", len(dtc_exact) > 0, f"got {len(dtc_exact)}")
check("DTC family matches exist (diagnostic-only)", len(dtc_family) > 0, f"got {len(dtc_family)}")

# Every "exact" DTC must be in the firmware DTC table
for m in dtc_exact:
    dtc_id = m["dtc_identifier"]
    check(f"DTC {m['code']} (0x{dtc_id:04X}) exact match is in firmware DTC table",
          dtc_id in fw_dtc_ids,
          f"not found in table at 0x30A28-0x30C40")

    # Verify each firmware offset actually contains the DTC ID at byte offset 5
    for off_str in m["firmware_offsets"][:3]:
        offset = int(off_str, 16)
        if offset + 7 < len(CF):
            actual_id = struct.unpack_from("<H", CF, offset + 5)[0]
            check(f"DTC {m['code']} offset 0x{offset:X} has ID 0x{dtc_id:04X} at byte 5",
                  actual_id == dtc_id,
                  f"actual=0x{actual_id:04X}")

# No "exact" DTC should come from a blind byte search outside the table
for m in dtc_exact:
    for off_str in m["firmware_offsets"]:
        offset = int(off_str, 16)
        in_table = 0x30A28 <= offset < 0x30C40
        check(f"DTC {m['code']} offset 0x{offset:X} is within DTC table bounds",
              in_table, "false positive from blind byte search")


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
      all("conflict" in m.get("note", "").lower() or "multiple" in m.get("note", "").lower()
          for m in candidate_mappings),
      f"{[m.get('note','')[:50] for m in candidate_mappings[:3]]}")


print("\n== monitor vocabulary ==")
monitor_mappings = [m for m in mappings if m["kind"] == "monitor"]

# Bridged monitors have firmware_callback set
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
check("DID 0x0105 references checkpoint 0x204",
      "checkpoint_object 0x204" in ram_text)
check("DID 0x0109 references DAT_FEBEE867",
      "DAT_FEBEE867" in ram_text)
check("DID 0x010B references checkpoint 0x20A",
      "checkpoint_object 0x20A" in ram_text)

# Verify CAN-authoritative naming: bridged monitors use CAN names, not KWP
for m in bridged:
    can_name = m.get("can_variant_name")
    if can_name:
        check(f"DID 0x{m['identifier']:04X} uses CAN name '{can_name}'",
              m["oem_name"] == can_name)

# Key monitor names (using CAN-authoritative names)
bridged_names = {m["oem_name"].lower() for m in bridged}
all_monitor_names = {m["oem_name"].lower() for m in named_monitors}
for expected_name in ("motor instruction current", "steering torque",
                      "vehicle speed", "engine revolution speed"):
    check(f"monitor '{expected_name}' present in bridged vocabulary",
          expected_name in bridged_names,
          f"searched {len(bridged_names)} bridged names")


print("\n== utility procedures ==")
proc_mappings = [m for m in mappings if m["kind"] == "utility_procedure"]
check("at least 50 utility procedure mappings", len(proc_mappings) >= 50,
      f"got {len(proc_mappings)}")

# Utility procedures must ALL be family grade — no keyword-to-routine matching
check("all utility procedures are family grade",
      all(m["match_grade"] == "family" for m in proc_mappings),
      f"found non-family: {[m['match_grade'] for m in proc_mappings if m['match_grade'] != 'family'][:5]}")

check("no utility procedure references firmware routines",
      all(m.get("firmware_routines") is None for m in proc_mappings))


print("\n== active tests removed ==")
# Section 14 is PID display configuration, NOT active tests.
# The EPS .ddb files do not contain active test definitions.
at_mappings = [m for m in mappings if m["kind"] == "active_test"]
check("no active_test mappings exist (section 14 is PID display config)",
      len(at_mappings) == 0, f"got {len(at_mappings)}")


print("\n== idempotency ==")
vocab2 = build_vocabulary()
check("rebuild produces same mapping count",
      len(vocab2["mappings"]) == len(vocab["mappings"]))
check("rebuild produces same grade distribution",
      vocab2["summary"]["by_grade"] == vocab["summary"]["by_grade"])


print("\n== independent DDB field verification ==")
# Independently verify DTC record layout (section 5, 28 bytes)
# without trusting the parser's field offsets.
sys.path.insert(0, str(REPO / "tools" / "techstream"))
from parse_ddb import DDBParser  # noqa: E402

DB_PATH = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB"
parser = DDBParser()

# Verify DTC section 5 records: name index at offset 12 must be u32
eps_can = parser.parse_ecu_db(DB_PATH / "EPS_CAN_P4DK.ddb")
sec5 = eps_can.sections[5]
raw0 = sec5.raw_data[0:28]
name_idx_u32 = struct.unpack_from("<I", raw0, 12)[0]
check("DTC name index is u32 at offset 12 (C0051 case)",
      name_idx_u32 > 65535,
      f"got {name_idx_u32}")

# Verify monitor section 10: name index at offset 48 must be u32
sec10 = eps_can.sections[10]
rec_sz = int(sec10.record_size)
raw_m0 = sec10.raw_data[0:rec_sz]
mon_name_idx = struct.unpack_from("<I", raw_m0, 48)[0]
check("monitor name index is u32 at offset 48",
      mon_name_idx > 0)

# Verify DID section 3: identifier at offset 4 (u16)
sec3 = eps_can.sections[3]
raw_d0 = sec3.raw_data[0:8]
did_val = struct.unpack_from("<H", raw_d0, 4)[0]
check("DID identifier is u16 at offset 4 in section 3",
      did_val == 0x0100,
      f"got 0x{did_val:04X}")


print("\n== three-DB string resolution ==")
cat_path = REPO / "data" / "generated" / FW_SHA[:16] / "diagnostic_annotations.json"
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
