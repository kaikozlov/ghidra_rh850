#!/usr/bin/env python3
"""Verify the tracked Span 2025 Discord driving-rlog -> opendbc evidence artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = json.loads((REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json").read_text())
LOCK = json.loads((REPO / "external-references.lock.json").read_text())
RLOG = REPO / "community/spanconstant/span_67fd5b833889fedf_00000010--17084916da--3--rlog.zst"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}{suffix}")


print("== source identity and provenance ==")
check("schema is v1", ART["schema"] == "corolla-2025-span-discord-rlog-opendbc-evidence-v1")
src = ART["source"]
row = next(x for x in LOCK["community_artifacts"] if x["path"] == src["path"])
check("source path is tracked Span Discord rlog", src["path"] == "community/spanconstant/span_67fd5b833889fedf_00000010--17084916da--3--rlog.zst")
raw = RLOG.read_bytes()
check("tracked raw rlog identity matches lock and artifact", hashlib.sha256(raw).hexdigest() == src["sha256"] == row["sha256"] == "f1ae7c40ad8e9ff8c462a3f5367d914873e93575d902ccb82f2c74984acd439f" and len(raw) == src["size"] == row["size"] == 11365866)
check("Discord provenance is explicit", all(x in src["attribution"] for x in ("Span", "Discord", "2026-07-29", "2026-08-24")))
check("incoming inventories exclude Panda returned/rejected echoes", all(x in src["can_source_filter"] for x in ("src<128", "returned/Tx", "excluded")))
check("CAN window is one minute", 59.98 < src["can_window_s"] < 60.01)

init = src["init_data"]
check("embedded source branch is exact", init == {
    "device_type": "mici",
    "dongle_id": "67fd5b833889fedf",
    "git_branch": "tskdash",
    "git_commit": "7e78a9d89728c4bd106838d40b5891ce3931de43",
    "git_remote": "https://github.com/spanconstant5/openpilot.git",
    "version": "0.11.2",
})
cp = src["car_params"]
check("embedded carParams is MOCK/noOutput", cp["car_fingerprint"] == "MOCK" and cp["brand"] == "mock" and cp["safety_configs"] == [{"model": "noOutput", "param": 0}])
panda = src["panda_state"]
check("Panda is Cuatro ELM327 param1 with controls disabled", panda == {"controls_allowed": False, "harness_status": "flipped", "panda_type": "cuatro", "safety_model": "elm327", "safety_param": 1})
ident = src["identity_boundary"]
check("rlog is not silently joined to August firmware dump", ident["rlog_car_params_is_mock"] and ident["rlog_has_no_usable_f181_join"] and ident["same_dongle"] is False and ident["rlog_dongle_id"] == "67fd5b833889fedf" and ident["firmware_dump_preflight_dongle_id"] == "23257862c6bf2f83")
check("identity boundary states contributor-attributed not exact-F join", all(x in ident["interpretation"] for x in ("Discord attribution", "MOCK", "differs", "not an exact 8965F1208000")))

print("\n== disabled parser/control boundary ==")
runtime = ART["runtime_boundary"]
check("openpilot remained disabled", runtime["selfdrive_state_values"] == ["disabled"] and runtime["lat_active_values"] == [False] and runtime["long_active_values"] == [False] and runtime["controls_allowed"] is False)
check("MOCK CarState is zero/unknown despite raw motion", runtime["mock_carstate"] == {"canValid": [True], "gearShifter": ["unknown"], "steeringAngleDeg": [0.0], "steeringTorque": [0.0], "vEgo": [0.0]})
check("raw CAN is declared authoritative over MOCK CarState", all(x in runtime["interpretation"] for x in ("Raw src<128 CAN", "MOCK CarState", "not used")))

print("\n== moving raw-vehicle evidence ==")
move = ART["moving_vehicle_evidence"]
check("capture is dynamically moving", move["wheel_speed_min_kph"] == 0.0 and move["wheel_speed_max_kph"] > 24.0 and "moving/driving" in move["interpretation"] and "does not by itself prove" in move["interpretation"])
check("brake toggles", move["brake_pressed_values"] == [0, 1])
check("gas is dynamically exercised", move["gas_pedal_user"]["count"] == 2548 and move["gas_pedal_user"]["unique_count"] == 121 and move["gas_pedal_user"]["min"] == 0.0 and move["gas_pedal_user"]["max"] == 0.73)
check("steering angle is dynamic", move["steering_angle_deg"]["count"] == 6003 and move["steering_angle_deg"]["min"] == -511.5 and move["steering_angle_deg"]["max"] == 123.0 and move["steering_angle_deg"]["unique_count"] == 337)
check("steering rate is dynamic", move["steering_rate_deg_s"]["count"] == 6003 and move["steering_rate_deg_s"]["min"] == -700 and move["steering_rate_deg_s"]["max"] == 800 and move["steering_rate_deg_s"]["unique_count"] == 186)

print("\n== prior-art-compatible state carriers ==")
reuse = ART["direct_reuse_evidence"]
check("0x025 exact-H-proved fields remain dynamic", reuse["0x025"]["steer_angle_deg"] == move["steering_angle_deg"] and reuse["0x025"]["steer_rate_deg_s"] == move["steering_rate_deg_s"] and reuse["0x025"]["steer_fraction_deg"]["unique_count"] == 15)
check("0x030 exact H/F additive rule passes all 6000 frames", reuse["0x030"]["frame_count"] == reuse["0x030"]["rule_matches"] == 6000 and reuse["0x030"]["exact_h_f_additive_rule"] == {"boundary": "recovered exact code behavior; OEM checksum naming/formula lineage is not inferred from the constant alone", "formula": "sum(payload_bytes_0_through_6) + 0x38, low byte", "wire_byte": 7})
check("0x030 join stays format-family not identity", "without creating an exact firmware identity join" in reuse["0x030"]["boundary"])
for wheel, max_expected in (("FR", 24.01), ("FL", 23.5), ("RR", 24.05), ("RL", 23.5)):
    w = reuse["0x0AA"]["speeds_kph"][wheel]
    check(f"0x0AA {wheel} speed is coherent", w["count"] == 6000 and w["min"] == 0.0 and abs(w["max"] - max_expected) < 1e-6 and reuse["0x0AA"]["fault_values"][wheel] == [0])
check("0x101 old brake bit and checksum survive", reuse["0x101"]["brake_pressed_values"] == [0, 1] and reuse["0x101"]["checksum_valid"] == reuse["0x101"]["frame_count"] == 3000)
check("0x116 old user-pedal field is dynamic", reuse["0x116"]["gas_pedal_user"] == move["gas_pedal_user"])
gear = reuse["0x127"]
check("0x127 carrier/checksum/D enum survive", gear["frame_count"] == gear["checksum_valid"] == 3662 and gear["gear_raw_values"] == [3] and gear["decoded_values"] == ["D"] and gear["prior_art_value_map"] == {"0": "P", "1": "R", "2": "N", "3": "D", "4": "B"})
check("0x127 unobserved gears remain bounded", all(x in gear["boundary"] for x in ("only D", "P/R/N/B transitions", "require dynamic validation")))
cruise = reuse["0x176"]
check("0x176 checksum survives but active cruise stays open", cruise["frame_count"] == cruise["checksum_valid"] == 1890 and cruise["cruise_active_values"] == [False] and cruise["cruise_state_values"] == [0] and "cruise never engages" in cruise["dynamic_boundary"])

print("\n== unswapped-harness observation boundary ==")
harness = ART["harness_observation_boundary"]
check("all Panda samples stayed ELM327 param1", harness["panda_state_samples"] == src["panda_state_samples"] == 599 and harness["all_samples_elm327_param1"] is True)
check("Panda flipped is orientation, not physical repin", harness["all_samples_harness_status_flipped"] is True and all(x in harness["interpretation"] for x in ("harnessStatus=flipped", "orientation", "not the Toyota-B physical CAN0/CAN1 repin")))
check("field context records no physical repin", "had not physically swapped" in harness["field_context"])
check("param1 enables passive stock-CAN1 observation but not interception", all(x in harness["interpretation"] for x in ("normal harness CAN1 wires", "passively observe", "prevents CAN0/CAN2 relay interception", "does not by itself make stock CAN1 traffic invisible")))

print("\n== exact H/F visibility while moving ==")
vis = ART["exact_h_f_visibility"]
check("moving capture sees H/F sync+D7 but no B6", vis["secoc_rx_expected"] == ["0x00F/8", "0x0D7/32", "0x0B6/32"] and vis["secoc_rx_observed_counts"] == {"0x00F/8": 600, "0x0B6/32": 0, "0x0D7/32": 3000})
check("moving capture sees only 0x030 of exact H/F Tx set", vis["tx_expected"] == ["0x030/32", "0x351/4", "0x394/3", "0x4A3/8", "0x4C8/8"] and vis["tx_observed_counts"] == {"0x030/32": 6000, "0x351/4": 0, "0x394/3": 0, "0x4A3/8": 0, "0x4C8/8": 0})
check("B6 absence remains a segment-level negative", all(x in vis["boundary"] for x in ("moving Span rlog", "ELM327 param=1", "passive CAN1 observation", "segment-level negative", "stock-LTA", "exact F181")))

print("\n== dynamic TSS3 FD topology ==")
fd = ART["tss3_fd_network"]
expected = {
    ("0x020", 12), ("0x123", 16), ("0x160", 32),
    *((f"0x{x:03X}", 64) for x in range(0x180, 0x18C)),
    ("0x18C", 48), ("0x1A0", 48), ("0x200", 64), ("0x201", 64),
    ("0x230", 64), ("0x440", 32), ("0x450", 32),
}
for bus_key in ("bus0", "bus2"):
    actual = {(x["can_id"], x["dlc"]) for x in fd[bus_key]}
    check(f"{bus_key} is exact 22-ID/DLC FD set", actual == expected and len(actual) == 22)
check("moving bus0/bus2 shapes and payload sequences are identical", fd["bus0_bus2_same_id_dlc_set"] is True and fd["bus0_bus2_payload_sequences_equal"] is True and len(fd["equality_by_id"]) == 22 and all(x["payload_sequence_equal"] for x in fd["equality_by_id"]))
check("moving topology is not promoted to semantics/ownership", all(x in fd["interpretation"] for x in ("moving", "topology invariant", "does not assign field semantics", "physical producer ownership")))

print("\n== no hidden tskdash radar decoder ==")
radar = ART["radar_parser_boundary"]
check("radarTracks has no parsed points", radar["radar_tracks_samples"] == 1200 and radar["nonempty_parsed_track_samples"] == 0)
check("source branch supplies no hidden TSS3 radar decoder", all(x in radar["interpretation"] for x in ("no parsed points", "radar=false", "no hidden TSS3 radar decoder")))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
