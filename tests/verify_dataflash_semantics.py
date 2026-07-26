#!/usr/bin/env python3
"""Verify DataFlash logical ownership, checkpoint records, and reserved regions.

Reads only committed CodeFlash/DataFlash images and the generated CSV. The checks
are independent of Ghidra and sibling repositories.
"""
from __future__ import annotations

import csv
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
DF = (REPO / "firmware" / "RH850_P1M-E_DataFlash.bin").read_bytes()
CSV_PATH = REPO / "data" / "dataflash_nvm_records.csv"
CHECKPOINT_CSV_PATH = REPO / "data" / "checkpoint_payload_map.csv"
TP = 0x23EE4
JOB_TABLE = TP + 0x2EFC
STORAGE_MAP = TP + 0x3924
CHECKPOINT_COUNT_ADDR = 0x2AF10
CHECKPOINT_TABLE = 0x2AF2C
REDUNDANT_TABLE = 0x2B0AC
OWNER_MAP = 0x2B1B0

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def physical_record(block: int) -> tuple[int, bytes, int]:
    storage = u16(CF, JOB_TABLE + block * 16 + 8)
    page_start = u16(CF, STORAGE_MAP + storage * 6)
    page_end = 479 if storage == 1 else u16(CF, STORAGE_MAP + (storage - 1) * 6) - 1
    record = DF[page_start * 64:(page_end + 1) * 64]
    return storage, record, u16(CF, STORAGE_MAP + storage * 6 + 2)


def record_valid(storage: int, record: bytes) -> bool:
    return struct.unpack_from("<H", record)[0] == storage and record[-4:] == b"\xAA" * 4


print("== logical-owner table ==")
check("checkpoint descriptor count is 32", u16(CF, CHECKPOINT_COUNT_ADDR) == 32)
owners = [struct.unpack_from("<BB", CF, OWNER_MAP + block * 2) for block in range(124)]
check("NvM blocks 0/1 are owner sentinels", owners[:2] == [(0xFF, 0xFF)] * 2)
check("blocks 2..49 are triplicate class 1", all(kind == 1 for _index, kind in owners[2:50]))
check("blocks 50..123 are checkpoint class 0", all(kind == 0 for _index, kind in owners[50:]))

triplicate_blocks = {
    index: [block for block in range(2, 50) if owners[block] == (index, 1)]
    for index in range(16)
}
expected_triplicate = {
    index: [2 + group * 12 + offset + 4 * copy for copy in range(3)]
    for group in range(4)
    for offset, index in enumerate(range(group * 4, group * 4 + 4))
}
check("all 16 triplicate owners map to raw/XOR55/XORAA blocks",
      triplicate_blocks == expected_triplicate, repr(triplicate_blocks))

checkpoint_blocks = {
    index: [block for block in range(50, 124) if owners[block] == (index, 0)]
    for index in range(32)
}
expected_checkpoint = {
    0: [50, 51], 1: [52, 53], 2: [54, 55], 3: [56, 57],
    4: [58, 59], 5: list(range(64, 70)), 6: list(range(70, 76)),
    7: [62, 63], 8: [76, 77], 9: [78, 79], 10: [60, 61],
    11: [80, 81], 12: [82, 83], 13: [84, 85], 14: [86, 87],
    15: [88, 89], 16: [90, 91], 17: [92, 93], 18: [94, 95],
    19: [96, 97], 20: [98, 99], 21: [100, 101], 22: [102, 103],
    23: [104, 105], 24: [106, 107], 25: list(range(108, 112)),
    26: list(range(112, 116)), 27: [116, 117], 28: [118, 119],
    29: [], 30: [120, 121], 31: [122, 123],
}
check("all 74 checkpoint blocks map to 32 logical slots",
      checkpoint_blocks == expected_checkpoint, repr(checkpoint_blocks))
check("ownership classes cover every persistent block exactly once",
      sum(map(len, triplicate_blocks.values())) == 48 and
      sum(map(len, checkpoint_blocks.values())) == 74)

print("\n== checkpoint descriptors and record envelope ==")
descriptors = [
    struct.unpack_from("<HHHHI", CF, CHECKPOINT_TABLE + index * 12)
    for index in range(32)
]
enabled = [index for index, (_length, count, base, _reserved, _ram) in enumerate(descriptors)
           if count and base != 0xFFFF]
