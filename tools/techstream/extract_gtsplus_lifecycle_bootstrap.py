#!/usr/bin/env python3
"""Extract the pinned GTS+ 2026.03.002.02 bootstrap/teardown lifecycle offline.

Defaults to the qualified aggregate's GTSPlus component. Exact manifest-relative
provenance and installed CP pins admit recovered images; full managed-body
validation classifies native/bodyless rows separately from valid IL. Semantic
body/branch pins remain exact. Explicit component roots do not use fallbacks.
"""
from __future__ import annotations

import argparse
import configparser
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tools import REPO_ROOT
from tools.techstream.extract_gtsplus_lifecycle_ui_ipc import _operand
from tools.techstream.extract_gtsplus_tse_managed_semantics import (
    _body,
    _instructions,
    _method_pin,
    _open,
)
from tools.techstream.gtsplus_local_crypto import decrypt_file
from tools.techstream.inspect_dotnet_il import format_operand, inspect_managed_bodies, resolve_token, validate_managed_bodies
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT as DEFAULT_RECOVERED, qualify_recovered_source

DEFAULT_INSTALLED = REPO_ROOT / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics/GTSPlus"
DEFAULT_MAIN = DEFAULT_RECOVERED / "GTSPlus"
DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/lifecycle_bootstrap.json"

SOURCE_PINS: dict[str, dict[str, Any]] = {'arb': {'file': 'GTSPlusArbitration.exe', 'protected': {'stub_sha256': '9f48c65cca6a91ec1e8f6dae15f04fe3f2f016f6bef7661ad2b3d3a852a5276b',
              'stub_size': 98320,
              'sidecar_sha256': '059648a21aca063c1135122c7e14124af7944930d1e21685c29f030be55a7dcc',
              'sidecar_size': 178160}},
 'pf': {'file': 'GTSPlus.exe', 'protected': {'stub_sha256': 'c2dc6d5ceefadf41165ff6be3bfc049f7bffb96f9f8bb63f26da0d851432cc24',
               'stub_size': 221200,
               'sidecar_sha256': 'd5399208fc0aa9a625b82c24c83b294f0c345ae79c0820d9a7afc8b352d90cab',
               'sidecar_size': 202960}},
 'common': {'file': 'GTSPlusCommon.dll', 'protected': {'stub_sha256': '3c1aef55d0875309217099877e7b5c3043327ff75897fdadcdc24fddcc2a883a',
               'stub_size': 53264,
               'sidecar_sha256': 'cbd0c6ae327f8be22e2fa7933c48fc3d884460216451d7d7bc309224dbd5d386',
               'sidecar_size': 118960}},
 'msg': {'file': 'MsgDatComm.dll', 'protected': {'stub_sha256': '4c513b522e58f98350d9e94c0db0b6ed3cbd30ed0d69f317e4b5921714321ccf',
               'stub_size': 69648,
               'sidecar_sha256': '6ef555bcfa2990c6ce1e9c122bcd44138f6009f94bd8668cc07317a5dd4440db',
               'sidecar_size': 125168}},
 'adapt': {'file': 'GTSPlusAdaptIF.dll', 'protected': {'stub_sha256': 'fd1868ee2cb490b0648cfe981074f03ae9c5b0f2a7adfd0646e8f866e4a4f4c4',
               'stub_size': 40976,
               'sidecar_sha256': '6671e80d4cdaa98e591375a997295b52057479cab992419db52c16eec0a876a4',
               'sidecar_size': 117648}},
 'err': {'file': 'GTSPlusErrorReport.dll', 'protected': {'stub_sha256': 'd4ba836a35c8397b5fde725f06c0effe21772819746942963c111528c06242d5',
               'stub_size': 102416,
               'sidecar_sha256': '9eef9b62fb6e83ac9c69f66440afb5353f1be6a50b955bbb93a00f1deeae2073',
               'sidecar_size': 131888}},
 'cm': {'file': 'GtsPlus-CM.dll', 'protected': {'stub_sha256': '22735bf1cad71320164a92ed14071b16d1547f63a76d85b88d612d888c459f95',
               'stub_size': 540688,
               'sidecar_sha256': 'db69e562601efdea05a06e924a9c06baf9ecee207ac3447cd0b7399e88ebce8f',
               'sidecar_size': 1350800}}}

CONFIG_PINS: dict[str, dict[str, Any]] = {'Env/ABSystem.yml': {'sha256': 'efdb6658fe0d9388177d74099170b92a243db47968688e7ca3ef1c045ac2996b',
                      'size': 1632},
 'Env/GTSPlus.pp': {'sha256': '3db86bbac46d10b0a81cefe23a922b77382db03e1b59ae95dc5a588424c61e4d',
                    'size': 256},
 'Env/GTSPlusInfo.ini': {'sha256': '6551ef8b53268645e2c690c4053f09830fc76d1d764a65fc2dbd32e3f3f6861f',
                         'size': 784}}

CONFIGURATION: dict[str, Any] = {'applications': [{'name': 'GTS+ InfoCenter',
                   'file_path': 'GtsPlus-InfoCenter\\GtsPlus-InfoCenter.exe',
                   'start_mode': 3,
                   'end_mode': 1,
                   'alive_monitor_mode': 0},
                  {'name': 'GTS+ PF',
                   'file_path': 'bin\\GTSPlus.exe',
                   'start_mode': 1,
                   'end_mode': 1,
                   'alive_monitor_mode': 2},
                  {'name': 'CUW+ PF',
                   'file_path': '..\\CUWPlus\\CuwBackendServiceConsoleApp.exe',
                   'start_mode': 1,
                   'end_mode': 1,
                   'alive_monitor_mode': 2}],
 'services': [{'name': 'GTS+ DataSync', 'end_mode': 0, 'alive_monitor_mode': 2},
              {'name': 'GTS+GUIServer', 'end_mode': 0, 'alive_monitor_mode': 2}],
 'timeouts_ms': {'application_confirm_start': 180000,
                 'application_confirm_end': 5000,
                 'ab_app_confirm_end': 5000,
                 'alive_monitor_interval': 2000,
                 'alive_monitor_freeze_timeout': 60000,
                 'session_end_check': 10000},
 'version': {'folder': 'Ver', 'manifest': 'Manifest.json', 'component_extension': 'json'},
 'report_limits': {'trace_trigger_max_count': 4,
                   'action_log': {'string_max_length': 2000,
                                  'buffer_max_count': 10000,
                                  'temp_save_interval': 1000,
                                  'temp_file_max_size': 10485760,
                                  'temp_file_max_count': 5},
                   'communication_log': {'string_max_length': 20647,
                                         'buffer_max_count': 3000,
                                         'temp_save_interval': 1000,
                                         'temp_file_max_size': 10485760,
                                         'temp_file_max_count': 5}},
 'report_includes': ['Env\\GTSPlusCommon.gstg',
                     'Env\\DistDep.gstg',
                     'Env\\PcSettings.gstg',
                     'Env\\VehicleConfigure.gstg',
                     'Env\\PF.cfg',
                     'Work\\TSE1\\activityreport.json'],
 'report_include_one': {'extension': '.txt',
                        'folder': '%PUBLIC%\\Documents\\GTSPlus\\ReproLog',
                        'order_by': 1}}
SOURCE_PINS["pfc"] = {'file': 'GTSPlusPFCommon.dll', 'protected': {'stub_sha256': '47a9e9a5b5623a37cdb7bd5d8e7616bfeb6c2fa9b2d0f5d37509e75562807079', 'stub_size': 172048, 'sidecar_sha256': 'ffd6f98fdeee317635ab52e7f6ec02f08596d62d0a63e7f36e293605a964ab2e', 'sidecar_size': 123360}}
CONFIG_PINS["Env/GTSPlusSetting.ini"] = {'sha256': '3b49eb5facfc3c0a4bbdeeda99ae0928dc62357a3d120cc9540bfda8e5e7a117', 'size': 656}
RETENTION_PLAINTEXT_SHA256 = 'e27a124952d6ff4dfaa69f7b63e844c8e2062f30ca88034428d6b9722583ad14'


