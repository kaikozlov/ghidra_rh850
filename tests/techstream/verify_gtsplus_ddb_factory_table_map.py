#!/usr/bin/env python3
"""Verify exact current-GTS+ DDB table-class factory identities."""
from __future__ import annotations

import json

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream.extract_gtsplus_factory_table_map import build
from tools.techstream.parse_ddb import (
    ECU_TABLE_CLASS_NAMES, MASTER_TABLE_CLASS_NAMES,
    DS4_ECU_TABLE_CLASS_NAMES, DS4_MASTER_TABLE_CLASS_NAMES,
    DS4_VIEWER_TABLE_CLASS_NAMES,
)
from tools.techstream.techstream_paths import resolve_gts_root

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

ds4 = artifact["ds4"]
ds4_factories = {
    f["format_version"]: f
    for source in ds4.values() for f in source["factories"]
}
for version, count, names in (
    (1, 92, DS4_MASTER_TABLE_CLASS_NAMES),
    (2, 151, DS4_ECU_TABLE_CLASS_NAMES),
    (3, 19, DS4_VIEWER_TABLE_CLASS_NAMES),
):
    rows = ds4_factories[version]["records"]
    check(f"DS4 format {version} exact contiguous case range",
          [r["table_type"] for r in rows] == list(range(count)))
    check(f"DS4 format {version} names match exact native source",
          all(names[r["table_type"]] == r["class_name"] for r in rows))
check("master type90 keeps separate main and DS4 identities",
      master[90]["class_name"] == "CDbExceptionProcessIdGroupTable"
      and ds4_factories[1]["records"][90]["class_name"] == "CDbTableBase")
for product in ("ds4", "supplemental"):
    sources = artifact[product]
    for version in (6, 7):
        factory = next(f for f in sources["UtilityDB.dll"]["factories"]
                       if f["format_version"] == version)
        check(f"{product} Utility format{version} exact four constructor cases",
              [r["class_name"] for r in factory["records"]] == [
                  "CDbStringTable", "CDbViewerResourceTable",
                  "CDbHelpInfoTable", "CDbErrorCodeTable",
              ])
    viewer = next(f for f in sources["ViewerDb.dll"]["factories"]
                  if f["format_version"] == 3)
    check(f"{product} Viewer complete 19-slot namespace",
          all(DS4_VIEWER_TABLE_CLASS_NAMES[r["table_type"]] == r["class_name"]
              for r in viewer["records"]) and len(viewer["records"]) == 19)
    for program, version in (("KgpDataCtrl.dll", 4), ("ViewerDb.dll", 5)):
        factory = next(f for f in sources[program]["factories"]
                       if f["format_version"] == version)
        check(f"{product} format{version} string/default constructor split",
              factory["records"][0]["table_type"] == 0
              and factory["records"][0]["class_name"] == "CDbStringTable"
              and factory["default"]["class_name"] == "CDbTableBase")
check("main and DS4 Viewer provenance stays distinct",
      artifact["supplemental"]["ViewerDb.dll"]["artifact"]["sha256"]
      != ds4["ViewerDb.dll"]["artifact"]["sha256"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
