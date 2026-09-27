#!/usr/bin/env python3
"""Raw-firmware XCP pins: window MPU permissions, boot handoff retention, and XCP security surface.

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

print("== xcp window mpu permissions ==")
def _section_xcp_window_mpu_permissions():
    import struct
    ROOT = REPO_ROOT
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
        print(f'\n{passed} passed, {failed} failed')
        return 1 if failed else 0
    main()
_section_xcp_window_mpu_permissions()
print()

print("== xcp boot handoff retention ==")
def _section_xcp_boot_handoff_retention():
    import struct
    ROOT = REPO_ROOT
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
    print('== composition boundary ==')
    check('live-handoff core contains no literal FEBF7C00 materialization', bytes.fromhex('007cbffe') not in CF[413384:413432] and bytes.fromhex('007cbffe') not in CF[40704:40804] and (bytes.fromhex('007cbffe') not in CF[5262:5282]) and (bytes.fromhex('007cbffe') not in CF[5016:5040]))
_section_xcp_boot_handoff_retention()
print()

print("== xcp security ==")
def _section_xcp_security():
    import struct
    REPO = REPO_ROOT
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
_section_xcp_security()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