disabled = [index for index in range(32) if index not in enabled]
check("24 checkpoint descriptors are enabled", len(enabled) == 24, repr(enabled))
check("disabled checkpoint slots are exact", disabled == [16, 22, 25, 26, 28, 29, 30, 31], repr(disabled))
check("enabled descriptors own 56 ring blocks", sum(len(checkpoint_blocks[i]) for i in enabled) == 56)
check("disabled descriptors reserve 18 physical blocks", sum(len(checkpoint_blocks[i]) for i in disabled) == 18)
check("every enabled descriptor base/count matches owner map",
      all(checkpoint_blocks[i] == list(range(descriptors[i][2], descriptors[i][2] + descriptors[i][1]))
          for i in enabled))
check("every disabled descriptor uses FFFF base",
      all(descriptors[i][2] == 0xFFFF for i in disabled))
check("disabled slot 16 retains count two; other disabled counts are zero",
      descriptors[16][1] == 2 and all(descriptors[i][1] == 0 for i in disabled if i != 16))
check("checkpoint descriptor reserved halfwords are zero", all(desc[3] == 0 for desc in descriptors))

active_valid = active_invalid = disabled_valid = 0
valid_counters = 0
active_generations: dict[int, list[int]] = {index: [] for index in enabled}
for index, blocks in checkpoint_blocks.items():
    data_length = descriptors[index][0]
    expected_payload_length = max(data_length, 56) + 8
    for block in blocks:
        storage, record, payload_length = physical_record(block)
        valid = record_valid(storage, record)
        if index in enabled:
            check(f"block {block} checkpoint payload length", payload_length == expected_payload_length)
        generation = struct.unpack_from("<I", record, 4)[0]
        inverse = struct.unpack_from("<I", record, 8 + max(data_length, 56))[0]
        complement_ok = inverse == (~generation & 0xFFFFFFFF)
        if index in enabled:
            active_valid += int(valid)
            active_invalid += int(not valid)
            if valid:
                valid_counters += int(complement_ok)
                active_generations[index].append(generation)
        else:
            disabled_valid += int(valid)

check("50 enabled checkpoint records have valid outer envelopes", active_valid == 50, str(active_valid))
check("six enabled checkpoint ring copies are invalid", active_invalid == 6, str(active_invalid))
check("all disabled checkpoint records are invalid", disabled_valid == 0, str(disabled_valid))
check("all valid enabled checkpoints have generation complements", valid_counters == 50, str(valid_counters))
check("six-slot checkpoint 5 generations span 0x2782..0x2787",
      sorted(active_generations[5]) == list(range(0x2782, 0x2788)))
check("six-slot checkpoint 6 generations span 0x277B..0x2780",
      sorted(active_generations[6]) == list(range(0x277B, 0x2781)))

print("\n== triplicate/total validity accounting ==")
redundant_desc = [struct.unpack_from("<HHI", CF, REDUNDANT_TABLE + index * 8) for index in range(16)]
trip_enabled = [i for i, (_length, base, _ram) in enumerate(redundant_desc) if base != 0xFFFF]
trip_valid_enabled = trip_invalid_disabled = 0
for index, blocks in triplicate_blocks.items():
    for block in blocks:
        storage, record, _payload_length = physical_record(block)
        valid = record_valid(storage, record)
        if index in trip_enabled:
            trip_valid_enabled += int(valid)
        else:
            trip_invalid_disabled += int(not valid)
check("11 triplicate descriptors are enabled", trip_enabled == list(range(7)) + list(range(12, 16)))
check("18 enabled triplicate records are valid", trip_valid_enabled == 18, str(trip_valid_enabled))
check("all 15 disabled triplicate records are invalid", trip_invalid_disabled == 15)
check("total valid configured records remains 68", active_valid + trip_valid_enabled == 68)

print("\n== lower unallocated half and protected ranges ==")
all_pages = []
for block in range(2, 124):
    storage = u16(CF, JOB_TABLE + block * 16 + 8)
    all_pages.append(u16(CF, STORAGE_MAP + storage * 6))
