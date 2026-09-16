#!/usr/bin/env python3
"""Find native cruise releases independently of host requests and button edges.

Offline source analysis only. Absence of a decoded input is not an autonomous
cancel classification. No CAN transmitter, security operation, or vehicle I/O.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import sys
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.targets.camry.analysis.analyze_camry_2026_cancel_request_causality import (
    input_assertions,
    sha,
)

FIXTURE = ROOT / 'tests/fixtures/camry_2026_native_cruise_release.jsonl.gz'
OUTPUT = ROOT / 'data/generated/camry_2026_native_cruise_release.json'
SCOPE = ROOT / 'tests/fixtures/camry_2026_cancel_host_attempts.jsonl.gz'
CONTEXT_NS = 500_000_000
WINDOW_NS = 3_000_000_000
# These are analysis observation windows, not vehicle runtime thresholds.
MAX_OBSERVATION_GAP_NS = 100_000_000


def write_rows(path: Path, header: dict, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with (path.open('wb') as raw,
          gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed,
          io.TextIOWrapper(compressed, encoding='utf-8') as stream):
        for row in (header, *rows):
            stream.write(json.dumps(row, separators=(',', ':')) + '\n')


def coverage(times: list[int], start: int, end: int) -> dict:
    observed = sorted({t for t in times if start <= t <= end})
    gaps = [right - left for left, right in zip([start, *observed], [*observed, end], strict=True)]
    largest = max(gaps)
    return {'count': len(observed), 'max_gap_ns': largest,
            'complete': bool(observed) and largest <= MAX_OBSERVATION_GAP_NS}


def classify(center: int, context: list[list]) -> dict:
    """Classify observed inputs, never infer missing inputs as deasserted."""
    input_times: dict[int, list[int]] = {0xFE: [], 0x101: []}
    assertions = []
    malformed = Counter()
    controls = []
    for _, nanos, kind, data in context:
        if kind == 'carControl':
            controls.append((nanos, data))
        if kind != 'can' or not center - CONTEXT_NS <= nanos <= center:
            continue
        for bus, address, text in data:
            if bus != 0 or address not in input_times:
                continue
            raw = bytes.fromhex(text)
            value = input_assertions(address, raw)
            if value is None:
                malformed[f'0x{address:03X}'] += 1
                continue
            input_times[address].append(nanos)
            for active, name in ((value[0], 'cancel'), (value[1], 'brake'),
                                 (address == 0xFE and bool(raw[7] & 4), 'main')):
                if active:
                    assertions.append({'nanos': nanos, 'kind': name, 'payload': text,
                                       'address': f'0x{address:03X}', 'bus': bus})
    source_coverage = {f'0x{a:03X}': coverage(t, center - CONTEXT_NS, center) for a, t in input_times.items()}
    complete = all(c['complete'] for c in source_coverage.values()) and not malformed
    disposition = ('decoded_driver_input_observed' if assertions else
                   'no_decoded_driver_input_observed' if complete else 'incomplete_input_coverage')
    before = [(t, value) for t, value in controls if center - CONTEXT_NS <= t <= center]
    last_control = max(before, default=None)
    control_coverage = coverage([t for t, _ in controls], center - CONTEXT_NS, center)
    return {'disposition': disposition, 'input_coverage': source_coverage,
            'malformed_inputs': dict(malformed),
            'observed_input_kinds': sorted({a['kind'] for a in assertions}),
            'first_observed_input': min(assertions, key=lambda r: r['nanos']) if assertions else None,
            'host_cancel_asserted_in_pre_window': any(value for _, value in before) if control_coverage['complete'] else None,
            'host_cancel_coverage': control_coverage,
            'last_host_cancel': {'nanos': last_control[0], 'value': last_control[1]} if last_control else None}


def discover(log_root: Path, openpilot_root: Path, output: Path) -> None:
    """Scan all sources in the already-pinned ten-route scope, then retain windows."""
    sys.path.insert(0, str(openpilot_root))
    from openpilot.tools.lib.logreader import LogReader

    with gzip.open(SCOPE, 'rt') as stream:
        scope = json.loads(next(stream))
    sources = scope['sources']
    routes, releases = [], []
    for route in scope['routes']:
        buffer: deque = deque()
        previous = None
        counts = Counter()
        for index in route['source_indices']:
            info = sources[index]
            path = log_root / info['path']
            if sha(path) != info['sha256']:
                raise ValueError(f'changed source: {info["path"]}')
            for event in LogReader(str(path)):
                nanos, kind = int(event.logMonoTime), event.which()
                if kind == 'carControl':
                    buffer.append([index, nanos, kind, bool(event.carControl.cruiseControl.cancel)])
                elif kind == 'can':
                    frames = [[int(f.src), int(f.address), bytes(f.dat).hex()] for f in event.can
                              if f.src in (0, 2) and f.address in (0xFE, 0x101, 0x08A, 0x251)]
                    if not frames:
                        continue
                    buffer.append([index, nanos, kind, frames])
                    while buffer and buffer[0][1] < nanos - CONTEXT_NS:
                        buffer.popleft()
                    for bus, address, text in frames:
                        raw = bytes.fromhex(text)
                        if (bus, address, len(raw)) != (2, 0x08A, 32):
                            continue
                        counts['native_0x08a'] += 1
                        active = bool(raw[3] & 8)
                        if previous is not None and previous['active'] and not active:
                            delta = nanos - previous['nanos']
                            if not 0 < delta <= MAX_OBSERVATION_GAP_NS:
                                counts['discontinuities_not_scored_as_release'] += 1
                            else:
                                context = list(buffer)
                                finding = classify(nanos, context)
                                releases.append({'route': route['route'], 'source_index': index,
                                                 'nanos': nanos, 'before': previous, 'after': text,
                                                 'context': context})
                                counts[finding['disposition']] += 1
                                counts['releases'] += 1
                        previous = {'source_index': index, 'nanos': nanos, 'active': active, 'payload': text}
        routes.append({'route': route['route'], 'source_indices': route['source_indices'], 'counts': dict(counts)})
        print(route['route'], dict(counts), flush=True)
    selected = [i for i, r in enumerate(releases) if classify(r['nanos'], r['context'])['disposition'] == 'no_decoded_driver_input_observed']
    windows = []
    for i in selected:
        release = releases[i]
        route = next(r for r in routes if r['route'] == release['route'])
        position = route['source_indices'].index(release['source_index'])
        # Adjacent segments preserve any window crossing a recording boundary.
        neighbors = route['source_indices'][max(0, position - 1):position + 2]
        for index in neighbors:
            info = sources[index]
            path = log_root / info['path']
            if sha(path) != info['sha256']:
                raise ValueError(f'changed source: {info["path"]}')
            for event in LogReader(str(path)):
                nanos, kind = int(event.logMonoTime), event.which()
                if abs(nanos - release['nanos']) > WINDOW_NS:
                    continue
                if kind in ('can', 'sendcan'):
                    data = [[int(f.src), int(f.address), bytes(f.dat).hex()] for f in getattr(event, kind)
                            if kind == 'sendcan' or f.src in (0, 1, 2)]
                elif kind == 'carControl':
                    data = bool(event.carControl.cruiseControl.cancel)
                elif kind == 'carState':
                    data = {'v_ego': float(event.carState.vEgo), 'gas_pressed': bool(event.carState.gasPressed),
                            'brake_pressed': bool(event.carState.brakePressed)}
                else:
                    continue
                windows.append(['window', i, index, nanos, kind, data])
    header = {'schema': 'camry-native-cruise-release-fixture-v1', 'sources': sources, 'routes': routes,
              'input_bus': 0, 'cruise_bus': 2, 'adas_bus': 1, 'topology': 'historical repin only',
              'context_ns': CONTEXT_NS, 'window_ns': WINDOW_NS, 'selected_release_indices': selected,
              'boundary': 'No decoded input observed is a selection, not proof of autonomous cancellation or host acceptance.'}
    write_rows(output, header, [['release', r] for r in releases] + windows)
    print(output, flush=True)


def reduce_native_window(release: dict, rows: list[list]) -> dict:
    center = release['nanos']
    native: dict[int, list[tuple[int, bytes]]] = {a: [] for a in (0x101, 0x251, 0x1B2, 0x198, 0x19C)}
    host_requests, host_sends, states = [], [], []
    for _, _, _, nanos, kind, data in rows:
        if kind == 'carControl' and data:
            host_requests.append(nanos)
        elif kind == 'sendcan':
            host_sends.extend((nanos, bus, address, text) for bus, address, text in data
                              if address in (0x101, 0x1B2, 0xFE, 0x343, 0x1D2))
        elif kind == 'carState':
            states.append((nanos, data))
        elif kind == 'can':
            for bus, address, text in data:
                if address in native and bus == (0 if address == 0x101 else 2):
                    native[address].append((nanos, bytes.fromhex(text)))
    def offsets(values):
        return [round((t - center) / 1e6, 6) for t in values]
    near_modes = [(t, d[0]) for t, d in native[0x251] if len(d) == 8 and center - CONTEXT_NS <= t <= center + CONTEXT_NS]
    pre_modes = [v for t, v in near_modes if t < center]
    post_modes = [v for t, v in near_modes if t >= center]
    mode = 'conventional' if pre_modes and pre_modes[-1] in (0x88, 0x90) else 'adaptive' if pre_modes and pre_modes[-1] in (0xA0, 0xC0) else 'unclassified'
    brakes = [(t, d) for t, d in native[0x101] if input_assertions(0x101, d) is not None]
    before_brake = [(t, d) for t, d in brakes if center - CONTEXT_NS <= t <= center]
    changes = []
    previous = None
    for t, d in before_brake:
        if previous != (d[0], d[1], d[3]):
            changes.append({'offset_ms': round((t - center) / 1e6, 6), 'payload': d.hex()})
            previous = d[0], d[1], d[3]
    baseline = [d[1] for t, d in brakes if center - 3_000_000_000 <= t < center - 1_000_000_000]
    current = min(states, key=lambda x: abs(x[0] - center)) if states else None
    return {'release_nanos': center, 'source_index': release['source_index'], 'route': release['route'],
            'classification': classify(center, release['context']),
            'mode_from_native_0x251_b0': mode, 'last_pre_mode': pre_modes[-1] if pre_modes else None,
            'first_post_mode': post_modes[0] if post_modes else None,
            'state_sample': {'offset_ms': round((current[0] - center) / 1e6, 6), **current[1]} if current else None,
            'host_request_offsets_ms': offsets(host_requests),
            'host_cancel_shaped_sends': [{'offset_ms': round((t - center) / 1e6, 6), 'bus': b, 'address': f'0x{a:03X}', 'payload': h}
                                        for t, b, a, h in host_sends],
            'brake_b1_baseline_values': sorted(set(baseline)),
            'brake_b1_pre_values': sorted({d[1] for _, d in before_brake}), 'brake_pre_changes': changes,
            'brake_assertion_offsets_ms': offsets([t for t, d in brakes if d[0] & 8]),
            'mirror_cancel_offsets_ms': offsets([t for t, d in native[0x1B2] if len(d) == 32 and d[0] & 0x20]),
            'boundary': 'Brake B1 is retained as an unnamed raw byte. Conventional mode and nearby speed do not identify a cancellation threshold or receiver command.'}


def build(path: Path = FIXTURE) -> dict:
    with gzip.open(path, 'rt') as stream:
        header = json.loads(next(stream))
        if header['schema'] != 'camry-native-cruise-release-fixture-v1':
            raise ValueError('unexpected native-release fixture')
        releases, windows = [], []
        for line in stream:
            row = json.loads(line)
            if row[0] == 'release':
                releases.append(row[1])
            else:
                windows.append(row)
    counts = Counter(classify(r['nanos'], r['context'])['disposition'] for r in releases)
    selected = [i for i, r in enumerate(releases) if classify(r['nanos'], r['context'])['disposition'] == 'no_decoded_driver_input_observed']
    if selected != header['selected_release_indices']:
        raise ValueError('native-release selection changed')
    return {'schema': 'camry-native-cruise-release-v1',
            'fixture_sha256': sha(path), 'source_count': len(header['sources']), 'routes': header['routes'],
            'dispositions': dict(counts), 'release_count': len(releases),
            'selected_windows': [reduce_native_window(releases[i], [r for r in windows if r[1] == i]) for i in selected],
            'boundaries': ['This scan is selected by native 0x08A falling edges, not by physical buttons or host cancel requests.',
                           'A <=100ms continuous cruise edge is required; absent/malformed inputs are unknown, never deasserted.',
                           'Publication ordering is not physical bus arbitration ordering.',
                           'Neither a native release nor a switch mirror is proof that an injected command is accepted.',
                           'No cancel sender, diagnostic operation, ECU fault, or vehicle write is performed.']}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--extract', action='store_true')
    ap.add_argument('--fixture', type=Path, default=FIXTURE)
    ap.add_argument('--out', type=Path, default=OUTPUT)
    ap.add_argument('--log-root', type=Path, default=ROOT.parents[1] / 'logs/camry-2026')
    ap.add_argument('--openpilot-root', type=Path, default=ROOT.parent / 'kai-openpilot')
    args = ap.parse_args()
    if args.extract:
        discover(args.log_root, args.openpilot_root, args.fixture)
    report = build(args.fixture)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(args.out)
    print(report['dispositions'])


if __name__ == '__main__':
    main()
