#!/usr/bin/env python3
"""Verify the retained Camry driver-steering low/high threshold split evidence."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = json.loads((REPO / "data/generated/camry_2026_driver_steering_threshold_split.json").read_text())


def check(label: str, condition: bool) -> None:
  if not condition:
    raise AssertionError(label)
  print(f"[PASS] {label}")

low = ART["same_car_low_sensitivity_detector"]
for route in ("3e", "3f"):
  row = low["routes"][route]
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
