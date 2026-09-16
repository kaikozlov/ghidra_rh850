#!/usr/bin/env python3
"""Test passive mirror binding, source separation and causal-confound handling."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis import analyze_camry_2026_cancel_ownership as evidence
from tools.targets.camry.extract import (
    extract_camry_2026_cancel_ownership as extraction,
)


class TestRetainedOwnership(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = evidence.build()

    def test_report_regenerates(self):
        self.assertEqual(self.report, json.loads(evidence.OUTPUT.read_text()))

    def test_isolated_stationary_buttons_have_distinct_mirrors(self):
        s = self.report['stationary_mirror']
        self.assertEqual(s['cruise_frames'], 1475)
        self.assertEqual(s['cruise_enabled_frames'], 0)
        self.assertEqual(s['mirror_frames'], s['mirror_tail_zero_frames'])
        self.assertEqual([r['mirror_bit'] for r in s['bindings']], [7, 6, 5])
        for r in s['bindings']:
            self.assertEqual(len(r['mirror_intervals_ns']), 1)
            start, end = r['mirror_intervals_ns'][0]
            self.assertLess(r['switch_first_ns'], r['gts_first_ns'])
            self.assertLess(r['gts_first_ns'], start)
            self.assertGreater(end, r['switch_last_ns'])
            self.assertTrue(bytes.fromhex(r['gts_payload'])[r['gts_oracle']['byte']] & (1 << r['gts_oracle']['bit']))

    def test_all_three_buses_and_header_bits_are_screened(self):
        b = self.report['all_buses']
        self.assertEqual(b['common_stream_count_by_bus'], {'0': 92, '1': 22, '2': 54})
        self.assertEqual(b['adas_p05'], {'valid': 16526})
        candidate = {'bus': 2, 'address': '0x1B2', 'length': 32, 'byte': 0, 'bit': 5, 'asserted': 1}
        self.assertIn(candidate, b['long_screen']['candidates'])
        self.assertFalse(any(c['bus'] == 1 for c in b['long_screen']['candidates']))
        self.assertEqual(len(b['events']), 21)
        for r in b['events']:
            self.assertEqual(r['mode_before'], [0xC0])
            self.assertEqual(len(r['mirror_cancel_intervals_ns']), 1)
            self.assertIsNotNone(r['native_drop_ns'])

    def test_preasserted_signals_cannot_be_promoted_to_cancel_inputs(self):
        b = self.report['all_buses']
        counterexamples = [e for e in b['events'] if e['non_cancel_counterexamples']]
        self.assertEqual([e['index'] for e in counterexamples], [11])
        for r in counterexamples[0]['non_cancel_counterexamples']:
            self.assertIn(r['address'], ('0x198', '0x19C'))
            self.assertEqual(r['concurrent_engaged_cruise_frames'], 34)
            self.assertGreater(r['last_ns'] - r['first_ns'], 800_000_000)

    def test_final_harness_mirrors_are_on_unsplit_bus_one(self):
        for source in self.report['all_buses']['stock_placement']:
            self.assertEqual({r['bus'] for r in source['streams']}, {1})
            self.assertTrue({'0x101', '0x0FE', '0x1B2', '0x5F6'}.issubset({r['address'] for r in source['streams']}))

    def test_full_route_host_census_has_no_independent_cancel_witness(self):
        h = self.report['host_attempts']
        self.assertEqual((h['routes'], h['original_segments']), (10, 463))
        self.assertEqual(h['host_frames_from_full_route_census'], 375)
        self.assertEqual(sum(e['host_frames'] for e in h['episodes']), 375)
        self.assertEqual(len(h['episodes']), 58)
        self.assertEqual(h['unconfounded_observations'], 0)
        for e in h['episodes']:
            self.assertTrue(e['host_checksum_valid'])
            self.assertTrue(e['physical_inputs_fresh'])
            self.assertTrue(e['native_cruise_engaged_before'])
            self.assertIsNotNone(e['native_drop_relative_ns'])
            self.assertEqual(e['host_buses'], [2])
            self.assertTrue(any(p['first_relative_ns'] <= 0 for p in e['competing_driver_inputs']))


class TestWitnessClassifier(unittest.TestCase):
    T = 1_000_000_000

    @staticmethod
    def brake(on):
        b = bytearray.fromhex('800000010000008b')
        b[0] |= 8 if on else 0
        b[7] = (0x01 + 0x01 + 8 + sum(b[:7])) & 255
        return b.hex()

    @staticmethod
    def button(on):
        b = bytearray(32)
        b[4] = 0x40 if on else 0
        b[7] = 0 if on else 0x20
        return b.hex()

    @staticmethod
    def cruise(on):
        b = bytearray(32)
        b[3] = 8 if on else 0
        return b.hex()

    def rows(self):
        return [[0, self.T - 30_000_000, 'can', [[0, 0x101, self.brake(False)], [0, 0xFE, self.button(False)], [2, 0x8A, self.cruise(True)]]],
                [0, self.T, 'sendcan', [[2, 0x101, self.brake(True)]]],
                [0, self.T + 2_000_000, 'can', [[130, 0x101, self.brake(True)]]],
                [0, self.T + 70_000_000, 'can', [[2, 0x8A, self.cruise(False)]]]]

    def test_positive_control_detects_a_candidate_not_provided_by_this_corpus(self):
        r = evidence.assess_host_attempt(self.rows(), self.T)
        self.assertTrue(r['unconfounded_observation'])
        self.assertTrue(r['host_checksum_valid'])

    def test_physical_cancel_or_brake_before_release_is_a_confound(self):
        for address, data in ((0x101, self.brake(True)), (0xFE, self.button(True))):
            for offset in (-10_000_000, 10_000_000):
                with self.subTest(address=address, offset=offset):
                    rows = self.rows() + [[0, self.T + offset, 'can', [[0, address, data]]]]
                    rows.sort(key=lambda row: row[1])
                    r = evidence.assess_host_attempt(rows, self.T)
                    self.assertFalse(r['unconfounded_observation'])
                    self.assertEqual(r['competing_driver_inputs'][0]['first_relative_ns'], offset)

    def test_later_physical_input_cannot_confound_earlier_release(self):
        rows = self.rows() + [[0, self.T + 150_000_000, 'can', [[0, 0xFE, self.button(True)]]]]
        self.assertTrue(evidence.assess_host_attempt(rows, self.T)['unconfounded_observation'])

    def test_forwarding_echo_is_not_a_host_attempt(self):
        rows = [r for r in self.rows() if r[2] != 'sendcan']
        self.assertFalse(evidence.assess_host_attempt(rows, self.T)['unconfounded_observation'])

    def test_corrupt_host_payload_cannot_supply_a_positive_candidate(self):
        rows = self.rows()
        rows[1][3][0][2] = rows[1][3][0][2][:-2] + '00'
        rows[2][3][0][2] = rows[1][3][0][2]
        r = evidence.assess_host_attempt(rows, self.T)
        self.assertFalse(r['host_checksum_valid'])
        self.assertFalse(r['unconfounded_observation'])

    def test_unrelated_native_brake_echo_is_not_a_matching_host_return(self):
        rows = self.rows()
        payload = bytearray.fromhex(rows[2][3][0][2])
        payload[3] += 1
        payload[7] += 1
        rows[2][3][0][2] = payload.hex()
        r = evidence.assess_host_attempt(rows, self.T)
        self.assertEqual(r['brake_asserted_tx_echoes'], 1)
        self.assertEqual(r['payload_matching_host_returns'], 0)
        self.assertFalse(r['unconfounded_observation'])

    def test_panda_echo_without_cruise_drop_is_not_acceptance(self):
        rows = self.rows()[:-1]
        self.assertFalse(evidence.assess_host_attempt(rows, self.T)['unconfounded_observation'])

    def test_wrong_bus_input_cannot_supply_physical_coverage(self):
        rows = self.rows()
        rows[0][3][1][0] = 2
        self.assertFalse(evidence.assess_host_attempt(rows, self.T)['unconfounded_observation'])

    def test_initially_asserted_mirror_is_not_a_rising_edge(self):
        self.assertEqual(evidence.edges([(0, b'\x20'), (1, b'\x20'), (2, b'\x00')], 5), [])

    def test_fixture_compression_is_deterministic_and_preserves_equal_timestamps(self):
        rows = [[0, self.T, 'can', []], [0, self.T, 'sendcan', []]]
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp) / 'a.gz', Path(temp) / 'b.gz'
            extraction.write_rows(a, {'schema': 'test'}, iter(rows))
            extraction.write_rows(b, {'schema': 'test'}, iter(rows))
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(evidence.load_rows(a)[1], rows)


if __name__ == '__main__':
    unittest.main()
