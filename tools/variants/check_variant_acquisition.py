#!/usr/bin/env python3
"""Triage an acquired firmware image and report P1M-E resolver readiness.

Report container layout, architecture and load-address evidence, vector entries,
and candidate protocol and CRC tables directly from the file.
"""

from __future__ import annotations

from tools import REPO_ROOT
import argparse
import hashlib
import json
import math
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = REPO_ROOT

from tools.firmware.analyze_rh850_codeflash_structure import analyze as scan_structure  # noqa: E402
from tools.firmware.p1me_codeflash import (  # noqa: E402
    P1M_E_CODEFLASH_SIZE,
    validate_codeflash_geometry,
)

SCHEMA = "variant-acquisition-readiness-v1"
CATALOG_SCHEMA = "variant-acquisition-readiness-catalog-v1"
RUN_SCHEMA = "p1me-codeflash-live-acquisition-v1"
MANIFEST_SCHEMA = "toyota-secoc-patch-manifest-v1"
PREFIX_SIZE = 0x8000
KNOWN_SIDS = frozenset(
    (0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x27, 0x28, 0x2C, 0x2E, 0x2F,
     0x31, 0x34, 0x35, 0x36, 0x37, 0x3D, 0x3E, 0x85, 0xAB, 0xBA, 0xBB)
)
XCP_COMMANDS = frozenset(
    (0xFF, 0xFE, 0xFD, 0xFC, 0xFB, 0xFA, 0xF8, 0xF7, 0xF5, 0xF3, 0xEB, 0xEA, 0xE4, 0xDA)
)


class AcquisitionReadinessError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _hex(value: int | None) -> str | None:
    return None if value is None else f"0x{value:X}"


