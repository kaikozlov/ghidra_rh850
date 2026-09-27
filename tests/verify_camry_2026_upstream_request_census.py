#!/usr/bin/env python3
"""Verify the deterministic 0x08A upstream-request field census and GTS+ joins."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_upstream_request_field_census.json"
BUILD = REPO / "tools/targets/camry/analysis/analyze_camry_2026_upstream_request_census.py"

passed = failed = 0


def check(name, condition, detail=""):
  global passed, failed
  ok = bool(condition)
  passed += int(ok)
  failed += int(not ok)
  print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


art = json.loads(ART.read_text())

print("== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as td:
  out = Path(td) / ART.name
  proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO,
                        capture_output=True, text=True, check=False)
  check("offline analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
  check("artifact regenerates byte-identically",
        proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

print("== drive identity and duplication ==")
for drive in ("drive_a", "drive_b"):
  d = art["drives"][drive]
  check(f"{drive}: frames > 15000", d["bus0_frames"] > 15000, str(d["bus0_frames"]))
  check(f"{drive}: B8==B11 in every frame", d["duplication_b8_eq_b11"] == d["bus0_frames"])
  check(f"{drive}: B9==B12 in every frame", d["duplication_b9_eq_b12"] == d["bus0_frames"])
  check(f"{drive}: B13:B14 == 0x7FFF in every frame",
        d["sentinel_b13_b14_0x7fff"] == d["bus0_frames"])
  check(f"{drive}: B16:B17 == 0x7FFF in every frame",
        d["sentinel_b16_b17_0x7fff"] == d["bus0_frames"])
  for byte in ("B00", "B01", "B02", "B05", "B15", "B25", "B27"):
    check(f"{drive}: {byte} zero in every frame",
          d["zero_byte_frames"][byte] == d["bus0_frames"])

print("== B21-state coupling invariants (both drives combined) ==")
inv = art["combined"]["invariants"]
check("B21=11 always carries the cruise latch",
      inv["b21_11_with_cruise_latch"] == inv["b21_11_frames"])
check("B21=11 always carries B24=100", inv["b21_11_with_b24_100"] == inv["b21_11_frames"])
check("B21=18 always has B3 clear", inv["b21_18_with_b3_clear"] == inv["b21_18_frames"])
check("B21=18 always sets B23 bit5", inv["b21_18_with_b23_bit5"] == inv["b21_18_frames"])
check("B21=18 always carries B24=50", inv["b21_18_with_b24_50"] == inv["b21_18_frames"])
check("B20[7:6]/B22[4] mirror the latch except bounded transitions",
      inv["latch_mirror_agreement"] >= art["combined"]["bus0_frames_total"] - 30,
      f"{inv['latch_mirror_agreement']}/{art['combined']['bus0_frames_total']}")

print("== request-word negative joins bound semantics ==")
for drive in ("drive_a", "drive_b"):
  j = art["drives"][drive]["request_word_negative_joins"]
  for join in ("speed_accel", "steer_angle_025", "driver_torque_030", "target_angle_rate"):
    check(f"{drive}: |r|({join}) <= 0.10", j[join] is not None and abs(j[join]) <= 0.10, str(j[join]))

print("== B21 state sets are exactly {0,11,18} ==")
for drive in ("drive_a", "drive_b"):
  states = set(art["drives"][drive]["byte_census_by_b21_state"])
  check(f"{drive}: B21 value set", states == {"0", "11", "18"}, str(sorted(states)))

print()
print(f"passed={passed} failed={failed}")
sys.exit(1 if failed else 0)
