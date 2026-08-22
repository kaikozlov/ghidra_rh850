#!/usr/bin/env python3
"""Prove same-address CodeFlash equivalence between two Corolla EPS specimens.

The report is deliberately byte-oriented.  It is intended to answer a narrow
question before any semantic transfer is attempted: which bytes are identical,
where are the exceptions, and do those exceptions cross the known Corolla
application boundary?
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.build_secoc_patch_manifest import discover_crc_descriptors  # noqa: E402

CODEFLASH_SIZE = 0x100000
RANGE_DUMP_SIZE = 0x200000
APPLICATION_START = 0x20000
COALESCE_EQUAL_GAP = 32

# Static roots and identity fields already established for the H-family image.
PINNED_RANGES = {
    "payload_build_secret": (0xBFD8, 0xBFE8),
    "boot_security_access_secret": (0xBFE8, 0xBFF8),
    "application_security_access_secret": (0x20840, 0x20850),
    "f181_primary_record": (0x20860, 0x20870),
    "f181_secondary_record": (0x17DC0, 0x17DD0),
    "single_record_identity": (0x17D80, 0x17D90),
    "serial": (0xA4DC, 0xA4F1),
}


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def source_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO))
    except ValueError:
        return str(resolved)


def load_codeflash(path: Path) -> tuple[bytes, dict]:
    raw = path.read_bytes()
    meta = {"path": source_path(path), "size": len(raw), "sha256": sha256(raw)}
    if len(raw) == CODEFLASH_SIZE:
        meta["normalization"] = "bare-codeflash"
        return raw, meta
    if len(raw) == RANGE_DUMP_SIZE and raw[CODEFLASH_SIZE:] == b"\xFF" * CODEFLASH_SIZE:
        meta["normalization"] = "trim-all-ff-upper-1mib-from-2mib-range-dump"
        return raw[:CODEFLASH_SIZE], meta
    raise ValueError(
        f"{path}: expected 1 MiB CodeFlash or 2 MiB range dump with all-FF upper MiB; got {len(raw):#x}"
    )


def runs(indices: list[int]) -> list[tuple[int, int]]:
    if not indices:
        return []
    out: list[tuple[int, int]] = []
    start = prev = indices[0]
    for value in indices[1:]:
        if value != prev + 1:
            out.append((start, prev + 1))
            start = value
        prev = value
    out.append((start, prev + 1))
    return out


def coalesced_runs(indices: list[int], equal_gap: int) -> list[tuple[int, int]]:
    if not indices:
        return []
    out: list[tuple[int, int]] = []
    start = prev = indices[0]
    for value in indices[1:]:
        if value - prev - 1 > equal_gap:
            out.append((start, prev + 1))
            start = value
        prev = value
    out.append((start, prev + 1))
    return out


def ascii_field(blob: bytes, start: int, end: int) -> str:
    return blob[start:end].split(b"\0", 1)[0].decode("ascii", errors="replace")


def crc_rows(blob: bytes) -> list[dict]:
    rows = []
    for row in discover_crc_descriptors(blob, 0):
        rows.append(
            {
                "descriptor_va": f"0x{row.descriptor_va:X}",
                "start": f"0x{row.start:X}",
                "end": f"0x{row.end:X}",
                "length": row.length,
                "fixup_va": f"0x{row.fixup_va:X}",
                "stored_fixup": f"0x{row.stored_fixup:08X}",
                "prefix_crc": f"0x{row.prefix_crc:08X}",
                "full_crc": f"0x{row.full_crc:08X}",
                "terminal_fixup_valid": row.terminal_fixup_valid,
            }
        )
    return rows


def build_report(baseline_path: Path, target_path: Path, baseline_id: str, target_id: str) -> dict:
    baseline, baseline_source = load_codeflash(baseline_path)
    target, target_source = load_codeflash(target_path)
    changed = [i for i, (a, b) in enumerate(zip(baseline, target)) if a != b]
    exact_runs = runs(changed)
    merged = coalesced_runs(changed, COALESCE_EQUAL_GAP)

    region_rows = []
    for start, end in merged:
        region_rows.append(
            {
                "start": f"0x{start:X}",
                "end_exclusive": f"0x{end:X}",
                "span": end - start,
                "changed_bytes": sum(baseline[i] != target[i] for i in range(start, end)),
            }
        )

    pinned = {}
    for name, (start, end) in PINNED_RANGES.items():
        pinned[name] = {
            "start": f"0x{start:X}",
            "end_exclusive": f"0x{end:X}",
            "identical": baseline[start:end] == target[start:end],
            "baseline_sha256": sha256(baseline[start:end]),
            "target_sha256": sha256(target[start:end]),
        }
    for name in ("f181_primary_record", "f181_secondary_record", "single_record_identity", "serial"):
        start, end = PINNED_RANGES[name]
        pinned[name]["baseline_ascii"] = ascii_field(baseline, start, end)
        pinned[name]["target_ascii"] = ascii_field(target, start, end)

    return {
        "schema": "toyota-corolla-codeflash-equivalence-v1",
        "baseline_id": baseline_id,
        "target_id": target_id,
        "baseline": {**baseline_source, "normalized_sha256": sha256(baseline)},
        "target": {**target_source, "normalized_sha256": sha256(target)},
        "comparison": {
            "total_bytes": CODEFLASH_SIZE,
            "identical_bytes": CODEFLASH_SIZE - len(changed),
            "different_bytes": len(changed),
            "identical_fraction": round((CODEFLASH_SIZE - len(changed)) / CODEFLASH_SIZE, 9),
            "first_difference": None if not changed else f"0x{changed[0]:X}",
            "last_difference": None if not changed else f"0x{changed[-1]:X}",
            "exact_changed_run_count": len(exact_runs),
            "coalesced_equal_gap_max": COALESCE_EQUAL_GAP,
            "coalesced_region_count": len(merged),
            "coalesced_regions": region_rows,
        },
        "application_equivalence": {
            "start": f"0x{APPLICATION_START:X}",
            "end_exclusive": f"0x{CODEFLASH_SIZE:X}",
            "size": CODEFLASH_SIZE - APPLICATION_START,
            "identical": baseline[APPLICATION_START:] == target[APPLICATION_START:],
            "baseline_sha256": sha256(baseline[APPLICATION_START:]),
            "target_sha256": sha256(target[APPLICATION_START:]),
            "different_bytes": sum(a != b for a, b in zip(baseline[APPLICATION_START:], target[APPLICATION_START:])),
        },
        "changed_byte_buckets_64k": {
            f"0x{bucket << 16:05X}-0x{((bucket + 1) << 16) - 1:05X}": sum((i >> 16) == bucket for i in changed)
            for bucket in sorted({i >> 16 for i in changed})
        },
        "pinned_ranges": pinned,
        "crc_descriptors": {
            "baseline": crc_rows(baseline),
            "target": crc_rows(target),
        },
        "interpretation_boundary": {
            "exact_application_byte_identity_allows_semantic_transfer": baseline[APPLICATION_START:] == target[APPLICATION_START:],
            "low_region_differences_require_independent_data_calibration_identity_audit": bool(changed and changed[0] < APPLICATION_START),
            "note": "Byte identity proves code/configuration equality only for the exact covered ranges. Low-region differences are retained explicitly and must not be erased by whole-variant semantic inheritance.",
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--baseline-id", required=True)
    p.add_argument("--target-id", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    report = build_report(args.baseline, args.target, args.baseline_id, args.target_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["comparison"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
