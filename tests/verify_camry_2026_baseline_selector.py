#!/usr/bin/env python3
"""Verify retained-drive behavior of the exact-F33 baseline parameter-bank selector."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_baseline_selector_live.json"
BUILD = REPO / "tools/analyze_camry_2026_baseline_selector.py"
STATIC = REPO / "data/generated/camry_8965F3307000_command_cone_ingress.json"
CENSUS = REPO / "data/generated/camry_2026_cruise_lta_edge_census.json"
RAW = REPO / "targets/camry-2026/raw-20260827"

STATIC_SHA = "01858fab5510b6302de9a57fa27ce09b3228670bd06ba8af082f7833ff5c1034"
CENSUS_SHA = "355ea5b408442a541bd946d21c3e85b0fa4d9e924474d3223189cb37894ee9fc"
DRIVE_SHA = {
    "drive_a": "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5",
    "drive_b": "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a",
}

passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][dynamic_trace] {name}" + (f" ({detail})" if detail else ""))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


art = json.loads(ART.read_text())

print("== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "selector.json"
    p = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO,
                       capture_output=True, text=True, check=False)
    check("analyzer succeeds", p.returncode == 0, p.stderr[-300:] if p.returncode else "")
    check("artifact regenerates byte-exact", p.returncode == 0 and out.read_bytes() == ART.read_bytes())

print("== provenance/static contract ==")
check("schema exact", art["schema"] == "camry-2026-baseline-selector-live-v1")
check("exact static selector artifact pinned",
      sha(STATIC) == STATIC_SHA and art["sources"]["static_selector"]["sha256"] == STATIC_SHA)
check("Class-L census pinned",
      sha(CENSUS) == CENSUS_SHA and art["sources"]["class_l_census"]["sha256"] == CENSUS_SHA)
check("selector scope is exactly seven ordinary COM signals",
      art["selector_scope"]["signals"] == [160, 163, 166, 224, 280, 281, 282]
      and art["selector_scope"]["can_ids"] == ["0x13B", "0x1DA", "0x490", "0x51E"]
      and "not command magnitudes" in art["selector_scope"]["role"])

expected = {
    "drive_a": {
        "file": RAW / "camry_relay_route_can_20260827.ndjson.gz",
        "class_l_duration_s": 16.119256,
        "counts": {"sig160": (519, 16), "sig163": (519, 16), "sig166": (519, 16), "sig224": (17176, 537)},
    },
    "drive_b": {
        "file": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
        "class_l_duration_s": 57.184128,
        "counts": {"sig160": (600, 57), "sig163": (600, 57), "sig166": (600, 57), "sig224": (20000, 1906)},
    },
}

print("== retained-drive selector inputs ==")
for label, exp in expected.items():
    drv = art["drives"][label]
    check(f"{label} raw source pinned", sha(exp["file"]) == DRIVE_SHA[label]
          and drv["source"]["sha256"] == DRIVE_SHA[label])
    check(f"{label} Class-L duration exact", drv["class_l_duration_s"] == exp["class_l_duration_s"])
    check(f"{label} four observed selector signals are zero over the complete route",
          all(drv["signals"][sig]["all"] == {"frames": all_n, "values": {"0": all_n}}
              for sig, (all_n, _class_n) in exp["counts"].items()))
    check(f"{label} same four selector signals stay zero throughout Class-L",
          all(drv["signals"][sig]["class_l"] == {"frames": class_n, "values": {"0": class_n}}
              for sig, (_all_n, class_n) in exp["counts"].items()))
    check(f"{label} 0x490/0x1DA selector signals are absent",
          drv["summary"]["unobserved_signals"] == ["sig280", "sig281", "sig282"]
          and all(drv["signals"][sig]["all"] == {"frames": 0, "values": {}}
                  for sig in ("sig280", "sig281", "sig282")))
    check(f"{label} no Class-L 3-second edge window changes selector value support",
          drv["summary"]["class_l_edge_value_changes"] == 0
          and all(not edge["value_set_changed"]
                  for sig in drv["signals"].values() for edge in sig["class_l_edges_3s"]
                  if edge["pre_frames"] and edge["post_frames"]))

print("== interpretation boundary ==")
combined = art["combined"]
check("all observed ordinary selector inputs are route-wide constant zero",
      combined["all_observed_selector_inputs_constant_zero"] is True)
check("zero reproduced selector edge changes", combined["class_l_edge_value_changes"] == 0)
check("conclusion excludes ordinary COM selector inputs but retains internal alternatives",
      "do not distinguish Class-L" in combined["classification"]
      and "Internal/fault/diagnostic selector alternatives remain" in combined["classification"])
check("production output remains unauthorized", combined["production_output_authorized"] is False)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
