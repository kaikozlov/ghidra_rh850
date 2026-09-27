#!/usr/bin/env python3
"""Verify retained-drive behavior of the exact-F33 baseline parameter-bank selector."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT
ART = REPO / "data/generated/camry_2026_baseline_selector_live.json"
BUILD = REPO / "tools/targets/camry/analysis/analyze_camry_2026_baseline_selector.py"
RAW = REPO / "targets/camry-2026/raw-20260827"

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
    check(f"{label} raw source pinned", sha(exp["file"]) == DRIVE_SHA[label])
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
check("zero reproduced selector edge changes", combined["class_l_edge_value_changes"] == 0)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
