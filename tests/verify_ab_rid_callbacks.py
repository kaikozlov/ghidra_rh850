#!/usr/bin/env python3
"""Verify the 0xAB RID callback + state-machine analysis from firmware bytes.

Decodes every jarl/jr instruction (op0610=0x1E) in three code ranges using
the SLEIGH-verified addr22 encoding (s0005<<16 | word1, + inst_start) with
the op1616=0 constraint (word1 must be even). Asserts:
1. No call/jump targets match sensitive crypto/NvM/SecOC/security functions
2. All targets match the firmware-derived expected set
3. No GP-relative SecOC key references appear in the ranges
4. The RID table at 0x25768 matches the documented entries
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


def decode_branch(addr):
    """Decode RH850 jarl/jr (op0610=0x1E, op1616=0).

    Returns (kind, target, reg2) where kind is 'jarl' (reg2!=0) or 'jr' (reg2==0).
    Returns None if the instruction is not a valid jarl/jr encoding.
    """
    if addr + 4 > len(CF):
        return None
    w0 = struct.unpack_from("<H", CF, addr)[0]
    if (w0 >> 6) & 0x1F != 0x1E:
        return None
    w1 = struct.unpack_from("<H", CF, addr + 2)[0]
    if w1 & 1:  # SLEIGH constraint: op1616=0
        return None
    reg2 = (w0 >> 11) & 0x1F
    s0005 = w0 & 0x3F
    if s0005 & 0x20:
        s0005 -= 0x40
    target = ((s0005 << 16) | w1) + addr
    kind = "jarl" if reg2 != 0 else "jr"
    return (kind, target, reg2)


# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════
SENSITIVE_TARGETS = {
    0x865D4,  # AES key expansion
    0x853EE,  # AES decrypt block
    0x852B0,  # AES encrypt wrapper
    0x8496C,  # AES encrypt rounds
    0x72F58,  # NvM ReadBlock
    0x72F84,  # NvM WriteBlock
    0x84850,  # ICU-S init
    0x84874,  # ICU-S process
    0x8488C,  # ICU-S finalize
    0x880DC,  # ICU verify adapter
    # Complete SecOC/CMAC verification chain (CSM/CryptoIf + ICU-S)
    0x88B6A,  # CSM job start / CMAC verify init
    0x88B9C,  # CSM process / CMAC update
    0x88BA8,  # CSM finish / CMAC finalize
    0x88556,  # CryptoIf job dispatch
    0x88080,  # ICU-S CMAC operation
    0x897F4,  # SecOC freshness / verify helper
    0x8C7BC,  # SA crypto stage 1
    0x8C7F6,  # SA crypto stage 2
    0x8FDCA,  # security-state reader
    0x8F242,  # security level checker
    0x92FEE,  # per-DID policy check
    0x900FC,  # unlock helper
}

# Three code ranges scanned for direct branch targets
SCAN_RANGES = [
    ("RID_callbacks", 0x4EC16, 0x4F000),
    ("state_machine_0x8CF84", 0x8CF84, 0x8D400),
    ("FUN_0x4F8BA", 0x4F8BA, 0x4FC00),
]

# Firmware-derived branch targets (39 unique valid addresses across all 3 ranges)
FIRMWARE_TARGETS = {
    0x4C4A4, 0x4C8A8, 0x4C8E8, 0x4EC5A, 0x4EC68,
    0x4F8BA, 0x4F9EA, 0x4FA32, 0x54748, 0x548B0,
    0x54BF2, 0x55F9C, 0x690DE, 0x8A01C, 0x8A020,
    0x8A6AA, 0x8CDCE, 0x8CDF2, 0x8CF06, 0x8D0F0,
    0x8D11E, 0x8D1EE, 0x8D2B2, 0x8D32E, 0x8D512,
    0x8D534, 0x8D5CA, 0x8D5E2, 0x96D98, 0x96DA6,
    0xFDE58, 0xFDED0, 0xFE04C, 0xFE060, 0xFE09C,
    0xFE0C4, 0xFE1B4, 0xFE1C8, 0xFE2A4,
}

# ═══════════════════════════════════════════════════════════════════
# 1. RID table at 0x25768
# ═══════════════════════════════════════════════════════════════════
print("== RID callback table at 0x25768 ==")

RID_CSV = REPO / "data" / "application_ab_rid_callbacks.csv"
check("RID callback CSV exists", RID_CSV.exists())
with open(RID_CSV) as f:
    rid_rows = list(csv.DictReader(f))
check("CSV has 13 RID entries", len(rid_rows) == 13, str(len(rid_rows)))

for i, row in enumerate(rid_rows):
    rid = int(row["rid"], 16)
    start_cb = int(row["start_cb"], 16)
    result_cb = int(row["result_cb"], 16)
    addr = 0x25768 + i * 0xC
    rid_actual = struct.unpack_from("<H", CF, addr)[0]
    start_actual = struct.unpack_from("<I", CF, addr + 4)[0]
    result_actual = struct.unpack_from("<I", CF, addr + 8)[0]
    check(f"RID table[{i}] RID=0x{rid:04X} start=0x{start_cb:X} result=0x{result_cb:X}",
          rid_actual == rid and start_actual == start_cb and result_actual == result_cb,
          f"got RID=0x{rid_actual:04X} start=0x{start_actual:X} result=0x{result_actual:X}")

# ═══════════════════════════════════════════════════════════════════
# 2. Firmware-derived branch scan across all 3 ranges
# ═══════════════════════════════════════════════════════════════════
print("\n== firmware-derived branch scan (jarl + jr) ==")

firmware_targets = set()
sensitive_hits = []
for name, start, end in SCAN_RANGES:
    for addr in range(start, end, 2):
        result = decode_branch(addr)
        if result is None:
            continue
        kind, target, reg2 = result
        if 0 < target < 0x100000:
            firmware_targets.add(target)
            if target in SENSITIVE_TARGETS:
                sensitive_hits.append((addr, kind, target))

check("no sensitive branch targets in scanned ranges (jarl + jr)",
      len(sensitive_hits) == 0,
      f"{len(sensitive_hits)} found: {[(hex(a), k, hex(t)) for a, k, t in sensitive_hits]}")

check("firmware-derived target set matches expected (39 targets)",
      firmware_targets == FIRMWARE_TARGETS,
      f"missing={FIRMWARE_TARGETS - firmware_targets}; "
      f"extra={firmware_targets - FIRMWARE_TARGETS}")

# ═══════════════════════════════════════════════════════════════════
# 3. GP-relative and literal SecOC key references
# ═══════════════════════════════════════════════════════════════════
print("\n== SecOC key references in scanned ranges ==")

for name, start, end in SCAN_RANGES:
    # GP-relative displacements (APP_GP = 0xFEBEB800)
    for disp, label in [(0x5AE8, "FEBF02E8"), (0x5AF8, "FEBF02F8")]:
        target_bytes = struct.pack("<h", disp)
        found = CF.find(target_bytes, start, end)
        check(f"{name}: no GP-disp 0x{disp:04X} ({label})",
              found < 0, f"at 0x{found:05X}")

    # Literal 32-bit addresses
    for addr_val in [0xFEBF02E8, 0xFF206E14]:
        target_bytes = struct.pack("<I", addr_val)
        found = CF.find(target_bytes, start, end)
        check(f"{name}: no literal 0x{addr_val:08X}",
              found < 0, f"at 0x{found:05X}")

# ═══════════════════════════════════════════════════════════════════
# 4. Callback liveness
# ═══════════════════════════════════════════════════════════════════
print("\n== callback liveness ==")
for row in rid_rows:
    rid = int(row["rid"], 16)
    for field in ("start_cb", "result_cb"):
        cb = int(row[field], 16)
        check(f"RID 0x{rid:04X} {field} 0x{cb:X} is live",
              CF[cb:cb + 2] != b"\x00\x00")

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    sys.exit(1)
