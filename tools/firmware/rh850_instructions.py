"""Small RH850 instruction readers for zero-based binary images."""
from __future__ import annotations

import struct


def is_jarl22(image: bytes, off: int) -> bool:
    """Return whether the image contains a complete JARL disp22,lp at off."""
    if off < 0 or off + 4 > len(image):
        return False
    first, second = struct.unpack_from("<HH", image, off)
    # v850_func.sinc selects op0610 and lp; addr22 requires op1616=0.
    return first & 0xFFC0 == 0xFF80 and second & 1 == 0


def jarl22_target(image: bytes, off: int) -> int:
    """Decode a JARL disp22,lp destination; reject other or incomplete encodings."""
    if not is_jarl22(image, off):
        raise ValueError(f"not a direct JARL disp22 at {off:#x}")
    first, second = struct.unpack_from("<HH", image, off)
    displacement = ((first & 0x3F) << 16) | second
    if displacement & 0x200000:
        displacement -= 0x400000
    return (off + displacement) & 0xFFFFFFFF
