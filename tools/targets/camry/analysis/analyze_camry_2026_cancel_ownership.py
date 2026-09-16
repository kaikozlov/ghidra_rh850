#!/usr/bin/env python3
"""Separate a decoded cancellation indication from evidence of receiver acceptance.

Uses raw all-bus windows, stationary GTS/button observations, and actual host
attempts. This tool is passive; it creates no CAN sender or executable command.
"""
from __future__ import annotations

import argparse
import binascii
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BUSES = ROOT / 'tests/fixtures/camry_2026_cancel_all_buses.jsonl.gz'
HOSTS = ROOT / 'tests/fixtures/camry_2026_cancel_host_attempts.jsonl.gz'
STATIONARY = ROOT / 'targets/camry-2026/raw-20260826/camry_nrtd_cruise_can_sync_20260826.json.gz'
OUTPUT = ROOT / 'data/generated/camry_2026_cancel_ownership.json'


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load_rows(path: Path):
    with gzip.open(path, 'rt') as stream:
        header = json.loads(next(stream))
        rows = [json.loads(line) for line in stream]
    return header, rows


def switch(data: bytes, name: str = 'cancel') -> bool:
    if len(data) != 32:
        raise ValueError('switch frame is not 32 bytes')
    byte, mask, inverse_byte, inverse_mask = {
        'cancel': (4, 0x40, 7, 0x20), 'res_plus': (3, 0x80, 6, 0x80), 'set_minus': (4, 0x80, 7, 0x40),
    }[name]
    return bool(data[byte] & mask) and not bool(data[inverse_byte] & inverse_mask)


def edges(samples, bit):
    """Return each rising interval; an initially asserted sample is not an edge."""
    result, start = [], None
    previous = None
    for time, data in samples:
        value = bool(data[0] & (1 << bit))
        if previous is False and value:
            start = time
        if previous is True and not value and start is not None:
            result.append([start, time])
            start = None
        previous = value
    if start is not None:
        result.append([start, None])
    return result


def stationary() -> dict:
    with gzip.open(STATIONARY, 'rt') as stream:
        recording = json.load(stream)
    registry_path = ROOT / 'data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json'
    registry = json.loads(registry_path.read_text())
    names = {r['bit_start']: r['name'] for r in registry['catalogs']['498']['data_list']['rows']
             if r['did'] == '0x1906' and r['bit_start'] == r['bit_end']}
    streams = defaultdict(list)
    for frame in recording['frames']:
        if frame['bus'] == 1:
            streams[frame['addr']].append((round(frame['t'] * 1e9), bytes.fromhex(frame['data'])))
    observations = []
    for name, bit, did_bit in (('res_plus', 7, 7), ('set_minus', 6, 6), ('cancel', 5, 5)):
        pressed = [(t, d) for t, d in streams[0xFE] if switch(d, name)]
        pulses = edges(streams[0x1B2], bit)
        oracle = [(round(r['t'] * 1e9), r['1906']) for r in recording['oracles']
                  if len(bytes.fromhex(r.get('1906', ''))) >= 4 and bytes.fromhex(r['1906'])[3] & (1 << did_bit)]
        if not pressed or not pulses or not oracle:
            raise ValueError(f'missing independent stationary evidence for {name}')
        observations.append({
            'physical_button': name, 'mirror_byte': 0, 'mirror_bit': bit,
            'switch_first_ns': pressed[0][0], 'switch_last_ns': pressed[-1][0],
            'mirror_intervals_ns': pulses, 'gts_first_ns': oracle[0][0], 'gts_payload': oracle[0][1],
            'gts_oracle': {'did': '0x1906', 'byte': 3, 'bit': did_bit,
                           'name': names[31 - did_bit]},
        })
    return {
        'source': {'path': str(STATIONARY.relative_to(ROOT)), 'sha256': sha(STATIONARY)},
        'gts_oracle_metadata': {'registry': str(registry_path.relative_to(ROOT)),
                                'ddb_source': registry['source_identity']['gtsplus/NA/DB/Gen/FRC_P5.ddb']},
        'secondary_cancel_mirror': {'address': '0x5F6', 'byte': 4, 'bit': 7,
                                    'intervals_ns': edges([(t, d[4:5]) for t, d in streams[0x5F6]], 7)},
        'mirror_frames': len(streams[0x1B2]),
        'cruise_frames': len(streams[0x8A]),
        'cruise_enabled_frames': sum(bool(d[3] & 8) for _, d in streams[0x8A]),
        'mirror_tail_zero_frames': sum(d[3:] == bytes(29) for _, d in streams[0x1B2]),
        'bindings': observations,
        'boundary': 'These isolated inputs identify a switch-event mirror, not a writable cruise-controller input. All retained cruise-state frames are inactive.',
    }