def _load_json(path: Path, expected_schema: str, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AcquisitionReadinessError(f"cannot load {label} {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema") != expected_schema:
        raise AcquisitionReadinessError(
            f"{label} {path} has unsupported schema (expected {expected_schema})"
        )
    return data


def _entropy(blob: bytes) -> float:
    if not blob:
        return 0.0
    length = len(blob)
    return -sum(
        (count / length) * math.log2(count / length)
        for count in Counter(blob).values()
    )


def _region(name: str, blob: bytes, start: int) -> dict[str, Any]:
    first = next((index for index, value in enumerate(blob) if value != 0xFF), None)
    last = next(
        (len(blob) - index - 1 for index, value in enumerate(reversed(blob)) if value != 0xFF),
        None,
    )
    return {
        "name": name,
        "file_start": _hex(start),
        "file_end_exclusive": _hex(start + len(blob)),
        "size_bytes": len(blob),
        "entropy_bits_per_byte": round(_entropy(blob), 6),
        "erased_ff_fraction": round(blob.count(0xFF) / len(blob), 6) if blob else 1.0,
        "zero_fraction": round(blob.count(0) / len(blob), 6) if blob else 0.0,
        "non_erased_start": _hex(start + first) if first is not None else None,
        "non_erased_end_inclusive": _hex(start + last) if last is not None else None,
    }


def _decode_vector_jump(blob: bytes, offset: int) -> dict[str, Any] | None:
    """Decode the reset-slot forms defined by the vendored V850 SLEIGH."""
    if offset + 2 > len(blob):
        return None
    cursor = offset
    prefix = ""
    if struct.unpack_from("<H", blob, cursor)[0] == 0x001F:
        prefix = "syncp; "
        cursor += 2
    if cursor + 6 > len(blob):
        return None
    opcode = struct.unpack_from("<H", blob, cursor)[0]
    encoded = struct.unpack_from("<I", blob, cursor + 2)[0] & 0xFFFFFFFE
    if opcode == 0x06E0:
        return {
            "size": cursor + 6 - offset,
            "mnemonic": f"{prefix}jmp {_hex(encoded)}[r0]",
            "target": encoded,
            "kind": "absolute",
        }
    if opcode == 0x02E0:
        target = (cursor + encoded) & 0xFFFFFFFF
        return {
            "size": cursor + 6 - offset,
            "mnemonic": f"{prefix}jr {_hex(target)}",
            "target": target,
            "kind": "pc-relative",
        }
    return None


def check_container(blob: bytes) -> tuple[dict[str, Any], bytes, int]:
    at_zero = _decode_vector_jump(blob, 0)
    at_prefix = _decode_vector_jump(blob, PREFIX_SIZE) if len(blob) > PREFIX_SIZE else None
    if at_prefix is not None and at_zero is None:
        code_offset = PREFIX_SIZE
        classification = "dataflash-prefix-plus-codeflash"
        regions = [
            _region("dataflash-prefix", blob[:PREFIX_SIZE], 0),
            _region("codeflash", blob[PREFIX_SIZE:], PREFIX_SIZE),
        ]
    else:
        code_offset = 0
        if at_zero is not None:
            classification = "bare-codeflash"
        elif blob and blob.count(0xFF) == len(blob):
            classification = "erased"
        elif len(blob) < PREFIX_SIZE:
            classification = "truncated-or-small-unknown"
        else:
            classification = "unknown-container"
        regions = [_region("image", blob, 0)]
    return (
        {
            "classification": classification,
            "codeflash_file_offset": _hex(code_offset) if code_offset else "0x0",
            "regions": regions,
        },
        blob[code_offset:],
        code_offset,
    )


def _mov32_at(blob: bytes, offset: int) -> tuple[int, int] | None:
    if offset + 6 > len(blob):
        return None
    word = struct.unpack_from("<H", blob, offset)[0]
    if word >> 5 != 0x31:
        return None
    return word & 0x1F, struct.unpack_from("<I", blob, offset + 2)[0]

def _constant_load_at(blob: bytes, offset: int) -> tuple[int, int, int, str] | None:
    move = _mov32_at(blob, offset)
    if move is not None:
        return move[0], move[1], 6, "mov-imm32"
    if offset + 4 > len(blob):
        return None
    word, immediate = struct.unpack_from("<HH", blob, offset)
    if ((word >> 5) & 0x3F) == 0x31 and (word & 0x1F) == 0:
        return (word >> 11) & 0x1F, immediate, 4, "movea-imm16-r0"
    return None


def _intbp_writes(blob: bytes) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for offset in range(0, len(blob) - 3, 2):
        low, high = struct.unpack_from("<HH", blob, offset)
        if (
            ((low >> 5) & 0x3F) != 0x3F
            or ((low >> 11) & 0x1F) != 4
            or (high & 0x7FF) != 0x20
            or (high >> 11) != 1
        ):
            continue
        register = low & 0x1F
        source = None
        for candidate in range(max(0, offset - 16), offset, 2):
            move = _mov32_at(blob, candidate)
            if move is not None and move[0] == register:
                source = (candidate, move[1])
        hits.append(
            {
                "load_offset": source[0] if source is not None else None,
                "write_offset": offset,
                "value": source[1] if source is not None else None,
                "register": register,
            }
        )
    return hits


def check_architecture(blob: bytes) -> dict[str, Any]:
    jump_slots = sum(
        _decode_vector_jump(blob, offset) is not None
        for offset in range(0, min(len(blob), 0x100), 0x10)
    )
    intbp = _intbp_writes(blob)
    mov_gp = mov_tp = 0
    for offset in range(0, min(len(blob), 0x10000) - 5, 2):
        move = _mov32_at(blob, offset)
        if move is not None:
            mov_gp += move[0] == 4
            mov_tp += move[0] == 5
    sourced_intbp = sum(hit["value"] is not None for hit in intbp)
    observations = [
        f"{jump_slots} of the first 16 vector slots decode as V850/RH850 jr/jmp forms",
        f"{len(intbp)} INTBP writes decoded; {sourced_intbp} have a nearby mov imm32 source",
        f"startup window contains {mov_gp} direct gp and {mov_tp} direct tp initializers",
    ]
    if not blob or blob.count(0xFF) == len(blob):
        architecture, confidence = "erased-or-empty", "high"
    elif jump_slots >= 4 and intbp:
        architecture, confidence = "RH850", "high"
    elif jump_slots >= 4:
        architecture, confidence = "V850/RH850-family", "medium"
    elif len(blob) >= 8:
        stack, reset = struct.unpack_from("<II", blob)
        if (stack & 0x2FF00000) == 0x20000000 and reset & 1:
            architecture, confidence = "ARM-Thumb", "medium"
            observations.append("initial little-endian words resemble an ARM vector SP/reset pair")
        elif _entropy(blob) > 7.8:
            architecture, confidence = "compressed-or-encrypted-blob", "medium"
        elif struct.unpack_from(">I", blob)[0] & 0xFC000003 == 0x48000000:
            architecture, confidence = "PowerPC-big-endian", "low"
        else:
            architecture, confidence = "unknown", "low"
    else:
        architecture, confidence = "unknown", "low"
    return {
        "decision": architecture,
        "confidence": confidence,
        "observations": observations,
        "alternatives_considered": [
            "ARM-Thumb", "PowerPC", "RL78", "older-V850", "TriCore",
            "compressed-or-encrypted", "erased-or-sparse",
        ],
    }


def _pointer_table_score(blob: bytes, offset: int, base: int) -> int:
    if offset < 0 or offset + 0x80 > len(blob):
        return -1
    score = 0
    for index in range(32):
        value = struct.unpack_from("<I", blob, offset + index * 4)[0]
        if base <= value < base + len(blob) and value & 1 == 0:
            score += 1
    return score


def check_load_address(blob: bytes) -> dict[str, Any]:
    votes: list[dict[str, Any]] = []
    reset = _decode_vector_jump(blob, 0)
    if reset is not None and reset["target"] < len(blob):
        votes.append(
            {
                "source": "reset-vector-target",
                "load_address": "0x0",
                "evidence": f"{reset['mnemonic']} has an in-file target at base zero",
            }
        )
    intbp_evidence = []
    for hit in _intbp_writes(blob):
        if hit["value"] is None:
            intbp_evidence.append(
                {
                    "instruction_offset": _hex(hit["write_offset"]),
                    "intbp_value": None,
                    "candidates": [],
                }
            )
            continue
        value = hit["value"]
        candidates = []
        first_base = max(0, value - len(blob) + 1)
        for base in range((first_base + 0xFFFF) & ~0xFFFF, value + 1, 0x10000):
            table_offset = value - base
            score = _pointer_table_score(blob, table_offset, base)
            if score >= 4:
                candidates.append((score, base, table_offset))
        candidates.sort(reverse=True)
        evidence = {
            "instruction_offset": _hex(hit["write_offset"]),
            "intbp_value": _hex(value),
            "candidates": [
                {
                    "load_address": _hex(base),
                    "table_file_offset": _hex(offset),
                    "in_range_pointers_first_32": score,
                }
                for score, base, offset in candidates[:3]
            ],
        }
        intbp_evidence.append(evidence)
        if candidates:
            score, base, offset = candidates[0]
            votes.append(
                {
                    "source": "INTBP-pointer-table",
                    "load_address": _hex(base),
                    "evidence": (
                        f"INTBP {_hex(value)} maps to file {_hex(offset)} with "
                        f"{score}/32 in-range pointers"
                    ),
                }
            )
    numeric_votes = [int(vote["load_address"], 16) for vote in votes]
    if numeric_votes:
        counts = Counter(numeric_votes)
        most_votes = max(counts.values())
        selected = min(
            value for value, count in counts.items() if count == most_votes
        )
        spread = max(numeric_votes) - min(numeric_votes)
    else:
        selected = None
        spread = None
    return {
        "selected_load_address": _hex(selected),
        "confidence": "high" if len(votes) >= 2 and spread == 0 else ("medium" if votes else "none"),
        "vote_spread_bytes": spread,
        "votes": votes,
        "intbp_evidence": intbp_evidence,
    }


def check_vectors(blob: bytes, load_base: int | None) -> dict[str, Any]:
    entries = []
    kinds: Counter[str] = Counter()
    base = load_base or 0
    for offset in range(0, min(len(blob), 0x100), 0x10):
        jump = _decode_vector_jump(blob, offset)
        if jump is not None:
            kind = "jump-instruction"
            evidence = jump["mnemonic"]
            size = jump["size"]
            target = _hex(jump["target"] + (base if jump["kind"] == "pc-relative" else 0))
        elif offset + 4 <= len(blob):
            pointer = struct.unpack_from("<I", blob, offset)[0]
            if base <= pointer < base + len(blob) and pointer & 1 == 0:
                kind, evidence, size, target = "pointer", f"little-endian pointer {_hex(pointer)}", 4, _hex(pointer)
            else:
                kind, evidence, size, target = "neither", "no supported vector form", min(8, len(blob) - offset), None
        else:
            kind, evidence, size, target = "neither", "truncated entry", len(blob) - offset, None
        kinds[kind] += 1
        entries.append(
            {
                "file_offset": _hex(offset),
                "virtual_address": _hex(base + offset),
                "classification": kind,
                "bytes": blob[offset:offset + size].hex(),
                "disassembly": evidence,
                "target": target,
            }
        )
    if not entries or kinds["neither"] == len(entries):
        form = "neither"
    elif kinds["jump-instruction"] > len(entries) // 2:
        form = "jump-instruction"
    elif kinds["pointer"] > len(entries) // 2:
        form = "pointer"
    else:
        form = "mixed"
    return {
        "decoder": "vendored-v850-sleigh-vector-subset",
        "entry_stride_bytes": 16,
        "form": form,
        "classification_counts": dict(kinds),
        "entries": entries,
    }


def _valid_address(value: int, base: int, size: int) -> bool:
    return value == 0 or base <= value < base + size


def _valid_pointer(value: int, base: int, size: int) -> bool:
    return _valid_address(value, base, size) and value & 1 == 0


def _uds8_record(blob: bytes, offset: int, base: int) -> tuple[int, int] | None:
    if offset + 8 > len(blob):
        return None
    sid, mask, zero1, zero2, pointer = struct.unpack_from("<BBBBI", blob, offset)
    if sid not in KNOWN_SIDS or mask > 0x0F or zero1 or zero2 or not _valid_pointer(pointer, base, len(blob)):
        return None
    return sid, pointer


def _uds24_record(blob: bytes, offset: int, base: int) -> tuple[int, int] | None:
    if offset + 24 > len(blob):
        return None
    direct, security, session, subfunctions = struct.unpack_from("<IIII", blob, offset)
    sid, has_sub, security_count, session_count, sub_count = struct.unpack_from(
        "<BBBBB", blob, offset + 16
    )
    pointers = (direct, security, session, subfunctions)
    if (
        sid not in KNOWN_SIDS
        or has_sub > 1
        or max(security_count, session_count, sub_count) > 32
        or any(not _valid_address(pointer, base, len(blob)) for pointer in pointers)
        or (direct and direct & 1)
    ):
        return None
    return sid, direct or subfunctions


def _table_runs(blob: bytes, base: int, stride: int, parser: Any, schema: str) -> list[dict[str, Any]]:
    candidates = []
    for offset in range(0, len(blob) - stride + 1, 4):
        if offset >= stride and parser(blob, offset - stride, base) is not None:
            continue
        rows = []
        cursor = offset
        while len(rows) < 64:
            row = parser(blob, cursor, base)
            if row is None:
                break
            rows.append(row)
            cursor += stride
        if len(rows) >= 5 and len({sid for sid, _ in rows}) >= 5:
            candidates.append(
                {
                    "address": _hex(base + offset),
                    "file_offset": _hex(offset),
                    "schema": schema,
                    "record_count": len(rows),
                    "sids": [f"0x{sid:02X}" for sid, _ in rows],
                    "handler_or_subfunction_pointer_count": sum(pointer != 0 for _, pointer in rows),
                }
            )
    candidates.sort(key=lambda item: (-item["record_count"], int(item["file_offset"], 16)))
    return candidates[:16]


def _nrc_compare_candidates(blob: bytes, base: int) -> dict[str, Any]:
    constants = (0x35, 0x36, 0x41)
    raw_counts = {f"0x{value:02X}": blob.count(bytes((value,))) for value in constants}
    hits = []
    for offset in range(0, len(blob) - 3, 2):
        load = _constant_load_at(blob, offset)
        if load is None or load[1] not in constants:
            continue
        register, value, size, encoding = load
        for compare in range(offset + size, min(offset + 64, len(blob) - 1), 2):
            word = struct.unpack_from("<H", blob, compare)[0]
            if ((word >> 5) & 0x3F) == 0x0F and (
                (word & 0x1F) == register or ((word >> 11) & 0x1F) == register
            ):
                hits.append(
                    {
                        "constant": f"0x{value:02X}",
                        "load_address": _hex(base + offset),
                        "compare_address": _hex(base + compare),
                        "evidence": (
                            f"{encoding} 0x{value:02X} into r{register}; "
                            f"nearby cmp uses r{register}"
                        ),
                    }
                )
                break
    return {"constants": ["0x35", "0x36", "0x41"], "compare_load_hits": hits, "raw_byte_counts": raw_counts}


def check_uds(blob: bytes, load_base: int | None) -> dict[str, Any]:
    base = load_base or 0
    candidates = _table_runs(blob, base, 24, _uds24_record, "denso-application-24-byte")
    candidates.extend(_table_runs(blob, base, 8, _uds8_record, "sid-mask-handler-8-byte"))
    candidates.sort(key=lambda item: (-item["record_count"], int(item["address"], 16)))
    return {
        "service_tables": candidates[:24],
        "nrc_compare_candidates": _nrc_compare_candidates(blob, base),
    }


def _find_all(blob: bytes, needle: bytes, alignment: int = 1, limit: int = 64) -> list[int]:
    hits = []
    start = 0
    while len(hits) < limit:
        offset = blob.find(needle, start)
        if offset < 0:
            break
        if offset % alignment == 0:
            hits.append(offset)
        start = offset + 1
    return hits


def check_ccp_xcp(blob: bytes, load_base: int | None) -> dict[str, Any]:
    base = load_base or 0
    route_values = {
        "standard-request-0x7F7": 0x7F7,
        "standard-response-0x7F8": 0x7F8,
        "extended-request-0x1FDC0002": 0x1FDC0002,
        "extended-response-0x1FE00002": 0x1FE00002,
    }
    routes = []
    for name, value in route_values.items():
        width = 2 if value <= 0xFFFF else 4
        for offset in _find_all(blob, value.to_bytes(width, "little"), alignment=2):
            routes.append({"constant": name, "address": _hex(base + offset), "width_bytes": width})
    tables = []
    def command_record(offset: int) -> tuple[int, int] | None:
        if offset + 8 > len(blob):
            return None
        selector, pad1, pad2, pad3, pointer = struct.unpack_from("<BBBBI", blob, offset)
        if pad1 or pad2 or pad3 or selector == 0 or not _valid_pointer(pointer, base, len(blob)):
            return None
        return selector, pointer

    for offset in range(0, len(blob) - 24, 4):
        if offset >= 8 and command_record(offset - 8) is not None:
            continue
        rows = []
        cursor = offset
        while cursor + 8 <= len(blob) and len(rows) < 64:
            row = command_record(cursor)
            if row is None:
                break
            rows.append(row)
            cursor += 8
        selectors = {selector for selector, _ in rows}
        ccp_shape = {0x01, 0x12, 0x13}.issubset(selectors)
        xcp_shape = len(selectors.intersection(XCP_COMMANDS)) >= 3
        if len(rows) >= 3 and (ccp_shape or xcp_shape):
            tables.append(
                {
                    "address": _hex(base + offset),
                    "record_count": len(rows),
                    "selectors": [f"0x{selector:02X}" for selector, _ in rows],
                    "seed_key_selectors": [
                        f"0x{selector:02X}" for selector in (0x12, 0x13, 0xF7, 0xF8)
                        if selector in selectors
                    ],
                    "evidence": "selector + three zero bytes + in-image handler pointer rows",
                }
            )
    tables.sort(key=lambda item: (-item["record_count"], int(item["address"], 16)))
    return {
        "route_constant_hits": routes,
        "command_table_candidates": tables[:16],
        "searched_commands": {
            "ccp": {"CONNECT": "0x01", "GET_SEED": "0x12", "UNLOCK": "0x13", "routes": ["0xBE", "0xBF"]},
            "xcp": {"CONNECT": "0xFF", "GET_SEED": "0xF8", "UNLOCK": "0xF7", "GET_DAQ_PROCESSOR_INFO": "0xDA"},
        },
    }


CRC_SIGNATURES = (
    (
        "CRC-32/ISO-HDLC reflected poly 0xEDB88320",
        bytes.fromhex("00000000963007772c610eeeba510999"),
        4,
    ),
    (
        "CRC-32/ISO-HDLC big-endian words",
        bytes.fromhex("0000000077073096ee0e612c990951ba"),
        4,
    ),
    (
        "CRC-16/MODBUS reflected poly 0xA001 little-endian words",
        bytes.fromhex("0000c1c081c1400101c3c0030082c241"),
        2,
    ),
    (
        "CRC-16/MODBUS split-byte table prefix",
        bytes.fromhex("00c0c101c30102c2c60107c5c40305c7"),
        1,
    ),
    (
        "CRC-16/CCITT poly 0x1021 big-endian words",
        bytes.fromhex("0000102120423063408450a560c670e7"),
        2,
    ),
    (
        "CRC-16/CCITT poly 0x1021 little-endian words",
        bytes.fromhex("00002110422063308440a550c660e770"),
        2,
    ),
)


def check_crc_tables(blob: bytes, load_base: int | None) -> dict[str, Any]:
    base = load_base or 0
    hits = []
    for name, signature, alignment in CRC_SIGNATURES:
        for offset in _find_all(blob, signature, alignment=alignment):
            hits.append(
                {
                    "polynomial": name,
                    "table_address": _hex(base + offset),
                    "signature_bytes": signature.hex(),
                }
            )
    return {
        "method": "exact standard table-prefix constants (findcrypt-style constant hit)",
        "hits": hits,
    }


def check_acquisition(image: Path, blob: bytes, run: dict[str, Any] | None) -> dict[str, Any]:
    """Geometry + SHA/size provenance, with optional dumper run-record binding."""
    try:
        validate_codeflash_geometry(len(blob))
        geometry_ok = True
        geometry_note = "exact bare 1 MiB RH850/P1M-E CodeFlash geometry"
    except ValueError as exc:
        geometry_ok = False
        geometry_note = str(exc)

    result: dict[str, Any] = {
        "geometry_valid": geometry_ok,
        "geometry_note": geometry_note,
        "size_bytes": len(blob),
        "expected_size_bytes": P1M_E_CODEFLASH_SIZE,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "path": str(image),
        "run_record": None,
    }
    if run is not None:
        image_record = run.get("image") or {}
        capture = run.get("capture") or {}
        resolver = run.get("resolver") or {}
        checks = {
            "run_schema": RUN_SCHEMA,
            "run_image_sha256": image_record.get("sha256"),
            "run_sha_matches_bytes": image_record.get("sha256") == result["sha256"],
            "run_reports_complete": image_record.get("complete") is True,
            "run_missing_word_count": image_record.get("missing_word_count"),
            "run_interrupted": run.get("interrupted") is True,
            "run_capture_sha256": capture.get("sha256"),
            "run_capture_accepted_frames": capture.get("accepted_frames"),
            "run_resolver_status": resolver.get("status"),
        }
        result["run_record"] = checks
        result["problems"] = [
            name
            for name, ok in (
                ("run sha256 does not match image bytes", checks["run_sha_matches_bytes"]),
                ("run record does not report a complete acquisition", checks["run_reports_complete"]),
            )
            if not ok
        ]
    else:
        result["problems"] = [] if geometry_ok else ["image geometry is not resolver-ready"]
    return result


def check_structure(blob: bytes) -> dict[str, Any]:
    """Summarize the P1M-E structural scanner when its geometry applies."""
    if len(blob) != P1M_E_CODEFLASH_SIZE:
        return {
            "available": False,
            "reason": "P1M-E structure scanner requires a bare 1 MiB CodeFlash region",
        }
    report = scan_structure(blob)
    xcp = report["xcp_command_surface"]
    boot = report["boot_trust"]
    ram_exec = report["ram_exec_gate"]
    prefilter = report["semantic_resolver_prefilter"]
    return {
        "available": True,
        "schema": report["schema"],
        "image_sha256": report["image"]["sha256"],
        "geometry": report["image"]["geometry"]["classification"],
        "boot_trust": {
            "crc_descriptor_count": boot["crc_descriptor_count"],
            "terminal_valid_descriptor_count": boot["terminal_valid_descriptor_count"],
            "validity_marker_count": boot["validity_marker_word"]["count"],
        },
        "ram_exec_gate": {
            "download_window_immediate_count": ram_exec["download_window_base_immediates"]["count"],
            "package_descriptor_pair_count": ram_exec["package_descriptor_pair_count"],
        },
        "xcp_surface": {
            "request_can_id_immediate_count": xcp["request_can_id_immediates"]["count"],
            "response_can_id_immediate_count": xcp["response_can_id_immediates"]["count"],
            "request_can_id_extended_descriptor_count": xcp["request_can_id_extended_descriptors"]["count"],
            "response_can_id_extended_descriptor_count": xcp["response_can_id_extended_descriptors"]["count"],
            "command_map_window_count": xcp["command_map_window_count"],
        },
        "semantic_resolver_prefilter": {
            "byte_load_then_cmov_site_count": prefilter["byte_load_then_cmov_site_count"],
        },
        "disclaimer": report["disclaimer"],
    }


def check_resolver_readiness(
    acquisition: dict[str, Any], manifest: dict[str, Any] | None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "resolver": "tools/security/resolve_secoc_patch_image.sh",
        "geometry_gate": acquisition["geometry_valid"],
        "manifest": None,
    }
    if manifest is not None:
        manifest_image = manifest.get("image") or {}
        result["manifest"] = {
            "schema": manifest.get("schema"),
            "image_sha256": manifest_image.get("sha256"),
            "sha_matches_bytes": manifest_image.get("sha256") == acquisition["sha256"],
            "semantic_resolution_present": isinstance(manifest.get("semantic_resolution"), dict),
        }
        result["manifest_bound"] = result["manifest"]["sha_matches_bytes"]
    else:
        result["manifest_bound"] = None
    result["ready"] = (
        acquisition["geometry_valid"]
        and not acquisition.get("problems")
        and result["manifest_bound"] is not False
    )
    result["next_step"] = (
        "run: tools/security/resolve_secoc_patch_image.sh <image> - (disposable Ghidra import; "
        "zero/multiple semantic candidates fail closed)"
        if result["ready"]
        else "fix acquisition problems above before invoking the semantic resolver"
    )
    return result


def build_report(
    image: Path,
    blob: bytes,
    run: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    notes: str | None,
) -> dict[str, Any]:
    acquisition = check_acquisition(image, blob, run)
    container, codeflash, _ = check_container(blob)
    architecture = check_architecture(codeflash)
    load_vote = check_load_address(codeflash)
    selected_text = load_vote["selected_load_address"]
    selected_base = int(selected_text, 16) if selected_text is not None else None
    resolver = check_resolver_readiness(acquisition, manifest)
    return {
        "schema": SCHEMA,
        "created_at": _utc_now(),
        "image_path": str(image),
        "notes": notes,
        "acquisition": acquisition,
        "architecture": architecture,
        "container_triage": container,
        "load_address_vote": load_vote,
        "vector_entries": check_vectors(codeflash, selected_base),
        "uds_table_candidates": check_uds(codeflash, selected_base),
        "ccp_xcp_candidates": check_ccp_xcp(codeflash, selected_base),
        "crc_table_constants": check_crc_tables(codeflash, selected_base),
        "structure_triage": check_structure(codeflash),
        "resolver_readiness": resolver,
        "ready": acquisition["geometry_valid"] and not acquisition["problems"],
    }


def build_registered_catalog(registry_path: Path) -> dict[str, Any]:
    registry = _load_json(registry_path, "ghidra-rh850-analysis-targets-v1", "target registry")
    reports = {}
    for target, entry in registry["targets"].items():
        image = REPO / entry["codeflash"]
        report = build_report(image, image.read_bytes(), None, None, f"registered target {target}")
        reports[target] = {
            "registered": {
                "codeflash_base": entry.get("codeflash_base"),
                "mcu": entry.get("mcu"),
                "processor": entry.get("processor"),
            },
            "readiness": report,
        }
    return {
        "schema": CATALOG_SCHEMA,
        "created_at": _utc_now(),
        "registry": str(registry_path),
        "targets": reports,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, help="acquired firmware image")
    parser.add_argument(
        "--registered-targets",
        action="store_true",
        help="emit one catalog containing triage for every registered CodeFlash image",
    )
    parser.add_argument(
        "--run-json",
        type=Path,
        help="optional .run.json written by tsk/dumper/dump_codeflash.py",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="optional patch manifest (toyota-secoc-patch-manifest-v1) to bind to the image",
    )
    parser.add_argument("--notes", help="free-form provenance note recorded verbatim")
    parser.add_argument("-o", "--output", type=Path, help="write the readiness artifact as JSON")
    args = parser.parse_args(argv)

    if args.registered_targets:
        if args.image is not None or args.run_json is not None or args.manifest is not None:
            parser.error("--registered-targets does not accept an image, run record, or manifest")
        try:
            report = build_registered_catalog(REPO / "data/analysis_targets.json")
        except (AcquisitionReadinessError, OSError, KeyError) as exc:
            parser.error(str(exc))
        return_code = 0
    else:
        if args.image is None:
            parser.error("image is required unless --registered-targets is used")
        try:
            blob = args.image.read_bytes()
        except OSError as exc:
            parser.error(f"cannot read image: {exc}")
        run = None
        manifest = None
        try:
            if args.run_json is not None:
                run = _load_json(args.run_json, RUN_SCHEMA, "dumper run record")
            if args.manifest is not None:
                manifest = _load_json(args.manifest, MANIFEST_SCHEMA, "patch manifest")
        except AcquisitionReadinessError as exc:
            parser.error(str(exc))
        report = build_report(args.image, blob, run, manifest, args.notes)
        return_code = 0 if report["ready"] else 1

    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
