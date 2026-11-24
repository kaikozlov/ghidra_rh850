"""Compare the five 0x18C entries to ordinary Camry radar and camera leads in a local rlog route."""
from __future__ import annotations

import argparse
import hashlib
import json
from binascii import crc_hqx
from collections import Counter
from pathlib import Path

import numpy as np

from tools.targets.camry.analysis.analyze_camry_2026_bus1_camera_output import (
    decode_object_geometry, decode_object_relative_speed, near_returns_18c,
)
from tools.toyota_support.route_log import RouteLogReader, load_logreader


def compare_route(route: Path, reader: RouteLogReader) -> dict:
    files = sorted(route.glob(f'{route.name}--*/rlog.zst'), key=lambda p: int(p.parent.name.rsplit('--', 1)[1]))
    if not files:
        raise ValueError(f'no segmented rlogs under {route}')
    identity = set()
    hashes = hashlib.sha256()
    counts = Counter()
    overlap = Counter()
    lateral_pairs = []
    ego, vision, times, observations = [], [], [], []
    burst = {}
    start, header = 0, b''
    for path in files:
        with path.open('rb') as src:
            hashes.update((hashlib.file_digest(src, 'sha256').hexdigest() + '\n').encode())
        for event in reader(path, sort_by_time=False):
            t = event.logMonoTime
            kind = event.which()
            if kind == 'carParams':
                identity.add((event.carParams.carFingerprint, event.carParams.radarUnavailable))
            elif kind == 'carState':
                ego.append((t, event.carState.vEgo))
            elif kind == 'modelV2' and event.modelV2.leadsV3:
                lead = event.modelV2.leadsV3[0]
                if lead.x:
                    vision.append((t, lead.prob, lead.x[0] - 1.52, -lead.y[0], lead.v[0]))
            elif kind == 'can':
                for frame in event.can:
                    a = frame.address
                    if frame.src != 1 or not 0x180 <= a <= 0x18C:
                        continue
                    d = frame.dat
                    if len(d) != (48 if a == 0x18C else 64) or int.from_bytes(d[:2], 'little') != crc_hqx(d[2:] + a.to_bytes(2, 'little'), 0xffff):
                        counts['invalid_frames'] += 1
                        burst.clear()
                        continue
                    counts['valid_frames'] += 1
                    if burst and (d[2:4] != header or t - start >= 50_000_000 or a in burst):
                        burst.clear()
                    if not burst:
                        start, header = t, d[2:4]
                    burst[a] = d
                    if len(burst) != 13:
                        continue
                    counts['complete_cycles'] += 1
                    near = np.array([row[1:] for row in near_returns_18c(burst[0x18C])])
                    if len(near):
                        normal = []
                        for bank in range(3):
                            for off in range(4, 60, 7):
                                g = burst[0x180 + bank][off:off + 7]
                                m = burst[0x183 + bank][off:off + 7]
                                x, y = decode_object_geometry(g)
                                if 0 < x < 0xfff8 * .005 and m[5] & 3 and (m[4] & 128 or not m[5] & 16):
                                    normal.append((x, y, decode_object_relative_speed(m)))
                        core = np.array(normal).reshape(-1, 3)
                        counts['populated_entries'] += len(near)
                        if len(core):
                            dif = abs(near[:, None, :] - core)
                            counts['with_core_neighbor'] += int(np.all(dif <= 1, axis=2).any(axis=1).sum())
                            # Pick by range and rate only; lateral sign/scale stays independent of selection.
                            for delta, (_, y, _) in zip(dif, near, strict=True):
                                cost = delta[:, 0] + 2 * delta[:, 2]
                                i = cost.argmin()
                                if delta[i, 0] < .5 and delta[i, 2] < .5 and (len(cost) == 1 or np.partition(cost, 1)[1] - cost[i] > .8):
                                    lateral_pairs.append((y, core[i, 1]))
                        times.append(start)
                        observations.append((near, core))
                    burst.clear()
    if identity != {('TOYOTA_CAMRY_TSS3', False)}:
        raise ValueError(f'unexpected recorded radar configuration: {identity}')
    if times and vision and ego:
        camera = np.array(vision)
        state = np.array(ego)
        ego_interp = np.interp(times, state[:, 0], state[:, 1])
        for t, speed, (near, core) in zip(times, ego_interp, observations, strict=True):
            i = np.searchsorted(camera[:, 0], t)
            i = min(range(max(i - 1, 0), min(i + 1, len(camera))), key=lambda j: abs(camera[j, 0] - t))
            ts, prob, x, y, v = camera[i]
            if prob < .9 or abs(ts - t) > 35_000_000:
                continue
            target = (x, y, v - speed)
            if np.all(abs(near - target) <= (1, 1, 1.5), axis=1).any():
                also_core = np.all(abs(core - target) <= (1, 1, 1.5), axis=1).any()
                overlap['both' if also_core else 'near_only'] += 1
    pairs = np.array(lateral_pairs)
    return {'route': route.name, 'segments': len(files), 'sha256_of_ordered_sha256_lines': hashes.hexdigest(), **counts,
            'lateral_pairs': len(pairs), 'lateral_r': float(np.corrcoef(pairs.T)[0, 1]) if len(pairs) > 1 else None,
            'vision_agreement_cycles': overlap}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('route', type=Path, nargs='+')
    parser.add_argument('--openpilot-root', type=Path, required=True, help='openpilot checkout providing the Cereal schema')
    args = parser.parse_args()
    reader = load_logreader(args.openpilot_root)
    for route in args.route:
        print(json.dumps(compare_route(route, reader), sort_keys=True), flush=True)
