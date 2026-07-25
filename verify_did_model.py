#!/usr/bin/env python3
"""Independent raw-firmware checks for DID_MODEL.md (no Ghidra required)."""
from pathlib import Path
import struct
import sys

HERE = Path(__file__).resolve().parent
CF = (HERE / "RH850_P1M-E_CodeFlash.bin").read_bytes()
REPOS = HERE.parent

passed = 0
failed = 0

def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{mark}] {name}{suffix}")

print("== DID descriptor table ==")
DESC = struct.Struct("<IHHBBBB")
rows = [DESC.unpack_from(CF, 0x8F14 + i * DESC.size) for i in range(4)]
expected = [
    (0x00000000, 32, 0xF181, 1, 0, 0x02, 0),
    (0xFEBF2D08, 16, 0x0201, 2, 1, 0xFF, 0),
    (0xFEBF2CF8, 16, 0x0202, 2, 1, 0xFF, 0),
    (0x00000000,  5, 0x0203, 2, 1, 0xFF, 0),
]
check("descriptor size is 12 bytes", DESC.size == 12)
check("all four descriptors match", rows == expected, repr(rows))
check("F181 is the sole readable descriptor", [r[2] for r in rows if r[3] & 1] == [0xF181])
check("0201/0202/0203 are the writable descriptors",
      [r[2] for r in rows if r[3] & 2] == [0x201, 0x202, 0x203])
check("F181 has no storage pointer", rows[0][0] == 0)
check("0203 has no storage pointer", rows[3][0] == 0)
check("0201/0202 use direct-copy mode", rows[1][4] == rows[2][4] == 1)
check("common ID/VIN DIDs are absent",
      not ({0xF180,0xF182,0xF187,0xF188,0xF189,0xF18C,0xF190} & {r[2] for r in rows}))

print("\n== handler bounds and access policy ==")
check("read handler loop bound is exactly four descriptors",
      CF[0x6048:0x604E] == bytes.fromhex("41326432f6d5"), CF[0x6048:0x604E].hex())
check("write handler loop bound is exactly four descriptors",
      CF[0x499C:0x49A2] == bytes.fromhex("410a640ae6ed"), CF[0x499C:0x49A2].hex())
check("read handler tests access bit 0 at descriptor+8",
      CF[0x600A:0x600E] == bytes.fromhex("dec70800"))
check("write handler tests access bit 1 at descriptor+8",
      CF[0x498C:0x4990] == bytes.fromhex("decf0800"))
check("read DID permitted-session list is 1/2/3", CF[0x8F00:0x8F03] == b"\x01\x02\x03")
check("write DID permitted session is programming (2)", CF[0x8EF8] == 2, hex(CF[0x8EF8]))
check("write handler requires security state 2",
      CF[0x49C6:0x49CC] == bytes.fromhex("a40f0f93620a"))
check("write handler's locked NRC is 0x33",
      CF[0x49CE:0x49D2] == bytes.fromhex("20363300"))
check("descriptor write length is data length + 3",
      CF[0x49B8:0x49C0] == bytes.fromhex("439ad300f3e9c205"))

print("\n== exact F181 synthesis ==")
check("F181 descriptor prefix is literal 0x02", rows[0][5] == 2)
check("read generator loads literal 0x21",
      CF[0x5F4C:0x5F50] == bytes.fromhex("209e2100"))
check("positive ReadDID responder loads SID 0x62",
      CF[0x5F80:0x5F84] == bytes.fromhex("200e6200"))
expected_response = bytes.fromhex("62f18102") + b"\x21" * 32
check("modeled F181 response is 36 bytes", len(expected_response) == 36)
check("modeled F181 data is 02 + 32 exclamation bytes",
      expected_response[3:] == b"\x02" + b"\x21" * 32)
check("F181 cannot point at BOOT INFO AREA", rows[0][0] == 0 and CF[0x180:0x18E] == b"BOOT INFO AREA")

