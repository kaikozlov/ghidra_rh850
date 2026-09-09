#!/usr/bin/env python3
"""Measure exact-Camry parser source cadence/gaps from retained relay-correct rlogs.

This is an integration-evidence reducer, not a CAN decoder. It pins the native
source side, median cadence, high-percentile jitter, and worst same-segment gap
for every message checked by the current Camry TSS3 CarState parser. The
``parser_hz`` values are conservative frequency settings used to derive the
normal CANParser ten-period alive timeout; they are not claims that the ECU
publishes at exactly that rate.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DEFAULT_LOG_ROOT = Path('/Users/kai/dev/inspect/logs/camry-2026')
DEFAULT_OPENPILOT_ROOT = Path('/Users/kai/dev/inspect/repos/kai-openpilot')
DEFAULT_OUT = REPO / 'data/generated/camry_2026_parser_liveness.json'

ROUTES = {
  '3d': ('2026-09-04', '0000003d--0e812cecba'),
  '3e': ('2026-09-06', '0000003e--1a2f20417d'),
  '3f': ('2026-09-06', '0000003f--36e72f5fdc'),
}

# address: (native Panda bus/src, conservative parser Hz)
CHECKS = {
  0x00F: (0, 10),
  0x025: (0, 100),
  0x030: (0, 100),
  0x08A: (2, 40),
  0x0AA: (0, 100),
  0x0FE: (0, 30),
  0x101: (0, 50),
  0x116: (0, 40),
  0x127: (0, 50),
  0x251: (2, 1),
  0x3B7: (0, 3),
  0x3F6: (2, 1),
  0x412: (2, 1),
  0x51E: (0, 1),
  0x610: (0, 3),
  0x614: (0, 1),
  0x620: (0, 3),
  0x622: (0, 1),
}


def load_logreader(openpilot_root: Path):
  sys.path.insert(0, str(openpilot_root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def discover(route_dir: Path) -> list[Path]:
  flat = sorted(route_dir.glob('rlog-*.zst'), key=lambda p: int(p.stem.split('-')[1].split('.')[0]))
  if flat:
    return flat
  return sorted(route_dir.glob('*/rlog.zst'), key=lambda p: int(p.parent.name.rsplit('--', 1)[1]))


def quantile(vals: list[float], frac: float) -> float:
  vals = sorted(vals)
  return vals[int((len(vals) - 1) * frac)]


def analyze_route(LogReader, route_dir: Path) -> dict:
  files = discover(route_dir)
  if not files:
    raise FileNotFoundError(route_dir)
  intervals = {addr: [] for addr in CHECKS}
  counts = {addr: 0 for addr in CHECKS}

  # Reset the previous timestamp at each rlog boundary so segment gaps are not
  # misclassified as source-message outages.
  for path in files:
    prev: dict[int, float] = {}
    for msg in LogReader(str(path), sort_by_time=True):
      if msg.which() != 'can':
        continue
      t = msg.logMonoTime / 1e9
      for frame in msg.can:
        addr = int(frame.address)
        if addr not in CHECKS or int(frame.src) != CHECKS[addr][0]:
          continue
        counts[addr] += 1
        if addr in prev and t > prev[addr]:
          intervals[addr].append((t - prev[addr]) * 1000.0)
        prev[addr] = t

  out = {'segments': len(files), 'messages': {}}
  for addr, (bus, parser_hz) in CHECKS.items():
    vals = intervals[addr]
    if not vals:
      raise RuntimeError(f'no intervals for 0x{addr:03X} on bus {bus} in {route_dir}')
    med = quantile(vals, .5)
    measured_hz = 1000.0 / med
    timeout_ms = 10000.0 / parser_hz
    max_gap = max(vals)
    out['messages'][f'0x{addr:03X}'] = {
      'bus': bus,
      'frame_count': counts[addr],
      'same_segment_interval_count': len(vals),
      'interval_ms': {
        'p50': round(med, 6),
        'p99': round(quantile(vals, .99), 6),
        'max': round(max_gap, 6),
      },
      'measured_hz_from_median': round(measured_hz, 6),
      'parser_hz': parser_hz,
      'parser_alive_timeout_ms': round(timeout_ms, 6),
      'nominal_floor_ok': parser_hz <= measured_hz * 1.05,
      'worst_gap_inside_timeout': max_gap < timeout_ms,
      'timeout_to_worst_gap_ratio': round(timeout_ms / max_gap, 6),
    }
  return out


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument('--log-root', type=Path, default=DEFAULT_LOG_ROOT)
  ap.add_argument('--openpilot-root', type=Path, default=DEFAULT_OPENPILOT_ROOT)
  ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  LogReader = load_logreader(args.openpilot_root)
  routes = {}
  for short, (day, route) in ROUTES.items():
    routes[short] = analyze_route(LogReader, args.log_root / day / route)

  # Cross-route summary is deliberately conservative: preserve the lowest
  # measured median rate and largest observed same-segment gap.
  summary = {}
  for addr, (bus, parser_hz) in CHECKS.items():
    key = f'0x{addr:03X}'
    rows = [routes[r]['messages'][key] for r in ROUTES]
    summary[key] = {
      'bus': bus,
      'parser_hz': parser_hz,
      'lowest_measured_hz_from_median': min(r['measured_hz_from_median'] for r in rows),
      'largest_same_segment_gap_ms': max(r['interval_ms']['max'] for r in rows),
      'parser_alive_timeout_ms': rows[0]['parser_alive_timeout_ms'],
      'all_routes_nominal_floor_ok': all(r['nominal_floor_ok'] for r in rows),
      'all_routes_worst_gap_inside_timeout': all(r['worst_gap_inside_timeout'] for r in rows),
    }

  payload = {
    'schema_version': 1,
    'scope': '2026 Camry exact-F33 relay-correct retained road routes; native Panda src only',
    'boundary': 'same-segment dynamic timing; parser Hz is a conservative liveness setting, not an exact ECU scheduler claim',
    'routes': routes,
    'summary': summary,
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
  print(f'wrote {args.out}')
  for key, row in summary.items():
    print(key, 'bus', row['bus'], 'parser', row['parser_hz'], 'min median Hz', row['lowest_measured_hz_from_median'], 'max gap ms', row['largest_same_segment_gap_ms'])
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
