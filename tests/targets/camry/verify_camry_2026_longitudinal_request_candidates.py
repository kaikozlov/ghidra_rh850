#!/usr/bin/env python3
"""Verify the bounded Camry longitudinal-request candidate ranking."""
from __future__ import annotations

import json
import unittest

from tools import REPO_ROOT
ROOT = REPO_ROOT
from tools.targets.camry.analysis.analyze_camry_2026_longitudinal_request_candidates import (
  build,
)

ARTIFACT = ROOT / 'data/generated/camry_2026_longitudinal_request_candidates.json'


class CandidateEvidence(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.report = build()

  def test_portable_regeneration(self):
    self.assertEqual(self.report, json.loads(ARTIFACT.read_text()))

  def test_08a_has_two_identical_signed16_candidate_words(self):
    for drive in self.report['protected_0x08a_acceleration_candidate']['drives'].values():
      self.assertEqual(drive['frames'], drive['b8_b9_equals_b11_b12'])
      self.assertEqual(drive['equality_fraction'], 1.0)
      self.assertLess(drive['scaled_mps2_range'][0], -0.9)
      self.assertGreater(drive['scaled_mps2_range'][1], 0.9)
    checks = self.report['protected_0x08a_acceleration_candidate']['prior_independence_checks']
    for drive in checks.values():
      for r in drive.values():
        self.assertLess(abs(r), .11)

  def test_three_no_input_resumes_have_request_candidate_before_motion(self):
    events = self.report['protected_0x08a_acceleration_candidate']['stock_resume_evidence']
    self.assertEqual(len(events), 3)
    for event in events:
      inputs = event['driver_inputs_minus1_to_plus0p5_seconds']
      self.assertTrue(all(v == 0 for k, v in inputs.items() if 'asserted' in k))
      sample_m500 = next(s for s in event['samples'] if s['offset_from_wheel_onset_ms'] == -500)
      sample_zero = next(s for s in event['samples'] if s['offset_from_wheel_onset_ms'] == 0)
      self.assertGreater(sample_m500['request_word_b8_b9_mps2'], .25)
      self.assertAlmostEqual(sample_m500['request_word_b8_b9_mps2'], sample_m500['request_word_b11_b12_mps2'])
      self.assertGreater(sample_zero['request_word_b8_b9_mps2'], .58)
      self.assertEqual(sample_m500['c9_b12_b13_raw'], 0x1838)
      self.assertEqual(sample_zero['c9_b12_b13_raw'], 0x1838)

  def test_simple_direct_frc_duplicate_search_is_negative_except_state_related_160(self):
    s = self.report['direct_frc_bus1_duplicate_request_screen']['per_id']
    for address in ('0x020', '0x230', '0x440'):
      self.assertEqual(s[address]['reproduced_abs_r_ge_0p25'], 0)
    self.assertGreater(s['0x160']['reproduced_abs_r_ge_0p25'], 0)
    top = s['0x160']['best_reproduced_same_sign'][0]
    self.assertEqual(top['drive_a']['lag_ms'], 300)
    self.assertEqual(top['drive_b']['lag_ms'], 300)
    self.assertGreater(top['min_abs_r'], .6)

  def test_protected_domain_has_coarse_lagging_companions_not_a_second_direct_magnitude(self):
    coarse = self.report['protected_0x5af_coarse_companion']['drives']
    self.assertEqual(coarse['drive_a']['signed6_b26_values'], [-1, 0, 1])
    self.assertEqual(coarse['drive_b']['signed6_b26_values'], [-2, -1, 0, 1])
    for drive, expected_lag in [('drive_a', -50), ('drive_b', -75)]:
      fit = coarse[drive]['best_vs_0x08a_request_word']
      self.assertEqual(fit['lag_ms'], expected_lag)
      self.assertGreater(fit['r'], .75)
      self.assertGreater(fit['slope'], .24)
      self.assertLess(fit['slope'], .26)
    screen = self.report['protected_bus4_companion_screen']['reproduced_same_sign']
    self.assertEqual((screen[0]['address'], screen[0]['field']), ('0x5AF', 'B26/s6'))
    self.assertEqual((screen[1]['address'], screen[1]['field']), ('0x5F7', 'B7/s6'))

  def test_c9_is_weak_and_ca_is_reverse_direction(self):
    c9 = self.report['other_candidates']['0x0C9']['b12_b13_vs_0x0ca']
    self.assertTrue(all(abs(row['r']) < .30 for row in c9.values()))


if __name__ == '__main__':
  unittest.main(verbosity=2)
