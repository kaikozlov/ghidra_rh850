#!/usr/bin/env python3
"""Verify the application security-state consumer mapping.

Key finding: the application level-2 SecurityAccess unlock gates NOTHING
in this calibration. All 17 services have sec_count=0 in the service
table, and no readable DIDs require security level > 0.
"""
from pathlib import Path
import csv
import struct
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

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


print("== application security-state consumers ==")

# -- CSV schema --
CSV_PATH = REPO / "data" / "application_security_consumers.csv"
check("consumer CSV exists", CSV_PATH.exists())
with open(CSV_PATH) as f:
    rows = list(csv.DictReader(f))
expected_cols = {"consumer_addr", "consumer_name", "check_type", "required_level",
                 "gated_service", "gated_did_or_rid", "operation", "relevance"}
check("CSV header schema", set(rows[0].keys()) == expected_cols,
      repr(sorted(rows[0].keys())))
check("CSV has at least 10 consumers", len(rows) >= 10, str(len(rows)))

# -- Consumer address liveness --
for row in rows:
    addr = int(row["consumer_addr"], 16)
    check(f"consumer 0x{addr:05X} starts at non-zero code",
          CF[addr:addr + 2] != b"\x00\x00")

# -- Service table: all SIDs have sec_count=0 --
print("\n== service-level security (all should be count=0) ==")
for i in range(17):
    entry_addr = 0x25E28 + i * 0x18
    sec_count = CF[entry_addr + 0x12]
    sid_byte = CF[entry_addr + 0x10]
    check(f"SID 0x{sid_byte:02X} has no service-level security (sec_count=0)",
          sec_count == 0, f"sec_count={sec_count}")

# -- RDBI per-DID security: no DIDs require level > 0 --
print("\n== per-DID RDBI security (none should require level > 0) ==")
ptr_to_table = struct.unpack_from("<I", CF, 0x26208)[0]
dids_with_security = 0
for did_idx in range(242):
    entry_offset = ptr_to_table + did_idx * 0xC
    if entry_offset + 4 > len(CF):
        break
    session_block_ptr = struct.unpack_from("<I", CF, entry_offset)[0]
    if session_block_ptr == 0 or session_block_ptr >= len(CF):
        continue
    for sess in range(3):
        sess_offset = session_block_ptr + sess * 0x10
        if sess_offset + 0x10 > len(CF):
            break
        sec_list_ptr = struct.unpack_from("<I", CF, sess_offset)[0]
        sec_count = CF[sess_offset + 0xC]
        if sec_count == 0 or sec_list_ptr < 0x1000 or sec_list_ptr >= len(CF):
            continue  # skip null or invalid list pointers
        if sec_count > 8:
            continue  # garbage / misaligned
        levels = list(CF[sec_list_ptr:sec_list_ptr + sec_count])
        if any(l > 0 for l in levels):
            dids_with_security += 1
check("no readable DIDs require security level > 0",
      dids_with_security == 0, f"{dids_with_security} DIDs with security")

# -- Bitmask machinery addresses are non-erased code --
check("security reader 0x8FDCA is live code",
      CF[0x8FDCA:0x8FDCC] != b"\x00\x00")
check("bitmask setter 0x9075A is live code",
      CF[0x9075A:0x9075C] != b"\x00\x00")
check("unlock helper 0x900FC starts with prepare",
      CF[0x900FC:0x90100] == bytes.fromhex("80072100"))
check("per-DID checker 0x92FEE is live code",
      CF[0x92FEE:0x92FF0] != b"\x00\x00")

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    sys.exit(1)