METHODS = (
    ('bootstrap.arb-entry', 'arb', 21396, 456, '738cc39233882a6d460e082df3666c6bc934ab05089009940d8ce27b5b252761', 'GTSPlusArbitration.Program::Main', 'Global\\ABAppMutex WaitOne(0,false); owner InitializeForm/Run/release; contention launches InfoCenter_Multi with cwd=executable parent. Exceptions log and return; no args parser or retry.', [(31, '72990e0070'), (53, '2c2a'), (78, '2c06'), (146, '28ca00000a'), (255, '2c06')]),
    ('bootstrap.pf-entry', 'pf', 40420, 101, 'faa455adb37b27d5ed01a07c83a17df98a87970863561cd4dba5571024c15dfe', 'GTSPlusController.Program::Main', 'Main() ignores CoInitializeSecurity HRESULT (auth1,impersonation3), starts STA thread and joins.', [(40, '2d17')]),
    ('bootstrap.pf-single-instance', 'pf', 89000, 432, '849e788f234d5f00e9e7774f95fafc60b8562012495d9898163fcac7f66656bc', '<>c::<Main>b__4_0', 'Global\\GTSPlusMutex nonblocking; owner constructs MainTask/Form1, Run only if not disposed; contention launches InfoCenter_Multi; exceptions log/return.', [(31, '72074d0070'), (53, '2c2f'), (83, '2d06'), (151, '280b03000a'), (246, '2c06')]),
    ('bootstrap.arb-initialize', 'arb', 8724, 756, '9bc0de78899f33d71e431642f3c6cf4390aed9a8feb810188ed066743c1aff61', 'GTSPlusArbitration.Form1::InitializeForm', 'Subscribe session-ending; require ABSystem decode; read distributor fallback; end receiver; error-report initialization; hook/hotkey/end/report workers; StartApplication; version check; service monitors; alive monitor and communication. Exception returns false.', [(25, '2d08'), (78, '2d37'), (318, '2834000006'), (345, '2d0e'), (407, '2d06'), (440, '2c49'), (522, '2d9c')]),
    ('bootstrap.arb-settings', 'arb', 10628, 400, '2710cfc46c98cec29e71af8c107ce4a184cf5db169b5f159574ef1aea78b6e0b', 'GTSPlusArbitration.Form1::ReadABSystemSetting', 'Decrypt install/Env/ABSystem.yml with kind1; nonzero aborts; strip header line; validating YamlDotNet deserialize. Exception returns false.', [(25, '2c5a'), (153, '2d17'), (184, '2d17'), (243, '2c07')]),
    ('bootstrap.arb-distributor', 'arb', 11028, 280, '34b3e8f695654a829e52e71eb0d6bca7f3f5b2034eb8c9b5d426afe8ab2a9e64', 'GTSPlusArbitration.Form1::ReadDistributorDepending', 'Distributor setting read type2: success disables DefaultStart; failure constructs loglevel3/compression3/level9/hotkey121 modifier2 defaults and enables restricted DefaultStart.', [(16, '2d0f')]),
    ('bootstrap.arb-launch', 'arb', 15060, 1312, 'd2c3632733ba058b2a859c2edeb4b68d466443f4187947cdfd5dbaeae022457d', 'GTSPlusArbitration.Form1::StartApplication', 'Sequential applications; normal launches all, DefaultStart only StartMode2/3; relative path from install root, cwd=exe parent, no arguments assigned. Modes1/3 wait ER_ApplicationStart using remaining timeout; mismatched PID loops, matching nonempty ResultCode notifies failure. Timeout/exception marks failed and continues; no retry launch.', [(41, '2d06'), (87, '2c20'), (95, '3919030000'), (107, '2e0c'), (116, '4004030000'), (703, '2c07'), (883, '2c07'), (902, '2c75'), (926, '2c43'), (1028, '3a33fcffff')]),
    ('bootstrap.arb-version', 'arb', 16932, 856, '0d0fa8d407fa9756b0611dd81446cd01713c5e981b9697755ca3f35e5f3db9f6', 'GTSPlusArbitration.Form1::ConfirmApplicationVersion', 'Postlaunch manifest/component version mismatch AB000005+name; component-read failure AB000004+name; manifest failure AB000003. Notify/log and continue, not startup veto.', [(23, '2d28'), (113, '2c06'), (252, '3982000000'), (391, '2c07'), (529, '3a89feffff'), (557, '3a55feffff')]),
    ('bootstrap.arb-confirm', 'arb', 12268, 1428, '9fd97feb1d02a5caf48429a2a5a1bae02abe9649c9964bb94270e096ed0c5103', 'GTSPlusArbitration.Form1::ConfirmEnding', 'Only EndMode1 app/service confirmations; nonempty ResultCode vetoes. Pipe exceptions log/continue. Saving report waits until configured ABAppConfirmEndTimeout then AB000002 veto. Outer exception logs then returns true (fail-open).', [(12, '2d06'), (46, '4072010000'), (51, '72d9020070'), (141, '2d79'), (268, '2c07'), (739, '2c07'), (889, '3a63feffff'), (933, '3998000000'), (961, '3151'), (1050, '2d17')]),
    ('bootstrap.arb-execute', 'arb', 13696, 1364, '7518f85e51ef899ef86361e786c52a04e59a8c969f642273691479c961508669', 'GTSPlusArbitration.Form1::ExecuteEnding', 'Send Shutdown/Exucute over ER_EndingExecute_<name> to EndMode1 apps/services; flush/drain. Execute=true waits unbounded for full-path-matching app exit. Other EndMode apps are killed only if execute=true, after remove monitor. Execute=true closes own form. Per-target exception logs/continues.', [(61, '2d06'), (105, '2d0f'), (130, '405c010000'), (135, '7203050070'), (233, '2c07'), (675, '7203050070'), (773, '2c07'), (787, '2c07'), (938, '3adefeffff'), (960, '2c13')]),
    ('bootstrap.arb-session', 'arb', 10468, 160, 'ed915a55e2781a2cf3bd08c4e869cea3c93b87fa05903df8fea9580ea3acdf1f', 'GTSPlusArbitration.Form1::SystemEvents_SessionEnding', 'ConfirmEnding then SetAppEndState only on approval; ExecuteEnding(true,approval); veto cancels Windows session end.', [(8, '2c0b'), (30, '2d07'), (34, '6f5f00000a')]),
    ('bootstrap.arb-end-request', 'arb', 23868, 612, 'a717252f1f7e9161719a8324a1e10dfbbaa2806d54598e946da3b4f9404be934', '<EndABAppAsync>d__92::MoveNext', 'ER_ABAppEnd async server: cancellation-aware wait, confirm, mark end state on approval, ExecuteEnding(false,approval), reply ABAppEndData.Result flush/drain, loop; cancellation exits, other exception logs/stops receiver.', [(18, '2c18'), (21, '7289100070'), (49, '2c52'), (58, '2814000006'), (63, '6fcd00000a'), (200, '2c0b'), (275, '2f0b'), (279, '2c07'), (293, '2f13'), (301, '2c0b')]),
    ('bootstrap.arb-child-end', 'arb', 24496, 556, '03938c7876391294b00a80529372ff674fd608cfcda6486c02d49f5e26e96ecf', '<EndApplicationAsync>d__96::MoveNext', 'ER_ApplicationEnd async receiver removes monitor for received ProcessId then loops; cancellation exits and other exception logs/stops. No restart.', [(18, '2c18'), (21, '72d7100070'), (49, '2c51'), (58, '2814000006'), (63, '6fcd00000a'), (95, '2d3f'), (222, '2f0b'), (226, '2c07'), (240, '2f13'), (248, '2c0b')]),
    ('bootstrap.arb-close', 'arb', 10204, 264, '6eadf008c78060f341d45e80411d07f276593ecb7a5824e03f455f08bbcaff56', 'GTSPlusArbitration.Form1::Form1_FormClosed', 'Cancel token; EndAppCommunication; StopAliveMonitor; signal AB_ErrorReportSave; join save/end/hotkey tasks; keyboard unhook; FinalizeErrorReport; unsubscribe session-end. Exception aborts remaining teardown after log.', [(1, '2814000006'), (6, '6f5800000a'), (51, '2c06'), (109, '6f5c00000a')]),
    ('bootstrap.pf-form-init', 'pf', 30736, 231, 'b0dcd54d4ce0f20afc98bb39bebb2c29e19593625721905da48bdd443f8aa0df', 'GTSPlusController.Form1::.ctor', 'InitializePlatform result0 registers GTS+ PF communication/alive callbacks, sends successful startup notification, registers ending callbacks. Nonzero sends remembered error then closes form; IPC boolean returns ignored.', [(37, '2d04'), (43, '2837010006'), (53, '2d7f'), (83, '6fce00000a'), (117, '6fd000000a'), (134, '6fd100000a'), (175, '6fd400000a'), (195, '2d04'), (206, '6fd100000a')]),
    ('bootstrap.pf-init', 'pf', 32832, 852, '8ebcf3149fbb10861c61d7bf14189a9fa702259d46d16e14118e0a8137cc1e59', 'GTSPlusController.MainTask::InitializePlatform', 'ConnectionManager, SetApplicationInfo, ResetPFConfig, InitializeAdaptation, five worker construction/init, sleep timer50000ms, StartMainSequence, AutoDelete/AutoSaveDelete timers. Early info/config/adaptation/worker failure returns. StartMainSequence result overwritten by setting lookup; AutoDelete StartTime<=0 returns current result, possibly success. Exceptions return logged failure.', [(30, '2c12'), (56, '6fc3000006'), (68, '2c12'), (106, '2c12'), (157, '282d010006'), (528, '2839010006'), (533, '0a'), (534, '280701000a'), (539, '280801000a'), (544, '1201'), (546, '280901000a'), (551, '0a'), (552, '06'), (553, '6f5a00000a'), (558, '2d04'), (560, '07'), (561, '16'), (562, '3007'), (564, '06'), (565, '0d'), (566, 'ddec000000'), (630, '280901000a'), (642, '2c07'), (653, '312f')]),
    ('bootstrap.pf-reset-config', 'pf', 28692, 248, 'e92675532a44eb52e58faa20115b91b905fcc1deb8fb53e91bdd6f2acb74973c', 'GTSPlusController.ConnectionManager::ResetPFConfig', 'Copy install Env/DefaultPF.cfg over SettingFileWrapper folder/current PF.cfg when default exists. Missing default tolerated; folder/copy failure returns error.', [(49, '2c3b'), (129, '2c09')]),
    ('bootstrap.pf-sequence', 'pf', 34344, 150, '6a2fcd28c7bda55da71228356c3d1ee17d04af8c08eb60ed97258f25dd26db65', 'GTSPlusController.MainTask::StartMainSequence', 'Start settings receiver, workers, managed WebSocket StartProcess, then main-task async before testing WebSocket result. False stores PF000002 and returns failure; no child Process.Start here.', [(27, '2d03'), (45, '32e8'), (75, '2d2f')]),
    ('bootstrap.pf-loop', 'pf', 34564, 1684, 'e070eb5b3413844d9d3b66d53e9a2d215a098f9825f9c8f567d447aa2bc70537', 'GTSPlusController.MainTask::StartMainTask', 'Poll/fetch/analyze/queue messages until cancellation requested. EndCheckFlag waits main confirmation barrier; EndFlag alone does not stop loop. Named events wake API workers.', [(240, '397f040000'), (251, '2c07'), (285, '2c11'), (340, '3974020000'), (357, '4063020000'), (1441, '2c07'), (1453, '2c07'), (1465, '2c07'), (1477, '2c07'), (1488, '2c06')]),
    ('bootstrap.pf-confirm', 'pf', 36844, 215, 'a39d8be537b23017cc765a540af5c000384aeeb638c3fc491b048607f73f4d1a', 'GTSPlusController.MainTask::AbAppEndConfirmSequence', 'Reset seven confirmation barriers; set main/worker EndCheckFlag; CheckEditFile true returns PF000003 veto, false empty approval. Does not itself wait barriers.', [(116, '72a82f0070'), (155, '2c07'), (172, '32e8'), (180, '6f2801000a'), (185, '2c08')]),
    ('bootstrap.pf-execute', 'pf', 37060, 202, 'ec23fb9a3feb1caf9be1c442cdf1d33062bc825483a7a273f6c1b16a6d654a36', 'GTSPlusController.MainTask::AbAppEndExecuteSequence', 'Execute=true clears queues IDs1..6; nonshutdown sends CN000008/id10 GUI broadcast; sets worker/main EndFlag. Always ResetEndCheckFlag. Execute=false resumes operation.', [(1, '39b1000000'), (28, '31ec'), (31, '2d64'), (153, '2c08'), (174, '32e1')]),
    ('bootstrap.pf-unfreeze', 'pf', 36660, 181, '63ee4d78eb5c5b944d5b7e26e0343e3e3aa15de1e5aa5b85a443a58a892bb1a9', 'GTSPlusController.MainTask::ResetEndCheckFlag', 'Clear EndCheckFlag on main/workers and Set all seven confirmation barriers, releasing paused work.', [(23, '2c07'), (40, '32e8'), (152, '72a82f0070')]),
    ('bootstrap.pf-execute-callback', 'pf', 31324, 88, '7bb9825c6e49a4abc14efa9c66a6fecc26fdbe1a9abcb95b4624bc0cac5b899c', 'GTSPlusController.Form1::CallbackAbAppEndExecute', 'Delegate end execution; execute=true closes form, false resets barriers; shutdown stores EndExecuteFlag and Set GTSP_END_SESSION_EVENT.', [(7, '2d03'), (20, '2c08'), (37, '2d03'), (48, '2c19')]),
    ('bootstrap.pf-session', 'pf', 31176, 120, 'bd465f682db37b6485ca95a898e2a5a5120d4b2e9a6bb08de20935e62e7f5112', 'GTSPlusController.Form1::SystemEvents_SessionEnding', 'Wait GTSP_END_SESSION_EVENT for configured timeout; signaled plus EndExecuteFlag=false vetoes; timeout runs own end confirmation and vetoes nonempty result.', [(27, '2c11'), (35, '2d29'), (39, '6fe500000a'), (53, '2d04'), (69, '2d07'), (73, '6fe500000a'), (81, '2c06')]),
    ('bootstrap.pf-timeout', 'pf', 31412, 79, '73377b8b1cdc7aeffe5b09ddf4a5d6c2db55fb639878806b3da6ea30f6adbe04', 'GTSPlusController.Form1::GetSessionEndTimeOut', 'Default session coordination10000ms; encrypted GTSPlusInfo.ini AppInfo/SessionEndCheckTimeout overrides only when positive; failed decode retains default.', [(33, '2d02'), (61, '3102')]),
    ('bootstrap.pf-close', 'pf', 30968, 129, '22ab1ea159a13bc6038b65214d31c96a28e3b4393fadf26b5a47be682ae03525', 'GTSPlusController.Form1::Form1_FormClosed', 'FinalizePlatform; ER_EndApplicationCS; stop alive/ending/communication workers; reset barriers; unsubscribe Windows session/network events.', [(7, '2d03'), (12, '2838010006'), (23, '6fd600000a'), (35, '6fd700000a'), (47, '6fd800000a'), (59, '6fd900000a'), (72, '2d03')]),
    ('bootstrap.pf-finalize', 'pf', 33684, 660, 'e1a67a40fceb16528355e802ca154f73325c33d96cb60f087fd08a68caab5b72', 'GTSPlusController.MainTask::FinalizePlatform', 'Cancel token; stop WebSocket; wait main; signal worker events and wait each worker; FinalizeAdaptation; wait settings receiver; stop sleep timer. Waits unbounded; broad exception logs then aborts remaining teardown, no retry.', [(0, '282d010006'), (5, '6f0b01000a'), (155, '2d17'), (210, '2c20'), (251, '2dc5'), (310, '2c06'), (322, '2c06'), (337, '6f1401000a'), (418, '72ca2b0070'), (462, '72042c0070')]),
    ('bootstrap.pf-alive', 'pf', 36248, 129, '1f740563395e03543ded1120c2cba6bb81647a54454f370ff8967ddecc1f3bc9', 'GTSPlusController.MainTask::CallbackAbAppAliveMonitorCheck', 'Main task, worker tasks and inner settings receiver task must have TaskStatus1 (WaitingForActivation) else PF000005; otherwise return remembered error or empty.', [(18, '2e06'), (38, '2c1b'), (59, '2e06'), (83, '32c9'), (102, '2e06')]),
    ('bootstrap.pf-settings-error', 'pf', 87500, 728, 'dfd2cd02f346e6ed946a4c95caf7d0014d086c8c781f7f5121399cece7a8e461', '<SettingFileErrorReceive>d__82::MoveNext', 'SettingFileTampering_<PID> server reads UTF8; UserProfile/VehicleConfigure excluded from global flag; other messages set all GUI tamper flags and remember PF000004. Successful receive loops; cancellation exits; other exception logs/stops.', [(18, '2c31'), (74, '2c53'), (82, '282d010006'), (87, '6f0201000a'), (92, '6fe002000a'), (347, '2c48'), (361, '2c3a'), (380, '2d17'), (425, '2f13'), (433, '2c0b')]),
    ('bootstrap.path', 'common', 9340, 368, '93399d4ad3d79e29aea097e9380b2e4f6143b30cba53e434052fdeea04bb9fd9', 'GTSPlusCommon.Function.PathFunction::GetInstallFolderPathCS', 'CustomSetting.yml InstallFolderPathGetRegistry defaulttrue; read exceptions reverttrue. Relative GTSPlusInfo.ini provides registry path; HKLM RootFolder used if config allows, missing registry yields empty. Disabled/failed config gate falls back to parent of DLL directory.', [(30, '2c6e'), (125, '2c07'), (143, '2c46'), (155, '2c38'), (169, '2c26'), (199, '2d04'), (216, '2c40'), (234, '2c20'), (260, '2c06'), (272, '2c07')]),
    ('bootstrap.path-constants', 'common', 10936, 103, '907e4de61a75b9e2564c8dafbc55b1b0b3c9288ddeba709d964041306cd8c421', 'PathFunctionConstants::.cctor', 'Relative files ..\\Env\\GTSPlusInfo.ini and ..\\Env\\CustomSetting.yml; registry RootFolder; duplicate target GtsPlus-InfoCenter\\GtsPlus-InfoCenter_Multi\\GtsPlus-InfoCenter_Multi.exe.', []),
    ('bootstrap.decrypt', 'common', 8516, 127, '8534c38493713c47b5602dbcea11ae9057cb6a544a651a51cab3e9dfcd547352', 'GTSPlusCommon.Wrapper.CryptManagerWrapper::DecryptFileCS', 'Managed native boundary authenticates CM once, selects packaged passphrase profile, calls DoFileDecryptionCS with SecretKeyType2; status0 UTF8 strips NUL, failure outputs empty.', [(5, '2d14'), (12, '2d0d'), (60, '2805000006'), (66, '2d27'), (90, '320b')]),
    ('bootstrap.packaging-profile', 'common', 9000, 232, '86c2ab18b1067b27cb86221d23ba1108bd26f411842b9f693cfc1f871c05f576', 'GTSPlusCommon.Wrapper.CryptManagerWrapper::GetPassphraseFilePath', 'Kind2 selects error-report passphrase profile; other kinds ordinary profile; CustomSetting override optional; combines with install root.', [(14, '3308'), (40, '3986000000'), (97, '331d'), (165, '2c06')]),
    ('bootstrap.ini-decrypt', 'common', 9760, 268, 'e31907c3972a539de01e94ed4c878dbc199246228a13912348144c6713dfe0d6', 'GTSPlusCommon.Function.CryptographicFunction::LoadEncryptFile', 'LoadEncryptFile reads IV prefix then AES-CBC decrypts remaining bytes with fixed embedded packaging material; UTF8 output; read/decrypt exception returns false.', [(46, '2c07'), (144, '6f3300000a'), (181, '2c07')]),
    ('bootstrap.ini-material', 'common', 10028, 32, 'e94be829d1d68280be35af491da01a704f5c451e456e68f99c5784da406277f0', 'GTSPlusCommon.Function.CryptographicFunction::.cctor', 'AES IV size16 and key byte-array populated from FieldRva via RuntimeHelpers.InitializeArray; extractor derives material without disclosing it.', []),
    ('bootstrap.msg-start', 'msg', 8448, 268, '91d7fda103cb9138070c30d63aca426c1c220b42b9321330dbc976526ba689c4', 'MsgDatComm.CExternalMethod::ER_StartApplicationCS', 'ER_ApplicationStart client sends current PID/ResultCode; Connect(1ms), serialize, flush/drain. Failure logs false; caller ignores.', [(34, '72f7040070'), (88, '2c06'), (100, '2c06')]),
    ('bootstrap.msg-end', 'msg', 8716, 260, '17e8fe3bc92bca6f951510497d86835adfb87920b9be3cd0cb88a14ce4c9cac2', 'MsgDatComm.CExternalMethod::ER_EndApplicationCS', 'ER_ApplicationEnd client sends current PID; Connect(1ms), serialize, flush/drain; failure logs false.', [(27, '7269050070'), (81, '2c06'), (93, '2c06')]),
    ('bootstrap.msg-end-servers', 'msg', 11180, 264, 'eacbbcb655d9167f5a006f0d4869136edcd59d47d4c638c785a1cea2758f616e', 'MsgDatComm.CExternalMethod::ER_StartWaitForEndingCS', 'Duplicate registration rejected; start cancellation-owned confirm/execute server tasks, store for joining.', [(12, '313d'), (81, '2806000006')]),
    ('bootstrap.msg-confirm', 'msg', 18100, 612, '524d9ed5dc4fd6dcbff74d415a02d9464c971f3fb4f3bdca8214f684e8c274ae', '<ConfirmEndingAsync>d__87::MoveNext', 'ER_EndingConfirm_<name> waits cancelably, invokes callback, writes result, flush/drain, repeats. Wait cancellation exits; other exception logs/stops.', [(18, '2c2f'), (21, '7275010070'), (72, '2c52'), (81, '2805000006'), (86, '6f1200000a'), (119, '2d3f'), (268, '2f0b'), (272, '2c07'), (286, '2f13'), (294, '2c0b')]),
    ('bootstrap.msg-execute', 'msg', 20332, 596, 'a30fe593b267d30f6f50e638e512db3be12b697f894d4d3dcb3fba06c69990cb', '<ExecuteEndingAsync>d__88::MoveNext', 'ER_EndingExecute_<name> waits cancelably, reads Shutdown/Exucute and invokes callback, repeats. Cancellation exits, other errors log/stop.', [(18, '2c2f'), (21, '7221040070'), (72, '2c51'), (81, '2805000006'), (86, '6f1200000a'), (118, '2d3f'), (252, '2f0b'), (256, '2c07'), (270, '2f13'), (278, '2c0b')]),
    ('bootstrap.msg-alive', 'msg', 16672, 612, '2a683cecf2a8b54494ff1cb36400362781a2955dec091828a382fc8701c2d441', '<AliveMonitorAsync>d__86::MoveNext', 'ER_AliveMonitor_<name> server callback produces ResultCode; flush/drain; loops; canceled wait exits, other error logs/stops.', [(18, '2c2f'), (21, '7201000070'), (72, '2c52'), (81, '2801000006'), (86, '6f1200000a'), (119, '2d3f'), (268, '2f0b'), (272, '2c07'), (286, '2f13'), (294, '2c0b')]),
    ('bootstrap.adapt-init', 'adapt', 8384, 1112, 'd1b69135337513b1fdd9efb9ba0e55fb34899ae6513cbcaf8c317152ac10234f', 'GTSPlusAdaptationIF.AdaptationInterface::InitializeAdaptation', 'Embedded XML table order: require module file; Assembly.LoadFrom/CreateInstance; AuthenticateAdaptation challenge/authorization with packaged configuration; InitializeAdaptation. Missing/load/auth/init failures return error, no retry.', [(187, '39a5020000'), (249, '39c1010000'), (299, '2c74'), (583, '2d68'), (693, '2c07'), (720, '2c30'), (960, '3ad7fcffff')]),
    ('bootstrap.adapt-finalize', 'adapt', 9496, 292, '7d99002c332a4897a95b27f2de7384814832f3aa1d5b1ca06c96b975d1ed7ad5', 'GTSPlusAdaptationIF.AdaptationInterface::FinalizeAdaptation', 'Finalize modules in original table order; per-module error logs/aggregates and continues. Platform ignores aggregate result.', [(64, '6f4a00000a'), (76, '2c1e'), (154, '72e3010070'), (226, '3a4bffffff')]),
    ('bootstrap.arb-notify', 'arb', 16440, 492, '11e17f05bb28aa56d07355c245fc041ca387cf489ea7f5d60b27a6a04d68cdba', 'GTSPlusArbitration.Form1::NotifyError', 'Send ErrorNotifyData timestamp/source/code via ER_ErrorNotify then save trace/screen bounds using configured trigger count; errors log; no restart.', [(40, '2d0b'), (65, '726b070070'), (117, '2c07'), (130, '2c06'), (146, '2807000006'), (268, '32d9')]),
    ('bootstrap.alive-app', 'err', 9496, 1316, '991d0ebc1ad0d644a8f8bae36e31767c74f3e16406836adcf8f4bc712acded1b', 'GTSPlusErrorReport.AliveMonitorTask::ConfirmAliveMonitorApplication', 'Match PID; probe main window using SendMessageTimeout; mode2 additionally queries ER_AliveMonitor_<name>. Missing process disables monitor. Prior healthy-to-failure notifies AB010001/AB010002 or returned code, store last result; no restart/kill.', [(19, '3a04040000'), (48, '39cd030000'), (89, '40ed000000'), (113, '39d5000000'), (131, '2d07'), (771, '2c07'), (785, '2c07'), (811, '399c000000'), (1016, '2c07'), (1047, '3ff1fbffff')]),
    ('bootstrap.alive-service', 'err', 10812, 1168, 'e3ad9ce73de36e9ad34965330634d664a9f7343e8833c4c00f8bfb988183494a', 'GTSPlusErrorReport.AliveMonitorTask::ConfirmAliveMonitorService', 'ServiceController.Status==Running(4), mode2 additionally queries ER_AliveMonitor_<name>; prior healthy-to-failure notifies AB010001/AB010002 or returned code then stores result; does not start/restart service.', [(13, '3a79030000'), (42, '3942030000'), (68, '3b90000000'), (81, '3983000000'), (232, '399c000000'), (628, '2c07'), (642, '2c07'), (667, '399c000000'), (871, '2c07'), (902, '3f7cfcffff')]),
    ('bootstrap.arb-paths', 'arb', 20876, 103, '8178d71648f1ec7d5dd90fda24d71cb150ecf84ff4cc1d4f49ac8fec7c9f7101', 'GTSPlusArbitration.Form1::.cctor', 'Default reports GTSPlus/ErrorReport/{ActLog,ComLog,Trace,TraceAutoSave,Unsend,Send}, DataSync/Logs/GTS-E02; ABSystem Env/ABSystem.yml; .gtsr extension.', []),
    ('bootstrap.retention-setting', 'pfc', 19612, 283, 'c581a31022d4a545df628f3dcb03f7b102aa8a92ee184697356c5dc03b2595ff', 'GTSPlusPFCommon.Function.CommonFunction::GetGTSPlusSetting', 'Read install/Env/GTSPlusSetting.ini; require file/decrypt(kind1) success, strip header, parse requested integer. Missing file/decrypt error returns failure; out value defaults0.', [(2, '720f010070'), (57, '720f010070'), (78, '720f010070'), (89, '7265070070'), (132, '286900000a'), (199, '720f010070'), (220, '720f010070'), (231, '729f070070')]),
    ('bootstrap.retention-constants', 'pfc', 21760, 173, 'd4f1dbd08b4dd8d75b6f23fadf5d89318b5342810506c29df1976ac3d55d2cb5', 'GTSPlusPFCommon.Constants.PFCommonConstants::.cctor', 'Startup timer sections AutoDeleteGTSE and AutoDeleteAutoSaveErrorReport; keys MaxCount/StartTime; current PF config PF.cfg, settings under Env.', [(0, '72070a0070'), (10, '720f0a0070'), (20, '72170a0070'), (30, '72250a0070'), (40, '724b0a0070'), (50, '725d0a0070'), (60, '727b0a0070'), (70, '728d0a0070'), (80, '72a50a0070'), (90, '72cf0a0070'), (100, '72e30a0070'), (110, '72010b0070'), (120, '723d0b0070'), (130, '724f0b0070'), (140, '72630b0070'), (150, '72750b0070')]),
    ('bootstrap.delete-gtse', 'pf', 38484, 620, '174c9e146d2501a115ba9b246bec7054aff7a3be1fef457a3aa7fb6b420be9d7', 'GTSPlusController.MainTask::DeleteGTSEFileTimerElapsed', 'One-shot timer stops itself; resolve configured UserStoredData folder, read MaxCount and if nonnegative enumerate *.gtse, order descending by LastWriteTime, skip newest MaxCount, delete remaining until EndFlag. Exceptions log; no timer restart here.', [(1, '2819010006'), (6, '6f1601000a'), (34, '72eb070070'), (56, '72eb070070'), (67, '7266310070'), (194, '72eb070070'), (216, '72eb070070'), (227, '72d0310070'), (326, '280901000a'), (350, '722e320070'), (436, '286b01000a'), (481, '72eb070070'), (503, '72eb070070'), (514, '723c320070')]),
    ('bootstrap.delete-report', 'pf', 39104, 724, '51f74fffac01f528ac37ad7cc01e0758b00386b0d199b4fc22ff602c22f21f7f', 'GTSPlusController.MainTask::DeleteErrorReportAutoSaveFileTimerElapsed', 'One-shot autosave cleanup stops timer; combine configured ErrorReport AutoSaveUnsend/AutoSaveSend folders, read nonnegative MaxCount, combine *.gtsr, order descending by LastWriteTime, skip newest MaxCount and delete remaining until EndFlag. Exceptions log; no restart here.', [(1, '281b010006'), (6, '6f1601000a'), (34, '72eb070070'), (56, '72eb070070'), (67, '7266310070'), (269, '280901000a'), (301, '72eb070070'), (323, '72eb070070'), (334, '729c320070'), (404, '7218330070'), (437, '7218330070'), (545, '286b01000a'), (588, '72eb070070'), (610, '72eb070070'), (621, '7226330070')]),
    ('bootstrap.retention-order-key', 'pf', 87458, 8, '4a1541f0a572908d22e2ea7fece28e9520d8f4cd0bff7352352d5d933649f6d6', '<>c::<DeleteGTSEFileTimerElapsed>b__84_1', 'Shared cleanup order key is File.GetLastWriteTime; both methods OrderByDescending then Skip(MaxCount).', [(1, '28dc02000a')]),
)

