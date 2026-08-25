#!/usr/bin/env python3
"""Regenerate exact-H non-steering engagement compact evidence from the disposable corpus."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "build/work/corpora/h_8965H1202000_decompilations.corrected-context.raw.jsonl"
TOOL = REPO / "tools/extract_corolla_h_nonsteering_engagement_evidence.py"
TRACKED = REPO / "data/generated/corolla_8965H1202000_nonsteering_engagement_decompiler_evidence.json"
passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition); passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][independent_external_artifact] {name}{suffix}")

if not CORPUS.is_file():
    print(f"[SKIP] exact-H disposable decompiler corpus unavailable: {CORPUS}")
    raise SystemExit(77)

with tempfile.TemporaryDirectory(prefix="h-engagement-evidence-") as td:
    out = Path(td) / "evidence.json"
    proc = subprocess.run([sys.executable, str(TOOL), "--corpus", str(CORPUS), "--out", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
    check("exact-H engagement extraction succeeds", proc.returncode == 0, proc.stderr[-300:])
    check("tracked compact evidence matches exact disposable corpus", out.exists() and json.loads(out.read_text()) == json.loads(TRACKED.read_text()))

art = json.loads(TRACKED.read_text())
check("six target-native functions promoted", art["function_count"] == 6)
roles = {x["role"] for x in art["functions"]}
check("Ready and gear roles are both represented", {"gear_packet_hybrid_scalar_unpacker", "ready_status_0x51e_scalar_unpacker", "ready_status_secondary_operational_copy", "ready_status_primary_operational_copy", "ready_status_snapshot_publish"} <= roles)
print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
