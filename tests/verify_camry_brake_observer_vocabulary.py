#!/usr/bin/env python3
"""Verify current-GTS+ category-435 observer vocabulary and its boundaries."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "data/generated/gtsplus_2026/camry_brake_observer_vocabulary.json"
BUILDER = REPO / "tools/techstream/build_camry_brake_observer_vocabulary.py"

passed = failed = 0
oracle = "generated_self_check+external_source+dynamic_probe_join"


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}")


spec = importlib.util.spec_from_file_location("camry_brake_observer_builder", BUILDER)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

check("artifact regenerates exactly", artifact == mod.build())
check("schema exact", artifact["schema"] == "camry-brake-observer-vocabulary-v1")

category = artifact["category_435"]
check(
    "current category-435 identity and monitor schema",
    category["category_id"] == 435
    and category["generation"] == 20
    and category["database"] == "ABS_P5.ddb"
    and category["name"] == "Brake/EPB"
    and category["monitor_schema"] == {
        "candidate_count": 554,
        "record_size": 80,
        "table": 62,
        "table_class": "CDbDatamonitorP5Table",
    },
)

angle = artifact["observer_vocabulary"]["ads_control_eps_pinion_angle2"]
check(
    "0x107E is the signed 24-bit 0.00025-rad observer",
    angle["did"] == "0x107E"
    and angle["alternate_did"] == "0x307E"
    and angle["bit_range_inclusive"] == [0, 23]
    and angle["width_bytes"] == 3
    and angle["signed"] is True
    and (angle["mul"], angle["div"], angle["decimal_point_count"], angle["unit"])
    == (25, 1, 5, "rad")
    and angle["semantic_role"] == "diagnostic_data_monitor_observer_candidate",
)

auth = artifact["observer_vocabulary"]["software_number_for_authentication"]
check(
    "0x10AF is an opaque 17-byte authentication software-number observer",
    auth["did"] == "0x10AF"
    and auth["alternate_did"] is None
    and auth["name"] == "Software Number for Authentication"
    and auth["bit_range_inclusive"] == [0, 135]
    and auth["width_bits"] == 136
    and auth["width_bytes"] == 17
    and auth["unit"] is None
    and auth["pattern_display"] == {}
    and auth["semantic_role"] == "diagnostic_data_monitor_observer_candidate",
)

runtime = artifact["runtime_support_boundary"]
check(
    "all category-435 monitor candidates require runtime support probing",
    runtime["candidate_partition"]
    == {"direct_exclude": 0, "direct_include": 0, "runtime_check_support_pid": 554}
    and "does not prove" in runtime["conclusion"],
)

camry = artifact["exact_camry_boundary"]
check(
    "exact Camry rejects 0x107E in tested sessions and 0x10AF remains unmeasured",
    camry["brake_identity"]["f181"] == "F152633K0000"
    and camry["did_107e_default"]["status"] == "negative_or_timeout"
    and "request out of range" in camry["did_107e_default"]["error"]
    and camry["did_107e_extended"]["status"] == "negative_or_timeout"
    and "request out of range" in camry["did_107e_extended"]["error"]
    and camry["did_10af_live_support"] == "not_measured",
)

producer = artifact["producer_boundary"]
check(
    "observer metadata changes neither acquisition nor producer ownership",
    producer["changes_acquisition_or_producer_hypothesis"] is False
    and "does not replace" in producer["conclusion"]
    and "CMAC/freshness" in producer["conclusion"],
)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
