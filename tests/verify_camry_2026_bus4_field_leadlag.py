#!/usr/bin/env python3
"""Verify the exhaustive relay-correct Toyota-Bus-4 field lead/lag census.

The normal edit-loop pins exact source/analyzer/artifact hashes and the substantive
cross-drive negative. ``--regenerate`` opts into the ~6-minute byte-exact full replay.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
ART = REPO / "data/generated/camry_2026_bus4_field_leadlag.json"
BUILD = REPO / "tools/analyze_camry_2026_bus4_field_leadlag.py"
CENSUS = REPO / "data/generated/camry_2026_cruise_lta_edge_census.json"
REGENERATE = "--regenerate" in sys.argv[1:]
passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


EXPECTED = {
    ART: "25d625ca2c5d1aeedcd06c3d1fe5647b3425e2470ff1ef806e98e9b7b77eaea0",
    BUILD: "e53e30ed28fac057459e32e7bf6615908aaf4dfb6faee6d80142d04653fd29ec",
    REPO / "tools/analyze_camry_2026_relay_capture.py": "1d361e985418b256a72e8d5e1e1018984850797ab09565edff8c05078930339a",
    REPO / "tools/toyota_route_opendbc_common.py": "1eab32c06d22c28305a89e14f8ba4c24af434461f1f2c270770c6d305fde8ec7",
    CENSUS: "355ea5b408442a541bd946d21c3e85b0fa4d9e924474d3223189cb37894ee9fc",
}
DRIVES = {
    "drive_a": (RAW / "camry_relay_route_can_20260827.ndjson.gz",
                "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5"),
    "drive_b": (RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
                "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a"),
}

art = json.loads(ART.read_text())

print("== provenance ==")
for path, digest in EXPECTED.items():
    check(f"pinned hash: {path.name}", path.is_file() and sha(path) == digest)
for i, label in enumerate(("drive_a", "drive_b")):
    path, digest = DRIVES[label]
    check(f"{label} raw capture hash pinned", path.is_file() and sha(path) == digest)
    check(f"{label} artifact source hash matches", art["sources"]["drives"][i] == {
        "label": label, "path": str(path.relative_to(REPO)), "sha256": digest})
check("census source hash matches", art["sources"]["census"]["sha256"] == EXPECTED[CENSUS])

if REGENERATE:
    print("== explicit byte-exact regeneration ==")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "bus4.json"
        p = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO,
                           capture_output=True, text=True, check=False)
        check("analyzer exits clean", p.returncode == 0, p.stderr[-300:])
        check("artifact regenerates byte-exact", p.returncode == 0 and out.read_bytes() == ART.read_bytes())
else:
    print("== deterministic regeneration ==")
    print("[SKIP] expensive full replay; use --regenerate (source/analyzer/artifact hashes pinned above)")

print("== method and denominator ==")
check("schema exact", art["schema"] == "camry-2026-bus4-field-leadlag-v1")
method = art["method"]
check("network identity is relay-correct Toyota Bus4", "Toyota Bus4 Brake/EPS" in method["network"])
check("lag convention is causal-positive", "tau>0 means field LEADS target" in method["lag_convention"])
check("decode set contains 10/12-bit, endian scalar, bits/nibbles/deltas",
      all(x in method["candidate_decodes"] for x in
          ("u8","s8","u16be","s16be","u16le","s16le","u24be","s24be",
           "w12","s12","w10","s10","nib_hi","nib_lo","b0..b7","du8","du16be","du16le","du24be")))
check("cross-drive threshold exact", method["reproduction"] == {"lead_min_ms": 50, "min_abs_r_both_drives": 0.4})
check("low-rate exclusion boundary explicit", "continuous EPS steering carrier" in method["low_rate_boundary"])

expected_drv = {
    "drive_a": (200, 5021, 2221, 0),
    "drive_b": (153, 5448, 1803, 190),
}
for label, (streams, kept, refined, control) in expected_drv.items():
    d = art["drives"][label]
    check(f"{label} stream/kept/refined denominator exact",
          d["candidate_totals"]["streams"] == streams
          and d["candidate_totals"]["kept"] == kept
          and len(d["refined_candidates"]) == refined)
    check(f"{label} local-control denominator exact", d["window"]["control_grid_points"] == control)

print("== substantive matched negative ==")
c = art["combined"]
check("930 fields refined in both drives", c["refined_in_both_drives"] == 930)
check("69 fields reproduce strongly vs motor", c["reproduced_strong_motor_fields"] == 69)
check("zero reproduced motor leads >=50 ms", c["reproduced_motor_leads_ge_50ms"] == [])
check("zero reproduced rate leads >=50 ms", c["reproduced_rate_leads_ge_50ms"] == [])
check("all reproduced angle leads are EPS Tx 0x030",
      len(c["reproduced_angle_leads_ge_50ms"]) == 10
      and all(x.startswith("0x030") for x in c["reproduced_angle_leads_ge_50ms"])
      and c["angle_leads_outside_eps_tx_0x030"] == [])
check("all 25-ms motor near-leads are EPS Tx 0x030",
      len(c["reproduced_motor_near_leads_25_to_49ms"]) == 4
      and all(x.startswith("0x030") for x in c["reproduced_motor_near_leads_25_to_49ms"]))

sel = c["selected_fields"]
check("0x030 motor proxy is identity at zero lag",
      sel["0x030[22]s16be"]["drive_a"]["motor_r"] == 0.999
      and sel["0x030[22]s16be"]["drive_a"]["motor_peak_lag_ms"] == 0
      and sel["0x030[22]s16be"]["drive_b"]["motor_r"] == 0.9994
      and sel["0x030[22]s16be"]["drive_b"]["motor_peak_lag_ms"] == 0)
check("0x030 torque-family byte positively leads measured steering angle",
      sel["0x030[8]s8"]["drive_a"]["angle_peak_lag_ms"] == 350
      and sel["0x030[8]s8"]["drive_b"]["angle_peak_lag_ms"] == 250
      and sel["0x030[8]s8"]["drive_a"]["torque_r"] == 0.9991
      and sel["0x030[8]s8"]["drive_b"]["torque_r"] == 0.9983)
check("0x081/0x08A angle echoes lag motor in both drives",
      all(sel[f][d]["motor_peak_lag_ms"] <= -200 for f in ("0x081[16]s16be","0x08A[18]s16be")
          for d in ("drive_a","drive_b")))
check("0x090 retained composite remains lagging in both drives",
      sel["0x090[12]w12"]["drive_a"]["motor_peak_lag_ms"] == -325
      and sel["0x090[12]w12"]["drive_b"]["motor_peak_lag_ms"] == -500)

print("== interpretation boundary ==")
interp = art["interpretation"]
check("ordinary-CAN negative does not claim physical actuation closure",
      "does not prove the physical LTA actuation path" in interp["meaning"]
      and "downstream motor-reference" in interp["meaning"])
check("production output stays unauthorized", interp["production_output_authorized"] is False)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
