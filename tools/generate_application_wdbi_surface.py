#!/usr/bin/env python3
"""Generate the firmware-derived application WriteDataByIdentifier surface.

The raw access-control, selector, descriptor-width, and callback columns are
parsed directly from the committed Sienna CodeFlash image. ``effect_class`` and
``action_summary`` are deliberately small semantic overlays for callbacks whose
behavior has been recovered; they are not OEM names.
"""
from __future__ import annotations

import argparse
import csv
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

WRITE_DID_TABLE = 0x26AEC
WRITE_DID_COUNT = 19
WRITE_DID = struct.Struct("<HBBI")
POLICY_INDEX_TABLE = 0x26690
POLICY_COUNTS = 0x26420       # per policy: security-count, session-count
POLICY_POINTERS = 0x26678     # per policy: security-list ptr, session-list ptr
CALLBACK_TABLE = 0x25804
CALLBACK = struct.Struct("<HHII")
CONFIG_TABLE = 0x26B8D
CONFIG_STRIDE = 15
SIZE_BITS = 0x263AC

# Config-byte offsets recovered from application_wdbi_selector_supported,
# application_wdbi_input_length_invalid, and FUN_00095966.
SELECTOR_SUPPORTED_OFFSET = {1: 4, 2: 9, 3: 1}
COUNT_OFFSET = {
    "selector1_input": 6,
    "selector1_output": 8,
    "selector2_input": 11,
    "selector2_output": 13,
    "selector3_output": 3,
}
DESCRIPTOR_PTR_TABLE = {
    "selector1_input": 0x2686C,
    "selector1_output": 0x268BC,
    "selector2_input": 0x269AC,
    "selector2_output": 0x269FC,
    "selector3_output": 0x267CC,
}

# SID 0x2E itself is configured for programming + extended session. The
# per-DID policy rows are intersected with this outer service gate below.
WDBI_SERVICE_SESSIONS = {2, 3}

SEMANTICS: dict[int, tuple[str, str]] = {
    0x1000: ("capability_query", "selector 1 builds a 32-byte supported-0x10xx WDBI bitmap"),
    0x1001: ("query_or_control", "selector 1 returns a 32-byte callback result; deeper OEM meaning unassigned"),
    0x1002: ("stateful_control", "selector 1 reaches FUN_00035582 then thunk_B7F7C(0x44); runtime preconditions apply"),
    0x1004: ("fixed_maintenance_trigger", "selector 1 requires fixed input FFFF then queues internal operation 5; tester value is not consumed by the action"),
    0x1007: ("live_lifecycle_reinit", "zero-payload selector 1 calls B7A36(0), forcing lifecycle groups FEBEB454/455 to state 0x11; no local speed/mode gate; one-shot per boot via FEBE8157"),
    0x1008: ("live_lifecycle_reinit", "zero-payload selector 1 calls diagnostic-only B7AAE, forcing lifecycle group FEBEB456 to state 0x11; no local speed/mode gate; one-shot per boot via FEBE8158"),
    0x1009: ("state_gated_live_lifecycle_reinit", "zero-payload selector 1 conditionally calls diagnostic-only B55E2, which forces FEBEB2D5 to lifecycle state 0x11; feature byte 0xAEC5D is enabled; start additionally requires FEBEE958==0; selector 3 can clear FEBE8159 when that aggregate-health condition changes"),
    0x100E: ("crypto_test_activation", "selector 1 wrapper 0x8A774 calls crypto_test_bank0_activate @ 0x68F92"),
    0x100F: ("crypto_test_activation", "selector 1 wrapper 0x8A782 calls crypto_test_bank1_activate @ 0x69018"),
    0x1010: ("authenticated_key_update", "selector 1/3 runs ICU-S command 8 SHE-compatible key update; package is authenticated internally"),
    0x1100: ("capability_query", "selector 1 builds a 32-byte supported-0x11xx WDBI bitmap"),
    0x1103: ("stateful_control", "selector 1 reaches FUN_00035576; deeper OEM meaning unassigned"),
    0x1106: ("stateful_control", "selector 1 reaches thunk_B3974; runtime preconditions apply"),
    0x1108: ("stateful_control", "selector 1 reaches FUN_00050760; deeper OEM meaning unassigned"),
    0x1109: ("stateful_control", "selector 1 reaches thunk_B7D26(0x22,1); runtime preconditions apply"),
    0x110A: ("service_mode_control", "selector 1 requests internal mode 2; selector 2 terminates; mode maps to system submode 0x520"),
    0x110B: ("no_op_or_status", "action callback is an immediate-success stub; selector 3 exposes status"),
    0x110C: ("service_mode_control", "selector 1 requests internal mode 3; mode maps to system submode 0x520"),
    0x110D: ("service_mode_control", "selector 1 requests internal mode 4; selector 2 terminates; mode maps to system submode 0x520"),
}


