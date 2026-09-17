#!/usr/bin/env python3
"""Bound the low-steering/higher-override split in the 2026 Camry TSS3 FRC path.

This reducer composes three evidence surfaces without pretending they are the
same thing:

* same-car September-6 EPS torque -> FRC 0x371 low-sensitivity driver-steering
  detector dynamics;
* a 12-route census showing that request-side 0x08A ID11->ID0 transitions are
  not a unique steering-override oracle; and
* Toyota diagnostic vocabulary separating driver steering detection / hands-on
  from steering override / LTA inhibition, including the P5 Low/High steering
  state dictionary.

The result deliberately does not assign a numeric high/override threshold.  It
identifies a plausible low-steering band and the experiment needed to recover
the upper boundary.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OPENPILOT = Path('/Users/kai/dev/inspect/repos/kai-openpilot')
DEFAULT_LOG_ROOT = Path('/Users/kai/dev/inspect/logs/camry-2026')
DEFAULT_CAP_ROOT = Path('/Users/kai/dev/inspect/captures')
DEFAULT_OUT = ROOT / 'data/generated/camry_2026_driver_steering_threshold_split.json'
HANDS_OFF_ART = ROOT / 'data/generated/camry_20260906_hands_off_warning_audit.json'
PCS_ART = ROOT / 'data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json'
P6_ART = ROOT / 'data/generated/gtsplus_2026/p5_adas_p6_migration.json'

ROUTES = {
  '1c': ('archive', '0000001c--574c06b528'),
  '27': ('archive', '00000027--885099a1d4'),
  '29': ('archive', '00000029--bae47e927f'),
  '2a': ('archive', '0000002a--c5647fd694'),
  '2c': ('archive', '0000002c--c784367b7e'),
  '2d': ('capture', '0000002d--4a4806c524'),
  '37': ('dated', '2026-09-01', '00000037--dec6fe39cb'),
  '3b': ('dated', '2026-09-04', '0000003b--62262eb7a1'),
  '3c': ('dated', '2026-09-04', '0000003c--97b9e7a69a'),
  '3d': ('dated', '2026-09-04', '0000003d--0e812cecba'),
  '3e': ('dated', '2026-09-06', '0000003e--1a2f20417d'),
  '3f': ('dated', '2026-09-06', '0000003f--36e72f5fdc'),
}

MAX_STATE_AGE_S = 0.2
MIN_SPEED_MS = 15.0


def segnum(path: Path) -> int:
  match = re.search(r'--(\d+)(?:/rlog|\.rlog|$)', str(path))
  if match:
    return int(match.group(1))
  match = re.search(r'rlog-(\d+)', path.name)
  return int(match.group(1)) if match else 0


def discover(route: tuple[str, ...], log_root: Path, cap_root: Path) -> list[Path]:
  if route[0] == 'archive':
    route_dir = log_root / 'archive' / route[1]
  elif route[0] == 'capture':
    route_dir = cap_root / route[1]
  else:
    route_dir = log_root / route[1] / route[2]
  files: set[Path] = set()
  for pattern in ('rlog-*.zst', '*.rlog.zst', '*/rlog.zst'):
    files.update(route_dir.glob(pattern))
  return sorted(files, key=segnum)


def signed8(value: int) -> int:
  return value - 256 if value & 0x80 else value


def signed4(value: int) -> int:
  value &= 0x0F
  return value - 16 if value & 0x08 else value


def decode_eps_torque(dat: bytes) -> float:
  return signed8(dat[8]) * 0.1 + signed4(dat[17]) * 0.01


def load_logreader(openpilot_root: Path):
  sys.path.insert(0, str(openpilot_root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def scan_request_withdrawals(LogReader, files: list[Path], route: str) -> list[dict[str, Any]]:
  rows: list[dict[str, Any]] = []
  latest_torque: float | None = None
  latest_torque_t = -1e99
  latest_371: bytes | None = None
  latest_371_t = -1e99
  latest_lane: tuple[float, float] | None = None
  latest_lane_t = -1e99
  cruise: bool | None = None
  v_ego: float | None = None
  blinker: bool | None = None
  carstate_t = -1e99
  previous_id: int | None = None
  previous_08a_t = -1e99

  for path in files:
    segment = segnum(path)
    for msg in LogReader(str(path), sort_by_time=True):
      t = msg.logMonoTime / 1e9
      which = msg.which()
      if which == 'carState':
        cs = msg.carState
        cruise = bool(cs.cruiseState.enabled)
        v_ego = float(cs.vEgo)
        blinker = bool(cs.leftBlinker or cs.rightBlinker)
        carstate_t = t
        continue
      if which == 'modelV2':
        if len(msg.modelV2.laneLineProbs) >= 3:
          latest_lane = (float(msg.modelV2.laneLineProbs[1]), float(msg.modelV2.laneLineProbs[2]))
          latest_lane_t = t
        continue
      if which != 'can':
        continue

      for frame in msg.can:
        dat = bytes(frame.dat)
        if frame.address == 0x030 and frame.src == 0 and len(dat) >= 18:
          latest_torque = decode_eps_torque(dat)
          latest_torque_t = t
          continue
        if frame.address == 0x371 and frame.src == 2 and len(dat) == 32:
          latest_371 = dat
          latest_371_t = t
          continue
        if frame.address != 0x08A or frame.src != 2 or len(dat) != 32:
          continue

        lateral_id = dat[21] & 0x3F
        cruise_latch = bool(dat[3] & 0x08)
        context_ok = (
          cruise is True and v_ego is not None and v_ego > MIN_SPEED_MS and blinker is False
          and 0 <= t - carstate_t <= MAX_STATE_AGE_S and cruise_latch
        )
        if context_ok and previous_id == 11 and lateral_id == 0 and 0 <= t - previous_08a_t <= MAX_STATE_AGE_S:
          torque = latest_torque if latest_torque is not None and 0 <= t - latest_torque_t <= MAX_STATE_AGE_S else None
          lane = latest_lane if latest_lane is not None and 0 <= t - latest_lane_t <= MAX_STATE_AGE_S else None
          frc_fresh = latest_371 is not None and 0 <= t - latest_371_t <= 0.3
          rows.append({
            'route': route,
            'segment': segment,
            't_mono_s': round(t, 6),
            'eps_torque_nm': None if torque is None else round(torque, 3),
            'abs_eps_torque_nm': None if torque is None else round(abs(torque), 3),
            'lane_line_probs': None if lane is None else [round(lane[0], 3), round(lane[1], 3)],
            'driver_detect_b20_bit4': None if not frc_fresh else bool(latest_371[20] & 0x10),
            'warning_b19_bit6': None if not frc_fresh else bool(latest_371[19] & 0x40),
            'request_target_raw': int.from_bytes(dat[18:20], 'big', signed=True),
            'request_b23': dat[23],
            'request_b24': dat[24],
          })
        if context_ok:
          previous_id = lateral_id
          previous_08a_t = t
        else:
          previous_id = None
          previous_08a_t = -1e99
  return rows


def extract_camry_ffd_semantics() -> dict[str, Any]:
  rows = json.loads(PCS_ART.read_text(encoding='utf-8'))['operation_ffd']['detail_rows']
  wanted: dict[str, list[str]] = {
    '560D': ['Driver Steering Control Detection Status', 'LTA Driver Steering Control prohibited'],
    '5774': ['Driver steering override'],
    '5776': ['Driver steering override for steering'],
    '550D': ['LDA Inhibition by Steering Override', 'LDA Warning Inhibition by Driver Steering'],
  }
  out: dict[str, Any] = {}
  for did, names in wanted.items():
    selected = [row for row in rows if row['DataID'].upper() == did and row['DataName'] in names]
    out[did] = [{
      'name': row['DataName'],
      'byte_position': row['BytePosition'],
      'bit_position': row['BitPosition'],
      'bit_length': row['BitLength'],
      'support_did': row['SupportDID'],
    } for row in selected]
  return out


def recursive_named_rows(obj: Any, names: set[str], out: list[dict[str, Any]]) -> None:
  if isinstance(obj, dict):
    if obj.get('name') in names:
      out.append(obj)
    for value in obj.values():
      recursive_named_rows(value, names, out)
  elif isinstance(obj, list):
    for value in obj:
      recursive_named_rows(value, names, out)


def extract_rob_discriminators() -> list[dict[str, Any]]:
  data = json.loads(PCS_ART.read_text(encoding='utf-8'))
  wanted = {
    '209D': 'LCS Steer Override',
    '2845': 'LTA Hands Free Cancel',
    '2846': 'CSF Hands Free Warning Operation',
    '229C': 'Late hands-on timing',
    '229F': 'End of hands-off control',
  }
  rows = []
  for row in data['rob_codes']['rows']:
    code = str(row['rob_code']).upper()
    if code not in wanted:
      continue
    if row['DataName'] != wanted[code]:
      raise RuntimeError(f"RoB {code} name drift: {row['DataName']!r}")
    rows.append({
      'rob_code': code,
      'name': row['DataName'],
      'system': row['SystemName'],
      'group': int(row['Group']),
      'sampling_s': float(row['Sampling']),
      'pre_trigger_samples': row['PreTriggerNumber'],
      'post_trigger_samples': row['PostTriggerNumber'],
    })
  if {row['rob_code'] for row in rows} != set(wanted):
    raise RuntimeError(f"missing steering/hands-off RoB discriminator(s): {rows!r}")
  return sorted(rows, key=lambda row: row['rob_code'])


def extract_p6_semantics() -> list[dict[str, Any]]:
  data = json.loads(P6_ART.read_text(encoding='utf-8'))
  rows: list[dict[str, Any]] = []
  recursive_named_rows(data, {'LTA Driver Hands-On Flag', 'LTA Inhibition By Steering Override'}, rows)
  # The migration artifact also contains higher-level summary dictionaries that
  # repeat the OEM names. Keep only concrete monitor rows with exact bit slices.
  concrete = [row for row in rows if isinstance(row.get('bit_start'), int) and isinstance(row.get('bit_end'), int)]
  unique: dict[tuple[Any, ...], dict[str, Any]] = {}
  for row in concrete:
    key = (row.get('source'), row.get('primary_did'), row.get('name'), row['bit_start'], row['bit_end'])
    unique[key] = {
      'source': row.get('source'),
      'primary_did': row.get('primary_did'),
      'name': row.get('name'),
      'bit_start': row['bit_start'],
      'bit_end': row['bit_end'],
      'pattern_display': row.get('signal_info', {}).get('pattern_display', {}),
    }
  return sorted(unique.values(), key=lambda row: (str(row['source']), int(str(row['primary_did'] or 0), 0), str(row['name'])))


def extract_low_high_vocabulary() -> dict[str, Any]:
  raw = subprocess.check_output(
    [str(ROOT / 'tools/gts'), 'did', 'ADS_Eth_P5', '0x1E0F', '--json'], cwd=ROOT, text=True,
  )
  rows = json.loads(raw)
  selected = [row for row in rows if row.get('name', '').startswith('Driver Steering Condition')]
  return {
    'database': 'ADS_Eth_P5.ddb',
    'did': '0x1E0F',
    'snapshot_count': len(selected),
    'snapshots': [{
      'name': row['name'],
      'bit_start': row['bit_start'],
      'bit_end': row['bit_end'],
      'pattern_display': row['signal_info']['pattern_display'],
    } for row in selected],
    'boundary': 'cross-system Toyota vocabulary only; the Low/High labels do not transfer numeric thresholds to the Camry FRC',
  }


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument('--openpilot-root', type=Path, default=DEFAULT_OPENPILOT)
  ap.add_argument('--log-root', type=Path, default=DEFAULT_LOG_ROOT)
  ap.add_argument('--capture-root', type=Path, default=DEFAULT_CAP_ROOT)
  ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  hands = json.loads(HANDS_OFF_ART.read_text(encoding='utf-8'))['routes']
  low_detector = {}
  for route in ('3e', '3f'):
    state = hands[route]['native_state_machine_candidate']
    low_detector[route] = {
      'set_abs_eps_torque_nm': state['driver_detect_set_abs_eps_torque_nm'],
      'release_abs_eps_torque_nm': state['driver_detect_release_abs_eps_torque_nm'],
      'fraction_0p75_to_1p0': state['driver_detect_by_abs_eps_torque_nm']['0.75-1'],
      'fraction_1p0_to_1p25': state['driver_detect_by_abs_eps_torque_nm']['1-1.25'],
    }

  LogReader = load_logreader(args.openpilot_root)
  withdrawals: list[dict[str, Any]] = []
  route_segment_counts = {}
  for route, spec in ROUTES.items():
    files = discover(spec, args.log_root, args.capture_root)
    route_segment_counts[route] = len(files)
    withdrawals.extend(scan_request_withdrawals(LogReader, files, route))

  high_lane = [row for row in withdrawals if row['lane_line_probs'] is not None and min(row['lane_line_probs']) >= 0.7]
  high_lane_torques = [row['abs_eps_torque_nm'] for row in high_lane if row['abs_eps_torque_nm'] is not None]

  payload = {
    'schema': 'camry-2026-driver-steering-threshold-split-v1',
    'same_car_low_sensitivity_detector': {
      'carrier': 'native FRC-side 0x371 B20[4]',
      'source_torque': 'exact-F33 EPS-origin 0x030 Steering Wheel Torque',
      'routes': low_detector,
      'interpretation': 'driver-steering/hands-on candidate with hysteretic set/release behavior; not the higher steering-override/prohibition state',
    },
    'toyota_semantic_split': {
      'camry_frc_operation_ffd': extract_camry_ffd_semantics(),
      'p6_successor': extract_p6_semantics(),
      'rob_discriminators': extract_rob_discriminators(),
      'p5_low_high_vocabulary': extract_low_high_vocabulary(),
      'interpretation': 'Toyota diagnostic vocabulary independently separates low/hands-on detection from higher steering override/inhibition',
    },
    'request_withdrawal_negative': {
      'routes_scanned': list(ROUTES),
      'segment_counts': route_segment_counts,
      'direct_id11_to_id0_count': len(withdrawals),
      'high_lane_count': len(high_lane),
      'high_lane_definition': 'both modelV2 inner-lane probabilities >= 0.7 within 200 ms at the direct ID11->ID0 edge',
      'high_lane_abs_torque_min_nm': None if not high_lane_torques else min(high_lane_torques),
      'high_lane_abs_torque_max_nm': None if not high_lane_torques else max(high_lane_torques),
      'events': withdrawals,
      'interpretation': '0x08A ID11->ID0 withdrawal is not a unique steering-override oracle: it occurs across low and higher torque and with the low-sensitivity detector both clear and asserted',
    },
    'bounded_conclusion': {
      'low_band_exists': 'supported structurally and dynamically',
      'candidate_experiment_band': 'roughly 0.75-1.0 N.m is already strongly associated with the low detector on both retained September-6 drives; this is not yet a qualified synthetic-torque value',
      'high_override_threshold': 'unrecovered',
      'next_discriminator': 'slow physical torque sweep with synchronized 0x030/0x371/0x08A/0x081/0x412 and FRC Operation-FFD 560D/5774/5776, followed only then by a one-shot ephemeral 0x030 substitution test',
      'production_boundary': 'do not add a periodic synthetic 0x030 keepalive until higher-threshold magnitude, dwell/hysteresis, sign behavior, and synthetic-vs-physical equivalence are measured',
    },
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
  print(args.out)
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
