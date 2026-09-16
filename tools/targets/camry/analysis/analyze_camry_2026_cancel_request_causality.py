#!/usr/bin/env python3
"""Separate recorded host cancel requests from independently initiated cancellation.

This is an offline evidence reducer, never a vehicle control policy. A driver
input preceding a host request makes the ensuing release causally confounded.
No input detected in the retained window is NOT proof of command acceptance.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / 'tests/fixtures/camry_2026_cancel_request_causality.jsonl.gz'
OUTPUT = ROOT / 'data/generated/camry_2026_cancel_request_causality.json'
RADIUS_NS = 1_000_000_000
INPUT_IDS = {0xFE, 0x101, 0x08A, 0x251}


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_fixture(path: Path) -> tuple[dict, list[list]]:
    with gzip.open(path, 'rt') as stream:
        header = json.loads(next(stream))
        if header['schema'] != 'camry-cancel-request-causality-fixture-v1':
            raise ValueError('unsupported fixture schema')
        return header, [json.loads(line) for line in stream]


def extract(header: dict, log_root: Path, openpilot_root: Path, output: Path) -> None:
    """Re-extract the declared windows from original, hash-checked rlogs."""
    sys.path.insert(0, str(openpilot_root))
    from openpilot.tools.lib.logreader import LogReader

    by_source: dict[int, list[int]] = defaultdict(list)
    for window, info in enumerate(header['windows']):
        for source in info['source_indices']:
            by_source[source].append(window)
    rows: list[list] = []
    for source, windows in sorted(by_source.items()):
        info = header['sources'][source]
        path = log_root / info['path']
        if sha(path) != info['sha256']:
            raise ValueError(f'original source changed: {info["path"]}')
        for event in LogReader(str(path)):
            nanos = int(event.logMonoTime)
            selected = [w for w in windows if abs(nanos - header['windows'][w]['request_nanos']) <= RADIUS_NS]
            if not selected:
                continue
            which = event.which()
            if which == 'carControl':
                data = bool(event.carControl.cruiseControl.cancel)
            elif which in ('can', 'sendcan'):
                data = [[int(frame.src), int(frame.address), bytes(frame.dat).hex()]
                        for frame in getattr(event, which)
                        if which == 'sendcan' or (frame.src in (0, 1, 2) and frame.address in INPUT_IDS)]
                if not data:
                    continue
            else:
                continue
            rows.extend([w, source, nanos, which, data] for w in selected)
    # Stable order preserves events sharing a timestamp within each source.
    rows.sort(key=lambda row: (row[0], row[2], row[1]))
    output.parent.mkdir(parents=True, exist_ok=True)
    with (
        output.open('wb') as raw,
        gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed,
        io.TextIOWrapper(compressed, encoding='utf-8') as stream,
    ):
        for row in (header, *rows):
            stream.write(json.dumps(row, separators=(',', ':')) + '\n')


def input_assertions(address: int, data: bytes) -> tuple[bool, bool] | None:
    """Return recovered CANCEL/brake assertions; malformed input stays unknown."""
    if address == 0xFE and len(data) == 32:
        asserted, inverse = bool(data[4] & 0x40), bool(data[7] & 0x20)
        if asserted == inverse:
            return None
        return asserted, False
    if address == 0x101 and len(data) == 8:
        if data[7] != ((sum(data[:7]) + 0x01 + 0x01 + 8) & 255):
            return None
        return False, bool(data[0] & 8)
    return None


def reduce_window(info: dict, rows: list[list]) -> dict:
    center = info['request_nanos']
    controls = sorted((r[2], r[4]) for r in rows if r[3] == 'carControl')
    before_control = [active for nanos, active in controls if nanos < center]
    at_control = [active for nanos, active in controls if nanos == center]
    if not before_control or before_control[-1] or at_control != [True]:
        raise ValueError('window is not a witnessed rising host cancel request')

    inputs, cruise, tx = [], [], []
    counts = Counter()
    for _, _, nanos, kind, payload in rows:
        if kind not in ('can', 'sendcan'):
            continue
        for bus, address, text in payload:
            data = bytes.fromhex(text)
            if kind == 'sendcan':
                if nanos >= center:
                    tx.append((nanos, bus, address, data))
                continue
            if bus == info['physical_input_bus'] and address in (0xFE, 0x101):
                value = input_assertions(address, data)
                if value is None:
                    counts['malformed_input'] += 1
                    continue
                inputs.append((nanos, address, data, value))
                counts[f'input_{address:03x}'] += 1
            if bus == info['cruise_bus'] and address == 0x08A and len(data) == 32:
                cruise.append((nanos, bool(data[3] & 8), data))
    inputs.sort()
    cruise.sort()
    preceding = [(nanos, address, data, value) for nanos, address, data, value in inputs
                 if center - 300_000_000 <= nanos <= center and any(value)]
    later_input = [r for r in inputs if center < r[0] <= center + 500_000_000 and any(r[3])]
    prior_cruise = [active for nanos, active, _ in cruise if nanos < center]
    releases = [(nanos, data) for nanos, active, data in cruise
                if center <= nanos <= center + 500_000_000 and not active]
    release = releases[0] if releases else None
    observation_complete = (all(any(t < center and a == addr for t, a, _, _ in inputs)
                                and any(t > center and a == addr for t, a, _, _ in inputs)
                                for addr in (0xFE, 0x101)) and bool(prior_cruise)
                            and not counts['malformed_input'])
    if preceding:
        disposition = 'preceding_driver_input_confounds_acceptance'
    elif release and any(r[0] <= release[0] for r in later_input):
        disposition = 'intervening_driver_input_confounds_acceptance'
    elif not observation_complete:
        disposition = 'incomplete_input_coverage'
    elif not prior_cruise[-1]:
        disposition = 'cruise_already_inactive'
    elif release:
        disposition = 'unconfounded_release_candidate_not_acceptance_proof'
    else:
        disposition = 'no_native_release_in_window'
    witness = None
    if preceding:
        nanos, address, data, value = preceding[0]
        witness = {'nanos': nanos, 'offset_ms': round((nanos - center) / 1e6, 6),
                   'bus': info['physical_input_bus'], 'address': f'0x{address:03X}',
                   'payload': data.hex(), 'cancel_asserted': value[0], 'brake_asserted': value[1]}
    tx_counts = Counter((bus, address, len(data)) for _, bus, address, data in tx)
    return {'request_nanos': center, 'source_indices': info['source_indices'],
            'physical_input_bus': info['physical_input_bus'], 'cruise_bus': info['cruise_bus'],
            'disposition': disposition, 'input_coverage_complete': observation_complete,
            'preceding_driver_input': witness, 'native_cruise_active_before': prior_cruise[-1] if prior_cruise else None,
            'release_offset_ms': round((release[0] - center) / 1e6, 6) if release else None,
            'release_payload': release[1].hex() if release else None,
            'sendcan_attempts': [{'bus': bus, 'address': f'0x{address:03X}', 'length': length, 'count': count}
                                 for (bus, address, length), count in sorted(tx_counts.items())],
            'counts': dict(sorted(counts.items()))}


def build(path: Path = FIXTURE) -> dict:
    header, rows = read_fixture(path)
    grouped: dict[int, list[list]] = defaultdict(list)
    for row in rows:
        grouped[row[0]].append(row)
    windows = [reduce_window(info, grouped[i]) for i, info in enumerate(header['windows'])]
    offsets = [-w['preceding_driver_input']['offset_ms'] for w in windows if w['preceding_driver_input']]
    return {'schema': 'camry-cancel-request-causality-v1',
            'fixture': {'sha256': sha(path), 'sources': header['sources']},
            'windows': windows, 'dispositions': dict(Counter(w['disposition'] for w in windows)),
            'driver_to_host_request_ms': {'min': min(offsets), 'median': statistics.median(offsets), 'max': max(offsets)} if offsets else None,
            'boundaries': [
                'Times are rlog publication times, not wire arbitration times or measured actuator delay.',
                'sendcan is a host transmission attempt, not an ECU acceptance acknowledgement.',
                'A physical input can explain a subsequent cruise release even when the host also transmits a cancel-shaped packet.',
                'Absence of a recovered input in this window cannot prove a new command or rule out unobserved causes.',
                'The protected switch is observed, never generated or replayed onto a vehicle.',
            ]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, default=FIXTURE)
    parser.add_argument('--out', type=Path, default=OUTPUT)
    parser.add_argument('--extract', action='store_true')
    parser.add_argument('--extracted-fixture', type=Path)
    parser.add_argument('--log-root', type=Path, default=Path('/Users/kai/dev/inspect/logs/camry-2026'))
    parser.add_argument('--openpilot-root', type=Path, default=ROOT.parent / 'kai-openpilot')
    args = parser.parse_args()
    if args.extract:
        header, _ = read_fixture(args.fixture)
        extract(header, args.log_root, args.openpilot_root, args.extracted_fixture or args.fixture)
    report = build(args.extracted_fixture or args.fixture)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(args.out)
    print(json.dumps(report['dispositions']))


if __name__ == '__main__':
    main()
