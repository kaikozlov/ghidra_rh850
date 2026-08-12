#!/usr/bin/env python3
"""Verify the reported 2023-US-Corolla community DataFlash evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.analyze_toyota_dataflash import analyze  # noqa: E402
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
sync, protected, summary = load_capture(TSKM_ORACLE)
check("TSKM oracle has 1232 synchronization rows", len(sync) == 1232, str(len(sync)))
check("TSKM oracle has no protected rows", len(protected) == 0, str(len(protected)))
check("TSKM oracle has sync on buses 0 and 2", summary["buses_with_sync"] == [0, 2], str(summary["buses_with_sync"]))
check("TSKM bus0 0x00F count is 616", summary["counts"].get("bus0:0x00F") == 616)
check("TSKM bus2 0x00F count is 616", summary["counts"].get("bus2:0x00F") == 616)
check("TSKM oracle contains no protected-ID count", len(summary["counts"]) == 2, str(summary["counts"]))

print("\n== public-route SecOC oracle ==")
sync, protected, summary = load_capture(ROUTE_ORACLE)
check("route oracle has 588 synchronization rows", len(sync) == 588, str(len(sync)))
check("route oracle retains bus 1 only", summary["buses_with_sync"] == [1], str(summary["buses_with_sync"]))
check("route oracle 0x00F count", summary["counts"].get("bus1:0x00F") == 588)
check("route oracle 0x116 count", summary["counts"].get("bus1:0x116") == 2499)
check("route oracle 0x24D count", summary["counts"].get("bus1:0x24D") == 59)
check("three initial 0x116 frames precede first sync", summary["orphan_protected"].get("bus1:0x116") == 3)
check("2555 protected samples have usable sync state", len(protected) == 2555, str(len(protected)))

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

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
