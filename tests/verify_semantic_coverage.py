#!/usr/bin/env python3
"""Verify the committed semantic coverage ledger against its schema and floors.

The ledger is a recovered-function inventory, not a claim that every function is
semantically understood. Most rows must remain evidence_grade=recovered.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CSV_PATH = REPO / "data" / "semantic_coverage_ledger.csv"
SUMMARY_PATH = REPO / "data" / "semantic_coverage_summary.json"

HEADER = [
    "entry_addr",
    "body_bytes",
    "name",
    "name_source",
    "is_thunk",
    "calling_convention",
    "caller_count",
    "callee_count",
    "root_kind",
    "ram_ref_count",
    "mmio_ref_count",
    "codeflash_data_ref_count",
    "string_ref_count",
    "subsystem",
    "evidence_grade",
]

# Floor from AssertNoUndefinedInFunctions on the current working project.
MIN_FUNCTIONS = 5858
CODEFLASH_END = 0x100000
APPLICATION_BASE = 0x20000
LOCAL_RAM_START = 0xFEBE0000
LOCAL_RAM_END = 0xFEC00000  # exclusive
ALLOWED_GRADES = {"annotated", "recovered", "thunk"}
ALLOWED_SOURCES = {
    "USER_DEFINED",
    "DEFAULT",
    "ANALYSIS",
    "IMPORTED",
    "CALCULATED",
    "UNKNOWN",
}
ALLOWED_ROOTS = {"", "interrupt", "scheduler"}
ALLOWED_SUBSYSTEMS = {"", "boot", "application"}


def in_mapped_image(addr: int) -> bool:
    return (0 <= addr < CODEFLASH_END) or (LOCAL_RAM_START <= addr < LOCAL_RAM_END)

# Documented landmarks: name / convention / grade / subsystem / optional root.
LANDMARKS = {
    0x000001B0: {
        "name": "boot_reset_startup",
        "calling_convention": "__stdcall",
        "evidence_grade": "annotated",
        "subsystem": "boot",
        "name_source": "USER_DEFINED",
    },
    0x00006FEC: {
        "name": "security_access_derive_stage1_key",
        "calling_convention": "__stdcall",
        "evidence_grade": "annotated",
        "subsystem": "boot",
        "name_source": "USER_DEFINED",
    },
    0x00007068: {
        "name": "payload_build_derive_key",
        "calling_convention": "__stdcall",
        "evidence_grade": "annotated",
        "subsystem": "boot",
        "name_source": "USER_DEFINED",
    },
    0x00020880: {
        "name": "application_entry",
        "calling_convention": "__stdcall",
        "evidence_grade": "annotated",
        "subsystem": "application",
        "name_source": "USER_DEFINED",
    },
    0x00064FCC: {
        "name": "application_foreground_cyclic_loop",
        "calling_convention": "__stdcall",
        "evidence_grade": "annotated",
        "subsystem": "application",
        "name_source": "USER_DEFINED",
        "root_kind": "scheduler",
    },
    0x00087610: {
        "name": "icus_interrupt_channel292_dispatch",
        "calling_convention": "__stdcall",
        "evidence_grade": "annotated",
        "subsystem": "application",
        "name_source": "USER_DEFINED",
    },
}

passed = 0
failed = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{mark}] {name}{suffix}")


def parse_addr(text: str) -> int:
    return int(text, 0)


def main() -> int:
    print("== semantic coverage ledger ==")
    check("CSV exists", CSV_PATH.is_file(), str(CSV_PATH))
    check("summary JSON exists", SUMMARY_PATH.is_file(), str(SUMMARY_PATH))
    if not CSV_PATH.is_file():
        print(f"\nSummary: {passed} passed, {failed} failed")
        return 1

    with CSV_PATH.open(newline="") as fh:
        reader = csv.DictReader(fh)
        check("header matches schema", reader.fieldnames == HEADER, repr(reader.fieldnames))
        rows = list(reader)

    check("function floor", len(rows) >= MIN_FUNCTIONS, f"{len(rows)} >= {MIN_FUNCTIONS}")
    check("at least one row", len(rows) > 0)

    addrs: list[int] = []
    grades: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    conventions: Counter[str] = Counter()
    by_addr: dict[int, dict[str, str]] = {}

    prev = -1
    for i, row in enumerate(rows):
        try:
            addr = parse_addr(row["entry_addr"])
            body = int(row["body_bytes"])
            callers = int(row["caller_count"])
            callees = int(row["callee_count"])
            for key in (
                "ram_ref_count",
                "mmio_ref_count",
                "codeflash_data_ref_count",
                "string_ref_count",
            ):
                int(row[key])
        except (KeyError, ValueError) as exc:
            check(f"row {i} parses", False, str(exc))
            continue

        addrs.append(addr)
        by_addr[addr] = row
        grades[row["evidence_grade"]] += 1
        sources[row["name_source"]] += 1
        conventions[row["calling_convention"]] += 1

        if addr <= prev:
            check("rows sorted unique by address", False, f"0x{addr:08x} after 0x{prev:08x}")
            break
        prev = addr

        if not in_mapped_image(addr):
            check("entry in CodeFlash or LocalRAM", False, row["entry_addr"])
        if body <= 0:
            check("body_bytes positive", False, f"{row['entry_addr']} body={body}")
        if callers < 0 or callees < 0:
            check("caller/callee non-negative", False, row["entry_addr"])
        if row["is_thunk"] not in ("true", "false"):
            check("is_thunk boolean", False, row["is_thunk"])
        if row["evidence_grade"] not in ALLOWED_GRADES:
            check("evidence_grade allowed", False, row["evidence_grade"])
        if row["name_source"] not in ALLOWED_SOURCES:
            check("name_source allowed", False, row["name_source"])
        if row["root_kind"] not in ALLOWED_ROOTS:
            check("root_kind allowed", False, row["root_kind"])
        if row["subsystem"] not in ALLOWED_SUBSYSTEMS:
            check("subsystem allowed", False, row["subsystem"])
        if row["subsystem"] == "boot" and not (0 <= addr < APPLICATION_BASE):
            check("boot subsystem address", False, row["entry_addr"])
        if row["subsystem"] == "application" and not (
            APPLICATION_BASE <= addr < CODEFLASH_END
        ):
            check("application subsystem address", False, row["entry_addr"])
        if addr >= CODEFLASH_END and row["subsystem"] != "":
            check("non-CodeFlash subsystem empty", False,
                  f"{row['entry_addr']} subsystem={row['subsystem']}")
        if row["is_thunk"] == "true" and row["evidence_grade"] != "thunk":
            check("thunk grade", False, row["entry_addr"])
        if (
            row["is_thunk"] == "false"
            and row["name_source"] == "USER_DEFINED"
            and row["evidence_grade"] != "annotated"
        ):
            check("USER_DEFINED grade", False, f"{row['entry_addr']} -> {row['evidence_grade']}")
        if (
            row["is_thunk"] == "false"
            and row["name_source"] != "USER_DEFINED"
            and row["evidence_grade"] != "recovered"
        ):
            check("auto-name grade", False, f"{row['entry_addr']} -> {row['evidence_grade']}")
    else:
        check("rows sorted unique by address", len(addrs) == len(set(addrs)), len(addrs))
        check(
            "CodeFlash-resident majority",
            sum(1 for a in addrs if a < CODEFLASH_END) >= MIN_FUNCTIONS - 8,
            f"codeflash={sum(1 for a in addrs if a < CODEFLASH_END)}",
        )

    check(
        "not all functions annotated",
        grades.get("annotated", 0) < len(rows),
        f"annotated={grades.get('annotated', 0)} / {len(rows)}",
    )
    check(
        "majority still recovered",
        grades.get("recovered", 0) > len(rows) // 2,
        f"recovered={grades.get('recovered', 0)} / {len(rows)}",
    )
    check("has annotated landmarks", grades.get("annotated", 0) > 0)
    check("has recovered functions", grades.get("recovered", 0) > 0)

    print("\n== landmarks ==")
    for addr, expect in sorted(LANDMARKS.items()):
        row = by_addr.get(addr)
        check(f"landmark 0x{addr:08x} present", row is not None)
        if row is None:
            continue
        for key, value in expect.items():
            check(
                f"landmark 0x{addr:08x} {key}",
                row.get(key) == value,
                f"{row.get(key)!r} == {value!r}",
            )

    # Known ISR wrappers from RecoverVectorHandlers / AssertDecompilerInvariants.
    for addr in (0x650AC, 0x650EE):
        row = by_addr.get(addr)
        check(f"ISR 0x{addr:08x} present", row is not None)
        if row is None:
            continue
        check(
            f"ISR 0x{addr:08x} convention",
            row["calling_convention"] == "__interrupt",
            row["calling_convention"],
        )
        check(
            f"ISR 0x{addr:08x} root_kind",
            row["root_kind"] == "interrupt",
            row["root_kind"],
        )

    print("\n== summary JSON ==")
    if SUMMARY_PATH.is_file():
        summary = json.loads(SUMMARY_PATH.read_text())
        check("summary function_count", summary.get("function_count") == len(rows),
              f"{summary.get('function_count')} == {len(rows)}")
        check(
            "summary grade counts",
            summary.get("evidence_grade_counts") == dict(sorted(grades.items())),
            repr(summary.get("evidence_grade_counts")),
        )
        check(
            "summary name_source counts",
            summary.get("name_source_counts") == dict(sorted(sources.items())),
        )
        check(
            "summary calling_convention counts",
            summary.get("calling_convention_counts") == dict(sorted(conventions.items())),
        )
        check("summary schema_version", summary.get("schema_version") == 1)

    print("\n== grade census ==")
    for grade, count in sorted(grades.items()):
        print(f"  {grade}: {count}")
    print(f"  total: {len(rows)}")

    print(f"\nSummary: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
