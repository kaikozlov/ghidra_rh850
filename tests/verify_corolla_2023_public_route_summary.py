#!/usr/bin/env python3
"""Verify the pinned 2023-US-Corolla public-route evidence summary."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUMMARY = json.loads((REPO / "data/generated/corolla_2023_public_route_summary.json").read_text())
LOCK = json.loads((REPO / "external-references.lock.json").read_text())
PROFILE = {
    int(row["can_id"], 0): row
    for row in __import__("csv").DictReader((REPO / "data/toyota_classic_secoc_profile.csv").open())
}

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


print("== route identity and provenance ==")
check("summary schema is 1", SUMMARY["schema_version"] == 1)
check("route ID is pinned", SUMMARY["route"] == "a74eba85c97eaf67|00000004--555953f500")
check("route inventory has 29 qlogs", SUMMARY["route_file_inventory_observed"]["qlogs"] == 29)
check("route inventory has 29 rlogs", SUMMARY["route_file_inventory_observed"]["rlogs"] == 29)
check("all 29 qlog hashes are retained", len(SUMMARY["qlogs"]) == 29 and {x["segment"] for x in SUMMARY["qlogs"]} == set(range(29)))
check("one full rlog is hash-pinned", SUMMARY["rlog_samples"] == [{"segment": 0, "sha256": "d246a55988889253c8d155f04b132b1bb443fdd74f1e6bad68eef8879a5c477b", "size": 9125881}])
check("logged software is exact sunnypilot commit", SUMMARY["software_provenance"]["commit"] == "af744c85e7c971e7bfbc8e6ee9e2bd75452a6f00")
check("logged branch is release-mici", SUMMARY["software_provenance"]["branch"] == "release-mici")

public_routes = LOCK.get("public_routes", [])
check("lock contains exactly this public route", len(public_routes) == 1 and public_routes[0]["route"] == SUMMARY["route"])
check("lock qlog hashes equal summary", public_routes[0]["qlogs"] == SUMMARY["qlogs"])
check("lock rlog sample equals summary", public_routes[0]["rlog_samples"] == SUMMARY["rlog_samples"])

print("\n== metadata boundary ==")
cp = SUMMARY["car_params"]
check("route used forced Corolla TSS2 fingerprint", cp["car_fingerprint"] == "TOYOTA_COROLLA_TSS2" and cp["fingerprint_source"] == "fixed")
check("route has no firmware inventory", cp["car_fw_count"] == 0)
check("route metadata says SecOC not required", cp["secoc_required"] is False and cp["secoc_key_available"] is False)
check("VIN is explicitly treated as placeholder", cp["vin_is_placeholder"] is True)
check("route cannot be used as physical F181 identity", any("does not identify the physical EPS F181" in item for item in SUMMARY["boundaries"]))

print("\n== selected CAN evidence ==")
rows = {(row["kind"], row["src"], row["can_id"], row["dlc"]): row["count"] for row in SUMMARY["rlog0_selected_can_counts"]}
check("incoming bus-1 sync is present", rows[("incoming", 1, "0x00F", 8)] == 588)
check("incoming bus-1 0x116 is present", rows[("incoming", 1, "0x116", 8)] == 2499)
check("incoming bus-1 0x24D is present", rows[("incoming", 1, "0x24D", 8)] == 59)
check("no incoming classic steering row is claimed", not any(k[0] == "incoming" and k[2] in {"0x131", "0x2E4"} for k in rows))
check("0x191 is instead Panda-returned bus-0 traffic", rows[("returned", 128, "0x191", 8)] == 2512)
check("0x2E4 is instead Panda-returned bus-0 traffic", rows[("returned", 128, "0x2E4", 5)] == 5025)
check("returned 0x191 corresponds to sendcan 0x191", rows[("sendcan", 0, "0x191", 8)] == 2519)
check("returned 0x2E4 corresponds to sendcan 0x2E4", rows[("sendcan", 0, "0x2E4", 5)] == 5037)
check("route contains 64-byte CAN-FD 0x183 rather than classic 8-byte 0x183", rows[("incoming", 0, "0x183", 64)] == 1221 and not any(k[0] == "incoming" and k[2] == "0x183" and k[3] == 8 for k in rows))

print("\n== known classic SecOC structure ==")
check("profile independently classifies 0x116 as protected", PROFILE[0x116]["kind"] == "protected")
check("profile independently classifies 0x24D as protected", PROFILE[0x24D]["kind"] == "protected")
struct = SUMMARY["classic_freshness_structure"]
check("0x116 reset-low2 aligns on 2476/2496 eligible frames", struct["0x116"]["reset_low2_matches"] == 2476 and struct["0x116"]["eligible_frames"] == 2496)
check("0x116 alignment exceeds 99 percent", struct["0x116"]["match_fraction"] > 0.99)
check("0x24D reset-low2 aligns on every eligible frame", struct["0x24D"]["reset_low2_matches"] == struct["0x24D"]["eligible_frames"] == 59)
check("summary does not promote structure to cryptographic key validation", any("not cryptographic key validation" in item for item in SUMMARY["boundaries"]))

print("\n== representative wire samples ==")
for can_id in ("0x00F", "0x116", "0x24D"):
    samples = SUMMARY["sample_frames"][can_id]
    check(f"{can_id} sample frames are classic 8-byte payloads", all(len(bytes.fromhex(sample)) == 8 for sample in samples))
check("returned 0x2E4 sample remains 5-byte old-profile traffic", all(len(bytes.fromhex(sample)) == 5 for sample in SUMMARY["sample_frames"]["returned_0x2E4"]))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
