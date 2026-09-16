#!/usr/bin/env python3
"""Retain passive original-log evidence for the Camry 0x160 role audit.

Only local rlogs are read. There is no Panda import, ECU session, frame builder,
or vehicle access. CAN publication batches and host/returned-TX distinctions
are retained; REFERENCE and build remain outside Git.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_FIXTURE = ROOT / 'tests/fixtures/camry_2026_longitudinal_role.jsonl.gz'
TRIAL_IDS = {0x08A, 0x0AA, 0x0CA, 0x13C, 0x160, 0x251}
DIRECTION_IDS = {0x08A, 0x0CA, 0x0C9, 0x160}
RESUME_IDS = {0x0AA, 0x0CA, 0x0FE, 0x101, 0x13C, 0x160}
GROUPS = (
    ('d1', 'logs/camry-2026/2026-09-11/000000d1--ad906be282', (3, 4, 5, 6, 9, 10, 11, 12), ()),
    ('d4', 'logs/camry-2026/2026-09-11/000000d4--327b2c4bb8', tuple(range(7)), ()),
    ('2d', 'captures/0000002d--4a4806c524', tuple(range(6)), ()),
    ('3b', 'logs/camry-2026/2026-09-04/0000003b--62262eb7a1', (83, 84, 85), (5122256000000,)),
    ('3c', 'logs/camry-2026/2026-09-04/0000003c--97b9e7a69a', (25, 26, 27, 28), (9068054000000, 9147517000000)),
)


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def extract(source_root: Path, openpilot_root: Path, output: Path) -> None:
    sys.path.insert(0, str(openpilot_root))
    from openpilot.tools.lib.logreader import LogReader

    sources, rows = [], []
    for group, relative, segments, centers in GROUPS:
        for segment in segments:
            name = f'{segment}.rlog.zst' if group == '2d' else f'rlog-{segment}.zst'
            path = source_root / relative / name
            source_index = len(sources)
            sources.append({'group': group, 'segment': segment,
                            'path': str(path.relative_to(source_root)), 'sha256': sha(path)})
            print(f'{group}: {name}', flush=True)
            for event in LogReader(str(path)):
                nanos, kind = int(event.logMonoTime), event.which()
                if centers and not any(abs(nanos - center) < 4_000_000_000 for center in centers):
                    continue
                payload = None
                if kind in ('can', 'sendcan'):
                    if group == '2d':
                        wanted = DIRECTION_IDS
                    elif centers:
                        wanted = RESUME_IDS
                    else:
                        wanted = TRIAL_IDS
                    payload = [[int(m.src), int(m.address), bytes(m.dat).hex()]
                               for m in getattr(event, kind) if m.address in wanted
                               and (kind == 'can' or m.address == 0x160)]
                    if not payload:
                        continue
                elif kind == 'carControl' and group in ('d1', 'd4'):
                    c = event.carControl
                    payload = [int(c.longActive), int(c.enabled), float(c.actuators.accel)]
                elif kind == 'carState' and group != '2d':
                    c = event.carState
                    payload = [float(c.vEgo), float(c.aEgo), int(c.gasPressed), int(c.brakePressed),
                               int(c.cruiseState.enabled), int(c.cruiseState.available),
                               int(c.cruiseState.standstill)]
                if payload is not None:
                    rows.append([source_index, nanos, kind, payload])
    header = {
        'schema': 'camry-longitudinal-role-fixture-v1', 'sources': sources,
        'selection': {
            'd1_d4': 'complete declared segments; selected CAN IDs, original sendcan, carState and carControl',
            '2d': 'complete six segments, both native and returned-TX sources for 08A/0CA/0C9/160',
            '3b_3c': 'original events within 4 seconds of the previously identified motion thresholds',
        },
        'resume_centers_ns': {g: list(c) for g, _, _, c in GROUPS if c},
        'carState_columns': ['vEgo', 'aEgo', 'gasPressed', 'brakePressed', 'cruiseEnabled', 'cruiseAvailable', 'cruiseStandstill'],
        'carControl_columns': ['longActive', 'enabled', 'actuatorAccel'],
        'topology': {'d1_d4': '0=ADAS downstream, 2=camera source, 1=unsplit chassis',
                     '2d_3b_3c': '0/2=historical chassis relay, 1=ADAS'},
        'timestamp_boundary': 'logMonoTime is a host publication timestamp shared by a CAN batch, not per-frame wire time',
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with (
        output.open('wb') as raw,
        gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as packed,
        io.TextIOWrapper(packed, encoding='utf-8') as stream,
    ):
        stream.write(json.dumps(header, separators=(',', ':')) + '\n')
        for row in rows:
            stream.write(json.dumps(row, separators=(',', ':')) + '\n')
    print(f'{output}: {len(rows)} events, SHA256 {sha(output)}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=ROOT.parents[1])
    parser.add_argument('--openpilot-root', type=Path, default=ROOT.parent / 'kai-openpilot')
    parser.add_argument('--output', type=Path, default=DEFAULT_FIXTURE)
    args = parser.parse_args()
    extract(args.source_root, args.openpilot_root, args.output)


if __name__ == '__main__':
    main()
