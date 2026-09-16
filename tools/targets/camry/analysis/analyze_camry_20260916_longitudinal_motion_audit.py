#!/usr/bin/env python3
"""Independent passive motion/causality audit of Camry 0x160.

Uses tracked August captures and a separate seven-source September fixture.
No vehicle connection, transmitter, diagnostic write, or firmware access.
"""
from __future__ import annotations

import argparse
import binascii
import bisect
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
STEM = 'camry_20260916_longitudinal_motion_audit'
FIXTURE = ROOT / f'tests/fixtures/{STEM}.jsonl.gz'
OUTPUT = ROOT / f'data/generated/{STEM}.json'
AUGUST = {
    'drive_a': ROOT / 'targets/camry-2026/raw-20260827/camry_relay_route_can_20260827.ndjson.gz',
    'drive_b': ROOT / 'targets/camry-2026/raw-20260827/camry_relay_lta_confirm_route_can_20260827.ndjson.gz',
}
SOURCE_GROUPS = (
    ('combined_trial', '2026-09-11/000000d4--327b2c4bb8', (2, 3, 4, 5)),
    ('stock_3b', '2026-09-04/0000003b--62262eb7a1', (84,)),
    ('stock_3c', '2026-09-04/0000003c--97b9e7a69a', (26, 27)),
)
RESUMES = (('stock_3b', 5122.256), ('stock_3c', 9068.054), ('stock_3c', 9147.517))
IDS = {0x160, 0x0CA, 0x0C9, 0x0AA, 0x08A, 0x251}


def source_path(path):
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def valid_160(data):
    return len(data) == 32 and int.from_bytes(data[:2], 'little') == binascii.crc_hqx(data[2:] + b'\x60\x01', 0xFFFF)


def signed(raw, bits):
    return (np.asarray(raw, dtype=np.int64) ^ (1 << (bits - 1))) - (1 << (bits - 1))


def word(data, offset, bits=16):
    d = np.asarray(data, dtype=np.int64)
    return signed(((d[:, offset] << 8) | d[:, offset + 1]) & ((1 << bits) - 1), bits)


def fine(data):
    return word(data, 4, 15) * .001


def coarse(data):
    """Existing comparison convention, not a calibrated actuation demand."""
    return -.1 * signed(np.asarray(data)[:, 12] & 127, 7)


def wheel_speed(data):
    d = np.asarray(data, dtype=np.int64)
    invalid = np.any((d[:, ::2] & 128) != 0, axis=1)
    values = sum(((((d[:, i] << 8) | d[:, i + 1]) & 32767) * .01 - 67.67) for i in (0, 2, 4, 6)) / 4 / 3.6
    return values, ~invalid


def series(rows):
    rows = sorted(rows, key=lambda r: (r[0], r[1]))
    if not rows or len({len(r[2]) for r in rows}) != 1:
        raise ValueError('Empty stream or mixed lengths')
    return {'segment': np.array([r[0] for r in rows], dtype=np.int64),
            'time': np.array([r[1] for r in rows], dtype=np.int64),
            'data': np.array([list(r[2]) for r in rows], dtype=np.uint8)}


def subset(s, mask):
    return {k: v[mask] for k, v in s.items()}


def nearest(ref, other, shift_ns=0, max_gap_ns=40_000_000, preceding=False):
    indices = np.zeros(len(ref['time']), dtype=np.int64)
    valid = np.zeros(len(ref['time']), dtype=bool)
    for seg in np.unique(ref['segment']):
        ri = np.flatnonzero(ref['segment'] == seg)
        oi = np.flatnonzero(other['segment'] == seg)
        if not len(oi):
            continue
        query, ts = ref['time'][ri] + shift_ns, other['time'][oi]
        hi = np.searchsorted(ts, query, side='right')
        lo = np.clip(hi - 1, 0, len(ts) - 1)
        if preceding:
            ix, ok = lo, hi > 0
        else:
            hi = np.clip(hi, 0, len(ts) - 1)
            ix = np.where(abs(ts[lo] - query) <= abs(ts[hi] - query), lo, hi)
            ok = np.ones(len(query), dtype=bool)
        indices[ri] = oi[ix]
        valid[ri] = ok & (abs(ts[ix] - query) <= max_gap_ns)
    return indices, valid


