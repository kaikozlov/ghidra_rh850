#!/usr/bin/env python3
"""Replay retained source bytes through the maintained opendbc RadarInterface.

Run with kai-openpilot's Python environment. Historical repin sources are
explicitly remapped from their observed source bus to stock-harness radar bus0;
the two stock-harness sources require no remapping. No vehicle connection.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENDBC = Path(os.environ.get('TOYOTA_OPENDBC_ROOT', ROOT.parent / 'kai-openpilot/opendbc_repo'))
PYTHON = OPENDBC.parent / '.venv/bin/python'
if '--worker' not in sys.argv:
    if not PYTHON.is_file() or not (OPENDBC / 'opendbc/car/toyota/radar_interface.py').is_file():
        print('[SKIP] external maintained opendbc/Python environment is unavailable')
        raise SystemExit(77)
    result = subprocess.run([str(PYTHON), str(Path(__file__).resolve()), '--worker'], cwd=ROOT, timeout=90)
    raise SystemExit(result.returncode)
sys.path.insert(0, str(OPENDBC))
from opendbc.car import CanData
from opendbc.car.toyota.interface import CarInterface
from opendbc.car.toyota.radar_interface import RadarInterface
from opendbc.car.toyota.values import CAR


def check_holdout() -> None:
    path = ROOT / 'tests/fixtures/camry_2026_radar_lifecycle_holdout.jsonl.gz'
    params = CarInterface.get_non_essential_params(CAR.TOYOTA_CAMRY_TSS3)
    assert not params.radarUnavailable
    source, interface, prior = None, None, {}
    counts = Counter()
    with gzip.open(path, 'rt') as stream:
        header = json.loads(next(stream))
        assert header['source_bus'] == 1
        for line in stream:
            index, nanos, bank, geometry, motion = json.loads(line)
            if index != source:
                source, interface, prior = index, RadarInterface(params), {}
                assert interface.rcp.bus == 0
            frames = [CanData(0x180 + bank, bytes.fromhex(geometry), 0),
                      CanData(0x183 + bank, bytes.fromhex(motion), 0)]
            output = interface.update([(nanos, frames)])
            counts['banks'] += 1
            if output is None:
                continue
            assert not output.errors.canError
            counts['outputs'] += 1
            counts['points'] += len(output.points)
            for slot, point in interface.pts.items():
                raw = interface.rcp.vl[0x183 + slot // 8]
                field = slot % 8
                assert raw[f'TRACK_STATE_{field}'] != 0
                if slot in prior and (raw[f'NEW_TRACK_{field}'] or raw[f'TRACK_ENDED_{field}']):
                    assert prior[slot] != point.trackId
                    counts['replacements'] += 1
            prior = {slot: point.trackId for slot, point in interface.pts.items()}
    assert counts == {'banks': 60969, 'outputs': 20323, 'points': 308111, 'replacements': 17868}, counts
    print('PASS: 17-source holdout:', dict(counts))


def check_original_publication_boundaries() -> None:
    path = ROOT / 'tests/fixtures/camry_2026_radar_lifecycle.jsonl.gz'
    params = CarInterface.get_non_essential_params(CAR.TOYOTA_CAMRY_TSS3)
    source, interface = None, None
    counts = [Counter() for _ in range(6)]
    with gzip.open(path, 'rt') as stream:
        header = json.loads(next(stream))
        assert [source['radar_bus'] for source in header['sources']] == [1, 1, 1, 1, 0, 0]
        for line in stream:
            index, nanos, frames = json.loads(line)
            if index != source:
                source, interface = index, RadarInterface(params)
            output = interface.update([(nanos, [CanData(address, bytes.fromhex(data), 0) for address, data in frames])])
            counts[index]['frames'] += len(frames)
            if output is not None:
                assert not output.errors.canError
                counts[index]['outputs'] += 1
                counts[index]['points'] += len(output.points)
    assert [c['outputs'] for c in counts] == [1200, 1200, 1200, 1200, 1199, 1199], counts
    assert [c['points'] for c in counts] == [16923, 21249, 20135, 19831, 19649, 21573], counts
    assert [c['frames'] for c in counts] == [7200, 7201, 7200, 7200, 7199, 7198], counts
    print('PASS: original publication boundaries, including two stock-harness sources:', [dict(c) for c in counts])


if __name__ == '__main__':
    check_holdout()
    check_original_publication_boundaries()
