#!/usr/bin/env python3
"""Portable offline recovery-image checks; no build artifacts or vehicle access."""

from __future__ import annotations

import importlib.util
import io
import json
import struct
import tempfile
import unittest
import zlib
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/targets/camry/analysis/analyze_camry_f33_recovery_image.py"
spec = importlib.util.spec_from_file_location("f33_recovery_image", MODULE_PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RecoveryImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.factory = module.STOCK.read_bytes()

    def changed(self, offset: int, value: int | None = None) -> bytes:
        data = bytearray(self.factory)
        data[offset] = data[offset] ^ 1 if value is None else value
        return bytes(data)

    def test_exact_factory_and_native_geometry(self) -> None:
        result = module.compare_image(self.factory, self.factory)
        self.assertTrue(result["exact_factory_codeflash"])
        self.assertEqual(result["different_bytes"], 0)
        self.assertEqual(
            result["native_upper_region_erase_extent"],
            {"start": 0x18000, "end_exclusive": 0x100000},
        )
        self.assertEqual(
            result["native_crc_input_ranges"],
            [
                {"start": 0x10000, "end_exclusive": 0x17DF0},
                {"start": 0x18000, "end_exclusive": 0xFFDF0},
            ],
        )
        self.assertEqual(
            [v["address"] for v in result["native_counter_words"]], [0x17F00, 0xFFF00]
        )

    def test_retained_lookup_identity_uses_the_actual_0105_backing_object(self) -> None:
        # ROM-selected DID callback and its actual object-read argument/callee.
        self.assertEqual(
            struct.unpack_from("<HHI", self.factory, 0x292BC),
            (0x0105, 12, 0x4D93C),
        )
        self.assertEqual(self.factory[0x4D95C:0x4D964].hex(), "2036040281ff9c94")
        self.assertEqual(self.factory[0x66E1A:0x66E24].hex(), "010600feca0580ffe803")
        # The ROM-object reader consumes +8, not the descriptor's RAM mirror.
        self.assertEqual(
            self.factory[0x6725A:0x6726A].hex(), "21068caf0200c1f1043d7040bfffc8fb"
        )
        length, _, source = struct.unpack_from("<3I", self.factory, 0x2AFBC)
        self.assertEqual((length, source), (16, 0xA0A0))
        self.assertEqual(
            zlib.crc32(self.factory[source : source + length + 4]), 0xFFFFFFFF
        )
        result = module.compare_image(self.factory, self.factory)[
            "retained_factory_calibration_lookup"
        ]
        self.assertEqual(result["ecu_assembly_number"], "8965033K90")
        self.assertEqual(
            result["base_software_numbers"], ["8965F3307000", "8A3113303100"]
        )
        self.assertFalse(result["live_identity_verified"])
        self.assertFalse(result["matching_calibration_package_evaluated"])

    def test_candidate_cannot_replace_archived_lookup_identity(self) -> None:
        # A candidate with altered part text must not redefine the trusted query.
        result = module.compare_image(self.changed(0xA0A4), self.factory)
        self.assertEqual(
            result["retained_factory_calibration_lookup"]["ecu_assembly_number"],
            "8965033K90",
        )
        self.assertFalse(result["exact_factory_codeflash"])

    def test_assembly_identity_corruption_is_not_covered_by_application_crc(
        self,
    ) -> None:
        result = module.compare_image(self.changed(0xA0A4), self.factory)
        self.assertFalse(result["all_differences_within_upper_region_erase_extent"])
        self.assertEqual(result["different_bytes_in_native_crc_inputs"], 0)
        self.assertEqual(result["different_bytes_outside_native_crc_inputs"], 1)

    def test_only_counter_difference_is_not_exact_factory(self) -> None:
        data = bytearray(self.factory)
        struct.pack_into("<I", data, 0xFFF00, 2)
        result = module.compare_image(bytes(data), self.factory)
        self.assertFalse(result["exact_factory_codeflash"])
        self.assertTrue(result["matches_factory_outside_native_counter_words"])
        self.assertFalse(
            result["counter_values_verified_against_live_programming_history"]
        )
        self.assertEqual(result["different_bytes_in_native_counter_words"], 1)

    def test_tail_residue_is_visible_despite_identical_crc_inputs(self) -> None:
        result = module.compare_image(self.changed(0xFFE04), self.factory)
        self.assertFalse(result["matches_factory_outside_native_counter_words"])
        self.assertEqual(result["different_bytes_in_native_crc_inputs"], 0)
        self.assertEqual(result["different_bytes_outside_native_crc_inputs"], 1)
        self.assertTrue(result["all_differences_within_upper_region_erase_extent"])

    def test_no_whole_counter_page_exemption(self) -> None:
        for address in (0x17F04, 0xFFF04, 0xFFFFF):
            with self.subTest(address=hex(address)):
                result = module.compare_image(self.changed(address), self.factory)
                self.assertFalse(result["matches_factory_outside_native_counter_words"])
                self.assertEqual(result["different_bytes_in_native_counter_words"], 0)

    def test_validity_marker_is_never_exempt(self) -> None:
        result = module.compare_image(self.changed(0xFFE00), self.factory)
        self.assertFalse(result["matches_factory_outside_native_counter_words"])
        self.assertEqual(result["different_bytes_outside_native_counter_words"], 1)

    def test_application_difference_is_visible(self) -> None:
        result = module.compare_image(self.changed(0x7A272), self.factory)
        self.assertEqual(result["different_bytes_in_native_crc_inputs"], 1)
        self.assertFalse(result["exact_factory_codeflash"])

    def test_boot_difference_is_outside_upper_erase(self) -> None:
        result = module.compare_image(self.changed(0x13B0), self.factory)
        self.assertFalse(result["all_differences_within_upper_region_erase_extent"])

    def test_candidate_cannot_redefine_counter_exemptions(self) -> None:
        data = bytearray(self.factory)
        struct.pack_into("<I", data, 0x8E2C, 0x7A272)
        data[0x7A272] ^= 1
        result = module.compare_image(bytes(data), self.factory)
        self.assertFalse(result["matches_factory_outside_native_counter_words"])
        self.assertEqual(
            [v["address"] for v in result["native_counter_words"]], [0x17F00, 0xFFF00]
        )

    def test_rejects_truncated_candidate(self) -> None:
        with self.assertRaises(ValueError):
            module.compare_image(self.factory[:-1], self.factory)

    def test_rejects_unreviewed_reference(self) -> None:
        with self.assertRaises(ValueError):
            module.compare_image(self.factory, self.changed(0x20000))

    def test_cli_reports_counter_difference_without_success_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "saved.bin"
            path.write_bytes(self.changed(0xFFF00))
            output = io.StringIO()
            with redirect_stdout(output):
                result = module.main([str(path)])
            self.assertEqual(result, 1)
            report = json.loads(output.getvalue())
            self.assertTrue(report["matches_factory_outside_native_counter_words"])
            self.assertFalse(report["exact_factory_codeflash"])


if __name__ == "__main__":
    unittest.main()
