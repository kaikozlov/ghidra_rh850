#!/usr/bin/env python3
"""Extract the installed browser, local content service and managed IPC lifecycle."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

import dnfile
import pefile
from dncil.cil.body import CilMethodBody

from tools import REPO_ROOT
from tools.techstream.gtsplus_local_crypto import decode_gui
from tools.techstream.inspect_dotnet_il import MethodBodyReader, format_operand, resolve_token, type_name
from tools.techstream.extract_gtsplus_tse_managed_semantics import _recovery_proof

DEFAULT_ROOT = REPO_ROOT / 'software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics'
DEFAULT_MAIN = REPO_ROOT / 'build/out/gtsplus-unprotected'
DEFAULT_AUX = REPO_ROOT / 'build/out/gts-lifecycle-aux'
DEFAULT_OUT = REPO_ROOT / 'data/generated/gtsplus_2026/lifecycle_ui_ipc.json'
D = 'ui_ipc.'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def js_function(text: str, owner: str, name: str, occurrence: int = 0) -> str:
    """Select a prototype assignment; occurrence=-1 selects the effective last body."""
    pattern = re.escape(owner) + r'\.prototype\.' + re.escape(name) + r'\s*=\s*function\b'
    matches = list(re.finditer(pattern, text))
    if not matches:
        raise ValueError(f'missing frontend function {owner}.{name}')
    match = matches[occurrence]
    # Decoded GTS production scripts concatenate complete prototype assignments.
    next_match = re.search(r'[A-Za-z_$][\w$]*\.prototype\.[\w$]+\s*=', text[match.end():])
    end = match.end() + next_match.start() if next_match else len(text)
    return text[match.start():end]


def _operand(pe: Any, value: Any) -> str:
    row = resolve_token(pe, value) if hasattr(value, 'table') else value
    if isinstance(row, dnfile.mdtable.MethodSpecRow):
        row = row.Method.row
    if isinstance(row, dnfile.mdtable.MemberRefRow) and isinstance(row.Class.row, dnfile.mdtable.TypeSpecRow):
        return f'TypeSpec[{bytes(row.Class.row.Signature.value).hex()}]::{row.Name}'
    if isinstance(row, dnfile.mdtable.TypeSpecRow):
        return f'TypeSpec[{bytes(row.Signature.value).hex()}]'
    return format_operand(pe, row)


def qdc_contracts(assets: dict[str, bytes]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Pin QDC's shipped feature and distinguish registration from UI reachability."""
    records: list[dict[str, Any]] = []

    def pin(key: str, path: str, finding: str, owner: str = '', method: str = '',
            needles: tuple[str, ...] = ()) -> str:
        raw = assets[path]
        text = raw.decode('utf-8-sig')
        body = js_function(text, owner, method, -1) if owner else text
        offset = text.index(body)
        anchors = []
        position = 0
        for needle in needles:
            at = body.find(needle, position)
            if at < 0:
                raise ValueError(f'QDC source drift: {path}:{method}:{needle}')
            anchors.append(dict(text=needle, character_offset=offset+at,
                                line=text.count('\n', 0, offset+at)+1))
            position = at + len(needle)
        eid = D+'qdc.'+key
        records.append(dict(id=eid, source=D+'qdc.gui', kind='authenticated-javascript-contract',
                            locator=path+(f'::{owner}.{method}' if owner else ''),
                            asset_sha256=digest(raw), body_sha256=digest(body.encode()),
                            character_offset=offset, line=text.count('\n', 0, offset)+1,
                            anchors=anchors, finding=finding))
        return eid

    main = 'js/gts/GTSMain.js'
    worker = 'js/gts/GTSWorker.js'
    quick = 'js/gts/quick_dtc_check/quick_dtc_check_worker.js'
    controller = 'js/gts/quick_dtc_check/quick_dtc_check_controller.js'
    frame = 'js/gts/main_frame/main_frame_controller.js'
    vehicle = 'js/gts/vehicle_connect/vehicle_connect_worker.js'
    refs = {}
    refs['purpose'] = pin('purpose', 'resources/en/resource.json',
        'Shipped title is DTC Quick Check after Reprogramming; instructions require existing GTS+ VehicleConnect, prohibit operating GTS+ concurrently, and direct further diagnosis back to GTS+.',
        needles=('"DTC Quick Check after Reprogramming"', '"Clear All DTCs"',
                 '"Refresh"', '"Absent/No Comm."', '"Close this window', '"If there were existent DTCs',
                 '"The carrying out this application requires a VehicleConnect.',
                 '"Note:\\nWhen this Application is active'))
    refs['entry'] = pin('entry', 'QDCMain.html',
        'Entry loads main/frame, VehicleConnect and QuickDtcCheck sources, not the normal GTS login/dashboard.',
        needles=('js/gts/GTSMain.js', 'js/gts/vehicle_connect/vehicle_connect_controller.js',
                 'js/gts/quick_dtc_check/quick_dtc_check_controller.js'))
    refs['launcher'] = pin('launcher', 'index.html',
        'Authenticated qdc/index.html binds start_btn_1 to window.open QDCMain.html in _BLANK with1024x768 resizable options. This is the evidenced shipped launcher; the after-reprogramming title does not establish a GTS/CUW launch edge.',
        needles=('button[id^=start_btn]', 'start_btn_1', 'html = "QDCMain.html"',
                 'width=1024px, height=768px, resizable=yes', "window.open(html, '_BLANK', opt)",
                 '<button id="start_btn_1">start(horizontal)</button>'))
    refs['profile'] = pin('profile', worker,
        'PF userProfile JSON is projected into shared worker userInfo. API rejection or malformed JSON resolves result=false with existing userInfo; no login is initiated.',
        'WorkerController', 'getPfUserProfile',
        ('getPfConfig()', 'createReturnValue(true)', '.catch', 'createReturnValue(false)',
         'JSON.parse(response.apiArgs.userProfile)', 'controller.commonInfo.setUserInfo(userInfo)'))
    refs['context'] = pin('context', worker,
        'Only successful getVehicleConfirmation with truthy vinCode yields result=true. Copy PF VIN, vehicleId, decisionVin, categories, car attributes and options; API/missing-VIN errors resolve false. Commented mounted/configuration/provenance fields are not hydrated.',
        'WorkerController', 'getCurrentInformation',
        ('getVehicleConfirmation()', 'createReturnValue(true)', '.catch', 'createReturnValue(false)',
         'response.apiArgs && response.apiArgs.vinCode', 'controller.commonInfo.vehicleInfo.vin',
         'controller.commonInfo.vehicleInfo.optionList', 'return Promise.reject()'))
    refs['context_ui'] = pin('context_ui', main,
        'Success displays do-not-operate-GTS warning then copies vehicle fields and enters frame after acknowledgement. No current context shows TryAgain/Exit: TryAgain re-queries PF, Exit closes. It does not create a new context.',
        'GTSMain', 'onCheckVehicle',
        ('getCurrentInformation()', 'showWarningDialog(response.vehicleInfo)',
         'showVehicleConfirmationErrorDialog()', "'r_msg_iAP99'", 'VEHICLE_CONNECTED',
         "'r_msg_wAP98'", "pressed.id === 'TryAgain'", 'VEHICLE_CHECK', 'gts.util.closeWindow()'))
    refs['new_context'] = pin('new_context', vehicle,
        'Registered callable clone refleshDiagnosis attempts forcedEndDiagnosis then startDiagnosis; both errors are swallowed, and diagnosisRestarted becomes true even when both fail. Not a QDC startup fallback.',
        'VehicleConnectWorkerModel', 'refleshDiagnosis',
        ('gtsPFApi.forcedEndDiagnosis()', '.catch', 'gtsPFApi.startDiagnosis()', '.catch',
         '.then(forcedEndDiagnosis)', '.then(startDiagnosis)', 'model.cache.diagnosisRestarted = true'))
    refs['orphan_connect'] = pin('orphan_connect', main,
        'showVehicleConnectView implements a selectable new-vehicle route but has no direct source call site in QDC assets. Startup/event routing instead evidences reuse/retry/exit; registration alone is not proof of normal UI reachability.',
        'GTSMain', 'showVehicleConnectView',
        ('mainObj.initUnitString()', 'mainObj.initUserTypeSettings()',
         'GTSMain.controller.VEHICLE_CONNECT', 'VehicleConnectController.ControllerEvent.VEHICLE_CONNECTED'))
    refs['frame'] = pin('frame', frame,
        'Frame has only QuickDtcCheck child; refresh mounted ECUs, start battery polling, mileage and display metadata, suppress normal navigation/print/stored controls, then enter quick check.',
        'MainFrameController', 'init',
        ('gtsWorkerApi.getECUList', '.then(initMountedEcuList)', 'startGetVBatteryValue',
         'getMileageInformation', 'getDisplayInfo', 'storedData: false', 'print: false',
         'MainFrameController.ControllerID.QUICK_DTC_CHECK'))
    refs['init'] = pin('init', quick,
        'Build ephemeral cache: VIN/date format, PC+distributor settings, country permanent-DTC policy, flattened equipped ECUs, softwareId. Any failure resolves result=false, possibly with partial ECU list.',
        'QuickDtcCheckWorkerModel', 'initQuickDtcCheck',
        ('model.cache=cache', 'getSettingFileInfo()', 'getEquippedEcuList()', 'getSoftwareId()',
         'createReturnValue(true)', 'createReturnValue(false)', 'cacheData.displayPermanent'))
    refs['scan'] = pin('scan', quick,
        'Start 100ms message pump then clear connection cache and scan ECUs serially. Cancel skips not-yet-started ECUs only. Connection rejection becomes WITHOUT; DTC-read rejection becomes UNKNOWN; capability/system/cache errors abort remaining scan and resolve false. Current DTC functions preferred over past; permanent regulatory function32 only when configured. Always enqueue END and reset cancel flag, including failure.',
        'QuickDtcCheckWorkerModel', 'startDtcCheck',
        ('INTERVAL_TIME=100', 'model.commandThread.start', 'clearEcuConnectCache()',
         'if(model.isCancel)', 'QuickDtcCheck.ecuStatus.ABNORMAL',
         'QuickDtcCheck.ecuStatus.NORMAL', 'QuickDtcCheck.ecuStatus.UNKNOWN',
         'QuickDtcCheck.ecuStatus.WITHOUT', 'createReturnValue(false)',
         'functionIdList=[DTC_FFD,CHECK_DTC,DTC_FFD_P5,CHECK_REGULATORY]',
         'if(currentList.length)', 'else if(pastList.length)',
         'QuickDtcCheck.messageId.END,cancel:model.isCancel', 'model.isCancel=false'))
    refs['clear'] = pin('clear', quick,
        'Clear all connected capable ECUs serially. Optional after-sales date/mileage write ignores error; non-Mazda clears per ECU, phase21 Mazda global clear once. First clear resultInfo error retained while scan continues; prerequisite errors resolve result=false. This is an ECU mutation, not a saved report.',
        'QuickDtcCheckWorkerModel', 'clearDtc',
        ('MAZDA_CAN=21', 'CLEAR_DTC_FFD_FAS=67', 'clearEcuConnectCache()',
         'isClearDtcFfdForAfterSales', 'ecuInfo.phaseType !== MAZDA_CAN',
         'writeAfterSalesZone(ecuInfo)', 'clearDtc(ecuInfo)', 'if(yetCleared)',
         'clearDtcForMazda()', 'yetCleared=false', 'createReturnValue(false)',
         'gtsPFApi.writeAfterSalesZone(para)', 'if(resultInfo.result === NORMAL)'))
    refs['cancel'] = pin('cancel', quick,
        'Cancel merely sets isCancel=true and returns true; it sends no PF cancel and does not interrupt in-flight ECU requests.',
        'QuickDtcCheckWorkerModel', 'cancelDtcCheck', ('model.isCancel=true',))
    refs['stop'] = pin('stop', quick,
        'endDtcCheck clears cancel flag and stops interval producer; not called automatically by scan promise, but by controller receiving END.',
        'QuickDtcCheckWorkerModel', 'endDtcCheck', ('model.isCancel=false', 'model.commandThread.stop'))
    refs['ui_results'] = pin('ui_results', controller,
        'GOT updates ECU status/DTC list; END stops pump, blanks timestamp on cancel, updates view and clears busy flag. Worker result=false is not inspected in this callback.',
        'QuickDtcCheckController', 'onReceiveMessage',
        ('QuickDtcCheck.messageId.GOT', 'updateEcuStatus', 'QuickDtcCheck.messageId.END',
         "message.cancel?'':message.timestamp", 'controller.model.endDtcCheck()',
         'controller.isCheckingDtc=false'))
    refs['ui_clear'] = pin('ui_clear', controller,
        'Clear shows wait modal; completion closes it and chooses retry dialog solely by response.resultInfo.result, not response.result. Success acknowledgement refreshes; failure Yes repeats clear.',
        'QuickDtcCheckController', 'onClearDtc',
        ('showSQuickDtcCheckDl001', 'controller.model.clearDtc()', 'showSQuickDtcCheckDl001',
         'if(response.resultInfo.result)', 'showSQuickDtcCheckDl003', 'showSQuickDtcCheckDl002'))
    refs['clear_ack'] = pin('clear_ack', controller,
        'Success-dialog acknowledgement triggers START_DTC_CHECK, including the outer-result=false/resultInfo-normal mismatch.',
        'QuickDtcCheckController', 'showSQuickDtcCheckDl002',
        ('dialog.buttonPressed.then', 'QuickDtcCheckController.ControllerEvent.START_DTC_CHECK'))
    refs['clear_retry_choice'] = pin('clear_retry_choice', controller,
        'Retry dialog Yes triggers CLEAR_DTC again; No resolves without retry or fresh scan, leaving displayed prior results.',
        'QuickDtcCheckController', 'showSQuickDtcCheckDl003',
        ('dialog.buttonPressed.then', 'BUTTON_YES', 'QuickDtcCheckController.ControllerEvent.CLEAR_DTC', 'else'))
    refs['dispose'] = pin('dispose', controller,
        'Disposal while checking hides status and rejects; idle disposal removes view/events. A source Back callback exists separately, but the shipped view binds only Clear/Cancel/Refresh.',
        'QuickDtcCheckController', 'dispose',
        ('if(controller.isCheckingDtc)', 'view.hideStatusPane()', 'Promise.reject()',
         'view.disposeView()', 'controller.eventDisp.dispose()'))
    refs['back'] = pin('back', controller, 'Callable controller Back callback closes browser directly; not a shipped view click binding.',
        'QuickDtcCheckController', 'onClickSQuickDtcCheck001ViewBackBtn', ('gts.util.closeWindow()',))
    view = 'js/gts/quick_dtc_check/quick_dtc_check_screen_01_view.js'
    refs['view_title'] = pin('view_title', view,
        'Actual view writes localized r_item_iAP01 to document title and header, establishing the after-reprogramming quick-check purpose from executable UI code.',
        'QuickDtcCheckScreen01View', 'initView',
        ("$('title').text(view.getResourceData('r_item_iAP01'))", "document.querySelector('#h_title').textContent"))
    refs['view_controls'] = pin('view_controls', view,
        'During scan Clear/Refresh disabled and Cancel enabled/visible; END enables Clear/Refresh, disables/hides Cancel. A cancelled END leaves checking text rather than writing Completed timestamp.',
        'QuickDtcCheckScreen01View', 'initEcuList',
        ("document.querySelector('#v_c_quick_dtc_check_btn_clear').disabled=true",
         "document.querySelector('#v_c_quick_dtc_check_btn_cancel').disabled=false",
         "document.querySelector('#v_c_quick_dtc_check_btn_refresh').disabled=true"))
    refs['view_end'] = pin('view_end', view,
        'END view update writes Completed only with nonempty timestamp; enables Clear and Refresh even after a failed/partial scan.',
        'QuickDtcCheckScreen01View', 'endUpdateStatus',
        ('if(timeStamp)', "'r_item_iAP03'", "document.querySelector('#v_c_quick_dtc_check_btn_clear').disabled=false",
         "document.querySelector('#v_c_quick_dtc_check_btn_cancel').disabled=true",
         "document.querySelector('#v_c_quick_dtc_check_btn_refresh').disabled=false"))
    refs['view_events'] = pin('view_events', view,
        'Shipped DOM click handlers bind Clear, Cancel and Refresh only. Back callback is present in source, but no Back click binding is installed here; shipped instructions instead say close window.',
        'QuickDtcCheckScreen01View', 'initEventHandler',
        ("$('#v_c_quick_dtc_check_btn_clear').on('click'", "$('#v_c_quick_dtc_check_btn_cancel').on('click'",
         "$('#v_c_quick_dtc_check_btn_refresh').on('click'"))
    refs['power_off'] = pin('power_off', worker,
        'Normal controller scan first requests cancelAutoPowerOff. Worker selects the last available ECU among454/6034/6534, sends its ecuId; no matching ECU and PF rejection both resolve without aborting scan.',
        'WorkerController', 'cancelAutoPowerOff',
        ('[454, 6034, 6534,]', 'getEcuInfoByEcuId(ecuId)', 'if (!powerEcuIdInfo)',
         'gtsPFApi.cancelAutoPowerOff(param)', '.catch'))
    refs['end_diagnosis_effective'] = pin('end_diagnosis_effective', worker,
        'Effective last endDiagnosis assignment overwrites the earlier wrapper before registration: success returns result.apiArgs, not the full PF response; PF rejection propagates.',
        'WorkerController', 'endDiagnosis',
        ('gtsPFApi.endDiagnosis()', 'Promise.resolve(result.apiArgs)', 'Promise.reject(reason)'))
    consumer = 'js/gts/common/gts_worker_api.js'
    refs['reverse_unregistered'] = pin('reverse_unregistered', consumer,
        'initMainCommand is empty. Defining utility WORKER_TO_MAIN metadata does not register a commandMap callback; normal consumer therefore drops reverse-worker messages.',
        'GtsWorkerApi', 'initMainCommand', ('function(){}',))
    refs['reverse_drop'] = pin('reverse_drop', consumer,
        'Unsolicited messages route by commandMap. Missing WORKER_TO_MAIN callback logs and returns; the worker deferred remains pending, with no timeout/drain. Helper dispatch is callable only if separately installed/invoked.',
        'GtsWorkerApi', 'onMessage',
        ('gtsWorkerApi.commandMap[response.commandId]', 'if(!commandFunc)', "'command not found: '", 'return;'))
    refs['main_request'] = pin('main_request', worker,
        'Worker-to-main request saves resolve/reject under Date.now modulo10^10, emits WORKER_TO_MAIN with nested requestId/command/parameter; no timeout or disconnect drain here. Collision loop waits synchronously for clock advance.',
        'WorkerController', 'callTaskOnMainThread',
        ('controller._requestMap', 'while (requestId in controller._requestMap)',
         "commandId: 'WORKER_TO_MAIN'", 'controller.SendToBrowser(commandParam)', 'Date.now() % 10000000000'))
    refs['main_response'] = pin('main_response', worker,
        'MAIN_TO_WORKER response with errorCode exactly0 resolves, otherwise rejects; delete deferred. Missing request logs/returns; absent _requestMap is not guarded.',
        'WorkerController', 'onRescieveMainThreadResponse',
        ('controller._requestMap[requestId]', 'if (!requestDef)', 'errorCode === 0x0000',
         'requestDef.resolve', 'requestDef.reject', 'delete controller._requestMap[requestId]'))
    refs['main_dispatch'] = pin('main_dispatch', 'js/gts/common/gts_utility.js',
        'Unregistered browser helper, not the normal QDC message route: if explicitly invoked, dispatches commandMap callback or returns error1. Its callable login helper opens blank window, polls certification/close, and cleans interval+popup+loader in finally.',
        needles=('gts.util.onRescieveMessageFromWorker = function', 'thisFunc.commandMap[commandId]',
                 'errorCode: 0x0001', 'gtsWorkerApi.sendMainThreadResponse',
                 'gts.util.startLoginProcess = function', "window.open('blank.html'",
                 'setInterval', '.finally', 'clearInterval'))

    worker_text = assets[worker].decode('utf-8-sig')
    model_paths = [path for path in re.findall(r"^importScripts\(BASE_PATH \+ '([^']+_worker\.js)'\);", worker_text, re.M)
                   if re.search(r"workerController\.workerModels\['[^']+'\]\s*=", assets[path].decode('utf-8-sig'))]
    registrations = []
    defaults = js_function(worker_text, 'WorkerController', 'init')
    # Start-of-line excludes commented clone assignments and preserves duplicate writes.
    for match in re.finditer(r"^\s*controller\.defaultCommands\['([^']+)'\]\s*=\s*controller\.(\w+)\.bind", defaults, re.M):
        registrations.append(dict(command=match[1], handler=match[2], owner='WorkerController', path=worker))
    for path in model_paths:
        text = assets[path].decode('utf-8-sig')
        owner = re.search(r'function\s+(\w+)\(', text)[1]
        constants = dict(re.findall(r"(\w+):'([^']+)'", text))
        body = js_function(text, owner, 'initCommandHandler')
        for match in re.finditer(r"model\.commandHandler\[([^\]]+)\]\s*=\s*model\.(\w+)\.bind", body):
            expression = match[1]
            command = expression.strip("'\"") if expression[0] in "'\"" else constants[expression.rsplit('.', 1)[1]]
            registrations.append(dict(command=command, handler=match[2], owner=owner, path=path))
    final_commands = {entry['command']: entry for entry in registrations}
    for entry in final_commands.values():
        text = assets[entry['path']].decode('utf-8-sig')
        body = js_function(text, entry['owner'], entry['handler'], -1)
        at = text.index(body)
        entry['handler_character_offset'] = at
        entry['handler_line'] = text.count('\n', 0, at)+1
        entry['handler_end_line'] = text.count('\n', 0, at+len(body))+1
        entry['handler_sha256'] = digest(body.encode())
        entry['direct_pf_methods'] = sorted(set(re.findall(r'gtsPFApi\.(\w+)\(', body)))
        pattern = re.escape(entry['owner'])+r'\.prototype\.'+re.escape(entry['handler'])+r'\s*=\s*function\b'
        assignments = list(re.finditer(pattern, text))
        entry['prototype_assignment_count'] = len(assignments)
        entry['overwritten_assignments'] = [
            dict(character_offset=match.start(), line=text.count('\n', 0, match.start())+1,
                 body_sha256=digest(js_function(text, entry['owner'], entry['handler'], index).encode()))
            for index, match in enumerate(assignments[:-1])]
    registry_id = pin('registry', worker,
        'Active default assignments plus four imported worker registries are censused, excluding commented echo/changeFunction/createTseFile and simple-utility imports. Registration is callable transport, not UI feature reachability.',
        'WorkerController', 'init', ('controller.defaultCommands', 'Object.assign({}, controller.defaultCommands)',
                                   'Object.assign(controller.commandHandler, controller.workerModels[fn].commandHandler)'))
    records[-1].update(registration_writes=len(registrations), unique_commands=len(final_commands),
                       duplicate_commands=[k for k, v in collections.Counter(r['command'] for r in registrations).items() if v > 1],
                       imported_models=model_paths, commands=list(final_commands.values()))
    # Record direct callers only; dynamic reachability is not disproved by a name scan.
    connect_calls = []
    for path, raw in assets.items():
        if path.endswith('.js'):
            text = raw.decode('utf-8-sig', errors='replace')
            for match in re.finditer(r'\.showVehicleConnectView\s*\(', text):
                connect_calls.append(dict(path=path, character_offset=match.start()))
    records[-1]['show_vehicle_connect_direct_callers'] = connect_calls
    raw_path = 'js/gts/common/gts_platform_raw_interface.js'
    raw_text = assets[raw_path].decode('utf-8-sig')
    constants = dict(re.findall(r"\bvar\s+(PFCMD_\w+)='([^']+)'", raw_text))
    wire_contracts = []
    for method in ('getPfConfig', 'getVehicleConfirmation', 'getSettingFileInfo', 'getEquippedEcuList',
                   'getSoftwareId', 'clearEcuConnectCache', 'checkEcuConnect', 'excuteSystemException',
                   'getEcuFunctionList', 'getDtc', 'writeAfterSalesZone', 'clearDtc', 'clearDtcForMazda',
                   'forcedEndDiagnosis', 'startDiagnosis', 'endDiagnosis', 'cancelAutoPowerOff'):
        body = js_function(raw_text, 'GtsPFRawInterface', method)
        match = re.search(r'\.send\((PFCMD_\w+),', body)
        if not match or match[1] not in constants:
            raise ValueError(f'QDC PF wire mapping drift: {method}')
        eid = pin('wire.'+method, raw_path,
                  f'QDC PF wrapper {method} sends {constants[match[1]]}; external execution outcome is outside this source contract.',
                  'GtsPFRawInterface', method, (match[0],))
        wire_contracts.append(dict(method=method, api_id=constants[match[1]], constant=match[1], evidence=eid))
    return records, dict(
        purpose='DTC Quick Check after Reprogramming', evidence=refs, registry_evidence=registry_id,
        launcher=dict(package='qdc.gui', asset='index.html', action='start_btn_1 click → window.open QDCMain.html',
                      evidence=refs['launcher'], integration_limit='No GTS/CUW direct-launch relationship is inferred.'),
        pf_wire_contracts=wire_contracts,
        smoke_scope='Prepared harness scope: actual GTSMain/event startup route to a synthetic frame boundary; worker scan, view/controller cleanup, clear-dialog choices and consumer dispatch in bounded separate segments. Does not establish periodic pump→browser→feature callback delivery or full frame startup integration; execution results are reported separately.',
        context_policy='Reuse PF profile/current confirmed vehicle; unavailable context requires VehicleConnect in GTS+ then TryAgain. No automatic new diagnosis.',
        normal_ui_features=['automatic serial DTC check', 'Refresh', 'cooperative Cancel', 'Clear All DTCs', 'window close'],
        registered_but_not_normal_ui=['VehicleConnect new-context selection/reset', 'diagnosis start/end', 'logout', 'footer bug URL'],
        source_only_helpers=['showVehicleConnectView (no direct caller found; not evidenced in startup route)', 'controller Back callback (no shipped view click binding)', 'reverse-worker helper (not installed in GtsWorkerApi.commandMap)', 'loadModel (no active command registration)', 'commented simple operation utility import'],
        persistence='Quick-check ECU statuses, DTC lists, timestamp and cancel state are in worker/browser memory only; no TSE/buffer/report save invoked by this feature. Settings/profile are read; after-sales date/mileage and clear requests mutate ECU state through PF.',
        limits='PF/API return handling is proven host behavior, not evidence of ECU clearing, durable report storage, or concurrent GTS+ exclusion.')


