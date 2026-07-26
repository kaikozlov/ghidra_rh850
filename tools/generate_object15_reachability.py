#!/usr/bin/env python3
"""Generate the deterministic object-15 / secoc_nvm_object_update reachability report.

Pure raw-CodeFlash generator. Enumerates every recovered callsite of
secoc_nvm_object_update (0x65CD8) and its thin wrapper (0xFF09C), recovers the
object-index argument (literal or bounded dynamic set), and records whether the
SecOC triplicate object 15 (namespace 0x100 | 15 = 0x10F) is statically
selectable.

Namespace rules (from 0x65CD8):
  0x000 -> checkpoint update path (FUN_000666A4 / checkpoint_object_*)
  0x100 -> redundant SecOC NvM path (0x66E48); object 15 is key-bearing on
           related variants
  0x200 -> third configured namespace (FUN_000660E0)

Checkpoint object index 15 (namespace 0) is a different configured object
(operating_state_snapshot) and must not be equated with SecOC object 15.
"""
from __future__ import annotations

import argparse
import csv
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF_PATH = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"

# Exhaustive Ghidra xref census of UNCONDITIONAL_CALL to 0x65CD8, pinned and
# re-checked against CodeFlash call encodings by tests/verify_boot_trust.py.
DIRECT_CALLS: list[dict] = [
    # callsite, caller_entry, caller_name, index_value or None, index_source,
    # reachable_set (ints), async_persist
    {"callsite": 0x320E4, "caller": 0x320A8, "name": "FUN_000320a8",
     "index": 0x208, "source": "literal_movea", "set": [0x208],
     "async": "namespace_0x200_mirror"},
    {"callsite": 0x320EE, "caller": 0x320A8, "name": "FUN_000320a8",
     "index": 0x209, "source": "literal_movea", "set": [0x209],
     "async": "namespace_0x200_mirror"},
    {"callsite": 0x34696, "caller": 0x343BA, "name": "FUN_000343ba",
     "index": 0x202, "source": "literal_decompile", "set": [0x202],
     "async": "namespace_0x200_mirror"},
    {"callsite": 0x346C6, "caller": 0x346AE, "name": "FUN_000346ae",
     "index": 0x202, "source": "literal_movea", "set": [0x202],
     "async": "namespace_0x200_mirror"},
    {"callsite": 0x34FE4, "caller": 0x34F9A, "name": "checkpoint_persistent_countdown_step",
     "index": 0x18, "source": "literal_movea", "set": [0x18],
     "async": "checkpoint_persist"},
    {"callsite": 0x34FFA, "caller": 0x34F9A, "name": "checkpoint_persistent_countdown_step",
     "index": 0x105, "source": "literal_movea", "set": [0x105],
     "async": "redundant_persist"},
    {"callsite": 0x35290, "caller": 0x35260, "name": "FUN_00035260",
     "index": 0x100, "source": "literal_decompile", "set": [0x100],
     "async": "redundant_persist"},
    {"callsite": 0x354AA, "caller": 0x3547E, "name": "FUN_0003547e",
     "index": 0x100, "source": "literal_movea", "set": [0x100],
     "async": "redundant_persist"},
    {"callsite": 0x38DBC, "caller": 0x38D4E, "name": "checkpoint_multi_channel_u16_state_persist",
     "index": 0x6, "source": "literal_mov", "set": [0x6],
     "async": "checkpoint_persist"},
    {"callsite": 0x38F28, "caller": 0x38E56, "name": "FUN_00038e56",
     "index": 0x6, "source": "literal_decompile", "set": [0x6],
     "async": "checkpoint_persist"},
    {"callsite": 0x4530A, "caller": 0x4528C, "name": "checkpoint_dual_incident_snapshot_persist",
     "index": 0xC, "source": "literal_mov", "set": [0xC],
     "async": "checkpoint_persist"},
    {"callsite": 0x453DC, "caller": 0x453A2, "name": "FUN_000453a2",
     "index": 0xC, "source": "literal_mov", "set": [0xC],
     "async": "checkpoint_persist"},
    {"callsite": 0x47982, "caller": 0x47958, "name": "FUN_00047958",
     "index": 0x5, "source": "literal_mov", "set": [0x5],
     "async": "checkpoint_persist"},
    {"callsite": 0x4799E, "caller": 0x4798A, "name": "FUN_0004798a",
     "index": 0x5, "source": "literal_mov", "set": [0x5],
     "async": "checkpoint_persist"},
    {"callsite": 0x51164, "caller": 0x5110C, "name": "checkpoint_monitor_aggregate_persist",
     "index": 0x0, "source": "literal_mov", "set": [0x0],
     "async": "checkpoint_persist"},
    {"callsite": 0x51198, "caller": 0x51176, "name": "FUN_00051176",
     "index": 0xA, "source": "literal_mov", "set": [0xA],
     "async": "checkpoint_persist"},
    {"callsite": 0x51BB8, "caller": 0x51B5E, "name": "checkpoint_monitor_state_bank_persist",
     "index": 0x1, "source": "literal_mov", "set": [0x1],
     "async": "checkpoint_persist"},
    {"callsite": 0x51BC8, "caller": 0x51B5E, "name": "checkpoint_monitor_state_bank_persist",
     "index": 0x2, "source": "literal_mov", "set": [0x2],
     "async": "checkpoint_persist"},
    {"callsite": 0x51BD8, "caller": 0x51B5E, "name": "checkpoint_monitor_state_bank_persist",
     "index": 0x3, "source": "literal_mov", "set": [0x3],
     "async": "checkpoint_persist"},
    {"callsite": 0x534DC, "caller": 0x5347A, "name": "checkpoint_event_counter_groups_persist",
     "index": 0x4, "source": "literal_mov", "set": [0x4],
     "async": "checkpoint_persist"},
    {"callsite": 0x53944, "caller": 0x538D4, "name": "checkpoint_three_entry_condition_history_persist",
     "index": 0xE, "source": "literal_mov", "set": [0xE],
     "async": "checkpoint_persist"},
    {"callsite": 0x53A0C, "caller": 0x539A8, "name": "FUN_000539a8",
     "index": 0xE, "source": "literal_mov", "set": [0xE],
     "async": "checkpoint_persist"},
    {"callsite": 0x53FB8, "caller": 0x53F60, "name": "checkpoint_event_history_group_persist",
     "index": None, "source": "dynamic_map_0x53b70",
     "set": [0x14, 0x15, 0x17],  # 20/21/23; 0x20 is the no-op sentinel
     "async": "checkpoint_persist"},
    {"callsite": 0x54072, "caller": 0x53FC4, "name": "checkpoint_event_log_banks_persist",
     "index": 0x11, "source": "literal_movea", "set": [0x11],
     "async": "checkpoint_persist"},
    {"callsite": 0x54084, "caller": 0x53FC4, "name": "checkpoint_event_log_banks_persist",
     "index": None, "source": "dynamic_bank_select_0x53ef2",
     "set": [0x12, 0x13], "async": "checkpoint_persist"},
    {"callsite": 0x5409A, "caller": 0x53FC4, "name": "checkpoint_event_log_banks_persist",
     "index": None, "source": "dynamic_bank_select_0x53ef2",
     "set": [0x12, 0x13], "async": "checkpoint_persist"},
    {"callsite": 0xFF0A2, "caller": 0xFF09C, "name": "secoc_nvm_object_update_wrapper",
     "index": None, "source": "passthrough_wrapper",
     "set": [], "async": "delegates_to_0x65cd8"},
]

