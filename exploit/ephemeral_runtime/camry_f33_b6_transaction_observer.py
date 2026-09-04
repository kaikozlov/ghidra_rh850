"""Pure layout/decoder contract for the exact-F33 B6 transaction observer."""
from __future__ import annotations

from typing import Any

TELEMETRY_BASE = 0xFEBFFBE0
TELEMETRY_SIZE = 28
HEARTBEAT_INITIAL = 0x4F364236

TELEMETRY_FIELDS = (
    {"name": "heartbeat", "offset": 0, "length": 4, "kind": "u32"},
    {"name": "queue_samples", "offset": 4, "length": 1, "kind": "u8_mod256"},
    {"name": "d7_queue_samples", "offset": 5, "length": 1, "kind": "u8_mod256"},
    {"name": "pre_profile_state", "offset": 8, "length": 1, "kind": "u8"},
    {"name": "post_profile_state", "offset": 9, "length": 1, "kind": "u8"},
    {"name": "post_queue_length", "offset": 10, "length": 2, "kind": "u16"},
    {"name": "post_secoc_result", "offset": 12, "length": 1, "kind": "u8"},
    {"name": "b6_b3_b7", "offset": 16, "length": 5, "kind": "bytes"},
    {"name": "b6_b28_b31", "offset": 24, "length": 4, "kind": "bytes"},
)


def decode_telemetry(raw: bytes) -> dict[str, Any]:
    if len(raw) != TELEMETRY_SIZE:
        raise ValueError(f"observer telemetry returned {len(raw)} bytes; expected {TELEMETRY_SIZE}")
    queue_samples = raw[4]
    queue_seen = queue_samples != 0
    wire = raw[16:21]
    trailer = raw[24:28]
    return {
        "heartbeat": int.from_bytes(raw[0:4], "little"),
        "queue_samples": queue_samples,
        "d7_queue_samples": raw[5],
        "pre_profile_state": raw[8],
        "post_profile_state": raw[9],
        "post_queue_length": int.from_bytes(raw[10:12], "little") if queue_seen else None,
        "post_secoc_result": raw[12] if queue_seen else None,
        "b6_target_id": (wire[0] & 0x3F) if queue_seen else None,
        "b6_target_raw": int.from_bytes(wire[1:3], "big", signed=True) if queue_seen else None,
        "b6_companion": wire[3] if queue_seen else None,
        "b6_sequence": (wire[4] & 0x3F) if queue_seen else None,
        "b6_fv4": (trailer[0] >> 4) if queue_seen else None,
        "b6_mac28": (int.from_bytes(trailer, "big") & 0x0FFFFFFF) if queue_seen else None,
        "raw": raw.hex(),
    }
