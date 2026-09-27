#!/usr/bin/env python3
"""Keyless execution portability and XCP composition pins.

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

print("== keyless exec portability ==")
def _section_keyless_exec_portability():
    import json
    ROOT = REPO_ROOT
    S = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    H = (ROOT / 'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin').read_bytes()
    F = (ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin').read_bytes()

    def exact_shift(image, off, size):
        return S[off:off + size] == image[off - 28:off - 28 + size]
    print('== shared roots and boot implementation ==')
    for name, img in [('H', H), ('F', F)]:
        check(f'{name} payload-build root matches Sienna', img[49112:49128] == S[49112:49128])
        check(f'{name} boot-SA root matches Sienna', img[49128:49144] == S[49128:49144])
        check(f'{name} app-SA root matches Sienna', img[133184:133200] == S[133184:133200])
    for name, img in [('H', H), ('F', F)]:
        for label, off, size in [('SecurityAccess', 21782, 110), ('RequestDownload', 23912, 468), ('TransferData', 19898, 56), ('TransferExit', 23698, 152), ('RoutineControl', 22142, 696), ('request-seed', 21288, 202), ('send-key', 21490, 12), ('payload-decrypt task', 27614, 116)]:
            check(f'{name} {label} body transfers at -0x1C', exact_shift(img, off, size))
    check('H/F boot domain is byte-identical through 0xA003', H[:40964] == F[:40964])
    check('H/F live handoff stays at absolute 0x9F00 with same fixed-state prefix', H[40704:40738] == F[40704:40738] == S[40704:40738])
    span_log = json.loads((ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/security_access_log.json').read_text())
    attempts = next(iter(span_log['ecus'].values()))['attempts']
    accepted = {a['caller'] for a in attempts if a['outcome'] == 'accepted' and a['call'] == 'send_key'}
    for caller in ('dump_range:codeflash', 'dump_range:local_ram_pe1', 'dump_range:local_ram_self', 'dump_range:dataflash'):
        check(f'Span log records accepted SecurityAccess for {caller}', caller in accepted)
_section_keyless_exec_portability()
print()

print("== keyless xcp composition ==")
def _section_keyless_xcp_composition():
    import struct
    ROOT = REPO_ROOT
    CF = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    LO, HI = (4273961984, 4273994751)

    def u16(o):
        return struct.unpack_from('<H', CF, o)[0]

    def u32(o):
        return struct.unpack_from('<I', CF, o)[0]
    print('== standard dispatcher is fixed and bounded ==')
    command_map = CF[142340:142340 + CF[142289]]
    callbacks = [u32(142384 + i * 4) for i in range(18)]
    check('standard callback table has exactly 18 configured slots', len(callbacks) == 18)
    check('standard map indices stay inside callback table', all((i < len(callbacks) for i in command_map)))
    check('GET_SEED/UNLOCK remain unconfigured', command_map[7] == 0 and command_map[8] == 0)
    check('DOWNLOAD maps to fixed 0x80F12', callbacks[command_map[255 - 240]] == 528146)
    check('MODIFY_BITS maps to fixed 0x80FD8', callbacks[command_map[255 - 236]] == 528344)
    check('XCP write window constants remain exact', u32(177084) == LO and u32(177088) == HI)
    print('\n== DAQ is read-direction only ==')
    check('WRITE_DAQ stores accepted address into DAQ pointer table', CF[529608:529612] == bytes.fromhex('7ee7f194'))
    check('SET_DAQ_LIST_MODE rejects mode bits 0x33 including STIM direction', CF[529728:529736] == bytes.fromhex('6108c10633009a2d'))
    check('DAQ sampler dereferences configured pointer for one-byte read', CF[529090:529104] == bytes.fromhex('00f5c49941d2410a9a0081006090'))
    check('DAQ sampler writes only DTO staging, not through configured pointer', CF[529104:529108] == bytes.fromhex('5397c894'))
    for op in (223, 220, 219):
        check(f'STIM-like opcode 0x{op:02X} is unconfigured', command_map[255 - op] == 0)
    print('\n== custom page/checksum commands cannot redirect writes ==')
    selectors = []
    targets = []
    for i in range(7):
        s, p, t = struct.unpack_from('<B3sI', CF, 177136 + i * 8)
        selectors.append(s)
        targets.append(t)
        check(f'custom record {i} padding is zero', p == b'\x00\x00\x00')
    check('custom selector set is fixed FB/FA/F5/F3/EB/EA/E4', selectors == [251, 250, 245, 243, 235, 234, 228])
    check('custom targets are fixed CodeFlash functions', targets == [619162, 619258, 619570, 619846, 620014, 620136, 620276])
    check('E4 hardcodes CodeFlash 0x10000 -> FEBF7C00', CF[620240:620254] == bytes.fromhex('3e06007cbffe210600000100e505'))
    check('E4 terminates at 0x17DF0', CF[620264:620276] == bytes.fromhex('3306f07d0100f309f1f57f00'))
    check('E4 gate requires source page 0 and destination page 1', CF[620344:620362] == bytes.fromhex('619a8a0d20e65a00e009da05bfff8cffa505'))
    check('F3 hardcodes the same 0x10000..0x17DF0 CodeFlash interval', CF[619896:619908] == bytes.fromhex('3306f07d0100320600000100'))
    check('F3 invokes shared range helper before checksum', CF[619950:619956] == bytes.fromhex('0a30bfffaafd'))
    print('\n== write-arithmetic near misses ==')

    def allowed(start, length):
        if length <= 0 or start > 4294967295 - (length - 1):
            return False
        end = start + length - 1
        return LO <= start <= end <= HI
    check('six-byte DOWNLOAD at window start is valid', allowed(LO, 6))
    check('DOWNLOAD crossing high bound is invalid', not allowed(HI - 2, 6))
    check('32-bit wrap is invalid before range comparison', not allowed(4294967294, 4))
    check('MODIFY_BITS requires word-aligned MTA', CF[528380:528392] == bytes.fromhex('80ffa6010ae0ca060300ba2d'))
    check('largest aligned u32 target cannot wrap below zero', 4294967292 + 3 == 4294967295)
    check('largest aligned u32 target is outside XCP write range', not allowed(4294967292, 4))
_section_keyless_xcp_composition()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
