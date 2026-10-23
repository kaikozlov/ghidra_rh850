#!/usr/bin/env python3
"""Offline VMC request decoding and joined-origin/phase regressions."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tools.targets.camry.analysis.analyze_camry_20260930_vmc_status import route_report
from tools.targets.camry.analysis.extract_camry_20260930_vmc_corpus import COLUMNS
from tools.targets.camry.analysis.join_camry_20260930_vmc_corpus import REQUEST_COLUMNS, join, requests
from tools.toyota_support.toyota_route_opendbc_common import toyota_checksum


def payload(latch: bool, byte4_bit6: bool = False, request_header: int = (11 << 2) | 1) -> bytes:
  data = bytearray(32)
  data[3] = 8 if latch else 0
  data[4] = 0x40 if byte4_bit6 else 0
  data[6] = request_header
  data[7] = toyota_checksum(0x08A, data[:8])
  data[8:10] = (-1250).to_bytes(2, "big", signed=True)
  data[11:13] = (375).to_bytes(2, "big", signed=True)
  data[21], data[26] = 0xCB, 0xFE
  return bytes(data)


class VmcRequestTests(unittest.TestCase):
  def test_checksum_tracks_header_flags_not_request_metadata(self):
    frames = [payload(True), payload(True, True), payload(False)]
    rows = requests(np.frombuffer(b"".join(frames), dtype=np.uint8).reshape(-1, 32))
    decoded = [dict(zip(REQUEST_COLUMNS, row)) for row in rows]
    for frame, row in zip(frames, decoded):
      self.assertEqual(row["byte7_checksum"], frame[7])
      self.assertEqual(row["request_id"], 11)
      self.assertEqual(row["allocation"], 1)
      self.assertAlmostEqual(row["upper"], -1.25)
      self.assertAlmostEqual(row["lower"], .375)
      self.assertEqual(row["lateral_id"], 11)
      self.assertEqual(row["sequence"], 62)
    self.assertEqual((int(decoded[1]["byte7_checksum"]) - int(decoded[0]["byte7_checksum"])) & 0xFF, 0x40)
    self.assertEqual([row["latch"] for row in decoded], [1, 1, 0])
    self.assertEqual(requests(np.empty((0, 32), dtype=np.uint8)).shape, (0, len(REQUEST_COLUMNS)))

  def test_b6_zero_comparison_population_is_independent_of_checksum(self):
    frames = [payload(False, request_header=0), payload(False, True, request_header=0),
              payload(False, request_header=1)]
    j = {
      "words": np.zeros((3, 14), dtype=np.int32), "v": np.ones(3), "t": np.arange(3),
      "age_gas": np.zeros(3), "gas": np.zeros((3, 4)),
      "age_brake": np.zeros(3), "brake": np.zeros((3, 5)),
      "age_native": np.zeros(3), "age_applied": np.full(3, np.nan), "age_cs": np.zeros(3),
      "native": requests(np.frombuffer(b"".join(frames), dtype=np.uint8).reshape(-1, 32)),
      "applied": np.zeros((3, len(REQUEST_COLUMNS))), "cs": np.zeros((3, len(COLUMNS["cs"]))),
      "cc": np.zeros((3, len(COLUMNS["cc"]))), "result_high_bits": np.zeros(3, dtype=int),
      "result_id": np.zeros(3, dtype=int), "request_loss": np.zeros(3, dtype=int),
      "phase": np.zeros(3, dtype=int), "gas_on": np.zeros(3, dtype=bool), "brake_on": np.zeros(3, dtype=bool),
    }
    row, _, _ = route_report({"route": "fixture", "primary": False, "files": []},
                             {"cp": {}, "errors": []}, {"status_source": 0}, j)
    self.assertEqual(row["b6_zero_native_upper_vs_b20"]["n"], 2)
    np.testing.assert_allclose(row["b6_zero_native_upper_minus_b20_q"], [-1.25, -1.25, -1.25])

  def test_join_preserves_origin_and_latch_phase_after_column_cutover(self):
    first, second = payload(True), payload(False)
    arrays = {key: np.empty((0, len(columns))) for key, columns in COLUMNS.items()}
    arrays.update({
      "status": np.array([[.02, 0, 0], [.04, 0, 0]]),
      "status_bytes": np.zeros((2, 32), dtype=np.uint8),
      "req": np.array([[.01, 0, 0, 1], [.011, 0, 1, 0], [.015, 0, 0, 128],
                       [.03, 0, 0, 1], [.035, 0, 0, 128]]),
      "req_bytes": np.frombuffer(first * 3 + second * 2, dtype=np.uint8).reshape(-1, 32),
      "cs": np.array([[0, 0, 10, 10, -.4, 0, 0, 0, 1, 0, 1, 0]]),
      "cc": np.zeros((1, len(COLUMNS["cc"]))),
    })
    with tempfile.TemporaryDirectory() as directory:
      corpus = Path(directory)
      np.savez(corpus / "fixture.npz", **arrays)
      (corpus / "fixture.json").write_text(json.dumps({"cp": {"openpilotLongitudinalControl": False}}))
      with contextlib.redirect_stdout(io.StringIO()):
        joined = join("fixture", corpus)
      np.testing.assert_array_equal(joined["origin"], [3, 2])
      np.testing.assert_array_equal(joined["phase"], [7, 8])
      np.testing.assert_allclose(joined["applied"][:, :2], [[-1.25, .375], [-1.25, .375]])
      np.testing.assert_array_equal(joined["applied"][:, 3], [first[7], second[7]])
      np.testing.assert_array_equal(joined["native"][:, 5], [1, 0])


if __name__ == "__main__":
  unittest.main()
