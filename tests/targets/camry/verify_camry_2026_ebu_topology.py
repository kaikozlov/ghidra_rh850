#!/usr/bin/env python3
"""Verify the exact-Camry EBU topology interpretation against current GTS+."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
ROOT = REPO_ROOT
ART = ROOT / "data/generated/camry_2026_ebu_topology.json"
GEN = ROOT / "tools/targets/camry/analysis/analyze_camry_2026_ebu_topology.py"

passed = failed = 0


def check(name: str, value: object) -> None:
    global passed, failed
    ok = bool(value)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][camry_ebu] {name}")


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "ebu.json"
    proc = subprocess.run([sys.executable, str(GEN), "--output", str(out)], cwd=ROOT,
                          capture_output=True, text=True, check=False)
    check("generator exits cleanly", proc.returncode == 0)
    check("artifact regenerates byte-exact", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
exact = art["exact_camry"]
check("exact Camry denominator is three current vehicle types and 18 options",
      [x["id"] for x in exact["vehicle_types"]] == [12704, 12862, 12984]
      and exact["can_bus_car_id"] == "0x00A7D910" and exact["option_count"] == 18)
check("logical membership is invariant while physical junction labels can vary",
      exact["network_membership_variant_count"] == 1 and exact["junction_attachment_variant_count"] == 12)

bus4 = {row["component_index"]: row for row in exact["bus4_placements"]}
check("EPS is Bus4 via literal EBU attachment in every option",
      bus4["0x32"]["junction_name"] == "EBU")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
