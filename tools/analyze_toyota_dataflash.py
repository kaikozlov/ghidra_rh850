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

try:
    from .sienna_target import DATAFLASH as SIENNA_DATAFLASH
except ImportError:  # direct script execution
    from sienna_target import DATAFLASH as SIENNA_DATAFLASH

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
CHECKPOINT_PAYLOAD_CSV = REPO / "data/checkpoint_payload_map.csv"
REFERENCE_DUMP = SIENNA_DATAFLASH
REFERENCE_OUTPUT = REPO / "data/generated/dataflash_structural_analysis_4512000.json"
OBJECT15_RELATED_VARIANT_ADDRESS = 0xFF206E14
OBJECT15_RELATED_VARIANT_SHA256_PREFIX = "1d1c53a6d634016a"

ENCODING_MASKS = {"raw": 0x00, "xor55": 0x55, "xoraa": 0xAA}
COMMIT_MARKER = b"\xAA" * 4
SHORT_BLOCK_CHECKSUM_LIMIT = 0x21
SHORT_BLOCK_CHECKSUM_BIAS = 0xC000
SHORT_BLOCK_CHECKSUM_BASE = SHORT_BLOCK_CHECKSUM_BIAS + sum(COMMIT_MARKER)  # 0xC2A8


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


def short_block_additive_checksum(storage_index: int, encoded_payload: bytes) -> int:
    """Reproduce the reader-enforced +2 checksum used by NvM payloads shorter than 0x21 bytes.

    Firmware helper 0x762C6 sums unsigned bytes. The committed-record path first
    validates/accumulates the four 0xAA trailer bytes (sum 0x2A8), then the two
    storage-index bytes and encoded payload, with a 0xC000 bias before the +2
    comparison. Cross-image validation yields the equivalent formula below for
    every committed short record in the 4512000 and albinoelephant dumps.
    """
    index_bytes = storage_index.to_bytes(2, "little", signed=False)
    return (SHORT_BLOCK_CHECKSUM_BASE + sum(index_bytes) + sum(encoded_payload)) & 0xFFFF


def analyze_physical_record(dump: bytes, row: dict[str, str], base_address: int) -> dict[str, object]:
    raw = record_bytes(dump, row, base_address)
    expected_index = int(row["storage_index"])
    payload_length = int(row["payload_length"])
    header_index = int.from_bytes(raw[0:2], "little")
    header_word1 = int.from_bytes(raw[2:4], "little")
    trailer = raw[-4:]
    marker_valid = header_index == expected_index and trailer == COMMIT_MARKER

    short_block = payload_length < SHORT_BLOCK_CHECKSUM_LIMIT
    checksum_expected: int | None = None
    checksum_matches: bool | None = None
    if short_block:
        checksum_expected = short_block_additive_checksum(
            expected_index, raw[4 : 4 + payload_length]
        )
        checksum_matches = header_word1 == checksum_expected

    # The short-block checksum is explicitly checked by the firmware read path
    # (0x7668A -> 0xFFFC on mismatch). Longer records skip that comparison; their
    # internal formats can impose separate integrity checks (for example the
    # checkpoint generation/complement envelope).
    valid = marker_valid and (checksum_matches is not False)
    return {
        "storage_index": expected_index,
        "va_start": row["va_start"],
        "allocation_bytes": len(raw),
        "payload_length": payload_length,
        "header_index": f"0x{header_index:04X}",
        "expected_header_index": f"0x{expected_index:04X}",
        "header_index_matches": header_index == expected_index,
        "header_word1": f"0x{header_word1:04X}",
        "header_word1_role": (
            "reader-enforced additive checksum" if short_block
            else "writer-formatted zero; short-block checksum path not used"
        ),
        "header_word1_expected": (
            f"0x{checksum_expected:04X}" if checksum_expected is not None else "0x0000"
        ),
        "header_word1_matches_expected": (
            checksum_matches if short_block else header_word1 == 0
        ),
        "header_word1_reader_enforced": short_block,
        "trailer": trailer.hex(),
        "trailer_committed_marker": trailer == COMMIT_MARKER,
        "observable_valid": valid,
        "integrity_boundary": (
            "short payloads (<0x21 bytes) require the additive +2 checksum on the firmware read path; "
            "longer records skip that read-side checksum and may have format-specific integrity"
        ),
    }


