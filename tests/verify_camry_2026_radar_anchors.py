#!/usr/bin/env python3
"""Reproduce independent radar anchors from retained raw object bytes."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis import analyze_camry_2026_radar_anchors as anchors


class TestIndependentRadarAnchors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = anchors.reduce(anchors.FIXTURE)

    def test_report_regenerates_exactly(self):
        self.assertEqual(self.report, json.loads(anchors.OUTPUT.read_text()))

    def test_range_scale_has_an_independent_vision_anchor(self):
        r = self.report['vision_range']
        self.assertGreater(r['n'], 1900)
        self.assertGreater(r['pearson_r'], .99)
        self.assertTrue(.97 < r['slope'] < 1.07)
        self.assertLess(r['absolute_error']['p05_median_p95'][1], 1.)

    def test_velocity_uses_its_own_vision_speed_anchor(self):
        r = self.report['vision_relative_speed']
        self.assertGreater(r['n'], 1900)
        self.assertTrue(.9 < r['slope'] < 1.1)
        self.assertLess(r['absolute_error']['p05_median_p95'][1], .4)

    def test_lateral_is_held_out_of_object_matching(self):
        r = self.report['vision_lateral_offcenter']
        inverse = self.report['vision_lateral_inverted_error']
        self.assertGreater(r['n'], 200)
        self.assertGreater(r['pearson_r'], .65)
        self.assertTrue(.85 < r['slope'] < 1.15)
        self.assertLess(r['absolute_error']['p05_median_p95'][1], inverse['p05_median_p95'][1] / 2)

    def test_calibrated_gyro_independently_anchors_lateral_units(self):
        r = self.report['gyro_lateral_derivative']
        self.assertGreater(r['n'], 27000)
        self.assertGreater(r['pearson_r'], .8)
        self.assertTrue(.035 < self.report['gyro_implied_lateral_lsb'] < .043)
        self.assertLess(r['absolute_error']['p05_median_p95'][1], self.report['gyro_inverted_sign_error']['p05_median_p95'][1] / 2)

    def test_retained_high_closing_speed_excludes_narrow_field(self):
        n = self.report['narrow_velocity_wrap_disagreements']
        self.assertGreater(n['12'], 100)
        self.assertEqual(n['13'], 0)  # explicitly bounded: 13/14 cannot be distinguished here
        self.assertGreater(n['14'], 20000)  # two top bits cannot be treated as speed
        self.assertAlmostEqual(anchors.decode(bytes.fromhex('074a010003ff0a'), bytes.fromhex('0836e400809a02'))[2], -58.3)


if __name__ == '__main__':
    unittest.main()