def preceding_counter_match(host, camera, max_age_ns=75_000_000):
    """Counter matching is local in time; never index a whole route by a byte."""
    indices = np.zeros(len(host['time']), dtype=np.int64)
    valid = np.zeros(len(host['time']), dtype=bool)
    for seg in np.unique(host['segment']):
        oi = np.flatnonzero(camera['segment'] == seg)
        ts = camera['time'][oi].tolist()
        for i in np.flatnonzero(host['segment'] == seg):
            t = int(host['time'][i])
            j = bisect.bisect_right(ts, t) - 1
            while j >= 0 and t - ts[j] <= max_age_ns:
                if host['data'][i, 2] == camera['data'][oi[j], 2]:
                    indices[i], valid[i] = oi[j], True
                    break
                j -= 1
    return indices, valid


def nearby_payload_match(host, echoes, max_gap_ns=40_000_000):
    matched = np.zeros(len(host['time']), dtype=bool)
    offsets = np.zeros(len(host['time']), dtype=np.int64)
    for seg in np.unique(host['segment']):
        ei = np.flatnonzero(echoes['segment'] == seg)
        ts = echoes['time'][ei].tolist()
        for i in np.flatnonzero(host['segment'] == seg):
            t = int(host['time'][i])
            lo, hi = bisect.bisect_left(ts, t - max_gap_ns), bisect.bisect_right(ts, t + max_gap_ns)
            js = [j for j in range(lo, hi) if np.array_equal(host['data'][i], echoes['data'][ei[j]])]
            if js:
                j = min(js, key=lambda j: abs(ts[j] - t))
                matched[i], offsets[i] = True, ts[j] - t
    return matched, offsets


def interpolate_valid(ts, values, query, max_gap_ns=40_000_000):
    ts, query = np.asarray(ts, dtype=np.int64), np.asarray(query, dtype=np.int64)
    hi = np.searchsorted(ts, query, side='left')
    hi_clip, lo = np.clip(hi, 0, len(ts) - 1), np.clip(hi - 1, 0, len(ts) - 1)
    exact, gap = ts[hi_clip] == query, ts[hi_clip] - ts[lo]
    ok = exact | ((hi > 0) & (hi < len(ts)) & (gap > 0) & (gap <= max_gap_ns))
    weights = np.divide(query - ts[lo], gap, out=np.zeros(len(query)), where=gap > 0)
    result = np.asarray(values)[lo] + weights * (np.asarray(values)[hi_clip] - np.asarray(values)[lo])
    result[exact] = np.asarray(values)[hi_clip[exact]]
    return result, ok


