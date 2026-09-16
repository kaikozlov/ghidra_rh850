#!/usr/bin/env python3
"""Guard independent motion comparison, bounded pairing, and retained counterfactuals."""
from __future__ import annotations

import binascii
import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis import analyze_camry_20260916_longitudinal_motion_audit as audit


def sample(counter=0, fine_raw=0, coarse_raw=0, flag=True):
    data = bytearray(32)
    data[2] = counter
    data[4:6] = ((fine_raw & 32767) | (32768 if flag else 0)).to_bytes(2, 'big')
    data[12] = coarse_raw & 127
    data[:2] = binascii.crc_hqx(data[2:] + b'\x60\x01', 0xFFFF).to_bytes(2, 'little')
    return bytes(data)


class TestOfflinePrimitives(unittest.TestCase):
    def test_signed_fields_do_not_include_the_preserved_flag(self):
        for flag in (False, True):
            for raw in (-16384, -1000, -1, 0, 1, 1000, 16383):
                with self.subTest(flag=flag, raw=raw):
                    data = np.array([list(sample(fine_raw=raw, flag=flag))], dtype=np.uint8)
                    self.assertAlmostEqual(audit.fine(data)[0], raw * .001)
        for raw in (-64, -1, 0, 1, 63):
            data = np.array([list(sample(coarse_raw=raw))], dtype=np.uint8)
            self.assertAlmostEqual(audit.coarse(data)[0], -raw * .1)

    def test_source_labels_accept_relative_and_external_fixture_paths(self):
        self.assertEqual(audit.source_path(audit.FIXTURE), str(audit.FIXTURE.relative_to(ROOT)))
        relative = Path('tests/fixtures/camry_20260916_longitudinal_motion_audit.jsonl.gz')
        self.assertEqual(audit.source_path(relative), audit.source_path(relative.resolve()))
        self.assertEqual(audit.source_path(Path('/tmp/external-fixture.jsonl.gz')), str(Path('/tmp/external-fixture.jsonl.gz').resolve()))

    def test_crc_and_length_validation(self):
        data = sample(255, -1000, 3)
        self.assertTrue(audit.valid_160(data))
        self.assertFalse(audit.valid_160(data[:-1]))
        broken = bytearray(data)
        broken[4] ^= 1
        self.assertFalse(audit.valid_160(broken))

    def test_wheel_offset_units_and_invalid_bit(self):
        # Four independent 36 km/h samples, corresponding to 10 m/s.
        word = int(round((36 + 67.67) * 100)).to_bytes(2, 'big')
        data = np.array([list(word * 4)], dtype=np.uint8)
        value, valid = audit.wheel_speed(data)
        self.assertAlmostEqual(value[0], 10)
        self.assertTrue(valid[0])
        data[0, 0] |= 128
        self.assertFalse(audit.wheel_speed(data)[1][0])

    def test_nearest_cannot_use_a_different_source_file(self):
        ref = audit.series([(1, 100, sample())])
        other = audit.series([(2, 100, sample())])
        self.assertFalse(audit.nearest(ref, other)[1][0])

    def test_preceding_state_does_not_read_a_future_sample(self):
        ref = audit.series([(0, 100, sample())])
        future = audit.series([(0, 101, sample())])
        self.assertFalse(audit.nearest(ref, future, preceding=True)[1][0])
        self.assertTrue(audit.nearest(ref, future)[1][0])

    def test_nearest_limit_and_tie_choose_earlier(self):
        ref = audit.series([(0, 100, sample())])
        other = audit.series([(0, 90, sample()), (0, 110, sample())])
        indices, valid = audit.nearest(ref, other, max_gap_ns=10)
        self.assertTrue(valid[0])
        self.assertEqual(indices[0], 0)
        self.assertFalse(audit.nearest(ref, other, max_gap_ns=9)[1][0])

    def test_wrapping_counter_is_matched_locally(self):
        camera = audit.series([(0, 0, sample(0)), (0, 6_390_000_000, sample(255)), (0, 6_415_000_000, sample(0))])
        host = audit.series([(0, 6_420_000_000, sample(0))])
        indices, valid = audit.preceding_counter_match(host, camera)
        self.assertTrue(valid[0])
        self.assertEqual(indices[0], 2)

    def test_matching_counter_cannot_be_stale_future_or_in_another_file(self):
        host = audit.series([(0, 1_000_000_000, sample(7))])
        for rows in ([(0, 900_000_000, sample(7))], [(0, 1_001_000_000, sample(7))], [(1, 999_000_000, sample(7))]):
            self.assertFalse(audit.preceding_counter_match(host, audit.series(rows))[1][0])

    def test_payload_match_checks_more_than_nearest_return(self):
        host = audit.series([(0, 100, sample(7, fine_raw=20))])
        returns = audit.series([(0, 101, sample(8)), (0, 120, sample(7, fine_raw=20))])
        matched, offsets = audit.nearby_payload_match(host, returns, max_gap_ns=25)
        self.assertTrue(matched[0])
        self.assertEqual(offsets[0], 20)
        self.assertFalse(audit.nearby_payload_match(host, returns, max_gap_ns=10)[0][0])

    def test_interpolation_rejects_gaps_and_extrapolation(self):
        ts = np.array([0, 10, 100])
        vals, valid = audit.interpolate_valid(ts, [0., 10., 100.], [-1, 0, 5, 10, 11, 99, 100, 101], max_gap_ns=20)
        self.assertEqual(valid.tolist(), [False, True, True, True, False, False, True, False])
        self.assertEqual(vals[2], 5.)

    def test_empty_stream_does_not_turn_into_zero_measurements(self):
        with self.assertRaises(ValueError):
            audit.series([])


class TestRetainedRoleEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build()

    def test_report_reproduces_without_ignored_workspaces(self):
        self.assertEqual(self.report, json.loads(audit.OUTPUT.read_text()))

    def test_both_complete_august_sources_are_crc_valid(self):
        self.assertEqual([x['valid_0x160_frames'] for x in self.report['august_motion'].values()], [20510, 23998])
        self.assertTrue(all(not x['rejected'] for x in self.report['august_motion'].values()))
        self.assertEqual(self.report['invalid_0x160'], [])

    def test_adjacent_c9_id_is_not_promoted_to_a_secoc_command(self):
        for d in self.report['august_motion'].values():
            self.assertGreater(d['c9_shape']['frames'], 16000)
            self.assertEqual(d['c9_shape']['frames_nonzero_outside_b12_b13'], 0)

    def test_independent_wheel_acceleration_agrees_without_cruise_latch(self):
        for d in self.report['august_motion'].values():
            observed = d['measured_motion_time_shift_ms']['-100']['cruise_latch_clear']
            self.assertGreater(observed['n'], 7000)
            self.assertGreater(observed['pearson_r'], .97)
            self.assertTrue(.95 < observed['slope_y_per_x'] < 1.02)
            self.assertLess(abs(observed['intercept']), .01)

    def test_every_trial_frame_has_a_fresh_same_counter_source_and_exact_tx_return(self):
        trial = self.report['combined_trial']
        self.assertEqual(trial['host_frames'], 1249)
        self.assertEqual(trial['source_counter_matched'], 1249)
        self.assertEqual(trial['byte_identical_nearby_returned_tx'], 1249)
        self.assertEqual(trial['b12_changed_from_counter_matched_native'], 970)
        self.assertTrue(0 <= trial['native_source_age_ms'][0] < trial['native_source_age_ms'][-1] < 3)
        self.assertGreater(trial['matching_return_offset_ms'][0], 0)

    def test_native_comparator_cannot_be_omitted_from_combined_trial(self):
        for shift in ('-100', '0', '100'):
            d = self.report['combined_trial']['ca_time_shift_ms'][shift]
            self.assertGreater(d['native_b12_hypothesis']['pearson_r'], .92)
            self.assertLess(d['host_b12_hypothesis']['pearson_r'], .74)
            self.assertEqual(d['b12_disagreement_only']['native_b12_hypothesis']['n'], 970)
            self.assertGreater(d['b12_disagreement_only']['native_b12_hypothesis']['pearson_r'], .91)

    def test_cruise_mode_is_not_healthy_adaptive_validation(self):
        counts = self.report['combined_trial']['preceding_mode_byte_counts']
        self.assertEqual(counts, {'0x88': 2, '0x90': 1247})

    def test_three_stock_starts_move_before_the_fine_field_leaves_zero(self):
        self.assertEqual(len(self.report['stock_resumes']), 3)
        for event in self.report['stock_resumes']:
            self.assertTrue(200 < event['b4_first_nonzero_after_motion_ms'] < 300)
            by_offset = {r['offset_ms']: r for r in event['samples']}
            self.assertEqual(by_offset[200]['b4_fine'], 0)
            self.assertGreater(by_offset[200]['wheel_speed_mps'], .4)
            self.assertGreater(by_offset[-500]['ca_result_like'], .3)
            self.assertEqual(by_offset[-500]['wheel_speed_mps'], 0)

    def test_ca_has_chassis_native_and_camera_bound_tx_not_two_native_sources(self):
        census = self.report['fixture_can_census']
        for group, n in [('stock_3b', 2547), ('stock_3c', 5094)]:
            ca = {r['panda_src']: r['n'] for r in census if r['group'] == group and r['address'] == '0xca' and r['service'] == 'can'}
            self.assertEqual(ca, {0: n, 130: n})


if __name__ == '__main__':
    unittest.main()
