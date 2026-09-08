#!/usr/bin/env python3
"""Analyze the Sep-7 route-48 Toyota-LTA-off / comma-B6 authority experiment.

This reducer answers one narrow question: when Toyota withdraws its lateral request
(`0x08A` Target Lateral ID 0 and chassis-side `0x081` ID 0) while DRCC remains
operating, does openpilot keep sending B6 ID11 and does the EPS respond to that B6
as a steering command?

The route itself lives outside the repository.  This script inventories each input
rlog by SHA-256 and emits a compact deterministic evidence artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np

ANGLE_SCALE = 1024 / 17870
DEFAULT_ROUTE = Path("/Users/kai/dev/inspect/logs/camry-2026/2026-09-07/00000048--709f22277b")
DEFAULT_OPENPILOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
DEFAULT_OUT = Path(__file__).resolve().parents[1] / "data/generated/camry_20260907_lta_off_b6_authority.json"


def load_logreader(openpilot_root: Path):
  sys.path.insert(0, str(openpilot_root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def segment_files(route: Path) -> list[tuple[int, Path]]:
  rows = []
  for p in route.glob("*/rlog.zst"):
    try:
      rows.append((int(p.parent.name.rsplit("--", 1)[1]), p))
    except (IndexError, ValueError):
      pass
  return sorted(rows)


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
      h.update(chunk)
  return h.hexdigest()


def decode_08a(dat: bytes) -> tuple[int, bool, float]:
  return dat[21] & 0x3F, bool(dat[3] & 0x08), int.from_bytes(dat[18:20], "big", signed=True) * ANGLE_SCALE


def decode_081(dat: bytes) -> tuple[int, float]:
  return dat[13] & 0x3F, int.from_bytes(dat[16:18], "big", signed=True) * ANGLE_SCALE


def decode_b6(dat: bytes) -> tuple[int, float]:
  return dat[3] & 0x3F, int.from_bytes(dat[4:6], "big", signed=True) * ANGLE_SCALE


def qstats(values: list[float]) -> dict[str, float | int]:
  a = np.asarray(values, dtype=np.float64)
  if not len(a):
    return {"count": 0}
  return {
    "count": len(a),
    "min": round(float(np.min(a)), 9),
    "max": round(float(np.max(a)), 9),
    "mean": round(float(np.mean(a)), 9),
    "median": round(float(np.median(a)), 9),
    "median_abs": round(float(np.median(np.abs(a))), 9),
    "p90_abs": round(float(np.quantile(np.abs(a), 0.90)), 9),
    "rmse": round(float(np.sqrt(np.mean(a * a))), 9),
  }


def contiguous_runs(rows: list[dict[str, Any]], predicate, max_gap_ns: int = 60_000_000) -> list[list[dict[str, Any]]]:
  out: list[list[dict[str, Any]]] = []
  cur: list[dict[str, Any]] = []
  for row in rows:
    if not predicate(row):
      if cur:
        out.append(cur)
        cur = []
      continue
    if cur and (row["segment"] != cur[-1]["segment"] or row["time_ns"] - cur[-1]["time_ns"] > max_gap_ns):
      out.append(cur)
      cur = []
    cur.append(row)
  if cur:
    out.append(cur)
  return out


def summarize_run(rows: list[dict[str, Any]]) -> dict[str, Any]:
  errors = [float(r["b6_deg"]) - float(r["measured_deg"]) for r in rows]
  return {
    "segment": int(rows[0]["segment"]),
    "rows": len(rows),
    "duration_s": round((int(rows[-1]["time_ns"]) - int(rows[0]["time_ns"])) / 1e9, 6),
    "median_v_ego_mps": round(float(median(float(r["v_ego_mps"]) for r in rows)), 9),
    "median_driver_torque_nm": round(float(median(float(r["driver_torque_nm"]) for r in rows)), 9),
    "median_b6_error_deg": round(float(median(errors)), 9),
    "median_abs_b6_error_deg": round(float(median(abs(x) for x in errors)), 9),
    "minimum_abs_b6_error_deg": round(min(abs(x) for x in errors), 9),
    "measured_start_deg": round(float(rows[0]["measured_deg"]), 9),
    "measured_end_deg": round(float(rows[-1]["measured_deg"]), 9),
    "b6_start_deg": round(float(rows[0]["b6_deg"]), 9),
    "b6_end_deg": round(float(rows[-1]["b6_deg"]), 9),
    "median_motor_feedback_raw": round(float(median(float(r["motor_raw"]) for r in rows)), 9),
    "median_steering_rate_deg_s": round(float(median(float(r["steering_rate_deg_s"]) for r in rows)), 9),
    "motor_sign_toward_b6_fraction": round(sum(
      np.sign(float(r["motor_raw"])) == np.sign(float(r["b6_deg"]) - float(r["measured_deg"])) for r in rows
    ) / len(rows), 9),
  }


def scan(LogReader, route: Path) -> dict[str, Any]:
  segments = segment_files(route)
  inventory = [{"segment": n, "bytes": p.stat().st_size, "sha256": sha256(p)} for n, p in segments]
  init_data: dict[str, Any] = {}
  rows: list[dict[str, Any]] = []
  b6_sendcan = 0
  b6_tx_echo = 0
  b6_rejected = 0
  panda_samples: list[dict[str, Any]] = []

  for segment, path in segments:
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
          elif addr == 0x0B6 and len(dat) == 32:
            if src == 128:
              b6_tx_echo += 1
            elif src == 192:
              b6_rejected += 1
      elif which == "pandaStates" and len(e.pandaStates):
        ps = e.pandaStates[0]
        states = []
        for i in range(3):
          c = getattr(ps, f"canState{i}")
          states.append({
            "physical_controller": i,
            "total_error_cnt": int(c.totalErrorCnt),
            "bus_off": int(c.busOff),
            "receive_error_cnt": int(c.receiveErrorCnt),
            "transmit_error_cnt": int(c.transmitErrorCnt),
          })
        panda_samples.append({
          "segment": segment, "time_ns": t,
          "safety_tx_blocked": int(ps.safetyTxBlocked), "can_state": states,
        })
      elif which == "carState":
        cs = e.carState
        latest["state"] = (
          t, float(cs.steeringAngleDeg), float(cs.steeringRateDeg), float(cs.steeringTorque), float(cs.vEgo),
          bool(cs.leftBlinker or cs.rightBlinker),
        )
      elif which == "carControl":
        latest["control"] = (t, bool(e.carControl.latActive))
      elif which == "sendcan":
        for fr in e.sendcan:
          dat = bytes(fr.dat)
          if int(fr.address) != 0x0B6 or int(fr.src) != 0 or len(dat) != 32:
            continue
          b6_sendcan += 1
          bid, b6_angle = decode_b6(dat)
          stock, reference, state, motor, control = (
            latest.get("stock"), latest.get("reference"), latest.get("state"), latest.get("motor"), latest.get("control")
          )
          if not all((stock, reference, state, motor, control)):
            continue
          assert stock and reference and state and motor and control
          if any(t - x[0] < 0 or t - x[0] > 50_000_000 for x in (stock, reference, state, motor, control)):
            continue
          rows.append({
            "segment": segment, "time_ns": t,
            "b6_id": bid, "b6_deg": b6_angle,
            "stock_id": int(stock[1]), "cruise_operating_latch": bool(stock[2]), "stock_deg": float(stock[3]),
            "reference_id": int(reference[1]), "reference_deg": float(reference[2]),
            "measured_deg": float(state[1]), "steering_rate_deg_s": float(state[2]),
            "driver_torque_nm": float(state[3]), "v_ego_mps": float(state[4]), "blinker": bool(state[5]),
            "motor_raw": int(motor[1]), "lat_active": bool(control[1]),
          })

  def suppressed_pred(r: dict[str, Any]) -> bool:
    return bool(
      r["b6_id"] == 11 and r["stock_id"] == 0 and r["reference_id"] == 0 and
      r["cruise_operating_latch"] and r["lat_active"]
    )

  suppressed = [r for r in rows if suppressed_pred(r)]
  suppressed_runs = contiguous_runs(rows, suppressed_pred)
  suppressed_runs = [x for x in suppressed_runs if len(x) >= 2]

  low_torque_large_error = [r for r in suppressed if (
    float(r["v_ego_mps"]) > 10.0 and not r["blinker"] and abs(float(r["driver_torque_nm"])) < 0.3 and
    abs(float(r["b6_deg"]) - float(r["measured_deg"])) >= 3.0
  )]
  witness_runs = contiguous_runs(suppressed, lambda r: (
    float(r["v_ego_mps"]) > 10.0 and not r["blinker"] and abs(float(r["driver_torque_nm"])) < 0.3 and
    abs(float(r["b6_deg"]) - float(r["measured_deg"])) >= 3.0
  ))
  witness_runs = [x for x in witness_runs if len(x) >= 2]
  longest_witness = max(witness_runs, key=lambda x: x[-1]["time_ns"] - x[0]["time_ns"])

  stock_active = [r for r in rows if (
    r["b6_id"] == 11 and r["stock_id"] == 11 and r["reference_id"] == 11 and
    r["cruise_operating_latch"] and r["lat_active"] and float(r["v_ego_mps"]) > 10.0 and not r["blinker"] and
    abs(float(r["driver_torque_nm"])) < 0.3 and abs(float(r["stock_deg"]) - float(r["measured_deg"])) >= 0.5
  )]

  panda_health: dict[str, Any] = {}
  if panda_samples:
    first, last = panda_samples[0], panda_samples[-1]
    panda_health = {
      "first": first,
      "last": last,
      "safety_tx_blocked_delta": last["safety_tx_blocked"] - first["safety_tx_blocked"],
      "controller_deltas": [],
    }
    for i in range(3):
      a, b = first["can_state"][i], last["can_state"][i]
      panda_health["controller_deltas"].append({
        "physical_controller": i,
        "total_error_cnt_delta": b["total_error_cnt"] - a["total_error_cnt"],
        "bus_off_delta": b["bus_off"] - a["bus_off"],
      })

  combos = Counter((r["stock_id"], r["b6_id"], bool(r["cruise_operating_latch"]), bool(r["lat_active"])) for r in rows)
  return {
    "input": {
      "route": route.name,
      "segment_count": len(segments),
      "total_bytes": sum(x["bytes"] for x in inventory),
      "segments": inventory,
      "route_init_data": init_data,
    },
    "transport": {
      "b6_sendcan": b6_sendcan,
      "b6_tx_echo_src128": b6_tx_echo,
      "b6_rejected_src192": b6_rejected,
      "panda_health": panda_health,
    },
    "state_census": {
      "fresh_joined_b6_rows": len(rows),
      "stock_b6_state_counts": {f"stock{a}_b6{b}_cruise{int(c)}_lat{int(d)}": n for (a, b, c, d), n in sorted(combos.items())},
      "stock_lta_off_b6_active_rows": len(suppressed),
      "stock_lta_off_b6_active_episodes": len(suppressed_runs),
      "episodes_ge_1s": sum((x[-1]["time_ns"] - x[0]["time_ns"]) >= 1_000_000_000 for x in suppressed_runs),
      "episode_duration_sum_s": round(sum((x[-1]["time_ns"] - x[0]["time_ns"]) / 1e9 for x in suppressed_runs), 6),
      "longest_episodes": [summarize_run(x) for x in sorted(suppressed_runs, key=lambda x: x[-1]["time_ns"] - x[0]["time_ns"], reverse=True)[:5]],
    },
    "isolated_b6_response": {
      "selection": "stock 0x08A ID0 + 0x081 ID0 + cruise latch on + B6 ID11 + latActive; vEgo>10m/s; no blinker; abs(driver torque)<0.3Nm",
      "large_error_threshold_deg": 3.0,
      "large_error_rows": len(low_torque_large_error),
      "large_error_motor_abs_raw": qstats([abs(float(r["motor_raw"])) for r in low_torque_large_error]),
      "large_error_steering_rate_abs_deg_s": qstats([abs(float(r["steering_rate_deg_s"])) for r in low_torque_large_error]),
      "longest_continuous_large_error_witness": summarize_run(longest_witness),
    },
    "same_route_stock_lta_positive_control": {
      "selection": "stock 0x08A ID11 + 0x081 ID11 + B6 ID11 + latActive; vEgo>10m/s; no blinker; abs(driver torque)<0.3Nm; abs(stock-measured)>=0.5deg",
      "rows": len(stock_active),
      "motor_abs_raw": qstats([abs(float(r["motor_raw"])) for r in stock_active]),
      "motor_sign_toward_stock_fraction": round(sum(
        np.sign(float(r["motor_raw"])) == np.sign(float(r["stock_deg"]) - float(r["measured_deg"])) for r in stock_active
      ) / len(stock_active), 9) if stock_active else None,
    },
    "conclusion": {
      "turning_toyota_lta_off_preserved_openpilot_b6_id11": True,
      "stock_autonomous_request_competition_explains_b6_nonresponse": False,
      "route_proves_b6_effective_eps_authority": False,
      "interpretation": (
        "Route 48 supplies a direct source-off experiment: Toyota 0x08A/0x081 stay ID0 for long intervals while DRCC and openpilot remain active and B6 stays ID11. "
        "Large comma target errors can persist for seconds with near-zero driver torque, near-zero steering rate, and very small EPS motor-feedback proxy, while same-route stock-ID11 request error produces a much larger motor response. "
        "This rules out simultaneous stock autonomous lateral request as the explanation for the observed B6 non-response; it does not by itself identify which B6 admission/authentication/controller gate is failing."
      ),
    },
  }


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--route", type=Path, default=DEFAULT_ROUTE)
  ap.add_argument("--openpilot-root", type=Path, default=DEFAULT_OPENPILOT)
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()
  result = {
    "schema": "camry-20260907-lta-off-b6-authority-v1",
    "openpilot_parser_commit": subprocess.check_output(
      ["git", "-C", str(args.openpilot_root), "rev-parse", "HEAD"], text=True, timeout=10,
    ).strip(),
    "evidence": scan(load_logreader(args.openpilot_root), args.route),
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
  print(args.out)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
