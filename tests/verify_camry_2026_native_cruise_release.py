#!/usr/bin/env python3
"""Verify native-release selection and prevent absent telemetry becoming proof."""
from __future__ import annotations

import binascii
import gzip
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis import (
    analyze_camry_2026_native_cruise_release as evidence,
)

CENTER = 1_000_000_000


def brake(pressed: bool = False, raw_b1: int = 0) -> bytes:
    data = bytearray([0x80 | (8 if pressed else 0), raw_b1, 0, 1, 0, 0, 0, 0])
    data[7] = (sum(data[:7]) + 10) & 255
    return bytes(data)


def switch(cancel: bool = False, main: bool = False) -> bytes:
    data = bytearray(32)
    data[4] = 0x40 if cancel else 0
    data[7] = (0 if cancel else 0x20) | (4 if main else 0)
    return bytes(data)


def context() -> list[list]:
    rows = []
    for t in range(CENTER - evidence.CONTEXT_NS, CENTER + 1, 50_000_000):
        rows.extend([[0, t, 'can', [[0, 0xFE, switch().hex()], [0, 0x101, brake().hex()]]],
                     [0, t, 'carControl', False]])
    return rows


class TestNativeReleaseSelection(unittest.TestCase):
    def test_fresh_deasserted_inputs_are_only_a_no_observed_input_class(self):
        result = evidence.classify(CENTER, context())
        self.assertEqual(result['disposition'], 'no_decoded_driver_input_observed')
        self.assertEqual(result['observed_input_kinds'], [])
        self.assertFalse(result['host_cancel_asserted_in_pre_window'])

    def test_each_recovered_driver_input_is_detected(self):
        for name, address, raw in [('cancel', 0xFE, switch(cancel=True)),
                                   ('main', 0xFE, switch(main=True)), ('brake', 0x101, brake(True))]:
            with self.subTest(name=name):
                rows = context() + [[0, CENTER, 'can', [[0, address, raw.hex()]]]]
                result = evidence.classify(CENTER, rows)
                self.assertEqual(result['disposition'], 'decoded_driver_input_observed')
                self.assertEqual(result['observed_input_kinds'], [name])

    def test_missing_stream_is_unknown_not_deasserted(self):
        for missing in (0xFE, 0x101):
            rows = context()
            for row in rows:
                if row[2] == 'can':
                    row[3] = [f for f in row[3] if f[1] != missing]
            self.assertEqual(evidence.classify(CENTER, rows)['disposition'], 'incomplete_input_coverage')

    def test_stale_stream_is_unknown(self):
        rows = [r for r in context() if r[1] < CENTER - 300_000_000 or r[2] == 'carControl']
        self.assertEqual(evidence.classify(CENTER, rows)['disposition'], 'incomplete_input_coverage')

    def test_corrupt_brake_and_contradictory_switch_are_unknown(self):
        for address, raw in [(0x101, brake()[:-1] + b'\x00'), (0xFE, bytes(32))]:
            rows = context() + [[0, CENTER, 'can', [[0, address, raw.hex()]]]]
            result = evidence.classify(CENTER, rows)
            self.assertEqual(result['disposition'], 'incomplete_input_coverage')
            self.assertEqual(sum(result['malformed_inputs'].values()), 1)

    def test_tx_echoes_wrong_bus_and_host_sends_do_not_supply_input_coverage(self):
        for bus, kind in ((128, 'can'), (2, 'can'), (0, 'sendcan')):
            rows = context()
            for row in rows:
                if row[2] == 'can':
                    row[2] = kind
                    for frame in row[3]:
                        frame[0] = bus
            self.assertEqual(evidence.classify(CENTER, rows)['disposition'], 'incomplete_input_coverage')

    def test_unnamed_brake_byte_is_not_a_new_brake_pressed_policy(self):
        rows = context()
        for row in rows:
            if row[2] == 'can':
                row[3][1][2] = brake(raw_b1=7).hex()
        self.assertEqual(evidence.classify(CENTER, rows)['observed_input_kinds'], [])

    def test_only_pre_window_host_requests_count(self):
        rows = context() + [[0, CENTER - 2_000_000_000, 'carControl', True],
                            [0, CENTER + 10_000_000, 'carControl', True]]
        self.assertFalse(evidence.classify(CENTER, rows)['host_cancel_asserted_in_pre_window'])
        rows.append([0, CENTER - 10_000_000, 'carControl', True])
        self.assertTrue(evidence.classify(CENTER, rows)['host_cancel_asserted_in_pre_window'])

    def test_missing_host_control_stays_unknown(self):
        rows = [r for r in context() if r[2] != 'carControl']
        self.assertIsNone(evidence.classify(CENTER, rows)['host_cancel_asserted_in_pre_window'])


