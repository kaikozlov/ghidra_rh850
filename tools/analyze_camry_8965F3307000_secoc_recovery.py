#!/usr/bin/env python3
"""Build the compact exact-target Camry F33 SecOC recovery artifact.

This analyzer intentionally separates two evidence classes:

* deterministic facts reproduced directly from retained DataFlash/RAM/CAN bytes;
* the retained exhaustive ``kai-openpilot`` matcher result, which is provenance-bound
  to those exact input hashes but is not re-run here because the full FD SecOC scan is
  deliberately too expensive for the core repository verification loop.

No recovered/candidate raw key bytes are emitted.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.common.payload_package import inspect_payload
from tools.analyze_toyota_dataflash import analyze_triplicate_objects

ROOT = REPO / "targets/camry-2026/raw-20260826/secoc-recovery"
DATAFLASH = ROOT / "dataflash/dump_ff200000_ff208000.bin"
ORACLE_GZ = ROOT / "can_oracle.ndjson.gz"
LOCAL_RAM = ROOT / "ram/local_ram_pe1.bin"
LOCAL_COVERAGE = ROOT / "ram/local_ram_pe1.coverage.bin"
LOCAL_RUN = ROOT / "ram/local_ram_pe1.run.json"
GLOBAL_RAM = ROOT / "ram/global_ram.bin"
GLOBAL_COVERAGE = ROOT / "ram/global_ram.coverage.bin"
GLOBAL_RUN = ROOT / "ram/global_ram.run.json"
SCAN_RESULTS = ROOT / "offline_scan_results.json"
PAYLOADS = {
    "dataflash": ROOT / "payloads/payload_dataflash_ff200000_ff208000.bin",
    "local_ram_pe1": ROOT / "payloads/payload_local_ram_pe1_febe0000_fec00000.bin",
    "global_ram": ROOT / "payloads/payload_global_ram_feef8000_fef08000.bin",
}

DATAFLASH_BASE = 0xFF200000
LOCAL_RAM_BASE = 0xFEBE0000
GLOBAL_RAM_BASE = 0xFEEF8000
LOCAL_CLOBBER = (0xFEBF0000, 0xFEBF1000)
APP_SA_ROOT = bytes.fromhex("893e08418c741ffa2a9c044bffa55813")
PAYLOAD_BUILD_ROOT = bytes.fromhex("ba052435f8843f985fd1329d2b6117b0")
BOOT_SA_ROOT = bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044")
EXPECTED_APP_F181_HEX = "023839363546333330373030300000000038413331313333303331303000000000"
EXPECTED_BOOT_F181_HEX = "02" + "21" * 32


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(REPO)),
        "size": len(data),
        "sha256": sha256(data),
    }


def find_all(blob: bytes, needle: bytes, base: int) -> list[str]:
    out: list[str] = []
    pos = 0
    while True:
        off = blob.find(needle, pos)
        if off < 0:
            return out
        out.append(f"0x{base + off:08X}")
        pos = off + 1


def memory_statistics(blob: bytes) -> dict[str, int]:
    return {
        "bytes": len(blob),
        "zero_bytes": blob.count(0),
        "ff_bytes": blob.count(0xFF),
        "distinct_byte_values": len(set(blob)),
    }


def legacy_checksum(record: bytes) -> bool:
    if len(record) != 0x20:
        return False
    return ((~sum(record[:0x1D])) & 0xFF) == record[0x1D]


def summarize_legacy_table(local: bytes) -> dict[str, object]:
    table_start = 0xFEBE6E34
    table_end = 0xFEBE6FF4
    off = table_start - LOCAL_RAM_BASE
    table = local[off : off + (table_end - table_start)]
    records = []
    for index in range(len(table) // 0x20):
        record = table[index * 0x20 : (index + 1) * 0x20]
        key = record[0x0C:0x1C]
        records.append(
            {
                "index": index,
                "record_address": f"0x{table_start + index * 0x20:08X}",
                "key_field_address": f"0x{table_start + index * 0x20 + 0x0C:08X}",
                "checksum_valid": legacy_checksum(record),
                "key_field_zero": key == bytes(16),
                "key_field_sha256": sha256(key),
            }
        )
    return {
        "range": [f"0x{table_start:08X}", f"0x{table_end:08X}"],
        "record_size": 0x20,
        "record_count": len(records),
        "valid_checksum_count": sum(row["checksum_valid"] for row in records),
        "records": records,
        "old_extractor_key_1": records[1],
        "old_extractor_key_4": records[4],
        "old_factory_record_0xFEBF42E0_zero": (
            local[0xFEBF42E0 - LOCAL_RAM_BASE : 0xFEBF4300 - LOCAL_RAM_BASE] == bytes(0x20)
        ),
        "interpretation": (
            "The old FEBE6E34 0x20-byte key-table contract does not transfer to F33: "
            "none of the 14 candidate records satisfies its own checksum rule."
        ),
    }


def summarize_oracle() -> dict[str, object]:
    compressed = ORACLE_GZ.read_bytes()
    digest = hashlib.sha256()
    size = 0
    event_counts: Counter[str] = Counter()
    stream_counts: Counter[tuple[int, int, int]] = Counter()
    first_ms: float | None = None
    last_ms: float | None = None
    with gzip.open(ORACLE_GZ, "rb") as stream:
        for raw in stream:
            digest.update(raw)
            size += len(raw)
            row = json.loads(raw)
            event = str(row.get("event", ""))
            event_counts[event] += 1
            if event != "can":
                continue
            bus = int(row["bus"])
            addr = int(row["addr"])
            length = int(row.get("len", len(bytes.fromhex(row["data"]))))
            stream_counts[(bus, addr, length)] += 1
            ts = float(row["ts_ms"])
            first_ms = ts if first_ms is None else min(first_ms, ts)
            last_ms = ts if last_ms is None else max(last_ms, ts)
    focus = (0x00F, 0x090, 0x0D7, 0x0B6, 0x116, 0x24D)
    return {
        "path": str(ORACLE_GZ.relative_to(REPO)),
        "compressed_size": len(compressed),
        "compressed_sha256": sha256(compressed),
        "uncompressed_size": size,
        "uncompressed_sha256": digest.hexdigest(),
        "event_counts": dict(sorted(event_counts.items())),
        "duration_ms": None if first_ms is None or last_ms is None else round(last_ms - first_ms, 6),
        "focus_bus1_streams": {
            f"0x{addr:03X}": {
                "count": sum(count for (bus, can_id, _length), count in stream_counts.items() if bus == 1 and can_id == addr),
                "length_counts": {
                    str(length): count
                    for (bus, can_id, length), count in sorted(stream_counts.items())
                    if bus == 1 and can_id == addr
                },
            }
            for addr in focus
        },
        "all_stream_count": len(stream_counts),
    }


def summarize_payloads() -> dict[str, object]:
    out: dict[str, object] = {}
    for name, path in PAYLOADS.items():
        payload = path.read_bytes()
        inspection = inspect_payload(payload, secret=PAYLOAD_BUILD_ROOT)
        out[name] = {
            **file_identity(path),
            "callback_address": f"0x{inspection.callback_address:08X}",
            "descriptor_address": f"0x{inspection.descriptor_address:08X}",
            "descriptor_length": inspection.descriptor_length,
            "crc_residue": f"0x{inspection.crc_residue:08X}",
            "cmac_valid": inspection.cmac_valid,
        }
    return out


def summarize_run(path: Path, coverage_path: Path, *, expected_profile: str, expected_size: int) -> dict[str, object]:
    run = json.loads(path.read_text())
    result = run["result"]
    coverage = coverage_path.read_bytes()
    stages = {row["name"]: row for row in run["stages"]}
    return {
        "run": file_identity(path),
        "coverage": {
            **file_identity(coverage_path),
            "all_words_covered": coverage == bytes([1]) * (expected_size // 4),
        },
        "schema": run["schema"],
        "profile": result["profile"],
        "status": result["status"],
        "range": [result["range_start"], result["range_end"]],
        "coverage_percent": result["coverage_percent"],
        "expected_words": result["expected_words"],
        "unique_words": result["unique_words"],
        "duplicate_words": result["duplicate_words"],
        "conflicts": result["conflicts"],
        "spi_errors": result["spi_errors"],
        "dump_sha256": result["sha256"],
        "clobber_range": result["clobber_range"],
        "application_f181_exact": stages["application identity"]["observed_hex"] == EXPECTED_APP_F181_HEX,
        "nrt_ready_values": stages["NRTD Ready-status guard"]["ready_values"],
        "boot_f181_exact": stages["boot identity"]["observed_hex"] == EXPECTED_BOOT_F181_HEX,
        "old_stack_zero_dids": (
            stages["UDS variant / DID 0x0203"].get("variant") == "old"
            and stages["DID 0x0201/0x0202"].get("value") == "zero16"
        ),
        "verify_10f0_accepted": stages["RoutineControl 0x10F0"]["status"] == "accepted",
        "ff00_sent": stages["RoutineControl 0xFF00 callback trigger"]["status"] == "sent",
        "expected_profile": expected_profile,
    }


def build() -> dict[str, object]:
    dataflash = DATAFLASH.read_bytes()
    local = LOCAL_RAM.read_bytes()
    global_ram = GLOBAL_RAM.read_bytes()
    objects = {int(row["object"]): row for row in analyze_triplicate_objects(dataflash, DATAFLASH_BASE)}
    obj15 = objects[15]
    obj15_copies = obj15["copies"]
    scan = json.loads(SCAN_RESULTS.read_text())

    return {
        "schema": "camry-8965f3307000-secoc-recovery-v1",
        "target": {
            "f181": "8965F3307000",
            "secondary_identity": "8A3113303100",
            "diagnostic_route": {"bus": 1, "elm327_param": 1, "tx": "0x7A1", "rx": "0x7A9"},
        },
        "payloads": summarize_payloads(),
        "oracle": summarize_oracle(),
        "dataflash": {
            **file_identity(DATAFLASH),
            "statistics": memory_statistics(dataflash),
            "object15": {
                "valid_copy_count": obj15["valid_copy_count"],
                "valid_consensus": obj15["valid_consensus"],
                "all_decoded_copies_equal": obj15["all_decoded_copies_equal"],
                "copy_addresses": [row["va_start"] for row in obj15_copies],
                "key_field_addresses": [row["second_field_address"] for row in obj15_copies],
                "key_fields_zero": [
                    dataflash[int(row["second_field_address"], 16) - DATAFLASH_BASE : int(row["second_field_address"], 16) - DATAFLASH_BASE + 16] == bytes(16)
                    for row in obj15_copies
                ],
                "interpretation": (
                    "Object 15 retains the known triplicate geometry but has zero valid copies; "
                    "all three 16-byte second/key-field locations are raw zero bytes."
                ),
            },
        },
        "local_ram_pe1": {
            **file_identity(LOCAL_RAM),
            "statistics": memory_statistics(local),
            "acquisition": summarize_run(LOCAL_RUN, LOCAL_COVERAGE, expected_profile="local_ram_pe1", expected_size=0x20000),
            "clobber_range": [f"0x{LOCAL_CLOBBER[0]:08X}", f"0x{LOCAL_CLOBBER[1]:08X}"],
            "app_sa_root_hits": find_all(local, APP_SA_ROOT, LOCAL_RAM_BASE),
            "payload_build_root_hits": find_all(local, PAYLOAD_BUILD_ROOT, LOCAL_RAM_BASE),
            "boot_sa_root_hits": find_all(local, BOOT_SA_ROOT, LOCAL_RAM_BASE),
            "legacy_key_table": summarize_legacy_table(local),
        },
        "global_ram": {
            **file_identity(GLOBAL_RAM),
            "statistics": memory_statistics(global_ram),
            "acquisition": summarize_run(GLOBAL_RUN, GLOBAL_COVERAGE, expected_profile="global_ram", expected_size=0x10000),
            "app_sa_root_hits": find_all(global_ram, APP_SA_ROOT, GLOBAL_RAM_BASE),
            "payload_build_root_hits": find_all(global_ram, PAYLOAD_BUILD_ROOT, GLOBAL_RAM_BASE),
            "boot_sa_root_hits": find_all(global_ram, BOOT_SA_ROOT, GLOBAL_RAM_BASE),
        },
        "offline_key_scan": scan,
        "boundaries": [
            "The exhaustive scan result is retained tool output bound to exact input hashes; core verification does not rerun the expensive FD SecOC scan.",
            "PE1 LocalRAM FEBF0000..FEBF0FFF is acquisition-clobbered by the authenticated 4 KiB payload and is excluded from the retained matcher scan.",
            "The RAM snapshots are post-application-to-boot-handoff observations. A transient application-only CPU-visible value could be cleared before these reads.",
            "No CPU-visible match does not imply an empty ICU-S slot 4: target-native firmware and live 0x0D7 traffic independently prove slot-4 command-7 verification is active.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