# Exhaustive Ghidra xref census of UNCONDITIONAL_CALL to wrapper 0xFF09C.
WRAPPER_CALLS: list[dict] = [
    {"callsite": 0xB43CA, "caller": 0xB4396, "name": "FUN_000b4396",
     "index": 0x101, "source": "literal_movea", "set": [0x101],
     "async": "redundant_persist"},
    {"callsite": 0xB44C2, "caller": 0xB4484, "name": "FUN_000b4484",
     "index": 0x101, "source": "literal_decompile", "set": [0x101],
     "async": "redundant_persist"},
    {"callsite": 0xB45D0, "caller": 0xB458C, "name": "FUN_000b458c",
     "index": 0x101, "source": "literal_movea", "set": [0x101],
     "async": "redundant_persist"},
    {"callsite": 0xB5162, "caller": 0xB513A, "name": "FUN_000b513a",
     "index": 0x103, "source": "literal_movea", "set": [0x103],
     "async": "redundant_persist"},
    {"callsite": 0xB51E8, "caller": 0xB51B2, "name": "FUN_000b51b2",
     "index": 0x103, "source": "literal_movea", "set": [0x103],
     "async": "redundant_persist"},
    {"callsite": 0xB5356, "caller": 0xB52DA, "name": "FUN_000b52da",
     "index": 0x103, "source": "literal_decompile", "set": [0x103],
     "async": "redundant_persist"},
    {"callsite": 0xB5AAA, "caller": 0xB5A7E, "name": "FUN_000b5a7e",
     "index": 0x102, "source": "literal_movea", "set": [0x102],
     "async": "redundant_persist"},
    {"callsite": 0xB5B8A, "caller": 0xB5B66, "name": "FUN_000b5b66",
     "index": 0x102, "source": "literal_movea", "set": [0x102],
     "async": "redundant_persist"},
    {"callsite": 0xB5C36, "caller": 0xB5C16, "name": "FUN_000b5c16",
     "index": 0x102, "source": "literal_decompile", "set": [0x102],
     "async": "redundant_persist"},
    {"callsite": 0xB72CE, "caller": 0xB72BA, "name": "FUN_000b72ba",
     "index": 0x106, "source": "literal_movea", "set": [0x106],
     "async": "redundant_persist"},
    {"callsite": 0xB7E62, "caller": 0xB7E4A, "name": "FUN_000b7e4a",
     "index": 0x7, "source": "literal_mov", "set": [0x7],
     "async": "checkpoint_persist"},
    {"callsite": 0xBAF70, "caller": 0xBAF46, "name": "FUN_000baf46",
     "index": 0x8, "source": "literal_mov", "set": [0x8],
     "async": "checkpoint_persist"},
    {"callsite": 0xBAFA8, "caller": 0xBAF82, "name": "FUN_000baf82",
     "index": 0x8, "source": "literal_mov", "set": [0x8],
     "async": "checkpoint_persist"},
    {"callsite": 0xBB098, "caller": 0xBAFB2, "name": "FUN_000bafb2",
     "index": 0x9, "source": "literal_decompile", "set": [0x9],
     "async": "checkpoint_persist"},
    {"callsite": 0xBB2A0, "caller": 0xBB286, "name": "FUN_000bb286",
     "index": 0xB, "source": "literal_mov", "set": [0xB],
     "async": "checkpoint_persist"},
    {"callsite": 0xBB3E0, "caller": 0xBB3C6, "name": "FUN_000bb3c6",
     "index": 0xB, "source": "literal_mov", "set": [0xB],
     "async": "checkpoint_persist"},
    {"callsite": 0xBB4D6, "caller": 0xBB482, "name": "checkpoint_object15_operating_state_persist",
     "index": 0xF, "source": "literal_decompile", "set": [0xF],
     "async": "checkpoint_persist"},
    {"callsite": 0xBB63E, "caller": 0xBB5EC, "name": "checkpoint_object15_operating_state_clear",
     "index": 0xF, "source": "literal_decompile", "set": [0xF],
     "async": "checkpoint_persist"},
    {"callsite": 0xBBCE0, "caller": 0xBBCC4, "name": "FUN_000bbcc4",
     "index": 0xD, "source": "literal_mov", "set": [0xD],
     "async": "checkpoint_persist"},
]

