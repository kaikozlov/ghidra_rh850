"""Measure Camry trip increments and low-speed distance counts in pinned capture spans."""

from __future__ import annotations

import argparse
import csv
import sys
from bisect import bisect_right
from collections import defaultdict
from itertools import pairwise
from pathlib import Path

from tools.targets.camry.analysis.extract_camry_20260930_vmc_corpus import sha256_file
from tools.toyota_support.route_log import load_logreader


def measure(manifest, spans, logs_root, reader, route_filter):
  paths = {(r['route'], r['segment']): r for r in manifest if r['source'] == '2'}
  groups = defaultdict(list)
  for row in spans:
    if route_filter is None or route_filter == row['route']:
      groups[row['route']].append(row)
  if not groups:
    raise ValueError('no matching spans')
  yield ('route', 'selection', 'start_ns', 'end_ns', 'trip_tenths_mile', 'distance_counts', 'low_speed_counts')
  for route, rows in groups.items():
    distance, trip = [], []
    segments = {n for r in rows for n in range(int(r['start_segment']), int(r['end_segment']) + 1)}
    # A first-in-segment trip increment needs the preceding old publication.
    for r in rows:
      previous = int(r['start_segment']) - 1
      if (route, str(previous)) in paths:
        segments.add(previous)
    for seg in sorted(segments):
      pin = paths[route, str(seg)]
      path = logs_root / pin['path']
      if sha256_file(path) != pin['sha256']:
        raise ValueError(f'SHA-256 mismatch: {path}')
      for event in reader(str(path), only_union_types=True):
        if event.which() != 'can':
          continue
        t = event.logMonoTime
        for msg in event.can:
          if msg.src != 0:
            continue
          if msg.address == 0x0D7 and len(msg.dat) == 32:
            distance.append((t, msg.dat[0] & 63, int.from_bytes(msg.dat[1:3], 'big')))
          elif msg.address == 0x614 and len(msg.dat) == 8:
            trip.append((t, int.from_bytes(msg.dat[4:8], 'big')))
    distance.sort(key=lambda r: r[0])
    trip.sort(key=lambda r: r[0])
    ticks = [r[0] for r in distance]
    steps = {b[0]: b[1] for a, b in pairwise(trip) if b[1] == a[1] + 1 and 0 < b[0] - a[0] < 1_100_000_000}
    for r in rows:
      start, end = int(r['start_ns']), int(r['end_ns'])
      first, last = (bisect_right(ticks, t) - 1 for t in (start, end))
      if first < 0 or last <= first or max(start - ticks[first], end - ticks[last]) >= 60_000_000:
        raise ValueError(f'no fresh distance at trip boundary: {route} {start}..{end}')
      counts = low = 0
      for i in range(first + 1, last + 1):
        t0, q0, s0 = distance[i-1]
        t1, q1, s1 = distance[i]
        if t1 - t0 > 100_000_000:
          raise ValueError(f'distance gap: {route} {t0}..{t1}')
        delta = (q1 - q0) % 64
        counts += delta
        if max(s0, s1) <= 175:
          low += delta
      yield (route, r['selection'], start, end, steps[end] - steps[start], counts, low)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('manifest', type=Path)
  parser.add_argument('spans', type=Path)
  parser.add_argument('--logs-root', type=Path, required=True)
  parser.add_argument('--openpilot-root', type=Path, required=True)
  parser.add_argument('--route', help='replay spans from a single full route ID')
  args = parser.parse_args()
  with args.manifest.open(newline='') as manifest, args.spans.open(newline='') as spans:
    csv.writer(sys.stdout, lineterminator='\n').writerows(measure(
      csv.DictReader(manifest), csv.DictReader(spans), args.logs_root, load_logreader(args.openpilot_root), args.route))


if __name__ == '__main__':
  main()
