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
check("schema", artifact["schema_version"] == 1)
check("current release", artifact["source"] == "GTS+ 2026.03.002.02")
check("KgpDataCtrl identity", artifact["artifact"]["sha256"] == "19e709e12e53f485a84ccfbf6b226922b88502206c34b767db543c7f3df101f8")
check("MakeTable entry", artifact["make_table"]["va"] == "0x10081C10")

factories = {f["format_version"]: f for f in artifact["factories"]}
check("format-1 geometry", factories[1]["maximum_type"] == 0x5D and len(factories[1]["records"]) == 94)
check("format-2 geometry", factories[2]["maximum_type"] == 0xAB and len(factories[2]["records"]) == 172)

master = {r["table_type"]: r for r in factories[1]["records"]}
ecu = {r["table_type"]: r for r in factories[2]["records"]}
check("master subsystem identity", master[23]["class_name"] == "CDbSubSystemTable")
check("master install identity", master[44]["class_name"] == "CDbInstallingEcuListTable")
check("master custom-list identity", master[60]["class_name"] == "CDbCustomListMTable")
check("P5 routine active-test identity", ecu[71]["class_name"] == "CDbRoutineActTestP5Table")
check("P5 factor-data identity", ecu[118]["class_name"] == "CDbFactorDataTable")
check("P5 DDR header/case/monitor identities", [ecu[i]["class_name"] for i in (108, 109, 110)] == [
    "CDbDDRHeaderInfoDataIdTable", "CDbDDRCaseInfoDataIdTable", "CDbDDRMonitorTable",
])
check("current generic-base cases", [r["table_type"] for r in factories[2]["records"] if r["status"] == "generic-base/default"] == [74, 75, 76, 158, 159, 169])

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