AB_PLAINTEXT_SHA256 = '9f034f95a6bda7a8d16f92f7593f2a38695609ad21e5b2ed31c6957ac5afed09'
INI_PLAINTEXT_SHA256 = 'a09bd0e8bfc0d2b03dfb1c2a7cc923116efbcef3e3eb13463c4d8dfbde62feba'
ADAPTATION_XML_SHA256 = '1fad76a8c94a6dca2a120ddf41a81f44909dc43b023df0ba53c947a1563b0ac9'

STATES = [{'id': 'bootstrap.off', 'owner': 'OS', 'meaning': 'No owned GTS+ bootstrap process'},
 {'id': 'bootstrap.arb-configuring',
  'owner': 'GTSPlusArbitration.exe',
  'meaning': 'Own ABAppMutex; configure supervisors'},
 {'id': 'bootstrap.arb-launching', 'owner': 'GTSPlusArbitration.exe', 'meaning': 'Launch configured apps sequentially'},
 {'id': 'bootstrap.arb-running',
  'owner': 'GTSPlusArbitration.exe',
  'meaning': 'Supervise children/services; GUI runs separately'},
 {'id': 'bootstrap.duplicate',
  'owner': 'second invocation',
  'meaning': 'Launch InfoCenter_Multi instead of second core'},
 {'id': 'bootstrap.startup-error',
  'owner': 'bootstrap caller',
  'meaning': 'Initialization failed/logged; partial children may remain'},
 {'id': 'bootstrap.pf-initializing',
  'owner': 'GTSPlus.exe',
  'meaning': 'Own GTSPlusMutex; initialize adapters/workers'},
 {'id': 'bootstrap.pf-running', 'owner': 'GTSPlus.exe', 'meaning': 'API workers and WebSocket dispatcher active'},
 {'id': 'bootstrap.degraded',
  'owner': 'GTSPlusArbitration.exe/GTSPlus.exe',
  'meaning': 'Error notification/trace without restart'},
 {'id': 'bootstrap.end-confirming',
  'owner': 'GTSPlusArbitration.exe',
  'meaning': 'Query EndMode1 participants, wait report saving'},
 {'id': 'bootstrap.pf-paused', 'owner': 'GTSPlus.exe', 'meaning': 'EndCheckFlag with confirmation barriers reset'},
 {'id': 'bootstrap.end-veto',
  'owner': 'GTSPlusArbitration.exe',
  'meaning': 'Participant busy or report-save timeout; do not execute exit'},
 {'id': 'bootstrap.ending', 'owner': 'GTSPlusArbitration.exe', 'meaning': 'Execute exit across participants'},
 {'id': 'bootstrap.pf-finalizing',
  'owner': 'GTSPlus.exe',
  'meaning': 'Cancel token, stop sockets, wake/join workers, finalize adapters'},
 {'id': 'bootstrap.closed', 'owner': 'process owner', 'meaning': 'Form loop exited; mutex released/disposed'}]

