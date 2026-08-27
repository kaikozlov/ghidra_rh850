#!/usr/bin/env python3
"""Raw-firmware proof for the keyless-execution surface.

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

print("== keyless application event formatter ==")
def _section_keyless_application_event_formatter():
    import hashlib, json, struct, subprocess, sys, tempfile
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    S = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    H = (ROOT / 'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin').read_bytes()[:1048576]
    F = (ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin').read_bytes()[:1048576]
    EVP = ROOT / 'data/generated/corolla_8965H1202000_keyless_event_formatter_decompiler_evidence.json'
    EV = json.loads(EVP.read_text())
    ARTP = ROOT / 'data/generated/corolla_8965H1202000_keyless_event_formatter.json'
    ART = json.loads(ARTP.read_text())
    BUILD = ROOT / 'tools/build_corolla_h_keyless_event_formatter.py'
    SC = {}
    for line in (ROOT / 'data/generated/decompilations.jsonl').read_text().splitlines():
        r = json.loads(line)
        if r.get('entry_addr'):
            SC[int(r['entry_addr'], 16)] = r
    HE = {int(x['entry'], 16): x for x in EV['functions']}

    def sha(b):
        return hashlib.sha256(b).hexdigest()

    def bounds(img, desc_base, count, event_base):
        rows = []
        for i in range(count):
            a = desc_base + i * 24
            rows.append((struct.unpack_from('<H', img, a + 20)[0], img[a + 22]))
        vals = []
        for i in range(64):
            a = event_base + i * 8
            eid = struct.unpack_from('<h', img, a)[0]
            mask = struct.unpack_from('<H', img, a + 2)[0]
            if not mask:
                continue
            selected = [ln for m, ln in rows if m & mask]
            vals.append((3 + sum((3 + ln for ln in selected)), eid, mask, len(selected), sum(selected)))
        return (rows, vals)
    print('== deterministic report regeneration ==')
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'event.json'
        r = subprocess.run([sys.executable, str(BUILD), '--out', str(out)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        check('event-formatter builder exits', r.returncode == 0, r.stdout[-500:] if r.returncode else '')
        check('event-formatter report regenerates exactly', r.returncode == 0 and out.read_bytes() == ARTP.read_bytes())
    check('three target-native role mappings are explicit', ART['role_closure_count'] == 3 and {(x['reference_entry'], x['target_entry']) for x in ART['role_closure']} == {('0x00054910', '0x00050038'), ('0x000549FA', '0x00050122'), ('0x00054A7E', '0x000501A6')})
    print('== target-native H evidence ==')
    check('six H functions are compacted', EV['function_count'] == 6 == len(HE))
    check('H image hash pinned', EV['image']['codeflash_sha256'] == sha(H))
    check('all H raw bodies validate', all((sha(H[a:a + x['body_size']]) == x['body_sha256'] for a, x in HE.items())))
    check('all H decompiler hashes validate', all((sha(x['decompiled_c'].encode()) == x['decompiled_c_sha256'] for x in HE.values())))
    inner_s = SC[346384]['decompiled_c']
    wrap_s = SC[346618]['decompiled_c']
    sib_s = SC[346750]['decompiled_c']
    worker_s = SC[577412]['decompiled_c']
    inner_h = HE[327736]['decompiled_c']
    wrap_h = HE[327970]['decompiled_c']
    sib_h = HE[328102]['decompiled_c']
    worker_h = HE[553860]['decompiled_c']
    helper_h = HE[331024]['decompiled_c']
    print('\n== unchecked formatter structure ==')
    for tag, c in [('Sienna', inner_s), ('Corolla H', inner_h)]:
        check(f'{tag} formatter advances output by descriptor length without capacity operand', 'iVar9 = iVar9 + 3 + (uint)*(byte *)(iVar1 + 0x16);' in c and 'param_4 & 0xffff' not in c)
    for tag, c in [('Sienna', wrap_s), ('Corolla H', wrap_h)]:
        check(f'{tag} wrapper can append both snapshot banks', c.count('param_1,param_2') >= 2 and c.count('param_3') >= 2)
        check(f'{tag} wrapper checks total against capacity only after formatter calls', c.rfind('param_4 & 0xffff') > c.rfind('param_1,param_2'))
    for tag, c in [('Sienna', sib_s), ('Corolla H', sib_h)]:
        check(f'{tag} sibling formatter has an in-loop capacity check', 'param_4 & 0xffff' in c and '+ uVar7 + 3' in c)
    print('\n== configured reachable output bounds ==')
    srows, svals = bounds(S, 173316, 75, 175376)
    hrows, hvals = bounds(H, 171804, 78, 173936)
    frows, fvals = bounds(F, 171804, 78, 173936)
    check('Sienna helper count is 75', '*param_1 = 0x4b;' in SC[349672]['decompiled_c'])
    check('H helper count is 78 and table is 0x29F1C', '*param_1 = 0x4e;' in helper_h and 'PTR_DAT_00029f1c' in helper_h)
    check('H/F descriptor tables are byte-identical', H[171804:171804 + 78 * 24] == F[171804:171804 + 78 * 24])
    check('H/F event maps are byte-identical', H[173936:174448] == F[173936:174448])
    check('Sienna reachable one-bank maximum is 207', max((x[0] for x in svals)) == 207, str(sorted(svals, reverse=True)[:1]))
    check('H reachable one-bank maximum is 202', max((x[0] for x in hvals)) == 202, str(sorted(hvals, reverse=True)[:1]))
    check('F reachable one-bank maximum is also 202', max((x[0] for x in fvals)) == 202)
    check('Sienna two-bank conservative maximum is 414', 2 * max((x[0] for x in svals)) == 414)
    check('H/F two-bank conservative maximum is 404', 2 * max((x[0] for x in hvals)) == 404 == 2 * max((x[0] for x in fvals)))
    print('\n== staging capacity and portability ==')
    check('Sienna AB worker resets staging capacity to 0x300', 'DAT_febf45d6 = 0x300;' in worker_s)
    check('H AB worker resets staging capacity to 0x300', '_DAT_febf45d6 = 0x300;' in worker_h)
    check('Sienna configured headroom is 354 bytes', 768 - 2 * max((x[0] for x in svals)) == 354)
    check('H/F configured headroom is 364 bytes', 768 - 2 * max((x[0] for x in hvals)) == 364)
    check('F carries H formatter/wrapper/worker bytes exactly', F[327736:327736 + 234] == H[327736:327736 + 234] and F[327970:327970 + 90] == H[327970:327970 + 90] and (F[553860:553860 + 364] == H[553860:553860 + 364]))
    check('tracked configurations stay below staging capacity', 414 < 768 and 404 < 768)
    check('generated report publishes exact S/H/F maxima', ART['bounds']['sienna']['conservative_two_bank_max'] == 414 and ART['bounds']['corolla_h']['conservative_two_bank_max'] == 404 and (ART['bounds']['corolla_f']['conservative_two_bank_max'] == 404))
    check('generated report preserves configuration-dependent safety boundary', ART['static_conclusion']['configuration_dependent_safety'] and (not ART['static_conclusion']['tracked_images_overflow']) and ('not a global static-attack absence claim' in ART['static_conclusion']['boundary']))
_section_keyless_application_event_formatter()
print()

print("== keyless boot variant residuals ==")
def _section_keyless_boot_variant_residuals():
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    S = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    H = (ROOT / 'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin').read_bytes()
    F = (ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin').read_bytes()
    check('Corolla H/F boot bytes are identical through 0xA003', H[:40964] == F[:40964])
    EXACT = [('warm reset', 432, 432, 66), ('EIC init', 6088, 6058, 1014), ('TAUJ0 init', 7200, 7170, 64), ('TAUJ1 init', 7264, 7234, 64), ('TAUJ sequencer', 7328, 7298, 72)]
    for name, sa, ha, size in EXACT:
        check(f'{name} body is byte-exact at residual placement', S[sa:sa + size] == H[ha:ha + size])
    check('default exception thunk target relinks 0x1E1E -> 0x1E02', S[48:60] == bytes.fromhex('1f00e0061e1e000000000000') and H[48:60] == bytes.fromhex('1f00e006021e000000000000'))
    check('old/new default-exception targets carry the same 12-byte stub', S[7710:7722] == H[7682:7694])
    check('cold-start TP immediate moves 0x869C -> 0x867C', S[504:510] == bytes.fromhex('25069c860000') and H[504:510] == bytes.fromhex('25067c860000'))
    for off in (510, 528, 546):
        check(f'cold-start PSW-family immediate at 0x{off:X} clears CU0', S[off:off + 6] == bytes.fromhex('2a0620800100') and H[off:off + 6] == bytes.fromhex('2a0620800000'))
    check('FPIPR changes from r10=0x10 to r0', S[1166:1176] == bytes.fromhex('20561000ea3f20081c00') and H[1166:1172] == bytes.fromhex('e03f20081c00'))
    check('H cold-start body is exactly 28 bytes shorter before dominant relocation', S[1668:1858] == H[1640:1830])
    check('CSIH TX base remaps by 0x2000', S[5672:5676] == bytes.fromhex('490840b0') and H[5644:5648] == bytes.fromhex('490800b0'))
    check('CSIH init saves two bytes with movhi FFD8', H[5862:5866] == bytes.fromhex('40f6d8ff'))
    check('-0x1E island closes with one zero pad before dominant -0x1C resumes', H[7382:7384] == b'\x00\x00' and S[7410:7412] != b'\x00\x00')
    for name, sa, ha in (('runtime init', 4920, 4892), ('CSIH TX', 5670, 5642), ('CSIH RX', 5788, 5760), ('CSIH init', 5874, 5846), ('EIC mask helper', 7102, 7072), ('timer trampoline', 7400, 7370), ('TAUJ ISR', 7748, 7720), ('RAM table copier', 13796, 13768), ('EIC helper A', 15006, 14978), ('EIC helper B', 15034, 15006)):
        check(f'{name} retains expected instruction-family prologue', S[sa:sa + 4] == H[ha:ha + 4])
    check('RAM table copier source table relocates 0x8370 -> 0x8350 with identical 0x32C bytes', S[33648:34460] == H[33616:34428])
    check('0x9F00 handoff stays at the same VA and same fixed-state prefix', S[40704:40738] == H[40704:40738])
    check('0x9F00 handoff PSW clears CU0 on H/F', S[40738:40744] == bytes.fromhex('2a0620800100') and H[40738:40744] == bytes.fromhex('2a0620800000'))
    check('0x9F00 handoff TP moves 0x869C -> 0x867C', S[40784:40790] == bytes.fromhex('25069c860000') and H[40784:40790] == bytes.fromhex('25067c860000'))
    check('0x9F00 direct call relinks 0x148E -> 0x1472', S[40798:40802] == bytes.fromhex('bfff3075') and H[40798:40802] == bytes.fromhex('bfff1475'))
_section_keyless_boot_variant_residuals()
print()

print("== keyless exec surface ==")
def _section_keyless_exec_surface():
    import json
    import struct
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
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

print("== keyless application diagnostic transport ==")
def _section_keyless_application_diagnostic_transport():
    import json, struct
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    FW = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    CORP = ROOT / 'data/generated/decompilations.jsonl'
    WANTED = {499174, 499674, 590760, 590908, 592150, 592316, 598226, 598936}
    by = {}
    for line in CORP.read_text().splitlines():
        r = json.loads(line)
        if r.get('entry_addr'):
            a = int(r['entry_addr'], 16)
            if a in WANTED:
                by[a] = r

    def u16(a):
        return struct.unpack_from('<H', FW, a)[0]

    def u32(a):
        return struct.unpack_from('<I', FW, a)[0]
    print('== CanTp framing and PduR routing ==')
    check('all required canonical functions are in the decompiler corpus', set(by) == WANTED, str(sorted(WANTED - set(by))))
    check('CanTp first-frame protocol ceiling is 0xFFF', u16(142624) == 4095, hex(u16(142624)))
    tp_ids = [u16(142526 + i * 32 + 8) for i in range(3)]
    check('three diagnostic CanTp connections route PDU IDs 0x802/803/804', tp_ids == [2050, 2051, 2052], str([hex(x) for x in tp_ids]))
    callbacks = [u32(137356 + 4 * i) for i in range(6)]
    check('PduR callback vector is exact', callbacks == [590760, 590908, 592316, 591036, 592672, 592944], str([hex(x) for x in callbacks]))
    check('generic 0x90916 copy belongs to CopyTxData, not receive reassembly', 'FUN_00090916' in by[592316]['decompiled_c'] and callbacks[2] == 592316)
    print('\n== DCM receive allocation ==')
    slots = [(u16(155748 + i * 8), u32(155748 + i * 8 + 4)) for i in range(3)]
    check('DCM has three fixed 256-byte request buffers', slots == [(256, 4273886761), (256, 4273887017), (256, 4273887273)], str([(hex(a), hex(b)) for a, b in slots]))
    check('DCM local PDU IDs are exactly 2/3/4', [u16(155846 + i * 12) for i in range(3)] == [2, 3, 4])
    sor = by[590760]['decompiled_c']
    check('StartOfReception rejects total length above configured slot capacity', '(param_3 & 0xffff) <=' in sor and 'return 3;' in sor)
    check('StartOfReception recognizes exactly three slots', 'if (2 < uVar4)' in sor)
    print('\n== segmented-copy bounds ==')
    copyrx = by[590908]['decompiled_c']
    copy = by[598226]['decompiled_c']
    rem = by[598936]['decompiled_c']
    cf = by[499674]['decompiled_c']
    ff = by[499174]['decompiled_c']
    check('CopyRxData obtains remaining capacity before copying', 'FUN_00092398' in copyrx and 'FUN_000920d2' in copyrx and (copyrx.index('FUN_00092398') < copyrx.index('FUN_000920d2')))
    check('CopyRxData requires chunk length <= remaining capacity', '*(ushort *)(param_2 + 4) <= uVar4' in copyrx)
    check('remaining-capacity getter reads the per-slot remaining field', 'DAT_febe59d0' in rem)
    check('copy helper advances destination pointer one byte per copied byte', '*(undefined1 *)*piVar1 = uVar3;' in copy and '*piVar1 = *piVar1 + 1;' in copy)
    check('copy helper decrements remaining capacity by copied length', 'DAT_febe59d0' in copy and '= sVar2 - sVar4;' in copy)
    check('CanTp CF path clips payload chunk to remaining TP length', 'if (uVar6 < uVar9)' in cf and 'uStack_24 = uVar6;' in cf and ('uVar9 = uVar9 - uStack_24;' in cf))
    check('CanTp FF parser enforces 0x22D20 configured ceiling', 'DAT_00022d20 < uVar2' in ff)
    check('protocol max is larger than each DCM allocation, making DCM check material', 4095 > 256)
_section_keyless_application_diagnostic_transport()
print()

print("== keyless reset entry ==")
def _section_keyless_reset_entry():
    import json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
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

print("== keyless exec portability ==")
def _section_keyless_exec_portability():
    import json, struct
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
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
    print('\n== field-acquisition provenance ==')
    h_manifest = (ROOT / 'community/albinoelephant/raw-20260818/MANIFEST.txt').read_text()
    check('Albino manifest says dump used public payload-build secret', 'public payload-build secret' in h_manifest)
    check('Albino manifest rules out glitch/bench/module removal for this acquisition', 'No glitching, no bench work, no module removal.' in h_manifest)
    span_log = json.loads((ROOT / 'community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/security_access_log.json').read_text())
    attempts = next(iter(span_log['ecus'].values()))['attempts']
    accepted = {a['caller'] for a in attempts if a['outcome'] == 'accepted' and a['call'] == 'send_key'}
    for caller in ('dump_range:codeflash', 'dump_range:local_ram_pe1', 'dump_range:local_ram_self', 'dump_range:dataflash'):
        check(f'Span log records accepted SecurityAccess for {caller}', caller in accepted)
    profiles = json.loads((ROOT / 'data/variant_bootstrap_profiles.json').read_text())['profiles']
    check('exactly one tracked authenticated-RAM bootstrap profile', len(profiles) == 1)
    profile = profiles[0]
    check('bootstrap profile pins FEBF0000/0x1000 staging', profile['authenticated_download_base'] == '0xFEBF0000' and profile['authenticated_download_size'] == '0x1000')
    check('bootstrap profile pins 10F0 verify and FF00 execute', profile['verify_routine'] == '0x10F0' and profile['execute_routine'] == '0xFF00')
    evidence = {e['software_id']: e for e in profile['evidence']}
    for sw, manifest in [('8965H1202000', 'community/albinoelephant/raw-20260818/MANIFEST.txt'), ('8965F1208000', 'community/spanconstant/raw-20260821/MANIFEST.txt')]:
        e = evidence[sw]
        check(f'{sw} profile records target-built range-payload execution', e['fixture_transfer'] == 'target-built-range-payloads-observed' and e['grade'] == 'observed')
        check(f'{sw} profile provenance names retained manifest', manifest in e['source'])
_section_keyless_exec_portability()
print()

print("== keyless xcp composition ==")
def _section_keyless_xcp_composition():
    import struct
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
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

print("== keyless application pc surfaces ==")
def _section_keyless_application_pc_surfaces():
    import json
    import struct
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    CF = (ROOT / 'firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
    CORPUS = ROOT / 'data/generated/decompilations.jsonl'
    XCP_LO, XCP_HI = (4273961984, 4273994751)

    def u32(off: int) -> int:
        return struct.unpack_from('<I', CF, off)[0]
    funcs: dict[int, dict] = {}
    with CORPUS.open() as f:
        for line in f:
            rec = json.loads(line)
            if rec.get('record') == 'function' and rec.get('entry_addr'):
                funcs[int(rec['entry_addr'], 16)] = rec

    def refs(entry: int) -> set[tuple[int, str, int]]:
        out = set()
        for r in funcs[entry].get('data_references') or []:
            try:
                out.add((int(r['from_addr'], 16), str(r['ref_type']), int(r['to_addr'], 16)))
            except (KeyError, TypeError, ValueError):
                pass
        return out
    print('== exception-return and saved-PC surfaces ==')
    return_sites = {131346: bytes.fromhex('e0074801'), 412618: bytes.fromhex('e0074a01'), 459490: bytes.fromhex('e0074801'), 459718: bytes.fromhex('e0074801'), 459890: bytes.fromhex('e0074801'), 460062: bytes.fromhex('e0074801'), 461312: bytes.fromhex('e0074801'), 461744: bytes.fromhex('e0074801')}
    for off, op in return_sites.items():
        check(f'exception return opcode pinned at 0x{off:X}', CF[off:off + 4] == op)
    check('return census has seven EIRET and one FERET', list(return_sites.values()).count(bytes.fromhex('e0074801')) == 7 and list(return_sites.values()).count(bytes.fromhex('e0074a01')) == 1)
    check('common restore reloads EIPC from RAM frame', CF[459474:459494] == bytes.fromhex('0a650c6de16f2000ec072000ed0f2000266d2465100d0ef53fff0000df1923ff0100441ae0074801')[-20:])
    for name, entry, stack_imm in (('TAUJ0', 459552, bytes.fromhex('4036befe261e0008')), ('TAUJ1', 459722, bytes.fromhex('4036befe261e0010')), ('TAUJ2', 459894, bytes.fromhex('4036befe261e0018'))):
        body = CF[entry:entry + 172]
        check(f'{name} saves EIPC at frame+0x14', bytes.fromhex('e057400063571500') in body)
        check(f'{name} work-stack switch is fixed FEBE address', stack_imm in body)
    check('application foreground SP is fixed FEBE2000', CF[460104:460110] == bytes.fromhex('23060020befe'))
    check('fast-exception handler saves FEPC into its RAM frame', CF[412486:412498] == bytes.fromhex('e25740000a56040063570d00'))
    check('fast-exception handler restores FEPC before FERET', CF[412602:412622] == bytes.fromhex('23570d00ea17200023571100031e1400e0074a01'))
    check('known fixed application stack anchors lie below XCP window', all((v < XCP_LO for v in (4273866752, 4273868800, 4273870848, 4273872896))))
    check('canonical function entries do not lie in XCP window', not any((XCP_LO <= a <= XCP_HI for a in funcs)))
    print('\n== near-window callback FEBF7704 ==')
    cb = 4273960708
    check('callback cell is exactly 0x4FC below XCP lower bound', XCP_LO - cb == 1276)
    cb_refs = {(e, fr, typ, to) for e in funcs for fr, typ, to in refs(e) if to == cb}
    check('callback cell has exactly one canonical read and one write globally', cb_refs == {(470602, 470610, 'READ', cb), (470622, 470642, 'WRITE', cb)}, repr(sorted(cb_refs)))
    check('callback setter embeds both fixed targets', (470642, 'DATA', 480868) in refs(470622) and (470642, 'DATA', 481114) in refs(470622))
    check('callback consumer performs computed JARL after loading FEBF7704', CF[470602:470618] == bytes.fromhex('8007610040eebffe3def0577fdc760f9'))
    check('setter selects only fixed 75664/7575A targets', CF[470622:470646] == bytes.fromhex('21065a570700d832ca05210664560700405ebffe6b0f0577'))
    print('\n== MPU selector provenance ==')
    check('MPU context selector bytes are only 0/1', CF[202764:202772] == bytes.fromhex('0000000001000000'))
    check('MPU loader table base is fixed 0x31894', CF[411886:411900] == bytes.fromhex('06f09e00c6f22a0694180300caf1'))
    expected_selector_refs = {395434: 202770, 411604: 202767, 459496: 202768, 459528: 202767, 413736: 202769, 413802: 202769, 413868: 202771, 413934: 202771, 459552: 202764, 459722: 202765, 459894: 202766}
    mpu_callers = {e for e, r in funcs.items() if e != 411886 and 'FUN_000648ee(' in (r.get('decompiled_c') or '')}
    check('MPU loader has exactly the 11 recovered canonical callers', mpu_callers == set(expected_selector_refs), repr(sorted(mpu_callers)))
    for entry, target in expected_selector_refs.items():
        check(f'MPU caller 0x{entry:X} reads fixed selector byte 0x{target:X}', any((r[1] == 'READ' and r[2] == target for r in refs(entry))), repr(refs(entry)))
    check('all recovered MPU selector bytes decode to context 0 or 1', {CF[t] for t in expected_selector_refs.values()} <= {0, 1})
    print('\n== architectural alias geometry ==')
    PE1_BASE, SELF_BASE, SIZE = (4273864704, 4275961856, 131072)
    check('self LocalRAM view is same-offset +0x200000 alias', SELF_BASE - PE1_BASE == 2097152)
    check('XCP shadow aliases to FEDF7C00, not a lower FEBE control object', XCP_LO + (SELF_BASE - PE1_BASE) == 4276059136)
    for control in (4273866752, 4273868800, 4273870848, 4273872896, 4273960708):
        check(f'control object 0x{control:X} physical offset differs from XCP start', (control - PE1_BASE) % SIZE != (XCP_LO - PE1_BASE) % SIZE)
_section_keyless_application_pc_surfaces()
print()

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
