#!/usr/bin/env python3
"""Verify raw cancel-input transitions, topology, integrity and bounded edge census."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis import analyze_camry_2026_cancel_evidence as evidence


class TestCancelEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = evidence.build()

    def test_regeneration(self):
        self.assertEqual(self.report, json.loads(evidence.OUTPUT.read_text()))

    def test_real_switch_transition_and_independent_native_cruise_drop(self):
        self.assertEqual(len(self.report['windows']), 21)
        for row in self.report['windows']:
            with self.subTest(route=row['route'], time=row['center_nanos']):
                self.assertFalse(evidence.is_cancel(bytes.fromhex(row['switch_before'])))
                self.assertTrue(evidence.is_cancel(bytes.fromhex(row['switch_pressed'])))
                self.assertTrue(bytes.fromhex(row['cruise_before'])[3] & 8)
                self.assertFalse(bytes.fromhex(row['cruise_released'])[3] & 8)
                self.assertFalse(row['concurrent_brake'])
                self.assertGreater(row['cruise_drop_delay_ms'], 0)
                self.assertLess(row['cruise_drop_delay_ms'], 200)

    def test_adas_integrity(self):
        self.assertEqual(self.report['integrity'].get('invalid', 0), 0)
        self.assertEqual(self.report['integrity']['valid'], 16526)

    def test_literal_edge_census_does_not_promote_an_incidental_correlate(self):
        screen = self.report['literal_edge_screen']
        self.assertEqual(screen['eligible_bit_polarities'], 17824)
        self.assertEqual(screen['reproduced_in_every_event'], [])
        self.assertEqual(screen['highest_coverage'][0]['events_with_edge'], 10)
        self.assertTrue(all(r['events_observed'] == 21 for r in screen['highest_coverage']))

    def test_all_22_streams_are_covered_by_the_multibit_screen(self):
        screen = self.report['enumerated_value_screen']
        self.assertEqual(len(screen['complete_streams']), 22)
        self.assertEqual(screen['field_specs'], 279904)
        self.assertEqual(screen['candidates'], [])
        for row in self.report['windows']:
            self.assertEqual(len(row['adas_streams']), 22)


if __name__ == '__main__':
    unittest.main()
