#!/usr/bin/env python3
"""Bound the exact-Camry 0x610 UI-speed carrier against source-real wheel speed.

The reducer deliberately does not call 0x610 the literal dash indication. It
joins native bus-0 0x610 B2 (legacy UI_SPEED, km/h) to the nearest native bus-0
0x0AA four-wheel mean in each rlog segment and records the complete current
archive-route population. Toyota Operation-FFD 5235/5236 remains the diagnostic
oracle required to distinguish a wheel-correlated UI carrier from the physical
meter display.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_LOG_ROOT = Path('/Users/kai/dev/inspect/logs/camry-2026')
DEFAULT_OPENPILOT_ROOT = Path('/Users/kai/dev/inspect/repos/kai-openpilot')
DEFAULT_ROUTE = '0000002c--c784367b7e'
DEFAULT_OUT = REPO / 'data/generated/camry_2026_cluster_ui_speed.json'


def load_logreader(openpilot_root: Path):
  sys.path.insert(0, str(openpilot_root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def be_raw(dat: bytes, start_bit: int, size: int) -> int:
  be_bits = [j + i * 8 for i in range(len(dat)) for j in range(7, -1, -1)]
  idx = be_bits.index(start_bit)
  value = 0
  for bit in be_bits[idx:idx + size]:
    byte_i, bit_i = divmod(bit, 8)
    value = (value << 1) | ((dat[byte_i] >> bit_i) & 1)
  return value


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
  return sorted(route_dir.glob('rlog-*.zst'), key=lambda p: int(p.stem.split('-')[1].split('.')[0]))


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


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument('--log-root', type=Path, default=DEFAULT_LOG_ROOT)
  ap.add_argument('--openpilot-root', type=Path, default=DEFAULT_OPENPILOT_ROOT)
  ap.add_argument('--route', default=DEFAULT_ROUTE)
  ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  route_dir = args.log_root / 'archive' / args.route
  files = discover(route_dir)
  if not files:
    raise FileNotFoundError(route_dir)
  LogReader = load_logreader(args.openpilot_root)

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
    ui: list[tuple[int, float]] = []
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
          ui.append((t, float(dat[2])))
        elif frame.src == 2 and frame.address == 0x251 and len(dat) == 8:
          frame_251 += 1

    wheel_times = [t for t, _ in wheels]
    for t, ui_kph in ui:
      i = bisect.bisect_left(wheel_times, t)
      candidates = []
      if i < len(wheels):
        candidates.append(wheels[i])
      if i:
        candidates.append(wheels[i - 1])
      if not candidates:
        continue
      wt, wheel_kph = min(candidates, key=lambda x: abs(x[0] - t))
      if abs(wt - t) > 100_000_000:
        continue
      error = ui_kph - wheel_kph
      errors_all.append(error)
      if abs(wheel_kph) > 2.0:
        errors_moving.append(error)

  payload = {
    'schema_version': 1,
    'route': args.route,
    'segments': len(files),
    'native_counts': {'0x251_bus2': frame_251, '0x610_bus0': frame_610},
    'ui_speed_decode': '0x610 B2 unsigned integer km/h (retained legacy UI_SPEED geometry)',
    'wheel_reference': 'nearest same-segment native bus0 0x0AA four-wheel mean within 100 ms',
    'all_speed_join': summarize_errors(errors_all),
    'moving_over_2kph_join': summarize_errors(errors_moving),
    'semantic_boundary': (
      '0x610.UI_SPEED is strongly wheel-speed coherent and is suitable as the retained openpilot vEgoCluster carrier, '
      'but this reduction does not observe the physical meter display. Toyota Operation-FFD 5235 Vehicle speed meter '
      'and 5236 Vehicle speed meter status remain the passive synchronized oracle for literal-dash semantics.'
    ),
    'source_files': source_files,
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
  print(args.out)
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
