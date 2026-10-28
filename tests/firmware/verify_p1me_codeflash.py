#!/usr/bin/env python3
"""Check CodeFlash input geometry without firmware images or build tools."""
from __future__ import annotations

import unittest

from tools.firmware.p1me_codeflash import (
    CONCATENATED_DUMP_SIZE,
    P1M_E_CODEFLASH_SIZE,
    P1M_E_DATAFLASH_PREFIX_SIZE,
    validate_codeflash_geometry,
)


class CodeFlashGeometryTests(unittest.TestCase):
    def test_bare_user_area(self) -> None:
        self.assertEqual(P1M_E_CODEFLASH_SIZE, 0x100000)
        self.assertIsNone(validate_codeflash_geometry(P1M_E_CODEFLASH_SIZE))

    def test_negative_size(self) -> None:
        with self.assertRaisesRegex(ValueError, "image size must not be negative"):
            validate_codeflash_geometry(-1)

    def test_truncated_and_oversized_images(self) -> None:
        for size in (0, 0x8000, 0x80000, 0xFFFFF, 0x100001, 0x100008, 0x200000):
            with self.subTest(size=size):
                with self.assertRaisesRegex(ValueError, "expected exactly"):
                    validate_codeflash_geometry(size)

    def test_concatenated_dump_diagnosis(self) -> None:
        self.assertEqual(P1M_E_DATAFLASH_PREFIX_SIZE, 0x8000)
        self.assertEqual(CONCATENATED_DUMP_SIZE, 0x108000)
        with self.assertRaises(ValueError) as caught:
            validate_codeflash_geometry(CONCATENATED_DUMP_SIZE)
        message = str(caught.exception)
        self.assertIn("DataFlash+CodeFlash concatenated", message)
        self.assertIn("strip the leading 0x8000 DataFlash bytes", message)
        self.assertIn("bare 0x100000-byte CodeFlash image", message)


if __name__ == "__main__":
    unittest.main()
