#!/usr/bin/env python3
"""Verify route-48 Toyota-LTA-off / comma-B6 authority evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_20260907_lta_off_b6_authority.json"
DOC = ROOT / "docs/variants/camry-2026-live-baseline.md"

x = json.loads(ART.read_text())
assert x["schema"] == "camry-20260907-lta-off-b6-authority-v2"
e = x["evidence"]
assert e["input"]["route"] == "00000048--709f22277b"
assert e["input"]["segment_count"] == 8
assert e["input"]["total_bytes"] == 74_680_855
assert len({r["sha256"] for r in e["input"]["segments"]}) == 8
assert e["input"]["route_init_data"] == {
  "dirty": False,
  "gitBranch": "kai",
  "gitCommit": "bfa1352b25e64e50e1332d8661af475be9be04a4",
  "version": "0.11.2",
}

transport = e["transport"]
assert transport["b6_sendcan"] == 21_347
assert transport["b6_tx_echo_src128"] == 21_339
assert transport["b6_rejected_src192"] == 8
fmt = transport["b6_frame_format"]
assert fmt["sendcan_fd_true"] == 21_347
assert fmt["sendcan_zero_mac28"] == 21_347
assert fmt["tx_echo_fd_true"] == 21_339
assert fmt["rejected_fd_true"] == 8
assert fmt["sendcan_with_preceding_panda_state"] == 21_347
assert fmt["preceding_physical2_canfd_enabled"] == 21_347
assert fmt["preceding_physical2_brs_enabled"] == 21_347
assert fmt["preceding_physical2_speed_mode_counts"] == [{
  "can_speed_kbps": 500, "can_data_speed_kbps": 2000, "canfd_non_iso": False, "count": 21_347,
}]
assert transport["panda_health"]["safety_tx_blocked_delta"] == 1
for row in transport["panda_health"]["controller_deltas"]:
  assert row["total_error_cnt_delta"] == 0
  assert row["bus_off_delta"] == 0

state = e["state_census"]
assert state["fresh_joined_b6_rows"] == 21_335
assert state["upstream_request_id0_b6_active_rows"] == 10_017
assert state["upstream_request_id0_b6_active_episodes"] == 15
assert state["episodes_ge_1s"] == 14
assert 200.8 < state["episode_duration_sum_s"] < 201.0
assert state["stock_b6_state_counts"]["stock0_b611_cruise1_lat1"] == 10_021
assert state["stock_b6_state_counts"]["stock11_b611_cruise1_lat1"] == 1_171

iso = e["request_plane_off_b6_response"]
assert iso["large_error_threshold_deg"] == 3.0
assert iso["large_error_rows"] == 1_040
assert iso["large_error_motor_abs_raw"]["median"] == 13.0
assert iso["large_error_steering_rate_abs_deg_s"]["median"] == 0.0
w = iso["longest_continuous_large_error_witness"]
assert w["segment"] == 3
assert w["rows"] == 270
assert 5.35 < w["duration_s"] < 5.45
assert w["minimum_abs_b6_error_deg"] > 3.0
assert -5.2 < w["median_b6_error_deg"] < -5.0
assert abs(w["median_driver_torque_nm"]) < 0.02
assert abs(w["median_motor_feedback_raw"]) <= 1.0
assert w["median_steering_rate_deg_s"] == 0.0
assert 17.5 < w["median_v_ego_mps"] < 17.7
assert 0.7 < w["measured_start_deg"] < 0.9
assert 0.5 < w["measured_end_deg"] < 0.7

positive = e["same_route_stock_lta_positive_control"]
assert positive["rows"] == 383
assert positive["motor_abs_raw"]["median"] == 309.0
assert positive["motor_abs_raw"]["median"] > 20 * iso["large_error_motor_abs_raw"]["median"]
assert positive["motor_sign_toward_stock_fraction"] > 0.95

c = e["conclusion"]
assert c["turning_toyota_lta_off_preserved_openpilot_b6_id11"] is True
assert c["simultaneous_upstream_stock_id11_required_for_b6_nonresponse"] is False
assert c["route_proves_all_ordinary_f33_assist_terms_absent"] is False
assert c["route_proves_b6_effective_eps_authority"] is False

text = DOC.read_text()
for token in (
  "## 62. Route-48 Toyota-LTA-off B6 isolation (VAR-145)",
  "10,017",
  "200.891",
  "5.402 s",
  "309",
  "21,347/21,347",
  "CAN-FD+BRS",
  "upstream Toyota autonomous",
  "not proof that every ordinary F33",
):
  assert token in text, token

print("camry 2026-09-07 Toyota-LTA-off B6 authority: PASS")