TRANSITIONS = [{'id': 'bootstrap.launch-arb',
  'from': 'bootstrap.off',
  'to': 'bootstrap.arb-configuring',
  'trigger': 'GTSPlusArbitration.Program.Main',
  'guard': 'ABAppMutex acquired',
  'action': 'InitializeForm; no command-line arguments consumed',
  'evidence': ['bootstrap.arb-entry']},
 {'id': 'bootstrap.duplicate-arb',
  'from': 'bootstrap.off',
  'to': 'bootstrap.duplicate',
  'trigger': 'arbitration invocation',
  'guard': 'ABAppMutex unavailable',
  'action': 'Start InfoCenter_Multi.exe cwd=its parent; return',
  'evidence': ['bootstrap.arb-entry', 'bootstrap.path-constants']},
 {'id': 'bootstrap.arb-config-error',
  'from': 'bootstrap.arb-configuring',
  'to': 'bootstrap.startup-error',
  'trigger': 'ReadABSystemSetting/InitializeForm',
  'guard': 'decode/validation false or exception',
  'action': 'Do not Run form; release mutex; no recovery launch',
  'evidence': ['bootstrap.arb-settings', 'bootstrap.arb-initialize', 'bootstrap.arb-entry']},
 {'id': 'bootstrap.start-children',
  'from': 'bootstrap.arb-configuring',
  'to': 'bootstrap.arb-launching',
  'trigger': 'InitializeForm',
  'guard': 'ABSystem valid; distributor normal or default',
  'action': 'StartApplication in exact config order',
  'evidence': ['bootstrap.arb-initialize', 'bootstrap.arb-launch']},
 {'id': 'bootstrap.restricted-launch',
  'from': 'bootstrap.arb-launching',
  'to': 'bootstrap.arb-running',
  'trigger': 'DistributorDepending read failure',
  'guard': 'DefaultStart=true',
  'action': 'Only InfoCenter StartMode3 runs; PF/CUW mode1 skipped; flag AB000006',
  'evidence': ['bootstrap.arb-distributor', 'bootstrap.arb-launch', 'bootstrap.arb-initialize']},
 {'id': 'bootstrap.normal-launch',
  'from': 'bootstrap.arb-launching',
  'to': 'bootstrap.arb-running',
  'trigger': 'ordered child launches complete',
  'guard': 'DefaultStart=false',
  'action': 'Launch InfoCenter then PF then CUW; confirm each startup PID/result; monitor services but never start '
            'them here',
  'evidence': ['bootstrap.arb-launch', 'bootstrap.arb-initialize']},
 {'id': 'bootstrap.child-start-error',
  'from': 'bootstrap.arb-launching',
  'to': 'bootstrap.degraded',
  'trigger': 'Process.Start/confirmation',
  'guard': 'launch exception, timeout, nonempty matching startup result',
  'action': 'Notify failure; continue next child; no launch retry',
  'evidence': ['bootstrap.arb-launch', 'bootstrap.arb-notify']},
 {'id': 'bootstrap.pid-mismatch',
  'from': 'bootstrap.arb-launching',
  'to': 'bootstrap.arb-launching',
  'trigger': 'ER_ApplicationStart data',
  'guard': 'received PID != new child PID',
  'action': 'Recreate server and wait remaining start timeout; no relaunch',
  'evidence': ['bootstrap.arb-launch']},
 {'id': 'bootstrap.version-error',
  'from': 'bootstrap.arb-running',
  'to': 'bootstrap.degraded',
  'trigger': 'version confirmation',
  'guard': 'manifest/component error or mismatch',
  'action': 'Notify AB000003/4/5; no startup veto',
  'evidence': ['bootstrap.arb-version']},
 {'id': 'bootstrap.start-pf',
  'from': 'bootstrap.off',
  'to': 'bootstrap.pf-initializing',
  'trigger': 'GTSPlusController.Program.Main',
  'guard': 'GTSPlusMutex acquired on STA thread',
  'action': 'CoInitializeSecurity; MainTask and hidden Form1',
  'evidence': ['bootstrap.pf-entry', 'bootstrap.pf-single-instance', 'bootstrap.pf-form-init']},
 {'id': 'bootstrap.duplicate-pf',
  'from': 'bootstrap.off',
  'to': 'bootstrap.duplicate',
  'trigger': 'GTSPlus invocation',
  'guard': 'GTSPlusMutex unavailable',
  'action': 'Launch InfoCenter_Multi, no second core',
  'evidence': ['bootstrap.pf-single-instance', 'bootstrap.path-constants']},
 {'id': 'bootstrap.pf-start-error',
  'from': 'bootstrap.pf-initializing',
  'to': 'bootstrap.startup-error',
  'trigger': 'InitializePlatform',
  'guard': 'info/config/adaptation/worker or caught exception failure',
  'action': 'ER_StartApplicationCS(error); close form',
  'evidence': ['bootstrap.pf-init', 'bootstrap.pf-form-init', 'bootstrap.msg-start']},
 {'id': 'bootstrap.pf-ready',
  'from': 'bootstrap.pf-initializing',
  'to': 'bootstrap.pf-running',
  'trigger': 'InitializePlatform result0',
  'guard': 'startup return path succeeds',
  'action': 'Start receiver/workers/socket/main and notify arbitration',
  'evidence': ['bootstrap.pf-init', 'bootstrap.pf-sequence', 'bootstrap.pf-form-init']},
 {'id': 'bootstrap.socket-error-overwrite',
  'from': 'bootstrap.pf-initializing',
  'to': 'bootstrap.degraded',
  'trigger': 'StartMainSequence false WSM result',
  'guard': 'subsequent settings lookup returns success',
  'action': 'Remember PF000002; overwritten status may still let InitializePlatform return0',
  'evidence': ['bootstrap.pf-sequence', 'bootstrap.pf-init']},
 {'id': 'bootstrap.settings-tamper',
  'from': 'bootstrap.pf-running',
  'to': 'bootstrap.degraded',
  'trigger': 'SettingFileTampering_<PID>',
  'guard': 'message not UserProfile/VehicleConfigure',
  'action': 'Mark common GUI flags; remember PF000004; receive next message',
  'evidence': ['bootstrap.pf-settings-error']},
 {'id': 'bootstrap.task-failure',
  'from': 'bootstrap.pf-running',
  'to': 'bootstrap.degraded',
  'trigger': 'arbitration alive query',
  'guard': 'any watched Task.Status !=1',
  'action': 'Reply PF000005; supervisor reports/records, no restart',
  'evidence': ['bootstrap.pf-alive', 'bootstrap.msg-alive', 'bootstrap.alive-app']},
 {'id': 'bootstrap.child-crash',
  'from': 'bootstrap.arb-running',
  'to': 'bootstrap.degraded',
  'trigger': 'alive monitor tick',
  'guard': 'configured mode nonzero and previously healthy child PID absent/unresponsive',
  'action': 'Notify once on state change; absent child disables monitor; no restart',
  'evidence': ['bootstrap.alive-app', 'bootstrap.arb-notify']},
 {'id': 'bootstrap.service-failure',
  'from': 'bootstrap.arb-running',
  'to': 'bootstrap.degraded',
  'trigger': 'alive monitor tick',
  'guard': 'service not Running or mode2 reply error',
  'action': 'Notify last-result transition; keep monitoring; no start/restart',
  'evidence': ['bootstrap.alive-service']},
 {'id': 'bootstrap.request-end',
  'from': 'bootstrap.arb-running',
  'to': 'bootstrap.end-confirming',
  'trigger': 'ER_ABAppEnd or Windows SessionEnding',
  'guard': 'request received',
  'action': 'ConfirmEnding; distinguish shutdown bool',
  'evidence': ['bootstrap.arb-end-request', 'bootstrap.arb-session']},
 {'id': 'bootstrap.pause-pf',
  'from': 'bootstrap.pf-running',
  'to': 'bootstrap.pf-paused',
  'trigger': 'ER_EndingConfirm_GTS+ PF',
  'guard': 'registered callback',
  'action': 'Reset barriers and set EndCheckFlag; CheckEditFile returns veto/empty',
  'evidence': ['bootstrap.msg-confirm', 'bootstrap.pf-confirm', 'bootstrap.pf-loop']},
 {'id': 'bootstrap.busy-veto',
  'from': 'bootstrap.end-confirming',
  'to': 'bootstrap.end-veto',
  'trigger': 'participant confirmation',
  'guard': 'nonempty ResultCode or report-saving timeout',
  'action': 'Notify and return false',
  'evidence': ['bootstrap.arb-confirm']},
 {'id': 'bootstrap.confirm-fail-open',
  'from': 'bootstrap.end-confirming',
  'to': 'bootstrap.end-confirming',
  'trigger': 'pipe participant exception',
  'guard': 'connection/read failure',
  'action': 'Log and continue confirmation of remaining participants',
  'evidence': ['bootstrap.arb-confirm']},
 {'id': 'bootstrap.approved-end',
  'from': 'bootstrap.end-confirming',
  'to': 'bootstrap.ending',
  'trigger': 'ConfirmEnding returns true',
  'guard': 'no observed veto; includes outer exception fail-open',
  'action': 'SetAppEndState then ExecuteEnding',
  'evidence': ['bootstrap.arb-confirm', 'bootstrap.arb-end-request', 'bootstrap.arb-session']},
 {'id': 'bootstrap.veto-resume',
  'from': 'bootstrap.end-veto',
  'to': 'bootstrap.arb-running',
  'trigger': 'ExecuteEnding(shutdown,false)',
  'guard': 'not approved',
  'action': 'Send execute=false to EndMode1 participants; no kill/close; Windows session cancelled if relevant',
  'evidence': ['bootstrap.arb-execute', 'bootstrap.arb-session', 'bootstrap.arb-end-request']},
 {'id': 'bootstrap.resume-pf',
  'from': 'bootstrap.pf-paused',
  'to': 'bootstrap.pf-running',
  'trigger': 'EndingExecuteData.Exucute=false',
  'guard': 'veto/cancel path',
  'action': 'Reset flags and Set barriers; keep form alive',
  'evidence': ['bootstrap.msg-execute',
               'bootstrap.pf-execute',
               'bootstrap.pf-execute-callback',
               'bootstrap.pf-unfreeze']},
 {'id': 'bootstrap.execute-pf',
  'from': 'bootstrap.pf-paused',
  'to': 'bootstrap.pf-finalizing',
  'trigger': 'EndingExecuteData.Exucute=true',
  'guard': 'approved exit',
  'action': 'Clear queues; optional nonshutdown GUI broadcast; end flags; close form',
  'evidence': ['bootstrap.msg-execute', 'bootstrap.pf-execute', 'bootstrap.pf-execute-callback', 'bootstrap.pf-close']},
 {'id': 'bootstrap.close-running-pf',
  'from': 'bootstrap.pf-running',
  'to': 'bootstrap.pf-finalizing',
  'trigger': 'FormClosed',
  'guard': 'direct close or initialization failure',
  'action': 'FinalizePlatform even after partial initialization',
  'evidence': ['bootstrap.pf-close', 'bootstrap.pf-finalize']},
 {'id': 'bootstrap.finalize-pf',
  'from': 'bootstrap.pf-finalizing',
  'to': 'bootstrap.closed',
  'trigger': 'FinalizePlatform and FormClosed',
  'guard': 'waited tasks complete or caught teardown exception',
  'action': 'Cancel/wake/join; adapter finalize; notify ER_ApplicationEnd; unregister IPC; release mutex',
  'evidence': ['bootstrap.pf-finalize', 'bootstrap.pf-close', 'bootstrap.msg-end', 'bootstrap.pf-single-instance']},
 {'id': 'bootstrap.release-child-monitor',
  'from': 'bootstrap.arb-running',
  'to': 'bootstrap.arb-running',
  'trigger': 'ER_ApplicationEnd(PID)',
  'guard': 'PID monitored',
  'action': 'RemoveAliveMonitor; no process restart',
  'evidence': ['bootstrap.arb-child-end']},
 {'id': 'bootstrap.finish-arb',
  'from': 'bootstrap.ending',
  'to': 'bootstrap.closed',
  'trigger': 'participants exit',
  'guard': 'execute=true; no indefinitely blocked WaitForExit/pipe drain',
  'action': 'Close own form; cancel/report flush and join workers; release mutex',
  'evidence': ['bootstrap.arb-execute', 'bootstrap.arb-close', 'bootstrap.arb-entry']},
 {'id': 'bootstrap.pf-session-veto',
  'from': 'bootstrap.pf-running',
  'to': 'bootstrap.pf-running',
  'trigger': 'Windows SessionEnding',
  'guard': 'coordination signal without execution or local CheckEditFile veto at timeout',
  'action': 'set SessionEndingEventArgs.Cancel; default timeout10000ms',
  'evidence': ['bootstrap.pf-session', 'bootstrap.pf-timeout', 'bootstrap.pf-execute-callback']}]

