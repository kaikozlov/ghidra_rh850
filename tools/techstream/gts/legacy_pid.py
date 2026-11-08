"""Offline legacy PID frame decoding using native P3/P4 dataflow.

CommandCommon.dll GetEcuDataP3 10017080 and GetEcuDataP4 100172A0
use native frame 0x6B, patch PID into request byte1, strip framing, then
extract table10 bits. P4 expands compact bytes with the Mode-A8 support
cache through ConvertPid 10060C60 before extracting any bit field.
"""
from __future__ import annotations
from typing import Any

from tools.techstream.gts.legacy_freeze import decode_legacy_scalar


def expand_p4_pid(compact: bytes, support: bytes) -> bytes:
    """Expand one compact PID payload using its native support-cache bytes.

    Each nonzero support byte consumes one received byte; zero inserts zero.
    Support byte bits are not a mask applied to the received value.
    """
    if not compact or len(compact) > len(support) or len(support) > 255:
        raise ValueError("invalid P4 receive/support lengths")
    needed = sum(value != 0 for value in support)
    if needed > len(compact):
        raise ValueError("P4 support map requires more received bytes than available")
    values = iter(compact)
    return bytes(next(values) if mask else 0 for mask in support)


def legacy_pid_request(row: dict[str, Any], frame: bytes) -> bytes:
    """Patch the selected native frame0x6B; caller supplies its resolved bytes."""
    if len(frame) < 2:
        raise ValueError("native PID request needs at least two bytes")
    pid = int(row["pid"])
    if not 0 <= pid <= 255:
        raise ValueError("legacy PID must fit one byte")
    return frame[:1] + bytes([pid]) + frame[2:]


def decode_legacy_pid_response(
    row: dict[str, Any], response: bytes, request: bytes, *,
    protocol: str, support: bytes | None = None,
) -> dict[str, Any]:
    """Decode a successful native response through table10/13/14 metadata.

    Transport response validation and vehicle exception selection precede this
    function. P3 removes the resolved request-length header. P4's native route
    has a two-byte request/response header and requires the live support cache.
    """
    if len(request) < 2 or request[1] != int(row["pid"]):
        raise ValueError("request does not select this monitor PID")
    if protocol == "p3":
        if support is not None:
            raise ValueError("P3 does not use P4 compact support expansion")
        payload = response[len(request):]
    elif protocol == "p4":
        if len(request) != 2:
            raise ValueError("native P4 PID path requires a two-byte frame")
        if support is None:
            raise ValueError("P4 PID decoding requires its live support cache")
        payload = expand_p4_pid(response[2:], support)
    else:
        raise ValueError(f"unsupported legacy PID protocol {protocol!r}")
    return {**decode_legacy_scalar(row, payload), "pid": row["pid"],
            "payload": payload.hex(), "protocol": protocol}
