#!/usr/bin/env python3
"""Verify the compact Sep-7 Camry stock/comma steering reconciliation artifact."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_20260907_steering_reconciliation.json"
DOC = ROOT / "docs/variants/camry-2026-live-baseline.md"

x = json.loads(ART.read_text(encoding="utf-8"))
e = x["evidence"]

assert x["schema"] == "camry-20260907-steering-reconciliation-v3"
assert e["input"]["route"] == "00000045--805b7ca6ab"
assert e["input"]["segment_count"] == 15
assert e["input"]["total_bytes"] == 149_376_764
assert len(e["input"]["segments"]) == 15
assert all(len(row["sha256"]) == 64 for row in e["input"]["segments"])
assert e["input"]["route_init_data"]["gitCommit"] == "f8bd956a4b23eb4992c6abbe899e72b27cd91d80"
assert e["input"]["route_init_data"]["dirty"] is False

wire = e["openpilot_to_b6"]
assert wire["active_b6_events_with_fresh_control"] == 17_461
assert wire["b6_minus_car_control_deg"]["count"] == 17_461
assert wire["b6_minus_car_control_deg"]["median_abs"] < 0.015
assert wire["b6_minus_car_control_deg"]["p90_abs"] < 0.027

both = e["stock_vs_openpilot_when_both_id11"]
assert both["count"] == 16_423
assert 0.56 < both["b6_minus_stock_deg"]["median_abs"] < 0.59
assert 1.36 < both["b6_minus_stock_deg"]["p90_abs"] < 1.39
assert 0.58 < both["raw_correlation"] < 0.61
assert 0.70 < both["stock_vs_b6_minus_live_offset_correlation"] < 0.73
assert both["b6_minus_live_offset_minus_stock_deg"]["rmse"] < both["b6_minus_stock_deg"]["rmse"]
assert both["opposite_sign_when_both_abs_gt_0p5_deg"] == 220
assert both["both_abs_gt_0p5_deg"] == 6_724

auth = e["request_reference_plane_observation"]
d05 = auth["divergence_0p5_deg"]
assert d05["count"] == 8_235
assert d05["reference_closer_to_stock_count"] == 8_229
assert d05["reference_closer_to_b6_count"] == 6
assert d05["reference_minus_stock_deg"]["median_abs"] == 0.0
assert d05["reference_minus_stock_deg"]["p90_abs"] < 0.058
assert d05["reference_position_ratio"]["median"] == 0.0
assert d05["reference_position_ratio"]["p90_abs"] <= 0.1
assert auth["divergence_2p5_deg"]["count"] == 53
assert auth["divergence_2p5_deg"]["reference_closer_to_stock_count"] == 53
assert auth["divergence_2p5_deg"]["reference_closer_to_b6_count"] == 0
stock0 = auth["stock_id0_b6_id11_low_torque"]
assert stock0["count"] == 228
assert stock0["reference_id_counts"] == {"0": 225, "11": 3}
assert stock0["reference_minus_stock_deg"]["median_abs"] == 0.0
assert 1.64 < stock0["reference_minus_b6_deg"]["median_abs"] < 1.68

manual = e["stock_id0_reference_plane"]
assert manual["count"] == 2_901
bfit = manual["b6_from_measured_fit"]
sfit = manual["stock_08a_from_measured_fit"]
assert abs(bfit["slope"] - 1.0) < 0.001
assert abs(bfit["intercept_deg"]) < 0.01
assert bfit["correlation"] > 0.9999
assert bfit["fit_residual_rmse_deg"] < 0.04
assert 0.95 < sfit["slope"] < 0.98
assert -0.80 < sfit["intercept_deg"] < -0.73
assert 0.998 < sfit["correlation"] < 0.999
assert 0.38 < sfit["fit_residual_rmse_deg"] < 0.42
assert -0.81 < manual["stock_minus_measured_deg"]["median"] < -0.76

path = e["model_path_vs_inner_lane_lines"]
assert path["active_model_rows"] == 7_014
assert path["high_confidence_rows"] == 6_836
assert path["outside_lane_count"] == {"10": 0, "20": 0, "30": 0}
assert path["full_rendered_path_0_to_100m_outside_rows"] == 0
assert path["full_rendered_path_0_to_100m_min_margin_m"]["count"] == 6_836
assert path["full_rendered_path_0_to_100m_min_margin_m"]["min"] > 1.0
for distance in ("10", "20", "30"):
  assert path["margin_m"][distance]["min"] > 1.10
  assert abs(path["path_minus_lane_center_m"][distance]["mean"]) < 0.03
assert path["lane_center_y_at_vehicle_m"]["max"] > 0.44
assert path["lane_center_y_at_vehicle_m"]["min"] < -0.35

off = path["offcenter_behavior"]
t03 = off["threshold_0p3m"]
assert t03["count"] == 230
assert t03["path10_same_edge_side_count"] == 230
assert t03["path10_farther_from_center_than_vehicle_count"] == 103
assert t03["b6_error_points_away_from_lane_center_count"] == 191
assert t03["stock_error_points_away_from_lane_center_count"] == 156
t04 = off["threshold_0p4m"]
assert t04["count"] == 57
assert t04["b6_error_points_away_from_lane_center_count"] == 55
assert off["edge_bias_rows"] == 103
assert off["edge_bias_episode_count"] == 8
w = off["longest_low_torque_edge_bias_episode"]
assert w["segment"] == 2
assert w["rows"] == 40
assert 1.95 < w["duration_s"] < 2.05
assert -0.39 < w["median_vehicle_offset_m"] < -0.36
assert -0.41 < w["median_path10_offset_m"] < -0.37
assert -1.20 < w["median_b6_error_deg"] < -1.14
assert -0.28 < w["median_stock_error_deg"] < -0.23
assert -0.28 < w["median_reference_error_deg"] < -0.23
assert abs(w["median_driver_torque_nm"]) < 0.05
assert 19.9 < w["median_v_ego_mps"] < 20.1

noncoincident = e["stock_id0_while_openpilot_b6_id11"]
assert noncoincident["model_rows"] == 416
assert noncoincident["rows_with_abs_driver_torque_lt_0p5_nm"] == 123

conclusion = e["conclusion"]
assert conclusion["b6_wire_angle_matches_openpilot_request"] is True
assert conclusion["stock_08a_and_b6_are_not_interchangeable_reference_planes"] is True
assert conclusion["fixed_stock_to_b6_offset_is_supported"] is False
assert conclusion["high_confidence_model_path_crossed_inner_lane_line"] is False
assert conclusion["route_proves_b6_only_physical_authority"] is False
assert conclusion["published_081_is_eps_b6_blend_discriminator"] is False
assert conclusion["forwarded_08a_is_f33_authority_isolation_switch"] is False
assert conclusion["route_observes_eps_side_b6_composition"] is False

text = DOC.read_text(encoding="utf-8")
for token in (
  "## 61. Route-45 stock/comma steering reconciliation (VAR-144)",
  "17,461",
  "16,423",
  "6,836/6,836",
  "191/230",
  "2.000 s",
  "not a stock→B6 transform",
  "8,229/8,235",
  "53/53",
  "does **not** identify EPS-side authority",
  "co-modulated with the ordinary EPS",
):
  assert token in text, token

print("camry 2026-09-07 steering reconciliation: PASS")
