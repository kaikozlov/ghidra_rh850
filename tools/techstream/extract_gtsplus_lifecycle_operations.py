#!/usr/bin/env python3
"""Extract offline, byte/IL-pinned GTS+ diagnostic operation lifecycle evidence.

Requires installer-original body recovery and auxiliary recovery. GUI members are
redecoded and signature-verified on every build; build/out JS is never trusted.
No application, network, credentials, vehicle, or Windows DLL entry is invoked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pefile

from tools import REPO_ROOT
from tools.techstream.extract_diagnostic_execution_model import anchor
from tools.techstream.extract_gtsplus_tse_managed_semantics import (
    _instructions, _lines, _method_pin, _open, _recovery_proof,
)
from tools.techstream.gtsplus_local_crypto import decode_gui
from tools.techstream.inspect_dotnet_il import format_operand

DEFAULT_ROOT = REPO_ROOT / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"
DEFAULT_RECOVERED = REPO_ROOT / "build/out/gtsplus-unprotected"
DEFAULT_AUX = REPO_ROOT / "build/out/gts-lifecycle-aux"
DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/lifecycle_operations.json"
MANAGED_TYPE = "GTSPlusDiagAdaptationManager.DiagAdaptationManager"

SOURCE_SHA256 = {'aux-installed/CryptgraphCommon.dll': 'a70a55a78b3bea044bffa624a9c2aa668d4621e1a03c213cc0d5eb3ff302b073',
 'aux-installed/CryptgraphResource.dll': 'c9d3d3c35f7af5f3fa4258cea547005846758f67fae2b3326f97b43be6da21b6',
 'aux-installed/GtsPlus-CM.dll': 'b0e8a25289d697bef0da31812d895e55f4745efd000700cfeb66c1e3135addd2',
 'aux-recovered/CryptgraphCommon.dll': '98fc5afd362f6e28aec9f06f71c15c4d6751751a27a8325cdc143ad9f57366b0',
 'aux-recovered/CryptgraphResource.dll': '7a9a2c08f0055fdfed82258835ba68c4a4d41ffeb537bd27caa19ad19d1f16f6',
 'aux-recovered/GtsPlus-CM.dll': 'ebc7c0b359c63d12a80c7fc596e93c226007b915f21032e05efa1046c2b292b2',
 'aux-sidecar/CryptgraphCommon.dll': 'c43577c8174b5d5c285c14f2582aaf1b84e19850b62283c6772fb711949a6176',
 'aux-sidecar/CryptgraphResource.dll': '9f2d7bba218e97aacac917321711e6abaac26625b509770727e4471440c57b47',
 'aux-sidecar/GtsPlus-CM.dll': 'db69e562601efdea05a06e924a9c06baf9ecee207ac3447cd0b7399e88ebce8f',
 'certificate': '857ec034c946604c52fd845134386b5b914936962254048e8766d78fa6b3ad50',
 'cpf': '773becfd6fad75bfaab3d0dbdb0f4e05cdf1511646f76d77ca2c3d0a914691dc',
 'gui': '80ff7eed3a3a429aedc14384befb0f43b8ebd8176868b0bf41135033ce4ea37d',
 'installed/CommandCommon.dll': '89fe3c1f17d7ec58e659a099fc4fc96b55d30534d813c2a4c26211c4d30284c2',
 'installed/DataListIF.dll': 'cce3ecd1203f81914c51d5b2599ee68eb4f7faafa8cbd9bb24fd7390b54d651d',
 'installed/DataMonitorPhase5_DT.dll': '676192240b05e68a890e45f48575f826bc1dd44f935f5df4b77ee36558467519',
 'installed/DataMonitorPhase6_DT.dll': '45633f2c6b2a1540e736cb55cf2374922bb97f97f516690d9b2c2cb710985eeb',
 'installed/DiagAdaptation.dll': '676e077cc4d5d64193687a541509e7adae98eee0b9d28347b748b272b02f2cc0',
 'installed/DiagCommCtrlMain.dll': 'd1ba329ba144bbfe49ba91a2e11bfee397f881e2f37c6c20c79376a6e9849967',
 'installed/GTSPlusDiagAdaptMng.dll': 'c3dd32e0ae0ba3816a1878785862d8cf1d0819d0c4cb5a1d2abf1873cfd9135d',
 'installed/KGP_CommFrameCtrl.dll': '5366aba0f1da6ec7806cb6c8346a4429ce61b9ac7b1495be53e35ee6263b9517',
 'installed/KgpDataMonitorCtrl.dll': '2aa996c250311793f2c865aaea13cb7436fc1ca6196dd7a91d3a5a9be8fa7ad2',
 'recovered/CommandCommon.dll': '98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3',
 'recovered/DiagAdaptation.dll': 'eb4b5ffd08bfd1e18b7c5aa5b3679893fb6d3efc2c9bcd655c5e40038fe8531a',
 'recovered/GTSPlusDiagAdaptMng.dll': '7a56cc6488ad0f982b3b8ed531d5da0677d04f58c92b4b4ea3d0ac6508f27f9e',
 'sidecar/CommandCommon.dll': '2fd7211088bee794d56239d3f2960d03f5747dbe7c20097fca6c34559f80d6da',
 'sidecar/DiagAdaptation.dll': '2912c35c790892ce80f549f213df66887b70a63e17a2c2c644fbeb8dd022d317',
 'sidecar/GTSPlusDiagAdaptMng.dll': '0fd228a9ed15971385d60e34b511b1ac4370adba05a376942c790d2296035748'}

NATIVE = {'active_stop_event': {'file': 'DataListIF.dll',
                       'finding': 'Wrong ECU returnsE0000102 and clears active flag; valid stop queues retained '
                                  'return-control and signals event+4C. Idle/not-active path signals stop event+30.',
                       'function': 'p5 active_test_stop',
                       'sha256': '3f18736e366c9a1b787c7caa2e4271253d805323dd2269af692c63f1b2520b3f',
                       'size': 170,
                       'va': 268688944},
 'active_stop_queue': {'file': 'DataListIF.dll',
                       'finding': 'Under global critical section100752F8 drops obsolete start nodes while keeping '
                                  'queued stop/return-control nodes; sets stop flag and clears current item pointers.',
                       'function': 'CCommEventPhase5AT::ActiveTestStop',
                       'sha256': '5850db93f58ad5454a0fc0e56c3e29cee275966f08addfad3ff2af342671a650',
                       'size': 150,
                       'va': 268662832},
 'adapt_cancel': {'file': 'DiagAdaptation.dll',
                  'finding': 'Requires DLL state2 and matching nonnull singleton; calls CCommCtrlMain::CommandCancel '
                             'and sets instance+10=1; returns boolean true without waiting. Invalid state C0270010, '
                             'mismatched handle C0270011, null C0270001.',
                  'function': 'cancel export',
                  'sha256': 'b1062707f4c4513d9f3d8ceac1b304f940d100bf9ccf62497280dd7751cde894',
                  'size': 915,
                  'va': 268886656},
 'adapt_cleanup': {'file': 'DiagAdaptation.dll',
                   'finding': 'Deletes command aggregate then viewer data controller; clears monitor cache/cancel; '
                              'posts WM_QUIT to adaptation thread, waits INFINITE, closes thread handle/deletes '
                              'critical section; clears caches and frees tracked response allocations.',
                   'function': 'adaptation-owned teardown',
                   'sha256': 'c606172982cff9f1830b9adf4bb8126d2035f8a5aaa51e6af163f02d4b9c2112',
                   'size': 284,
                   'va': 268847024},
 'adapt_execute': {'file': 'DiagAdaptation.dll',
                   'finding': 'Requires DLL state2, exact singleton handle and nonnull instance; accepts UTF8 JSON '
                              'common.apiId/apiArgs/free.freeMsg; resets instance cancel byte+10, parses API id then '
                              'generic-utility or typed dispatch. Invalid JSON C0270003; cancelled before dispatch '
                              'C027000F; response contains common/apiId,resultInfo,optional apiArgs/free. Response '
                              'allocation is tracked for freememory/destroy.',
                   'function': 'execute export',
                   'sha256': '8fbb757e05694a92f0519770edf0d713a78dc56680a8617f8d00838925f52084',
                   'size': 6331,
                   'va': 268880288},
 'aggregate_ctor': {'file': 'DiagCommCtrlMain.dll',
                    'finding': 'One aggregate owns CDataCtrl+4, command controller+7B0, frame controller+7E0, monitor '
                               'controller+B80 and per-ECU capability/response/session caches; their pointers are '
                               'wired together.',
                    'function': 'CCommCtrlSub constructor',
                    'sha256': 'f7b3f41c407f1ebca469017c051d52ed1767486b84ac1747a58295e3a1a3bcb1',
                    'size': 855,
                    'va': 268503440},
 'aggregate_exit': {'file': 'DiagCommCtrlMain.dll',
                    'finding': 'Clears shared-data references, calls frame Disconnect(1), CloseDevice, destroys '
                               'caches, then monitor controller, frame controller, command controller and data '
                               'controller. Transport disconnect occurs before monitor destructor/plugin Stop.',
                    'function': 'CCommCtrlSub destructor',
                    'sha256': 'e7ea89efa9e3f9b853edd7eda8e7f5618165c08fc22d15278ac1169859a88e28',
                    'size': 896,
                    'va': 268504320},
 'api_dispatch': {'file': 'DiagAdaptation.dll',
                  'finding': 'Switch maps DV000008 DTC,009 FFD,013/014 monitor catalog/metadata,015 start,016 '
                             'value,017 stop,019/020/021/022 active catalog/direct/multi/routine init,023 direct '
                             'start,024 routine start,025 stop;038/039/040 customize support/items/set,059/060 simple '
                             'utility info/control,117 create DRS,118 copy DRS,119 copy DLOG,120 read DLOG; '
                             'SC000001/002 diagnosis start/end. Unknown typed id C0270003.',
                  'function': 'ExecuteApi',
                  'sha256': 'f146c6777ab0e0ce3125a110aec8e16589a3845b2d3f68a0e8c4e2002f124789',
                  'size': 5907,
                  'va': 268906672},
 'api_parse': {'file': 'DiagAdaptation.dll',
               'finding': 'Eight-character API grammar: DV=1,SC=2,UG=3 prefix table; positions2..3 and4..7 decimal; '
                          'internal id=(prefix*100+first2digits)*10000+last4digits; stored instance+94.',
               'function': 'GetApiId',
               'sha256': '82e4faaae6880ea1dddf5d89d1903ae1461c6051f5cd2b78165159a2f64d74de',
               'size': 797,
               'va': 268905232},
 'cancel': {'file': 'DiagCommCtrlMain.dll',
            'finding': 'Writes caller value to controller+2C; no wait, thread termination, or transport teardown here.',
            'function': 'CCommandCtrl cancel setter',
            'sha256': '598565f02142df8ec9f97a3dd1c6dddcfcc3999593c5fb3333ac39f7e4c8b4d1',
            'size': 18,
            'va': 268499760},
 'cancel_entry': {'file': 'DiagCommCtrlMain.dll',
                  'finding': 'Missing aggregate returns C0070301; otherwise sets aggregate+7B0+2C to1 and returns0.',
                  'function': 'CCommCtrlMain::CommandCancel',
                  'sha256': '7d77fe0654d3f50127653af56c0625e6f6932cfe605faea35f8f54e747b01aff',
                  'size': 33,
                  'va': 268503056},
 'close_device': {'file': 'KGP_CommFrameCtrl.dll',
                  'finding': 'If device exists disconnect(1) if protocol active, FinalizeDevice, reset connection '
                             'info; returns0.',
                  'function': 'CloseDevice',
                  'sha256': '16015a3db0936f2ac34260e6f9ce7e751a2e0890a329a15f8893f2b90aa7071e',
                  'size': 55,
                  'va': 268642336},
 'customize': {'file': 'DiagAdaptation.dll',
               'finding': 'Parses setCustomizeList entries supportId,itemId,valueList into CSetCustomSnd; one '
                          'CommandExecute; emits successList with supportId,itemId,success per response item; '
                          'validation/command failure maps resultInfo.',
               'function': 'CDAExecSetCustomize::Execute',
               'sha256': '29027fc76a7aacd98b58d018ad8d4de85714a334a7ed4bdfdbe050dc8e1a2e62',
               'size': 1965,
               'va': 268814432},
 'diagnosis_exit': {'file': 'DiagAdaptation.dll',
                    'finding': 'StopCommunicationUtility then DisconnectUtility then unconditional adaptation-owned '
                               'teardown; abort error takes precedence over disconnect error in mapped result.',
                    'function': 'CDAExecEndDiagnosis::Execute',
                    'sha256': '41ae3e0e35ade49b066b5e1df59714f91854681f625c4cbdb1352d50ea8ad336',
                    'size': 508,
                    'va': 268496928},
 'disconnect': {'file': 'KGP_CommFrameCtrl.dll',
                'finding': 'Optional TestPresentStop, signals idle stop; P5/P6 stop keepalive, may initialize '
                           'stop-session path; calls protocol disconnect/destructor, clears active ECU,bus/session and '
                           'selected modes; device kinds1/4 finalize.',
                'function': 'Disconnect',
                'sha256': 'bee0fb37b8bf53393e8200bc99d2feaddff57646cacb3b60f15681f6b003a02c',
                'size': 448,
                'va': 268648720},
 'dispatch': {'file': 'DiagCommCtrlMain.dll',
              'finding': 'Requires data/frame/monitor controllers; resolves (command+8,ECU+1C) plugin; missing module '
                         'C0070101, missing Execute C0070102; clears cancel+2C, constructs six-dword context '
                         '[request,response,&cancel,frame,data,monitor], LineCriticalSection(1), Execute, '
                         'LineCriticalSection(2); returns plugin status without host retry.',
              'function': 'CCommandCtrl::CommandExecute',
              'sha256': '6a12c3284213eb888a67694de9208b4eb27f510843f25a6962953779074aea21',
              'size': 421,
              'va': 268496992},
 'frame_retry': {'file': 'CommandCommon.dll',
                 'finding': 'CCommFrameData+20 signed retry count permits initial attempt plus count retries; retries '
                            'send failure/ordinary receive failure/positive-SID mismatch;90020323 breaks '
                            'immediately.90020326 with receive byte1=31 preserves reply; exhausted90020321 preserves '
                            'negative response bytes. Always frees request/receive temporaries on recovered exits.',
                 'function': 'CCommCachePlus::CommFrameSendReceiveExt',
                 'sha256': 'aa127f5ec9aebeffdd74821523e0dfe4ca9f34c3f6fae43ec8e56c68d104d4d4',
                 'size': 915,
                 'va': 268888816},
 'generic_utility': {'file': 'DiagAdaptation.dll',
                     'finding': 'SC000013/014 select generic utility start/stop; internal ids3000000..3999999 route '
                                'CDAExecUtilityGeneral. Ordinary typed APIs fall through to ExecuteApi.',
                     'function': 'ExecuteUtilityGenericApi',
                     'sha256': '68574168ee5c6e7decf484d61c35fb32e105dc0763a40db8a7648e904bc3d446',
                     'size': 634,
                     'va': 268906032},
 'idle_worker': {'file': 'KGP_CommFrameCtrl.dll',
                 'finding': 'For bus low-nibbleA checks elapsed3000ms under line lock+74; calls stop communication '
                            'service, protocol idle/reset,clears ECU. Distinct legacy idle-session timer, not P5 '
                            'tester-present cadence.',
                 'function': 'WatchIdleThread',
                 'sha256': '97d9e1536877e899cbbf4b80d06503ae9d0d27a3252a96ac8ffb5e9e3527f9ae',
                 'size': 569,
                 'va': 268673616},
 'keepalive_start': {'file': 'KGP_CommFrameCtrl.dll',
                     'finding': 'Skips bus1C/low-nibbleA; DB class112 selectorDD then class111 frame; under lock+8C '
                                'caches frame, sets start event and waits5000ms readiness. Same active ECU is no-op. '
                                'Startup failure90020401; missing frame90020104.',
                     'function': 'CCommFrameCtrl::TestPresentStart',
                     'sha256': '004e791dc89e6507f26699528453d938769952918e73455b540788f37d356a6a',
                     'size': 504,
                     'va': 268672624},
 'keepalive_stop': {'file': 'KGP_CommFrameCtrl.dll',
                    'finding': 'If no thread90020402; if active signals stop then waits185000ms acknowledgement; '
                               'nonzero wait90020402, otherwise0.',
                    'function': 'TestPresentStop',
                    'sha256': '5e8578e74142171781cf7cd4a4b6486d4ba469e60aba54bfa42efa20619e4fe7',
                    'size': 78,
                    'va': 268673136},
 'keepalive_worker': {'file': 'KGP_CommFrameCtrl.dll',
                      'finding': '2000ms idle cadence with last-activity timestamp under lock+8C. Successful SID10/50 '
                                 'sets current session3; other frames require rx>=4,SID+40,and two echoed bytes then '
                                 'copy byte3. Send/receive/malformed response resets session0; thread continues to '
                                 'next cadence.',
                      'function': 'SendTestPresentThread',
                      'sha256': 'cbc4bc090fb569e497f76cdb0acca6647414359170a6290578577aa4fcf88474',
                      'size': 807,
                      'va': 268667424},
 'line_lock': {'file': 'KGP_CommFrameCtrl.dll',
               'finding': 'Mode1 EnterCriticalSection(this+74); other mode LeaveCriticalSection. This is distinct from '
                          'keepalive lock+8C.',
               'function': 'CCommFrameCtrl::LineCriticalSection',
               'sha256': '3742cda83c3ae738366ed5aadc0564e6f7e00c01dead5d1eea027a704bd3c77d',
               'size': 32,
               'va': 268657600},
 'monitor_destroy': {'file': 'KgpDataMonitorCtrl.dll',
                     'finding': 'If loaded resolves Stop, calls it then FreeLibrary; queue destructor subsequently '
                                'closes both events.',
                     'function': 'CDataMonitorCtrl destructor',
                     'sha256': '85697e98a3a0574edd8c68c1160fe1ca81faa08cf23553f4626c9324e57fe5d1',
                     'size': 97,
                     'va': 268653808},
 'monitor_load': {'file': 'KgpDataMonitorCtrl.dll',
                  'finding': 'LoadLibraryExW(flags8), resolves Run and passes queue,data controller,frame controller. '
                             'Nonzero Run calls Stop,FreeLibrary,clears module.',
                  'function': 'CDataMonitorCtrl::DataMonitorInit',
                  'sha256': 'd2d54ad5a2141c2f3d18ac15029f086d40e670913d6db4fd23c9240b4e35240c',
                  'size': 337,
                  'va': 268656528},
 'monitor_route': {'file': 'KgpDataMonitorCtrl.dll',
                   'finding': 'Checks request/frame/monitor pointers; selects generation/multi-monitor mode; same '
                              'ECU/mode reuses DLL, otherwise Stop+FreeLibrary then reinitialize. Enqueues only after '
                              'Run succeeds. Missing module C0060501.',
                   'function': 'CDataMonitorCtrl::DataMonitorRun',
                   'sha256': '9f9dba15e36b4941d7af80ba32fc69f04781064079de913250a052204fcb9df6',
                   'size': 826,
                   'va': 268656880},
 'p5_cleanup': {'file': 'DataMonitorPhase5_DT.dll',
                'finding': 'Mode0 is idempotent; stops active test or data monitor according to mode bits; optional '
                           'additional active cleanup for bit40; final vtable54 teardown and resets mode+1C4=0.',
                'function': 'worker stop-monitor callback',
                'sha256': '1374ae4e6cc5421250964c6f11dca3bad800556000201845cbcd4949b1943885',
                'size': 110,
                'va': 268505968},
 'p5_commands': {'file': 'DataMonitorPhase5_DT.dll',
                 'finding': 'Mode+1C4 gates starts vs active operations:9 start;A idempotent stop;B direct active '
                            'value;C active stop;38 multimonitor start;57 DRS capture;60 dual active;89 fuel;B0 '
                            'routine active. Invalid mode/command90050405; writes response error/status before '
                            'signaling completion. DRS57 brackets settings/start and stop records, retains first error '
                            'until final stop write.',
                 'function': 'CDataMonitorThreadP5::command dispatch',
                 'sha256': '259e7e45e4d4e88f6889dfcc14a1b98888e066f52f7529b32c76026a20a7deec',
                 'size': 285,
                 'va': 268487664},
 'p5_error': {'file': 'DataMonitorPhase5_DT.dll',
              'finding': 'Sets error-present+1070 and original error+1074 in each nonnull of three live buffers.',
              'function': 'worker error propagation',
              'sha256': '14534d2a738695d4460399f634d82c993cc4a449291814bc8d6b1ee7aa555467',
              'size': 149,
              'va': 268502912},
 'p5_run': {'file': 'DataMonitorPhase5_DT.dll',
            'finding': 'Requires no worker handle and nonnull queue/data/frame; borrows queue events; CreateThread '
                       'stack4000 at10011400, priority1; copies frame cancel pointer+C0.',
            'function': 'CDataMonitorThreadBase::Run',
            'sha256': '67298194b0cfc68bafc21f19f6a5b56151700c85c8ca38db4e83d437a5582055',
            'size': 343,
            'va': 268502560},
 'p5_stop': {'file': 'DataMonitorPhase5_DT.dll',
             'finding': 'Signals exit event+1B0; waits worker1000ms; ALL nonzero wait results invoke '
                        'TerminateThread(handle,0) and vtable+20 stop-monitor. Then CloseHandle,clear worker '
                        'handle,delete3 subobjects at+50,+98,+E0.',
             'function': 'CDataMonitorThreadBase::Stop',
             'sha256': '5044e0a746a90eb22966b87c8ce1e4081e026cf5344dc2d78befb06b251e1b1f',
             'size': 128,
             'va': 268505728},
 'p5_worker': {'file': 'DataMonitorPhase5_DT.dll',
               'finding': 'Waits write/exit events INFINITE; gets six-pointer context, dispatches vtable0, signals '
                          'finish even after nonzero command status, then propagates error. Exit event invokes '
                          'stop-monitor then returns. Wait failure reports A0050511.',
               'function': 'CDataMonitorThreadBase::ThreadProc',
               'sha256': '4e23c90c08c0e891737dacbdd8fa1582f3b5afd2bd56340b2256841f0ac077a1',
               'size': 469,
               'va': 268506112},
 'p6_run': {'file': 'DataMonitorPhase6_DT.dll',
            'finding': 'Same explicit queue/data/frame prerequisites, borrowed event ownership, stack4000 worker '
                       'at1000F8D0 and priority1.',
            'function': 'P6 worker Run',
            'sha256': '98abfc34ba86d8ae2391f27f9e79fe7e5a62f05fc6ece679a8bc59db2f39564e',
            'size': 343,
            'va': 268495600},
 'p6_stop': {'file': 'DataMonitorPhase6_DT.dll',
             'finding': 'Exit event,1000ms wait, any nonzero=>TerminateThread then stop callback; closes handle and '
                        'deletes three subobjects, matching P5 contract by independently inspected body.',
             'function': 'P6 worker Stop',
             'sha256': '1232cb06644db6c1c2b5c11aba616e6d45b99625abd2cc582acb6d0156308575',
             'size': 128,
             'va': 268498768},
 'plugin_cancel_poll': {'file': 'CommandCommon.dll',
                        'finding': 'Reads shared pointed flag exactly==1 and returns A0040003; otherwise0. This proves '
                                   'recorder reader cooperative poll, not every plugin polls at the same granularity.',
                        'function': 'CCmdGetDdrInfoP5Base::CheckCommandCancel',
                        'sha256': 'e73e95ddc5da555be6277fe661b0346cb52950f4dd9876dae564c8c98d84a4a8',
                        'size': 54,
                        'va': 268649744},
 'poll_thread': {'file': 'DataListIF.dll',
                 'finding': 'Event-driven sender/receiver states choose active/event/live-poll slots0/1/2. Slot2 alone '
                            'retries send/receive up to configured+84 bound. Negative responses retain NRC and become '
                            'operation-specific E00002xx/03xx/05xx/06xx/08xx/09xx callbacks; certain active-stop '
                            'failures end slot and continue, others park state4 until event. Stop attempts queued '
                            'active return-control, clears dynamic DIDs, notifies stop; thread exit releases line, '
                            'Disconnects and frees receive buffer.',
                 'function': 'p5diag_tf::J2534DiagInterface::ThreadMain',
                 'sha256': '6ea9c2cc2db3a1d5d39e968568ac8209e4537264e472528ad623159af0f9abae',
                 'size': 4027,
                 'va': 268684464},
 'queue_ctor': {'file': 'KgpDataMonitorCtrl.dll',
                'finding': 'Creates two unnamed manual-reset initially nonsignaled events; single pending pointer '
                           'starts null.',
                'function': 'CDataMonitorCommandQue constructor',
                'sha256': '61816cbeee3b06b62290b0e3f2906c30a52239255a6976a0f1a8fd953f698389',
                'size': 54,
                'va': 268496112},
 'queue_get': {'file': 'KgpDataMonitorCtrl.dll',
               'finding': 'Copies exactly24 bytes/six pointers from pending context; empty C0060603/null output '
                          'C0000001. Does not consume/free request or response.',
               'function': 'CDataMonitorCommandQue::GetCommandQue',
               'sha256': 'd2567dd1d94215afb809bcb7a3032dc2eff83dd4b5756b04d320435be3f89a8d',
               'size': 57,
               'va': 268641056},
 'queue_set': {'file': 'KgpDataMonitorCtrl.dll',
               'finding': 'Null C0000001; occupied slot C0060601. Stores borrowed tagCOMMAND_DATA*, resets finish '
                          'event, sets write event, waits INFINITE for finish, reads response+18; nonzero wait '
                          'A0060702; resets write event and clears slot.',
               'function': 'CDataMonitorCommandQue::SetCommandQue',
               'sha256': 'bdff55bf874a3354e7063229ca81e9637c50ea2157be8fbe10405d9d38664f9e',
               'size': 221,
               'va': 268641152},
 'response': {'file': 'DiagCommCtrlMain.dll',
              'finding': 'Copies GetTickCount into response+10, target ECU into+1C, status into+18 and status!=0 '
                         'into+14.',
              'function': 'CCommCtrlSub::CommandExecute',
              'sha256': 'b274a061c84ba6cead473cef9eaf454353a66d111e31a21845f6c0c42fb87302',
              'size': 64,
              'va': 268505296},
 'response_cache': {'file': 'CommandCommon.dll',
                    'finding': 'Per-ECU/request cache hit reuses returned bytes; cached empty reply returns91010009. '
                               'Miss performs wire helper and stores eligible statuses0,91010009,90020323. Distinguish '
                               'cached lookup from retry.',
                    'function': 'CCommCachePlus::CommCacheSndRcvExt',
                    'sha256': 'c9ab431b808c328c2860e4b00a5636826b973a15af984dbb6c93fc21e4996bb4',
                    'size': 306,
                    'va': 268887040},
 'result_classifier': {'file': 'DiagAdaptation.dll',
                       'finding': '0=>result0/code0; C0270003=>-1/1FFF; C027000F or A0040003=>result1/codeC000 '
                                  'cancellation; other adaptation-family errors=>-1/3FFF; '
                                  '91010008/91010009/90020A01=>-1/3002; remaining=>-1/3001. Detail code is supplied '
                                  'separately from original status.',
                       'function': 'resultInfo classifier',
                       'sha256': 'df75528947e5c2d75bf514d0a2addf2044dee44a4c21ac9d99e1944972690e1f',
                       'size': 168,
                       'va': 268859760},
 'send_session': {'file': 'KGP_CommFrameCtrl.dll',
                  'finding': 'Stops active keepalive while switching/initializing transport; P5/P6 generation '
                             'low5=14/15/16 and classifier2 require D1 then D2 session when current!=3; forced session '
                             'path checks each result and clears judgement flag. Initialization failure Disconnect(0); '
                             'ordinary send result is returned, not a blanket retry loop.',
                  'function': 'CCommFrameCtrl::SendProc',
                  'sha256': '8056d7e922f04a0845a5f0b9b6e43fba9877606559a28079a7ce7a45f39697ce',
                  'size': 1670,
                  'va': 268664592},
 'simple_control': {'file': 'DiagAdaptation.dll',
                    'finding': 'Parses ecuId/urId/ctrlType; ctrlType1 emits start/routineInfo and optional '
                               'resultPatternData; ctrlType3 emits '
                               'result,routineStatusRecordList,statusDisplayData/stringId; CommandExecute status maps '
                               'resultInfo.',
                    'function': 'CDAExecGetSimpleOperationUtilityResult::Execute',
                    'sha256': 'a9f987d590d456a20493aad87a64feb3f57908436ac6c1ef3e1d49fb4c4adb4d',
                    'size': 1526,
                    'va': 268765776},
 'simple_info': {'file': 'DiagAdaptation.dll',
                 'finding': 'Parses ecuId/urId; typed command returns timer/checkInterval/startScreen metadata; joins '
                            'viewer class302 startScreenId_V.',
                 'function': 'CDAExecGetSimpleOperationUtilityInfo::Execute',
                 'sha256': '97bdf98e237df4f1450bf2b094e80df3fa5fd1267d4d9f4069c94be87ca7065b',
                 'size': 846,
                 'va': 268764912},
 'stop_active': {'file': 'DiagAdaptation.dll',
                 'finding': 'Constructs CStopActTstSnd(version2), parses ecuId, CommandExecute, resultInfo mapping; '
                            'destroys typed stack objects on exit.',
                 'function': 'CDAExecStopActTst::Execute',
                 'sha256': 'a3d8436b0f6a0b4d72a29e9addc07c2fe6acdd337e6c798d7adaad121da4e302',
                 'size': 553,
                 'va': 268840464},
 'stop_monitor': {'file': 'DiagAdaptation.dll',
                  'finding': 'Parses ecuId, constructs CStopDatMonSnd/Rcv, calls CommandExecute. Only success invokes '
                             'adaptation monitor-buffer reset; error maps resultInfo and destroys typed stack objects.',
                  'function': 'CDAExecStopDatMon::Execute',
                  'sha256': '467e1b0e9f62a39e252e16a0f2db362c5242ed22cf19391b74e22e678341970c',
                  'size': 563,
                  'va': 268841024},
 'utility_abort': {'file': 'DiagCommCtrlMain.dll',
                   'finding': 'If UtilityPlusFrontNK is loaded and ComUtilityAbort resolves, clears same cancel '
                              'pointer and calls it with null request/response six-dword context; absent utility '
                              'module/export returns0.',
                   'function': 'CCommandCtrl::StopCommunicationUtility',
                   'sha256': '455e3a637aaa21340e4234cdbb5756ef32dd5652c0654744af555d778aad6a43',
                   'size': 323,
                   'va': 268501760},
 'utility_disconnect': {'file': 'DiagCommCtrlMain.dll',
                        'finding': 'ComUtilityDisconnect uses same six-dword context and clears cancel; absent utility '
                                   'module/export is benign0.',
                        'function': 'CCommandCtrl::DisconnectUtility',
                        'sha256': 'bca63b42403b6015e9c080d58e156a9400988e94427b7350c97a4364931ff949',
                        'size': 323,
                        'va': 268497424},
 'utility_stop': {'file': 'DiagCommCtrlMain.dll',
                  'finding': 'Requires loaded utility module and ComUtilityFront; null owner A0040004, missing module '
                             'C0070101, missing export C0070102. Clears cancel and returns plugin result.',
                  'function': 'CCommandCtrl::StopUtility',
                  'sha256': 'b4ad4d1abdebce48f769cd3ac6573e954b5710803c4044e7ea0f0995b48e7ab5',
                  'size': 471,
                  'va': 268502096},
 'plugin_resolver': {'file': 'DiagCommCtrlMain.dll',
                     'function': 'CCommandCtrl plugin resolver',
                     'va': 0x1000F540,
                     'size': 1111,
                     'sha256': 'c50355448ea1e91cf291a8a71edcd7448b837e67979ce54deb5808504cff7ef8',
                     'finding': 'Start commands9/38 changing ECU preload roleA/B/C/47 modules for stop,active,'
                                'active-stop and related operations. Other roles use one replaceable module slot; '
                                'previous module is freed before LoadLibraryExW(flags8). DB class113 resolves '
                                '(role,ECU); missing DB row C0040101. Cached modules are reused by later stop/'
                                'active commands; missing cached module falls back to ordinary DB lookup.'}}

BYTE_WINDOWS = {'api_parse': [(269175136, '010000004456000002000000534300000300000055470000')],
 'dispatch': [(268497159, '8b43048b4b088945f48b430c83c32c6a01897de48975e88945f8894df0c70300000000895decff1560510110')],
 'frame_retry': [(268889355, '8b4db841894db83b4db00f8fbd000000')],
 'p5_stop': [(268505753, '68e8030000ffb6a4010000ff15f0b2011085c074156a00ffb6a4010000ff1510b30110')],
 'plugin_cancel_poll': [(268649744, '8b41088b40088338017528')],
 'poll_thread': [(268685352, '83fe020f8542feffff8b8590efffff40398784000000')],
 'queue_set': [(268641175, '837b0400740ab8010606c0'), (268641262, '6affff730cff15a000041085c07409')],
 'result_classifier': [(268859794, '81fe030027c0741281fe0f0027c0744a'), (268859866, '81fe030004a0740abf01300000')]}

MANAGED = {'DiagFunction': {'body_sha256': '28f823b223bc27b453f111a5d2f875937a99f95f97b9ead30e57b128abe59943',
                  'body_size': 652,
                  'rva': 12092},
 'EndDiagnosis': {'body_sha256': 'b137c0ef6edbf41d868926b42bc9cd52807368f589a83db4ff8536374bd760a9',
                  'body_size': 456,
                  'rva': 11636},
 'ExecuteAdaptation': {'body_sha256': 'f28b676190c3efcf42d19a084af1ac758ea6a1ab0fff1025fb76659cf1ca3988',
                       'body_size': 216,
                       'rva': 10184},
 'FinalizeAdaptation': {'body_sha256': 'a5b2b0847e4e53712a38f4d051466ac5f94c78fe7dcc3a47594d24be9bc632c9',
                        'body_size': 40,
                        'rva': 8423},
 'LoadDiagAdaptation': {'body_sha256': '9e1c00be34c4a9c906263b6b03bad82e235457a2fe34d4450ae2ef9569329ccd',
                        'body_size': 1528,
                        'rva': 8464},
 'StartDiagnosis': {'body_sha256': '13c775ada20d9faef7c6516a557dca27118aecffbadb17f7393a0e9796bd0d38',
                    'body_size': 1236,
                    'rva': 10400},
 'UnloadDiagAdaptation': {'body_sha256': 'f0d37834e283747d152d48cdc3a3fda3742d878775c6122ab064253c945c585a',
                          'body_size': 192,
                          'rva': 9992}}

UI = {'buffer_close': {'asset': 'js/gts/common/gts_base_buffer.js',
                  'class': 'GtsBaseBuffer',
                  'finding': 'Waits savingProm.finally before close acknowledgement,port.close and reference clearing.',
                  'method': 'cmdClose',
                  'sha256': 'c96a53fa3551aeb5c38fd5329a504a0337e7c66e0a3e2b2ea683e42b2d684ac8'},
 'buffer_save': {'asset': 'js/gts/common/gts_base_buffer.js',
                 'class': 'GtsBaseBuffer',
                 'finding': 'Writes timestamped path/data filename through writeFile(mode0,ack=true); ACK includes '
                            'key/path/time, final result sends Succeed/Failed; savingProm completion always released '
                            'in finally.',
                 'method': 'saveToPlatform',
                 'sha256': 'db120939adbcc88ccd7cd217c91f130f2949bbfd4da0eab4c09329d7a9c18167'},
 'buffer_save_completion': {'asset': 'js/gts/common/buffer_interface.js',
                            'class': 'BufferInterface',
                            'finding': 'Verifies stored hash, posts save, waits saveFinish plus saveInfo then addData '
                                       'and optional createHashFile; resolves save deferred only then.',
                            'method': 'save',
                            'sha256': '24acb3cfd3180cd24ea87a45bb6a2382e18821cfbf5e8230f81f38526ea9f05b'},
 'frontend_active_close': {'asset': 'js/gts/active_test_panel/active_test_panel_worker.js',
                           'class': 'ActiveTestPanelWorkerModel',
                           'finding': 'Panel close requests moveSessionCgw(ecuId,sessionDiagMode0); distinct from '
                                      'stopActTst.',
                           'method': 'closeActiveTestPanel',
                           'sha256': '301b8e96e3c3d5d313ba918d6e4eb4f96a1856a4d6fd39906e772ebec8eacd35'},
 'frontend_active_start': {'asset': 'js/gts/active_test_panel/active_test_panel_worker.js',
                           'class': 'ActiveTestPanelWorkerModel',
                           'finding': 'Passes parameter payload unchanged to platform startActTst and propagates '
                                      'rejection.',
                           'method': 'startActiveTest',
                           'sha256': '4e482c8a1640bd22382cc21057bbed9941bbd95555c1f05ba046a3db76f9fec5'},
 'frontend_active_stop': {'asset': 'js/gts/active_test_panel/active_test_panel_worker.js',
                          'class': 'ActiveTestPanelWorkerModel',
                          'finding': 'Stops multi-active JavaScript periodic command before stopActTst; error '
                                     'rejected.',
                          'method': 'stopActiveTest',
                          'sha256': 'cbd75a934ffc7000ab8a4a9e49dc53fe0b426f11ea70108df68d4f9517b82356'},
 'frontend_customize': {'asset': 'js/gts/customize/customize_worker.js',
                        'class': 'CustomizeWorkerModel',
                        'finding': 'Maps supportId,itemId,valueList; Subaru exclusion returns code without write; '
                                   'otherwise setCustomize; failures return {detailCode,code,isError:true} rather than '
                                   'throwing.',
                        'method': 'setCustomize',
                        'sha256': '68a4f7438e0f5efb6b85460dc1d6ca77125bc35414d16198b65d5c55c6f95921'},
 'frontend_monitor_exit': {'asset': 'js/gts/datalist/datalist_worker.js',
                           'class': 'DatalistWorkerModel',
                           'finding': 'Attempts stop unless already stopped; logs stop errors and continues '
                                      'normal-mode restoration/confirmation; buffer closes only if check mode cleared; '
                                      'result retains current check mode.',
                           'method': 'exitDatalist',
                           'sha256': '9296a2f2cb4b2d35832f01a11ac58a91456422bef429ad14fe0187254e6d8dae'},
 'frontend_monitor_start': {'asset': 'js/gts/datalist/datalist_worker.js',
                            'class': 'DatalistWorkerModel',
                            'finding': 'Leaves check mode if needed, clears buffer, sends startDatMon with per-ECU '
                                       'signal list; only enable==1 starts value polling and resets timing/trigger '
                                       'state.',
                            'method': 'startDatalist',
                            'sha256': 'f83e44bf7f270219b80397bf761a68fca86570da285efca81368cdf1d2241589'},
 'frontend_monitor_stop': {'asset': 'js/gts/datalist/datalist_worker.js',
                           'class': 'DatalistWorkerModel',
                           'finding': 'Stops JavaScript polling before stopDatMon; MODE_STOP set only on success; '
                                      'failure rejected.',
                           'method': 'stopDatalist',
                           'sha256': '41bb96a9e71d6d431baa9e48a97b6c265bf7ec397d4c6605b5229fa77b9b7dfa'},
 'frontend_poll': {'asset': 'js/gts/common/command_thread_object.js',
                   'class': 'CommandThreadObject',
                   'finding': 'First poll setTimeout0; schedules next only after successful Promise completion and '
                              'only while command id remains registered. Rejection deletes registration and sends '
                              'error result; stop clears timer/registration but does not cancel an in-flight Promise.',
                   'method': 'start',
                   'sha256': 'd7f96e48033e766450e9ab71faa61971cfa4667c31eb98d06a04c7331b25cde1'},
 'frontend_reader_poll': {'asset': 'js/gts/dtc/dtc_worker.js',
                          'class': 'DtcWorkerModel',
                          'finding': 'Sequential DTC,MIL,monitor status,enhanced-generic-setting,save-system-DTC and '
                                     'presentation Promise chain; failure rejects mapped result/errorCode and shared '
                                     'command scheduler stops the loop.',
                          'method': 'getDtcOfRepeat',
                          'sha256': 'a95124b4e168c64f7495d07adab9bf7eff9342f3e59e7352b644160f291d9629'},
 'frontend_reader_stop': {'asset': 'js/gts/dtc/dtc_worker.js',
                          'class': 'DtcWorkerModel',
                          'finding': 'Stops JS DTC loop registration; no automatic cancellation of already-running '
                                     'native read.',
                          'method': 'stopDtcLoop',
                          'sha256': '666d21fe55fa6462d40fda31973d88e8221c88af6c121bc4319cd4ae84ccd1da'},
 'frontend_record_exit': {'asset': 'js/gts/datalist/datalist_worker.js',
                          'class': 'DatalistWorkerModel',
                          'finding': 'Stops poll/native monitor, attempts normal-mode restore, changes record mode; '
                                     'optional isStop prevents restart only after normal mode confirmed; returns '
                                     'errors as resolved values.',
                          'method': 'exitRecording',
                          'sha256': 'c223d74a504a08c82f97d0480d46f5a2ad99dfd3af2d093aecd49d81504c7fe5'},
 'frontend_record_save': {'asset': 'js/gts/datalist/datalist_worker.js',
                          'class': 'DatalistWorkerModel',
                          'finding': 'Builds selected-signal/ECU/trigger/flag metadata; Promise.all buffer '
                                     'configuration,saveBuffer,clearBuffer. BufferInterface defers clear while save '
                                     'pending.',
                          'method': 'saveSnapshotRecord',
                          'sha256': '30ed00435ed8fc70538eb399243e5b15a25d945f804f4f76bc2a242eeda6e131'},
 'frontend_record_start': {'asset': 'js/gts/datalist/datalist_worker.js',
                           'class': 'DatalistWorkerModel',
                           'finding': 'DTC/check-trigger recording stops monitor, optionally moves/confirms check '
                                      'mode, clears/reselects buffer trigger PID (P5/P6 PID8100), restarts monitor and '
                                      'polling. Other trigger types change mode only. DTC branches resolve failures as '
                                      'values.',
                           'method': 'startRecording',
                           'sha256': '8401c00892c8d09592df0d0a37faa943d1992225c593a890d5c3a1e22027e081'},
 'frontend_routine_start': {'asset': 'js/gts/active_test_panel/active_test_panel_worker.js',
                            'class': 'ActiveTestPanelWorkerModel',
                            'finding': 'Separate platform startRoutineActTst call, same parameter and Promise '
                                       'contract.',
                            'method': 'startRoutineActiveTest',
                            'sha256': '727e05a69c2ab77da18fd46d9387e86970019f8833f8b760d751ea302145e3e5'},
 'frontend_simple_poll': {'asset': 'js/gts/simple_operation_utility/simple_operation_utility_worker.js',
                          'class': 'SimpleOperationUtilityWorkerModel',
                          'finding': 'Polls native ctrlType3; terminal result1/2/3/5/6 or API error forces '
                                     'processing-time beyond configured timer; timer tracks checkInterval plus call '
                                     'runtime, finally ends/sets timeout or schedules next setTimeout(checkInterval).',
                          'method': 'simpleOperationUtilityRoutine',
                          'sha256': '30027677ee243e60fcec4651f2375f7bb3f6b9cd599d7b33cbb43845abd9090a'},
 'frontend_simple_stop': {'asset': 'js/gts/simple_operation_utility/simple_operation_utility_worker.js',
                          'class': 'SimpleOperationUtilityWorkerModel',
                          'finding': 'Stop is ctrlType2; rejection converted to a resolved resultInfo response. '
                                     'Stopping interval-response timer is a separate worker command.',
                          'method': 'getSimpleOperationUtilityStop',
                          'sha256': 'c586d5d022c034654e9017c024a2bc6f62d3e2b75573c35ecd9ac3bc13d414ae'},
 'frontend_stop_timer': {'asset': 'js/gts/common/command_thread_object.js',
                         'class': 'CommandThreadObject',
                         'finding': 'Clears scheduled timeout and deletes command id; native cancel is a separate API.',
                         'method': 'stop',
                         'sha256': 'ddea2cd2d76988ee9f6d6fa26f386590e5f82646c68e4ca9064513d82541299b'}}

UI_SHA256 = {'js/gts/active_test_panel/active_test_panel_worker.js': '635414357cb27bed9b64b5b0f2d8b689fa80d93e1432de2aa53e8e8c56da39d3',
 'js/gts/common/buffer_interface.js': 'e36b60b6144ab91b31fe1f03ac78e1b66b55ee9d8fa745766e0910fc0839be0d',
 'js/gts/common/command_thread_object.js': '903018328a971050998fd2582e7608bcf47d8eb04f948a1379dead88996602b9',
 'js/gts/common/gts_base_buffer.js': '4c88bfa0675bfdac9cfec1482a1b53a64ce9cb71dc2c0bf3cbd9914098493dac',
 'js/gts/common/gts_platform_raw_interface.js': '00e737331886aade43df5102c81c643defdc566ea0461f22cfa96ded4c4d019f',
 'js/gts/customize/customize_worker.js': '49515174dd52742c74a854f0405df17141be4b71fecb6f7d314deeae43396244',
 'js/gts/datalist/datalist_worker.js': 'f7b4d225ef6c6367fccba401a2f74c1a0f6c1644cf3df6a39b37a5a13b1daf4c',
 'js/gts/dtc/dtc_worker.js': 'a4879f86d677ca7af886f700698cbbfd20858022a586f40ce2c5f35594977c4d',
 'js/gts/simple_operation_utility/simple_operation_utility_worker.js': 'f4fad09f781ea94dcece724367ea7565cc041fed2f554b58e19f5a8423e760c9'}

API_NAMES = ['PFCMD_CANCEL_BY_CANCEL_ID',
 'PFCMD_GET_DTC',
 'PFCMD_GET_FFD',
 'PFCMD_GET_DAT_MON_SIGNAL_LIST',
 'PFCMD_GET_DAT_MON_SIGNAL_INFO',
 'PFCMD_START_DAT_MON',
 'PFCMD_GET_DAT_MON_VALUE',
 'PFCMD_STOP_DAT_MON',
 'PFCMD_START_ACT_TST',
 'PFCMD_START_ROUTINE_ACT_TST',
 'PFCMD_STOP_ACT_TST',
 'PFCMD_SET_CUSTOMIZE',
 'PFCMD_GET_SIMPLE_OPERATION_UTILITY_INFO',
 'PFCMD_GET_SIMPLE_OPERATION_UTILITY_RESULT',
 'PFCMD_CREATE_DRS_FILE',
 'PFCMD_READ_DLOG_FILE']

LIFECYCLE = {'states': [{'id': 'operations.unloaded', 'owner': 'GTSPlusDiagAdaptMng', 'meaning': 'No native module/instance'},
            {'id': 'operations.ready',
             'owner': 'GTSPlusDiagAdaptMng + DiagAdaptation',
             'meaning': 'Created singleton owns native aggregate; eligible typed operations'},
            {'id': 'operations.executing',
             'owner': 'CCommandCtrl',
             'meaning': 'Caller owns request/response; line-critical plugin call running'},
            {'id': 'operations.cancel_requested',
             'owner': 'Cancel lane + DiagAdaptation',
             'meaning': 'Cooperative cancel pointer and adaptation byte set; completion not acknowledged'},
            {'id': 'operations.monitor_idle',
             'owner': 'CDataMonitorCtrl',
             'meaning': 'DLL/worker may remain loaded but active mode0'},
            {'id': 'operations.monitor_running',
             'owner': 'DataMonitor worker + DataListIF',
             'meaning': 'Native polling/active engine active; frontend values read live buffers'},
            {'id': 'operations.active_running',
             'owner': 'DataListIF',
             'meaning': 'DID/RID keyed start/return-control items queued alongside monitor'},
            {'id': 'operations.recording',
             'owner': 'Frontend Datalist worker + buffer worker',
             'meaning': 'Trigger/wait/record modes and selected-signal snapshot buffer'},
            {'id': 'operations.saving',
             'owner': 'BufferInterface + buffer worker',
             'meaning': 'File ACK issued; data and index/hash completion may remain pending'},
            {'id': 'operations.faulted',
             'owner': 'DataListIF + frontend',
             'meaning': 'Error callback/response recorded; loop can stop/park until explicit command'},
            {'id': 'operations.teardown',
             'owner': 'DiagAdaptation',
             'meaning': 'Utility abort/disconnect, aggregate deletion and worker/file closure'},
            {'id': 'operations.closed',
             'owner': 'GTSPlusDiagAdaptMng',
             'meaning': 'Successful destroy and unload; fresh StartDiagnosis required'}],
 'transitions': [{'id': 'operations.start',
                  'from': 'operations.unloaded',
                  'to': 'operations.ready',
                  'trigger': 'SC000001',
                  'guard': 'No existing instance; settings/DLL/create/native response successful',
                  'action': 'Build AppPath/region/language payload; create aggregate,retain instance',
                  'evidence': ['operations.managed.StartDiagnosis', 'operations.aggregate_ctor']},
                 {'id': 'operations.start_failure',
                  'from': 'operations.unloaded',
                  'to': 'operations.unloaded',
                  'trigger': 'StartDiagnosis failure',
                  'guard': 'Serialization/create or native response missing/nonzero',
                  'action': 'Destroy created instance when applicable,clear it and unload; JSON error response',
                  'evidence': ['operations.managed.StartDiagnosis']},
                 {'id': 'operations.dispatch_command',
                  'from': 'operations.ready',
                  'to': 'operations.executing',
                  'trigger': 'DV request',
                  'guard': 'Valid eight-character apiId and required typed arguments',
                  'action': 'Construct typed command/response; resolve plugin; clear cancel; enter line lock; call '
                            'Execute',
                  'evidence': ['operations.api_parse',
                               'operations.api_dispatch',
                               'operations.dispatch',
                               'operations.frontend_api_ids']},
                 {'id': 'operations.command_complete',
                  'from': 'operations.executing',
                  'to': 'operations.ready',
                  'trigger': 'Plugin returns',
                  'guard': 'Any status',
                  'action': 'Release line lock; stamp response; classify resultInfo; convert response UTF8/free native '
                            'memory',
                  'evidence': ['operations.dispatch',
                               'operations.response',
                               'operations.result_classifier',
                               'operations.managed.DiagFunction']},
                 {'id': 'operations.request_cancel',
                  'from': 'operations.executing',
                  'to': 'operations.cancel_requested',
                  'trigger': 'SC000005 on cancel lane',
                  'guard': 'Matching created singleton/native state2',
                  'action': 'Set controller cancel flag and adaptation cancelled byte; return acceptance boolean '
                            'without waiting',
                  'evidence': ['operations.managed.DiagFunction',
                               'operations.adapt_cancel',
                               'operations.cancel_entry',
                               'operations.cancel']},
                 {'id': 'operations.cancel_complete',
                  'from': 'operations.cancel_requested',
                  'to': 'operations.ready',
                  'trigger': 'Plugin cancellation poll/return',
                  'guard': 'Flag observed by participating plugin',
                  'action': 'A0040003/C027000F mapped result1/codeC000; response completes independently of cancel '
                            'acceptance',
                  'evidence': ['operations.plugin_cancel_poll',
                               'operations.result_classifier',
                               'operations.managed.DiagFunction']},
                 {'id': 'operations.monitor_start',
                  'from': 'operations.ready',
                  'to': 'operations.monitor_running',
                  'trigger': 'DV000015',
                  'guard': 'Native enable1; idle mode; supported bus/category',
                  'action': 'Load/reuse generation DLL; create worker; borrowed single-slot context waits completion; '
                            'frontend starts value polls',
                  'evidence': ['operations.monitor_load',
                               'operations.monitor_route',
                               'operations.queue_set',
                               'operations.p5_commands',
                               'operations.frontend_monitor_start']},
                 {'id': 'operations.monitor_switch',
                  'from': 'operations.monitor_running',
                  'to': 'operations.monitor_running',
                  'trigger': 'Monitor request for different ECU/mode',
                  'guard': 'Loaded module context differs',
                  'action': 'Stop old worker,FreeLibrary,reload Run then queue request; initialization failure '
                            'stops/unloads module',
                  'evidence': ['operations.monitor_route', 'operations.monitor_load']},
                 {'id': 'operations.monitor_stop',
                  'from': 'operations.monitor_running',
                  'to': 'operations.monitor_idle',
                  'trigger': 'DV000017',
                  'guard': 'Frontend poll may be registered',
                  'action': 'Stop JS timer first; native commandA stops monitor idempotently; clear adaptation buffer '
                            'only on success',
                  'evidence': ['operations.frontend_monitor_stop',
                               'operations.stop_monitor',
                               'operations.p5_commands',
                               'operations.p5_cleanup']},
                 {'id': 'operations.active_start',
                  'from': 'operations.monitor_running',
                  'to': 'operations.active_running',
                  'trigger': 'DV000023/024',
                  'guard': 'Monitor mode nonzero; target ECU/test valid',
                  'action': 'Build direct/routine start+return-control work; active parameter updates share engine '
                            'events',
                  'evidence': ['operations.frontend_active_start',
                               'operations.frontend_routine_start',
                               'operations.api_dispatch',
                               'operations.p5_commands',
                               'operations.poll_thread']},
                 {'id': 'operations.active_stop',
                  'from': 'operations.active_running',
                  'to': 'operations.monitor_running',
                  'trigger': 'DV000025',
                  'guard': 'Matching ECU',
                  'action': 'Stop multi-active JS timer; retain native return-control queue; event thread attempts '
                            'stop frames; panel-close separately requests CGW sessionDiagMode0',
                  'evidence': ['operations.frontend_active_stop',
                               'operations.frontend_active_close',
                               'operations.stop_active',
                               'operations.active_stop_queue',
                               'operations.active_stop_event',
                               'operations.poll_thread']},
                 {'id': 'operations.record_start',
                  'from': 'operations.monitor_running',
                  'to': 'operations.recording',
                  'trigger': 'startRecording',
                  'guard': 'DTC/check trigger or ordinary trigger',
                  'action': 'For DTC/check:stop monitor,shift/confirm check mode,clear/reselect trigger data,restart '
                            'monitor; otherwise change record mode',
                  'evidence': ['operations.frontend_record_start']},
                 {'id': 'operations.record_stop',
                  'from': 'operations.recording',
                  'to': 'operations.monitor_running',
                  'trigger': 'exitRecording(isStop=false)',
                  'guard': 'Normal mode restored; enable1 on restart',
                  'action': 'Stop monitor,restore/confirm normal mode,restart polling; errors can return resolved '
                            'values rather than throw',
                  'evidence': ['operations.frontend_record_exit']},
                 {'id': 'operations.record_stop_final',
                  'from': 'operations.recording',
                  'to': 'operations.monitor_idle',
                  'trigger': 'exitRecording(isStop=true)',
                  'guard': 'Normal mode confirmed',
                  'action': 'Stops without restarting; if normal-mode restoration fails, source may restart with '
                            'previous snapshot mode',
                  'evidence': ['operations.frontend_record_exit']},
                 {'id': 'operations.record_save',
                  'from': 'operations.recording',
                  'to': 'operations.saving',
                  'trigger': 'saveSnapshotRecord',
                  'guard': 'Buffer exists',
                  'action': 'Concurrent configuration/save/clear; BufferInterface defers clear until save completion',
                  'evidence': ['operations.frontend_record_save', 'operations.buffer_save_completion']},
                 {'id': 'operations.save_complete',
                  'from': 'operations.saving',
                  'to': 'operations.recording',
                  'trigger': 'saveFinish + metadata completion',
                  'guard': 'Successful data write and saveInfo/addData/hash as applicable',
                  'action': 'Resolve deferred; queued clear can proceed; failure rejects save but worker savingProm '
                            'always released',
                  'evidence': ['operations.buffer_save',
                               'operations.buffer_save_completion',
                               'operations.buffer_close']},
                 {'id': 'operations.read_fault',
                  'from': 'operations.executing',
                  'to': 'operations.faulted',
                  'trigger': 'Typed/native error',
                  'guard': 'Nonzero native status or frontend rejected result',
                  'action': 'Classify cancellation/argument/general/device statuses; JS polling rejection deletes '
                            'registration,not automatic retry',
                  'evidence': ['operations.result_classifier',
                               'operations.frontend_poll',
                               'operations.frontend_reader_poll']},
                 {'id': 'operations.wire_retry',
                  'from': 'operations.monitor_running',
                  'to': 'operations.monitor_running',
                  'trigger': 'Transient slot2 send/receive failure',
                  'guard': 'Attempt counter below DataListIF+84',
                  'action': 'Retry live acquisition only; operation-specific failure/NRC callback otherwise',
                  'evidence': ['operations.poll_thread']},
                 {'id': 'operations.frame_retries',
                  'from': 'operations.executing',
                  'to': 'operations.executing',
                  'trigger': 'Frame transaction failure',
                  'guard': 'Signed retry count+20 not exhausted; not90020323',
                  'action': 'Retry send/receive or SID mismatch; retain selected negative response bytes at exit',
                  'evidence': ['operations.frame_retry']},
                 {'id': 'operations.poll_fault',
                  'from': 'operations.monitor_running',
                  'to': 'operations.faulted',
                  'trigger': 'Monitor/active acquisition error',
                  'guard': 'Error not designated active-stop continuation',
                  'action': 'Record original status in live buffers; callback classifies NRC; park native state4; '
                            'frontend loop stops on rejected Promise',
                  'evidence': ['operations.poll_thread', 'operations.p5_error', 'operations.frontend_poll']},
                 {'id': 'operations.monitor_exit',
                  'from': 'operations.monitor_running',
                  'to': 'operations.monitor_idle',
                  'trigger': 'Frontend exitDatalist',
                  'guard': 'Any monitor mode',
                  'action': 'Best-effort stop/normal-mode restore despite errors; buffer close only after leaving '
                            'check mode',
                  'evidence': ['operations.frontend_monitor_exit', 'operations.buffer_close']},
                 {'id': 'operations.begin_end',
                  'from': 'operations.ready',
                  'to': 'operations.teardown',
                  'trigger': 'SC000002',
                  'guard': 'Destroy delegate exists',
                  'action': 'Utility abort then disconnect then delete native aggregate/viewer; stop message '
                            'thread;free tracked responses',
                  'evidence': ['operations.managed.EndDiagnosis',
                               'operations.diagnosis_exit',
                               'operations.adapt_cleanup',
                               'operations.aggregate_exit']},
                 {'id': 'operations.end_success',
                  'from': 'operations.teardown',
                  'to': 'operations.closed',
                  'trigger': 'Native response + destroy successful',
                  'guard': 'Response exists/result!=-1; destroy true',
                  'action': 'Zero instance; FreeLibrary and null delegates',
                  'evidence': ['operations.managed.EndDiagnosis', 'operations.managed.UnloadDiagAdaptation']},
                 {'id': 'operations.end_failure',
                  'from': 'operations.teardown',
                  'to': 'operations.faulted',
                  'trigger': 'Missing/error response or false destroy',
                  'guard': 'Managed EndDiagnosis failure branches',
                  'action': 'Return before successful destroy/unload; preserve remaining instance/module for caller '
                            'recovery decision',
                  'evidence': ['operations.managed.EndDiagnosis']},
                 {'id': 'operations.worker_destroy',
                  'from': 'operations.monitor_idle',
                  'to': 'operations.closed',
                  'trigger': 'Monitor owner destructor/module switch',
                  'guard': 'Native worker exists',
                  'action': 'Signal exit;wait1000ms;all nonzero waits force TerminateThread+cleanup;close '
                            'handle;delete subobjects;FreeLibrary;close queue events',
                  'evidence': ['operations.monitor_destroy', 'operations.p5_stop', 'operations.p6_stop']},
                 {'id': 'operations.keepalive_invalid',
                  'from': 'operations.monitor_running',
                  'to': 'operations.monitor_running',
                  'trigger': 'Keepalive send/receive/malformed reply',
                  'guard': 'Timer2000ms active',
                  'action': 'Reset software session0; continue worker; later ordinary send rejudges/reinitializes '
                            'session as needed',
                  'evidence': ['operations.keepalive_worker', 'operations.send_session']}],
 'handoffs': [{'to_domain': 'bootstrap',
               'caller': 'MainTask Vehicle/Cancel lanes',
               'callee': 'GTSPlusDiagAdaptMng.ExecuteAdaptation',
               'mechanism': 'Managed adaptation dispatch; shared process cancellation token owns outer task shutdown',
               'payload': 'apiId,UTF8 JSON request,response; native SC000005 cancellation distinct from outer task '
                          'token',
               'evidence': ['operations.managed.ExecuteAdaptation', 'operations.managed.DiagFunction']},
              {'to_domain': 'ui_ipc',
               'caller': 'GtsPFApi/GtsPFRawInterface',
               'callee': 'DiagAdaptationManager',
               'mechanism': 'DV/SC API envelope over platform IPC; ACK/final response distinguished by outer scheduler',
               'payload': 'common.apiId,apiArgs,free.freeMsg; cancellation carries cancelId at outer layer',
               'evidence': ['operations.frontend_api_ids',
                            'operations.adapt_execute',
                            'operations.managed.DiagFunction']},
              {'to_domain': 'vci_transport',
               'caller': 'CCommCtrlSub::~CCommCtrlSub / DataListIF thread',
               'callee': 'CCommFrameCtrl::Disconnect(1),CloseDevice / SendIntExt,ReceiveExt',
               'mechanism': 'Native controller ownership and line-critical-section API',
               'payload': 'ECU,bus,frames,timeouts,status; aggregate disconnect precedes monitor destructor',
               'evidence': ['operations.aggregate_exit',
                            'operations.line_lock',
                            'operations.poll_thread',
                            'operations.disconnect',
                            'operations.close_device']},
              {'to_domain': 'vehicle_session',
               'caller': 'CCommFrameCtrl::SendProc/TestPresentStart',
               'callee': 'Generation protocol session and DB selector DD/D1/D2',
               'mechanism': 'Cached category generation/session judgement + separate keepalive thread',
               'payload': 'ECU,bus,request SID; current session byte+29,selectorDD frame; software session3/0',
               'evidence': ['operations.send_session',
                            'operations.keepalive_start',
                            'operations.keepalive_worker',
                            'operations.keepalive_stop']},
              {'to_domain': 'persistence',
               'caller': 'Datalist/active-test worker BufferInterface',
               'callee': 'BufferWorker/StoredDataManager/platform writeFile',
               'mechanism': 'MessagePort saveAck/saveFinish protocol,writeFile and stored metadata/hash operations',
               'payload': 'Selected signal/trigger/flag metadata,recorded values,memo; timestamp path and data file',
               'evidence': ['operations.frontend_record_save',
                            'operations.buffer_save',
                            'operations.buffer_save_completion',
                            'operations.buffer_close']},
              {'to_domain': 'cuw_utility',
               'caller': 'DiagAdaptation ExecuteUtilityGenericApi / CCommandCtrl',
               'callee': 'UtilityPlusFrontNK ComUtilityFront/Abort/Disconnect',
               'mechanism': 'Native utility export resolution and same six-pointer context',
               'payload': 'SC000013/014 or UG-family APIs; null request/response on abort/disconnect; shared cancel '
                          'pointer',
               'evidence': ['operations.generic_utility',
                            'operations.utility_stop',
                            'operations.utility_abort',
                            'operations.utility_disconnect']}],
 'persistence': [{'path_pattern': '<BufferWorker savePath>/<yyyyMMddHHmmssSSS>/<StoredData.JsonFile.DATA>',
                  'producer': 'Buffer worker GtsBaseBuffer',
                  'consumer': 'StoredDataManager and saved-data viewers',
                  'created': 'saveToPlatform writeFile(mode0) / divided write starts mode0 then appends mode2',
                  'flushed': 'saveFinish acknowledgement plus saveInfo/addData and optional createHashFile precede '
                             'BufferInterface deferred resolution',
                  'deleted': 'clear resets in-memory buffer after pending save; no disk deletion in these methods',
                  'evidence': ['operations.buffer_save',
                               'operations.buffer_save_completion',
                               'operations.frontend_record_save',
                               'operations.buffer_close']},
                 {'path_pattern': '<DRS file object supplied by request command57>',
                  'producer': 'DataMonitorThreadP5 DRS capture + CDrsFileWriter',
                  'consumer': 'DRS recorder/viewer domain',
                  'created': 'Caller supplies request+50 writer; command57 brackets setting/start/stop records',
                  'flushed': 'Final writer stop callback is called; error propagated; actual file flush ownership '
                             'handed to persistence',
                  'deleted': 'Not deleted by monitor command switch',
                  'evidence': ['operations.p5_commands', 'operations.api_dispatch']},
                 {'path_pattern': 'Process-local per-ECU/request caches and shared-data references',
                  'producer': 'CCommCtrlSub/CCommCachePlus',
                  'consumer': 'Plugins and monitor session',
                  'created': 'Aggregate construction and eligible request/response completion',
                  'flushed': 'No disk flush; memory only',
                  'deleted': 'Aggregate destructor clears shared references then destroys cache objects; adaptation '
                             'cleanup drains native response allocations',
                  'evidence': ['operations.aggregate_ctor',
                               'operations.aggregate_exit',
                               'operations.response_cache',
                               'operations.adapt_cleanup']}],
 'coverage': {'components': ['DiagCommCtrlMain.dll',
                             'DiagAdaptation.dll',
                             'KgpDataMonitorCtrl.dll',
                             'DataMonitorPhase5_DT.dll',
                             'DataMonitorPhase6_DT.dll',
                             'KGP_CommFrameCtrl.dll',
                             'DataListIF.dll',
                             'CommandCommon.dll',
                             'GTSPlusDiagAdaptMng.dll',
                             'Authenticated gts.gui diagnostic workers; CommandAPI.dll absent in current release'],
              'entrypoints': ['SC000001 start diagnosis',
                              'SC000002 end diagnosis',
                              'SC000005 cooperative cancel',
                              'DV000008/009 DTC/FFD readers',
                              'DV000013..017 monitor catalog/metadata/start/value/stop',
                              'DV000019..025 direct/multi/routine active test catalog/init/start/stop',
                              'DV000038..040 customize',
                              'DV000059/060 simple utility info/start/status/stop',
                              'DV000117..120 DRS/DLOG create/copy/read',
                              'SC000013/014 generic utility start/stop; UG family'],
              'branches': ['Plugin module/export/prerequisite failures',
                           'Managed start failure destroys/unloads; end failures retain ownership',
                           'Single borrowed-slot queue occupied/empty/event failure',
                           'P5 and P6 1000ms normal join vs all-nonzero forced termination',
                           'Frontend polling rejection halts future scheduling; stop does not abort in-flight Promise',
                           'Frame retry bound and receive-status-specific exits',
                           'P5 live acquisition retry/NRC callbacks/park/stop-return-control',
                           'Keepalive session validity reset and next-send rejudgement',
                           'Record normal/check-mode entry/exit and save completion/error',
                           'Customize resolved-error contract; simple utility terminal status/deadline polling']},
 'residuals': [{'question': 'Which ECU-dependent support,session and stop/return-control responses occur on a real '
                            'run?',
                'why_unclosed': 'Static/offline evidence cannot supply live VCI/ECU responses; no vehicle or network '
                                'interaction is permitted.',
                'next_evidence': 'Authorized bench trace with real selected ECU,VCI and exact '
                                 'request/response/session/cancel timing; retain offline boundaries.'},
               {'question': 'What wall-clock delay separates accepted cancellation from operation completion when '
                            'the vendor VCI or ECU is blocked?',
                'why_unclosed': 'The source closes cooperative acceptance, native waits and P5/P6 forced-stop '
                                'branches; actual vendor-driver, ECU and Windows scheduling latency requires '
                                'an authorized live environment unavailable to this offline investigation.',
                'next_evidence': 'Authorized dependency-isolated Windows timing harness and selected VCI/ECU trace; '
                                 'measure acceptance and final-response/cleanup timestamps separately.'}]}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_path(key: str, root: Path, recovered: Path, aux: Path) -> Path:
    if "/" not in key:
        return {"gui": root / "GTSPlusGUI/gts.gui", "cpf": root / "GTSPlusGUI/gts.cpf",
                "certificate": root / "ContentServer/dist.crt"}[key]
    kind, filename = key.split("/", 1)
    if kind == "recovered":
        return recovered / "bin" / filename
    if kind.startswith("aux-"):
        base = aux if kind == "aux-recovered" else root
        return base / "ContentServer" / (filename + ("._" if kind == "aux-sidecar" else ""))
    return root / "GTSPlus/bin" / (filename + ("._" if kind == "sidecar" else ""))


def _ui_method(text: str, cls: str, method: str) -> str:
    marker = cls + ".prototype."
    start = text.index(marker + method + "=")
    end = text.find(marker, start + len(cls) + 12)
    return text[start:end if end != -1 else len(text)]


def build(root: Path = DEFAULT_ROOT, recovered_root: Path = DEFAULT_RECOVERED,
          aux_root: Path = DEFAULT_AUX) -> dict:
    root, recovered_root, aux_root = (p.resolve() for p in (root, recovered_root, aux_root))
    paths = {key: _source_path(key, root, recovered_root, aux_root) for key in SOURCE_SHA256}
    sources = []
    for key, path in paths.items():
        raw = path.read_bytes()
        if sha(raw) != SOURCE_SHA256[key]:
            raise ValueError(f"source drift: {key}")
        representation = "shipped"
        if "recovered/" in key:
            representation = "recovered-executable-body"
        elif "sidecar/" in key:
            representation = "shipped-CP-sidecar"
        entry = {"id": "operations.source." + key, "path": path.relative_to(REPO_ROOT).as_posix(),
                 "sha256": sha(raw), "size": len(raw), "representation": representation}
        if key.startswith("recovered/"):
            filename = key.split("/", 1)[1]
            entry["derived_from"] = ["operations.source.installed/" + filename,
                                     "operations.source.sidecar/" + filename]
            entry["recovery"] = "tools.techstream.recover_gtsplus_bodies installer-original plaintext recovery"
        elif key.startswith("aux-recovered/"):
            filename = key.split("/", 1)[1]
            entry["derived_from"] = ["operations.source.aux-installed/" + filename,
                                     "operations.source.aux-sidecar/" + filename]
            entry["recovery"] = "tools.techstream.recover_cp_bodies; see auxiliary manifest"
        sources.append(entry)
    # Validate recovery provenance, not just a same-name plaintext file.
    manifest = json.loads((recovered_root / "manifest.json").read_text())
    for filename in ("CommandCommon.dll", "DiagAdaptation.dll", "GTSPlusDiagAdaptMng.dll"):
        row = next(v for v in manifest["binaries"] if v["path"] == "bin/" + filename)
        if (row["plaintext"]["sha256"] != SOURCE_SHA256["recovered/" + filename]
                or row["protected"]["stub_sha256"] != SOURCE_SHA256["installed/" + filename]
                or row["protected"]["sidecar_sha256"] != SOURCE_SHA256["sidecar/" + filename]):
            raise ValueError(f"recovery provenance drift: {filename}")
    aux_manifest = json.loads((aux_root / "manifest.json").read_text())
    for filename in ("GtsPlus-CM.dll", "CryptgraphResource.dll", "CryptgraphCommon.dll"):
        row = next(v for v in aux_manifest["entries"] if v["relative_path"] == "ContentServer/" + filename)
        if (row["output_sha256"] != SOURCE_SHA256["aux-recovered/" + filename]
                or row["stub_sha256"] != SOURCE_SHA256["aux-installed/" + filename]
                or row["sidecar_sha256"] != SOURCE_SHA256["aux-sidecar/" + filename]):
            raise ValueError(f"auxiliary recovery provenance drift: {filename}")
    evidence = []
    for ident, spec in NATIVE.items():
        filename = spec["file"]
        key = ("recovered/" if "recovered/" + filename in paths else "installed/") + filename
        path = paths[key]
        pe = pefile.PE(str(path), fast_load=True)
        body = pe.get_data(spec["va"] - pe.OPTIONAL_HEADER.ImageBase, spec["size"])
        if len(body) != spec["size"] or not any(body) or sha(body) != spec["sha256"]:
            raise ValueError(f"native body drift/unmaterialized: {ident}")
        windows = [anchor(path, va, expected) for va, expected in BYTE_WINDOWS.get(ident, [])]
        evidence.append({"id": "operations." + ident, "source": "operations.source." + key,
                         "kind": "native-body-and-branch-pins", "locator": spec["function"],
                         "va": hex(spec["va"]), "size": spec["size"], "body_sha256": spec["sha256"],
                         "anchors": windows, "finding": spec["finding"]})
    assembly = paths["recovered/GTSPlusDiagAdaptMng.dll"]
    materialization = _recovery_proof(assembly)
    pe = _open(assembly)
    managed_findings = {
        "ExecuteAdaptation": "SC000001/002 start/end, SCXX0003 startup information; SC000010/011/015 file-edit-bracketed exports; other APIs DiagFunction.",
        "StartDiagnosis": "Rejects existing instance; reads PC/PF settings and builds native AppPath/region/language JSON; LoadDiagAdaptation,create,DiagFunction. Null/missing/nonzero response result destroys instance and unloads module; successful creation retains singleton.",
        "EndDiagnosis": "Clears manager information under Monitor lock; invokes native end operation; missing response or result=-1 returns before destroy. Successful response then destroy; false destroy retains instance; only successful destroy clears instance and unloads.",
        "DiagFunction": "Requires execute/cancel delegates and created instance except start; SC000005 invokes cancel. Other APIs invoke execute, require response pointer, convert UTF8 and invoke freememory. Native execute boolean is discarded; payload/pointer determines managed result. Cancel false maps code4002. Outer ResultInfoData often success while error is encoded in response JSON.",
        "UnloadDiagAdaptation": "FreeLibrary,zero module handle,null create/destroy/execute/cancel/freememory delegates; does not destroy instance itself.",
        "FinalizeAdaptation": "If module handle nonzero calls UnloadDiagAdaptation; returns success. Normal diagnosis-end contract must not be conflated with this unload-only finalizer.",
        "LoadDiagAdaptation": "Loads configured native DLL, obtains export delegates and performs local compatibility/authentication handshake; missing/delegate/auth failures abort initialization. No live authentication service invoked by this extractor.",
    }
    for name, expected in MANAGED.items():
        row, instructions, body = _instructions(pe, MANAGED_TYPE, name)
        pin = _method_pin(row, body)
        if pin != expected:
            raise ValueError(f"managed method drift: {name}")
        code_start = instructions[0].offset
        # Compact branch/call anchors, preserving true code-relative offsets.
        anchors = []
        for ins in instructions:
            op = str(ins.opcode)
            operand = format_operand(pe, ins.operand)
            if op.startswith(("br", "bne", "beq", "leave")) or any(x in operand for x in (
                    "DiagAdaptation", "DiagFunction", "Monitor::", "SC000005", "SC000001", "Unload")):
                if isinstance(ins.operand, int) and op.startswith(("br", "bne", "beq", "leave")):
                    operand = "IL_" + format(ins.operand - code_start, "04X")
                anchors.append({"offset": ins.offset - code_start, "opcode": op, "operand": operand})
        evidence.append({"id": "operations.managed." + name,
                         "source": "operations.source.recovered/GTSPlusDiagAdaptMng.dll",
                         "kind": "managed-IL-body-pin", "locator": MANAGED_TYPE + "::" + name,
                         **pin, "anchors": anchors, "finding": managed_findings[name]})
    assets = decode_gui(paths["gui"], paths["aux-recovered/GtsPlus-CM.dll"],
                        paths["aux-recovered/CryptgraphResource.dll"],
                        paths["aux-recovered/CryptgraphCommon.dll"], paths["certificate"])
    assets = {k.lstrip("/"): v for k, v in assets.items()}
    for member, expected in UI_SHA256.items():
        data = assets[member]
        if sha(data) != expected:
            raise ValueError(f"signed GUI asset drift: {member}")
        sources.append({"id": "operations.ui." + member,
                        "path": "build/out/gts-lifecycle-ui/gts/" + member,
                        "sha256": sha(data), "size": len(data),
                        "representation": "authenticated-decoded-GUI-member",
                        "derived_from": ["operations.source.gui", "operations.source.cpf"],
                        "member": member, "recovery": "gtsplus_local_crypto.decode_gui; decoded in build()"})
    for ident, spec in UI.items():
        text = assets[spec["asset"]].decode("utf-8-sig")
        method = _ui_method(text, spec["class"], spec["method"])
        if sha(method.encode()) != spec["sha256"]:
            raise ValueError(f"frontend method drift: {ident}")
        evidence.append({"id": "operations." + ident, "source": "operations.ui." + spec["asset"],
                         "kind": "authenticated-frontend-method-pin",
                         "locator": spec["class"] + ".prototype." + spec["method"],
                         "method_sha256": spec["sha256"], "finding": spec["finding"]})
    raw = assets["js/gts/common/gts_platform_raw_interface.js"].decode("utf-8-sig")
    import re
    api_ids = dict(re.findall(r"var (PFCMD_[A-Z0-9_]+)='([^']+)'", raw))
    api_map = {k: v for k, v in api_ids.items() if k in API_NAMES}
    if len(api_map) != len(API_NAMES):
        raise ValueError("frontend API mapping drift")
    evidence.append({"id": "operations.frontend_api_ids",
                     "source": "operations.ui.js/gts/common/gts_platform_raw_interface.js",
                     "kind": "authenticated-frontend-API-constants", "locator": "PFCMD_* + send wrappers",
                     "api_ids": api_map,
                     "finding": "Current JavaScript operation APIs send DV/SC IDs through platform raw interface to adaptation manager; CommandAPI.dll is a V18 predecessor, absent from current bin."})
    return {"schema": "gtsplus-lifecycle-domain-v1", "domain": "operations", "sources": sources,
            "evidence": evidence, **LIFECYCLE,
            "managed_materialization": materialization,
            "provenance": {"main_recovery_manifest": (recovered_root / "manifest.json").relative_to(REPO_ROOT).as_posix(),
                           "aux_recovery_manifest": (aux_root / "manifest.json").relative_to(REPO_ROOT).as_posix(),
                           "GUI_signature_verified": True},
            "safety": "Offline extraction only; no diagnostic, auth, network, or vehicle operation executed."}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--recovered-root", type=Path, default=DEFAULT_RECOVERED)
    ap.add_argument("--aux-root", type=Path, default=DEFAULT_AUX)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    result = build(args.root, args.recovered_root, args.aux_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.out)


if __name__ == "__main__":
    main()
