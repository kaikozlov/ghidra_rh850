#!/usr/bin/env python3
"""Raw-firmware keyless-execution surface and reset-entry pins.

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

print("== keyless exec surface ==")
def _section_keyless_exec_surface():
    import json
    import struct
    REPO = REPO_ROOT
    SIENNA = (REPO / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    ALBINO = (REPO / 'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin').read_bytes()
    SPAN = (REPO / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin').read_bytes()
    IMAGES = {'sienna-8965B4512000': SIENNA, 'albinoelephant-8965H1202000': ALBINO, 'spanconstant-8965F1208000': SPAN}
    FOREIGN = {'albinoelephant-8965H1202000': ALBINO, 'spanconstant-8965F1208000': SPAN}
    PAYLOAD_BUILD_SECRET = bytes.fromhex('ba052435f8843f985fd1329d2b6117b0')
    BOOT_SA_SECRET = bytes.fromhex('f05f36b7d78c03e24ab4faef2a57d044')
    APP_SA_SECRET = bytes.fromhex('893e08418c741ffa2a9c044bffa55813')
    BOOT_UDS_TABLE = {'sienna': 36436, 'corolla': 36404}
    UDS_RECORD_COUNT = 20
    COROLLA_SHIFT = -28
    EXPECTED_SIDS = [16, 17, 39, 40, 62, 133, 34, 35, 44, 46, 20, 25, 47, 49, 52, 54, 55, 171, 186, 187]
    EXPECTED_POLICIES = [3, 2, 2, 1, 1, 1, 2, 3, 3, 2, 2, 3, 3, 2, 2, 2, 2, 3, 3, 3]
    UDS_HANDLER_BODIES = [('uds_diagnostic_session_control', 24906, 186), ('uds_ecu_reset', 24770, 114), ('uds_security_access', 21782, 110), ('uds_communication_control', 26762, 112), ('uds_tester_present', 20472, 104), ('uds_control_dtc_setting', 26938, 96), ('uds_read_data_by_identifier', 24504, 70), ('uds_unsupported_service_handler', 27056, 34), ('uds_write_data_by_identifier', 18760, 328), ('uds_routine_control', 22142, 696), ('uds_request_download', 23912, 468), ('uds_transfer_data', 19898, 56), ('uds_request_transfer_exit', 23698, 152)]
    CRITICAL_BOOT_BODIES = [('uds_security_access_request_seed', 21288, 202), ('uds_security_access_send_key', 21490, 12), ('routine_verify_crc_cmac_task', 22838, 206), ('payload_decrypt_enqueue', 27572, 30), ('payload_decrypt_transfer_task', 27614, 116), ('boot_diag_init_root', 1904, 16), ('boot_diag_enable_record', 27090, 52), ('boot_diag_init_dispatch', 27170, 138), ('boot_transfer_auth_state_init', 20614, 100)]
    XCP_ROUTE_IDS = (2039, 2040)
    XCP_DESCRIPTOR_ATTR = 2
    XCP_DESCRIPTOR_TAG = 2147483648
    XCP_WINDOW = (4273961984, 4273994751)
    BOOT_GP = 4273969152
    APP_INFO_COPY = {'sienna-8965B4512000': (403042, 4273961904, 155296, 168948), 'albinoelephant-8965H1202000': (379318, 4273961808, 154544, 167692), 'spanconstant-8965F1208000': (379318, 4273961808, 154544, 167692)}
    APP_INFO_SOURCE = 133136
    APP_SA_OFFSET_IN_COPY = 133184 - APP_INFO_SOURCE
    SECURITY_STATE = {'boot SecurityAccess state': 4273941263, 'payload authorization bitfield': 4273941265, 'SA seed buffer': 4273941284, 'SA key/data buffer': 4273941300, 'SA handshake state': 4273941333, 'payload decrypt queue/busy flag': 4273941470}

    def find_all(image: bytes, needle: bytes) -> list[int]:
        offs: list[int] = []
        start = 0
        while True:
            i = image.find(needle, start)
            if i < 0:
                return offs
            offs.append(i)
            start = i + 1

    def uds_table(image: bytes, base: int) -> list[bytes]:
        raw = image[base:base + UDS_RECORD_COUNT * 8]
        if len(raw) != UDS_RECORD_COUNT * 8:
            return []
        return [raw[i * 8:(i + 1) * 8] for i in range(UDS_RECORD_COUNT)]

    def shift_record(rec: bytes, delta: int) -> bytes:
        handler, = struct.unpack_from('<H', rec, 4)
        return rec[:4] + struct.pack('<H', handler + delta & 65535) + rec[6:]

    def exact_shifted_body(image: bytes, sienna_entry: int, size: int) -> bool:
        target = sienna_entry + COROLLA_SHIFT
        return SIENNA[sienna_entry:sienna_entry + size] == image[target:target + size]

    def overlaps(start: int, size: int, exclusions: list[tuple[int, int]]) -> bool:
        end = start + size - 1
        return any((start <= hi and lo <= end for lo, hi in exclusions))

    def canonical_sienna_boot_window_refs() -> list[tuple[str, int, list[tuple[str, str]]]]:
        rows = []
        lo, hi = XCP_WINDOW
        with (REPO / 'data/generated/decompilations.jsonl').open() as f:
            for line in f:
                rec = json.loads(line)
                if rec.get('record') != 'function':
                    continue
                try:
                    entry = int(rec.get('entry_addr') or '', 16)
                except ValueError:
                    continue
                if entry >= 131072:
                    continue
                hits = []
                for ref in rec.get('data_references') or []:
                    try:
                        target = int(str(ref.get('to_addr')), 16)
                    except (TypeError, ValueError):
                        continue
                    if lo <= target <= hi:
                        hits.append((ref.get('ref_type'), ref.get('to_addr')))
                if hits:
                    rows.append((rec.get('name') or f'FUN_{entry:08x}', entry, hits))
        return rows

    def canonical_function(name: str) -> dict:
        with (REPO / 'data/generated/decompilations.jsonl').open() as f:
            for line in f:
                rec = json.loads(line)
                if rec.get('record') == 'function' and rec.get('name') == name:
                    return rec
        raise AssertionError(f'canonical function missing: {name}')
    print('== KEYLESS-001: security roots ==')
    for image_name, image in IMAGES.items():
        for label, secret, expected_off in (('payload-build', PAYLOAD_BUILD_SECRET, 49112), ('boot-SA', BOOT_SA_SECRET, 49128), ('application-SA', APP_SA_SECRET, 133184)):
            check(f'{image_name}: {label} root occurs exactly once at 0x{expected_off:X}', find_all(image, secret) == [expected_off])
    print('== KEYLESS-002: table and handler implementation transfer ==')
    sienna_table = uds_table(SIENNA, BOOT_UDS_TABLE['sienna'])
    check('Sienna boot UDS table has exactly 20 complete records', len(sienna_table) == 20)
    check('Sienna boot UDS SID order is pinned', [r[0] for r in sienna_table] == EXPECTED_SIDS)
    check('Sienna boot UDS policy-byte order is pinned', [r[1] for r in sienna_table] == EXPECTED_POLICIES)
    for image_name, image in FOREIGN.items():
        table = uds_table(image, BOOT_UDS_TABLE['corolla'])
        check(f'{image_name}: 20 complete boot UDS records', len(table) == 20)
        check(f'{image_name}: table is exact Sienna table with handler pointers shifted -0x1C', table == [shift_record(r, COROLLA_SHIFT) for r in sienna_table])
        for body_name, entry, size in UDS_HANDLER_BODIES + CRITICAL_BOOT_BODIES:
            check(f'{image_name}: {body_name} complete body transfers at -0x1C', exact_shifted_body(image, entry, size))
    print('== KEYLESS-003: RequestDownload is SA-gated; wrap guard is defense-in-depth ==')
    request_download = canonical_function('uds_request_download')
    check('canonical RequestDownload reads boot SA state FEBF2B0F at 0x5EFC', any((ref.get('from_addr') == '0x00005efc' and ref.get('ref_type') == 'READ' and (ref.get('to_addr') == '0xfebf2b0f') for ref in request_download.get('data_references') or [])))
    SA_GATE = bytes.fromhex('a49f0f93629ac20520363300')
    check('Sienna RequestDownload SA gate bytes pinned at 0x5EFC', SIENNA[24316:24328] == SA_GATE)
    for image_name, image in FOREIGN.items():
        target = 24316 + COROLLA_SHIFT
        check(f'{image_name}: RequestDownload SA gate transfers at 0x{target:X}', image[target:target + len(SA_GATE)] == SA_GATE)
    WRAP_GUARD = bytes.fromhex('c6390796fffff231ab1d')
    WRAP_GUARD_OFFSETS = {'sienna-8965B4512000': [13018, 13088], 'albinoelephant-8965H1202000': [12990, 13060], 'spanconstant-8965F1208000': [12990, 13060]}
    for image_name, expected in WRAP_GUARD_OFFSETS.items():
        image = IMAGES[image_name]
        found = [off for off in range(12288, 16384) if image[off:off + len(WRAP_GUARD)] == WRAP_GUARD]
        check(f'{image_name}: unsigned interval-wrap guard sites are exact', found == expected)
    print('== KEYLESS-004: exact application XCP route descriptor absent from boot ==')
    for image_name, image in IMAGES.items():
        hits = []
        for off in range(0, 131072 - 3):
            for endian in ('<', '>'):
                value = struct.unpack_from(endian + 'I', image, off)[0]
                for ident in XCP_ROUTE_IDS:
                    if value == XCP_DESCRIPTOR_TAG + (ident << 18) + XCP_DESCRIPTOR_ATTR:
                        hits.append((off, endian, ident))
        check(f'{image_name}: no exact packed 0x7F7/0x7F8 application descriptor in boot', hits == [])
    print('== KEYLESS-005: recovered boot auth state does not overlap XCP window ==')
    check('boot GP lies numerically inside XCP write window', XCP_WINDOW[0] <= BOOT_GP <= XCP_WINDOW[1])
    for label, addr in SECURITY_STATE.items():
        check(f'{label} is below XCP write window', addr < XCP_WINDOW[0])
    refs = canonical_sienna_boot_window_refs()
    check('Sienna boot direct-reference census is only zero-trip startup WRITE to FEBF7C00', refs == [('FUN_00001404', 5124, [('WRITE', '0xfebf7c00')])])
    STARTUP_ENTRY = 5124
    STARTUP_SIZE = 116
    STARTUP_TARGET = STARTUP_ENTRY + COROLLA_SHIFT
    ZERO_TRIP_LOOP = bytes.fromhex('3e06007cbffeb505010544f221060070befee1f1a1fd')
    check('Sienna zero-trip clear-shape bytes pinned', SIENNA[5158:5180] == ZERO_TRIP_LOOP)
    check('zero-trip loop direction is false', not 4273961984 < 4273893376)
    for image_name, image in FOREIGN.items():
        check(f'{image_name}: complete startup body transfers at -0x1C', SIENNA[STARTUP_ENTRY:STARTUP_ENTRY + STARTUP_SIZE] == image[STARTUP_TARGET:STARTUP_TARGET + STARTUP_SIZE])
    print('== KEYLESS-006: application SA root is self-disclosing before SA ==')
    for image_name, image in IMAGES.items():
        copy_entry, copy_base, rmba_obj, xcp_excl_base = APP_INFO_COPY[image_name]
        mirror = copy_base + APP_SA_OFFSET_IN_COPY
        body = image[copy_entry:copy_entry + 32]
        check(f'{image_name}: app-info copier has pinned 32-byte loop shape', len(body) == 32 and body[:14] == bytes.fromhex('000a409e0200c199939f11083e06') and (body[16:] == bytes.fromhex('bffec1f1410a0106c0ff809bb9f57f00')) and (body[14:16] == struct.pack('<H', copy_base & 65535)))
        check(f'{image_name}: app-info source ends with application-SA root', image[APP_INFO_SOURCE + APP_SA_OFFSET_IN_COPY:APP_INFO_SOURCE + APP_SA_OFFSET_IN_COPY + 16] == APP_SA_SECRET)
        check(f'{image_name}: startup copy places application-SA root at 0x{mirror:08X}', APP_INFO_SOURCE + APP_SA_OFFSET_IN_COPY == 133184 and mirror == (4273961952 if image_name.startswith('sienna') else 4273961856))
        callback, sec_ptr, session_ptr, sub_ptr = struct.unpack_from('<IIII', image, rmba_obj)
        sid, has_sub, sec_count, session_count, sub_count = image[rmba_obj + 16:rmba_obj + 21]
        check(f'{image_name}: SID 0x23 RMBA service object has no SA policy', sid == 35 and has_sub == 0 and (sec_ptr == 0) and (sec_count == 0) and (session_count == 1) and (image[session_ptr] == 3) and (sub_ptr == 0) and (sub_count == 0) and (callback != 0))
        exclusions = [struct.unpack_from('<II', image, xcp_excl_base + i * 8) for i in range(5)]
        check(f'{image_name}: 16-byte application-SA mirror is outside LocalRAM read exclusions', not overlaps(mirror, 16, exclusions))
    for image_name, image in IMAGES.items():
        if image_name.startswith('sienna'):
            count_off, map_off, cb_off, short_upload = (142289, 142340, 142384, 530990)
        else:
            count_off, map_off, cb_off, short_upload = (141845, 141896, 141940, 507434)
        command_map = image[map_off:map_off + image[count_off]]
        callbacks = [struct.unpack_from('<I', image, cb_off + i * 4)[0] for i in range(18)]
        f4_index = command_map[255 - 244]
        check(f'{image_name}: XCP SHORT_UPLOAD remains configured without GET_SEED/UNLOCK', command_map[255 - 248] == 0 and command_map[255 - 247] == 0 and (f4_index != 0) and (callbacks[f4_index] == short_upload))
    print('== KEYLESS-007: retained TransferData context is reset before boot DCM ==')
    transfer_data = canonical_function('uds_transfer_data')
    transfer_init = canonical_function('FUN_00005086')
    boot_diag_enable = canonical_function('FUN_000069d2')
    boot_diag_dispatch = canonical_function('FUN_00006a22')
    boot_failure_loop = canonical_function('boot_failure_main_loop')
    boot_failure_init = canonical_function('FUN_00001338')
    live_entry = canonical_function('FUN_0000148e')
    check('Sienna TransferData dispatches only from transfer-state FEBF2B13', any((ref.get('from_addr') == '0x00004dc0' and ref.get('ref_type') == 'READ' and (ref.get('to_addr') == '0xfebf2b13') for ref in transfer_data.get('data_references') or [])))
    check('Sienna diagnostic init clears transfer-state FEBF2B13', any((ref.get('ref_type') == 'WRITE' and ref.get('to_addr') == '0xfebf2b13' for ref in transfer_init.get('data_references') or [])) and 'DAT_febf2b13 = 0;' in transfer_init.get('decompiled_c', ''))
    check('Sienna diagnostic init re-locks boot SA and clears authorization bits', all((token in transfer_init.get('decompiled_c', '') for token in ("uds_security_access_state = '\\x01';", 'DAT_febf2b11 = 0;', "payload_did_crypto_ready = '\\0';", 'DAT_febf2b17 = 0;'))))
    check('live 0x9F00 path enters failure/programming main-loop init', 'boot_failure_main_loop();' in live_entry.get('decompiled_c', '') and 'FUN_00001338();' in boot_failure_loop.get('decompiled_c', '') and ('FUN_00000770();' in boot_failure_init.get('decompiled_c', '')))
    check('boot diagnostic root enables and then runs state initializer', 'DAT_febf2bd0 = 1;' in boot_diag_enable.get('decompiled_c', '') and 'FUN_00005086();' in boot_diag_dispatch.get('decompiled_c', ''))
    check('fixed live-handoff record requests programming session', SIENNA[203028:203028 + 20] == struct.pack('<IIIII', 0, 1953, 0, 0, 2))
    for image_name, image in FOREIGN.items():
        check(f'{image_name}: TransferData complete body transfers at -0x1C for context-bypass audit', exact_shifted_body(image, 19898, 56))
    print('== KEYLESS-008: live handoff cannot inherit attacker-selected CTBP ==')
    CTBP_ZERO = bytes.fromhex('e0a72000')
    for image_name, image in IMAGES.items():
        hits = [off for off in range(len(image) - len(CTBP_ZERO) + 1) if image[off:off + len(CTBP_ZERO)] == CTBP_ZERO]
        check(f'{image_name}: CTBP-zero instruction occurs exactly once at reset startup ({[hex(x) for x in hits]})', hits == [606])
        check(f'{image_name}: live 0x9F00 handoff does not rewrite CTBP', CTBP_ZERO not in image[40704:40804])
    check('Sienna boot CALLT 0x22 is pinned at 0x1D5C', SIENNA[7516:7518] == bytes.fromhex('2202'))
    check('Sienna CTBP=0 table entry 0x22 resolves to fixed 0x1E1E', struct.unpack_from('<H', SIENNA, 68)[0] == 7710)
    for image_name, image in FOREIGN.items():
        check(f'{image_name}: relocated boot CALLT 0x22 is pinned at 0x1D40', image[7488:7490] == bytes.fromhex('2202'))
        check(f'{image_name}: CTBP=0 table target relocates exactly -0x1C', struct.unpack_from('<H', image, 68)[0] == 7682)
    print('== KEYLESS-009: RequestDownload pre-SA side effects cannot arm a transfer ==')
    request_download = canonical_function('uds_request_download')
    wdbi = canonical_function('uds_write_data_by_identifier')
    boot_init = canonical_function('FUN_00005086')
    check('Sienna RequestDownload reads payload-ready before final SA gate', any((ref.get('from_addr') == '0x00005e4a' and ref.get('to_addr') == '0xfebf2b16' for ref in request_download.get('data_references') or [])) and any((ref.get('from_addr') == '0x00005efc' and ref.get('to_addr') == '0xfebf2b0f' for ref in request_download.get('data_references') or [])))
    check('Sienna RequestDownload can write transfer-status before final SA gate', any((ref.get('from_addr') == '0x00005e60' and ref.get('to_addr') == '0xfebf2b17' for ref in request_download.get('data_references') or [])))
    check('Sienna WDBI SA gate precedes its payload-ready write', any((ref.get('from_addr') == '0x000049c6' and ref.get('to_addr') == '0xfebf2b0f' for ref in wdbi.get('data_references') or [])) and any((ref.get('from_addr') == '0x00004a76' and ref.get('to_addr') == '0xfebf2b16' for ref in wdbi.get('data_references') or [])))
    check('Sienna boot init clears payload-ready and transfer-status', "payload_did_crypto_ready = '\\0';" in boot_init.get('decompiled_c', '') and 'DAT_febf2b17 = 0;' in boot_init.get('decompiled_c', ''))
    for addr, target in (('0x00005f1e', '0xfebf2b00'), ('0x00005f22', '0xfebf2b04')):
        check(f'Sienna RequestDownload commits {target} only after SA gate', any((ref.get('from_addr') == addr and ref.get('ref_type') == 'WRITE' and (ref.get('to_addr') == target) for ref in request_download.get('data_references') or [])))
    for image_name, image in FOREIGN.items():
        check(f'{image_name}: complete RequestDownload body carries the same ordering at -0x1C', exact_shifted_body(image, 23912, 468))
        check(f'{image_name}: complete WDBI body carries the same payload-ready prerequisite at -0x1C', exact_shifted_body(image, 18760, 328))
    print('== KEYLESS-012: recovered application SA only adds the BA F7 local gate ==')
    app_sec_counts = [SIENNA[155176 + i * 24 + 18] for i in range(17)]
    check('Sienna primary application Dcm service security counts are all zero', app_sec_counts == [0] * 17)
    check('Sienna BA service itself has no Dcm-level SA requirement', SIENNA[155176 + 16 * 24 + 16] == 186 and SIENNA[155176 + 16 * 24 + 18] == 0)
    check('Sienna BA F7 local helper tests application-SA level-2 mask bit 0x02', SIENNA[216482:216486] == bytes.fromhex('ca9e0200'))
    check('Sienna BA F7/BAENA token is pinned', SIENNA[135350:135355] == b'BAENA')
    for image_name, image in FOREIGN.items():
        check(f'{image_name}: BAENA token remains present at target-native location', image[135288:135293] == b'BAENA')
        check(f'{image_name}: BA F7 target-native gate retains level-2 bit-test tail', image[199044:199060] == SIENNA[216478:216494])
_section_keyless_exec_surface()
print()

print("== keyless reset entry ==")
def _section_keyless_reset_entry():
    import json
    ROOT = REPO_ROOT
    CF = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    CORPUS = ROOT / 'data/generated/decompilations.jsonl'
    funcs = {}
    with CORPUS.open() as f:
        for line in f:
            r = json.loads(line)
            if r.get('record') == 'function' and r.get('entry_addr'):
                funcs[int(r['entry_addr'], 16)] = r

    def c(entry):
        return funcs[entry].get('decompiled_c', '')
    print('== triple-copy reset latch ==')
    text = c(400122)
    check('reset-latch setter writes raw/XOR55/XORAA triplet', 'Ramffc0a000 = param_1;' in text and '^ 0x55555555' in text and ('^ 0xaaaaaaaa' in text))
    for entry, val in [(405006, '0x3e3e3e3e'), (407904, '0x6d6d6d6d'), (412740, '0xd6d6d6d6')]:
        check(f'known latch producer 0x{entry:X} supplies fixed sentinel {val}', f'FUN_00061afa({val});' in c(entry))
    check('live application-to-boot handoff zeros all four latch words before 0x9F00', all((s in c(413384) for s in ['Ramffc0a000 = 0;', 'Ramffc0a004 = 0;', 'Ramffc0a008 = 0;', 'Ramffc0a00c = 0;', 'FUN_00009f00(&DAT_00031914);'])))
    print('\n== reset-mode translation has fixed callers ==')
    tr = c(395376)
    for src, dst in [('param_1 == -1', 'uVar1 = 0;'), ("param_1 == '\\x01'", 'uVar1 = 0x50;'), ("param_1 == '\\x02'", 'uVar1 = 0x3d;'), ("param_1 != '\\0'", 'return 0x11;'), ('uVar1 = 0x73;', 'FUN_000607de(uVar1);')]:
        check(f'reset translator pins {src}', src in tr and dst in tr)
    caller_entries = set()
    for e, r in funcs.items():
        if e != 395376 and 'FUN_00060870(' in r.get('decompiled_c', ''):
            caller_entries.add(e)
    check('reset translator has only three canonical callers', caller_entries == {395434, 403842, 404210}, repr(sorted(caller_entries)))
    check('62AF2 calls translator with fixed mode 1', 'FUN_00060870(1);' in c(404210))
    check('system_hard_reset calls translator with fixed FF mode', 'FUN_00060870(0xff);' in c(395434))
    print('\n== startup coordinator is internal and fixed-policy ==')
    coord_callers = {e for e, r in funcs.items() if e != 404422 and 'FUN_00062bc6(' in r.get('decompiled_c', '')}
    check('reset/startup coordinator has one canonical caller', len(coord_callers) == 1, repr(sorted(coord_callers)))
    coord = c(404422)
    for fixed in ('FUN_000628ee(0x11);', 'FUN_000628ee(0x22);', 'FUN_000628ee(0x33);', 'FUN_000628ee(0x44);'):
        check(f'coordinator uses fixed action {fixed}', fixed in coord)
    check('coordinator does not reference application XCP window', 'febf7c' not in coord.lower() and 'febffb' not in coord.lower())
    print('\n== power-on validation remains data/status selection, not PC selection ==')
    restore = c(400152)
    check('reset-latch consumer copies all four words to FEBE status state', all((x in restore for x in ('DAT_febe39b4 = Ramffc0a000;', 'DAT_febe8d90 = Ramffc0a004;', 'DAT_febe8da4 = Ramffc0a008;', 'DAT_febe39b8 = Ramffc0a00c;'))))
    check('reset-latch consumer then overwrites hardware words with fixed sentinels', all((x in restore for x in ('Ramffc0a000 = 0xa5a5a5a5;', 'Ramffc0a004 = 0xf0f0f0f0;', 'Ramffc0a008 = 0xf0f0f0f;', 'Ramffc0a00c = 0;'))))
    check('live 9F00 handoff remains direct CodeFlash call, not latch-derived target', CF[413420:413424] == bytes.fromhex('baff1450') and 'FUN_00009f00' in c(413384))
_section_keyless_reset_entry()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
