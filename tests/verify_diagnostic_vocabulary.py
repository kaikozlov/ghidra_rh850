#!/usr/bin/env python3
"""Deterministic verification for the Techstream↔firmware diagnostic vocabulary.

Verifies that:
  1. The correlation engine produces the expected vocabulary artifact.
  2. Every "exact" DID match has a real callback address in the firmware DID table.
  3. Every DTC "exact" match is in the firmware DTC table, preserving the UDS failure-type byte and Dem-event links.
  4. Every "exact" service match references a real callback in the service table.
  5. The firmware SHA256 in the vocabulary matches the actual firmware hash.
  6. Auto-applied mappings are exact or independently recovered structural matches.
  7. Monitor→DID bridges do not overstate vocabulary identity as exact.
  8. U_English steering strings are family-only (no guessed firmware binding).
  9. Active tests are NOT extracted (section 14 is PID display config, not active tests).

Independently verifies DDB parsing against raw bytes — does not trust the
correlation engine's own output for DDB field offsets.

No Ghidra required — all checks use raw firmware bytes and the generated JSON.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import struct
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
FW_SHA = hashlib.sha256(CF).hexdigest()

passed = 0
failed = 0
oracle = "generated_self_check"


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{mark}][{oracle}] {name}{suffix}")


# ── Regenerate the vocabulary on the fly ──────────────────────────────────────

sys.path.insert(0, str(REPO / "tools" / "diagnostics"))
sys.path.insert(0, str(REPO / "tools" / "techstream"))
from correlate_vocabulary import (  # noqa: E402
    DTC_EVENT_TABLE_COUNT,
    DTC_EVENT_TABLE_START,
    DTC_TABLE_END,
    DTC_TABLE_START,
    build_vocabulary,
    scan_firmware_dtc_event_links,
    scan_firmware_dtc_table,
)
import extract_catalog as extract_catalog_module  # noqa: E402
from firmware_tables import (  # noqa: E402
    DID_TABLE_BASE,
    DID_TABLE_COUNT,
    extract_all,
    extract_services,
)
from extract_catalog import build_catalog  # noqa: E402
from extract_p4dk4_catalog import build_p4dk4_catalog  # noqa: E402
from extract_steering_corpus import build_steering_corpus  # noqa: E402

generated_dir = REPO / "data" / "generated" / FW_SHA[:16]
committed_catalog = json.loads(
    (generated_dir / "diagnostic_annotations.json").read_text()
)
committed_vocab = json.loads(
    (generated_dir / "diagnostic_vocabulary.json").read_text()
)
TECHSTREAM_ROOT = Path(os.environ.get(
    "TECHSTREAM_DDB_ROOT",
    REPO / "Techstream" / "unpacked" / "toyota" / "Toyota Diagnostics"
    / "Techstream",
))
ALLOW_EXTERNAL = os.environ.get("RH850_VERIFY_EXTERNAL") == "1"
HAS_TECHSTREAM_SOURCE = ALLOW_EXTERNAL and all(
    (TECHSTREAM_ROOT / region / "DB" / filename).is_file()
    for region, filename in (
        ("NA", "EPS_P4DK3.ddb"),
        ("NA", "EPS_CAN_P4DK.ddb"),
        ("NA", "M_English.ddb"),
        ("NA", "V_English.ddb"),
        ("NA", "U_English.ddb"),
    )
)
vocab = build_vocabulary() if HAS_TECHSTREAM_SOURCE else committed_vocab
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
check("vocabulary firmware service table base is corrected runtime base",
      vocab["firmware_tables"]["service_table"] == {"base": "0x25E28", "count": 23})
check("vocabulary firmware WDBI callback table is 13 active rows",
      vocab["firmware_tables"]["wdbi_callback_table"] == {"base": "0x25768", "count": 13})
check("vocabulary firmware RoutineControl table is 19 RID rows",
      vocab["firmware_tables"]["routine_control_table"] == {"base": "0x26AEC", "count": 19})
check("vocabulary has DTC table metadata", "dtc_table" in vocab["firmware_tables"])
check("firmware DTC table metadata covers 0xA0 records from 0x309DC",
      vocab["firmware_tables"]["dtc_table"] == {
          "base": "0x309DC",
          "end": "0x30EDC",
          "count": 0xA0,
          "record_size": 8,
          "failure_type_offset": 0,
          "dtc_identifier_offset": 1,
      })
check("vocabulary has Dem event table metadata",
      vocab["firmware_tables"]["dtc_event_table"] == {
          "base": "0x2FDDC",
          "count": 0x180,
          "record_size": 8,
          "dtc_table_index_offset": 2,
      })
check("vocabulary has summary with grade counts", "by_grade" in vocab["summary"])
check("vocabulary has mappings list", len(mappings) > 0)
if HAS_TECHSTREAM_SOURCE:
    check("committed catalog exactly matches deterministic rebuild",
          committed_catalog == build_catalog())
    check("committed vocabulary exactly matches deterministic rebuild",
          committed_vocab == vocab)
else:
    print("[SKIP] exact DDB artifact rebuild (proprietary source absent)")
check("DID mappings do not expose the disproved firmware_flags field",
      all("firmware_flags" not in mapping
          for mapping in mappings if mapping["kind"] in ("did", "monitor")))

consumer_source = (
    REPO / "ghidra" / "scripts" / "annotate" / "ApplyDiagnosticVocabulary.java"
).read_text()
assertion_source = (
    REPO / "ghidra/scripts/verify/AssertDiagnosticVocabulary.java"
).read_text()
rebuild_source = (REPO / "tools/rebuild_project.sh").read_text()
seed_source = (
    REPO / "ghidra" / "scripts" / "seed" / "SeedDidCallbacks.java"
).read_text()
check("Java consumer accepts structural callback mappings",
      'grade.equals("structural")' in consumer_source)
check("Java consumer fails closed on a missing exact/structural callback",
      "missing \" + grade + \" callback function" in consumer_source)
check("Java consumer deduplicates exact comment text, not the Techstream namespace",
      "existing.contains(text)" in consumer_source
      and 'existing.contains("Techstream")' not in consumer_source)
check("rebuild seeds DID callbacks before applying vocabulary",
      "-preScript SeedDidCallbacks.java" in rebuild_source
      and "-postScript ApplyDiagnosticVocabulary.java" in rebuild_source)
check("rebuild asserts applied vocabulary against decompiler landmarks",
      "-postScript AssertDiagnosticVocabulary.java" in rebuild_source
      and "[RAM source]" in assertion_source
      and "LANDMARKS" in assertion_source)
check("clean rebuild uses tracked vocabulary without proprietary source",
      "Using tracked diagnostic vocabulary artifact" in rebuild_source
      and "REFRESH_DIAGNOSTIC_VOCABULARY" in rebuild_source)
check("durable DID seed is limited to seven independently verified callbacks",
      "STRUCTURAL_CALLBACKS.length" in seed_source
      and all(f"0x{address:x}L" in seed_source
              for address in (0x4CBFC, 0x4CC76, 0x4CCC4, 0x4CD38,
                              0x4CD74, 0x4CDD4, 0x4CE00)))
check("durable DID seed does not create all 242 table callbacks",
      "0xF2" not in seed_source and "DID_TABLE_BASE" not in seed_source)


print("\n== independent firmware-table field semantics ==")
oracle = "raw_bytes"
did_by_id = tables.did_by_id
check("DID 0x0100 response-size/attribute is 0x20",
      did_by_id[0x0100].response_size_or_attribute == 0x20)
check("identification DID sizes/attributes are 0x11, 0x01, 0x14",
      [did_by_id[did].response_size_or_attribute
       for did in (0xF181, 0xF186, 0xF18C)] == [0x11, 0x01, 0x14])
check("DID 0x0102 attribute 0x07 is not a write-access bitfield",
      did_by_id[0x0102].response_size_or_attribute == 0x07
      and 0x0102 not in {entry.identifier for entry in tables.wdbi_callbacks})

primary_services = {
    entry.sid: entry for entry in tables.services if entry.table_index < 17
}
expected_service_sessions = {
    0x10: [1, 2, 3],
    0x22: [1, 2, 3],
    0x31: [1, 2, 3],
    0x3E: [1, 2, 3],
}
check("service session counts come from byte 11",
      all(primary_services[sid].sessions == sessions
          for sid, sessions in expected_service_sessions.items()))
check("service routing-mode byte is retained separately from session count",
      primary_services[0x22].subfunction_mode == 0
      and primary_services[0x22].session_count == 3)
check("corrected primary direct-service callback ownership is exact",
      {sid: primary_services[sid].callback for sid in (0x14,0x22,0x23,0x2E,0x31,0xBA)}
      == {0x14:0x8B1F0,0x22:0x945DC,0x23:0x948AA,0x2E:0x93C62,0x31:0x95DCE,0xBA:0x8D344})
check("WDBI lower table has exact 13 implemented DIDs",
      [entry.identifier for entry in tables.wdbi_callbacks]
      == [0x0204,0x2001,0x2002,0x2005,0x2006,0x2007,0x2008,0x2009,0x200D,0x2010,0x2012,0x2013,0x2014])
check("RoutineControl table has 19 RIDs 1000..110D",
      len(tables.routine_control) == 19
      and tables.routine_control[0].identifier == 0x1000
      and tables.routine_control[-1].identifier == 0x110D)

modified_cf = bytearray(CF)
sid22 = primary_services[0x22]
modified_cf[sid22.session_list_ptr:sid22.session_list_ptr + 3] = b"\x09\x08\x07"
modified_sid22 = next(
    entry for entry in extract_services(bytes(modified_cf))
    if entry.table_index < 17 and entry.sid == 0x22
)
check("alternate firmware service extraction does not reread global Sienna bytes",
      modified_sid22.sessions == [9, 8, 7], f"got {modified_sid22.sessions}")

raw_dtc_records = [
    struct.unpack_from("<BHBI", CF, 0x309DC + index * 8)
    for index in range(0xA0)
]
check("raw DTC table is 0xA0 aligned records at 0x309DC",
      len(raw_dtc_records) == 0xA0
      and all(enabled in (0, 1) and pad == 0
              for _flags, _dtc_id, pad, enabled in raw_dtc_records))
check("raw DTC table contains enabled entries beyond old 0x30C40 bound",
      any(enabled == 1 and dtc_id == 0xC100
          for _failure_type, dtc_id, _pad, enabled in raw_dtc_records))
check("U023A base record is index 92 with failure type 0x00",
      raw_dtc_records[92] == (0x00, 0xC23A, 0x00, 1),
      f"got {raw_dtc_records[92]}")
check("U023A87 record is index 93 with failure type 0x87",
      raw_dtc_records[93] == (0x87, 0xC23A, 0x00, 1),
      f"got {raw_dtc_records[93]}")

raw_event_links = scan_firmware_dtc_event_links(CF)
check("firmware Dem event table covers 0x180 records",
      DTC_EVENT_TABLE_COUNT == 0x180 and DTC_EVENT_TABLE_START == 0x2FDDC)
check("no configured Dem event maps directly to base U023A record index 92",
      raw_event_links.get(92, []) == [],
      f"got {raw_event_links.get(92, [])}")
check("five configured Dem events map specifically to U023A87 record index 93",
      raw_event_links.get(93, []) == [0xB0, 0xB3, 0x138, 0x13C, 0x13D],
      f"got {raw_event_links.get(93, [])}")
for event_id in [0xB0, 0xB3, 0x138, 0x13C, 0x13D]:
    off = DTC_EVENT_TABLE_START + event_id * 8
    check(f"Dem event 0x{event_id:X} raw record points to DTC index 93",
          CF[off + 2] == 93,
          f"record={CF[off:off + 8].hex()}")

check("catalog has no wall-clock generated_at field", "generated_at" not in committed_catalog)
check("vocabulary has no wall-clock generated_at field", "generated_at" not in committed_vocab)
check("neutral catalog does not infer sparse DID-table membership from bounds",
      "dids_in_firmware" not in committed_catalog["summary"]
      and all("in_firmware_table" not in entry
              for entry in committed_catalog["entries"]))
catalog_supported_pids = [
    entry for entry in committed_catalog["entries"]
    if entry["kind"] == "supported_pid_record"
]
check("catalog preserves all 12 selected CDbSupPidTable rows",
      len(catalog_supported_pids) == 12)
check("catalog contains no database-derived DID claims",
      not any(entry["kind"] == "did" for entry in committed_catalog["entries"]))


print("\n== DID correlations ==")
did_mappings = [m for m in mappings if m["kind"] == "did"]
check("no false section-3 DIDs reach firmware correlation", did_mappings == [])

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
            check(
                f"DID 0x{did_id:04X} response-size/attribute matches firmware",
                fw_did.response_size_or_attribute
                == int(m["firmware_response_size_or_attribute"], 16),
            )


print("\n== DTC correlations (structural table match) ==")
dtc_mappings = [m for m in mappings if m["kind"] == "dtc"]

# Independently scan the firmware DTC table
fw_dtcs = scan_firmware_dtc_table(CF)
fw_dtc_ids = set(fw_dtcs.keys())

dtc_exact = [m for m in dtc_mappings if m["match_grade"] == "exact"]
dtc_family = [m for m in dtc_mappings if m["match_grade"] == "family"]
check("DTC exact matches are non-zero", len(dtc_exact) > 0, f"got {len(dtc_exact)}")
check("DTC family matches exist (diagnostic-only)", len(dtc_family) > 0, f"got {len(dtc_family)}")
exact_dtc_codes = {mapping["code"] for mapping in dtc_exact}
check("full DTC table recovers five CAN-communication DTCs beyond old bound",
      {"U0100", "U0126", "U023A", "U0293", "U1103"} <= exact_dtc_codes,
      f"exact codes={sorted(exact_dtc_codes)}")

u023a = next(m for m in dtc_exact if m["code"] == "U023A" and m["source_db"] == "EPS_CAN_P4DK")
check("U023A mapping preserves two enabled firmware subtype variants",
      [v["failure_type"] for v in u023a["firmware_variants"]] == [0x00, 0x87],
      f"got {u023a['firmware_variants']}")
check("U023A subtype labels include exact U023A87",
      [v["full_code"] for v in u023a["firmware_variants"]] == ["U023A", "U023A87"])
check("U023A87 mapping carries its five concrete Dem event IDs",
      u023a["firmware_variants"][1]["event_ids"]
      == ["0xB0", "0xB3", "0x138", "0x13C", "0x13D"])
check("base U023A mapping has no direct Dem event",
      u023a["firmware_variants"][0]["event_ids"] == [])

# Every "exact" DTC must be in the firmware DTC table
for m in dtc_exact:
    dtc_id = m["dtc_identifier"]
    check(f"DTC {m['code']} (0x{dtc_id:04X}) exact match is in firmware DTC table",
          dtc_id in fw_dtc_ids,
          f"table IDs include={dtc_id in fw_dtc_ids}")

    # Verify each firmware offset actually contains the DTC ID at byte offset 1.
    for off_str in m["firmware_offsets"][:3]:
        offset = int(off_str, 16)
        if offset + 7 < len(CF):
            actual_id = struct.unpack_from("<H", CF, offset + 1)[0]
            check(f"DTC {m['code']} offset 0x{offset:X} has ID 0x{dtc_id:04X} at byte 1",
                  actual_id == dtc_id,
                  f"actual=0x{actual_id:04X}")

# No "exact" DTC should come from a blind byte search outside the table
for m in dtc_exact:
    for off_str in m["firmware_offsets"]:
        offset = int(off_str, 16)
        in_table = DTC_TABLE_START <= offset < DTC_TABLE_END
        check(f"DTC {m['code']} offset 0x{offset:X} is within DTC table bounds",
              in_table,
              f"bounds=0x{DTC_TABLE_START:X}..0x{DTC_TABLE_END:X}, "
              f"in_table={in_table}")


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
check("name_callback mappings are exact or structural",
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
check("seven decompiled monitor bridges are structural and auto-named",
      sum(m["match_grade"] == "structural" for m in bridged) == 7)
check("unverified/stub monitor bridges remain family comment-only",
      all(m["match_grade"] == "family" and m["annotation_action"] == "comment"
          for m in bridged if m["identifier"] in (0x0101, 0x0111)))
check("no monitor bridge is overstated as exact",
      all(m["match_grade"] != "exact" for m in bridged))

family_monitors = [m for m in monitor_mappings if "firmware_callback" not in m]
check("remaining family-grade monitors >= 80", len(family_monitors) >= 80,
      f"got {len(family_monitors)}")
bridged_dids = {m["identifier"] for m in bridged}
check("bridged monitors are not duplicated as family vocabulary",
      all(0x0100 + m["monitor_seq"] not in bridged_dids for m in family_monitors))

named_monitors = [m for m in monitor_mappings if m.get("oem_name")]
check("every monitor mapping has an OEM name",
      len(named_monitors) == len(monitor_mappings),
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


print("\n== U_English steering strings ==")
utility_mappings = [m for m in mappings if m["kind"] == "utility_string"]
check("at least 100 steering-anchored utility strings", len(utility_mappings) >= 100,
      f"got {len(utility_mappings)}")

# U_English has no ECU/procedure linkage. All extracted strings must use an
# explicit steering anchor and remain family-only vocabulary.
anchors = re.compile(
    r"\b(torque sensor|power steering|electric power steering|steering torque|"
    r"steering angle sensor|assist map|EPS)\b",
    re.IGNORECASE,
)
check("every utility string contains an explicit steering anchor",
      all(anchors.search(m["text"]) for m in utility_mappings))
check("bare EPS matching does not select the substring 'steps'",
      all("steps" not in m["text"].lower() or anchors.search(m["text"])
          for m in utility_mappings))
check("all utility strings are family grade",
      all(m["match_grade"] == "family" for m in utility_mappings),
      f"found non-family: {[m['match_grade'] for m in utility_mappings if m['match_grade'] != 'family'][:5]}")

check("no utility string references firmware routines",
      all(m.get("firmware_routines") is None for m in utility_mappings))


print("\n== active tests removed ==")
# Section 14 is PID display configuration, NOT active tests.
# The EPS .ddb files do not contain active test definitions.
at_mappings = [m for m in mappings if m["kind"] == "active_test"]
check("no active_test mappings exist (section 14 is PID display config)",
      len(at_mappings) == 0, f"got {len(at_mappings)}")


print("\n== idempotency ==")
if HAS_TECHSTREAM_SOURCE:
    vocab2 = build_vocabulary()
    check("rebuild produces same mapping count",
          len(vocab2["mappings"]) == len(vocab["mappings"]))
    check("rebuild produces same grade distribution",
          vocab2["summary"]["by_grade"] == vocab["summary"]["by_grade"])
    check("rebuild is byte-for-byte deterministic", vocab2 == vocab)
else:
    print("[SKIP] source-backed idempotency rebuild (proprietary source absent)")


print("\n== independent DDB field verification ==")
if not HAS_TECHSTREAM_SOURCE:
    print("[SKIP] raw DDB verification (proprietary source absent)")
    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    sys.exit(1 if failed else 0)

# Independently verify DTC record layout (section 5, 28 bytes)
# without trusting the parser's field offsets.
sys.path.insert(0, str(REPO / "tools" / "techstream"))
from parse_ddb import (  # noqa: E402
    DDBParser,
    ECU_TABLE_CLASS_NAMES,
    Section,
    TableDataHead,
    lzss_decompress,
)

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

# Factory identity is authoritative: section 3 is supported-PID metadata, not
# a DID table.  The old pipeline reinterpreted bytes 4-5 as a little-endian DID.
sec3 = eps_can.sections[3]
raw_d0 = sec3.raw_data[0:8]
check("section 3 factory class is CDbSupPidTable",
      ECU_TABLE_CLASS_NAMES[3] == "CDbSupPidTable")
check("section 7 factory class is CDbDidTable",
      ECU_TABLE_CLASS_NAMES[7] == "CDbDidTable")
check("former 0x0100 DID bytes are retained as supported-PID raw evidence",
      raw_d0.hex() == "0000000000010000")
check("selected EPS_CAN_P4DK database has no CDbDidTable section",
      7 not in eps_can.sections)

# Walk the raw directory independently of DDBParser. Directory slot N is
# section type N and extends to the first section pointer (0x280 in V18).
steering_root = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
raw_section_types: dict[str, set[int]] = {}
for source in sorted(
    path for path in steering_root.glob("*/DB/*.ddb")
    if path.stem.startswith(("EPS", "EMPS"))
):
    data = source.read_bytes()
    directory_end = next(
        struct.unpack_from("<I", data, slot)[0]
        for slot in range(0x24, len(data) - 3, 4)
        if struct.unpack_from("<I", data, slot)[0]
    )
    types = set()
    for slot in range(0x24, directory_end, 4):
        section_offset = struct.unpack_from("<I", data, slot)[0]
        if not section_offset:
            continue
        section_type = data[section_offset]
        expected_type = (slot - 0x24) // 4
        if section_type == expected_type:
            types.add(section_type)
    relative = source.relative_to(steering_root).as_posix()
    raw_section_types[relative] = types
    parsed = parser.parse_ecu_db(source)
    check(f"parser covers every raw section in {relative}",
          set(parsed.sections) == types,
          f"raw={sorted(types)} parsed={sorted(parsed.sections)}")
check("steering corpus includes high section types through 91",
      max(type_id for types in raw_section_types.values() for type_id in types) == 91)

def ddb_format(path: Path) -> int | None:
    with path.open("rb") as stream:
        header = stream.read(9)
    return header[8] if len(header) == 9 else None


def ddb_language_tag(path: Path) -> int | None:
    with path.open("rb") as stream:
        header = stream.read(8)
    return header[7] if len(header) == 8 else None


all_type2_paths = sorted(
    path for path in steering_root.glob("*/DB/*.ddb")
    if ddb_format(path) == 0x02
)
all_type2_sections = 0
all_type2_mismatches = []
for source_path in all_type2_paths:
    raw = source_path.read_bytes()
    directory_end = next(
        struct.unpack_from("<I", raw, slot)[0]
        for slot in range(0x24, len(raw) - 3, 4)
        if struct.unpack_from("<I", raw, slot)[0] != 0
    )
    raw_types = {
        (slot - 0x24) // 4
        for slot in range(0x24, directory_end, 4)
        if struct.unpack_from("<I", raw, slot)[0] != 0
    }
    parsed_types = set(parser.parse_ecu_db(source_path).sections)
    all_type2_sections += len(raw_types)
    if raw_types != parsed_types:
        all_type2_mismatches.append(str(source_path.relative_to(steering_root)))
check("all 1368 type-2 ECU databases match the independent raw directory walk",
      len(all_type2_paths) == 1368
      and all_type2_sections == 25361
      and not all_type2_mismatches,
      f"files={len(all_type2_paths)} sections={all_type2_sections} "
      f"mismatches={all_type2_mismatches[:3]}")

# Malformed inputs must fail closed instead of returning truncated data or
# silently flooring a fractional record size.
try:
    lzss_decompress(struct.pack("<I", 4) + b"\x00\xffA")
except ValueError:
    truncated_lzss_rejected = True
else:
    truncated_lzss_rejected = False
check("truncated LZSS stream is rejected", truncated_lzss_rejected)

bad_section = Section(TableDataHead(10, 0, 3, 10), 0, b"\x00" * 10)
try:
    _ = bad_section.record_size
except ValueError:
    fractional_record_rejected = True
else:
    fractional_record_rejected = False
check("non-integral section record size is rejected", fractional_record_rejected)

try:
    parser.parse_ecu_db(DB_PATH / "M_English.ddb")
except ValueError:
    string_as_ecu_rejected = True
else:
    string_as_ecu_rejected = False
check("string database passed to ECU parser is rejected", string_as_ecu_rejected)

try:
    parser.load_string_db(DB_PATH / "EPS_CAN_P4DK.ddb")
except ValueError:
    ecu_as_string_rejected = True
else:
    ecu_as_string_rejected = False
check("ECU database passed to string parser is rejected", ecu_as_string_rejected)

bad_u_header = bytearray((DB_PATH / "U_English.ddb").read_bytes())
bad_u_header[0] ^= 0xFF
try:
    parser._validate_header(bytes(bad_u_header))
except ValueError:
    bad_u_magic_rejected = True
else:
    bad_u_magic_rejected = False
check("format-6 string database with bad magic is rejected", bad_u_magic_rejected)

format6_paths = sorted(
    path for path in steering_root.glob("*/DB/*.ddb")
    if ddb_format(path) == 0x06
)
format6_databases = [parser.load_string_db(path) for path in format6_paths]
check("all 13 regional/language format-6 databases parse",
      len(format6_databases) == 13
      and all(db.entry_count == 25_957
              and db.metadata is not None
              and len(db.metadata) == 25_957
              for db in format6_databases))
check("format-6 language tags cover the observed 0x16..0x1A set",
      {ddb_language_tag(path) for path in format6_paths}
      == set(range(0x16, 0x1B)))

original_techstream_db = extract_catalog_module.TECHSTREAM_DB
extract_catalog_module.TECHSTREAM_DB = Path("/nonexistent/techstream-db")
try:
    build_catalog()
    missing_catalog_source_rejected = False
except FileNotFoundError:
    missing_catalog_source_rejected = True
finally:
    extract_catalog_module.TECHSTREAM_DB = original_techstream_db
check("catalog rebuild rejects missing required sources",
      missing_catalog_source_rejected)


print("\n== three-DB string resolution ==")
catalog = committed_catalog
check("catalog loaded all three string DBs",
      set(catalog["string_databases"].keys()) == {"M_English", "V_English", "U_English"})

u_strings = parser.load_string_db(DB_PATH / "U_English.ddb")
check("U_English type-1 metadata section has all 25,957 records",
      u_strings.metadata is not None and len(u_strings.metadata) == 25_957)
torque_metadata = u_strings.get_metadata(6585)
check("U_English metadata aligns resource ID with string index 6585",
      torque_metadata is not None
      and torque_metadata.identifier == "IDS_D_EFI_02_003_TITLE"
      and torque_metadata.auxiliary_value == 6490
      and u_strings.get_string(6585) == "Torque Sensor Writing")

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
utility_strings = [e for e in catalog["entries"] if e["kind"] == "utility_string"]
check("all extracted utility strings retain U_English resource identifiers",
      all(e.get("resource_identifier") for e in utility_strings))


print("\n== complete regional steering corpus ==")
corpus_path = REPO / "data/generated/techstream_v18/steering_diagnostic_corpus.json"
committed_corpus = json.loads(corpus_path.read_text())
rebuilt_corpus = build_steering_corpus()
check("committed steering corpus exactly matches deterministic rebuild",
      committed_corpus == rebuilt_corpus)
summary = committed_corpus["summary"]
check("all 35 regional EPS/EMPS files are inventoried",
      summary["source_files"] == 35)
check("regional corpus has 25 structural payload variants",
      summary["structural_payload_variants"] == 25)
check("regional corpus recovers 129 unique DTC identifiers",
      summary["unique_dtc_identifiers"] == 129)
check("regional corpus has one real CDbDidTable record",
      summary["did_records"] == 1 and summary["unique_did_record_keys"] == 1)
check("former 146 DID rows are classified as supported-PID records",
      summary["supported_pid_records"] == 146
      and summary["unique_supported_pid_record_keys"] == 16)
check("regional corpus recovers 1257 monitor records",
      summary["monitor_records"] == 1257)
raw_sources = sorted(
    path.relative_to(REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream").as_posix()
    for path in (REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream").glob("*/DB/*.ddb")
    if path.stem.startswith(("EPS", "EMPS"))
)
check("corpus source list equals raw filesystem discovery",
      committed_corpus["source_files"] == raw_sources)
variant_sections_by_source = {
    source: {int(type_id) for type_id in variant["sections"]}
    for variant in committed_corpus["structural_payload_variants"]
    for source in variant["source_files"]
}
check("corpus section inventories equal independent raw directory walk",
      variant_sections_by_source == raw_section_types)

p4_path = REPO / "data/generated/p4dk4_template/p4dk4_vocabulary.json"
p4 = json.loads(p4_path.read_text())
check("committed P4DK4 artifact exactly matches deterministic rebuild",
      p4 == build_p4dk4_catalog())
check("P4DK4 artifact has corrected Techstream distribution",
      p4["techstream_distribution"] == "V18.00.003")
check("P4DK4 artifact is deterministic (no generated_at)",
      "generated_at" not in p4)
check("P4DK4 description does not call it a newer generation",
      "co-shipped" in p4["description"].lower()
      and "not evidence" in p4["description"].lower())
check("P4DK4 seq-derived DID labels are explicitly structural candidates",
      p4["summary"]["structural_monitor_bridges"] == 78
      and p4["summary"]["candidate_firmware_did_count"] == 62
      and "bridged_did_count" not in p4["summary"]
      and all("candidate_firmware_did" in entry
              for entry in p4["structural_monitor_bridges"]))
check("P4DK4 section-3 rows are supported-PID records, not DIDs",
      p4["summary"]["supported_pid_records"] == 16
      and "dids" not in p4["summary"]
      and "dids" not in p4)
check("P4DK4 section-6 rows are PID records, not subfunctions",
      p4["summary"]["pid_records"] == 85
      and "subfunctions" not in p4["summary"]
      and all(entry["kind"] == "pid_record" for entry in p4["pid_records"]))


print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
