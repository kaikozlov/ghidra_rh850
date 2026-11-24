"""Replay Camry 0x08A B22[2] in stationary trials or the full road manifest."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from itertools import pairwise
from pathlib import Path

from tools import REPO_ROOT
from tools.targets.camry.analysis.extract_camry_20260930_vmc_corpus import sha256_file
from tools.targets.camry.analysis.analyze_camry_2026_bus1_camera_output import decode_object_geometry, decode_object_relative_speed
from tools.targets.camry.support import camry_f33_corpus as f33
from tools.toyota_support.route_log import load_logreader

# Native request bus changes across the August 27 harness repin.
_CAPTURES = (
  ('raw-20260826/camry_nrtd_cruise_can_sync_20260826.json.gz', 1, '083435105745d928ceea5dea2a614b7a1fbd32341ba4c94987c73ef6287e87fa'),
  ('raw-20260826/camry_ready_gear_20260826.json.gz', 1, '379ec28fba65191d2898ebb156fe83e2e8e59c38bbf5fcfb7166ec9ff32c3889'),
  ('raw-20260826/camry_ready_b_20260826.json.gz', 1, '7bae994dea1caff06d8f31f58558f67d646da38bd9531557875858eb33fa4db3'),
  ('raw-20260827/camry_post_repin_nrtd_20260827.json.gz', 2, '4e061d5ec06b0dee0b208e7bc34d5f8050af565978ef3254ce221ad329b4f74d'),
  ('raw-20260827/camry_post_repin_ready_20260827.json.gz', 2, '32e9ac52c53ac05248b45c2f0eb6a6d50c59c11a9db4fafb31e145919078a58d'),
)
_GEARS = {0: 'P', 1: 'R', 2: 'N', 3: 'D', 4: 'B'}
_LENGTH = {0x081: 32, 0x08A: 32, 0x0AA: 8, 0x101: 8, 0x116: 8, 0x127: 8,
           0x3B7: 8, 0x51E: 8, 0x5AE: 32, 0x620: 8}


def _wheels_at_zero(data):
  return data == b'\x1a\x6f' * 4


def _trial_frames(relative, pin):
  blob = (f33.CAPTURE / relative).read_bytes()
  if hashlib.sha256(blob).hexdigest() != pin:
    raise ValueError(f'wrong capture: {relative}')
  return json.loads(gzip.decompress(blob))['frames']


def _pcs_lateral_code(data):
  return ((data[6] >> 3) ^ 16) - 16


def _trial(relative, bus, pin):
  streams = defaultdict(list)
  for row in _trial_frames(relative, pin):
    addr = row['addr']
    if row['bus'] == bus and _LENGTH.get(addr) == row['len']:
      streams[addr].append((row['t'], bytes.fromhex(row['data'])))
  times = {}
  for addr, rows in streams.items():
    rows.sort(key=lambda pair: pair[0])  # Preserve receive order within USB batches.
    times[addr] = [t for t, _ in rows]

  def prior(addr, t, max_age):
    i = bisect_right(times[addr], t) - 1
    if i >= 0 and t - times[addr][i] <= max_age:
      return streams[addr][i][1]
    return None

  request = streams[0x08A]
  high = [(t, d) for t, d in request if d[22] & 4]
  by_gear = Counter()
  gates = defaultdict(Counter)
  for t, _ in high:
    gear = prior(0x127, t, .12)
    by_gear['unobserved' if gear is None else _GEARS[gear[5] >> 4]] += 1
    for field, addr, age, decode in _GATES:
      d = prior(addr, t, age)
      gates[field]['unobserved' if d is None else str(int(decode(d)))] += 1

  changes = [(int(bool(d[22] & 4)), (d[26] - before[26]) % 64, d[26] % 2)
             for (_, before), (_, d) in pairwise(request) if (before[22] ^ d[22]) & 4]
  # Sample at the 5 Hz companion publication. Do not repeat one HUD reading
  # across multiple 20 Hz decisions; ignore the initial buffered receive burst.
  confusion = Counter()
  boundary = defaultdict(Counter)
  prev = None
  for t, hud in streams[0x5AE]:
    if t < 1:
      continue
    d = prior(0x08A, t, .050)
    w = prior(0x0AA, t, .075)
    if d is None or w is None or not _wheels_at_zero(w):
      prev = None
      continue
    state = int(bool(d[22] & 4))
    lateral = _pcs_lateral_code(hud)
    confusion[state, lateral == 2] += 1
    if 0 < (hud[4] & 127) <= 3:
      if prev is not None:
        prev_t, prev_lat, prev_state = prev
        if .125 < t - prev_t < .275 and abs(prev_lat - lateral) == 1 and {abs(prev_lat), abs(lateral)} == {2, 3}:
          boundary['inward' if abs(lateral) == 2 else 'outward'][f'{prev_state}_to_{state}'] += 1
      prev = t, lateral, state
    else:
      prev = None
  return {
    'capture': relative, 'sha256': pin, 'native_bus': bus, 'frames': len(request),
    'highs': len(high), 'highs_by_selector': dict(sorted(by_gear.items())),
    'highs_by_independent_report': gates,
    'rises': sum(v for v, _, _ in changes), 'falls': sum(not v for v, _, _ in changes),
    'contiguous_edge_counts_by_sequence_parity': [sum(step == 1 and phase == p for _, step, phase in changes) for p in (0, 1)],
    'edges_across_missing_publications': sum(step != 1 for _, step, _ in changes),
    'pcs_close_lateral_bin_crossings': boundary,
    'pcs_lateral_code_eq_2': {key: confusion[actual, predicted] for key, actual, predicted in
                        [('true_high', 1, 1), ('missed_high', 1, 0), ('false_high', 0, 1), ('true_low', 0, 0)]},
  }


_GATES = (
  ('ready', 0x51E, 1.2, lambda d: d[0] >> 7),
  ('all_four_wheels_raw_zero', 0x0AA, .1, _wheels_at_zero),
  ('door_open', 0x620, .6, lambda d: bool(d[5] & 0x3C)),
  ('epb', 0x620, .6, lambda d: d[7] >> 4 & 1),
  ('foot_brake', 0x101, .1, lambda d: d[0] >> 3 & 1),
  ('accelerator_raw', 0x116, .1, lambda d: d[1]),
  ('brake_hold', 0x3B7, .4, lambda d: d[4] >> 4 & 1),
  ('vmc_result_id', 0x081, .1, lambda d: d[6] & 63),
)


def _streams(path, sizes, reader):
  streams = defaultdict(list)
  for event in reader(str(path), only_union_types=True):
    if event.which() != 'can':
      continue
    for f in event.can:
      if sizes.get((f.src, f.address)) == len(f.dat):
        streams[f.address].append((event.logMonoTime, bytes(f.dat)))
  for rows in streams.values():
    rows.sort(key=lambda pair: pair[0])
  return streams


def _road_edges(path, source, reader):
  radar_bus = 3 - source
  streams = _streams(path, {(source, 0x08A): 32, (0, 0x127): 8,
                            (radar_bus, 0x160): 32, (radar_bus, 0x180): 64}, reader)
  times = {a: [t for t, _ in rows] for a, rows in streams.items()}
  speed = [((int.from_bytes(d[7:10], 'big') >> 5) & 0x7fff) - 6767 for _, d in streams[0x160]]
  for (_, prev), (t, d) in pairwise(streams[0x08A]):
    if not (prev[22] ^ d[22]) & 4:
      continue
    last = {}
    for addr, age in ((0x127, 120_000_000), (0x160, 100_000_000), (0x180, 65_000_000)):
      i = bisect_right(times.get(addr, ()), t) - 1
      if i >= 0 and t - times[addr][i] <= age:
        last[addr] = i
    gear = _GEARS[streams[0x127][last[0x127]][1][5] >> 4] if 0x127 in last else ''
    first_negative = first_speed = ''
    if gear == 'R' and 0x160 in last:
      st = times[0x160]
      for i in range(max(1, bisect_left(st, t - 500_000_000)), last[0x160] + 1):
        if speed[i-1] == 0 and speed[i] < 0 and st[i] - st[i-1] <= 100_000_000:
          first_negative, first_speed = st[i], speed[i]
          break
    yield (t, int(bool(d[22] & 4)), (d[26] - prev[26]) % 64, d[26] % 2, gear,
           speed[last[0x160]] if 0x160 in last else '',
           t - times[0x180][last[0x180]] if 0x180 in last else '', first_negative, first_speed)


def _crossing(path, reader):
  # The observed crossing brackets both bit edges in route 140/4. Join from
  # each display timestamp backwards; B6 is never used to pick a radar point.
  banks = range(0x180, 0x186)
  sizes = {(1, a): 64 for a in banks} | {(2, 0x08A): 32, (2, 0x5AE): 32, (0, 0x0AA): 8}
  streams = _streams(path, sizes, reader)
  times = {a: [t for t, _ in rows] for a, rows in streams.items()}
  for t, hud in streams[0x5AE]:
    if not 948_800_000_000 <= t <= 951_100_000_000:
      continue
    previous = {}
    for addr in (*banks, 0x08A, 0x0AA):
      i = bisect_right(times[addr], t) - 1
      max_age_ns = 70_000_000 if addr in banks else 50_000_000
      if i < 0 or t - times[addr][i] > max_age_ns:
        raise ValueError(f'no fresh {addr:#x} for crossing at {t}')
      previous[addr] = streams[addr][i][1]
    if len({previous[a][2:4] for a in banks}) != 1:
      raise ValueError(f'incomplete radar cycle at {t}')
    candidates = []
    for bank in range(3):
      for off in range(4, 60, 7):
        geom = previous[0x180 + bank][off:off + 7]
        motion = previous[0x183 + bank][off:off + 7]
        x, y = decode_object_geometry(geom)
        if 0 < x < 320 and motion[5] & 3:
          candidates.append((x, y, decode_object_relative_speed(motion)))
    closest = min(candidates, default=('', '', ''), key=lambda point: point[0])
    yield (t, int(bool(previous[0x08A][22] & 4)), int(_wheels_at_zero(previous[0x0AA])),
           hud[3:7].hex(), hud[4] & 127, _pcs_lateral_code(hud), *closest)


def _print_crossing(logs_root, openpilot_root):
  reader = load_logreader(openpilot_root)
  manifest = REPO_ROOT / 'data/generated/camry_2026_08a_bit_census/captures.csv'
  with manifest.open(newline='') as f:
    row, = (r for r in csv.DictReader(f) if r['route'] == '00000140--7bec8dde3f' and r['segment'] == '4')
  path = logs_root / row['path']
  if row['source'] != '2' or sha256_file(path) != row['sha256']:
    raise ValueError(f'wrong native source or hash: {path}')
  out = csv.writer(sys.stdout, lineterminator='\n')
  out.writerow(('pcs_logger_ns', 'b22_bit2', 'four_wheels_zero', 'pcs_B3_B6_hex', 'pcs_range_code',
                'pcs_lateral_code_right', 'nearest_radar_x_m', 'nearest_radar_y_left_m', 'nearest_radar_vrel_mps'))
  out.writerows(_crossing(path, reader))


def _print_road(logs_root, openpilot_root):
  reader = load_logreader(openpilot_root)
  out = csv.writer(sys.stdout, lineterminator='\n')
  out.writerow(('route', 'segment', 'edge_logger_ns', 'new_level', 'sequence_step', 'sequence_parity',
                'selector', 'ego_speed_0_01_kmh', 'age_of_180_ns', 'reverse_speed_onset_ns', 'onset_speed_0_01_kmh'))
  manifest = REPO_ROOT / 'data/generated/camry_2026_08a_bit_census/captures.csv'
  with manifest.open(newline='') as f:
    for row in csv.DictReader(f):
      source = int(row['source'])
      path = logs_root / row['path']
      if source not in (1, 2) or sha256_file(path) != row['sha256']:
        raise ValueError(f'wrong native source or hash: {path}')
      for edge in _road_edges(path, source, reader):
        out.writerow((row['route'], row['segment'], *edge))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--road-logs', type=Path, help='replay manifest-pinned rlogs instead of the checked-in trials')
  parser.add_argument('--openpilot-root', type=Path, help='matching log reader for --road-logs')
  parser.add_argument('--crossing', action='store_true', help='emit the roadside target crossing on 140/4')
  args = parser.parse_args()
  if bool(args.road_logs) != bool(args.openpilot_root):
    parser.error('--road-logs and --openpilot-root must be supplied together')
  if args.crossing and not args.road_logs:
    parser.error('--crossing requires --road-logs')
  if args.road_logs:
    if args.crossing:
      _print_crossing(args.road_logs, args.openpilot_root)
    else:
      _print_road(args.road_logs, args.openpilot_root)
  else:
    json.dump([_trial(*record) for record in _CAPTURES], sys.stdout, indent=2)
    print()
