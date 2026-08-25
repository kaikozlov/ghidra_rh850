#!/usr/bin/env python3
"""Regenerate the H/F 0x00F freshness bridge from all retained raw CAN sources."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OPENPILOT = (REPO / "../kai-openpilot").resolve()
PYTHON = OPENPILOT / ".venv/bin/python"
SPAN = REPO / "community/spanconstant/span_67fd5b833889fedf_00000010--17084916da--3--rlog.zst"
PUBLIC = REPO / "REFERENCE/public_route_corolla_2023_segment0_rlog.zst"
ALBINO = REPO / "community/albinoelephant/can_oracle.ndjson"
BUILDER = REPO / "tools/build_corolla_hf_secoc_00f_freshness_bridge.py"
TRACKED = REPO / "data/generated/corolla_hf_secoc_00f_freshness_bridge.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}{suffix}")


required = {"openpilot python": PYTHON, "Span rlog": SPAN, "public rlog": PUBLIC, "Albino sync oracle": ALBINO}
missing = [name for name, path in required.items() if not path.is_file()]
if missing:
    print(f"[SKIP] required external/local sources unavailable: {', '.join(missing)}")
    raise SystemExit(77)

for name, path in required.items():
    check(f"{name} exists", path.is_file())

with tempfile.TemporaryDirectory(prefix="corolla-00f-freshness-") as td:
    out = Path(td) / "bridge.json"
    proc = subprocess.run([
        str(PYTHON), str(BUILDER),
        "--openpilot-root", str(OPENPILOT),
        "--span-rlog", str(SPAN),
        "--public-rlog", str(PUBLIC),
        "--albino-oracle", str(ALBINO),
        "--output", str(out),
    ], cwd=REPO, capture_output=True, text=True, timeout=180, check=False)
    check("raw 00F/D7 bridge regeneration succeeds", proc.returncode == 0, proc.stderr.strip()[:300])
    if out.is_file():
        regenerated = json.loads(out.read_text())
        tracked = json.loads(TRACKED.read_text())
        check("regenerated bridge matches tracked JSON exactly", regenerated == tracked)
        span = regenerated["captures"]["span_2025_discord"]
        check("raw Span replay retains exact current/current-1 reset mapping", span["d7_receiver_model_replay"]["candidate_delta_counts"] == {"-1": 200, "0": 2797})
        check("raw Span replay retains 199 exact 1..15 D7 epochs", span["d7_receiver_model_replay"]["complete_epochs_exact_message8_1_through_15"] == 199)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