check("no persistent owner starts below page 256", min(all_pages) == 256)
lower = DF[:0x4000]
lower_words = Counter(lower[offset:offset + 4] for offset in range(0, len(lower), 4))
check("lower half is exactly 256 pages / 4096 words", len(lower) == 0x4000 and sum(lower_words.values()) == 4096)
check("lower half contains no configured AAAAAAAA trailer", b"\xAA" * 4 not in lower)
check("lower readback word classes match captured image",
      (lower_words[b"\x00" * 4], lower_words[b"\xFF" * 4],
       4096 - lower_words[b"\x00" * 4] - lower_words[b"\xFF" * 4]) == (2250, 1306, 540))

protected = struct.unpack_from("<IIII", CF, 0x293E4)
check("compiled DataFlash protected-range table",
      protected == (0xFF207800, 0xFF207FFF, 0xFF206C00, 0xFF206EFF),
      repr(tuple(hex(value) for value in protected)))
check("DataFlash range validator starts at 0x4EAD8",
      CF[0x4EAD8:0x4EADC] == bytes.fromhex("400e20ff"), CF[0x4EAD8:0x4EADC].hex())
check("range validator references protected table 0x293E4",
      (0x293E4).to_bytes(4, "little") in CF[0x4EAD8:0x4EB1C])
check("optional objects 12..15 occupy protected range FF206C00..FF206EFF",
      min(physical_record(block)[0] for block in range(38, 50)) == 37 and
      432 * 64 == 0x6C00 and 444 * 64 - 1 == 0x6EFF)

tail = DF[0x7800:]
tail_words = Counter(tail[offset:offset + 4] for offset in range(0, len(tail), 4))
check("protected tail is exactly 2 KiB / 32 pages", len(tail) == 0x800)
check("tail contains only all-zero/all-one words", set(tail_words) == {b"\x00" * 4, b"\xFF" * 4})
check("tail readback has 236 zero and 276 all-one words",
      (tail_words[b"\x00" * 4], tail_words[b"\xFF" * 4]) == (236, 276))

print("\n== generated CSV semantic columns ==")
with CSV_PATH.open(newline="", encoding="utf-8") as stream:
    csv_rows = list(csv.DictReader(stream))
check("CSV has 122 physical records", len(csv_rows) == 122)
check("CSV ownership split is 48 triplicate / 74 checkpoint",
      Counter(row["owner_class"] for row in csv_rows) == {"triplicate": 48, "checkpoint": 74})
check("CSV enabled split matches firmware descriptors",
      sum(row["owner_class"] == "checkpoint" and row["owner_enabled"] == "yes" for row in csv_rows) == 56 and
      sum(row["owner_class"] == "checkpoint" and row["owner_enabled"] == "no" for row in csv_rows) == 18)
check("CSV maps disabled triplicate objects 7..11",
      {int(row["owner_index"]) for row in csv_rows
       if row["owner_class"] == "triplicate" and row["owner_enabled"] == "no"} == set(range(7, 12)))
check("CSV reports checkpoint generations for 56 enabled ring records",
      sum(bool(row["checkpoint_generation"]) for row in csv_rows) == 56)
check("CSV identifies all 50 valid checkpoint complements",
      sum(row["owner_class"] == "checkpoint" and row["record_valid"] == "yes" and
          row["checkpoint_counter_valid"] == "yes" for row in csv_rows) == 50)

print("\n== checkpoint payload producer map ==")
with CHECKPOINT_CSV_PATH.open(newline="", encoding="utf-8") as stream:
    payload_rows = list(csv.DictReader(stream))
check("checkpoint payload CSV has all 32 descriptors", len(payload_rows) == 32)
check("checkpoint payload CSV geometry matches raw descriptors",
      all(int(row["object_index"]) == index and
          int(row["data_length"]) == descriptors[index][0] and
          int(row["ring_blocks"]) == descriptors[index][1] and
          row["ram_mirror"] == f"0x{descriptors[index][4]:08X}"
          for index, row in enumerate(payload_rows)))
check("checkpoint payload CSV marks exact active objects",
      [int(row["object_index"]) for row in payload_rows if row["enabled"] == "yes"] == enabled)
