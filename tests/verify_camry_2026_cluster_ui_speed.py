#!/usr/bin/env python3
"""Verify the bounded exact-Camry 0x610 UI-speed interpretation."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
d = json.loads((REPO / 'data/generated/camry_2026_cluster_ui_speed.json').read_text())
pcs = json.loads((REPO / 'data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json').read_text())


def check(name: str, cond: bool) -> None:
  if not cond:
    raise AssertionError(name)
  print(f'[PASS] {name}')


check('schema version', d['schema_version'] == 1)
check('complete current route 2c archive is reduced',
      d['route'] == '0000002c--c784367b7e' and d['segments'] == 26 and len(d['source_files']) == 26)
check('complete native 0x251/0x610 populations are pinned',
      d['native_counts'] == {'0x251_bus2': 1546, '0x610_bus0': 3247})
check('every native 0x610 frame joins a nearby wheel-speed sample', d['all_speed_join']['samples'] == 3247)
check('moving 0x610 UI speed remains tightly wheel-correlated',
      d['moving_over_2kph_join']['samples'] == 703 and
      d['moving_over_2kph_join']['absolute_error_kph']['p50'] == 0.25 and
      d['moving_over_2kph_join']['absolute_error_kph']['p95'] < 0.7 and
      d['moving_over_2kph_join']['absolute_error_kph']['max'] < 1.6)
check('artifact does not promote wheel correlation to literal dash semantics',
      'does not observe the physical meter display' in d['semantic_boundary'] and
      '5235' in d['semantic_boundary'] and '5236' in d['semantic_boundary'])

rows = pcs['operation_ffd']['detail_rows']
vehicle_speed = [r for r in rows if r['DataID'] in ('5235', '5236')]
check('current Toyota Operation-FFD exposes the meter semantic oracles',
      {(r['DataID'], r['DataName']) for r in vehicle_speed} == {
        ('5235', 'Vehicle speed meter'), ('5236', 'Vehicle speed meter status'),
      })
check('meter semantic oracles are not ordinary SupportDID joins', all(r['SupportDID'] == 0 for r in vehicle_speed))
