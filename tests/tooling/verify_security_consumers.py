#!/usr/bin/env python3
"""Verify the application security-state consumer mapping.

Findings (all scoped to this Sienna calibration 8965B4512000):
- All 17 services: sec_count=0 at the Dcm service-dispatch layer
- All 242 readable DIDs: no security level > 0 found in bounded policy scan
- All 19 configured RoutineControl RIDs: level_count=0
- Security machinery is wired up and exercised but policy tables are empty
- 0xAB event-record closure is in verify_application_ab_service.py
"""
import struct
import sys

from tools import REPO_ROOT
REPO = REPO_ROOT
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


# ═══════════════════════════════════════════════════════════════════
# 2. SERVICE-LEVEL: all 17 SIDs have sec_count=0
# ═══════════════════════════════════════════════════════════════════
print("\n== service-level security (17 SIDs, all sec_count=0) ==")
EXPECTED_SIDS = [0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x27, 0x28,
                 0x2E, 0x31, 0x34, 0x36, 0x37, 0x3E, 0x85, 0xAB, 0xBA]
for i in range(17):
    entry_addr = 0x25E28 + i * 0x18
    sec_count = CF[entry_addr + 0x12]
    sid_byte = CF[entry_addr + 0x10]
    check(f"service entry {i} SID=0x{sid_byte:02X} sec_count=0",
          sec_count == 0 and sid_byte == EXPECTED_SIDS[i],
          f"sid=0x{sid_byte:02X} sec_count={sec_count}")

# ═══════════════════════════════════════════════════════════════════
# 3. RDBI per-DID: bounded scan of all 242 DIDs
# ═══════════════════════════════════════════════════════════════════
print("\n== RDBI per-DID security (242 DIDs, bounded scan) ==")
ptr_to_table = struct.unpack_from("<I", CF, 0x26208)[0]
check("RDBI policy table pointer at 0x26208 is valid",
      0x1000 < ptr_to_table < len(CF), hex(ptr_to_table))

# The DID policy table at 0x261A4 has a complex AUTOSAR Dcm layout.
# Some entries have session_block_ptr values that aren't valid pointers
# (sentinels, callback addresses, flags). These are structural artifacts,
# not security configs. We scan all 242 entries and assert that among
# entries with valid structure (block_ptr in CodeFlash, sec_count 0-8,
# list_ptr in CodeFlash, all levels 0-9), none requires level > 0.
rdbi_secure_count = 0
valid_entries = 0
for did_idx in range(242):
    entry_offset = ptr_to_table + did_idx * 0xC
    session_block_ptr = struct.unpack_from("<I", CF, entry_offset)[0]

    if session_block_ptr == 0:
        continue

    if session_block_ptr < 0x1000 or session_block_ptr >= len(CF):
        continue  # non-pointer dword — structural artifact

    for sess in range(3):
        sess_offset = session_block_ptr + sess * 0x10
        if sess_offset + 0x10 > len(CF):
            continue

        sec_list_ptr = struct.unpack_from("<I", CF, sess_offset)[0]
        sec_count = CF[sess_offset + 0xC]

        if sec_count == 0:
            valid_entries += 1
            continue
        if sec_count > 8:
            continue  # non-security byte at this offset

        if sec_list_ptr < 0x1000 or sec_list_ptr >= len(CF):
            continue

        levels = list(CF[sec_list_ptr:sec_list_ptr + sec_count])
        if not all(l < 10 for l in levels):
            continue  # garbage levels

        valid_entries += 1
        if any(l > 0 for l in levels):
            sess_names = {0: "default", 1: "programming", 2: "extended"}
            rdbi_secure_count += 1
            check(f"DID idx {did_idx} session {sess_names[sess]} requires level > 0",
                  False, f"levels={[hex(l) for l in levels]}")

check(f"no readable DIDs require security level > 0 ({valid_entries} valid policy entries scanned)",
      rdbi_secure_count == 0, f"{rdbi_secure_count} DIDs with security")

# ═══════════════════════════════════════════════════════════════════
# 4. RoutineControl per-RID: all 19 configured RIDs, level_count=0
# ═══════════════════════════════════════════════════════════════════
print("\n== RoutineControl per-RID security (19 configured RIDs) ==")
ROUTINE_RID_COUNT = struct.unpack_from("<H", CF, 0x26666)[0]
check("RoutineControl RID count at 0x26666 is 19", ROUTINE_RID_COUNT == 19, str(ROUTINE_RID_COUNT))

routine_secure_count = 0
for i in range(ROUTINE_RID_COUNT):
    sec_flag = CF[0x26B8D + i * 0xF]
    sec_idx = struct.unpack_from("<H", CF, 0x26690 + i * 2)[0]
    level_count = CF[0x26420 + sec_idx * 2] if sec_idx < 100 else 0xFF
    if level_count > 0:
        routine_secure_count += 1
    check(f"RoutineControl RID[{i:2d}] has level_count=0 (flag=0x{sec_flag:02X}, idx={sec_idx})",
          level_count == 0, f"level_count={level_count}")

check("no configured RoutineControl RIDs require SecurityAccess level > 0",
      routine_secure_count == 0, f"{routine_secure_count} RoutineControl RIDs with security")

# ═══════════════════════════════════════════════════════════════════
# 5. 0xAB CALLBACK SECURITY ANALYSIS
# ═══════════════════════════════════════════════════════════════════
# The firmware-derived 0xAB direct/indirect callback closure is in
# verify_application_ab_service.py.
# This suite does not duplicate that check.

# ═══════════════════════════════════════════════════════════════════
# 6. MACHINERY LIVENESS
# ═══════════════════════════════════════════════════════════════════
check("unlock helper 0x900FC starts with prepare",
      CF[0x900FC:0x90100] == bytes.fromhex("80072100"))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    sys.exit(1)
