#!/usr/bin/env python3
"""Raw-firmware XCP reachability and shadow-write plan pins.

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

print("== xcp reachability ==")
def _section_xcp_reachability():
    import subprocess
    import sys
    REPO = REPO_ROOT
    from exploit.followups.xcp_read_probe import CONNECT_REQUEST
    from exploit.followups.xcp_reachability import FORBIDDEN_COMMANDS, VERDICT_REACHABLE_ERROR, VERDICT_REACHABLE_POSITIVE, VERDICT_TIMEOUT, VERDICT_UNEXPECTED, XcpReachabilityError, assert_connect_only, build_plan, classify_response, forbidden_opcode_audit
    print('== CONNECT-only guard ==')
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
    check('no page-copy / SET_MTA / DOWNLOAD / MODIFY_BITS byte literal appears in the module', all((token not in source for token in ('"\\xe4', '"\\xf6', '"\\xf0\\x', '"\\xec\\x'))))
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
    REPO = REPO_ROOT
    from exploit.followups.xcp_shadow_write_plan import MAX_DOWNLOAD, SHADOW_END, SHADOW_SIZE, SHADOW_START, XcpShadowWriteError, build_download_plan, chunk_write, download_request, modify_bits_request, set_mta_request, simulate_plan, simulate_write, validate_window

    def rejects(fn) -> bool:
        try:
            fn()
        except XcpShadowWriteError:
            return True
        return False
    print('== exact request encoding ==')
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
    check('planner has no live execution path', plan['live_execution_implemented'] is False)
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
