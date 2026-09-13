#!/usr/bin/env python3
"""Verify canonical Crown 8965F3012000 target identity and Camry comparison."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = ROOT / "firmware/crown-8965F3012000/CodeFlash.bin"
DF = ROOT / "firmware/crown-8965F3012000/DataFlash.bin"
ART = ROOT / "data/generated/crown_8965F3012000_camry_comparison.json"

passed = failed = 0

def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond); passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))

check("Crown CodeFlash exact", CF.stat().st_size == 0x100000 and hashlib.sha256(CF.read_bytes()).hexdigest() == "5b89fdbc69edc2f66ef8a557f88b08c758e3146bd4e90067320d7966812b1273")
check("Crown DataFlash exact", DF.stat().st_size == 0x8000 and hashlib.sha256(DF.read_bytes()).hexdigest() == "0c7b027900d4ac12a4e665e17c0575d44efb0ccfbcb6239416a40c8260c50872")
for tool in (
    ROOT / "tools/targets/crown/builders/promote_crown_analysis_inputs.py",
    ROOT / "tools/targets/crown/analysis/analyze_crown_8965F3012000_camry_comparison.py",
):
    r = subprocess.run([sys.executable, str(tool), "--check"], cwd=ROOT, capture_output=True, text=True)
    check(f"{tool.name} reproduces tracked output", r.returncode == 0, r.stderr.strip())

x = json.loads(ART.read_text())
check("comparison schema exact", x["schema"] == "crown-8965f3012000-camry-f33-comparison-v1")
check("boot core transfers byte-for-byte", x["raw_identity"]["boot_core_0_9200_identical"] and x["raw_identity"]["first_differing_offset"] == "0x00A004")
check("application entry stays 0x20880", x["raw_identity"]["application_entry_pointer_same"] and x["raw_identity"]["application_entry_pointer"] == "0x00020880")
check("all three recovered crypto roots transfer", all(v["identical"] for v in x["crypto_roots"].values()))
check("RDBI DID surface transfers exactly", x["rdbi"]["count"] == 241 and x["rdbi"]["unique_callbacks"] == 195 and x["rdbi"]["did_membership_identical"])
check("Crown context loader only changes TP immediate", x["application_context"]["differing_byte_offsets"] == [32,33] and x["application_context"]["crown_tp"] == "0x00023C98")
check("command5 wrapper/dispatcher/payload packer raw bodies transfer", all(k in x["exact_body_mappings"] for k in ("command5_sync_wrapper","command5_dispatcher","freshness48_packer")))
check("Camry C7 raw ID does not transfer blindly", x["c7_ingress_boundary"]["camry_raw_occurrences"] == 2 and x["c7_ingress_boundary"]["crown_raw_occurrences"] == 0)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