HANDOFFS = [{'to_domain': 'auth_settings',
  'caller': 'GTSPlusArbitration.Form1.StartApplication',
  'callee': 'GtsPlus-InfoCenter/GtsPlus-InfoCenter.exe',
  'mechanism': 'Process.Start; no args; cwd executable directory',
  'payload': 'first normal child; StartMode3 means start even on distributor fallback; EndMode1; alive mode0',
  'evidence': ['bootstrap.config', 'bootstrap.arb-launch']},
 {'to_domain': 'auth_settings',
  'caller': 'second arbitration/PF invocation',
  'callee': 'GtsPlus-InfoCenter/GtsPlus-InfoCenter_Multi/GtsPlus-InfoCenter_Multi.exe',
  'mechanism': 'Process.Start after nonblocking global mutex contention',
  'payload': 'no arguments; cwd executable directory; original instance remains owner',
  'evidence': ['bootstrap.arb-entry', 'bootstrap.pf-single-instance', 'bootstrap.path-constants']},
 {'to_domain': 'cuw_utility',
  'caller': 'GTSPlusArbitration.Form1.StartApplication',
  'callee': 'CUWPlus/CuwBackendServiceConsoleApp.exe',
  'mechanism': 'third sequential child, Process.Start and startup named-pipe handshake',
  'payload': 'StartMode1,EndMode1,alive2; startup timeout180000ms; cwd CUWPlus; no args',
  'evidence': ['bootstrap.config', 'bootstrap.arb-launch']},
 {'to_domain': 'sync_upload',
  'caller': 'GTSPlusArbitration.InitializeForm',
  'callee': 'GTS+ DataSync Windows service',
  'mechanism': 'monitor externally-owned services; no ServiceController.Start in arbitration launch path',
  'payload': 'EndMode0/alive2; query service Running and ER_AliveMonitor_<name>; excluded from normal EndMode1 ending confirmation/execution',
  'evidence': ['bootstrap.config', 'bootstrap.arb-initialize', 'bootstrap.alive-service']},
 {'to_domain': 'ui_ipc',
  'caller': 'GTSPlusArbitration.InitializeForm',
  'callee': 'GTS+GUIServer Windows service',
  'mechanism': 'monitor externally-owned service; no ServiceController.Start in arbitration launch path',
  'payload': 'EndMode0/alive2; query service Running and ER_AliveMonitor_<name>; SCM OnStop owns host teardown',
  'evidence': ['bootstrap.config', 'bootstrap.arb-initialize', 'bootstrap.alive-service']},
 {'to_domain': 'operations',
  'caller': 'MainTask.InitializePlatform/FinalizePlatform',
  'callee': 'GTSPlusAdaptIF AdaptationInterface',
  'mechanism': 'managed XML ordered Assembly.LoadFrom/CreateInstance/init/finalize',
  'payload': 'DiagAdaptationManager third adapter; five scheduler lanes; shared cancellation source; queue event '
             'wake/join',
  'evidence': ['bootstrap.pf-init',
               'bootstrap.pf-finalize',
               'bootstrap.adapt-init',
               'bootstrap.adapt-finalize',
               'bootstrap.adaptation-table']},
 {'to_domain': 'ui_ipc',
  'caller': 'MainTask.StartMainSequence/FinalizePlatform',
  'callee': 'GtsPlus-WebSocketManager.WebSocketManager.StartProcess/StopProcess',
  'mechanism': 'in-process managed method, not OS Process.Start',
  'payload': 'StartProcess(false); message fetch queue; cancellation teardown',
  'evidence': ['bootstrap.pf-sequence', 'bootstrap.pf-loop', 'bootstrap.pf-finalize']},
 {'to_domain': 'auth_settings',
  'caller': 'InitializePlatform / ReadDistributorDepending / ResetPFConfig',
  'callee': 'SettingFileWrapper and CM packaged configuration decoder',
  'mechanism': 'managed wrapper + native CM PInvoke',
  'payload': 'type2 distributor fallback; restore PF.cfg from DefaultPF.cfg; tamper notification per-process pipe',
  'evidence': ['bootstrap.arb-distributor',
               'bootstrap.pf-reset-config',
               'bootstrap.decrypt',
               'bootstrap.packaging-profile',
               'bootstrap.pf-settings-error']},
 {'to_domain': 'persistence',
  'caller': 'Arbitration.FormClosed/ErrorReport',
  'callee': 'local report/log persistence and DataSync upload pipeline',
  'mechanism': 'cancel/join reporting workers, local error traces',
  'payload': 'ABSystem log limits and report include paths; no upload/network execution in this extractor',
  'evidence': ['bootstrap.arb-close', 'bootstrap.arb-notify', 'bootstrap.arb-paths', 'bootstrap.config']}]

