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
timing3f = hud3f["native_timing"]
check("3f 0x412 native heartbeat is approximately 1 Hz",
      990 <= timing3f["interval_ms"]["p50"] <= 1010)
check("3f 0x412 has event-driven publications but no sub-75-ms burst",
      75 <= timing3f["interval_min_ms"] < 100 and timing3f["payload_change_interval_count"] > 300)

check("report schema includes state-machine, HUD timing, stock-ACC hold, and lane-orientation bounds", report["schema_version"] == 6)

hold3b = routes["3b"]["stock_acc_standstill_candidate"]
hold3c = routes["3c"]["stock_acc_standstill_candidate"]
check("3b stock-ACC standstill state has 152 source-real frames", hold3b["frames"] == 152)
check("3c stock-ACC standstill state has 46 source-real frames", hold3c["frames"] == 46)
check("3b stock-ACC standstill states are exactly 45/103 and 44/102",
      hold3b["cruise_substate_pair_counts"].get("45,103") == 148 and
      hold3b["cruise_substate_pair_counts"].get("44,102") == 4)
check("3c stock-ACC standstill states are exactly 45/103 and 44/102",
      hold3c["cruise_substate_pair_counts"].get("45,103") == 44 and
      hold3c["cruise_substate_pair_counts"].get("44,102") == 2)
check("all retained stock-ACC hold frames are exactly stopped",
      hold3b["all_frames_exactly_stopped"] and hold3c["all_frames_exactly_stopped"])
check("stock-ACC hold remains native LTA/LCA ID11", hold3b["all_episode_target_lateral_ids"] == [11] and
      hold3c["all_episode_target_lateral_ids"] == [11])
check("stock-ACC hold appears in three independent stop episodes",
      len(hold3b["episodes"]) == 2 and len(hold3c["episodes"]) == 1)
check("all retained stock-ACC hold episodes clear with accelerator input before motion",
      all(e["clear_gas_pressed"] is True and e["clear_abs_speed_m_s"] < 0.1 for e in hold3b["episodes"] + hold3c["episodes"]))
check("stock-ACC reducer does not overclaim a RES-button clear join", "no RES-button clear join" in hold3b["boundary"])
check("stock-ACC hold is delayed after the vehicle first stops",
      all(e["time_since_last_moving_at_start_s"] > 5.0 for e in hold3b["episodes"] + hold3c["episodes"]))
check("other September highway routes do not spuriously enter stock-ACC hold",
      all(routes[short]["stock_acc_standstill_candidate"]["frames"] == 0 for short in ("3d", "3e", "3f")))

lane_counts = hud3f["lane_nibble_counts_high_low"]
lane_join = hud3f["lane_nibble_model_join"]
check("3f HUD active recognized-lane state dominates", lane_counts["4,4"] > 3000)
check("3f HUD inactive recognized and missing states are well populated",
      lane_counts["1,1"] > 500 and lane_counts["2,2"] > 1000)
check("3f HUD mixed per-side recognition states are observed",
      lane_counts["1,2"] > 100 and lane_counts["2,1"] > 100)
check("3f HUD has no state-3 rows on this route",
      all("3" not in key.split(",") for key in lane_counts))
check("3b HUD retains the four observed high/low 2,3 rows",
      routes["3b"]["hud_companion_candidate"]["lane_nibble_counts_high_low"].get("2,3") == 4)
check("HUD reducer keeps nibble side orientation explicitly unproved",
      "does not by itself prove which nibble is left versus right" in hud3f["lane_state_boundary"] and
      "5514" in hud3f["lane_state_boundary"])
check("3f active HUD 4,4 joins strong model lane visibility",
      lane_join["4,4"]["left_lane_visible_fraction_gt_0_5"] > 0.98 and
      lane_join["4,4"]["right_lane_visible_fraction_gt_0_5"] > 0.98)
check("3f inactive HUD 1,1 joins recognized model lanes",
      lane_join["1,1"]["left_lane_prob_mean"] > 0.85 and
      lane_join["1,1"]["right_lane_prob_mean"] > 0.85)
check("3f inactive HUD 2,2 joins weak/missing model lanes",
      lane_join["2,2"]["left_lane_prob_mean"] < 0.40 and
      lane_join["2,2"]["right_lane_prob_mean"] < 0.35)

for short, expected_starts in (("3e", 20), ("3f", 25)):
  sm = routes[short]["native_state_machine_candidate"]
  fit = sm["single_threshold_fit"]
  sign = sm["lane_change_starting_sign"]
  selected = fit["selected_threshold_witnesses"]["0.60"]
  check(f"{short} driver torque policy threshold recorded as 0.6 N.m",
        fit["selected_policy_threshold_nm"] == 0.6)
  check(f"{short} 0.6 N.m policy has high Toyota-state specificity",
        selected["true_negative_rate"] > 0.94)
  check(f"{short} 0.6 N.m policy retains useful Toyota-state sensitivity",
        selected["true_positive_rate"] > 0.74)
  check(f"{short} all post-fix lane-change starts match Toyota torque sign convention",
        sign["count"] == expected_starts and sign["sign_matches_direction"] == expected_starts)
  check(f"{short} post-fix lane-change starts exercise both directions",
        sign["left"] > 0 and sign["right"] > 0)
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
operation_rows = pcs["operation_ffd"]["detail_rows"]
rows_5609 = {row["DataName"]: row for row in operation_rows if row["DataID"] == "5609"}
rows_5514 = {row["DataName"]: row for row in operation_rows if row["DataID"] == "5514"}
check("5514 exposes left/right lane and steering-symbol passive oracles",
      set(rows_5514) == {"Left Lane Display", "Right Lane Display", "Steering Symbol Display"} and
      [rows_5514[name]["BytePosition"] for name in ("Left Lane Display", "Right Lane Display", "Steering Symbol Display")] == [1, 2, 3] and
      all(rows_5514[name]["SupportDID"] == 0 for name in rows_5514))
rows_525e = [row for row in operation_rows if row["DataID"] == "525E" and row["DataName"] == "Stop holding status"]
check("525E exposes the stop-holding semantic oracle without a SupportDID join",
      len(rows_525e) == 1 and rows_525e[0]["SupportDID"] == 0)
check("5609 Hands-Off capability bit position pinned",
      (rows_5609["Hands-Off Exist"]["BytePosition"], rows_5609["Hands-Off Exist"]["BitPosition"]) == (2, 4))
check("5609 driver-camera collaboration bit position pinned",
      (rows_5609["LTA Driver Monitor Camera Collaboration Exist"]["BytePosition"],
       rows_5609["LTA Driver Monitor Camera Collaboration Exist"]["BitPosition"]) == (2, 3))
check("same-car FFD says ordinary LTA exists", bool(same_car_5609[1] & 0x80))
check("same-car FFD says Toyota Hands-Off feature does not exist", not bool(same_car_5609[1] & 0x10))
check("same-car FFD says LTA driver-camera collaboration does not exist", not bool(same_car_5609[1] & 0x08))
