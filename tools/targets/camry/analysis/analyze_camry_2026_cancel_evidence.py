#!/usr/bin/env python3
"""Audit retained genuine cancel transitions without inventing a sender command.

The fixture preserves two-second source windows around 21 physical CANCEL
presses followed by cruise disengagement. Diagnostic monitor bit positions
are intentionally not interpreted as CAN-field positions or write commands.
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
FIXTURE = ROOT / 'tests/fixtures/camry_2026_cancel_windows.jsonl.gz'
OUTPUT = ROOT / 'data/generated/camry_2026_cancel_evidence.json'


def is_cancel(data: bytes) -> bool:
    return bool(data[4] & 0x40) and not bool(data[7] & 0x20)


def multibit_screen(windows, metadata):
    """Look for any short-field value newly appearing after every real cancel.

    This catches a single-frame pulse as well as a maintained request. It does
    not assume that a CANCEL button press must be copied literally by the FRC.
    A negative result cannot exclude an unexercised automatic-cancel command.
    """
    shared = set.intersection(*(set(window) for window in windows))
    tested = 0
    results = []
    for bus, address, size in sorted(shared):
        if bus != 1:
            continue
        before_sets, after_sets = [], []
        for info, streams in zip(metadata, windows, strict=True):
            center = info['center_nanos']
            rows = streams[(bus, address, size)]
            before = [data for time, data in rows if center - 300_000_000 <= time < center - 25_000_000]
            after = [data for time, data in rows if center <= time <= center + 250_000_000]
            if not before or not after:
                break
            before_sets.append(before)
            after_sets.append(after)
        if len(before_sets) != len(windows):
            continue
        best, reproduced = None, []
        for endian in ('little', 'big'):
            for byte in range(3, size):
                old_words = [[int.from_bytes(data[byte:byte + 2].ljust(2, b'\x00'), endian) for data in rows] for rows in before_sets]
                new_words = [[int.from_bytes(data[byte:byte + 2].ljust(2, b'\x00'), endian) for data in rows] for rows in after_sets]
                for width in (2, 3, 4, 8, 12):
                    for bit in range(8):
                        if byte == size - 1 and bit + width > 8:
                            continue
                        shift = bit if endian == 'little' else 16 - bit - width
                        if shift < 0:
                            continue
                        mask, counts = (1 << width) - 1, Counter()
                        for old, new in zip(old_words, new_words, strict=True):
                            old_values = {(word >> shift) & mask for word in old}
                            new_values = {(word >> shift) & mask for word in new}
                            counts.update(new_values - old_values)
                        tested += 1
                        if not counts:
                            continue
                        value, count = min(counts.items(), key=lambda item: (-item[1], item[0]))
                        row = {'address': f'0x{address:03X}', 'byte': byte, 'first_bit': bit,
                               'width': width, 'endian': endian, 'value': value,
                               'events_with_new_value': count, 'events_observed': len(windows)}
                        if best is None or count > best['events_with_new_value']:
                            best = row
                        if count == len(windows):
                            reproduced.append(row)
        results.append({'address': f'0x{address:03X}', 'length': size,
                        'highest_coverage': best, 'reproduced_in_every_event': reproduced})
    return {'field_specs_tested': tested, 'widths': [2, 3, 4, 8, 12],
            'endianness': ['little', 'big'], 'before': '-300..-25 ms', 'after': '0..250 ms',
            'criterion': 'a common value absent from every pre-window and present at least once in every post-window',
            'per_stream': results}


def enum_screen(windows: list, sources: list) -> dict:
    """Test a new literal value, allowing different pre-cancel enum states.

    Unlike the single-bit screen, this does not require the previous state to
    be constant or identical across events. A common post-only value remains
    necessary evidence, not proof of a command rather than a result-state echo.
    """
    specifications = 0
    candidates = []
    complete_streams = []
    for bus, address, size in sorted(windows[0]):
        if bus != 1:
            continue
        arrays = []
        for stream, source in zip(windows, sources, strict=True):
            center = source['center_nanos']
            rows = [(t, d) for t, d in stream.get((bus, address, size), [])
                    if int.from_bytes(d[:2], 'little') == binascii.crc_hqx(d[2:] + address.to_bytes(2, 'little'), 0xffff)]
            before = np.array([list(d) for t, d in rows if center - 1_000_000_000 <= t < center - 25_000_000], dtype=np.uint32)
            after = np.array([list(d) for t, d in rows if center <= t <= center + 1_000_000_000], dtype=np.uint32)
            if not len(before) or not len(after):
                break
            arrays.append((np.pad(before, ((0, 0), (0, 2))), np.pad(after, ((0, 0), (0, 2)))))
        if len(arrays) != len(windows):
            continue
        complete_streams.append({'address': f'0x{address:03X}', 'length': size})
        for byte in range(3, size):
            for endian in ('big', 'little'):
                weights = (65536, 256, 1) if endian == 'big' else (1, 256, 65536)
                words = [tuple(d[:, byte] * weights[0] + d[:, byte + 1] * weights[1] + d[:, byte + 2] * weights[2]
                               for d in pair) for pair in arrays]
                for bit in range(8):
                    for width in range(1, min(16, (size - byte) * 8 - bit) + 1):
                        specifications += 1
                        shift = 24 - bit - width if endian == 'big' else bit
                        mask = (1 << width) - 1
                        allowed = None
                        for pre, post in words:
                            values = set(((post >> shift) & mask).tolist()) - set(((pre >> shift) & mask).tolist())
                            allowed = values if allowed is None else allowed & values
                            if not allowed:
                                break
                        if allowed:
                            candidates.append({'address': f'0x{address:03X}', 'length': size, 'byte': byte,
                                               'bit_offset': bit, 'endian': endian, 'width': width, 'values': sorted(allowed)})
    return {'field_specs': specifications, 'complete_streams': complete_streams, 'candidates': candidates,
            'scope': 'every contiguous 1..16-bit field after B2, big/MSB-first and little/LSB-first; intersection of post-minus-pre value sets over all 21 events',
            'boundary': 'does not exclude a command unexercised by physical CANCEL, noncontiguous encodings, context-dependent values, or an unobserved input path'}


def build() -> dict:
    with gzip.open(FIXTURE, 'rt') as f:
        header = json.loads(next(f))
        windows = [defaultdict(list) for _ in header['windows']]
        for line in f:
            window, _segment, nanos, frames = json.loads(line)
            for bus, address, hx in frames:
                data = bytes.fromhex(hx)
                windows[window][(bus, address, len(data))].append((nanos, data))
    summaries = []
    coverage = Counter()
    eligible = Counter()
    integrity = Counter()
    for source, streams in zip(header['windows'], windows, strict=True):
        center = source['center_nanos']
        switch = streams[(0, 0xfe, 32)]
        cruise = streams[(2, 0x8a, 32)]
        before_switch = [row for row in switch if row[0] < center]
        pressed = next(row for row in switch if row[0] >= center)
        before_cruise = [row for row in cruise if row[0] < center]
        released = next(row for row in cruise if row[0] >= center and not row[1][3] & 8)
        if not before_switch or is_cancel(before_switch[-1][1]) or not is_cancel(pressed[1]):
            raise ValueError('fixture does not contain the claimed physical cancel edge')
        if not before_cruise or not before_cruise[-1][1][3] & 8:
            raise ValueError('cruise was not enabled before the cancel edge')
        brake_rows = [data for t, data in streams[(0, 0x101, 8)] if center - 200_000_000 <= t <= released[0]]
        summary = {
            **source, 'cruise_drop_delay_ms': round((released[0] - center) * 1e-6, 6),
            'concurrent_brake': any(data[0] & 8 for data in brake_rows),
            'switch_before': before_switch[-1][1].hex(), 'switch_pressed': pressed[1].hex(),
            'cruise_before': before_cruise[-1][1].hex(), 'cruise_released': released[1].hex(),
            'adas_streams': [],
        }
        for (bus, address, size), rows in sorted(streams.items()):
            if bus != 1:
                continue
            valid_rows = []
            for t, data in rows:
                ok = int.from_bytes(data[:2], 'little') == binascii.crc_hqx(data[2:] + address.to_bytes(2, 'little'), 0xffff)
                integrity['valid' if ok else 'invalid'] += 1
                if ok:
                    valid_rows.append((t, data))
            before = [d for t, d in valid_rows if center - 1_000_000_000 <= t < center - 25_000_000]
            after = [d for t, d in valid_rows if center <= t <= center + 1_000_000_000]
            if not before or not after:
                continue
            summary['adas_streams'].append({'address': f'0x{address:03X}', 'length': size,
                                             'pre_samples': len(before), 'post_samples': len(after)})
            # Test both polarities. A literal cancel edge must leave its prior
            # stable state in every event; this is necessary, not sufficient,
            # evidence for a command (a result-state echo can do the same).
            for byte in range(3, size):
                for bit in range(8):
                    old = {bool(d[byte] & (1 << bit)) for d in before}
                    new = {bool(d[byte] & (1 << bit)) for d in after}
                    for assertion in (False, True):
                        key = (address, size, byte, bit, assertion)
                        eligible[key] += 1
                        coverage[key] += int(old == {not assertion} and assertion in new)
        summaries.append(summary)
    count = len(summaries)
    complete = [key for key, n in eligible.items() if n == count]
    ranked = sorted(complete, key=lambda k: (-coverage[k], k))
    def field(key):
        address, size, byte, bit, assertion = key
        return {'address': f'0x{address:03X}', 'length': size, 'byte': byte, 'bit': bit,
                'assertion_value': int(assertion), 'events_with_edge': coverage[key], 'events_observed': eligible[key]}
    registry = json.loads((ROOT / 'data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json').read_text())
    tests = registry['catalogs']['498']['active_tests']
    return {
        'schema': 'camry-2026-cancel-evidence-v2',
        'fixture': {'path': str(FIXTURE.relative_to(ROOT)), 'sha256': hashlib.sha256(FIXTURE.read_bytes()).hexdigest()},
        'source_layout': header['source_layout'],
        'windows': summaries,
        'integrity': dict(integrity),
        'literal_edge_screen': {
            'before': '-1000..-25 ms relative to physical CANCEL assertion',
            'after': '0..1000 ms; includes possible state echoes after cruise disengages',
            'fields': 'each bit after CRC/counter prefix B0..B2, both polarities, every retained ADAS stream',
            'eligible_bit_polarities': len(complete),
            'reproduced_in_every_event': [field(k) for k in ranked if coverage[k] == count],
            'highest_coverage': [field(k) for k in ranked[:12]],
        },
        'multibit_pulse_screen': multibit_screen(windows, header['windows']),
        'enumerated_value_screen': enum_screen(windows, header['windows']),
        'gts_surface': {
            'database': 'FRC_P5', 'active_test_count': len(tests),
            'named_cancel_active_tests': [r['name'] for r in tests if 'cancel' in r['name'].lower()],
            'named_test_disposition': 'PDA Cancel Notification Display is a display active test, not an adaptive-cruise cancellation command',
            'monitor_oracle': 'DID 0x1B01 groups ISA main-switch recognition with output set-cancel/cancel/resume switch monitors. These read-only observations are not a DRCC CAN field map or an actuator API',
            'boundary': 'absence of a named GTS active test is not proof that ECU firmware has no cancellation command',
        },
        'conclusion': {
            'physical_cancel_observed': True,
            'supported_automatic_cancel_sender_recovered': False,
            'interpretation': 'Physical CANCEL and downstream disengagement are observed. No direct literal bit transition or new contiguous 1..16-bit enum value reproduces in every retained ADAS-side event under the declared screens. No command is inferred from correlations, read-only DIDs, or legacy Toyota CAN layouts.',
            'not_excluded': 'multibit or multiplexed encodings, sparse traffic outside these windows, a cancellation command not exercised by physical-switch cancellation, or an unacquired receiver implementation',
            'runtime_change': 'none; stock-harness 0x101/0xFE remain on the unsplit chassis network, so the prior wrong-relay brake spoof is not restored',
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=OUTPUT)
    args = parser.parse_args()
    report = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(args.out)


if __name__ == '__main__':
    main()
