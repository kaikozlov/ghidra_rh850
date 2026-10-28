#!/usr/bin/env python3
"""Verify generic RH850 instruction readers using synthetic bytes."""
from __future__ import annotations

import struct
import unittest

from tools.firmware.rh850_instructions import is_jarl22, jarl22_target


class Jarl22Tests(unittest.TestCase):
    def test_signed_displacements_and_pc_relative_target(self) -> None:
        vectors = (
            ("80ff0000", 0),
            ("80ff0200", 2),
            ("80fffeff", 0xFFFE),
            ("81ff0000", 0x10000),
            ("9ffffeff", 0x1FFFFE),
            ("a0ff0000", -0x200000),
            ("bfff0000", -0x10000),
            ("bffffeff", -2),
        )
        for encoded, displacement in vectors:
            for offset in (0, 2, 8):
                with self.subTest(encoded=encoded, offset=offset):
                    image = bytes(offset) + bytes.fromhex(encoded)
                    self.assertTrue(is_jarl22(image, offset))
                    self.assertEqual(
                        jarl22_target(image, offset),
                        (offset + displacement) & 0xFFFFFFFF,
                    )

    def test_opcode_and_link_register(self) -> None:
        # Every possible first halfword, with a valid even displacement tail.
        for first in range(0x10000):
            image = struct.pack("<HH", first, 0x20)
            expected = first in range(0xFF80, 0xFFC0)
            self.assertEqual(is_jarl22(image, 0), expected, f"{first:#06x}")

    def test_rejects_second_halfword_low_bit(self) -> None:
        for first in range(0xFF80, 0xFFC0):
            for second in (1, 0x21, 0xFFFF):
                with self.subTest(first=first, second=second):
                    image = struct.pack("<HH", first, second)
                    self.assertFalse(is_jarl22(image, 0))
                    with self.assertRaises(ValueError):
                        jarl22_target(image, 0)

    def test_rejects_wrong_opcode_or_link_register(self) -> None:
        for encoded in ("00000000", "80072000", "80f72000", "40ff2000"):
            with self.subTest(encoded=encoded):
                image = bytes.fromhex(encoded)
                self.assertFalse(is_jarl22(image, 0))
                with self.assertRaises(ValueError):
                    jarl22_target(image, 0)

    def test_bounds_and_truncation(self) -> None:
        instruction = bytes.fromhex("80ff2000")
        for image, offset in (
            *((instruction[:size], 0) for size in range(4)),
            (instruction, -1),
            (instruction, 1),
            (instruction, 4),
            (instruction, 100),
        ):
            with self.subTest(image=image.hex(), offset=offset):
                self.assertFalse(is_jarl22(image, offset))
                with self.assertRaises(ValueError):
                    jarl22_target(image, offset)


if __name__ == "__main__":
    unittest.main()
