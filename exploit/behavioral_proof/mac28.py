#!/usr/bin/env python3
"""Pure helpers for the Toyota SecOC MAC28-only behavioral ablation."""

from __future__ import annotations

from dataclasses import dataclass

MAC28_IDS = frozenset((0x2E4, 0x131))
STOCK_CAMERA_PROOF_IDS = frozenset((0x191, 0x412, 0x2E4, 0x131))


class Mac28Error(ValueError):
    pass


@dataclass(frozen=True)
class CanFrame:
    address: int
    bus: int
    data: bytes
    timestamp_ns: int | None = None


def invalidate_mac28(data: bytes) -> bytes:
    """Zero exactly MAC28: byte4 low nibble plus bytes5..7.

    The byte4 high nibble is deliberately preserved because it is outside the
    28-bit authenticator and may contain freshness/counter state.
    """
    if len(data) != 8:
        raise Mac28Error(f"MAC28 proof expects an 8-byte SecOC frame, got {len(data)}")
    out = bytearray(data)
    out[4] &= 0xF0
    out[5] = 0
    out[6] = 0
    out[7] = 0
    return bytes(out)


def expected_forward(address: int, source: bytes, *, mode: str = "invalid-mac28") -> bytes:
    if address not in STOCK_CAMERA_PROOF_IDS:
        raise Mac28Error(f"0x{address:X} is outside the bounded proof message set")
    if len(source) != 8:
        raise Mac28Error("bounded proof messages must be exactly 8 bytes")
    if mode not in ("stock", "invalid-mac28"):
        raise Mac28Error(f"unsupported forwarding mode: {mode}")
    if mode == "stock":
        return source
    return invalidate_mac28(source) if address in MAC28_IDS else source


def changed_bit_positions(before: bytes, after: bytes) -> set[int]:
    if len(before) != len(after):
        raise Mac28Error("cannot compare frames with different lengths")
    changed: set[int] = set()
    for byte_index, (lhs, rhs) in enumerate(zip(before, after)):
        delta = lhs ^ rhs
        for bit in range(8):
            if delta & (1 << bit):
                changed.add(byte_index * 8 + bit)
    return changed


def validate_forward_pair(
    address: int,
    source: bytes,
    forwarded: bytes,
    *,
    mode: str = "invalid-mac28",
) -> list[str]:
    errors: list[str] = []
    try:
        expected = expected_forward(address, source, mode=mode)
    except Mac28Error as exc:
        return [str(exc)]
    if forwarded != expected:
        errors.append(
            f"0x{address:X}: forwarded bytes differ from bounded expectation: "
            f"source={source.hex()} expected={expected.hex()} observed={forwarded.hex()}"
        )
    if mode == "invalid-mac28" and address in MAC28_IDS:
        if (forwarded[4] & 0xF0) != (source[4] & 0xF0):
            errors.append(f"0x{address:X}: byte4 high nibble/freshness was modified")
        if (forwarded[4] & 0x0F) != 0 or forwarded[5:8] != b"\x00\x00\x00":
            errors.append(f"0x{address:X}: MAC28 is not exactly zero")
        allowed_changed_bits = set(range(32, 36)) | set(range(40, 64))
        unexpected = changed_bit_positions(source, forwarded) - allowed_changed_bits
        if unexpected:
            errors.append(f"0x{address:X}: bits outside MAC28 changed: {sorted(unexpected)}")
    return errors
