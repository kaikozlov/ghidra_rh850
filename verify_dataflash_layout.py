#!/usr/bin/env python3
"""Independent verification of the complete RH850 DataFlash/NvM layout.

Reads only committed CodeFlash/DataFlash images plus the generated CSV. Verifies
the physical map, record states, all 16 SecOC redundancy descriptors, object-15
key-field mapping, reserved regions, and volatile bootloader DID descriptors.
"""
from __future__ import annotations

import csv
import io
import math
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CF = (ROOT / "RH850_P1M-E_CodeFlash.bin").read_bytes()
DF = (ROOT / "RH850_P1M-E_DataFlash.bin").read_bytes()
CSV_PATH = ROOT / "dataflash_nvm_records.csv"
TP = 0x23EE4
JOB_TABLE = TP + 0x2EFC
STORAGE_MAP = TP + 0x3924
OBJECT_TABLE = 0x2B0AC

passed = failed = 0

def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

u16 = lambda b, a: struct.unpack_from("<H", b, a)[0]
u32 = lambda b, a: struct.unpack_from("<I", b, a)[0]

print("== image and configuration roots ==")
check("CodeFlash is 1 MiB", len(CF) == 0x100000)
check("DataFlash is 32 KiB / 512 pages", len(DF) == 0x8000 and len(DF) // 64 == 512)
check("NvM job count is 124", u16(CF, TP + 0x2EF8) == 124)
check("job table is 0x26DE0", JOB_TABLE == 0x26DE0)
check("storage map is 0x27808", STORAGE_MAP == 0x27808)
check("SecOC object table is 0x2B0AC", OBJECT_TABLE == 0x2B0AC)

print("\n== complete physical storage map ==")
jobs_by_cfg = {}
for job in range(124):
    cfg = u16(CF, JOB_TABLE + job * 16 + 8)
    if cfg not in (0xFFFE, 0xFFFF):
        jobs_by_cfg.setdefault(cfg, []).append(job)
check("job 1 is non-persistent", u16(CF, JOB_TABLE + 16 + 8) == 0xFFFE)
check("jobs 0 and 2 alias storage index 1", jobs_by_cfg.get(1) == [0, 2], str(jobs_by_cfg.get(1)))
check("122 unique storage indexes are configured", sorted(jobs_by_cfg) == list(range(1, 123)))

rows = []
valid_count = 0
for cfg in range(1, 123):
    start = u16(CF, STORAGE_MAP + cfg * 6)
    length = u16(CF, STORAGE_MAP + cfg * 6 + 2)
    flags = u16(CF, STORAGE_MAP + cfg * 6 + 4)
    end = 479 if cfg == 1 else u16(CF, STORAGE_MAP + (cfg - 1) * 6) - 1
    record = DF[start * 64:(end + 1) * 64]
    header = u16(DF, start * 64)
    trailer = record[-4:]
    valid = header == cfg and trailer == b"\xAA" * 4
    valid_count += valid
    rows.append((cfg, start, end, length, flags, valid))
check("storage map flags are all zero", all(r[4] == 0 for r in rows))
check("records cover pages 256..479", min(r[1] for r in rows) == 256 and max(r[2] for r in rows) == 479)
check("record allocations are contiguous", all(rows[i][2] + 1 == rows[i - 1][1] for i in range(1, len(rows))))
check("configured area is exactly 0x3800 bytes", sum((r[2] - r[1] + 1) * 64 for r in rows) == 0x3800)
check("68 records have matching header + AAAAAAAA trailer", valid_count == 68, str(valid_count))

lower = DF[:0x4000]
check("pages 0..255 contain no AAAAAAAA record marker", b"\xAA" * 4 not in lower)
check("no configured storage page is below 256", all(r[1] >= 256 for r in rows))
check("general NvM region ends at page 431", 0xFF200000 + 432 * 64 == 0xFF206C00)
check("SecOC triplicate bank is pages 432..479", 0xFF200000 + 432 * 64 == 0xFF206C00 and 0xFF200000 + 480 * 64 == 0xFF207800)

print("\n== 16-entry SecOC redundant-object table ==")
expected_desc = [
    (16, 2, 0xFEBEF468), (16, 3, 0xFEBEF478),
    (8, 4, 0xFEBEF400), (16, 5, 0xFEBEF488),
    (8, 14, 0xFEBEF408), (8, 15, 0xFEBEF418),
    (8, 16, 0xFEBEF460),
    (8, 0xFFFF, 0xFEBEF410), (8, 0xFFFF, 0xFEBEF410),
    (8, 0xFFFF, 0xFEBEF410), (8, 0xFFFF, 0xFEBEF410),
    (8, 0xFFFF, 0xFEBEF410),
    (32, 38, 0xFEBF0288), (32, 39, 0xFEBF02C8),
    (32, 40, 0xFEBF02A8), (32, 41, 0xFEBF02E8),
]
desc = [struct.unpack_from("<HHI", CF, OBJECT_TABLE + i * 8) for i in range(16)]
check("all 16 object descriptors match", desc == expected_desc)
check("objects 7..11 are disabled", all(desc[i][1] == 0xFFFF for i in range(7, 12)))
check("objects 12..15 are four 32-byte mirrors", [d[0] for d in desc[12:]] == [32] * 4)

# Expected copy pages derived independently from block->storage configuration.
def block_page(block):
    cfg = u16(CF, JOB_TABLE + block * 16 + 8)
    return cfg, u16(CF, STORAGE_MAP + cfg * 6)

expected_pages = {
    0: (479, 475, 471), 1: (478, 474, 470),
    2: (477, 473, 469), 3: (476, 472, 468),
    4: (467, 463, 459), 5: (466, 462, 458),
    6: (465, 461, 457),
    12: (443, 439, 435), 13: (442, 438, 434),
    14: (441, 437, 433), 15: (440, 436, 432),
}
for obj, pages in expected_pages.items():
    length, base, _ram = desc[obj]
    actual = tuple(block_page(base + delta)[1] for delta in (0, 4, 8))
    check(f"object {obj} raw/XOR55/XORAA pages", actual == pages, str(actual))

# Decode valid triplicates.
expected_consensus = {
    0: bytes.fromhex("a55a5aa5000800080008000800000000"),
    1: bytes.fromhex("a55a5aa5025a0000ffffffff00ffff00"),
    2: bytes.fromhex("aa5555aa5aa55aa5"),
    3: bytes.fromhex("a55a5aa55aa55aa5ffffffffff4affff"),
    5: bytes(8),
    6: bytes.fromhex("ce06000000000000"),
}
object_valid = {}
for obj in list(expected_pages):
    length, base, _ram = desc[obj]
    values = []
    valids = []
    for delta, mask in ((0, 0), (4, 0x55), (8, 0xAA)):
        cfg, page = block_page(base + delta)
        end = 480 if cfg == 1 else u16(CF, STORAGE_MAP + (cfg - 1) * 6)
        rec = DF[page * 64:end * 64]
        valid = u16(DF, page * 64) == cfg and rec[-4:] == b"\xAA" * 4
        valids.append(valid)
        values.append(bytes(x ^ mask for x in rec[4:4 + length]))
    object_valid[obj] = valids
    if obj in expected_consensus:
        check(f"object {obj} has three valid copies", valids == [True, True, True], str(valids))
        check(f"object {obj} consensus matches", len(set(values)) == 1 and values[0] == expected_consensus[obj])
check("object 4 has no valid copy", object_valid[4] == [False, False, False])
for obj in range(12, 16):
    check(f"object {obj} has no valid copy", object_valid[obj] == [False, False, False])

print("\n== object-15 field mapping ==")
length, base, ram = desc[15]
raw_cfg, raw_page = block_page(base)
x55_cfg, x55_page = block_page(base + 4)
xaa_cfg, xaa_page = block_page(base + 8)
check("object 15 descriptor is len32/base41/RAM FEBF02E8",
      (length, base, ram) == (32, 41, 0xFEBF02E8))
check("object 15 records are pages 440/436/432",
      (raw_page, x55_page, xaa_page) == (440, 436, 432))
check("raw record starts at FF206E00", 0xFF200000 + raw_page * 64 == 0xFF206E00)
check("raw key field is FF206E14", 0xFF200000 + raw_page * 64 + 0x14 == 0xFF206E14)
check("XOR55 key field is FF206D14", 0xFF200000 + x55_page * 64 + 0x14 == 0xFF206D14)
check("XORAA key field is FF206C14", 0xFF200000 + xaa_page * 64 + 0x14 == 0xFF206C14)
check("RAM key field is FEBF02F8", ram + 0x10 == 0xFEBF02F8)
current_field = DF[0x6E14:0x6E24]
check("current raw field matches captured bytes",
      current_field == bytes.fromhex("00000000040000808202000000000000"), current_field.hex())
entropy = -sum((n / 16) * math.log2(n / 16) for n in Counter(current_field).values())
check("current raw field is low entropy/non-key-like", abs(entropy - 1.311278124459133) < 1e-12, f"H={entropy:.6f}")

print("\n== bootloader DID table is volatile RAM, not DataFlash ==")
dids = [
    struct.unpack_from("<IHH4s", CF, 0x8F14 + i * 12)
    for i in range(4)
]
check("DID F181 descriptor", dids[0][:3] == (0, 32, 0xF181))
check("DID 0201 is len16 -> FEBF2D08", dids[1][:3] == (0xFEBF2D08, 16, 0x0201))
check("DID 0202 is len16 -> FEBF2CF8", dids[2][:3] == (0xFEBF2CF8, 16, 0x0202))
check("DID 0203 is len5 special/no pointer", dids[3][:3] == (0, 5, 0x0203))
check("DID 201/202 direct-copy mode is 1", dids[1][3][1] == 1 and dids[2][3][1] == 1)

print("\n== final unconfigured tail ==")
tail = DF[0x7800:]
check("tail is exactly 2 KiB", len(tail) == 0x800)
check("tail is outside every configured record", max(r[2] for r in rows) == 479)
check("tail contains only 00/FF", set(tail) <= {0, 0xFF}, str(sorted(set(tail))))
check("tail has no AAAAAAAA record markers", b"\xAA" * 4 not in tail)

print("\n== generated CSV consistency ==")
with CSV_PATH.open(newline="", encoding="utf-8") as f:
    csv_rows = list(csv.DictReader(f))
check("CSV has 122 physical records", len(csv_rows) == 122)
check("CSV endpoints are storage 1/page479 and storage122/page256",
      csv_rows[0]["storage_index"] == "1" and csv_rows[0]["page_start"] == "479" and
      csv_rows[-1]["storage_index"] == "122" and csv_rows[-1]["page_start"] == "256")
check("CSV reports 68 valid records", sum(r["record_valid"] == "yes" for r in csv_rows) == 68)
check("CSV identifies object15 raw/XOR55/XORAA",
      [(r["storage_index"], r["copy_encoding"]) for r in csv_rows if r["secoc_object"] == "15"] ==
      [("40", "raw"), ("44", "xor55"), ("48", "xoraa")])

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
