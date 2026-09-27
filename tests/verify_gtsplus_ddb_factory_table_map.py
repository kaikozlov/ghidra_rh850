#!/usr/bin/env python3
"""Verify exact current-GTS+ DDB table-class factory identities."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_factory_table_map import build
from parse_ddb import ECU_TABLE_CLASS_NAMES, MASTER_TABLE_CLASS_NAMES
from techstream_paths import resolve_gts_root

ARTIFACT = REPO / "data/generated/gtsplus_2026/ddb_factory_table_map.json"

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


artifact = json.loads(ARTIFACT.read_text())
factories = {f["format_version"]: f for f in artifact["factories"]}
master = {r["table_type"]: r for r in factories[1]["records"]}
ecu = {r["table_type"]: r for r in factories[2]["records"]}
# The parser's human-readable class maps must never regress to a smaller local
# subset now that the current factory is recovered exactly.
check("parser covers every current ECU type", set(ECU_TABLE_CLASS_NAMES) >= set(ecu))
check("parser ECU names agree with current factory", all(ECU_TABLE_CLASS_NAMES[i] == r["class_name"] for i, r in ecu.items()))
check("parser covers every current master type", set(MASTER_TABLE_CLASS_NAMES) >= set(master))
check("parser master names agree with current factory", all(MASTER_TABLE_CLASS_NAMES[i] == r["class_name"] for i, r in master.items()))

fresh = build(resolve_gts_root() / "bin/KgpDataCtrl.dll")
check("artifact regenerates exactly", fresh == artifact)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
