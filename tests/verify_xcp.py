#!/usr/bin/env python3
"""Raw-firmware and offline-helper proof for the XCP command surface.

Merged portable family module.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

print("== xcp window mpu permissions ==")
def _section_xcp_window_mpu_permissions():
    import struct
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    CF = (ROOT / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()

    def u8(addr: int) -> int:
        return CF[addr]

    def u32(addr: int) -> int:
        return struct.unpack_from('<I', CF, addr)[0]

    def mpat_decode(value: int) -> dict[str, bool]:
        return {'SX': bool(value & 32), 'SW': bool(value & 16), 'SR': bool(value & 8), 'UX': bool(value & 4), 'UW': bool(value & 2), 'UR': bool(value & 1)}
    WINDOW_LO, WINDOW_HI = (4273961984, 4273994748)

    def main() -> int:
        print('== MPU region-1 covers the XCP write window ==')
        check('region-1 lower bound @0x3181C == FEBF7C00', u32(202780) == WINDOW_LO, hex(u32(202780)))
        check('region-1 upper bound @0x31820 == FEBFFBFC', u32(202784) == WINDOW_HI, hex(u32(202784)))
        print('== context/ASID selectors ==')
        check('0x3180F == 0x00 (initial application MPU context)', u8(202767) == 0, hex(u8(202767)))
        check('0x31810 == 0x01 (foreground/flash-end MPU context selector)', u8(202768) == 1, hex(u8(202768)))
        check('0x31811 == 0x00 (CAN1 Tx/Rx ISR MPU context selector)', u8(202769) == 0, hex(u8(202769)))
        check('reset startup explicitly clears ASID to 0 at 0x27A', CF[634:638] == bytes.fromhex('e03f2010'), CF[634:638].hex())
        print('== MPAT1 attribute bytes ==')
        ctx0 = mpat_decode(u8(202904))
        ctx1 = mpat_decode(u8(202968))
        check('ctx0 MPAT1 @0x31898 == 0x000000B8', u32(202904) == 184, hex(u32(202904)))
        check('ctx1 MPAT1 @0x318D8 == 0x000000A8', u32(202968) == 168, hex(u32(202968)))
        check('both MPAT1 values use ASID=0 and G=0', u32(202904) >> 16 & 1023 == 0 and (not u32(202904) & 64) and (u32(202968) >> 16 & 1023 == 0) and (not u32(202968) & 64))
        check('application MPU init enables MPE+SVP (MPM=3)', CF[411836:411842] == bytes.fromhex('0352ea072028'), CF[411836:411842].hex())
        check('ctx0 grants supervisor R/W/execute', ctx0 == {'SX': True, 'SW': True, 'SR': True, 'UX': False, 'UW': False, 'UR': False})
        check('ctx1 grants supervisor R/execute (no write)', ctx1 == {'SX': True, 'SW': False, 'SR': True, 'UX': False, 'UW': False, 'UR': False})
        check('neither context grants user-mode access', not any(((ctx0[k], ctx1[k]) != (False, False) for k in ('UX', 'UW', 'UR'))))
        print('== corrected impact statement boundary ==')
        check('supervisor-executable window: this test asserts permission bits only, no consumer claim', ctx0['SX'] and ctx1['SX'])
        print("NOTE: Ghidra LocalRAM block execute=false is analysis metadata, not a hardware bound.\n      Direct consumer/callback/function census into the window remains zero, so COM-005\n      impact stays 'attacker-writable supervisor-executable RAM, no recovered\n      control-transfer consumer' — not an RCE claim.")
        print(f'\n{passed} passed, {failed} failed')
        return 1 if failed else 0
    main()
_section_xcp_window_mpu_permissions()
print()

print("== xcp boot handoff retention ==")
def _section_xcp_boot_handoff_retention():
    import struct
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    CF = (ROOT / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()

    def u32(addr: int) -> int:
        return struct.unpack_from('<I', CF, addr)[0]
    print('== fixed application handoff source ==')
    check('0x64EE6 loads r6=0x31914 then calls 0x9F00', CF[413414:413424] == bytes.fromhex('260614190300baff1450'), CF[413414:413424].hex())
    record = tuple((u32(203028 + i * 4) for i in range(9)))
    check('retained programming record is fixed {kind=0,id=0x7A1,session=2}', record == (0, 1953, 0, 0, 2, 0, 0, 0, 0), repr(record))
    print('== live boot context establishment ==')
    check('0x9F44 establishes SP/GP/TP and clears MPM before 0x148E', CF[40772:40802] == bytes.fromhex('23060080befe24060098bffe25069c860000e00720281c001f00bfff3075'), CF[40772:40802].hex())
    check('0x148E copies exactly nine dwords into FEBF2908 then enters 0x1398', CF[5262:5280] == bytes.fromhex('80072100243e08910942bfffe0ffbffffcfe'), CF[5262:5280].hex())
    check('0x1398 enters boot init 0x1338', CF[5016:5024] == bytes.fromhex('80072100bfff9cff'), CF[5016:5024].hex())
    print('== reset-only initializer is not on live handoff ==')
    check('reset startup is the sole direct caller of 0x1404', CF[1660:1664] == bytes.fromhex('80ff880d'), CF[1660:1664].hex())
    check('boot runtime init 0x1338 has no call to 0x1404', bytes.fromhex('80ff68') not in CF[4920:4984])
    print('== apparent FEBF7C00 reset clear is zero-trip ==')
    check('0x1426 loads FEBF7C00 but compares against lower FEBE7000', CF[5158:5180] == bytes.fromhex('3e06007cbffeb505010544f221060070befee1f1a1fd'), CF[5158:5180].hex())
    check('FEBF7C00 is above FEBE7000', 4273961984 > 4273893376)
    print('== composition boundary ==')
    check('live-handoff core contains no literal FEBF7C00 materialization', bytes.fromhex('007cbffe') not in CF[413384:413432] and bytes.fromhex('007cbffe') not in CF[40704:40804] and (bytes.fromhex('007cbffe') not in CF[5262:5282]) and (bytes.fromhex('007cbffe') not in CF[5016:5040]))
_section_xcp_boot_handoff_retention()
print()

print("== xcp security ==")
def _section_xcp_security():
    import struct
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    CF = (REPO / 'firmware' / 'RH850_P1M-E_CodeFlash.bin').read_bytes()
    LOCAL_RAM_START = 4273864704
    LOCAL_RAM_END = 4273995775
    SHADOW_START = 4273961984
    SHADOW_END = 4273994751
    COPY_START = 65536
    COPY_END = 97776

    def u16(offset: int) -> int:
        return struct.unpack_from('<H', CF, offset)[0]

    def u32(offset: int) -> int:
        return struct.unpack_from('<I', CF, offset)[0]

    def upload_allowed(start: int, length: int, exclusions: list[tuple[int, int]]) -> bool:
        if length <= 0 or start > 4294967295 - (length - 1):
            return False
        end = start + length - 1
        if LOCAL_RAM_START <= start and end <= LOCAL_RAM_END:
            return not any((start <= excluded_end and excluded_start <= end for excluded_start, excluded_end in exclusions))
        return False

    def shadow_write_allowed(start: int, length: int) -> bool:
        if length <= 0 or start > 4294967295 - (length - 1):
            return False
        end = start + length - 1
        return LOCAL_RAM_START <= start and end <= LOCAL_RAM_END and (SHADOW_START <= start) and (end <= SHADOW_END)
    print('== physical CAN route and command dispatch ==')
    tx_record = struct.unpack_from('<IBBH', CF, 139112)
    rx_record = struct.unpack_from('<IBBH', CF, 139120)
    check('special request CAN ID is 0x7F7', rx_record[0] == 2039, repr(rx_record))
    check('special response CAN ID is 0x7F8', tx_record[0] == 2040, repr(tx_record))
    check('class-5 receive descriptor selects callback 0x82042', u32(137924) == 139120 and u32(137928) == 532546)
    check('receive callback reaches protocol dispatcher', CF[532578:532582] == bytes.fromhex('bfff82ff') and CF[532538:532542] == bytes.fromhex('bfffc6fe'))
    selectors = []
    targets = []
    for index in range(7):
        selector, padding, target = struct.unpack_from('<B3sI', CF, 177136 + index * 8)
        check(f'custom command record {index} has zero padding', padding == b'\x00\x00\x00')
        selectors.append(selector)
        targets.append(target)
    check('custom selectors are FB/FA/F5/F3/EB/EA/E4', selectors == [251, 250, 245, 243, 235, 234, 228], repr(selectors))
    check('custom callback targets match exact handler entries', targets == [619162, 619258, 619570, 619846, 620014, 620136, 620276])
    print('\n== no challenge/unlock gate before memory commands ==')
    command_map = CF[142340:142340 + CF[142289]]
    callback_table = [u32(142384 + index * 4) for index in range(18)]
    check('CONNECT 0xFF maps to connection callback', callback_table[command_map[0]] == 530800)
    check('SET_MTA 0xF6 maps to callback 0x81B76', callback_table[command_map[255 - 246]] == 531318)
    check('SHORT_UPLOAD 0xF4 maps to callback 0x81A2E', callback_table[command_map[255 - 244]] == 530990)
    check('DOWNLOAD 0xF0 maps to callback 0x80F12', callback_table[command_map[255 - 240]] == 528146)
    check('MODIFY_BITS 0xEC maps to callback 0x80FD8', callback_table[command_map[255 - 236]] == 528344)
    check('GET_SEED 0xF8 has no configured callback', command_map[255 - 248] == 0)
    check('UNLOCK 0xF7 has no configured callback', command_map[255 - 247] == 0)
    check('CONNECT, SHORT_UPLOAD, and SET_MTA require eight-byte requests', u16(142244) == 8 and u16(142254) == 8 and (u16(142252) == 8))
    check('SET_MTA stores request bytes 4..7 without an authorization call', CF[531346:531364] == bytes.fromhex('6308e0099a0d0235bfff02f6010a00527d0f'))
    check('custom command dispatcher checks the connection/channel predicate before table scan', CF[618876:618886] == bytes.fromhex('1c30beff08aee051aa25'))
    check('connection predicate rejects disconnected or wrong-channel requests', CF[533636:533660] == bytes.fromhex('a40ff997610a8a0d840ff9978600e609ea5700007f000152'))
    check('standard command dispatcher independently requires matching connected channel', CF[528668:528684] == bytes.fromhex('849ff997a40ff997fc999a3d610afa35'))
    check('receive transport rejects zero or greater-than-eight-byte CTO lengths', CF[532458:532474] == bytes.fromhex('e7470500e041f225a50fb9ece141bb25') and CF[142237] == 8)
    check('receive transport clears the eight-byte staging slot before bounded copy', CF[532474:532504] == bytes.fromhex('a59fbbec000aa50d01f0c3f2c4f1410a3ef62894810001050305f309e1f5') and CF[142239] == 1)
    check('receive transport copies only supplied bytes before dispatch', CF[532504:532542] == bytes.fromhex('000ac50d279f010001f0c4f1c199939f0100410ac1005e9f2894e809c1f5243e2894bfffc6fe'))
    check('generic responder zero-pads short responses to the eight-byte CTO', CF[142292] == 0 and CF[142240] == 8 and (CF[528744:528780] == bytes.fromhex('850ff1ece009fa0d859fbdec830f0300e50501f0ddf18003410a8100f309a1fd639f0200')))
    print('\n== unauthenticated direct SHORT_UPLOAD ==')
    check('SHORT_UPLOAD requires address extension zero', CF[531016:531024] == bytes.fromhex('a60f0300e009da45'))
    check('SHORT_UPLOAD accepts only lengths 1..7', CF[531024:531042] == bytes.fromhex('a6e70100e0e1e23d850fbdec5f0ae1e19f3d'))
    check('SHORT_UPLOAD reads tester little-endian address from request bytes 4..7', CF[531042:531046] == bytes.fromhex('26df0500'))
    check('SHORT_UPLOAD rejects address wrap before validation', CF[531046:531058] == bytes.fromhex('1cd6ffff9a003b08fa09c12d'))
    check('SHORT_UPLOAD calls the shared five-interval exclusion validator', CF[531058:531068] == bytes.fromhex('dbd11b301c3880ff4205'))
    check('SHORT_UPLOAD enforces full LocalRAM bounds after exclusion validation', CF[531068:531088] == bytes.fromhex('250fa1ece1d9b125250f9dece1d1fb1de051da1d'))
    check('SHORT_UPLOAD copies source bytes directly into the response payload', CF[531100:531122] == bytes.fromhex('0198db99939f010001f0ddf1410a8100809bfc09e1f5'))
    check('SHORT_UPLOAD exclusion helper is the same five-entry table used by DAQ', CF[618974:618980] == bytes.fromhex('3206f4930200') and u32(177080) == 5)
    check('SHORT_UPLOAD can directly read an allowed LocalRAM byte', upload_allowed(4273892648, 1, [struct.unpack_from('<II', CF, 168948 + index * 8) for index in range(u32(177080))]))
    print('\n== unauthenticated DAQ read configuration ==')
    daq_commands = {227: 530324, 226: 529356, 225: 529444, 224: 529706, 222: 529898, 221: 530120, 218: 530544, 217: 530606, 216: 530468, 215: 530658}
    for opcode, callback in daq_commands.items():
        index = command_map[255 - opcode]
        check(f'DAQ opcode 0x{opcode:02X} maps to 0x{callback:X}', index < len(callback_table) and callback_table[index] == callback)
    for opcode in (223, 220, 219):
        check(f'DAQ opcode 0x{opcode:02X} is unconfigured', command_map[255 - opcode] == 0)
    check('all configured DAQ requests are eight bytes', all((u16(off) == 8 for off in range(142256, 142276, 2))))
    check('DAQ geometry is four lists x four ODTs x seven byte entries = 112 pointers', u16(142276) == 112 and CF[142279] == 4 and (CF[142280] == 4) and (CF[142281] == 7) and (CF[142279] * CF[142280] * CF[142281] == 112))
    check('four DAQ event slots are configured', CF[142278] == 4)
    check('DAQ event records are reload=2 with event/list IDs 0..3', [tuple(CF[142194 + i * 3:142194 + i * 3 + 3]) for i in range(4)] == [(2, 0, 0), (2, 1, 1), (2, 2, 2), (2, 3, 3)])
    check('WRITE_DAQ validates bit-offset FF, size 1, extension 0', CF[529472:529492] == bytes.fromhex('610862986390010601ff9a6d619afa65e091da65'))
    check('WRITE_DAQ loads request address and invokes one-byte exclusion validator', CF[529492:529504] == bytes.fromhex('26e705001a381c3080ff5e0b'))
    check('WRITE_DAQ validator walks the shared five-entry exclusion table', CF[618974:618980] == bytes.fromhex('3206f4930200') and u32(177080) == 5)
    check('WRITE_DAQ bounds are full LocalRAM FEBE0000..FEBFFFFF', u32(142212) == LOCAL_RAM_START and u32(142208) == LOCAL_RAM_END)
    check('WRITE_DAQ stores the accepted address into the DAQ pointer table', CF[529608:529612] == bytes.fromhex('7ee7f194'))
    check('SET_DAQ_LIST_MODE rejects every mode with mask bits 0x33 set', CF[529728:529736] == bytes.fromhex('6108c10633009a2d'))
    check('DAQ periodic callback chain slots are 810AA -> 81358', u32(142320) == 528554 and u32(142304) == 529240)
    check('DAQ scheduler reloads event record and samples only when counter is zero', CF[529274:529300] == bytes.fromhex('e009ca0dfdf60300c5f13ef68eec600861305c0f0000bfff66ff'))
    check('DAQ scheduler decrements counter on every eligible pass', CF[529300:529312] == bytes.fromhex('1cf0600841ea9d005f0a800b'))
    check('DAQ sampler queues each DTO through 0x81E58', CF[529122:529130] == bytes.fromhex('243ec89480ff720b'))
    check('DAQ sampler loads configured pointer then reads one byte through it', CF[529090:529104] == bytes.fromhex('00f5c49941d2410a9a0081006090'))
    check('DAQ sampled byte is stored into DTO staging, not through configured pointer', CF[529104:529108] == bytes.fromhex('5397c894'))
    check('DAQ transmit callback is 0x8206C and selects special class 0xF800', u32(142224) == 532588 and CF[532600:532610] == bytes.fromhex('863600f80338bfff8ecd'))
    check('DAQ special transmit class resolves to CAN 0x7F8', tx_record[0] == 2040)
    print('\n== RAM upload geometry ==')
    exclusion_count = u32(177080)
    exclusions = [struct.unpack_from('<II', CF, 168948 + index * 8) for index in range(exclusion_count)]
    expected_exclusions = [(4273864704, 4273879039), (4273885232, 4273885851), (4273930888, 4273935307), (4273949016, 4273949491), (4273957888, 4273961183)]
    check('five upload exclusions match firmware table', exclusions == expected_exclusions, repr(exclusions))
    for address in (4273892648, 4273892650, 4273879202, 4273879204, 4273879206):
        check(f'DAQ can select observation byte 0x{address:08X}', upload_allowed(address, 1, exclusions))
    excluded_bytes = sum((end - start + 1 for start, end in exclusions))
    check('107,924 LocalRAM bytes remain readable', 131072 - excluded_bytes == 107924)
    check('shadow start permits seven-byte upload', upload_allowed(SHADOW_START, 7, exclusions))
    check('last copied byte permits one-byte upload', upload_allowed(SHADOW_START + (COPY_END - COPY_START) - 1, 1, exclusions))
    check('upload crossing a protected interval is rejected', not upload_allowed(4273879036, 8, exclusions))
    check('upload wraparound is rejected', not upload_allowed(4294967294, 4, exclusions))
    print('\n== unauthenticated RAM write geometry ==')
    check('write window constants are exact 32 KiB range', u32(177084) == SHADOW_START and u32(177088) == SHADOW_END and (SHADOW_END - SHADOW_START + 1 == 32768))
    check('DOWNLOAD duplicate LocalRAM bounds are FEBE0000..FEBFFFFF', u32(142220) == LOCAL_RAM_START and u32(142216) == LOCAL_RAM_END)
    check('DOWNLOAD gets current MTA through 0x811A2', CF[528210:528214] == bytes.fromhex('80ff5002'))
    check('MTA getter reads FEBE4FF4', CF[528802:528808] == bytes.fromhex('2457f5977f00'))
    check('MTA setter writes FEBE4FF4', CF[528796:528802] == bytes.fromhex('6437f5977f00'))
    check('DOWNLOAD invokes shadow-window validator for requested count', CF[528230:528238] == bytes.fromhex('0a301d3880ff4210'))
    check('shadow validator loads exact low/high constants', CF[619020:619032] == bytes.fromhex('25f6d8740095f231a10d029d'))
    check('DOWNLOAD performs direct tester-byte store through MTA', CF[528270:528292] == bytes.fromhex('0198dc99939f010001f0dbf1410a8100809bfd09e1f5'))
    check('DOWNLOAD advances MTA to end+1', CF[528296:528304] == bytes.fromhex('1a36010080fff001'))
    check('DOWNLOAD max CTO 8 yields payload counts 1..6', CF[142240] == 8 and CF[528172:528192] == bytes.fromhex('a6ef0100850fbdece0e9f2450196fefff2e9bf45'))
    check('zero-length shadow write rejected', not shadow_write_allowed(SHADOW_START, 0))
    check('six-byte shadow write accepted', shadow_write_allowed(SHADOW_START, 6))
    check('write crossing shadow end rejected', not shadow_write_allowed(SHADOW_END - 2, 6))
    check('write address wrap rejected', not shadow_write_allowed(4294967294, 4))
    write_model = bytearray(SHADOW_END - SHADOW_START + 1)
    mta_write = SHADOW_START
    written = 0
    while written < len(write_model):
        count = min(6, len(write_model) - written)
        if not shadow_write_allowed(mta_write, count):
            break
        payload = bytes((written + i & 255 for i in range(count)))
        offset = mta_write - SHADOW_START
        write_model[offset:offset + count] = payload
        mta_write += count
        written += count
    check('repeated DOWNLOAD model covers all 32 KiB', written == 32768)
    check('repeated DOWNLOAD advances MTA exactly one byte past shadow end', mta_write == SHADOW_END + 1)
    check('full-window write model changed final byte', write_model[-1] == 255)
    check('MODIFY_BITS gets same MTA and requires word alignment', CF[528380:528392] == bytes.fromhex('80ffa6010ae0ca060300ba2d'))
    check('MODIFY_BITS validates four bytes against same write window', CF[528392:528404] == bytes.fromhex('0ac603000a30043a80ff9c0f'))
    check('MODIFY_BITS performs in-place 32-bit read-modify-write', CF[528450:528464] == bytes.fromhex('19f0000d0a3041e13ce901edbfff'))
    print('\n== CodeFlash-to-RAM disclosure chain ==')
    check('calibration write window is exact 32 KiB shadow range', u32(177084) == SHADOW_START and u32(177088) == SHADOW_END)
    check('E4 copy loop loads 0x10000 and stores at 0xFEBF7C00', CF[620240:620254] == bytes.fromhex('3e06007cbffe210600000100e505'))
    check('E4 copy loop stops at 0x17DF0', CF[620264:620276] == bytes.fromhex('3306f07d0100f309f1f57f00'))
    check('E4 request gate calls copy only for source page zero and destination page one', CF[620344:620362] == bytes.fromhex('619a8a0d20e65a00e009da05bfff8cffa505'))
    check('F5 accepts only upload lengths 1..7', CF[619602:619620] == bytes.fromhex('683a8a1d61e8e0e9b20568eab10541e29515'))
    check('F5 invokes range check then copies into response bytes', CF[619620:619650] == bytes.fromhex('beff3cab0a301d38bfffeefee0518a0d20de5a0023460100bfff8affa505'))
    check('F5 zeroes all eight local response bytes before copying', CF[619586:619602] == bytes.fromhex('000a0398c19953070000410a680aa6fd'))
    check('positive response helper emits FF then local bytes 1..7', CF[619086:619130] == bytes.fromhex('87003e06945ebefe0706a6ff8a151f0a800b010a0190c691929701000198de99410a680a53970000e6f57f00'))
    copy_length = COPY_END - COPY_START
    shadow = bytearray(SHADOW_END - SHADOW_START + 1)
    shadow[:copy_length] = CF[COPY_START:COPY_END]
    mta = SHADOW_START
    recovered = bytearray()
    while len(recovered) < copy_length:
        chunk_length = min(7, copy_length - len(recovered))
        if not upload_allowed(mta, chunk_length, exclusions):
            break
        offset = mta - SHADOW_START
        recovered.extend(shadow[offset:offset + chunk_length])
        mta += chunk_length
    check('CONNECT/E4/SET_MTA/F5 model recovers low CodeFlash byte-for-byte', bytes(recovered) == CF[COPY_START:COPY_END])
    check('repeated F5 uploads advance MTA to exact copied end', mta == SHADOW_START + copy_length)
    frames = {'connect': bytes.fromhex('ff00000000000000'), 'copy_page': bytes.fromhex('e400000001000000'), 'set_mta': bytes.fromhex('f6000000007cbffe'), 'upload_7': bytes.fromhex('f507000000000000')}
    check('minimal proof sequence uses four exact eight-byte requests', all((len(frame) == 8 for frame in frames.values())))
    check('SET_MTA proof frame targets shadow start little-endian', int.from_bytes(frames['set_mta'][4:8], 'little') == SHADOW_START)
_section_xcp_security()
print()

print("== xcp daq probe ==")
def _section_xcp_daq_probe():
    import subprocess
    import sys
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO))
    from exploit.followups.xcp_daq_probe import ENTRIES_PER_ODT, FORBIDDEN_COMMANDS, MAX_ENTRIES, PROFILES, SCHEMA, SECOC_XCP_EXCLUDED_CANDIDATES, XcpDaqError, assert_no_write_commands, build_plan, clear_daq_list_request, configure_daq, configuration_requests, control_rtt_statistics, decode_dto, layout, profile_or_addresses, set_daq_list_mode_request, set_daq_ptr_request, start_stop_daq_list_request, validate_addresses, write_daq_request
    from exploit.followups.xcp_read_probe import LOCALRAM_EXCLUSIONS
    CF = (REPO / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()

    def rejects(fn) -> bool:
        try:
            fn()
        except (XcpDaqError, Exception) as exc:
            return isinstance(exc, XcpDaqError) or exc.__class__.__name__ == 'XcpReadError'
        return False
    print('== exact DAQ request encodings ==')
    check('CLEAR_DAQ_LIST list 0', clear_daq_list_request().hex() == 'e300000000000000')
    check('SET_DAQ_PTR list0/odt2/entry0', set_daq_ptr_request(0, 2, 0).hex() == 'e200000002000000')
    check('WRITE_DAQ uses FF/01/00 plus little-endian address', write_daq_request(4273892648).hex() == 'e1ff0100286dbefe')
    check('SET_DAQ_LIST_MODE uses event0/prescaler1/priority0', set_daq_list_mode_request().hex() == 'e000000000000100')
    check('START_DAQ_LIST list0', start_stop_daq_list_request(True).hex() == 'de01000000000000')
    check('STOP_DAQ_LIST list0', start_stop_daq_list_request(False).hex() == 'de00000000000000')
    print('\n== firmware-bound limits and profiles ==')
    expected_exclusions = tuple(((int.from_bytes(CF[168948 + i * 8:168952 + i * 8], 'little'), int.from_bytes(CF[168952 + i * 8:168956 + i * 8], 'little') + 1) for i in range(5)))
    check('DAQ helper inherits exact firmware LocalRAM exclusions', LOCALRAM_EXCLUSIONS == expected_exclusions, repr(expected_exclusions))
    check('one list exposes 4x7=28 byte entries', MAX_ENTRIES == 28 and ENTRIES_PER_ODT == 7)
    check('all named profile addresses pass the firmware read validator', all((not rejects(lambda p=p: validate_addresses(p.addresses)) for p in PROFILES.values())))
    check('actuation profile is exactly one full ODT', len(PROFILES['actuation-discriminator'].addresses) == 7)
    check('diagnostic-control profile maps DIAG-APP-016/017/018', PROFILES['diagnostic-control-state'].finding_ids == ('DIAG-APP-016', 'DIAG-APP-017', 'DIAG-APP-018'))
    check('routine-lifecycle profile maps DIAG-APP-010/011', PROFILES['routine-lifecycle-state'].finding_ids == ('DIAG-APP-010', 'DIAG-APP-011'))
    check('routine-lifecycle profile fits exactly one ODT', len(PROFILES['routine-lifecycle-state'].addresses) == 7)
    check('async/BA profile maps DIAG-APP-023 and SEC-APP-007', PROFILES['async-ba-state'].finding_ids == ('DIAG-APP-023', 'SEC-APP-007'))
    check('BA operational profile maps DIAG-APP-024', PROFILES['ba-operational-state'].finding_ids == ('DIAG-APP-024',))
    print('\n== SecOC verification-state profile is firmware-pinned, not guessed ==')
    secoc = PROFILES['secoc-verification-state']
    check('SecOC profile maps SECOC-011/012/029', secoc.finding_ids == ('SECOC-011', 'SECOC-012', 'SECOC-029'))
    check('SecOC profile observes exactly the pinned SecOC state bytes', secoc.addresses == (4273886556, 4273886568, 4273886572, 4273886560, 4273886562, 4273886564), repr([hex(a) for a in secoc.addresses]))
    check('SecOC profile fits one ODT', len(secoc.addresses) <= ENTRIES_PER_ODT)
    import json as _json
    import struct as _struct
    CANON = {'0x0008e9fc': {'febe5568', 'febe556c'}, '0x0008e7d4': {'febe5560', 'febe5562', 'febe5564'}, '0x0008ef9e': {'febe5568', 'febe556c'}}
    corpus_refs: dict[str, set[str]] = {}
    with (REPO / 'data/generated/decompilations.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            row = _json.loads(line)
            if row.get('record') == 'function' and row.get('entry_addr') in CANON:
                corpus_refs[row['entry_addr']] = {ref['to_addr'].lower().lstrip('0x') for ref in row.get('data_references', []) if isinstance(ref.get('to_addr'), str)}
    for entry, expected in CANON.items():
        check(f'corpus function {entry} references the claimed sync words', expected <= corpus_refs.get(entry, set()), repr(sorted(corpus_refs.get(entry, set()))))
    check('MAC-result byte FEBE555C is loaded by the unique pinned Gate-2 instruction', CF[583326:583336] == bytes.fromhex('840f5d9de009e10f14d3') and CF.count(bytes.fromhex('840f5d9d')) == 1)
    check('MAC-result GP-relative offset -0x62A4 resolves to FEBE555C', 4273911808 - 25252 == 4273886556)
    for address, reason in SECOC_XCP_EXCLUDED_CANDIDATES:
        check(f'firmware-excluded SecOC candidate {address:#010X} is rejected by the validator', rejects(lambda a=address: validate_addresses((a,))), reason)
    check('no profile contains a firmware-excluded SecOC candidate', all((addr not in p.addresses for p in PROFILES.values() for addr, _ in SECOC_XCP_EXCLUDED_CANDIDATES)))
    check('SecOC profile mentions the deliberately excluded observation paths', 'firmware-excluded' in secoc.description and 'command-5 generated-result buffer' in secoc.description)
    check('protected XCP interval cannot be configured as a DAQ source', rejects(lambda: validate_addresses((4273949016,))))
    check('duplicate sources rejected', rejects(lambda: validate_addresses((4273892648, 4273892648))))
    check('more than 28 sources rejected', rejects(lambda: validate_addresses(tuple((4273889280 + i for i in range(29))))))
    print('\n== deterministic layout and DTO decoding ==')
    addresses = tuple((4273889280 + i for i in range(10)))
    groups = layout(addresses)
    check('ten sources split as 7+3 across two ODTs', [len(group) for group in groups] == [7, 3])
    first = decode_dto(bytes.fromhex('0001020304050607'), addresses)
    second = decode_dto(bytes.fromhex('0108090a00000000'), addresses)
    check('PID0 decodes first seven configured sources', first is not None and [v['value'] for v in first['values']] == [1, 2, 3, 4, 5, 6, 7])
    check('PID1 decodes remaining three sources', second is not None and [v['value'] for v in second['values']] == [8, 9, 10])
    check('command response PID FF is ignored by DTO decoder', decode_dto(bytes.fromhex('ff00000000000000'), addresses) is None)
    check('unconfigured PID is ignored', decode_dto(bytes.fromhex('0300000000000000'), addresses) is None)
    print('\n== configuration plan is observation-only ==')
    profile = PROFILES['actuation-discriminator']
    plan = build_plan(profile.addresses, name=profile.name, description=profile.description, finding_ids=profile.finding_ids)
    opcodes = [int(row['request'][:2], 16) for row in plan['configuration']]
    check('plan declares no source-memory write primitive', plan['source_memory_write_implemented'] is False)
    check('plan declares DAQ configuration volatile only', plan['volatile_daq_configuration_only'] is True)
    check('plan makes no wall-clock sampling-rate claim', plan['wall_clock_rate_claimed'] is False)
    check('one-ODT profile uses CONNECT/CLEAR/PTR/7 WRITE_DAQ/MODE/START', opcodes == [255, 227, 226] + [225] * 7 + [224, 222], repr(opcodes))
    check('plan contains no generic XCP memory-write opcode F0/EC', 240 not in opcodes and 236 not in opcodes)
    check('cleanup is explicit STOP_DAQ_LIST', plan['cleanup']['request'] == 'de00000000000000' and plan['cleanup']['required_even_on_capture_error'])
    requests = configuration_requests(profile.addresses)
    check('configuration request count is 12 for seven-source profile', len(requests) == 12)
    check('every DAQ request is an eight-byte CTO', all((len(request) == 8 for _, request in requests)))

    class InterleavedDtoPanda:

        def __init__(self):
            self.queue = []

        def can_send(self, address, data, bus):
            request = bytes(data)
            if request[:2] == bytes.fromhex('de01'):
                self.queue.append((2040, 0, bytes.fromhex('0001020304050607'), bus))
            self.queue.append((2040, 0, bytes.fromhex('ff00000000000000'), bus))

        def can_recv(self):
            queued, self.queue = (self.queue, [])
            return queued
    interleaved = InterleavedDtoPanda()
    try:
        configured = configure_daq(interleaved, bus=1, timeout=0.01, addresses=profile.addresses)
    except Exception:
        interleaved_ok = False
    else:
        interleaved_ok = configured[0]['entry_count'] == 7
    check('control exchange ignores interleaved DTO before START positive response', interleaved_ok)

    class StartTimeoutPanda:

        def __init__(self):
            self.queue = []
            self.sent = []

        def can_send(self, address, data, bus):
            request = bytes(data)
            self.sent.append((int(address), request, int(bus)))
            if request[:2] == bytes.fromhex('de01'):
                return
            self.queue.append((2040, 0, bytes.fromhex('ff00000000000000'), bus))

        def can_recv(self):
            queued, self.queue = (self.queue, [])
            return queued
    cleanup_panda = StartTimeoutPanda()
    check('start-response timeout fails closed', rejects(lambda: configure_daq(cleanup_panda, bus=1, timeout=0.001, addresses=profile.addresses)))
    check('start-response timeout still sends STOP_DAQ_LIST cleanup', len(cleanup_panda.sent) >= 2 and cleanup_panda.sent[-2][1][:2] == bytes.fromhex('de01') and (cleanup_panda.sent[-1][1][:2] == bytes.fromhex('de00')))
    print('\n== v2 evidence/provenance hardening ==')
    check('DAQ observer schema pinned as v2', SCHEMA == 'sienna-xcp-daq-observer-v2')
    check('plan declares no generic write command implementation', plan['write_commands_implemented'] is False)
    check('plan publishes the forbidden-opcode audit including E4 page copy', set(plan['forbidden_command_opcodes']) == {f'0x{op:02X}' for op in FORBIDDEN_COMMANDS} and 228 in FORBIDDEN_COMMANDS and (240 in FORBIDDEN_COMMANDS) and (236 in FORBIDDEN_COMMANDS))
    assert_no_write_commands(requests)
    check('real configuration requests pass the no-write guard', True)
    try:
        assert_no_write_commands((('download', bytes([240]) + bytes(7)),))
    except XcpDaqError:
        check('guard refuses a crafted F0 DOWNLOAD request', True)
    else:
        check('guard refuses a crafted F0 DOWNLOAD request', False)
    try:
        assert_no_write_commands((('copy_page', bytes([228]) + bytes(7)),))
    except XcpDaqError:
        check('guard refuses the E4 page copy as shadow mutation', True)
    else:
        check('guard refuses the E4 page copy as shadow mutation', False)

    class TimingPanda:
        """Answers every control request positively so timing evidence is produced."""

        def __init__(self):
            self.queue = []

        def can_send(self, address, data, bus):
            request = bytes(data)
            response = bytes([255]) + request[1:]
            if request[:2] == bytes.fromhex('de01'):
                response = bytes([255, 0]) + request[2:]
            self.queue.append((2040, 0, response, bus))

        def can_recv(self):
            queued, self.queue = (self.queue, [])
            return queued
    timing_panda = TimingPanda()
    try:
        counts, timings = configure_daq(timing_panda, bus=1, timeout=0.05, addresses=profile.addresses)
    except Exception as exc:
        raise exc
    stats = control_rtt_statistics(timings)
    check('configure_daq now returns per-request control timings', counts['entry_count'] == 7 and len(timings) == 12 and ({row['operation'] for row in timings} == {op for op, _ in configuration_requests(profile.addresses)}), repr(sorted({row['operation'] for row in timings})))
    check('each timing row records request hex and both-clock stamps', all((set(row) >= {'operation', 'request_hex', 'requested_monotonic', 'received_monotonic', 'rtt_seconds', 'received_wall_utc'} for row in timings)) and all((row['rtt_seconds'] >= 0 for row in timings)))
    check('control RTT statistics summarize the recorded timings', stats is not None and stats['count'] == len(timings) and (stats['min_seconds'] <= stats['mean_seconds'] <= stats['max_seconds']) and (stats['jitter_seconds'] == stats['max_seconds'] - stats['min_seconds']) and (stats['samples_source'] == 'time.monotonic deltas only'))

    class StreamingDtoPanda:
        """Emits one DTO per can_recv poll so capture wall stamps are exercised."""

        def __init__(self):
            self.calls = 0

        def can_send(self, address, data, bus):
            pass

        def can_recv(self):
            self.calls += 1
            return [(2040, 0, bytes.fromhex('0001020304050607'), 1)]
    from exploit.followups.xcp_daq_probe import capture_dto_frames
    streamed = capture_dto_frames(StreamingDtoPanda(), bus=1, addresses=profile.addresses, duration_seconds=0.05, max_frames=5)
    check('captured DTO frames now carry wall-clock stamps', len(streamed) == 5 and all(('captured_wall_utc' in row and 'captured_monotonic' in row for row in streamed)) and all((row['captured_wall_utc'].startswith('2') for row in streamed)))
    check('run-live metadata schema fields exist in source', all((token in (REPO / 'exploit/followups/xcp_daq_probe.py').read_text() for token in ('"control_timing"', '"capture_window"', '"truncated_by_frame_cap"'))))
    print('\n== CLI guardrails ==')
    probe = REPO / 'exploit/followups/xcp_daq_probe.py'
    plan_cli = subprocess.run([sys.executable, str(probe), '--profile', 'actuation-discriminator'], cwd=REPO, capture_output=True, text=True, check=False)
    check('CLI defaults to non-live plan', plan_cli.returncode == 0 and '"mode": "plan"' in plan_cli.stdout)
    check('CLI publishes COM-007 profile binding', '"COM-007"' in plan_cli.stdout and '"source_memory_write_implemented": false' in plan_cli.stdout)
    unsafe = subprocess.run([sys.executable, str(probe), '--profile', 'actuation-discriminator', '--execute'], cwd=REPO, capture_output=True, text=True, check=False)
    check('live DAQ refuses missing bench acknowledgement', unsafe.returncode != 0)
    conflict = subprocess.run([sys.executable, str(probe), '--profile', 'actuation-discriminator', '--address', '0xFEBE6D28'], cwd=REPO, capture_output=True, text=True, check=False)
    check('CLI rejects profile plus custom-address ambiguity', conflict.returncode != 0)
_section_xcp_daq_probe()
print()

print("== xcp reachability ==")
def _section_xcp_reachability():
    import subprocess
    import sys
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO))
    from exploit.followups.xcp_daq_probe import XcpDaqError
    from exploit.followups.xcp_read_probe import CONNECT_REQUEST
    from exploit.followups.xcp_reachability import CONNECT_PID, FORBIDDEN_COMMANDS, SCHEMA, VERDICT_REACHABLE_ERROR, VERDICT_REACHABLE_POSITIVE, VERDICT_TIMEOUT, VERDICT_UNEXPECTED, XcpReachabilityError, assert_connect_only, build_plan, classify_response, forbidden_opcode_audit
    print('== CONNECT-only guard ==')
    check('schema pinned as v1', SCHEMA == 'sienna-xcp-reachability-v1')
    assert_connect_only(CONNECT_REQUEST)
    check('stock CONNECT frame passes the guard', True)
    for opcode in (228, 240, 236, 246, 245, 244, 227, 226, 225, 224, 222):
        try:
            assert_connect_only(bytes([opcode]) + bytes(7))
        except XcpReachabilityError:
            check(f'opcode 0x{opcode:02X} is refused', True)
        else:
            check(f'opcode 0x{opcode:02X} is refused', False)
    try:
        assert_connect_only(CONNECT_REQUEST + b'\x00')
    except XcpReachabilityError:
        check('non-eight-byte request is refused', True)
    else:
        check('non-eight-byte request is refused', False)
    check('E4 refusal names the shadow-window mutation explicitly', 'shadow' in FORBIDDEN_COMMANDS[228].lower() and 'mutates' in FORBIDDEN_COMMANDS[228].lower())
    check('generic write opcodes F0/EC are in the forbidden table', 240 in FORBIDDEN_COMMANDS and 236 in FORBIDDEN_COMMANDS)
    print('\n== plan artifact ==')
    plan = build_plan()
    check('plan declares the single CONNECT request', plan['single_request'] == {'operation': 'connect', 'request': CONNECT_REQUEST.hex()})
    check('plan declares CONNECT-only with one request per run', plan['no_write_guard']['connect_only'] is True and plan['no_write_guard']['single_request_per_run'] is True)
    check('plan declares no write commands and no page copy', plan['no_write_guard']['write_commands_implemented'] is False and plan['no_write_guard']['page_copy_sent'] is False)
    check('plan forbids every non-CONNECT opcode it names', set(plan['no_write_guard']['forbidden_command_opcodes']) == {f'0x{op:02X}' for op in FORBIDDEN_COMMANDS})
    check('plan binds the 0x7F7/0x7F8 route', plan['request_can_id'] == '0x7F7' and plan['response_can_id'] == '0x7F8')
    check('plan requires bench isolation', plan['bench_isolated_required'] is True)
    check('audit helper matches the plan guard', forbidden_opcode_audit()['forbidden_command_opcodes'] == plan['no_write_guard']['forbidden_command_opcodes'])
    print('\n== response classification ==')
    positive = classify_response(bytes.fromhex('ff00000000000000'))
    check('positive CONNECT response is reachable', positive['verdict'] == VERDICT_REACHABLE_POSITIVE and positive['reachable'] is True and (positive['raw_response_hex'] == 'ff00000000000000'))
    error = classify_response(bytes.fromhex('fe22000000000000'))
    check('XCP error response still proves physical reachability', error['verdict'] == VERDICT_REACHABLE_ERROR and error['reachable'] is True and (error['error_code'] == '0x22'))
    unexpected = classify_response(bytes.fromhex('5500000000000000'))
    check('unexpected PID is not reachable evidence', unexpected['verdict'] == VERDICT_UNEXPECTED and unexpected['reachable'] is False)
    try:
        classify_response(bytes(9))
    except XcpReachabilityError:
        check('non-eight-byte response is rejected', True)
    else:
        check('non-eight-byte response is rejected', False)
    check('timeout verdict exists and is not reachable', VERDICT_TIMEOUT == 'no_response_timeout')
    print('\n== source-level no-write invariants ==')
    source = (REPO / 'exploit/followups/xcp_reachability.py').read_text(encoding='utf-8')
    can_send_calls = [line.strip() for line in source.splitlines() if '.can_send(' in line]
    check('exactly one transmit call site exists', len(can_send_calls) == 1, repr(can_send_calls))
    check('the only transmit sends the guarded CONNECT frame', 'panda.can_send(REQUEST_ID, CONNECT_REQUEST, route.bus)' in can_send_calls[0])
    check('guard runs against the literal frame before transmit', source.index('assert_connect_only(CONNECT_REQUEST)') < source.index('panda.can_send(REQUEST_ID, CONNECT_REQUEST, route.bus)'))
    check('no page-copy / SET_MTA / DOWNLOAD / MODIFY_BITS byte literal appears in the module', all((token not in source for token in ('"\\xe4', '"\\xf6', '"\\xf0\\x', '"\\xec\\x'))))
    check('module documents why E4 is excluded', 'mutates' in source.lower() and 'shadow' in source.lower())
    print('\n== read/DAQ probes keep their intentional behavior ==')
    read_source = (REPO / 'exploit/followups/xcp_read_probe.py').read_text(encoding='utf-8')
    check('acquisition probe still performs its E4 page copy', 'COPY_REQUEST = bytes.fromhex("e400000001000000")' in read_source)
    daq_source = (REPO / 'exploit/followups/xcp_daq_probe.py').read_text(encoding='utf-8')
    check('DAQ probe still declares volatile-configuration-only DAQ', '"volatile_daq_configuration_only": True' in daq_source)
    check('DAQ probe forbids generic write opcodes', 'FORBIDDEN_COMMANDS' in daq_source)
    print('\n== CLI guardrails ==')
    probe = REPO / 'exploit/followups/xcp_reachability.py'
    plan_cli = subprocess.run([sys.executable, str(probe)], cwd=REPO, capture_output=True, text=True, check=False)
    check('CLI defaults to non-live plan', plan_cli.returncode == 0 and '"mode": "plan"' in plan_cli.stdout and ('"connect_only": true' in plan_cli.stdout))
    unsafe = subprocess.run([sys.executable, str(probe), '--execute'], cwd=REPO, capture_output=True, text=True, check=False)
    check('live reachability refuses missing bench acknowledgement', unsafe.returncode != 0)
    mismatch = subprocess.run([sys.executable, str(probe), '--execute', '--bench-isolated'], cwd=REPO, capture_output=True, text=True, check=False)
    check('live reachability refuses to run without route/identity binding', mismatch.returncode != 0)
    bad_frame = subprocess.run([sys.executable, str(probe), '--execute', '--bench-isolated', '--timeout', '0'], cwd=REPO, capture_output=True, text=True, check=False)
    check('non-positive timeout is rejected', bad_frame.returncode != 0)
_section_xcp_reachability()
print()

print("== xcp shadow write plan ==")
def _section_xcp_shadow_write_plan():
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(REPO))
    from exploit.followups.xcp_shadow_write_plan import MAX_DOWNLOAD, SHADOW_END, SHADOW_SIZE, SHADOW_START, XcpShadowWriteError, build_download_plan, chunk_write, download_request, modify_bits_request, set_mta_request, simulate_plan, simulate_write, validate_window

    def rejects(fn) -> bool:
        try:
            fn()
        except XcpShadowWriteError:
            return True
        return False
    print('== exact request encoding ==')
    check('shadow geometry is exact 32 KiB', SHADOW_START == 4273961984 and SHADOW_END == 4273994751 and (SHADOW_SIZE == 32768))
    check('SET_MTA encodes tester address little-endian', set_mta_request(SHADOW_START).hex() == 'f6000000007cbffe')
    check('DOWNLOAD 1 byte is padded to CTO 8', download_request(bytes.fromhex('aa')).hex() == 'f001aa0000000000')
    check('DOWNLOAD 6 bytes fills CTO 8', download_request(bytes.fromhex('010203040506')).hex() == 'f006010203040506')
    check('DOWNLOAD maximum is six data bytes', MAX_DOWNLOAD == 6 and rejects(lambda: download_request(b'1234567')))
    check('MODIFY_BITS raw fields encode as EC/shift/u16le/u16le/pad', modify_bits_request(3, 4660, 43981).hex() == 'ec033412cdab0000')
    print('\n== range and chunk model ==')
    check('zero-length write rejected', rejects(lambda: validate_window(SHADOW_START, 0)))
    check('write before shadow rejected', rejects(lambda: validate_window(SHADOW_START - 1, 1)))
    check('write crossing shadow end rejected', rejects(lambda: validate_window(SHADOW_END, 2)))
    chunks = chunk_write(SHADOW_START + 4, bytes(range(14)))
    check('14-byte write chunks as 6/6/2', [len(chunk.data) for chunk in chunks] == [6, 6, 2])
    check('chunk addresses advance by payload length', [chunk.address for chunk in chunks] == [SHADOW_START + 4, SHADOW_START + 10, SHADOW_START + 16])
    check('chunk payloads reconstruct exactly', b''.join((chunk.data for chunk in chunks)) == bytes(range(14)))
    plan = build_download_plan(SHADOW_START + 4, bytes(range(14)))
    check('plan binds COM-005', plan['finding_id'] == 'COM-005')
    check('planner has no live execution path', plan['live_execution_implemented'] is False)
    check('plan records impact bounds: Ghidra execute=false is analysis metadata; hardware MPU grants supervisor execute; no direct consumer', plan['window']['executable'] is False and plan['window']['executable_basis'] == 'ghidra_localram_block_metadata' and (plan['window']['hardware_mpu_supervisor_executable'] is True) and (plan['window']['direct_runtime_consumer_recovered'] is False))
    check('plan emits CONNECT + SET_MTA + three DOWNLOAD frames', [row['operation'] for row in plan['requests']] == ['connect', 'set_mta', 'download', 'download', 'download'])
    check('all planned frames are exactly eight bytes', all((len(bytes.fromhex(row['request'])) == 8 for row in plan['requests'])))
    print('\n== deterministic local simulation ==')
    shadow = bytes((index & 255 for index in range(SHADOW_SIZE)))
    data = bytes.fromhex('deadbeef001122')
    updated = simulate_write(shadow, SHADOW_START + 256, data)
    check('simulation preserves 32 KiB geometry', len(updated) == SHADOW_SIZE)
    check('simulation changes exact requested slice', updated[256:263] == data)
    check('simulation preserves prefix/suffix', updated[:256] == shadow[:256] and updated[263:] == shadow[263:])
    updated2, simulated = simulate_plan(shadow, SHADOW_START + 256, data)
    check('simulation helper returns identical bytes', updated2 == updated)
    check('simulation metadata reports output hash and bounded changes', simulated['mode'] == 'simulation' and 0 < simulated['simulation']['changed_bytes'] <= len(data))
    print('\n== CLI is offline-only ==')
    probe = REPO / 'exploit/followups/xcp_shadow_write_plan.py'
    source = probe.read_text(encoding='utf-8')
    check('planner source has no Panda import', 'from panda import' not in source and 'import panda' not in source)
    check('planner source exposes no execute flag', '--execute' not in source)
    cli = subprocess.run([sys.executable, str(probe), hex(SHADOW_START), '01020304050607'], cwd=REPO, capture_output=True, text=True, check=False)
    check('CLI emits two DOWNLOADs for seven bytes', cli.returncode == 0 and '"download_requests": 2' in cli.stdout)
    unsafe = subprocess.run([sys.executable, str(probe), hex(SHADOW_START - 1), '01'], cwd=REPO, capture_output=True, text=True, check=False)
    check('CLI rejects address outside shadow window', unsafe.returncode != 0)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source_shadow = root / 'shadow.bin'
        output_shadow = root / 'out.bin'
        source_shadow.write_bytes(shadow)
        simulated_cli = subprocess.run([sys.executable, str(probe), hex(SHADOW_START + 256), data.hex(), '--simulate-shadow', str(source_shadow), '--simulation-output', str(output_shadow)], cwd=REPO, capture_output=True, text=True, check=False)
        check('CLI simulation writes exact local output only', simulated_cli.returncode == 0 and output_shadow.read_bytes() == updated)
_section_xcp_shadow_write_plan()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
