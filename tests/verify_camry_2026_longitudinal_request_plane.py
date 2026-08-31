#!/usr/bin/env python3
"""Verify the retained Camry TSS3 longitudinal protected/plaintext cross-plane join."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_longitudinal_request_plane.json"
BUILD = REPO / "tools/analyze_camry_2026_longitudinal_request_plane.py"

passed = failed = 0


def check(name: str, cond, detail: str = "") -> None:
  global passed, failed
  ok = bool(cond)
  passed += int(ok)
  failed += int(not ok)
  print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def approx(a: float, b: float, eps: float = 1e-9) -> bool:
  return abs(a - b) <= eps


art = json.loads(ART.read_text())
check("schema", art["schema"] == "camry-2026-longitudinal-request-plane-v1")

print("== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as td:
  out = Path(td) / ART.name
  proc = subprocess.run(
    [sys.executable, str(BUILD), "--output", str(out)],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
  )
  check("analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
  check("artifact regenerates byte-exact", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

expected = {
  "drive_a": {
    "sha": "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5",
    "ca_buses": {"0": 21879, "1": 0, "2": 21880},
    "x160": 20510,
    "reset": 0.855706385,
    "app_pairs": (21729, 20026, 20026),
    "auth": 0.999954294,
    "geom_n": 1947,
    "geom": 0.978941962,
    "accel_r": 0.519732977,
    "accel_shift": 0.6,
    "join_n": 1834,
    "join_r": -0.951664059,
    "join_slope": -0.097299385,
    "unsat_n": 1218,
    "unsat_r": -0.911522875,
    "unsat_slope": -0.099274255,
  },
  "drive_b": {
    "sha": "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a",
    "ca_buses": {"0": 25475, "1": 0, "2": 25475},
    "x160": 23998,
    "reset": 0.858903894,
    "app_pairs": (25465, 23465, 23465),
    "auth": 0.999921492,
    "geom_n": 4804,
    "geom": 0.944421316,
    "accel_r": 0.785714287,
    "accel_shift": 0.3,
    "join_n": 4526,
    "join_r": -0.989395798,
    "join_slope": -0.118672776,
    "unsat_n": 3826,
    "unsat_r": -0.986808299,
    "unsat_slope": -0.119391143,
  },
}

for label, e in expected.items():
  d = art["drives"][label]
  ca = d["protected_0x0CA"]
  sec = ca["secoc_shape_bus0"]
  seq = sec["application_sequence_relation"]
  geom = ca["longitudinal_geometry"]
  x = d["plaintext_candidate_0x160"]
  join = x["B12_signed7_to_0x0CA_result"]

  print(f"== {label} ==")
  check(f"{label}: raw route identity", d["source"]["sha256"] == e["sha"])
  check(f"{label}: 0x0CA is Bus0/Bus2 protected-plane traffic, absent Bus1", ca["panda_bus_counts"] == e["ca_buses"])
  check(f"{label}: 0x0CA full FV4 nibble cycle", sec["fv4_value_set"] == list(range(16)))
  check(f"{label}: 0x0CA B27 zero", sec["b27_value_set"] == [0])
  check(f"{label}: 0x0CA reset-low2 follows 0x00F", approx(sec["preceding_0x00F_reset_low2"]["matching_fraction"], e["reset"]))
  check(f"{label}: 0x0CA application/message sequence relation exact",
        (seq["same_segment_plus1_pairs"], seq["same_reset_plus1_pairs"], seq["same_reset_pairs_with_message_low2_plus1"]) == e["app_pairs"]
        and seq["same_reset_message_plus1_fraction"] == 1.0)
  check(f"{label}: 0x0CA authenticator candidate nearly frame-unique", approx(sec["auth28_unique_fraction"], e["auth"]))
  check(f"{label}: 0x0CA upper/lower/result-like cruise geometry",
        geom["stock_cruise_frame_count"] == e["geom_n"]
        and approx(geom["B5_B6_le_B7_B8_le_B3_B4"]["matching_fraction"], e["geom"]))
  check(f"{label}: 0x0CA B7:B8 tracks wheel-speed-derived acceleration",
        approx(ca["measured_acceleration_join"]["pearson_r"], e["accel_r"])
        and ca["measured_acceleration_join"]["best_shift_s"] == e["accel_shift"])

  check(f"{label}: 0x160 exists only on native Bus1", x["panda_bus_counts"] == {"0": 0, "1": e["x160"], "2": 0})
  check(f"{label}: 0x160 has constant zero trailing four bytes", x["last4_histogram"] == {"00000000": e["x160"]})
  check(f"{label}: 0x160 B12 is a valid signed7 candidate", x["B12_high_bit_histogram"] == {"0": e["x160"]})
  check(f"{label}: 0x160 B12 signed7 tightly joins 0x0CA B7:B8",
        join["all"]["sample_count"] == e["join_n"]
        and approx(join["all"]["pearson_r"], e["join_r"])
        and approx(join["all"]["slope"], e["join_slope"]))
  check(f"{label}: 0x160/0x0CA relation persists away from arbitration bounds",
        join["unsaturated_result"]["sample_count"] == e["unsat_n"]
        and approx(join["unsaturated_result"]["pearson_r"], e["unsat_r"])
        and approx(join["unsaturated_result"]["slope"], e["unsat_slope"]))

print("== interpretation boundaries ==")
check("0x0CA is explicitly not classified as unsigned pre-sign", "Already-protected" in art["interpretation"]["0x0CA"])
check("0x160 candidate remains source/direction bounded", "producer, direction" in art["interpretation"]["0x160_B12"])
check("next discriminator is the prepared synchronized FRC/Brake capture",
      "camry_tss3_request_capture.py" in art["interpretation"]["next_discriminator"]
      and "1B03..1B07" in art["interpretation"]["next_discriminator"]
      and "10A1..10A4" in art["interpretation"]["next_discriminator"])

print(f"Summary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
