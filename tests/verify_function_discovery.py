#!/usr/bin/env python3
"""Verify the generated outside-function census and callback discovery floor.

The callback-table anchors in this test are decoded directly from the pinned
CodeFlash image.  The generated candidate ledger is evidence, not its own
oracle: any dispatch-proven target that remains outside every function is a
failure until the reproducible seed stage creates it.
"""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
FIRMWARE = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
CANDIDATES = REPO / "data" / "outside_function_candidates.csv"
SUMMARY = REPO / "data" / "outside_function_summary.json"

HEADER = [
    "target_addr",
    "decoded_instruction_count",
    "decoded_byte_count",
    "run_start",
    "run_end",
    "incoming_call_refs",
    "incoming_data_refs",
    "incoming_computed_refs",
    "source_pointer_addrs",
    "source_function_entries",
    "starts_at_instruction_boundary",
    "starts_with_prepare",
    "contains_dispose",
    "terminating_flow_count",
    "overlaps_defined_data",
    "overlaps_existing_function",
    "candidate_class",
    "adjudication_state",
]

KNOWN_TABLE = 0x2B3F0
KNOWN_RECORDS = [
    (0xFB, 0x9729A),
    (0xFA, 0x972FA),
    (0xF5, 0x97432),
    (0xF3, 0x97546),
    (0xEB, 0x975EE),
    (0xEA, 0x97668),
    (0xE4, 0x976F4),
]
REVIEWED_CLUSTER_START = 0x27C88
REVIEWED_CLUSTER_END = 0x27D78
REVIEWED_CLUSTER_DESCRIPTOR = 0x27D84
REVIEWED_CLUSTER_SHA256 = "53d8c3f4dd2de0354cadac93118c67ef2485d4b3a22d1c5d9cae82de918d9a78"
BOOT_ROUTINE_CONTROL_POINTER = 0x8EC0
BOOT_ROUTINE_CONTROL_ENTRY = 0x567E
BOOT_ROUTINE_CONTROL_END = 0x5936
BOOT_ROUTINE_CONTROL_PROLOGUE = bytes.fromhex("8a07e170")
ALLOWED_CLASSES = {
    "direct-call-target",
    "table-callback-target",
    "pointer-referenced-code-run",
    "orphan-decoded-run",
    "ambiguous-data",
}
ALLOWED_STATES = {
    "unresolved",
    "unresolved-reviewed",
    "seeded",
    "rejected-data",
    "alternate-entry",
}

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        marker = "PASS"
    else:
        failed += 1
        marker = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{marker}] {name}{suffix}")


def parse_int(text: str) -> int:
    return int(text, 0)


def decode_known_table() -> list[tuple[int, int, int]]:
    image = FIRMWARE.read_bytes()
    records: list[tuple[int, int, int]] = []
    for index in range(len(KNOWN_RECORDS)):
        record = image[KNOWN_TABLE + index * 8 : KNOWN_TABLE + (index + 1) * 8]
        selector = record[0]
        padding = record[1:4]
        target = struct.unpack_from("<I", record, 4)[0]
        check(f"known table record {index} has zero padding", padding == b"\0\0\0")
        records.append((KNOWN_TABLE + index * 8 + 4, selector, target))
    return records


