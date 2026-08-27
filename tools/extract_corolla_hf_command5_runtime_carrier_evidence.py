#!/usr/bin/env python3
"""Extract exact-H/F static evidence for the Corolla command-5 runtime carrier candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = REPO / "build/work/corpora/h_8965H1202000_decompilations.corrected-context.raw.jsonl"
DEFAULT_OUTPUT = REPO / "data/generated/corolla_hf_command5_runtime_carrier_evidence.json"
H_CODE = H_CODEFLASH
F_SOURCE = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"

H_SHA256 = "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f"
F_SOURCE_SHA256 = "b8fa3d951f59fb75c190ce1b2c73164adb952f871650cfcd3b7656f08a9c448d"
F_NORMALIZED_SHA256 = "fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6"
EXPECTED_CORPUS_SHA256 = "c3411eec57b9d55c004b0b0f328394bb152577c3398084dccc729dab5da54656"

APP_GP = 0xFEBEB800
POCKET_LO = 0xFEBF0000
POCKET_HI = 0xFEBF01CF
POCKET_END = POCKET_HI + 1
MAILBOX_LO = 0xFEBFFB80
MAILBOX_END = 0xFEBFFBBC

SELECTED_FUNCTIONS = {
    0x0006A8C4: "application_cpu_context_init",
    0x0005CAAC: "startup_coordinator",
    0x0005F30C: "foreground_scheduler",
    0x0005EB14: "application_mpu_loader",
    0x0005C586: "application_mpu_startup_caller",
    0x0006149A: "localram_initializer",
    0x00060562: "first_live_pocket_neighbor_consumer",
    0x00082750: "command5_dispatcher",
    0x00081E94: "command5_variable_length_prepare",
}

TRANSFER_RANGES = [
    ("application_cpu_context_init", 0x0006A8C4, 44),
    ("startup_coordinator", 0x0005CAAC, 98),
    ("foreground_scheduler", 0x0005F30C, 92),
    ("application_mpu_loader", 0x0005EB14, 244),
    ("application_mpu_tables", 0x0002D1E4, 0x100),
    ("localram_initializer", 0x0006149A, 222),
    ("command5_dispatcher", 0x00082750, 150),
    ("command5_variable_length_prepare", 0x00081E94, 178),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def u32(blob: bytes, address: int) -> int:
    return struct.unpack_from("<I", blob, address)[0]


def normalize_ref(address: int) -> tuple[int | None, str | None]:
    if 0xFEBF0000 <= address < 0xFEC00000:
        return address, "absolute"
    if 0x4800 <= address < 0x5800:
        return APP_GP + address, "simple-gp-offset"
    return None, None


def mpat_decode(value: int) -> dict[str, bool]:
    return {
        "supervisor_execute": bool(value & 0x20),
        "supervisor_write": bool(value & 0x10),
        "supervisor_read": bool(value & 0x08),
        "user_execute": bool(value & 0x04),
        "user_write": bool(value & 0x02),
        "user_read": bool(value & 0x01),
    }


def load_functions(corpus: Path) -> tuple[dict[int, dict[str, Any]], list[dict[str, Any]]]:
    functions: dict[int, dict[str, Any]] = {}
    normalized_refs: list[dict[str, Any]] = []
    with corpus.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") != "function":
                continue
            entry = int(row["entry_addr"], 16)
            functions[entry] = row
            for ref in row.get("data_references", []):
                try:
                    raw = int(ref["to_addr"], 16)
                except (KeyError, TypeError, ValueError):
                    continue
                normalized, method = normalize_ref(raw)
                if normalized is None:
                    continue
                normalized_refs.append({
                    "function_entry": f"0x{entry:08X}",
                    "from_addr": ref.get("from_addr"),
                    "raw_to_addr": f"0x{raw:08X}",
                    "normalized_to_addr": f"0x{normalized:08X}",
                    "normalization": method,
                    "ref_type": ref.get("ref_type"),
                })
    return functions, normalized_refs


def build(corpus: Path = DEFAULT_CORPUS) -> dict[str, Any]:
    h = H_CODE.read_bytes()
    f_source = F_SOURCE.read_bytes()
    if sha256_bytes(h) != H_SHA256:
        raise ValueError("8965H1202000 normalized CodeFlash identity mismatch")
    if sha256_bytes(f_source) != F_SOURCE_SHA256:
        raise ValueError("8965F1208000 source range-dump identity mismatch")
    if len(f_source) < 0x100000:
        raise ValueError("F source range dump too small for normalized application image")
    f = f_source[:0x100000]
    if sha256_bytes(f) != F_NORMALIZED_SHA256:
        raise ValueError("8965F1208000 normalized first-MiB identity mismatch")
    corpus_sha = sha256_file(corpus)
    if corpus_sha != EXPECTED_CORPUS_SHA256:
        raise ValueError(f"unexpected H corrected decompiler corpus identity: {corpus_sha}")

    functions, refs = load_functions(corpus)
    selected: list[dict[str, Any]] = []
    for entry, role in SELECTED_FUNCTIONS.items():
        row = functions.get(entry)
        if row is None:
            raise ValueError(f"missing selected H function 0x{entry:08X}")
        body_size = int(row["body_size"])
        selected.append({
            "entry": f"0x{entry:08X}",
            "role": role,
            "body_size": body_size,
            "body_sha256": sha256_bytes(h[entry:entry + body_size]),
            "decompiled_c_sha256": sha256_bytes(row.get("decompiled_c", "").encode()),
            "data_reference_count": len(row.get("data_references", [])),
            "h_f_body_equal": h[entry:entry + body_size] == f[entry:entry + body_size],
        })

    refs_sorted = sorted(refs, key=lambda r: (int(r["normalized_to_addr"], 16), int(r["function_entry"], 16)))
    refs_at_or_above_pocket = [r for r in refs_sorted if int(r["normalized_to_addr"], 16) >= POCKET_LO]
    first_ref = int(refs_at_or_above_pocket[0]["normalized_to_addr"], 16) if refs_at_or_above_pocket else None
    pocket_refs = [r for r in refs_sorted if POCKET_LO <= int(r["normalized_to_addr"], 16) < POCKET_END]
    mailbox_refs = [r for r in refs_sorted if MAILBOX_LO <= int(r["normalized_to_addr"], 16) < MAILBOX_END]
    if first_ref != POCKET_END or pocket_refs:
        raise ValueError("H normalized direct-reference pocket boundary drift")
    if mailbox_refs:
        raise ValueError("H normalized direct references entered the selected XCP mailbox")

    regions: list[dict[str, Any]] = []
    for index in range(16):
        lower = u32(h, 0x2D1E4 + index * 8)
        upper = u32(h, 0x2D1E8 + index * 8)
        attr0 = u32(h, 0x2D264 + index * 4)
        attr1 = u32(h, 0x2D2A4 + index * 4)
        regions.append({
            "index": index,
            "lower": f"0x{lower:08X}",
            "upper_inclusive": f"0x{upper:08X}",
            "ctx0_mpat": f"0x{attr0:08X}",
            "ctx1_mpat": f"0x{attr1:08X}",
            "ctx0_permissions": mpat_decode(attr0),
            "ctx1_permissions": mpat_decode(attr1),
        })
    region5 = regions[5]
    if not (
        region5["lower"] == "0xFEBEF400"
        and region5["upper_inclusive"] == "0xFEBF33FC"
        and region5["ctx0_mpat"] == "0x000000B8"
        and region5["ctx1_mpat"] == "0x000000B8"
    ):
        raise ValueError("H MPU region-5 geometry/permissions drift")

    transfers: list[dict[str, Any]] = []
    for name, start, size in TRANSFER_RANGES:
        hb = h[start:start + size]
        fb = f[start:start + size]
        transfers.append({
            "name": name,
            "start": f"0x{start:08X}",
            "size": size,
            "h_sha256": sha256_bytes(hb),
            "f_sha256": sha256_bytes(fb),
            "byte_equal": hb == fb,
        })
    if not all(row["byte_equal"] for row in transfers):
        raise ValueError("one or more H/F runtime-carrier prerequisite ranges differ")

    startup_first = 0x5CAB4
    startup_after = 0x5CAFC
    startup_count = (startup_after - startup_first) // 4
    if startup_count != 18:
        raise ValueError("H startup JARL count drift")

    return {
        "schema": "corolla-hf-command5-runtime-carrier-evidence-v1",
        "schema_version": 1,
        "generator": {
            "path": str(Path(__file__).resolve().relative_to(REPO)),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "title": "Corolla H/F target-native command-5 runtime carrier static evidence",
        "sources": {
            "h_normalized_codeflash": {
                "path": str(H_CODE.relative_to(REPO)),
                "sha256": H_SHA256,
                "size": len(h),
            },
            "f_source_range_dump": {
                "path": str(F_SOURCE.relative_to(REPO)),
                "sha256": F_SOURCE_SHA256,
                "size": len(f_source),
            },
            "f_normalized_first_mib": {
                "sha256": F_NORMALIZED_SHA256,
                "size": len(f),
                "normalization": "first 1 MiB of 2-MiB range dump; upper half is not used as H/F code-equality evidence",
            },
            "h_corrected_decompiler_corpus": {
                "path": str(corpus.relative_to(REPO)) if corpus.is_relative_to(REPO) else str(corpus),
                "sha256": corpus_sha,
            },
        },
        "carrier_candidate": {
            "start": f"0x{POCKET_LO:08X}",
            "end_inclusive": f"0x{POCKET_HI:08X}",
            "end_exclusive": f"0x{POCKET_END:08X}",
            "size": POCKET_END - POCKET_LO,
            "first_normalized_direct_reference": f"0x{first_ref:08X}",
            "normalized_direct_reference_count_inside": len(pocket_refs),
            "normalization": {
                "application_gp": f"0x{APP_GP:08X}",
                "covered_forms": ["absolute FEBFxxxx references", "simple GP offsets 0x4800..0x57FF"],
                "boundary": "This is a negative census of recovered direct references and simple GP-offset aliases only. Arbitrary computed aliases, DMA ownership and undocumented hardware writers are outside the static proof; live canary validation is required before treating the pocket as retained/free.",
            },
        },
        "xcp_mailbox_candidate": {
            "start": f"0x{MAILBOX_LO:08X}",
            "end_exclusive": f"0x{MAILBOX_END:08X}",
            "size": MAILBOX_END - MAILBOX_LO,
            "normalized_direct_reference_count_inside": len(mailbox_refs),
            "xcp_shadow_write_window": ["0xFEBF7C00", "0xFEBFFBFF"],
            "startup_shadow_copy_end_inclusive": "0xFEBFF9EF",
            "boundary": "Zero recovered normalized direct references does not prove the mailbox is free of computed/DMA ownership; it is a staging/observation candidate for isolated live validation.",
        },
        "application_mpu": {
            "loader_entry": "0x0005EB14",
            "bounds_table": "0x0002D1E4",
            "ctx0_attr_table": "0x0002D264",
            "ctx1_attr_table": "0x0002D2A4",
            "regions": regions,
            "carrier_region_index": 5,
            "carrier_region": region5,
            "mpat_bit_semantics": {
                "bit5": "SX",
                "bit4": "SW",
                "bit3": "SR",
                "bit2": "UX",
                "bit1": "UW",
                "bit0": "UR",
            },
            "carrier_permission_conclusion": "Region 5 is supervisor read/write/execute (MPAT 0xB8) in both recovered H application MPU contexts and has no user permissions.",
        },
        "startup_scheduler_contract": {
            "application_context_init": "0x0006A8C4",
            "startup_coordinator": "0x0005CAAC",
            "startup_jarl_first": f"0x{startup_first:08X}",
            "startup_jarl_after": f"0x{startup_after:08X}",
            "startup_jarl_count": startup_count,
            "startup_final_init": "0x000694FA",
            "foreground_scheduler": "0x0005F30C",
            "foreground_tick_counter": "0xFEBE38EF",
        },
        "selected_functions": selected,
        "h_f_exact_transfer": {
            "all_ranges_byte_equal": all(row["byte_equal"] for row in transfers),
            "ranges": transfers,
            "boundary": "Only the listed H/F code/data ranges are transferred by exact byte equality. This does not assert whole-image identity or live RAM-state identity.",
        },
        "static_conclusion": {
            "target_native_carrier_candidate_identified": True,
            "carrier_candidate_size": POCKET_END - POCKET_LO,
            "carrier_supervisor_rwx_both_contexts": True,
            "carrier_zero_normalized_direct_refs": True,
            "mailbox_zero_normalized_direct_refs": True,
            "h_f_prerequisites_transfer_byte_exact": True,
            "carrier_retention_live_verified": False,
            "live_canary_required": True,
            "vehicle_actuation_authorized": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()
    obj = build(args.corpus)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