expected_writers = {
    0: "0x5110A", 1: "0x51B70", 2: "0x51B70", 3: "0x51B70",
    4: "0x53492", 5: "0x477C8;0x47958", 6: "0x38CEC;0x38EAA",
    7: "0xB7E4A", 8: "0xBAF46", 9: "0xBAFB2", 10: "0x51176",
    11: "0xBB286", 12: "0x4528C;0x453A2", 13: "0xBBCC4",
    14: "0x538D4", 15: "0xBB482;0xBB508", 17: "0x53FC4",
    18: "0x53FC4", 19: "0x53FC4", 20: "0x53F5E", 21: "0x53F5E",
    23: "0x53F5E", 24: "0x34FB6", 27: "",
}
check("all active checkpoint objects have bounded writer ownership",
      {int(row["object_index"]): row["writer_functions"]
       for row in payload_rows if row["enabled"] == "yes"} == expected_writers)
check("object 27 remains an explicit configured orphan",
      payload_rows[27]["evidence_name"] == "configured_orphan_slot" and
      payload_rows[27]["data_length"] == "72" and
      payload_rows[27]["writer_functions"] == "")
check("disabled checkpoint objects receive no invented payload semantics",
      all(row["evidence_name"] == "disabled" for row in payload_rows
          if row["enabled"] == "no"))

print("\n== checkpoint writer field assembly machine checks ==")
# Object-index + secoc_nvm_object_update (0x65CD8) call sites, plus layout loop bounds.
check("object 4 first group copies 18 halfwords",
      CF[0x534B6:0x534BA] == bytes.fromhex("0106eeff"))  # addi -0x12
check("object 4 second group copies 10 halfwords",
      CF[0x534CE:0x534D0] == bytes.fromhex("6a0a"))  # cmp 0xa
check("object 4 calls update with object index 4",
      CF[0x534DA:0x534E0] == bytes.fromhex("043281fffc27"),
      CF[0x534DA:0x534E0].hex())
check("object 5 restore/writer embeds signed sentinel 32000",
      CF[0x47808:0x4780C] == bytes.fromhex("200e007d"), CF[0x47808:0x4780C].hex())
check("object 5 persist path moves index 5 then calls update",
      CF[0x4796E:0x47970] == bytes.fromhex("0532") and
      CF[0x47982:0x47986] == bytes.fromhex("81ff56e3"),
      CF[0x4796E:0x47986].hex())
check("object 5 persist zero-fills reserved u32",
      CF[0x47978:0x4797A] == bytes.fromhex("0305"))  # sst.w 0x4[ep], r0
check("object 12 persist moves index 0xC then calls update",
      CF[0x452F8:0x452FA] == bytes.fromhex("0c32") and
      CF[0x4530A:0x4530E] == bytes.fromhex("82ffce09"),
      CF[0x452F8:0x4530E].hex())
check("object 12 packs reserved-zero and pad bytes before update",
      CF[0x45304:0x4530A] == bytes.fromhex("030589039103"))
check("object 12 reset writer also calls update(0xC)",
      CF[0x453DC:0x453E0] == bytes.fromhex("82fffc08"))
check("object 14 copies 12 trigger bytes then 3 history entries",
      CF[0x538EC:0x538EE] == bytes.fromhex("6c0a") and  # cmp 0xc
      CF[0x5393A:0x53948] == bytes.fromhex("630a9693b6dd03380e3281ff9423"),
      CF[0x5393A:0x53948].hex())
check("object 24 decrements countdown then calls update(0x18)",
      CF[0x34FCA:0x34FCC] == bytes.fromhex("5fea") and  # add -1,r29
      CF[0x34FE0:0x34FE8] == bytes.fromhex("2036180083fff40c"),
      CF[0x34FE0:0x34FE8].hex())
check("object 24 zero-fills reserved halfword before update",
      CF[0x34FDA:0x34FDC] == bytes.fromhex("8104"))  # sst.h 2[ep],r0

with tempfile.TemporaryDirectory() as directory:
    generated = Path(directory) / "checkpoint_payload_map.csv"
    result = subprocess.run(
        [sys.executable, str(REPO / "tools" / "generate_checkpoint_payload_map.py"),
         "-o", str(generated)], capture_output=True, text=True,
    )
    check("checkpoint payload generator exits successfully", result.returncode == 0,
          result.stderr.strip())
    check("checkpoint payload CSV regeneration is byte-for-byte deterministic",
          result.returncode == 0 and generated.read_bytes() == CHECKPOINT_CSV_PATH.read_bytes())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