class TestRetainedNativeReleases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = evidence.build()
        with gzip.open(evidence.FIXTURE, 'rt') as stream:
            cls.header = json.loads(next(stream))
            cls.rows = [json.loads(line) for line in stream]

    def test_report_regenerates_from_retained_bytes(self):
        self.assertEqual(self.report, json.loads(evidence.OUTPUT.read_text()))

    def test_every_release_contains_a_continuous_native_active_to_inactive_edge(self):
        releases = [row[1] for row in self.rows if row[0] == 'release']
        self.assertEqual(len(releases), 77)
        self.assertEqual(sum(self.report['dispositions'].values()), len(releases))
        for release in releases:
            before = release['before']
            self.assertTrue(bytes.fromhex(before['payload'])[3] & 8)
            self.assertFalse(bytes.fromhex(release['after'])[3] & 8)
            self.assertTrue(0 < release['nanos'] - before['nanos'] <= evidence.MAX_OBSERVATION_GAP_NS)
            # The release PDU itself must occur on native bus2 in the raw context.
            self.assertTrue(any(t == release['nanos'] and kind == 'can' and
                                [2, 0x08A, release['after']] in data for _, t, kind, data in release['context']))

    def test_selected_windows_are_not_host_cancel_acceptance_examples(self):
        self.assertEqual(len(self.report['selected_windows']), 3)
        for row in self.report['selected_windows']:
            self.assertFalse(row['classification']['host_cancel_asserted_in_pre_window'])
            self.assertEqual(row['host_request_offsets_ms'], [])
            self.assertEqual(row['host_cancel_shaped_sends'], [])
            self.assertEqual(row['mirror_cancel_offsets_ms'], [])
            self.assertEqual(row['brake_assertion_offsets_ms'], [])

    def test_actual_mode_bytes_distinguish_conventional_from_adaptive(self):
        rows = {r['route']: r for r in self.report['selected_windows']}
        conventional = rows['0000008d--a9f348691a']
        self.assertEqual(conventional['mode_from_native_0x251_b0'], 'conventional')
        self.assertEqual((conventional['last_pre_mode'], conventional['first_post_mode']), (0x90, 0x88))
        self.assertLess(abs(conventional['state_sample']['offset_ms']), 10)
        self.assertAlmostEqual(conventional['state_sample']['v_ego'], 8.08436, places=4)
        self.assertEqual(rows['0000003b--62262eb7a1']['mode_from_native_0x251_b0'], 'adaptive')
        self.assertEqual(rows['00000045--805b7ca6ab']['mode_from_native_0x251_b0'], 'adaptive')

    def test_brake_byte_context_is_preserved_without_a_pedal_claim(self):
        rows = {r['route']: r for r in self.report['selected_windows']}
        self.assertEqual(rows['00000045--805b7ca6ab']['brake_b1_baseline_values'], [0])
        self.assertEqual(rows['00000045--805b7ca6ab']['brake_b1_pre_values'], [3, 4, 5, 6, 7])
        self.assertEqual(rows['0000003b--62262eb7a1']['brake_b1_baseline_values'], [0, 1])
        self.assertEqual(rows['0000003b--62262eb7a1']['brake_b1_pre_values'], [0, 1, 2, 3])

    def test_observed_adas_request_packets_have_valid_profile5_crc(self):
        count = 0
        for row in self.rows:
            if row[0] != 'window' or row[4] != 'can':
                continue
            for bus, address, text in row[5]:
                if (bus, address) != (1, 0x160):
                    continue
                data = bytes.fromhex(text)
                self.assertEqual(len(data), 32)
                self.assertEqual(int.from_bytes(data[:2], 'little'),
                                 binascii.crc_hqx(data[2:] + address.to_bytes(2, 'little'), 0xFFFF))
                count += 1
        self.assertGreater(count, 600)


if __name__ == '__main__':
    unittest.main()
