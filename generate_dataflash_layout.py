#!/usr/bin/env python3
"""Generate the complete configured NvM/DataFlash record map as CSV.

Reads only the committed split images. The map is defined by the 124-entry NvM
block table at CodeFlash 0x26DE0 and the six-byte storage table at 0x27808.
"""
from __future__ import annotations

import argparse
import csv
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CF = (ROOT / "RH850_P1M-E_CodeFlash.bin").read_bytes()
DF = (ROOT / "RH850_P1M-E_DataFlash.bin").read_bytes()
TP = 0x23EE4
JOB_COUNT = struct.unpack_from("<H", CF, TP + 0x2EF8)[0]
JOB_TABLE = TP + 0x2EFC
STORAGE_MAP = TP + 0x3924
OBJECT_TABLE = 0x2B0AC
DF_BASE = 0xFF200000

u16 = lambda b, a: struct.unpack_from("<H", b, a)[0]


def build_rows():
    jobs_by_storage: dict[int, list[int]] = {}
    for job in range(JOB_COUNT):
        cfg = u16(CF, JOB_TABLE + job * 16 + 8)
        if cfg not in (0xFFFE, 0xFFFF):
            jobs_by_storage.setdefault(cfg, []).append(job)

    object_by_job: dict[int, tuple[int, str]] = {}
    for obj in range(16):
        length, base_block, _ram = struct.unpack_from("<HHI", CF, OBJECT_TABLE + obj * 8)
        if base_block == 0xFFFF:
            continue
        for delta, encoding in ((0, "raw"), (4, "xor55"), (8, "xoraa")):
            object_by_job[base_block + delta] = (obj, encoding)

    rows = []
    # Storage indexes 1..122 are the configured physical records. Index 0 is a
    # sentinel (page FFFF); job 1 is non-persistent; jobs 0 and 2 alias index 1.
    for cfg in range(1, 123):
        page_start = u16(CF, STORAGE_MAP + cfg * 6)
        payload_length = u16(CF, STORAGE_MAP + cfg * 6 + 2)
        page_end = 479 if cfg == 1 else u16(CF, STORAGE_MAP + (cfg - 1) * 6) - 1
        start = page_start * 64
        end = (page_end + 1) * 64
        record = DF[start:end]
        header_index = u16(DF, start)
        trailer = record[-4:]
        valid = header_index == cfg and trailer == b"\xAA" * 4
        jobs = jobs_by_storage.get(cfg, [])
        memberships = [object_by_job[j] for j in jobs if j in object_by_job]
        obj = memberships[0][0] if memberships else ""
        encoding = memberships[0][1] if memberships else ""
        rows.append({
            "storage_index": cfg,
            "nvm_jobs": ";".join(str(j) for j in jobs),
            "page_start": page_start,
            "page_end": page_end,
            "va_start": f"0x{DF_BASE + start:08X}",
            "va_end": f"0x{DF_BASE + end - 1:08X}",
            "payload_length": payload_length,
            "allocation_bytes": len(record),
            "header_index": f"0x{header_index:04X}",
            "trailer": trailer.hex(),
            "record_valid": "yes" if valid else "no",
            "secoc_object": obj,
            "copy_encoding": encoding,
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=Path,
                        default=ROOT / "dataflash_nvm_records.csv")
    args = parser.parse_args()
    rows = build_rows()
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
