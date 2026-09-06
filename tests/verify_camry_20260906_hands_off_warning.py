#!/usr/bin/env python3
"""Verify the tracked 2026-09-06 Camry hands-off warning reduction."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
report = json.loads((REPO / "data/generated/camry_20260906_hands_off_warning_audit.json").read_text())
routes = report["routes"]


def check(name: str, condition: bool) -> None:
  if not condition:
    raise AssertionError(name)
  print(f"[PASS] {name}")


for short, expected in (("3e", 43), ("3f", 63)):
  w = routes[short]["warning_candidate"]
  state = w["onset_openpilot_state"]
  check(f"{short} warning onset count", w["rising_edges"] == expected)
  check(f"{short} onset while latActive", state["lat_active_true"] == expected)
  check(f"{short} onset while selfdrive enabled", state["selfdrive_enabled_true"] == expected)
  check(f"{short} onset before steeringPressed", state["steering_pressed_true"] == 0)
  check(f"{short} onset with active B6 ID11", state["b6_id11"] == expected)
  check(f"{short} Toyota timer median ~16 s", 15.0 <= w["onset_time_since_touch_s"]["p50"] <= 17.0)

hud3e = routes["3e"]["hud_companion_candidate"]
hud3f = routes["3f"]["hud_companion_candidate"]
check("3e normal HUD payload observed", hud3e["payload_counts"].get("1400004401ee9307", 0) > 1000)
check("3e warning HUD payload observed", hud3e["payload_counts"].get("140c004401ee9307", 0) > 100)
check("3f normal HUD payload observed", hud3f["payload_counts"].get("1400004401ee9307", 0) > 1000)
check("3f warning HUD payload observed", hud3f["payload_counts"].get("140c004401ee9307", 0) > 100)
check("3f escalation payload observed exactly six times", hud3f["payload_counts"].get("140c404401ee9307") == 6)
check("all B2[6] escalation frames occur during 0x371 warning state",
      hud3f["b2_bit6_frames"] == 6 and hud3f["b2_bit6_frames_while_0x371_active"] == 6)
check("3e all qualified 0x371 rises have paired HUD edges",
      hud3e["rise_edges_paired_to_0x371_within_2s"] == routes["3e"]["warning_candidate"]["rising_edges"])
check("3f all qualified 0x371 rises have paired HUD edges",
      hud3f["rise_edges_paired_to_0x371_within_2s"] == routes["3f"]["warning_candidate"]["rising_edges"])

check("report schema includes state-machine reduction", report["schema_version"] == 2)

for short in ("3e", "3f"):
  sm = routes[short]["native_state_machine_candidate"]
  check(f"{short} B17[0] exactly complements B20[4] in clean ID11",
        sm["b17lsb_equals_not_b20bit4_violations"] == 0)
  check(f"{short} warning and driver-detect states are mutually exclusive",
        sm["warning_and_driver_detect_overlap_frames"] == 0)
  check(f"{short} low torque rarely asserts driver-detect",
        sm["driver_detect_by_abs_eps_torque_nm"]["0-0.25"]["driver_detect_fraction"] < 0.03)
  check(f"{short} >=1 N.m strongly asserts driver-detect",
        sm["driver_detect_by_abs_eps_torque_nm"]["1-1.25"]["driver_detect_fraction"] > 0.90)
  check(f"{short} detector set transition is higher than release transition",
        sm["driver_detect_set_abs_eps_torque_nm"]["p50"] > sm["driver_detect_release_abs_eps_torque_nm"]["p50"])
  counts = routes[short]["native_source_counts"]
  check(f"{short} EPS torque 0x030 is native chassis-side",
        counts["0x030/src0"] > 100 * counts["0x030/src2"])
  check(f"{short} 0x371 is native FRC-side",
        counts["0x371/src2"] > 100 * counts["0x371/src0"])

sm3d = routes["3d"]["native_state_machine_candidate"]
sm3f = routes["3f"]["native_state_machine_candidate"]
check("3d has one ~6 s second-stage escalation episode",
      sm3d["escalation_episode_count"] == 1 and
      5.8 <= sm3d["first_escalation_lag_from_warning_s"]["p50"] <= 6.1 and
      sm3d["escalation_episode_target_lateral_ids"] == [[11]])
check("3f has three ~6 s second-stage escalation episodes",
      sm3f["escalation_episode_count"] == 3 and
      5.8 <= sm3f["first_escalation_lag_from_warning_s"]["p50"] <= 6.1 and
      sm3f["escalation_episode_target_lateral_ids"] == [[11], [11], [11]])

for short in ("3d", "3e", "3f"):
  sm = routes[short]["native_state_machine_candidate"]
  release_timer = sm["warning_onset_time_since_driver_detect_release_s"]
  last_detect_timer = sm["warning_onset_time_since_last_driver_detect_s"]
  check(f"{short} Toyota warning follows driver-detect release at ~13 s",
        12.85 <= release_timer["p10"] <= release_timer["p50"] <= release_timer["p90"] <= 13.10)
  check(f"{short} last asserted detector sample is one 0x371 interval earlier",
        13.0 <= last_detect_timer["p10"] <= last_detect_timer["p50"] <= last_detect_timer["p90"] <= 13.30)

# Same-car stored FRC Operation-FFD witness from the retained 2818/0100 EB13
# response in the 2026-09-01 live communication notebook. This is a feature-
# capability discriminator, not a CAN-bit mapping.
same_car_5609 = bytes.fromhex("f8c0")
pcs = json.loads((REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json").read_text())
rows_5609 = {row["DataName"]: row for row in pcs["operation_ffd"]["detail_rows"] if row["DataID"] == "5609"}
check("5609 Hands-Off capability bit position pinned",
      (rows_5609["Hands-Off Exist"]["BytePosition"], rows_5609["Hands-Off Exist"]["BitPosition"]) == (2, 4))
check("5609 driver-camera collaboration bit position pinned",
      (rows_5609["LTA Driver Monitor Camera Collaboration Exist"]["BytePosition"],
       rows_5609["LTA Driver Monitor Camera Collaboration Exist"]["BitPosition"]) == (2, 3))
check("same-car FFD says ordinary LTA exists", bool(same_car_5609[1] & 0x80))
check("same-car FFD says Toyota Hands-Off feature does not exist", not bool(same_car_5609[1] & 0x10))
check("same-car FFD says LTA driver-camera collaboration does not exist", not bool(same_car_5609[1] & 0x08))
