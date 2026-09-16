#!/usr/bin/env python3
"""Reproduce passive 0x160 role evidence and test alignment failure modes."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis.analyze_camry_2026_longitudinal_role import (
    FIXTURE,
    OUTPUT,
    build,
    crc_valid,
    hold,
    matching_template,
    quantities_160,
    signed,
    stats,
    wheel_speed,
)


class AlignmentAndDecoding(unittest.TestCase):
    def test_signed_boundaries(self):
        self.assertEqual([signed(v, 7) for v in (0, 63, 64, 127)], [0, 63, -64, -1])
        self.assertEqual(signed(0x4000, 15), -16384)
        self.assertEqual(signed(0x7FFF, 15), -1)
        with self.assertRaises(ValueError):
            signed(0, 0)

    def test_observed_field_geometry(self):
        d = bytearray.fromhex('210e2082800040034de813007fe8008000a000f005b000040000000000000000')
        a = np.array([[0, 0, *d]], dtype=np.int64)
        q = quantities_160(a)
        self.assertEqual(q['fine'][0], 0)
        self.assertAlmostEqual(q['speed_candidate_mps'][0], 0)
        self.assertAlmostEqual(q['b12_candidate'][0], .1)
        a[0, 6:8] = [0x82, 0x0A]
        self.assertAlmostEqual(quantities_160(a)['fine'][0], .522)
        a[0, 6:8] = [0xFF, 0xFF]
        self.assertAlmostEqual(quantities_160(a)['fine'][0], -.001)
        with self.assertRaises(ValueError):
            quantities_160(a[:, :-1])

    def test_invalid_wheel_is_not_stationary_evidence(self):
        payload = bytes.fromhex('1a6f1a6f1a6f1a6f')  # four valid zero-speed values
        row = np.array([[0, 0, *payload]], dtype=np.int64)
        self.assertAlmostEqual(wheel_speed(row)[0], 0)
        for i in (0, 2, 4, 6):
            bad = row.copy(); bad[0, i + 2] |= 0x80
            self.assertTrue(np.isnan(wheel_speed(bad)[0]))

    def test_received_crc_rejects_corruption(self):
        d = bytes.fromhex('210e2082800040034de813007fe8008000a000f005b000040000000000000000')
        self.assertTrue(crc_valid(d))
        for i in (0, 2, 4, 12, 31):
            bad = bytearray(d); bad[i] ^= 1
            self.assertFalse(crc_valid(bytes(bad)))
        self.assertFalse(crc_valid(d[:-1]))

    def test_hold_never_uses_future_or_stale_sample(self):
        a = np.array([[0, 100, 11], [0, 200, 22], [1, 150, 99]])
        v, good = hold(a, a[:, 2], 0, np.array([50, 100, 150, 201, 300]), 60)
        self.assertEqual(good.tolist(), [False, True, True, True, False])
        self.assertEqual(v[good].tolist(), [11, 11, 22])

    def test_hold_does_not_bridge_sources(self):
        a = np.array([[0, 100, 11], [1, 150, 99]])
        v, good = hold(a, a[:, 2], 1, np.array([120, 150]), 1000)
        self.assertEqual(good.tolist(), [False, True])
        self.assertEqual(v[1], 99)
        _, good = hold(a, a[:, 2], 2, np.array([150]), 1000)
        self.assertFalse(good.any())

    def test_hold_rejects_unordered_source(self):
        a = np.array([[0, 200, 1], [0, 100, 2]])
        with self.assertRaises(ValueError):
            hold(a, a[:, 2], 0, np.array([150]))

    def test_counter_match_also_needs_recent_past_and_same_source(self):
        def row(source, t, counter):
            d = [0] * 32; d[2] = counter
            return np.array([source, t, *d], dtype=np.int64)
        camera = np.array([row(0, 0, 7), row(0, 6_400_000_000, 7), row(1, 6_410_000_000, 7)])
        host = row(0, 6_420_000_000, 7)
        self.assertEqual(matching_template(camera, host)[1], 6_400_000_000)
        self.assertIsNone(matching_template(camera[:1], host))
        self.assertIsNone(matching_template(camera, row(0, 6_390_000_000, 7)))
        self.assertIsNone(matching_template(camera, row(2, 6_420_000_000, 7)))

    def test_statistics_handle_constant_and_invalid_values(self):
        self.assertNotIn('r', stats([0, 0, 0], [0, 0, 0]))
        self.assertEqual(stats([1, float('nan')], [1, 2])['n'], 1)
        with self.assertRaises(ValueError):
            stats([1], [1, 2])


class OriginalEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build(FIXTURE)

    def test_portable_regeneration(self):
        expected = json.loads(OUTPUT.read_text())
        self.assertEqual(self.report, expected)

    def test_native_camera_integrity(self):
        for label, count in [('a', 20510), ('b', 23998)]:
            r = self.report['native'][label]
            self.assertEqual(r['camera_frames'], count)
            self.assertEqual(r['valid_camera_crc'], count)

    def test_ego_motion_relationship_repeats(self):
        for r in self.report['native'].values():
            self.assertGreater(r['fine_vs_chassis_13c']['all']['r'], .97)
            self.assertLess(r['fine_vs_chassis_13c']['all']['median_abs_error'], .02)
            self.assertGreater(r['speed_vs_raw_wheels']['r'], .999)
            self.assertLess(r['speed_vs_raw_wheels']['median_abs_error'], .025)
        for r in self.report['trials'].values():
            a = r['fine_vs_carState_aEgo_cruise_off_above_2mps']
            self.assertGreater(a['n'], 6000)
            self.assertGreater(a['r'], .95)

    def test_resultlike_channel_precedes_b12_best_alignment(self):
        for r in self.report['native'].values():
            peak = r['b12_vs_ca_lag']['peak_level']
            self.assertLess(peak['lag_ms'], 0)
            self.assertGreater(peak['levels']['r'], .95)

    def test_lag_peak_is_not_a_unique_causal_delay(self):
        for r in self.report['native'].values():
            lag = r['b12_vs_ca_lag']
            self.assertGreater(lag['peak_level_r_gain_over_zero'], 0)
            self.assertLess(lag['peak_level_r_gain_over_zero'], .001)
            self.assertLess(lag['peak_change']['changes_200ms']['r'], .5)

    def test_physical_chassis_return_direction(self):
        d = self.report['historical_relay_direction']
        self.assertEqual(d['0x0CA'], {'0': 13756, '1': 0, '2': 503, '128': 0, '130': 13256})
        self.assertEqual(d['0x160'], {'0': 0, '1': 12771, '2': 0, '128': 0, '130': 0})
        self.assertEqual(d['0x08A']['2'], 12960)
        self.assertEqual(d['0x0C9']['2'], 10128)

    def test_actual_host_changes_and_tx_returns(self):
        expected = {'d1': (10259, 10228, 0, 10246), 'd4': (1249, 1243, 970, 1249)}
        for group, values in expected.items():
            d = self.report['trials'][group]['delivery']; c = d['counts']
            self.assertEqual(tuple(c[k] for k in ('host_frames', 'fine_changed', 'b12_changed', 'exact_payload_return_after_host_send')), values)
            self.assertEqual(c['counter_and_time_matched_template'], c['host_frames'])
            self.assertEqual(c['only_expected_offsets_changed'], c['host_frames'])
            for crc in d['checksum_checks'].values():
                self.assertEqual(crc['valid'], crc['n'])

    def test_untouched_source_comparison_was_not_omitted(self):
        r = self.report['trials']['d4']['comparison']
        self.assertGreater(r['native_b12_vs_0ca_resultlike']['r'], .93)
        self.assertLess(r['host_b12_vs_0ca_resultlike']['r'], .71)
        self.assertEqual(r['n_grid_samples'], 1244)

    def test_three_observed_input_free_resumes_precede_fine_demand(self):
        events = [r for group in self.report['stock_resumes'].values() for r in group]
        self.assertEqual(len(events), 3)
        for e in events:
            inputs = e['driver_inputs_minus1_to_plus0p5_seconds']
            self.assertGreater(inputs['carState_samples'], 140)
            self.assertGreater(inputs['switch_frames'], 40)
            self.assertTrue(all(v == 0 for k, v in inputs.items() if 'asserted' in k))
            wheel = e['raw_wheels_above_0p025_mps_ns']
            self.assertLess(e['ca_above_0p5_ns'], wheel - 300_000_000)
            self.assertGreater(e['fine_above_0p05_ns'], wheel + 200_000_000)
            sample = next(s for s in e['samples'] if s['relative_to_prior_motion_threshold_ms'] == 100)
            self.assertEqual(sample['fine'], 0)
            self.assertGreater(sample['wheel_mean_mps'], .1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
