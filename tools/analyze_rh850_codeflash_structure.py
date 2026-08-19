#!/usr/bin/env python3
"""Offline RH850/P1M-E CodeFlash structural fingerprint scanner (triage only).

Scans a raw CodeFlash image for structural anchors already recovered on the
Sienna 8965B4512000 calibration:

- exact image geometry (bare 1 MiB CodeFlash vs DataFlash+CodeFlash dump);
- self-describing boot-CRC descriptors and the boot-validity marker value;
- RAM-exec gate / MEM-SAFE-001 structural immediates (download-window base,
  post-link package descriptor pair);
- XCP 0x7F7/0x7F8 route constants in both plain-u32 and the packed
  standard-ID descriptor representation observed on the tracked Corolla H,
  page-copy window/shadow constants, and eight-byte command-map records
  (selector byte + little-endian callback);
- a byte-level prefilter for the SecOC semantic gate resolver shape
  (32-bit-displacement byte loads feeding a cmov-family materialization).

Every match is a TRIAGE CANDIDATE. Nothing here proves that a mechanism
transfers to a new calibration, and the scanner deliberately contains no
per-calibration software-ID offset fallback table: identify targets by their
own structure, not by inherited offsets.

Usage:
  analyze_rh850_codeflash_structure.py IMAGE.bin [-o report.json] [--max-vas 16]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.build_secoc_patch_manifest import (  # noqa: E402
    CONCATENATED_DUMP_SIZE,
    P1M_E_CODEFLASH_SIZE,
    P1M_E_DATAFLASH_PREFIX_SIZE,
    VALIDITY_MARKER,
    discover_crc_descriptors,
)

SCHEMA = "rh850-codeflash-structure-triage-v1"
CODEFLASH_SIZE = P1M_E_CODEFLASH_SIZE

# Structural anchor constants. These are FAMILY/GATE anchors, not per-target
# patch offsets: boot-validity marker word, RAM-exec download-window base and
# its post-link package length, XCP CAN route pair, page-copy window end and
# shadow destination.
RAM_EXEC_WINDOW_BASE = 0xFEBF0000
RAM_EXEC_PACKAGE_LENGTH = 0x00000FF0
RAM_EXEC_CALLBACK_SLOT = 0xFEBF0FD0
XCP_REQUEST_CAN_ID = 0x7F7
XCP_RESPONSE_CAN_ID = 0x7F8
XCP_PAGE_COPY_WINDOW_END = 0x17DF0
XCP_PAGE_COPY_SHADOW_BASE = 0xFEBF7C00

# Command-map record shape: 8-byte records, selector byte at offset 0,
# little-endian callback pointer at offset 4 (recovered on Sienna at 0x2B3F0).
COMMAND_MAP_RECORD_SIZE = 8
COMMAND_MAP_MIN_RECORDS = 4
COMMAND_MAP_SELECTOR_MIN = 0xC0  # XCP standard/optional command-code space
COMMAND_MAP_SELECTOR_MAX = 0xFF
COMMAND_MAP_POINTER_MIN = 0x1000

# Byte-level SecOC resolver prefilter families (RH850 16-bit instruction
# halfwords, little-endian). Masks keep opcode bits only; register fields vary.
LD_BU_DISP32_OPCODE_MASK = 0xFFC0
LD_BU_DISP32_OPCODE = 0x0F80  # ld.bu disp32[reg1],reg3 (32-bit displacement)
CMOV_OPCODE_MASK = 0xFFF8
CMOV_OPCODE = 0x0FE0  # cmov family with cond/reg2 fields in low bits
PREFILTER_LOOKAHEAD_HALFWORDS = 4
TRIAGE_NOTE = (
    "candidate only — structural presence does not prove the recovered Sienna "
    "mechanism transfers to this calibration"
)


def _u16(blob: bytes, off: int) -> int:
    return struct.unpack_from("<H", blob, off)[0]


def _u32(blob: bytes, off: int) -> int:
    return struct.unpack_from("<I", blob, off)[0]


def _find_u32(blob: bytes, value: int, max_vas: int) -> dict[str, Any]:
    needle = struct.pack("<I", value)
    offsets: list[int] = []
    start = 0
    while len(offsets) < max_vas:
        idx = blob.find(needle, start)
        if idx < 0:
            break
        offsets.append(idx)
        start = idx + 1
    total = blob.count(needle)
    return {
        "value": f"0x{value:08X}",
        "count": total,
        "first_vas": [f"0x{off:X}" for off in offsets],
        "triage": TRIAGE_NOTE,
    }


def _packed_standard_can_id_word(can_id: int) -> int:
    """Encode the alternative standard-ID descriptor word seen on Corolla H.

    The tracked H image stores its special 0x7F7/0x7F8 route as
    ``0x80000000 | (id << 18) | 2`` rather than as a plain u32 CAN ID.  This
    helper records that exact structural representation only; it does not claim
    every matching word is a live CAN route without target-side table tracing.
    """
    if not 0 <= can_id <= 0x7FF:
        raise ValueError(f"standard CAN ID out of range: {can_id:#x}")
    return 0x80000000 | (can_id << 18) | 0x2


def _find_packed_standard_can_id(blob: bytes, can_id: int, max_vas: int) -> dict[str, Any]:
    packed = _packed_standard_can_id_word(can_id)
    result = _find_u32(blob, packed, max_vas)
    result["decoded_standard_can_id"] = f"0x{can_id:03X}"
    result["encoding"] = "0x80000000 | (standard_can_id << 18) | 0x2"
    return result


def classify_geometry(size: int) -> dict[str, Any]:
    if size == CODEFLASH_SIZE:
        kind = "bare-codeflash-1m"
        note = "matches the bare 1 MiB RH850/P1M-E CodeFlash geometry"
    elif size == CONCATENATED_DUMP_SIZE:
        kind = "dataflash-codeflash-concat"
        note = (
            "0x108000 bytes: DataFlash+CodeFlash concatenated dump; CodeFlash VA = "
            f"file offset - 0x{P1M_E_DATAFLASH_PREFIX_SIZE:X}, so all reported VAs are "
            "DataFlash-relative until the prefix is stripped"
        )
    elif size < CODEFLASH_SIZE:
        kind = "truncated-or-foreign"
        note = f"smaller than the expected 0x{CODEFLASH_SIZE:X} CodeFlash image"
    else:
        kind = "oversized-or-foreign"
        note = f"larger than the expected 0x{CODEFLASH_SIZE:X} CodeFlash image"
    return {
        "size": size,
        "size_hex": f"0x{size:X}",
        "expected_codeflash_size": f"0x{CODEFLASH_SIZE:X}",
        "classification": kind,
        "geometry_matches_bare_codeflash": size == CODEFLASH_SIZE,
        "note": note,
    }


def scan_boot_trust(blob: bytes) -> dict[str, Any]:
    descriptors = discover_crc_descriptors(blob, 0)
    return {
        "classification": "triage-candidate",
        "crc_descriptor_count": len(descriptors),
        "terminal_valid_descriptor_count": sum(1 for d in descriptors if d.terminal_fixup_valid),
        "crc_descriptors": [
            {
                "descriptor_va": f"0x{d.descriptor_va:X}",
                "start": f"0x{d.start:X}",
                "end": f"0x{d.end:X}",
                "fixup_va": f"0x{d.fixup_va:X}",
                "terminal_fixup_valid": d.terminal_fixup_valid,
                "validity_marker_va": None if d.validity_marker_va is None else f"0x{d.validity_marker_va:X}",
            }
            for d in descriptors
        ],
        "validity_marker_word": {
            "value": f"0x{VALIDITY_MARKER:08X}",
            "count": blob.count(struct.pack("<I", VALIDITY_MARKER)),
        },
        "interpretation": (
            "self-describing CRC records validate the terminal-fixup boot-integrity scheme; "
            + TRIAGE_NOTE
        ),
    }


def scan_ram_exec_gate(blob: bytes, max_vas: int) -> dict[str, Any]:
    descriptor_pair = blob.count(
        struct.pack("<II", RAM_EXEC_WINDOW_BASE, RAM_EXEC_PACKAGE_LENGTH)
    )
    return {
        "classification": "triage-candidate",
        "download_window_base_immediates": _find_u32(blob, RAM_EXEC_WINDOW_BASE, max_vas),
        "package_descriptor_pair_count": descriptor_pair,
        "package_descriptor_pair": f"0x{RAM_EXEC_WINDOW_BASE:08X},0x{RAM_EXEC_PACKAGE_LENGTH:08X}",
        "callback_slot_immediates": _find_u32(blob, RAM_EXEC_CALLBACK_SLOT, max_vas),
        "interpretation": (
            "immediates match the authenticated RAM-exec download window used by the "
            "MEM-SAFE-001 decrypt-transfer/bootstrap chain; presence bounds where the "
            "window lives, it does not prove the missing-alignment defect or the "
            "bootstrap protocol transfer — " + TRIAGE_NOTE
        ),
    }


def scan_command_map_windows(blob: bytes) -> list[dict[str, Any]]:
    size = len(blob)
    windows: list[dict[str, Any]] = []
    off = 0
    while off + COMMAND_MAP_RECORD_SIZE <= size:
        if _command_map_record_ok(blob, off, size):
            start = off
            selectors: list[int] = []
            while off + COMMAND_MAP_RECORD_SIZE <= size and _command_map_record_ok(blob, off, size):
                selectors.append(blob[off])
                off += COMMAND_MAP_RECORD_SIZE
            if len(selectors) >= COMMAND_MAP_MIN_RECORDS:
                windows.append(
                    {
                        "va": f"0x{start:X}",
                        "record_count": len(selectors),
                        "record_size": COMMAND_MAP_RECORD_SIZE,
                        "selectors": [f"0x{s:02X}" for s in selectors],
                        "distinct_selectors": len(set(selectors)),
                        "callbacks": [
                            f"0x{_u32(blob, start + i * COMMAND_MAP_RECORD_SIZE + 4):X}"
                            for i in range(len(selectors))
                        ],
                    }
                )
        else:
            off += 4
    return windows


def _command_map_record_ok(blob: bytes, off: int, size: int) -> bool:
    selector = blob[off]
    pointer = _u32(blob, off + 4)
    return (
        COMMAND_MAP_SELECTOR_MIN <= selector <= COMMAND_MAP_SELECTOR_MAX
        and COMMAND_MAP_POINTER_MIN <= pointer < size
        and pointer % 2 == 0
    )


def scan_xcp_surface(blob: bytes, max_vas: int) -> dict[str, Any]:
    windows = scan_command_map_windows(blob)
    return {
        "classification": "triage-candidate",
        "request_can_id_immediates": _find_u32(blob, XCP_REQUEST_CAN_ID, max_vas),
        "response_can_id_immediates": _find_u32(blob, XCP_RESPONSE_CAN_ID, max_vas),
        "request_can_id_packed_standard_descriptors": _find_packed_standard_can_id(
            blob, XCP_REQUEST_CAN_ID, max_vas
        ),
        "response_can_id_packed_standard_descriptors": _find_packed_standard_can_id(
            blob, XCP_RESPONSE_CAN_ID, max_vas
        ),
        "page_copy_window_end_immediates": _find_u32(blob, XCP_PAGE_COPY_WINDOW_END, max_vas),
        "page_copy_shadow_base_immediates": _find_u32(blob, XCP_PAGE_COPY_SHADOW_BASE, max_vas),
        "command_map_window_count": len(windows),
        "command_map_windows": windows,
        "interpretation": (
            "paired CAN route constants (plain or packed standard-ID representation), "
            "page-copy window/shadow constants, and eight-byte selector/callback "
            "command-map records are the structural "
            "signature of the XCP-shaped calibration surface; candidate maps must be "
            "decompiled and validated against their own firmware before use — " + TRIAGE_NOTE
        ),
    }


def scan_resolver_prefilter(blob: bytes, max_vas: int) -> dict[str, Any]:
    size = len(blob)
    ld_bu_count = 0
    cmov_count = 0
    pair_sites: list[int] = []
    for off in range(0, size - 2, 2):
        half = _u16(blob, off)
        if (half & LD_BU_DISP32_OPCODE_MASK) == LD_BU_DISP32_OPCODE:
            ld_bu_count += 1
            for delta in range(2, 2 + 2 * PREFILTER_LOOKAHEAD_HALFWORDS, 2):
                if off + delta + 2 > size:
                    break
                if (_u16(blob, off + delta) & CMOV_OPCODE_MASK) == CMOV_OPCODE:
                    pair_sites.append(off)
                    break
        elif (half & CMOV_OPCODE_MASK) == CMOV_OPCODE:
            cmov_count += 1
    return {
        "classification": "triage-candidate",
        "ld_bu_disp32_halfword_count": ld_bu_count,
        "cmov_family_halfword_count": cmov_count,
        "byte_load_then_cmov_site_count": len(pair_sites),
        "byte_load_then_cmov_first_vas": [f"0x{off:X}" for off in pair_sites[:max_vas]],
        "encoding_masks": {
            "ld_bu_disp32": f"(hw & 0x{LD_BU_DISP32_OPCODE_MASK:04X}) == 0x{LD_BU_DISP32_OPCODE:04X}",
            "cmov_family": f"(hw & 0x{CMOV_OPCODE_MASK:04X}) == 0x{CMOV_OPCODE:04X}",
            "lookahead_bytes": 2 * PREFILTER_LOOKAHEAD_HALFWORDS,
        },
        "interpretation": (
            "byte-level counts of the load->booleanize shape the SecOC semantic gate "
            "resolver scans after disassembly; they are NOT disassembly and cannot "
            "identify a gate target by themselves — " + TRIAGE_NOTE
        ),
    }


def analyze(blob: bytes, *, max_vas: int = 16) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "classification": "triage",
        "disclaimer": (
            "All matches are structural triage candidates recovered from the Sienna "
            "8965B4512000 calibration; they are not transfer proof for any other image. "
            "Validate every mechanism against the target's own firmware."
        ),
        "image": {
            "sha256": hashlib.sha256(blob).hexdigest(),
            "geometry": classify_geometry(len(blob)),
            # Intentionally absent: a per-calibration software-ID offset table is a
            # provenance hazard (stale offsets silently misidentify targets). Identify
            # images by hash and structure instead.
            "software_id_offsets": None,
        },
        "boot_trust": scan_boot_trust(blob),
        "ram_exec_gate": scan_ram_exec_gate(blob, max_vas),
        "xcp_command_surface": scan_xcp_surface(blob, max_vas),
        "semantic_resolver_prefilter": scan_resolver_prefilter(blob, max_vas),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--max-vas", type=int, default=16)
    args = parser.parse_args(argv)

    blob = args.image.read_bytes()
    report = analyze(blob, max_vas=args.max_vas)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
