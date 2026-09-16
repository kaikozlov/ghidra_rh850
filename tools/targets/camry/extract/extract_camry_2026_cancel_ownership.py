#!/usr/bin/env python3
"""Retain all-bus cancellation windows and independently discover host attempts.

Offline only: reads original rlogs. It neither imports Panda nor transmits CAN.
Host attempts are discovered from sendcan, never from forwarding/TX echoes.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import sys
from collections import Counter, deque
from itertools import chain
from pathlib import Path

from tools.targets.camry.extract.extract_camry_2026_cancel_windows import WINDOWS

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / 'tests/fixtures'
ROUTES = (
    ('2026-09-01', '00000037--dec6fe39cb'),
    ('2026-09-04', '0000003b--62262eb7a1'),
    ('2026-09-04', '0000003c--97b9e7a69a'),
    ('2026-09-04', '0000003d--0e812cecba'),
    ('2026-09-06', '0000003e--1a2f20417d'),
    ('2026-09-06', '0000003f--36e72f5fdc'),
    ('2026-09-07', '00000045--805b7ca6ab'),
    ('2026-09-07', '00000048--709f22277b'),
    ('2026-09-10', '0000008d--a9f348691a'),
    ('2026-09-10', '00000093--4066e7ae51'),
)
HOST_IDS = {0x101, 0xFE, 0x8A, 0x251, 0x116, 0x1B2}
RADIUS = 2_000_000_000


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_rows(path: Path, header: dict, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with (path.open('wb') as raw,
          gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed,
          io.TextIOWrapper(compressed, encoding='utf-8') as stream):
        for row in chain((header,), rows):
            stream.write(json.dumps(row, separators=(',', ':')) + '\n')


def source_record(path: Path, root: Path) -> dict:
    return {'path': str(path.relative_to(root)), 'sha256': sha(path)}


def extract_buses(log_root: Path, reader, output: Path) -> None:
    metadata, rows = [], []
    for index, (center, relatives) in enumerate(WINDOWS):
        sources = [source_record(log_root / relative, log_root) for relative in relatives]
        metadata.append({'kind': 'switch_cancel', 'center_ns': center, 'sources': sources})
        for source_index, relative in enumerate(relatives):
            for event in reader(str(log_root / relative)):
                nanos = int(event.logMonoTime)
                if event.which() != 'can' or abs(nanos - center) > 1_000_000_000:
                    continue
                frames = [[int(m.src), int(m.address), bytes(m.dat).hex()]
                          for m in event.can if m.src in (0, 1, 2)]
                if frames:
                    rows.append([index, source_index, nanos, frames])
    for route in ('000000d1--ad906be282', '000000d4--327b2c4bb8'):
        for segment in (3, 4):
            path = log_root / '2026-09-11' / route / f'rlog-{segment}.zst'
            index, start = len(metadata), None
            for event in reader(str(path)):
                if event.which() != 'can':
                    continue
                nanos = int(event.logMonoTime)
                if start is None:
                    start = nanos
                if nanos > start + 1_000_000_000:
                    break
                frames = [[int(m.src), int(m.address), bytes(m.dat).hex()] for m in event.can
                          if m.src in (0, 1, 2) and m.address in {0x101, 0xFE, 0x198, 0x19C, 0x1B2, 0x371, 0x5F6}]
                if frames:
                    rows.append([index, 0, nanos, frames])
            metadata.append({'kind': 'stock_placement', 'start_ns': start,
                             'sources': [source_record(path, log_root)]})
    write_rows(output, {
        'schema': 'camry-cancel-all-bus-windows-v1', 'windows': metadata,
        'layout': 'historical repin: chassis/car bus0, FRC chassis side bus2, ADAS bus1',
        'selection': 'switch_cancel: all native 0/1/2 frames within +/-1s, no address/length filter; stock_placement: selected native mirror IDs in the first second of four stock-harness rlogs',
        'timestamps': 'host publication timestamps, not physical wire arbitration timing',
    }, rows)
    print(output, flush=True)


def route_paths(root: Path) -> list[Path]:
    candidates = []
    for path in root.rglob('rlog*.zst'):
        match = re.fullmatch(r'rlog-(\d+)\.zst', path.name)
        if match:
            candidates.append((int(match[1]), path))
        elif path.name == 'rlog.zst' and path.parent.name.rsplit('--', 1)[-1].isdigit():
            candidates.append((int(path.parent.name.rsplit('--', 1)[-1]), path))
    if len({segment for segment, _ in candidates}) != len(candidates):
        raise ValueError(f'duplicate segment representations: {root}')
    if not candidates:
        raise ValueError(f'no complete rlog segments: {root}')
    return [p for _, p in sorted(candidates)]


def extract_hosts(log_root: Path, reader, output: Path) -> None:
    sources, routes, episodes = [], [], []
    for date, name in ROUTES:
        paths = route_paths(log_root / date / name)
        route_index = len(routes)
        source_indices = []
        counts, native_counts = Counter(), Counter()
        buffer = deque()
        active = None
        route_episodes = []
        previous_control = None
        for path in paths:
            source_index = len(sources)
            source_indices.append(source_index)
            sources.append(source_record(path, log_root))
            for event in reader(str(path)):
                nanos, kind = int(event.logMonoTime), event.which()
                if active is not None and nanos > active['last_send_ns'] + RADIUS:
                    route_episodes.append(active)
                    active = None
                while buffer and buffer[0][1] < nanos - RADIUS:
                    buffer.popleft()
                data = None
                if kind in ('can', 'sendcan'):
                    frames = getattr(event, kind)
                    data = [[int(m.src), int(m.address), bytes(m.dat).hex()]
                            for m in frames if m.address in HOST_IDS]
                    if kind == 'can':
                        native_counts.update((int(m.src), int(m.address), len(m.dat))
                                             for m in frames if m.src in (0, 1, 2) and m.address in HOST_IDS)
                    else:
                        attempts = [m for m in frames if m.address == 0x101]
                        counts.update((int(m.src), len(m.dat)) for m in attempts)
                        if attempts:
                            if active is None:
                                active = {'route': route_index, 'first_send_ns': nanos, 'rows': list(buffer)}
                            active['last_send_ns'] = nanos
                elif kind == 'carControl':
                    c = event.carControl
                    control = [bool(c.enabled), bool(c.latActive), bool(c.longActive), bool(c.cruiseControl.cancel)]
                    if control != previous_control:
                        data = control
                        previous_control = control
                elif kind == 'selfdriveState' and event.selfdriveState.alertType:
                    data = [str(event.selfdriveState.state), str(event.selfdriveState.alertType)]
                if data is None or not data:
                    continue
                row = [source_index, nanos, kind, data]
                if active is not None:
                    active['rows'].append(row)
                buffer.append(row)
        if active is not None:
            route_episodes.append(active)
        episodes.extend(route_episodes)
        routes.append({'date': date, 'route': name, 'source_indices': source_indices,
                       'host_0x101': [{'bus': b, 'length': n, 'count': c} for (b, n), c in sorted(counts.items())],
                       'native_counts': [{'bus': b, 'address': hex(a), 'length': n, 'count': c}
                                         for (b, a, n), c in sorted(native_counts.items())],
                       'episodes': len(route_episodes)})
        print(name, len(paths), 'segments;', sum(counts.values()), 'host frames;', len(route_episodes), 'episodes', flush=True)
    metadata = [{k: v for k, v in e.items() if k != 'rows'} for e in episodes]
    rows = ([index, *row] for index, episode in enumerate(episodes) for row in episode['rows'])
    write_rows(output, {
        'schema': 'camry-cancel-host-attempts-v1', 'routes': routes, 'sources': sources, 'episodes': metadata,
        'layout': 'historical repin: native switch/brake bus0 and cruise bus2; host brake sender bus2',
        'selection': 'every sendcan 0x101 in the enumerated complete routes; group sends separated by <=2s; retain +/-2s',
        'format_boundary': 'address, payload, source, publication time only; no FDF/BRS claim from the current cereal schema',
    }, rows)
    print(output, flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--log-root', type=Path, default=ROOT.parents[1] / 'logs/camry-2026')
    ap.add_argument('--openpilot-root', type=Path, default=ROOT.parent / 'kai-openpilot')
    ap.add_argument('--output-dir', type=Path, default=FIXTURES)
    ap.add_argument('--kind', choices=('buses', 'hosts', 'both'), default='both')
    args = ap.parse_args()
    sys.path.insert(0, str(args.openpilot_root))
    from openpilot.tools.lib.logreader import LogReader
    if args.kind in ('buses', 'both'):
        extract_buses(args.log_root, LogReader, args.output_dir / 'camry_2026_cancel_all_buses.jsonl.gz')
    if args.kind in ('hosts', 'both'):
        extract_hosts(args.log_root, LogReader, args.output_dir / 'camry_2026_cancel_host_attempts.jsonl.gz')


if __name__ == '__main__':
    main()