def load_checkpoint_data_lengths(path: Path = CHECKPOINT_PAYLOAD_CSV) -> dict[int, int]:
    with path.open(newline="", encoding="utf-8") as stream:
        return {
            int(row["object_index"]): int(row["data_length"])
            for row in csv.DictReader(stream)
        }


def analyze_reference_nvm_geometry(dump: bytes, base_address: int = DEFAULT_BASE) -> dict[str, object]:
    """Apply the 4512000 physical owner map without promoting its semantics to the target.

    The storage/page extents and owner indexes are reference geometry. A target image can
    independently corroborate that geometry by satisfying the outer commit markers and,
    for checkpoint-shaped records, the generation/complement envelope at the reference
    descriptor's inverse offset.
    """
    rows = load_layout()
    checkpoint_lengths = load_checkpoint_data_lengths()
    committed_by_class: Counter[str] = Counter()
    checkpoint_records = []

    for row in rows:
        physical = analyze_physical_record(dump, row, base_address)
        if not physical["observable_valid"]:
            continue
        committed_by_class[row["owner_class"]] += 1
        if row["owner_class"] != "checkpoint":
            continue

        raw = record_bytes(dump, row, base_address)
        owner_index = int(row["owner_index"])
        reference_data_length = checkpoint_lengths[owner_index]
        inverse_offset = 8 + max(reference_data_length, 56)
        generation = int.from_bytes(raw[4:8], "little")
        inverse = int.from_bytes(raw[inverse_offset : inverse_offset + 4], "little")
        envelope_valid = inverse == (~generation & 0xFFFFFFFF)
        checkpoint_records.append({
            "storage_index": int(row["storage_index"]),
            "va_start": row["va_start"],
            "reference_owner_index": owner_index,
            "reference_owner_enabled": row["owner_enabled"] == "yes",
            "reference_owner_slot": int(row["owner_slot"]),
            "reference_data_length": reference_data_length,
            "generation": f"0x{generation:08X}",
            "inverse_generation": f"0x{inverse:08X}",
            "inverse_offset": inverse_offset,
            "generation_complement_valid": envelope_valid,
            "nonzero_bytes_after_reference_data_before_inverse": sum(
                value != 0 for value in raw[8 + reference_data_length : inverse_offset]
            ),
        })

    disabled = [
        row for row in checkpoint_records
        if not row["reference_owner_enabled"] and row["generation_complement_valid"]
    ]
    return {
        "reference": "8965B4512000 data/dataflash_nvm_records.csv + checkpoint_payload_map.csv",
        "semantic_transfer": "unproven; owner indexes and data lengths are reference labels",
        "configured_physical_records": len(rows),
        "committed_records": sum(committed_by_class.values()),
        "committed_by_reference_owner_class": dict(sorted(committed_by_class.items())),
        "checkpoint_committed_records": len(checkpoint_records),
        "checkpoint_generation_complement_valid": sum(
            row["generation_complement_valid"] for row in checkpoint_records
        ),
        "reference_enabled_checkpoint_envelopes": sum(
            row["reference_owner_enabled"] and row["generation_complement_valid"]
            for row in checkpoint_records
        ),
        "reference_disabled_checkpoint_envelopes": disabled,
        "checkpoint_records": checkpoint_records,
    }


