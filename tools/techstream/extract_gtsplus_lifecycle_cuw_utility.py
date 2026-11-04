#!/usr/bin/env python3
"""Extract offline CUW+/privileged-utility integration contracts from exact release bodies.

No application, vehicle, auth endpoint, or native export is executed. GUI sources
are authenticated/decrypted locally using the existing packaging decoder.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pefile

from tools import REPO_ROOT
from tools.techstream.extract_gtsplus_tse_managed_semantics import (
    _instructions, _lines, _method_pin, _open, _recovery_proof,
)
from tools.techstream.gtsplus_local_crypto import decode_gui

DEFAULT_INSTALLED = REPO_ROOT / 'software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics'
DEFAULT_CUW = REPO_ROOT / 'software/Techstream/gtsplus/gts-all-unprotected/CUWPlus'
DEFAULT_MAIN = REPO_ROOT / 'software/Techstream/gtsplus/gts-all-unprotected/GTSPlus'
DEFAULT_ENTRY = REPO_ROOT / 'build/out/gts-lifecycle-cuw-entry'
DEFAULT_LAUNCHER = REPO_ROOT / 'build/out/gts-lifecycle-launcher'
DEFAULT_AUX = REPO_ROOT / 'build/out/gts-lifecycle-aux'
DEFAULT_OUT = REPO_ROOT / 'data/generated/gtsplus_2026/lifecycle_cuw_utility.json'
DOMAIN = 'cuw_utility'
JS_FILES = {
    'cuw-main': ('cuw', 'js/cuw/cuw_main.js'),
    'cuw-controller': ('cuw', 'js/cuw/controllers/cuw_controller.js'),
    'cuw-model': ('cuw', 'js/cuw/models/cuw_model.js'),
    'key-controller': ('gts', 'js/gts/ecu_security_key/ecu_security_key_controller.js'),
    'key-worker': ('gts', 'js/gts/ecu_security_key/ecu_security_key_worker.js'),
    'gts-raw-api': ('gts', 'js/gts/common/gts_platform_raw_interface.js'),
    'health-controller': ('gts', 'js/gts/health_check/health_check_controller.js'),
    'hino-controller': ('gts', 'js/gts/ecu_search_for_hino/ecu_search_for_hino_controller.js'),
    'saap-controller': ('gts', 'js/gts/software_as_a_part/software_as_a_part_controller.js'),
    'saap2-controller': ('gts', 'js/gts/software_as_a_part_aisac2/software_as_a_part_aisac2_controller.js'),
}
PACKAGE_SHA = {
    'cuw.gui': 'c01ac058c24f125ffa2e294575b2ab9e1ce9fd7a9f728fa2e01f3dd2c783f30d',
    'cuw.cpf': '7889d150e5273ca5bccafde7e1487eacdf9324dd2f4ab9e877351ec1e657ed1c',
    'gts.gui': '80ff7eed3a3a429aedc14384befb0f43b8ebd8176868b0bf41135033ce4ea37d',
    'gts.cpf': '773becfd6fad75bfaab3d0dbdb0f4e05cdf1511646f76d77ca2c3d0a914691dc',
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def q(name: str) -> str:
    return f'{DOMAIN}.{name}'


def build(*, installed: Path = DEFAULT_INSTALLED, cuw_root: Path = DEFAULT_CUW,
          main_root: Path = DEFAULT_MAIN, entry_root: Path = DEFAULT_ENTRY,
          launcher_root: Path = DEFAULT_LAUNCHER, aux_root: Path = DEFAULT_AUX) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    pes: dict[str, Any] = {}

    def source(name: str, path: Path, expected: str | None, representation: str) -> str:
        data = path.read_bytes()
        actual = digest(data)
        if expected is not None and actual != expected:
            raise ValueError(f'source identity drift: {name}')
        sources.append(dict(id=q(name), path=path.relative_to(REPO_ROOT).as_posix(),
                            sha256=actual, size=len(data), representation=representation))
        return q(name)

    def recovered(name: str, path: Path, original: Path, expected: str, manifest: Path) -> None:
        data = json.loads(manifest.read_text())
        rows = data.get('entries', data.get('binaries', []))
        row = next(r for r in rows if Path(r.get('relative_path', r.get('path', ''))).name == path.name)
        protected = row.get('protected', row)
        out_hash = row.get('output_sha256', row.get('plaintext', {}).get('sha256'))
        if out_hash != expected:
            raise ValueError(f'recovery manifest identity drift: {name}')
        source(name + '-installed', original, protected['stub_sha256'], 'installed protected PE')
        source(name + '-sidecar', original.with_name(original.name + '._'), protected['sidecar_sha256'], 'installed protected body sidecar')
        source(name, path, expected, 'recovered materialized PE')
        pes[name] = path

    recovered('backend', cuw_root / 'CuwBackendService.dll', installed / 'CUWPlus/CuwBackendService.dll',
              'eb0177bf3a4f608b216541e1a4c088d69ef1037f486110ffa958407735c29ca5', cuw_root / 'manifest.json')
    recovered('entry', entry_root / 'CuwBackendServiceConsoleApp.exe', installed / 'CUWPlus/CuwBackendServiceConsoleApp.exe',
              '6bd3c9d1d3b759f1cf95e812d29f101045194cd79c9083b7b30339905e04813d', entry_root / 'manifest.json')
    recovered('launcher', launcher_root / 'CUWLauncher.exe', installed.parent / 'CUWLauncher/CUWLauncher.exe',
              '1bce32d2d60ebf78191f39c6231366c1248c7813f4e61191e6a5367e26ca4f79', launcher_root / 'manifest.json')
    recovered('core', cuw_root / 'CUW.dll', installed / 'CUWPlus/CUW.dll',
              '0e9ba6fd54b8301948309b5fb0571c0b99b40276dec3f0d229a44b7890cda603', cuw_root / 'manifest.json')
    recovered('gene', main_root / 'bin/UtilityGene.dll', installed / 'GTSPlus/bin/UtilityGene.dll',
              'a844d3045b2cb780a63e3959ec04bd27baab4ea7195080876bbdf6d2cf86c4cc', main_root / 'manifest.json')
    source('utility-front', installed / 'GTSPlus/bin/UtilityPlusFrontNK.dll',
           '3472091a3c2f8df114fbab491dc442c3aee25a3485ce6390653413cb029d871a', 'installed native plaintext PE')
    pes['utility-front'] = installed / 'GTSPlus/bin/UtilityPlusFrontNK.dll'
    managed = {}
    for name in ('backend', 'entry', 'launcher'):
        proof = _recovery_proof(pes[name])
        managed[name] = _open(pes[name])
        evidence.append(dict(id=q(name + '-materialized'), source=q(name), kind='managed-body-materialization', locator='MethodDef RVA census', **proof,
                             finding='Every nonzero MethodDef RVA has materialized bytes; hollow CP bodies are rejected.'))

    def il(name: str, component: str, typename: str, method: str, anchors: tuple[str, ...], finding: str, index: int = 0) -> None:
        pe = managed[component]
        row, ins, body = _instructions(pe, typename, method, index=index)
        rendered = _lines(pe, ins)
        hits = []
        for anchor in anchors:
            found = [(n, line) for n, line in enumerate(rendered) if anchor in line]
            if not found:
                raise ValueError(f'IL control-flow drift: {typename}::{method}: {anchor}')
            n, line = found[0]
            hits.append(dict(il_offset=ins[n].offset - ins[0].offset, instruction=line))
        evidence.append(dict(id=q(name), source=q(component), kind='managed-il', locator=f'{typename}::{method}',
                             **_method_pin(row, body), anchors=hits, finding=finding))

    il('entry-main', 'entry', 'Cuw.Program', 'Main', ('WaitOne', 'Init', 'Start', 'ER_StartAliveMonitorRunningCS', 'ER_StartWaitForEndingCS', 'Application::Run', 'Stop', 'endfinally'),
       'Global executable-path-derived mutex rejects duplicate backend with exit code -1; Init/Start register platform liveness and ending callbacks; hidden WinForms loop owns process; finally Stop runs after startup failure or loop return.')
    il('entry-mutex', 'entry', 'Cuw.Program', '.cctor', ('Assembly::get_Location', 'MD5::Create', "'Global\\\\'", 'stsfld MUTEX_NAME'),
       'Backend instance mutex is Global plus lowercase hexadecimal MD5 of executable assembly location, not a vehicle or browser-session ID.')
    il('form-close', 'entry', 'Cuw.MainForm', 'MainForm_FormClosing', ('ldsfld SVR_SHUTDOWN', 'ceq', 'set_Cancel'),
       'Ordinary form close is cancelled until the service OnShutdown callback sets SVR_SHUTDOWN; power-change event only logs.')
    il('backend-init', 'backend', 'Cuw.CuwBackendService', 'Init', ('conf\\\\cuwpf.yaml', 'conf\\\\gtsplus.pp', 'ReadConfig', 'add_SessionEnding', 'WebSocketServer::.ctor', 'set_EnabledSslProtocols'),
       'Backend loads encrypted CUW config beside entry assembly, installs OS session-ending handler, and creates Fleck WebSocket server with TLS protocol value 0xC00.')
    il('backend-admit', 'backend', 'Cuw.CuwBackendService', 'OnClientConnect', ('get_IsRunning', 'brtrue', 'get_MaxConnection', 'blt', 'Close', 'add_OnClose', 'Add'),
       'Connection rejected by Close if service is not running or count reaches MaxConnection; admitted socket gets ClientSession and pool membership.')
    il('backend-stop', 'backend', 'Cuw.CuwBackendService', 'Stop', ('set_Status', 'Clear', 'Timer::Stop', 'WebSocketServer::Dispose', 'Invoke'),
       'Stop marks service stopped, clears/disconnects clients, stops timer, disposes listener and raises OnShutdown.')
    il('can-exit', 'backend', 'Cuw.CuwBackendService', 'CanExit', ('get_ConnectionCount', 'get_ReprogrammingFlag', 'brtrue', 'ceq'),
       'CanExit requires ReprogrammingFlag false AND ConnectionCount zero; UI disconnect alone does not authorize backend exit while programming flag remains set.')
    il('confirm-ending', 'backend', 'Cuw.CuwBackendService', 'ConfirmEnding', ('CanExit', 'brfalse', 'Suspend', "'000'"),
       'ConfirmEnding suspends new work on allowed exit; otherwise returns 000 veto.')
    il('execute-ending', 'backend', 'Cuw.CuwBackendService', 'ExecuteEnding', ('set_EndExecute', 'EventWaitHandle::Set', 'ER_EndAliveMonitorRunningCS', 'ER_EndWaitForEndingCS', 'ER_EndApplicationCS', 'Resume'),
       'Shutdown decision signals EndExecuteEvent; non-OS executed ending unregisters platform callbacks; cancelled ending resumes a suspended service.')
    il('os-ending', 'backend', 'Cuw.CuwBackendService', 'SessionEnding', ('0x2710', 'WaitOne', 'get_EndExecute', 'set_Cancel', 'CanExit', 'Reset'),
       'OS logoff/shutdown waits at most 10000ms for platform decision; explicit false decision cancels; timeout falls back to CanExit and cancels if busy.')
    il('permission', 'backend', 'Cuw.Command.CuwCommand', 'CheckPermitExecuteCommand', ('get_HasExclusiveLock', 'brfalse', 'get_IsAppAuthenticated', 'Unknown command'),
       'Existing exclusive-lock holder is immediately permitted. Otherwise bootstrap commands are public; LockExclusive/config/path require app authentication; programming/transport commands require authentication AND exclusive lock; unknown commands throw.')
    il('command-result', 'backend', 'Cuw.Command.CuwCommand', 'ExecuteCommand', ('CheckPermitExecuteCommand', 'brtrue', 'ldc.i4.2', 'ExecuteStartReprogramming', 'ExecuteClearStatusOfReprogramming'),
       'JSON CommandName/RequestID route through admission before dispatch; permission failure returns ResultCode2, unsupported route ResultCode3; native returnValue remains separate.')
    il('command-error', 'backend', 'Cuw.Command.CuwCommand', 'Execute', ('ExecuteCommand', 'Send', 'ErrorInfo::set_Exception', 'set_Message', 'set_Detail', 'ldc.i4.3'),
       'Execution errors become JSON error object (exception/message/detail), ResultCode1 or unknown-command3, sent to same client with request correlation.')
    il('chap', 'backend', 'ChapAuthentication', 'Authenticate', ('String::IsNullOrEmpty', 'get_ChallengeCode', 'get_IsAppAuthenticated', 'SHA256CryptoServiceProvider::.ctor', 'String::op_Inequality', 'set_IsAppAuthenticated', 'set_ChallengeCode'),
       'Local application challenge-response is separate from account and ECU auth: empty/wrong response returns1, missing challenge2, already authenticated0; success marks this session authenticated and consumes challenge. Packaging/auth secret values are omitted.')
    il('lock', 'backend', 'Cuw.Model.CuwModel', 'LockExclusive', ('get_HasExclusiveLock', 'get_Clients', 'get_IsConnected', 'Remove', 'set_HasExclusiveLock', 'ResetDisconnectError'),
       'Lock is per ClientSession: own lock returns0; connected other owner returns1; disconnected lock holders removed; success sets lock and clears ReportDisconnected.')
    il('start-flag', 'backend', 'Cuw.Command.CuwCommand', 'ExecuteStartReprogramming', ('StartReprogramming', 'get_ReturnValue', 'brtrue', 'ldc.i4.1', 'SetReprogrammingStatus'),
       'Successful native StartReprogramming (returnValue0) sets global service ReprogrammingFlag true; wrapper ResultCode0 can coexist with nonzero native returnValue.')
    il('clear-flag', 'backend', 'Cuw.Command.CuwCommand', 'ExecuteClearStatusOfReprogramming', ('ClearStatusOfReprogramming', 'get_ReturnValue', 'brtrue', 'ldc.i4.0', 'SetReprogrammingStatus'),
       'Only successful native clear sets service programming flag false.')
    il('disconnect', 'backend', 'Cuw.ClientSession', 'Disconnect', ('set_NomallyClosed', 'set_HasExclusiveLock', 'Disconnect'),
       'Explicit client Disconnect marks normal closure, releases session lock and closes connection; it does not kill backend process or unconditionally stop native worker.')
    il('socket-close', 'backend', 'Cuw.ClientSession', 'Session_OnClose', ('GetStatusOfReprogramming', 'get_ReturnValue', 'brfalse', 'set_IsForced', 'ClearStatusOfReprogramming', 'endfinally'),
       'Socket close queries native status; nonzero status attempts non-forced clear. Errors are logged; OnClose is raised in finally. This does not force-clear active native programming.')
    il('pool-remove', 'backend', 'Cuw.ClientSessionPool', 'Remove', ('ContainsKey', 'get_IsConnected', 'Disconnect', 'Remove'),
       'Removing a live session disconnects it before deleting pool entry.')
    core = 'Cuw.Model.CuwCoreModel'
    il('cal-read', 'backend', core, 'ReadReprogrammingDataFile', ('get_FilePath', 'String::IsNullOrEmpty', 'ReadReprogrammingDataFile', 'brtrue', 'MarshalToCpuInfoList', 'FreeCoTaskMem'),
       'Selected path/mode/destination/CPU capacity passed to CUW.dll; missing path fails; nonzero native return or invalid CPU count returns failure without calibration projection; allocated native buffers freed in finally.')
    il('cal-search', 'backend', core, 'GetRewriteFilesInfo', ('get_DirList', 'ReadCuwFile', 'get_IsValid', 'get_InvalidCalFileList', 'get_AllNewCalIds', 'set_Target'),
       'Search scans supplied directories, records invalid calibration files, maps old/new CID matches and distinguishes target0/display candidates,1/already-new CID,2/no matching target.')
    il('progress', 'backend', core, 'GetStatusOfReprogramming', ('GetStatusOfReprogramming', 'set_TragetCPUIndex', 'set_RemainigTime', 'set_NeedIGOffOn', 'set_IGStatusChangeableType', 'set_ErrorDetail', 'set_UserErrorCode', 'FreeCoTaskMem'),
       'Polling returns native status plus CPU progress/retry/whole-repro flags, remaining/estimated time, IG constraints and structured error detail, freeing marshalled buffer in finally.')
    il('retry', 'backend', core, 'InformResultOfQueryRetry', ('get_ResultOfQueryRetry', 'get_IsWholeReproSwitched', 'InformResultOfQueryRetry'),
       'UI owns retry/cancel decision and whole-reprogramming switch; backend forwards both values to native engine.')
    il('recovery-read', 'backend', core, 'ReadRecoveryInfoFile', ('ReadRecoveryInfoFile', 'brtrue', 'set_DeviceId', 'set_Vin', 'set_CalInfo', 'set_StoredData', 'FreeCoTaskMem'),
       'Recovery returns saved J2534 device, VIN, calibration/CPU list and Suzuki/Daihatsu security-support storage after native success.')
    il('clear-xml', 'backend', core, 'ClearStatusOfReprogramming', ('get_IsForced', 'ClearStatusOfReprogramming', 'brtrue', 'DeleteAllXMLFileForRequestReprogrammingKey'),
       'Native clear receives explicit isForced. Request-key XML deletion runs only when clear returns0.')
    il('key-request', 'backend', core, 'StartRequestReprogrammingKey', ('get_MethodOfRequest', 'get_Url', 'StartRequestReprogrammingKey', 'ldc.i4.3', 'bne.un', 'set_RepSecInfo'),
       'Request method and configured URL forwarded to CUW.dll; method3 returns native security seed/key-pair metadata for frontend server workflow.')
    il('key-cancel', 'backend', core, 'CancelRequestReprogrammingKey', ('CancelRequestReprogrammingKey', 'set_ReturnValue'),
       'Key-request cancellation has a separate native API and return code from reprogramming retry/cancel.')
    il('last-folder', 'backend', 'Cuw.Model.CuwModel', 'StoreLastAccessFolderPath', ('LastAccessFolder', 'Registry::SetValue'),
       'Last selected calibration directory persists as HKCU Software/Toyota Diagnostics/Calibration Update Wizard/LastAccessFolder.')
    il('server-data', 'backend', 'Cuw.Model.CuwModel', 'SaveData', ('ContainsKey', 'set_Item', 'Add'),
       'SaveData updates the backend-owned dictionary used to restore browser state; it is not a disk flush.')
    il('launcher-start', 'launcher', 'CUWLauncher.App', 'Application_Startup', ('.cuwd', 'SettingForDH.xml', 'Mutex::.ctor', 'WaitOne', '.scuw', 'LaunchCUWPlus', 'ReleaseMutex', 'Environment::Exit'),
       'External file association launcher routes by extension/installed brand/running legacy GTS, enforces named launcher mutex, and releases/disposes mutex before Environment.Exit(0); CUWLauncher errors are UI messages, not meaningful process exit codes.')
    il('launcher-open', 'launcher', '<Launch>d__9', 'MoveNext', ('CUWMain.html', '?P2=', 'EscapeDataString', 'Process::Start', 'ConnectToGTSPlusPF', 'SetConnectionConditionToGTSPlusPF', 'WaitForDisconnectCUWPlusFromGTSPlusPF', 'ldc.i4.3', 'IDisposable::Dispose'),
       'Launches local HTTPS browser URL with escaped calibration path P2, then connects to platform; failed connection registration/existence checks retry while counters <=3, except connection failure401; socket disposed after each attempt.')
    il('launcher-connect', 'launcher', '<ConnectToGTSPlusPF>d__10', 'MoveNext', ('0x1388', 'wss://127.0.0.1:', 'ConnectAsync', 'mintWSSPortTo', 'ble', '0x191'),
       'Tries configured platform WSS port ranges on loopback with 5000ms cancellation per connect; exhausted range/connection failure surfaces launcher error401.')
    il('launcher-register', 'launcher', '<SetConnectionConditionToGTSPlusPF>d__11', 'MoveNext', ('CN000001', 'CUWLauncher', '0x1388', 'ReceiveSpecifiedAPIIDMsgFromWebSocket', 'resultInfo', 'brfalse', '0x192'),
       'Registers CN000001 name CUWLauncher maxNum2 with platform; reply result nonzero or timeout produces error402.')
    il('launcher-wait', 'launcher', '<WaitForDisconnectCUWPlusFromGTSPlusPF>d__12', 'MoveNext', ('CN000004', 'existNum', 'ldc.i4.2', '30000.0', '0x1f4', '0x193'),
       'Polls platform CUW connection name, waits for first existNum>0 then zero to finish; first admission timeout30s ->301, poll errors403, 500ms between polls. Browser-process lifetime itself is not the return contract.')

    def native(name: str, component: str, va: int, size: int, expected_hash: str, finding: str,
               byte_anchors: tuple[tuple[int, str], ...] = ()) -> None:
        pe = pefile.PE(str(pes[component]))
        raw = pe.get_data(va - pe.OPTIONAL_HEADER.ImageBase, size)
        if digest(raw) != expected_hash:
            raise ValueError(f'native body window drift: {name}')
        anchors = []
        for address, hexbytes in byte_anchors:
            if pe.get_data(address - pe.OPTIONAL_HEADER.ImageBase, len(bytes.fromhex(hexbytes))) != bytes.fromhex(hexbytes):
                raise ValueError(f'native branch drift: {name} @{address:x}')
            anchors.append(dict(va=hex(address), bytes=hexbytes))
        evidence.append(dict(id=q(name), source=q(component), kind='native-control-flow', locator=hex(va),
                             byte_window_size=size, byte_window_sha256=expected_hash, anchors=anchors, finding=finding))

    native('native-clear', 'core', 0x10063A80, 246, '3a5f63392a3aa6d0126969ccf1ba084d28a02d717201d888af3be044bda5ca5a',
           'ClearStatusOfReprogramming is not unconditional: state1 or (busy-byte zero AND (forced OR completion flag OR state4/0 OR cancel flag)) calls reset and returns0; otherwise returns0xBBF (3007).',
           ((0x10063B25, '803de2bf0810007527'), (0x10063B2E, '807d0800752e'), (0x10063B55, 'b8bf0b0000'), (0x10063B67, 'e894c2fdff')))
    native('native-reset', 'core', 0x1003FE00, 80, 'c5f91943b2b45b6b42eda7e2d3c4effa1422febde55a97042e10b7e7e6fbe49f',
           'Reset 0x1003FE00 signals request/copy worker events, requests worker termination, waits INFINITE on running thread then Sleep(500) until worker pointer clears, resets calibration/state storage and frees buffers. No bounded join is present in this cleanup path.')
    native('gene-before', 'gene', 0x1000E2C0, 586, 'd23207445585b875ca353c08dabbdb3c629099e9d913f3fdf6aaa936be6b0a0a',
           'KeyUpdate_before rejects unsupported protocol discriminator !=0x34 with99; auth helper25890 accepts 0xFFA/0xFFB modes, otherwise returns error; helper262D0 prepares selected topology and exports admitted identities plus M1/M2/M3 to caller on success.')
    native('gene-validate', 'gene', 0x1000E510, 815, '07790f263273a5f0c7b3fd4658fa10c7dd642894ec4a92b4eb43ef748e6b19af',
           'KeyValidation uses protocol0x34 gate and session auth helper25930; 0xFB8 becomes status1 with success return; helper263F0 maps key status2->0,0/1->3,other->2; returns selected ECU identities only for local_80==1.')
    native('gene-after', 'gene', 0x1000DF20, 928, '793695c48ad32efeabe052125fea1466e6221c690898b4aaa870f359b57e7cba',
           'KeyUpdate_after binds supplied selected IDs and six update-data arrays, processes master then selected nine-entry participant table, aborts on helper result !=3, performs final helper24730 and returns per-selected ECU success booleans;0 is wrapper success, not uniform ECU success.')
    native('utility-command-map', 'utility-front', 0x100014AA, 183, '6e1b890356474bf69c67d8dc6bcb4cfee04cdac7288db24d88284da9663498a9',
           'Table initializer FUN10001020 binds exact JSON API strings UG000021/22/23 to switch selectors0x15/16/17. ComUtilityFront compares parsed API ID against this28-byte-entry table then switches on its selector, closing the signed Subaru API-to-native wrapper join.',
           ((0x100014B3, '6858730010'), (0x100014DD, 'c70594d4001015000000'),
            (0x100014F0, '6864730010'), (0x1000151A, 'c705b0d4001016000000'),
            (0x1000152D, '6870730010'), (0x10001557, 'c705ccd4001017000000'),
            (0x10007358, '5547303030303231'), (0x10007364, '5547303030303232'),
            (0x10007370, '5547303030303233'),
            (0x10002ECF, '8b048580d20010'), (0x10002EDA, '0f87181f0000'),
            (0x10002EE0, 'ff248570500010')))
    front_pe = pefile.PE(str(pes['utility-front']))
    front_windows = (
        (0x10004A37, 'ff15ac7000108bf085f6740a'),
        (0x10004AA5, '833dc0c10010007518'),
        (0x10004AD8, 'ff15b07000108bf085f6740a'),
        (0x10004CA9, 'ff15b4700010'),
        (0x100036C9, 'a8017443fec83c7e773d'),
        (0x100036F6, 'ff15a07000108bf085f6'),
    )
    checked = []
    for va, hexbytes in front_windows:
        if front_pe.get_data(va - 0x10000000, len(bytes.fromhex(hexbytes))) != bytes.fromhex(hexbytes):
            raise ValueError(f'UtilityPlusFront branch drift @{va:x}')
        checked.append(dict(va=hex(va), bytes=hexbytes))
    evidence.append(dict(id=q('utility-dispatch'), source=q('utility-front'), kind='native-control-flow', locator='ComUtilityFront @0x10002990; cases1,2,5,0x15/16/17', anchors=checked,
                         finding='Initialization case1 sets global ready only after Ex2initialCom success. Cases0x15/16/17 require ready, call UtilityGene ordinals98/99/100 and map argument/native failures to0x90281115/16/17. Case5 SecurityAccess requires initialized communication and odd byte level1..0x7F then ordinal request. Case2 stops periodic messages, finalizes transport, resets parameters/ready, stops keepalive even on finalize failure; return restores CCommFrameCtrl connection info.'))

    cm = aux_root / 'ContentServer/GtsPlus-CM.dll'
    resource = aux_root / 'ContentServer/CryptgraphResource.dll'
    crypt = aux_root / 'ContentServer/CryptgraphCommon.dll'
    for name, path, expected in (
        ('decode-cm', cm, 'ebc7c0b359c63d12a80c7fc596e93c226007b915f21032e05efa1046c2b292b2'),
        ('decode-resource', resource, '7a9a2c08f0055fdfed82258835ba68c4a4d41ffeb537bd27caa19ad19d1f16f6'),
        ('decode-crypt', crypt, '98fc5afd362f6e28aec9f06f71c15c4d6751751a27a8325cdc143ad9f57366b0'),
    ):
        recovered(name, path, installed / 'ContentServer' / path.name, expected, aux_root / 'manifest.json')
    certificate = installed / 'ContentServer/dist.crt'
    source('gui-certificate', certificate, '857ec034c946604c52fd845134386b5b914936962254048e8766d78fa6b3ad50', 'installed public signature certificate')
    packages = {}
    for package in ('cuw', 'gts'):
        for suffix in ('gui', 'cpf'):
            source(package + '-' + suffix, installed / 'GTSPlusGUI' / f'{package}.{suffix}', PACKAGE_SHA[f'{package}.{suffix}'], 'installed authenticated GUI envelope' if suffix == 'gui' else 'installed GUI packaging envelope')
        packages[package] = decode_gui(installed / 'GTSPlusGUI' / f'{package}.gui', cm, resource, crypt, certificate)
    texts = {}
    for name, (package, member) in JS_FILES.items():
        raw = packages[package][member]
        texts[name] = raw.decode('utf-8-sig')
        sources.append(dict(id=q(name), path=(installed / 'GTSPlusGUI' / f'{package}.gui').relative_to(REPO_ROOT).as_posix(),
                            member=member, sha256=digest(raw), size=len(raw), representation='authenticated decoded JavaScript member', parent_source=q(package + '-gui')))

    def js(name: str, component: str, method: str, anchors: tuple[str, ...], finding: str,
           absent: tuple[str, ...] = ()) -> None:
        text = texts[component]
        match = re.search(r'\w+\.prototype\.' + re.escape(method) + r'=(?:async )?function', text)
        if not match:
            raise ValueError(f'JS function drift: {component}::{method}')
        end = re.search(r'\w+\.prototype\.\w+=(?:async )?function', text[match.end():])
        part = text[match.start():match.end() + end.start()] if end else text[match.start():]
        hits = []
        for anchor in anchors:
            offset = part.find(anchor)
            if offset < 0:
                raise ValueError(f'JS branch drift: {component}::{method}: {anchor}')
            hits.append(dict(character_offset=match.start() + offset, expression=anchor))
        for expression in absent:
            if expression in part:
                raise ValueError(f'JS absent-check drift: {component}::{method}: {expression}')
        evidence.append(dict(id=q(name), source=q(component), kind='javascript-control-flow', locator=method,
                             function_sha256=digest(part.encode()), anchors=hits, finding=finding,
                             **({'absent_expressions': list(absent)} if absent else {})))

    js('hc-launch', 'health-controller', 'onClickCalibrationToCuw', ('../cuw/CUWMain.html?P1=', 'encodeURIComponent(calibrationId)', "window.open(url,'_blank')"),
       'GTS Health Check launches a separate CUW browser page with old calibration ID P1; calibration path selection is deferred to CUW.')
    js('ui-entry', 'cuw-main', 'init', ("getParam('P1')", "getParam('P2')", "getParam('P3')", "getParam('P4')", 'EXEC_REPROGRAMMING', 'connectCuwPf()', 'connectGtsPf()', 'loginController.init()'),
       'UI parses P1 old CID/P2 path/P3 file list/P4 caller application, connects independently to CUW and GTS platform, initializes settings then login; beforeunload warning exists only while EXEC_REPROGRAMMING; failed embedded init responds CANCEL when P4 nonempty.')
    js('ui-login', 'cuw-main', 'onLoggedIn', ('model.lockExclusive()', 'model.stopReceivingOfCID()', 'model.stopReproDataFileCopyToUSBMemory()', 'gtsApi.startDiagnosis(param)', 'cuwController.initCuw()'),
       'Login completion obtains CUW lock, attempts stop of previous CID/USB copy workers, starts platform diagnosis, initializes dealer/user settings, then CUW controller.')
    js('ui-init', 'cuw-controller', 'initCuw', ('model.lockExclusive()', 'result.returnValue === SUCCESS', 'model.configureCuwDll()', 'controller.goStartCuw()', 'controller.disconnect()'),
       'Controller requires lock success, configures native DLL and GTS identity/CID conversion map; initialization failure disconnects and shows end view.')
    js('ui-admission', 'cuw-controller', 'goStartCuw', ('getApiExclusiveControlLock()', 'sendLogoutControl(true)', 'REPROGRAMMING_NOT_STARTED_ERROR', 'readRecoveryInfoFile', 'initViewS70174', 'judgmentOfReprogrammingFileSearch()', 'restoreClientData()', 'showS70117()'),
       'Separate platform exclusive-control lock and logout inhibit protect session. Not-started status chooses saved recovery or fresh calibration selection; existing native activity restores backend client data and resumes progress UI instead of restarting engine.')
    js('ui-recovery', 'cuw-controller', 'onClickS70174RetryBtn', ('checkRecoveryVin', 'judgeFlashable', 'startReprogramming()', 'recoveryStartReprogramming'),
       'Recovery retry verifies VIN then native flashability before restarting; failed flashability routes fatal/end flow.')
    js('ui-recovery-delete', 'cuw-controller', 'onClickS70174DeleteBtn', ('deleteRecoveryInfoFile()', 'DATA_KEY_VIN', 'DATA_KEY_IS_EXISTS_REPRO_SECURITY'),
       'User-confirmed discard deletes native recovery state and clears saved VIN/security metadata rather than silently resuming.')
    js('ui-start', 'cuw-controller', 'startReprogramming', ('SUCCESS || result.returnValue === REPROGRAMMING_IN_PROGRESS', 'showS70117()', 'FAILED_TO_REPROGRAMMING_START', 'showS70181()'),
       'Start accepts success/in-progress into status polling; native start failure or rejected Promise enters failure teardown.')
    js('ui-progress', 'cuw-controller', 'recursiveCheckStatusOfReprogramming', ('REPROGRAMMING_IN_PROGRESS', 'WAITING_FOR_REPROGRAMMING', 'goAfterRecv()', 'extendRetryLimitFlag', 'confirmationOfRewriteRetry', 'GET_STATUS_OF_REPROGRAMMING_REQUIRED_REQUEST_REP_KEY', 'REPROGRAMMING_INPUT_SIGNATURE_ERROR', 'J2534DEVICE_AND_PC_NOT_CONNECTED){}'),
       'Status drives progress, inter-CPU IG/battery waits, success postprocess, preparation/retry UI, key/signature request and terminal errors. PC-disconnected branch is literally empty: it neither schedules another poll nor teardown in this function.')
    js('ui-retry', 'cuw-controller', 'confirmationOfRewriteRetry', ('model.checkMaxRetryCount < retryCount', 'CuwModel.Retry.CANCEL', 'showS70130', 'wholeReproNotifyFlag', 'EVENT_BTN.RETRY'),
       'Native retry count and extended-limit flag constrain UI retries; exceeded count sends CANCEL and exit screen. Otherwise USB/battery/transport-specific retry or whole-repro choices remain caller-selected.')
    js('ui-retry-send', 'cuw-controller', 'informResultOfQueryRetry', ('CuwModel.Retry.RETRY,model.isSwitchedToWholeRepro()', 'RETRY_INQUIRY_NOTIFICATION_ERROR', 'showS70181()', 'successCallback()'),
       'Retry/whole-repro decision crosses native API; adapter errors show reconnect/retry/cancel screens, retry notification failure tears down.')
    js('ui-key-request', 'cuw-controller', 'getReprogrammingKeyFromServer', ('model.sendSignatureRequest()', "statusCode !== 'MIR2000000'", 'faultMessage', 'setTimeout(controller.recursiveGetReprogrammingKey,1000'),
       'Online method3 request requires success status and no faultMessage then polls by returned ID; errors become frontend fallback decisions, never implicit native authorization.')
    js('ui-key-poll', 'cuw-controller', 'recursiveGetReprogrammingKey', ("statusCode === 'MIR2020000'", 'endTime - startTime > 301000', '1000,controller,def,id,startTime', "ret.result='nosignature'", 'response.apiResult.Signature'),
       'Pending signature polls every1s with301000ms cutoff; failures reject, missing signature is explicit nosignature, available signature returns to SetReprogrammingKey caller.')
    js('ui-key-fallback', 'cuw-controller', 'getRequestReprogrammingKeyByAuto', ('getReprogrammingKeyFromServer()', "result.result === 'nosignature'", 'setReprogrammingKey(result.signature)', 'getRequestReprogrammingKeyByOffline', 'CONFIG_KEY_CAN_OFFLINE_REPSEC'),
       'Online unavailable/fault/no-signature enters offline XML selection or user retry/cancel subject to allow-offline config; server-returned signature is passed to native setter.')
    js('ui-key-offline', 'cuw-controller', 'readSignature', ('saveXMLFileForRequestReprogrammingKey()', 'loadXMLFileForReprogrammingKey', 'FileDialogController', 'cancelRequestReprogrammingKey()'),
       'Offline request XML is saved once/reused; selected response XML is loaded through native key parser; dialog back/retry/cancel is explicit.')
    js('ui-cancel', 'cuw-controller', 'cancelRequestReprogrammingKey', ('model.cancelRequestReprogrammingKey()', 'recursiveCheckCancelRequest'),
       'User key cancellation first invokes native cancel then polls until native engine leaves key-required/in-progress status.')
    js('ui-failure-exit', 'cuw-controller', 'showS70181', ('model.clearStatusOfReprogramming(true)', 'isFlashSuccess:false', 'model.cancelingSleepMode()', 'model.clearServerData()', 'SendValue.CANCEL', 'apiExclusiveControlUnlock()', 'sendLogoutControl(false)', 'controller.disconnect()', 'showEndView()'),
       'Fatal/cancel flow force-clears native status; on success sends failure vehicle info/report, restores sleep, clears backend dictionary, responds CANCEL to embedding caller, unlocks platform/logout inhibit and disconnects both sockets. A catch swallows earlier failure then still disconnects/end-view; later steps in rejected chain may therefore be skipped.')
    js('ui-finish', 'cuw-controller', 'onClickS70126FinishBtn', ('ProgressState.END', 'controller.clearServerData()'),
       'Ordinary finish marks END and clears server data; Mazda15GA follows S701108 instead.')
    js('ui-finish-cleanup', 'cuw-controller', 'cancelingSleepMode', ('clearStatusOfReprogramming(true)', 'model.cancelingSleepMode()', 'controller.disconnect()', 'showEndView()'),
       'Normal cleanup ultimately force-clears status, cancels sleep suppression and disconnects; failure path still disconnects and finally displays end view.')
    js('ui-disconnect', 'cuw-controller', 'disconnect', ('model.gtsDisconnect().then(function(){return model.disconnect()',),
       'UI closes GTS platform session before CUW backend session; native lifetime remains backend-owned.')
    js('key-init', 'key-worker', 'initEcuSecurityKey', ('2592000000', 'getEquippedEcuList()', 'subaruEcuExists', 'suzukiEcuExists', 'checkDisconnected:true'),
       'MACKey UI removes saved exchange XML/JSON >=30days old, enumerates equipped ECUs and chooses ordinary, Suzuki or Subaru family; per-ECU disconnect status is refreshed.')
    js('key-server', 'key-worker', 'serverCommunication', ('sendMACKey_url', 'getMACKeyInfoRequest_url', "var pendingCode='MIR2020000'", 'getMacKeyInfoRequest(requestData)', '1000'),
       'Read exchange request is posted using configured service/format; pending result polls every1s and returns success/dialog/fault status. Actual URLs/account/license values are not exported.')
    js('key-vin', 'key-worker', 'checkWriteData', ('vin === model.cache.getMACKeyInfoRequestData.vin', 'resultCode === 0', 'isValid()'),
       'Ordinary writer admission requires valid server/offline exchange object, success result and matching current VIN (padded17 chars); this is not the Subaru data gate.')
    js('key-safekey', 'key-worker', 'checkSafeKeyNumber', ('safekeyList.length !== getMACKeyInfoResult.safekeyList.length', 'safekeyValid', 'writeKey=match'),
       'Ordinary writer freshly read participant identities must match server exchange list/count; matched tuple becomes that ECU writeKey; failed ECU list is returned. Subaru has separate native-prepared matching.')
    js('key-subaru-pre', 'key-worker', 'validationPreprocess1', ('ecuInfo.ecuId === 722', 'startGeneralComm', '[0x22,0x10,0x00]', 'isSupport(0x1010)', 'battelyVoltage < 10', 'endGeneralComm()'),
       'Subaru validation admission checks central ECU722 DID1010 support and converted battery voltage>=10V; unsupported/communication/voltage failure closes general communication.')
    js('key-subaru-ig', 'key-worker', 'validationPreprocess2', ('[0x22,0x10,0x3B]', '=== 0xFF', '[0x22,0x10,0x2F]', '& 0x01', 'endGeneralComm()'),
       'Subaru validation requires IG-ON and update-status bit0; error paths return failed ECUs and close general communication.')
    js('key-subaru-validate', 'key-worker', 'validationProcess', ('validateSbrMac()', 'finally(function(){return gtsPFApi.endGeneralComm()', 'statusFlg', 'validationKeys()', 'checkUpdateStatus(targetEcuList)'),
       'Subaru validation delegates native MAC validation, always ends general communication, then maps status flags into validation/readback or selected ECU DTC checks.')
    js('key-record-integrity', 'key-worker', 'isValid', ("new jsSHA('SHA-256','TEXT')", 'data.vin + data.safekeyList.sort', 'keyInfo.safekey + keyInfo.macm1 + keyInfo.macm2 + keyInfo.macm3 + keyInfo.mack4', "shaObj.getHash('HEX').toUpperCase()", 'hashValue === data.hashValue'),
       'Exchange integrity verifies required fields and SHA256(record VIN + safekey-sorted exchange tuple strings). The VIN is supplied by the exchange record itself; this method does not read the current vehicle VIN.',
       absent=('getVin', 'padEnd'))
    js('key-subaru-data-gate', 'key-worker', 'checkWriteDataSUBARU', ('getMACKeyInfoRequestData.isValid() && model.cache.getMACKeyInfoRequestData.resultCode === 0', 'dataValid=true', 'dataValid:dataValid'),
       'Subaru data-validity admission requires only exchange internal-integrity isValid() and resultCode0. Unlike ordinary checkWriteData it does not getVin or compare a current-vehicle VIN; consistently hashed different-VIN input can pass this particular gate.',
       absent=('getVin', 'padEnd'))
    js('key-subaru-controller-admit', 'key-controller', 'writingProcessSUBARUOnline', ('model.checkWriteDataSUBARU()', 'if(!result.dataValid)', 'model.writeSecurityKeySUBARU()', 'result.commError', 'result.updateFailEcuList.length', 'result.failedEcuList.length', 'controller.transitionPreviousScreen()'),
       'Subaru online controller checks its own data-validity gate then invokes Subaru writer. Invalid exchange offers server retry/previous-screen return; communication/update/ECU failures have separate return dialogs before ignition postprocessing. It does not inherit ordinary VIN or SafeKey admission methods.',
       absent=('checkWriteData()', 'checkSafeKeyNumber'))
    js('key-exit', 'key-controller', 'onClickExit', ('BUTTON_YES', 'transitionPreviousScreen()', 'BUTTON_NO'),
       'Exit asks yes/no and returns previous caller screen on yes; UI controller disposal alone does not perform native finalCom.')
    js('key-controller-return', 'key-controller', 'transitionPreviousScreen', ('ControllerTransEvent.PREV_SCREEN', 'triggerEvent'),
       'Security-key controller returns to dashboard/health-check owner by PREV_SCREEN event, not by terminating application.')
    js('key-standard-write', 'key-worker', 'writeSecurityKeyToEcu', ('writeKeyPhase4', 'writeKeyPhase5', 'writeKeyPhase6', '[0x31,0x01,0x10,0x10]', '[0x31,0x01,0xD9,0x04]', 'var maxWait=1000', '},100)', 'validateValue !== macm5Str', 'transitSession(apiParam)', 'endGeneralComm()'),
       'Ordinary non-Subaru ECU Security Key worker has direct phase-selected transports: P4 3BF5/F6, P5 RID1010, P6 RIDD904. P5/P6 zero proof polls100ms up to1000ms; returned M4/M5 are CMAC-checked; error/proof mismatch accumulates failed ECUs, restores default session and ends general communication. This is distinct from native UtilityGene selected RID3002 wrappers.')
    js('key-subaru-write', 'key-worker', 'writeSecurityKeySUBARU', ('prepareSbrMacUpd()', 'ecuInfo.ecuId === 722', 'keyCmpFlg:1', 'keyCmpFlg:0', 'updateSbrMac(apiParam)', 'resultFlg === 0', 'finally(function(){return gtsPFApi.endGeneralComm()'),
       'Subaru update uses prepareSbrMacUpd then maps returned identities to exchange tuples, tags absent matches keyCmpFlg0, invokes updateSbrMac and returns failed resultFlg0 IDs. Master/participant communication is ended in finally; native wrappers are this separate API family, not every ordinary MACKey write.')
    js('key-suzuki-admission', 'key-worker', 'checkWriteTargetSystemExistsForSuzuki', ('targetEcuIdForSuzuki', 'checkEcuConnect(apiParam)', '0xf01b', "['U131600','U131657']", 'model.cache.targetEcuList=targetEcuList', 'indexForSuzuki.ECGW'),
       'Suzuki admission enumerates known connected participants, checks EVC ROB F01B and other ECU active DTC U131600/U131657; displayed no-target flag derives from fault targets, while cached write target list is then all connected participants except ECGW.')
    js('key-suzuki-identities', 'key-worker', 'checkWriteTargetSystemStatusForSuzuki', ('getEcuInfoByEcuId(8502)', '[0x22,0x01,0x0b]', 'safekeyList.length !== getMACKeyInfoResult.safekeyList.length', 'readSafeKeyInfo.writeKey=match', 'endGeneralComm()'),
       'Suzuki exchange admission rereads gateway8502 and participant DID010B identities, requires server list/count match and associates tuples; failed communication produces failed IDs/dialog flag and attempts endGeneralComm.')
    js('key-suzuki-write', 'key-worker', 'writeSecurityKeyToEcuForSuzuki', ('[0x31,0x01,0x10,0x10]', '[0x31,0x03,0x10,0x10]', 'var maxWait=600', 'writeStatus === 0x01', 'writeStatus === 0x02', 'validateValue !== macm5Str', 'ecuId === 8508', '},700)', 'endGeneralComm()'),
       'Suzuki RID1010 writes ECU8508 first then remaining prepared participants, default->extended session, polls100ms with600ms deadline: status1 pending/status2 proof, rejects zero proof and CMAC mismatch. Each ECU attempts default-session/end communication even on failure. All-success clears mounted DTC/ROB; ROB retry waits700ms once then another immediate try.')
    js('key-suzuki-postcheck', 'key-worker', 'lastProcessForSuzuki', ('},15000)', '0xf01b', "['U131600','U131657']", 'failedEcuList.push(ecuInfo)'),
       'Suzuki final stage waits15000ms then checks connected EVC ROB F01B and other ECU DTC U131600/U131657, returning failed IDs; status-read errors are deliberately resolved rather than promoted to write failure.')
    js('key-write-admission', 'key-controller', 'writingProcessOnline', ('!result.canVinRead', '!result.dataValid', '!result.readTargetEcuExists', '!result.needWriteKey', '!result.isSafekryValid', 'model.writeSecurityKeyToEcu()', 'controller.showFirstView()', 'controller.transitionPreviousScreen()'),
       'Ordinary online writer gates current VIN, exchange validity, equipped target/status and matching safekeys before write. Each rejection exposes retry/server-requery/return choices; failed ECU write can restart first view or return; busy dialog closes in finally.')
    js('key-write-offline', 'key-controller', 'writingProcessOffline', ('model.readSelectFile(selectFilePath)', '!result.dataValid', '!result.isSafekryValid', 'model.writeSecurityKeyToEcu()', 'controller.transitionPreviousScreen()', 'finally(function(){controller.closeS33100DL003()'),
       'Ordinary offline exchange import uses the same VIN/target/status/safekey gates as ordinary online, not a privileged bypass; user returns to choose another file or previous screen on rejection.')
    js('key-server-timeout', 'key-worker', 'serverCommunication', ('var maxWait=300000', 'Date.now() - startTime > maxWait', 'return Promise.resolve(false)', "var pendingCode='MIR2020000'", '},1000)'),
       'MACKey server exchange polling is separately bounded to300000ms; pending retries1s, timeout/error yields success:false and dialog/fault fields for caller retry/offline/return.')
    js('key-subaru-validate-api', 'gts-raw-api', 'validateSbrMac', ('this.send(PFCMD_VALIDATE_SBR_MAC,param,receiveAck)',),
       'Subaru validation sends the platform utility command selected by PFCMD_VALIDATE_SBR_MAC.')
    js('key-subaru-prepare-api', 'gts-raw-api', 'prepareSbrMacUpd', ('this.send(PFCMD_PREPARE_SBR_MAC_UPD,param,receiveAck)',),
       'Subaru preparation sends the platform utility command selected by PFCMD_PREPARE_SBR_MAC_UPD.')
    js('key-subaru-update-api', 'gts-raw-api', 'updateSbrMac', ('this.send(PFCMD_UPDATE_SBR_MAC,param,receiveAck)',),
       'Subaru write sends the platform utility command selected by PFCMD_UPDATE_SBR_MAC.')
    api_ids = {
        'PFCMD_VALIDATE_SBR_MAC': 'UG000021',
        'PFCMD_PREPARE_SBR_MAC_UPD': 'UG000022',
        'PFCMD_UPDATE_SBR_MAC': 'UG000023',
    }
    api_anchors = []
    for variable, command in api_ids.items():
        anchor = f"var {variable}='{command}'"
        offset = texts['gts-raw-api'].find(anchor)
        if offset < 0:
            raise ValueError(f'Subaru API command-ID drift: {variable}')
        api_anchors.append(dict(character_offset=offset, expression=anchor))
    evidence.append(dict(id=q('key-subaru-command-ids'), source=q('gts-raw-api'),
                         kind='javascript-command-map', locator='Subaru utility command constants',
                         anchors=api_anchors,
                         finding='Signed frontend maps validate/prepare/update Subaru MAC APIs to UG000021/22/23 respectively; decimal21/22/23 equal native selectors0x15/16/17.'))

    js('saap-cuw-call', 'saap-controller', 'reprogramStart', ('CUWMain.html?P3=cuwFileList.json&P4=GTS', 'waitCuwResponse', 'cuwResponseCode === normalCode', 'win.closed', 'model.initCheckCid()'),
       'Software-as-a-Part opens CUW with P3 file list/P4 GTS, listens once for result relay, then waits for browser closure: result0 rechecks CID,1 offers retry/cancel continuation, missing result offers launch retry.')
    js('saap2-cuw-call', 'saap2-controller', 'reprogramStart', ('CUWMain.html?P3=cuwFileList.json&P4=GTS', 'waitCuwResponse', 'cuwResponseCode === normalCode', 'win.closed', 'model.clearRob()'),
       'AISAC2 uses absolute loopback HTTPS CUW URL and same relay-plus-window-close contract; normal0 clears ROB then resumes CBest check, cancel1 and absent result select distinct retry dialogs.')
    js('hino-cuw-call', 'hino-controller', 'executeCuwPlusFunc', ('CUWMain.html?P5=cuwFileList.json&P4=GTS', 'waitCuwResponse', 'cuwResponseCode === normalCode', 'win.closed', 'executeInfProcess()'),
       'Hino caller explicitly supplies P5 (not ordinary P3), subscribes to CUW result, then waits for window closure; normal0 resumes INF generation, cancel1 asks retry/continue, missing result offers retry.')
    js('ui-success-cleanup', 'cuw-controller', 'initViewS70126', ('isFlashSuccess:true', 'model.clearDTC()', 'controller.sendInfoAfterReprogramming(repInfo)', 'controller.sendReprogrammingReport(repReport)', 'model.clearStatusOfReprogramming(false)', 'SendValue.NORMAL', 'apiExclusiveControlUnlock()', 'sendLogoutControl(false)'),
       'Successful post-CID flow performs configured DTC/traceability work, sends success info/report, NON-forced native clear, restores sleep and clears server data, sends caller NORMAL, unlocks platform/logout inhibit before final Finish screen. Any rejected required step prevents the later success relay.')
    js('ui-post-cid', 'cuw-controller', 'recursiveCheckStatusAfterRepro', ('COMPLETED_CID_ACQUISITION_CANCELLATION', 'initViewS70126', 'CID_ACQUISITION_IN_PROGRESS', 'setTimeout', 'EVENT_BTN.RETRY', 'EVENT_BTN.CANCEL'),
       'Post-write CID collection has independent poll/retry/cancel states; success or completed acquisition cancellation enters report/completion, parameter/driver failure tears down.')
    js('ui-result-relay', 'cuw-model', 'sendResponseSoftwareAsAPart', ('commandId:4', 'returnValue:sendValue', 'name:model.appName', 'relayGuiMessage(param)', 'catch(function(reason){return Promise.resolve()'),
       'Embedded result is relayGuiMessage to named P4 app: from CUW, commandId4, ResultInfo success envelope and data.returnValue NORMAL0/CANCEL1; relay failures are swallowed.')
    js('ui-logout-relay', 'cuw-model', 'sendLogoutControl', ('commandId:6', 'status:isLock?1:0', "name:'GTS'", 'relayGuiMessage(param)'),
       'Logout inhibit is separate CUW->GTS relay command6 status1/0; relay failure is swallowed.')
    js('ui-report-persist', 'cuw-model', 'sendReprogrammingReport', ('CONFIG_KEY_DATA_SYNC_FOLDERPATH', 'createReprogrammingReportPath', 'model.cuwApi.createReprogrammingReport(param)'),
       'Completion report destination derives from configured DataSync folder and software ID; report contains before/new CID lists, success flag and session metadata, with no values exported here.')

    states = [dict(id=q(n), owner=o, meaning=m) for n, o, m in (
        ('external-launch', 'CUWLauncher.exe', 'File association request owns launcher mutex until CUW platform-name admission then disconnect.'),
        ('backend-idle', 'CuwBackendServiceConsoleApp.exe', 'Singleton native-session owner listening independently of browser.'),
        ('ui-connect', 'CUWMain browser page', 'Independent CUW/GTS sockets and local challenge auth followed by user login.'),
        ('exclusive', 'CUW ClientSession + GTS platform', 'CUW session lock plus platform API-exclusive/logout-inhibit ownership.'),
        ('select', 'CUW controller', 'Choose/read compatible calibration or discard/retry recovery.'),
        ('recovery', 'CUW.dll + CUW controller', 'Saved device/VIN/calibration used to validate recovery restart.'),
        ('programming', 'CUW.dll worker in backend process', 'Native engine owns programming; UI polls structured progress.'),
        ('wait-ig', 'CUW controller', 'User ignition/battery transition required between CPUs/retry.'),
        ('retry', 'CUW controller', 'User retry/cancel/whole-repro decision constrained by native retry count.'),
        ('key-wait', 'CUW.dll + CUW controller', 'Key-required native state waits online signature, offline XML, retry or cancel.'),
        ('postprocess', 'CUW controller', 'Post-write CID/vehicle information/report/readback workflow.'),
        ('ending', 'CUW controller', 'Clear native state, restore sleep, return caller result, unlock and disconnect.'),
        ('disconnected', 'CUW backend', 'Socket gone; active native state may remain and can be restored by next authenticated UI.'),
        ('stopped', 'CUW backend process', 'Allowed platform/OS ending disposes listener and leaves hidden form loop.'),
        ('utility-idle', 'GTS native utility dispatch', 'UtilityPlusFront communication not initialized.'),
        ('utility-ready', 'UtilityPlusFrontNK + UtilityGene', 'Utility session initialized, communication/keepalive state owned by frontend.'),
        ('utility-exchange', 'GTS ECU Security Key worker', 'OEM-specific exchange admission: ordinary current-VIN/participant matching; Subaru internally hashed record VIN/tuples and resultCode0, without current-VIN comparison.'),
        ('utility-write', 'UtilityGene native wrappers', 'Admitted selected identities receive returned exchange keys and per-ECU result flags.'),
        ('utility-standard-write', 'GTS signed JavaScript ECU Security Key worker', 'Ordinary phase-selected P4/P5/P6 direct GTS communication writer, distinct from Subaru native wrapper family.'),
        ('utility-return', 'GTS controller owner', 'Completed/error/cancel result returns via PREV_SCREEN; explicit finalCom releases native session.'),
    )]
    transitions = []

    def tr(name: str, frm: str, to: str, trigger: str, guard: str, action: str, *ev: str) -> None:
        transitions.append(dict(id=q(name), **{'from': q(frm), 'to': q(to)}, trigger=trigger, guard=guard, action=action, evidence=[q(e) for e in ev]))

    tr('launch-file', 'external-launch', 'ui-connect', 'Associated calibration file opened', 'Launcher mutex/install/extension route admits CUW+', 'Open local CUWMain P2 URL; register platform name and wait for CUW connection lifetime.', 'launcher-start', 'launcher-open', 'launcher-register', 'launcher-wait')
    tr('launch-health', 'backend-idle', 'ui-connect', 'GTS Health Check calibration link', 'CID supplied', 'Open separate CUW page with P1; connect/auth/login independently.', 'hc-launch', 'ui-entry')
    tr('launch-embedded', 'backend-idle', 'ui-connect', 'Software-as-a-Part/AISAC2/Hino opens CUW', 'Caller checks CUW availability or preparation succeeds', 'Open P3 file list/P4 GTS (Hino P5); subscribe result relay then wait for child window close.', 'saap-cuw-call', 'saap2-cuw-call', 'hino-cuw-call')
    tr('login-lock', 'ui-connect', 'exclusive', 'Login complete', 'CUW lock success and platform exclusive admission', 'Stop prior CID/copy work; start diagnosis/configure engine; inhibit logout.', 'ui-login', 'ui-init', 'ui-admission', 'lock', 'permission')
    tr('select-fresh', 'exclusive', 'select', 'Read native status', 'Not started and no usable saved recovery', 'Validate configured vehicle confirmation; scan calibration directories by old CID.', 'ui-admission', 'cal-search', 'cal-read')
    tr('select-recovery', 'exclusive', 'recovery', 'Read native recovery file', 'Not started and native recovery success', 'Load saved device/VIN/calibration/security metadata; show recovery choices.', 'ui-admission', 'recovery-read')
    tr('discard-recovery', 'recovery', 'select', 'User confirms recovery deletion', 'Delete chosen', 'Delete recovery file and clear saved VIN/security state.', 'ui-recovery-delete')
    tr('resume-recovery', 'recovery', 'programming', 'User retries saved session', 'VIN check and JudgeFlashable succeed', 'Start native engine with recovery marker; poll status.', 'ui-recovery', 'start-flag')
    tr('start-native', 'select', 'programming', 'User starts after calibration/J2534/battery checks', 'Native start0 or in-progress accepted by UI', 'Set backend programming flag only for native0 and show progress.', 'ui-start', 'start-flag')
    tr('poll-native', 'programming', 'programming', 'Timer poll', 'REPROGRAMMING_IN_PROGRESS', 'Update CPU/progress/remaining time then schedule next poll.', 'ui-progress', 'progress')
    tr('ig-wait', 'programming', 'wait-ig', 'Native WAITING_FOR_REPROGRAMMING', 'IG change/disconnect-battery required', 'Render inter-CPU ignition/battery prompts instead of restarting.', 'ui-progress')
    tr('ig-continue', 'wait-ig', 'programming', 'User finishes required ignition/battery sequence', 'Native/user conditions met', 'Start next programming stage and resume status polling.', 'ui-progress', 'ui-start')
    tr('retry-choice', 'programming', 'retry', 'Native preparation/reprogramming/USB error', 'Retry count <= configured normal/extended limit', 'Show appropriate adapter/USB/voltage retry/whole-repro choice.', 'ui-progress', 'ui-retry')
    tr('retry-send', 'retry', 'programming', 'User chooses Retry or Whole Repro', 'Retry notification succeeds', 'InformResultOfQueryRetry(RETRY,isWholeReproSwitched), reconnect/IG prompt as required.', 'ui-retry-send', 'retry')
    tr('retry-exhaust', 'retry', 'ending', 'Retry count exceeds limit or notification fails', 'checkMaxRetryCount < retryCount / native failure', 'Send CANCEL or failure flow; show terminal error and teardown.', 'ui-retry', 'ui-retry-send', 'ui-failure-exit')
    tr('need-key', 'programming', 'key-wait', 'Native status requires reprogramming key', 'Configured request method2 or3', 'Start/poll native request or frontend online signature workflow.', 'ui-progress', 'key-request')
    tr('key-poll', 'key-wait', 'key-wait', 'Server pending/no signature/fault/offline login', 'Pending <301000ms, or user chooses allowed fallback/retry', 'Poll1s or export request XML/import response XML; no implicit success.', 'ui-key-poll', 'ui-key-fallback', 'ui-key-offline')
    tr('key-admit', 'key-wait', 'programming', 'Signature or offline key accepted', 'Native setter/parser returns SUCCESS', 'Pass returned signature/response XML to native engine and resume progress.', 'ui-key-fallback', 'ui-key-offline')
    tr('key-cancel', 'key-wait', 'ending', 'User confirms cancellation', 'Cancel chosen', 'Cancel native request, wait until native leaves key-required/in-progress, run failure teardown.', 'ui-cancel', 'key-cancel', 'ui-failure-exit')
    tr('program-success', 'programming', 'postprocess', 'Native GetStatus returns SUCCESS', 'All target stage progress complete', 'Readback/post-write vehicle info/report flow then Finish.', 'ui-progress', 'ui-finish')
    tr('success-return', 'postprocess', 'ending', 'Post-write CID/report path succeeds', 'Required native non-forced clear returns0', 'Restore sleep/dictionary, relay NORMAL0, release platform lock/logout inhibit, render Finish; calling GTS page waits browser close before resuming.', 'ui-post-cid', 'ui-success-cleanup', 'ui-result-relay', 'saap-cuw-call', 'saap2-cuw-call')
    tr('finish', 'postprocess', 'ending', 'User Finish', 'Normal finish or OEM-specific finish stage complete', 'Set END, clear server data; force-clear native status and restore sleep.', 'ui-finish', 'ui-finish-cleanup', 'clear-xml', 'clear-flag')
    tr('fatal', 'programming', 'ending', 'Native terminal error/Promise rejection/cancel', 'Failure end flow selected', 'Failure report/caller CANCEL, platform unlock/logout inhibit release attempted; rejected step skips rest of chain but disconnect/end still follows.', 'ui-failure-exit')
    tr('disconnect-ui', 'ending', 'disconnected', 'Cleanup completion or caught cleanup failure', 'UI end path', 'Disconnect GTS then CUW session, release session lock and remove pool member.', 'ui-disconnect', 'disconnect', 'pool-remove')
    tr('disconnect-abnormal', 'programming', 'disconnected', 'Browser/socket closes unexpectedly', 'Socket event; no guaranteed force-clear', 'Attempt non-forced clear and remove pool member; native busy3007 may persist.', 'socket-close', 'native-clear', 'can-exit')
    tr('restore-ui', 'disconnected', 'programming', 'New authenticated exclusive UI connects', 'Native status not not-started', 'Restore backend dictionary and progress; do not blindly restart native operation.', 'ui-admission', 'lock')
    tr('exit-veto', 'programming', 'programming', 'Platform or OS requests shutdown', 'Programming flag true OR clients remain', 'ConfirmEnding veto000 or OS Cancel; timeout uses CanExit.', 'can-exit', 'confirm-ending', 'os-ending')
    tr('exit-allowed', 'backend-idle', 'stopped', 'Platform/OS ending accepted', 'No native programming flag and no connections', 'Suspend admission, ending callbacks, OnShutdown form close, finally Stop.', 'can-exit', 'execute-ending', 'entry-main', 'backend-stop', 'form-close')
    tr('utility-init', 'utility-idle', 'utility-ready', 'ComUtilityFront case1', 'DMGR args and Ex2initialCom succeed', 'Set native ready flag; initialize connection/negative-response/keepalive defaults.', 'utility-dispatch')
    tr('utility-sa', 'utility-ready', 'utility-ready', 'ComUtilityFront case5', 'Odd level1..0x7F and parsed arguments', 'Invoke Ex2ReqSecurityAccess; native failure maps0x90281105.', 'utility-dispatch')
    tr('utility-before', 'utility-ready', 'utility-exchange', 'Subaru MACKey case0x15 validation or0x16 before', 'Ready and supported protocol0x34; helper auth/topology succeeds', 'Return selected identities/status/M1-M3; Subaru response integrity binds its own record VIN/tuples, not a current-vehicle VIN comparison.', 'utility-dispatch', 'utility-command-map', 'gene-before', 'gene-validate', 'key-server', 'key-record-integrity', 'key-subaru-data-gate', 'key-subaru-command-ids')
    tr('utility-after', 'utility-exchange', 'utility-write', 'Subaru MACKey case0x17 after', 'Subaru internal exchange hash valid and resultCode0; six native DMGR update-data reads succeed; no current-vehicle VIN comparison in this frontend gate', 'Map server tuples to native-prepared participants with keyCmpFlg1 for matches or0 for missing matches; process master/selected participants and return per-ECU flags; native errors fail fast.', 'utility-dispatch', 'gene-after', 'key-record-integrity', 'key-subaru-data-gate', 'key-subaru-controller-admit', 'key-subaru-write')
    tr('utility-subaru-data-reject', 'utility-exchange', 'utility-return', 'Subaru online controller receives dataValid false', 'Internal record integrity false, resultCode nonzero or caught validation error', 'Do not call Subaru writer; offer server requery or previous-screen return with result-specific dialog.', 'key-record-integrity', 'key-subaru-data-gate', 'key-subaru-controller-admit')
    tr('utility-ordinary-admit', 'utility-exchange', 'utility-standard-write', 'Online/offline ECU Security Key user requests write', 'Valid VIN/exchange, admitted targets/status, fresh matching safekeys; ordinary non-Subaru/non-Suzuki branch', 'Select P4 3BF5/F6, P5 RID1010 or P6 RIDD904 directly; not native Subaru RID3002.', 'key-write-admission', 'key-write-offline', 'key-standard-write')
    tr('utility-ordinary-return', 'utility-standard-write', 'utility-return', 'All ordinary target writes complete or an ECU transport/proof fails', 'P5/P6 zero proof polls100ms up to1000ms; CMAC(MACK4,M4) must equal M5', 'Collect failed ECU IDs; restore default session and end communication; controller offers first-view retry or previous-screen return.', 'key-standard-write', 'key-write-admission', 'key-write-offline', 'key-controller-return')
    tr('utility-suzuki-admit', 'utility-exchange', 'utility-standard-write', 'Suzuki family online/offline write requested', 'Connected/fault-status admission and DID010B identities match exchange', 'Write8508 first then other participants with RID1010; status1 pending/status2 CMAC proof and600ms deadline, restore default session/end communication per ECU.', 'key-suzuki-admission', 'key-suzuki-identities', 'key-suzuki-write')
    tr('utility-suzuki-return', 'utility-standard-write', 'utility-return', 'Suzuki write loop and postcheck complete', 'Any failed ECU retained; postcheck after15000ms', 'Clear DTC/ROB only after all-success writes; final ROB/DTC faults add failed IDs; controller handles retry/return.', 'key-suzuki-write', 'key-suzuki-postcheck', 'key-write-admission')
    tr('utility-exchange-timeout', 'utility-exchange', 'utility-return', 'Configured MACKey service returns fault or stays pending past300000ms', 'Pending poll every1000ms or explicit API failure', 'Return failed/dialog/fault result for user retry/offline/previous-screen choice; never write unvalidated response.', 'key-server-timeout', 'key-write-admission', 'key-write-offline')
    tr('utility-return-screen', 'utility-write', 'utility-return', 'Done/error/user exit', 'Caller selected return', 'Return previous screen event; UI disposal alone is not finalCom.', 'key-exit', 'key-controller-return')
    tr('utility-release', 'utility-ready', 'utility-idle', 'ComUtilityFront case2 explicit finalize', 'Initialized ready session', 'Stop periodic and keepalive, finalize/reset connection parameters and clear ready even if finalCom errors.', 'utility-dispatch')

    handoffs = [dict(to_domain=domain, caller=caller, callee=callee, mechanism=mechanism, payload=payload, evidence=[q(e) for e in ev]) for domain, caller, callee, mechanism, payload, ev in (
        ('ui_ipc', 'GTS HealthCheckController', 'CUWMain.init', 'new browser page URL', 'P1=encoded old calibration ID; external launcher instead supplies P2=file path; P3=file list and P4=caller application are parsed.', ['hc-launch', 'ui-entry', 'launcher-open']),
        ('bootstrap', 'Cuw.Program.Main', 'GTSPlus error-report/lifecycle coordination', 'managed CExternalMethodWrapper callbacks', 'CUW+ PF liveness, ConfirmEnding veto string, ExecuteEnding shutdown/execute booleans.', ['entry-main', 'can-exit', 'execute-ending']),
        ('ui_ipc', 'CUWLauncher', 'GTS platform connection registry', 'loopback WSS JSON CN000001/CN000004', 'Register name CUWLauncher/maxNum2; poll name CUW existNum for admitted->disconnected completion.', ['launcher-register', 'launcher-wait']),
        ('vehicle_session', 'CUW browser', 'GTS platform', 'independent JSON socket', 'Start diagnosis; API-exclusive lock, logout-control inhibit, release VIM/transport, report and final unlock.', ['ui-login', 'ui-admission', 'ui-failure-exit']),
        ('vci_transport', 'CuwCoreModel', 'CUW.dll native engine', 'P/Invoke within backend process', 'Calibration path/mode/destination, J2534 selection, start/status, retry and forced-clear booleans; native worker owns programming lifetime.', ['cal-read', 'progress', 'retry', 'native-clear']),
        ('auth_settings', 'CUW controller/model', 'configured reprogramming signature service or offline response XML', 'platform web-service API / local file dialog', 'Method3 seed/keyPairID request; returned ID/status/signature, or saved request and imported response XML; no values exported.', ['key-request', 'ui-key-request', 'ui-key-poll', 'ui-key-offline']),
        ('operations', 'GTS Subaru ECU Security Key worker', 'UtilityPlusFrontNK.ComUtilityFront -> UtilityGene ord98/99/100', 'signed platform UG000021/22/23 -> native initialized command table selectors0x15/16/17 and DMGR native arguments', 'Initialized utility session; Subaru internally hashed exchange VIN/tuples, resultCode0 and native-prepared participant matching (not ordinary current-VIN admission); wrapper status and per-ECU result array. Ordinary P5/P6 worker takes separate direct RID1010/D904 path.', ['utility-dispatch', 'utility-command-map', 'gene-before', 'gene-after', 'key-subaru-command-ids', 'key-record-integrity', 'key-subaru-data-gate', 'key-subaru-controller-admit', 'key-subaru-write', 'key-standard-write']),
        ('ui_ipc', 'CUW postprocess/failure end', 'GTS Software-as-a-Part/AISAC2/Hino caller', 'relayGuiMessage plus browser-window-close polling', 'fromAppName CUW,commandId4,data.returnValue NORMAL0/CANCEL1 to P4 app; GTS waits win.closed before CID/ROB/CBest/INF continuation. Logout inhibit is command6,status1/0.', ['ui-result-relay', 'ui-logout-relay', 'saap-cuw-call', 'saap2-cuw-call', 'hino-cuw-call', 'ui-success-cleanup']),
        ('sync_upload', 'CUW completion model/backend', 'DataSync report consumer', 'configured output path and native report create API', 'Before/new calibration IDs, flash success flag, session metadata; report path uses configured DataSync folder/software ID.', ['ui-report-persist']),
    )]
    persistence = [dict(path_pattern=path, producer=producer, consumer=consumer, created=created, flushed=flushed, deleted=deleted, evidence=[q(e) for e in ev]) for path, producer, consumer, created, flushed, deleted, ev in (
        ('HKCU/Software/Toyota Diagnostics/Calibration Update Wizard/LastAccessFolder', 'CuwModel.StoreLastAccessFolderPath', 'GetLastAccessFolderPath / calibration file picker', 'User folder selection', 'Registry.SetValue immediate API', 'No deletion in observed folder setter/getter', ['last-folder']),
        ('CUW backend ServerData dictionary (process memory)', 'SaveData / CUW model saveReprogrammingState', 'restoreClientData after browser reconnect', 'Key/value added or overwritten during CUW workflow', 'No file flush in SaveData; lifetime is backend process', 'ClearServerData on finish/failure; process exit', ['server-data', 'ui-admission', 'ui-failure-exit']),
        ('CUW.dll recovery storage (native path list)', 'CUW native engine / SetInfoInStorageForRecovery', 'ReadRecoveryInfoFile and recovery retry UI', 'Programming/recovery storage lifecycle', 'Native implementation owns serialization', 'Explicit recovery Delete choice; not assumed deleted by every socket close', ['recovery-read', 'ui-recovery-delete', 'native-clear']),
        ('Request-reprogramming-key XML (native returned requestKeyFile)', 'SaveXMLFileForRequestReprogrammingKey', 'Offline signer exchange and LoadXMLFileForReprogrammingKey', 'User chooses offline authorization', 'Native API returns saved path; frontend reuses it', 'DeleteAllXMLFileForRequestReprogrammingKey only after native clear success', ['ui-key-offline', 'clear-xml']),
        ('configured ecuSecurityKeySavedFile/{request XML,exchange JSON}', 'ECU Security Key worker', 'OEM-specific exchange admission: ordinary current-VIN/SafeKey matching; Subaru internal record-hash/resultCode gate', 'Key read and save request or imported exchange response', 'Platform writeFile API in request workflow', 'Initialization attempts remove files >=2592000000ms (30days)', ['key-init', 'key-server', 'key-vin', 'key-safekey', 'key-record-integrity', 'key-subaru-data-gate']),
        ('configured DataSync folder/{software-ID-derived reprogramming-report path}', 'CUW completion CuwModel/CuwBackendService', 'DataSync service', 'Post-write success/failure report stage', 'CreateReprogrammingReport API', 'Consumer retention/acknowledgement belongs to DataSync domain', ['ui-report-persist', 'ui-success-cleanup', 'ui-failure-exit']),
    )]
    return dict(schema='gtsplus-lifecycle-domain-v1', domain=DOMAIN, sources=sources, evidence=evidence,
                states=states, transitions=transitions, handoffs=handoffs, persistence=persistence,
                coverage=dict(components=['CUWLauncher external file association executable (outside previous installed-root249 count)', 'CuwBackendServiceConsoleApp hidden WinForms singleton', 'CuwBackendService session/command/auth/lock/end handlers', 'CUW.dll native clear/reset/recovery interface', 'authenticated cuw.gui UI/controller/model', 'authenticated gts.gui Health Check and ECU Security Key producers', 'UtilityPlusFrontNK ComUtilityFront and recovered UtilityGene selected wrappers'],
                              entrypoints=['File association launcher startup', 'GTS HealthCheck calibration browser link', 'CUWMain init/login', 'Backend Program.Main and ClientSession JSON commands', 'ComUtilityFront cases1/2/5/0x15/0x16/0x17'],
                              branches=['Normal calibration/read/flash/progress/postprocess/end', 'Recovery resume/discard and reconnect restore', 'IG/battery/USB/adapter retry and whole-repro', 'Online key pending/timeout/fault/missing-signature/offline XML/cancel', 'Session-exclusive contention and failed command dispatch', 'Browser abnormal disconnect versus native worker lifetime', 'Busy shutdown veto/OS10s fallback/cancel-resume', 'Utility ready/protocol/SA-level/VIN/participant admission and per-ECU result return', 'Subaru-specific support/battery/IG validation and cleanup', 'Literal empty UI PC-disconnection branch']),
                residuals=[
                    dict(question='Vehicle- and service-specific success outcomes', why_unclosed='Offline execution does not provide matching calibration payload, actual ECU responses, server signature, or authenticated account session; these are runtime inputs, not missing code bodies.', next_evidence='Authorized captured transcript tied to exact calibration/ECU and configured service; never invoke from this extractor.'),
                    dict(question='Crash/power-loss durability and native worker join completion on the target OS', why_unclosed='Offline source/IL evidence identifies recovery reader/deletion ownership and the reset unbounded worker join, but does not observe target filesystem flush completion or an actual crashing worker.', next_evidence='Isolated Windows harness with fake file/J2534 interfaces and interrupted native worker; no vehicle or service access.'),
                ],
                safety=dict(mode='offline static source/IL/native-byte extraction', application_executed=False, vehicle_contact=False, network_contact=False, credentials_used=False),
                smoke_plan=['Run this extractor; it authenticates actual packaged JS and validates IL/materialized bodies/native branch bytes without loading PE code.', 'Use Node isolated VM with signed-source CuwController prototype and fake Promise APIs to exercise status SUCCESS/IN_PROGRESS/WAITING/key-required/error/PC-disconnected branches; ensure the last branch schedules no poll.', 'Use managed reflection-only/dncil decoding for CanExit/SessionEnding/lock and command ResultCode branches; do not instantiate backend listener.', 'Native Windows harness must stub imports/J2534, initialize only private synthetic state, and exercise UtilityPlusFront ready/level guard and CUW clear rejection before allowing worker/reset execution; never call real mutation exports.'],
                native_projects=['lc_cuw_utility', 'lc_cuw_utility_gene', 'lc_cuw_utility_core', 'lc_cuw_utility_adapt'])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed', type=Path, default=DEFAULT_INSTALLED)
    parser.add_argument('--cuw-root', type=Path, default=DEFAULT_CUW)
    parser.add_argument('--main-root', type=Path, default=DEFAULT_MAIN)
    parser.add_argument('--entry-root', type=Path, default=DEFAULT_ENTRY)
    parser.add_argument('--launcher-root', type=Path, default=DEFAULT_LAUNCHER)
    parser.add_argument('--aux-root', type=Path, default=DEFAULT_AUX)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = build(installed=args.installed, cuw_root=args.cuw_root, main_root=args.main_root,
                   entry_root=args.entry_root, launcher_root=args.launcher_root, aux_root=args.aux_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(f'{args.output}: {len(result["evidence"])} evidence anchors, {len(result["transitions"])} transitions')


if __name__ == '__main__':
    main()
