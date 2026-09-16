#!/usr/bin/env python3
"""Pin stock-Toyota-B native message sides from retained September 11 logs."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / 'data/generated/camry_2026_stock_harness_topology.json'
LOG_ROOT = Path('/Users/kai/dev/inspect/logs/camry-2026/2026-09-11')
OPENPILOT = Path('/Users/kai/dev/inspect/repos/kai-openpilot')
ROUTES = ('000000d1--ad906be282', '000000d4--327b2c4bb8')
IDS = (0x025, 0x030, 0x101, 0x160, *range(0x180, 0x186), 0x412)


def analyze(log_root: Path, openpilot: Path) -> dict:
    sys.path.insert(0, str(openpilot))
    from openpilot.tools.lib.logreader import LogReader
    sources = []
    for route in ROUTES:
        for segment in (3, 4):
            path = log_root / route / f'rlog-{segment}.zst'
            counts, samples = Counter(), {}
            for event in LogReader(str(path)):
                if event.which() != 'can':
                    continue
                for frame in event.can:
                    if frame.src not in (0, 1, 2) or frame.address not in IDS:
                        continue
                    key = (frame.address, frame.src, len(frame.dat))
                    counts[key] += 1
                    samples.setdefault(key, {'mono_ns': event.logMonoTime, 'payload': bytes(frame.dat).hex()})
            sources.append({
                'path': str(path.relative_to(log_root)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'native_messages': [{'address': hex(a), 'bus': b, 'length': n, 'count': count, **samples[a, b, n]}
                                    for (a, b, n), count in sorted(counts.items())],
            })
    return {'schema': 'camry-stock-harness-topology-v1', 'sources': sources,
            'boundary': 'incident-era native traffic proves message placement, not healthy EPS operation or actuation; EPS 0x030 is absent',
            'parser_bus': {'radar_objects': 0, 'camera_0x160': 2, 'chassis_0x025_0x101_0x412': 1},
            'hud_cancel_replacement_on_adas_relay_qualified': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=OUTPUT)
    ap.add_argument('--log-root', type=Path, default=LOG_ROOT)
    ap.add_argument('--openpilot-root', type=Path, default=OPENPILOT)
    args = ap.parse_args()
    result = analyze(args.log_root, args.openpilot_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(args.out)


if __name__ == '__main__':
    main()