def main() -> int:
    print("== firmware-derived callback table ==")
    check("pinned CodeFlash exists", FIRMWARE.is_file(), str(FIRMWARE))
    if not FIRMWARE.is_file():
        return 1
    observed = decode_known_table()
    check(
        "0x2B3F0 selectors and targets match",
        [(selector, target) for _, selector, target in observed] == KNOWN_RECORDS,
        repr([(hex(selector), hex(target)) for _, selector, target in observed]),
    )

    image = FIRMWARE.read_bytes()
    cluster = image[REVIEWED_CLUSTER_START:REVIEWED_CLUSTER_END]
    cluster_targets = [struct.unpack_from("<I", cluster, offset)[0]
                       for offset in range(0, len(cluster), 4)]
    check("0x27C88 cluster byte hash matches firmware",
          hashlib.sha256(cluster).hexdigest() == REVIEWED_CLUSTER_SHA256)
    check("0x27C88 cluster contains 60 valid CodeFlash pointers",
          len(cluster_targets) == 60 and len(set(cluster_targets)) == 60
          and all(target <= 0xFFFFF and target % 2 == 0 for target in cluster_targets))
    base_literal = struct.pack("<I", REVIEWED_CLUSTER_START)
    literal_offsets = [offset for offset in range(len(image) - 3)
                       if image[offset:offset + 4] == base_literal]
    check("cluster base has one raw literal descriptor",
          literal_offsets == [REVIEWED_CLUSTER_DESCRIPTOR], repr(literal_offsets))
    check("boot SID 0x31 service pointer is authoritative entry 0x567E",
          struct.unpack_from("<I", image, BOOT_ROUTINE_CONTROL_POINTER)[0]
          == BOOT_ROUTINE_CONTROL_ENTRY)
    check("boot SID 0x31 entry starts with complete four-byte prepare",
          image[BOOT_ROUTINE_CONTROL_ENTRY:BOOT_ROUTINE_CONTROL_ENTRY + 4]
          == BOOT_ROUTINE_CONTROL_PROLOGUE)

    print("\n== generated outside-function ledger ==")
    check("candidate CSV exists", CANDIDATES.is_file(), str(CANDIDATES))
    check("candidate summary exists", SUMMARY.is_file(), str(SUMMARY))
    if not CANDIDATES.is_file() or not SUMMARY.is_file():
        print(f"\nSummary: {passed} passed, {failed} failed")
        return 1

    with CANDIDATES.open(newline="") as handle:
        reader = csv.DictReader(handle)
        check("candidate schema is exact", reader.fieldnames == HEADER, repr(reader.fieldnames))
        rows = list(reader)

    addresses: list[int] = []
    by_addr: dict[int, dict[str, str]] = {}
    parse_errors: list[str] = []
    no_code: list[str] = []
    bad_classes: list[str] = []
    bad_states: list[str] = []
    bad_booleans: list[str] = []
    for index, row in enumerate(rows):
        try:
            address = parse_int(row["target_addr"])
            numeric = [
                "decoded_instruction_count",
                "decoded_byte_count",
                "incoming_call_refs",
                "incoming_data_refs",
                "incoming_computed_refs",
                "terminating_flow_count",
            ]
            values = {field: int(row[field]) for field in numeric}
            parse_int(row["run_start"])
            parse_int(row["run_end"])
        except (KeyError, ValueError) as exc:
            parse_errors.append(f"row {index}: {exc}")
            continue
        addresses.append(address)
        by_addr[address] = row
        if values["decoded_instruction_count"] <= 0 or values["decoded_byte_count"] <= 0:
            no_code.append(row["target_addr"])
        if row["candidate_class"] not in ALLOWED_CLASSES:
            bad_classes.append(f"{row['target_addr']}={row['candidate_class']}")
        if row["adjudication_state"] not in ALLOWED_STATES:
            bad_states.append(f"{row['target_addr']}={row['adjudication_state']}")
        for field in (
            "starts_at_instruction_boundary",
            "starts_with_prepare",
            "contains_dispose",
            "overlaps_defined_data",
            "overlaps_existing_function",
        ):
            if row[field] not in {"true", "false"}:
                bad_booleans.append(f"{row['target_addr']}:{field}={row[field]}")

    check("all candidate rows parse", not parse_errors, repr(parse_errors[:5]))
    check("all candidates contain decoded code", not no_code, repr(no_code[:10]))
    check("all candidate classes are allowed", not bad_classes, repr(bad_classes[:10]))
    check("all adjudication states are allowed", not bad_states, repr(bad_states[:10]))
    check("all candidate flags are booleans", not bad_booleans, repr(bad_booleans[:10]))

    check("candidate addresses are sorted and unique", addresses == sorted(set(addresses)))
    routine_control_orphans = [
        row["target_addr"] for row in rows
        if BOOT_ROUTINE_CONTROL_ENTRY <= parse_int(row["target_addr"]) < BOOT_ROUTINE_CONTROL_END
    ]
    check("boot SID 0x31 body has no outside-function candidates",
          not routine_control_orphans, repr(routine_control_orphans))

    reviewed_cluster = [
        row
        for row in rows
        if any(
            REVIEWED_CLUSTER_START <= parse_int(pointer) < REVIEWED_CLUSTER_END
            for pointer in row["source_pointer_addrs"].split(";")
            if pointer
        )
    ]
    check("0x27C88 pointer cluster has 60 candidates", len(reviewed_cluster) == 60)
    check(
        "0x27C88 pointer cluster is explicitly reviewed-unresolved",
        all(row["adjudication_state"] == "unresolved-reviewed" for row in reviewed_cluster),
    )

    known_targets = {target for _, _, target in observed}
    remaining = known_targets.intersection(by_addr)
    for pointer_addr, selector, target in observed:
        row = by_addr.get(target)
        if row is None:
            continue
        check(
            f"selector 0x{selector:02x} target is dispatch-classified",
            row["candidate_class"] == "table-callback-target",
            row["candidate_class"],
        )
        check(
            f"selector 0x{selector:02x} retains pointer-field provenance",
            f"0x{pointer_addr:08x}" in row["source_pointer_addrs"].split(";"),
            row["source_pointer_addrs"],
        )
    check(
        "dispatch-proven 0x2B3F0 targets are all inside exact functions",
        not remaining,
        "still outside: " + ", ".join(f"0x{x:08x}" for x in sorted(remaining)),
    )

    summary = json.loads(SUMMARY.read_text())
    check("summary schema version", summary.get("schema_version") == 1)
    check("summary candidate count", summary.get("candidate_count") == len(rows))
    expected_counts: dict[str, int] = {}
    for row in rows:
        cls = row["candidate_class"]
        expected_counts[cls] = expected_counts.get(cls, 0) + 1
    check(
        "summary evidence-class counts",
        summary.get("candidate_class_counts") == dict(sorted(expected_counts.items())),
        repr(summary.get("candidate_class_counts")),
    )

    print(f"\nSummary: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
