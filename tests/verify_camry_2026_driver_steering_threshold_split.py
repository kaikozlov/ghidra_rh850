#!/usr/bin/env python3
"""Verify the retained Camry driver-steering low/high threshold split evidence."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = json.loads((REPO / "data/generated/camry_2026_driver_steering_threshold_split.json").read_text())
HANDS = json.loads((REPO / "data/generated/camry_20260906_hands_off_warning_audit.json").read_text())


def check(label: str, condition: bool) -> None:
  if not condition:
    raise AssertionError(label)
  print(f"[PASS] {label}")


check("schema", ART["schema"] == "camry-2026-driver-steering-threshold-split-v1")

# The new artifact must reuse, not silently reinterpret, the already-qualified
# same-car low-sensitivity detector evidence.
low = ART["same_car_low_sensitivity_detector"]
check("low detector carrier", low["carrier"] == "native FRC-side 0x371 B20[4]")
for route in ("3e", "3f"):
  src = HANDS["routes"][route]["native_state_machine_candidate"]
  row = low["routes"][route]
  check(f"{route} set transition matches source artifact", row["set_abs_eps_torque_nm"] == src["driver_detect_set_abs_eps_torque_nm"])
  check(f"{route} release transition matches source artifact", row["release_abs_eps_torque_nm"] == src["driver_detect_release_abs_eps_torque_nm"])
  check(f"{route} 0.75-1.0 N.m detector population matches", row["fraction_0p75_to_1p0"] == src["driver_detect_by_abs_eps_torque_nm"]["0.75-1"])
  check(f"{route} 1.0-1.25 N.m detector population matches", row["fraction_1p0_to_1p25"] == src["driver_detect_by_abs_eps_torque_nm"]["1-1.25"])
  check(f"{route} median set is 0.67 N.m", row["set_abs_eps_torque_nm"]["p50"] == 0.67)
  check(f"{route} low band already strongly asserts detector", row["fraction_0p75_to_1p0"]["driver_detect_fraction"] > 0.85)

# Request withdrawal is deliberately a negative discriminator: it occurs at a
# broad range of physical torque and with the low detector both clear and set.
withdraw = ART["request_withdrawal_negative"]
check("12-route corpus totals 513 segments", sum(withdraw["segment_counts"].values()) == 513 and len(withdraw["routes_scanned"]) == 12)
check("nine direct ID11-to-ID0 edges retained", withdraw["direct_id11_to_id0_count"] == len(withdraw["events"]) == 9)
check("seven high-lane edges retained", withdraw["high_lane_count"] == 7)
check("high-lane torque span is 0.23..1.37 N.m", withdraw["high_lane_abs_torque_min_nm"] == 0.23 and withdraw["high_lane_abs_torque_max_nm"] == 1.37)
high_lane = [e for e in withdraw["events"] if e["lane_line_probs"] is not None and min(e["lane_line_probs"]) >= 0.7]
check("high-lane count recomputes", len(high_lane) == withdraw["high_lane_count"])
check("high-lane withdrawals include detector-clear and detector-set states", {e["driver_detect_b20_bit4"] for e in high_lane} == {False, True})

# Toyota's own semantic surfaces keep hands-on/detection and override/inhibit
# separate; the cross-system low/high dictionary is retained only as vocabulary.
split = ART["toyota_semantic_split"]
ffd = split["camry_frc_operation_ffd"]
check("560D separates driver detection from LTA prohibition",
      [x["name"] for x in ffd["560D"]] == ["Driver Steering Control Detection Status", "LTA Driver Steering Control prohibited"])
check("5774/5776 are support-gated override fields",
      [(x["name"], x["support_did"]) for did in ("5774", "5776") for x in ffd[did]] == [
        ("Driver steering override", 1), ("Driver steering override for steering", 1)])
check("550D distinguishes override and warning inhibition",
      [x["name"] for x in ffd["550D"]] == ["LDA Inhibition by Steering Override", "LDA Warning Inhibition by Driver Steering"])

p5 = split["p5_low_high_vocabulary"]
check("P5 low/high vocabulary has four temporal snapshots", p5["snapshot_count"] == 4 and len(p5["snapshots"]) == 4)
check("all P5 snapshots use Not/Low/High dictionary",
      all(row["pattern_display"] == {"0": "Not Steering", "1": "Steering(Low)", "2": "Steering(High)"} for row in p5["snapshots"]))

p6_names = {row["name"] for row in split["p6_successor"]}
check("P6 successor keeps hands-on and override inhibition distinct",
      p6_names == {"LTA Driver Hands-On Flag", "LTA Inhibition By Steering Override"})

robs = {row["rob_code"]: row for row in split["rob_discriminators"]}
check("209D is LCS Steer Override with pre/post window",
      robs["209D"] == {
        "group": 2, "name": "LCS Steer Override", "post_trigger_samples": 8,
        "pre_trigger_samples": 36, "rob_code": "209D", "sampling_s": 0.2, "system": "LDA",
      })
check("neighboring hands-off RoBs retained", {"229C", "229F", "2845", "2846"} <= set(robs))

conclusion = ART["bounded_conclusion"]
check("high threshold remains explicitly unrecovered", conclusion["high_override_threshold"] == "unrecovered")
check("periodic synthetic keepalive remains outside qualified output", "do not add" in conclusion["production_boundary"])
