#!/usr/bin/env python3
"""Shared raw-CAN helpers for Toyota route -> opendbc evidence extractors."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def be_raw(dat: bytes, start_bit: int, size: int, signed: bool = False) -> int:
    """Decode one Motorola DBC signal using opendbc's bit-numbering convention."""
    be_bits = [j + i * 8 for i in range(len(dat)) for j in range(7, -1, -1)]
    idx = be_bits.index(start_bit)
    bits = be_bits[idx:idx + size]
    value = 0
    for bit in bits:
        byte_i, bit_i = divmod(bit, 8)
        value = (value << 1) | ((dat[byte_i] >> bit_i) & 1)
    if signed and value & (1 << (size - 1)):
        value -= 1 << size
    return value


def toyota_checksum(addr: int, dat: bytes) -> int:
    return (addr + (addr >> 8) + len(dat) + sum(dat[:-1])) & 0xFF


def rate_hz(rows: list[tuple[int, bytes]]) -> float | None:
    if len(rows) < 2:
        return None
    span_s = (rows[-1][0] - rows[0][0]) * 1e-9
    return (len(rows) - 1) / span_s if span_s > 0 else None


def stats(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "unique_count": len(set(values)),
        "min": min(values),
        "max": max(values),
    }
