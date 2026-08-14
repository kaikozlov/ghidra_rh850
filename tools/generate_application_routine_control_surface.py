#!/usr/bin/env python3
"""Generate the firmware-derived application RoutineControl surface.

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

RID_TABLE = 0x26AEC
RID_COUNT = 19
RID = struct.Struct("<HBBI")
POLICY_INDEX_TABLE = 0x26690
POLICY_COUNTS = 0x26420       # per policy: security-count, session-count
POLICY_POINTERS = 0x26678     # per policy: security-list ptr, session-list ptr
CALLBACK_TABLE = 0x25804
CALLBACK = struct.Struct("<HHII")
CONFIG_TABLE = 0x26B8D
CONFIG_STRIDE = 15
SIZE_BITS = 0x263AC

# Config-byte offsets recovered from the RoutineControl control-type support,
# input-length validation, and result-encoding paths.
CONTROL_TYPE_SUPPORTED_OFFSET = {1: 4, 2: 9, 3: 1}
COUNT_OFFSET = {
    "control_type1_input": 6,
    "control_type1_output": 8,
    "control_type2_input": 11,
    "control_type2_output": 13,
    "control_type3_output": 3,
}
DESCRIPTOR_PTR_TABLE = {
    "control_type1_input": 0x2686C,
    "control_type1_output": 0x268BC,
    "control_type2_input": 0x269AC,
    "control_type2_output": 0x269FC,
    "control_type3_output": 0x267CC,
}

# SID 0x31 is configured in default/programming/extended sessions. The
# per-RID policy rows are intersected with this outer service gate below.
ROUTINE_CONTROL_SERVICE_SESSIONS = {1, 2, 3}

SEMANTICS: dict[int, tuple[str, str]] = {
    0x1000: ("capability_query", "control type 1 builds a 32-byte supported-0x10xx RoutineControl bitmap"),
    0x1001: ("capability_bitmap_query", "control type 1 clears/fills a 32-byte RoutineControl support bitmap via 0x4C5AE, marks status complete, and does not start an application state machine"),
    0x1002: ("speed_gated_lifecycle_reinit", "control type 1 is alternate-handoff/speed/busy gated, calls 0x35582 then requests FEBEAF47=0x44; B7E6E normalizes FEBEAF46=0x5A and can invoke B7A36(1) lifecycle-group reinitialization before selector-2 completion"),
    0x1004: ("no_speed_event_history_persistent_rewrite", "fixed payload FFFF; no recovered vehicle-speed gate; type 1 starts/queues operation 5, whose event-log/history initializer forces persistence of checkpoint objects 17/18/19/20/21/23 and selector-3 completion; operation 6 coalesces through the same selector"),
    0x1007: ("live_lifecycle_reinit", "zero-payload control type 1 calls B7A36(0), forcing lifecycle groups FEBEB454/455 to state 0x11; no local speed/mode gate; one-shot per boot via FEBE8157"),
    0x1008: ("live_lifecycle_reinit", "zero-payload control type 1 calls diagnostic-only B7AAE, forcing lifecycle group FEBEB456 to state 0x11; no local speed/mode gate; one-shot per boot via FEBE8158"),
    0x1009: ("state_gated_live_lifecycle_reinit", "zero-payload control type 1 conditionally calls diagnostic-only B55E2, which forces FEBEB2D5 to lifecycle state 0x11; feature byte 0xAEC5D is enabled; start additionally requires FEBEE958==0; control type 3 can clear FEBE8159 when that aggregate-health condition changes"),
    0x100E: ("crypto_test_activation", "control type 1 wrapper 0x8A774 calls crypto_test_bank0_activate @ 0x68F92"),
    0x100F: ("crypto_test_activation", "control type 1 wrapper 0x8A782 calls crypto_test_bank1_activate @ 0x69018"),
    0x1010: ("authenticated_key_update", "control type 1/3 runs ICU-S command 8 SHE-compatible key update; package is authenticated internally"),
    0x1100: ("capability_query", "control type 1 builds a 32-byte supported-0x11xx RoutineControl bitmap"),
    0x1103: ("gated_mode1_service_control", "control type 1 passes runtime eligibility helper 0x354E6 (including vehicle-speed/state gates), sets FEBE6ABA=0x11, and the per-tick 0x352A0 path requests B1F34 internal mode 1 with selector-8 completion"),
    0x1106: ("speed_gated_multigroup_reinit", "control type 1 is speed/busy gated and, when FEBEE958==0, calls B3974 to start lifecycle states FEBEB25A/FEBEB325 plus marker FEBEB48D; B38C0 reports selector-9 success when all three reach 0x44"),
    0x1108: ("no_speed_persistent_checkpoint_reset", "zero-payload control type 1 has no vehicle-speed gate and starts/queues operation 2 via 0x50760; initializer 0x5070C resets/persists checkpoint objects 9/11/12/14/15 and queue monitor 0x50A1C completes selector 10; operation 6 coalesces through 0x4C474"),
    0x1109: ("speed_state_gated_redundant_object0_update", "control type 1 is speed/state gated and calls B7D26(0x22,1); when required, 0x3547E persists redundant namespace-0x100 object 0 and B7CC6/B7C4A resolve selector-11 completion"),
    0x110A: ("service_mode_control", "control type 1 requests internal mode 2; control type 2 terminates; mode maps to system submode 0x520"),
    0x110B: ("no_op_or_status", "action callback is an immediate-success stub; control type 3 exposes status"),
    0x110C: ("service_mode_control", "control type 1 requests internal mode 3; mode maps to system submode 0x520"),
    0x110D: ("service_mode_control", "control type 1 requests internal mode 4; control type 2 terminates; mode maps to system submode 0x520"),
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
        raise ValueError(f"invalid {kind} descriptor pointer for RoutineControl index {index}")
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
    for index in range(RID_COUNT):
        row_addr = RID_TABLE + index * RID.size
        rid, _pad, enabled, policy_ptr = RID.unpack_from(CF, row_addr)
        callback_rid, callback_pad, precondition_cb, action_cb = CALLBACK.unpack_from(
            CF, CALLBACK_TABLE + index * CALLBACK.size
        )
        if callback_rid != rid or callback_pad != 0:
            raise ValueError(
                f"RoutineControl/callback row mismatch at index {index}: {rid:#x}/{callback_rid:#x}"
            )
        policy_index = u16(POLICY_INDEX_TABLE + index * 2)
        security_count, sessions = policy_sessions(policy_index)
        effective_sessions = sorted(set(sessions) & ROUTINE_CONTROL_SERVICE_SESSIONS)
        effect_class, action_summary = SEMANTICS[rid]
        cfg = CONFIG_TABLE + index * CONFIG_STRIDE
        rows.append(
            {
                "table_index": str(index),
                "rid": f"0x{rid:04X}",
                "enabled": str(enabled),
                "policy_index": str(policy_index),
                "security_level_count": str(security_count),
                "policy_sessions": ",".join(map(str, sessions)),
                "effective_routine_control_sessions": ",".join(map(str, effective_sessions)),
                "control_type1_supported": str(CF[cfg + CONTROL_TYPE_SUPPORTED_OFFSET[1]]),
                "control_type2_supported": str(CF[cfg + CONTROL_TYPE_SUPPORTED_OFFSET[2]]),
                "control_type3_supported": str(CF[cfg + CONTROL_TYPE_SUPPORTED_OFFSET[3]]),
                "control_type1_input_bytes": str(descriptor_width(index, "control_type1_input")),
                "control_type1_output_bytes": str(descriptor_width(index, "control_type1_output")),
                "control_type2_input_bytes": str(descriptor_width(index, "control_type2_input")),
                "control_type2_output_bytes": str(descriptor_width(index, "control_type2_output")),
                "control_type3_output_bytes": str(descriptor_width(index, "control_type3_output")),
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
        default=REPO / "data" / "application_routine_control_surface.csv",
    )
    args = parser.parse_args()
    rows = build_rows()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} RoutineControl rows to {args.output}")


if __name__ == "__main__":
    main()
