#!/usr/bin/env python3
"""Verify source integrity and out-of-sample object lifecycle behavior."""
import gzip
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis import analyze_camry_2026_radar_lifecycle as lifecycle


class TestRadarLifecycleEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = lifecycle.build()

    def test_report_regenerates(self):
        self.assertEqual(self.report, json.loads(lifecycle.OUTPUT.read_text()))

    def test_source_integrity(self):
        for name, row in self.report['datasets'].items():
            with self.subTest(source=name):
                checks = [row['integrity']] if 'integrity' in row else row['header']['source_counts']
                self.assertEqual(sum(c.get('crc_invalid', 0) for c in checks), 0)
                self.assertGreater(sum(c.get('crc_valid', 0) for c in checks), 60000)
                self.assertGreater(row['counts']['bank_cycles'], 30000)

    def test_new_and_end_bits_distinguish_birth_death_and_replacement(self):
        for name, row in self.report['datasets'].items():
            c = row['counts']
            with self.subTest(source=name):
                self.assertGreater(c['birth'], 1000)
                self.assertEqual(c['birth_start'], c['birth'])
                self.assertEqual(c['birth_end'], 0)
                self.assertEqual(c['death_end'], c['death'])
                self.assertEqual(c['death_start'], 0)
                self.assertGreater(c['occupied_end_and_start'], 5000)

    def test_replacement_flag_generalizes_beyond_discovery(self):
        c = self.report['datasets']['september_holdout']['counts']
        self.assertGreater(c['large_change'], 16000)
        self.assertGreater(c['large_change_start'] / c['large_change'], .995)
        self.assertLess(c['steady_start'] / c['steady'], .001)

    def test_status_is_not_a_range_only_validity_rule(self):
        rows = list(self.report['datasets'].values())
        self.assertEqual(sum(r['counts']['empty_state_nonzero'] for r in rows), 0)
        self.assertGreater(sum(r['counts']['nonempty_state_zero'] for r in rows), 100)
        for row in rows:
            for value in (1, 2, 3):
                self.assertGreater(row['raw_state_counts'][f'occupied_state_{value}'], 0)

    def test_literal_replacement_without_an_empty_slot(self):
        example = self.report['datasets']['september_holdout']['examples']['occupied_replacement']
        old_a, old_b = map(bytes.fromhex, example['before'])
        a, b = map(bytes.fromhex, example['after'])
        self.assertNotEqual(old_a, lifecycle.EMPTY)
        self.assertNotEqual(a, lifecycle.EMPTY)
        self.assertTrue(old_b[5] & 3)
        self.assertTrue(b[5] & 3)
        self.assertTrue(b[4] & 0x80)
        self.assertTrue(b[5] & 0x10)

    def test_additional_original_frames_include_final_stock_harness(self):
        fixture = ROOT / 'tests/fixtures/camry_2026_radar_lifecycle.jsonl.gz'
        with gzip.open(fixture, 'rt') as f:
            header = json.loads(next(f))
            frames = [[] for _ in header['sources']]
            for line in f:
                source, nanos, packets = json.loads(line)
                for address, data in packets:
                    frames[source].append((source, nanos, address, bytes.fromhex(data)))
        self.assertEqual(sum(s['radar_bus'] == 0 for s in header['sources']), 2)
        for source, values in zip(header['sources'], frames, strict=True):
            with self.subTest(source=source['path']):
                integrity = Counter()
                result = lifecycle.reduce_rows(lifecycle.banks(values, integrity))
                c = result['counts']
                self.assertEqual(integrity.get('crc_invalid', 0), 0)
                self.assertGreater(integrity['crc_valid'], 7000)
                self.assertEqual(c['birth_start'], c['birth'])
                self.assertEqual(c['death_end'], c['death'])
                self.assertEqual(c['empty_state_nonzero'], 0)
                self.assertGreater(c['large_change_start'] / c['large_change'], .995)


if __name__ == '__main__':
    unittest.main()
