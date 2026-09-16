#!/usr/bin/env python3
"""Reject confounded cancel acceptance claims using original and synthetic timing."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis import (
    analyze_camry_2026_cancel_request_causality as evidence,
)

CENTER = 2_000_000_000
INFO = {'request_nanos': CENTER, 'source_indices': [0], 'physical_input_bus': 1, 'cruise_bus': 1}


def row(offset_ms, kind, payload):
    return [0, 0, CENTER + int(offset_ms * 1e6), kind, payload]


def frame(address, active=False, bus=1):
    data = bytearray(8 if address == 0x101 else 32)
    if address == 0x101:
        data[0] = 0x88 if active else 0x80
        data[7] = (sum(data[:7]) + 10) & 255
    elif address == 0xFE:
        # Structural read-only predicate, not an authenticated vehicle packet.
        data[4] = 0x40 if active else 0
        data[7] = 0 if active else 0x20
    elif address == 0x08A:
        data[3] = 8 if active else 0
    return [bus, address, data.hex()]


def window():
    return [row(-100, 'carControl', False), row(0, 'carControl', True),
            row(-100, 'can', [frame(0xFE), frame(0x101), frame(0x08A, True)]),
            row(5, 'sendcan', [frame(0x101, True, 2)]),
            row(100, 'can', [frame(0xFE), frame(0x101), frame(0x08A)])]


class TestCancelCausality(unittest.TestCase):
    def test_retained_report_regenerates(self):
        self.assertEqual(evidence.build(), json.loads(evidence.OUTPUT.read_text()))

    def test_every_retained_request_has_a_preceding_raw_driver_input(self):
        report = evidence.build()
        self.assertEqual(len(report['windows']), 79)
        for item in report['windows']:
            with self.subTest(request=item['request_nanos']):
                self.assertTrue(item['input_coverage_complete'])
                witness = item['preceding_driver_input']
                self.assertLess(witness['nanos'], item['request_nanos'])
                self.assertLess(item['request_nanos'] - witness['nanos'], 10_000_000)
                self.assertTrue(any(evidence.input_assertions(int(witness['address'], 16), bytes.fromhex(witness['payload']))))
                self.assertEqual(item['disposition'], 'preceding_driver_input_confounds_acceptance')

    def test_preceding_button_and_brake_each_confounds_host_cancellation(self):
        for address in (0xFE, 0x101):
            rows = window() + [row(-5, 'can', [frame(address, True)])]
            result = evidence.reduce_window(INFO, rows)
            self.assertEqual(result['disposition'], 'preceding_driver_input_confounds_acceptance')
            self.assertEqual(result['preceding_driver_input']['offset_ms'], -5)

    def test_driver_input_after_host_but_before_release_is_also_confounded(self):
        result = evidence.reduce_window(INFO, window() + [row(20, 'can', [frame(0x101, True)])])
        self.assertEqual(result['disposition'], 'intervening_driver_input_confounds_acceptance')

    def test_later_driver_input_cannot_explain_an_earlier_release(self):
        result = evidence.reduce_window(INFO, window() + [row(150, 'can', [frame(0x101, True)])])
        self.assertEqual(result['disposition'], 'unconfounded_release_candidate_not_acceptance_proof')

    def test_transmit_echo_and_wrong_bus_do_not_manufacture_driver_input(self):
        rows = window() + [row(-5, 'can', [frame(0xFE, True, 129), frame(0x101, True, 0)])]
        result = evidence.reduce_window(INFO, rows)
        self.assertIsNone(result['preceding_driver_input'])
        self.assertEqual(result['disposition'], 'unconfounded_release_candidate_not_acceptance_proof')

    def test_unconfounded_release_remains_only_a_candidate(self):
        result = evidence.reduce_window(INFO, window())
        self.assertEqual(result['disposition'], 'unconfounded_release_candidate_not_acceptance_proof')
        self.assertEqual(result['release_offset_ms'], 100)

    def test_missing_or_malformed_input_is_not_treated_as_no_driver_input(self):
        rows = window()
        rows[2][4] = [frame(0x101), frame(0x08A, True)]
        result = evidence.reduce_window(INFO, rows)
        self.assertFalse(result['input_coverage_complete'])
        self.assertEqual(result['disposition'], 'incomplete_input_coverage')
        for payload in (bytes(3), bytes(8)):
            self.assertIsNone(evidence.input_assertions(0x101, payload))
        self.assertIsNone(evidence.input_assertions(0xFE, bytes(8)))

    def test_malformed_recovered_input_prevents_a_clean_candidate(self):
        rows = window() + [row(-5, 'can', [[1, 0x101, bytes(8).hex()]])]
        self.assertEqual(evidence.reduce_window(INFO, rows)['disposition'], 'incomplete_input_coverage')

    def test_inactive_stock_cruise_and_absent_release_are_distinguished(self):
        rows = window()
        rows[2][4][-1] = frame(0x08A)
        self.assertEqual(evidence.reduce_window(INFO, rows)['disposition'], 'cruise_already_inactive')
        rows = window()
        rows[-1][4][-1] = frame(0x08A, True)
        self.assertEqual(evidence.reduce_window(INFO, rows)['disposition'], 'no_native_release_in_window')

    def test_held_or_unobserved_host_flag_is_not_a_rising_request(self):
        for prior in (True, None):
            rows = window()
            if prior is None:
                rows.pop(0)
            else:
                rows[0][4] = prior
            with self.assertRaises(ValueError):
                evidence.reduce_window(INFO, rows)

    def test_redundant_cancel_bit_must_agree(self):
        packet = frame(0xFE, True)
        data = bytearray.fromhex(packet[2])
        data[7] |= 0x20
        self.assertIsNone(evidence.input_assertions(0xFE, bytes(data)))
        rows = window() + [row(-5, 'can', [[1, 0xFE, data.hex()]])]
        self.assertEqual(evidence.reduce_window(INFO, rows)['disposition'], 'incomplete_input_coverage')


if __name__ == '__main__':
    unittest.main()