PERSISTENCE = [{'path_pattern': '<install>/Env/ABSystem.yml; <install>/Env/GTSPlus.pp',
  'producer': 'shipped installation',
  'consumer': 'GTSPlusArbitration.ReadABSystemSetting / GTSPlusCommon.CryptManagerWrapper',
  'created': 'installer input, not created by observed bootstrap code',
  'flushed': 'read/decrypt before children launch',
  'deleted': 'not deleted by examined bootstrap methods',
  'evidence': ['bootstrap.arb-settings', 'bootstrap.decrypt', 'bootstrap.packaging-profile', 'bootstrap.config']},
 {'path_pattern': '<SettingFileWrapper folder>/PF.cfg',
  'producer': 'ConnectionManager.ResetPFConfig',
  'consumer': 'PF configuration users',
  'created': 'copy <install>/Env/DefaultPF.cfg if present; overwrite existing',
  'flushed': 'File.Copy returns before startup adapters initialize; no explicit fsync',
  'deleted': 'not deleted; overwritten on reset',
  'evidence': ['bootstrap.pf-reset-config', 'bootstrap.pf-init']},
 {'path_pattern': '<LocalApplicationData>/GTSPlus/ErrorReport/{ActLog,Trace,TraceAutoSave,Unsend,Send}; '
                  'communication-log temp path may resolve from install root',
  'producer': 'Arbitration/ErrorReport workers',
  'consumer': 'report tasks and DataSync/report domain',
  'created': 'report infrastructure InitializeErrorReport and NotifyError trace save; config supplies log file '
             'size/count limits',
  'flushed': 'FormClosed signals AB_ErrorReportSave and joins report tasks before FinalizeErrorReport; this does not '
             'establish fsync or success after process crash',
  'deleted': 'retention/packaging owned by reporting/persistence domain, not inferred from form teardown',
  'evidence': ['bootstrap.arb-paths',
               'bootstrap.arb-initialize',
               'bootstrap.arb-close',
               'bootstrap.arb-notify',
               'bootstrap.config']},
 {'path_pattern': '<install>/Ver/Manifest.json; <install>/Ver/<component>.json',
  'producer': 'installer/update components',
  'consumer': 'ConfirmApplicationVersion',
  'created': 'preexisting shipped/update state',
  'flushed': 'read after child launch',
  'deleted': 'not modified by version checks',
  'evidence': ['bootstrap.arb-version', 'bootstrap.config']}]

COVERAGE = {'components': ['GTSPlusArbitration.exe',
                'GTSPlus.exe',
                'GTSPlusCommon.dll',
                'MsgDatComm.dll',
                'GTSPlusAdaptIF.dll',
                'GTSPlusErrorReport.dll',
                'GtsPlus-CM.dll',
                'Env/ABSystem.yml',
                'Env/GTSPlus.pp',
                'Env/GTSPlusInfo.ini',
                'embedded AdaptationTable.xml'],
 'entrypoints': ['GTSPlusArbitration.Program.Main token0x0600005A RVA0x5394 void()',
                 'GTSPlusController.Program.Main token0x06000156 RVA0x9DE4 void()',
                 'GTSPlusController.Program nested STA callback RVA0x15BA8',
                 'Windows SessionEnding/FormClosed and MsgDatComm callbacks'],
 'branches': ['mutex owner/contention/exception',
              'ABSystem decrypt/validation/exception',
              'normal/distributor-default launch',
              'PID mismatch/start result/timeout/launch failure',
              'version mismatch/component-read/manifest failure',
              'end approval/veto/pipe fail-open/report-save timeout',
              'shutdown versus ordinary requested end',
              'cancel/resume barriers',
              'token-canceled workers and unbounded join paths',
              'task liveness and crash/hung process monitor with no restart',
              'settings tamper exclusions/global error',
              'StartMainSequence result overwritten by settings result'],
 'execution_limits': ['Offline decode and IL parsing only; no vehicle, network, account use or Windows application run',
                      'Fixed shipped packaging material derived only from pinned binary/resource inputs; not emitted']}

RESIDUALS = [{'question': 'Windows named-pipe timing, global mutex ACL behavior, abandoned mutex, COM security result and shutdown '
              'event ordering under live OS execution',
  'why_unclosed': 'Executable branches and config pinned offline; no Windows runtime/vehicle/network execution '
                  'performed. Main ignores COM HRESULT; WaitOne exception path logs rather than a dedicated '
                  'abandoned-owner recovery.',
  'next_evidence': 'Isolated Windows harness with synthetic IPC peers, registry/temp folders and no vehicle or real '
                   'account; verify startup PID handshake, veto/resume and bounded/unbounded waits.'},
 {'question': 'Bootstrap process crash before FormClosed or while waiting on child/task',
  'why_unclosed': 'Inspected entrypoints have local catches, no global unhandled-exception/relaunch handler. Forced '
                  'process termination does not run guaranteed FormClosed persistence; unbounded '
                  'Task.Wait/WaitForExit/WaitForPipeDrain can stop forward progress.',
  'next_evidence': 'Throwaway Windows crash/kill harness and storage-worker flush implementation; do not label crash '
                   'as graceful teardown.'}]

COVERAGE["components"].extend(["GTSPlusPFCommon.dll", "Env/GTSPlusSetting.ini"])
COVERAGE["branches"].append("one-shot retention cleanup, negative MaxCount, EndFlag interruption and file-operation exception")
TRANSITIONS.append({
    "id": "bootstrap.retention-timers",
    "from": "bootstrap.pf-running", "to": "bootstrap.pf-running",
    "trigger": "GTSE/autosave cleanup timers expire",
    "guard": "configured60000ms elapsed; configuration reads succeed; MaxCount>=0",
    "action": "Stop timer; enumerate configured files; descending LastWriteTime; retain newest300; delete excess until EndFlag; log exceptions; no restart",
    "evidence": ["bootstrap.pf-init", "bootstrap.retention-setting", "bootstrap.retention-config",
                 "bootstrap.retention-order-key", "bootstrap.delete-gtse", "bootstrap.delete-report"],
})
PERSISTENCE.append({
    "path_pattern": "<configured UserStoredData>/*.gtse; <configured ErrorReportFileAutoSave{Unsend,Send}>/*.gtsr",
    "producer": "diagnostic recorder / error-report tasks",
    "consumer": "MainTask one-shot retention cleanup",
    "created": "producer domain, not created by cleanup",
    "flushed": "not established by retention code",
    "deleted": "60000ms startup timer; retain newest300 by LastWriteTime; GTSE folder independently, combined autosave send/unsend pool; stop early on EndFlag",
    "evidence": ["bootstrap.retention-config", "bootstrap.retention-order-key",
                 "bootstrap.delete-gtse", "bootstrap.delete-report"],
})


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source(source_id: str, path: Path, expected_sha: str, expected_size: int, representation: str) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) != expected_size or _sha(data) != expected_sha:
        raise ValueError(f"source identity drift: {path.name}")
    resolved = path.resolve()
    return {"id": source_id,
            "path": resolved.relative_to(REPO_ROOT.resolve()).as_posix() if resolved.is_relative_to(REPO_ROOT.resolve()) else str(resolved),
            "sha256": expected_sha, "size": expected_size, "representation": representation}


