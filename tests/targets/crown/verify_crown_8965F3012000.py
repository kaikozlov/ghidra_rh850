#!/usr/bin/env python3
"""Verify canonical Crown 8965F3012000 target identity and Camry comparison."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys

from tools import REPO_ROOT
ROOT = REPO_ROOT
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
check("boot core transfers byte-for-byte", x["raw_identity"]["boot_core_0_9200_identical"] and x["raw_identity"]["first_differing_offset"] == "0x00A004")
check("application entry stays 0x20880", x["raw_identity"]["application_entry_pointer_same"] and x["raw_identity"]["application_entry_pointer"] == "0x00020880")
check("all three recovered crypto roots transfer", all(v["identical"] for v in x["crypto_roots"].values()))
cf = CF.read_bytes()
camry = (ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()
check("independent getters return complete DID metadata geometry",
      cf[0x4FE86:0x4FE96] == bytes.fromhex("06f0200ef200800c2a06988f02007f00")
      and camry[0x50990:0x509A0] == bytes.fromhex("06f0200ef200800c2a067c9202007f00")
      and x["rdbi"]["crown_table"] == "0x00028F98"
      and x["rdbi"]["camry_table"] == "0x0002927C"
      and x["rdbi"]["count"] == 242)
check("full DID metadata membership transfers including leading 0100",
      x["rdbi"]["did_membership_identical"]
      and cf[0x28F98:0x28F9C] == camry[0x2927C:0x29280] == bytes.fromhex("00012000")
      and all(cf[0x28F98 + i * 16:0x28F9C + i * 16]
              == camry[0x2927C + i * 16:0x29280 + i * 16]
              for i in range(242)))
check("Crown context loader only changes TP immediate", x["application_context"]["differing_byte_offsets"] == [32,33] and x["application_context"]["crown_tp"] == "0x00023C98")
check("command5 wrapper/dispatcher/payload packer raw bodies transfer", all(k in x["exact_body_mappings"] for k in ("command5_sync_wrapper","command5_dispatcher","freshness48_packer")))
c7 = x["c7_ingress_boundary"]
check("Camry production config enables XCP family5", c7["camry"]["family_routes"] == [0,255,2,255,255,4] and c7["camry"]["family_counts"] == [5,0,4,0,0,1] and c7["camry"]["family5_route"] == 4 and c7["camry"]["family5_count"] == 1)
check("Crown production config disables XCP family5", c7["crown"]["family_routes"] == [0,255,2,255,255,255] and c7["crown"]["family_counts"] == [5,0,4,0,0,0] and c7["crown"]["family5_route"] == 0xFF and c7["crown"]["family5_count"] == 0)
check("Camry XCP rule and wire IDs are exact", c7["camry"]["xcp_rule_raw_gaflid"] == "0x9FDC0002" and c7["camry"]["request_word_occurrences"] == 2 and c7["camry"]["response_word_occurrences"] == 1)
check("Crown omits stock XCP rule and wire IDs coherently", "0x9FDC0002" not in c7["crown"]["acceptance_ids"] and c7["crown"]["request_word_occurrences"] == 0 and c7["crown"]["response_word_occurrences"] == 0)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
