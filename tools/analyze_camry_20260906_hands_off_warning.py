#!/usr/bin/env python3
"""Reduce Camry highway rlogs for the native Toyota hands-off warning cycle.

The reducer is intentionally passive. It compares the three 2026-09-04 highway
routes (before the exact-F33 ``steeringPressed`` integration fix) with the
2026-09-06 Chicago outbound/return routes (after that fix).

The recovered wire observation is deliberately not assigned an OEM bit name:
while stock LTA is active, native bus-2 0x371 byte 19 switches into bit6 state
(typically 0x20 -> 0x40) after a long no-driver-torque interval and clears
immediately after renewed steering torque. A native 0x412 HUD-state transition
(B0=0x14 with B1[3:2]=3) is paired to the same edges. Current Techstream
Operation-FFD vocabulary independently contains Hands-Off Judgment, Message,
Buzzer Request, and State objects, but no static CAN-bit join is claimed here.

Full regeneration requires the maintainer's local rlogs and a kai-openpilot
checkout providing LogReader.
"""
from __future__ import annotations

import argparse
import bisect
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_ROOT = Path("/Users/kai/dev/inspect/logs/camry-2026")
DEFAULT_OPENPILOT_ROOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
DEFAULT_OUT = ROOT / "data/generated/camry_20260906_hands_off_warning_audit.json"

ROUTES = {
  "3b": ("2026-09-04", "0000003b--62262eb7a1", "pre-fix"),
  "3c": ("2026-09-04", "0000003c--97b9e7a69a", "pre-fix"),
  "3d": ("2026-09-04", "0000003d--0e812cecba", "pre-fix"),
  "3e": ("2026-09-06", "0000003e--1a2f20417d", "post-fix-outbound"),
  "3f": ("2026-09-06", "0000003f--36e72f5fdc", "post-fix-return"),
}

TOUCH_TORQUE_NM = 0.9
MIN_SPEED_MS = 15.0
MAX_STATE_AGE_S = 0.2
PAIR_WINDOW_S = 2.0


