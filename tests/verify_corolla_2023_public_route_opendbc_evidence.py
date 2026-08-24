#!/usr/bin/env python3
"""Verify the tracked 2023 Corolla route -> opendbc compatibility extraction."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = json.loads((REPO / "data/generated/corolla_2023_public_route_opendbc_evidence.json").read_text())
LOCK = json.loads((REPO / "external-references.lock.json").read_text())
SUMMARY = json.loads((REPO / "data/generated/corolla_2023_public_route_summary.json").read_text())

passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition); passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}{suffix}")

print("== source identity and scope ==")
check("schema is v1", ART["schema"] == "corolla-2023-public-route-opendbc-evidence-v1")
route = next(x for x in LOCK["public_routes"] if x["route"] == ART["source"]["route"])
rlog0 = next(x for x in route["rlog_samples"] if x["segment"] == 0)
check("source identity matches pinned segment-0 rlog", ART["source"]["sha256"] == rlog0["sha256"] and ART["source"]["size"] == rlog0["size"])
check("legacy public-route summary uses same source", SUMMARY["rlog_samples"] == [rlog0] and SUMMARY["route"] == ART["source"]["route"])
check("route/F181 boundary is explicit", all(x in ART["source"]["identity_note"] for x in ("forced", "no carFw", "not an exact H/F")))
check("route inventories exclude Panda returned/rejected echoes", all(x in ART["source"]["can_source_filter"] for x in ("src<128", "src=bus+128", "excluded")))
check("TSS and SecOC axes are explicitly independent", all(x in ART["axis_boundary"] for x in ("TSS generation", "SecOC/TSK", "does not classify")))

rows = {r["can_id"]: r for r in ART["incoming_state_inventory"]}
def instance(cid: str, *, bus: int, dlc: int):
    return next((x for x in rows[cid]["instances"] if x["bus"] == bus and x["dlc"] == dlc), None)

print("\n== directly useful state carriers ==")
for cid, dlc, count in (
    ("0x00F", 8, 588),
    ("0x025", 32, 5887),
    ("0x030", 32, 5888),
    ("0x0AA", 8, 5888),
    ("0x101", 8, 2943),
    ("0x116", 8, 2499),
    ("0x176", 8, 1855),
):
    i = instance(cid, bus=1, dlc=dlc)
    check(f"{cid}/{dlc} is observed on logical bus 1", i is not None and i["count"] == count)

reuse = ART["direct_reuse_evidence"]
check("0x030 matches exact H/F additive-byte rule on every frame", reuse["0x030"]["frame_count"] == reuse["0x030"]["rule_matches"] == 5888 and reuse["0x030"]["exact_h_f_additive_rule"] == {"boundary": "recovered exact code behavior; OEM checksum naming/formula lineage is not inferred from the constant alone", "formula": "sum(payload_bytes_0_through_6) + 0x38, low byte", "wire_byte": 7})
check("0x030 rule match remains a format-family join, not identity", all(x in reuse["0x030"]["boundary"] for x in ("format/producer-family", "not an exact firmware/vehicle identity")))
check("0x025 old signal positions decode coherently inside FD PDU", reuse["0x025"]["steer_angle_deg"]["count"] == 5887 and reuse["0x025"]["steer_angle_deg"]["min"] == -471.0 and reuse["0x025"]["steer_angle_deg"]["max"] == 348.0 and reuse["0x025"]["steer_fraction_deg"]["unique_count"] == 15)
check("0x0AA four wheel speeds remain coherent", all(v["count"] == 5888 and v["min"] == 0.0 and 41.0 < v["max"] < 42.0 for v in reuse["0x0AA"]["speeds_kph"].values()))
check("0x0AA wheel fault bits are all clear in segment", all(v == [0] for v in reuse["0x0AA"]["fault_values"].values()))
check("0x101 old brake bit toggles", reuse["0x101"]["brake_pressed_values"] == [0, 1])
check("0x116 old user-pedal field has dynamic range", reuse["0x116"]["gas_pedal_user"]["unique_count"] == 76 and reuse["0x116"]["gas_pedal_user"]["max"] == 0.375)
check("all 0x176 checksums validate", reuse["0x176"]["checksum_valid"] == reuse["0x176"]["frame_count"] == 1855)
check("0x176 active semantics remain dynamically untested", reuse["0x176"]["cruise_active_values"] == [False] and reuse["0x176"]["cruise_state_values"] == [0] and "never engages" in reuse["0x176"]["dynamic_boundary"])

print("\n== old-contract holes ==")
for cid in ("0x127", "0x1D3", "0x260", "0x262", "0x283", "0x320", "0x343", "0x399", "0x3BC", "0x3F6"):
    check(f"{cid} is absent from incoming route", rows[cid]["instances"] == [])
for cid in ("0x3B7", "0x411", "0x412", "0x610", "0x614", "0x620", "0x622"):
    check(f"{cid} same-ID/8-byte lead remains present", any(x["bus"] == 1 and x["dlc"] == 8 for x in rows[cid]["instances"]))
check("route evidence does not call all same-ID body fields reusable", any("Same CAN ID does not imply" in x for x in ART["boundaries"]))

print("\n== exact-H/F visibility boundary ==")
vis = ART["route_vs_exact_h_f_visibility"]
check("route exposes H/F SecOC sync and D7 but no B6", vis["secoc_rx_observed_counts"] == {"0x00F/8": 588, "0x0B6/32": 0, "0x0D7/32": 2943})
check("route exposes only 0x030 from exact H/F five-PDU Tx set", vis["tx_observed_counts"] == {"0x030/32": 5888, "0x351/4": 0, "0x394/3": 0, "0x4A3/8": 0, "0x4C8/8": 0})
check("route is explicitly not promoted to complete H/F EPS-bus mirror", all(x in vis["boundary"] for x in ("no 0x0B6", "only 0x030", "no carFw/F181", "not evidence of a complete")))

print("\n== forced old-profile failure ==")
forced = ART["forced_old_profile_result"]
check("forced profile produced CarState samples", forced["sample_count"] == 5639)
check("forced profile stayed canValid false", forced["fields"]["canValid"] == [False])
check("forced profile reported zero vehicle speed", forced["fields"]["vEgo"] == [0.0])
check("forced profile reported zero steering state", forced["fields"]["steeringAngleDeg"] == [0.0] and forced["fields"]["steeringTorque"] == [0.0])
check("forced profile interpretation requires a new bus/DBC parser", all(x in forced["interpretation"] for x in ("generation-specific", "bus/DBC", "canValid=false")))

print("\n== TSS3 FD baseline ==")
expected = {
    ("0x020", 12), ("0x123", 16), ("0x160", 32),
    *((f"0x{x:03X}", 64) for x in range(0x180, 0x18C)),
    ("0x18C", 48), ("0x1A0", 48), ("0x200", 64), ("0x201", 64),
    ("0x230", 64), ("0x440", 32), ("0x450", 32),
}
actual = {(r["can_id"], r["dlc"]) for r in ART["bus0_canfd_baseline"]}
check("public bus-0 baseline is exact 22-ID/DLC set", actual == expected and len(actual) == 22)
by_id = {r["can_id"]: r for r in ART["bus0_canfd_baseline"]}
check("old radar status ID has hard 7->16 byte break", by_id["0x123"]["dlc"] == 16)
check("0x18A is 64-byte ~20Hz family member", by_id["0x18A"]["dlc"] == 64 and 19.5 < by_id["0x18A"]["rate_hz"] < 20.5)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
