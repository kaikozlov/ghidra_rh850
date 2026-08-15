#!/usr/bin/env python3
"""Build a fail-closed SecOC patch manifest from semantic resolver output.

The semantic target is produced by ResolveSecocAcceptanceGate.java. This tool
adds image identity, verifies the expected patch bytes against the supplied
CodeFlash image, and dynamically discovers the boot CRC descriptor covering the
patch. It does not contain Sienna patch, MAC-result, CRC-range, adjustment-word,
or marker addresses.

The CRC descriptor recognizer searches for 16-byte records:

    <region_start, region_length, embedded_start_ptr, embedded_length_ptr>

where dereferencing the final two fields inside the image reproduces the first
two fields. The terminal adjustment word is inferred as the last four bytes of
the CRC-covered region and validated with standard reflected CRC-32/Ethernet.

Usage:
  build_secoc_patch_manifest.py RESOLUTION.json CODEFLASH.bin -o manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
EXPECTED_CRC_RESIDUE = 0xFFFFFFFF
P1M_E_FCU_BLOCK_SIZE = 0x8000
VALIDITY_MARKER = 0x5AA5A55A
# RH850/P1M-E CodeFlash geometry. The semantic resolver and patch manifest
# are defined for a bare 1 MiB CodeFlash image imported at base 0. Public dump
# tools sometimes ship a DataFlash+CodeFlash concatenation whose 0x8000-byte
# DataFlash prefix shifts every CodeFlash VA by -0x8000; accepting it here would
# silently mis-resolve every target address.
P1M_E_CODEFLASH_SIZE = 0x100000
P1M_E_DATAFLASH_PREFIX_SIZE = 0x8000
CONCATENATED_DUMP_SIZE = P1M_E_CODEFLASH_SIZE + P1M_E_DATAFLASH_PREFIX_SIZE


def validate_codeflash_geometry(size: int) -> None:
    """Fail closed unless the image has the bare 1 MiB CodeFlash geometry."""
    if size < 0:
        raise ValueError("image size must not be negative")
    if size == P1M_E_CODEFLASH_SIZE:
        return
    if size == CONCATENATED_DUMP_SIZE:
        raise ValueError(
            f"image is {size} (0x{size:X}) bytes: this is the DataFlash+CodeFlash concatenated "
            f"dump geometry; strip the leading 0x{P1M_E_DATAFLASH_PREFIX_SIZE:X} DataFlash bytes "
            f"and supply the bare 0x{P1M_E_CODEFLASH_SIZE:X}-byte CodeFlash image"
        )
    raise ValueError(
        f"unexpected CodeFlash image geometry: {size} (0x{size:X}) bytes; expected exactly "
        f"0x{P1M_E_CODEFLASH_SIZE:X} (1 MiB) RH850/P1M-E CodeFlash — reject truncated or oversized images"
    )


@dataclass(frozen=True)
class CrcDescriptor:
    descriptor_va: int
    start: int
    length: int
    end: int
    embedded_start_va: int
    embedded_length_va: int
    fixup_va: int
    stored_fixup: int
    prefix_crc: int
    expected_fixup: int
    full_crc: int
    terminal_fixup_valid: bool
    validity_marker_va: int | None


def parse_int(value: str) -> int:
    return int(value, 0)


def va_to_offset(va: int, image_base: int, size: int, width: int = 1) -> int | None:
    off = va - image_base
    if off < 0 or off + width > size:
        return None
    return off


def u32_at_va(blob: bytes, va: int, image_base: int) -> int | None:
    off = va_to_offset(va, image_base, len(blob), 4)
    if off is None:
        return None
    return struct.unpack_from("<I", blob, off)[0]


def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def discover_crc_descriptors(blob: bytes, image_base: int) -> list[CrcDescriptor]:
    out: list[CrcDescriptor] = []
    size = len(blob)
    for off in range(0, size - 16 + 1, 4):
        start, length, embedded_start, embedded_length = struct.unpack_from("<IIII", blob, off)
        if length < 4:
            continue
        start_off = va_to_offset(start, image_base, size)
        end_off = va_to_offset(start + length, image_base, size, 0)
        if start_off is None or end_off is None or end_off <= start_off:
            continue
        if u32_at_va(blob, embedded_start, image_base) != start:
            continue
        if u32_at_va(blob, embedded_length, image_base) != length:
            continue

        end = start + length
        fixup = end - 4
        fixup_off = va_to_offset(fixup, image_base, size, 4)
        if fixup_off is None:
            continue
        prefix = blob[start_off:fixup_off]
        full = blob[start_off:end_off]
        prefix_value = crc32(prefix)
        stored = struct.unpack_from("<I", blob, fixup_off)[0]
        expected = prefix_value ^ 0xFFFFFFFF
        residue = crc32(full)

        marker_va: int | None = None
        # Do not assume a fixed marker offset. Search a short aligned trailer
        # after the CRC region for the known boot-validity marker value.
        for delta in range(0, 0x40, 4):
            candidate = end + delta
            if u32_at_va(blob, candidate, image_base) == VALIDITY_MARKER:
                marker_va = candidate
                break

        out.append(CrcDescriptor(
            descriptor_va=image_base + off,
            start=start,
            length=length,
            end=end,
            embedded_start_va=embedded_start,
            embedded_length_va=embedded_length,
            fixup_va=fixup,
            stored_fixup=stored,
            prefix_crc=prefix_value,
            expected_fixup=expected,
            full_crc=residue,
            terminal_fixup_valid=(stored == expected and residue == EXPECTED_CRC_RESIDUE),
            validity_marker_va=marker_va,
        ))
    return out


def patch_bytes(blob: bytes, patch_va: int, original: bytes, replacement: bytes, image_base: int) -> bytes:
    if len(original) != len(replacement) or not original:
        raise ValueError("patch original/replacement lengths must match and be non-zero")
    off = va_to_offset(patch_va, image_base, len(blob), len(original))
    if off is None:
        raise ValueError(f"patch VA 0x{patch_va:X} is outside supplied image")
    actual = blob[off:off + len(original)]
    if actual != original:
        raise ValueError(
            f"patch preimage mismatch at 0x{patch_va:X}: expected {original.hex()}, got {actual.hex()}"
        )
    out = bytearray(blob)
    out[off:off + len(original)] = replacement
    return bytes(out)


def build_manifest(resolution: dict[str, Any], image: Path, image_base: int) -> dict[str, Any]:
    if resolution.get("schema") != "toyota-secoc-semantic-target-v1":
        raise ValueError("unsupported semantic resolver schema")
    if resolution.get("resolution") != "unique" or resolution.get("candidate_count") != 1:
        raise ValueError("semantic target did not resolve uniquely")

    blob = image.read_bytes()
    validate_codeflash_geometry(len(blob))
    image_sha256 = hashlib.sha256(blob).hexdigest()
    program_sha256 = resolution.get("program_sha256")
    if not program_sha256:
        raise ValueError("semantic resolution is missing program_sha256")
    if program_sha256.lower() != image_sha256.lower():
        raise ValueError(
            f"semantic-resolution/image SHA-256 mismatch: resolver={program_sha256} image={image_sha256}"
        )

    patch = resolution["patch"]
    patch_va = parse_int(patch["address"])
    original = bytes.fromhex(patch["original"])
    replacement = bytes.fromhex(patch["replacement"])
    patched = patch_bytes(blob, patch_va, original, replacement, image_base)

    descriptors = discover_crc_descriptors(blob, image_base)
    covering = [d for d in descriptors if d.start <= patch_va < d.end]
    if len(covering) != 1:
        raise ValueError(
            f"expected exactly one self-describing CRC region covering patch 0x{patch_va:X}; found {len(covering)}"
        )
    crc = covering[0]

    validated_siblings = [
        d for d in descriptors if d.descriptor_va != crc.descriptor_va and d.terminal_fixup_valid
    ]
    if not crc.terminal_fixup_valid and not validated_siblings:
        raise ValueError(
            "target CRC region does not validate and no sibling descriptor proves the terminal-fixup scheme"
        )

    start_off = va_to_offset(crc.start, image_base, len(blob))
    fixup_off = va_to_offset(crc.fixup_va, image_base, len(blob), 4)
    end_off = va_to_offset(crc.end, image_base, len(blob), 0)
    assert start_off is not None and fixup_off is not None and end_off is not None

    patched_prefix_crc = crc32(patched[start_off:fixup_off])
    patched_fixup = patched_prefix_crc ^ 0xFFFFFFFF
    offline_resigned = bytearray(patched)
    struct.pack_into("<I", offline_resigned, fixup_off, patched_fixup)
    patched_residue = crc32(offline_resigned[start_off:end_off])
    if patched_residue != EXPECTED_CRC_RESIDUE:
        raise ValueError(f"internal CRC resigning failure: residue 0x{patched_residue:08X}")

    block_base = patch_va & ~(P1M_E_FCU_BLOCK_SIZE - 1)
    crc_block_base = crc.fixup_va & ~(P1M_E_FCU_BLOCK_SIZE - 1)

    try:
        display_image = str(image.resolve().relative_to(REPO.resolve()))
    except ValueError:
        display_image = str(image.resolve())

    manifest: dict[str, Any] = {
        "schema": "toyota-secoc-patch-manifest-v1",
        "backend": "rh850-p1m-e-fcu",
        "image": {
            "path": display_image,
            "sha256": image_sha256,
            "size": len(blob),
            "base": f"0x{image_base:X}",
        },
        "semantic_resolution": resolution,
        "patch": {
            "address": f"0x{patch_va:X}",
            "original": original.hex(),
            "replacement": replacement.hex(),
            "block_base": f"0x{block_base:X}",
            "block_size": P1M_E_FCU_BLOCK_SIZE,
            "preimage_verified": True,
        },
        "boot_crc": {
            "descriptor_va": f"0x{crc.descriptor_va:X}",
            "start": f"0x{crc.start:X}",
            "end": f"0x{crc.end:X}",
            "length": crc.length,
            "embedded_start_va": f"0x{crc.embedded_start_va:X}",
            "embedded_length_va": f"0x{crc.embedded_length_va:X}",
            "fixup_va": f"0x{crc.fixup_va:X}",
            "fixup_block_base": f"0x{crc_block_base:X}",
            "stored_fixup": f"0x{crc.stored_fixup:08X}",
            "stock_prefix_crc": f"0x{crc.prefix_crc:08X}",
            "stock_expected_fixup": f"0x{crc.expected_fixup:08X}",
            "stock_residue": f"0x{crc.full_crc:08X}",
            "stock_region_valid": crc.terminal_fixup_valid,
            "validated_sibling_descriptor_count": len(validated_siblings),
            "validity_marker_va": None if crc.validity_marker_va is None else f"0x{crc.validity_marker_va:X}",
            "patched_prefix_crc_for_supplied_image": f"0x{patched_prefix_crc:08X}",
            "patched_fixup_for_supplied_image": f"0x{patched_fixup:08X}",
            "patched_residue_for_supplied_image": f"0x{patched_residue:08X}",
            "live_policy": (
                "recompute prefix CRC from live CodeFlash after target-block RMW; "
                "write complement at discovered fixup VA; require final residue 0xFFFFFFFF"
            ),
        },
        "discovery": {
            "crc_descriptor_count": len(descriptors),
            "crc_descriptors": [
                {
                    **asdict(d),
                    "descriptor_va": f"0x{d.descriptor_va:X}",
                    "start": f"0x{d.start:X}",
                    "end": f"0x{d.end:X}",
                    "embedded_start_va": f"0x{d.embedded_start_va:X}",
                    "embedded_length_va": f"0x{d.embedded_length_va:X}",
                    "fixup_va": f"0x{d.fixup_va:X}",
                    "stored_fixup": f"0x{d.stored_fixup:08X}",
                    "prefix_crc": f"0x{d.prefix_crc:08X}",
                    "expected_fixup": f"0x{d.expected_fixup:08X}",
                    "full_crc": f"0x{d.full_crc:08X}",
                    "validity_marker_va": None if d.validity_marker_va is None else f"0x{d.validity_marker_va:X}",
                }
                for d in descriptors
            ],
        },
        "safety": {
            "fail_closed": True,
            "requirements": [
                "semantic resolver produced exactly one candidate",
                "patch preimage matches supplied image",
                "exactly one self-describing CRC descriptor covers patch",
                "target CRC scheme validates directly or via a valid sibling descriptor",
                "live patcher recomputes CRC from live flash rather than trusting offline fixup",
            ],
        },
    }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resolution", type=Path)
    parser.add_argument("image", type=Path)
    parser.add_argument("--image-base", type=parse_int, default=0)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    resolution = json.loads(args.resolution.read_text(encoding="utf-8"))
    manifest = build_manifest(resolution, args.image, args.image_base)
    text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
