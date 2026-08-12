#!/usr/bin/env python3
"""Verify the reported 2023-US-Corolla community DataFlash evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.analyze_toyota_dataflash import (  # noqa: E402
    DEFAULT_BASE,
    analyze,
    load_layout,
    record_bytes,
    scan_key_domains,
)
from tools.toyota_secoc_oracle import load_capture  # noqa: E402

COMMUNITY = REPO / "community" / "albinoelephant"
DUMP = COMMUNITY / "dump_ff200000_ff208000.bin"
TSKM_ORACLE = COMMUNITY / "can_oracle.ndjson"
ROUTE_ORACLE = COMMUNITY / "public_route_secoc_oracle.ndjson"
GENERATED = REPO / "data" / "generated" / "corolla_2023_albino_dataflash_analysis.json"
REFERENCE = REPO / "data" / "generated" / "dataflash_structural_analysis_4512000.json"

EXPECTED = {
    DUMP: (32768, "8ac2a6beecb4ca2e6caf695eebffe440478171b4e093a1b2a36ab4e4ff313299"),
    TSKM_ORACLE: (97768, "8863398a98875a853e722a6ba83fc10563d5764cea33719c8af34225efa189a3"),
    ROUTE_ORACLE: (212536, "a9bf3f279001b8b77e96acfc186944a962c59cc7bedf739d902d971ff4b03f15"),
}

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


print("== artifact integrity ==")
for path, (size, digest) in EXPECTED.items():
    check(f"{path.name} exists", path.is_file())
    check(f"{path.name} size", path.stat().st_size == size, str(path.stat().st_size))
    check(f"{path.name} SHA-256", sha256(path) == digest, sha256(path)[:16])

print("\n== contributor TSKM oracle ==")
tskm_sync, tskm_protected, tskm_summary = load_capture(TSKM_ORACLE)
check("TSKM oracle has 1232 synchronization rows", len(tskm_sync) == 1232, str(len(tskm_sync)))
check("TSKM oracle has no protected rows", len(tskm_protected) == 0, str(len(tskm_protected)))
check("TSKM oracle has sync on buses 0 and 2", tskm_summary["buses_with_sync"] == [0, 2], str(tskm_summary["buses_with_sync"]))
check("TSKM bus0 0x00F count is 616", tskm_summary["counts"].get("bus0:0x00F") == 616)
check("TSKM bus2 0x00F count is 616", tskm_summary["counts"].get("bus2:0x00F") == 616)
check("TSKM oracle contains no protected-ID count", len(tskm_summary["counts"]) == 2, str(tskm_summary["counts"]))
check("local TSKM capture TRIP is 0xD0D", {sample.trip for sample in tskm_sync} == {0xD0D})
check("local TSKM capture has 320 reset-count span", max(s.reset for s in tskm_sync) - min(s.reset for s in tskm_sync) == 319)
same_session_sync_scan = scan_key_domains(
    DUMP.read_bytes(), tskm_sync, tskm_protected, min_entropy=0.0
)
check(
    "local TSKM sync scan tests all 23277 unique raw windows",
    same_session_sync_scan["candidates_tested"] == 23277,
    str(same_session_sync_scan["candidates_tested"]),
)
check(
    "local TSKM sync scan finds no raw DataFlash key",
    same_session_sync_scan["matches"] == [],
)

print("\n== public-route SecOC oracle ==")
route_sync, route_protected, route_summary = load_capture(ROUTE_ORACLE)
check("route oracle has 588 synchronization rows", len(route_sync) == 588, str(len(route_sync)))
check("route oracle retains bus 1 only", route_summary["buses_with_sync"] == [1], str(route_summary["buses_with_sync"]))
check("route oracle 0x00F count", route_summary["counts"].get("bus1:0x00F") == 588)
check("route oracle 0x116 count", route_summary["counts"].get("bus1:0x116") == 2499)
check("route oracle 0x24D count", route_summary["counts"].get("bus1:0x24D") == 59)
check("three initial 0x116 frames precede first sync", route_summary["orphan_protected"].get("bus1:0x116") == 3)
check("2555 protected samples have usable sync state", len(route_protected) == 2555, str(len(route_protected)))
check("public-route TRIP is 0xCE9", {sample.trip for sample in route_sync} == {0xCE9})
check(
    "local TSKM and public-route captures have different TRIP epochs",
    {sample.trip for sample in tskm_sync} != {sample.trip for sample in route_sync},
)

print("\n== exhaustive raw-window domain scan ==")
rebuilt = analyze(DUMP, capture_path=ROUTE_ORACLE, domain_scan=True, min_entropy=0.0)
committed = json.loads(GENERATED.read_text(encoding="utf-8"))
check("committed analysis equals deterministic rebuild", committed == rebuilt)
check("dump is exactly 32 KiB", rebuilt["size"] == 0x8000)
check("all 32753 overlapping windows are considered", rebuilt["entropy_windows"]["sliding_window_count"] == 32753)
check("23277 unique raw windows are cryptographically tested", rebuilt["key_domain_scan"]["candidates_tested"] == 23277)
check("domain scan has no entropy cutoff", rebuilt["key_domain_scan"]["min_entropy"] == 0.0)
check("no raw DataFlash key matches any observed domain", rebuilt["key_domain_scan"]["matches"] == [])
check("analysis sees 588 public-route sync samples", rebuilt["capture"]["sync_samples"] == 588)
check("analysis sees 2555 synchronized protected samples", rebuilt["capture"]["protected_samples"] == 2555)

print("\n== NvM cross-family structure ==")
objects = {row["object"]: row for row in rebuilt["triplicate_objects"]}
reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
ref_objects = {row["object"]: row for row in reference["triplicate_objects"]}
for object_id in (0, 2, 5):
    check(
        f"Corolla object {object_id} has three valid triplicate copies",
        objects[object_id]["valid_copy_count"] == 3 and objects[object_id]["valid_consensus"],
    )
for object_id in (1, 3, 4, 6, 12, 13, 14, 15):
    check(f"Corolla object {object_id} has no valid copy", objects[object_id]["valid_copy_count"] == 0)
check(
    "object 0 consensus matches 4512000",
    objects[0]["consensus_payload_sha256"] == ref_objects[0]["consensus_payload_sha256"],
)
check(
    "object 5 consensus matches 4512000",
    objects[5]["consensus_payload_sha256"] == ref_objects[5]["consensus_payload_sha256"],
)
check(
    "object 2 consensus differs from 4512000",
    objects[2]["consensus_payload_sha256"] != ref_objects[2]["consensus_payload_sha256"],
)
check("object 15 remains physically uncommitted", not objects[15]["valid_consensus"])
check(
    "object 15 retains known raw second-field geometry",
    objects[15]["known_key_field_geometry"]["raw"] == "0xFF206E14",
)

print("\n== full reference NvM geometry transfer ==")
dump_bytes = DUMP.read_bytes()
checkpoint_lengths = {
    int(row["object_index"]): int(row["data_length"])
    for row in csv.DictReader((REPO / "data/checkpoint_payload_map.csv").open(encoding="utf-8"))
}
checkpoint_rows = [row for row in load_layout() if row["owner_class"] == "checkpoint"]
physical_valid = []
envelope_valid = []
for row in checkpoint_rows:
    raw = record_bytes(dump_bytes, row, DEFAULT_BASE)
    storage_index = int(row["storage_index"])
    committed = int.from_bytes(raw[:2], "little") == storage_index and raw[-4:] == b"\xAA" * 4
    if not committed:
        continue
    physical_valid.append(row)
    owner_index = int(row["owner_index"])
    inverse_offset = 8 + max(checkpoint_lengths[owner_index], 56)
    generation = int.from_bytes(raw[4:8], "little")
    inverse = int.from_bytes(raw[inverse_offset:inverse_offset + 4], "little")
    if inverse == (~generation & 0xFFFFFFFF):
        envelope_valid.append((row, generation, inverse_offset))

check("Corolla has 51 committed checkpoint records at reference geometry", len(physical_valid) == 51, str(len(physical_valid)))
check("all 51 committed checkpoint records satisfy generation/complement envelope", len(envelope_valid) == 51, str(len(envelope_valid)))
check(
    "49 checkpoint records map to 4512000-enabled owners",
    sum(row["owner_enabled"] == "yes" for row, _, _ in envelope_valid) == 49,
)
disabled = [(row, generation, inverse_offset) for row, generation, inverse_offset in envelope_valid if row["owner_enabled"] == "no"]
check("only reference-disabled committed records are storage 117/118", [int(row["storage_index"]) for row, _, _ in disabled] == [117, 118])
check("storage 117/118 map to reference owner 28", {int(row["owner_index"]) for row, _, _ in disabled} == {28})
check("storage 117/118 generations are adjacent 0x25/0x24", [generation for _, generation, _ in disabled] == [0x25, 0x24])
check("storage 117/118 inverse-generation field is at +0x40", {inverse_offset for _, _, inverse_offset in disabled} == {0x40})
for row, _, _ in disabled:
    raw = record_bytes(dump_bytes, row, DEFAULT_BASE)
    check(
        f"storage {row['storage_index']} contains nonzero data beyond reference owner28's 8-byte payload",
        any(raw[16:64]),
    )

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
