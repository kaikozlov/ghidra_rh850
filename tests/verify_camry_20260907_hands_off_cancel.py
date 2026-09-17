#!/usr/bin/env python3
"""Verify the retained route-45 hands-off cancellation reduction."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'data/generated/camry_20260907_hands_off_cancel.json'

passed = failed = 0


def check(label: str, condition: bool, detail: str = '') -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f' ({detail})' if detail else ''))


obj = json.loads(ART.read_text())
check('schema', obj['schema'] == 'camry-20260907-hands-off-cancel-v1')
check('route identity', obj['source']['route'] == '00000045--805b7ca6ab' and obj['source']['segments'] == 15)
check('route openpilot commit pinned', obj['source']['openpilot_commit'] == 'f8bd956a4b23eb4992c6abbe899e72b27cd91d80')
check('nine operating-latch falls retained', obj['latch_fall_count'] == 9)
check('cancel classification census', obj['classification_counts'] == {
    'openpilot_button_cancel': 4,
    'stock_pcm_disable_other': 4,
    'strong_hands_off_cancel_witness': 1,
})
check('three stock-origin active-ID11 drops', obj['stock_active_lta_drop_count'] == 3)
check('one strongest hands-off witness', obj['strong_hands_off_witness_count'] == 1)

w = obj['strong_hands_off_witnesses'][0]
check('strong witness is segment10 at 1041.318670 s', w['segment'] == 10 and w['t_mono_s'] == 1041.31867)
check('no openpilot 0x101 precedes strong witness', w['openpilot_0x101_in_preceding_250ms'] == [])
check('only near-edge event is post-wire pcmDisable',
      w['onroad_events_near_edge'] == [{'lag_s': 0.004511, 'names': ['pcmDisable']}])
check('driver inputs do not explain strong witness',
      w['car_state_before']['cruise_enabled'] is True
      and w['car_state_before']['brake'] is False
      and w['car_state_before']['gas'] is False)

before = w['request_before']
after = w['request_after']
check('0x08A operating/lateral state withdraws',
      before['cruise_operating_latch'] == 1 and after['cruise_operating_latch'] == 0
      and before['lateral_request_id'] == 11 and after['lateral_request_id'] == 0)
check('0x08A set speed clears', before['set_speed_kph'] == 72 and after['set_speed_kph'] == 0)
check('0x08A longitudinal package A changes 11/1 -> 0/0',
      (before['longitudinal_request_id_a'], before['longitudinal_allocation_a']) == (11, 1)
      and (after['longitudinal_request_id_a'], after['longitudinal_allocation_a']) == (0, 0))
check('0x08A longitudinal package B changes 17/3 -> 4/2',
      (before['longitudinal_request_id_b'], before['longitudinal_allocation_b']) == (17, 3)
      and (after['longitudinal_request_id_b'], after['longitudinal_allocation_b']) == (4, 2))
check('0x08A accel packages change +0.011 -> -0.578 m/s2',
      before['longitudinal_accel_a_m_s2'] == 0.011 and before['longitudinal_accel_b_m_s2'] == 0.011
      and after['longitudinal_accel_a_m_s2'] == -0.578 and after['longitudinal_accel_b_m_s2'] == -0.578)
check('0x08A application sequence remains continuous',
      before['request_sequence'] == 50 and after['request_sequence'] == 51)

check('warning stage precedes cancel by 14.563771 s', w['warning_stage']['age_s'] == 14.563771 and w['warning_stage']['b19'] == 0x40)
check('HUD escalation precedes cancel by 8.605508 s',
      w['hud_escalation_stage']['age_s'] == 8.605508 and w['hud_escalation_stage']['raw'] == '140c404401ee9307')
check('late/final 0x371 state is B19=0x60 5.563167 s before cancel',
      w['late_final_stage_candidate']['age_s'] == 5.563167 and w['late_final_stage_candidate']['b19'] == 0x60)
check('late driver detection clears 0x60 but cancel still follows',
      w['late_final_stage_clear']['age_s'] == 4.159527
      and w['latest_driver_detect_rise']['age_s'] == 4.159527
      and w['late_final_stage_clear']['b19'] == 0x20
      and (w['latest_driver_detect_rise']['b20'] & 0x10) != 0)

r0 = w['result_lateral_id0_after']
r63 = w['result_driver_operation_id63_after']
check('0x081 lateral result follows to ID0 within 21 ms',
      r0['lag_s'] == 0.02084 and r0['decoded']['lateral_result_id'] == 0)
check('0x081 then selects longitudinal Driver Operation ID63 within 51 ms',
      r63['lag_s'] == 0.050637 and r63['decoded']['longitudinal_result_id'] == 63)
check('0x081 request-loss stays clear',
      r0['decoded']['request_loss_status'] == 0 and r63['decoded']['request_loss_status'] == 0)

check('native 0x101 does not change across cancellation',
      w['brake_0x101_before']['raw'] == '800000010000008b'
      and w['brake_0x101_after']['raw'] == '800000010000008b')
check('0x251 cruise main remains available',
      w['cruise_display_0x251_before']['decoded']['cruise_main_state'] == 1
      and w['cruise_display_0x251_after']['decoded']['cruise_main_state'] == 1)
check('FRC/chassis direction census is unambiguous',
      obj['native_source_counts']['0x08A/src2'] > 80 * obj['native_source_counts']['0x08A/src0']
      and obj['native_source_counts']['0x081/src0'] > 80 * obj['native_source_counts']['0x081/src2'])

print(f'\nSummary: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
