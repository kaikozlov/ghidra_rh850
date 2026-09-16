#!/usr/bin/env python3
"""Retain original source windows around observed driver CANCEL transitions.

This is an offline rlog extractor, not a vehicle cancellation experiment.
The event selection is frozen; raw bytes, timestamps, and original hashes
are acquired again from the corresponding rlog files on regeneration.
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
OUTPUT = ROOT / 'tests/fixtures/camry_2026_cancel_windows.jsonl.gz'
WINDOWS = [(944177318754, ('2026-09-04/0000003b--62262eb7a1/rlog-14.zst',)),
 (1765674076305, ('2026-09-04/0000003b--62262eb7a1/rlog-28.zst',)),
 (2506506722272, ('2026-09-04/0000003b--62262eb7a1/rlog-40.zst',)),
 (3301638307698, ('2026-09-04/0000003b--62262eb7a1/rlog-54.zst',)),
 (3442747385144, ('2026-09-04/0000003b--62262eb7a1/rlog-56.zst',)),
 (4011390671646,
  ('2026-09-04/0000003b--62262eb7a1/rlog-65.zst', '2026-09-04/0000003b--62262eb7a1/rlog-66.zst')),
 (4480811557717, ('2026-09-04/0000003b--62262eb7a1/rlog-73.zst',)),
 (4729058273976, ('2026-09-04/0000003b--62262eb7a1/rlog-77.zst',)),
 (4785218367497, ('2026-09-04/0000003b--62262eb7a1/rlog-78.zst',)),
 (5452185405211, ('2026-09-04/0000003b--62262eb7a1/rlog-90.zst',)),
 (5864015418960, ('2026-09-04/0000003b--62262eb7a1/rlog-96.zst',)),
 (5896422235458, ('2026-09-04/0000003b--62262eb7a1/rlog-97.zst',)),
 (8479996219889, ('2026-09-04/0000003c--97b9e7a69a/rlog-16.zst',)),
 (9838689485569, ('2026-09-04/0000003c--97b9e7a69a/rlog-39.zst',)),
 (10017511754928, ('2026-09-04/0000003c--97b9e7a69a/rlog-42.zst',)),
 (10505504054585, ('2026-09-04/0000003c--97b9e7a69a/rlog-50.zst',)),
 (10714004826172, ('2026-09-04/0000003c--97b9e7a69a/rlog-53.zst',)),
 (10740190154548, ('2026-09-04/0000003c--97b9e7a69a/rlog-54.zst',)),
 (11038342725840, ('2026-09-04/0000003c--97b9e7a69a/rlog-59.zst',)),
 (22984178110606, ('2026-09-04/0000003d--0e812cecba/rlog-18.zst',)),
 (24852900632185, ('2026-09-04/0000003d--0e812cecba/rlog-49.zst',))]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--openpilot-root', type=Path, default=ROOT.parent / 'kai-openpilot')
    parser.add_argument('--log-root', type=Path, default=ROOT.parents[1] / 'logs/camry-2026')
    parser.add_argument('--out', type=Path, default=OUTPUT)
    args = parser.parse_args()
    sys.path.insert(0, str(args.openpilot_root))
    from openpilot.tools.lib.logreader import LogReader
    windows = []
    for center, paths in WINDOWS:
        sources = [{'path': path, 'sha256': hashlib.sha256((args.log_root / path).read_bytes()).hexdigest()}
                   for path in paths]
        windows.append({'route': Path(paths[0]).parent.name, 'center_nanos': center, 'sources': sources})
    header = {'schema': 'camry-cancel-windows-v2', 'window_radius_ns': 1_000_000_000,
              'source_layout': 'historical repin: switch/brake bus0; native cruise state bus2; ADAS sideband bus1',
              'windows': windows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('wb') as stream:
        with gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding='utf-8') as output:
                def emit(row):
                    output.write(json.dumps(row, separators=(',', ':')) + '\n')
                emit(header)
                for index, (center, paths) in enumerate(WINDOWS):
                    for relative in paths:
                        segment = int(Path(relative).stem.split('-')[-1])
                        for event in LogReader(str(args.log_root / relative)):
                            nanos = int(event.logMonoTime)
                            if event.which() != 'can' or abs(nanos - center) > 1_000_000_000:
                                continue
                            frames = []
                            for m in event.can:
                                selected = ((m.src == 1 and len(m.dat) >= 12)
                                            or (m.src == 0 and m.address in (0xfe, 0x101))
                                            or (m.src == 2 and m.address in (0x8a, 0x251)))
                                if selected:
                                    frames.append([m.src, m.address, bytes(m.dat).hex()])
                            if frames:
                                emit([index, segment, nanos, frames])
    print(args.out)


if __name__ == '__main__':
    main()
