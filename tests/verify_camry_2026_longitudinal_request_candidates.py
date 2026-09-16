#!/usr/bin/env python3
"""Verify the bounded Camry longitudinal-request candidate ranking."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
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

  def test_current_stock_topology_is_role_normalized(self):
    t = self.report['topology_normalization']
    self.assertEqual(t['current_stock_candidate_planes']['direct_frc_bus1_pdus']['panda_bus'], 2)
    self.assertEqual(t['current_stock_candidate_planes']['protected_bus4_request_result_family']['panda_bus'], 1)
    self.assertIn('era-dependent', t['rule'])

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

  def test_gts_semantics_match_width_and_scale_without_claiming_wire_identity(self):
    g = self.report['gts_semantic_template']
    for did in ('0x10A1', '0x10A2'):
      row = g['brake_tss_receive'][did]
      self.assertEqual(row['bit_width'], 16)
      self.assertTrue(row['signed'])
      self.assertEqual(row['decimal_point_count'], 3)
      self.assertEqual(row['unit'], 'm/s^2')
    for did in ('0x10A3', '0x10A4'):
      self.assertEqual(g['brake_tss_receive'][did]['bit_width'], 6)
    lower = next(r for r in g['pcs_operation_ffd_5280_lower'] if 'acceleration' in r['name'])
    upper = next(r for r in g['pcs_operation_ffd_5281_upper'] if 'acceleration' in r['name'])
    for row in (lower, upper):
      self.assertEqual(row['bit_length'], 16)
      self.assertEqual(row['type'], 's')
      self.assertEqual(row['lsb'], '0.001')
    self.assertIn('not the 0x08A byte assignment', g['boundary'])

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

  def test_simple_direct_frc_precursor_search_is_negative_except_state_related_160(self):
    s = self.report['direct_frc_bus1_precursor_screen']['per_id']
    for address in ('0x020', '0x230', '0x440'):
      self.assertEqual(s[address]['reproduced_abs_r_ge_0p25'], 0)
    self.assertGreater(s['0x160']['reproduced_abs_r_ge_0p25'], 0)
    top = s['0x160']['best_reproduced_same_sign'][0]
    self.assertEqual(top['drive_a']['lag_ms'], 300)
    self.assertEqual(top['drive_b']['lag_ms'], 300)
    self.assertGreater(top['min_abs_r'], .6)

  def test_c9_is_weak_and_ca_is_reverse_direction(self):
    c9 = self.report['other_candidates']['0x0C9']['b12_b13_vs_0x0ca']
    self.assertTrue(all(abs(row['r']) < .30 for row in c9.values()))
    self.assertIn('chassis -> upstream', self.report['other_candidates']['0x0CA']['direction'])

  def test_no_runtime_authority_claim(self):
    self.assertIn('Do not restore Camry 0x160 longitudinal output', self.report['implementation_boundary'])
    self.assertIn('do not inject 0x08A', self.report['implementation_boundary'])


if __name__ == '__main__':
  unittest.main(verbosity=2)
