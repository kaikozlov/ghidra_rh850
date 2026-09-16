#!/usr/bin/env python3
"""Recover source-driven object lifecycle from passive Camry CAN captures.

Discovery uses both complete August drives. Seventeen disjoint September log
segments verify the resulting bit positions without fitting them again. GTS+
provides object/fusion vocabulary, not a CAN field map or a quality threshold.
"""
from __future__ import annotations

import argparse
import binascii
import gzip
import hashlib
import io
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / 'tests/fixtures/camry_2026_radar_lifecycle_holdout.jsonl.gz'
OUTPUT = ROOT / 'data/generated/camry_2026_radar_lifecycle.json'
DRIVES = {
    'august_a': ROOT / 'targets/camry-2026/raw-20260827/camry_relay_route_can_20260827.ndjson.gz',
    'august_b': ROOT / 'targets/camry-2026/raw-20260827/camry_relay_lta_confirm_route_can_20260827.ndjson.gz',
}
EMPTY = bytes.fromhex('fff8000000ffff')


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def banks(frames: Iterable[tuple[int, int, int, bytes]], counts: Counter) -> Iterator[list]:
    """Join a geometry/motion pair only within the same source and source cycle."""
    pending = {}
    emitted = {}
    for source, nanos, address, data in frames:
        if not 0x180 <= address <= 0x185 or len(data) != 64:
            continue
        expected = binascii.crc_hqx(data[2:] + address.to_bytes(2, 'little'), 0xFFFF)
        if int.from_bytes(data[:2], 'little') != expected:
            counts['crc_invalid'] += 1
            continue
        counts['crc_valid'] += 1
        bank = (address - 0x180) % 3
        key = source, bank
        pending.setdefault(key, {})[address] = nanos, data
        pair = pending[key]
        if len(pair) != 2:
            continue
        ta, a = pair[0x180 + bank]
        tb, b = pair[0x183 + bank]
        if a[2:4] != b[2:4] or abs(ta - tb) > 50_000_000 or emitted.get(key) == (ta, tb):
            continue
        emitted[key] = ta, tb
        yield [source, min(ta, tb), bank, a.hex(), b.hex()]


def raw_frames(path: Path):
    with gzip.open(path, 'rt') as f:
        for line in f:
            segment, nanos, bus, address, data = json.loads(line)
            if bus == 1 and 0x180 <= address <= 0x185:
                yield segment, nanos, address, bytes.fromhex(data)


def decode(a: bytes, b: bytes) -> tuple[float, float, float]:
    lateral = int.from_bytes(a[2:4], 'big') >> 4
    speed = int.from_bytes(b[1:3], 'big') & 0x3FFF
    return (int.from_bytes(a[:2], 'big') * .005,
            ((lateral + 2048) % 4096 - 2048) * .04,
            ((speed + 8192) % 16384 - 8192) * .025)


def reduce_rows(rows: Iterable[list]) -> dict:
    counts = Counter()
    states = Counter()
    previous = {}
    examples = {}
    for source, nanos, bank, ah, bh in rows:
        a, b = bytes.fromhex(ah), bytes.fromhex(bh)
        if a[2:4] != b[2:4]:
            raise ValueError('mixed source cycles')
        for address, data in ((0x180 + bank, a), (0x183 + bank, b)):
            if len(data) != 64 or int.from_bytes(data[:2], 'little') != binascii.crc_hqx(data[2:] + address.to_bytes(2, 'little'), 0xFFFF):
                raise ValueError('corrupt lifecycle fixture')
        counts['bank_cycles'] += 1
        for slot in range(8):
            offset = 4 + slot * 7
            aa, bb = a[offset:offset + 7], b[offset:offset + 7]
            occupied = aa != EMPTY
            started, ended = bool(bb[4] & 0x80), bool(bb[5] & 0x10)
            state = bb[5] & 3
            states[f'{"occupied" if occupied else "empty"}_state_{state}'] += 1
            counts['object_samples'] += 1
            counts['occupied'] += occupied
            counts['nonempty_state_zero'] += occupied and state == 0
            counts['empty_state_nonzero'] += not occupied and state != 0
            counts['occupied_end_and_start'] += occupied and started and ended
            x, y, v = decode(aa, bb)
            key = source, bank, slot
            prior = previous.get(key)
            if prior is not None:
                pt, po, px, py, pv, pc, pa, pb = prior
                dt = (nanos - pt) * 1e-9
                if .035 < dt < .075 and (a[2] - pc) % 256 == 1:
                    categories = []
                    if occupied and not po:
                        categories.append('birth')
                    if po and not occupied:
                        categories.append('death')
                    if po and occupied:
                        residual = abs(x - px - (v + pv) * dt / 2)
                        if residual > 5 or abs(y - py) > 3 or abs(v - pv) > 8:
                            categories.append('large_change')
                        if residual < .5 and abs(y - py) < .5 and abs(v - pv) < 1:
                            categories.append('steady')
                    for category in categories:
                        counts[category] += 1
                        counts[category + '_start'] += started
                        counts[category + '_end'] += ended
                        example_key = 'occupied_replacement' if category == 'large_change' and started and ended else category
                        examples.setdefault(example_key, {
                            'source': source, 'time_ns': nanos, 'bank': bank, 'slot': slot,
                            'before': [pa, pb], 'after': [aa.hex(), bb.hex()],
                        })
            previous[key] = nanos, occupied, x, y, v, a[2], aa.hex(), bb.hex()
    return {'counts': dict(sorted(counts.items())), 'raw_state_counts': dict(sorted(states.items())), 'examples': examples}


