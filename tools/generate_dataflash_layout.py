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

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
DF = (REPO / "firmware" / "RH850_P1M-E_DataFlash.bin").read_bytes()
TP = 0x23EE4
JOB_COUNT = struct.unpack_from("<H", CF, TP + 0x2EF8)[0]
JOB_TABLE = TP + 0x2EFC
STORAGE_MAP = TP + 0x3924
OBJECT_TABLE = 0x2B0AC
CHECKPOINT_COUNT = struct.unpack_from("<H", CF, 0x2AF10)[0]
CHECKPOINT_TABLE = 0x2AF2C
OWNER_MAP = 0x2B1B0
DF_BASE = 0xFF200000

u16 = lambda b, a: struct.unpack_from("<H", b, a)[0]


def build_rows():
    jobs_by_storage: dict[int, list[int]] = {}
    for job in range(JOB_COUNT):
        cfg = u16(CF, JOB_TABLE + job * 16 + 8)
        if cfg not in (0xFFFE, 0xFFFF):
            jobs_by_storage.setdefault(cfg, []).append(job)

    # The two-byte table at 0x2B1B0 assigns every persistent NvM block to one
    # of the firmware's two logical ownership classes. Byte 0 is the logical
    # object index; byte 1 is 0 for checkpoint rings and 1 for triplicate
    # raw/XOR55/XORAA objects. Blocks 0/1 are sentinels/non-persistent.
    jobs_by_owner: dict[tuple[int, int], list[int]] = {}
    for job in range(2, JOB_COUNT):
        owner_index, owner_class = struct.unpack_from("<BB", CF, OWNER_MAP + job * 2)
        jobs_by_owner.setdefault((owner_class, owner_index), []).append(job)

    checkpoint_desc = [
        struct.unpack_from("<HHHHI", CF, CHECKPOINT_TABLE + index * 12)
        for index in range(CHECKPOINT_COUNT)
    ]
    redundant_desc = [
        struct.unpack_from("<HHI", CF, OBJECT_TABLE + index * 8)
        for index in range(16)
    ]

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
        owner_class_name = ""
        owner_index: int | str = ""
        owner_enabled = ""
        owner_slot: int | str = ""
        obj: int | str = ""
        encoding = ""
        generation = ""
        inverse = ""
        counter_valid = ""
        if jobs:
            job = jobs[-1]  # storage index 1 aliases jobs 0 and 2; job 2 is persistent.
            map_index, map_class = struct.unpack_from("<BB", CF, OWNER_MAP + job * 2)
            owner_index = map_index
            members = jobs_by_owner[(map_class, map_index)]
            owner_slot = members.index(job)
            if map_class == 1:
                owner_class_name = "triplicate"
                length, base_block, _ram = redundant_desc[map_index]
                owner_enabled = "yes" if base_block != 0xFFFF else "no"
                obj = map_index
                encoding = ("raw", "xor55", "xoraa")[owner_slot]
            else:
                owner_class_name = "checkpoint"
                data_length, ring_blocks, base_block, _reserved, _ram = checkpoint_desc[map_index]
                owner_enabled = "yes" if base_block != 0xFFFF and ring_blocks else "no"
                if owner_enabled == "yes":
                    generation_value = struct.unpack_from("<I", record, 4)[0]
                    inverse_offset = 8 + max(data_length, 56)
                    inverse_value = struct.unpack_from("<I", record, inverse_offset)[0]
                    generation = f"0x{generation_value:08X}"
                    inverse = f"0x{inverse_value:08X}"
                    counter_valid = "yes" if inverse_value == (~generation_value & 0xFFFFFFFF) else "no"
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
            "owner_class": owner_class_name,
            "owner_index": owner_index,
            "owner_enabled": owner_enabled,
            "owner_slot": owner_slot,
            "secoc_object": obj,
            "copy_encoding": encoding,
            "checkpoint_generation": generation,
            "checkpoint_inverse": inverse,
            "checkpoint_counter_valid": counter_valid,
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=Path,
                        default=REPO / "data" / "dataflash_nvm_records.csv")
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
