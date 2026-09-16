#!/usr/bin/env python3
"""Audit whether retained Camry 0x160 quantities establish command authority.

Offline only. Source direction, ego-motion agreement, temporal ordering, and
actual host replacement are tested separately. Correlation, a valid CRC, or a
Panda TX return never counts as evidence of actuator acceptance.
"""
from __future__ import annotations

import argparse
import binascii
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / 'tests/fixtures/camry_2026_longitudinal_role.jsonl.gz'
OUTPUT = ROOT / 'data/generated/camry_2026_longitudinal_role.json'
NATIVE = {
    'a': 'camry_relay_route_can_20260827.ndjson.gz',
    'b': 'camry_relay_lta_confirm_route_can_20260827.ndjson.gz',
}
STEP_NS = 25_000_000
MAX_AGE_NS = 120_000_000


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def signed(value, bits: int):
    if not 1 <= bits <= 32:
        raise ValueError('signed width must be 1..32 bits')
    return (value + (1 << (bits - 1))) % (1 << bits) - (1 << (bits - 1))


def crc_valid(data: bytes) -> bool:
    return len(data) == 32 and int.from_bytes(data[:2], 'little') == binascii.crc_hqx(data[2:] + b'\x60\x01', 0xFFFF)


def quantities_160(a: np.ndarray) -> dict[str, np.ndarray]:
    d = a[:, 2:]
    if d.shape[1] != 32:
        raise ValueError('0x160 must have 32 payload bytes')
    return {
        'fine': signed(((d[:, 4] << 8) | d[:, 5]) & 0x7FFF, 15) * .001,
        'b12_candidate': -signed(d[:, 12] & 0x7F, 7) * .1,
        'speed_candidate_mps': (((((d[:, 7] << 16) | (d[:, 8] << 8) | d[:, 9]) >> 5) & 0x7FFF) * .01 - 67.67) / 3.6,
    }


def quantity_ca(a: np.ndarray) -> np.ndarray:
    d = a[:, 2:]
    return signed((d[:, 7] << 8) | d[:, 8], 16) * .001


def wheel_speed(a: np.ndarray) -> np.ndarray:
    d = a[:, 2:]
    value = np.mean([(((d[:, i] << 8) | d[:, i + 1]) & 0x7FFF) * .01 - 67.67
                     for i in (0, 2, 4, 6)], axis=0) / 3.6
    valid = np.all((d[:, (0, 2, 4, 6)] & 0x80) == 0, axis=1)
    # Invalid wheel data is neither zero speed nor independent motion evidence.
    return np.where(valid, value, np.nan)


def hold(a: np.ndarray, values: np.ndarray, source: int, times: np.ndarray,
         max_age: int = MAX_AGE_NS) -> tuple[np.ndarray, np.ndarray]:
    """Last observation, never a future sample or one across a source gap."""
    mask = a[:, 0] == source
    at, av = a[mask, 1], values[mask]
    if not len(at):
        return np.zeros(len(times)), np.zeros(len(times), dtype=bool)
    if np.any(np.diff(at) < 0):
        raise ValueError('source times are not ordered')
    idx = np.searchsorted(at, times, side='right') - 1
    valid = idx >= 0
    idx = np.clip(idx, 0, len(at) - 1)
    valid &= (times >= at[idx]) & (times - at[idx] <= max_age)
    return av[idx], valid


def stats(x, y) -> dict:
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) != len(y):
        raise ValueError('unaligned vectors')
    good = np.isfinite(x) & np.isfinite(y)
    x, y = x[good], y[good]
    out = {'n': len(x)}
    if not len(x):
        return out
    out.update(median_abs_error=float(np.median(np.abs(x - y))),
               p95_abs_error=float(np.quantile(np.abs(x - y), .95)))
    if len(x) > 2 and np.std(x) > 1e-9 and np.std(y) > 1e-9:
        slope, offset = np.polyfit(x, y, 1)
        out.update(r=float(np.corrcoef(x, y)[0, 1]), slope=float(slope), offset=float(offset))
    return out