def screen(streams, *, pre_end=-150_000_000, post_start=-100_000_000, post_end=200_000_000) -> dict:
    shared = set.intersection(*(set(window) for window in streams))
    qualified, candidates = [], []
    for key in sorted(shared):
        bus, address, length = key
        if length == 0:
            continue
        count = np.zeros((length * 8, 2), dtype=int)
        for window in streams:
            before = [list(d) for t, d in window[key] if -1_000_000_000 <= t < pre_end]
            after = [list(d) for t, d in window[key] if post_start <= t <= post_end]
            if not before or not after:
                break
            old = np.unpackbits(np.array(before, dtype=np.uint8), axis=1)
            new = np.unpackbits(np.array(after, dtype=np.uint8), axis=1)
            count[:, 0] += (old.min(0) == 1) & (new.min(0) == 0)
            count[:, 1] += (old.max(0) == 0) & (new.max(0) == 1)
        else:
            qualified.append(key)
            for bit, polarity in np.argwhere(count == len(streams)):
                candidates.append({'bus': bus, 'address': f'0x{address:03X}', 'length': length,
                                   'byte': int(bit) // 8, 'bit': 7 - int(bit) % 8, 'asserted': int(polarity)})
    return {'pre_ns': [-1_000_000_000, pre_end], 'post_ns': [post_start, post_end],
            'fully_sampled_stream_count_by_bus': dict(sorted(Counter(str(k[0]) for k in qualified).items())),
            'candidates': candidates,
            'scope': 'all payload bits, including B0..B2; raw observations without a SecOC-authentication claim; stable pre-state and at least one opposite post-state in every event'}


def all_buses() -> dict:
    header, rows = load_rows(BUSES)
    windows = [defaultdict(list) for _ in header['windows']]
    for index, _source, time, frames in rows:
        info = header['windows'][index]
        center = info.get('center_ns', info.get('start_ns'))
        for bus, address, hx in frames:
            data = bytes.fromhex(hx)
            windows[index][bus, address, len(data)].append((time - center, data))
    discovery = [w for w, info in zip(windows, header['windows'], strict=True) if info['kind'] == 'switch_cancel']
    shared = set.intersection(*(set(w) for w in discovery))
    p05 = Counter()
    events = []
    for index, window in enumerate(discovery):
        mirror = window[2, 0x1B2, 32]
        native_cruise = window[2, 0x8A, 32]
        post_cruise = [(t, d) for t, d in native_cruise if t >= 0 and not d[3] & 8]
        pulses = edges(mirror, 5)
        mode_before = [d[0] for t, d in window[2, 0x251, 8] if t < 0]
        counterexamples = []
        for address, byte, bit in ((0x198, 4, 3), (0x19C, 0, 1)):
            high = [(t, d) for t, d in window[2, address, 8] if -1_000_000_000 <= t < -150_000_000 and d[byte] & (1 << bit)]
            low = [(t, d) for t, d in window[2, address, 8] if -1_000_000_000 <= t < -150_000_000 and not d[byte] & (1 << bit)]
            engaged = [d for t, d in native_cruise if -1_000_000_000 <= t < -150_000_000]
            if high and not low and engaged and all(d[3] & 8 for d in engaged):
                counterexamples.append({'address': f'0x{address:03X}', 'byte': byte, 'bit': bit,
                                        'asserted_before_cancel': len(high), 'concurrent_engaged_cruise_frames': len(engaged),
                                        'first_ns': high[0][0], 'last_ns': high[-1][0], 'first_payload': high[0][1].hex()})
        events.append({'index': index, 'sources': header['windows'][index]['sources'],
                       'mode_before': sorted(set(mode_before)), 'native_drop_ns': post_cruise[0][0] if post_cruise else None,
                       'mirror_cancel_intervals_ns': pulses, 'non_cancel_counterexamples': counterexamples})
        for (bus, address, length), samples in window.items():
            if bus == 1 and length >= 12:
                for _, d in samples:
                    correct = int.from_bytes(d[:2], 'little') == binascii.crc_hqx(d[2:] + address.to_bytes(2, 'little'), 0xFFFF)
                    p05['valid' if correct else 'invalid'] += 1
    placements = []
    for info, window in zip(header['windows'], windows, strict=True):
        if info['kind'] == 'stock_placement':
            placements.append({'sources': info['sources'], 'streams': [
                {'bus': bus, 'address': f'0x{address:03X}', 'length': length, 'count': len(samples), 'first_payload': samples[0][1].hex()}
                for (bus, address, length), samples in sorted(window.items())]})
    return {
        'fixture': {'path': str(BUSES.relative_to(ROOT)), 'sha256': sha(BUSES)},
        'common_stream_count_by_bus': dict(sorted(Counter(str(k[0]) for k in shared).items())),
        'events': events, 'adas_p05': dict(p05), 'stock_placement': placements,
        'early_screen': screen(discovery), 'long_screen': screen(discovery, post_end=1_000_000_000),
        'boundary': 'A cancellation-linked output is not automatically a cancel input. Native2 identifies the FRC-side link, not exclusive logical ECU ownership behind it.',
    }


def assess_host_attempt(rows, first_send_ns: int) -> dict:
    streams = defaultdict(list)
    sends, returned, rejected = [], [], []
    alerts = Counter()
    for _source, time, kind, data in rows:
        if kind == 'selfdriveState':
            alerts[data[1]] += 1
        if kind not in ('can', 'sendcan'):
            continue
        for bus, address, hx in data:
            payload = bytes.fromhex(hx)
            if kind == 'sendcan' and address == 0x101:
                sends.append((time, bus, payload))
            if kind == 'can':
                streams[bus, address].append((time, payload))
                if address == 0x101 and len(payload) == 8 and bus == 130 and payload[0] & 8:
                    returned.append((time, payload))
                if address == 0x101 and len(payload) == 8 and bus == 194 and payload[0] & 8:
                    rejected.append((time, payload))
    cruise = streams[2, 0x8A]
    before = [(t, d) for t, d in cruise if t < first_send_ns]
    after = [(t, d) for t, d in cruise if t >= first_send_ns and not d[3] & 8]
    dropped = after[0][0] if after else None
    end = dropped if dropped is not None else first_send_ns + 500_000_000
    # Retain the raw publication batch containing any competing physical input.
    # Later driver actions must not retroactively confound an earlier release.
    inputs = []
    for name, address, predicate in (('brake', 0x101, lambda d: bool(d[0] & 8)), ('cancel', 0xFE, switch)):
        selected = [(t, d) for t, d in streams[0, address]
                    if first_send_ns - 250_000_000 <= t <= end and predicate(d)]
        if selected:
            t, d = selected[0]
            inputs.append({'input': name, 'first_relative_ns': t - first_send_ns, 'payload': d.hex()})
    fresh_inputs = all(any(first_send_ns - 150_000_000 <= t <= first_send_ns for t, _ in streams[0, a]) for a in (0x101, 0xFE))
    native_engaged = bool(before and before[-1][1][3] & 8 and first_send_ns - before[-1][0] < 100_000_000)
    tx_valid = all(len(d) == 8 and d[7] == (0x01 + 0x01 + 8 + sum(d[:7])) % 256 for _, _, d in sends)
    # A native forwarded brake return is not necessarily a return of our send.
    # Even a matching return remains transport evidence, never an ECU ACK.
    matched_returns = sum(any(bus == 2 and sent == payload and 0 <= time - sent_ns <= 100_000_000
                              for sent_ns, bus, sent in sends) for time, payload in returned)
    return {
        'host_frames': len(sends), 'host_buses': sorted({b for _, b, _ in sends}), 'host_checksum_valid': tx_valid,
        'native_cruise_engaged_before': native_engaged, 'physical_inputs_fresh': fresh_inputs,
        'native_drop_relative_ns': dropped - first_send_ns if dropped is not None else None,
        'competing_driver_inputs': inputs, 'brake_asserted_tx_echoes': len(returned), 'brake_asserted_rejections': len(rejected),
        'payload_matching_host_returns': matched_returns,
        'selfdrive_alerts': dict(sorted(alerts.items())),
        'unconfounded_observation': native_engaged and fresh_inputs and bool(sends) and tx_valid and matched_returns > 0 and dropped is not None and not inputs,
        # Even an unconfounded temporal association would need full review of
        # other causes. It is a candidate witness, not an automatic causal proof.
    }


def hosts() -> dict:
    header, rows = load_rows(HOSTS)
    grouped = [[] for _ in header['episodes']]
    for index, *row in rows:
        grouped[index].append(row)
    results = []
    for info, data in zip(header['episodes'], grouped, strict=True):
        result = assess_host_attempt(data, info['first_send_ns'])
        sources = sorted({r[0] for r in data})
        results.append({'route': header['routes'][info['route']]['route'], 'first_send_ns': info['first_send_ns'],
                        'sources': [header['sources'][s] for s in sources], **result})
    return {'fixture': {'path': str(HOSTS.relative_to(ROOT)), 'sha256': sha(HOSTS)},
            'routes': len(header['routes']), 'original_segments': len(header['sources']),
            'host_frames_from_full_route_census': sum(r['count'] for route in header['routes'] for r in route['host_0x101']),
            'episodes': results, 'unconfounded_observations': sum(e['unconfounded_observation'] for e in results),
            'boundary': 'Only actual sendcan frames count as host attempts. Physical input before native release confounds attribution; a TX echo alone proves neither ECU parsing nor cancellation.'}


def build() -> dict:
    return {'schema': 'camry-2026-cancel-ownership-v1', 'stationary_mirror': stationary(), 'all_buses': all_buses(), 'host_attempts': hosts(),
            'conclusion': {'sender_recovered': False, 'runtime_changed': False, 'vehicle_commands_sent': False,
                           'new_wire_fact': '0x1B2 B0 bits7/6/5 mirror RES-plus/SET-minus/CANCEL events independently of cruise operation.',
                           'missing_fact': 'Which ordinary received command the cruise controller accepts to cancel, and on which receiver path.',
                           'topology_correction': 'Unsplit placement prevents replacing a source stream but does not by itself rule out a cancel-only event command. That generic possibility is not target-specific acceptance evidence.'}}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=OUTPUT)
    args = ap.parse_args()
    report = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(args.out)


if __name__ == '__main__':
    main()
