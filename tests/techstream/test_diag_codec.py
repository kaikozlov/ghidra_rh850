"""Database compression stays standard, lossless and backward-readable."""
import unittest
import zlib
from unittest.mock import patch

import zstandard

from tools.techstream.diag_codec import ZSTD_MAGIC, compress, decompress


class CodecTests(unittest.TestCase):
    def test_standard_zstd_round_trip(self):
        for raw in (b"", b"{}", b'{"source":"Toyota","value":123}' * 100):
            with self.subTest(size=len(raw)):
                packed = compress(raw)
                self.assertTrue(packed.startswith(ZSTD_MAGIC))
                self.assertEqual(zstandard.ZstdDecompressor().decompress(packed), raw)
                self.assertEqual(decompress(packed), raw)

    def test_writer_rejects_documents_larger_than_reader_limit(self):
        with patch("tools.techstream.diag_codec.MAX_DOCUMENT_BYTES", 4):
            self.assertEqual(decompress(compress(b"1234")), b"1234")
            with self.assertRaisesRegex(ValueError, "semantic document sections"):
                compress(b"12345")

    def test_legacy_zlib_read(self):
        raw = b'{"legacy":true}'
        self.assertEqual(decompress(zlib.compress(raw)), raw)

    def test_corrupt_truncated_and_trailing_frames_rejected(self):
        packed = compress(b'{"data":123456789}')
        broken = bytearray(packed)
        broken[-1] ^= 1
        for data in (bytes(broken), packed[:-1], packed + b"trailing"):
            with self.subTest(data=data), self.assertRaises(zstandard.ZstdError):
                decompress(data)


if __name__ == "__main__":
    unittest.main()