def load_native(label: str) -> tuple[dict, dict]:
    path = ROOT / 'targets/camry-2026/raw-20260827' / NATIVE[label]
    rows = defaultdict(list)
    with gzip.open(path, 'rt') as stream:
        for line in stream:
            segment, nanos, bus, address, text = json.loads(line)
            if (bus == 0 and address in (0x08A, 0x0AA, 0x0CA, 0x13C)) or (bus == 1 and address == 0x160):
                data = bytes.fromhex(text)
                rows[f'can_{address:03x}_{bus}_{len(data)}'].append([segment, nanos, *data])
    return {k: np.array(v, dtype=np.int64) for k, v in rows.items()}, {
        'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def load_fixture(path: Path) -> tuple[dict, dict]:
    groups = defaultdict(lambda: defaultdict(list))
    with gzip.open(path, 'rt') as stream:
        header = json.loads(next(stream))
        if header.get('schema') != 'camry-longitudinal-role-fixture-v1':
            raise ValueError('unsupported fixture schema')
        for line in stream:
            source, nanos, kind, payload = json.loads(line)
            group = header['sources'][source]['group']
            if kind in ('can', 'sendcan'):
                for bus, address, text in payload:
                    data = bytes.fromhex(text)
                    groups[group][f'{kind}_{address:03x}_{bus}_{len(data)}'].append([source, nanos, *data])
            else:
                groups[group][kind].append([source, nanos, *payload])
    return header, {g: {k: np.array(v, dtype=float if k in ('carState', 'carControl') else np.int64)
                        for k, v in rows.items()} for g, rows in groups.items()}


def sensor_summary(z: dict, camera_bus: int, chassis_bus: int) -> dict:
    camera = z[f'can_160_{camera_bus}_32']
    measurement = z[f'can_13c_{chassis_bus}_8']
    state = z[f'can_08a_{chassis_bus}_32']
    wheels = z[f'can_0aa_{chassis_bus}_8']
    q = quantities_160(camera)
    md = measurement[:, 2:]
    measured = signed(((md[:, 0] << 8) | md[:, 1]) & 0x7FFF, 15) * .001
    active = (state[:, 5] & 8) != 0
    rows, speed_rows, actual_rows = [], [], []
    for source in np.unique(camera[:, 0]):
        mask = camera[:, 0] == source
        times = camera[mask, 1]
        y, gy = hold(measurement, measured, source, times, 100_000_000)
        a, ga = hold(state, active, source, times, 100_000_000)
        g = gy & ga
        rows.extend(zip(q['fine'][mask][g], y[g], a[g]))
        v, gv = hold(wheels, wheel_speed(wheels), source, times, 80_000_000)
        g = gv & (q['speed_candidate_mps'][mask] > (6900 * .01 - 67.67) / 3.6)
        speed_rows.extend(zip(q['speed_candidate_mps'][mask][g], v[g]))
        if 'carState' in z:
            cs = z['carState']
            cv, gcv = hold(cs, cs[:, 2], source, times, 100_000_000)
            ca, gca = hold(cs, cs[:, 3], source, times, 100_000_000)
            enabled, ge = hold(cs, cs[:, 6], source, times, 100_000_000)
            g = gcv & gca & ge & (cv > 2) & (enabled == 0)
            actual_rows.extend(zip(q['fine'][mask][g], ca[g]))
    rows, speed_rows = np.array(rows), np.array(speed_rows)
    out = {'fine_vs_chassis_13c': {name: stats(rows[g, 0], rows[g, 1]) for name, g in (
        ('all', np.ones(len(rows), dtype=bool)), ('cruise_off', rows[:, 2] == 0), ('cruise_on', rows[:, 2] != 0))},
        'speed_vs_raw_wheels': stats(speed_rows[:, 0], speed_rows[:, 1])}
    if actual_rows:
        actual = np.array(actual_rows)
        out['fine_vs_carState_aEgo_cruise_off_above_2mps'] = stats(actual[:, 0], actual[:, 1])
    return out


def native_lag(z: dict, camera_bus: int, chassis_bus: int) -> dict:
    camera, ca, state = z[f'can_160_{camera_bus}_32'], z[f'can_0ca_{chassis_bus}_32'], z[f'can_08a_{chassis_bus}_32']
    x = quantities_160(camera)['b12_candidate']
    y = quantity_ca(ca)
    active = (state[:, 5] & 8) != 0
    sweep = []
    for lag in range(-500_000_000, 500_000_001, STEP_NS):
        xs, ys, dxs, dys = [], [], [], []
        for source in np.unique(camera[:, 0]):
            a = camera[camera[:, 0] == source]
            times = np.arange(a[0, 1] + 750_000_000, a[-1, 1] - 750_000_000, STEP_NS, dtype=np.int64)
            xx, gx = hold(camera, x, source, times)
            yy, gy = hold(ca, y, source, times + lag)
            aa, ga = hold(state, active, source, times)
            good = gx & gy & ga & (aa != 0)
            xs.extend(xx[good]); ys.extend(yy[good])
            # Do not form a difference across an unobserved or inactive interval.
            dg = np.convolve(good.astype(int), np.ones(9, dtype=int), 'valid') == 9 if len(good) >= 9 else np.array([], dtype=bool)
            if len(dg):
                dxs.extend((xx[8:] - xx[:-8])[dg]); dys.extend((yy[8:] - yy[:-8])[dg])
        sweep.append({'lag_ms': lag // 1_000_000, 'levels': stats(xs, ys), 'changes_200ms': stats(dxs, dys)})
    peak = max(sweep, key=lambda r: r['levels'].get('r', -2))
    zero = next(r for r in sweep if r['lag_ms'] == 0)
    return {'convention': 'corr(0x160(t), 0x0CA(t+lag)); positive means 0x160 leads; negative means it lags',
            'peak_level': peak, 'zero_lag': zero,
            'peak_level_r_gain_over_zero': peak['levels']['r'] - zero['levels']['r'],
            'timing_boundary': ('Small broad-peak gains and autocorrelated levels do not establish a unique '
                                'dataflow or ECU delay; compare changes and original transient windows.'),
            'peak_change': max(sweep, key=lambda r: r['changes_200ms'].get('r', -2)), 'sweep': sweep}


def matching_template(camera: np.ndarray, host_row: np.ndarray) -> np.ndarray | None:
    """Counter identity must also match source and a bounded preceding time."""
    segment, nanos = host_row[:2]
    eligible = ((camera[:, 0] == segment) & (camera[:, 1] <= nanos)
                & (camera[:, 1] >= nanos - 100_000_000) & (camera[:, 4] == host_row[4]))
    candidates = camera[eligible]
    return candidates[-1] if len(candidates) else None


def delivery_summary(z: dict) -> dict:
    camera, host, echo = z['can_160_2_32'], z['sendcan_160_0_32'], z['can_160_128_32']
    counts, diffs = Counter(), Counter()
    for h in host:
        counts['host_frames'] += 1
        template = matching_template(camera, h)
        if template is None:
            counts['no_recent_template'] += 1
            continue
        counts['counter_and_time_matched_template'] += 1
        different = tuple(np.flatnonzero(h[2:] != template[2:]).tolist())
        diffs[','.join(map(str, different)) or 'unchanged'] += 1
        counts['only_expected_offsets_changed'] += int(set(different) <= {0, 1, 4, 5, 12})
        counts['fine_changed'] += int(4 in different or 5 in different)
        counts['b12_changed'] += int(12 in different)
        e = echo[(echo[:, 0] == h[0]) & (echo[:, 1] >= h[1]) & (echo[:, 1] <= h[1] + 100_000_000)]
        counts['exact_payload_return_after_host_send'] += int(any(np.array_equal(a[2:], h[2:]) for a in e))
    checksums = {}
    for name, a in [('source', camera), ('host', host), ('returned_tx', echo)]:
        checksums[name] = {'n': len(a), 'valid': sum(crc_valid(bytes(row[2:].tolist())) for row in a)}
    return {'counts': dict(counts), 'changed_payload_offsets': dict(diffs), 'checksum_checks': checksums,
            'boundary': 'Panda delivery and CRC do not establish ECU command acceptance'}


def trial_comparison(z: dict) -> dict:
    camera, host, ca = z['can_160_2_32'], z['sendcan_160_0_32'], z['can_0ca_1_32']
    cq, hq = quantities_160(camera), quantities_160(host)
    cc = z['carControl']
    rows, modes = [], Counter()
    mode = z['can_251_1_8']
    for source in np.unique(host[:, 0]):
        h = host[host[:, 0] == source]
        times = np.arange(h[0, 1], h[-1, 1], STEP_NS, dtype=np.int64)
        columns, good = [], np.ones(len(times), dtype=bool)
        for a, value, age in [(camera, cq['fine'], MAX_AGE_NS), (host, hq['fine'], 60_000_000),
                              (camera, cq['b12_candidate'], MAX_AGE_NS), (host, hq['b12_candidate'], 60_000_000),
                              (ca, quantity_ca(ca), MAX_AGE_NS), (cc, cc[:, 4], MAX_AGE_NS)]:
            v, g = hold(a, value, source, times, age); columns.append(v); good &= g
        active, ga = hold(cc, cc[:, 2], source, times)
        good &= ga & (active != 0)
        rows.extend(np.column_stack(columns)[good].tolist())
        m, gm = hold(mode, mode[:, 2], source, times, 1_500_000_000)
        modes.update(f'0x{int(v):02X}' for v in m[good & gm])
    a = np.array(rows)
    out = {'n_grid_samples': len(a), 'grid_period_ms': 25, 'cruise_mode_histogram': dict(modes),
           'cruise_mode_max_age_ms': 1500, 'cruise_mode_unknown_samples': len(a) - sum(modes.values())}
    for name, i in [('native_fine', 0), ('host_fine', 1), ('native_b12', 2), ('host_b12', 3)]:
        out[f'{name}_vs_0ca_resultlike'] = stats(a[:, i], a[:, 4])
    strong = a[:, 5] <= -.75
    if strong.any():
        out['requested_deceleration_at_least_0p75'] = {
            'n': int(strong.sum()), 'host_request_range': [float(v) for v in (a[strong, 5].min(), a[strong, 5].max())],
            'ca_resultlike_range': [float(v) for v in (a[strong, 4].min(), a[strong, 4].max())],
            'host_vs_ca': stats(a[strong, 5], a[strong, 4])}
    out['boundary'] = ('The native value is an observed comparison, not a randomized counterfactual. Better native fit '
                       'invalidates the previous correlation-only proof of host authority, but cannot rule out indirect influence.')
    return out


def direction(z: dict) -> dict:
    return {f'0x{address:03X}': {str(bus): len(z.get(f'can_{address:03x}_{bus}_{32}', []))
                               for bus in (0, 1, 2, 128, 130)} for address in (0x08A, 0x0CA, 0x0C9, 0x160)}


def latest(a: np.ndarray, nanos: int) -> np.ndarray:
    """Bounded latest event across consecutive retained segments for a resume window."""
    eligible = a[(a[:, 1] <= nanos) & (a[:, 1] >= nanos - MAX_AGE_NS)]
    if not len(eligible):
        raise ValueError('resume sample lacks preceding evidence')
    return eligible[np.argmax(eligible[:, 1])]


def resume_summary(z: dict, centers: list[int]) -> list[dict]:
    camera, ca, cs, wheels = z['can_160_1_32'], z['can_0ca_0_32'], z['carState'], z['can_0aa_0_8']
    fine, qca, v = quantities_160(camera)['fine'], quantity_ca(ca), wheel_speed(wheels)
    result = []
    for center in centers:
        samples = []
        input_window = (cs[:, 1] >= center - 1_000_000_000) & (cs[:, 1] <= center + 500_000_000)
        switch = z['can_0fe_0_32']
        switch = switch[(switch[:, 1] >= center - 1_000_000_000) & (switch[:, 1] <= center + 500_000_000)]
        sw = switch[:, 2:]
        inputs = {
            'carState_samples': int(input_window.sum()), 'switch_frames': len(switch),
            'gas_asserted_samples': int(np.count_nonzero(cs[input_window, 4])),
            'brake_asserted_samples': int(np.count_nonzero(cs[input_window, 5])),
            'res_asserted_frames': int(np.count_nonzero(sw[:, 3] & 0x80)),
            'set_asserted_frames': int(np.count_nonzero(sw[:, 4] & 0x80)),
            'cancel_asserted_frames': int(np.count_nonzero(sw[:, 4] & 0x40)),
        }
        for delta in (-500, -300, -100, 0, 100, 300):
            nanos = center + delta * 1_000_000
            f, c, state, w = latest(camera, nanos), latest(ca, nanos), latest(cs, nanos), latest(wheels, nanos)
            fq = quantities_160(f[None, :])
            samples.append({'relative_to_prior_motion_threshold_ms': delta, 'camera_time_ns': int(f[1]),
                            'fine': float(fq['fine'][0]), 'b12_candidate': float(fq['b12_candidate'][0]),
                            'ca_resultlike': float(quantity_ca(c[None, :])[0]), 'wheel_mean_mps': float(wheel_speed(w[None, :])[0]),
                            'vEgo': float(state[2]), 'aEgo': float(state[3]), 'gas': bool(state[4]), 'brake': bool(state[5])})
        def first_time(a: np.ndarray, value: np.ndarray, threshold: float, center_ns: int) -> int | None:
            g = (a[:, 1] >= center_ns - 1_000_000_000) & (a[:, 1] <= center_ns + 800_000_000)
            aa, vv = a[g], value[g]
            for i in range(len(vv) - 2):
                if np.all(vv[i:i + 3] > threshold) and aa[i + 2, 1] - aa[i, 1] < 100_000_000:
                    return int(aa[i, 1])
            return None
        result.append({'prior_motion_threshold_ns': center, 'driver_inputs_minus1_to_plus0p5_seconds': inputs,
                       'raw_wheels_above_0p025_mps_ns': first_time(wheels, v, .025, center),
                       'fine_above_0p05_ns': first_time(camera, fine, .05, center),
                       'ca_above_0p5_ns': first_time(ca, qca, .5, center), 'samples': samples})
    return result


def rounded(value):
    if isinstance(value, (float, np.floating)):
        if not np.isfinite(value):
            raise ValueError('nonfinite output')
        return round(float(value), 9)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, dict):
        return {str(k): rounded(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [rounded(v) for v in value]
    return value


def build(fixture: Path) -> dict:
    header, groups = load_fixture(fixture)
    report = {
        'schema': 'camry-longitudinal-role-audit-v1', 'vehicle_access': False,
        'fixture': {'path': 'tests/fixtures/camry_2026_longitudinal_role.jsonl.gz', 'sha256': sha(fixture)},
        'sources': header['sources'],
        'methods': {'alignment': 'preceding observations only, source-bound, bounded age; no frame-counter-only pairing',
                    'lag': '25 ms grid, +/-500 ms sweep, no interpolation across source gaps; 200 ms differences require all intermediate grid samples valid',
                    'timing_limit': header['timestamp_boundary'],
                    'semantic_limit': 'Decoded numerical candidates are not OEM names or receiver contracts.'},
        'native': {}, 'trials': {},
        'historical_relay_direction': direction(groups['2d']),
        'stock_resumes': {g: resume_summary(groups[g], header['resume_centers_ns'][g]) for g in ('3b', '3c')},
    }
    for label in NATIVE:
        z, source = load_native(label)
        camera = z['can_160_1_32']
        report['native'][label] = {'source': source, 'camera_frames': len(camera),
                                  'valid_camera_crc': sum(crc_valid(bytes(row[2:].tolist())) for row in camera),
                                  **sensor_summary(z, 1, 0), 'b12_vs_ca_lag': native_lag(z, 1, 0)}
    for label in ('d1', 'd4'):
        report['trials'][label] = {**sensor_summary(groups[label], 2, 1),
                                   'delivery': delivery_summary(groups[label]), 'comparison': trial_comparison(groups[label])}
    report['conclusions'] = {
        'fine_field': 'Strongly supported as ego-acceleration/measurement-like on this Camry, not a demonstrated independent acceleration demand.',
        'b12_field': 'Closely follows a chassis acceleration/result-like channel; native timing and the untouched-camera comparison do not establish host command authority.',
        'whole_pdu': 'FRC-origin ADAS publication containing ego-state information; a report to the perception/radar domain is the leading interpretation. The consumer and every field are not recovered.',
        'not_proven': ['All 0x160 fields are telemetry', 'Exact OEM signal names and validity contracts',
                       'An exact byte-copy from a different FRC command', 'Which ECU physically originates 0x0CA',
                       'Receiver acceptance under healthy adaptive cruise', 'A validated replacement longitudinal target'],
        'withdrawn': 'The prior claim that d4 correlation proves combined B4:B5+B12 influence on the protected plane.',
        'implementation': 'No vehicle-control, Panda, authentication, or firmware changes in this audit.',
    }
    return rounded(report)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, default=FIXTURE)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = build(args.fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(args.output)


if __name__ == '__main__':
    main()
