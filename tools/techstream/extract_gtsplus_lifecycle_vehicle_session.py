#!/usr/bin/env python3
"""Pin GTS+ 2026.03.002.02 vehicle-workspace lifecycle from authenticated GUI and executable bodies.

Offline only: decode local GUI packaging, inspect recovered native/CLR bytes, and
reuse vehicle_resolver_semantics.json for Toyota database decision-table closure.
No application process, network request, credential, or vehicle operation is run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

import dnfile
from tools import REPO_ROOT
from tools.techstream.extract_gtsplus_vehicle_resolver import sha256_file, va_bytes
from tools.techstream.gtsplus_local_crypto import decode_gui
from tools.techstream.inspect_dotnet_il import CilMethodBody, MethodBodyReader, format_operand

DEFAULT_INSTALLED = REPO_ROOT / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"
DEFAULT_RECOVERED = REPO_ROOT / "build/out/gtsplus-unprotected"
DEFAULT_AUX = REPO_ROOT / "build/out/gts-lifecycle-aux"
DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/lifecycle_vehicle_session.json"
PREFIX = "vehicle_session."

EXPECTED_MAIN = {'native': 'eb4b5ffd08bfd1e18b7c5aa5b3679893fb6d3efc2c9bcd655c5e40038fe8531a',
 'managed': '7a56cc6488ad0f982b3b8ed531d5da0677d04f58c92b4b4ea3d0ac6508f27f9e',
 'pf_contract': 'd1972962a04b711eeb78c940b5d1c02b43d72959f7db61823a11df3c1d30227a'}

EXPECTED_EXTRA = {'gui': '80ff7eed3a3a429aedc14384befb0f43b8ebd8176868b0bf41135033ce4ea37d',
 'gui_envelope': '773becfd6fad75bfaab3d0dbdb0f4e05cdf1511646f76d77ca2c3d0a914691dc',
 'certificate': '857ec034c946604c52fd845134386b5b914936962254048e8766d78fa6b3ad50',
 'crypto_native': 'ebc7c0b359c63d12a80c7fc596e93c226007b915f21032e05efa1046c2b292b2',
 'crypto_resource': '7a9a2c08f0055fdfed82258835ba68c4a4d41ffeb537bd27caa19ad19d1f16f6',
 'crypto_common': '98fc5afd362f6e28aec9f06f71c15c4d6751751a27a8325cdc143ad9f57366b0',
 'resolver': 'bf94b12b3f6b4e6f22880a96c4dc5840578759849368bb8f044efd381101b421'}

EXPECTED_ORIGINALS = {
    "native": ["676e077cc4d5d64193687a541509e7adae98eee0b9d28347b748b272b02f2cc0",
               "2912c35c790892ce80f549f213df66887b70a63e17a2c2c644fbeb8dd022d317"],
    "managed": ["c3dd32e0ae0ba3816a1878785862d8cf1d0819d0c4cb5a1d2abf1873cfd9135d",
                "0fd228a9ed15971385d60e34b511b1ac4370adba05a376942c790d2296035748"],
    "pf_contract": ["47a9e9a5b5623a37cdb7bd5d8e7616bfeb6c2fa9b2d0f5d37509e75562807079",
                    "ffd6f98fdeee317635ab52e7f6ec02f08596d62d0a63e7f36e293605a964ab2e"],
    "crypto_native": ["b0e8a25289d697bef0da31812d895e55f4745efd000700cfeb66c1e3135addd2",
                      "db69e562601efdea05a06e924a9c06baf9ecee207ac3447cd0b7399e88ebce8f"],
    "crypto_resource": ["c9d3d3c35f7af5f3fa4258cea547005846758f67fae2b3326f97b43be6da21b6",
                        "9f2d7bba218e97aacac917321711e6abaac26625b509770727e4471440c57b47"],
    "crypto_common": ["a70a55a78b3bea044bffa624a9c2aa668d4621e1a03c213cc0d5eb3ff302b073",
                      "c43577c8174b5d5c285c14f2582aaf1b84e19850b62283c6772fb711949a6176"],
}

JS_SPECS = [{'id': 'preconnect',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_controller.js',
  'owner': 'VehicleConnectController',
  'method': 'preConnectLogic',
  'sha256': '21bd2b7168e1b0d2cb151d9a7fcecf0a8b03af47d8870cf1412d366e7cc4c93b',
  'finding': 'VIM-version confirmation and 8000-mV battery precheck; 0x3001/0x3002 route no-connect view, '
             'other errors return menu; technician can continue low voltage or cancel.'},
 {'id': 'reuse',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_controller.js',
  'owner': 'VehicleConnectController',
  'method': 'initLogic',
  'sha256': '5557ec7d20fbe52b727505b46bcf644609bd0d94483b21352e292da4107cce3c',
  'finding': 'Acquire PF lock; reuse fixed matching VIN; missing VIN forces end/start; mismatched/unfixed '
             'VIN prompts when other client exists, otherwise restart then recurse. Lock failure or '
             'cancellation releases lock and returns menu. SelectVehicle 0x3002 opens retry view; absent VIN '
             'opens manual input.'},
 {'id': 'vin',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'getVIN',
  'sha256': 'e86686337e3f8e727a8878c074be97573c856d23ee70f2b95798c61704b19c75',
  'finding': 'Compare PF-confirmed VIN/decisionVin==1 with live getVin. gtsOnlyConnect controls other-client '
             'branch (returned as otherClientExist despite inverted-sounding name).'},
 {'id': 'restart',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'refleshDiagnosis',
  'sha256': '6762040047894824fbcc1b50c08b0a3cd2543b1107560e2275664c44e4abb532',
  'finding': 'forcedEndDiagnosis then startDiagnosis; both errors logged/consumed; diagnosisRestarted=true.'},
 {'id': 'auto',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'startSelectVehicle',
  'sha256': '4cab11009164d7b1f296e8002437e53acf483ecb46eb430c059055909d3b7bfb',
  'finding': 'Regional category IDs + brand division + index0/selectId0 + nonDispInfoList enter resolver; '
             'nonempty category map selects auto mode1, otherwise manual mode2; vehicleId65535 excluded from '
             'confirmation.'},
 {'id': 'manual',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'startManualMode',
  'sha256': '55cb27b029f86e696c832bcd8acf00fe2ac75ef1bbc273afb0c4f71cd4ea3dd1',
  'finding': 'Clear confirmed vehicle/category/option/parent phase; selectVehicleCategory drives '
             'hierarchical manual selection; decision mode1->2, modes3/4->0.'},
 {'id': 'manual_vin',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'getCategoriesWithVin',
  'sha256': '937658c4bd2a1d2ae0d53ef7215ed8963641fc461b2f4f78ed5718f8f704a252',
  'finding': 'Pad manual VIN to11; queryVehiclebyManualVin and relations constrain category/options, mode4 '
             'on resolved category map; reset invalidates cached selections; no match falls back manual.'},
 {'id': 'category',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'setCategory',
  'sha256': '1269e78554ea68ce8e913339681c7802f8f1123e4158c334f9740e568c2b6bb5',
  'finding': 'Category changes truncate downstream selections/options, query category hierarchy or filter '
             'VIN candidates, re-resolve confirmation.'},
 {'id': 'option',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'setOption',
  'sha256': 'a585dc1865b01cf4c6bcf50736ca47816051daa0758a7d9c84c7a461daa72259',
  'finding': 'Option index/selectId feeds subsequent SelectVehicle requests or VIN candidate filtering; '
             'replaces downstream option state and confirmed vehicle.'},
 {'id': 'confirm',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'vehicleDecision',
  'sha256': '3ccc419a642cbf873ee02886ff1fd02a99ef34a2ce055cd83b320d97d658e7d5',
  'finding': 'Manual-VIN mode4 selectsVehicleById; nondefault OEM forces end/start/selectById. Publish '
             'vehicle/VIN/category/car/option/decisionVin/parentPhase/OEM confirmation; apply vehicle '
             'exception; fetch equipped candidates; optionally connect443, apply system exception and '
             'functions; share is19pfVer3 storage3.'},
 {'id': 'context',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'loadVehicleInformation',
  'sha256': 'f1fb87a9b93f2c08623c33bfdbe8e5246600af81a2146301b36742ed04f9a960',
  'finding': 'Rebuild worker mountedEcuMap from equipped candidates with '
             'status-1/hasConnected=false/functions=null and group/bus/phase; read descriptions/mileage; '
             'serialize VehicleInfo for controller.'},
 {'id': 'postconnect',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_controller.js',
  'owner': 'VehicleConnectController',
  'method': 'vehicleDecisionPostprocessingLogic',
  'sha256': '7b1b0dd4f8e7858307400a446d69f06ba8cfaffe79b86877921eca370a2d0262',
  'finding': 'Initialize legacy phase7 if needed; load shared VehicleInfo; web-service failure ends '
             'diagnosis/logs out; initialHealthCheck Required/Optional/None controls '
             'vehicleConnectTransitionFlag before VEHICLE_CONNECTED.'},
 {'id': 'back',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_controller.js',
  'owner': 'VehicleConnectController',
  'method': 'onClickBack',
  'sha256': 'e6f98af963cccde1890811a930ea4b657c1ea0491164c75ab1a11120c7ff4113',
  'finding': 'Release PF exclusive lock and return main menu.'},
 {'id': 'disconnect_ui',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'disconnectJ2534Device',
  'sha256': '15603cb0ec9a7e5c32e2bad668b8071df2a535fe961a6e975f5e653a25fb7549',
  'finding': 'Invoke explicit J2534 device disconnect; rejection consumed.'},
 {'id': 'ecu_cache',
  'asset': 'js/gts/common/common_info_worker.js',
  'owner': 'EcuInfo',
  'method': 'getEcuStatus',
  'sha256': '0dd2dbb34479720f2dd77ab01e2aeb9b3927412fc4ce3913edb16f1eb90afb13',
  'finding': 'Status-threshold cache avoids repeated connect; explicit recheck clears native ECU/bus cache '
             'except UNCHECKED; connect failure sets status0; connected sets hasConnected; '
             'replace-system/function discovery only when connected and missing/forced, function failure '
             'caches empty list.'},
 {'id': 'current_ecu',
  'asset': 'js/gts/common/common_info.js',
  'owner': 'CommonInfo',
  'method': 'setCurrentEcuId',
  'sha256': '1957318a477569d9b911ecdff9e52327ad3e80c68ee2044db1cd104e0952110b',
  'finding': 'Selected ECU ID/name are references copied from mounted map, independent of vehicle '
             'identity/session owner.'},
 {'id': 'clear_context',
  'asset': 'js/gts/common/common_info_worker.js',
  'owner': 'CommonInfo',
  'method': 'clearVehicleInfo',
  'sha256': 'a49dd86b3972b317ed13abac0508531f746612442a1f125b06172cac675e8cc4',
  'finding': 'Replace VehicleInfo and SharedData on workspace invalidation.'},
 {'id': 'workspace_close',
  'asset': 'js/gts/main_frame/main_frame_controller.js',
  'owner': 'MainFrameController',
  'method': 'dispose',
  'sha256': '594c8dc58c56270ad9bfd9af79799c22f968578fc5560f478c30e4291c7e3a37',
  'finding': 'Dispose active controller, stop voltage polling, remove UI/header, clear selected vehicle then '
             'end diagnosis, reset stored data, start a fresh diagnostic context; logs and consumes restart '
             'errors.'},
 {'id': 'workspace_end',
  'asset': 'js/gts/main_frame/main_frame_worker.js',
  'owner': 'MainFrameWorkerModel',
  'method': 'endDiagnosis',
  'sha256': 'ae23d3333af83aec1f875269ce42096a62df0817d15e3117790bb2031657c48e',
  'finding': 'Worker clears VehicleInfo before PF endDiagnosis; rejection is logged and resolved.'},
 {'id': 'hc_before',
  'asset': 'js/gts/health_check/health_check_worker.js',
  'owner': 'HealthCheckWorkerModel',
  'method': 'healthCheckOnLoadBeforePart',
  'sha256': '7b61d8b7d64a5ecd18e6c279ecc6a64e25f85d09dc36c8e44ee269da17172550',
  'finding': 'Initialize healthcheck flags/cache; reread equipped list when requested; sort shared mounted '
             'candidates; finally clear isRunning.'},
 {'id': 'hc_after',
  'asset': 'js/gts/health_check/health_check_worker.js',
  'owner': 'HealthCheckWorkerModel',
  'method': 'healthCheckOnLoadAfterPart',
  'sha256': 'b81a465e0f5eba0a76f0a971cfca8105324800130d0ac992205c03a8948fc106',
  'finding': 'Run healthcheck and postprocessing, produce buffer/IPK and latest JSON cache; finally clear '
             'isRunning.'},
 {'id': 'hc_scan',
  'asset': 'js/gts/health_check/health_check_worker.js',
  'owner': 'HealthCheckWorkerModel',
  'method': '_startHealthCheckFunc',
  'sha256': '5f36fea4776b78a6b481a1f8415681ac9bdeb0086c6c58ef56f56c1e65c57826',
  'finding': 'Sequential sorted mounted candidates; stop scheduling on cancelFlag; getEcuStatus with '
             'clearEcuConnectCache1 forcing connected/function refresh; only CONNECTED runs '
             'DTC/monitor/RoB/CID. Save each result and enqueue progress.'},
 {'id': 'hc_flow',
  'asset': 'js/gts/health_check/health_check_worker.js',
  'owner': 'HealthCheckWorkerModel',
  'method': '_startHealthCheck',
  'sha256': 'aa6167d6c7ade3c24ee65e8587c2993f167af6f793fe77a3ed79c5af949e0be0',
  'finding': 'Gateway/wired data start then ECU scan; cancel returns summary early; otherwise timestamps/CAN '
             'bus/tires/SOH/web-service enrichment and final wired-data save; revoke error routes revoke '
             'UI.'},
 {'id': 'hc_cancel',
  'asset': 'js/gts/health_check/health_check_worker.js',
  'owner': 'HealthCheckWorkerModel',
  'method': 'cancelHealthCheck',
  'sha256': 'b594dd0f9a065b2fdce6df41cc989ef8aa1d344f11af8686cdd7ed5a598c889b',
  'finding': 'If running and not already canceled, end wired collection, retain callback+args, set '
             'cancelFlag and enqueue START_HEALTH_CHECK_CANCEL; cooperative between ECU work, not global '
             'forced abort.'},
 {'id': 'hc_cancel_end',
  'asset': 'js/gts/health_check/health_check_worker.js',
  'owner': 'HealthCheckWorkerModel',
  'method': '_healthCheckSummaryEndFunc',
  'sha256': '3f92785990f363da555b3a59041795be0f43fcfedc84d7dfb7856a8e413e83f6',
  'finding': 'Enqueue END_HEALTH_CHECK_CANCEL with callback and ECU arg once summary sees cancelFlag; clear '
             'callback storage.'},
 {'id': 'hc_cache',
  'asset': 'js/gts/health_check/health_check_worker.js',
  'owner': 'HealthCheckWorkerModel',
  'method': 'saveCacheData',
  'sha256': 'ec31e7596071cdfaaafda2e0150eb022bedfcaf46a22e565130097918502908c',
  'finding': 'Write latest JSON mode1 after stripping specificFolder/settings/settingExcerpt; write failure '
             'returns undefined, not success timestamp.'},
 {'id': 'hc_read',
  'asset': 'js/gts/health_check/health_check_worker.js',
  'owner': 'HealthCheckWorkerModel',
  'method': 'readCacheData',
  'sha256': '5df6b0d721e0f33f39ad85d4b4a971042729e117f7e484fd45e95ce4b0bd7862',
  'finding': 'Read latest JSON and rehydrate healthcheck view/cache with current settings.'},
 {'id': 'hc_path',
  'asset': 'js/gts/health_check/health_check_worker.js',
  'owner': 'HealthCheckWorkerModel',
  'method': 'makeCacheFilePath',
  'sha256': 'd7c7c2b0d1a90820e7d1c129d7b7e1950da2dae0717651271c5ba78510cb997b',
  'finding': 'specificFolder folderNo1 + distributor specificSubFolders/cacheDataHealthCheck + '
             'LatestHealthCheckData.json.'},
 {'id': 'by_id',
  'asset': 'js/gts/vehicle_connect_by_id/vehicle_connect_by_id_worker.js',
  'owner': 'VehicleConnectByIdWorkerModel',
  'method': 'vehicleConnectById',
  'sha256': 'f7ae2c2fb027eedcd9cd2029096fdae27247c661e579724ba19a8ca7ac5441fc',
  'finding': 'Saved/linkage vehicleId and supplied VIN check existing PF-confirmed vehicle; only when '
             'present force end/start. selectVehicleById -> notify confirmation -> vehicle exception -> set '
             'worker VehicleInfo from linkage/resolver output.'},
 {'id': 'configuration_cache',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'getCategories',
  'sha256': 'fa246d55f51206e8f810066357d377a3a5f094440b3ebaadc53f305c13d03066',
  'finding': 'When resolver nonDispInfo exists, save fileType5 vehicleConfigration ngCount0/password lookup '
             'metadata/package version before manual/auto category processing; failure logged.'},
 {'id': 'configuration_read',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'getEnvInfo',
  'sha256': 'a7b5229824d60b963d713540270e6270a01a8ce21e45cddd8eab02405fe86a2f',
  'finding': 'New VehicleInfo and fresh connect cache; read vehicle configuration fileType5, retain password '
             'lookup array as nonDispInfoList; errors logged.'},
 {'id': 'switch_controller',
  'asset': 'js/gts/ecu_function/ecu_function_controller.js',
  'owner': 'EcuFunctionController',
  'method': 'setCurrentEcu',
  'sha256': 'c7302c9de2ed1f1f93ad4fd8db0d4df42946709e521f05fbb239113816cc3416',
  'finding': 'Different selected ECU changes common current ID and retrieves cached worker function list; '
             'NaN clears display; does not recreate vehicle context.'},
 {'id': 'battery_threshold',
  'asset': 'js/gts/vehicle_connect/vehicle_connect_worker.js',
  'owner': 'VehicleConnectWorkerModel',
  'method': 'checkBatteryVoltage',
  'sha256': '050e2c4c60baff62b0bf5e57255b02e3e208dc1a06827ea455904f72d26a784d',
  'finding': 'Compare batteryVoltage <8000; return lowBattery plus structured error code/detailCode.'},
 {'id': 'api_contracts',
  'asset': 'js/gts/common/gts_platform_raw_interface.js',
  'owner': 'GtsPFRawInterface',
  'method': 'getEquippedEcuList',
  'sha256': 'c57db63912ed96557bd9d2fe18a375f6d404b46e2ac1b237c4554ff5c03cffd2',
  'finding': 'GtsPFRawInterface methods use constants listed in api_ids; entire raw-interface asset pinned. '
             'apiArgs routed as request payload.'}]

NATIVE_HANDLERS = [{'name': 'StartDiagnosis',
  'vtable': 269060940,
  'execute': 268834880,
  'entry': '558bec6aff687c5b081064a100000000'},
 {'name': 'EndDiagnosis',
  'vtable': 269060924,
  'execute': 268496928,
  'entry': '558bec6aff688dcf071064a100000000'},
 {'name': 'SelectVehicle',
  'vtable': 269060908,
  'execute': 268809040,
  'entry': '558bec6aff686250081064a100000000'},
 {'name': 'SelectVehicleCategory',
  'vtable': 269060892,
  'execute': 268811952,
  'entry': '558bec6aff687a51081064a100000000'},
 {'name': 'SetVehicleId',
  'vtable': 269060876,
  'execute': 268818320,
  'entry': '558bec6aff685654081064a100000000'},
 {'name': 'GetMountEcuList',
  'vtable': 269060856,
  'execute': 268706592,
  'entry': '558bec6aff688127081064a100000000'},
 {'name': 'CheckECUConnect',
  'vtable': 269060840,
  'execute': 268456864,
  'entry': '558bec6aff6831c0071064a100000000'},
 {'name': 'GetVehicleCache',
  'vtable': 269059372,
  'execute': 268904656,
  'entry': '558bec6aff686774081064a100000000'},
 {'name': 'DelEcuCnctCache',
  'vtable': 269060244,
  'execute': 268495216,
  'entry': '558bec6aff68bfce071064a100000000'},
 {'name': 'J2534DeviceDisconnection',
  'vtable': 269060212,
  'execute': 268794496,
  'entry': '558bec6aff68f549081064a100000000'},
 {'name': 'QueryVehiclebyManualVin',
  'vtable': 269059084,
  'execute': 268819696,
  'entry': '558bec6aff680355081064a100000000'},
 {'name': 'QueryVehicleDBbyId',
  'vtable': 269059288,
  'execute': 268799648,
  'entry': '558bec6aff68174c081064a100000000'},
 {'name': 'GetVIN', 'vtable': 269059356, 'execute': 268789072, 'entry': '558bec6aff68f746081064a100000000'}]

NATIVE_ANCHORS = [{'id': 'end_order',
  'va': 268497117,
  'bytes': '8b46048b480485c97417ff15848c08108b4e048945f08b4904ff15808c08108bf88b4e04e8aa560500837df000747c',
  'finding': 'StopCommunicationUtility -> DisconnectUtility -> CDAInstance clear unconditionally before '
             'error selection; stop error takes precedence.'},
 {'id': 'disconnect_order',
  'va': 268794679,
  'bytes': '8b4e048b4904ff15848c08108b4df08bf08975e88b49048b4904ff15808c08108bd88b45f08b48048b4904ff157c8c08108945ec85c0747f',
  'finding': 'Explicit device disconnect invokes stop utility, disconnect utility, then physical Disconnect '
             'before reporting any failure.'},
 {'id': 'mount_guard',
  'va': 268707845,
  'bytes': '80791000747a',
  'finding': 'NoComm list guarded by instance+0x10==0; JZ enters dispatch. Equipped list does not itself '
             'establish ECU connection.'},
 {'id': 'clear_objects',
  'va': 268847024,
  'bytes': '5356578bf98b4f0485c9740d8b016a01ff10c74704000000008b770885f6741d8bceff15b48d081068e006000056e8f85e010083c408c7470800000000',
  'finding': 'Destroy+zero shared CCommCtrlMain and ViewerDataCtrl members at+4/+8.'},
 {'id': 'clear_thread',
  'va': 268847105,
  'bytes': '837f60008d775c74336a006a006a12ff36ff15688d08106affff7760ff15fc8c0810ff7760ff15008d08108d4744c747600000000050ff15048d0810',
  'finding': 'If queue thread exists post WM_QUIT0x12, wait INFINITE, close handle, delete critical '
             'section.'},
 {'id': 'invalidate_result',
  'va': 268495662,
  'bytes': 'ff15888c08108bf085f60f84b30000008d4da4c745a400000000e8f32bffff81fe010604c0755c',
  'finding': 'CDelEcuCnctCache nonzero command result compared with0xC0040601; special warning result branch '
             'distinct from other failures.'}]

MANAGED_SPECS = [('LoadDiagAdaptation',
  8464,
  1528,
  '9e1c00be34c4a9c906263b6b03bad82e235457a2fe34d4450ae2ef9569329ccd',
  'Load configured cassette/bin DiagAdaptation; resolve create/destroy/execute/cancel/freememory and perform '
  'local module challenge check; unload on binding/auth failure.'),
 ('UnloadDiagAdaptation',
  9992,
  192,
  'f0d37834e283747d152d48cdc3a3fda3742d878775c6122ab064253c945c585a',
  'FreeLibrary then zero handle and delegates.'),
 ('ExecuteAdaptation',
  10184,
  216,
  'f28b676190c3efcf42d19a084af1ac758ea6a1ab0fff1025fb76659cf1ca3988',
  'SC000001 start,SC000002 end,SCXX0003 cached start info, other diagnostic requests delegated; SC000005 '
  'reaches cancel branch in DiagFunction.'),
 ('StartDiagnosis',
  10400,
  1236,
  '13c775ada20d9faef7c6516a557dca27118aecffbadb17f7393a0e9796bd0d38',
  'Reject duplicate nonzero instance in response; read settings and deserialize OEM request; load native '
  'module, build AppPath/RegionId/LanguageCode, create native instance, execute start; missing/nonzero '
  'response result destroys instance+zeros it+unloads. Outer manager often returns success envelope while '
  'response carries failure.'),
 ('EndDiagnosis',
  11636,
  456,
  'b137c0ef6edbf41d868926b42bc9cd52807368f589a83db4ff8536374bd760a9',
  'Clear region/language under monitor first; call native end; missing result or result==-1 returns without '
  'destroy; destroy failure also preserves instance; success zeros instance then unloads.'),
 ('DiagFunction',
  12092,
  652,
  '28f823b223bc27b453f111a5d2f875937a99f95f97b9ead30e57b128abe59943',
  'Require execute+cancel delegates and instance except start; execute returns UTF8 response pointer copied '
  'to string then freememory; null pointer yields error. SC000005 invokes cancel(instance); false cancel '
  'produces response code0x4002.')]

API_IDS = {'startDiagnosis': 'SC000001',
 'endDiagnosis': 'SC000002',
 'forcedEndDiagnosis': 'SC000007',
 'getEquippedEcuList': 'DV000004',
 'checkEcuConnect': 'DV000005',
 'clearEcuConnectCache': 'DV000033',
 'selectVehicle': 'DV000001',
 'selectVehicleById': 'DV000003',
 'notifySelectedVehicle': 'SC000003',
 'getVehicleConfirmation': 'IF000004',
 'getVin': 'DV000090',
 'queryVehiclebyManualVin': 'DV000103',
 'disconnectJ2534Device': 'DV000035'}

STATES = [('idle', 'PF+GUI', 'Fresh diagnostic instance; no confirmed vehicle.'),
 ('precheck', 'GUI VehicleConnectController', 'VIM/battery checks and PF exclusive lock.'),
 ('select', 'GUI worker + native resolver', 'Resolve VIN/category/options or manual vehicle identity.'),
 ('confirmed', 'PF arbitration + GUI worker', 'Vehicle identity published through SC000003.'),
 ('workspace',
  'MainFrame/CommonInfo',
  'Shared VehicleInfo and ECU candidate map; per-ECU status/function caches.'),
 ('healthcheck', 'HealthCheckWorkerModel', 'Cooperative sequential ECU acquisition and enrichment.'),
 ('cancelling',
  'HealthCheckWorkerModel',
  'cancelFlag set; next ECU scheduling skipped; summary callback pending.'),
 ('ecu', 'CommonInfo/EcuInfo', 'Current ECU selected in existing vehicle workspace.'),
 ('disconnected',
  'native CCommCtrlMain',
  'Physical J2534 disconnect requested; shared instance remains allocated.'),
 ('closing',
  'managed/native adaptation',
  'Stop utility, clear native context; manager may retain instance on failure.'),
 ('error', 'GUI/PF', 'Error response or user cancellation; caller-specific handling.')]

TRANSITIONS = [{'id': 'vehicle_session.precheck',
  'from': 'vehicle_session.idle',
  'to': 'vehicle_session.precheck',
  'trigger': 'connect requested',
  'guard': 'VIM confirmation and battery precheck passed/continued',
  'action': 'Acquire PF exclusive lock',
  'evidence': ['vehicle_session.preconnect', 'vehicle_session.reuse']},
 {'id': 'vehicle_session.precheck_abort',
  'from': 'vehicle_session.precheck',
  'to': 'vehicle_session.error',
  'trigger': 'outdated VIM No/low battery Cancel/other error',
  'guard': 'User choice or failure code',
  'action': 'Return menu; lock acquisition failure releases lock',
  'evidence': ['vehicle_session.preconnect', 'vehicle_session.reuse']},
 {'id': 'vehicle_session.reuse_context',
  'from': 'vehicle_session.precheck',
  'to': 'vehicle_session.select',
  'trigger': 'getVIN completion',
  'guard': 'matching VIN and decisionVin==1',
  'action': 'Keep existing PF context and start resolver selection',
  'evidence': ['vehicle_session.reuse', 'vehicle_session.vin']},
 {'id': 'vehicle_session.restart_context',
  'from': 'vehicle_session.precheck',
  'to': 'vehicle_session.select',
  'trigger': 'missing/mismatched/unfixed VIN',
  'guard': 'Mismatch may require confirmation when other PF client exists',
  'action': 'forcedEndDiagnosis then startDiagnosis; restart selection; consumed restart errors do not prove '
            'success',
  'evidence': ['vehicle_session.reuse', 'vehicle_session.restart']},
 {'id': 'vehicle_session.manual_fallback',
  'from': 'vehicle_session.select',
  'to': 'vehicle_session.select',
  'trigger': 'no VIN/no auto category map/manual button',
  'guard': 'Regional resolver result or technician choice',
  'action': 'Clear dependent identity and option cache; hierarchical category or manual VIN candidate '
            'resolution',
  'evidence': ['vehicle_session.auto',
               'vehicle_session.manual',
               'vehicle_session.manual_vin',
               'vehicle_session.category',
               'vehicle_session.option']},
 {'id': 'vehicle_session.confirm_vehicle',
  'from': 'vehicle_session.select',
  'to': 'vehicle_session.confirmed',
  'trigger': 'technician confirms selected identity',
  'guard': 'vehicleId !=65535 and selection complete',
  'action': 'Mode4 selectById; nondefault OEM restart; publish confirmation and apply vehicle exception',
  'evidence': ['vehicle_session.confirm']},
 {'id': 'vehicle_session.populate_workspace',
  'from': 'vehicle_session.confirmed',
  'to': 'vehicle_session.workspace',
  'trigger': 'loadVehicleInformation',
  'guard': 'Resolver candidate list available',
  'action': 'Create status-1 ECU objects with group/bus/phase; hand serialized VehicleInfo to UI',
  'evidence': ['vehicle_session.context',
               'vehicle_session.postconnect',
               'vehicle_session.native_mount_guard']},
 {'id': 'vehicle_session.initial_healthcheck',
  'from': 'vehicle_session.workspace',
  'to': 'vehicle_session.healthcheck',
  'trigger': 'VEHICLE_CONNECTED',
  'guard': 'initialHealthCheck Required or Optional Yes',
  'action': 'Set vehicleConnectTransitionFlag=true; route healthcheck',
  'evidence': ['vehicle_session.postconnect', 'vehicle_session.hc_before', 'vehicle_session.hc_after']},
 {'id': 'vehicle_session.select_ecu',
  'from': 'vehicle_session.workspace',
  'to': 'vehicle_session.ecu',
  'trigger': 'system selection/feature navigation',
  'guard': 'ECU ID in shared mounted map',
  'action': 'Set current ECU ID/name; lazily check native connection and discover functions',
  'evidence': ['vehicle_session.current_ecu', 'vehicle_session.ecu_cache']},
 {'id': 'vehicle_session.switch_ecu',
  'from': 'vehicle_session.ecu',
  'to': 'vehicle_session.ecu',
  'trigger': 'select another ECU',
  'guard': 'ECU candidate exists',
  'action': 'Update current reference only; reuse vehicle and per-ECU status/function caches; force flags '
            'trigger clear/recheck',
  'evidence': ['vehicle_session.current_ecu', 'vehicle_session.ecu_cache']},
 {'id': 'vehicle_session.scan',
  'from': 'vehicle_session.workspace',
  'to': 'vehicle_session.healthcheck',
  'trigger': 'manual healthcheck',
  'guard': 'selected scan pattern',
  'action': 'Sort candidates; getEcuStatus; only CONNECTED runs DTC/monitor/RoB/CID, persist and queue '
            'progress',
  'evidence': ['vehicle_session.hc_before', 'vehicle_session.hc_scan', 'vehicle_session.hc_flow']},
 {'id': 'vehicle_session.recheck',
  'from': 'vehicle_session.healthcheck',
  'to': 'vehicle_session.healthcheck',
  'trigger': 'clearEcuConnectCache==1',
  'guard': 'ECU already checked',
  'action': 'Clear native (ECU,bus) cache, connect(group,ECU,bus), refresh functions',
  'evidence': ['vehicle_session.ecu_cache', 'vehicle_session.hc_scan']},
 {'id': 'vehicle_session.connect_failure',
  'from': 'vehicle_session.ecu',
  'to': 'vehicle_session.workspace',
  'trigger': 'connection or function-list rejection',
  'guard': 'getEcuStatus catches promise rejection',
  'action': 'Connection status=0 or functions=[] cached; subsequent explicit recheck can retry',
  'evidence': ['vehicle_session.ecu_cache']},
 {'id': 'vehicle_session.cancel_scan',
  'from': 'vehicle_session.healthcheck',
  'to': 'vehicle_session.cancelling',
  'trigger': 'cancelHealthCheck',
  'guard': 'isRunning and !cancelFlag',
  'action': 'End wired collection; store callback/args; set cancelFlag and enqueue start-cancel',
  'evidence': ['vehicle_session.hc_cancel']},
 {'id': 'vehicle_session.finish_cancel',
  'from': 'vehicle_session.cancelling',
  'to': 'vehicle_session.workspace',
  'trigger': 'scan sees cancelFlag/summary completes',
  'guard': 'cooperative boundary',
  'action': 'Stop scheduling remaining ECU work; enqueue end-cancel callback and retain partial acquired '
            'cache',
  'evidence': ['vehicle_session.hc_scan', 'vehicle_session.hc_flow', 'vehicle_session.hc_cancel_end']},
 {'id': 'vehicle_session.finish_healthcheck',
  'from': 'vehicle_session.healthcheck',
  'to': 'vehicle_session.workspace',
  'trigger': 'scan/enrichment completion',
  'guard': 'not canceled',
  'action': 'Finalize buffer/IPK, latest JSON cache; clear running in finally',
  'evidence': ['vehicle_session.hc_flow', 'vehicle_session.hc_after', 'vehicle_session.hc_cache']},
 {'id': 'vehicle_session.disconnect',
  'from': 'vehicle_session.workspace',
  'to': 'vehicle_session.disconnected',
  'trigger': 'DV000035',
  'guard': 'native input guard succeeds',
  'action': 'Stop utility -> disconnect utility -> physical Disconnect, report priority error; do not '
            'destroy context here',
  'evidence': ['vehicle_session.disconnect_ui', 'vehicle_session.native_disconnect_order']},
 {'id': 'vehicle_session.close',
  'from': 'vehicle_session.workspace',
  'to': 'vehicle_session.closing',
  'trigger': 'MainFrame.dispose/back/logout',
  'guard': 'active child disposal permits transition',
  'action': 'Stop polling; clear UI and worker VehicleInfo, endDiagnosis; reset stored data; start fresh '
            'diagnosis',
  'evidence': ['vehicle_session.workspace_close',
               'vehicle_session.workspace_end',
               'vehicle_session.clear_context']},
 {'id': 'vehicle_session.native_clear',
  'from': 'vehicle_session.closing',
  'to': 'vehicle_session.idle',
  'trigger': 'SC000002 native completion',
  'guard': 'native base input check succeeds',
  'action': 'Stop/disconnect utility; unconditional context deletion/zeroing and WM_QUIT join; managed '
            'destroy+unload only if end result permits',
  'evidence': ['vehicle_session.native_end_order',
               'vehicle_session.native_clear_objects',
               'vehicle_session.native_clear_thread',
               'vehicle_session.il_EndDiagnosis']},
 {'id': 'vehicle_session.end_failure_retains',
  'from': 'vehicle_session.closing',
  'to': 'vehicle_session.error',
  'trigger': 'native end missing response/-1 or destroy false',
  'guard': 'managed EndDiagnosis branches',
  'action': 'Manager retains native instance/handle on failure despite already-cleared manager info; GUI '
            'close wrapper consumes failure',
  'evidence': ['vehicle_session.il_EndDiagnosis', 'vehicle_session.workspace_end']},
 {'id': 'vehicle_session.start',
  'from': 'vehicle_session.idle',
  'to': 'vehicle_session.idle',
  'trigger': 'SC000001',
  'guard': 'instance==0 and settings/load/create/start succeed',
  'action': 'Create CDAInstance then native CCommCtrlMain+ViewerDataCtrl and cache region/language',
  'evidence': ['vehicle_session.il_StartDiagnosis', 'vehicle_session.native_StartDiagnosis']},
 {'id': 'vehicle_session.start_failure',
  'from': 'vehicle_session.idle',
  'to': 'vehicle_session.error',
  'trigger': 'SC000001 failure',
  'guard': 'settings/load/serialize/create/native response failure',
  'action': 'Construct error response; after failed native start destroy+zero+unload; duplicate instance '
            'rejected without replacement',
  'evidence': ['vehicle_session.il_StartDiagnosis']},
 {'id': 'vehicle_session.api_cancel',
  'from': 'vehicle_session.ecu',
  'to': 'vehicle_session.ecu',
  'trigger': 'SC000005',
  'guard': 'execute/cancel delegates and instance exist',
  'action': 'cancel(instance); false cancel response code0x4002; context not destroyed',
  'evidence': ['vehicle_session.il_DiagFunction']},
 {'id': 'vehicle_session.linkage_reconnect',
  'from': 'vehicle_session.idle',
  'to': 'vehicle_session.confirmed',
  'trigger': 'connect by saved/linkage vehicleId',
  'guard': 'PF-confirmed prior vehicle exists -> end/start; otherwise reuse fresh context',
  'action': 'selectVehicleById + VIN fallback, notify confirmation, vehicle exception, populate linkage '
            'VehicleInfo',
  'evidence': ['vehicle_session.by_id']}]

HANDOFFS = [{'to_domain': 'ui_ipc',
  'caller': 'VehicleConnectController/HealthCheckWorkerModel',
  'callee': 'GtsPFApi -> GtsPFRawInterface',
  'mechanism': 'worker commands -> PF request/response',
  'payload': 'apiId + apiArgs; response resultInfo is separate from outer manager result',
  'evidence': ['vehicle_session.api_contracts', 'vehicle_session.il_DiagFunction']},
 {'to_domain': 'vci_transport',
  'caller': 'CDAExecCheckECUConnect/DV000005',
  'callee': 'CCommCtrlMain::CommandExecute(CEcuEachConnectSnd)',
  'mechanism': 'native in-process command',
  'payload': 'groupId:u16,ecuId:int,busId:u16; connect response',
  'evidence': ['vehicle_session.native_CheckECUConnect', 'vehicle_session.ecu_cache']},
 {'to_domain': 'operations',
  'caller': 'DiagAdaptation vehicle/ECU handlers',
  'callee': 'CCommCtrlMain',
  'mechanism': 'shared native instance+4 across operations',
  'payload': 'typed CCmdBase send/receive; resolver family, cache delete, support execution and category-local default/extended/keepalive session ownership',
  'evidence': ['vehicle_session.native_SelectVehicle',
               'vehicle_session.native_SetVehicleId',
               'vehicle_session.native_GetVehicleCache']},
 {'to_domain': 'persistence',
  'caller': 'HealthCheckWorkerModel',
  'callee': 'GtsPFApi.writeFile + healthcheck/IPK buffer',
  'mechanism': 'PF file API',
  'payload': 'LatestHealthCheckData.json and stored acquisition data',
  'evidence': ['vehicle_session.hc_cache', 'vehicle_session.hc_after', 'vehicle_session.hc_read']},
 {'to_domain': 'auth_settings',
  'caller': 'VehicleConnect postprocessing',
  'callee': 'configuration/data collection web services',
  'mechanism': 'existing PF web service wrappers',
  'payload': 'vehicle configuration/initial healthcheck policy; rejection can end diagnosis and LOGOUT',
  'evidence': ['vehicle_session.postconnect', 'vehicle_session.hc_flow']}]

PERSISTENCE = [{'path_pattern': '<specificFolder '
                  'folderNo1><DistDep.specificSubFolders.cacheDataHealthCheck>/LatestHealthCheckData.json',
  'producer': 'HealthCheckWorkerModel.saveCacheData',
  'consumer': 'HealthCheckWorkerModel.readCacheData',
  'created': 'healthCheckOnLoadAfterPart completion',
  'flushed': 'writeFile(mode1) promise completion; failures logged and return undefined',
  'deleted': 'No deletion in inspected save/read path; latest file overwritten',
  'evidence': ['vehicle_session.hc_after',
               'vehicle_session.hc_cache',
               'vehicle_session.hc_read',
               'vehicle_session.hc_path']},
 {'path_pattern': 'GTSPlus/Env/VehicleConfigure.gstg (PF fileType5)',
  'producer': 'VehicleConnectWorkerModel.getCategories',
  'consumer': 'VehicleConnectWorkerModel.getEnvInfo',
  'created': 'save ngCount/password lookup metadata and current package version when resolver returns '
             'nonDispInfo',
  'flushed': 'saveSettingFileInfo promise; failure logged',
  'deleted': 'No deletion in inspected producer/consumer',
  'evidence': ['vehicle_session.configuration_cache']},
 {'path_pattern': 'memory:CDAInstance +4/+8; GUI/worker CommonInfo.VehicleInfo',
  'producer': 'managed StartDiagnosis/native start; vehicle confirmation/context load',
  'consumer': 'all diagnostic requests and ECU switching',
  'created': 'per diagnosis native create; per vehicle GUI VehicleInfo reconstruction',
  'flushed': 'not disk state; worker serializes VehicleInfo across GUI boundary',
  'deleted': 'MainFrame dispose replaces VehicleInfo/SharedData; native clear destroys controllers and '
             'worker queue; managed end success destroys/unloads',
  'evidence': ['vehicle_session.il_StartDiagnosis',
               'vehicle_session.context',
               'vehicle_session.clear_context',
               'vehicle_session.native_clear_objects',
               'vehicle_session.native_clear_thread']}]


def _check(value: Any, expected: Any, label: str) -> None:
    if value != expected:
        raise ValueError(f"vehicle-session evidence drift: {label}")


def _method(text: str, owner: str, name: str) -> str:
    matches = list(re.finditer(re.escape(owner) + r"\.prototype\.([\w$]+)=", text))
    for index, match in enumerate(matches):
        if match.group(1) == name:
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            return text[match.start():end]
    raise ValueError(f"missing frontend method {owner}.{name}")


def load_gui(installed: Path = DEFAULT_INSTALLED, auxiliary: Path = DEFAULT_AUX) -> dict[str, bytes]:
    content = auxiliary / "ContentServer"
    return decode_gui(installed / "GTSPlusGUI/gts.gui", content / "GtsPlus-CM.dll",
                      content / "CryptgraphResource.dll", content / "CryptgraphCommon.dll",
                      installed / "ContentServer/dist.crt")


def build(installed: Path = DEFAULT_INSTALLED, recovered: Path = DEFAULT_RECOVERED,
          auxiliary: Path = DEFAULT_AUX) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []

    def source(key: str, path: Path, representation: str, expected: str | None = None) -> str:
        digest = sha256_file(path)
        if expected is not None:
            _check(digest, expected, str(path.name))
        sid = PREFIX + key
        sources.append({"id": sid, "path": path.resolve().relative_to(REPO_ROOT).as_posix(),
                        "sha256": digest, "size": path.stat().st_size, "representation": representation})
        return sid

    manifest = json.loads((recovered / "manifest.json").read_text())
    entries = {item["path"]: item for item in manifest["binaries"]}
    names = {"native": "DiagAdaptation.dll", "managed": "GTSPlusDiagAdaptMng.dll",
             "pf_contract": "GTSPlusPFCommon.dll"}
    for key, name in names.items():
        rel = "bin/" + name
        entry = entries[rel]
        _check([entry["protected"]["stub_sha256"], entry["protected"]["sidecar_sha256"]],
               EXPECTED_ORIGINALS[key], rel + " protected identity")
        _check(entry["plaintext"]["sha256"], EXPECTED_MAIN[key], rel + " recovery")
        source(key, recovered / rel, "installer-recovered plaintext; native text or materialized CLR bodies",
               EXPECTED_MAIN[key])
        source(key + ".original", installed / "GTSPlus" / rel, "installed protected stub",
               entry["protected"]["stub_sha256"])
        source(key + ".sidecar", installed / "GTSPlus" / (rel + "._"), "installed protected sidecar",
               entry["protected"]["sidecar_sha256"])
    source("gui", installed / "GTSPlusGUI/gts.gui", "authenticated encrypted GUI package", EXPECTED_EXTRA["gui"])
    source("gui_envelope", installed / "GTSPlusGUI/gts.cpf", "local package envelope", EXPECTED_EXTRA["gui_envelope"])
    source("certificate", installed / "ContentServer/dist.crt", "GUI signature verification certificate", EXPECTED_EXTRA["certificate"])
    aux_manifest = json.loads((auxiliary / "manifest.json").read_text())
    aux_entries = {item["relative_path"]: item for item in aux_manifest["entries"]}
    for key, name in (("crypto_native", "GtsPlus-CM.dll"), ("crypto_resource", "CryptgraphResource.dll"),
                      ("crypto_common", "CryptgraphCommon.dll")):
        rel = "ContentServer/" + name
        entry = aux_entries[rel]
        _check([entry["stub_sha256"], entry["sidecar_sha256"]],
               EXPECTED_ORIGINALS[key], rel + " protected identity")
        _check(entry["output_sha256"], EXPECTED_EXTRA[key], rel + " recovery")
        source(key, auxiliary / rel, "recovered packaging implementation", EXPECTED_EXTRA[key])
        source(key + ".original", installed / rel, "installed protected stub", entry["stub_sha256"])
        source(key + ".sidecar", installed / (rel + "._"), "installed protected sidecar", entry["sidecar_sha256"])
    resolver = REPO_ROOT / "data/generated/gtsplus_2026/vehicle_resolver_semantics.json"
    source("resolver", resolver, "existing resolver executable/database closure", EXPECTED_EXTRA["resolver"])
    assets = load_gui(installed, auxiliary)
    # Asset identities pin executable JS control flow, not a keyword census.
    for asset in sorted({spec["asset"] for spec in JS_SPECS}):
        data = assets[asset]
        sid = PREFIX + "asset." + asset
        sources.append({"id": sid, "path": (installed / "GTSPlusGUI/gts.gui").relative_to(REPO_ROOT).as_posix(),
                        "sha256": hashlib.sha256(data).hexdigest(), "size": len(data),
                        "representation": "authenticated decoded GUI ZIP member", "member": asset})
    for spec in JS_SPECS:
        text = assets[spec["asset"]].decode("utf-8-sig")
        body = _method(text, spec["owner"], spec["method"])
        digest = hashlib.sha256(body.encode()).hexdigest()
        _check(digest, spec["sha256"], spec["asset"] + ":" + spec["method"])
        evidence.append({"id": PREFIX + spec["id"], "source": PREFIX + "asset." + spec["asset"],
                         "kind": "javascript-control-flow", "locator": spec["owner"] + ".prototype." + spec["method"],
                         "method_sha256": digest, "finding": spec["finding"]})
    raw = assets["js/gts/common/gts_platform_raw_interface.js"].decode("utf-8-sig")
    for name, api_id in API_IDS.items():
        method = _method(raw, "GtsPFRawInterface", name)
        constant = re.search(r"this.send\((\w+)", method).group(1)
        value = re.search(re.escape(constant) + r"\s*=\s*'([^']+)'", raw).group(1)
        _check(value, api_id, name + " API id")
    native = recovered / "bin/DiagAdaptation.dll"
    for item in NATIVE_HANDLERS:
        _check(va_bytes(native, item["execute"], 16).hex(), item["entry"], item["name"] + " entry")
        _check(struct.unpack("<I", va_bytes(native, item["vtable"] + 4, 4))[0], item["execute"], item["name"] + " vtable")
        evidence.append({"id": PREFIX + "native_" + item["name"], "source": PREFIX + "native",
                         "kind": "native-decompiled-handler", "locator": f"CDAExec{item['name']}::Execute @ 0x{item['execute']:08X}",
                         "vtable": f"0x{item['vtable']:08X}", "entry_bytes": item["entry"],
                         "finding": "RTTI-derived execute slot, decompiled with PE_PROJECT=lc_vehicle_session; typed command ownership is retained in frontend/native handoffs."})
    for item in NATIVE_ANCHORS:
        _check(va_bytes(native, item["va"], len(bytes.fromhex(item["bytes"]))).hex(), item["bytes"], item["id"])
        evidence.append({"id": PREFIX + "native_" + item["id"], "source": PREFIX + "native",
                         "kind": "native-instruction-dataflow", "locator": f"0x{item['va']:08X}",
                         "bytes": item["bytes"], "finding": item["finding"]})
    pe = dnfile.dnPE(str(recovered / "bin/GTSPlusDiagAdaptMng.dll"))
    rows = {str(row.Name): row for row in pe.net.mdtables.MethodDef}
    for name, rva, size, expected, finding in MANAGED_SPECS:
        row = rows[name]
        _check(row.Rva, rva, name + " RVA")
        body = CilMethodBody(MethodBodyReader(pe, row))
        _check(body.size, size, name + " body size")
        digest = hashlib.sha256(pe.get_data(rva, size)).hexdigest()
        _check(digest, expected, name + " IL bytes")
        if not body.instructions:
            raise ValueError("unmaterialized CLR body: " + name)
        start = body.instructions[0].offset
        anchors = []
        for instruction in body.instructions:
            op = str(instruction.opcode)
            operand = format_operand(pe, instruction.operand)
            if (op in {"call", "callvirt"} and any(s in operand for s in
                ("DiagAdaptation", "DiagFunction", "Invoke", "FreeLibrary", "LoadLibrary", "GetResultInfoFromResponse"))):
                anchors.append({"il": f"IL_{instruction.offset - start:04X}", "opcode": op, "operand": operand})
            elif op.startswith(("br", "beq", "bne", "bgt", "blt")):
                anchors.append({"il": f"IL_{instruction.offset - start:04X}", "opcode": op,
                                "target_il": f"IL_{int(instruction.operand) - start:04X}"})
        evidence.append({"id": PREFIX + "il_" + name, "source": PREFIX + "managed", "kind": "managed-IL",
                         "locator": f"DiagAdaptationManager::{name} RVA 0x{rva:X}",
                         "body_sha256": digest, "body_size": size, "anchors": anchors, "finding": finding})
    return {"schema": "gtsplus-lifecycle-domain-v1", "domain": "vehicle_session", "release": "2026.03.002.02",
            "sources": sources, "evidence": evidence,
            "states": [{"id": PREFIX + sid, "owner": owner, "meaning": meaning} for sid, owner, meaning in STATES],
            "transitions": TRANSITIONS, "handoffs": HANDOFFS, "persistence": PERSISTENCE,
            "api_ids": API_IDS,
            "resolver_reuse": {"artifact": "data/generated/gtsplus_2026/vehicle_resolver_semantics.json",
                               "layers": ["VIN/type41/type59 decision", "expected installation", "category+phase route", "live connectivity", "support-family dispatch"],
                               "frontend_distinction": "DV000004 returns CGetMountEcuListNoComm candidates; EcuInfo.getEcuStatus/DV000005 independently confirms connectivity. GUI named mounted map initially contains UNCHECKED candidates."},
            "coverage": {"components": ["authenticated gts.gui frontend", "GTSPlusDiagAdaptMng.dll", "DiagAdaptation.dll", "existing Toyota resolver closure"],
                         "entrypoints": list(API_IDS.values()) + [spec["owner"] + "." + spec["method"] for spec in JS_SPECS],
                         "branches": ["VIM/battery continue/cancel", "PF lock failure", "matching/missing/mismatched/unfixed VIN", "manual VIN and category/option fallback", "default/nondefault OEM restart", "initial healthcheck Optional/Required/None", "ECU cache reuse/refresh/failure", "healthcheck cooperative cancel/revoke/completion", "physical disconnect vs context destruction", "start failure cleanup and end failure retention"]},
            "residuals": [{"question": "Vehicle- and service-dependent results", "why_unclosed": "Offline corpus supplies executable request/response branches but no current live mounted list, VIN, web-service policy or timings.", "next_evidence": "Authorized capture of PF request/response and J2534 transcript, without changing extracted static model."}]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed", type=Path, default=DEFAULT_INSTALLED, help="Installed Toyota Diagnostics root inside this repository")
    parser.add_argument("--recovered", type=Path, default=DEFAULT_RECOVERED, help="Main recovered body root inside this repository")
    parser.add_argument("--auxiliary", type=Path, default=DEFAULT_AUX, help="Auxiliary recovered body root inside this repository")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build(args.installed, args.recovered, args.auxiliary)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
