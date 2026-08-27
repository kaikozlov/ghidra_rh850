#!/usr/bin/env python3
"""Verify exact-F33 Tx/status evidence for the passive Camry TSS3 opendbc port."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
EVID = ROOT / "data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json"
ART = ROOT / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"
BUILD = ROOT / "tools/build_camry_8965F3307000_tss3_opendbc_port.py"
REPORT = ROOT / "docs/variants/camry-2026-tss3-opendbc-port.md"
FINDINGS = ROOT / "docs/status/FINDINGS.md"
CORRECTIONS = ROOT / "docs/status/CORRECTIONS.md"
PRIORITIES = ROOT / "docs/status/PRIORITIES.md"

p = f = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, ok: object) -> None:
    global p, f
    yes = bool(ok)
    p += int(yes)
    f += int(not yes)
    print(f"[{'PASS' if yes else 'FAIL'}] {name}")


img = IMAGE.read_bytes()
evid = json.loads(EVID.read_text(encoding="utf-8"))
art = json.loads(ART.read_text(encoding="utf-8"))
funcs = {int(row["entry"], 16): row for row in evid["functions"]}

print("== target/evidence identity ==")
check("artifact schema/target", art["schema"] == "camry-8965f3307000-tss3-opendbc-port-v1" and art["target"]["software_id"] == "8965F3307000")
check("exact image hash", sha(img) == evid["image"]["sha256"] == art["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7")
check("compact evidence exact", evid["schema"] == "camry-8965f3307000-tss3-tx-decompiler-evidence-v1" and evid["function_count"] == len(funcs) == 11)
for entry, row in sorted(funcs.items()):
    check(f"0x{entry:08X} body hash", sha(img[entry:entry + row["body_size"]]) == row["body_sha256"])
with tempfile.TemporaryDirectory(prefix="camry-f33-tss3-port-") as td:
    out = Path(td) / "port.json"
    r = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
    check("builder exits cleanly", r.returncode == 0)
    check("builder reproduces artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

print("\n== exact F33 generated-COM Tx geometry ==")
tx = art["generated_com_tx"]
check("Tx table exact address", tx["tx_table"] == "0x00021F58")
check("first five Tx IDs exact", [(x["can_id"], x["can_fd"]) for x in tx["first_five"]] == [("0x030", True), ("0x351", False), ("0x394", False), ("0x4A3", False), ("0x4C8", False)])
check("signal/PDU tables exact", tx["signal_to_pdu_table"] == "0x00022488" and tx["pdu_table"] == "0x000226C0" and tx["signal_count"] == 284)
check("PDU descriptors exact", tx["pdu_descriptors"] == {
    "0": [2, 0, 0, 32, 0, 3], "1": [200, 0, 0, 4, 0, 3], "2": [60, 0, 0, 3, 0, 3],
    "3": [100, 0, 0, 8, 0, 3], "4": [196, 0, 0, 8, 0, 3],
})
check("0x351 signal allocation exact", tx["signal_allocations"]["1"] == [38, 39])
check("0x394 signal allocation exact", tx["signal_allocations"]["2"] == [40, 41, 42, 43])
check("0x4A3 signal allocation exact", tx["signal_allocations"]["3"] == list(range(44, 52)))
check("generic scalar packer target-native", "unaff_tp + -0x1974" in funcs[0x7D1DC]["decompiled_c"])

print("\n== exact F33 status carrier packers ==")
s = art["status_carriers"]
check("351 exact functions", s["0x351"]["producer"] == "0x0004C216" and s["0x351"]["debounce"] == "0x0004C1C0" and s["0x351"]["packer"] == "0x0004CED0")
check("351 exact packing", "FUN_0007d1dc(0x26,0x22,3,5" in funcs[0x4CED0]["decompiled_c"] and "FUN_0007d1dc(0x27,0x22,1,4" in funcs[0x4CED0]["decompiled_c"])
check("351 policy remains bounded", "no openpilot temporary/permanent fault mapping" in s["0x351"]["policy_boundary"])
check("394 exact functions", s["0x394"]["projection"] == "0x0004C24A" and s["0x394"]["packer"] == "0x0004CE08")
check("394 exact packing", all(tok in funcs[0x4CE08]["decompiled_c"] for tok in (
    "FUN_0007d1dc(0x28,0x25,2,6", "FUN_0007d1dc(0x29,0x25,3,3", "FUN_0007d1dc(0x2a,0x26,3,1", "FUN_0007d1dc(0x2b,0x26,1,0")))
check("394 policy remains bounded", "not promoted to Ready" in s["0x394"]["policy_boundary"])
check("4A3 exact functions", s["0x4A3"]["source_preparation"] == "0x0004C000" and s["0x4A3"]["staging"] == "0x0004C14E" and s["0x4A3"]["packer"] == "0x0004C7AA")
check("4A3 packs signals44..51", "FUN_0007d31e(0x2c,0x27,8,0" in funcs[0x4C7AA]["decompiled_c"] and "FUN_0007d31e(0x33,0x2e,8,0" in funcs[0x4C7AA]["decompiled_c"])
check("4A3 signed12 angle staging exact", all(tok in funcs[0x4C14E]["decompiled_c"] for tok in ("unaff_gp + -0x37b8", ">> 8) & 0xf", "unaff_gp + -0x3aba", "0x7ff", "0xfffff800")))
check("4A3 torque staging exact", "unaff_gp + -0x5158" in funcs[0x4C000]["decompiled_c"] and "* 100) / 0x100" in funcs[0x4C000]["decompiled_c"] and "unaff_gp + -0x36ae) / 10" in funcs[0x4C14E]["decompiled_c"])
check("4A3 alternate current source exact", "unaff_gp + -0x50e8" in funcs[0x4C000]["decompiled_c"] and "* -100) / 0x80" in funcs[0x4C000]["decompiled_c"])
check("4A3 current is not mislabeled DID1151", "GP-0x50E8" in s["0x4A3"]["current_semantic_boundary"] and "GP-0x50F2" in s["0x4A3"]["current_semantic_boundary"])

print("\n== VAR-056 bounded-census correction ==")
c = art["census_correction"]
check("torque direct-reference count corrected 4->5", c["old_recovered_count"] == 4 and c["new_recovered_count"] == 5 and c["new_entry"] == "0x0004C000")
check("updated torque entries exact", c["driver_torque_direct_fixed_gp_entries"] == ["0x00035A06", "0x0004C000", "0x0004DB70", "0x00054244", "0x000564CE"])
check("control-cone conclusion unchanged", c["control_cone_conclusion_changed"] is False and "outside the cooperative C8xxx-D1xxx" in c["reason"])
check("alternate-current census distinct", [x["entry"] for x in evid["fixed_gp_census"]["alternate_4a3_current_source_gp_minus_0x50e8"]] == ["0x0004C000"])
check("DID1151 source census remains distinct", [x["entry"] for x in evid["fixed_gp_census"]["did1151_q_current_source_gp_minus_0x50f2"]] == ["0x0004E394", "0x00054244", "0x000564CE"])
check("negative census boundary retained", "computed aliases" in evid["fixed_gp_census"]["boundary"].lower() and "dma" in evid["fixed_gp_census"]["boundary"].lower())

print("\n== passive opendbc integration boundary ==")
o = art["passive_opendbc_integration"]
check("implementation commits pinned", o["nested_opendbc_commit"] == "ab60fd95d8a7b566e10ed1cf59738292f3498932" and o["parent_kai_openpilot_commit"] == "d7d7dfd7e49961e9d35eb7a7681e8756ceee8d04")
check("exact platform/F181 binding recorded", o["exact_platform"] == "TOYOTA_CAMRY_TSS3" and "byte-exact EPS F181" in o["identity_binding"])
check("ambiguous legacy fingerprint avoided", "179-ID" in o["can_census"] and "147-ID Corolla" in o["can_census"] and "strict subset" in o["can_census"])
check("same-car replay coverage recorded", o["carstate_replay"] == ["0x025", "0x030", "0x127 P/R/N/D/B", "0x51E Ready 0/1"])
check("shadow controller sends zero CAN", "returns zero CAN" in o["controller_boundary"])
check("Panda production path remains disabled", "ALLOW_DEBUG-only" in o["panda_boundary"] and "0x0B6 is absent" in o["panda_boundary"] and "SafetyModel.noOutput" in o["panda_boundary"])
check("production output remains unauthorized", o["production_output_authorized"] is False and "steering CAN transmission" in art["boundary"])

print("\n== canonical documentation ==")
report = REPORT.read_text(encoding="utf-8")
findings = FINDINGS.read_text(encoding="utf-8")
corrections = CORRECTIONS.read_text(encoding="utf-8")
priorities = PRIORITIES.read_text(encoding="utf-8")
for token in ("ab60fd95", "d7d7dfd7e", "0x4C000", "0x4C7AA", "0x4CED0", "0x4CE08", "SafetyModel.noOutput", "179-ID", "147-ID"):
    check(f"dedicated port report contains {token}", token in report)
check("VAR-058 registered", "| VAR-058 |" in findings and "8965F3307000" in findings and "ab60fd95" in findings)
check("CORR-120 registered", "### CORR-120" in corrections and "0x4C000" in corrections and "VAR-056" in corrections and "five" in corrections.lower())
check("priorities record passive port", "ab60fd95" in priorities and "production output remains disabled" in priorities.lower())

print(f"\nResults: {p} passed, {f} failed")
raise SystemExit(1 if f else 0)
