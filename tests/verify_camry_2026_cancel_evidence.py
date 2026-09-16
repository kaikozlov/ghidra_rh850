#!/usr/bin/env python3
"""Verify raw cancel-input transitions, topology, integrity and bounded edge census."""
import binascii
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


    @staticmethod
    def pulse_fixture(endian, width=16, bit=7, suppress_last=False, corrupt_last=False):
        # Exercise a field crossing three bytes rather than only aligned words.
        # Pre-cancel states deliberately differ between events.
        address, size, byte, pulse = 0x160, 32, 5, 0xA53C if width == 16 else 0xA5
        windows, metadata = [], []
        for event in range(3):
            center = (event + 1) * 2_000_000_000
            metadata.append({'center_nanos': center})
            def encode(value):
                data = bytearray(size)
                shift = bit if endian == 'little' else 24 - bit - width
                data[byte:byte + 3] = (value << shift).to_bytes(3, endian)
                data[:2] = binascii.crc_hqx(data[2:] + address.to_bytes(2, 'little'), 0xffff).to_bytes(2, 'little')
                return bytes(data)
            old = encode(event + 1)
            active = old if suppress_last and event == 2 else encode(pulse)
            if corrupt_last and event == 2:
                active = bytes([active[0] ^ 1]) + active[1:]
            windows.append({(1, address, size): [
                (center - 600_000_000, old), (center - 200_000_000, old),
                (center + 10_000_000, old), (center + 40_000_000, active),
                (center + 80_000_000, old),
            ]})
        return windows, metadata, {'address': '0x160', 'length': size, 'byte': byte,
                                   'bit_offset': bit, 'endian': endian, 'width': width, 'values': [pulse]}

    def test_enum_screen_finds_cross_byte_short_pulses_in_both_directions(self):
        for endian in ('little', 'big'):
            with self.subTest(endian=endian):
                windows, metadata, expected = self.pulse_fixture(endian)
                self.assertIn(expected, evidence.enum_screen(windows, metadata)['candidates'])

    def test_enum_screen_requires_the_pulse_in_every_event(self):
        for endian in ('little', 'big'):
            with self.subTest(endian=endian):
                windows, metadata, _ = self.pulse_fixture(endian, suppress_last=True)
                self.assertEqual(evidence.enum_screen(windows, metadata)['candidates'], [])

    def test_corrupt_crc_cannot_supply_a_missing_cancel_observation(self):
        for endian in ('little', 'big'):
            with self.subTest(endian=endian):
                windows, metadata, _ = self.pulse_fixture(endian, corrupt_last=True)
                self.assertEqual(evidence.enum_screen(windows, metadata)['candidates'], [])

    def test_narrow_window_screen_also_detects_a_one_frame_pulse(self):
        for endian in ('little', 'big'):
            with self.subTest(endian=endian):
                windows, metadata, expected = self.pulse_fixture(endian, width=8, bit=3)
                result = evidence.multibit_screen(windows, metadata)
                reproduced = result['per_stream'][0]['reproduced_in_every_event']
                self.assertTrue(any(r['endian'] == endian and r['width'] == 8 and
                                    r['byte'] == expected['byte'] and r['first_bit'] == 3 and
                                    r['value'] == 0xA5 for r in reproduced))


if __name__ == '__main__':
    unittest.main()
