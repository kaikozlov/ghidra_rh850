#!/usr/bin/env python3
"""Verify the application control-ID callback table from firmware bytes.

These callbacks are separate from SID 0xAB and are not attached to SID 0x31.
They are structurally present under the SID 0x28 generic-control machinery, but
their selector ranges start with subfunctions 0x02/0x20 while the stock SID
0x28 gate admits only 0x00/0x01/0x03. The callbacks are therefore stock-wire
gated in this calibration. If invoked internally, several result callbacks arm
asynchronous namespace-0x100 NvM updates.

Decode every jarl/jr instruction (op0610=0x1E) in the callback code range using
the SLEIGH-verified addr22 encoding (s0005<<16 | word1, + inst_start) with
the op1616=0 constraint (word1 must be even). Asserts:
1. The application SID 0x31 record has no service callback
2. SID 0x28's allowed subfunctions exclude both callback-bearing selector ranges
3. No *direct* callback target matches crypto/NvM/SecOC/security functions
4. The state-mediated object-0x101/0x102/0x103 update paths remain present
5. No GP-relative SecOC key references appear in the callback range
6. The RID table at 0x25768 matches the documented entries
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

# Routine callback code range scanned for direct branch targets.
SCAN_RANGES = [
    ("RID_callbacks", 0x4EC16, 0x4F000),
]

# Firmware-derived direct branch targets in the 13 callback pairs.
FIRMWARE_TARGETS = {
    0x4C4A4, 0x4EC5A, 0x4EC68, 0x8A6AA,
    0xFDE58, 0xFDED0, 0xFE04C, 0xFE060, 0xFE09C,
    0xFE0C4, 0xFE1B4, 0xFE1C8, 0xFE2A4,
}


def branch_targets(start, end):
    """Return direct RH850 jarl/jr targets in a bounded code interval."""
    targets = set()
    for addr in range(start, end, 2):
        result = decode_branch(addr)
        if result is not None:
            targets.add(result[1])
    return targets


def veneer_target(addr):
    """Decode the generated ``mov imm32,r12; jmp r12`` veneer form."""
    if CF[addr:addr + 2] != b"\x2c\x06" or CF[addr + 6:addr + 8] != b"\x6c\x00":
        return None
    return struct.unpack_from("<I", CF, addr + 2)[0]

# ═══════════════════════════════════════════════════════════════════
# 1. RID table at 0x25768
# ═══════════════════════════════════════════════════════════════════
print("== RID callback table at 0x25768 ==")

SID_31_RECORD = 0x25F08
check("SID 0x31 application callback is null",
      struct.unpack_from("<I", CF, SID_31_RECORD + 0x10)[0] == 0)

RID_CSV = REPO / "data" / "application_routine_id_callbacks.csv"
check("RID callback CSV exists", RID_CSV.exists())
with open(RID_CSV) as f:
    rid_rows = list(csv.DictReader(f))
check("CSV has 13 RID entries", len(rid_rows) == 13, str(len(rid_rows)))

EXPECTED_SIZES = {
    0x0204: (20, 28),
    0x2001: (20, 68),
    0x2002: (20, 76),
    0x2005: (20, 54),
    0x2006: (20, 54),
    0x2007: (20, 54),
    0x2008: (20, 54),
    0x2009: (20, 54),
    0x200D: (20, 54),
    0x2010: (20, 70),
    0x2012: (4, 26),
    0x2013: (40, 28),
    0x2014: (40, 42),
}

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
    csv_sizes = (int(row["start_size_bytes"]), int(row["result_size_bytes"]))
    check(f"RID 0x{rid:04X} callback sizes match recovered bodies",
          csv_sizes == EXPECTED_SIZES[rid], repr(csv_sizes))
    csv_targets = (set() if row["call_targets"] == "none" else
                   {int(value, 16) for value in row["call_targets"].split(";")})
    actual_targets = (
        branch_targets(start_cb, start_cb + csv_sizes[0]) |
        branch_targets(result_cb, result_cb + csv_sizes[1])
    )
    check(f"RID 0x{rid:04X} direct-target census matches callback bodies",
          csv_targets == actual_targets,
          f"csv={sorted(map(hex, csv_targets))}; actual={sorted(map(hex, actual_targets))}")

# The worker wrappers are the fourth callbacks in generic-control records for
# 0x0201..0x02FF and 0x2001..0x20FF. The configured SID 0x28 subfunction gate
# admits only 0x00/0x01/0x03, so neither high byte can reach this machinery from
# the stock wire dispatcher.
CONTROL_RECORD = struct.Struct("<IIIIIHHB3x")
control_rows = [CONTROL_RECORD.unpack_from(CF, 0x26210 + i * CONTROL_RECORD.size)
                for i in range(5)]
check("generic-control record size is 0x1C", CONTROL_RECORD.size == 0x1C)
check("range 0x0201..0x02FF uses worker wrapper 0x936AA",
      control_rows[1][5:8] == (0x0201, 0x02FF, 1) and control_rows[1][3] == 0x936AA)
check("range 0x2001..0x20FF uses worker wrapper 0x936D6",
      control_rows[3][5:8] == (0x2001, 0x20FF, 1) and control_rows[3][3] == 0x936D6)

SUBFN = struct.Struct("<IIIHH")
sid28_subfunctions = {
    SUBFN.unpack_from(CF, 0x25C70 + i * SUBFN.size)[3] for i in range(3)
}
worker_selector_high_bytes = {control_rows[i][5] >> 8 for i in (1, 3)}
check("SID 0x28 stock subfunctions are 00/01/03",
      sid28_subfunctions == {0x00, 0x01, 0x03}, repr(sid28_subfunctions))
check("stock SID 0x28 gate excludes worker selector high bytes 02/20",
      sid28_subfunctions.isdisjoint(worker_selector_high_bytes),
      f"allowed={sid28_subfunctions}; worker={worker_selector_high_bytes}")
wrapper_0201_call = decode_branch(0x936BE)
wrapper_2001_call = decode_branch(0x936EA)
check("both generic-control wrappers call worker 0x8A630",
      wrapper_0201_call is not None and wrapper_0201_call[1] == 0x8A630 and
      wrapper_2001_call is not None and wrapper_2001_call[1] == 0x8A630)
check("worker reaches start and result dispatchers",
      0x8A482 in branch_targets(0x8A630, 0x8A68A) and
      0x8A542 in branch_targets(0x8A630, 0x8A68A))
check("dispatchers reach both 13-entry callback lookups",
      0x8D3CC in branch_targets(0x8A482, 0x8A542) and
      0x8D416 in branch_targets(0x8A542, 0x8A630))

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

check("no direct sensitive branch targets in callback range (jarl + jr)",
      len(sensitive_hits) == 0,
      f"{len(sensitive_hits)} found: {[(hex(a), k, hex(t)) for a, k, t in sensitive_hits]}")

check("firmware-derived target set matches expected (13 targets)",
      firmware_targets == FIRMWARE_TARGETS,
      f"missing={FIRMWARE_TARGETS - firmware_targets}; "
      f"extra={firmware_targets - FIRMWARE_TARGETS}")

# Direct callback closure is not the whole story. Successful result callbacks
# arm three byte-state machines whose consumers submit namespace-0x100 objects
# 0x101, 0x102, and 0x103 through wrapper 0xFF09C -> dispatcher 0x65CD8.
print("\n== state-mediated namespace-0x100 persistence paths ==")
result_helper_by_rid = {
    0x2001: 0xFE060,
    0x2002: 0xFDE58,
    0x2005: 0xFE0C4,
    0x2006: 0xFE0C4,
    0x2007: 0xFE0C4,
    0x2008: 0xFE0C4,
    0x2009: 0xFE0C4,
    0x200D: 0xFE0C4,
}
for row in rid_rows:
    rid = int(row["rid"], 16)
    if rid not in result_helper_by_rid:
        continue
    result_cb = int(row["result_cb"], 16)
    helper = result_helper_by_rid[rid]
    check(f"RID 0x{rid:04X} result reaches state-arm helper 0x{helper:X}",
          helper in branch_targets(result_cb, result_cb + int(row["result_size_bytes"])))

check("veneer 0xFE060 reaches object-0x101 state producer 0xB47A6",
      veneer_target(0xFE060) == 0xB47A6)
check("veneer 0xFDE58 reaches object-0x102 state producer 0xB5D0C",
      veneer_target(0xFDE58) == 0xB5D0C)
check("veneer 0xFE0C4 reaches object-0x103 state producer 0xB55C4",
      veneer_target(0xFE0C4) == 0xB55C4)

persistence_paths = [
    (0x101, 0xB44CA, 0xB45A2, 0xB4484, 0xB44CA),
    (0x102, 0xB5C3E, 0xB5CD0, 0xB5C16, 0xB5C3E),
    (0x103, 0xB535E, 0xB53E8, 0xB52DA, 0xB535E),
]
for object_id, consumer_start, consumer_end, update_start, update_end in persistence_paths:
    check(f"object 0x{object_id:03X} state consumer reaches update helper 0x{update_start:X}",
          update_start in branch_targets(consumer_start, consumer_end))
    check(f"object 0x{object_id:03X} update helper embeds selector and calls 0xFF09C",
          b"\x20\x36" + struct.pack("<H", object_id) in CF[update_start:update_end] and
          0xFF09C in branch_targets(update_start, update_end))

check("thin update wrapper 0xFF09C reaches dispatcher 0x65CD8",
      0x65CD8 in branch_targets(0xFF09C, 0xFF0B0))

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
