#!/usr/bin/env python3
"""Regenerate committed Corolla H/F builder artifacts (full/local only)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = REPO = Path(__file__).resolve().parents[1]
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


BUILDERS = [
    ("command5 runtime carrier", "tools/build_corolla_hf_command5_runtime_carrier.py", "data/generated/corolla_hf_command5_runtime_carrier.json"),
    ("steering limits", "tools/build_corolla_hf_steering_limits.py", "data/generated/corolla_hf_steering_limits.json"),
    ("nonsteering engagement state", "tools/build_corolla_hf_nonsteering_engagement_state.py", "data/generated/corolla_hf_nonsteering_engagement_state.json"),
    ("cooperative authority wire visibility", "tools/build_corolla_hf_cooperative_authority_wire_visibility.py", "data/generated/corolla_hf_cooperative_authority_wire_visibility.json"),
    ("B6 competing sender arbitration", "tools/build_corolla_hf_b6_competing_sender_arbitration.py", "data/generated/corolla_hf_b6_competing_sender_arbitration.json"),
    ("fault state contract", "tools/build_corolla_hf_fault_state_contract.py", "data/generated/corolla_hf_fault_state_contract.json"),
    ("panda lateral safety contract", "tools/build_corolla_hf_panda_lateral_safety_contract.py", "data/generated/corolla_hf_panda_lateral_safety_contract.json"),
    ("remaining status contract", "tools/build_corolla_hf_remaining_status_contract.py", "data/generated/corolla_hf_remaining_status_contract.json"),
    ("command5 portability", "tools/build_corolla_hf_command5_portability.py", "data/generated/corolla_hf_command5_portability.json"),
]

for title, builder, artifact in BUILDERS:
    print(f"== {title} regen ==")
    tool = ROOT / builder
    art = ROOT / artifact
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.json"
        proc = subprocess.run(
            [sys.executable, str(tool), "--out", str(out)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        check(f"{title} builder exits cleanly", proc.returncode == 0, (proc.stderr or proc.stdout)[-300:] if proc.returncode else "")
        check(
            f"{title} artifact regenerates exactly",
            proc.returncode == 0 and out.exists() and out.read_bytes() == art.read_bytes(),
        )
    print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
