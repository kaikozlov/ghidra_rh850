#!/usr/bin/env python3
"""Offline structural and cryptographic analysis of a Toyota EPS DataFlash dump.

The analyzer combines two independent evidence layers:

1. Known NvM geometry from ``data/dataflash_nvm_records.csv``: physical record
   validity, raw/XOR55/XORAA triplicate decoding, redundant-object consensus,
   and the structurally known object-15 second-field locations.
2. Optional capture-driven AES-CMAC evidence using ``toyota_secoc_oracle``.
   A full-domain scan can test every unique sliding 16-byte window for sync and
   each observed classic protected CAN ID, allowing protected-only and
   cross-ID key-domain classifications instead of requiring one universal key.

No raw candidate key bytes are printed. Candidates are reported by offset,
virtual address, entropy, and SHA-256.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_secoc_oracle import (  # noqa: E402
    ProtectedSample,
    SyncSample,
    iter_key_windows,
    load_capture,
    verify_key,
    verify_protected_sample,
    verify_sync_sample,
)

DEFAULT_BASE = 0xFF200000
LAYOUT_CSV = REPO / "data/dataflash_nvm_records.csv"
REFERENCE_DUMP = REPO / "firmware/RH850_P1M-E_DataFlash.bin"
REFERENCE_OUTPUT = REPO / "data/generated/dataflash_structural_analysis_4512000.json"
OBJECT15_RELATED_VARIANT_ADDRESS = 0xFF206E14
OBJECT15_RELATED_VARIANT_SHA256_PREFIX = "1d1c53a6d634016a"

ENCODING_MASKS = {"raw": 0x00, "xor55": 0x55, "xoraa": 0xAA}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((count / n) * math.log2(count / n) for count in counts.values())


def load_layout(path: Path = LAYOUT_CSV) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def record_bytes(dump: bytes, row: dict[str, str], base_address: int) -> bytes:
    start = int(row["va_start"], 0) - base_address
    allocation = int(row["allocation_bytes"])
    if start < 0 or start + allocation > len(dump):
        raise ValueError(
            f"dump does not cover configured record {row['storage_index']} "
            f"at {row['va_start']} ({allocation} bytes)"
        )
    return dump[start : start + allocation]


def analyze_physical_record(dump: bytes, row: dict[str, str], base_address: int) -> dict[str, object]:
    raw = record_bytes(dump, row, base_address)
    expected_index = int(row["storage_index"])
    header_index = int.from_bytes(raw[0:2], "little")
    header_word1 = int.from_bytes(raw[2:4], "little")
    trailer = raw[-4:]
    valid = header_index == expected_index and trailer == b"\xAA" * 4
    return {
        "storage_index": expected_index,
        "va_start": row["va_start"],
        "allocation_bytes": len(raw),
        "payload_length": int(row["payload_length"]),
        "header_index": f"0x{header_index:04X}",
        "expected_header_index": f"0x{expected_index:04X}",
        "header_index_matches": header_index == expected_index,
        "opaque_header_word1": f"0x{header_word1:04X}",
        "trailer": trailer.hex(),
        "trailer_committed_marker": trailer == b"\xAA" * 4,
        "observable_valid": valid,
        "integrity_boundary": (
            "header word at +2 is retained as opaque; firmware-static work has not proved it is a checksum"
        ),
    }


def decode_triplicate_payload(dump: bytes, row: dict[str, str], base_address: int) -> tuple[bytes, dict[str, object]]:
    raw = record_bytes(dump, row, base_address)
    length = int(row["payload_length"])
    encoded = raw[4 : 4 + length]
    encoding = row["copy_encoding"]
    if encoding not in ENCODING_MASKS:
        raise ValueError(f"unknown triplicate encoding {encoding!r}")
    mask = ENCODING_MASKS[encoding]
    decoded = bytes(value ^ mask for value in encoded)
    physical = analyze_physical_record(dump, row, base_address)
    return decoded, {
        **physical,
        "nvm_jobs": row["nvm_jobs"],
        "copy_encoding": encoding,
        "decoded_payload_sha256": sha256(decoded),
        "decoded_payload_entropy": entropy(decoded),
    }


def analyze_triplicate_objects(dump: bytes, base_address: int = DEFAULT_BASE) -> list[dict[str, object]]:
    rows = [
        row for row in load_layout()
        if row["owner_class"] == "triplicate" and row["owner_enabled"] == "yes"
    ]
    by_object: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_object[int(row["secoc_object"])].append(row)

    objects = []
    for object_id, copies in sorted(by_object.items()):
        copies.sort(key=lambda row: {"raw": 0, "xor55": 1, "xoraa": 2}[row["copy_encoding"]])
        decoded_values = []
        copy_reports = []
        for row in copies:
            decoded, report = decode_triplicate_payload(dump, row, base_address)
            decoded_values.append(decoded)
            if object_id == 15 and len(decoded) >= 32:
                field = decoded[16:32]
                record_start = int(row["va_start"], 0)
                report["second_field_address"] = f"0x{record_start + 0x14:08X}"
                report["second_field_sha256"] = sha256(field)
                report["second_field_entropy"] = entropy(field)
            copy_reports.append(report)

        valid_values = [
            decoded for decoded, report in zip(decoded_values, copy_reports)
            if report["observable_valid"]
        ]
        counts = Counter(decoded_values)
        consensus_value, consensus_count = counts.most_common(1)[0]
        valid_counts = Counter(valid_values)
        valid_consensus_count = valid_counts.most_common(1)[0][1] if valid_counts else 0
        obj = {
            "object": object_id,
            "payload_length": int(copies[0]["payload_length"]),
            "copy_count": len(copies),
            "valid_copy_count": len(valid_values),
            "all_decoded_copies_equal": len(counts) == 1,
            "decoded_consensus_count": consensus_count,
            "valid_decoded_consensus_count": valid_consensus_count,
            "valid_consensus": bool(valid_values) and valid_consensus_count >= 2,
            "consensus_payload_sha256": sha256(consensus_value) if consensus_count >= 2 else None,
            "copies": copy_reports,
        }
        if object_id == 15:
            raw = next(report for report in copy_reports if report["copy_encoding"] == "raw")
            obj["known_key_field_geometry"] = {
                "raw": "0xFF206E14",
                "xor55": "0xFF206D14",
                "xoraa": "0xFF206C14",
                "ram_after_restore": "0xFEBF02F8",
                "related_8965B4514000_observed_raw_address": f"0x{OBJECT15_RELATED_VARIANT_ADDRESS:08X}",
                "related_8965B4514000_reported_key_sha256_prefix": OBJECT15_RELATED_VARIANT_SHA256_PREFIX,
                "geometry_alignment": raw.get("second_field_address") == "0xFF206E14",
                "runtime_key_equivalence": "unproven",
            }
        objects.append(obj)
    return objects


def entropy_ranked_windows(dump: bytes, base_address: int, limit: int = 100) -> dict[str, object]:
    ranked = sorted(
        iter_key_windows(dump, min_entropy=0.0),
        key=lambda item: (-item[2], item[0]),
    )
    output = []
    for offset, key, h in ranked[:limit]:
        output.append({
            "offset": offset,
            "address": f"0x{base_address + offset:08X}",
            "entropy": h,
            "sha256": sha256(key),
        })
    return {
        "sliding_window_count": max(0, len(dump) - 15),
        "unique_window_count": len(ranked),
        "rank_limit": limit,
        "ranked": output,
    }


def passing_protected_ids(verification: dict[str, object], threshold: float) -> list[int]:
    passing = []
    for can_id, result in verification["protected"].items():
        if result["total"] and result["matches"] / result["total"] >= threshold:
            passing.append(int(can_id, 0))
    return sorted(passing)


def classify_verification(
    verification: dict[str, object], *, sync_threshold: float = 0.98, protected_threshold: float = 0.98
) -> dict[str, object]:
    sync = verification["sync"]
    sync_pass = bool(sync["total"]) and sync["matches"] / sync["total"] >= sync_threshold
    protected = passing_protected_ids(verification, protected_threshold)

    if sync_pass and protected:
        label = "common sync+protected"
    elif sync_pass:
        label = "sync only"
    elif len(protected) == 1:
        label = f"0x{protected[0]:03X} only"
    elif protected == [0x116, 0x24D]:
        label = "common 0x116+0x24D"
    elif protected:
        label = "common protected " + "+".join(f"0x{x:03X}" for x in protected)
    else:
        label = "no cryptographic evidence"
    return {
        "classification": label,
        "sync_pass": sync_pass,
        "protected_ids_passing": [f"0x{x:03X}" for x in protected],
    }


def grouped_protected(samples: list[ProtectedSample]) -> dict[int, list[ProtectedSample]]:
    result: dict[int, list[ProtectedSample]] = defaultdict(list)
    for sample in samples:
        result[sample.can_id].append(sample)
    return result


def candidate_passes_any_probe(
    key: bytes,
    sync_samples: list[SyncSample],
    protected_samples: list[ProtectedSample],
) -> bool:
    if sync_samples and verify_sync_sample(key, sync_samples[0]):
        return True
    for samples in grouped_protected(protected_samples).values():
        if samples and verify_protected_sample(key, samples[0])[0]:
            return True
    return False


def scan_key_domains(
    dump: bytes,
    sync_samples: list[SyncSample],
    protected_samples: list[ProtectedSample],
    *,
    base_address: int = DEFAULT_BASE,
    min_entropy: float = 3.0,
    sync_threshold: float = 0.98,
    protected_threshold: float = 0.98,
) -> dict[str, object]:
    matches = []
    candidates_tested = 0
    for offset, key, h in iter_key_windows(dump, min_entropy=min_entropy):
        candidates_tested += 1
        if not candidate_passes_any_probe(key, sync_samples, protected_samples):
            continue
        verification = verify_key(key, sync_samples, protected_samples)
        classification = classify_verification(
            verification,
            sync_threshold=sync_threshold,
            protected_threshold=protected_threshold,
        )
        if classification["classification"] == "no cryptographic evidence":
            continue
        matches.append({
            "offset": offset,
            "address": f"0x{base_address + offset:08X}",
            "entropy": h,
            "sha256": sha256(key),
            "verification": verification,
            **classification,
        })
    return {
        "candidates_tested": candidates_tested,
        "min_entropy": min_entropy,
        "matches": matches,
    }


def analyze(
    dump_path: Path,
    *,
    base_address: int = DEFAULT_BASE,
    rank_limit: int = 100,
    capture_path: Path | None = None,
    min_entropy: float = 3.0,
    domain_scan: bool = False,
) -> dict[str, object]:
    dump = dump_path.read_bytes()
    try:
        display_dump = str(dump_path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        display_dump = str(dump_path.resolve())
    result: dict[str, object] = {
        "schema_version": 1,
        "dump": display_dump,
        "dump_sha256": sha256(dump),
        "base_address": f"0x{base_address:08X}",
        "size": len(dump),
        "entropy_windows": entropy_ranked_windows(dump, base_address, rank_limit),
        "triplicate_objects": analyze_triplicate_objects(dump, base_address),
        "physical_validity_model": {
            "valid_when": "first u16 == configured storage index AND final u32 == 0xAAAAAAAA",
            "opaque_field": "record header u16 at +2 is retained but not named as CRC/checksum",
        },
    }
    if capture_path is not None:
        sync_samples, protected_samples, summary = load_capture(capture_path)
        try:
            display_capture = str(capture_path.resolve().relative_to(REPO.resolve()))
        except ValueError:
            display_capture = str(capture_path.resolve())
        result["capture"] = {
            "path": display_capture,
            "sync_samples": len(sync_samples),
            "protected_samples": len(protected_samples),
            "summary": summary,
        }
        if domain_scan:
            result["key_domain_scan"] = scan_key_domains(
                dump,
                sync_samples,
                protected_samples,
                base_address=base_address,
                min_entropy=min_entropy,
            )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump", type=Path)
    parser.add_argument("--base-address", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--domain-scan", action="store_true", help="test every unique high-entropy 16-byte window across sync and each protected ID")
    parser.add_argument("--min-entropy", type=float, default=3.0)
    parser.add_argument("--rank-limit", type=int, default=100)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = analyze(
        args.dump,
        base_address=args.base_address,
        rank_limit=args.rank_limit,
        capture_path=args.capture,
        min_entropy=args.min_entropy,
        domain_scan=args.domain_scan,
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