def build(root: Path = DEFAULT_ROOT, main_root: Path = DEFAULT_MAIN, aux_root: Path = DEFAULT_AUX) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    binaries: dict[str, Any] = {}
    paths: dict[str, Path] = {}

    def source(key: str, path: Path, representation: str) -> str:
        sid = D + key
        data = path.read_bytes()
        sources.append(dict(id=sid, path=rel(path), sha256=digest(data), size=len(data), representation=representation))
        paths[sid] = path
        return sid

    main_manifest = json.loads((main_root / 'manifest.json').read_text())
    aux_manifest = json.loads((aux_root / 'manifest.json').read_text())
    source('main_manifest', main_root / 'manifest.json', 'recovery manifest')
    source('aux_manifest', aux_root / 'manifest.json', 'recovery manifest')
    components = {
        'controller': ('main', 'bin/GTSPlus.exe'),
        'websocket': ('main', 'bin/GtsPlus-WebSocketManager.dll'),
        'server': ('aux', 'ContentServer/LocalWebServer.dll'),
        'service': ('aux', 'ContentServer/LocalWebServerWindowsService.exe'),
        'crypt': ('aux', 'ContentServer/CryptgraphCommon.dll'),
        'resource': ('aux', 'ContentServer/CryptgraphResource.dll'),
        'cm': ('aux', 'ContentServer/GtsPlus-CM.dll'),
    }
    for key, (corpus, name) in components.items():
        recovered = (main_root if corpus == 'main' else aux_root) / name
        original = root / ('GTSPlus' if corpus == 'main' else '') / name
        # Auxiliary names already carry their installed subdirectory.
        if corpus == 'aux':
            original = root / name
        if corpus == 'main':
            entry = next(x for x in main_manifest['binaries'] if x['path'] == name)
            expected = entry['plaintext']['sha256']
            stub = entry['protected']['stub_sha256']
            sidecar = entry['protected']['sidecar_sha256']
        else:
            entry = next(x for x in aux_manifest['entries'] if x['relative_path'] == name)
            expected, stub, sidecar = entry['output_sha256'], entry['stub_sha256'], entry['sidecar_sha256']
        for path, wanted in [(recovered, expected), (original, stub), (original.with_name(original.name + '._'), sidecar)]:
            if digest(path.read_bytes()) != wanted:
                raise ValueError(f'recovery identity drift: {rel(path)}')
        source(key + '.original', original, 'installed protected PE stub')
        source(key + '.sidecar', original.with_name(original.name + '._'), 'installed CP sidecar')
        sid = source(key, recovered, 'CP-recovered materialized PE')
        if key != 'cm':
            proof = _recovery_proof(recovered)
            binaries[key] = dnfile.dnPE(str(recovered))
            evidence.append(dict(id=D+key+'.materialization', source=sid, kind='managed-materialization', locator='all nonzero MethodDef RVAs', **proof, finding='Every declared managed body RVA has materialized bytes.'))

    def il(key: str, owner: str, method: str, finding: str, needles: tuple[str, ...], index: int = 0) -> str:
        pe = binaries[key]
        td = next(t for t in pe.net.mdtables.TypeDef if type_name(t) == owner and any(str(m.row.Name) == method for m in t.MethodList))
        row = [m.row for m in td.MethodList if str(m.row.Name) == method][index]
        body = CilMethodBody(MethodBodyReader(pe, row))
        lines = [f'{str(i.opcode)} {_operand(pe, i.operand)}'.rstrip() for i in body.instructions]
        pos = 0
        anchors = []
        for needle in needles:
            while pos < len(lines) and needle not in lines[pos]:
                pos += 1
            if pos == len(lines):
                raise ValueError(f'IL drift: {owner}.{method}: {needle}')
            ins = body.instructions[pos]
            anchors.append(dict(offset_from_body=int(ins.offset)-int(body.offset), instruction=lines[pos]))
            pos += 1
        eid = D + key + '.' + owner.split('.')[-1] + '.' + method + (f'.{index}' if index else '')
        branches = [dict(offset_from_body=int(i.offset)-int(body.offset), opcode=str(i.opcode), target=_operand(pe, i.operand)) for i in body.instructions if i.opcode.flow_control.name in ('Branch', 'Cond_Branch')]
        evidence.append(dict(id=eid, source=D+key, kind='managed-il', locator=f'{owner}::{method} overload {index}', rva=int(row.Rva), body_size=int(body.size), body_sha256=digest(body.raw_bytes), anchors=anchors, branches=branches, finding=finding))
        return eid

    s = 'LocalWebServer.LocalHttpService'
    g = 'LocalWebServer.GuiFileContainer'
    svc = 'LocalWebServerWindowsService.LocalWebServerService'
    w = 'GtsPlus_WebSocketManager.WebSocketManager'
    c = 'GtsPlus_WebSocketManager.Component.WebSocketServerComponent'
    p = 'GtsPlus_WebSocketManager.Component.PortNoComponent'
    controller = 'GTSPlusController.ConnectionManager'
    ids: dict[str, str] = {}
    specs = [
        ('host','service',svc,'OnStart','SCM start constructs service and host, initializes content, subscribes host callbacks then opens WCF; startup exceptions set ExitCode=-1 and StopService(1064).',('LocalHttpService::.ctor','Init','add_Faulted','::Open','set_ExitCode','StopService')),
        ('stop','service',svc,'OnStop','Close WCF host and dispose HTTP service; each exception records ExitCode=-1; finally clear owned references.',('::Close','set_ExitCode','Dispose')),
        ('fault','service',svc,'OnHttpSvcFaulted','Faulted callback logs only, with no restart or stop call.',('WriteEventErrorLog',)),
        ('service_name','service',svc,'InitializeComponent','Windows service is GTS+GUIServer.',("'GTS+GUIServer'",'set_ServiceName')),
        ('content_init','server',s,'Init','Public key validation failure sets status1; GUI load failure sets status2; success status0. Alive/end callbacks are installed in finally.',('CheckPubkeyFile','brfalse','Init','brfalse','set_Status','set_Status','set_Status','ER_StartAliveMonitorRunningCS','ER_StartWaitForEndingCS')),
        ('content','server',s,'GetResource','Nonzero service status returns HTTP500; missing archive/resource returns404; success sets MIME type and returns stream.',('get_Status','brfalse','0x1f4','GetResource','brtrue','0x194','GetContentType','set_ContentType')),
        ('gui_init','server',g,'Init','Enumerates every *.gui, loads with distribution certificate public RSA key. Any load false/exception sets HasError; returns true only if some apps exist and none errored.',("'*.gui'",'GetFiles','set_HasError','X509Certificate2::.ctor','GuiFile::Load','brfalse','::Add','set_HasError','get_HasError')),
        ('gui_deleted','server',g,'OnGuiFileDeleted','If invoked for .gui deletion, removes stem from in-memory apps; constructor does not install a filesystem watcher.',("'.gui'",'ContainsKey','Remove')),
        ('ending','server',s,'ExecuteEnding','Execute-ending callback unregisters alive/end monitors only when execute flag is true; does not invoke service shutdown event.',('ldarg.2','brfalse','ER_EndAliveMonitorRunningCS','ER_EndWaitForEndingCS')),
        ('passphrase','crypt','CryptographCommon.GuiFile','GetPassphrase','Sibling <stem>.cpf must exist and is decrypted by packaged CM resource path.',("'.cpf'",'::Exists','brtrue','Decrypt')),
        ('gui_load','crypt','CryptographCommon.GuiFile','Load','Reads IV-length+IV, decrypts AES128CBC; first256 decrypted bytes are signature, remainder ZIP. Computes SHA256(ZIP), then VerifyData hashes this digest again; invalid signature clears zipData and returns false.',('ReadBytes','ToInt32','ReadBytes','GetDecryptor','0x100','ReadBytes','stfld zipData','ComputeHash',"'SHA256'",'VerifyData','brtrue','stfld zipData'),1),
        ('resource','crypt','CryptographCommon.GuiFile','GetResource','Remove one leading slash; ZIP exact entry lookup; missing returns null; XOR transform decodes selected entry into a seeked memory stream.',('ZipArchive::.ctor','GetEntry','brtrue','GetDecryptor','CryptoStream::.ctor','CopyTo','::Seek')),
        ('mask','crypt','CryptographCommon.MaskEncryptor','System.Security.Cryptography.ICryptoTransform.TransformBlock','Entry transform XORs each byte with eight-byte packaging mask; mask resets per transform block.',('ldfld mask','xor','stelem.i1','blt')),
        ('ws_start','websocket',w,'StartProcess','Initializes only on attempt0; scans configured TLS ports; retries recursively only for error5 listener-start failure; other errors return failure.',('Initialize','get_WebSocketServerBaseUrlSsl','GetAvailablePortNo','Initialize','get_ErrorCode','ldc.i4.5','brfalse','StartProcess')),
        ('port_scan','websocket',p,'DoPortScan','Validates configured UInt16 list; attempt index skips prior candidates. First netstat-available port wins; exhaustion throws error1.',('::Split','ToUInt16','CheckPort','brfalse','ret','throw')),
        ('ws_init','websocket',c,'Initialize','Fleck starts TLS listener, auto-restart after listen error and TLS1.2; installed server certificate loaded locally; listener-start exception wraps code5.',('set_RestartAfterListenError','0xc00','set_EnabledSslProtocols','set_Certificate','::Start','stfld serverStatus')),
        ('ws_callbacks','websocket',c,'<Initialize>b__10_0','Per connection callbacks are OnOpen/OnClose/OnMessage/OnError.',('set_OnOpen','set_OnClose','set_OnMessage','set_OnError')),
        ('ws_open','websocket',c,'OpenConnection','Adds connection under monitor then queues synthetic Connect SessionMessage.',('::Add','MESSAGE_WEB_SOCKET_CONNECT','CreateSessionMessage','::Add')),
        ('ws_close','websocket',c,'CloseConnection','While RUNNING remove connection and queue synthetic Disconnect; during Terminate STOPPED suppresses this callback path.',('RUNNING','bne.un','::Remove','MESSAGE_WEB_SOCKET_DISCONNECT','::Add')),
        ('ws_error','websocket',c,'NotifyError','Transport error removes session, closes it and queues Disconnect.',('::Remove','::Close','MESSAGE_WEB_SOCKET_DISCONNECT','::Add')),
        ('ws_receive','websocket',c,'ReceiveMessage','Wraps raw frame with session Guid and TLS flag, then queues for managed controller.',('CreateSessionMessage','::Add')),
        ('ws_fetch','websocket',w,'FetchMessage','Blocking queue Take uses cancellation token. OperationCanceled/ObjectDisposed return failure9; other exceptions failure0.',('::Take','OperationCanceledException','ObjectDisposedException','0x9')),
        ('ws_terminate','websocket',c,'Terminate','Set STOPPED, close all clients, clear session list, dispose server; failure wraps code6.',('STOPPED','::Close','::Clear','::Dispose')),
        ('ws_stop','websocket',w,'StopProcess','Terminate listener before cancellation; cancel/dispose token, then lock/dispose receive queue; exceptions return failures.',('Terminate','::Cancel','::Dispose','Monitor::Enter','::Dispose')),
        ('request','controller',controller,'AnalysisRequestMessage','Synthetic Connect/Disconnect have separate handlers. JSON decode errors respond 0x1fff/error16. Increment cancelId1..10000, optional ACK precedes availability checks and dispatch.',("'Connect'",'Connect',"'Disconnect'",'Disconnect','DeserializeObject','SendResultInfoResponseMessage','0x2710','SendAck','CheckApiAvailable','SetApiTaskMessageList')),
        ('admission','controller',controller,'CheckApiAvailable','Reject settings tampering; except CN000001 require connection condition, API authentication and API exclusive lock availability.',('get_SettingFileTampering',"'CN000001'",'CheckConnectionCondition','CheckApiAuthentication','CheckApiExclusiveLock')),
        ('ack','controller',controller,'SendAck','ACK returns API id and cancelId and preserves free correlation data, serialized as JSON and unicasted to originating session.',('set_ApiId','set_CancelId','set_Free','SerializeObject','SendAsync')),
        ('response','controller',controller,'MakeResponseMessage','Copy request Common and Free into response, add ResultInfo, serialize JSON. Serialization exception returns empty string after error logging.',('set_Common','set_Free','set_ResultInfo','SerializeObject','OutputErrorReportActionLog')),
        ('disconnect','controller',controller,'Disconnect','Unknown session errors. Known session schedules TGXX0001, conditionally DVXX0001/2 monitoring/test cleanup; last matching-name CNXX0001; last diagnosing session DVXX0004; exclusive-owner SCXX0002/LNXX0003, optional SCXX0004 and IFXX0001; finally removes session.',("'TGXX0001'",'get_DataMonitorStarted',"'DVXX0002'","'DVXX0001'","'CNXX0001'",'get_DiagnosisStarted',"'DVXX0004'","'SCXX0002'","'LNXX0003'","'IFXX0001'",'RemoveAllSafe')),
        ('dispatch','controller','GTSPlusController.MainTask','StartMainTask','Fetch each envelope, pause on end-check event; analyze then enqueue by API exact id/prefix and signal named worker EventWaitHandles; cancel token exits loop.',("'GTSP_MAIN_TASK_END_CONFIRM_EVENT_MESSAGE'","'GTSP_VEHICLE_API'","'GTSP_NON_VEHICLE_API'","'GTSP_MESSAGE_API'","'GTSP_CANCEL_API'","'GTSP_WEB_SERVICE_API'",'FetchMessage','AnalysisRequestMessage','EnqueueMessage','EventWaitHandle::Set','get_IsCancellationRequested')),
        ('cancel','controller','GTSPlusController.ExecuteTask.CancelExecuteTask','MessageFunction','SC000004 cancels awaiting execution; SC000005 cancels by cancelId; unknown ids respond error.',("'SC000004'","'SC000005'",'ExecuteCancelAwaitingExecution','ExecuteCancelByCancelID')),
        ('cancel_id','controller','GTSPlusController.ExecuteTask.CancelExecuteTask','ExecuteCancelByCancelID','Malformed/null cancel request returns success/no action; pending vehicle task removed and receives cancellation result0xc000. Otherwise only matching current VehicleConnectionCancelId forwards to adaptation.',('get_CancelId','SearchMessage','RemoveMessage','0xc000','get_VehicleConnectionCancelId','bne.un','ExecuteAdaptation')),
        ('gui_ctor','server',g,'.ctor','Container constructor creates app dictionary and sets paths/error=false; no filesystem watcher is registered.',('stfld apps','set_TargetDir','set_CertFilePath','set_HasError','ret')),
        ('dispose','server',s,'Dispose','HTTP service Dispose is a single ret instruction; owned-host closure occurs in Windows service OnStop.',('ret',)),
        ('alive','server',s,'AliveMonitorCallback','Return empty alive status for service status0, otherwise ERROR_CODE.',('get_Status','brtrue','ret',"'ERROR_CODE'")),
        ('confirm','server',s,'ConfirmEnding','End-confirm callback logs and returns an empty confirmation string; no veto or wait.',('::Info','System.String::Empty','ret')),
        ('unicast','websocket','<SendAsync>d__19','MoveNext','Resolve connection by sessionId; missing throws error7. Await Fleck Send; task faults propagate through async builder.',('SearchTargetConnection','brtrue','ldc.i4.7','throw','IWebSocketConnection::Send','Task::GetAwaiter','TaskAwaiter::GetResult','SetException')),
        ('broadcast_others','websocket','<BroadcastOthersAsync>d__18','MoveNext','Hold session-list monitor, exclude senderSessionId, Send each other connection; returned send tasks are popped, not awaited; outer exceptions fault task.',('Monitor::Enter','senderSessionId','op_Inequality','brfalse','IWebSocketConnection::Send','pop','SetException')),
        ('disconnect_client','websocket',c,'DisconnectClient','Explicit disconnect resolves target session, removes and closes it; missing target throws error8.',('SearchTargetConnection','brfalse','::Remove','::Close','ldc.i4.8','throw')),
        ('cancel_pending','controller','GTSPlusController.ExecuteTask.CancelExecuteTask','ExecuteCancelAwaitingExecution','Remove queued requests from task categories1,2,5,6, using same-session and non-internal-XX predicate; returns response for cancel command, not each removed item.',('ldc.i4.4','InitializeArray','RemoveMessage','BaseErrorResponseMessage')),
        ('cancel_pending_predicate','controller','<>c__DisplayClass9_0','<ExecuteCancelAwaitingExecution>b__0','Pending-cancel removal requires identical SessionId and API id not containing XX.',('get_SessionId','get_SessionId','op_Equality','brfalse',"'XX'",'Contains','ceq')),
        ('cancel_id_predicate','controller','<>c__DisplayClass10_0','<ExecuteCancelByCancelID>b__0','Search pending vehicle queue by cancelId, API containing DV and not XX; predicate itself does not compare sessionId.',('get_CancelId','get_CancelId','bne.un',"'DV'",'Contains',"'XX'",'Contains','ceq')),
    ]
    for entry in specs:
        name, key, owner, method, finding, needles, *overload = entry
        ids[name] = il(key, owner, method, finding, needles, overload[0] if overload else 0)
    category_row = next(r for r in binaries['controller'].net.mdtables.FieldRva if str(r.Field.row.Name).startswith('7E5BBC676CAB163A'))
    category_bytes = binaries['controller'].get_data(category_row.Rva, 16)
    if category_bytes.hex() != '01000000020000000500000006000000':
        raise ValueError('pending cancellation category table drift')
    evidence.append(dict(id=D+'cancel_categories',source=D+'controller',kind='managed-field-rva',locator='PrivateImplementationDetails pending cancellation categories',rva=int(category_row.Rva),bytes_hex=category_bytes.hex(),categories=[1,2,5,6],finding='SC000004 iterates vehicle,non-vehicle,message,web-service queues, excluding currently running work.'))

    config_path = root / 'ContentServer/LocalWebServerWindowsService.exe.config'
    source('host_config', config_path, 'installed XML configuration')
    xml = ET.parse(config_path).getroot()
    base = xml.find('.//baseAddresses/add').attrib['baseAddress']
    if base != 'https://127.0.0.1:50005/':
        raise ValueError('content server base address drift')
    evidence.append(dict(id=D+'https_endpoint', source=D+'host_config', kind='config-and-il', locator='system.serviceModel/services/service', base_address=base, app_settings={x.attrib['key']:x.attrib['value'] for x in xml.findall('./appSettings/add')}, finding='WCF host opens configuration endpoint; Transport security webHttp binding serves GUI resources.'))
    pe = binaries['server']
    method_owner = {id(m.row):type_name(t)+'::'+str(m.row.Name) for t in pe.net.mdtables.TypeDef for m in t.MethodList}
    routes = []
    for attr in pe.net.mdtables.CustomAttribute:
        name = method_owner.get(id(attr.Parent.row), '')
        value = bytes(attr.Value.value)
        if name.startswith('LocalWebServer.ILocalHttpService::') and b'UriTemplate' in value:
            template = value.split(b'UriTemplate',1)[1][1:].decode()
            routes.append(dict(method=name, template=template, attribute_sha256=digest(value)))
    if len(routes) != 8:
        raise ValueError('WCF resource route count drift')
    evidence.append(dict(id=D+'routes', source=D+'server', kind='CLR-custom-attributes-and-il', locator='ILocalHttpService.GetResource1..8 WebGet attributes', routes=routes, finding='Eight GET resource routes support archive stem plus one through eight path segments; implementation joins with slash and calls GetResource.'))
    source('ports', root/'GTSPlus/bin/GtsPlus-WebSocketManager.ini', 'installed listener port policy')
    port_text = (root/'GTSPlus/bin/GtsPlus-WebSocketManager.ini').read_text()
    ports = [int(x) for x in port_text.split('=',1)[1].strip().split(',')]
    if len(ports) != 57:
        raise ValueError('listener port list drift')
    attrs = [bytes(a.Value.value) for a in binaries['websocket'].net.mdtables.CustomAttribute if str(getattr(a.Parent.row,'Name','')) == 'WebSocketServerBaseUrlSsl']
    if not any(b'wss://127.0.0.1:{0}/' in a for a in attrs):
        raise ValueError('WebSocket default URL drift')
    evidence.append(dict(id=D+'ports_policy',source=D+'ports',kind='config-and-CLR-attribute',locator='WebSocketServerDefaultPortNoSsl; Settings.WebSocketServerBaseUrlSsl',ports=ports,url_template='wss://127.0.0.1:{0}/',finding='TLS IPC port selection shared with browser scan list.'))
    cm = pefile.PE(str(aux_root/'ContentServer/GtsPlus-CM.dll'))
    native = {0x2321:'8db049311b10',0x232c:'80f149',0x2d23:'6800040000',0x2d34:'e827230100',0x1010:'e81b6c0000a32caf1b10c3',0x13bb18:'ab0100001000000020000000100000000200000001000000',0x13d604:'5348413100'}
    for rva, value in native.items():
        if cm.get_data(rva,len(value)//2).hex() != value:
            raise ValueError(f'native packaging drift at {rva:#x}')
    evidence.append(dict(id=D+'native_packaging',source=D+'cm',kind='native-decompile-and-instructions',locator='DoFileDecryption@10002aa0; PPF loader100021e0; KDF10015060/10015650; cipher init10001010',anchors=[dict(rva=rva,bytes_hex=value) for rva,value in native.items()],finding='Local RSA-wrapped packaged passphrase; salt16,IV16,AES256CBC; PBKDF2-SHA1 output32 and instruction-proven1024 rounds. No application authentication or network calls executed.'))

    assets_by_package = {}
    inventory = []
    for stem, count in [('gts',3887),('cuw',356),('qdc',399)]:
        source(stem+'.gui',root/f'GTSPlusGUI/{stem}.gui','installed authenticated encrypted frontend package')
        source(stem+'.cpf',root/f'GTSPlusGUI/{stem}.cpf','installed encrypted packaging descriptor')
        assets = decode_gui(root/f'GTSPlusGUI/{stem}.gui',aux_root/'ContentServer/GtsPlus-CM.dll',aux_root/'ContentServer/CryptgraphResource.dll',aux_root/'ContentServer/CryptgraphCommon.dll',root/'ContentServer/dist.crt')
        if len(assets) != count:
            raise ValueError(f'{stem} frontend member count drift')
        assets_by_package[stem] = assets
        entries = []
        for name, data in sorted(assets.items()):
            if '/' not in name and name.endswith('.html'):
                text = data.decode('utf-8-sig')
                entries.append(dict(path=name,size=len(data),sha256=digest(data),scripts=re.findall(r'<script[^>]+src=[\"\']([^\"\']+)',text,re.I),inline_script_count=len(re.findall(r'<script(?![^>]+src=)',text,re.I))))
        census = [(name,len(data),digest(data)) for name,data in sorted(assets.items())]
        inventory.append(dict(package=stem,member_count=count,extension_counts=dict(sorted(collections.Counter(Path(n).suffix for n in assets).items())),member_inventory_sha256=digest(json.dumps(census,separators=(',',':')).encode()),entry_assets=entries))
    source('dist_certificate',root/'ContentServer/dist.crt','installed public distribution certificate')
    evidence.append(dict(id=D+'frontend_inventory',source=D+'gts.gui',kind='executed-offline-decoder',locator='all3 GuiFile envelopes; root HTML entry assets',packages=inventory,signature_validation='RSA PKCS1-v1_5 verify SHA256(SHA256(zipData)) using installed public certificate',finding='All3 packages decoded and RSA signatures verified; no Windows UI or service launched.'))
    worker_entries = []
    for package, assets in assets_by_package.items():
        for path, raw in sorted(assets.items()):
            if not path.endswith('.js') or '/jquery/' in path or '/highcharts/' in path:
                continue
            text = raw.decode('utf-8-sig', errors='replace')
            for match in re.finditer(r'new\s+(SharedWorker|Worker)\s*\(([^;\n]{1,220}?)\)', text):
                worker_entries.append(dict(package=package,caller=path,character_offset=match.start(),constructor=match.group(1),argument_expression=match.group(2),asset_sha256=digest(raw)))
    evidence.append(dict(id=D+'worker_entrypoints',source=D+'gts.gui',kind='decoded-javascript-worker-construction',locator='all3 authenticated package JavaScript assets',workers=worker_entries,finding='Enumerated shipped Worker/SharedWorker producers, including command, buffer, monitoring, logger, active-test-panel and CUW workers; argument expressions retained rather than claiming runtime-resolved URLs.'))

    def js(name: str, path: str, owner: str, method: str, finding: str, needles: tuple[str,...], package: str = 'gts') -> str:
        raw = assets_by_package[package][path]
        text = raw.decode('utf-8-sig')
        body = js_function(text,owner,method)
        pos=0
        anchors=[]
        for needle in needles:
            offset = body.find(needle,pos)
            if offset < 0:
                raise ValueError(f'frontend flow drift {path}:{method}:{needle}')
            anchors.append(dict(character_offset=offset,text=needle))
            pos=offset+len(needle)
        eid=D+'frontend.'+name
        evidence.append(dict(id=eid,source=D+package+'.gui',kind='decoded-javascript',locator=path+'::'+owner+'.'+method,asset_sha256=digest(raw),function_sha256=digest(body.encode()),function_character_offset=text.index(body),anchors=anchors,finding=finding))
        return eid
    raw_path='js/gts/common/gts_platform_raw_interface.js'
    js_specs=[
        ('scan',raw_path,'GtsPFRawInterface','connect','Browser scans57 wss loopback ports; Firefox serial with2s each discards every candidate error and reports REFUSED after exhaustion, even for HELLO rejection. Other browsers race with10s timeouts and preserve HANDSHAKE if any candidate reports it. HELLO requires result0 and appName GTS+.',('scanPorts=','ErrorType=','tryCreateConnections','CONNECTION_HANDSHAKE','CONNECTION_REFUSED',"'firefox'",'2000','catch(e){}}reject(new Array(ErrorType.TIMEOUT))','raceToSuccess','timeout = 10000','new self[objSupport]','PFCMD_SET_CONNECTION_CONDITION','response.resultInfo.result','response.apiArgs.appName')),
        ('send',raw_path,'GtsPFRawInterface','send','Correlate request by Date.now-derived free.freeMsg; requestMap deferred; wire common.apiId/ack, optional apiArgs, free.freeMsg, JSON serialization.',('getNewRequestId','requestMap[requestId]','common:{apiId:command,ack:receiveAck?1:0}','free:{freeMsg:String(requestId)}','JSON.stringify')),
        ('receive',raw_path,'GtsPFRawInterface','onMessage','Parse JSON; route unsolicited guiRelayMsg/broadcastMsg by commandMap; ACK resolves cancelId+response promise and replaces deferred; final result1 marks cancellation,0 success,other reject then deletes map entry.',('JSON.parse','requestMap[requestId]','response.guiRelayMsg','response.broadcastMsg','response.ackMsg','cancelId:response.ackMsg.cancelId','requestMap[requestId]=','case 1','cancel=1','case 0','reject(response)','delete gtsPFApi.requestMap')),
        ('cancel',raw_path,'GtsPFRawInterface','sendCancel','SC000005 frame has ack0 and cancelId arguments; send returns resolved promise without registering response deferred.',('PFCMD_CANCEL_BY_CANCEL_ID','ack:0','JSON.stringify','Promise.resolve')),
        ('cancel_pending',raw_path,'GtsPFRawInterface','sendCancelAwaiting','Sends SC000004, then attempts local result1/cancel1 settlement. The forEach callback accesses this.requestMap without a bound this/thisArg; with pending requests and no ambient requestMap it throws TypeError before resolving, and map entries remain.',('PFCMD_CANCEL_AWAITING_EXECUTION','JSON.stringify','Object.keys(this.requestMap).forEach(function(requestKey){var def=this.requestMap[requestKey]','result:1,cancel:1','def.resolve(result);});')),
        ('worker_send','js/gts/common/gts_worker_api.js','GtsWorkerApi','send','Browser/worker transport is postMessage requestId,commandId,parameter; own deferred correlation separate from native API freeMsg.',('requestMap[requestId]','commandParam={requestId:requestId,commandId:_command,parameter:_param}','postMessage')),
        ('worker_receive','js/gts/common/gts_worker_api.js','GtsWorkerApi','onMessage','Worker callback with requestId resolves/rejects correlated promise then deletes map entry; no requestId invokes commandMap unsolicited notification.',('requestId !== undefined','requestMap[requestId]','requestDef.resolve','requestDef.reject','delete','commandMap[response.commandId]')),
        ('worker_connect','js/gts/common/gts_worker_api.js','GtsWorkerApi','connect','Creates dedicated GTSWorker and installs response/error/messageerror callbacks; sends connect command.',('new Worker','onmessage=','onerror=','onmessageerror=',"send('connect')")),
        ('worker_stop','js/gts/common/gts_worker_api.js','GtsWorkerApi','disconnect','Sends disconnect; only on resolution waits1second then terminates dedicated worker.',("send('disconnect')",'1000','terminate')),
        ('socket_close',raw_path,'GtsPFRawInterface','onClose','Empty raw socket-close callback: no deferred drain, cancellation, or reconnect. The connection closure wrapper only clears isConnected.',('function(evt,gtsPFApi){};',)),
        ('worker_error','js/gts/common/gts_worker_api.js','GtsWorkerApi','onError','Worker onerror callback is empty; no outstanding-request rejection or worker replacement.',('function(evt,gtsWorkerApi){};',)),
        ('worker_message_error','js/gts/common/gts_worker_api.js','GtsWorkerApi','onMessageError','Worker messageerror callback is empty; no outstanding-request rejection.',('function(evt,gtsWorkerApi){};',)),
        ('worker_dispatch','js/gts/GTSWorker.js','WorkerController','onMessageFunction','Select commandHandler; call promise chain, catch into error payload and post back. Unknown-command branch only binds SendToBrowser, does not invoke bound function.',('commandHandler[evt.data.commandId]','commandFunc(evt.data)','catch','retMessage.errorCode','SendToBrowser.bind','else','SendToBrowser.bind')),
        ('broadcast_register','js/gts/GTSWorker.js','WorkerController','init','Worker binds PFCMD_API_BROADCAST (CN000008) to onReceiveBroadCast.',('setBroadcastHandler(PFCMD_API_BROADCAST,controller.onReceiveBroadCast.bind(controller,controller))',)),
        ('broadcast_dispatch','js/gts/GTSWorker.js','WorkerController','onReceiveBroadCast','Only string broadcast IDs1..7 assign a browser command. ID10 keeps commandId empty and forwards it to browser; it does not initiate shutdown or settle pending work.',("var id=param.broadcastMsg.id","var _commandId=''",'switch(id)',"case '1'","case '2'","case '3'","case '4'","case '5'","case '6'","case '7'",'commandId:_commandId','controller.SendToBrowser(retMessage)')),
        ('broadcast_browser_drop','js/gts/common/gts_worker_api.js','GtsWorkerApi','onMessage','Unsolicited notification with absent commandMap entry, including empty commandId from broadcast10, logs command-not-found and returns without settling deferred requests.',('commandMap[response.commandId]','if(!commandFunc)',"'command not found: '",'return;', 'commandFunc(Promise.resolve(response.result))')),
        ('login_error','js/gts/GTSMain.js','GTSMain','showLoginErrorDialog','CONNECTION_REFUSED displays r_msg_w0496; CONNECTION_HANDSHAKE displays r_msg_w0245; acknowledgement closes browser window.',("'CONNECTION_REFUSED'","'r_msg_w0496'",'closeWindow',"'CONNECTION_HANDSHAKE'","'r_msg_w0245'",'closeWindow')),
        ('worker_native_connect','js/gts/GTSWorker.js','WorkerController','cmdConnect','Dedicated worker opens GTS named session max3, creates challenge/checks API auth then starts buffer worker.',('ScreenRelay.API_ID.GTS','maxNum=3','connect(name,maxNum)','initBufferworker','createChallengeCode','checkApiAuthentication')),
        ('worker_native_stop','js/gts/GTSWorker.js','WorkerController','cmdDisconnect','Dispose worker common state; close all buffers; finally terminate buffer worker and disconnect native socket.',('commonInfo.dispose','closeAllBuffers','finally','bufferWorker.terminate','gtsPFApi.disconnect')),
        ('ui_init','js/gts/GTSMain.js','GTSMain','init','Top owner creates CommonInfo/header/footer/login/menu/main frame; starts at login; localization, shared session, dedicated worker, settings and saved-data init precede controllers.',('new CommonInfo','new HeaderPaneController','new LoginController','currentController=mainObj.loginController','ViewUtil.readResource','platformSession.connect','gtsWorkerApi.connect','initCommonSettings')),
        ('ui_transition','js/gts/GTSMain.js','GTSMain','controllerTransition','Dispose current top controller then init next; finally assign currentController even when init rejects; catch common error and clear transition flag.',('processingTransition=true','currentController.dispose','nextController.init','finally','currentController=nextController','catch','processingTransition=false')),
        ('ui_logout','js/gts/GTSMain.js','GTSMain','onLoggedOut','Dispose current/header/footer; relay logout, endDiagnosis and logout (those errors swallowed); dispose common state; disconnect workers/shared session; reconnect/init login. Not process exit.',('currentController.dispose','headerController.dispose','footerController.dispose','sendLogoutMessage','endDiagnosis','logout','commonInfo.dispose','gtsWorkerApi.disconnect','platformSession.disconnect','platformSession.connect','gtsWorkerApi.connect','loginController.init')),
        ('frame_transition','js/gts/main_frame/main_frame_controller.js','MainFrameController','controllerTransition','Dispose current child then bind next navigation events and init; finally installs next controller even on init error; common catch handles display.',('currentController?.dispose','PREV_SCREEN','LOGOUT','MAIN_MENU','TRANSIT_FUNCTION','nextController.init','finally(doneFunc)','catch')),
        ('frame_stop','js/gts/main_frame/main_frame_controller.js','MainFrameController','dispose','Dispose child, stop battery polling and detach header/view; clear vehicle state, endDiagnosis, init stored data and startDiagnosis for returning menu session.',('currentController.dispose','stopGetVBatteryValue','removeHeaderEvents','disposeView','clearVehicleInfo','endDiagnosis','startDiagnosis','endDiagnosisFunc().then(initStoredData).then(startDiagnosisFunc)')),
        ('stored_init','js/gts/GTSStoredMain.js','GTSStoredMain','init','Stored entry reads tse query argument, sets open TSE path, creates StoredFrameController; follows localization/shared+dedicated connection/settings/login startup.',("getFilePath('tse')",'setOpenTseFile','new StoredFrameController','platformSession.connect','gtsWorkerApi.connect','initStoredData','loginController.init','decodeURIComponent')),
        ('stored_enter','js/gts/GTSStoredMain.js','GTSStoredMain','onLoggedIn','After login, startDiagnosis then unit/user settings and STORED_FRAME transition with tse path; errors show dialog whose acknowledgement closes browser window.',('startDiagnosis','initUnitString','initUserTypeSettings','STORED_FRAME','tsefilePath','catch','closeWindow')),
        ('panel_init','js/gts/ActiveTestPanelMain.js','ActiveTestPanelMain','init','Panel entry parses appid/ecuid/didid/busid/phasetype, builds active-test panel then relays RESPONSE_OPEN_ACTIVE_TEST_PANEL to invoking TGD app.',('param.appid','param.ecuid','param.didid','param.busid','param.phasetype','new ActiveTestPanelController','getActiveTestPanelInfo','RESPONSE_OPEN_ACTIVE_TEST_PANEL','setScreenRelayHandler','then(mainObj.sendScreenRelay')),
        ('panel_error','js/gts/ActiveTestPanelMain.js','ActiveTestPanelMain','onErrorOpenActiveTestPanel','Open failure relays original resultInfo or generic result-2/code0xffff/detailFFFFFFFF.',('RESPONSE_OPEN_ACTIVE_TEST_PANEL','response.resultInfo','result=-2','code=0xffff',"'0xFFFFFFFF'",'sendScreenRelay')),
        ('panel_close','js/gts/ActiveTestPanelMain.js','ActiveTestPanelMain','onSuccessCloseActiveTestPanel','Success-close event callback is empty; this browser callback does not close the window or worker.',('function(mainObj,evt){};',)),
    ]
    front={}
    for spec in js_specs:
        front[spec[0]]=js(*spec)
    front['qdc_init']=js('qdc_init','js/gts/GTSMain.js','GTSMain','init','QDC reuses platform/worker but omits login and menu, gets PF user profile then triggers VEHICLE_CHECK.',('platformSession.connect','gtsWorkerApi.connect','getPfUserProfile','VEHICLE_CHECK'),package='qdc')
    front['qdc_connect']=js('qdc_connect','js/gts/GTSWorker.js','WorkerController','cmdConnect','QDC dedicated worker registers QDC,max3, then challenge/API authentication; no buffer worker startup.',('ScreenRelay.API_ID.QDC','maxNum = 3','connect(name, maxNum)','createChallengeCode','checkApiAuthentication'),package='qdc')
    front['qdc_disconnect']=js('qdc_disconnect','js/gts/GTSWorker.js','WorkerController','cmdDisconnect','QDC worker disposes common state then disconnects native socket; buffer infrastructure was removed in this entry variant.',('commonInfo.dispose','gtsPFApi.disconnect()'),package='qdc')
    qdc_evidence, qdc_features = qdc_contracts(assets_by_package['qdc'])
    evidence.extend(qdc_evidence)
    main_html=assets_by_package['gts']['GTSMain.html']
    if b'window.onbeforeunload = confirmExit' not in main_html or b'return "Are you sure you want to close GTS+?"' not in main_html:
        raise ValueError('browser close prompt drift')
    evidence.append(dict(id=D+'browser_close',source=D+'gts.gui',kind='decoded-inline-javascript',locator='GTSMain.html::confirmExit',asset_sha256=digest(main_html),anchors=['window.onbeforeunload = confirmExit','return \"Are you sure you want to close GTS+?\"'],finding='Browser beforeunload returns a close prompt only; it does not call native shutdown or promise-drain API.'))
    # Same full scan policy must occur in decoded production source, not strings-only endpoint inference.
    scan = assets_by_package['gts'][raw_path].decode()
    broadcast_source=assets_by_package['gts']['js/gts/GTSWorker.js'].decode()
    broadcast_body=js_function(broadcast_source,'WorkerController','onReceiveBroadCast')
    handled_broadcast_ids=re.findall(r"case\s*'([^']+)'",broadcast_body)
    if handled_broadcast_ids != list('1234567') or "var PFCMD_API_BROADCAST='CN000008'" not in assets_by_package['gts'][raw_path].decode():
        raise ValueError('broadcast wire key or handled ID census drift')
    match=re.search(r'var scanPorts=\[([^]]+)\]',scan)
    if not match or [int(x) for x in re.findall(r"'(\d+)'",match.group(1))] != ports:
        raise ValueError('browser/server port policy mismatch')
    frame=assets_by_package['gts']['js/gts/main_frame/main_frame_controller.js'].decode()
    registry=re.findall(r'(\w+):new (\w+Controller)\(',frame.split('this.controllers={',1)[1].split('};',1)[0])
    evidence.append(dict(id=D+'screen_registry',source=D+'gts.gui',kind='decoded-javascript-registry',locator='js/gts/main_frame/main_frame_controller.js::MainFrameController constructor',controllers=[dict(key=k,constructor=v) for k,v in registry],asset_sha256=digest(frame.encode()),finding='Imperative event/controller ownership, not an HTTP SPA route router; child disposal/init controls screen transitions.'))
    shared=assets_by_package['gts']['js/gts/GTSLoginSession.js']
    required=('currentPromise=currentPromise.then','connectToPlatform','port.postMessage(\'success.\')','disconnectFromPlatform','connection.disconnect()')
    if not all(x in shared.decode() for x in required):
        raise ValueError('shared login session flow drift')
    evidence.append(dict(id=D+'shared_session',source=D+'gts.gui',kind='decoded-javascript',locator='js/gts/GTSLoginSession.js::onconnect/onMessageFunc/connectToPlatform/disconnectFromPlatform',asset_sha256=digest(shared),anchors=list(required),finding='SharedWorker serializes connect/disconnect commands from MessagePorts on one promise chain and owns an additional GTS max3 native connection. Disconnect closes shared socket without reference-counting browser ports.'))

    state_rows=[('stopped','SCM/browser','No content host/socket'),('hosting','GTS+GUIServer','WCF TLS50005 host opened'),('content_error','GTS+GUIServer','Public-key/archive initialization failed; GET500'),('assets','browser','Authenticated HTML/JS loaded'),('connecting','browser workers/GTSPlus.exe','TLS port discovery/HELLO/connection admission'),('connected','GTSPlus.exe','Session registered; worker command transport ready'),('request','browser worker','Correlated JSON API outstanding'),('acked','browser worker','cancelId available; final response pending'),('queued','GTSPlus.exe','Admitted message enqueued to category worker'),('complete','browser worker','Result success/error/cancellation promise settled'),('disconnecting','GTSPlus.exe/browser workers','Session-scoped cleanup and worker termination'),('login','browser','Login controller active'),('menu','browser','Main menu controller active'),('frame','browser','Diagnostic frame child active')]
    states=[dict(id=D+i,owner=o,meaning=m) for i,o,m in state_rows]
    states.extend([
        dict(id=D+'stored',owner='browser StoredFrameController',meaning='Stored entry with tse query path'),
        dict(id=D+'panel',owner='browser ActiveTestPanelMain',meaning='TGD-embedded active-test panel with screen relay'),
        dict(id=D+'qdc',owner='browser QDC MainFrameController',meaning='DTC Quick Check after Reprogramming, reusing PF vehicle context without login/menu'),
    ])
    states.extend(dict(id=D+'qdc_'+name, owner=owner, meaning=meaning) for name, owner, meaning in [
        ('context_wait', 'QDC GTSMain', 'PF vehicle unavailable; GTS+ VehicleConnect required, retry/exit dialog'),
        ('warning', 'QDC GTSMain', 'Current PF context found; do-not-operate-GTS warning awaiting acknowledgement'),
        ('scanning', 'QuickDtcCheckWorkerModel', 'Serial ECU checks and 100ms message pump; transient status queue'),
        ('results', 'QuickDtcCheckController', 'Completed/cancelled/partial statuses displayed; no saved report'),
        ('clearing', 'QuickDtcCheckWorkerModel', 'Serial capability-gated clear requests; aggregate first error'),
        ('clear_success_dialog', 'QuickDtcCheckController', 'Clear success dialog pending acknowledgement; also reached on outer false with normal resultInfo'),
        ('clear_retry_dialog', 'QuickDtcCheckController', 'Clear resultInfo error; awaiting retry Yes/No'),
        ('new_context_callable', 'VehicleConnectWorkerModel', 'Registered reset/selection clone, not reached by shipped QDC startup'),
        ('main_request', 'QDC worker/browser bridge', 'Worker request deferred pending main-thread callback'),
    ])
    transitions=[]
    def tr(name: str, start: str, end: str, trigger: str, guard: str, action: str, refs: list[str]) -> None:
        transitions.append(dict(id=D+name,**{'from':D+start,'to':D+end},trigger=trigger,guard=guard,action=action,evidence=refs))
    tr('start_host','stopped','hosting','SCM OnStart','ServiceHost.Open succeeds','Initialize public-key+archives and open configured WCF endpoint',[ids['host'],D+'https_endpoint'])
    tr('content_init_failure','hosting','content_error','Public key invalid or archive load false/exception','status1/2','Retain host but resource GET returns500',[ids['content_init'],ids['content']])
    tr('load_assets','hosting','assets','Browser resource GET','status0 and archive entry exists','Get exact ZIP member; XOR decode; MIME stream',[D+'routes',ids['content'],ids['resource'],D+'frontend_inventory'])
    tr('connect_workers','assets','connecting','GTSMain.init','WebSocket/SharedWorker available','Shared session then dedicated worker + buffer worker connections',[front['ui_init'],front['worker_connect'],front['worker_native_connect'],D+'shared_session'])
    tr('connect_success','connecting','connected','Loopback TLS HELLO reply','CN000001 result0 and appName GTS+','Record native session then API challenge/auth admission',[front['scan'],ids['ws_open'],ids['admission']])
    tr('connect_retry','connecting','connecting','Port fail/timeout or native listener error5','Candidates remain','Firefox sequential2s; other browser race10s; native increments scan attempt',[front['scan'],ids['ws_start'],ids['port_scan']])
    tr('connect_failure','connecting','assets','All parallel candidates fail','Browser is not Firefox; no successful HELLO','Report CONNECTION_HANDSHAKE if any failure preserves HANDSHAKE, else CONNECTION_REFUSED; select r_msg_w0245 versus r_msg_w0496.',[front['scan'],front['login_error']])
    tr('serial_connect_failure','connecting','assets','All serial candidates fail','Browser is Firefox; no successful HELLO','Discard candidate failure types and reject TIMEOUT array, mapped to CONNECTION_REFUSED/r_msg_w0496 even when HELLO was rejected.',[front['scan'],front['login_error']])
    tr('json_request','connected','request','UI worker command','Command exists','Worker postMessage→native JSON {common,apiArgs,free}',[front['worker_send'],front['worker_dispatch'],front['send']])
    tr('ack','request','acked','Controller parses request','common.ack=1','Return ackMsg.apiId/cancelId + copied free; replace browser deferred for final result',[ids['request'],ids['ack'],front['receive']])
    tr('admit_request','request','queued','Controller CheckApiAvailable','No tampering; required condition/auth/exclusive checks pass','Enqueue category worker and Set EventWaitHandle',[ids['admission'],ids['dispatch']])
    tr('admit_acked','acked','queued','Controller CheckApiAvailable','Same checks apply after ACK','Enqueue; ACK is not completion or authorization',[ids['request'],ids['admission'],ids['dispatch']])
    tr('reject_request','request','complete','Malformed JSON or admission failure','Deserialize/check fails','Return ResultInfo error and preserve origin-session routing',[ids['request'],ids['admission'],ids['response'],front['receive']])
    tr('final_response','queued','complete','Execution response','result0/1/other','Native JSON→resolve success/cancel or reject; remove deferred→worker result postMessage',[ids['response'],front['receive'],front['worker_receive']])
    tr('cancel_by_id','queued','complete','SC000005','Queued matching id OR currently matching VehicleConnectionCancelId','Remove pending vehicle request and respond0xc000 or forward running cancel to adaptation',[ids['cancel'],ids['cancel_id'],front['cancel']])
    tr('cancel_pending','request','request','SC000004','Nonempty frontend requestMap; no ambient global requestMap','Send native pending-cancel; unbound forEach this then throws, leaving local pending promises. Native independently removes same-session non-XX queued work.',[ids['cancel_pending'],ids['cancel_pending_predicate'],front['cancel_pending']])
    tr('unknown_worker_command','request','request','Worker commandId has no commandHandler','Unrecognized command','Unknown branch creates a bound error-reply function without invoking it; caller deferred remains outstanding.',[front['worker_dispatch']])
    tr('shutdown_broadcast_dropped','connected','connected','CN000008 broadcastMsg.id is string10','Worker handles only string IDs1..7; no browser handler for empty commandId','Worker forwards commandId empty; browser logs command-not-found and returns. This notification neither closes UI/workers nor settles pending requests.',[front['broadcast_register'],front['broadcast_dispatch'],front['broadcast_browser_drop']])
    tr('transport_disconnect','connected','disconnecting','OnClose/OnError','Close path only while server RUNNING','Queue Disconnect; schedule owned-operation cleanup and remove session',[ids['ws_close'],ids['ws_error'],ids['disconnect']])
    tr('shutdown_socket','connected','stopped','WebSocketManager.StopProcess','Stop called','STOPPED; close clients; clear list; dispose listener; cancel fetch then dispose queue',[ids['ws_stop'],ids['ws_terminate'],ids['ws_fetch']])
    tr('service_stop','hosting','stopped','SCM OnStop','Host exists','Close host; dispose HTTP service; exceptions log/set-1',[ids['stop']])
    tr('login_init','assets','login','Initial UI startup','Localization/settings/workers initialize','Create login/header/footer',[front['ui_init']])
    tr('top_navigation','login','menu','Logged-in event','Target controller selected','Dispose current then initialize next; assign target in finally',[front['ui_transition']])
    tr('vehicle_navigation','menu','frame','Vehicle-connected event','Vehicle/domain validation handled by vehicle_session','Top controller disposal and frame init',[front['ui_transition'],D+'screen_registry'])
    tr('child_navigation','frame','frame','Navigation event','Target controller selected','Dispose current child, bind events, init target; common catch',[front['frame_transition']])
    tr('return_to_menu','frame','menu','Main menu event','Frame disposal resolves','Stop battery polling; end diagnosis; reset stored data; start menu diagnosis',[front['frame_stop']])
    tr('logout','frame','login','UI logout','Disposal/connection sequence resolves','Relay logout/end diagnosis/logout; dispose common and workers; reconnect login',[front['ui_logout'],front['worker_native_stop'],front['worker_stop']])
    tr('stored_entry','login','stored','GTSStoredMain logged-in event','startDiagnosis and unit/user settings resolve','Select STORED_FRAME with decoded tse query path; failure acknowledgement closes window',[front['stored_init'],front['stored_enter']])
    tr('panel_entry','connected','panel','ActiveTestPanelMain.init','Panel metadata load succeeds','Parse operation identifiers and relay open result to TGD caller',[front['panel_init'],front['panel_error']])
    tr('qdc_entry','connected','qdc','QDC GTSMain.init','PF user profile/vehicle check domain sequence','Dedicated/shared QDC session,max3; no normal login/menu or buffer worker',[front['qdc_init'],front['qdc_connect']])
    tr('qdc_stop','qdc','disconnecting','QDC worker disconnect','Worker stop command','Dispose common state then native socket disconnect',[front['qdc_disconnect']])
    q = qdc_features['evidence']
    tr('qdc_no_context', 'qdc', 'qdc_context_wait', 'getCurrentInformation completes false', 'PF rejection or missing vinCode', 'Prompt to perform VehicleConnect in GTS+; no new diagnosis fallback', [q['context'], q['context_ui'], q['purpose']])
    tr('qdc_retry_context', 'qdc_context_wait', 'qdc', 'TryAgain', 'User chooses retry', 'Repeat VEHICLE_CHECK and query current PF context', [q['context_ui']])
    tr('qdc_exit_context', 'qdc_context_wait', 'disconnecting', 'Exit', 'No current vehicle required', 'Close browser; socket cleanup is separate', [q['context_ui']])
    tr('qdc_reuse_context', 'qdc', 'qdc_warning', 'Current PF vehicle returned', 'Truthy vinCode', 'Reuse vehicle identity/category/options and warn not to operate GTS+', [q['context'], q['context_ui']])
    tr('qdc_begin_scan', 'qdc_warning', 'qdc_scanning', 'Warning acknowledgement/frame initialization', 'Settings/equipped ECU/softwareId initialization succeeds', 'Enter sole QuickDtcCheck child, best-effort cancelAutoPowerOff, then serial scan/message pump', [q['frame'], q['init'], q['power_off'], q['scan']])
    tr('qdc_scan_end', 'qdc_scanning', 'qdc_results', 'END dequeued', 'Success, capability failure, cancellation, or partial read failures', 'Update statuses, stop pump, clear busy flag; failure result itself not checked by controller', [q['scan'], q['ui_results'], q['stop']])
    tr('qdc_cancel_scan', 'qdc_scanning', 'qdc_scanning', 'Cancel', 'Scan in progress', 'Set flag only; current PF request continues, subsequent ECUs skipped, END cancel hides timestamp', [q['cancel'], q['scan'], q['ui_results']])
    tr('qdc_refresh', 'qdc_results', 'qdc_scanning', 'Refresh', 'Quick-check initialized', 'Reinitialize displayed ECU statuses, best-effort cancelAutoPowerOff, and scan again', [q['scan'], q['power_off']])
    tr('qdc_clear', 'qdc_results', 'qdc_clearing', 'Clear All DTCs', 'Connected ECU exposes clear detail or Mazda phase21', 'After-sales write best effort then clear per ECU/global Mazda once; retain first error', [q['clear']])
    tr('qdc_clear_retry', 'qdc_clearing', 'qdc_clear_retry_dialog', 'Clear response contains resultInfo error', 'response.resultInfo.result is nonzero', 'Close wait modal and offer retry', [q['clear'], q['ui_clear']])
    tr('qdc_clear_success', 'qdc_clearing', 'qdc_clear_success_dialog', 'Clear completes with normal resultInfo', 'response.result=true and resultInfo.result=0', 'Close wait modal and display success dialog', [q['clear'], q['ui_clear']])
    tr('qdc_clear_false_success', 'qdc_clearing', 'qdc_clear_success_dialog', 'Prerequisite failure before recorded clear error', 'response.result=false but resultInfo.result=0', 'Controller ignores outer failure and displays success dialog', [q['clear'], q['ui_clear']])
    tr('qdc_clear_success_ack', 'qdc_clear_success_dialog', 'qdc_scanning', 'Success acknowledgement', 'User acknowledges dialog', 'Trigger START_DTC_CHECK and scan again', [q['clear_ack'], q['power_off'], q['scan']])
    tr('qdc_clear_retry_yes', 'qdc_clear_retry_dialog', 'qdc_clearing', 'Retry Yes', 'User chooses Yes', 'Trigger CLEAR_DTC again', [q['clear_retry_choice']])
    tr('qdc_clear_retry_no', 'qdc_clear_retry_dialog', 'qdc_results', 'Retry No', 'User declines retry', 'Resolve without clearing or scanning again; leave prior display', [q['clear_retry_choice']])
    tr('qdc_close', 'qdc_results', 'disconnecting', 'User closes browser window', 'Shipped instruction says close window; view binds no Back click', 'No feature report-save or explicit endDiagnosis close hook; native transport cleanup is separately owned', [q['purpose'], q['view_events'], front['qdc_disconnect'], ids['disconnect']])
    tr('qdc_new_context_callable', 'qdc', 'qdc_new_context_callable', 'Explicit registered vehicleConnect.refleshDiagnosis invocation', 'Not a normal QDC UI route', 'Attempt forced end then start; swallow failures and set diagnosisRestarted', [q['new_context'], q['orphan_connect'], qdc_features['registry_evidence']])
    tr('qdc_main_request', 'qdc', 'qdc_main_request', 'callTaskOnMainThread', 'Request id unused', 'Emit WORKER_TO_MAIN and retain deferred; normal QDC consumer has no registered reverse callback', [q['main_request'], q['reverse_unregistered']])
    tr('qdc_main_dropped', 'qdc_main_request', 'qdc_main_request', 'Browser GtsWorkerApi.onMessage', 'No commandMap.WORKER_TO_MAIN callback', 'Log command-not-found and return; worker promise remains pending', [q['reverse_drop'], q['reverse_unregistered']])
    tr('qdc_main_response', 'qdc_main_request', 'qdc', 'Explicit MAIN_TO_WORKER response (not normal reverse-route continuation)', 'Response externally supplied for matching requestId', 'Resolve only errorCode0, otherwise reject; delete deferred', [q['main_response']])
    tr('tab_close','connected','disconnecting','Browser unload proceeds','User accepts browser close prompt','No direct native shutdown call in unload handler; transport disconnect drives native session cleanup',[D+'browser_close',ids['ws_close'],ids['disconnect']])
    handoffs=[
        dict(to_domain='bootstrap',caller='LocalWebServerWindowsService.Program.Main',callee='SCM GTS+GUIServer / arbitration monitoring',mechanism='ServiceBase.Run; MsgDatComm alive/end callback registration; SCM owns actual host stop',payload='OnStart/OnStop; alive string; execute flag. Bootstrap config sets service EndMode0, so ordinary arbitration exit does not invoke registered ending callbacks. ExecuteEnding itself only unregisters monitors when execute=true.',policy_reference=['bootstrap.config','bootstrap.arb-confirm','bootstrap.arb-execute'],evidence=[ids['host'],ids['stop'],ids['ending']]),
        dict(to_domain='auth_settings',caller='GTSMain.init/onLoggedOut + ConnectionManager.CheckApiAvailable',callee='login worker/domain auth and settings',mechanism='worker promises then JSON CN000002/CN000003; admission guard',payload='challenge/authentication result; GUI settings/common info',evidence=[front['ui_init'],front['ui_logout'],ids['admission']]),
        dict(to_domain='vehicle_session',caller='MainFrameController / GTSPlusController.MainTask',callee='VehicleConnectionExecuteTask / adaptation',mechanism='JSON SC*/DV*; GTSP_VEHICLE_API event+queue',payload='sessionId/TLS/message/apiId/cancelId; vehicle common state',evidence=[ids['dispatch'],ids['disconnect'],front['frame_stop']]),
        dict(to_domain='operations',caller='CancelExecuteTask.ExecuteCancelByCancelID',callee='AdaptationInterface.ExecuteAdaptation',mechanism='managed dispatch to native adapters',payload='apiId,sessionId,raw JSON,out result when current cancelId matches',evidence=[ids['cancel_id']]),
        dict(to_domain='persistence',caller='GTSMain / MainFrameController',callee='stored-data workers',mechanism='initStoredData; browser workers',payload='CommonInfo session model and saved-data registry',evidence=[front['ui_init'],front['frame_stop']]),
        dict(to_domain='cuw_utility',caller='ContentServer GUI resource service',callee='CUWMain.html',mechanism='TLS GET /GetResource/cuw/CUWMain.html plus browser workers',payload='Authenticated cuw.gui resources; command contracts owned by CUW domain',evidence=[D+'routes',D+'frontend_inventory']),
    ]
    handoffs.extend([
        dict(to_domain='vehicle_session', caller='QDC getCurrentInformation / registered VehicleConnect clone', callee='PF getVehicleConfirmation / diagnosis reset',
             mechanism='QDC worker → PF API', payload='Current VIN/vehicleId/category/options read PF common[0]; explicit diagnosis start may attach shared adaptation; reset remains separately callable and is not the evidenced startup route',
             policy_reference=['vehicle_session.pf_ExecuteGetVehicleConfirmation', 'vehicle_session.pf_ExecuteNotifyVehicleConfirmation',
                               'vehicle_session.pf_ExecuteStartDiagnosis', 'vehicle_session.pf_ExecuteEndDiagnosis', 'vehicle_session.pf_ExecuteEndDiagAdaptation'],
             evidence=[q['context'], q['context_ui'], q['new_context']]),
        dict(to_domain='operations', caller='QuickDtcCheckWorkerModel.startDtcCheck/clearDtc', callee='PF ECU connect/capabilities/DTC/after-sales/clear',
             mechanism='Sequential API promises, 100ms worker message pump', payload='Best-effort cancelAutoPowerOff for last matching ECU454/6034/6534 precedes normal scan; groupId,ecuId,busId,phaseType,getDtcList; date/mileage; Mazda global clear', evidence=[q['power_off'], q['scan'], q['clear'], q['cancel']]),
        dict(to_domain='auth_settings', caller='QDC getPfUserProfile / worker-to-main login helper', callee='PF profile / browser login callback',
             mechanism='PF profile JSON; reverse-worker helper is not registered in normal QDC consumer', payload='userInfo fallback=false is not fresh login; WORKER_TO_MAIN is dropped and its worker deferred remains pending; callable login helper behavior is separate', evidence=[q['profile'], q['main_request'], q['reverse_drop'], q['main_dispatch']]),
    ])
    persistence=[dict(path_pattern='%SystemDrive%/Toyota Diagnostics/GTSPlusGUI/{gts,cuw,qdc}.{gui,cpf}',producer='installed package/update system',consumer='GTS+GUIServer GuiFileContainer',created='installer/update outside this domain',flushed='archives immutable during load; decrypted ZIP stays in process memory',deleted='OnGuiFileDeleted can remove cached app if invoked; watcher not registered here',evidence=[ids['gui_init'],ids['gui_deleted'],ids['passphrase'],D+'frontend_inventory'])]
    persistence.append(dict(path_pattern='QDC worker/browser memory (no file output)', producer='QuickDtcCheckWorkerModel', consumer='QuickDtcCheckController/view',
                            created='init cache; scan queues GOT/END status and timestamp', flushed='100ms queue delivery to browser, not disk commit',
                            deleted='worker/browser lifetime; no explicit report-save path in quick-check feature',
                            evidence=[q['init'], q['scan'], q['ui_results'], q['clear']]))
    return dict(
        schema='gtsplus-lifecycle-domain-v1', domain='ui_ipc',
        sources=sources, evidence=evidence, states=states,
        transitions=transitions, handoffs=handoffs, persistence=persistence,
        qdc_feature_map=qdc_features,
        coverage=dict(
            components=list(components)+['gts.gui','cuw.gui','qdc.gui','shared browser login worker','dedicated command/buffer workers'],
            entrypoints=['SCM ServiceBase.Run→OnStart/OnStop','GTSMain.html','GTSStoredMain.html','ActiveTestPanel.html','CUWMain.html','QDCMain.html','qdc/index.html','blank.html (inert)'],
            branches=['public key/archive init false/exception→500','resource missing→404','native port/start retry and exhaustion','browser serial/racing scans and HELLO failure','JSON parse, ACK, admission, dispatch, success/error/cancel','unsolicited GUI relay and broadcasts','disconnect ownership cleanup','shared/dedicated worker stop','imperative top/child navigation disposal/init','logout reconnect vs application exit','unbound pending-cancel callback','unknown worker command missing reply','inert worker/transport error callbacks'],
        ),
        residuals=[dict(
            question='Windows SCM/TLS/browser execution and environment-specific failure observations',
            why_unclosed='Offline macOS investigation; executable IL and authenticated shipped JS inspected and decoder executed; no Windows application launched.',
            next_evidence='Isolated Windows harness without external network/VCI, using actual ServiceHost+browser and captured trace.',
        )],
    )


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=DEFAULT_ROOT)
    parser.add_argument('--main-root',type=Path,default=DEFAULT_MAIN)
    parser.add_argument('--aux-root',type=Path,default=DEFAULT_AUX)
    parser.add_argument('--output',type=Path,default=DEFAULT_OUT)
    args=parser.parse_args()
    data=build(args.root,args.main_root,args.aux_root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print(f'{len(data["evidence"])} evidence anchors; {len(data["transitions"])} transitions → {rel(args.output)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
