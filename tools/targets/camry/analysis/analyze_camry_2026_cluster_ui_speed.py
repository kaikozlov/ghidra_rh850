#!/usr/bin/env python3
"""Map the exact-Camry vehicle-speed carriers to Toyota diagnostic semantics."""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

from tools import REPO_ROOT
from tools.toyota_support.toyota_route_opendbc_common import be_raw

REPO = REPO_ROOT
DEFAULT_LOG_ROOT = Path('/Users/kai/dev/inspect/logs/camry-2026')
DEFAULT_OPENPILOT_ROOT = Path('/Volumes/data/altdev/inspect/repos/kai-openpilot')
DEFAULT_ROUTE = '0000002c--c784367b7e'
HIGHWAY_ROUTES = (
  ('2026-09-06', '0000003e--1a2f20417d'),
  ('2026-09-06', '0000003f--36e72f5fdc'),
)
DEFAULT_OUT = REPO / 'data/generated/camry_2026_cluster_ui_speed.json'
KPH_TO_MPH = 0.62137119223733
SPEED_BINS_MPH = ((0, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80))


def load_logreader(openpilot_root: Path):
  sys.path.insert(0, str(openpilot_root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def wheel_speed_kph(dat: bytes) -> float:
  vals = [be_raw(dat, s, 15) * 0.01 - 67.67 for s in (6, 22, 38, 54)]
  return sum(vals) / 4


def quantile(values: list[float], frac: float) -> float:
  vals = sorted(values)
  return vals[int((len(vals) - 1) * frac)]


def discover(route_dir: Path) -> list[Path]:
  flat = sorted(route_dir.glob('*.rlog.zst'), key=lambda p: int(p.name.rsplit('--', 1)[1].split('.')[0]))
  if flat:
    return flat
  old_flat = sorted(route_dir.glob('rlog-*.zst'), key=lambda p: int(p.stem.split('-')[1].split('.')[0]))
  if old_flat:
    return old_flat
  nested = list(route_dir.glob('*--*/rlog.zst'))
  return sorted(nested, key=lambda p: int(p.parent.name.rsplit('--', 1)[1]))


def nearest(points, t: int, max_delta_ns: int, times: list[int] | None = None):
  if not points:
    return None
  if times is None:
    times = [x[0] for x in points]
  i = bisect.bisect_left(times, t)
  candidates = []
  if i < len(points):
    candidates.append(points[i])
  if i:
    candidates.append(points[i - 1])
  if not candidates:
    return None
  result = min(candidates, key=lambda x: abs(x[0] - t))
  return result if abs(result[0] - t) <= max_delta_ns else None


def summarize_errors(errors_kph: list[float]) -> dict:
  abs_errors = [abs(x) for x in errors_kph]
  return {
    'samples': len(errors_kph),
    'signed_error_kph': {
      'p05': round(quantile(errors_kph, .05), 6),
      'p50': round(quantile(errors_kph, .50), 6),
      'p95': round(quantile(errors_kph, .95), 6),
    },
    'absolute_error_kph': {
      'p50': round(quantile(abs_errors, .50), 6),
      'p95': round(quantile(abs_errors, .95), 6),
      'max': round(max(abs_errors), 6),
    },
  }


def analyze_legacy_route(LogReader, files: list[Path]) -> dict:
  frame_610 = 0
  frame_251 = 0
  errors_all: list[float] = []
  errors_moving: list[float] = []
  source_files = []

  for path in files:
    source_files.append({
      'name': path.name,
      'size': path.stat().st_size,
      'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    })
    wheels: list[tuple[int, float]] = []
    meter_integer: list[tuple[int, float]] = []
    for msg in LogReader(str(path), sort_by_time=True):
      if msg.which() != 'can':
        continue
      t = int(msg.logMonoTime)
      for frame in msg.can:
        dat = bytes(frame.dat)
        if frame.src == 0 and frame.address == 0x0AA and len(dat) == 8:
          wheels.append((t, wheel_speed_kph(dat)))
        elif frame.src == 0 and frame.address == 0x610 and len(dat) == 8:
          frame_610 += 1
          meter_integer.append((t, float(dat[2])))
        elif frame.src == 2 and frame.address == 0x251 and len(dat) == 8:
          frame_251 += 1

    for t, meter_kph in meter_integer:
      wheel = nearest(wheels, t, 100_000_000)
      if wheel is None:
        continue
      error = meter_kph - wheel[1]
      errors_all.append(error)
      if abs(wheel[1]) > 2.0:
        errors_moving.append(error)

  return {
    'route': DEFAULT_ROUTE,
    'segments': len(files),
    'native_counts': {'0x251_bus2': frame_251, '0x610_bus0': frame_610},
    'all_speed_join': summarize_errors(errors_all),
    'moving_over_2kph_join': summarize_errors(errors_moving),
    'source_files': source_files,
  }


def round_half_up(value: float) -> int:
  return math.floor(value + 0.5)


def summarize_bin(rows: list[tuple[float, float, float, float, float, bool, bool, bool]]) -> dict:
  # wheel_mph, sp1-wheel_mph, signal247-wheel_mph, meter-sp1_kph, meter-signal247_kph,
  # meter==ceil(wheel), meter==round(sp1), meter==ceil(signal247)
  return {
    'samples': len(rows),
    'sp1_minus_wheel_mph_p50': round(quantile([r[1] for r in rows], .5), 6),
    'signal247_minus_wheel_mph_p50': round(quantile([r[2] for r in rows], .5), 6),
    'meter_integer_minus_sp1_kph_p50': round(quantile([r[3] for r in rows], .5), 6),
    'meter_integer_minus_signal247_kph_p50': round(quantile([r[4] for r in rows], .5), 6),
    'meter_integer_equals_ceil_wheel_fraction': round(sum(r[5] for r in rows) / len(rows), 6),
    'meter_integer_equals_round_sp1_fraction': round(sum(r[6] for r in rows) / len(rows), 6),
    'meter_integer_equals_ceil_signal247_fraction': round(sum(r[7] for r in rows) / len(rows), 6),
  }


def linear_fit(points: list[tuple[float, float]]) -> dict:
  n = len(points)
  sx = sum(x for x, _ in points)
  sy = sum(y for _, y in points)
  sxx = sum(x * x for x, _ in points)
  sxy = sum(x * y for x, y in points)
  slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
  intercept = (sy - slope * sx) / n
  ratios = [y / x for x, y in points if x != 0]
  return {
    'samples': n,
    'slope': round(slope, 9),
    'intercept_kph': round(intercept, 6),
    'ratio_p50': round(quantile(ratios, .5), 9),
    'ratio_p10': round(quantile(ratios, .1), 9),
    'ratio_p90': round(quantile(ratios, .9), 9),
  }


def analyze_highway_route(LogReader, route: str, files: list[Path]) -> dict:
  rows: list[tuple[float, float, float, float, float, bool, bool, bool]] = []
  d7_pairs: list[tuple[float, float]] = []
  frc_diffs: list[float] = []
  byte_stats: dict[tuple[int, int, int], list[float]] = {}
  counts = {'0x0AA_bus0': 0, '0x0D7_bus0': 0, '0x610_bus0': 0, '0x1B2_bus2': 0}

  for path in files:
    wheels: list[tuple[int, float]] = []
    d7: list[tuple[int, float, float]] = []
    meter_integer: list[tuple[int, float]] = []
    frc_integer: list[tuple[int, float]] = []
    last_sp1: tuple[int, float] | None = None
    for msg in LogReader(str(path), sort_by_time=True):
      if msg.which() != 'can':
        continue
      t = int(msg.logMonoTime)
      frames = list(msg.can)
      for frame in frames:
        dat = bytes(frame.dat)
        if frame.src == 0 and frame.address == 0x0D7 and len(dat) == 32:
          last_sp1 = (t, int.from_bytes(dat[1:3], 'big') * 0.01)
      for frame in frames:
        dat = bytes(frame.dat)
        if frame.src == 2 and frame.address == 0x1B2 and len(dat) == 32:
          counts['0x1B2_bus2'] += 1
          frc_integer.append((t, float(dat[2])))
          continue
        if frame.src != 0:
          continue
        if frame.address == 0x0AA and len(dat) == 8:
          counts['0x0AA_bus0'] += 1
          wheels.append((t, wheel_speed_kph(dat)))
        elif frame.address == 0x0D7 and len(dat) == 32:
          counts['0x0D7_bus0'] += 1
          d7.append((t, int.from_bytes(dat[1:3], 'big') * 0.01, int.from_bytes(dat[3:5], 'big') * 0.01))
        elif frame.address == 0x610 and len(dat) == 8:
          counts['0x610_bus0'] += 1
          meter_integer.append((t, float(dat[2])))

        if last_sp1 is not None and t - last_sp1[0] <= 100_000_000 and 20 <= last_sp1[1] <= 130:
          target = round_half_up(last_sp1[1])
          for pos, value in enumerate(dat):
            key = (int(frame.address), len(dat), pos)
            stat = byte_stats.setdefault(key, [0.0, 0.0, 255.0, 0.0])
            stat[0] += 1
            stat[1] += abs(value - target)
            stat[2] = min(stat[2], value)
            stat[3] = max(stat[3], value)

    d7_pairs.extend((signal247_kph, sp1_kph) for _, sp1_kph, signal247_kph in d7 if 30 <= signal247_kph <= 150)
    meter_times = [x[0] for x in meter_integer]
    for t, value in frc_integer:
      meter = nearest(meter_integer, t, 1_000_000_000, meter_times)
      if meter is not None:
        frc_diffs.append(value - meter[1])
    wheel_times = [x[0] for x in wheels]
    d7_values = [(dt, (sp1_kph, signal247_kph)) for dt, sp1_kph, signal247_kph in d7]
    d7_times = [x[0] for x in d7_values]
    for t, meter_kph in meter_integer:
      wheel = nearest(wheels, t, 100_000_000, wheel_times)
      d7_value = nearest(d7_values, t, 100_000_000, d7_times)
      if wheel is None or d7_value is None:
        continue
      wheel_kph = wheel[1]
      sp1_kph, signal247_kph = d7_value[1]
      if not 0 <= wheel_kph * KPH_TO_MPH < 80:
        continue
      rows.append((
        wheel_kph * KPH_TO_MPH,
        (sp1_kph - wheel_kph) * KPH_TO_MPH,
        (signal247_kph - wheel_kph) * KPH_TO_MPH,
        meter_kph - sp1_kph,
        meter_kph - signal247_kph,
        meter_kph == math.ceil(wheel_kph - 1e-9),
        meter_kph == round_half_up(sp1_kph),
        meter_kph == math.ceil(signal247_kph - 1e-9),
      ))

  bins = {}
  for low, high in SPEED_BINS_MPH:
    selected = [r for r in rows if low <= r[0] < high]
    if selected:
      bins[f'{low}-{high}'] = summarize_bin(selected)
  highway = [r for r in rows if 60 <= r[0] < 80]
  byte_census = []
  for (addr, length, pos), (samples, error_sum, low, high) in byte_stats.items():
    if samples < 1000 or high - low < 10:
      continue
    byte_census.append({
      'wire': f'0x{addr:03X}/{length} B{pos}',
      'samples': int(samples),
      'range': [int(low), int(high)],
      'mae_to_round_sp1': round(error_sum / samples, 6),
    })
  byte_census.sort(key=lambda x: x['mae_to_round_sp1'])
  return {
    'route': route,
    'segments': len(files),
    'native_counts': counts,
    'joined_samples': len(rows),
    'sp1_vs_signal247': linear_fit(d7_pairs),
    'bins_mph': bins,
    'highway_60_80_mph': summarize_bin(highway),
    'frc_integer_mirror': {
      'samples': len(frc_diffs),
      'exact_fraction': round(sum(x == 0 for x in frc_diffs) / len(frc_diffs), 6),
      'difference_p10': quantile(frc_diffs, .1),
      'difference_p50': quantile(frc_diffs, .5),
      'difference_p90': quantile(frc_diffs, .9),
    },
    'bus0_byte_census_vs_round_sp1': byte_census[:10],
  }


def gts_json(*args: str) -> dict | list:
  return json.loads(subprocess.check_output([str(REPO / 'tools/gts'), *args, '--json'], cwd=REPO, text=True))


def decomp_function(name: str) -> dict:
  corpus = REPO / 'data/generated/camry-8965F3307000/decompilations.jsonl'
  needle = f'"name":"{name}"'
  with corpus.open() as f:
    for line in f:
      if needle in line:
        return json.loads(line)
  raise KeyError(name)


def did_summary(ecu: str, did: str, expected_name: str) -> dict:
  rows = gts_json('did', ecu, did)
  matches = [r for r in rows if r.get('name') == expected_name]
  if len(matches) != 1:
    raise ValueError(f'{ecu} {did} {expected_name}: expected one row, got {len(matches)}')
  row = matches[0]
  info = row['signal_info']
  return {
    'ecu': ecu,
    'did': f"0x{row['primary_did']:04X}",
    'name': row['name'],
    'bit_start': row['bit_start'],
    'bit_end': row['bit_end'],
    'bit_width': info['bit_width'],
    'signed': info['signed'],
    'mul': info['mul'],
    'div': info['div'],
    'offset': info['offset'],
    'unit': info['unit'],
    'data_range': info['data_range'],
    'decimal_point_count': info['decimal_point_count'],
  }


def active_test_summary(active_test_id: int) -> dict:
  d = gts_json('active-test', 'Meter_P5', str(active_test_id))
  test = d['selected_test']
  executor = d['executor']
  examples = executor['minimum_length_examples']
  return {
    'active_test_id': active_test_id,
    'name': test['name'],
    'did': executor['data_id_for_act']['did_hex'],
    'bit_start': test['bit_start'],
    'bit_end': test['bit_end'],
    'start_examples': examples['start'],
    'return_control_examples': examples['stop'],
  }


def find_meter_route(registry: dict) -> dict:
  candidates = registry['profile']['vehicle_resolution']['mount']['candidates']
  matches = [x for x in candidates if x.get('category_id') == 409 and x.get('database') == 'Meter_P5.ddb']
  if len(matches) != 1:
    raise ValueError(f'expected one current Combination Meter route, got {len(matches)}')
  row = matches[0]
  route = row['transport_route']
  return {
    'category_id': row['category_id'],
    'name': row['name'],
    'database': row['database'],
    'generation': row['generation'],
    'route_selector': row['connection_route_selector'],
    'request_address': route['request_address'],
    'request_address_hex': f"0x{route['request_address']:03X}",
    'response_mask': route['response_mask'],
    'protocol_info_id': route['protocol_info_id'],
  }


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument('--log-root', type=Path, default=DEFAULT_LOG_ROOT)
  ap.add_argument('--openpilot-root', type=Path, default=DEFAULT_OPENPILOT_ROOT)
  ap.add_argument('--route', default=DEFAULT_ROUTE)
  ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  LogReader = load_logreader(args.openpilot_root)
  route_dir = args.log_root / 'archive' / args.route
  files = discover(route_dir)
  if not files:
    raise FileNotFoundError(route_dir)
  baseline = analyze_legacy_route(LogReader, files)

  highway = []
  for date, route in HIGHWAY_ROUTES:
    route_files = discover(args.log_root / date / route)
    if not route_files:
      raise FileNotFoundError(args.log_root / date / route)
    highway.append(analyze_highway_route(LogReader, route, route_files))

  command_cone = json.loads((REPO / 'data/generated/camry_8965F3307000_command_cone_ingress.json').read_text())
  d7_geometry = command_cone['positive_non_b6_cluster_inputs'][1]['geometry']
  signal246, = [g for g in d7_geometry if g['signal'] == 246]
  signal247, = [g for g in d7_geometry if g['signal'] == 247]
  did_1185 = decomp_function('did_1185_can_vehicle_speed_sp1')
  d7_unpacker = decomp_function('decode_changed_rx17_two_words_and_flags_4bb62')
  did_1185_reads = {r['to_addr'] for r in did_1185['data_references'] if r['ref_type'] == 'READ'}
  d7_destinations = {r['to_addr'] for r in d7_unpacker['data_references'] if r['ref_type'] == 'DATA'}
  if '0xfebe809a' not in did_1185_reads or not {'0xfebe809a', '0xfebe809c'} <= d7_destinations:
    raise ValueError('tracked exact-F33 SP1 dataflow no longer matches the speed-carrier model')

  registry = gts_json('registry', 'camry-2026-f33')
  payload = {
    'schema_version': 2,
    **baseline,
    'carrier_map': {
      'wheel_reference': {
        'wire': '0x0AA FL/FR/RL/RR wheel-speed fields',
        'decode': 'four 15-bit 0.01 km/h channels with -67.67 km/h offset; arithmetic mean is the analysis reference',
      },
      'sp1': {
        'wire': '0x0D7 B1:B2 big-endian unsigned 16-bit',
        'scale': '0.01 km/h/count',
        'exact_f33_signal_id': signal246['signal'],
        'exact_f33_ram': 'FEBE809A',
        'exact_f33_did_callback': did_1185['entry_addr'],
        'exact_f33_did_callback_sha256': did_1185['decompiled_c_sha256'],
        'exact_f33_unpacker': d7_unpacker['entry_addr'],
        'exact_f33_unpacker_sha256': d7_unpacker['decompiled_c_sha256'],
        'gts': did_summary('EMPS_P5', '0x1185', 'CAN Vehicle Speed (SP1)'),
        'evidence': 'direct OEM join: exact F33 DID 0x1185 reads FEBE809A and exact F33 0x0D7 signal246 writes FEBE809A',
      },
      'd7_signal247': {
        'wire': '0x0D7 B3:B4 big-endian unsigned 16-bit',
        'scale': '0.01 km/h/count',
        'exact_f33_signal_id': signal247['signal'],
        'exact_f33_ram': 'FEBE809C -> FEBEF1B8 -> FEBEAED6',
        'evidence': 'exact F33 wire geometry and dataflow; no diagnostic DID or runtime consumer recovered after the foreground snapshot',
        'oem_name': None,
      },
      'meter_integer': {
        'wire': '0x610 B2 unsigned 8-bit',
        'scale': '1 km/h/count',
        'gts_candidates': [
          did_summary('Meter_P5', '0x1041', 'Vehicle Speed Meter'),
          did_summary('Meter_P5', '0x1081', 'Vehicle Speed Meter'),
        ],
        'evidence': (
          'strong semantic join: among every native bus0 byte on the complete route3e highway capture, 0x610 B2 is the unique '
          'field matching the Toyota Vehicle Speed Meter 8-bit/1-km/h geometry; with 0x610 timestamps as the anchor, high-speed '
          'captures match nearest-integer SP1 in about nine-tenths of samples'
        ),
        'direct_live_meter_did_read': False,
      },
      'frc_integer_mirror': {
        'wire': '0x1B2 B2 unsigned 8-bit',
        'scale': '1 km/h/count',
        'evidence': 'FRC-side publication closely mirrors 0x610 B2; no OEM field-level name is assigned',
        'oem_name': None,
      },
    },
    'gts_meter': {
      'transport': find_meter_route(registry),
      'speedometer_operation_40': active_test_summary(200),
      'speed_signal_input_40': active_test_summary(301),
      'interpretation': (
        'Toyota exposes separate Combination Meter active-test stages named Speedometer Operation and Speed Signal Input; '
        'Speed Signal Input is an active-test/status surface, not a second passive numeric speed DID.'
      ),
      'retained_meter_endpoint_traffic': 'none found on 0x7C0 in the retained Camry rlogs; no live 0x1041/0x1081 meter read is available',
    },
    'highway_routes': highway,
    'semantic_boundary': (
      'Exact F33 directly binds 0x0D7 B1:B2 to Toyota CAN Vehicle Speed (SP1). SP1 runs about 0.5% above the wheel-equivalent '
      '0x0D7 signal247 on highway captures, and 0x610 B2 most closely matches SP1 rounded to the nearest whole km/h. 0x610 B2 is '
      'also the unique whole-km/h bus0 carrier matching Meter_P5 Vehicle Speed Meter geometry, but the '
      'retained logs contain no Combination Meter 0x7C0 diagnostic read to make that second join direct. The physical dashboard '
      'number is not logged, so its additional 1-2 mph optimism remains downstream of the recovered whole-km/h carrier or otherwise internal to the meter.'
    ),
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
  print(args.out)
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
