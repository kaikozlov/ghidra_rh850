#!/usr/bin/env python3
"""Verify current GTS+ vehicle/profile and live capability resolver semantics."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_vehicle_resolver import (
    analyze_support_bitmap,
    build,
    vin_decision_matches,
)

ARTIFACT = REPO / "data/generated/gtsplus_2026/vehicle_resolver_semantics.json"

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


artifact = json.loads(ARTIFACT.read_text())
check("schema", artifact["schema"] == "gtsplus-current-vehicle-resolver-v1")
check("current release", artifact["release"] == "2026.03.002.02")
check("VIN table/class", artifact["vin_vehicle_decision"]["ddb_type"] == 59 and artifact["vin_vehicle_decision"]["db_class_id"] == "0x13B")
check("vehicle decision table/class", artifact["vehicle_decision"]["ddb_type"] == 41 and artifact["vehicle_decision"]["db_class_id"] == "0x129")
check("four vehicle decision modes", artifact["vehicle_decision"]["mode_dispatch"] == {
    "0": "DecisionKey", "1": "DecisionKeyNew", "2": "DecisionKeyEU", "3": "DecisionKeyNewEU",
})
check("current P5 bypasses type-41 vehicle decision", artifact["vehicle_decision"]["current_p5_boundary"] == {
    "generation_low5": [20, 21],
    "phase5_vehicle_decision_virtual": "0x10004D80",
    "phase5_vehicle_decision_bytes": "b8010104c0c21400",
    "return_status": "0xC0040101",
    "meaning": "current Phase5 does not query class 0x129; type-41 vehicle decision is the P3/P4 path",
})

na = artifact["regions"]["NA"]
check("NA table geometry", na["tables"]["vehicle_decision"]["record_count"] == 1869 and na["tables"]["vin_vehicle_decision"]["record_count"] == 2402)
camry = na["camry_hv_witness"]
check("Camry-HV vehicle type/name join", camry["vehicle_type"] == 12704 and camry["vehicle_name"] == "Camry HV")
check("Camry VIN decision rows", len(camry["vin_rows"]) == 2)
check("Camry install resolver candidate count", camry["mount_candidate_count"] == 34)
check("Camry mount candidates are Toyota install rows", len({row["category_id"] for row in camry["mount_candidates"]}) == 34)
check("Camry protocol table/class", na["tables"]["protocol_info"] == {
    "ddb_type": 13, "db_class_id": "0x10D", "record_size": 28, "record_count": 756,
})
check("all Camry mount candidates have Toyota transport routes",
      len(camry["mount_candidates"]) == 34 and all(isinstance(row.get("transport_route"), dict) for row in camry["mount_candidates"]))
routes = {row["category_id"]: row["transport_route"] for row in camry["mount_candidates"]}
check("Toyota GetEcuAddr route implementation pinned", artifact["functions"]["mounted_ecu"] == {
    "CommConnectionNoBuffer": "0x100829C0",
    "GetEcuAddr": "0x10035420",
    "ProtInfo.FindDbItem1": "0x100C2590",
    "ProtInfo.FindDbItem2": "0x100C2690",
})
check("Toyota protocol +0x14 is legislated request, not response",
      routes[372]["legislated_request_address"] == 0x7E0 and
      all(route["legislated_request_address"] == 0 or 0x7E0 <= route["legislated_request_address"] <= 0x7E7 for route in routes.values()))
check("direct current-P5 Toyota route witnesses",
      (routes[372]["request_address"], routes[372]["address_extension"], routes[372]["phase_type"]) == (0x700, 0, 0x12) and
      (routes[445]["request_address"], routes[445]["address_extension"], routes[445]["phase_type"]) == (0x7B3, 0, 0x12) and
      (routes[498]["request_address"], routes[498]["address_extension"], routes[498]["phase_type"]) == (0x792, 0, 0x12) and
      (routes[5005]["request_address"], routes[5005]["address_extension"], routes[5005]["phase_type"]) == (0x7A2, 0, 0x12))
check("Toyota route exposes endpoints absent from the old local sweep",
      routes[409]["request_address"] == 0x7C0 and routes[444]["request_address"] == 0x780)
check("Toyota 0x750 logical-address-extension witnesses",
      (routes[452]["request_address"], routes[452]["address_extension"]) == (0x750, 0x2A) and
      (routes[466]["request_address"], routes[466]["address_extension"]) == (0x750, 0x29) and
      (routes[470]["request_address"], routes[470]["address_extension"]) == (0x750, 0x7B) and
      (routes[492]["request_address"], routes[492]["address_extension"]) == (0x750, 0x96))
check("Camry mount connection profiles", camry["connection_profiles"] == [
    {"frame_id": 0, "comm_set_id": 9, "phase_type": 0x12},
    {"frame_id": 0, "comm_set_id": 9, "phase_type": 0x22},
])
check("Camry mount frame 0 is empty", camry["connection_frame_witness"] == {
    "frame_id": 0, "send_variable_id": 0, "receive_mask_variable_id": 0,
    "receive_check_variable_id": 0, "empty": True,
})
check("Camry mount CommSet 9", camry["connection_comm_set_witness"] == {
    "comm_set_id": 9, "send_parameter": 1000, "receive_timeout": 1020,
    "retry_count": 0, "exception_handler_id": 0, "exception_handler_flag": 0,
})
check("mount connection implementation pinned", artifact["functions"]["mounted_ecu"]["CommConnectionNoBuffer"] == "0x100829C0")
check("mount connection DB classes pinned", artifact["mounted_ecu"]["connection_algorithm"]["comm_frame_db_class_id"] == "0x111" and artifact["mounted_ecu"]["connection_algorithm"]["ecu_category_db_class_id"] == "0x110")
check("mount resolver is not an identity DID probe", "not an identity-DID probe" in artifact["mounted_ecu"]["current_na_camry"]["meaning"])
check("mount phase types preserved", sorted({row["connection_phase_type"] for row in camry["mount_candidates"]}) == [0x12, 0x22])

# The current Camry rows wildcard every VIN[0:11] position except indexes
# 4/7/9.  They accept A or B at index4, K at index7, and S at index9.
row_a, row_b = [bytes.fromhex(value) for value in camry["vin_rows"]]
vin_a = b"XXXXAXXKXSX"
vin_b = b"XXXXBXXKXSX"
vin_bad = b"XXXXCXXKXSX"
check("VIN decision key is category/phase/VIN[0:11]", vin_decision_matches(row_a, 372, 0x12, vin_a))
check("second current Camry VIN branch", vin_decision_matches(row_b, 372, 0x12, vin_b))
check("VIN non-wildcard mismatch rejected", not vin_decision_matches(row_a, 372, 0x12, vin_bad))
check("category mismatch rejected", not vin_decision_matches(row_a, 373, 0x12, vin_a))
check("phase mismatch rejected", not vin_decision_matches(row_a, 372, 0x13, vin_a))
check("VIN decision returns Camry vehicle type at +0x0E", int.from_bytes(row_a[0x0E:0x10], "little") == 12704)

# MSB-first root bitmap: bit0 -> 0000, bit1 -> 0100, byte1 bit0 -> 0800.
check("root support bitmap is MSB-first", analyze_support_bitmap(0, bytes.fromhex("c080"), 8) == [0x0000, 0x0100, 0x0800])
# Second level starts at xx01, and the final bitmap bit (xx100) is skipped.
check("group support bitmap starts at xx01", analyze_support_bitmap(0x5200, bytes.fromhex("a0"), 0) == [0x5201, 0x5203])
check("group bitmap skips next xx00 alias", analyze_support_bitmap(0x5200, bytes(31) + b"\x01", 0) == [])
check("P5 DID root frame", artifact["p5_support"]["did_root"]["request"] == "220101" and artifact["p5_support"]["did_root"]["positive_sid"] == "0x62")
check("GetSupportP5 dispatch", artifact["p5_support"]["options"] == {"1": "PID", "2": "DID", "3": "RID"})
check("resolver pipeline order", [row["stage"] for row in artifact["pipeline"]] == [
    "vehicle-resolution", "mounted-ecu-resolution", "feature-support-resolution",
])

fresh = build()
check("artifact regenerates exactly", fresh == artifact)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