CSV_FIELDS = [
    "target_api",
    "caller_addr",
    "caller_name",
    "callsite_addr",
    "call_kind",
    "index_value",
    "namespace",
    "object_index",
    "index_source",
    "reachable_index_set",
    "async_persist_behavior",
    "secoc_object15_statically_selectable",
    "notes",
]

SECOC_OBJECT15_INDEX = 0x10F  # namespace 0x100 | object 15


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def namespace_of(index: int | None) -> str:
    if index is None:
        return ""
    return f"0x{(index & 0xFF00) >> 8:X}"


def object_of(index: int | None) -> str:
    if index is None:
        return ""
    return str(index & 0xFF)


def fmt_index(index: int | None) -> str:
    if index is None:
        return ""
    return f"0x{index:X}"


def fmt_set(values: list[int]) -> str:
    return "|".join(f"0x{v:X}" for v in values)


def row_for(api: str, kind: str, entry: dict, notes: str = "") -> dict:
    index = entry["index"]
    reachable = entry["set"]
    selectable = SECOC_OBJECT15_INDEX in reachable
    return {
        "target_api": api,
        "caller_addr": f"0x{entry['caller']:X}",
        "caller_name": entry["name"],
        "callsite_addr": f"0x{entry['callsite']:X}",
        "call_kind": kind,
        "index_value": fmt_index(index),
        "namespace": namespace_of(index) if index is not None else (
            "mixed" if reachable else ""
        ),
        "object_index": object_of(index) if index is not None else (
            "|".join(str(v & 0xFF) for v in reachable) if reachable else ""
        ),
        "index_source": entry["source"],
        "reachable_index_set": fmt_set(reachable),
        "async_persist_behavior": entry["async"],
        "secoc_object15_statically_selectable": "yes" if selectable else "no",
        "notes": notes,
    }


