#!/usr/bin/env python3
"""Verify the current GTS+ DDB corpus census and steering-control witnesses."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_ddb_corpus_census import build
from techstream_paths import resolve_gts_root

ARTIFACT = REPO / "data/generated/gtsplus_2026/ddb_corpus_census.json"

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


a = json.loads(ARTIFACT.read_text())
check("schema", a["schema"] == "gtsplus-current-ddb-corpus-census-v1")
check("release", a["release"] == "2026.03.002.02")
check("KgpDataCtrl identity", a["source"]["kgp_data_ctrl_sha256"] == "19e709e12e53f485a84ccfbf6b226922b88502206c34b767db543c7f3df101f8")

c = a["corpus"]
check("full Gen+Spe DDB count", c["ddb_files"] == 1805)
check("parseable ECU DB count", c["ecu_databases"] == 1703)
check("non-ECU DDB count", c["non_ecu_ddb_files"] == 102)
check("regional DDB counts", {r: c["regions"][r]["ddb_files"] for r in ("NA", "EU", "JP")} == {"NA": 546, "EU": 612, "JP": 647})
check("regional ECU counts", {r: c["regions"][r]["ecu_databases"] for r in ("NA", "EU", "JP")} == {"NA": 512, "EU": 578, "JP": 613})
check("current host PE count", c["host_pe_files"] == 485)

check("observed ECU table-type count", a["table_types"]["used_count"] == 162)
check("every observed ECU table type is factory-named", a["table_types"]["all_named_by_parser"] is True)
tables = {row["table_type"]: row for row in a["table_types"]["rows"]}
check("type 118 exact class", tables[118]["class_name"] == "CDbFactorDataTable")
check("airbag DDR monitor exact class", tables[110]["class_name"] == "CDbDDRMonitorTable")

active = a["active_tests"]
check("active-test row count", active["row_count"] == 24332)
check("active-test table split", active["by_table"] == {"11": 14152, "68": 7358, "71": 2822})
check("active-test unique-name count", active["unique_resolved_name_count"] == 3717)
check("active-test census preserves semantic boundary", "not proof" in active["boundary"])

frc = a["current_camry_relevant"]["frc_pcs_collision_avoidance_routine"]
check("FRC collision-avoidance routine identity", (frc["active_test_id"], frc["routine_id"], frc["name"]) == (0xA411, 0x1604, "PCS Collision Avoidance Assist"))
check("FRC collision-avoidance fixed RoutineControl requests", (frc["start_request"], frc["stop_request"], frc["result_request"]) == ("31011604", "31021604", "31031604"))
check("FRC routine is parameterless/fixed", frc["fixed_request"] is True)

selected = a["current_camry_relevant"]["selected_monitors"]
pcs2 = {row["name"]: row for row in selected["PCS2_P5.ddb"]}
check("P5 PCS steering request semantic oracle", pcs2["PCS Steering Request"]["primary_did"] == 0x1017 and pcs2["PCS Steering Request"]["alternate_did"] == 0x3017)
check("P5 emergency steering invalid bits", pcs2["Emergency Steering Assist Invalid 1"]["bit_start"] == 25 and pcs2["Emergency Steering Assist Invalid 2"]["bit_start"] == 26)
frc_mon = {row["name"]: row for row in selected["FRC_P5.ddb"]}
check("FRC collision-avoidance function monitor", frc_mon["PCS Collision Avoidance Assist Function"]["primary_did"] == 0x2122 and frc_mon["PCS Collision Avoidance Assist Function"]["alternate_did"] == 0x4122)
check("P5 active-steering permission oracle", selected["DRS_P5.ddb"][0]["name"] == "Active Steering Control Permission")
check("P6 active-steering successor oracle", selected["ADCU_P6.ddb"][0]["name"] == "Active Steering Status")

airbag = a["current_camry_relevant"]["airbag_ddr_steering_control_names"]
check("Camry-installed SRS DDR has emergency-steering request names", any(row["name"] == "Emergency Steering Assist Request Flag" for row in airbag))
check("Camry-installed SRS DDR has collision-avoidance request names", {"Collision Avoidance Assist 1", "Collision Avoidance Assist 2", "Collision Avoidance Assist 3"} <= {row["name"] for row in airbag})
check("SRS witnesses are exact DDR monitor tables", {row["table"] for row in airbag} <= {110, 129, 138, 147})

factor = a["current_camry_relevant"]["psc_factor_data"]
check("PSC type118 is RoB factor metadata", factor["class_name"] == "CDbFactorDataTable" and "GetRoBP5_DT.dll" in factor["host_consumer"])
check("PSC factor geometry", factor["record_count"] == 396 and factor["record_size"] == 20)
check("PSC factor group is not constant 0x12D", set(factor["group_counts"]) == {"301", "401", "501", "601", "701", "801"})
check("PSC steering-lock start factor", any(row["factor"] == "Stop Start-up (Steering Lock)" for row in factor["selected_rows"]))

limit = a["req_limit_eps_boundary"]
check("Req Limit shared-string entries retained", [r["string_index"] for r in limit["global_string_entries"]] == [0x30CE, 0x30F5, 0x30F6, 0x30F8, 0x30FB])
check("Req Limit numeric/string collision explicitly bounded", "not a semantic string reference" in limit["host_boundary"]["meaning"])
emps_collision = limit["collision_witnesses"][0]
check("EMPS 0x30F5 collision witness", emps_collision["numeric_value"] == 0x30F5 and {r["name"] for r in emps_collision["type62_monitors_with_same_alternate_did"]} == {"Motor 2 V Phase Duty"})

fresh = build(resolve_gts_root())
check("artifact regenerates exactly", fresh == a)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
