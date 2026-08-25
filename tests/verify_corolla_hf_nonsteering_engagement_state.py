#!/usr/bin/env python3
"""Verify the H/F Corolla non-steering engagement-state contract."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_hf_nonsteering_engagement_state.json"
BUILD = REPO / "tools/build_corolla_hf_nonsteering_engagement_state.py"
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
ENG = REPO / "data/generated/corolla_8965H1202000_nonsteering_engagement_decompiler_evidence.json"
TECH = REPO / "data/generated/techstream_v18/tss3_cruise_engagement_semantics.json"
DOC = REPO / "docs/architecture/toyota-openpilot-porting-contract.md"
STATE_DOC = REPO / "docs/variants/corolla-h-f-openpilot-state-bridge.md"

passed = failed = 0

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition); passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}{suffix}")

art = json.loads(ART.read_text())
eng = json.loads(ENG.read_text())
tech = json.loads(TECH.read_text())
image = IMAGE.read_bytes()

print("== deterministic synthesis ==")
with tempfile.TemporaryDirectory(prefix="engagement-state-") as td:
    out = Path(td) / "engagement.json"
    proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
    check("engagement builder succeeds", proc.returncode == 0, proc.stderr[-300:])
    check("engagement artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
check("schema exact", art["schema"] == "corolla-hf-nonsteering-engagement-state-v1")
check("H/F application identity retained", art["software_family"] == {"h": "8965H1202000", "f": "8965F1208000", "application_byte_identical": True})
check("compact H engagement evidence is raw-byte-bound", eng["schema"] == "corolla-h-nonsteering-engagement-decompiler-evidence-v1" and eng["function_count"] == 6 and eng["image"]["sha256"] == sha(image))
for row in eng["functions"]:
    start = int(row["entry"], 16)
    check(f"raw H body {row['entry']}", sha(image[start:start + row["body_size"]]) == row["body_sha256"])

print("\n== exact Ready Status wire join ==")
ready = art["ready_status"]
check("Ready Status carrier is exact H 0x51E B0[7]", ready["classification"] == "wire field closed" and ready["can_id"] == "0x51E" and ready["length"] == 8 and ready["h_rx_descriptor_index"] == 24 and ready["h_signal_id"] == 154 and ready["wire"] == "B0[7]")
check("Ready Status exact source chain reaches DID1033", ready["source_chain"] == ["0x51E B0[7]", "0xFEBE7D1B", "0xFEBEF052", "0xFEBEB5A8", "0xFEBEE811", "DID 0x1033"] and ready["techstream"] == {"name": "Ready Status", "did": "0x1033", "boolean_domain": [0, 1]})
check("Ready Status copy provenance does not claim an exclusive writer", ready["operational_copy_sites"] == ["0x000BAB58", "0x000BAC16"] and all(x in ready["writer_boundary"] for x in ("two operational copy sites", "initialization/reset", "exclusive-writer")))
check("public route corroborates Ready=1", ready["route_corroboration"]["public_2023"] == {"frames": 59, "values": [1], "payloads": ["8000004500000000"]})
check("Span route corroborates Ready=1", ready["route_corroboration"]["span_2025"] == {"frames": 60, "values": [1], "payloads": ["86001a0000000000"]})
check("Ready=0 remains bounded", all(x in ready["boundary"] for x in ("value 0", "uncaptured", "incoming", "not proof")))

print("\n== 0x127 gear carrier ==")
gear = art["gear"]
check("exact H retains 0x127/8 as Rx PDU20", gear["can_id"] == "0x127" and gear["length"] == 8 and gear["h_rx_descriptor_index"] == 20)
check("exact H generated signal ownership is 123..132", gear["h_signal_ids"] == list(range(123, 133)))
check("exact H scalar extraction positions are regenerated", gear["h_scalar_extractions"] == [{"signal_id": 123, "wire": "B0[7:2]", "length": 6}, {"signal_id": 125, "wire": "B1[3]", "length": 1}, {"signal_id": 129, "wire": "B3/B4 signed11 domain", "length": 11}])
check("legacy B5 gear nibble is not statically consumed by exact H scalar unpacker", "does not consume" in gear["h_static_boundary"] and gear["legacy_gear_field"]["wire"] == "B5[3:0]")
check("Span observes raw3 with prior-art D compatibility only", gear["span_dynamic"]["frames"] == gear["span_dynamic"]["checksum_valid"] == 3662 and gear["span_dynamic"]["raw_values"] == [3] and gear["span_dynamic"]["prior_art_decoded_values"] == ["D"] and "MOCK" in gear["span_dynamic"]["decode_basis"])
check("gear target-native validation remains bounded", all(x in gear["production_boundary"] for x in ("no independent gear-state oracle", "target-native D semantics", "P/R/N/B", "live transitions")))

print("\n== retained cruise prior art and false-positive rejection ==")
cruise = art["cruise"]
c176 = cruise["retained_wire_prior_art"]["0x176"]
check("0x176 survives both captures with valid checksum", c176["public_2023_frames"] == 1855 and c176["span_2025_frames"] == 1890 and c176["checksums_all_valid"] is True)
check("old 0x176 cruise-active/state fields stay inactive", c176["legacy_cruise_active_values"] == [False] and c176["legacy_cruise_state_values"] == [0])
check("0x176 B0[3] is not justified as cruise replacement", c176["b0_bit3_values"] == [0, 1] and "accelerator-release" in c176["b0_bit3_interpretation"] and "does not disprove every possible cruise-related meaning" in c176["b0_bit3_interpretation"] and c176["public_2023_b0_bit3_context"]["0"]["gas_positive_fraction"] > 0.99 and c176["public_2023_b0_bit3_context"]["1"]["gas_positive_fraction"] == 0.0 and c176["span_2025_b0_bit3_context"]["0"]["gas_positive_fraction"] > 0.97 and c176["span_2025_b0_bit3_context"]["1"]["gas_positive_fraction"] < 0.01)
c24d = cruise["retained_wire_prior_art"]["0x24D"]
check("0x24D survives but old switch fields remain inactive", c24d["public_2023_frames"] == 59 and c24d["span_2025_frames"] == 60 and all(v == [0] for v in c24d["legacy_button_fields"].values()))
check("old cruise replacement IDs absent in both captures", cruise["legacy_ids_absent_in_both_captures"] == ["0x177", "0x1A2", "0x1D3", "0x399"])

print("\n== Toyota P5 engagement diagnostic oracles ==")
rows = {x["name"]: x for x in cruise["techstream_p5_frc_oracles"]}
for name, data_id, bits in (
    ("Cruise Control Permission Flag", "0x1905", [8, 8]),
    ("Main Switch Recognition Flag", "0x1906", [8, 8]),
    ("ACC Not Available Icon Lighting Request Flag", "0x1906", [40, 40]),
    ("ACC Control in Operation Flag", "0x1914", [8, 8]),
    ("Set Vehicle Interval Time", "0x1912", [0, 7]),
    ("Current Vehicle Speed", "0x1901", [0, 31]),
    ("Memory Vehicle Speed", "0x1901", [32, 63]),
):
    check(f"FRC oracle {name}", rows[name]["primary_data_id"] == data_id and rows[name]["bit_range"] == bits)
check("permission dictionary exact", rows["Cruise Control Permission Flag"]["pattern_values"] == {"0": "Cruise Control Not Allowed", "1": "Cruise Control Allowed"})
check("ACC-operation dictionary exact", rows["ACC Control in Operation Flag"]["pattern_values"] == {"0": "Cruise Control Not in Operation", "1": "Cruise Control in Operation"})
check("set-speed oracle is physical km/h", rows["Memory Vehicle Speed"]["conversion"]["unit"] == "km/h" and rows["Memory Vehicle Speed"]["conversion"]["mul"] == rows["Memory Vehicle Speed"]["conversion"]["div"] == 1)
check("follow-distance dictionary exact", rows["Set Vehicle Interval Time"]["pattern_values"] == {"1": "Set Vehicle Interval Time4", "2": "Set Vehicle Interval Time3", "3": "Set Vehicle Interval Time2", "4": "Set Vehicle Interval Time1"})
check("diagnostic semantics remain wire-unmapped", cruise["classification"] == "diagnostic semantics narrowed; live CAN mapping not closed" and "no CAN field may be promoted" in cruise["boundary"])

print("\n== implementation boundary ==")
safe = art["implementation_consequence"]["safe_now"]
unsafe = art["implementation_consequence"]["not_safe_yet"]
check("Ready input is safe for inspection", any("0x51E B0[7]" in x for x in safe))
check("production cruise remains neutral", any("cruiseState.available/enabled/set-speed neutral" in x for x in safe))
check("B0[3] promotion explicitly prohibited", any("0x176 B0[3]" in x for x in unsafe))
check("P/R/N/B promotion explicitly prohibited", any("P/R/N/B" in x for x in unsafe))
check("capture recipe is concrete and P5-Data-ID addressed", all(any(data_id in x for x in cruise["capture_recipe"]) for data_id in ("0x1905", "0x1906", "0x1914", "0x1901", "0x1912")) and all("Data ID" in x for x in cruise["capture_recipe"]))
check("P5 Data IDs are not mislabeled as direct UDS DIDs", all(x in cruise["diagnostic_transport_boundary"] for x in ("P5 diagnostic Data IDs", "not automatically UDS", "Techstream/GTS+", "0x22")))

print("\n== documentation/status integration ==")
doc = DOC.read_text() if DOC.exists() else ""
state_doc = STATE_DOC.read_text() if STATE_DOC.exists() else ""
findings = (REPO / "docs/status/FINDINGS.md").read_text()
priorities = (REPO / "docs/status/PRIORITIES.md").read_text()
for token in ("0x51E", "Ready Status", "0x1905", "0x1906", "0x1914", "0x24D"):
    check(f"porting doc preserves {token}", token in doc)
check("porting doc preserves Memory Vehicle Speed oracle", "Memory" in doc and "Vehicle Speed" in doc and "Data ID `0x1901`" in doc)
check("state-bridge doc closes 0x51E Ready input", all(x in state_doc for x in ("0x51E", "B0[7]", "Ready Status", "DID `0x1033`")))
check("COM-017 integrated", "| COM-017 |" in findings and "nonsteering_engagement_state" in findings)
check("priority consumes engagement-state contract", "corolla_hf_nonsteering_engagement_state.json" in priorities)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
