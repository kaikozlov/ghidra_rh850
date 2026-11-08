#!/usr/bin/env python3
"""Verify the exact-Camry vehicle-speed carrier map."""
from __future__ import annotations

import json

from tools import REPO_ROOT

REPO = REPO_ROOT
d = json.loads((REPO / 'data/generated/camry_2026_cluster_ui_speed.json').read_text())
pcs = json.loads((REPO / 'data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json').read_text())


def check(name: str, cond: bool) -> None:
  if not cond:
    raise AssertionError(name)
  print(f'[PASS] {name}')


check('schema version', d['schema_version'] == 2)
check('complete current route 2c archive is reduced',
      d['route'] == '0000002c--c784367b7e' and d['segments'] == 26 and len(d['source_files']) == 26)
check('complete native 0x251/0x610 populations are pinned',
      d['native_counts'] == {'0x251_bus2': 1546, '0x610_bus0': 3247})
check('every native 0x610 frame joins a nearby wheel-speed sample', d['all_speed_join']['samples'] == 3247)
check('moving 0x610 integer speed remains tightly wheel-correlated',
      d['moving_over_2kph_join']['samples'] == 703 and
      d['moving_over_2kph_join']['absolute_error_kph']['p50'] == 0.25 and
      d['moving_over_2kph_join']['absolute_error_kph']['p95'] < 0.7 and
      d['moving_over_2kph_join']['absolute_error_kph']['max'] < 1.6)

carriers = d['carrier_map']
sp1 = carriers['sp1']
check('exact F33 0x0D7 signal246 is Toyota CAN Vehicle Speed SP1',
      sp1['wire'] == '0x0D7 B1:B2 big-endian unsigned 16-bit' and
      sp1['scale'] == '0.01 km/h/count' and sp1['exact_f33_signal_id'] == 246 and
      sp1['exact_f33_ram'] == 'FEBE809A' and int(sp1['exact_f33_did_callback'], 16) == 0x4E5A8 and
      sp1['gts']['did'] == '0x1185' and sp1['gts']['name'] == 'CAN Vehicle Speed (SP1)' and
      sp1['gts']['bit_width'] == 16 and sp1['gts']['decimal_point_count'] == 1)
check('adjacent 0x0D7 signal247 remains unnamed and snapshot-only',
      carriers['d7_signal247']['wire'] == '0x0D7 B3:B4 big-endian unsigned 16-bit' and
      carriers['d7_signal247']['exact_f33_signal_id'] == 247 and
      carriers['d7_signal247']['oem_name'] is None and 'FEBEAED6' in carriers['d7_signal247']['exact_f33_ram'])

meter = carriers['meter_integer']
check('GTS Vehicle Speed Meter candidates have the exact 8-bit 1-km/h shape',
      {(x['did'], x['name'], x['bit_width'], x['unit'], x['mul'], x['div']) for x in meter['gts_candidates']} == {
        ('0x1041', 'Vehicle Speed Meter', 8, 'km/h', 1, 1),
        ('0x1081', 'Vehicle Speed Meter', 8, 'km/h', 1, 1),
      } and meter['wire'] == '0x610 B2 unsigned 8-bit' and not meter['direct_live_meter_did_read'])
check('exact current Combination Meter transport resolves to 0x7C0',
      d['gts_meter']['transport']['category_id'] == 409 and
      d['gts_meter']['transport']['database'] == 'Meter_P5.ddb' and
      d['gts_meter']['transport']['route_selector'] == 0x12 and
      d['gts_meter']['transport']['request_address'] == 0x7C0)
check('GTS separates Speedometer Operation from Speed Signal Input active tests',
      d['gts_meter']['speedometer_operation_40']['did'] == '0x2801' and
      d['gts_meter']['speedometer_operation_40']['name'] == 'Speedometer Operation (40km/h,40MPH)' and
      d['gts_meter']['speed_signal_input_40']['did'] == '0x2A01' and
      d['gts_meter']['speed_signal_input_40']['name'] == 'Speed Signal Input (40)')

highway = {r['route']: r for r in d['highway_routes']}
check('both complete September-6 highway routes are analyzed',
      set(highway) == {'0000003e--1a2f20417d', '0000003f--36e72f5fdc'} and
      highway['0000003e--1a2f20417d']['segments'] == 78 and
      highway['0000003f--36e72f5fdc']['segments'] == 84 and
      highway['0000003e--1a2f20417d']['joined_samples'] == 16230 and
      highway['0000003f--36e72f5fdc']['joined_samples'] == 16657)
check('SP1 is about 0.5 percent above the wheel-equivalent signal247',
      all(1.0045 < r['sp1_vs_signal247']['slope'] < 1.0056 for r in highway.values()) and
      all(-0.06 < r['sp1_vs_signal247']['intercept_kph'] < 0 for r in highway.values()))
check('SP1 bias grows to roughly a third mph at highway speed',
      all(0.30 < r['bins_mph']['60-70']['sp1_minus_wheel_mph_p50'] < 0.34 for r in highway.values()) and
      all(0.33 < r['bins_mph']['70-80']['sp1_minus_wheel_mph_p50'] < 0.36 for r in highway.values()) and
      all(abs(r['bins_mph']['70-80']['signal247_minus_wheel_mph_p50']) < 0.01 for r in highway.values()))
check('whole-km/h 0x610 is best explained by nearest-integer SP1',
      all(r['highway_60_80_mph']['meter_integer_equals_round_sp1_fraction'] > .89 for r in highway.values()) and
      all(r['highway_60_80_mph']['meter_integer_equals_round_sp1_fraction'] >
          r['highway_60_80_mph']['meter_integer_equals_ceil_signal247_fraction'] for r in highway.values()))
check('0x610 B2 is unique in the exhaustive bus0 byte census',
      all(r['bus0_byte_census_vs_round_sp1'][0]['wire'] == '0x610/8 B2' and
          r['bus0_byte_census_vs_round_sp1'][0]['mae_to_round_sp1'] < .1 and
          r['bus0_byte_census_vs_round_sp1'][1]['mae_to_round_sp1'] > 16 for r in highway.values()))
check('FRC 0x1B2 B2 mirrors the whole-km/h meter carrier',
      all(.83 < r['frc_integer_mirror']['exact_fraction'] < .86 and
          r['frc_integer_mirror']['difference_p10'] == 0 and
          r['frc_integer_mirror']['difference_p50'] == 0 and
          r['frc_integer_mirror']['difference_p90'] == 0 for r in highway.values()))
check('artifact preserves the missing live-meter boundary',
      'no Combination Meter 0x7C0 diagnostic read' in d['semantic_boundary'] and
      'physical dashboard number is not logged' in d['semantic_boundary'])

rows = pcs['operation_ffd']['detail_rows']
vehicle_speed = [r for r in rows if r['DataID'] in ('5235', '5236')]
check('current Toyota Operation-FFD exposes the meter semantic oracles',
      {(r['DataID'], r['DataName']) for r in vehicle_speed} == {
        ('5235', 'Vehicle speed meter'), ('5236', 'Vehicle speed meter status'),
      })
check('meter semantic oracles are not ordinary SupportDID joins', all(r['SupportDID'] == 0 for r in vehicle_speed))
