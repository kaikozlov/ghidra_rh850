"""Replay pinned camera-side 0x08A observations; print one CSV row per wire bit."""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from tools.targets.camry.analysis.extract_camry_20260930_vmc_corpus import sha256_file
from tools.toyota_support.route_log import load_logreader

# First wire byte, low bit, width, field, interpretation, evidence. Multibyte
# numeric fields are big-endian; the authentication trailer is opaque.
_FIELDS = (
  (3, 2, 1, 'pcs_opening', 'short PCS-associated phase', 'one recorded episode'),
  (3, 3, 1, 'cruise_operating', 'adaptive or conventional cruise operating', 'cross-stream'),
  (4, 5, 1, 'hold', 'delayed camera hold state', 'cross-stream'),
  (4, 6, 1, 'pcs_extended', 'extended PCS-associated phase', 'one recorded episode'),
  (4, 7, 1, 'startup_complete', 'request/display startup complete', 'cross-stream'),
  (5, 2, 1, 'nonordinary_long', 'longitudinal ID 13 or 17 in observed traffic', 'exact association'),
  (6, 2, 6, 'longitudinal_id', 'application code: 0, 11, 13, 17 observed', 'recorder and chassis result'),
  (6, 0, 2, 'allocation', 'allocation code: 0, 1, 3 observed', 'recorder and pedal comparison'),
  (7, 0, 8, 'prefix_checksum', 'prefix integrity field', 'integrity'),
  (8, 0, 16, 'acceleration_1', 'upper acceleration slot in ordinary DRCC; nominal 0.001 m/s^2/count', 'recorder and cross-stream'),
  (10, 0, 8, 'cruise_setpoint', 'internal cruise speed in km/h', 'cross-stream'),
  (11, 0, 16, 'acceleration_2', 'lower acceleration slot in ordinary DRCC; nominal 0.001 m/s^2/count', 'recorder and cross-stream'),
  (13, 0, 16, 'fixed_word_1', 'observed 0x7fff; physical function unknown', 'constant word'),
  (16, 0, 16, 'fixed_word_2', 'observed 0x7fff; physical function unknown', 'constant word'),
  (18, 0, 16, 'pinion_reference', 'requested pinion angle; 0.00100012 rad/count', 'controller and feedback'),
  (20, 6, 2, 'cruise_policy', 'policy code: 0, 1, 3 observed', 'cross-stream association'),
  (21, 0, 6, 'lateral_id', 'application code: 0, 4, 11, 18 observed', 'recorder and chassis result'),
  (22, 2, 1, 'in_path_target_at_rest', 'near frontal target selected while the vehicle is stopped (inferred); 20 Hz', 'stationary selector trials and radar crossing'),
  (22, 4, 1, 'long_app_present', 'nonzero longitudinal application ID', 'exact association'),
  (22, 5, 1, 'delayed_release', 'delayed longitudinal release after cruise exits', 'cross-stream'),
  (23, 5, 1, 'application_effort', 'lateral-ID-dependent steering effort or fixed state', 'cross-stream'),
  (24, 0, 8, 'assist_gain', 'retained lateral assist gain; 0.01/count', 'recorder and cross-stream'),
  (25, 0, 8, 'warning_gain', 'lane-departure vibration phase; damping gain at 0.01/count is a candidate', 'warning observed; gain inferred'),
  (26, 0, 6, 'request_sequence', 'request sequence field', 'transport'),
  (28, 0, 32, 'authentication_trailer', 'opaque transport bytes; no per-bit vehicle quantity', 'transport'),
)
_SIGNED = {'acceleration_1', 'acceleration_2', 'pinion_reference'}


def _annotate(rows):
  layout = {}
  for first, low, width, field, interpretation, evidence in _FIELDS:
    last = first + (low + width - 1) // 8
    for k in range(width):
      byte_offset, bit = divmod(low + k, 8)
      pos = last - byte_offset, bit
      if pos in layout:
        raise ValueError(f'overlapping 0x08A fields at {pos}')
      if field == 'authentication_trailer':
        part = 'opaque'
      elif width == 1:
        part = 'flag'
      elif field in _SIGNED and k == width - 1:
        part = 'sign'
      else:
        part = f'bit {k}'
      layout[pos] = (field, part, interpretation, evidence)
  rows = iter(rows)
  yield (*next(rows), 'field', 'field_part', 'interpretation', 'evidence')
  for row in rows:
    pos = int(row[0]), int(row[1])
    yield (*row, *layout.get(pos, ('unassigned', '', 'no established field assignment', 'unknown')))


def census(manifest, logs_root, log_reader, only_route=None):
  ones = np.zeros((32, 8), dtype=np.int64)
  flips = np.zeros_like(ones)
  routes_varying = np.zeros_like(ones)
  n = pairs = 0
  groups = defaultdict(list)
  for row in csv.DictReader(manifest):
    if only_route is None or row['route'] == only_route:
      groups[row['route']].append(row)
  if not groups:
    raise ValueError('no matching captures')
  seen_pins = set()
  for route, rows in groups.items():
    route_ones = np.zeros_like(ones)
    route_n = 0
    segments = set()
    for row in rows:
      path = logs_root / row['path']
      seg, source = row['segment'], int(row['source'])
      if seg in segments or row['sha256'] in seen_pins:
        raise ValueError(f'duplicate segment or capture: {route}/{seg}')
      segments.add(seg)
      seen_pins.add(row['sha256'])
      if sha256_file(path) != row['sha256']:
        raise ValueError(f'SHA-256 mismatch: {path}')
      events = []
      for event in log_reader(str(path), only_union_types=True):
        if event.which() == 'can':
          events.extend((event.logMonoTime, bytes(frame.dat)) for frame in event.can
                        if frame.address == 0x08A and frame.src == source and len(frame.dat) == 32)
      events.sort(key=lambda pair: pair[0])  # stable for equal logger timestamps
      if not events:
        raise ValueError(f'no selected frames: {path} (source {source})')
      data = np.frombuffer(b''.join(payload for _, payload in events), dtype=np.uint8).reshape(-1, 32)
      bits = np.unpackbits(data[:, :, None], axis=2, bitorder='little')
      route_ones += bits.sum(axis=0, dtype=np.int64)
      flips += np.count_nonzero(bits[1:] != bits[:-1], axis=0)
      route_n += len(events)
      pairs += len(events) - 1
    ones += route_ones
    routes_varying += (route_ones > 0) & (route_ones < route_n)
    n += route_n
  yield ('byte', 'bit', 'frames', 'ones', 'zeros', 'within_segment_pairs', 'flips', 'routes_varying')
  for b in range(32):
    for k in range(8):
      yield (b, k, n, ones[b, k], n - ones[b, k], pairs, flips[b, k], routes_varying[b, k])


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('manifest', type=Path, help='CSV: route,segment,source,path,sha256')
  parser.add_argument('--logs-root', required=True, type=Path)
  parser.add_argument('--openpilot-root', required=True, type=Path)
  parser.add_argument('--route', help='replay only this route')
  args = parser.parse_args()
  with args.manifest.open(newline='') as manifest:
    counts = census(manifest, args.logs_root, load_logreader(args.openpilot_root), args.route)
    csv.writer(sys.stdout, lineterminator='\n').writerows(_annotate(counts))


if __name__ == '__main__':
  main()
