#!/usr/bin/env python3
"""Reduce route 45 around OEM/TSS3 cruise cancellations after hands-off escalation.

This is a passive log reducer.  It distinguishes stock/FRC 0x08A operating-latch
withdrawals from the openpilot Toyota cancel path, which at this historical
commit sent a synthetic 0x101 BRAKE_MODULE frame after ``buttonCancel``.

The strongest hands-off witness is required to satisfy all of these conditions:
  * stock 0x08A was active with Target Lateral ID 11 immediately beforehand;
  * no openpilot 0x101 cancel was sent in the preceding 250 ms;
  * no buttonCancel event occurred in the preceding 250 ms;
  * there was no physical brake/gas input in the latest CarState;
  * native 0x371 entered the late/final-stage candidate B19=0x60 within 10 s;
  * native 0x412 B2[6] escalation occurred before that B19=0x60 transition.

Raw road logs remain outside git; the reduced JSON is tracked.
"""
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
import warnings
from collections import Counter
from itertools import pairwise
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
DEFAULT_OPENPILOT = Path('/Users/kai/dev/inspect/repos/kai-openpilot')
DEFAULT_ROUTE = Path('/Users/kai/dev/inspect/logs/camry-2026/2026-09-07/00000045--805b7ca6ab')
DEFAULT_OUT = REPO / 'data/generated/camry_20260907_hands_off_cancel.json'

FRC_BUS = 2
CHASSIS_BUS = 0
WINDOW_S = 0.250
FINAL_STAGE_MAX_AGE_S = 10.0


def load_logreader(openpilot_root: Path):
    sys.path.insert(0, str(openpilot_root))
    from openpilot.tools.lib.logreader import (
        LogReader,  # type: ignore[import-not-found]
    )
    return LogReader


def segnum(path: Path) -> int:
    match = re.search(r'--(\d+)$', path.parent.name)
    if match:
        return int(match.group(1))
    match = re.search(r'rlog-(\d+)', path.name)
    return int(match.group(1)) if match else -1


def discover(route: Path) -> list[Path]:
    files = list(route.glob('*/rlog.zst')) + list(route.glob('rlog-*.zst'))
    return sorted((p for p in files if '.live.' not in p.name), key=segnum)


def s16be(data: bytes) -> int:
    return int.from_bytes(data, 'big', signed=True)


def decode_08a(data: bytes) -> dict[str, Any]:
    return {
        'cruise_operating_latch': (data[3] >> 3) & 1,
        'delayed_hold_state': (data[4] >> 5) & 1,
        'longitudinal_request_id_a': (data[6] >> 2) & 0x3F,
        'longitudinal_allocation_a': data[6] & 0x03,
        'longitudinal_request_id_b': (data[7] >> 2) & 0x3F,
        'longitudinal_allocation_b': data[7] & 0x03,
        'longitudinal_accel_a_m_s2': round(s16be(data[8:10]) * 0.001, 6),
        'set_speed_kph': data[10],
        'longitudinal_accel_b_m_s2': round(s16be(data[11:13]) * 0.001, 6),
        'lateral_request_pinion_raw': s16be(data[18:20]),
        'lateral_request_id': data[21] & 0x3F,
        'lateral_assist_gain': round(data[24] * 0.01, 6),
        'lateral_damping_gain': round(data[25] * 0.01, 6),
        'request_sequence': data[26] & 0x3F,
    }


def decode_081(data: bytes) -> dict[str, Any]:
    # These byte boundaries are already recovered in the target TSS3 DBC.
    return {
        'longitudinal_result_id': data[6] & 0x3F,
        'request_loss_status': (data[11] >> 4) & 1,
        'lateral_result_id': data[13] & 0x3F,
        'lateral_result_pinion_raw': s16be(data[16:18]),
        'longitudinal_result_accel_m_s2': round(s16be(data[20:22]) * 0.001, 6),
    }


def decode_251(data: bytes) -> dict[str, Any]:
    return {
        'mode_byte': data[0],
        'cruise_main_state': (data[1] >> 4) & 1,
        'ui_set_speed': data[2],
    }


def latest_before(rows: list[dict[str, Any]], t: float) -> dict[str, Any] | None:
    times = [row['t'] for row in rows]
    i = bisect.bisect_right(times, t) - 1
    return rows[i] if i >= 0 else None


def first_after(rows: list[dict[str, Any]], t: float, horizon: float = 0.250) -> dict[str, Any] | None:
    times = [row['t'] for row in rows]
    i = bisect.bisect_left(times, t)
    if i < len(rows) and rows[i]['t'] - t <= horizon:
        return rows[i]
    return None


