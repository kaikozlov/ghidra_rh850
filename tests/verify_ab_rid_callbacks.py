#!/usr/bin/env python3
"""Verify the 0xAB RID callback analysis from firmware bytes.

Decodes every jarl instruction in the 13 RID callback range (0x4EC16..0x4F000)
using the RH850 addr22 encoding (s0005<<16 | word1, + inst_start) and asserts:
1. No call targets match sensitive crypto/NvM/SecOC/security functions
2. All call targets match the firmware-derived expected set
3. No GP-relative SecOC key references appear in the byte range
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


def decode_jarl(addr):
    """Decode RH850 jarl (op0610=0x1E). Returns (target, reg2) or None."""
    if addr + 4 > len(CF):
        return None
    w0 = struct.unpack_from("<H", CF, addr)[0]
    opcode = (w0 >> 6) & 0x1F
    if opcode != 0x1E:
        return None
    w1 = struct.unpack_from("<H", CF, addr + 2)[0]
    reg2 = (w0 >> 11) & 0x1F
    s0005 = w0 & 0x3F
    if s0005 & 0x20:
        s0005 -= 0x40
    # addr22 = (s0005 << 16 | word1) + inst_start  [per SLEIGH]
    target = ((s0005 << 16) | w1) + addr
    return (target, reg2)


# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════
CB_START = 0x4EC16   # first RID start callback
CB_END = 0x4F000     # past last RID result callback + padding

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
    0x8C7BC,  # SA crypto stage 1
    0x8C7F6,  # SA crypto stage 2
    0x8FDCA,  # security-state reader
    0x8F242,  # security level checker
    0x92FEE,  # per-DID policy check
    0x900FC,  # unlock helper
}

# Expected jarl call targets derived from firmware bytes
# (30 unique valid targets in the callback range)
FIRMWARE_TARGETS = {
    0x4C4A4, 0x4EC5A, 0x4EC68, 0x4EC7B, 0x4EC89,
    0x4ED59, 0x4EDA1, 0x4EDB1, 0x4EDEB, 0x4EE35,
    0x4EE7F, 0x4EEC9, 0x4EF1B, 0x4EF25, 0x4EF6F,
    0x4EFB1, 0x4EFF5, 0x8A6AA, 0x9B7E7, 0x9B82B,
    0x9B951, 0xFDE58, 0xFDED0, 0xFE04C, 0xFE060,
    0xFE09C, 0xFE0C4, 0xFE1B4, 0xFE1C8, 0xFE2A4,
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
# 2. Firmware-derived jarl scan: no sensitive call targets
# ═══════════════════════════════════════════════════════════════════
print("\n== firmware-derived jarl scan ==")

firmware_targets = set()
sensitive_hits = []
for addr in range(CB_START, CB_END, 2):
    result = decode_jarl(addr)
    if result is None:
        continue
    target, reg2 = result
    if target > 0 and target < 0x100000:
        firmware_targets.add(target)
        if target in SENSITIVE_TARGETS:
            sensitive_hits.append((addr, target))

check("no sensitive call targets in RID callback range",
      len(sensitive_hits) == 0,
      f"{len(sensitive_hits)} found: {[(hex(a), hex(t)) for a, t in sensitive_hits]}")

# Assert the exact target set matches (catches new calls if firmware changes)
check("firmware-derived target set matches expected",
      firmware_targets == FIRMWARE_TARGETS,
      f"missing={FIRMWARE_TARGETS - firmware_targets}; "
      f"extra={firmware_targets - FIRMWARE_TARGETS}")

# ═══════════════════════════════════════════════════════════════════
# 3. GP-relative SecOC key references
# ═══════════════════════════════════════════════════════════════════
print("\n== GP-relative and literal SecOC references ==")

# APP_GP = 0xFEBEB800
# FEBF02E8 - GP = 0x5AE8  (SecOC key RAM)
# FEBF02F8 - GP = 0x5AF8  (SecOC key field)
for disp, label in [(0x5AE8, "FEBF02E8"), (0x5AF8, "FEBF02F8")]:
    target_bytes = struct.pack("<h", disp)
    found = CF.find(target_bytes, CB_START, CB_END)
    check(f"no GP-displacement 0x{disp:04X} ({label}) in callback range",
          found < 0, f"found at 0x{found:05X}")

# Also check literal 32-bit addresses
for addr_val in [0xFEBF02E8, 0xFF206E14]:
    target_bytes = struct.pack("<I", addr_val)
    found = CF.find(target_bytes, CB_START, CB_END)
    check(f"no literal 0x{addr_val:08X} in callback range",
          found < 0, f"found at 0x{found:05X}")

# ═══════════════════════════════════════════════════════════════════
# 4. Callback addresses are live code
# ═══════════════════════════════════════════════════════════════════
print("\n== callback liveness ==")
for row in rid_rows:
    rid = int(row["rid"], 16)
    start_cb = int(row["start_cb"], 16)
    result_cb = int(row["result_cb"], 16)
    check(f"RID 0x{rid:04X} start 0x{start_cb:X} is live",
          CF[start_cb:start_cb + 2] != b"\x00\x00")
    check(f"RID 0x{rid:04X} result 0x{result_cb:X} is live",
          CF[result_cb:result_cb + 2] != b"\x00\x00")

# ═══════════════════════════════════════════════════════════════════
# 5. State machine liveness
# ═══════════════════════════════════════════════════════════════════
print("\n== 0xAB state machine ==")
check("state machine 0x8CF84 is live code",
      CF[0x8CF84:0x8CF86] != b"\x00\x00")

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    sys.exit(1)