def load_logreader(openpilot_root: Path):
  sys.path.insert(0, str(openpilot_root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def discover(route_dir: Path) -> list[Path]:
  flat = sorted(route_dir.glob("rlog-*.zst"), key=lambda p: int(p.stem.split("-")[1].split(".")[0]))
  if flat:
    return flat
  return sorted(route_dir.glob("*/rlog.zst"), key=lambda p: int(p.parent.name.rsplit("--", 1)[1]))


def quantiles(values: list[float]) -> dict[str, float] | None:
  if not values:
    return None
  vals = sorted(values)
  def q(frac: float) -> float:
    return vals[int((len(vals) - 1) * frac)]
  return {"p10": round(q(.1), 6), "p50": round(q(.5), 6), "p90": round(q(.9), 6)}


def pair_lags(source: list[float], target: list[float]) -> list[float]:
  out: list[float] = []
  for t in source:
    i = bisect.bisect_left(target, t)
    candidates = []
    if i < len(target):
      candidates.append(target[i] - t)
    if i:
      candidates.append(target[i - 1] - t)
    if candidates:
      lag = min(candidates, key=abs)
      if abs(lag) <= PAIR_WINDOW_S:
        out.append(lag)
  return out


def analyze_route(LogReader, route_dir: Path, label: str) -> dict:
  files = discover(route_dir)
  if not files:
    raise FileNotFoundError(route_dir)

  first_t = None
  last_t = None
  commit = None
  last_touch_t = None
  last_cs_t = None
  latest_stock_id = None
  latest_b6_id = None
  latest_b6_t = None
  lat_active = None
  selfdrive_enabled = None
  steering_pressed = None
  steering_torque = None
  v_ego = 0.0
  cruise = False
  blinker = False

  prev_cs_t = None
  prev_cs_eligible = False
  eligible_s = 0.0

  prev_371 = None
  prev_412 = None
  rises_371: list[float] = []
  falls_371: list[float] = []
  rises_412: list[float] = []
  falls_412: list[float] = []
  onset_rows: list[dict] = []
  fall_touch_age: list[float] = []
  b19_values: Counter[int] = Counter()
  hud_payloads: Counter[str] = Counter()
  hud_escalation_frames = 0
  hud_escalation_while_371_active = 0
  eligible_371_frames = 0

  for path in files:
    for msg in LogReader(str(path), sort_by_time=True):
      t = msg.logMonoTime / 1e9
      first_t = t if first_t is None else min(first_t, t)
      last_t = t if last_t is None else max(last_t, t)
      which = msg.which()

      if which == "initData" and commit is None:
        commit = msg.initData.gitCommit
      elif which == "carControl":
        lat_active = bool(msg.carControl.latActive)
      elif which == "selfdriveState":
        selfdrive_enabled = bool(msg.selfdriveState.enabled)
      elif which == "sendcan":
        for frame in msg.sendcan:
          if frame.address == 0x0B6 and len(frame.dat) >= 4:
            latest_b6_id = int(frame.dat[3]) & 0x3F
            latest_b6_t = t
      elif which == "carState":
        cs = msg.carState
        if prev_cs_t is not None and prev_cs_eligible:
          gap = t - prev_cs_t
          if 0 <= gap <= MAX_STATE_AGE_S:
            eligible_s += gap
        v_ego = float(cs.vEgo)
        cruise = bool(cs.cruiseState.enabled)
        blinker = bool(cs.leftBlinker or cs.rightBlinker)
        steering_pressed = bool(cs.steeringPressed)
        steering_torque = float(cs.steeringTorque)
        if abs(steering_torque) >= TOUCH_TORQUE_NM:
          last_touch_t = t
        last_cs_t = t
        prev_cs_t = t
        prev_cs_eligible = cruise and v_ego > MIN_SPEED_MS and not blinker and latest_stock_id == 11
      elif which == "can":
        for frame in msg.can:
          if frame.src != 2:
            continue
          dat = bytes(frame.dat)
          if frame.address == 0x08A and len(dat) > 21:
            latest_stock_id = dat[21] & 0x3F
            continue
          if frame.address == 0x412 and len(dat) > 1:
            hud_payloads[dat.hex()] += 1
            if len(dat) > 2 and dat[2] & 0x40:
              hud_escalation_frames += 1
              hud_escalation_while_371_active += int(bool(prev_371))
            state_412 = dat[0] == 0x14 and (dat[1] & 0x0C) == 0x0C
            if prev_412 is not None and state_412 != prev_412:
              (rises_412 if state_412 else falls_412).append(t)
            prev_412 = state_412
            continue
          if frame.address != 0x371 or len(dat) <= 19:
            continue

          state_371 = bool(dat[19] & 0x40)
          eligible = (last_cs_t is not None and t - last_cs_t <= MAX_STATE_AGE_S and
                      cruise and v_ego > MIN_SPEED_MS and not blinker and latest_stock_id == 11)
          if eligible:
            eligible_371_frames += 1
            b19_values[dat[19]] += 1

          if prev_371 is not None and state_371 != prev_371:
            if state_371:
              if eligible:
                rises_371.append(t)
                onset_rows.append({
                  "time_since_touch_s": None if last_touch_t is None else round(t - last_touch_t, 9),
                  "steering_torque_nm": steering_torque,
                  "steering_pressed": steering_pressed,
                  "lat_active": lat_active,
                  "selfdrive_enabled": selfdrive_enabled,
                  "latest_b6_target_lateral_id": latest_b6_id,
                  "latest_b6_age_s": None if latest_b6_t is None else round(t - latest_b6_t, 9),
                })
            else:
              falls_371.append(t)
              if last_touch_t is not None:
                fall_touch_age.append(t - last_touch_t)
          prev_371 = state_371

  rise_lags = pair_lags(rises_371, rises_412)
  fall_lags = pair_lags(falls_371, falls_412)
  route_s = 0.0 if first_t is None or last_t is None else last_t - first_t
  onset_touch = [r["time_since_touch_s"] for r in onset_rows if r["time_since_touch_s"] is not None]
  onset_torque = [abs(r["steering_torque_nm"]) for r in onset_rows if r["steering_torque_nm"] is not None]

  return {
    "label": label,
    "route": route_dir.name,
    "segments": len(files),
    "openpilot_commit": commit,
    "route_duration_s": round(route_s, 6),
    "clean_stock_lta_duration_s": round(eligible_s, 6),
    "clean_stock_lta_371_frames": eligible_371_frames,
    "b19_values_in_clean_stock_lta": {f"0x{k:02X}": v for k, v in sorted(b19_values.items())},
    "warning_candidate": {
      "carrier": "native Panda bus2 0x371/32 B19 bit6",
      "rising_edges": len(rises_371),
      "falling_edges": len(falls_371),
      "rate_per_route_hour": round(len(rises_371) / (route_s / 3600), 6) if route_s else None,
      "rate_per_clean_stock_lta_hour": round(len(rises_371) / (eligible_s / 3600), 6) if eligible_s else None,
      "onset_time_since_touch_s": quantiles(onset_touch),
      "onset_abs_torque_nm": quantiles(onset_torque),
      "fall_time_since_touch_s": quantiles(fall_touch_age),
      "onset_openpilot_state": {
        "lat_active_true": sum(r["lat_active"] is True for r in onset_rows),
        "selfdrive_enabled_true": sum(r["selfdrive_enabled"] is True for r in onset_rows),
        "steering_pressed_true": sum(r["steering_pressed"] is True for r in onset_rows),
        "b6_id11": sum(r["latest_b6_target_lateral_id"] == 11 for r in onset_rows),
        "max_latest_b6_age_s": round(max((r["latest_b6_age_s"] for r in onset_rows if r["latest_b6_age_s"] is not None), default=0.0), 9),
      },
    },
    "hud_companion_candidate": {
      "carrier": "native Panda bus2 0x412/8 B0=0x14 and B1[3:2]=3",
      "rising_edges": len(rises_412),
      "falling_edges": len(falls_412),
      "rise_edges_paired_to_0x371_within_2s": len(rise_lags),
      "fall_edges_paired_to_0x371_within_2s": len(fall_lags),
      "rise_lag_0x412_minus_0x371_s": quantiles(rise_lags),
      "fall_lag_0x412_minus_0x371_s": quantiles(fall_lags),
      "payload_counts": dict(sorted(hud_payloads.items())),
      "b2_bit6_frames": hud_escalation_frames,
      "b2_bit6_frames_while_0x371_active": hud_escalation_while_371_active,
      "boundary": "historical 0x412 signal names/layout are not transferred to this TSS3 payload",
    },
  }


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
  ap.add_argument("--openpilot-root", type=Path, default=DEFAULT_OPENPILOT_ROOT)
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()
  LogReader = load_logreader(args.openpilot_root)

  routes = {}
  for short, (day, route, label) in ROUTES.items():
    routes[short] = analyze_route(LogReader, args.log_root / day / route, label)

  payload = {
    "schema_version": 1,
    "method": {
      "touch_proxy": f"abs(carState.steeringTorque) >= {TOUCH_TORQUE_NM} N.m",
      "clean_stock_lta": f"carState cruise enabled, vEgo > {MIN_SPEED_MS} m/s, no blinker, latest native bus2 0x08A B21 low6 == 11",
      "warning_candidate": "native bus2 0x371 B19 bit6",
      "hud_companion_candidate": "native bus2 0x412 B0=0x14 and B1[3:2]=3",
      "semantic_boundary": "dynamic timing/edge join only; exact OEM CAN bit names remain unproved",
    },
    "routes": routes,
    "comparison": {
      "pre_fix_routes": ["3b", "3c", "3d"],
      "post_fix_outbound": "3e",
      "post_fix_return": "3f",
      "causality_boundary": "The post-fix warning onsets are observed before steeringPressed becomes true and while latActive and transmitted B6 ID11 remain active; this rules out the new steeringPressed event as the immediate trigger of the native warning onset, not every possible indirect vehicle-policy interaction.",
    },
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
  print(f"wrote {args.out}")
  for short, row in routes.items():
    w = row["warning_candidate"]
    print(short, "rises", w["rising_edges"], "clean-LTA/h", w["rate_per_clean_stock_lta_hour"], "onset p50", w["onset_time_since_touch_s"]["p50"])
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