def stats(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 2 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return {'n': len(x), 'pearson_r': None}
    slope, intercept = np.polyfit(x, y, 1)
    return {'n': len(x), 'pearson_r': round(float(np.corrcoef(x, y)[0, 1]), 9),
            'slope_y_per_x': round(float(slope), 9), 'intercept': round(float(intercept), 9),
            'x_minmax': [round(float(x.min()), 6), round(float(x.max()), 6)],
            'y_minmax': [round(float(y.min()), 6), round(float(y.max()), 6)]}


def physical_motion(s, wheels, cruise):
    v, good = wheel_speed(wheels['data'])
    wheels, v = subset(wheels, good), v[good]
    state_i, state_ok = nearest(s, cruise, max_gap_ns=100_000_000, preceding=True)
    engaged = (cruise['data'][state_i, 3] & 8) != 0
    result = {}
    for lag_ms in (-100, 0):
        y, valid = np.zeros(len(s['time'])), np.zeros(len(s['time']), dtype=bool)
        for seg in np.unique(s['segment']):
            ri, wi = np.flatnonzero(s['segment'] == seg), np.flatnonzero(wheels['segment'] == seg)
            if len(wi) < 2:
                continue
            t, wt = s['time'][ri], wheels['time'][wi]
            v0, g0 = interpolate_valid(wt, v[wi], t)
            vl, gl = interpolate_valid(wt, v[wi], t + lag_ms * 1_000_000 - 200_000_000)
            vr, gr = interpolate_valid(wt, v[wi], t + lag_ms * 1_000_000 + 200_000_000)
            y[ri], valid[ri] = (vr - vl) / .4, g0 & gl & gr & (v0 > 2.)
        valid &= state_ok
        result[str(lag_ms)] = {label: stats(fine(s['data'])[valid & mode], y[valid & mode])
                              for label, mode in [('all_moving', np.ones(len(valid), dtype=bool)),
                                                  ('cruise_latch_clear', ~engaged), ('cruise_latch_set', engaged)]}
    return result


def packed_speed(data):
    """Observed ego-speed candidate, not a recovered OEM signal name."""
    d = np.asarray(data, dtype=np.int64)
    raw = (((d[:, 7] << 16) | (d[:, 8] << 8) | d[:, 9]) >> 5) & 32767
    return (raw * .01 - 67.67) / 3.6


def feedback_crosscheck(s, brake, wheels, ca, cruise):
    """Compare camera fields with independent native chassis publications.

    All joins stay within a source file. For every queried instant, only the
    most recent preceding native observation is used. Lag sweeps are descriptive
    alignment tests, not an inference of physical causation or actuator delay.
    """
    def metric(x, y):
        result = stats(x, y)
        if len(x):
            error = np.abs(np.asarray(x) - np.asarray(y))
            result.update(median_absolute_error=round(float(np.median(error)), 9),
                          p95_absolute_error=round(float(np.quantile(error, .95)), 9))
        return result

    bi, bok = nearest(s, brake, preceding=True, max_gap_ns=100_000_000)
    ai, aok = nearest(s, cruise, preceding=True, max_gap_ns=100_000_000)
    active = (cruise['data'][ai, 3] & 8) != 0
    x, y = fine(s['data']), word(brake['data'][bi], 0, 15) * .001
    acceleration = {}
    for name, mode in [('all', np.ones(len(x), dtype=bool)), ('cruise_off', ~active), ('cruise_on', active)]:
        valid = bok & aok & mode
        acceleration[name] = metric(x[valid], y[valid])

    v, wheel_ok = wheel_speed(wheels['data'])
    wi, wok = nearest(s, wheels, preceding=True, max_gap_ns=80_000_000)
    speed_valid = wok & wheel_ok[wi] & (v[wi] > 2.)
    speed = metric(packed_speed(s['data'])[speed_valid], v[wi[speed_valid]])

    profile = []
    for lag_ms in range(-250, 251, 25):
        ci, cok = nearest(s, ca, shift_ns=lag_ms * 1_000_000,
                          preceding=True, max_gap_ns=100_000_000)
        valid = cok & aok & active
        profile.append({'lag_ms': lag_ms,
                        **metric(coarse(s['data'])[valid], word(ca['data'][ci[valid]], 7) * .001)})
    peak = max(profile, key=lambda row: row['pearson_r'] if row['pearson_r'] is not None else -2.)
    return {'fine_vs_native_13c': acceleration,
            'packed_speed_vs_valid_wheels_above_2mps': speed,
            'b12_vs_native_ca': {
                'convention': 'corr(B12(t), CA(t+lag)); negative lag aligns B12 with an earlier chassis publication.',
                'peak': peak, 'sweep': profile,
                'limit': 'Temporal co-movement, quantization, smoothing and publication delay do not establish a unique producer/consumer path.'},
            'semantic_limit': 'Numerical ego-state matches are not OEM names, a full-PDU telemetry proof, or a literal byte-copy proof.'}


def load_august(path):
    rows, rejected = defaultdict(list), Counter()
    with gzip.open(path, 'rt') as f:
        for line in f:
            seg, t, bus, a, text = json.loads(line)
            if not ((a == 0x160 and bus == 1) or (a in (0x0AA, 0x08A, 0x0C9, 0x13C, 0x0CA) and bus == 0)):
                continue
            d = bytes.fromhex(text)
            if a == 0x160 and not valid_160(d):
                rejected['bad_0x160_crc_or_length'] += 1
                continue
            if len(d) != (8 if a in (0x0AA, 0x13C) else 32):
                rejected['bad_length'] += 1
                continue
            rows[a].append((seg, t, d))
    return {a: series(r) for a, r in rows.items()}, dict(rejected)


def extract_fixture(log_root, openpilot_root, path):
    sys.path.insert(0, str(openpilot_root))
    from openpilot.tools.lib.logreader import LogReader
    sources, rows = [], []
    for group, route, segments in SOURCE_GROUPS:
        for segment in segments:
            src = log_root / route / f'rlog-{segment}.zst'
            index = len(sources)
            sources.append({'group': group, 'path': str(src.relative_to(log_root)), 'sha256': sha256(src)})
            print(f'Read {src}', flush=True)
            for event in LogReader(str(src)):
                kind = event.which()
                if kind in ('can', 'sendcan'):
                    for frame in getattr(event, kind):
                        if frame.address in IDS:
                            rows.append([index, int(event.logMonoTime), kind, int(frame.src), int(frame.address), bytes(frame.dat).hex()])
    rows.sort(key=lambda r: (r[0], r[1]))
    header = {'schema': 'camry-longitudinal-role-fixture-v1', 'sources': sources,
              'rows': '[source_index, publication_ns, service, panda_src, address, payload_hex]',
              'boundary': 'Original captured frames only. sendcan and returned TX are not ECU acceptance acknowledgements.'}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as f:
        f.write((json.dumps(header, sort_keys=True) + '\n').encode())
        for row in rows:
            f.write((json.dumps(row, separators=(',', ':')) + '\n').encode())


def read_fixture(path):
    rows, census, invalid = defaultdict(list), Counter(), Counter()
    with gzip.open(path, 'rt') as f:
        header = json.loads(next(f))
        for line in f:
            source, t, kind, bus, a, text = json.loads(line)
            group = header['sources'][source]['group']
            census[(group, kind, bus, a)] += 1
            d = bytes.fromhex(text)
            if a == 0x160 and not valid_160(d):
                invalid[(group, kind, bus)] += 1
                continue
            if len(d) != (8 if a in (0x0AA, 0x251) else 32):
                raise ValueError('Unexpected retained frame length')
            rows[(group, kind, bus, a)].append((source, t, d))
    return header, {key: series(r) for key, r in rows.items()}, census, invalid


def trial_analysis(streams):
    def get(kind, bus, a):
        return streams[('combined_trial', kind, bus, a)]
    host, camera, ca, echoes = get('sendcan', 0, 0x160), get('can', 2, 0x160), get('can', 1, 0x0CA), get('can', 128, 0x160)
    ci, cok = preceding_counter_match(host, camera)
    returned, offsets = nearby_payload_match(host, echoes)
    result = {}
    for lag in (-100, 0, 100):
        yi, yok = nearest(host, ca, shift_ns=lag * 1_000_000)
        valid, y = cok & yok, word(ca['data'][yi], 7) * .001
        vals = {'native_b4': fine(camera['data'][ci]), 'host_b4': fine(host['data']),
                'native_b12_hypothesis': coarse(camera['data'][ci]), 'host_b12_hypothesis': coarse(host['data'])}
        result[str(lag)] = {key: stats(x[valid], y[valid]) for key, x in vals.items()}
        disagree = valid & (camera['data'][ci, 12] != host['data'][:, 12])
        result[str(lag)]['b12_disagreement_only'] = {key: stats(vals[key][disagree], y[disagree])
                                                   for key in ('native_b12_hypothesis', 'host_b12_hypothesis')}
    ages = (host['time'][cok] - camera['time'][ci[cok]]) / 1e6
    mi, mok = nearest(host, get('can', 1, 0x251), preceding=True, max_gap_ns=2_000_000_000)
    modes = Counter(int(x) for x in get('can', 1, 0x251)['data'][mi[mok], 0])
    return {'host_frames': len(host['time']), 'source_counter_matched': int(cok.sum()),
            'byte_identical_nearby_returned_tx': int(returned.sum()),
            'matching_return_offset_ms': [round(float(x), 6) for x in np.percentile(offsets[returned] / 1e6, [0, 50, 100])],
            'b12_changed_from_counter_matched_native': int((cok & (host['data'][:, 12] != camera['data'][ci, 12])).sum()),
            'b4_changed_from_counter_matched_native': int((cok & (fine(host['data']) != fine(camera['data'][ci]))).sum()),
            'native_source_age_ms': [round(float(x), 6) for x in np.percentile(ages, [0, 50, 100])],
            'preceding_mode_byte_counts': {hex(k): n for k, n in sorted(modes.items())}, 'mode_coverage_frames': int(mok.sum()),
            'ca_time_shift_ms': result,
            'boundary': 'Predictive comparison, not a causal effect estimate. Conventional mode and absent EPS do not qualify healthy DRCC.'}


def resume_analysis(streams):
    results = []
    for group, motion in RESUMES:
        s, ca, w = streams[(group, 'can', 1, 0x160)], streams[(group, 'can', 0, 0x0CA)], streams[(group, 'can', 0, 0x0AA)]
        v, good = wheel_speed(w['data'])
        landmark = round(motion * 1e9)
        near = (abs(w['time'] - landmark) <= 300_000_000) & good & (v > .1)
        if not near.any():
            raise ValueError('Missing motion onset')
        first = np.flatnonzero(near)[0]
        onset, seg = int(w['time'][first]), w['segment'][first]
        nonzero = np.flatnonzero((s['segment'] == seg) & (s['time'] >= onset) & (s['time'] <= onset + 1_000_000_000) & (abs(fine(s['data'])) > .005))
        rows = []
        for offset in (-700, -500, -400, -300, -200, -100, 0, 100, 200, 300, 500, 700):
            ref = {'segment': np.array([seg]), 'time': np.array([onset + offset * 1_000_000])}
            si, so = nearest(ref, s)
            yi, yo = nearest(ref, ca)
            wi, wo = nearest(ref, w)
            if not (so[0] and yo[0] and wo[0] and good[wi[0]]):
                raise ValueError('Incomplete resume neighborhood')
            rows.append({'offset_ms': offset, 'b4_fine': round(float(fine(s['data'][si])[0]), 6),
                         'b12_hypothesis': round(float(coarse(s['data'][si])[0]), 6),
                         'ca_result_like': round(float(word(ca['data'][yi], 7)[0] * .001), 6),
                         'wheel_speed_mps': round(float(v[wi[0]]), 6)})
        results.append({'group': group, 'prior_report_motion_landmark_s': motion, 'wheel_onset_ns': onset, 'source_index': int(seg),
                        'b4_first_nonzero_after_motion_ms': round((int(s['time'][nonzero[0]]) - onset) / 1e6, 6) if len(nonzero) else None, 'samples': rows})
    return results


def build(fixture=FIXTURE):
    header, streams, census, invalid = read_fixture(fixture)
    august = {}
    for name, path in AUGUST.items():
        data, rejected = load_august(path)
        c9 = data[0x0C9]['data']
        august[name] = {'path': source_path(path), 'sha256': sha256(path), 'valid_0x160_frames': len(data[0x160]['time']), 'rejected': rejected,
                         'c9_shape': {'frames': len(c9), 'frames_nonzero_outside_b12_b13': int(np.any(np.delete(c9, [12, 13], axis=1) != 0, axis=1).sum())},
                         'measured_motion_time_shift_ms': physical_motion(data[0x160], data[0x0AA], data[0x08A]),
                         'native_feedback_crosscheck': feedback_crosscheck(data[0x160], data[0x13C], data[0x0AA], data[0x0CA], data[0x08A])}
    return {'schema': 'camry-longitudinal-motion-audit-v1', 'vehicle_access': False,
            'fixture': {'path': source_path(fixture), 'sha256': sha256(fixture), 'sources': header['sources']},
            'methods': {
                'motion': 'Signed15 B4 x0.001 versus 400-ms centered derivative of independent mean wheel speed; speed>2m/s, fixed -100/0ms shifts. Invalid wheels, gaps, extrapolation and cross-file joins excluded.',
                'negative_shift': 'Later field versus earlier measured motion; publication and filtering delays are not actuator latency.',
                'trial': 'Preceding same-counter native frame <=75ms old in same file; CA nearest within40ms at stated shifts.',
                'resume': 'First mean-wheel speed>0.1m/s within300ms of prior stock-resume landmark; no new proof about unrecorded driver inputs.',
                'b12_units': '-0.1*signed7(B12) is the old comparison convention, not an independently calibrated demand.'},
            'august_motion': august, 'combined_trial': trial_analysis(streams), 'stock_resumes': resume_analysis(streams),
            'fixture_can_census': [{'group': g, 'service': k, 'panda_src': b, 'address': hex(a), 'n': n} for (g, k, b, a), n in sorted(census.items())],
            'invalid_0x160': [{'group': g, 'service': k, 'panda_src': b, 'n': n} for (g, k, b), n in sorted(invalid.items())],
            'boundaries': [
                'No 0x160 receiver implementation in this audit; EPS firmware does not establish a longitudinal contract.',
                'B4 measured-motion tracking and zero-until-after-motion are feedback-like, not an OEM field-name recovery.',
                'The intact native source defeats the earlier combined-trial correlation as independent proof of host influence.',
                'State mirror, parallel output, mode-dependent request, or mixed-role PDU remain incompletely distinguished.',
                'Panda TX returns prove transport only, not receiver acceptance; no alternative FRC command is identified.']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--extract-fixture', action='store_true')
    ap.add_argument('--log-root', type=Path, default=ROOT.parents[1] / 'logs/camry-2026')
    ap.add_argument('--openpilot-root', type=Path, default=ROOT.parent / 'kai-openpilot')
    ap.add_argument('--fixture', type=Path, default=FIXTURE)
    ap.add_argument('--out', type=Path, default=OUTPUT)
    args = ap.parse_args()
    if args.extract_fixture:
        extract_fixture(args.log_root, args.openpilot_root, args.fixture)
    result = build(args.fixture)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(args.out)


if __name__ == '__main__':
    main()
