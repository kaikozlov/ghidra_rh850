#!/usr/bin/env python3
"""Independent verification of the corrected SecOC-associated NvM analysis.

Reads only the committed CodeFlash/DataFlash split images. It verifies the object
descriptors, AUTOSAR NvM service mapping, triplicate DataFlash records, decoded
RAM values, NvM page ceiling, and the unconfigured final 2 KiB DataFlash tail.
It covers the original objects 0..3 correction; verify_dataflash_layout.py checks
the complete 16-object map and field-known object-15 key location.
"""
from pathlib import Path
import struct
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
DF = (REPO / "firmware" / "RH850_P1M-E_DataFlash.bin").read_bytes()

passed = failed = 0

def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += ok
    failed += not ok
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

u8 = lambda b, a: b[a]
u16 = lambda b, a: struct.unpack_from("<H", b, a)[0]
u32 = lambda b, a: struct.unpack_from("<I", b, a)[0]

print("== static sizes and configuration roots ==")
check("CodeFlash is 1 MiB", len(CF) == 0x100000, hex(len(CF)))
check("DataFlash is 32 KiB", len(DF) == 0x8000, hex(len(DF)))
check("redundant object count @ 0x2AF12 is 16", u16(CF, 0x2AF12) == 16)
check("object request queue has 49 entries", u8(CF, 0x2AF2B) == 49)

# Descriptor: uint16 length, uint16 NvM base block, uint32 RAM mirror.
expected_desc = [
    (16, 2, 0xFEBEF468),
    (16, 3, 0xFEBEF478),
    (8,  4, 0xFEBEF400),
    (16, 5, 0xFEBEF488),
]
print("\n== redundant object descriptors @ 0x2B0AC ==")
for obj, expected in enumerate(expected_desc):
    a = 0x2B0AC + obj * 8
    actual = (u16(CF, a), u16(CF, a + 2), u32(CF, a + 4))
    check(f"object {obj} descriptor", actual == expected,
          f"len={actual[0]} base={actual[1]} ram={actual[2]:#x}")

# Application TP is 0x23EE4. Its configured NvM service map starts at TP+0x38BC.
TP = 0x23EE4
MAGIC_TABLE = TP + 0x38BC
READ_ENTRY = MAGIC_TABLE + 0x10
WRITE_ENTRY = MAGIC_TABLE + 0x18
print("\n== AUTOSAR NvM service identification ==")
check("magic table is at 0x277A0", MAGIC_TABLE == 0x277A0)
check("service 0x06 maps to 0xA1A62093",
      (u32(CF, READ_ENTRY), u32(CF, READ_ENTRY + 4)) == (6, 0xA1A62093))
check("service 0x07 maps to 0x22AA8A36",
      (u32(CF, WRITE_ENTRY), u32(CF, WRITE_ENTRY + 4)) == (7, 0x22AA8A36))
services = [u32(CF, MAGIC_TABLE + 0x10 + i * 8) for i in range(9)]
check("accepted service list matches NvM family",
      services == [6, 7, 8, 10, 22, 23, 24, 12, 13], str(services))
check("0x72F58 wrapper embeds ReadBlock magic",
      (0xA1A62093).to_bytes(4, "little") in CF[0x72F58:0x72F84])
check("0x72F84 wrapper embeds WriteBlock magic",
      (0x22AA8A36).to_bytes(4, "little") in CF[0x72F84:0x72FB0])

# Job descriptor +8 gives an index into TP+0x3924; first uint16 of that
# six-byte storage record is the DataFlash page.
JOB_COUNT = u16(CF, TP + 0x2EF8)
JOB_TABLE = TP + 0x2EFC
STORAGE_MAP = TP + 0x3924
expected_pages = {
    2: 479, 6: 475, 10: 471,
    3: 478, 7: 474, 11: 470,
    4: 477, 8: 473, 12: 469,
    5: 476, 9: 472, 13: 468,
}
print("\n== NvM job to DataFlash mapping ==")
check("NvM job count is 124", JOB_COUNT == 124, str(JOB_COUNT))
configured_pages = []
for job in range(JOB_COUNT):
    cfg = u16(CF, JOB_TABLE + job * 16 + 8)
    if cfg in (0xFFFE, 0xFFFF):
        continue
    entry = STORAGE_MAP + cfg * 6
    if entry + 2 <= len(CF):
        configured_pages.append(u16(CF, entry))
for job, expected_page in expected_pages.items():
    cfg = u16(CF, JOB_TABLE + job * 16 + 8)
    page = u16(CF, STORAGE_MAP + cfg * 6)
    check(f"NvM block/job {job} maps to page {expected_page}", page == expected_page)

objects = [
    (0, 16, (479, 475, 471), bytes.fromhex("a55a5aa5000800080008000800000000")),
    (1, 16, (478, 474, 470), bytes.fromhex("a55a5aa5025a0000ffffffff00ffff00")),
    (2,  8, (477, 473, 469), bytes.fromhex("aa5555aa5aa55aa5")),
    (3, 16, (476, 472, 468), bytes.fromhex("a55a5aa55aa55aa5ffffffffff4affff")),
]
print("\n== decode raw / XOR55 / XORAA triplicate records ==")
for obj, length, pages, expected in objects:
    decoded = []
    for copy, (page, mask) in enumerate(zip(pages, (0x00, 0x55, 0xAA))):
        record = DF[page * 64:(page + 1) * 64]
        stored = record[4:4 + length]
        value = bytes(x ^ mask for x in stored)
        decoded.append(value)
        check(f"object {obj} copy {copy} page header identifies NvM block",
              u16(DF, page * 64) == (1 + obj + copy * 4))
    check(f"object {obj} three copies decode identically", len(set(decoded)) == 1)
    check(f"object {obj} decoded structured value", decoded[0] == expected, decoded[0].hex())

print("\n== normal NvM boundary and unconfigured/reserved tail ==")
check("highest configured normal NvM page is 479", max(configured_pages) == 479,
      str(max(configured_pages)))
check("no normal NvM job maps into pages 480..511",
      all(page < 480 for page in configured_pages))
tail = DF[480 * 64:]
check("unconfigured tail is exactly 2 KiB", len(tail) == 0x800)
check("tail contains only 0x00 and 0xFF", set(tail) <= {0x00, 0xFF}, str(sorted(set(tail))))
check("tail is non-erased/masked-looking rather than all 0xFF",
      0 in tail and 0xFF in tail, f"00={tail.count(0)} ff={tail.count(0xff)}")
check("tail starts at VA 0xFF207800", 0xFF200000 + 480 * 64 == 0xFF207800)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