def u16(offset: int) -> int:
    return struct.unpack_from("<H", CF, offset)[0]


def u32(offset: int) -> int:
    return struct.unpack_from("<I", CF, offset)[0]


def descriptor_width(index: int, kind: str) -> int:
    """Return payload/output byte width from the last configured bit descriptor."""
    count = CF[CONFIG_TABLE + index * CONFIG_STRIDE + COUNT_OFFSET[kind]]
    if count == 0:
        return 0
    descriptor_base = u32(DESCRIPTOR_PTR_TABLE[kind] + index * 4)
    if descriptor_base == 0 or descriptor_base >= len(CF):
        raise ValueError(f"invalid {kind} descriptor pointer for WDBI index {index}")
    desc = descriptor_base + (count - 1) * 6
    field_type = CF[desc + 1]
    bit_offset = u16(desc + 4)
    if field_type == 7:
        field_bits = u16(desc + 2)
    else:
        field_bits = CF[SIZE_BITS + field_type]
    return (field_bits + bit_offset + 7) // 8


def policy_sessions(policy_index: int) -> tuple[int, list[int]]:
    security_count = CF[POLICY_COUNTS + policy_index * 2]
    session_count = CF[POLICY_COUNTS + policy_index * 2 + 1]
    _security_ptr, session_ptr = struct.unpack_from(
        "<II", CF, POLICY_POINTERS + policy_index * 8
    )
    sessions: list[int] = []
    for j in range(session_count):
        record = u32(session_ptr + j * 4)
        if not 0 < record < len(CF) - 1:
            raise ValueError(f"invalid policy {policy_index} session record {record:#x}")
        sessions.append(CF[record + 1])
    return security_count, sessions


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index in range(WRITE_DID_COUNT):
        row_addr = WRITE_DID_TABLE + index * WRITE_DID.size
        did, _pad, enabled, policy_ptr = WRITE_DID.unpack_from(CF, row_addr)
        callback_did, callback_pad, precondition_cb, action_cb = CALLBACK.unpack_from(
            CF, CALLBACK_TABLE + index * CALLBACK.size
        )
        if callback_did != did or callback_pad != 0:
            raise ValueError(
                f"WDBI/callback row mismatch at index {index}: {did:#x}/{callback_did:#x}"
            )
        policy_index = u16(POLICY_INDEX_TABLE + index * 2)
        security_count, sessions = policy_sessions(policy_index)
        effective_sessions = sorted(set(sessions) & WDBI_SERVICE_SESSIONS)
        effect_class, action_summary = SEMANTICS[did]
        cfg = CONFIG_TABLE + index * CONFIG_STRIDE
        rows.append(
            {
                "table_index": str(index),
                "did": f"0x{did:04X}",
                "enabled": str(enabled),
                "policy_index": str(policy_index),
                "security_level_count": str(security_count),
                "policy_sessions": ",".join(map(str, sessions)),
                "effective_wdbi_sessions": ",".join(map(str, effective_sessions)),
                "selector1_supported": str(CF[cfg + SELECTOR_SUPPORTED_OFFSET[1]]),
                "selector2_supported": str(CF[cfg + SELECTOR_SUPPORTED_OFFSET[2]]),
                "selector3_supported": str(CF[cfg + SELECTOR_SUPPORTED_OFFSET[3]]),
                "selector1_input_bytes": str(descriptor_width(index, "selector1_input")),
                "selector1_output_bytes": str(descriptor_width(index, "selector1_output")),
                "selector2_input_bytes": str(descriptor_width(index, "selector2_input")),
                "selector2_output_bytes": str(descriptor_width(index, "selector2_output")),
                "selector3_output_bytes": str(descriptor_width(index, "selector3_output")),
                "policy_record_ptr": f"0x{policy_ptr:X}",
                "precondition_callback": f"0x{precondition_cb:X}" if precondition_cb else "",
                "action_callback": f"0x{action_cb:X}" if action_cb else "",
                "effect_class": effect_class,
                "action_summary": action_summary,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o", "--output", type=Path,
        default=REPO / "data" / "application_wdbi_surface.csv",
    )
    args = parser.parse_args()
    rows = build_rows()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} WDBI rows to {args.output}")


if __name__ == "__main__":
    main()