def _decode_info(pe: Any, path: Path) -> bytes:
    # Derive fixed application packaging material by the exact initializer's FieldRva.
    _, instructions, _ = _instructions(pe, "GTSPlusCommon.Function.CryptographicFunction", ".cctor")
    fields = [resolve_token(pe, ins.operand) for ins in instructions if str(ins.opcode) == "ldtoken"]
    if len(fields) != 1:
        raise ValueError("INI packaging initializer drift")
    rvas = [row.Rva for row in pe.net.mdtables.FieldRva if row.Field.row is fields[0]]
    if len(rvas) != 1:
        raise ValueError("INI packaging FieldRva drift")
    data = path.read_bytes()
    return unpad(AES.new(pe.get_data(rvas[0], 16), AES.MODE_CBC, data[:16]).decrypt(data[16:]), 16)


def _api_routing(pe: Any, adaptation_pe: Any, evidence: list[dict[str, Any]],
                 adaptations: list[dict[str, Any]], census: dict[str, Any]) -> dict[str, Any]:
    """Recover selector cases and first target blocks, not API implementation claims."""
    workers = ("Cancel", "WebService", "Message", "NonVehicleConnection", "VehicleConnection")
    specs = [
        ("connection", "GTSPlusController.ConnectionManager", "AnalysisRequestMessage", 0x31D),
        ("queue", "GTSPlusController.MainTask", "StartMainTask", 0x541),
        *[(name, "GTSPlusController.ExecuteTask." + name + "ExecuteTask", "MessageFunction", default)
          for name, default in zip(workers, (0x45, 0x121, 0x79, 0x232, 0x751))],
    ]
    owner_by_row = {id(m.row): f"{t.TypeNamespace}.{t.TypeName}".lstrip(".")
                    for t in pe.net.mdtables.TypeDef for m in t.MethodList}

    def integer(instruction: Any) -> int:
        op = str(instruction.opcode)
        if op in ("ldc.i4", "ldc.i4.s"):
            return int(instruction.operand)
        if op.startswith("ldc.i4."):
            suffix = op.rsplit(".", 1)[1]
            return -1 if suffix == "m1" else int(suffix)
        raise ValueError(f"expected direct integer constant, got {op}")

    def target_row(instruction: Any) -> Any:
        row = resolve_token(pe, instruction.operand)
        return row.Method.row if hasattr(row, "Method") else row

    def call_name(instruction: Any) -> str:
        row = target_row(instruction)
        owner = owner_by_row.get(id(row))
        return f"{owner}::{row.Name}" if owner else _operand(pe, instruction.operand)

    def instruction_record(instruction: Any, base: int) -> dict[str, Any]:
        value = _operand(pe, instruction.operand)
        if instruction.opcode.flow_control.name in ("Branch", "Cond_Branch"):
            if isinstance(instruction.operand, int):
                value = f"IL_{instruction.operand - base:04X}"
            elif isinstance(instruction.operand, list):
                value = ", ".join(f"IL_{target - base:04X}" for target in instruction.operand)
        return {"il": f"IL_{instruction.offset - base:04X}", "opcode": str(instruction.opcode),
                "operand": value, "bytes": (instruction.opcode_bytes + instruction.operand_bytes).hex()}

    selectors = []
    for key, owner, method, default in specs:
        row, instructions, body = _instructions(pe, owner, method)
        base = instructions[0].offset
        positions = {instruction.offset: index for index, instruction in enumerate(instructions)}
        cases = []
        targets = {base + default}
        if key == "VehicleConnection":
            targets.add(base + 0x77E)  # Non-UG continuation of the default prefix selector.
        # The later CN000001 comparison only selects status logging, not dispatch.
        end = next((i for i, instruction in enumerate(instructions)
                    if str(instruction.opcode) == "call"
                    and _operand(pe, instruction.operand) == "SetApiTaskMessageList"), len(instructions))
        if key != "connection":
            end = len(instructions)
        for index, instruction in enumerate(instructions[:end]):
            if str(instruction.opcode) != "ldstr":
                continue
            literal = resolve_token(pe, instruction.operand)
            if not isinstance(literal, str) or not re.fullmatch(r"[A-Z]{2}(?:(?:[0-9]{6}|XX[0-9]{4}))?", literal):
                continue
            equality, branch = instructions[index + 1:index + 3]
            if _operand(pe, equality.operand) != "System.String::op_Equality":
                continue
            op = str(branch.opcode)
            if not op.startswith(("brtrue", "brfalse")):
                raise ValueError(f"selector equality lowering drift: {owner}::{method}")
            target = branch.operand if op.startswith("brtrue") else instructions[index + 3].offset
            targets.add(target)
            cases.append({"value": literal, "comparison": instruction_record(instruction, base),
                          "branch": instruction_record(branch, base), "target_il": f"IL_{target - base:04X}"})
        blocks = []
        for target in sorted(targets):
            block = []
            for instruction in instructions[positions[target]:]:
                block.append(instruction)
                if instruction.opcode.flow_control.name in ("Branch", "Cond_Branch", "Return", "Throw"):
                    break
            entry = {"il": f"IL_{target - base:04X}",
                     "instructions": [instruction_record(instruction, base) for instruction in block],
                     "calls": [call_name(instruction) for instruction in block
                               if str(instruction.opcode) in ("call", "callvirt", "newobj")]}
            if key == "queue":
                enqueue = next(i for i, instruction in enumerate(block)
                               if str(instruction.opcode) == "callvirt"
                               and _operand(pe, instruction.operand) == "EnqueueMessage")
                entry["queue_id"] = integer(block[enqueue - 2])
            blocks.append(entry)
        eid = f"bootstrap.api.{key}"
        evidence.append({"id": eid, "source": "bootstrap.pf.recovered", "kind": "managed-dispatch-selector",
                         "locator": f"{owner}::{method}", **_method_pin(row, body),
                         "offset_basis": "relative to first IL instruction", "cases": cases,
                         "default_target_il": f"IL_{default:04X}", "target_blocks": blocks,
                         "finding": "Exact equality selectors and their first target blocks; admission and downstream implementation are separate contracts."})
        if key == "VehicleConnection":
            evidence[-1]["prefix_default_target_il"] = "IL_077E"
        selectors.append(eid)

    worker_owners = []
    for name in workers:
        owner = "GTSPlusController.ExecuteTask." + name + "ExecuteTask"
        row, instructions, body = _instructions(pe, owner, ".ctor")
        assignments = {}
        for index, instruction in enumerate(instructions):
            if str(instruction.opcode) != "stfld":
                continue
            field = _operand(pe, instruction.operand)
            if field == "<ApiTaskId>k__BackingField":
                assignments["queue_id"] = integer(instructions[index - 1])
            elif field == "<MessageEventName>k__BackingField":
                assignments["event_name"] = resolve_token(pe, instructions[index - 1].operand)
        if set(assignments) != {"queue_id", "event_name"}:
            raise ValueError(f"worker registration drift: {owner}")
        eid = f"bootstrap.api.{name}.constructor"
        evidence.append({"id": eid, "source": "bootstrap.pf.recovered", "kind": "managed-worker-registration",
                         "locator": owner + "::.ctor", **_method_pin(row, body), **assignments,
                         "finding": "Constructor constants bind this worker to its queue and named wake event."})
        worker_owners.append({"owner": owner, **assignments, "evidence": [eid, f"bootstrap.api.{name}"]})

    enqueue_sites = []
    method_count = 0
    for row, identity in zip(pe.net.mdtables.MethodDef, census["methods"], strict=True):
        if identity["implementation"] != "il":
            continue
        method_count += 1
        body = _body(pe, row)
        for index, instruction in enumerate(body.instructions):
            if str(instruction.opcode) not in ("call", "callvirt"):
                continue
            if str(getattr(target_row(instruction), "Name", "")) != "EnqueueMessage":
                continue
            enqueue_sites.append({"caller": identity["full_nested_name"] + "::" + identity["name"],
                                  "method_identity": identity,
                                  **_method_pin(row, body), "queue_id": integer(body.instructions[index - 2]),
                                  "call": instruction_record(instruction, body.instructions[0].offset)})
    evidence.append({"id": "bootstrap.api.enqueue-census", "source": "bootstrap.pf.recovered",
                     "kind": "managed-callsite-census", "locator": "all validated IL MethodDef bodies; native and bodyless rows classified separately",
                     "methods_scanned": method_count, "method_census": census, "callsites": enqueue_sites,
                     "finding": "All direct call/callvirt EnqueueMessage sites, including internal insertions that bypass main classification."})
    row, _, body = _instructions(adaptation_pe, "GTSPlusAdaptationIF.AdaptationInterface", "ExecuteAdaptation")
    evidence.append({"id": "bootstrap.api.adapter-routing", "source": "bootstrap.adapt.recovered",
                     "kind": "managed-il", "locator": "GTSPlusAdaptationIF.AdaptationInterface::ExecuteAdaptation",
                     **_method_pin(row, body),
                     "finding": "Substring(0,2) selects the first category match in adaptation order. It invokes that instance and returns; it does not try another adapter after a failure. Unknown category and caught adapter exceptions produce AdaptIf error3; the initial substring is outside that catch."})
    return {"selectors": selectors, "workers": worker_owners, "adaptation_categories": adaptations,
            "evidence": ["bootstrap.api.enqueue-census", "bootstrap.api.adapter-routing", "bootstrap.adaptation-table"],
            "scope": "Complete PF selector/queue/category census, not an assertion that every native API suffix is implemented.",
            "precedence": "Seven immediate ConnectionManager selectors precede the main classifier. Queued exact IDs precede two-character family routing; unknown families use message queue5. Internal callers can enqueue directly.",
            "input_boundary": "Main classification falls back to Substring(0,2); null/short inputs throw in this method. Its exception regions are finally-only. Network admission is an earlier, separate boundary."}


