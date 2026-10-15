#!/usr/bin/env python3
"""Exact-F33 NvM descriptors, record markers and retained RAM observations.

The descriptor accessors at 74884/74892/748A2 and allocation helper 748B0
establish the six-byte table at 27634. The bound read by 77982 is at 27928.
Handle zero has page FFFF; the remaining descriptors include multi-page
allocations, not just the first 48 single-page records.

Record header/commit-marker checks are not checksum validation or application
copy consensus. Likewise, a direct-reference census cannot exclude transitive
learned-state influence on assist. This tool records those evidence boundaries
instead of treating a neutral-looking snapshot as an architectural proof.

All inputs are tracked. No payload or key bytes are printed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from tools import REPO_ROOT
from tools.targets.camry.support import camry_f33_corpus as f33

REPO = REPO_ROOT

F33_CODEFLASH = f33.IMAGE
F33_DATAFLASH = f33.DATAFLASH
F33_CORPUS = f33.CORPUS
F33_RAM = f33.CAPTURE / "raw-20260826/secoc-recovery/ram/local_ram_pe1.bin"
OUTPUT = REPO / "data/generated/camry_8965F3307000_dataflash_nvm_owners.json"

JOB_TABLE = 0x27634  # stride 6: u16 page, u16 payload length, u8 option, u8 opaque
JOB_COUNT = 0x27928
JOB_STRIDE = 6
DATAFLASH_BASE = 0xFF200000
PAGE_SIZE = 64

# Retained RAM windows. Their values alone do not identify logical NvM objects
# or establish whether they can influence the assist path transitively.
LEARNED_CELLS = {
    "staged_45b_block": (0xFEBE6A26, 45),
    "active_45b_block": (0xFEBE6A84, 45),
    "four_channel_offsets_staged": (0xFEBE6AD2, 8),
    "four_channel_offsets_active": (0xFEBE6AE6, 8),
    "window_6aaa": (0xFEBE6AAA, 16),
    "window_7d70": (0xFEBE7D70, 8),
    "window_7d78": (0xFEBE7D78, 8),
}

# Assist-funnel cells from VAR-104/CORR-135 (D0218 term/composition family).
FUNNEL_CELLS = (
    0xFEBEC43C, 0xFEBEC4C0, 0xFEBEC3BA, 0xFEBECC2C, 0xFEBEBF3C,
    0xFEBECB08, 0xFEBECB20, 0xFEBECC50, 0xFEBECC60,
)

CAPTURE_OFFSET_WORD = 0x0800


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_corpus_functions(path: Path) -> list[dict]:
    out = []
    with path.open() as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("record") == "metadata":
                continue
            out.append(rec)
    return out


def decode_job_table(codeflash: bytes) -> list[dict]:
    """Decode complete descriptors using the firmware's handle bound."""
    rows = []
    count = struct.unpack_from("<H", codeflash, JOB_COUNT)[0]
    for handle in range(count):
        off = JOB_TABLE + handle * JOB_STRIDE
        page, payload_len, option, opaque = struct.unpack_from("<HHBB", codeflash, off)
        # Literal 748B0 arithmetic; do not confuse this with 77314's payload
        # page count, which excludes record overhead.
        allocation_pages = (
            payload_len + (4 if payload_len > 32 else 0)
            + (12 if option else 4) + PAGE_SIZE
        ) >> 6
        rows.append({
            "handle": handle,
            "page": page,
            "payload_len": payload_len,
            "option_byte": option,
            "opaque_05": opaque,
            "allocation_pages": allocation_pages,
            "rom_offset": off,
        })
    return rows


def decode_dataflash_records(dump: bytes, jobs: list[dict]) -> list[dict]:
    """Check the handle and final-allocation marker, not complete validity."""
    out = []
    for job in jobs:
        if job["page"] == 0xFFFF:
            continue
        off = job["page"] * PAGE_SIZE
        size = job["allocation_pages"] * PAGE_SIZE
        if off + size > len(dump):
            raise ValueError(f"descriptor {job['handle']} extends beyond DataFlash")
        stored_handle = struct.unpack_from("<H", dump, off)[0]
        # 7786A compares the stored u16 with the actual descriptor handle.
        # 778FE/77AA8 locate and compare the last word of the whole allocation.
        header_matches = stored_handle == job["handle"]
        marker_present = struct.unpack_from("<I", dump, off + size - 4)[0] == 0xAAAAAAAA
        out.append({
            "handle": job["handle"],
            "dataflash_address": f"0x{DATAFLASH_BASE + off:08x}",
            "stored_handle": stored_handle,
            "header_matches_handle": header_matches,
            "commit_marker_present": marker_present,
            "markers_match": header_matches and marker_present,
        })
    return out


def marker_census(records: list[dict]) -> dict:
    """Keep marker observations separate from logical copy identity."""
    matching = [r["handle"] for r in records if r["markers_match"]]
    return {
        "mapped_records": len(records),
        "records_with_both_markers": len(matching),
        "matching_handles": matching,
        "single_page_handles_1_48_with_markers": sum(1 <= h <= 48 for h in matching),
        "checksum_or_copy_consensus_checked": False,
    }