print("\n== 0203 -> 0201 -> 0202 sequence ==")
check("DID state reset clears sequence and pending bytes",
      CF[0x4A90:0x4A9A] == bytes.fromhex("24f6b092820381037f00"))
check("0203 compares required state against zero",
      CF[0x49E4:0x49EC] == bytes.fromhex("840fb392e009ea0d"))
check("0201 compares required state against one",
      CF[0x49F6:0x49FE] == bytes.fromhex("840fb392610ac505"))
check("0202 compares required state against two",
      CF[0x49FE:0x4A06] == bytes.fromhex("840fb392620ac2f5"))
arm = CF[0x4A1A:0x4A2A]
check("0203 synchronously responds then sets sequence state 1",
      arm == bytes.fromhex("bffffafe010a24f6b092820b8103a535"), arm.hex())
check("0203 branch never passes stack+4 payload to dispatcher",
      bytes.fromhex("233e0400") not in CF[0x4A12:0x4A2A])
check("handler contains exactly two stack+4 dispatcher payload paths",
      CF[0x4948:0x4A8C].count(bytes.fromhex("233e0400")) == 2)
check("0201 success sets sequence state 2",
      CF[0x4A44:0x4A4C] == bytes.fromhex("020a24f6b092820b"))
check("0202 success sets crypto-ready and sequence state 0",
      CF[0x4A70:0x4A7C] == bytes.fromhex("010a24f6b092440f16938203"))
check("0201/0202 success sets asynchronous pending flag 1",
      CF[0x4A7C:0x4A80] == bytes.fromhex("810bf505"))
check("out-of-order path uses NRC 0x22",
      CF[0x4A06:0x4A0A] == bytes.fromhex("20362200"))

print("\n== volatile RAM consumers ==")
check("0201 destination is FEBF2D08", rows[1][0] == 0xFEBF2D08)
check("payload key derivation references gp-0x6AF8/FEBF2D08",
      CF[0x7080:0x7084] == bytes.fromhex("24360895"))
check("0202 destination is FEBF2CF8", rows[2][0] == 0xFEBF2CF8)
check("CBC initialization references gp-0x6B08/FEBF2CF8",
      CF[0x70B0:0x70B4] == bytes.fromhex("2446f894"))
check("CMAC setup references gp-0x6B08/FEBF2CF8",
      CF[0x713C:0x7140] == bytes.fromhex("2436f894"))
check("diagnostic init clears crypto-ready gp-0x6CEA",
      CF[0x50AE:0x50B2] == bytes.fromhex("44071693"))
ready_load = bytes.fromhex("840f1793")
check("RequestDownload checks crypto-ready three times",
      CF[0x5D68:0x5F38].count(ready_load) == 3,
      str(CF[0x5D68:0x5F38].count(ready_load)))
check("no DID destination points into DataFlash",
      all(not (0xFF200000 <= r[0] <= 0xFF207FFF) for r in rows))

print("\n== public tooling correlation ==")
source = (REPOS / "secoc" / "extract_keys.py").read_text(encoding="utf-8")
p203 = source.find("write_data_by_identifier(0x203")
p201 = source.find("write_data_by_identifier(0x201")
p202 = source.find("write_data_by_identifier(0x202")
check("Willem tooling writes 0203 -> 0201 -> 0202", -1 < p203 < p201 < p202)
check("Willem tooling uses exactly five bytes for 0203", '0x203, b"\\x00" * 5' in source)
check("Willem's unresolved state-machine comment is present", "not sure why but needed for state machine" in source)
uds_source = (REPOS / "calvinpark-openpilot" / "opendbc_repo" / "opendbc" / "car" / "uds.py").read_text(encoding="utf-8")
check("local UDS enum identifies F181 as application software ID",
      "APPLICATION_SOFTWARE_IDENTIFICATION = 0xF181" in uds_source)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
