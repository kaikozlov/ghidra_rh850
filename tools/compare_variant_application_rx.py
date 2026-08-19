#!/usr/bin/env python3
"""Compare generated normal application Rx descriptor tables across CodeFlash images.

The table shape is a contiguous run of eight-byte ``software_id:u32,length:u32``
records.  Standard-CAN descriptors use the low 11 bits; bit 30 marks CAN-FD in
these images.  Length is 1, 8, or 32 bytes.  The longest valid run is selected
and must be unique at its maximal length.

This is intentionally a raw-CodeFlash configuration comparison.  It does not
assign signal semantics to IDs that happen to retain the same numeric signal
index across calibrations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.build_ephemeral_runtime_manifest import load_codeflash  # noqa: E402

SCHEMA = "rh850-cross-image-application-rx-descriptor-diff-v1"
_ALLOWED_LENGTHS = {1, 8, 32}
_ALLOWED_SOFTWARE_ID_MASK = 0x400007FF
_FD_MARKER = 0x40000000


def _sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _valid_record(blob: bytes, offset: int) -> tuple[int, int] | None:
    if offset < 0 or offset + 8 > len(blob):
        return None
    software_id, length = struct.unpack_from("<II", blob, offset)
    if software_id & ~_ALLOWED_SOFTWARE_ID_MASK:
        return None
    if (software_id & 0x7FF) > 0x7FF or length not in _ALLOWED_LENGTHS:
        return None
    return software_id, length


def find_normal_rx_descriptor_table(blob: bytes) -> tuple[int, list[tuple[int, int]]]:
    candidates: list[tuple[int, int]] = []
    for start in range(0, len(blob) - 7, 4):
        count = 0
        while _valid_record(blob, start + count * 8) is not None:
            count += 1
        if count >= 8:
            candidates.append((count, start))
    if not candidates:
        raise ValueError("no normal-Rx descriptor run found")
    max_count = max(count for count, _ in candidates)
    maximal = sorted(start for count, start in candidates if count == max_count)
    if len(maximal) != 1:
        raise ValueError(
            f"normal-Rx descriptor run is ambiguous: count={max_count} starts={maximal}"
        )
    start = maximal[0]
    records = [_valid_record(blob, start + i * 8) for i in range(max_count)]
    assert all(record is not None for record in records)
    return start, [record for record in records if record is not None]


def _record_dict(index: int, record: tuple[int, int]) -> dict[str, Any]:
    software_id, length = record
    return {
        "index": index,
        "software_id": f"0x{software_id:08X}",
        "can_id": f"0x{software_id & 0x7FF:03X}",
        "length": length,
        "can_fd": bool(software_id & _FD_MARKER),
    }


def _key(record: tuple[int, int]) -> tuple[int, int, bool]:
    software_id, length = record
    return software_id & 0x7FF, length, bool(software_id & _FD_MARKER)


def compare(
    reference: bytes,
    target: bytes,
    *,
    reference_id: str,
    target_id: str,
    target_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ref_start, ref_records = find_normal_rx_descriptor_table(reference)
    target_start, target_records = find_normal_rx_descriptor_table(target)
    ref_keys = [_key(record) for record in ref_records]
    target_keys = [_key(record) for record in target_records]
    target_set = set(target_keys)
    ref_set = set(ref_keys)

    removed = [
        _record_dict(index, record)
        for index, record in enumerate(ref_records)
        if _key(record) not in target_set
    ]
    added = [
        _record_dict(index, record)
        for index, record in enumerate(target_records)
        if _key(record) not in ref_set
    ]
    common = [
        _record_dict(index, record)
        for index, record in enumerate(target_records)
        if _key(record) in ref_set
    ]
    return {
        "schema": SCHEMA,
        "evidence_boundary": (
            "Raw generated normal-Rx descriptor-table comparison only. Same CAN ID/length "
            "proves a shared configured receive descriptor, not identical downstream signal "
            "semantics, SecOC policy, hardware routing, or consumer behavior."
        ),
        "reference": {
            "id": reference_id,
            "sha256": _sha256(reference),
            "table_start": f"0x{ref_start:08X}",
            "descriptor_count": len(ref_records),
            "descriptors": [_record_dict(i, row) for i, row in enumerate(ref_records)],
        },
        "target": {
            "id": target_id,
            "sha256": _sha256(target),
            "source_sha256": None if target_source is None else target_source.get("sha256"),
            "source_size": None if target_source is None else target_source.get("size"),
            "normalization": None if target_source is None else target_source.get("normalization"),
            "table_start": f"0x{target_start:08X}",
            "descriptor_count": len(target_records),
            "descriptors": [_record_dict(i, row) for i, row in enumerate(target_records)],
        },
        "summary": {
            "shared_descriptor_count": len(common),
            "removed_descriptor_count": len(removed),
            "added_descriptor_count": len(added),
            "removed": removed,
            "added": added,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-image", type=Path, required=True)
    parser.add_argument("--target-image", type=Path, required=True)
    parser.add_argument("--reference-id", default="reference")
    parser.add_argument("--target-id", default="target")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    target, target_source = load_codeflash(args.target_image)
    report = compare(
        args.reference_image.read_bytes(),
        target,
        reference_id=args.reference_id,
        target_id=args.target_id,
        target_source=target_source,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "summary": report["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
