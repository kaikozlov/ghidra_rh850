#!/usr/bin/env python3
"""Reduce Camry highway rlogs for the native Toyota hands-off warning cycle.

The reducer is intentionally passive. It compares the three 2026-09-04 highway
routes (before the exact-F33 ``steeringPressed`` integration fix) with the
2026-09-06 Chicago outbound/return routes (after that fix).

The recovered wire observation is deliberately not assigned an OEM bit name:
while stock LTA is active, native bus-2 0x371 byte 19 switches into bit6 state
(typically 0x20 -> 0x40) after a long no-driver-torque interval and clears
immediately after renewed steering torque. In the same clean-LTA population,
0x371 B20[4] is strongly associated with exact-F33 0x030 physical driver torque
and B17[0] is its exact structural complement; this is retained as a dynamic
driver-steering detector candidate, not assigned a static OEM CAN-bit name. A
native 0x412 HUD-state transition (B0=0x14 with B1[3:2]=3) is paired to the
warning edges, with B2[6] providing a later ~6-second escalation stage. Current
Techstream Operation-FFD vocabulary independently contains Hands-Off Judgment,
Message, Buzzer Request, State, and Driver Steering Control Detection objects,
but no static DID-to-CAN-bit join is claimed here.

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

ROOT = Path(__file__).resolve().parents[4]
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
DRIVER_DETECT_FOLLOW_S = 0.35
TORQUE_BINS_NM = (
  (0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0),
  (1.0, 1.25), (1.25, 1.5), (1.5, 2.0), (2.0, 99.0),
)


def signed8(value: int) -> int:
  return value - 256 if value & 0x80 else value


def signed4(value: int) -> int:
  value &= 0x0F
  return value - 16 if value & 0x08 else value


def decode_eps_driver_torque(dat: bytes) -> float:
  return signed8(dat[8]) * 0.1 + signed4(dat[17]) * 0.01


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
  latest_eps_torque = None
  latest_eps_torque_t = None
  latest_lane_probs = None
  latest_lane_probs_t = None
  v_ego = 0.0
  cruise = False
  gas_pressed = False
  blinker = False
  left_blinker = False
  right_blinker = False
  last_moving_cs_t = None

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
  hud_intervals_ms: list[float] = []
  hud_change_intervals_ms: list[float] = []
  hud_lane_nibbles: Counter[tuple[int, int]] = Counter()
  hud_lane_model: dict[tuple[int, int], dict[str, float]] = {}
  hud_escalation_frames = 0
  hud_escalation_while_371_active = 0
  eligible_371_frames = 0
  source_counts: Counter[tuple[int, int]] = Counter()
  state_tuples: Counter[tuple[int, int, int]] = Counter()
  state_counts: Counter[str] = Counter()
  complement_violations = 0
  warning_driver_detect_overlap = 0
  torque_bin_total: Counter[str] = Counter()
  torque_bin_detect: Counter[str] = Counter()
  detect_set_torque: list[float] = []
  detect_release_torque: list[float] = []
  prev_detect = None
  prev_detect_t = None
  prev_detect_eligible = False
  driver_detect_samples: list[tuple[float, bool]] = []
  prev_id11_detect = None
  prev_lane_change_state = None
  lane_change_starts: list[dict] = []
  last_driver_detect_t = None
  last_driver_detect_release_t = None
  warning_falls_with_detect = 0
  warning_falls_detect_within_window = 0
  pending_warning_fall_t = None
  warning_episode = None
  warning_episodes: list[dict] = []
  cruise_substate_pairs: Counter[tuple[int, int]] = Counter()
  cruise_hold_episode = None
  cruise_hold_episodes: list[dict] = []

  for path in files:
    prev_hud_t = None
    prev_hud_dat = None
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
      elif which == "modelV2":
        if len(msg.modelV2.laneLineProbs) >= 3:
          latest_lane_probs = (float(msg.modelV2.laneLineProbs[1]), float(msg.modelV2.laneLineProbs[2]))
          latest_lane_probs_t = t
        lane_change_state = int(msg.modelV2.meta.laneChangeState.raw)
        lane_change_direction = int(msg.modelV2.meta.laneChangeDirection.raw)
        if lane_change_state == 2 and prev_lane_change_state != 2 and last_cs_t is not None and abs(t - last_cs_t) <= MAX_STATE_AGE_S:
          sign_match = ((lane_change_direction == 1 and steering_torque is not None and steering_torque > 0) or
                        (lane_change_direction == 2 and steering_torque is not None and steering_torque < 0))
          lane_change_starts.append({
            "direction": "left" if lane_change_direction == 1 else "right" if lane_change_direction == 2 else f"raw-{lane_change_direction}",
            "steering_torque_nm": steering_torque,
            "steering_pressed": steering_pressed,
            "left_blinker": left_blinker,
            "right_blinker": right_blinker,
            "sign_matches_direction": sign_match,
          })
        prev_lane_change_state = lane_change_state
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
        gas_pressed = bool(cs.gasPressed)
        if abs(v_ego) >= 0.1:
          last_moving_cs_t = t
        left_blinker = bool(cs.leftBlinker)
        right_blinker = bool(cs.rightBlinker)
        blinker = left_blinker or right_blinker
        steering_pressed = bool(cs.steeringPressed)
        steering_torque = float(cs.steeringTorque)
        if abs(steering_torque) >= TOUCH_TORQUE_NM:
          last_touch_t = t
        last_cs_t = t
        prev_cs_t = t
        prev_cs_eligible = cruise and v_ego > MIN_SPEED_MS and not blinker and latest_stock_id == 11
      elif which == "can":
        for frame in msg.can:
          dat = bytes(frame.dat)
          if frame.address in (0x030, 0x08A, 0x371, 0x412):
            source_counts[(frame.address, frame.src)] += 1
          if frame.address == 0x030 and frame.src == 0 and len(dat) >= 18:
            latest_eps_torque = decode_eps_driver_torque(dat)
            latest_eps_torque_t = t
          if frame.src != 2:
            continue
          if frame.address == 0x08A and len(dat) > 21:
            latest_stock_id = dat[21] & 0x3F
            if warning_episode is not None:
              warning_episode["target_lateral_ids"].add(latest_stock_id)

            # Same-car stock-ACC stop/hold state. B7 0x66/0x67 is distinct
            # from generic zero vehicle speed: it appears only after several
            # seconds stopped and clears with accelerator input before motion.
            # Keep B6/B7 pair counts as a falsification surface: B7 bit5 alone
            # is insufficient because the moving transition 0x47/0x65 exists.
            if dat[3] & 0x08 and last_cs_t is not None and 0 <= t - last_cs_t <= MAX_STATE_AGE_S:
              pair = (dat[6], dat[7])
              cruise_substate_pairs[pair] += 1
              hold = dat[7] in (0x66, 0x67)
              if hold:
                if cruise_hold_episode is None:
                  cruise_hold_episode = {
                    "start_s": t,
                    "end_s": t,
                    "frames": 0,
                    "gas_pressed_frames": 0,
                    "max_abs_speed_m_s": 0.0,
                    "state_pair_counts": Counter(),
                    "target_lateral_ids": set(),
                    "time_since_last_moving_at_start_s": None if last_moving_cs_t is None else t - last_moving_cs_t,
                  }
                cruise_hold_episode["end_s"] = t
                cruise_hold_episode["frames"] += 1
                cruise_hold_episode["gas_pressed_frames"] += int(gas_pressed)
                cruise_hold_episode["max_abs_speed_m_s"] = max(cruise_hold_episode["max_abs_speed_m_s"], abs(v_ego))
                cruise_hold_episode["state_pair_counts"][pair] += 1
                cruise_hold_episode["target_lateral_ids"].add(latest_stock_id)
              elif cruise_hold_episode is not None:
                cruise_hold_episode["duration_s"] = cruise_hold_episode["end_s"] - cruise_hold_episode["start_s"]
                cruise_hold_episode["clear_gas_pressed"] = gas_pressed
                cruise_hold_episode["clear_abs_speed_m_s"] = abs(v_ego)
                cruise_hold_episodes.append(cruise_hold_episode)
                cruise_hold_episode = None
            continue
          if frame.address == 0x412 and len(dat) > 3:
            hud_payloads[dat.hex()] += 1
            if prev_hud_t is not None and t > prev_hud_t:
              interval_ms = (t - prev_hud_t) * 1000
              hud_intervals_ms.append(interval_ms)
              if dat != prev_hud_dat:
                hud_change_intervals_ms.append(interval_ms)
            prev_hud_t = t
            prev_hud_dat = dat
            lane_key = (dat[3] >> 4, dat[3] & 0x0F)
            hud_lane_nibbles[lane_key] += 1
            if latest_lane_probs is not None and latest_lane_probs_t is not None and 0 <= t - latest_lane_probs_t <= MAX_STATE_AGE_S:
              row = hud_lane_model.setdefault(lane_key, {
                "frames": 0.0,
                "left_prob_sum": 0.0,
                "right_prob_sum": 0.0,
                "left_visible_gt_0_5": 0.0,
                "right_visible_gt_0_5": 0.0,
              })
              row["frames"] += 1
              row["left_prob_sum"] += latest_lane_probs[0]
              row["right_prob_sum"] += latest_lane_probs[1]
              row["left_visible_gt_0_5"] += float(latest_lane_probs[0] > 0.5)
              row["right_visible_gt_0_5"] += float(latest_lane_probs[1] > 0.5)
            if len(dat) > 2 and dat[2] & 0x40:
              hud_escalation_frames += 1
              hud_escalation_while_371_active += int(bool(prev_371))
              if warning_episode is not None:
                warning_episode["escalation_times"].append(t)
            state_412 = dat[0] == 0x14 and (dat[1] & 0x0C) == 0x0C
            if prev_412 is not None and state_412 != prev_412:
              (rises_412 if state_412 else falls_412).append(t)
            prev_412 = state_412
            continue
          if frame.address != 0x371 or len(dat) <= 19:
            continue

          state_371 = bool(dat[19] & 0x40)
          driver_detect = bool(dat[20] & 0x10)
          driver_detect_complement = bool(dat[17] & 0x01)
          if latest_stock_id == 11:
            if driver_detect:
              last_driver_detect_t = t
            if prev_id11_detect is True and not driver_detect:
              last_driver_detect_release_t = t
            prev_id11_detect = driver_detect
          else:
            prev_id11_detect = None
          eligible = (last_cs_t is not None and t - last_cs_t <= MAX_STATE_AGE_S and
                      cruise and v_ego > MIN_SPEED_MS and not blinker and latest_stock_id == 11)
          if eligible:
            eligible_371_frames += 1
            b19_values[dat[19]] += 1
            state_tuples[(dat[17] & 0x01, dat[19], dat[20])] += 1
            state_name = "warning" if state_371 else ("driver_steering_detected" if driver_detect else "no_touch")
            state_counts[state_name] += 1
            complement_violations += int(driver_detect_complement == driver_detect)
            warning_driver_detect_overlap += int(state_371 and driver_detect)

            if latest_eps_torque is not None and latest_eps_torque_t is not None and t - latest_eps_torque_t <= MAX_STATE_AGE_S:
              abs_torque = abs(latest_eps_torque)
              driver_detect_samples.append((abs_torque, driver_detect))
              for low, high in TORQUE_BINS_NM:
                if low <= abs_torque < high:
                  bin_label = f"{low:g}-{high:g}"
                  torque_bin_total[bin_label] += 1
                  torque_bin_detect[bin_label] += int(driver_detect)
                  break
              if (prev_detect is not None and prev_detect_eligible and prev_detect_t is not None and
                  0 <= t - prev_detect_t <= 0.5 and driver_detect != prev_detect):
                (detect_set_torque if driver_detect else detect_release_torque).append(abs_torque)

            if pending_warning_fall_t is not None and driver_detect and 0 <= t - pending_warning_fall_t <= DRIVER_DETECT_FOLLOW_S:
              warning_falls_detect_within_window += 1
              pending_warning_fall_t = None

          if prev_371 is not None and state_371 != prev_371:
            if state_371:
              if eligible:
                rises_371.append(t)
                warning_episode = {"start": t, "target_lateral_ids": {latest_stock_id}, "escalation_times": []}
                onset_rows.append({
                  "time_since_touch_s": None if last_touch_t is None else round(t - last_touch_t, 9),
                  "time_since_driver_detect_s": None if last_driver_detect_t is None else round(t - last_driver_detect_t, 9),
                  "time_since_driver_detect_release_s": None if last_driver_detect_release_t is None else round(t - last_driver_detect_release_t, 9),
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
              if eligible:
                warning_falls_with_detect += int(driver_detect)
                pending_warning_fall_t = None if driver_detect else t
              if warning_episode is not None:
                warning_episode["end"] = t
                warning_episode["end_driver_detect"] = driver_detect
                warning_episodes.append(warning_episode)
                warning_episode = None
          prev_371 = state_371
          prev_detect = driver_detect
          prev_detect_t = t
          prev_detect_eligible = eligible

  if cruise_hold_episode is not None:
    cruise_hold_episode["duration_s"] = cruise_hold_episode["end_s"] - cruise_hold_episode["start_s"]
    cruise_hold_episode["clear_gas_pressed"] = None
    cruise_hold_episode["clear_abs_speed_m_s"] = None
    cruise_hold_episodes.append(cruise_hold_episode)

  cruise_hold_episodes_out = []
  for episode in cruise_hold_episodes:
    row = dict(episode)
    row["start_s"] = round(row["start_s"], 6)
    row["end_s"] = round(row["end_s"], 6)
    row["duration_s"] = round(row["duration_s"], 6)
    row["max_abs_speed_m_s"] = round(row["max_abs_speed_m_s"], 9)
    if row["time_since_last_moving_at_start_s"] is not None:
      row["time_since_last_moving_at_start_s"] = round(row["time_since_last_moving_at_start_s"], 6)
    if row["clear_abs_speed_m_s"] is not None:
      row["clear_abs_speed_m_s"] = round(row["clear_abs_speed_m_s"], 9)
    row["state_pair_counts"] = {f"{a},{b}": n for (a, b), n in sorted(row["state_pair_counts"].items())}
    row["target_lateral_ids"] = sorted(row["target_lateral_ids"])
    cruise_hold_episodes_out.append(row)

  rise_lags = pair_lags(rises_371, rises_412)
  fall_lags = pair_lags(falls_371, falls_412)
  route_s = 0.0 if first_t is None or last_t is None else last_t - first_t
  onset_touch = [r["time_since_touch_s"] for r in onset_rows if r["time_since_touch_s"] is not None]
  onset_driver_detect = [r["time_since_driver_detect_s"] for r in onset_rows if r["time_since_driver_detect_s"] is not None and 0 <= r["time_since_driver_detect_s"] < 60]
  onset_driver_release = [r["time_since_driver_detect_release_s"] for r in onset_rows if r["time_since_driver_detect_release_s"] is not None and 0 <= r["time_since_driver_detect_release_s"] < 60]
  onset_torque = [abs(r["steering_torque_nm"]) for r in onset_rows if r["steering_torque_nm"] is not None]
  episode_durations = [e["end"] - e["start"] for e in warning_episodes if "end" in e]
  escalation_lags = [e["escalation_times"][0] - e["start"] for e in warning_episodes if e["escalation_times"]]
  escalation_episodes = [e for e in warning_episodes if e["escalation_times"]]
  hud_lane_model_out = {}
  for key, row in sorted(hud_lane_model.items()):
    frames = int(row["frames"])
    hud_lane_model_out[f"{key[0]},{key[1]}"] = {
      "frames": frames,
      "left_lane_prob_mean": round(row["left_prob_sum"] / frames, 6),
      "right_lane_prob_mean": round(row["right_prob_sum"] / frames, 6),
      "left_lane_visible_fraction_gt_0_5": round(row["left_visible_gt_0_5"] / frames, 6),
      "right_lane_visible_fraction_gt_0_5": round(row["right_visible_gt_0_5"] / frames, 6),
    }

  threshold_sweep = []
  for i in range(0, 201):
    threshold = i / 100
    tp = sum(value >= threshold and detected for value, detected in driver_detect_samples)
    tn = sum(value < threshold and not detected for value, detected in driver_detect_samples)
    fp = sum(value >= threshold and not detected for value, detected in driver_detect_samples)
    fn = sum(value < threshold and detected for value, detected in driver_detect_samples)
    tpr = tp / (tp + fn) if tp + fn else 0.0
    tnr = tn / (tn + fp) if tn + fp else 0.0
    threshold_sweep.append({
      "threshold_nm": round(threshold, 2),
      "classification_error": round((fp + fn) / len(driver_detect_samples), 9) if driver_detect_samples else None,
      "balanced_accuracy": round((tpr + tnr) / 2, 9),
      "true_positive_rate": round(tpr, 9),
      "true_negative_rate": round(tnr, 9),
      "false_positive": fp,
      "false_negative": fn,
    })
  best_threshold = max(threshold_sweep, key=lambda row: (row["balanced_accuracy"], -row["threshold_nm"])) if threshold_sweep else None
  best_min_error = min(threshold_sweep, key=lambda row: (row["classification_error"], row["threshold_nm"])) if threshold_sweep else None
  threshold_witnesses = {f"{threshold:.2f}": next(row for row in threshold_sweep if row["threshold_nm"] == threshold)
                         for threshold in (0.5, 0.6, 0.7, 0.8, 1.0, 1.2)} if threshold_sweep else {}

  torque_bins = {}
  for low, high in TORQUE_BINS_NM:
    bin_label = f"{low:g}-{high:g}"
    total = torque_bin_total[bin_label]
    torque_bins[bin_label] = {
      "frames": total,
      "driver_detect_frames": torque_bin_detect[bin_label],
      "driver_detect_fraction": round(torque_bin_detect[bin_label] / total, 9) if total else None,
    }

  return {
    "label": label,
    "route": route_dir.name,
    "segments": len(files),
    "openpilot_commit": commit,
    "route_duration_s": round(route_s, 6),
    "clean_stock_lta_duration_s": round(eligible_s, 6),
    "clean_stock_lta_371_frames": eligible_371_frames,
    "b19_values_in_clean_stock_lta": {f"0x{k:02X}": v for k, v in sorted(b19_values.items())},
    "native_source_counts": {f"0x{addr:03X}/src{src}": count for (addr, src), count in sorted(source_counts.items())},
    "stock_acc_standstill_candidate": {
      "wire_state": "native bus2 0x08A with CRUISE_OPERATING_LATCH=1 and CRUISE_SUBSTATE_2 in {102,103}",
      "cruise_substate_pair_counts": {f"{a},{b}": n for (a, b), n in sorted(cruise_substate_pairs.items())},
      "frames": sum(episode["frames"] for episode in cruise_hold_episodes_out),
      "episodes": cruise_hold_episodes_out,
      "all_frames_exactly_stopped": all(episode["max_abs_speed_m_s"] < 1e-6 for episode in cruise_hold_episodes_out),
      "all_episode_target_lateral_ids": sorted({lid for episode in cruise_hold_episodes_out for lid in episode["target_lateral_ids"]}),
      "boundary": "dynamic stock-ACC resume-required/hold interpretation: the state enters only after several seconds already stopped and all three retained episodes clear with accelerator input before motion; no RES-button clear join is established. B7 bit5 alone is explicitly rejected because moving 0x65 transition state exists",
    },
    "native_state_machine_candidate": {
      "driver_steering_candidate": "native bus2 0x371 B20 bit4",
      "structural_complement": "native bus2 0x371 B17 bit0",
      "exact_eps_torque_source": "native bus0 0x030: signed(B8)*0.1 + signed4(B17 low nibble)*0.01 N.m",
      "state_counts": dict(sorted(state_counts.items())),
      "state_tuples_b17lsb_b19_b20": {f"{b17},0x{b19:02X},0x{b20:02X}": n for (b17, b19, b20), n in sorted(state_tuples.items())},
      "b17lsb_equals_not_b20bit4_violations": complement_violations,
      "warning_and_driver_detect_overlap_frames": warning_driver_detect_overlap,
      "driver_detect_by_abs_eps_torque_nm": torque_bins,
      "driver_detect_set_abs_eps_torque_nm": quantiles(detect_set_torque),
      "driver_detect_release_abs_eps_torque_nm": quantiles(detect_release_torque),
      "single_threshold_fit": {
        "sample_count": len(driver_detect_samples),
        "best_balanced_accuracy": best_threshold,
        "best_minimum_classification_error": best_min_error,
        "selected_policy_threshold_nm": 0.6,
        "selected_threshold_witnesses": threshold_witnesses,
        "boundary": "classification against Toyota's slower hysteretic driver-detect state; intended to choose a simple upstream-style steeringPressed threshold, not to claim Toyota itself uses one static torque comparator",
      },
      "lane_change_starting_sign": {
        "count": len(lane_change_starts),
        "left": sum(row["direction"] == "left" for row in lane_change_starts),
        "right": sum(row["direction"] == "right" for row in lane_change_starts),
        "sign_matches_direction": sum(bool(row["sign_matches_direction"]) for row in lane_change_starts),
        "samples": lane_change_starts,
        "boundary": "post-fix openpilot DesireHelper transitions; validates the sign convention used by lane-change nudge logic on these routes",
      },
      "warning_onset_time_since_last_driver_detect_s": quantiles(onset_driver_detect),
      "warning_onset_time_since_driver_detect_release_s": quantiles(onset_driver_release),
      "warning_falls_with_driver_detect_same_frame": warning_falls_with_detect,
      "warning_falls_with_driver_detect_same_or_within_0_35s": warning_falls_with_detect + warning_falls_detect_within_window,
      "warning_episode_count": len(warning_episodes),
      "warning_episode_duration_s": quantiles(episode_durations),
      "escalation_episode_count": len(escalation_episodes),
      "first_escalation_lag_from_warning_s": quantiles(escalation_lags),
      "escalation_episode_target_lateral_ids": [sorted(e["target_lateral_ids"]) for e in escalation_episodes],
      "boundary": "dynamic state/timing join; B20[4] is a strong low-sensitivity driver-steering detector candidate, not a statically joined OEM bit name or exact torque threshold",
    },
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
      "native_timing": {
        "interval_count_same_segment": len(hud_intervals_ms),
        "interval_ms": quantiles(hud_intervals_ms),
        "interval_min_ms": round(min(hud_intervals_ms), 6) if hud_intervals_ms else None,
        "interval_max_ms": round(max(hud_intervals_ms), 6) if hud_intervals_ms else None,
        "payload_change_interval_count": len(hud_change_intervals_ms),
        "payload_change_interval_ms": quantiles(hud_change_intervals_ms),
        "payload_change_interval_min_ms": round(min(hud_change_intervals_ms), 6) if hud_change_intervals_ms else None,
        "stable_heartbeat_interpretation": "~1 Hz periodic heartbeat with bounded event-driven publications; no constant 5 Hz source cadence is observed",
      },
      "lane_nibble_counts_high_low": {f"{high},{low}": count for (high, low), count in sorted(hud_lane_nibbles.items())},
      "lane_nibble_model_join": hud_lane_model_out,
      "lane_state_boundary": (
        "same-car road data supports 1=recognized, 2=not-recognized/faded and 4=active-LTA recognized for the two B3 nibbles; "
        f"state value 3 appears in {sum(count for (high, low), count in hud_lane_nibbles.items() if high == 3 or low == 3)} frame(s) on this route and is not synthesized. "
        "The modelV2 join does not by itself prove which nibble is left versus right; a synchronized Toyota 5514 Left/Right Lane Display observation would close orientation."
      ),
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
    "schema_version": 6,
    "method": {
      "touch_proxy": f"abs(carState.steeringTorque) >= {TOUCH_TORQUE_NM} N.m",
      "clean_stock_lta": f"carState cruise enabled, vEgo > {MIN_SPEED_MS} m/s, no blinker, latest native bus2 0x08A B21 low6 == 11",
      "warning_candidate": "native bus2 0x371 B19 bit6",
      "driver_steering_candidate": "native bus2 0x371 B20 bit4; B17 bit0 is its observed structural complement",
      "countdown_reset_candidate": "last native ID11 0x371 B20 bit4 driver-detect state; warning follows detector release at ~13 s",
      "exact_eps_torque": "native bus0 0x030 signed(B8)*0.1 + signed4(B17 low nibble)*0.01 N.m",
      "hud_companion_candidate": "native bus2 0x412 B0=0x14 and B1[3:2]=3",
      "hud_escalation_candidate": "native bus2 0x412 B2 bit6 while warning active",
      "stock_acc_standstill_candidate": "native bus2 0x08A B7 in {0x66,0x67} while cruise latch is set; delayed zero-speed hold state, not generic vehicle standstill",
      "semantic_boundary": "dynamic timing/torque/state joins only; exact OEM CAN bit names and exact torque threshold remain unproved",
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
