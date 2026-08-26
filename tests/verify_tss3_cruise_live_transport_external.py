#!/usr/bin/env python3
"""Verify current-GTS+ FRC_P5 cruise Data-ID live transport from the pinned local archive."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARCHIVE = REPO / "REFERENCE/gtsplus.7z"
TOOL = REPO / "tools/techstream/extract_tss3_cruise_live_transport.py"
ART = REPO / "data/generated/techstream_v18/tss3_cruise_live_transport.json"
SEM = REPO / "data/generated/techstream_v18/tss3_cruise_engagement_semantics.json"
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}" + (f" ({detail})" if detail else ""))


if not ARCHIVE.is_file():
    print(f"[SKIP] local GTS+ archive unavailable: {ARCHIVE}")
    raise SystemExit(77)

with tempfile.TemporaryDirectory(prefix="tss3-cruise-live-") as td:
    out = Path(td) / "transport.json"
    proc = subprocess.run([sys.executable, str(TOOL), "--archive", str(ARCHIVE), "--out", str(out)], cwd=REPO, capture_output=True, text=True)
    check("live transport extraction succeeds", proc.returncode == 0, proc.stderr[-400:] if proc.returncode else "")
    check("tracked live transport regenerates exactly", out.exists() and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
sem = json.loads(SEM.read_text())
check("schema/category/FRC target exact", art["schema"] == "techstream-gtsplus-p5-cruise-live-dataid-transport-v1" and art["scope"] == {"category_id": 498, "database": "FRC_P5.ddb", "ecu_name": "Front Recognition Camera 2", "physical_request_address": "0x792"})
check("DataListIF identity pinned", art["sources"]["data_list_if"] == {"size": 507920, "sha256": "cce3ecd1203f81914c51d5b2599ee68eb4f7faafa8cbd9bb24fd7390b54d651d"})
check("FRC physical address is source-backed by P5 VDS anchor", art["scope"]["physical_request_address"] == "0x792" and art["sources"]["p5_lateral_control_semantics"]["frc_vds_anchor"]["ecu_no"] == 498 and art["sources"]["p5_lateral_control_semantics"]["frc_vds_anchor"]["address"] == "792")
check("two function bodies raw pinned", art["raw_function_evidence"] == {
    "check_rcv_frame": {"sha256": "932e5eee05d5605f13611e35bf9aad62fbb3dc3f86a8b444da5200f6a5d8a54e", "size": 577, "va": "0x10038FD0"},
    "dataid_setup": {"sha256": "4e08f6fcf01fd9d5511b73783c2bf5af9670360d3e856e866252b19aa5fc7ec6", "size": 486, "va": "0x100393D0"},
})
anchors = art["raw_instruction_anchors"]
check("request is raw-pinned SID22 + big-endian DID", anchors["request_service_22"]["bytes"] == "c60022" and anchors["request_did_hi_load"]["bytes"] == "0fb6445801" and anchors["request_did_lo_load"]["bytes"] == "0fb60458" and anchors["request_length_3"]["bytes"] == "c7460403000000")
check("response raw-pins SID62 and three-byte stripping", anchors["response_mode_is_22"]["bytes"] == "80f922" and anchors["response_positive_service_62"]["bytes"] == "3c62" and anchors["response_skip_three_bytes"]["bytes"] == "83c203" and anchors["response_length_minus_three"]["bytes"] == "83c0fd")
check("response copy is capped by expected Data-ID length", anchors["response_expected_length_lookup"]["bytes"] == "0fb70448" and anchors["response_length_cap_compare"]["bytes"] == "663bc3" and "min(received_length-3, runtime_expected_data_id_length)" in art["transport"]["payload_copy"])
expected = {
    "0x1901": ("221901", "621901", 8, {"Current Vehicle Speed", "Memory Vehicle Speed"}),
    "0x1905": ("221905", "621905", 2, {"Cruise Control Permission Flag"}),
    "0x1906": ("221906", "621906", 6, {"Main Switch Recognition Flag", "Set Cancel Switch Condition", "ACC Not Available Icon Lighting Request Flag"}),
    "0x1912": ("221912", "621912", 1, {"Set Vehicle Interval Time"}),
    "0x1914": ("221914", "621914", 2, {"ACC Control in Operation Flag"}),
}
rows = {row["data_id"]: row for row in art["selected_cruise_oracles"]}
check("exact five selected Data IDs", set(rows) == set(expected))
for did, (req, resp, minimum, names) in expected.items():
    row = rows[did]
    check(f"{did} request/strict response/minimum span", row["request"] == req and row["strict_capture_positive_prefix"] == resp and row["minimum_payload_bytes_from_monitored_bits"] == minimum)
    check(f"{did} monitor names exact", {x["name"] for x in row["monitor_rows"]} == names)
semantic_rows = {(x["primary_data_id"], x["name"], tuple(x["bit_range"]), x["monitor_record_sha256"]) for x in sem["frc_p5"]["monitors"]}
check("selected monitor rows remain joined to semantic artifact", all((row["data_id"], mon["name"], tuple(mon["bit_range"]), mon["monitor_record_sha256"]) in semantic_rows for row in rows.values() for mon in row["monitor_rows"]))
check("outer session remains explicitly bounded", "does not prove a named outer UDS DiagnosticSessionControl prerequisite" in art["transport"]["outer_session_boundary"])
check("host DID-response validation weakness is not hidden", "does not compare response bytes 1/2" in art["transport"]["returned_did_validation_boundary"] and "stricter conventional" in art["transport"]["returned_did_validation_boundary"])
check("capture recipe directly pollable", art["capture_recipe"]["poll"] == ["221901", "221905", "221906", "221912", "221914"])

print("\n== documentation/status integration ==")
tech_doc = (REPO / "docs/tooling/techstream.md").read_text()
findings = (REPO / "docs/status/FINDINGS.md").read_text()
corrections = (REPO / "docs/status/CORRECTIONS.md").read_text()
check("canonical Techstream report records direct cruise RDBI transport", all(x in tech_doc for x in ("### 6.3", "22 19 01", "22 19 05", "22 19 06", "22 19 12", "22 19 14", "stricter than GTS+")))
check("TMS-057 integrated", "| TMS-057 |" in findings and "tss3_cruise_live_transport.json" in findings)
check("CORR-117 integrated", "### CORR-117" in corrections and "direct SID-0x22 RDBI" in corrections)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
