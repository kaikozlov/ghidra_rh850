#!/usr/bin/env python3
"""Verify exact-F33 normal-COM lateral-ingress closure against retained live CAN."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_8965F3307000_external_lateral_ingress.json"
BUILD = REPO / "tools/build_camry_8965F3307000_external_lateral_ingress.py"

passed = failed = 0

def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond); passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][dynamic_trace] {name}" + (f" ({detail})" if detail else ""))

with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "ingress.json"
    p = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True)
    check("generator succeeds", p.returncode == 0, p.stderr[-300:])
    check("artifact regenerates byte-exact", p.returncode == 0 and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
check("schema/target exact", art["schema"] == "camry-8965f3307000-external-lateral-ingress-v1" and art["target"]["software_id"] == "8965F3307000" and art["target"]["corpus_function_count"] == 6065)
check("normal Rx/scalar census exact", art["normal_rx"]["descriptor_count"] == 43 and art["normal_rx"]["scalar_receive_call_count"] == 116)
ctrl = art["controller1_acceptance"]
check("controller1 acceptance span is exhausted", ctrl["count"] == 47 and ctrl["normal_rule_indices"] == [0,42] and ctrl["normal_rules_equal_descriptor_order"] is True)
check("only diagnostic/XCP rules follow normal COM", [(x.get("can_id"), x["role"]) for x in ctrl["special_tail"]] == [("0x7A1","physical UDS"),("0x777","functional UDS"),("0x7A0","secondary diagnostics"),("0x7F7","application XCP")])

cands = {(x["can_id"], x["signal"]): x for x in art["normal_rx"]["signed_12plus_candidates"]}
check("signed >=12-bit ingress set exact", set(cands) == {(0x025,187),(0x025,189),(0x0B6,262),(0x0D5,212),(0x0D5,213),(0x115,134),(0x1C5,141),(0x64F,255),(0x64F,257)})
check("025 large fields are measured feedback", cands[(0x025,187)]["classification"] == cands[(0x025,189)]["classification"] == "measured-feedback")
check("B6 signed16 remains external lateral command", cands[(0x0B6,262)]["classification"] == "external-lateral-command" and cands[(0x0B6,262)]["byte_offset"] == 4)
check("D5 signed16s are monitor paths", cands[(0x0D5,212)]["classification"] == cands[(0x0D5,213)]["classification"] == "monitor/plausibility")
check("115 signed16 is engine-domain", cands[(0x115,134)]["classification"] == "engine-domain" and art["special_paths"]["0x115"]["gtsplus_name"] == "Engine Revolution")
check("1C5/64F command-sized fields are not observed", all(cands[k]["classification"] == "not-observed" for k in ((0x1C5,141),(0x64F,255),(0x64F,257))))

live = art["live_intersection"]
check("two drives total 3.574M frames", live["combined_incoming_frames"] == 3574703)
check("B6 absent on every bus", live["selected_counts"]["0x0B6/32"] == {"0":0,"1":0,"2":0})
check("D5 first signed16 stays tiny", live["d5_signed16_b1_b2"] == {"count":55793,"min":-5,"max":11,"unique":17})
check("D5 second signed16 is identically zero", live["d5_signed16_b3_b4"] == {"count":55793,"min":0,"max":0,"unique":1})
check("115 engine-revolution field is dynamically populated", live["id115_signed16_b0_b1"]["count"] == 47384 and live["id115_signed16_b0_b1"]["max"] == 2884 and live["id115_signed16_b0_b1"]["unique"] > 1000)
check("generic group receive surface is absent live", art["special_paths"]["generic_group_receive"]["can_ids"] == [f"0x{x:03X}" for x in range(0x13,0x20)] and art["special_paths"]["generic_group_receive"]["live_total"] == 0)
check("B6 reaches Toyota-named command torque", art["b6_to_command_torque"]["gtsplus_terminal"] == "0x1C02 Command Value Torque")
check("normal-COM conclusion is bounded", "No observed ordinary EPS-CAN field besides B6" in art["conclusion"]["normal_com"] and "does not prove" in art["boundary"][1])
check("production output remains disabled", art["conclusion"]["production_output_authorized"] is False)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
