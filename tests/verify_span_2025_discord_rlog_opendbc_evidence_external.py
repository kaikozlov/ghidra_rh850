#!/usr/bin/env python3
"""Regenerate Span's tracked Discord-rlog opendbc evidence from the raw rlog."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RLOG = REPO / "community/spanconstant/span_67fd5b833889fedf_00000010--17084916da--3--rlog.zst"
OPENPILOT = (REPO / "../kai-openpilot").resolve()
PYTHON = OPENPILOT / ".venv/bin/python"
TRACKED = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}{suffix}")

if not RLOG.is_file() or not PYTHON.is_file():
    print(f"[SKIP] tracked Span rlog/logreader unavailable: rlog={RLOG.is_file()} python={PYTHON.is_file()}")
    raise SystemExit(77)

check("tracked Span Discord rlog exists", RLOG.is_file())
check("external openpilot logreader environment exists", PYTHON.is_file())
with tempfile.TemporaryDirectory(prefix="span-rlog-opendbc-") as td:
    out = Path(td) / "evidence.json"
    proc = subprocess.run([
        str(PYTHON), str(REPO / "tools/extract_span_2025_discord_rlog_opendbc_evidence.py"),
        "--rlog", str(RLOG), "--openpilot-root", str(OPENPILOT), "--output", str(out),
    ], cwd=REPO, capture_output=True, text=True, timeout=180, check=False)
    check("raw Span-rlog extraction succeeds", proc.returncode == 0, proc.stderr.strip()[:200])
    if out.exists():
        check("tracked extraction matches exact raw Span rlog", json.loads(out.read_text()) == json.loads(TRACKED.read_text()))

tracked = json.loads(TRACKED.read_text())
s030 = tracked["direct_reuse_evidence"]["0x030"]
bridge = s030["steering_state_bridge"]
check("Span has 6,000 exact-H/F 0x030 frames", s030["frame_count"] == 6000 and s030["rule_matches"] == 6000)
check("0x030 selected steering fault/inhibit status is nominal-clear in every frame", bridge["steering_fault_inhibit_status"]["values"] == [0] and bridge["steering_fault_inhibit_status"]["clear_frames"] == 6000)
check("0x030 driver-torque-invalid is nominal-clear in every frame", bridge["driver_torque_invalid"]["values"] == [0] and bridge["driver_torque_invalid"]["clear_frames"] == 6000)
check("0x030 neighboring status bit is live", bridge["b6_bit1"]["values"] == [0, 1])
torque = bridge["steering_wheel_torque"]
check("0x030 driver torque exact reconstruction spans real steering load", torque["torque_nm"]["count"] == 6000 and torque["torque_nm"]["min"] < -8.0 and torque["torque_nm"]["max"] > 2.8 and torque["torque_nm"]["unique_count"] > 500)
check("0x030 torque fine remainder is signed decimal digit", torque["fine_values"] == [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
check("0x030 coarse views differ only by expected rounding", torque["coarse_rounding_delta_values"] == [-1, 0, 1] and torque["coarse_rounding_delta_nonzero_frames"] == 2488)
check("0x030 byte16 nominal value is pinned", bridge["byte16_values"] == [2])

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
