#!/usr/bin/env python3
"""Verify retained same-car cadence evidence for the Camry TSS3 parser."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
d = json.loads((REPO / 'data/generated/camry_2026_parser_liveness.json').read_text())


def check(name: str, cond: bool) -> None:
  if not cond:
    raise AssertionError(name)
  print(f'[PASS] {name}')


check('schema version', d['schema_version'] == 1)
check('three independent long routes retained', {k: v['segments'] for k, v in d['routes'].items()} == {'3d': 62, '3e': 78, '3f': 84})
check('all 18 parser-checked sources are covered', len(d['summary']) == 18)
check('all configured rates are conservative nominal floors', all(v['all_routes_nominal_floor_ok'] for v in d['summary'].values()))
check('all worst same-segment gaps fit normal ten-period timeout', all(v['all_routes_worst_gap_inside_timeout'] for v in d['summary'].values()))

s = d['summary']
check('0x08A source/rate is bus2 and safely above 40 Hz parser setting',
      s['0x08A']['bus'] == 2 and s['0x08A']['parser_hz'] == 40 and s['0x08A']['lowest_measured_hz_from_median'] > 43.0)
check('0x127 is ~51 Hz and parser is corrected to 50 Hz',
      s['0x127']['bus'] == 0 and s['0x127']['parser_hz'] == 50 and 50.5 < s['0x127']['lowest_measured_hz_from_median'] < 51.5)
check('0x0FE remains ~33 Hz with conservative 30 Hz parser setting',
      s['0x0FE']['parser_hz'] == 30 and s['0x0FE']['lowest_measured_hz_from_median'] > 33.0)
check('0x412 is native bus2 ~1 Hz with large timeout margin',
      s['0x412']['bus'] == 2 and s['0x412']['parser_hz'] == 1 and
      0.99 < s['0x412']['lowest_measured_hz_from_median'] < 1.01 and
      s['0x412']['largest_same_segment_gap_ms'] < 1800 and s['0x412']['parser_alive_timeout_ms'] == 10000.0)
check('0x610 variable cadence still has >3x timeout margin',
      s['0x610']['parser_hz'] == 3 and s['0x610']['largest_same_segment_gap_ms'] < 1010 and
      s['0x610']['parser_alive_timeout_ms'] > 3333)