def build(installed_root: Path = DEFAULT_INSTALLED, recovered_root: Path = DEFAULT_MAIN) -> dict[str, Any]:
    installed_root, recovered_root = Path(installed_root), Path(recovered_root)
    sources: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    assemblies: dict[str, Any] = {}
    for key, pin in SOURCE_PINS.items():
        name, cp = pin["file"], pin["protected"]
        recovered = recovered_root / "bin" / name
        original = installed_root / "bin" / name
        source_id = f"bootstrap.{key}.recovered"
        qualification = qualify_recovered_source(recovered, original, component_root=recovered_root)
        recovered_source = _source(source_id, recovered, qualification["recovered_sha256"],
                                   recovered.stat().st_size, "manifest-qualified recovered PE")
        recovered_source["recovery"] = qualification
        sources.append(recovered_source)
        sources.append(_source(f"bootstrap.{key}.installed", original, cp["stub_sha256"], cp["stub_size"], "installed CP stub"))
        sources.append(_source(f"bootstrap.{key}.sidecar", Path(str(original) + "._"), cp["sidecar_sha256"], cp["sidecar_size"], "installed CP sidecar"))
        if key != "cm":
            assemblies[key] = _open(recovered)
            proof = validate_managed_bodies(recovered)
            evidence.append({"id": f"bootstrap.{key}.materialized", "source": source_id, "kind": "recovery-provenance",
                             "locator": "all MethodDef classifications; complete valid IL bodies", **proof,
                             "qualification": qualification,
                             "original_sources": [f"bootstrap.{key}.installed", f"bootstrap.{key}.sidecar"],
                             "finding": "Every required IL body passes full decoding, framing, operand and branch validation. Native and legitimately bodyless methods remain separately classified; exact manifest links recovered bytes to pinned installed CP sources."})
        else:
            evidence.append({"id": "bootstrap.cm.provenance", "source": source_id, "kind": "recovery-provenance",
                             "locator": "manifest-qualified native CM recovered PE",
                             "qualification": qualification,
                             "original_sources": ["bootstrap.cm.installed", "bootstrap.cm.sidecar"],
                             "finding": "Native packaging decoder is qualified against the exact manifest and pinned installed CP pair; reused local decoder checks native byte anchor."})
    for eid, key, rva, size, digest, locator, finding, anchor_pins in METHODS:
        pe = assemblies[key]
        rows = [row for row in pe.net.mdtables.MethodDef
                if int(row.Rva) == rva and str(row.Name) == locator.rsplit("::", 1)[1]]
        if len(rows) != 1:
            raise ValueError(f"method RVA drift: {locator}")
        body = _body(pe, rows[0])
        if body.size != size or _sha(body.raw_bytes) != digest:
            raise ValueError(f"method body drift: {locator}")
        instructions = body.instructions
        base = instructions[0].offset
        by_offset = {ins.offset - base: ins for ins in instructions}
        anchors = []
        for offset, hex_bytes in anchor_pins:
            ins = by_offset[offset]
            if (ins.opcode_bytes + ins.operand_bytes).hex() != hex_bytes:
                raise ValueError(f"decisive instruction drift: {locator}+{offset:x}")
            operand = format_operand(pe, ins.operand)
            if ins.opcode.flow_control.name in ("Branch", "Cond_Branch") and isinstance(ins.operand, int):
                operand = f"IL_{ins.operand - base:04X}"
            anchors.append({"il": f"IL_{offset:04X}", "opcode": str(ins.opcode), "operand": operand, "bytes": hex_bytes})
        evidence.append({"id": eid, "source": f"bootstrap.{key}.recovered", "kind": "managed-il", "locator": locator,
                         **_method_pin(rows[0], body), "offset_basis": "IL offsets relative to first instruction, excluding method header",
                         "anchors": anchors, "exception_regions": [{"try_start": eh.try_start, "try_end": eh.try_end,
                             "handler_start": eh.handler_start, "handler_end": eh.handler_end, "kind": int(eh.exception_type)}
                            for eh in body.exception_handlers], "finding": finding})
    for key, token in (("arb", 0x0600005A), ("pf", 0x06000156)):
        pe = assemblies[key]
        if int(pe.net.struct.EntryPointTokenOrRva) != token:
            raise ValueError("CLR entry point token drift")
        row = pe.net.mdtables.MethodDef.rows[(token & 0xffffff) - 1]
        if str(row.Name) != "Main" or row.Signature.value != bytes.fromhex("000001"):
            raise ValueError("Main signature drift")
        evidence.append({"id": f"bootstrap.{key}.entry-token", "source": f"bootstrap.{key}.recovered", "kind": "cli-header",
                         "locator": f"EntryPointToken=0x{token:08X}", "signature_hex": "000001",
                         "finding": "Real CLR entry point is static void Main() with zero parameters."})
    for relative, pin in CONFIG_PINS.items():
        sid = "bootstrap.input." + Path(relative).name
        sources.append(_source(sid, installed_root / relative, pin["sha256"], pin["size"], "shipped encrypted configuration/packaging input"))
    ab = decrypt_file(installed_root / "Env/ABSystem.yml", installed_root / "Env/GTSPlus.pp",
                      recovered_root / "bin/GtsPlus-CM.dll", key_type=2)
    if _sha(ab) != AB_PLAINTEXT_SHA256:
        raise ValueError("ABSystem plaintext drift")
    info = _decode_info(assemblies["common"], installed_root / "Env/GTSPlusInfo.ini")
    if _sha(info) != INI_PLAINTEXT_SHA256:
        raise ValueError("GTSPlusInfo plaintext drift")
    ini = configparser.ConfigParser(interpolation=None)
    ini.read_string(info.decode("utf-8-sig"))
    if ini.getint("AppInfo", "SessionEndCheckTimeout") != CONFIGURATION["timeouts_ms"]["session_end_check"]:
        raise ValueError("session coordination timeout drift")
    evidence.append({"id": "bootstrap.config", "source": "bootstrap.input.ABSystem.yml", "kind": "decoded-packaged-config",
                     "locator": "ABSystem application/service roster, timeout and reporting policy",
                     "packaging_sources": ["bootstrap.input.GTSPlus.pp", "bootstrap.cm.recovered"],
                     "plaintext_sha256": AB_PLAINTEXT_SHA256, "plaintext_size": len(ab),
                     "finding": "Decoded locally using native CM key-type2. Exact plaintext hash pins the exported nonsecret configuration.",
                     "configuration": copy.deepcopy(CONFIGURATION)})
    evidence.append({"id": "bootstrap.info-config", "source": "bootstrap.input.GTSPlusInfo.ini", "kind": "decoded-packaged-config",
                     "locator": "AppInfo/SessionEndCheckTimeout", "plaintext_sha256": INI_PLAINTEXT_SHA256,
                     "material_source": "bootstrap.common.recovered", "value_ms": 10000,
                     "finding": "Distinct managed AES IV-prefix encoding, not CM salt/IV envelope; key material is derived and not emitted."})
    retention = decrypt_file(installed_root / "Env/GTSPlusSetting.ini", installed_root / "Env/GTSPlus.pp",
                             recovered_root / "bin/GtsPlus-CM.dll", key_type=2)
    if _sha(retention) != RETENTION_PLAINTEXT_SHA256:
        raise ValueError("retention configuration drift")
    parsed_retention = configparser.ConfigParser(interpolation=None)
    parsed_retention.read_string(retention.decode("utf-8-sig").split("\n", 1)[1])
    retention_policy = {section: {"start_time_ms": parsed_retention.getint(section, "StartTime"),
                                 "max_count": parsed_retention.getint(section, "MaxCount")}
                        for section in ("AutoDeleteGTSE", "AutoDeleteAutoSaveErrorReport")}
    evidence.append({"id": "bootstrap.retention-config", "source": "bootstrap.input.GTSPlusSetting.ini",
                     "kind": "decoded-packaged-config", "locator": "AutoDeleteGTSE/AutoDeleteAutoSaveErrorReport",
                     "packaging_sources": ["bootstrap.input.GTSPlus.pp", "bootstrap.cm.recovered"],
                     "plaintext_sha256": RETENTION_PLAINTEXT_SHA256, "policy": retention_policy,
                     "finding": "Both one-shot cleanup timers start after60000ms and retain newest300 files by LastWriteTime."})
    resources = [r for r in assemblies["adapt"].net.resources if str(r.name) == "GTSPlusAdaptationInterface.AdaptationTable.xml"]
    if len(resources) != 1 or _sha(resources[0].data) != ADAPTATION_XML_SHA256:
        raise ValueError("embedded adaptation roster drift")
    adaptations = []
    for element in ET.fromstring(resources[0].data).findall("Adaptation"):
        adaptations.append({"file": element.findtext("FileName"), "class": element.findtext("ClassName"),
                            "categories": [c.text for c in element.findall("Categories/Category")]})
    evidence.append({"id": "bootstrap.adaptation-table", "source": "bootstrap.adapt.recovered", "kind": "managed-resource",
                     "locator": "GTSPlusAdaptationInterface.AdaptationTable.xml", "resource_sha256": ADAPTATION_XML_SHA256,
                     "initialization_and_finalization_order": adaptations,
                     "finding": "UserInfo, TGD, DiagAdaptationManager, WebServiceAdaptationManager, FileAdaptation in table order."})
    api_routing = _api_routing(assemblies["pf"], assemblies["adapt"], evidence, adaptations,
                               inspect_managed_bodies(recovered_root / "bin/GTSPlus.exe"))
    for key, pe in assemblies.items():
        imports = [{"dll": str(r.ImportScope.row.Name), "export": str(r.ImportName), "method": str(r.MemberForwarded.row.Name)}
                   for r in (pe.net.mdtables.ImplMap or [])]
        evidence.append({"id": f"bootstrap.{key}.dependencies", "source": f"bootstrap.{key}.recovered", "kind": "cli-metadata",
                         "locator": "AssemblyRef/ImplMap", "assemblies": [str(r.Name) for r in (pe.net.mdtables.AssemblyRef or [])],
                         "pinvoke": imports, "finding": "Exact managed dependencies and native import boundaries; roles are established by the pinned method bodies."})
    ids = {e["id"] for e in evidence}
    for record in TRANSITIONS + HANDOFFS + PERSISTENCE:
        if not set(record["evidence"]) <= ids:
            raise ValueError("unresolved lifecycle evidence reference")
    return {"schema": "gtsplus-lifecycle-domain-v1", "domain": "bootstrap", "sources": sources,
            "evidence": evidence, "states": copy.deepcopy(STATES), "transitions": copy.deepcopy(TRANSITIONS),
            "handoffs": copy.deepcopy(HANDOFFS), "persistence": copy.deepcopy(PERSISTENCE),
            "coverage": copy.deepcopy(COVERAGE), "residuals": copy.deepcopy(RESIDUALS),
            "api_routing": api_routing}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-root", type=Path, default=DEFAULT_INSTALLED)
    parser.add_argument("--recovered-root", type=Path, default=DEFAULT_MAIN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = build(args.installed_root, args.recovered_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out}: "
          f"{len(result['evidence'])} evidence, {len(result['transitions'])} transitions")


if __name__ == "__main__":
    main()
