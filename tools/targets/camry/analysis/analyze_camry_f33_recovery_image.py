#!/usr/bin/env python3
"""Compare a saved F33 CodeFlash image with the exact retained factory baseline.

Offline only: no vehicle transport, image modification, payload generation or
programming authorization. An image comparison never establishes ECU liveness.
Exit 0 means exact baseline equality; every difference, including a native
programming-counter difference, exits 1 and remains visible in the JSON report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from collections.abc import Sequence
from itertools import pairwise
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
STOCK_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
IMAGE_SIZE = 0x100000


def _spans(offsets: list[int]) -> list[dict[str, int]]:
    result: list[dict[str, int]] = []
    for offset in offsets:
        if result and result[-1]["end_exclusive"] == offset:
            result[-1]["end_exclusive"] += 1
        else:
            result.append({"start": offset, "end_exclusive": offset + 1})
    return result


def _factory_lookup_identity(factory: bytes) -> dict[str, Any]:
    """Read the reviewed 0105 backing object, not a guessed serial-number prefix.

    The caller has already verified the complete factory-reference hash. These
    are archived lookup inputs, never substituted for a live diagnostic reply.
    """
    descriptor = 0x2AF8C + 4 * 12  # 0105 -> object 0204 -> ROM-object index 4.
    length = struct.unpack_from("<H", factory, descriptor)[0]
    address = struct.unpack_from("<I", factory, descriptor + 8)[0]
    block = factory[address : address + length + 4]
    marker = struct.unpack_from("<I", block)[0]
    crc = zlib.crc32(block)
    if length != 16 or marker != 0xA55A5AA5 or crc != 0xFFFFFFFF:
        raise ValueError("The retained assembly-number object failed validation")
    return {
        "scope": "Original saved factory dump only; not a live response or proof of package availability.",
        "ecu_assembly_number": block[4:14].decode("ascii"),
        "base_software_numbers": [
            factory[offset : offset + 16].split(b"\0", 1)[0].decode("ascii")
            for offset in (0x20860, 0x17DC0)
        ],
        "assembly_did": 0x0105,
        "assembly_object": 0x0204,
        "assembly_descriptor_address": descriptor,
        "assembly_storage_address": address,
        "assembly_object_crc32_with_checkword": crc,
        "live_identity_verified": False,
        "matching_calibration_package_evaluated": False,
    }


def compare_image(candidate: bytes, factory: bytes) -> dict[str, Any]:
    """Describe all differences; never treat a counter exception as exact equality."""
    if len(candidate) != IMAGE_SIZE:
        raise ValueError(
            f"Expected a complete {IMAGE_SIZE}-byte CodeFlash image; got {len(candidate)}"
        )
    if hashlib.sha256(factory).hexdigest() != STOCK_SHA256:
        raise ValueError(
            "The reference is not the reviewed 8965F3307000 factory baseline"
        )

    # Exact-target native descriptors, not fields supplied by the candidate image.
    descriptors = [
        struct.unpack_from("<7I", factory, 0x8E00 + i * 28) for i in range(2)
    ]
    crc_ranges = []
    counters = []
    counter_offsets: set[int] = set()
    for descriptor in descriptors:
        crc_start, crc_length = struct.unpack_from("<2I", factory, descriptor[6])
        crc_ranges.append((crc_start, crc_start + crc_length))
        address = descriptor[4]
        counter_offsets.update(range(address, address + 4))
        counters.append(
            {
                "address": address,
                "factory_value": struct.unpack_from("<I", factory, address)[0],
                "candidate_value": struct.unpack_from("<I", candidate, address)[0],
            }
        )

    # The actual sector lookup consumes these 39 ascending boundaries (38 blocks).
    boundaries = struct.unpack_from("<39I", factory, 0x86EC)
    upper_start, upper_end_inclusive = descriptors[1][:2]
    first_sector = next(a for a, b in pairwise(boundaries) if a <= upper_start < b)
    last_sector_end = next(
        b for a, b in pairwise(boundaries) if a <= upper_end_inclusive < b
    )
    diffs = [
        i for i, (a, b) in enumerate(zip(candidate, factory, strict=True)) if a != b
    ]
    counter_diffs = [i for i in diffs if i in counter_offsets]
    other_diffs = [i for i in diffs if i not in counter_offsets]
    crc_diffs = [i for i in diffs if any(start <= i < end for start, end in crc_ranges)]
    return {
        "schema": "camry-f33-saved-codeflash-comparison-v1",
        "scope": "Offline saved-image comparison only; no live contents, execution, repair, or roadworthiness established.",
        "factory_sha256": STOCK_SHA256,
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "retained_factory_calibration_lookup": _factory_lookup_identity(factory),
        "size": len(candidate),
        "exact_factory_codeflash": not diffs,
        "matches_factory_outside_native_counter_words": not other_diffs,
        "counter_values_verified_against_live_programming_history": False,
        "native_counter_words": counters,
        "native_crc_input_ranges": [
            {"start": a, "end_exclusive": b} for a, b in crc_ranges
        ],
        "native_upper_region_erase_extent": {
            "start": first_sector,
            "end_exclusive": last_sector_end,
        },
        "different_bytes": len(diffs),
        "different_bytes_in_native_counter_words": len(counter_diffs),
        "different_bytes_outside_native_counter_words": len(other_diffs),
        "different_bytes_in_native_crc_inputs": len(crc_diffs),
        "different_bytes_outside_native_crc_inputs": len(diffs) - len(crc_diffs),
        "all_differences_within_upper_region_erase_extent": all(
            first_sector <= i < last_sector_end for i in diffs
        ),
        "difference_spans": _spans(diffs),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "image",
        type=Path,
        help="A complete saved CodeFlash image; no device reads are performed",
    )
    parser.add_argument(
        "--factory", type=Path, default=STOCK, help="Exact retained factory baseline"
    )
    args = parser.parse_args(argv)
    try:
        result = compare_image(args.image.read_bytes(), args.factory.read_bytes())
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["exact_factory_codeflash"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
