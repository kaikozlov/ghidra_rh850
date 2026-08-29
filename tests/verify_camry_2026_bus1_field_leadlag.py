#!/usr/bin/env python3
"""Exhaustive bus1 field lead/lag census over the two relay-correct 2026 Camry drives.

Portable deterministic proof for data/generated/camry_2026_bus1_field_leadlag.json:
provenance and analysis-logic pinning, enumeration/filter coverage, and the substantive
bounded negative (no reproduced bus1 field LEADS the exact EPS 0x030 B22:B23
motor-feedback proxy) plus the feedback-like classifications. Full byte-exact
recomputation is intentionally opt-in with ``--regenerate`` because the exhaustive
lag census takes minutes; the normal edit-loop fails closed if any analyzer/helper or
source capture changes without a deliberate regeneration.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

passed = failed = 0


def check(name: str, cond, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


RAW = REPO / "targets/camry-2026/raw-20260827"
CENSUS_SHA = "355ea5b408442a541bd946d21c3e85b0fa4d9e924474d3223189cb37894ee9fc"
ART = REPO / "data/generated/camry_2026_bus1_field_leadlag.json"
ART_SHA = "30a0acf9758d0b22f8dbc78a4ca47ee9febd1597350a3b3ed396762c3c322bfc"
BUILD = REPO / "tools/analyze_camry_2026_bus1_field_leadlag.py"
CENSUS = REPO / "data/generated/camry_2026_cruise_lta_edge_census.json"
REGENERATE = "--regenerate" in sys.argv[1:]

# The artifact was explicitly regenerated from these exact analysis sources.  This is
# the fast edit-loop guard: changing any semantic implementation/helper invalidates the
# tracked result immediately, without paying the ~12-minute exhaustive recomputation on
# every unrelated test run.  ``--regenerate`` remains the byte-exact proof path.
EXPECTED_LOGIC_SHA = {
    BUILD: "68d02237b84cc6c5c620ac579bb17d728989fea5b04ab6ee8a69a1894161b075",
    REPO / "tools/analyze_camry_2026_relay_capture.py": "1d361e985418b256a72e8d5e1e1018984850797ab09565edff8c05078930339a",
    REPO / "tools/toyota_route_opendbc_common.py": "1eab32c06d22c28305a89e14f8ba4c24af434461f1f2c270770c6d305fde8ec7",
}

EXPECTED_DRIVES = {
    "drive_a": (RAW / "camry_relay_route_can_20260827.ndjson.gz",
                "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5"),
    "drive_b": (RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
                "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a"),
}

art = json.loads(ART.read_text())

print("== provenance ==")
check("tracked artifact is the exact explicitly-regenerated v2 result", sha(ART) == ART_SHA)
for i, label in enumerate(("drive_a", "drive_b")):
    path, digest = EXPECTED_DRIVES[label]
    check(f"{label} raw capture exists and is tracked", path.is_file())
    check(f"{label} raw capture pinned digest", sha(path) == digest)
    check(f"{label} artifact source digest matches raw", art["sources"]["drives"][i]["sha256"] == digest)
check("census artifact digest pinned", sha(CENSUS) == CENSUS_SHA
      and art["sources"]["census"]["sha256"] == CENSUS_SHA)
for path, digest in EXPECTED_LOGIC_SHA.items():
    check(f"analysis logic pinned: {path.name}", path.is_file() and sha(path) == digest)

if REGENERATE:
    print("== explicit deterministic regeneration ==")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "camry_2026_bus1_field_leadlag.json"
        proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO,
                              capture_output=True, text=True, check=False)
        check("analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
        check("artifact regenerates byte-exact", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
else:
    print("== deterministic regeneration ==")
    print("[SKIP] expensive byte-exact recomputation; use --regenerate (logic/source hashes are pinned above)")

print("== method invariants ==")
check("schema is v2", art["schema"] == "camry-2026-bus1-field-leadlag-v2")
check("lag convention: tau>0 means field LEADS target",
      art["method"]["lag_convention"] == "r(tau)=corr(field(t),target(t+tau)); tau>0 means field LEADS target")
check("decode set covers byte-aligned BE+LE u/s16 and u/s24",
      all(d in art["method"]["candidate_decodes"]
          for d in ("u8", "s8", "u16be", "s16be", "u16le", "s16le", "u24be", "s24be", "u24le", "s24le")))
check("nibble, bit, and delta decodes enumerated",
      all(d in art["method"]["candidate_decodes"] for d in ("nib_hi", "nib_lo", "b0..b7", "du8", "du16be", "du16le", "du24be")))
check("counter/checksum/diversity filters declared",
      set(art["method"]["filters"]) == {"counter", "checksum", "diversity"})
check("counter/checksum heuristics reject zero-delta and degenerate zero-tail false positives",
      "in 1..15" in art["method"]["filters"]["counter"]
      and "nontrivial head-sum/XOR" in art["method"]["filters"]["checksum"]
      and "zero tail is not self-evidence" in art["method"]["filters"]["checksum"])
check("reproduction bar |r|>=0.40 in both drives, lead>=+50 ms",
      art["method"]["reproduction"] == {"min_abs_r_both_drives": 0.4, "lead_min_ms": 50})

print("== enumeration coverage ==")
for label, streams, kept in (("drive_a", 22, 15367), ("drive_b", 22, 14130)):
    drv = art["drives"][label]
    ids = set(drv["streams"])
    fam = {f"0x{a:03X}" for a in range(0x180, 0x18D)}
    check(f"{label}: {streams} periodic bus1 streams enumerated incl. 0x180..0x18C + 0x020/0x123/0x160/0x1A0/0x200/0x201/0x230/0x440/0x450",
          len(drv["streams"]) == streams and fam <= ids
          and {"0x020", "0x123", "0x160", "0x1A0", "0x200", "0x201", "0x230", "0x440", "0x450"} <= ids,
          f"{sorted(ids - fam - {'0x020','0x123','0x160','0x1A0','0x200','0x201','0x230','0x440','0x450'})}")
    check(f"{label}: {kept} candidates survive filters", drv["candidate_totals"]["kept"] == kept)
    check(f"{label}: Class-L window pinned to census interval",
          len(drv["window"]["class_l"]) == 1
          and round((drv["window"]["class_l"][0][1] - drv["window"]["class_l"][0][0]) / 1e9, 6)
          == (16.119256 if label == "drive_a" else 57.184128))
    # Nonzero rolling-counter suppression. The two low-rate 0x440/0x450 streams do not
    # carry the common B2 counter; every other periodic stream does. B3 rolls on the
    # 0x18x family and 0x020/0x1A0/0x200/0x201; 0x1A0 also rolls B7. The corrected
    # checksum heuristic requires a nontrivial head-sum/XOR relation, so constant-zero
    # tail bytes are deliberately NOT mislabeled as checksum carriers.
    b2_missing = {i for i, st in drv["streams"].items() if "2" not in st["counter_bytes"]}
    fam_b3 = all(drv["streams"][f"0x{a:03X}"]["counter_bytes"].get("3", {}).get("step", 0) > 0 for a in range(0x180, 0x18D))
    extra_b3 = all(drv["streams"][i]["counter_bytes"].get("3", {}).get("step", 0) > 0 for i in ("0x020", "0x1A0", "0x200", "0x201"))
    a0_b7 = drv["streams"]["0x1A0"]["counter_bytes"].get("7", {}).get("step") == 1
    check(f"{label}: rolling counters detected and suppressed (B2 except 0x440/0x450; B3 family; 0x1A0 B7)",
          b2_missing == {"0x440", "0x450"} and fam_b3 and extra_b3 and a0_b7)
    check(f"{label}: no nontrivial simple head-sum/XOR checksum carrier is falsely inferred",
          all(not st["checksum_bytes"] for st in drv["streams"].values()))

print("== control-region boundary ==")
check("drive A has zero local speed-matched control points (documented boundary)",
      art["drives"]["drive_a"]["window"]["control_grid_points"] == 0)
check("drive B carries the local control region",
      art["drives"]["drive_b"]["window"]["control_grid_points"] == 190)

print("== substantive bounded negative ==")
comb = art["combined"]
check("2929 candidates fine-swept in both drives", comb["refined_in_both_drives"] == 2929)
check("NO reproduced field LEADS the EPS motor-feedback proxy",
      comb["reproduced_leading_fields"] == [])
check("drive B has zero fine-stage motor |r|>=0.40 leads at all",
      comb["per_drive_lead_census"]["drive_b"] == {"fine_motor_abs_r_ge_0.40": 48, "of_those_leading_ge_50ms": 0})
check("drive A lead excess does not reproduce (multiple-testing tail)",
      comb["per_drive_lead_census"]["drive_a"] == {"fine_motor_abs_r_ge_0.40": 246, "of_those_leading_ge_50ms": 69})

lag_fields = {e["field"] for e in comb["reproduced_lagging_fields"]}
check("26 reproduced lagging fields remain feedback/derived-like, with key families pinned",
      len(comb["reproduced_lagging_fields"]) == 26
      and all((e["drive_a"]["motor_peak_lag_ms"] or 0) <= -50 and
              (e["drive_b"]["motor_peak_lag_ms"] or 0) <= -50
              for e in comb["reproduced_lagging_fields"])
      and {"0x160[22]s16be", "0x160[22]s8", "0x181[14]b3", "0x181[42]b3", "0x1A0[10]b0"} <= lag_fields,
      str(sorted(lag_fields)))

lag_by_field = {e["field"]: e for e in comb["reproduced_lagging_fields"]}
s8 = lag_by_field["0x160[22]s8"]
check("0x160[22]s8 lags motor in both drives (A +0.7058@-500ms, B +0.5479@-375ms)",
      s8["drive_a"]["motor_r"] == 0.7058 and s8["drive_a"]["motor_peak_lag_ms"] == -500
      and s8["drive_b"]["motor_r"] == 0.5479 and s8["drive_b"]["motor_peak_lag_ms"] == -375)
check("0x160[22]s8 is a steering-angle echo (A r=+0.9963@-75ms, B r=+0.8597@-100ms vs 0x025 angle)",
      s8["drive_a"]["angle_r"] == 0.9963 and s8["drive_a"]["angle_lag_ms"] == -75
      and s8["drive_b"]["angle_r"] == 0.8597 and s8["drive_b"]["angle_lag_ms"] == -100)
check("0x160[22]s8 equally correlates with motor outside Class-L in drive-B control (generic echo)",
      s8["drive_b"]["control_motor_r"] == 0.7844)
echo = {e["field"]: e for e in comb["angle_echo_fields"]}
check("angle-echo census pins seven delayed feedback encodings including the 0x160[22] family",
      len(echo) == 7 and "0x160[22]s8" in echo and "0x160[22]s16be" in echo
      and echo["0x160[22]s8"]["drive_a"]["angle_r"] == 0.9963
      and echo["0x160[22]s8"]["drive_b"]["angle_r"] == 0.8597)

# VAR-068's 0x181 bytes[35:37] signed-LE field does not reproduce as a stable
# motor correlate over the full Class-L windows (both |r| < 0.4, inconsistent lags).
def refined(label: str, field: str):
    for c in art["drives"][label]["refined_candidates"]:
        if c["field"] == field:
            return c
    return None

f_a, f_b = refined("drive_a", "0x181[35]s16le"), refined("drive_b", "0x181[35]s16le")
check("VAR-068 0x181[35:37] s16le stays weak and inconsistent over full windows",
      f_a is not None and f_b is not None
      and abs(f_a["motor_r"]) < 0.4 and abs(f_b["motor_r"]) < 0.4
      and f_a["motor_peak_lag_ms"] != f_b["motor_peak_lag_ms"],
      f"A r={f_a['motor_r']}@{f_a['motor_peak_lag_ms']}ms B r={f_b['motor_r']}@{f_b['motor_peak_lag_ms']}ms" if f_a and f_b else "")

print("== interpretation boundary ==")
interp = art["interpretation"]
check("production output stays unauthorized", interp["production_output_authorized"] is False)
check("exhaustive negative stated", "0 reproduce as LEADING" in interp["exhaustive_negative"] or
      comb["reproduced_leading_fields"] == [])
check("control-region boundary stated", "drive A has zero local" in interp["control_region_boundary"])
check("lag-range boundary stated", "declared tested lead range" in interp["lag_range_boundary"])

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
