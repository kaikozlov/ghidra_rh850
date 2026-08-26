#!/usr/bin/env python3
"""Verify the exact H/F FEBE7C58 -> FEBEF000 -> FEBEACBD monitor contract."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
EVID = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_decompiler_evidence.json"
ART = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_gate.json"
TOOL = REPO / "tools/build_corolla_h_power_supply_monitor_gate.py"
passed = failed = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "monitor.json"
    run = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO, capture_output=True, text=True)
    check("monitor builder exits", run.returncode == 0, (run.stdout + run.stderr)[-500:] if run.returncode else "")
    check("monitor artifact regenerates exactly", run.returncode == 0 and out.read_bytes() == ART.read_bytes())

raw = RAW.read_bytes()
ev = json.loads(EVID.read_text())
art = json.loads(ART.read_text())

print("\n== source binding ==")
check("schema exact", art["schema"] == "corolla-8965H1202000-power-supply-monitor-gate-v1")
check("exact H image", len(raw) == 0x100000 and sha(raw) == art["sources"]["codeflash"]["sha256"] == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
check("14 compact functions", ev["function_count"] == art["sources"]["decompiler_evidence"]["function_count"] == 14)
check("all compact function bodies raw-bound", all(sha(raw[int(row["entry"], 16):int(row["entry"], 16) + row["body_size"]]) == row["body_sha256"] for row in ev["functions"]))
check("H/F application transfer exact", art["applies_to"] == ["8965H1202000", "8965F1208000"] and art["sources"]["hf_application_equivalence"]["region"]["identical"] is True and art["sources"]["hf_application_equivalence"]["region"]["different_bytes"] == 0)

print("\n== exact state chain ==")
chain = art["state_chain"]
check("native to scheduler snapshot exact", chain["native_state"] == "0xFEBE7C58" and chain["snapshot_copy"] == {"entry": "0x0005262C", "destination": "0xFEBEF000"})
check("B8EE4 normalization body exact", chain["normalizer"] == {"entry": "0x000B8EE4", "tracked_body_continuation": "0x000B8EEC"} and chain["normalized_output"] == "0xFEBEACBD")
check("normalization mapping exact", chain["mapping"] == {"0": 0, "2": 2, "3": 4, "other_nonzero": 1})
check("fixed-GP arithmetic exact", chain["exact_fixed_gp_arithmetic"] == {"gp": "0xFEBEB800", "native": "GP-0x3BA8", "snapshot": "GP+0x3800", "normalized": "GP-0x0B43"})
check("direct census counts pinned", {key: value["match_count"] for key, value in chain["direct_text_reference_census"].items()} == {"native_state": 47, "normalized_state": 21, "snapshot_state": 31})

print("\n== three power-supply monitors ==")
dispatch = art["monitor_dispatch"]
check("three configured channels active", dispatch["entry"] == "0x000450FC" and dispatch["feature_bytes"]["address"] == "0x0002B864" and dispatch["feature_bytes"]["raw_hex"] == raw[0x2B864:0x2B867].hex() == "000000")
check("three monitor/classifier pairs exact", [(row["monitor"], row["classifier"]) for row in dispatch["channels"]] == [("0x00044D84", "0x0004516A"), ("0x00044EC2", "0x000451C4"), ("0x00044FC4", "0x00045212")])
check("combined, A6, and A8 input sets exact", [row["supply_inputs"] for row in dispatch["channels"]] == [["0xFEBE63B0", "0xFEBE63A6", "0xFEBE63A8"], ["0xFEBE63B0", "0xFEBE63A6"], ["0xFEBE63B0", "0xFEBE63A8"]])
check("shared state writers exact", dispatch["shared_state_writes"] == {"0": "0x00045268", "1": "0x00045260", "2": "0x00045272", "3": ["0x0004527A", "0x0004528A", "0x0004529A"]})
check("raw calibration bytes exact", dispatch["calibration"]["address"] == "0x0002B69A" and dispatch["calibration"]["raw_hex"] == raw[0x2B69A:0x2B6B6].hex() == "00100009001000090500c8000000c8000500c80000000500c8000000")

print("\n== diagnostic join and boundaries ==")
join = art["diagnostic_input_join"]
check("IG supply cell exact", join["0xFEBE63B0"]["producer"] == "0x000488E6" and {x["name"] for x in join["0xFEBE63B0"]["rows"]} == {"IG Power Supply", "IG Power Supply (System 2)"})
check("A6 retains both supported OEM labels", join["0xFEBE63A6"]["producers"] == ["0x00048918", "0x00048CFC"] and {x["name"] for x in join["0xFEBE63A6"]["rows"]} == {"PIG Power Supply", "PIG Power Supply (System 2)", "Motor 1 Power Supply"})
check("A8 motor-2 supply cell exact", join["0xFEBE63A8"]["producer"] == "0x00048E90" and join["0xFEBE63A8"]["rows"] == [{"did": "0x10FA", "name": "Motor 2 Power Supply"}])
check("unlabeled control inputs remain unnamed", all(token in join["boundary"] for token in ("FEBE63A4", "FEBE65E4", "FEBE7C5F")))
classification = art["classification"]
check("state classified as graded receive-validity/freeze gate", "power-supply receive-validity/freeze state" in classification["recovered"] and "scheduler snapshot" in classification["recovered"] and "normalized downstream gate" in classification["recovered"])
check("B6 loss remains separate", classification["distinct_from_b6_loss"] == "B6 missing-message loss remains the separate FEBEADB9 -> FEBEC26D path.")
check("confidence boundary explicit", classification["not_established"] == ["literal OEM name for any of the three state bytes", "physical units of the raw supply cells", "wall-clock debounce durations", "a wire-visible FEBEACBD feedback field", "arbitrary computed-pointer aliases outside the census"])


print("\n== documentation/status integration ==")
state_doc = (REPO / "docs/variants/corolla-h-f-openpilot-state-bridge.md").read_text()
findings = (REPO / "docs/status/FINDINGS.md").read_text()
check("canonical report records power-supply gate semantics", all(x in state_doc for x in ("### 6.5", "FEBE7C58", "FEBEF000", "FEBEACBD", "power-supply receive-validity/freeze state", "FEBEADB9 -> FEBEC26D")))
check("TMS-055 integrated", "| TMS-055 |" in findings and "power_supply_monitor_gate.json" in findings)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
