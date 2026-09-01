#!/usr/bin/env python3
"""Verify the exact-F33 DataFlash NvM owner/layout closure artifact.

Asserts the maintainer-question closure: on the exact maintainer Camry, the
unexamined DataFlash learned NvM state does not feed the assist funnel. Every
pillar is checked against the generated artifact, and the artifact must
regenerate byte-identically from the tracked tool.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_8965F3307000_dataflash_nvm_owners.json"
TOOL = ROOT / "tools/analyze_camry_8965F3307000_dataflash_nvm_owners.py"
D = json.loads(ART.read_text())
failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name}: {detail}")
        failures.append(name)


check("schema pinned", D["schema"] == "camry-8965f3307000-dataflash-nvm-owner-closure-v1")
check("inputs bind the exact F33 image",
      D["inputs"]["codeflash"]["sha256"].startswith("42dce8ef")
      and D["inputs"]["dataflash"]["sha256"].startswith("231fbdde"))

jt = D["job_table"]
check("boot job table decoded at ROM 0x27636",
      jt["rom_address"] == "0x27636" and jt["handle_count"] == 48
      and "FUN_00074884" in jt["decoded_from"])

sc = D["slot_census"]
check("per-slot committed census present",
      sc["committed_slots"] == 9 and sc["total_slots"] == 48)
banks = sc["slot_census"]
check("object-0 raw/xor55/xoraa family fully committed",
      banks["bank_si_1_5_9_..."]["committed"] == 3)
check("adjacent interleaved banks uncommitted",
      banks["bank_si_2_6_10_..."]["committed"] == 0
      and banks["bank_si_4_8_12_..."]["committed"] == 0)

live = D["live_learned_state"]
check("live four-channel torque offsets at neutral 0x0800",
      live["four_channel_offsets_neutral"] is True)
check("live 45-byte learned block staged==active",
      live["staged_active_equal_45b"] is True)

cen = D["census"]
check("45 corpus functions touch learned cells", cen["functions_touching_learned_cells"] == 45)
check("zero functions touch both learned cells and the assist funnel",
      cen["functions_touching_both"] == [])

con = D["conclusion"]
check("conclusion records the negative",
      con["dataflash_learned_state_feeds_assist_funnel"] is False
      and any("0x0800" in r for r in con["reasons"]))

with tempfile.TemporaryDirectory() as td:
    regen = Path(td) / "nvm_owners.json"
    subprocess.run([sys.executable, str(TOOL), "--output", str(regen)], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    check("artifact regenerates byte-identically", regen.read_bytes() == ART.read_bytes())

if failures:
    raise SystemExit(f"{len(failures)} failed checks: {', '.join(failures)}")
print("all checks passed")
