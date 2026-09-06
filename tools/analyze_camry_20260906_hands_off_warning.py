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
  prev_id11_detect = None
  last_driver_detect_t = None
  last_driver_detect_release_t = None
  warning_falls_with_detect = 0
  warning_falls_detect_within_window = 0
  pending_warning_fall_t = None
  warning_episode = None
  warning_episodes: list[dict] = []

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
            continue
          if frame.address == 0x412 and len(dat) > 1:
            hud_payloads[dat.hex()] += 1
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
    "schema_version": 2,
    "method": {
      "touch_proxy": f"abs(carState.steeringTorque) >= {TOUCH_TORQUE_NM} N.m",
      "clean_stock_lta": f"carState cruise enabled, vEgo > {MIN_SPEED_MS} m/s, no blinker, latest native bus2 0x08A B21 low6 == 11",
      "warning_candidate": "native bus2 0x371 B19 bit6",
      "driver_steering_candidate": "native bus2 0x371 B20 bit4; B17 bit0 is its observed structural complement",
      "countdown_reset_candidate": "last native ID11 0x371 B20 bit4 driver-detect state; warning follows detector release at ~13 s",
      "exact_eps_torque": "native bus0 0x030 signed(B8)*0.1 + signed4(B17 low nibble)*0.01 N.m",
      "hud_companion_candidate": "native bus2 0x412 B0=0x14 and B1[3:2]=3",
      "hud_escalation_candidate": "native bus2 0x412 B2 bit6 while warning active",
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
