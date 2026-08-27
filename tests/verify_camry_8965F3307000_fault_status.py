#!/usr/bin/env python3
"""Verify exact-F33 0x394 DEM/classifier fault-status recovery."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
EVID = ROOT / "data/generated/camry_8965F3307000_fault_status_decompiler_evidence.json"
ART = ROOT / "data/generated/camry_8965F3307000_fault_status.json"
BUILD = ROOT / "tools/build_camry_8965F3307000_fault_status.py"
REPORT = ROOT / "docs/variants/camry-2026-tss3-fault-status.md"
FINDINGS = ROOT / "docs/status/FINDINGS.md"
PRIORITIES = ROOT / "docs/status/PRIORITIES.md"

passed = failed = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}")


img = IMAGE.read_bytes()
evid = json.loads(EVID.read_text(encoding="utf-8"))
art = json.loads(ART.read_text(encoding="utf-8"))
funcs = {int(row["entry"], 16): row for row in evid["functions"]}

print("== exact target/evidence identity ==")
check("artifact schema", art["schema"] == "camry-8965f3307000-fault-status-v1")
check("exact target", art["target"]["software_id"] == "8965F3307000")
check("image hash", sha(img) == evid["image"]["sha256"] == art["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7")
check("evidence schema/count", evid["schema"] == "camry-8965f3307000-fault-status-decompiler-evidence-v1" and evid["function_count"] == len(funcs) == 10)
for entry, row in sorted(funcs.items()):
    check(f"0x{entry:08X} body hash", sha(img[entry:entry + row["body_size"]]) == row["body_sha256"])
with tempfile.TemporaryDirectory(prefix="camry-f33-fault-status-") as td:
    out = Path(td) / "fault-status.json"
    proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
    check("builder exits cleanly", proc.returncode == 0)
    check("builder reproduces artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

print("\n== target-native 0x394 classifier ==")
c = art["classifier"]
check("classifier entry exact", c["entry"] == "0x000512E4" and c["class_accumulator"] == "0x00050FC8")
check("state table exact address", c["state_table"] == "0x0002A19C")
check("state table has 17 rows", len(c["state_table_rows"]) == 17)
check("state table exact bytes", img[0x2A19C:0x2A19C + 85].hex() == "00000000000403000000040700000005030000000403000000010100000003030201020303020100060303000206030300000307010101030704010106070700010607060001060705000102020000000407000000")
check("state0 role bounded", "clear/normal" in c["state_roles"]["0"] and "Ready" not in c["state_roles"]["0"])
check("class states exact", c["state_roles"]["6"].startswith("class-0x02") and c["state_roles"]["10"].startswith("class-0x10") and c["state_roles"]["12"].startswith("class-0x40"))
check("state16 remains operational inhibit", "inhibit" in c["state_roles"]["16"])

print("\n== exact wire projection ==")
w = art["wire"]
proj = {tuple(row["wire"]): tuple(row["states"]) for row in w["projection_to_state_candidates"]}
check("0x394 exact carrier", w["can_id"] == "0x394" and w["length"] == 3)
check("unique state0 projection", proj[(0, 0, 0, 0)] == (0,))
check("class02 unique projection", proj[(2, 3, 2, 1)] == (6,))
check("class10 unique projection", proj[(1, 7, 1, 1)] == (10,))
check("first lossy projection exact", proj[(0, 3, 0, 0)] == (1, 3, 4))
check("second lossy projection exact", proj[(0, 7, 0, 0)] == (2, 16))
check("wire boundary is candidate-only", "lossy" in w["boundary"] and "fabricate" in w["boundary"])

print("\n== target-native aging/calibration ==")
a = art["aging"]
check("calibration address exact", a["calibration_address"] == "0x00030E40")
check("raw calibration words exact", a["raw_u16"] == [200, 200, 600, 22170, 200, 200, 1000])
check("primary/aggregate/secondary ages exact", (a["primary_latch_bank_355d_age"], a["aggregate_latch_bank_355c_age"], a["class2_class4_secondary_latch_age"]) == (200, 200, 600))
check("F33 clear-enable age is target-specific", a["primary_clear_enable_age"] == 22170 and a["comparison_to_h"] == {"h_primary_clear_enable_age": 17736, "f33_primary_clear_enable_age": 22170})
check("aging is not promoted to wall-clock policy", "No wall-clock" in a["boundary"] and "temporary/permanent" in a["boundary"])

print("\n== target-native DEM/DTC census ==")
d = art["dem"]
check("event table geometry exact", d["event_table"] == "0x0002FC50" and d["event_count"] == 0x180 and d["record_size"] == 8)
check("class histogram exact", d["class_counts"] == {"0x01":8,"0x02":34,"0x04":1,"0x08":1,"0x0F":1,"0x10":171,"0x20":16,"0x40":1,"0x80":7})
check("240 classified events", sum(d["class_counts"].values()) == 240)
comp = d["comparison_to_h"]
check("31 H/F event records differ", comp["changed_record_count"] == 31 and len(comp["changed_records"]) == 31)
check("only thermal events leave class10", comp["class_removed_events"] == ["0x0085", "0x0088"])
check("only event0AC loses DTC index", comp["dtc_index_removed_events"] == ["0x00AC"])
thermal = comp["thermal_dtcs_removed_from_class_0x10"]
check("thermal A/B DTC names exact", [(x["event"], x["dtc"]["techstream_code"], x["dtc"]["techstream_description"]) for x in thermal] == [
    ("0x0085", "C10051C", 'Control Module Internal Temperature Sensor "B"'),
    ("0x0088", "C10001C", 'Control Module Internal Temperature Sensor "A"'),
])
check("DTC table exact relocation", art["dtc"]["table"] == "0x00030850")
check("80 referenced DTC rows remain byte-identical", art["dtc"]["referenced_index_count"] == 80 and art["dtc"]["referenced_rows_identical_to_h"] is True)
check("DTC index120 exact disable", art["dtc"]["index_120_disabled"] == {"h_raw":"8710d10001000000", "f33_raw":"8710d10000000000"})
check("Techstream join is raw-record based", "identical packed-DTC bytes" in art["dtc"]["vocabulary_join"])

print("\n== openpilot policy boundary ==")
op = art["openpilot_policy"]
check("internal state exposure only", "candidate set" in op["internal_state_exposure"])
check("state0 is not Ready authorization", "not independently a Ready" in op["state0"])
check("temporary fault policy unresolved", op["steerFaultTemporary"] == "unresolved policy mapping")
check("permanent fault policy unresolved", op["steerFaultPermanent"] == "unresolved policy mapping")
check("production output remains unauthorized", op["production_output_authorized"] is False)
integ = art["passive_opendbc_integration"]
check("passive implementation hashes pinned", integ["nested_opendbc_commit"] == "0d5773bd393bbf3d4109728171d2390b60fcde16" and integ["parent_kai_openpilot_commit"] == "191aeb43df3fb72f3264209be1aad57b9ca42e2d")
check("public fault flags remain unchanged", integ["public_fault_flags_changed"] is False)
check("full nested gate recorded", "4077 passed / 719 skipped" in integ["full_gate"] and "MISRA" in integ["full_gate"])

print("\n== documentation integration ==")
report = REPORT.read_text(encoding="utf-8")
findings = FINDINGS.read_text(encoding="utf-8")
priorities = PRIORITIES.read_text(encoding="utf-8")
for tok in ("0x512E4", "0x2A19C", "0x2FC50", "0x30850", "22,170", "240", "C10051C", "C10001C", "steerFaultTemporary", "steerFaultPermanent"):
    check(f"report contains {tok}", tok in report)
check("VAR-059 registered", "| VAR-059 |" in findings and "0x512E4" in findings and "240" in findings)
check("priorities consume F33 fault-status closure", "VAR-059" in priorities and "0x394" in priorities and "asserted/recovery" in priorities)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
