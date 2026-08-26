#!/usr/bin/env python3
"""Regenerate TSS3 cruise/engagement semantics from local Techstream P5 DDBs."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DB = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB/FRC_P5.ddb"
TOOL = REPO / "tools/techstream/extract_tss3_cruise_engagement_semantics.py"
TRACKED = REPO / "data/generated/techstream_v18/tss3_cruise_engagement_semantics.json"
passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition); passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}{suffix}")

if not DB.is_file():
    print(f"[SKIP] local Techstream FRC_P5.ddb unavailable: {DB}")
    raise SystemExit(77)

original = TRACKED.read_bytes()
with tempfile.TemporaryDirectory(prefix="techstream-engagement-") as td:
    out = Path(td) / "engagement.json"
    proc = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
    check("Techstream P5 engagement extraction succeeds", proc.returncode == 0, proc.stderr[-300:])
    check("tracked P5 engagement semantics regenerate exactly", out.exists() and out.read_bytes() == original)

art = json.loads(original)
rows = {x["name"]: x for x in art["frc_p5"]["monitors"]}
check("FRC permission/main/operation oracles exist", all(x in rows for x in ("Cruise Control Permission Flag", "Main Switch Recognition Flag", "ACC Control in Operation Flag")))
check("FRC memory speed oracle is km/h", rows["Memory Vehicle Speed"]["primary_data_id"] == "0x1901" and rows["Memory Vehicle Speed"]["bit_range"] == [32, 63] and rows["Memory Vehicle Speed"]["conversion"]["unit"] == "km/h")
check("P5 DDB/transport boundary reflects host closure", all(x in art["frc_p5"]["boundary"] for x in ("DDB rows alone", "current-GTS+ host evidence", "SID 0x22 ReadDataByIdentifier", "outer diagnostic-session prerequisite")))
print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
