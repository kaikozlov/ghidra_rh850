#!/usr/bin/env python3
"""AUTOSAR E2E Profile 5 helpers for Toyota native CAN-FD PDUs.

The Camry Bus-1 family recovered in VAR-107 uses the standard Profile-5 shape:
CRC-16/CCITT polynomial 0x1021, initial value 0xFFFF, 16-bit little-endian CRC,
8-bit counter at offset+2, and an implicit 16-bit Data ID appended low byte then
high byte to the CRC input.  On the retained Camry family the Data ID equals the
CAN identifier.
"""
from __future__ import annotations

CRC16_POLY = 0x1021
CRC16_INIT = 0xFFFF


def _build_crc16_table() -> tuple[int, ...]:
    out = []
    for byte in range(256):
        crc = byte << 8
        for _ in range(8):
            crc = ((crc << 1) & 0xFFFF) ^ (CRC16_POLY if crc & 0x8000 else 0)
        out.append(crc)
    return tuple(out)


_CRC16_TABLE = _build_crc16_table()


def crc16_update_byte(crc: int, byte: int) -> int:
    """Advance non-reflected CRC-16/CCITT by one byte."""
    if not 0 <= crc <= 0xFFFF:
        raise ValueError(f"CRC state must be in [0, 0xffff], got {crc}")
    if not 0 <= byte <= 0xFF:
        raise ValueError(f"CRC byte must be in [0, 0xff], got {byte}")
    return ((crc << 8) & 0xFFFF) ^ _CRC16_TABLE[((crc >> 8) ^ byte) & 0xFF]


def crc16_reverse_byte(crc: int, byte: int) -> int:
    """Reverse one known input byte of the non-reflected CRC-16/CCITT state."""
    if not 0 <= crc <= 0xFFFF:
        raise ValueError(f"CRC state must be in [0, 0xffff], got {crc}")
    if not 0 <= byte <= 0xFF:
        raise ValueError(f"CRC byte must be in [0, 0xff], got {byte}")
    state = crc
    for _ in range(8):
        old_msb = state & 1
        state ^= CRC16_POLY if old_msb else 0
        state = (state >> 1) | (old_msb << 15)
    return state ^ (byte << 8)


def crc16_ccitt(data: bytes, start: int = CRC16_INIT) -> int:
    """AUTOSAR Crc_CalculateCRC16-compatible non-reflected CRC-16/CCITT."""
    if not 0 <= start <= 0xFFFF:
        raise ValueError(f"CRC start must be in [0, 0xffff], got {start}")
    crc = start
    for byte in data:
        crc = crc16_update_byte(crc, byte)
    return crc


def _e2e_p05_payload_state(data: bytes, *, offset: int = 0) -> int:
    if not 0 <= offset <= len(data) - 3:
        raise ValueError(f"Profile-5 CRC offset {offset} invalid for {len(data)}-byte buffer")
    crc = CRC16_INIT
    if offset:
        crc = crc16_ccitt(data[:offset], crc)
    return crc16_ccitt(data[offset + 2 :], crc)


def e2e_p05_crc(data: bytes, data_id: int, *, offset: int = 0) -> int:
    """Compute the AUTOSAR E2E Profile-5 CRC for one protected data buffer.

    ``data`` is the complete transmitted payload including the two CRC bytes.
    The CRC bytes at ``offset`` and ``offset+1`` are skipped, all other bytes
    are processed in wire order, then the implicit 16-bit Data ID is processed
    low byte followed by high byte.
    """
    if not 0 <= data_id <= 0xFFFF:
        raise ValueError(f"Data ID must be in [0, 0xffff], got {data_id}")
    crc = _e2e_p05_payload_state(data, offset=offset)
    crc = crc16_update_byte(crc, data_id & 0xFF)
    return crc16_update_byte(crc, (data_id >> 8) & 0xFF)


def e2e_p05_recover_data_id(data: bytes, *, offset: int = 0) -> int:
    """Recover the unique implicit 16-bit Profile-5 Data ID from one valid wire image.

    The two appended Data-ID bytes form a bijective 16-bit transform for a fixed
    payload CRC state, so the low/high bytes can be recovered with two 256-entry
    one-byte searches rather than assuming a configured identifier.
    """
    if not 0 <= offset <= len(data) - 3:
        raise ValueError(f"Profile-5 CRC offset {offset} invalid for {len(data)}-byte buffer")
    target = int.from_bytes(data[offset : offset + 2], "little")
    payload_state = _e2e_p05_payload_state(data, offset=offset)
    after_low = {crc16_update_byte(payload_state, low): low for low in range(256)}
    matches = []
    for high in range(256):
        before_high = crc16_reverse_byte(target, high)
        if before_high in after_low:
            matches.append(after_low[before_high] | (high << 8))
    if len(matches) != 1:
        raise ValueError(f"expected one Profile-5 Data ID candidate, recovered {len(matches)}")
    return matches[0]


def e2e_p05_check(data: bytes, data_id: int, *, offset: int = 0) -> bool:
    """Return whether the transmitted little-endian Profile-5 CRC is valid."""
    if not 0 <= offset <= len(data) - 3:
        return False
    stored = int.from_bytes(data[offset : offset + 2], "little")
    return stored == e2e_p05_crc(data, data_id, offset=offset)


def e2e_p05_protect(data: bytes, data_id: int, *, offset: int = 0) -> bytes:
    """Return ``data`` with its Profile-5 CRC bytes recomputed in place."""
    out = bytearray(data)
    crc = e2e_p05_crc(out, data_id, offset=offset)
    out[offset : offset + 2] = crc.to_bytes(2, "little")
    return bytes(out)
