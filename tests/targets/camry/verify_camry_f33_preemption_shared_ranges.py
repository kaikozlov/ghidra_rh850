#!/usr/bin/env python3
"""Verify Camry F33 interrupt shared-range classification."""
from __future__ import annotations

from tools.targets.camry.research import (
    report_camry_f33_preemption_shared_ranges as shared,
)

FUNCTIONS = shared.FunctionIndex((
    shared.FunctionRange(0x100, 0x110, 0x100, "interrupted"),
    shared.FunctionRange(0x200, 0x210, 0x200, "handler"),
))


def report(write_address: int, psw_id: int) -> dict:
    return {
        "scenario": "fixture",
        "instruction_trace": [],
        "device_events": [
            {
                "kind": "interrupt-enter",
                "channel": 7,
                "priority": 3,
                "return_pc": "0x102",
                "handler": "0x200",
                "scheduler_tick": 1,
                "psw_id": psw_id,
                "pmr": "0",
            },
            {
                "kind": "interrupt-return",
                "pc": "0x20e",
                "return_pc": "0x102",
                "scheduler_tick": 2,
            },
        ],
        "memory_accesses": [
            {
                "kind": "read", "pc": "0x100", "instruction": 0,
                "address": "0x1000", "size": 1, "value": "0x12",
            },
            {
                "kind": "write", "pc": "0x200", "instruction": 1,
                "address": hex(write_address), "size": 1, "value": "0x34",
            },
            {
                "kind": "read", "pc": "0x102", "instruction": 2,
                "address": "0x1000", "size": 1, "value": "0x34",
            },
        ],
    }


def main() -> int:
    unprotected = shared.analyze_report(report(0x1000, 0), "unprotected", FUNCTIONS)
    assert len(unprotected["rows"]) == 1
    row = unprotected["rows"][0]
    assert row["range"] == {"start": "0x00001000", "end": "0x00001000", "width": 1}
    assert row["disposition"] == "shared without protection"
    assert row["before_accesses"][0]["value"] == "0x12"
    assert row["after_accesses"][0]["value"] == "0x34"

    protected = shared.analyze_report(report(0x1000, 1), "protected", FUNCTIONS)
    assert protected["rows"][0]["disposition"] == "protected by DI/EI"
    assert protected["deliveries"][0]["delivery_status"] == "forced, ID masked at delivery"

    disjoint = shared.analyze_report(report(0x2000, 0), "disjoint", FUNCTIONS)
    assert disjoint["rows"] == []
    assert disjoint["deliveries"][0]["shared_range_count"] == 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
