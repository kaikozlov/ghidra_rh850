"""Standard compression for diagnostic database JSON, with legacy reads."""
import zlib

import zstandard

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
MAX_DOCUMENT_BYTES = 64 * 1024 * 1024


def compress(raw: bytes) -> bytes:
    """Encode one independently readable standard Zstandard frame."""
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise ValueError(f"diagnostic document exceeds {MAX_DOCUMENT_BYTES} decoded bytes; "
                         "split it into semantic document sections")
    return zstandard.ZstdCompressor(level=9, write_checksum=True).compress(raw)


def decompress(packed: bytes) -> bytes:
    """Read new Zstandard frames and earlier zlib database records."""
    if packed.startswith(ZSTD_MAGIC):
        return zstandard.ZstdDecompressor().decompress(packed, allow_extra_data=False)
    return zlib.decompress(packed)
