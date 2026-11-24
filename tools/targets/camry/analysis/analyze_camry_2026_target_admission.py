"""Compare private 0x230 objects with native Camry 0x08A B22[2] at rest."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from bisect import bisect_right
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from itertools import pairwise
from pathlib import Path
from struct import Struct

from tools import REPO_ROOT
from tools.targets.camry.analysis.analyze_camry_2026_stationary_state import (
  _CAPTURES,
  _pcs_lateral_code,
  _streams,
  _trial_frames,
  _wheels_at_zero,
)
from tools.targets.camry.analysis.extract_camry_20260930_vmc_corpus import sha256_file
from tools.toyota_support.route_log import load_logreader


_WHEELS = Struct('>4H')
_RECORD_OFFSETS = (6, 20, 34, 48)


def corridor(payload):
  """Yield (record offset, lateral corner sum) for 0 < x <= 3 m, |y| <= 0.8 m."""
  for i in _RECORD_OFFSETS:
    packed = int.from_bytes(payload[i + 3:i + 10], 'big')
    sx = sy = 0
    for shift in (42, 28, 14, 0):
      corner = packed >> shift
      sx += (corner >> 7) & 127
      sy += ((corner & 127) ^ 64) - 64
    if 0 < sx <= 4 * 60 and abs(sy) <= 4 * 16:
      yield i, sy


def _road_streams(row, logs_root, openpilot_root, *, pcs=False):
  source = int(row['source'])
  if source not in (1, 2):
    raise ValueError(f'unattributed perception bus: {row}')
  path = logs_root / row['path']
  if sha256_file(path) != row['sha256']:
    raise ValueError(f'wrong capture: {path}')
  sizes = {(source, 0x08A): 32, (3 - source, 0x230): 64, (0, 0x0AA): 8, (0, 0x127): 8}
  if pcs:
    sizes[source, 0x5AE] = 32
  return _streams(path, sizes, load_logreader(openpilot_root))


def _parked_reports(streams):
  times = {a: [t for t, _ in rows] for a, rows in streams.items()}

  def held(addr, at, latest, age):
    idx = bisect_right(times.get(addr, ()), latest) - 1
    if idx >= 0 and abs(at - times[addr][idx]) <= age:
      return streams[addr][idx][1]
    return None

  for t, data in streams[0x230]:
    if not _wheels_at_zero(held(0x0AA, t, t, 100_000_000)):
      continue
    gear = held(0x127, t, t, 180_000_000)
    if gear is None or gear[5] >> 4 != 0:
      continue
    # Compare the nearby native output, not a causal estimate. Its observed
    # update follows the private cycle on some routes and shares a batch on others.
    q = held(0x08A, t, t + 15_000_000, 50_000_000)
    if q is None:
      continue
    yield t, q[22] >> 2 & 1, data


def road_segment(row, logs_root, openpilot_root):
  counts = Counter()
  for _, state, data in _parked_reports(_road_streams(row, logs_root, openpilot_root)):
    codes = list(corridor(data))
    admitted = [data[i + 2] & 7 for i, _ in codes if data[i] & 15 != 0xA]
    counts[state, 'samples'] += 1
    counts[state, 'in_corridor'] += bool(codes)
    counts[state, 'non_a'] += bool(admitted)
    counts[state, 'point_only'] += bool(admitted) and all(shape == 4 for shape in admitted)
  return row['route'], counts


def _cohort_segment(row, logs_root, openpilot_root):
  streams = _road_streams(row, logs_root, openpilot_root, pcs=True)
  # Require all four raw wheels >= 1 km/h. Read motion even from segments
  # without a parked candidate. A missing route prefix is not evidence of rest.
  first_motion = next((t for t, d in streams[0x0AA] if all(6867 <= w < 32768 for w in _WHEELS.unpack(d))), None)
  pcs = streams[0x5AE]
  times = [t for t, _ in pcs]
  samples = []
  for t, state, d in _parked_reports(streams):
    slots = [(i, sy) for i, sy in corridor(d) if d[i] & 15 != 0xA]
    if not slots:
      continue
    moving = [(i, sy) for i, sy in slots if d[i] & 15 == 1 and d[i + 2] & 7 == 2 and abs((d[i + 11] ^ 128) - 128) >= 6]
    if moving:
      kind = 'lateral_square'
    elif all(d[i + 2] & 7 == 4 for i, _ in slots):
      kind = 'points_only'
    else:
      kind = 'other_outline'
    j = bisect_right(times, t) - 1
    matched = False
    if j >= 0 and t - times[j] <= 230_000_000:
      hud = pcs[j][1]
      ident = hud[5] >> 3
      speed_half_kmh = (((hud[3] * 2 + (hud[4] >> 7)) ^ 256) - 256) - 155
      close = (hud[4] & 127) <= 3 and abs(_pcs_lateral_code(hud)) <= 2 and abs(speed_half_kmh) <= 2
      matched = close and ident < 16 and any((d[i] >> 4) == (ident + 1) % 16 for i, _ in slots)
    marked = [abs(sy) for i, sy in moving if d[i + 1] == 0x3C]
    centered_point = kind == 'points_only' and any(d[i] & 15 == 0 and abs(sy) <= 4 * 3 for i, sy in slots)
    samples.append((t, state, kind, matched, bool(marked), any(y <= 4 * 12 for y in marked), centered_point))
  return row['route'], first_motion, samples


def _print_cohorts(manifest, args):
  motion, samples = {}, defaultdict(list)
  replay = partial(_cohort_segment, logs_root=args.road_logs, openpilot_root=args.openpilot_root)
  with manifest.open(newline='') as f, ProcessPoolExecutor(args.jobs) as pool:
    for route, first, rows in pool.map(replay, csv.DictReader(f), chunksize=3):
      if first is not None:
        motion[route] = min(motion.get(route, first), first)
      samples[route].extend(rows)
  out = csv.writer(sys.stdout, lineterminator='\n')
  out.writerow(('route', 'prior_wheel_motion', 'candidate', 'b22_bit2', 'epochs', 'pcs_same_id_close_static',
                'square_R1_3c', 'square_R1_3c_within_0_60m_lateral', 'point_status0_within_0_15m_lateral'))
  for route, rows in sorted(samples.items()):
    counts = defaultdict(Counter)
    for t, state, kind, matched, flagged, central, centered_point in rows:
      count = counts[route in motion and motion[route] < t, kind, state]
      count['epochs'] += 1
      count['pcs'] += matched
      count['flagged'] += flagged
      count['central'] += central
      count['centered_point'] += centered_point
    for (seen, kind, state), count in sorted(counts.items()):
      out.writerow((route, int(seen), kind, state, count['epochs'], count['pcs'], count['flagged'], count['central'], count['centered_point']))


def _handoff_route(item, logs_root, openpilot_root):
  route, rows = item
  reports = sorted((obs for row in rows for obs in _parked_reports(_road_streams(row, logs_root, openpilot_root))),
                   key=lambda obs: obs[0])
  events = []
  origins = {}
  previous = {}
  prev_t = 0
  for t, level, data in reports:
    window = dict(corridor(data))
    # An ID is a publication link only when it is unique in both reports.
    records = {}
    for i in _RECORD_OFFSETS:
      if data[i + 2] & 7:
        ident = data[i] >> 4
        records[ident] = None if ident in records else i
    if not 25_000_000 <= t - prev_t <= 80_000_000:
      previous.clear()
      origins.clear()
    points = {ident: i for ident, i in records.items() if i is not None and data[i] & 15 != 0xA and data[i + 2] & 7 == 4}
    origins = {ident: event for ident, event in origins.items() if ident in points}
    admitted = [data[i + 2] & 7 for i in window if data[i] & 15 != 0xA]
    point_only = bool(admitted) and all(shape == 4 for shape in admitted)
    for ident, i in points.items():
      if ident in previous:
        old = previous[ident]
        event = [route, ident, prev_t, t, old.hex(), data[i:i + 12].hex(), int(i in window),
                 (old[11] ^ 128) - 128, level, t, 0, 0]
        origins[ident] = event
        events.append(event)
      if ident in origins:
        event = origins[ident]
        event[9] = t
        if point_only and i in window:
          event[10 + level] += 1
    previous = {ident: data[i:i + 12] for ident, i in records.items() if i in window and
                data[i] & 15 == 1 and data[i + 2] & 7 in (1, 2, 3)}
    prev_t = t
  return events


def _print_handoffs(manifest, args):
  routes = defaultdict(list)
  with manifest.open(newline='') as f:
    for row in csv.DictReader(f):
      routes[row['route']].append(row)
  replay = partial(_handoff_route, logs_root=args.road_logs, openpilot_root=args.openpilot_root)
  out = csv.writer(sys.stdout, lineterminator='\n')
  out.writerow(('route', 'track_id', 'last_outline_ns', 'first_point_ns', 'last_outline_R', 'first_point_R',
                'first_point_in_window', 'outline_R11_signed', 'level_at_handoff', 'last_linked_point_ns',
                'point_only_low', 'point_only_high'))
  with ProcessPoolExecutor(args.jobs) as pool:
    for events in pool.map(replay, sorted(routes.items())):
      out.writerows(events)


def _selected_record(objects, pcs):
  ident = pcs[5] >> 3
  if ident >= 16:
    return None
  slots = [i for i in _RECORD_OFFSETS if objects[i + 2] & 7 and objects[i] >> 4 == (ident + 1) % 16]
  return objects[slots[0]:slots[0] + 12] if len(slots) == 1 else None


def _history_fork(decisions):
  """Longest matching input history with the same prior output and observed run length, but opposite next bits."""
  groups = defaultdict(list)
  best = None
  for j, (t, state, ticks, inputs) in enumerate(decisions):
    if inputs is None or ticks is None:
      continue
    for i in groups[ticks, inputs, 1 - state]:
      n = 1
      while n <= i and decisions[i - n][3] is not None and decisions[i - n][3] == decisions[j - n][3]:
        n += 1
      score = n, -(t - decisions[i][0])
      if best is None or score > best[0]:
        best = score, i, j
    groups[ticks, inputs, state].append(j)
  if best is None:
    return None
  (n, _), i, j = best
  return {
    'matching_decisions': n, 'prior_state_updates': decisions[j][2],
    'selected_record_hex': decisions[j][3][0].hex(), 'pcs_B0_through_B25': decisions[j][3][1].hex(),
    'previous_request_B0_through_B25': decisions[j][3][-1].hex(),
    'observations': [{'first_matching_ns': decisions[k - n + 1][0], 'decision_ns': decisions[k][0],
                      'b22_bit2': decisions[k][1]} for k in (i, j)],
  }


def _trial_selection(frames, phases):
  last = {}
  boundary = defaultdict(lambda: [0, 0])
  decisions = []
  prev = ticks = None
  for t, _, addr, d in frames:
    last[addr] = t, d
    if addr not in (0x08A, 0x5AE) or t < 1_000_000_000:
      continue
    if addr == 0x08A and d[26] & 1 not in phases:
      continue
    fresh = all(a in last and t - last[a][0] <= age for a, age in
                ((0x230, 75_000_000), (0x5AE, 230_000_000), (0x0AA, 75_000_000), (0x127, 150_000_000)))
    rec = _selected_record(last[0x230][1], last[0x5AE][1]) if fresh and _wheels_at_zero(last[0x0AA][1]) else None
    if addr == 0x5AE:
      if not rec or rec[2] & 7 != 3 or 0x08A not in last or t - last[0x08A][0] > 50_000_000:
        continue
      packed = int.from_bytes(rec[3:10], 'big')
      # Sum the four forward corners in 5 cm counts; retain the exact 2.80 m bin.
      sx = sum((packed >> shift) & 127 for shift in (49, 35, 21, 7))
      band = '<2.80' if sx < 224 else '=2.80' if sx == 224 else '>2.80'
      reverse = last[0x127][1][5] >> 4 == 1
      state = last[0x08A][1][22] >> 2 & 1
      boundary[reverse, _pcs_lateral_code(d), band][state] += 1
      continue
    state = d[22] >> 2 & 1
    contiguous = prev is not None and (d[26] - prev[1][26]) % 64 == 2 and 33_000_000 < t - prev[0] < 68_000_000
    if not contiguous:
      ticks = None
    inputs = None
    if contiguous and rec and all(a in last and t - last[a][0] <= age for a, age in
                                  ((0x51E, 1_200_000_000), (0x116, 100_000_000), (0x081, 100_000_000))):
      inputs = (rec, last[0x5AE][1][:26], last[0x127][1][5] >> 4, last[0x51E][1][0] >> 7,
                last[0x116][1][1], last[0x081][1][:28], last[0x0AA][1], prev[1][:26])
    decisions.append((t, state, ticks, inputs))
    if contiguous and (d[22] ^ prev[1][22]) & 4:
      ticks = 1
    elif ticks is not None:
      ticks += 1
    prev = t, d
  return {
    'selected_shape3_at_pcs_publication': [
      {'reverse': reverse, 'pcs_lateral_code': code, 'forward_m': band, 'low': counts[0], 'high': counts[1]}
      for (reverse, code, band), counts in sorted(boundary.items())],
    'selected_history_fork': _history_fork(decisions),
  }


def controlled(relative, bus, pin):
  sizes = {(bus, a): size for a, size in ((0x08A, 32), (0x5AE, 32), (0x0AA, 8), (0x127, 8),
                                          (0x51E, 8), (0x116, 8), (0x081, 32))}
  sizes[3 - bus, 0x230] = 64
  frames = sorted((round(f['t'] * 1e9), i, f['addr'], bytes.fromhex(f['data']))
                  for i, f in enumerate(_trial_frames(relative, pin)) if sizes.get((f['bus'], f['addr'])) == f['len'])
  requests = [(t, d) for t, _, a, d in frames if a == 0x08A]
  phases = {d[26] & 1 for (t0, before), (t, d) in pairwise(requests) if (before[22] ^ d[22]) & 4
            and 10_000_000 < t - t0 < 50_000_000 and (d[26] - before[26]) % 64 == 1}
  if len(phases) > 1:
    raise ValueError(f'inconsistent update phase: {relative}')
  last, previous = {}, {}
  best = None
  for t, _, addr, d in frames:
    last[addr] = t, d
    if addr != 0x08A or t < 1_000_000_000 or d[26] & 1 not in phases:
      continue
    if any(a not in last or t - last[a][0] > age for a, age in
           ((0x230, 75_000_000), (0x5AE, 230_000_000), (0x0AA, 100_000_000), (0x127, 180_000_000))):
      continue
    if not _wheels_at_zero(last[0x0AA][1]):
      continue
    key = last[0x127][1][5] >> 4, last[0x230][1][3:], last[0x5AE][1][:26]
    state = d[22] >> 2 & 1
    obs = {'request_ns': t, 'b22_bit2': state, 'object_age_ns': t - last[0x230][0], 'pcs_age_ns': t - last[0x5AE][0]}
    other = previous.get((key, 1 - state))
    if other and (best is None or t - other['request_ns'] < best[0]):
      best = t - other['request_ns'], key, (other, obs)
    previous[key, state] = obs
  result = {'capture': relative, 'update_parity': sorted(phases), 'nearest_opposite_pair': None,
            **_trial_selection(frames, phases)}
  if best:
    dt, (gear, objects, hud), observations = best
    # A later 5 Hz publication can expose a newer lateral estimate. It is
    # evidence about timing, never an input to the earlier 20 Hz decision.
    for obs in observations:
      following = next(((t, _pcs_lateral_code(d)) for t, _, a, d in frames
                        if a == 0x5AE and 0 < t - obs['request_ns'] <= 230_000_000), None)
      if following:
        obs['next_pcs_ns'], obs['next_pcs_lateral_code_right'] = following
    result['nearest_opposite_pair'] = {'separation_ns': dt, 'gear': gear, 'object_B3_through_B63': objects.hex(),
                                       'pcs_B0_through_B25': hud.hex(), 'observations': observations}
  return result


def _print_rises(manifest, logs_root, openpilot_root):
  with manifest.with_name('stationary_road_edges.csv').open(newline='') as f:
    rises = defaultdict(list)
    for row in csv.DictReader(f):
      if row['new_level'] == '1':
        rises[row['route'], row['segment']].append(int(row['edge_logger_ns']))
  out = csv.writer(sys.stdout, lineterminator='\n')
  out.writerow(('route', 'segment', 'rise_ns', 'object_ns', 'delta_ns', 'corridor_status_shape_hex', 'four_cells_hex'))
  with manifest.open(newline='') as f:
    for row in csv.DictReader(f):
      key = row['route'], row['segment']
      if key not in rises:
        continue
      streams = _road_streams(row, logs_root, openpilot_root)
      edges = {t for (prev_t, prev), (t, d) in pairwise(streams[0x08A]) if not prev[22] & 4 and d[22] & 4
               and (d[26] - prev[26]) % 64 == 1 and 0 < t - prev_t < 50_000_000}
      times = [t for t, _ in streams[0x230]]
      for t in rises[key]:
        if t not in edges:
          raise ValueError(f'missing contiguous native rise: {key} {t}')
        j = bisect_right(times, t)
        for i in (j - 1, j):
          if not 0 <= i < len(times) or abs(times[i] - t) > 65_000_000:
            raise ValueError(f'missing adjacent object report: {key} {t}')
          ts, d = streams[0x230][i]
          codes = ' '.join(f'{d[offset] & 15:x}/{d[offset + 2] & 7:x}' for offset, _ in corridor(d))
          out.writerow((*key, t, ts, ts - t, codes, d[4:60].hex()))


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--road-logs', type=Path, help='all original rlogs pinned by the bit census (default: five checked-in trials)')
  parser.add_argument('--openpilot-root', type=Path, help='matching openpilot log reader')
  parser.add_argument('--jobs', type=int, default=1)
  mode = parser.add_mutually_exclusive_group()
  mode.add_argument('--rises', action='store_true', help='emit the two private object reports bracketing each road rise')
  mode.add_argument('--cohorts', action='store_true', help='split in-corridor candidates by previous wheel motion and track type')
  mode.add_argument('--point-handoffs', action='store_true', help='follow each in-path status-1 outline ID that becomes a point')
  args = parser.parse_args()
  if bool(args.road_logs) != bool(args.openpilot_root) or args.jobs < 1:
    parser.error('supply both --road-logs and --openpilot-root for road replay; --jobs must be positive')
  if (args.rises or args.cohorts or args.point_handoffs) and not args.road_logs:
    parser.error('road output modes require --road-logs')
  if not args.road_logs:
    print(json.dumps([controlled(*entry) for entry in _CAPTURES], indent=2))
    return
  manifest = REPO_ROOT / 'data/generated/camry_2026_08a_bit_census/captures.csv'
  if args.point_handoffs:
    _print_handoffs(manifest, args)
    return
  if args.cohorts:
    _print_cohorts(manifest, args)
    return
  if args.rises:
    _print_rises(manifest, args.road_logs, args.openpilot_root)
    return
  totals = defaultdict(Counter)
  replay = partial(road_segment, logs_root=args.road_logs, openpilot_root=args.openpilot_root)
  with manifest.open(newline='') as f, ProcessPoolExecutor(args.jobs) as pool:
    for route, counts in pool.map(replay, csv.DictReader(f), chunksize=3):
      totals[route].update(counts)
  fields = ('samples', 'in_corridor', 'non_a', 'point_only')
  out = csv.writer(sys.stdout, lineterminator='\n')
  out.writerow(('route', 'b22_bit2', *fields))
  for route, counts in sorted(totals.items()):
    for state in (0, 1):
      out.writerow((route, state, *(counts[state, field] for field in fields)))


if __name__ == '__main__':
  main()