def main() -> int:
    doc = (__doc__ or "").splitlines()
    ap = argparse.ArgumentParser(description=doc[0] if doc else "F33 DataFlash NvM owner closure")
    ap.add_argument("--output", type=Path, default=OUTPUT, help="write JSON artifact")
    ap.add_argument("--json", action="store_true", help="print JSON to stdout")
    args = ap.parse_args()

    codeflash = F33_CODEFLASH.read_bytes()
    dataflash = F33_DATAFLASH.read_bytes()
    corpus = load_corpus_functions(F33_CORPUS)

    jobs = decode_job_table(codeflash)
    records = decode_dataflash_records(dataflash, jobs)
    markers = marker_census(records)

    # Live learned-state values from the retained READY LocalRAM dump.
    ram = F33_RAM.read_bytes()
    ram_base = 0xFEBE0000
    live: dict[str, str] = {}
    for name, (va, n) in LEARNED_CELLS.items():
        live[name] = ram[va - ram_base:va - ram_base + n].hex()

    offsets = bytes.fromhex(live["four_channel_offsets_active"])
    four_channel_words_equal_0800 = all(b == CAPTURE_OFFSET_WORD for b in struct.unpack("<4H", offsets))
    staged_active_equal = live["staged_45b_block"] == live["active_45b_block"]

    # Instruction-anchored direct references survive decompiler renaming.
    # Neither this census nor an empty intersection is transitive dataflow.
    learned_fns, funnel_fns, both_fns, four_channel_consumers = [], [], [], []
    for rec in corpus:
        addresses = {
            int(ref["to_addr"], 16) for ref in rec["data_references"]
            if ref["to_space"] == "ram"
        }
        has_l = any(0xFEBE6A00 <= address < 0xFEBE6B00 for address in addresses)
        has_f = bool(addresses.intersection(FUNNEL_CELLS))
        if has_l:
            learned_fns.append(rec["entry_addr"])
        if has_f:
            funnel_fns.append(rec["entry_addr"])
        if has_l and has_f:
            both_fns.append(rec["entry_addr"])
        if any(0xFEBE6AD0 <= address < 0xFEBE6B00 for address in addresses):
            four_channel_consumers.append(rec["entry_addr"])

    result = {
        "schema": "camry-8965f3307000-dataflash-nvm-owner-closure-v2",
        "software_id": "8965F3307000",
        "question": "Does unexamined F33 DataFlash learned NvM state feed the assist funnel?",
        "inputs": {
            "codeflash": {"path": str(F33_CODEFLASH.relative_to(REPO)), "sha256": sha256(codeflash)},
            "dataflash": {"path": str(F33_DATAFLASH.relative_to(REPO)), "sha256": sha256(dataflash)},
            "corpus": {"path": str(F33_CORPUS.relative_to(REPO)), "functions": len(corpus)},
            "local_ram_ready": {
                "path": str(F33_RAM.relative_to(REPO)),
                "sha256": sha256(ram),
                "note": "post application->boot handoff READY snapshot",
            },
        },
        "job_table": {
            "rom_address": f"0x{JOB_TABLE:05x}",
            "decoded_from": ["0x74884", "0x74892", "0x748a2", "0x748b0", "0x77982"],
            "handle_count": len(jobs),
            "count_address": f"0x{JOB_COUNT:05x}",
            "layout": "u16 page; u16 payload length; u8 option; u8 opaque; stride6",
            "sentinel_handles": [job["handle"] for job in jobs if job["page"] == 0xFFFF],
            "descriptors": jobs,
        },
        "record_marker_census": markers,
        "record_markers": records,
        "live_learned_state": {
            **live,
            "four_channel_words_equal_0800": four_channel_words_equal_0800,
            "staged_active_equal_45b": staged_active_equal,
        },
        "census": {
            "method": "canonical instruction-anchored direct data references; not transitive closure",
            "functions_touching_learned_cells": len(learned_fns),
            "functions_touching_funnel_cells": len(funnel_fns),
            "functions_touching_both": both_fns,
            "four_channel_offset_consumers": len(four_channel_consumers),
        },
        "conclusion": {
            "dataflash_learned_state_feeds_assist_funnel": None,
            "reasons": [
                "a same-function reference intersection cannot exclude indirect state propagation",
                "equal staged/active snapshot values do not establish absence of a runtime dependency",
                "record markers do not identify application copy groups or validate all checksums",
            ],
        },
    }

    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text + "\n")
    if args.json:
        print(text)
    else:
        print(f"job table: {len(jobs)} handles at ROM 0x{JOB_TABLE:05x}")
        print(f"records with both markers: {markers['records_with_both_markers']}/{markers['mapped_records']}")
        print(f"live four-channel words equal 0x0800: {four_channel_words_equal_0800}")
        print(f"learned-cell functions: {len(learned_fns)}, funnel functions: {len(funnel_fns)}, both: {len(both_fns)}")
        print("assist influence: unresolved by this descriptor/snapshot/direct-reference analysis")
    return 0


if __name__ == "__main__":
    sys.exit(main())