def extract(openpilot_root: Path, log_root: Path) -> None:
    sys.path.insert(0, str(openpilot_root))
    from openpilot.tools.lib.logreader import LogReader
    sources = json.loads((ROOT / 'data/generated/camry_2026_radar_anchors.json').read_text())['fixture']['sources']
    rows, source_counts = [], []
    for index, source in enumerate(sources):
        path = log_root / source['path']
        if sha(path) != source['sha256']:
            raise ValueError(f'source identity mismatch: {path}')
        def frames():
            for event in LogReader(str(path)):
                if event.which() == 'can':
                    for frame in event.can:
                        if frame.src == 1:
                            yield index, event.logMonoTime, frame.address, bytes(frame.dat)
        counts = Counter()
        part = list(banks(frames(), counts))
        rows.extend(part)
        source_counts.append({'banks': len(part), **counts})
    header = {'schema': 'camry-radar-lifecycle-holdout-v1', 'source_bus': 1,
              'source_topology': 'historical repin', 'sources': sources, 'source_counts': source_counts}
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    with FIXTURE.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding='utf-8') as f:
                for row in (header, *rows):
                    f.write(json.dumps(row, separators=(',', ':')) + '\n')


def build() -> dict:
    datasets = {}
    for name, path in DRIVES.items():
        counts = Counter()
        reduction = reduce_rows(banks(raw_frames(path), counts))
        datasets[name] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'integrity': dict(counts), **reduction}
    with gzip.open(FIXTURE, 'rt') as f:
        header = json.loads(next(f))
        datasets['september_holdout'] = {'fixture_sha256': sha(FIXTURE), 'header': header,
                                         **reduce_rows(json.loads(line) for line in f)}
    return {
        'schema': 'camry-2026-radar-lifecycle-v1', 'datasets': datasets,
        'wire': {'motion_record_bytes': 7, 'start': 'record B byte4 bit7', 'end_previous': 'record B byte5 bit4',
                 'raw_state': 'record B byte5 low2; zero is not a qualified measurement',
                 'geometry_empty_sentinel': EMPTY.hex(), 'cycle': 'both PDU bytes2 and3 increment independently modulo256'},
        'interpretation': {
            'lifecycle': 'Birth, deletion and occupied-to-occupied replacement are source flags, not motion thresholds.',
            'processing_order': 'End old identity, then start replacement; both flags may be set in one occupied record.',
            'qualifier': 'Reject empty/sentinel range and raw state zero. Keep states1/2/3 unnamed; no confidence percentage or radar-versus-camera attribution is inferred.',
            'loss': 'An unobserved cycle may contain a one-frame end/start event; restart identities rather than silently bridge it.',
            'boundary': 'These are passive wire/lifecycle observations. The precise nonzero state labels and additional object-class/confidence fields are not recovered.',
        },
        'motion_screen': {'adjacent_seconds': [.035, .075], 'counter_delta': 1,
                          'large_change': 'range residual>5m OR lateral delta>3m OR relative-speed delta>8m/s',
                          'steady': 'range residual<0.5m AND lateral delta<0.5m AND relative-speed delta<1m/s',
                          'purpose': 'corroboration only; these thresholds are NOT controller/parser policy'},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract-holdout', action='store_true')
    parser.add_argument('--openpilot-root', type=Path, default=Path('/Users/kai/dev/inspect/repos/kai-openpilot'))
    parser.add_argument('--log-root', type=Path, default=Path('/Users/kai/dev/inspect/logs/camry-2026'))
    parser.add_argument('--out', type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.extract_holdout:
        extract(args.openpilot_root, args.log_root)
    result = build()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(args.out)
    for name, data in result['datasets'].items():
        print(name, data['counts'])


if __name__ == '__main__':
    main()
