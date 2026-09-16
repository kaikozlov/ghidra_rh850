#!/usr/bin/env python3
"""Retain unfiltered radar frames from six original Camry rlog segments.

Historical repinned captures use bus 1; the two final stock-harness captures
use bus 0. Only the observed source bus and radar message family are selected.
This extractor never connects to a vehicle and never generates CAN traffic.
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
SOURCES = (
    ('2026-09-04', '0000003b--62262eb7a1', 54, 1),
    ('2026-09-04', '0000003b--62262eb7a1', 90, 1),
    ('2026-09-10', '0000008d--a9f348691a', 6, 1),
    ('2026-09-10', '00000093--4066e7ae51', 3, 1),
    ('2026-09-11', '000000d1--ad906be282', 3, 0),
    ('2026-09-11', '000000d4--327b2c4bb8', 4, 0),
)
OUTPUT = ROOT / 'tests/fixtures/camry_2026_radar_lifecycle.jsonl.gz'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--openpilot-root', type=Path, default=ROOT.parent / 'kai-openpilot')
    parser.add_argument('--log-root', type=Path, default=ROOT.parents[1] / 'logs/camry-2026')
    parser.add_argument('--out', type=Path, default=OUTPUT)
    args = parser.parse_args()
    sys.path.insert(0, str(args.openpilot_root))
    from openpilot.tools.lib.logreader import LogReader

    sources = []
    paths = []
    for date, route, segment, bus in SOURCES:
        path = args.log_root / date / route / f'rlog-{segment}.zst'
        sources.append({'path': str(path.relative_to(args.log_root)),
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'radar_bus': bus})
        paths.append(path)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('wb') as stream:
        with gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding='utf-8') as output:
                def emit(row):
                    output.write(json.dumps(row, separators=(',', ':')) + '\n')
                emit({'schema': 'camry-radar-lifecycle-fixture-v1', 'sources': sources})
                for index, (source, path) in enumerate(zip(sources, paths, strict=True)):
                    for event in LogReader(str(path)):
                        if event.which() != 'can':
                            continue
                        frames = [[m.address, bytes(m.dat).hex()] for m in event.can
                                  if m.src == source['radar_bus'] and 0x180 <= m.address <= 0x185]
                        if frames:
                            emit([index, int(event.logMonoTime), frames])
    print(args.out)


if __name__ == '__main__':
    main()
