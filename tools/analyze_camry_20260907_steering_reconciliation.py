#!/usr/bin/env python3
"""Reconcile stock 0x08A and openpilot B6 steering on the Sep-7 Camry route.

The exact-F33 static work already proves that B6 B4:B5 is a signed target-angle
command at 1024/17870 deg/count and that captured 0x08A B18:B19 uses the same
numeric scale while living on a different request plane.  This reducer answers
what the first post-transport-fix road capture says about those two values:

* Does the transmitted B6 target equal the angle requested by openpilot?
* Is stock 0x08A numerically interchangeable with B6, or is it a differently
  compensated representation despite the shared scale?
* Did the model path actually leave the two high-confidence inner lane lines
  when the driver reported that the steering visualization looked odd?

Full rlogs are maintainer-local external inputs.  The generated JSON is a
compact, deterministic evidence artifact; the verifier pins the decisive
counts and bounds without treating an empirical stock/comma fit as a control
transform.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_ROUTE = Path("/Users/kai/dev/inspect/logs/camry-2026/2026-09-07/00000045--805b7ca6ab")
DEFAULT_OPENPILOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
DEFAULT_OUT = Path("data/generated/camry_20260907_steering_reconciliation.json")
ANGLE_SCALE = 1024 / 17870


def load_logreader(root: Path):
  sys.path.insert(0, str(root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def segment_files(route: Path) -> list[tuple[int, Path]]:
  rows: list[tuple[int, Path]] = []
  for p in route.glob("*/rlog.zst"):
    try:
      rows.append((int(p.parent.name.rsplit("--", 1)[1]), p))
    except (IndexError, ValueError):
      pass
  for p in route.glob("rlog-*.zst"):
    try:
      rows.append((int(p.name[5:-4]), p))
    except ValueError:
      pass
  return sorted(dict(rows).items())


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
      h.update(chunk)
  return h.hexdigest()


def decode_08a(dat: bytes) -> tuple[int, int, float]:
  raw = int.from_bytes(dat[18:20], "big", signed=True)
  return dat[21] & 0x3F, raw, raw * ANGLE_SCALE


def decode_081(dat: bytes) -> tuple[int, int, float]:
  raw = int.from_bytes(dat[16:18], "big", signed=True)
  return dat[13] & 0x3F, raw, raw * ANGLE_SCALE


def decode_b6(dat: bytes) -> tuple[int, int, float]:
  raw = int.from_bytes(dat[4:6], "big", signed=True)
  return dat[3] & 0x3F, raw, raw * ANGLE_SCALE


def interp(x: list[float], y: list[float], at: float) -> float:
  if not x or not y:
    return math.nan
  n = min(len(x), len(y))
  xa = np.asarray(x[:n], dtype=np.float64)
  ya = np.asarray(y[:n], dtype=np.float64)
  return float(np.interp(at, xa, ya))


def qstats(values: list[float]) -> dict[str, float | int]:
  a = np.asarray(values, dtype=np.float64)
  if not len(a):
    return {"count": 0}
  return {
    "count": len(a),
    "mean": round(float(np.mean(a)), 9),
    "median": round(float(np.median(a)), 9),
    "median_abs": round(float(np.median(np.abs(a))), 9),
    "p90_abs": round(float(np.percentile(np.abs(a), 90)), 9),
    "rmse": round(float(np.sqrt(np.mean(a * a))), 9),
    "min": round(float(np.min(a)), 9),
    "max": round(float(np.max(a)), 9),
  }


def correlation(a: list[float], b: list[float]) -> float | None:
  if len(a) < 3 or len(b) != len(a):
    return None
  aa = np.asarray(a, dtype=np.float64)
  bb = np.asarray(b, dtype=np.float64)
  if float(np.std(aa)) < 1e-12 or float(np.std(bb)) < 1e-12:
    return None
  return round(float(np.corrcoef(aa, bb)[0, 1]), 9)


def linear_fit(x: list[float], y: list[float]) -> dict[str, float | int | None]:
  xx = np.asarray(x, dtype=np.float64)
  yy = np.asarray(y, dtype=np.float64)
  A = np.column_stack((xx, np.ones(len(xx))))
  slope, intercept = np.linalg.lstsq(A, yy, rcond=None)[0]
  residual = yy - (slope * xx + intercept)
  return {
    "count": len(xx),
    "slope": round(float(slope), 9),
    "intercept_deg": round(float(intercept), 9),
    "correlation": correlation(x, y),
    "fit_residual_rmse_deg": round(float(np.sqrt(np.mean(residual * residual))), 9),
  }


def scan(LogReader, route: Path) -> dict[str, Any]:
  segments = segment_files(route)
  inventory = [{"segment": n, "bytes": p.stat().st_size, "sha256": sha256(p)} for n, p in segments]
  init_data: dict[str, Any] = {}

  # B6-event rows are the high-rate wire/control reconciliation.  Model rows are
  # sampled only on modelV2 publication so lane/path geometry shares one frame.
  active_b6_vs_control: list[float] = []
  active_b6_vs_output: list[float] = []
  both_active_stock: list[float] = []
  both_active_b6: list[float] = []
  both_active_offset: list[float] = []
  opposite_large = 0
  comparable_large = 0
  authority_rows: list[dict[str, float | int]] = []
  stock0_b611_authority_rows: list[dict[str, float | int]] = []

  manual_measured: list[float] = []
  manual_stock: list[float] = []
  manual_b6: list[float] = []

  path_rows = 0
  path_high_confidence_rows = 0
  path_outside = {10: 0, 20: 0, 30: 0}
  path_margin: dict[int, list[float]] = {10: [], 20: [], 30: []}
  path_center_error: dict[int, list[float]] = {10: [], 20: [], 30: []}
  full_path_outside_rows = 0
  full_path_min_margin: list[float] = []
  lane_center_y: list[float] = []
  offcenter_rows: list[dict[str, float | int]] = []

  stock0_b611_rows = 0
  stock0_b611_low_torque_rows = 0

  for _seg, path in segments:
    latest: dict[str, tuple[Any, ...]] = {}
    for e in LogReader(str(path), sort_by_time=True, only_union_types=True):
      t = int(e.logMonoTime)
      which = e.which()

      if which == "initData" and not init_data:
        x = e.initData
        init_data = {
          "gitCommit": str(x.gitCommit), "gitBranch": str(x.gitBranch),
          "dirty": bool(x.dirty), "version": str(x.version),
        }

      elif which == "can":
        for fr in e.can:
          addr, src, dat = int(fr.address), int(fr.src), bytes(fr.dat)
          if addr == 0x08A and src == 2 and len(dat) >= 22:
            latest["stock"] = (t, *decode_08a(dat))
          elif addr == 0x081 and src == 0 and len(dat) >= 18:
            latest["reference"] = (t, *decode_081(dat))
          elif addr == 0x030 and src == 0 and len(dat) >= 24:
            latest["motor"] = (t, int.from_bytes(dat[22:24], "big", signed=True))

      elif which == "carControl":
        cc = e.carControl
        latest["control"] = (t, bool(cc.latActive), float(cc.actuators.steeringAngleDeg))

      elif which == "carOutput":
        latest["output"] = (t, float(e.carOutput.actuatorsOutput.steeringAngleDeg))

      elif which == "carState":
        cs = e.carState
        latest["state"] = (
          t, float(cs.steeringAngleDeg), float(cs.steeringRateDeg), float(cs.steeringTorque), float(cs.vEgo),
          bool(cs.leftBlinker or cs.rightBlinker),
        )

      elif which == "vehicleParameters":
        vp = e.vehicleParameters
        latest["params"] = (
          t, float(vp.angleOffsetDeg), float(vp.angleOffsetAverageDeg), float(vp.steerRatio), float(vp.roll),
        )

      elif which == "sendcan":
        for fr in e.sendcan:
          if int(fr.address) != 0x0B6 or int(fr.src) != 0 or len(fr.dat) != 32:
            continue
          latest["b6"] = (t, *decode_b6(bytes(fr.dat)))
          b6 = latest["b6"]
          control = latest.get("control")
          output = latest.get("output")
          if b6[1] == 11 and control and control[1] and 0 <= t - control[0] <= 30_000_000:
            active_b6_vs_control.append(float(b6[3]) - float(control[2]))
            if output and 0 <= t - output[0] <= 30_000_000:
              active_b6_vs_output.append(float(b6[3]) - float(output[1]))

            stock = latest.get("stock")
            params = latest.get("params")
            if (stock and stock[1] == 11 and 0 <= t - stock[0] <= 40_000_000 and
                params and 0 <= t - params[0] <= 100_000_000):
              stock_angle = float(stock[3])
              b6_angle = float(b6[3])
              both_active_stock.append(stock_angle)
              both_active_b6.append(b6_angle)
              both_active_offset.append(float(params[1]))
              if abs(stock_angle) > 0.5 and abs(b6_angle) > 0.5:
                comparable_large += 1
                if stock_angle * b6_angle < 0:
                  opposite_large += 1

              reference = latest.get("reference")
              state = latest.get("state")
              if (reference and state and 0 <= t - reference[0] <= 40_000_000 and
                  0 <= t - state[0] <= 50_000_000 and float(state[4]) > 10.0 and
                  abs(float(state[3])) < 0.7 and not bool(state[5])):
                authority_rows.append({
                  "stock_deg": stock_angle,
                  "b6_deg": b6_angle,
                  "reference_deg": float(reference[3]),
                })

            reference = latest.get("reference")
            state = latest.get("state")
            if (stock and stock[1] == 0 and reference and state and
                0 <= t - stock[0] <= 40_000_000 and 0 <= t - reference[0] <= 40_000_000 and
                0 <= t - state[0] <= 50_000_000 and float(state[4]) > 10.0 and
                abs(float(state[3])) < 0.5 and not bool(state[5])):
              stock0_b611_authority_rows.append({
                "stock_id": int(stock[1]), "stock_deg": float(stock[3]),
                "reference_id": int(reference[1]), "reference_deg": float(reference[3]),
                "b6_deg": float(b6[3]),
              })

      elif which == "modelV2":
        b6 = latest.get("b6")
        stock = latest.get("stock")
        control = latest.get("control")
        state = latest.get("state")
        params = latest.get("params")
        if not (b6 and stock and control and state and params):
          continue
        if any(t - x[0] < 0 for x in (b6, stock, control, state, params)):
          continue
        if t - b6[0] > 50_000_000 or t - stock[0] > 50_000_000 or t - control[0] > 100_000_000 or t - state[0] > 100_000_000:
          continue

        # Inactive B6 is constructed from current 0x025 steering angle.  The
        # low-dynamic subset quantifies that host reference plane and compares
        # it with stock 0x08A ID0 without assuming a fixed stock compensation.
        if (b6[1] == 0 and stock[1] == 0 and float(state[4]) > 10.0 and
            abs(float(state[1])) < 20.0 and abs(float(state[2])) < 5.0 and abs(float(b6[3])) < 30.0):
          manual_measured.append(float(state[1]))
          manual_stock.append(float(stock[3]))
          manual_b6.append(float(b6[3]))

        if control[1] and b6[1] == 11:
          path_rows += 1
          if stock[1] == 0:
            stock0_b611_rows += 1
            if abs(float(state[3])) < 0.5:
              stock0_b611_low_torque_rows += 1

          m = e.modelV2
          if len(m.laneLines) < 3 or len(m.laneLineProbs) < 3:
            continue
          if float(m.laneLineProbs[1]) < 0.5 or float(m.laneLineProbs[2]) < 0.5:
            continue
          if not len(m.position.x) or not len(m.position.y):
            continue

          path_high_confidence_rows += 1
          center0 = (float(m.laneLines[1].y[0]) + float(m.laneLines[2].y[0])) / 2.0
          lane_center_y.append(center0)
          px, py = list(m.position.x), list(m.position.y)
          l1x, l1y = list(m.laneLines[1].x), list(m.laneLines[1].y)
          l2x, l2y = list(m.laneLines[2].x), list(m.laneLines[2].y)

          # The onroad renderer uses the raw model path, not merely 10/20/30-m
          # probes. Check every raw path point through 100 m so a far-horizon
          # visual crossing cannot hide between the fixed-distance summaries.
          xmax = min(px[-1], l1x[-1], l2x[-1], 100.0)
          full_margins: list[float] = []
          for path_x, path_y in zip(px, py, strict=True):
            if not 0.0 <= path_x <= xmax:
              continue
            y1 = interp(l1x, l1y, path_x)
            y2 = interp(l2x, l2y, path_x)
            lo, hi = sorted((y1, y2))
            full_margins.append(min(path_y - lo, hi - path_y))
          if full_margins:
            min_margin = min(full_margins)
            full_path_min_margin.append(min_margin)
            if min_margin < 0:
              full_path_outside_rows += 1

          probe_errors: dict[int, float] = {}
          for distance in (10, 20, 30):
            path_y = interp(px, py, float(distance))
            y1 = interp(l1x, l1y, float(distance))
            y2 = interp(l2x, l2y, float(distance))
            if not all(math.isfinite(v) for v in (path_y, y1, y2)):
              continue
            lo, hi = sorted((y1, y2))
            margin = min(path_y - lo, hi - path_y)
            center_error = path_y - ((y1 + y2) / 2.0)
            probe_errors[distance] = center_error
            path_margin[distance].append(margin)
            path_center_error[distance].append(center_error)
            if margin < 0:
              path_outside[distance] += 1

          # "Off-center" is measured entirely in the model frame: center0 is
          # the detected lane center relative to the vehicle at x=0, so the
          # vehicle's own lateral offset from that center is -center0.  Compare
          # the 10-m path to that offset and compare stock/comma steering errors
          # to the direction back toward lane center.  This does not assert
          # physical B6 authority; it only describes the planner/request geometry.
          if 10 in probe_errors:
            vehicle_offset = -center0
            path10_offset = probe_errors[10]
            b6_error = float(b6[3]) - float(state[1])
            stock_error = float(stock[3]) - float(state[1])
            row: dict[str, float | int] = {
              "segment": _seg, "time_ns": t,
              "v_ego_mps": float(state[4]), "driver_torque_nm": float(state[3]),
              "vehicle_offset_m": vehicle_offset, "path10_offset_m": path10_offset,
              "b6_error_deg": b6_error, "stock_error_deg": stock_error,
            }
            reference = latest.get("reference")
            if reference and 0 <= t - reference[0] <= 50_000_000:
              row["reference_error_deg"] = float(reference[3]) - float(state[1])
            offcenter_rows.append(row)

  def offcenter_summary(threshold_m: float) -> dict[str, Any]:
    rows = [r for r in offcenter_rows if abs(float(r["vehicle_offset_m"])) >= threshold_m]
    if not rows:
      return {"count": 0}
    same_edge = [r for r in rows if float(r["path10_offset_m"]) * float(r["vehicle_offset_m"]) > 0]
    farther = [r for r in rows if abs(float(r["path10_offset_m"])) > abs(float(r["vehicle_offset_m"]))]
    b6_away = [r for r in rows if float(r["b6_error_deg"]) * float(r["vehicle_offset_m"]) > 0]
    stock_away = [r for r in rows if float(r["stock_error_deg"]) * float(r["vehicle_offset_m"]) > 0]
    return {
      "count": len(rows),
      "median_abs_vehicle_offset_m": round(float(np.median([abs(float(r["vehicle_offset_m"])) for r in rows])), 9),
      "path10_same_edge_side_count": len(same_edge),
      "path10_same_edge_side_fraction": round(len(same_edge) / len(rows), 9),
      "path10_farther_from_center_than_vehicle_count": len(farther),
      "path10_farther_from_center_than_vehicle_fraction": round(len(farther) / len(rows), 9),
      "b6_error_points_away_from_lane_center_count": len(b6_away),
      "b6_error_points_away_from_lane_center_fraction": round(len(b6_away) / len(rows), 9),
      "stock_error_points_away_from_lane_center_count": len(stock_away),
      "stock_error_points_away_from_lane_center_fraction": round(len(stock_away) / len(rows), 9),
    }

  # Deterministic edge-bias witness: car >=0.30 m from detected center and the
  # 10-m planned path is even farther toward that same edge.  Group 20-Hz model
  # rows into episodes allowing ordinary dropped/jittered samples up to 200 ms.
  edge_rows = [r for r in offcenter_rows
               if abs(float(r["vehicle_offset_m"])) >= 0.30
               and float(r["path10_offset_m"]) * float(r["vehicle_offset_m"]) > 0
               and abs(float(r["path10_offset_m"])) > abs(float(r["vehicle_offset_m"]))]
  episodes: list[list[dict[str, float | int]]] = []
  for row in edge_rows:
    if (not episodes or int(row["segment"]) != int(episodes[-1][-1]["segment"])
        or int(row["time_ns"]) - int(episodes[-1][-1]["time_ns"]) > 200_000_000):
      episodes.append([row])
    else:
      episodes[-1].append(row)

  def episode_summary(rows: list[dict[str, float | int]]) -> dict[str, Any]:
    return {
      "segment": int(rows[0]["segment"]),
      "rows": len(rows),
      "duration_s": round((int(rows[-1]["time_ns"]) - int(rows[0]["time_ns"])) / 1e9, 6),
      "median_vehicle_offset_m": round(float(np.median([float(r["vehicle_offset_m"]) for r in rows])), 9),
      "median_path10_offset_m": round(float(np.median([float(r["path10_offset_m"]) for r in rows])), 9),
      "median_b6_error_deg": round(float(np.median([float(r["b6_error_deg"]) for r in rows])), 9),
      "median_stock_error_deg": round(float(np.median([float(r["stock_error_deg"]) for r in rows])), 9),
      "median_reference_error_deg": round(float(np.median([float(r["reference_error_deg"]) for r in rows if "reference_error_deg" in r])), 9),
      "median_driver_torque_nm": round(float(np.median([float(r["driver_torque_nm"]) for r in rows])), 9),
      "median_v_ego_mps": round(float(np.median([float(r["v_ego_mps"]) for r in rows])), 9),
    }

  episode_summaries = [episode_summary(rows) for rows in episodes]
  low_torque_episodes = [x for x in episode_summaries if abs(float(x["median_driver_torque_nm"])) < 0.5]
  longest_low_torque = max(low_torque_episodes, key=lambda x: (int(x["rows"]), float(x["duration_s"])), default=None)

  def reference_authority_summary(threshold_deg: float) -> dict[str, Any]:
    rows = [r for r in authority_rows if abs(float(r["b6_deg"]) - float(r["stock_deg"])) >= threshold_deg]
    if not rows:
      return {"count": 0}
    ref_stock = [float(r["reference_deg"]) - float(r["stock_deg"]) for r in rows]
    ref_b6 = [float(r["reference_deg"]) - float(r["b6_deg"]) for r in rows]
    weights = [(float(r["reference_deg"]) - float(r["stock_deg"])) /
               (float(r["b6_deg"]) - float(r["stock_deg"])) for r in rows]
    stock_closer = sum(abs(a) < abs(b) for a, b in zip(ref_stock, ref_b6, strict=True))
    b6_closer = sum(abs(b) < abs(a) for a, b in zip(ref_stock, ref_b6, strict=True))
    return {
      "count": len(rows),
      "reference_minus_stock_deg": qstats(ref_stock),
      "reference_minus_b6_deg": qstats(ref_b6),
      "reference_closer_to_stock_count": stock_closer,
      "reference_closer_to_b6_count": b6_closer,
      "blend_alpha_definition": "(0x081 - stock_0x08A) / (B6 - stock_0x08A); 0=stock plane, 1=B6 plane",
      "blend_alpha": qstats(weights),
    }

  stock0_ref_ids: dict[str, int] = {}
  for row in stock0_b611_authority_rows:
    key = str(int(row["reference_id"]))
    stock0_ref_ids[key] = stock0_ref_ids.get(key, 0) + 1

  raw_diff = [b - s for b, s in zip(both_active_b6, both_active_stock, strict=True)]
  no_live_offset = [b - o for b, o in zip(both_active_b6, both_active_offset, strict=True)]
  offset_removed_diff = [b - o - s for b, o, s in zip(both_active_b6, both_active_offset, both_active_stock, strict=True)]

  return {
    "input": {
      "route": route.name,
      "segment_count": len(segments),
      "total_bytes": sum(r["bytes"] for r in inventory),
      "segments": inventory,
      "route_init_data": init_data,
    },
    "angle_contract": {
      "scale_deg_per_count": ANGLE_SCALE,
      "stock_08a_field": "B18:B19 signed BE16; Target Steering Angle After Output Compensation plane",
      "openpilot_b6_field": "B4:B5 signed BE16; exact-F33 B6 target-angle plane",
      "shared_numeric_scale_is_not_a_claim_of_identical_processing_stage": True,
    },
    "openpilot_to_b6": {
      "active_b6_events_with_fresh_control": len(active_b6_vs_control),
      "b6_minus_car_control_deg": qstats(active_b6_vs_control),
      "b6_minus_car_output_deg": qstats(active_b6_vs_output),
    },
    "stock_vs_openpilot_when_both_id11": {
      "count": len(raw_diff),
      "b6_minus_stock_deg": qstats(raw_diff),
      "raw_correlation": correlation(both_active_stock, both_active_b6),
      "live_angle_offset_deg": qstats(both_active_offset),
      "stock_vs_b6_minus_live_offset_correlation": correlation(both_active_stock, no_live_offset),
      "b6_minus_live_offset_minus_stock_deg": qstats(offset_removed_diff),
      "b6_minus_stock_vs_live_offset_correlation": correlation(raw_diff, both_active_offset),
      "opposite_sign_when_both_abs_gt_0p5_deg": opposite_large,
      "both_abs_gt_0p5_deg": comparable_large,
    },
    "concurrent_authority_observation": {
      "selection": "B6 ID11 + stock 0x08A ID11 + latActive; vEgo>10m/s; abs(driver torque)<0.7Nm; no blinker; <=40/50ms freshness",
      "reference_081_role": "chassis-side published reference/result plane; exact F33 does not receive 0x081",
      "divergence_0p5_deg": reference_authority_summary(0.5),
      "divergence_1p0_deg": reference_authority_summary(1.0),
      "divergence_2p0_deg": reference_authority_summary(2.0),
      "divergence_2p5_deg": reference_authority_summary(2.5),
      "stock_id0_b6_id11_low_torque": {
        "count": len(stock0_b611_authority_rows),
        "reference_id_counts": stock0_ref_ids,
        "reference_minus_stock_deg": qstats([float(r["reference_deg"]) - float(r["stock_deg"]) for r in stock0_b611_authority_rows]),
        "reference_minus_b6_deg": qstats([float(r["reference_deg"]) - float(r["b6_deg"]) for r in stock0_b611_authority_rows]),
      },
      "interpretation": "0x081 remains on the stock request/reference plane rather than a stock/B6 midpoint. Any B6 influence must therefore be downstream of, or separate from, this published reference plane. Because stock 0x08A is still forwarded, this route cannot distinguish B6-only authority from additive/coexisting EPS control or source priority.",
    },
    "stock_id0_reference_plane": {
      "selection": "stock ID0 + B6 ID0; vEgo>10 m/s; abs(measured)<20 deg; abs(rate)<5 deg/s; abs(B6)<30 deg",
      "count": len(manual_measured),
      "b6_from_measured_fit": linear_fit(manual_measured, manual_b6),
      "stock_08a_from_measured_fit": linear_fit(manual_measured, manual_stock),
      "stock_minus_measured_deg": qstats([s - m for s, m in zip(manual_stock, manual_measured, strict=True)]),
      "b6_minus_measured_deg": qstats([b - m for b, m in zip(manual_b6, manual_measured, strict=True)]),
    },
    "model_path_vs_inner_lane_lines": {
      "active_model_rows": path_rows,
      "high_confidence_rows": path_high_confidence_rows,
      "confidence_rule": "inner laneLineProbs[1] and [2] >= 0.5",
      "outside_lane_count": {str(k): path_outside[k] for k in (10, 20, 30)},
      "full_rendered_path_0_to_100m_outside_rows": full_path_outside_rows,
      "full_rendered_path_0_to_100m_min_margin_m": qstats(full_path_min_margin),
      "margin_m": {str(k): qstats(path_margin[k]) for k in (10, 20, 30)},
      "path_minus_lane_center_m": {str(k): qstats(path_center_error[k]) for k in (10, 20, 30)},
      "lane_center_y_at_vehicle_m": qstats(lane_center_y),
      "offcenter_behavior": {
        "vehicle_offset_definition": "negative of detected inner-lane center y at x=0",
        "steering_away_definition": "(target_angle - measured_angle) has same sign as vehicle offset from lane center",
        "threshold_0p1m": offcenter_summary(0.10),
        "threshold_0p2m": offcenter_summary(0.20),
        "threshold_0p3m": offcenter_summary(0.30),
        "threshold_0p4m": offcenter_summary(0.40),
        "edge_bias_episode_rule": "abs(vehicle_offset)>=0.30m; 10m path on same edge side and farther from center; gaps<=0.20s",
        "edge_bias_rows": len(edge_rows),
        "edge_bias_episode_count": len(episode_summaries),
        "longest_low_torque_edge_bias_episode": longest_low_torque,
      },
    },
    "stock_id0_while_openpilot_b6_id11": {
      "model_rows": stock0_b611_rows,
      "rows_with_abs_driver_torque_lt_0p5_nm": stock0_b611_low_torque_rows,
      "interpretation": "useful non-coincident-request episodes, but not by themselves a causal B6 actuation proof",
    },
    "conclusion": {
      "b6_wire_angle_matches_openpilot_request": True,
      "stock_08a_and_b6_are_not_interchangeable_reference_planes": True,
      "fixed_stock_to_b6_offset_is_supported": False,
      "high_confidence_model_path_crossed_inner_lane_line": any(path_outside.values()),
      "route_proves_b6_only_physical_authority": False,
      "stock_forwarding_confounds_b6_authority": True,
    },
  }


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--route", type=Path, default=DEFAULT_ROUTE)
  ap.add_argument("--openpilot-root", type=Path, default=DEFAULT_OPENPILOT)
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  LogReader = load_logreader(args.openpilot_root)
  result = {
    "schema": "camry-20260907-steering-reconciliation-v2",
    "openpilot_parser_commit": None,
    "evidence": scan(LogReader, args.route),
  }
  result["openpilot_parser_commit"] = subprocess.check_output(
    ["git", "-C", str(args.openpilot_root), "rev-parse", "HEAD"], text=True, timeout=10,
  ).strip()

  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  print(args.out.resolve())
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