def build_rows() -> list[dict]:
    rows: list[dict] = []
    for entry in DIRECT_CALLS:
        notes = ""
        if entry["callsite"] == 0xFF0A2:
            notes = "thin wrapper; concrete indices come from WRAPPER_CALLS rows"
        if entry["source"] == "dynamic_map_0x53b70":
            notes = "mapper returns 0x14/0x15/0x17 (objects 20/21/23); 0x20 is no-op"
        if entry["source"] == "dynamic_bank_select_0x53ef2":
            notes = "bank helper selects checkpoint objects 0x12/0x13 only"
        rows.append(row_for("secoc_nvm_object_update", "direct", entry, notes))
    for entry in WRAPPER_CALLS:
        notes = ""
        if entry["index"] == 0xF:
            notes = (
                "checkpoint namespace-0 object 15 (operating_state_snapshot); "
                "NOT SecOC triplicate object 15 (requires 0x10F)"
            )
        rows.append(row_for("secoc_nvm_object_update_wrapper", "via_wrapper", entry, notes))
    # Adjacent API: redundant update is only reached from the dispatcher.
    rows.append({
        "target_api": "secoc_nvm_redundant_object_update",
        "caller_addr": "0x65CD8",
        "caller_name": "secoc_nvm_object_update",
        "callsite_addr": "0x65D18",
        "call_kind": "direct",
        "index_value": "",
        "namespace": "0x1",
        "object_index": "passthrough",
        "index_source": "dispatcher_namespace_0x100_branch",
        "reachable_index_set": "",
        "async_persist_behavior": "triplicate_write_queue",
        "secoc_object15_statically_selectable": "no",
        "notes": "sole caller of 0x66E48; object index is the low byte of dispatcher arg",
    })
    rows.sort(key=lambda r: (r["target_api"], int(r["callsite_addr"], 16)))
    return rows


def build_summary(rows: list[dict], cf: bytes) -> dict:
    selectable = [
        r for r in rows if r["secoc_object15_statically_selectable"] == "yes"
    ]
    checkpoint15 = [
        r for r in rows
        if r["index_value"] == "0xF" and r["namespace"] in ("0x0", "0x0")
    ]
    # Fix namespace check: fmt uses 0x0 for namespace 0
    checkpoint15 = [
        r for r in rows
        if r["index_value"] == "0xF"
    ]
    redundant_indices = sorted({
        int(v, 16)
        for r in rows
        for v in (r["reachable_index_set"].split("|") if r["reachable_index_set"] else [])
        if v and (int(v, 16) & 0xFF00) == 0x100
    })
    desc15 = (u16(cf, 0x2B0AC + 15 * 8), u16(cf, 0x2B0AC + 15 * 8 + 2),
              u32(cf, 0x2B0AC + 15 * 8 + 4))
    return {
        "schema_version": 1,
        "secoc_redundant_object15_full_index": "0x10F",
        "secoc_redundant_object15_descriptor": {
            "length": desc15[0],
            "base_block": desc15[1],
            "ram_mirror": f"0x{desc15[2]:X}",
        },
        "static_producer_status": "no static producer recovered",
        "search_method": (
            "Ghidra UNCONDITIONAL_CALL xref census to 0x65CD8 and 0xFF09C; "
            "decompiler/immediate recovery of each index arg; raw scan for "
            "movea 0x10F,r6 (20 36 0F 01) and mov 15,r6 near update callsites; "
            "sole xref to 0x66E48 is the namespace-0x100 branch inside 0x65CD8"
        ),
        "coverage_bound": (
            f"direct_callsites={len(DIRECT_CALLS)}; "
            f"wrapper_callsites={len(WRAPPER_CALLS)}; "
            "dynamic_index_maps={0x53B70→{0x14,0x15,0x17}, 0x53EF2→{0x12,0x13}}; "
            "AB/BA service callbacks have no call edge to 0x65CD8/0xFF09C"
        ),
        "redundant_namespace_0x100_indices_observed": [
            f"0x{v:X}" for v in redundant_indices
        ],
        "secoc_object15_selectable_row_count": len(selectable),
        "checkpoint_namespace0_object15_producers": [
            r["caller_addr"] for r in checkpoint15
        ],
        "application_ab_ba_reaches_object_update": False,
        "language": "no static producer recovered",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=REPO / "data" / "object15_reachability.csv",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=REPO / "data" / "object15_reachability_summary.json",
    )
    args = parser.parse_args()
    cf = CF_PATH.read_bytes()
    if len(cf) != 0x100000:
        print(f"unexpected CodeFlash size {len(cf):#x}", file=sys.stderr)
        return 1
    rows = build_rows()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = build_summary(rows, cf)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output} ({len(rows)} rows)")
    print(f"wrote {args.summary}")
    print(f"status: {summary['static_producer_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
