import unittest
from tools.techstream.native_conversion import convert_scalar


class NativeConversionTests(unittest.TestCase):
    def test_signed_modes(self):
        self.assertEqual(convert_scalar(0x81, 8, 1, 1, 0, 1), -127)
        self.assertEqual(convert_scalar(0x81, 8, 1, 1, 0, 3), -1)
        self.assertEqual(convert_scalar(0x80, 8, 1, 1, 0, 3), 0)
        for mode in (0, 2, 4, 255):
            self.assertEqual(convert_scalar(0x81, 8, 1, 1, 0, mode), 129)

    def test_truncation_and_zero_divisor(self):
        self.assertEqual(convert_scalar(0xFD, 8, 3, 2, 1, 1), -3)
        self.assertEqual(convert_scalar(3, 8, 2, 0, 1, 0), 7)
        self.assertEqual(convert_scalar(3, 8, 2, -2, 1, 0), -2)

    def test_unsigned_input_and_wrapping(self):
        self.assertEqual(convert_scalar(0xFFFFFFFF, 32, 1, 2, 0, 0), 0x7FFFFFFF)
        self.assertEqual(convert_scalar(0x7FFFFFFF, 32, 2, 1, 3, 0), 1)
        self.assertEqual(convert_scalar(0x1FF, 8, 1, 1, 0, 1), -1)
        self.assertEqual(convert_scalar(1, 33, 1, 1, 0, 1), -1)
