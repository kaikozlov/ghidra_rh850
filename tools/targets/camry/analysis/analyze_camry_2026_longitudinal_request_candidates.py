#!/usr/bin/env python3
"""Rank 2026 Camry longitudinal request candidates from retained evidence.

Offline only. This joins three independent evidence planes:
  * complete tracked Aug-27 relay-correct CAN captures,
  * the retained Sep-4 healthy-DRCC resume fixture, and
  * generated Toyota GTS+ TSS/brake request vocabulary.

Raw Panda bus numbers are never compared across harness eras without an explicit
physical-network normalization. No transmitter, vehicle session, or firmware
mutation is used here.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'data/generated/camry_2026_longitudinal_request_candidates.json'
ROLE_FIXTURE = ROOT / 'tests/fixtures/camry_2026_longitudinal_role.jsonl.gz'
ROLE_REPORT = ROOT / 'data/generated/camry_2026_longitudinal_role.json'
TOPOLOGY = ROOT / 'data/generated/camry_2026_stock_harness_topology.json'
GTS = ROOT / 'data/generated/gtsplus_2026/tss3_control_ownership_surface.json'
CENSUS = ROOT / 'data/generated/camry_2026_upstream_request_field_census.json'
DRIVES = {
    'drive_a': ROOT / 'targets/camry-2026/raw-20260827/camry_relay_route_can_20260827.ndjson.gz',
    'drive_b': ROOT / 'targets/camry-2026/raw-20260827/camry_relay_lta_confirm_route_can_20260827.ndjson.gz',
}
DIRECT_FRC_IDS = (0x020, 0x160, 0x230, 0x440)
# Sep-1 FRC CommunicationControl suppression + relay-open direction recovery.
# These recurring protected Toyota-Bus-4 PDUs vanished with FRC normal TX and
# are native on the upstream side of the temporary CAN0/CAN1 repin.
FRC_DEPENDENT_BUS4_IDS = (
    0x08A, 0x0C9, 0x13F, 0x159, 0x15A, 0x198, 0x19C, 0x19F, 0x1B1, 0x1B2,
    0x1BC, 0x1D9, 0x1DE, 0x1DF, 0x20F, 0x251, 0x252, 0x261, 0x274, 0x275,
    0x276, 0x277, 0x27B, 0x27C, 0x28A, 0x28B, 0x28C, 0x28D, 0x317, 0x36D,
    0x371, 0x411, 0x412, 0x414, 0x489, 0x48A, 0x48B, 0x494, 0x4D3, 0x5AE,
    0x5AF, 0x5F1, 0x5F6, 0x5F7, 0x5F9, 0x608, 0x68D,
)
LAGS_MS = tuple(range(-300, 301, 25))
MAX_JOIN_NS = 30_000_000

sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis.analyze_camry_2026_longitudinal_role import (
    latest,
    load_fixture,
)


def sha(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def s16be(data: bytes | np.ndarray, offset: int) -> int:
    if isinstance(data, np.ndarray):
        a, b = int(data[offset]), int(data[offset + 1])
        raw = (a << 8) | b
        return raw - 0x10000 if raw & 0x8000 else raw
    return int.from_bytes(data[offset:offset + 2], 'big', signed=True)


def request_word(data: bytes | np.ndarray) -> float:
    return s16be(data, 8) * .001


def ca_result(data: bytes | np.ndarray) -> float:
    return s16be(data, 7) * .001


def load_august(path: Path) -> dict:
    direct = defaultdict(lambda: defaultdict(list))
    protected = defaultdict(lambda: defaultdict(list))
    a8 = defaultdict(list)
    ca = defaultdict(list)
    c9 = defaultdict(list)
    m5af = defaultdict(list)
    with gzip.open(path, 'rt') as f:
        for line in f:
            seg, nanos, bus, address, text = json.loads(line)
            data = bytes.fromhex(text)
            if bus == 1 and address in DIRECT_FRC_IDS:
                direct[address][seg].append((nanos, data))
            if bus == 2 and address in FRC_DEPENDENT_BUS4_IDS:
                protected[(address, len(data))][seg].append((nanos, data))
            if bus == 2 and address == 0x08A and len(data) == 32:
                a8[seg].append((nanos, data))
            elif bus == 0 and address == 0x0CA and len(data) == 32:
                ca[seg].append((nanos, data))
            elif bus == 2 and address == 0x0C9 and len(data) == 32:
                c9[seg].append((nanos, data))
            elif bus == 2 and address == 0x5AF and len(data) == 32:
                m5af[seg].append((nanos, data))
    for family in (direct, protected):
        for streams in family.values():
            for rows in streams.values():
                rows.sort()
    for family in (a8, ca, c9, m5af):
        for rows in family.values():
            rows.sort()
    return {'direct': direct, 'protected': protected, 'a8': a8, 'ca': ca, 'c9': c9, 'm5af': m5af}


def nearest(rows: list[tuple[int, bytes]], nanos: int, max_gap_ns: int = MAX_JOIN_NS):
    if not rows:
        return None
    ts = [r[0] for r in rows]
    i = bisect.bisect_left(ts, nanos)
    choices = [j for j in (i - 1, i) if 0 <= j < len(rows)]
    if not choices:
        return None
    j = min(choices, key=lambda k: abs(ts[k] - nanos))
    return rows[j] if abs(ts[j] - nanos) <= max_gap_ns else None


def stats(x, y) -> dict:
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return {'n': len(x), 'r': None}
    slope, intercept = np.polyfit(x, y, 1)
    return {'n': len(x), 'r': round(float(np.corrcoef(x, y)[0, 1]), 9),
            'slope': round(float(slope), 9), 'intercept': round(float(intercept), 9)}


def byte_fields(rows: list[tuple[int, bytes]]):
    data = np.asarray([list(d) for _, d in rows], dtype=np.uint8)
    length = data.shape[1]
    for width in (1, 2, 3, 4):
        for offset in range(length - width + 1):
            chunk = data[:, offset:offset + width]
            for order in ('big', 'little'):
                if order == 'big':
                    weights = 1 << (8 * np.arange(width - 1, -1, -1, dtype=np.uint64))
                else:
                    weights = 1 << (8 * np.arange(width, dtype=np.uint64))
                unsigned = (chunk.astype(np.uint64) @ weights).astype(np.float64)
                yield f'B{offset}:B{offset + width - 1}/u{width * 8}/{order}', unsigned
                sign = 1 << (width * 8 - 1)
                signed = np.where(unsigned >= sign, unsigned - (1 << (width * 8)), unsigned)
                yield f'B{offset}:B{offset + width - 1}/s{width * 8}/{order}', signed


def screen_direct_frc(loaded: dict) -> dict:
    per_drive = {}
    for drive, z in loaded.items():
        rows_out = []
        for address in DIRECT_FRC_IDS:
            by_seg = z['direct'][address]
            if not by_seg:
                continue
            # All source PDUs use a stable length per ID. Evaluate fields segment-locally,
            # preserving the raw source cadence and never joining across segment boundaries.
            field_data: dict[str, list[np.ndarray]] = defaultdict(list)
            lag_targets: dict[int, list[np.ndarray]] = defaultdict(list)
            lag_masks: dict[int, list[np.ndarray]] = defaultdict(list)
            total = 0
            for seg, rows in by_seg.items():
                if seg not in z['a8']:
                    continue
                total += len(rows)
                fields = list(byte_fields(rows))
                for key, values in fields:
                    field_data[key].append(values)
                source_times = np.asarray([t for t, _ in rows], dtype=np.int64)
                target_rows = z['a8'][seg]
                target_times = np.asarray([t for t, _ in target_rows], dtype=np.int64)
                target_data = np.asarray([list(d) for _, d in target_rows], dtype=np.uint8)
                target_values = np.asarray([request_word(d) for _, d in target_rows], dtype=float)
                for lag in LAGS_MS:
                    query = source_times + lag * 1_000_000
                    hi = np.searchsorted(target_times, query)
                    lo = np.clip(hi - 1, 0, len(target_times) - 1)
                    hc = np.clip(hi, 0, len(target_times) - 1)
                    ix = np.where(np.abs(target_times[lo] - query) <= np.abs(target_times[hc] - query), lo, hc)
                    valid = (np.abs(target_times[ix] - query) <= MAX_JOIN_NS) & ((target_data[ix, 3] & 0x08) != 0)
                    lag_targets[lag].append(target_values[ix])
                    lag_masks[lag].append(valid)
            fields = {k: np.concatenate(v) for k, v in field_data.items()}
            targets = {k: np.concatenate(v) for k, v in lag_targets.items()}
            masks = {k: np.concatenate(v) for k, v in lag_masks.items()}
            for key, values in fields.items():
                if np.std(values) == 0:
                    continue
                best = None
                for lag in LAGS_MS:
                    good = masks[lag]
                    if good.sum() < 100 or np.std(values[good]) == 0 or np.std(targets[lag][good]) == 0:
                        continue
                    r = float(np.corrcoef(values[good], targets[lag][good])[0, 1])
                    row = (abs(r), r, lag, int(good.sum()))
                    if best is None or row[0] > best[0]:
                        best = row
                if best is not None:
                    rows_out.append({'address': f'0x{address:03X}', 'field': key,
                                     'abs_r': round(best[0], 9), 'r': round(best[1], 9),
                                     'lag_ms': best[2], 'n': best[3], 'source_frames': total,
                                     'unique': len(np.unique(values))})
        rows_out.sort(key=lambda r: (-r['abs_r'], r['address'], r['field']))
        per_drive[drive] = rows_out

    reproduced = []
    indexes = [{(r['address'], r['field']): r for r in per_drive[d]} for d in DRIVES]
    for key in indexes[0].keys() & indexes[1].keys():
        a, b = indexes[0][key], indexes[1][key]
        if a['r'] * b['r'] <= 0:
            continue
        reproduced.append({'address': key[0], 'field': key[1],
                           'min_abs_r': round(min(a['abs_r'], b['abs_r']), 9),
                           'drive_a': a, 'drive_b': b})
    reproduced.sort(key=lambda r: (-r['min_abs_r'], r['address'], r['field']))
    by_id = {}
    for address in (f'0x{x:03X}' for x in DIRECT_FRC_IDS):
        rows = [r for r in reproduced if r['address'] == address]
        by_id[address] = {'best_reproduced_same_sign': rows[:5],
                          'reproduced_abs_r_ge_0p25': sum(r['min_abs_r'] >= .25 for r in rows)}
    return {
        'method': 'Every byte-aligned 8/16/24/32-bit BE/LE signed+unsigned field; nearest protected 0x08A B8:B9 request-word candidate at source time + lag; lags -300..+300 ms/25 ms; <=30 ms join; cruise latch B3[3] asserted; segment-local only.',
        'lag_convention': 'positive lag means the direct FRC PDU field is compared to a later protected 0x08A request word',
        'per_id': by_id,
        'top_reproduced': reproduced[:30],
        'boundary': 'Correlation is a screening bound, not source-code dataflow proof. Closed-loop ego-state fields can correlate strongly at long lags.',
    }


def summarize_08a(loaded: dict, census: dict) -> dict:
    drives = {}
    for drive, z in loaded.items():
        rows = [(t, d) for seg in sorted(z['a8']) for t, d in z['a8'][seg]]
        upper = np.array([s16be(d, 8) for _, d in rows], dtype=np.int64)
        lower = np.array([s16be(d, 11) for _, d in rows], dtype=np.int64)
        active = np.array([bool(d[3] & 8) for _, d in rows])
        drives[drive] = {
            'frames': len(rows), 'b8_b9_equals_b11_b12': int(np.count_nonzero(upper == lower)),
            'equality_fraction': round(float(np.mean(upper == lower)), 9),
            'signed16_raw_range': [int(upper.min()), int(upper.max())],
            'scaled_mps2_range': [round(float(upper.min() * .001), 6), round(float(upper.max() * .001), 6)],
            'cruise_active_frames': int(active.sum()),
            'cruise_active_scaled_mps2_range': [round(float(upper[active].min() * .001), 6), round(float(upper[active].max() * .001), 6)],
        }
    old = {name: row['request_word_negative_joins'] for name, row in census['drives'].items()}
    return {'drives': drives,
            'prior_independence_checks': old,
            'prior_census_boundary': census['interpretation']['field_boundary']}



def latest_preceding(a: np.ndarray, nanos: int, max_age_ns: int) -> np.ndarray:
    eligible = a[(a[:, 1] <= nanos) & (a[:, 1] >= nanos - max_age_ns)]
    if not len(eligible):
        raise ValueError('sample lacks preceding evidence inside explicit age bound')
    return eligible[np.argmax(eligible[:, 1])]

def resume_evidence(role_report: dict, groups: dict) -> list[dict]:
    out = []
    for group in ('3b', '3c'):
        z = groups[group]
        a8, ca, c9, m5af = z['can_08a_2_32'], z['can_0ca_0_32'], z['can_0c9_2_32'], z['can_5af_2_32']
        for event in role_report['stock_resumes'][group]:
            onset = int(event['raw_wheels_above_0p025_mps_ns'])
            samples = []
            for delta in (-700, -500, -300, -200, -100, 0, 100, 200, 300, 500, 700):
                t = onset + delta * 1_000_000
                ar, cr, nr, mr = latest(a8, t), latest(ca, t), latest(c9, t), latest_preceding(m5af, t, 300_000_000)
                ad, cd, nd, md = ar[2:].astype(np.uint8), cr[2:].astype(np.uint8), nr[2:].astype(np.uint8), mr[2:].astype(np.uint8)
                samples.append({'offset_from_wheel_onset_ms': delta,
                                'request_word_b8_b9_mps2': round(s16be(ad, 8) * .001, 6),
                                'request_word_b11_b12_mps2': round(s16be(ad, 11) * .001, 6),
                                'ca_resultlike_mps2': round(s16be(cd, 7) * .001, 6),
                                'c9_b12_b13_raw': int((int(nd[12]) << 8) | int(nd[13])),
                                '5af_b26_signed6': s6(int(md[26])), '5af_b24': int(md[24]),
                                'acc_state': int(ad[7]), 'target_lateral_id_low6': int(ad[21] & 0x3F)})
            out.append({'group': group, 'wheel_onset_ns': onset,
                        'driver_inputs_minus1_to_plus0p5_seconds': event['driver_inputs_minus1_to_plus0p5_seconds'],
                        'samples': samples})
    return out




def screen_protected_bus4(loaded: dict) -> dict:
    per_drive = {}
    for drive, z in loaded.items():
        rows_out = []
        for (address, dlc), by_seg in z['protected'].items():
            if address == 0x08A or dlc < 1:
                continue
            total = sum(len(rows) for rows in by_seg.values())
            if total < 100:
                continue
            # Precompute target alignment once per source stream/lag.
            seg_info = []
            for seg, rows in by_seg.items():
                targets = z['a8'].get(seg, [])
                if not targets:
                    continue
                source_times = np.asarray([t for t, _ in rows], dtype=np.int64)
                source_data = np.asarray([list(d) for _, d in rows], dtype=np.uint8)
                target_times = np.asarray([t for t, _ in targets], dtype=np.int64)
                target_data = np.asarray([list(d) for _, d in targets], dtype=np.uint8)
                target_values = np.asarray([request_word(d) for _, d in targets], dtype=float)
                aligned = {}
                for lag in LAGS_MS:
                    query = source_times + lag * 1_000_000
                    hi = np.searchsorted(target_times, query)
                    lo = np.clip(hi - 1, 0, len(target_times) - 1)
                    hc = np.clip(hi, 0, len(target_times) - 1)
                    ix = np.where(np.abs(target_times[lo] - query) <= np.abs(target_times[hc] - query), lo, hc)
                    good = (np.abs(target_times[ix] - query) <= MAX_JOIN_NS) & ((target_data[ix, 3] & 0x08) != 0)
                    aligned[lag] = (good, target_values[ix])
                seg_info.append((source_data, aligned))
            if not seg_info:
                continue
            fields = []
            for offset in range(dlc - 1):
                parts = []
                for data, _ in seg_info:
                    raw = (data[:, offset].astype(np.int64) << 8) | data[:, offset + 1].astype(np.int64)
                    parts.append(np.where(raw & 0x8000, raw - 0x10000, raw).astype(float))
                fields.append((f'B{offset}:B{offset + 1}/s16be', parts))
            for offset in range(dlc):
                parts = []
                for data, _ in seg_info:
                    raw = (data[:, offset] & 0x3F).astype(np.int64)
                    parts.append(np.where(raw & 0x20, raw - 0x40, raw).astype(float))
                fields.append((f'B{offset}/s6', parts))
            for key, xparts in fields:
                all_x = np.concatenate(xparts)
                if len(np.unique(all_x)) < 2:
                    continue
                best = None
                for lag in LAGS_MS:
                    xs, ys = [], []
                    for x, (_, aligned) in zip(xparts, seg_info):
                        good, target = aligned[lag]
                        xs.append(x[good]); ys.append(target[good])
                    x = np.concatenate(xs); y = np.concatenate(ys)
                    st = stats(x, y)
                    if st['r'] is None:
                        continue
                    row = {'lag_ms': lag, **st}
                    if best is None or abs(row['r']) > abs(best['r']):
                        best = row
                if best is not None and abs(best['r']) >= .25:
                    rows_out.append({'address': f'0x{address:03X}', 'dlc': dlc, 'field': key,
                                     'source_frames': total, 'raw_range': [int(all_x.min()), int(all_x.max())],
                                     'unique': len(np.unique(all_x)), **best})
        rows_out.sort(key=lambda r: (-abs(r['r']), r['address'], r['field']))
        per_drive[drive] = rows_out
    indexes = [{(r['address'], r['dlc'], r['field']): r for r in per_drive[d]} for d in DRIVES]
    reproduced = []
    for key in indexes[0].keys() & indexes[1].keys():
        a, b = indexes[0][key], indexes[1][key]
        if a['r'] * b['r'] <= 0:
            continue
        reproduced.append({'address': key[0], 'dlc': key[1], 'field': key[2],
                           'min_abs_r': round(min(abs(a['r']), abs(b['r'])), 9),
                           'drive_a': a, 'drive_b': b})
    reproduced.sort(key=lambda r: (-r['min_abs_r'], r['address'], r['field']))
    return {
        'method': ('All byte-aligned signed16-BE and signed-low6 fields in the 47 FRC-dependent upstream Bus-4 PDUs; '
                   '0x08A itself excluded; compared to protected 0x08A B8:B9 over -300..+300 ms/25 ms, <=30 ms joins, cruise latch asserted.'),
        'reproduced_same_sign': reproduced[:40],
        'interpretation': ('No second same-scale signed16 acceleration carrier is recovered. The strongest repeated non-0x08A companions are '
                           '0x5AF B26 and low-rate 0x5F7 B7 as signed6-like coarse states; 0x5AF separately fits ~0.25 m/s^2/count and publishes after 0x08A.'),
        'boundary': 'Correlation screens wire candidates; they do not prove producer code dataflow or OEM signal names.',
    }

def s6(value: int) -> int:
    value &= 0x3F
    return value - 64 if value & 0x20 else value


def coarse_5af_companion(loaded: dict) -> dict:
    out = {}
    for drive, z in loaded.items():
        best = None
        raw_values = [s6(d[26]) for rows in z['m5af'].values() for _, d in rows]
        for lag in LAGS_MS:
            x, y = [], []
            for seg, rows in z['m5af'].items():
                targets = z['a8'].get(seg, [])
                if not targets:
                    continue
                st = np.asarray([t for t, _ in rows], dtype=np.int64)
                tt = np.asarray([t for t, _ in targets], dtype=np.int64)
                query = st + lag * 1_000_000
                hi = np.searchsorted(tt, query)
                lo = np.clip(hi - 1, 0, len(tt) - 1)
                hc = np.clip(hi, 0, len(tt) - 1)
                ix = np.where(np.abs(tt[lo] - query) <= np.abs(tt[hc] - query), lo, hc)
                good = np.abs(tt[ix] - query) <= MAX_JOIN_NS
                for source, j, ok in zip(rows, ix, good):
                    if not ok or not (targets[j][1][3] & 0x08):
                        continue
                    x.append(s6(source[1][26]))
                    y.append(request_word(targets[j][1]))
            st = stats(x, y)
            if st['r'] is not None and (best is None or abs(st['r']) > abs(best['r'])):
                best = {'lag_ms': lag, **st}
        out[drive] = {
            'frames': sum(len(rows) for rows in z['m5af'].values()),
            'signed6_b26_values': sorted(set(raw_values)),
            'best_vs_0x08a_request_word': best,
        }
    return {
        'drives': out,
        'lag_convention': 'corr(0x5AF.B26_s6(t), 0x08A_request(t+lag)); negative best lag means 0x5AF publishes after the request word',
        'interpretation': ('B26 behaves as a coarse longitudinal companion at roughly 0.25 m/s^2/count, but its best alignment lags 0x08A by 50-75 ms. '
                           'Treat it as quantized request/result/status state, not the missing upstream acceleration command. No OEM field name is assigned.'),
    }

def c9_vs_ca(loaded: dict) -> dict:
    out = {}
    for drive, z in loaded.items():
        best = None
        for lag in LAGS_MS:
            x, y = [], []
            for seg, rows in z['c9'].items():
                targets = z['ca'].get(seg, [])
                if not targets:
                    continue
                source_times = np.asarray([t for t, _ in rows], dtype=np.int64)
                target_times = np.asarray([t for t, _ in targets], dtype=np.int64)
                query = source_times + lag * 1_000_000
                hi = np.searchsorted(target_times, query)
                lo = np.clip(hi - 1, 0, len(target_times) - 1)
                hc = np.clip(hi, 0, len(target_times) - 1)
                ix = np.where(np.abs(target_times[lo] - query) <= np.abs(target_times[hc] - query), lo, hc)
                good = np.abs(target_times[ix] - query) <= MAX_JOIN_NS
                x.extend(((d[12] << 8) | d[13]) for (_, d), ok in zip(rows, good) if ok)
                y.extend(ca_result(targets[j][1]) for j, ok in zip(ix, good) if ok)
            st = stats(x, y)
            if st['r'] is not None and (best is None or abs(st['r']) > abs(best['r'])):
                best = {'lag_ms': lag, **st}
        out[drive] = best
    return out


def gts_join(gts: dict) -> dict:
    surface = gts['longitudinal_request_surface']
    brake = surface['brake_receive_vocabulary']['dids']
    recorder = surface['pcs_recorder_vocabulary']
    def one(did):
        row = brake[did][0]
        return {k: row[k] for k in ('name', 'bit_width', 'signed', 'decimal_point_count', 'unit')}
    return {
        'brake_tss_receive': {did: one(did) for did in ('0x10A1', '0x10A2', '0x10A3', '0x10A4')},
        'pcs_operation_ffd_5280_lower': recorder['5280'],
        'pcs_operation_ffd_5281_upper': recorder['5281'],
        'pcs_arbitration_result_id': recorder['5284'],
        'pcs_arbitration_result_acceleration': recorder['57DB'],
        'static_join': surface['static_join'],
        'boundary': 'The diagnostic/recorder vocabulary establishes Toyota semantics and width/scale, not the 0x08A byte assignment or SecOC publisher identity.',
    }


def build() -> dict:
    loaded = {name: load_august(path) for name, path in DRIVES.items()}
    header, groups = load_fixture(ROLE_FIXTURE)
    role_report = json.loads(ROLE_REPORT.read_text())
    topology = json.loads(TOPOLOGY.read_text())
    gts = json.loads(GTS.read_text())
    census = json.loads(CENSUS.read_text())
    direct = screen_direct_frc(loaded)
    a8 = summarize_08a(loaded, census)
    resumes = resume_evidence(role_report, groups)
    return {
        'schema': 'camry-longitudinal-request-candidates-v3',
        'vehicle_access': False,
        'sources': {
            'august_drives': {name: {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)} for name, path in DRIVES.items()},
            'role_fixture': {'path': str(ROLE_FIXTURE.relative_to(ROOT)), 'sha256': sha(ROLE_FIXTURE), 'source_count': len(header['sources'])},
            'role_report': {'path': str(ROLE_REPORT.relative_to(ROOT)), 'sha256': sha(ROLE_REPORT)},
            'stock_topology': {'path': str(TOPOLOGY.relative_to(ROOT)), 'sha256': sha(TOPOLOGY)},
            'gts_surface': {'path': str(GTS.relative_to(ROOT)), 'sha256': sha(GTS)},
            'upstream_request_census': {'path': str(CENSUS.relative_to(ROOT)), 'sha256': sha(CENSUS)},
        },
        'topology_normalization': {
            'stock_toyota_b': topology['physical_network_roles'],
            'current_stock_candidate_planes': topology['candidate_direction'],
            'historical_repin': {
                'panda_bus0_bus2': 'Toyota Bus-4 Brake/EPS/chassis relay pair; native upstream 0x08A/0x0C9 on bus2, native chassis 0x0CA on bus0',
                'panda_bus1': 'Toyota Bus-1 camera/radar/ADAS; direct FRC 0x020/0x160/0x230/0x440 observed here',
            },
            'route_classification_signatures': {
                'stock_toyota_b': 'native 0x160/FRC-P05 source on bus2; 0x08A/0x0C9/0x0CA on unsplit bus1; radar-object family downstream on bus0',
                'temporary_repin': 'native 0x160/FRC-P05 on bus1; native upstream 0x08A/0x0C9 on bus2; native chassis 0x0CA on bus0',
                'echo_rule': 'Panda src>=128 denotes returned host TX and must not be counted as an ECU-native source when classifying topology',
            },
            'rule': 'Compare Toyota network role and physical direction first; raw Panda bus number is era-dependent and dates are secondary evidence.',
        },
        'protected_0x08a_acceleration_candidate': {
            **a8, 'stock_resume_evidence': resumes,
            'interpretation': ('B8:B9 and B11:B12 are the strongest retained chassis-facing longitudinal request candidates: '
                               'duplicated signed16 words with a natural 0.001 m/s^2 scale, upstream-to-chassis direction, '
                               'pre-motion behavior, and an exact width/scale semantic match to Toyota TSS upper/lower request vocabulary. '
                               'Upper-versus-lower byte identity and request-ID fields are not recovered.'),
        },
        'gts_semantic_template': gts_join(gts),
        'direct_frc_bus1_duplicate_request_screen': direct,
        'protected_bus4_companion_screen': screen_protected_bus4(loaded),
        'protected_0x5af_coarse_companion': coarse_5af_companion(loaded),
        'other_candidates': {
            '0x0C9': {'direction': 'upstream -> chassis on Toyota Bus 4 during repin', 'b12_b13_vs_0x0ca': c9_vs_ca(loaded),
                      'disposition': 'possible longitudinal sideband/state metadata; weak magnitude candidate and remains static through early stock-resume ramp'},
            '0x0CA': {'direction': 'chassis -> upstream on Toyota Bus 4 during repin',
                      'disposition': 'other protected longitudinal/chassis state; the cleaner arbitration-result ID/acceleration pair is in Brake-owned 0x081'},
            '0x160': {'direction': 'FRC -> camera/ADAS Toyota Bus 1',
                      'disposition': 'longitudinal-related state publication; known fine field is measurement-like and prior B12 command mapping is withdrawn'},
        },
        'request_plane_architecture': {
            'logical_request': ('0x08A is already the recovered upstream/FRC-side request plane. FRC normal-Tx suppression removes '
                                '0x08A, while the Brake-owned 0x081 result/reference publication survives FRC loss and asserts its '
                                'request-loss response. A downstream signer/proxy may physically publish protected 0x08A, but that '
                                'does not create a second semantic request layer.'),
            'selected_result': ('0x081 is the established Brake/chassis-side selected/result/reference publication for lateral. '
                                'The corresponding longitudinal result may be distributed across 0x0CA/0x5AF/0x5F7 or other fields; '
                                'this audit does not assign one PDU as the complete longitudinal analogue.'),
            'exhaustiveness_boundary': ('0x08A is the central observed continuous TSS request PDU and carries the recovered lateral '
                                        'request plus the strongest longitudinal acceleration-request candidates. It is not proved '
                                        'to contain every authoritative TSS3 control parameter: Toyota recorder semantics also expose '
                                        'upper/lower longitudinal request IDs, force-allocation, shift/EPB, override/priority and other '
                                        'request metadata whose exact wire locations are not all mapped. Ordinary FRC state/display/ego '
                                        'publications also exist outside 0x08A.'),
        },
        'ranking': [
            {'rank': 1, 'candidate': 'protected 0x08A B8:B9 and B11:B12', 'role': 'FRC-side TSS acceleration-request fields',
             'status': 'strong bounded candidate inside the already-established 0x08A request plane; exact upper/lower wire identity remains open'},
            {'rank': 2, 'candidate': 'protected 0x5AF B26 signed6', 'role': 'coarse longitudinal request/result companion',
             'status': 'tracks 0x08A at about 0.25 m/s^2/count but lags it; not a primary request magnitude'},
            {'rank': 3, 'candidate': '0x0C9', 'role': 'possible sideband/request metadata', 'status': 'weak magnitude candidate'},
            {'rank': 4, 'candidate': '0x0CA', 'role': 'other protected longitudinal/chassis state', 'status': 'wrong direction for direct FRC request; superseded as the primary arbitration-result interpretation by 0x081'},
        ],
        'implementation_boundary': (
            'Do not restore Camry 0x160 longitudinal output and do not inject a competing 0x08A from this analysis alone. '
            'The semantic request plane is already 0x08A. On stock Toyota-B that protected PDU is on unsplit Bus 4, so production '
            'integration still needs a clean source-suppression/sole-emitter boundary or the physical FRC-to-signer publication handoff. '
            'That is a transport/ownership problem, not evidence of a different upstream command. No runtime or Panda policy is authorized here.'),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=OUT)
    args = ap.parse_args()
    report = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(args.output)


if __name__ == '__main__':
    main()
