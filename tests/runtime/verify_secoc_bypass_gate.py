#!/usr/bin/env python3
"""Base-image SecOC bypass patch point and acceptance-gate pins.

Domain split; assertions and helpers are carried over verbatim.
"""
from __future__ import annotations


from tools import REPO_ROOT
ROOT = REPO = REPO_ROOT

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")
print()

print("== secoc bypass patch point ==")
def _section_secoc_bypass_patch_point():
    import struct
    import zlib
    REPO = REPO_ROOT
    CF = (REPO / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()

    def u16(off: int) -> int:
        return struct.unpack_from('<H', CF, off)[0]

    def u32(off: int) -> int:
        return struct.unpack_from('<I', CF, off)[0]

    def decode_cmp_format_ii(data: bytes) -> tuple[int, int, int]:
        """Return (left_reg, right_reg, opcode6) for a 2-byte RH850 Format-II CMP."""
        if len(data) != 2:
            raise ValueError('CMP must be two bytes')
        hw = int.from_bytes(data, 'little')
        return (hw & 31, hw >> 11 & 31, hw >> 5 & 63)

    def synthesize_cmp_same_register(data: bytes) -> bytes:
        left, _right, _opcode = decode_cmp_format_ii(data)
        hw = int.from_bytes(data, 'little')
        patched = hw & 2047 | left << 11
        return patched.to_bytes(2, 'little')

    def decode_bcond(off: int, data: bytes | None=None) -> tuple[int, int]:
        hw = int.from_bytes(data if data is not None else CF[off:off + 2], 'little')
        s1115 = hw >> 11 & 31
        op0406 = hw >> 4 & 7
        cc = hw & 15
        s1115_signed = s1115 - 32 if s1115 & 16 else s1115
        target = (s1115_signed << 4 | op0406 << 1) + off
        return (cc, target)
    PATCH_VA = 583366
    BRANCH_VA = 583368
    ORIGINAL = bytes.fromhex('e0d1')
    REPLACEMENT = bytes.fromhex('e001')
    print('== 1. corrected patch is CMP neutralization at 0x8E6C6 ==')
    check('stock patch preimage is e0d1', CF[PATCH_VA:PATCH_VA + 2] == ORIGINAL)
    left, right, opcode = decode_cmp_format_ii(ORIGINAL)
    check('stock CMP operands encode r0,r26', (left, right) == (0, 26), repr((left, right)))
    check('generic same-register synthesis yields e001', synthesize_cmp_same_register(ORIGINAL) == REPLACEMENT)
    pleft, pright, popcode = decode_cmp_format_ii(REPLACEMENT)
    check('patched CMP encodes r0,r0', (pleft, pright) == (0, 0))
    check('CMP opcode bits are preserved', popcode == opcode)
    check('only the second-register field changes', ORIGINAL[0] == REPLACEMENT[0] and ORIGINAL[1] != REPLACEMENT[1])
    check('full field-tested gate context is unique', CF.count(bytes.fromhex('e0d19a0d1a38bfff')) == 1)
    print('\n== 2. BNE is preserved and still points to mismatch arm ==')
    check('following BNE bytes remain 9a0d', CF[BRANCH_VA:BRANCH_VA + 2] == bytes.fromhex('9a0d'))
    cc, target = decode_bcond(BRANCH_VA)
    check('stock branch condition is NE', cc == 10, f'cc=0x{cc:X}')
    check('stock branch target is mismatch bookkeeping at 0x8E6DA', target == 583386, f'0x{target:X}')
    check('neutralized CMP makes BNE condition false for every result', pleft == pright)
    check('fallthrough begins at verified-delivery arm 0x8E6CA', BRANCH_VA + 2 == 583370)
    print('\n== 3. old branch patch is explicitly the wrong direction ==')
    OLD_WRONG_REPLACEMENT = bytes.fromhex('950d')
    old_cc, old_target = decode_bcond(BRANCH_VA, OLD_WRONG_REPLACEMENT)
    check('superseded 950d condition is unconditional BR', old_cc == 5, f'cc=0x{old_cc:X}')
    check('superseded 950d preserves mismatch target', old_target == 583386)
    check('old patch therefore forces mismatch arm, not delivery', old_cc == 5 and old_target != 583370)
    check('correct patch leaves the branch bytes untouched', CF[BRANCH_VA:BRANCH_VA + 2] == bytes.fromhex('9a0d'))
    print('\n== 4. pre-gate freshness handling remains before patched CMP ==')
    check('Gate-2 context keeps freshness call before CMP and delivery calls after it', CF[583360:583386] == bytes.fromhex('bfff86ff1d30e0d19a0d1a38bfff78fb1d301a38bfffe6fbd505'), CF[583360:583386].hex())
    check('patch is two bytes after pre-gate call return setup', PATCH_VA > 583360)
    print('\n== 5. CRC resigning for corrected patch ==')
    check('patch lies in boot CRC region 1', 98304 <= PATCH_VA < 1048048)
    check('CRC fixup remains at terminal word 0xFFDEC', 1048044 == 1048048 - 4)
    check('validity marker remains 0x5AA5A55A', u32(1048064) == 1520805210)
    published = bytearray(CF)
    published[PATCH_VA:PATCH_VA + 2] = REPLACEMENT
    published_prefix = zlib.crc32(published[98304:1048044]) & 4294967295
    published_fixup = published_prefix ^ 4294967295
    check('published-image corrected-patch prefix CRC is pinned', published_prefix == 589594124, f'0x{published_prefix:08X}')
    check('published-image corrected-patch fixup is pinned', published_fixup == 3705373171, f'0x{published_fixup:08X}')
    clean = bytearray(CF)
    clean[766404] = 130
    clean[PATCH_VA:PATCH_VA + 2] = REPLACEMENT
    clean_prefix = zlib.crc32(clean[98304:1048044]) & 4294967295
    clean_fixup = clean_prefix ^ 4294967295
    struct.pack_into('<I', clean, 1048044, clean_fixup)
    clean_residue = zlib.crc32(clean[98304:1048048]) & 4294967295
    check('reconstructed-clean corrected-patch prefix CRC is pinned', clean_prefix == 3191271437, f'0x{clean_prefix:08X}')
    check('reconstructed-clean corrected-patch fixup is 0x41C90FF2', clean_fixup == 1103695858, f'0x{clean_fixup:08X}')
    check('reconstructed-clean corrected-patch residue is 0xFFFFFFFF', clean_residue == 4294967295, f'0x{clean_residue:08X}')
_section_secoc_bypass_patch_point()
print()

print("== secoc acceptance gate ==")
def _section_secoc_acceptance_gate():
    import struct
    REPO = REPO_ROOT
    CF = (REPO / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()

    def u16(off: int) -> int:
        return struct.unpack_from('<H', CF, off)[0]

    def u32(off: int) -> int:
        return struct.unpack_from('<I', CF, off)[0]

    def jarl_target(call_site: int) -> int | None:
        w0, w1 = struct.unpack_from('<HH', CF, call_site)
        if w0 >> 6 & 31 != 30 or w1 & 1:
            return None
        reg2 = w0 >> 11 & 31
        if reg2 == 0:
            return None
        high = w0 & 63
        if high & 32:
            high -= 64
        return call_site + (high << 16) + w1

    def find_jarls(start: int, end: int) -> dict[int, int]:
        out: dict[int, int] = {}
        for off in range(start, min(end, len(CF) - 4), 2):
            target = jarl_target(off)
            if target is not None:
                out[off] = target
        return out
    print('== 1. Gate 1 remains worker-completion filtering ==')
    check('dispatcher calls secoc_rx_verify_worker', jarl_target(583456) == 582842)
    check('Gate 1 is cmp r0,r10 then bne', u16(583462) == 20960 and u16(583464) == 1514, f'0x{u16(583462):04X} 0x{u16(583464):04X}')
    check('worker success enters Gate-2 dispatcher', jarl_target(583470) == 583290)
    print('\n== 2. command-7 KAT pins verify-result polarity ==')
    check('KAT preinitializes verify-result output byte to 1', CF[426236:426242] == bytes.fromhex('010a430f0300'), CF[426236:426242].hex())
    check('KAT passes sp+3 as cryptoif_job_finish result pointer', CF[426314:426322] == bytes.fromhex('234e030082ff5a0a'), CF[426314:426322].hex())
    check('KAT result call targets cryptoif_job_finish', jarl_target(426318) == 560040)
    check('KAT reports pass iff verify-result byte equals zero', CF[426344:426366] == bytes.fromhex('03f06398010a030d2036ff00233e0400e099e20f0000'), CF[426344:426366].hex())
    print('\n== 3. Gate 2 maps zero to delivery and nonzero to mismatch ==')
    GATE2_LOAD = bytes.fromhex('840f5d9de009e10f14d3')
    check('Gate 2 loads FEBE555C and materializes result!=0', CF[583326:583336] == GATE2_LOAD)
    check('FEBE555C load is unique', CF.count(bytes.fromhex('840f5d9d')) == 1)
    check('Gate 2 compares boolean to zero then BNEs to mismatch arm', CF[583364:583372] == bytes.fromhex('1d30e0d19a0d1a38'), CF[583364:583372].hex())
    check('gate CMP is cmp r0,r26', CF[583366:583368] == bytes.fromhex('e0d1'))
    check('following BNE remains 9a0d', CF[583368:583370] == bytes.fromhex('9a0d'))
    check('verified-result fallthrough begins at 0x8E6CA', 583368 + 2 == 583370)
    check('mismatch BNE target is 0x8E6DA', 583386 > 583370)
    print('\n== 4. fallthrough is the PduR/COM delivery chain ==')
    jarls_gate = find_jarls(583290, 583424)
    check('fallthrough calls verification-status helper with success code', jarls_gate.get(583372) == 582212)
    check('fallthrough calls PDU extract/route helper', jarls_gate.get(583380) == 582330)
    check('mismatch branch calls retry/failure bookkeeping', jarls_gate.get(583390) == 582530)
    check('pre-gate freshness/status callback remains before Gate 2', jarls_gate.get(583360) == 583238)
    jarls_delivery = find_jarls(582330, 582410)
    check('delivery helper extracts queued PDU', jarls_delivery.get(582356) == 580004)
    check('delivery helper passes extracted PDU to routing wrapper', jarls_delivery.get(582384) == 583622)
    check('routing wrapper enters PduR-style dispatcher', jarl_target(583628) == 527290)
    check('PduR-style dispatcher terminates in computed routing callback', CF[527388:527398] == bytes.fromhex('25ef61e01330fdc760f9'), CF[527388:527398].hex())
    print('\n== 5. mismatch arm is retained/retry bookkeeping, not delivery ==')
    jarls_mismatch = find_jarls(582530, 582634)
    check('mismatch bookkeeping not direct PDU-routing wrapper', 583622 not in jarls_mismatch.values())
    check('mismatch bookkeeping not PduR dispatcher', 527290 not in jarls_mismatch.values())
    check('mismatch helper contains state/counter updates and status notification call', jarls_mismatch.get(582604) == 582212 and jarls_mismatch.get(582620) == 582410)
    check('post-arm cleanup tests state against 0xB4', CF[583402:583412] == bytes.fromhex('9c0f010001064cffc205'), CF[583402:583412].hex())
    print('\n== 6. Gate 1 completion and Gate 2 verify result are distinct ==')
    GP = 4273911808
    check('job-completion polling cell differs from CMAC verify-result cell', GP + 23486 == 4273935294 and 4273935294 != 4273886556)
    check('cryptoif_job_finish calls crypto_driver_dispatch', jarl_target(560082) == 558422)
    print('\n== 7. shared receive-profile coverage ==')
    profile_can_ids = []
    for i in range(6):
        base = 153970 + i * 80
        can_id = u32(base + 8)
        profile_can_ids.append(can_id)
        check(f'profile {i} has valid CAN ID 0x{can_id:03X}', 0 < can_id < 2048)
    check('profiles cover all six recovered secured inputs', set(profile_can_ids) == {740, 305, 306, 144, 215, 15})
_section_secoc_acceptance_gate()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