def reference_region_statistics(dump: bytes) -> list[dict[str, object]]:
    """Describe the four page ranges established by the 4512000 DataFlash geometry."""
    regions = (
        ("lower_unallocated_reference", 0x0000, 0x4000),
        ("checkpoint_reference", 0x4000, 0x6C00),
        ("triplicate_reference", 0x6C00, 0x7800),
        ("tail_protected_reference", 0x7800, 0x8000),
    )
    output = []
    for name, start, end in regions:
        region = dump[start:end]
        page_classes: Counter[str] = Counter()
        for offset in range(0, len(region), 64):
            page = region[offset : offset + 64]
            if page == b"\x00" * len(page):
                page_classes["all_00"] += 1
            elif page == b"\xFF" * len(page):
                page_classes["all_ff"] += 1
            elif set(page) <= {0x00, 0xFF}:
                page_classes["00_ff_only"] += 1
            else:
                page_classes["mixed"] += 1
        word_classes: Counter[str] = Counter()
        for offset in range(0, len(region), 4):
            word = region[offset : offset + 4]
            if word == b"\x00" * 4:
                word_classes["all_00"] += 1
            elif word == b"\xFF" * 4:
                word_classes["all_ff"] += 1
            else:
                word_classes["mixed"] += 1
        zero_bytes = region.count(0)
        ff_bytes = region.count(0xFF)
        output.append({
            "name": name,
            "offset_start": start,
            "offset_end_exclusive": end,
            "size": len(region),
            "page_classes": dict(sorted(page_classes.items())),
            "word_classes": dict(sorted(word_classes.items())),
            "zero_bytes": zero_bytes,
            "ff_bytes": ff_bytes,
            "other_bytes": len(region) - zero_bytes - ff_bytes,
            "distinct_byte_values": len(set(region)),
        })
    return output


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
    sync_probe: SyncSample | None,
    protected_probes: tuple[ProtectedSample, ...],
) -> bool:
    """Cheaply reject a key before the full capture verification.

    Probe selection is invariant across candidate keys.  Keep the selected
    samples outside the sliding-window loop so a large capture is not regrouped
    tens of thousands of times during an exhaustive DataFlash scan.
    """
    if sync_probe is not None and verify_sync_sample(key, sync_probe):
        return True
    return any(verify_protected_sample(key, sample)[0] for sample in protected_probes)


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
    sync_probe = sync_samples[0] if sync_samples else None
    protected_probes = tuple(
        samples[0]
        for samples in grouped_protected(protected_samples).values()
        if samples
    )
    for offset, key, h in iter_key_windows(dump, min_entropy=min_entropy):
        candidates_tested += 1
        if not candidate_passes_any_probe(key, sync_probe, protected_probes):
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
    physical_prefix_size: int | None = None,
) -> dict[str, object]:
    source_dump = dump_path.read_bytes()
    if physical_prefix_size is not None:
        if physical_prefix_size <= 0 or physical_prefix_size > len(source_dump):
            raise ValueError(
                f"physical prefix size must be within source dump: {physical_prefix_size:#x} vs {len(source_dump):#x}"
            )
        dump = source_dump[:physical_prefix_size]
    else:
        dump = source_dump
    try:
        display_dump = str(dump_path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        display_dump = str(dump_path.resolve())
    result: dict[str, object] = {
        "schema_version": 2,
        "dump": display_dump,
        "dump_sha256": sha256(dump),
        "base_address": f"0x{base_address:08X}",
        "size": len(dump),
        "entropy_windows": entropy_ranked_windows(dump, base_address, rank_limit),
        "reference_region_statistics": reference_region_statistics(dump),
        "reference_nvm_geometry": analyze_reference_nvm_geometry(dump, base_address),
        "triplicate_objects": analyze_triplicate_objects(dump, base_address),
        "physical_validity_model": {
            "committed_marker_rule": "first u16 == configured storage index AND final u32 == 0xAAAAAAAA",
            "short_block_integrity": (
                "for payload_length < 0x21, the read path accumulates the 0xAAAAAAAA trailer, "
                "storage-index bytes, and encoded payload, then 0x7668A requires header +2 == "
                "(0xC000 + sum(trailer bytes) + sum(storage-index bytes) + "
                "sum(encoded payload bytes)) mod 2^16; committed trailers reduce this to base 0xC2A8"
            ),
            "short_block_mismatch_result": "0xFFFC",
            "long_block_header": (
                "writer 0x765D0 formats header +2 as zero for payload_length >= 0x21; "
                "reader 0x7668A skips the short-block checksum comparison"
            ),
            "observable_valid_when": (
                "committed marker rule, plus the reader-enforced additive checksum for short blocks"
            ),
        },
    }
    if physical_prefix_size is not None:
        result["source_dump_sha256"] = sha256(source_dump)
        result["source_size"] = len(source_dump)
        result["normalization"] = f"physical-prefix-{physical_prefix_size:#x}"
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
    parser.add_argument(
        "--physical-prefix-size",
        type=lambda value: int(value, 0),
        help="analyze only this leading physical span while preserving source-dump provenance",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = analyze(
        args.dump,
        base_address=args.base_address,
        rank_limit=args.rank_limit,
        capture_path=args.capture,
        min_entropy=args.min_entropy,
        domain_scan=args.domain_scan,
        physical_prefix_size=args.physical_prefix_size,
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