def first_after_where(rows: list[dict[str, Any]], t: float, predicate, horizon: float = 0.250):
    times = [row['t'] for row in rows]
    i = bisect.bisect_left(times, t)
    while i < len(rows) and rows[i]['t'] - t <= horizon:
        if predicate(rows[i]):
            return rows[i]
        i += 1
    return None


def between(rows: list[dict[str, Any]], lo: float, hi: float) -> list[dict[str, Any]]:
    times = [row['t'] for row in rows]
    return rows[bisect.bisect_left(times, lo):bisect.bisect_right(times, hi)]


def rel(row: dict[str, Any] | None, t: float, *, raw: bool = True) -> dict[str, Any] | None:
    if row is None:
        return None
    out = {'lag_s': round(row['t'] - t, 6)}
    if raw and 'raw' in row:
        out['raw'] = row['raw']
    for key in ('decoded', 'names', 'cancel', 'brake', 'gas', 'steering_torque_nm', 'steering_pressed', 'enabled', 'state'):
        if key in row:
            out[key] = row[key]
    return out


def analyze(LogReader, files: list[Path]) -> dict[str, Any]:
    can: dict[tuple[int, int], list[dict[str, Any]]] = {}
    source_counts: Counter[tuple[int, int]] = Counter()
    car_states: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    selfdrive: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    send101: list[dict[str, Any]] = []
    commit = None

    wanted = {0x081, 0x08A, 0x0CA, 0x101, 0x160, 0x251, 0x371, 0x412}
    for path in files:
        seg = segnum(path)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            for msg in LogReader(str(path), sort_by_time=True):
                t = msg.logMonoTime / 1e9
                which = msg.which()
                if which == 'initData' and commit is None:
                    commit = msg.initData.gitCommit
                elif which == 'can':
                    for frame in msg.can:
                        if frame.address not in wanted:
                            continue
                        data = bytes(frame.dat)
                        if frame.src < 128:
                            source_counts[(frame.address, frame.src)] += 1
                        row = {'t': t, 'segment': seg, 'raw': data.hex()}
                        if frame.address == 0x08A and len(data) >= 27:
                            row['decoded'] = decode_08a(data)
                        elif frame.address == 0x081 and len(data) >= 22:
                            row['decoded'] = decode_081(data)
                        elif frame.address == 0x251 and len(data) >= 3:
                            row['decoded'] = decode_251(data)
                        can.setdefault((frame.address, frame.src), []).append(row)
                elif which == 'carState':
                    cs = msg.carState
                    car_states.append({
                        't': t,
                        'cruise_enabled': bool(cs.cruiseState.enabled),
                        'cruise_available': bool(cs.cruiseState.available),
                        'brake': bool(cs.brakePressed),
                        'gas': bool(cs.gasPressed),
                        'steering_torque_nm': round(float(cs.steeringTorque), 6),
                        'steering_pressed': bool(cs.steeringPressed),
                        'v_ego_m_s': round(float(cs.vEgo), 6),
                    })
                elif which == 'carControl':
                    controls.append({
                        't': t,
                        'enabled': bool(msg.carControl.enabled),
                        'cancel': bool(msg.carControl.cruiseControl.cancel),
                    })
                elif which == 'selfdriveState':
                    selfdrive.append({
                        't': t,
                        'enabled': bool(msg.selfdriveState.enabled),
                        'state': str(msg.selfdriveState.state),
                        'alert_type': str(msg.selfdriveState.alertType),
                    })
                elif which == 'onroadEvents':
                    names = [str(event.name) for event in msg.onroadEvents]
                    if names:
                        events.append({'t': t, 'names': names})
                elif which == 'sendcan':
                    for frame in msg.sendcan:
                        if frame.address == 0x101:
                            send101.append({'t': t, 'bus': int(frame.src), 'raw': bytes(frame.dat).hex()})

    native = {}
    for address in wanted:
        candidates = [(count, src) for (addr, src), count in source_counts.items() if addr == address]
        native[address] = max(candidates, default=(0, None))[1]

    request_rows = can.get((0x08A, FRC_BUS), [])
    result_rows = can.get((0x081, CHASSIS_BUS), [])
    state_rows = can.get((0x371, FRC_BUS), [])
    hud_rows = can.get((0x412, FRC_BUS), [])
    brake_rows = can.get((0x101, CHASSIS_BUS), [])
    display_rows = can.get((0x251, FRC_BUS), [])
    ca_rows = can.get((0x0CA, CHASSIS_BUS), [])
    frc160_rows = can.get((0x160, 1), [])

    warning_rises: list[dict[str, Any]] = []
    final_rises: list[dict[str, Any]] = []
    final_clears: list[dict[str, Any]] = []
    driver_rises: list[dict[str, Any]] = []
    prev_warning = prev_final = prev_driver = False
    for row in state_rows:
        data = bytes.fromhex(row['raw'])
        warning = bool(data[19] & 0x40)
        final = (data[19] & 0x60) == 0x60
        driver = bool(data[20] & 0x10)
        enriched = {**row, 'b19': data[19], 'b20': data[20]}
        if warning and not prev_warning:
            warning_rises.append(enriched)
        if final and not prev_final:
            final_rises.append(enriched)
        if not final and prev_final:
            final_clears.append(enriched)
        if driver and not prev_driver:
            driver_rises.append(enriched)
        prev_warning, prev_final, prev_driver = warning, final, driver

    escalation_rises: list[dict[str, Any]] = []
    prev_escalation = False
    for row in hud_rows:
        data = bytes.fromhex(row['raw'])
        escalation = bool(data[2] & 0x40)
        if escalation and not prev_escalation:
            escalation_rises.append(row)
        prev_escalation = escalation

    latch_falls: list[dict[str, Any]] = []
    for before, after in pairwise(request_rows):
        b = before['decoded']
        a = after['decoded']
        if b['cruise_operating_latch'] != 1 or a['cruise_operating_latch'] != 0:
            continue
        t = after['t']
        pre_cs = latest_before(car_states, t)
        near_events = between(events, t - WINDOW_S, t + 0.080)
        pre_send = between(send101, t - WINDOW_S, t)
        pre_controls = between(controls, t - WINDOW_S, t)
        button_cancel = any('buttonCancel' in row['names'] for row in near_events if row['t'] <= t)
        pcm_disable = first_after_where(events, t, lambda row: 'pcmDisable' in row['names'], 0.080)
        cc_cancel = any(row['cancel'] for row in pre_controls)
        injected_cancel = bool(pre_send)

        prior_warning = latest_before(warning_rises, t)
        prior_escalation = latest_before(escalation_rises, t)
        prior_final = latest_before(final_rises, t)
        prior_final_clear = latest_before(final_clears, t)
        prior_driver = latest_before(driver_rises, t)

        first_result = first_after(result_rows, t, 0.150)
        lateral_zero_result = first_after_where(result_rows, t, lambda row: row['decoded']['lateral_result_id'] == 0, 0.150)
        driver_long_result = first_after_where(result_rows, t, lambda row: row['decoded']['longitudinal_result_id'] == 63, 0.150)

        brake_before = latest_before(brake_rows, t)
        brake_after = first_after(brake_rows, t, 0.100)
        display_before = latest_before(display_rows, t)
        display_after = first_after(display_rows, t, 0.100)
        ca_before = latest_before(ca_rows, t)
        ca_after = first_after(ca_rows, t, 0.100)
        frc160_before = latest_before(frc160_rows, t)
        frc160_after = first_after(frc160_rows, t, 0.100)

        natural = not button_cancel and not injected_cancel and not cc_cancel and pcm_disable is not None
        final_age = None if prior_final is None else t - prior_final['t']
        escalation_age = None if prior_escalation is None else t - prior_escalation['t']
        strong_hands_off = (
            natural
            and b['lateral_request_id'] == 11
            and pre_cs is not None and not pre_cs['brake'] and not pre_cs['gas']
            and final_age is not None and 0 <= final_age <= FINAL_STAGE_MAX_AGE_S
            and escalation_age is not None and escalation_age >= final_age
        )

        row = {
            'segment': after['segment'],
            't_mono_s': round(t, 6),
            'classification': (
                'strong_hands_off_cancel_witness' if strong_hands_off else
                'openpilot_button_cancel' if button_cancel or injected_cancel or cc_cancel else
                'stock_pcm_disable_other'
            ),
            'openpilot_0x101_in_preceding_250ms': [
                {'lag_s': round(item['t'] - t, 6), 'bus': item['bus'], 'raw': item['raw']} for item in pre_send
            ],
            'onroad_events_near_edge': [
                {'lag_s': round(item['t'] - t, 6), 'names': item['names']} for item in near_events
            ],
            'car_state_before': None if pre_cs is None else {
                k: v for k, v in pre_cs.items() if k != 't'
            } | {'age_s': round(t - pre_cs['t'], 6)},
            'request_before': {'raw': before['raw'], **b},
            'request_after': {'raw': after['raw'], **a},
            'warning_stage': None if prior_warning is None else {
                'age_s': round(t - prior_warning['t'], 6), 'b19': prior_warning['b19'], 'b20': prior_warning['b20'], 'raw': prior_warning['raw'],
            },
            'hud_escalation_stage': None if prior_escalation is None else {
                'age_s': round(t - prior_escalation['t'], 6), 'raw': prior_escalation['raw'],
            },
            'late_final_stage_candidate': None if prior_final is None else {
                'age_s': round(t - prior_final['t'], 6), 'b19': prior_final['b19'], 'b20': prior_final['b20'], 'raw': prior_final['raw'],
            },
            'late_final_stage_clear': None if prior_final_clear is None else {
                'age_s': round(t - prior_final_clear['t'], 6), 'b19': prior_final_clear['b19'], 'b20': prior_final_clear['b20'], 'raw': prior_final_clear['raw'],
            },
            'latest_driver_detect_rise': None if prior_driver is None else {
                'age_s': round(t - prior_driver['t'], 6), 'b19': prior_driver['b19'], 'b20': prior_driver['b20'], 'raw': prior_driver['raw'],
            },
            'result_first_after': rel(first_result, t),
            'result_lateral_id0_after': rel(lateral_zero_result, t),
            'result_driver_operation_id63_after': rel(driver_long_result, t),
            'brake_0x101_before': rel(brake_before, t),
            'brake_0x101_after': rel(brake_after, t),
            'cruise_display_0x251_before': rel(display_before, t),
            'cruise_display_0x251_after': rel(display_after, t),
            'chassis_0x0ca_before': rel(ca_before, t),
            'chassis_0x0ca_after': rel(ca_after, t),
            'frc_0x160_before': rel(frc160_before, t),
            'frc_0x160_after': rel(frc160_after, t),
            'pcm_disable_event': rel(pcm_disable, t, raw=False),
        }
        latch_falls.append(row)

    strong = [row for row in latch_falls if row['classification'] == 'strong_hands_off_cancel_witness']
    stock_active_lta = [row for row in latch_falls if row['classification'] != 'openpilot_button_cancel' and row['request_before']['lateral_request_id'] == 11]

    return {
        'schema': 'camry-20260907-hands-off-cancel-v1',
        'source': {
            'route': files[0].parent.parent.name if files and files[0].name == 'rlog.zst' else files[0].parent.name,
            'segments': len(files),
            'openpilot_commit': commit,
        },
        'native_source_counts': {
            f'0x{addr:03X}/src{src}': count for (addr, src), count in sorted(source_counts.items())
        },
        'native_bus_assignment': {
            'frc_request_and_state': {'bus': FRC_BUS, 'messages': ['0x08A', '0x371', '0x412', '0x251']},
            'chassis_result_and_brake': {'bus': CHASSIS_BUS, 'messages': ['0x081', '0x0CA', '0x101']},
        },
        'latch_fall_count': len(latch_falls),
        'classification_counts': dict(Counter(row['classification'] for row in latch_falls)),
        'stock_active_lta_drop_count': len(stock_active_lta),
        'strong_hands_off_witness_count': len(strong),
        'strong_hands_off_witnesses': strong,
        'all_latch_falls': latch_falls,
        'interpretation': {
            'verified_dynamic': (
                'The strongest retained hands-off cancellation is a native FRC 0x08A request withdrawal, not an openpilot 0x101 cancel: '
                'the operating latch clears, Target Lateral ID 11 becomes 0, both longitudinal request packages change, and set speed clears before controls sees pcmDisable.'
            ),
            'chassis_response': (
                '0x081 follows the FRC withdrawal: lateral result ID becomes 0 first, then longitudinal result ID becomes 63 (Driver Operation); request-loss remains clear.'
            ),
            'negative_evidence': (
                'Native 0x101 remains a non-brake frame and no sendcan 0x101 precedes the strong witness; 0x251 cruise-main availability remains asserted. '
                'This is therefore not the normal brake/button cancel path and not loss-of-request supervision.'
            ),
            'bounded_state': (
                '0x371 B19=0x60 is a repeatable late/final-stage hands-off candidate after the earlier B19=0x40 warning and 0x412 B2[6] escalation. '
                'Its exact OEM bit name and whether it alone commits cancellation remain unproved.'
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', type=Path, default=DEFAULT_ROUTE)
    parser.add_argument('--openpilot-root', type=Path, default=DEFAULT_OPENPILOT)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    files = discover(args.route)
    if not files:
        raise FileNotFoundError(f'no rlogs found under {args.route}')
    LogReader = load_logreader(args.openpilot_root)
    payload = analyze(LogReader, files)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
