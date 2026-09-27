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
import struct
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
FIRMWARE = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
CANDIDATES = REPO / "data" / "outside_function_candidates.csv"


KNOWN_TABLE = 0x2B3F0
RDBI_TABLE = 0x2941C
RDBI_COUNT = 242
RDBI_STRIDE = 16
RDBI_TABLE_SHA256 = "4b84c14b28e1518fae9a12de032b935503a22bda2c8797d330011d73ae848520"
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

    rdbi_region = image[RDBI_TABLE:RDBI_TABLE + RDBI_COUNT * RDBI_STRIDE]
    rdbi_callbacks = [
        struct.unpack_from("<I", rdbi_region, index * RDBI_STRIDE + 4)[0]
        for index in range(RDBI_COUNT)
    ]
    rdbi_targets = {target for target in rdbi_callbacks if target}
    check("application RDBI table byte hash matches firmware",
          hashlib.sha256(rdbi_region).hexdigest() == RDBI_TABLE_SHA256)
    check("application RDBI table has 242 rows and 196 unique callbacks",
          len(rdbi_callbacks) == 242 and len(rdbi_targets) == 196)


    with CANDIDATES.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    by_addr: dict[int, dict[str, str]] = {}
    for index, row in enumerate(rows):
        try:
            by_addr[parse_int(row["target_addr"])] = row
        except (KeyError, ValueError) as exc:
            check(f"candidate row {index} parses", False, str(exc))
            continue

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
    rdbi_remaining = rdbi_targets.intersection(by_addr)
    check(
        "all 196 firmware-proven application RDBI callbacks are inside exact functions",
        not rdbi_remaining,
        "still outside: " + ", ".join(f"0x{x:08x}" for x in sorted(rdbi_remaining)),
    )

    print(f"\nSummary: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
