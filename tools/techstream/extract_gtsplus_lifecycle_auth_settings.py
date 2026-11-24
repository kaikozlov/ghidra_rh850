#!/usr/bin/env python3
"""Extract current GTS+ authentication/settings and security from executable evidence.

Offline only. Re-decodes the signed shipped frontend; never sends an application
request or loads a target DLL into the host process. Sensitive configuration and
identity values are excluded by an explicit scalar allowlist.
Recovered inputs default to the aggregate's GTSPlus/Auxiliary components, with
exact source-relative manifest/installed-CP qualification and full valid IL
admission. Native/bodyless rows retain their classifications. Selected semantic
byte pins stay exact; explicit component roots never use stale-corpus fallbacks.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pefile
from tools import REPO_ROOT
from tools.techstream.extract_gtsplus_tse_managed_semantics import (
    _body, _method_pin, _method_rows, _open,
)
from tools.techstream.gtsplus_local_crypto import decode_gui, decrypt_file
from tools.techstream.inspect_dotnet_il import format_operand, inspect_managed_bodies, type_name, validate_managed_bodies
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT as DEFAULT_RECOVERED, qualify_recovered_source

DEFAULT_ROOT = REPO_ROOT / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"
DEFAULT_MAIN = DEFAULT_RECOVERED / "GTSPlus"
DEFAULT_AUX = DEFAULT_RECOVERED / "Auxiliary"
DEFAULT_CUW = DEFAULT_RECOVERED / "CUWPlus"
DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/lifecycle_auth_settings.json"

# Current source contracts and evidence pins; not decompiler inventories or generated PE inputs.
_evidence = json.loads(
    (REPO_ROOT / "data/techstream/lifecycle/auth_settings.json").read_text(encoding="utf-8")
)
INPUTS = _evidence["INPUTS"]
MANAGED = _evidence["MANAGED"]
NATIVE = _evidence["NATIVE"]
JAVASCRIPT = _evidence["JAVASCRIPT"]
STATES = _evidence["STATES"]
TRANSITIONS = _evidence["TRANSITIONS"]
HANDOFFS = _evidence["HANDOFFS"]
PERSISTENCE = _evidence["PERSISTENCE"]
SERVICE_MANAGED = _evidence["SERVICE_MANAGED"]
SECURITY_SOURCES = _evidence["SECURITY_SOURCES"]
# Restore the ordered (RVA, length) windows and tuple records stored as JSON arrays.
SECURITY_NATIVE = [
    (source_sha256, tuple(map(tuple, windows)), digest, finding)
    for source_sha256, windows, digest, finding in _evidence["SECURITY_NATIVE"]
]
SECURITY_MANAGED = [tuple(row) for row in _evidence["SECURITY_MANAGED"]]
SECURITY_CONTRACT_MATRIX = _evidence["SECURITY_CONTRACT_MATRIX"]
del _evidence

ASSEMBLIES = {'GtsPlus-AuthenticationManager.dll': 'bin/GtsPlus-AuthenticationManager.dll',
 'GTSPlusPFCommon.dll': 'bin/GTSPlusPFCommon.dll',
 'GtsPlus-LoginSequenceManager.dll': 'bin/GtsPlus-LoginSequenceManager.dll',
 'info': 'GtsPlus-InfoCenter/GtsPlus-InfoCenter.exe',
 'GTSPlusUserInfoAdapt.dll': 'bin/GTSPlusUserInfoAdapt.dll',
 'GTSPlusWebServiceAdaptMng.dll': 'bin/GTSPlusWebServiceAdaptMng.dll',
 'GTSPlus.exe': 'bin/GTSPlus.exe',
 'GTSPlusSettingFileWrapper.dll': 'bin/GTSPlusSettingFileWrapper.dll',
 'GTSPlusCommon.dll': 'bin/GTSPlusCommon.dll',
 'GtsPlus-UserProfileManager.dll': 'bin/GtsPlus-UserProfileManager.dll',
 'info_multi': 'GtsPlus-InfoCenter/GtsPlus-InfoCenter_Multi/GtsPlus-InfoCenter_Multi.exe',
 'info_msg': 'GtsPlus-InfoCenter/MsgDatComm.dll',
 'GtsPlus-GeneralWebService.dll': 'bin/GtsPlus-GeneralWebService.dll',
 'GtsPlus-FileDownloadManager.dll': 'bin/GtsPlus-FileDownloadManager.dll'}

STATIC_EVIDENCE = [{'id': 'auth_settings.multi_text',
  'source': 'auth_settings.multi_text_en',
  'kind': 'config-resource',
  'locator': 'UIText.en-US.yml text-title,text-guide1..3',
  'anchors': ['GTS+ is already running.',
              '1. Press the X button on the top right of this screen to close it.',
              '2. Log off the user who is running GTS+, or restart the PC.',
              '3. Restart GTS+ with the user who wants to run GTS+.'],
  'finding': 'Duplicate-instance notifier instructs closing this screen and logging off other user/restarting '
             'PC,then relaunching GTS+. It does not claim to activate the existing original-process window.'}]

POLICY_SCALARS = {'region': '1',
 'userProfilePeriodTime': '30',
 'localTimeCycle': '60',
 'differenceToleranceTime': '10',
 'licenseUpdatePeriod': '7',
 'licenseTypeValue': '',
 'webApiInLogoutFlag': 'false',
 'offlinePermissionDays': '30',
 'licenseWarning': '3',
 'independentDealerMode': '0',
 'displayOfflineModeLink': '1',
 'guestUserDispFlag': '0',
 'displayNumberOfAvatar': '6'}

DESKTOP_RESOURCE_PINS = [{'resource': 'GtsPlus-InfoCenter.g.resources',
  'member': 'mainwindow.baml',
  'size': 12721,
  'sha256': '03ea1d3d8164284961d291c994df7a5b96683c00732a7569fe2a8c54d1846777'},
 {'resource': 'GtsPlus-InfoCenter.g.resources',
  'member': 'app.baml',
  'size': 2435,
  'sha256': 'f36b83bd953aa1adaa81564079fb66fa7160885f02011cd5fe66002cb9b49ebe'}]

DESKTOP_CONFIG = {'ApplicationName': 'GtsPlus-InfoCenter',
 'SenderApplicationName': 'GTS+ InfoCenter',
 'DestinationApplicationName': 'GTS+ DataSync',
 'IconFileName': 'GtsPlus-InfoCenter.ico',
 'DataSyncExePath': '../../GTSPlus DataSync/GTSPlusDataSync.exe',
 'CUWPlusExePath': '../../CUWPlus/CuwBackendServiceConsoleApp.exe',
 'UITextMasterDirectoryName': 'UITextMaster',
 'UITextMasterFileNameTemplate': 'UIText.{0}.yml',
 'DatabaseDirectoryPath': '%Public%\\Documents\\GTSPlus\\InfoCenter',
 'DatabaseFileName': 'GtsPlus-InfoCenter.db'}

RESIDUALS = [{'question': 'OEM SSO callback producer and server-side account entitlement/token minting/revocation',
  'why_unclosed': 'Packaged assets expose only LN000003 wrapper and consumer; ContentServer peer confirms '
                  'resource-only routes. Remote portal/service implementation is not in installed package and no '
                  'network/account interaction permitted.',
  'next_evidence': 'Pinned offline server/portal implementation or sanitized existing callback transcript; never '
                   'live credentials.'},
 {'question': 'Wall-clock, Windows crypto/registry/filesystem runtime error timing and UI interleavings',
  'why_unclosed': 'Executable branches pinned statically; Windows host runtime not exercised. Artifact maps decision '
                  'paths, not a live authorization outcome.',
  'next_evidence': 'Throwaway offline Windows harness invoking validators with synthetic invalid inputs and isolated '
                   'temp paths/registry; no real auth/network/vehicle.'}]


def _desktop_evidence(assemblies: dict[str, Any], roots: dict[str, Path]) -> list[dict[str, Any]]:
    primary = assemblies["info"]
    embedded = {
        (str(resource.name), str(entry.name)): bytes(entry.value)
        for resource in primary.net.resources
        for entry in getattr(resource.data, "entries", [])
        if str(entry.name) in ("app.baml", "mainwindow.baml")
    }
    for pin in DESKTOP_RESOURCE_PINS:
        raw = embedded[(pin["resource"], pin["member"])]
        if len(raw) != pin["size"] or _digest(raw) != pin["sha256"]:
            raise ValueError("primary InfoCenter BAML resource drift")
    tree = ET.parse(roots["installed"] / "GTSPlus/GtsPlus-InfoCenter/GtsPlus-InfoCenter.exe.config")
    settings = {element.attrib["name"]: element.findtext("value") for element in tree.findall(".//setting")}
    if any(settings.get(key) != value for key, value in DESKTOP_CONFIG.items()):
        raise ValueError("primary InfoCenter lifecycle configuration drift")
    writes, launches, counter_writes = [], [], []
    census = inspect_managed_bodies(roots["recovered"] / ASSEMBLIES["info"])
    for row, identity in zip(primary.net.mdtables.MethodDef, census["methods"], strict=True):
        if identity["implementation"] != "il":
            continue
        body = _body(primary, row)
        for instruction in body.instructions:
            operand = format_operand(primary, instruction.operand)
            if instruction.opcode.name in ("stfld", "stsfld"):
                if operand == "terminateRequestFromABApp":
                    writes.append(identity)
                elif operand == "_getAllRunningStatusSuccessCount":
                    counter_writes.append(identity)
            if "System.Diagnostics.Process::Start" == operand:
                launches.append(identity)
    def pinned_identity(eid: str) -> dict[str, Any]:
        pin = next(spec for spec in MANAGED if spec["id"] == eid)
        matches = [identity for identity in census["methods"]
                   if identity.get("body", {}).get("sha256") == pin["body_sha256"]
                   and identity["rva"] == pin["rva"]]
        if len(matches) != 1:
            raise ValueError(f"ambiguous desktop semantic identity: {eid}")
        return matches[0]
    if writes or launches != [pinned_identity("auth_settings.info_faq_browser")] or counter_writes != [
        pinned_identity("auth_settings.info_status_success_count")
    ]:
        raise ValueError("primary InfoCenter desktop ownership/counter dataflow drift")
    return [
        {"id": "auth_settings.info_baml_resources", "source": "auth_settings.info", "kind": "embedded-baml",
         "locator": "GtsPlus-InfoCenter.g.resources::{app.baml,mainwindow.baml}",
         "members": copy.deepcopy(DESKTOP_RESOURCE_PINS),
         "finding": "Pin compiled App/MainWindow resources actually loaded by InitializeComponent; startup and Loaded/Closing ownership are joined by managed callsites,not inferred from resource strings."},
        {"id": "auth_settings.info_desktop_config", "source": "auth_settings.info_desktop_config", "kind": "config",
         "locator": "GtsPlus-InfoCenter.exe.config applicationSettings", "values": copy.deepcopy(DESKTOP_CONFIG),
         "finding": "Primary mutex ApplicationName differs from sender used in named pipes: GtsPlus-InfoCenter versus GTS+ InfoCenter. DataSync/CUW EXE paths gate optional readiness checks; no browser-launch URL in these selected lifecycle settings."},
        {"id": "auth_settings.info_desktop_negative_scan", "source": "auth_settings.info", "kind": "whole-managed-body-dataflow-scan",
         "locator": "Every validated IL primary InfoCenter MethodDef; native/bodyless rows classified separately",
         "method_census": census,
         "terminateRequestFromABApp_writers": writes, "process_start_callers": launches,
         "status_success_counter_writers": counter_writes,
         "finding": "No IL writer to terminateRequestFromABApp; success counter only incremented in status callback,not reset. Sole Process.Start callsite is FAQ click. Together with inspected startup/tray/readiness/window bodies,this rules out assigning GTSMain browser autolaunch to these primary InfoCenter paths; it does not prove an absent external launcher."},
    ]


def _service_managed_evidence(assemblies: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for spec in SERVICE_MANAGED:
        pe = assemblies[spec["assembly"]]
        row = pe.net.mdtables.MethodDef.rows[(spec["method_token"] & 0xffffff) - 1]
        body = _body(pe, row)
        pin = _method_pin(row, body)
        if str(row.Name) != spec["method"] or any(pin[k] != spec[k] for k in pin):
            raise ValueError(f"service body drift: {spec['id']}")
        records.append({
            "id": spec["id"], "source": "auth_settings." + spec["assembly"].replace(".", "_"),
            "kind": "managed-il", "locator": {"type": spec["type"], "method": spec["method"],
                "method_token": hex(spec["method_token"]), "offset_base": "method header", **pin},
            "anchors": copy.deepcopy(spec["anchors"]), "finding": spec["finding"],
        })
    for name in ("GtsPlus-GeneralWebService.dll", "GtsPlus-FileDownloadManager.dll"):
        pe = assemblies[name]
        defaults = {}
        for attr in pe.net.mdtables.CustomAttribute:
            owner = getattr(getattr(attr.Type.row, "Class", None), "row", None)
            if owner is None or type_name(owner) != "System.Configuration.DefaultSettingValueAttribute":
                continue
            key = str(attr.Parent.row.Name)
            if key not in ("DefaultRequestIntervalMilliseconds", "DefaultMaxRetryCount", "DefaultConnectionTimeoutMilliseconds"):
                continue
            blob = bytes(attr.Value.value)
            defaults[key] = blob[3:3 + blob[2]].decode("ascii")
        if defaults != {"DefaultRequestIntervalMilliseconds": "1000", "DefaultMaxRetryCount": "5", "DefaultConnectionTimeoutMilliseconds": "60000"}:
            raise ValueError(f"service retry defaults drift: {name}")
        records.append({"id": "auth_settings.service_defaults_" + name.replace(".", "_"),
            "source": "auth_settings." + name.replace(".", "_"), "kind": "managed-custom-attributes",
            "locator": "Settings DefaultSettingValueAttribute blobs", "values": defaults,
            "finding": "Five fixed-interval retries after initial attempt;1000ms interval,60000ms timeout. GWS adapter overrides timeout from matching distributor basicAuthentication row when present."})
    common = assemblies["GTSPlusPFCommon.dll"]
    wire_types = ("GeneralWebServiceRequestApiArgs", "GeneralWebServiceResponseApiArgs", "DownloadFileRequestApiArgs")
    schemas = {}
    for short_name in wire_types:
        full_name = "GTSPlusPFCommon.Message.WSMessage." + short_name
        td = next(td for td in common.net.mdtables.TypeDef if type_name(td) == full_name)
        properties = next(pm.PropertyList for pm in common.net.mdtables.PropertyMap if pm.Parent.row is td)
        fields = []
        for item in properties:
            for attr in common.net.mdtables.CustomAttribute:
                owner = getattr(getattr(attr.Type.row, "Class", None), "row", None)
                if attr.Parent.row is not item.row or owner is None or type_name(owner) != "Newtonsoft.Json.JsonPropertyAttribute":
                    continue
                blob = bytes(attr.Value.value)
                offset = blob.index(b"PropertyName") + len(b"PropertyName")
                wire_name = blob[offset + 1:offset + 1 + blob[offset]].decode("ascii")
                fields.append({"managed_property": str(item.row.Name), "wire_name": wire_name,
                               "custom_attribute_blob": blob.hex()})
        schemas[short_name] = fields
    records.append({"id": "auth_settings.service_wire_schema", "source": "auth_settings.GTSPlusPFCommon_dll",
        "kind": "managed-custom-attributes", "locator": "WSMessage request/response PropertyMap JsonPropertyAttribute blobs",
        "schemas": schemas,
        "finding": "Raw/typed names are managed wire names,not an inferred SDK schema. Crucial inversion: wire authHeader binds AuthHeaderRemove;true removes Bearer only. Absent bool defaults false. folderPath is required destination file path. requestData and responseData remain strings."})
    return records


def _service_js_sections(text: str) -> list[tuple[str, int, str]]:
    # Top-level prototype assignments are the shipped frontend's method boundaries.
    matches = list(re.finditer(r"([A-Za-z_$][\w$]*\.prototype\.[\w$]+)\s*=\s*(?:async\s+)?function", text))
    return [(m.group(1), m.start(), text[m.start():matches[i + 1].start() if i + 1 < len(matches) else len(text)])
            for i, m in enumerate(matches)]


def _public_service_rows(text: str) -> list[dict[str, Any]]:
    """Extract only public URL/routing scalars; never serialize arbitrary YAML values."""
    rows = []
    current = None
    for line_no, line in enumerate(text.splitlines(), 1):
        top = re.match(r"^(\w+)\s*:\s*(?:#.*)?$", line)
        if top:
            current = {"setting": top.group(1), "line": line_no}
            rows.append(current)
            continue
        if line and not line[0].isspace():
            current = None
        match = re.match(r"^  (\w+)\s*:\s*(.*?)\s*(?:#.*)?$", line)
        if current is None or match is None:
            continue
        key, value = match.groups()
        if key == "url" or key.endswith("_url"):
            value = value.strip('"')
            if value and not (value.startswith(("https://", "http://", "C:\\"))):
                raise ValueError(f"unexpected public service URL format: {key}")
            current[key] = value
        elif key in ("id", "formatFlg") and re.fullmatch(r"\d+", value):
            current[key] = int(value)
    return [row for row in rows if any(k == "url" or k.endswith("_url") for k in row)]


def _service_surface(assets: dict[str, bytes], roots: dict[str, Path], sources: list[dict[str, Any]],
                     evidence: list[dict[str, Any]]) -> dict[str, Any]:
    source_ids = {s["id"] for s in sources}
    sections = {}
    producers = []
    for member, data in sorted(assets.items()):
        if not member.endswith(".js") or not member.startswith("js/gts/"):
            continue
        text = data.decode("utf-8")
        for marker, start, segment in _service_js_sections(text):
            sections[marker] = (member, start, segment)
            calls = list(re.finditer(r"(?:gts\.util|gtsPFApi|this\.gtsPFRawInterface|gtsPFRawInterface)\.(executeGenWebService|downloadFile)\(([^)]*)\)", segment))
            if not calls:
                continue
            eid = "auth_settings.service_producer_" + marker.replace(".", "_")
            producers.append({"evidence": eid, "member": member, "function": marker,
                "calls": [{"operation": m[1], "argument_expression": m[2], "character_offset": start + m.start()} for m in calls],
                "serializers": sorted(set(re.findall(r"JSON\.stringify\(([^)]*)\)", segment))),
                "status_literals": sorted(set(re.findall(r"['\"]((?:MIR|TGD|GWS|AISAC)[0-9]+)['\"]", segment))),
                "cancellation_fields": sorted(set(re.findall(r"\b(?:model|cacheData)\.(?:isCancel|cancelFlag|isCancelRequested)\b", segment))),
                "persistence_calls": sorted(set(re.findall(r"gtsPFApi\.(writeFile|saveSettingFileInfo|downloadFile|extractFile|moveFile|deleteFile)\(", segment)))})
            _service_js_record(member, data, marker, start, segment, eid, sources, source_ids, evidence,
                "Actual frontend service producer; request serializers,status literals,cancel guards and local persistence calls are indexed in service_contract_matrix.frontend_producers. PF completion is not remote commit evidence.")
    curated = [
        ("raw", "js/gts/common/gts_platform_raw_interface.js", "GtsPFRawInterface.prototype.executeGenWebService", "Raw WS000001 send passes identical param and receiveAck references; no service-specific request/response translation."),
        ("raw_download", "js/gts/common/gts_platform_raw_interface.js", "GtsPFRawInterface.prototype.downloadFile", "Raw WS000002 send passes identical param/receiveAck and returns send promise; destination file path and optional header flags are not translated."),
        ("typed", "js/gts/common/gts_platform_api.js", "GtsPFApi.prototype.executeGenWebService", "Online typed wrapper passes identical param/receiveAck and resolved response object. Ack envelope is retained; only nested response promise is translated. Offline loginMode2 performs no raw request and resolves JSON '{}' or XML '' with no resultInfo: this is a local no-op,not remote success."),
        ("download_typed", "js/gts/common/gts_platform_api.js", "GtsPFApi.prototype.downloadFile", "Download typed API passes param/receiveAck and response unchanged,including ack envelope. Unlike general-service typed wrapper,it has no offline shortcut."),
        ("calibration", "js/gts/health_check/health_check_worker.js", "HealthCheckWorkerModel.prototype._webServiceCalibrationUpdateCheckFunc", "Skip canceled,empty VIN/IDs,invalid URL or healthCheckCid undefined/truthy. POST JSON scantoolVersion/domain/language/calibrationId array. Parse failure becomes empty objects; transport rejection resolves; MIR4000000/TGD4000000 rejects revoke; otherwise cache commonResult/apiResult and fault messages."),
        ("production", "js/gts/health_check/health_check_worker.js", "HealthCheckWorkerModel.prototype._webServiceGetProductionDateFunc", "Only initial required or optional transition with SSC/CID enabled and absent cached production date. POST JSON vin; successful parse caches commonResult/apiResult and calls overwriteProductionDate WITHOUT awaiting its promise. Transport rejection resolves; business revoke rejects; service completion is not stored-data write completion."),
        ("production_persistence", "js/gts/health_check/health_check_worker.js", "HealthCheckWorkerModel.prototype.overwriteProductionDate", "Truthy date updates commonInfo immediately,then asynchronously reads StoredDataManager vehicleInfo storedId0/allData=true,sets productionDate,and returns overwirteVehicleInfo promise. Calling service handler does not await this promise. Backend write/hash-refresh semantics belong to persistence_commit."),
        ("health_revoke", "js/gts/health_check/health_check_worker.js", "HealthCheckWorkerModel.prototype.isRevoke", "MIR4000000 or TGD4000000 sets isRunning=false and reports revoke; other business codes do not imply revoke."),
        ("datalist", "js/gts/datalist/datalist_worker.js", "DatalistWorkerModel.prototype.executeGenWebService", "POST JSON milInput with session/version/VIN/date/language/userTypeCode/type DataListData/dd. Response JSON is returned to caller; transport/body parse rejection is not a durable upload receipt."),
        ("dtc", "js/gts/dtc/dtc_worker.js", "DtcWorkerModel.prototype.saveSystemDtc", "POST JSON milInput type SystemDTC plus status/DTC arrays; systemDtc/selected URL/id and already-executed ECU gates. Only rejection of original PF request is swallowed. Fulfillment JSON.parse failure and MIR4000000 revoke reject through final handler; executed-ECU marker is appended only on resolved path,including swallowed transport rejection."),
        ("dtc_caller", "js/gts/dtc/dtc_worker.js", "DtcWorkerModel.prototype.getDtcOfStart", "Await saveSystemDtc before createReturnValue. Catch resolves revoke reason without createReturnValue; other failures reject using reason.resultInfo.code/detailCode. Parse SyntaxError lacks resultInfo,so this catch can itself throw TypeError; it does not turn parsing failure into successful diagnostic continuation."),
        ("download_prepare", "js/gts/software_as_a_part_aisac2/software_as_a_part_aisac2_worker.js", "SoftwareAsAPartAisac2WorkerModel.prototype.sendDownloadCalFile", "POST downloadtoCalFile SoftwareID/ID and reqData swNo/fileName/filePath. Require MIR2000000 and no fault. Direct apiResult.URL skips polling; otherwise uppercase SHA256(ID) forms requestDownloadtoCalFileURL ID/HashValue. Errors resolve isShowDl007=true."),
        ("download_poll", "js/gts/software_as_a_part_aisac2/software_as_a_part_aisac2_worker.js", "SoftwareAsAPartAisac2WorkerModel.prototype.receiveDownloadCalFile", "Wait1000ms before first request; POST correlation body repeatedly on MIR2020000 or MIR2000000 without URL;15-minute accumulated timer,not wall-clock deadline. This polling body has no isCancel guard. Failure/fault/timeout resolves dialog flag,not an exception to outer workflow."),
        ("download_install", "js/gts/software_as_a_part_aisac2/software_as_a_part_aisac2_worker.js", "SoftwareAsAPartAisac2WorkerModel.prototype.downloadtocalFile", "WS000002 downloads returned URL to timestamp.zip with wire authHeader:true (AuthHeaderRemove: remove Bearer,retain GUID/MSK/Basic),then enumerate all *.zip,extract tmp,move selected calibration/package extensions overwrite=true,delete tmp and ZIP. Each extraction/move/delete failure is swallowed. A false dialog flag is not proof all calibration files were installed; failed ZIP deletion can leave repeated enumeration."),
        ("help", "js/gts/active_test/active_test_controller.js", "ActiveTestController.prototype.showHelp", "Help uses createHelpInfoUrl and window.open _blank; it is browser navigation,not WS000001/GeneralWebService. No client entitlement or remote receipt inferred."),
        ("settings_selection", "js/gts/GTSWorker.js", "WorkerController.prototype.initUserTypeSettings", "Resolve country/user-type configuration selection before service consumers; filePath drives getSettingFileInfo. See source-pinned country/userType mapping and per-file public endpoint rows."),
    ]
    curated_records = []
    for key, member, marker, finding in curated:
        if marker not in sections:
            raise ValueError(f"service producer missing: {marker}")
        _, start, segment = sections[marker]
        eid = "auth_settings.service_contract_" + key
        _service_js_record(member, assets[member], marker, start, segment, eid, sources, source_ids, evidence, finding)
        curated_records.append({"contract": key, "evidence": eid, "finding": finding})
    for member, marker, finding in [
        ("js/gts/common/gts_worker_util.js", "gts.util.executeGenWebService", "Utility wrapper inspects XML statusCode or JSON root/commonResult only for JSON enum (not JSON_UTF-8). Suffix4010002 plus nested commonResult.secureWebService.ssoURL starts secondary login; success replays identical request once,login rejection resolves original response. Second reply is not inspected recursively."),
        ("js/gts/common/gts_utility.js", "gts.util.createHelpInfoUrl", "Help concatenates commonInfo.getHelpInfoUrl() and specification/function ID verbatim; no request serialization or native web-service call."),
    ]:
        text = assets[member].decode("utf-8")
        start = text.index(marker + "=")
        end = text.find(";gts.util.", start)
        segment = text[start:end + 1 if end >= 0 else len(text)]
        _service_js_record(member, assets[member], marker, start, segment, "auth_settings.service_" + marker.rsplit(".", 1)[1], sources, source_ids, evidence, finding)
    config_rows = []
    decoder = roots["aux"] / "ContentServer/GtsPlus-CM.dll"
    for spec in INPUTS:
        if not spec["id"].startswith("auth_settings.service_config_"):
            continue
        clear = decrypt_file(roots["installed"] / spec["relative"], roots["installed"] / "GTSPlus/Env/GTSPlus.pp", decoder, key_type=2)
        text = clear.decode("utf-8-sig").rstrip("\x00")
        eid = spec["id"] + "_public_rows"
        rows = _public_service_rows(text)
        config_rows.append({"source": spec["id"], "evidence": eid, "file": spec["relative"], "services": rows})
        evidence.append({"id": eid, "source": spec["id"], "kind": "decrypted-config-allowlist", "plaintext_sha256": _digest(clear),
            "locator": "top-level service sections; only URL,id,formatFlg emitted", "services": rows,
            "finding": "Deployed selectable user-type service surface,including empty disabled endpoints. Public endpoint names/routing only; credentials and arbitrary scalars are excluded."})
    setting_keys = {row["setting"] for config in config_rows for row in config["services"]}
    references: dict[str, list[dict[str, str]]] = {key: [] for key in setting_keys}
    folded = {key.lower(): key for key in setting_keys}
    for marker, (member, _, segment) in sections.items():
        for word in set(re.findall(r"\b[A-Za-z_][A-Za-z_0-9]*\b", segment)):
            key = folded.get(word.lower())
            if key:
                references[key].append({"member": member, "function": marker})
    for config in config_rows:
        for row in config["services"]:
            row["frontend_references"] = references[row["setting"]]
    routing = _service_routing(roots, decoder, evidence)
    return {"frontend_producers": producers, "contracts": curated_records, "deployed_user_type_endpoints": config_rows,
        "deployed_routing": routing,
        "api_to_client": [{"api": "WS000001", "raw": "executeGenWebService", "adapter": "GeneralWebService", "client": "GtsPlus-GeneralWebService.GeneralWebService.SendRequest"},
                          {"api": "WS000002", "raw": "downloadFile", "adapter": "DownloadFile", "client": "GtsPlus-FileDownloadManager.FileDownloadManager.DownloadFile"}],
        "selection": "Country/userType selects UserTypeSettings filePath; each service URL and id are frontend input. Native adapter Find(basicAuthentication.id==serverId) chooses credentials and optional timeout,not endpoint URL. Secure IDs100..199 add secondResponseID,Tascal200..299 add X-Requested-With and ticket; selected installed credential rows1,2,3,101,102 have timeouts60000,5000,300000,60000,60000ms. No URL-to-serverId binding is enforced here.",
        "envelopes": "Raw and online typed API preserve request and response; native forwards requestData unchanged. RestClient adds protocol media type and headers. HTTP200/202/204 -> Result=true,error=null; mapped HTTP errors also Result=true,so adapter returns PF result0 with raw responseData. Only Result=false becomes PF5001 with GWS detail. GUI business commonResult/status/fault handling remains per service.",
        "error_layers": {"MSK": "GWS4003 -> RenewalMSK and one replay with updated MSK; no regenerated auth hash on replay. GWS4004 -> credential deletion/revoke sequence. GWS4005 -> cache new requestId/ssoUrl,not revoke.",
            "transport": "GWS retries empty body or status suffix5000000/5030000,plus policy exception handling,5 retries at1000ms by default. FDM retries500/503 or nonpositive ContentLength/inspection exceptions,not canceled Task. Neither public GWS API nor PF download message exposes caller cancellation; FDM creates its own unexposed token.",
            "escaping_exceptions": "Unexpected adapter/helper/cleanup exceptions are not caught by ExecuteAdaptation. GWS license Monitor exits in finally,but EndFileEdit is normal-only. FDM has no license Monitor; EndFileEdit also skipped on throw. No fabricated PF result is assigned to these escaping exceptions.",
            "observable": "Local PF completion,parsed business status,cache mutation,file operation ordering only. No remote durability,OEM entitlement,server-side idempotence or ECU write success is established."}}


def _service_js_record(member: str, data: bytes, marker: str, start: int, segment: str, eid: str,
                       sources: list[dict[str, Any]], source_ids: set[str], evidence: list[dict[str, Any]], finding: str) -> None:
    sid = "auth_settings.service_asset_" + member.replace("/", "_").replace(".", "_")
    if sid not in source_ids:
        sources.append({"id": sid, "path": next(s["path"] for s in sources if s["id"] == "auth_settings.gts_gui"),
            "member": member, "sha256": _digest(data), "size": len(data), "representation": "authenticated decoded ZIP member",
            "derived_from": ["auth_settings.gts_gui", "auth_settings.dist_crt"],
            "recovery": "fresh gtsplus_local_crypto.decode_gui; shipped ZIP hash and RSA authentication"})
        source_ids.add(sid)
    evidence.append({"id": eid, "source": sid, "kind": "signed-javascript", "locator": {"member": member,
        "function": marker, "character_start": start, "character_length": len(segment), "segment_sha256": _digest(segment.encode())}, "finding": finding})


def _service_routing(roots: dict[str, Path], decoder: Path, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    decoded = {}
    for name in ("DistDep", "GTSPlusCommon"):
        clear = decrypt_file(roots["installed"] / f"GTSPlus/Env/{name}.gstg",
                             roots["installed"] / "GTSPlus/Env/GTSPlus.pp", decoder, key_type=2)
        decoded[name] = (clear, clear.decode("utf-8-sig").rstrip("\x00"))
    clear, dist = decoded["DistDep"]
    auth = dist[dist.index("basicAuthentication:"):dist.index("\nfileDownloadAuthentication:")]
    auth_rows = [{"serverId": int(m[1]), "timeout_ms": int(m[2])} for m in
                 re.finditer(r"  - id:\s*(\d+)[\s\S]*?    timeout:\s*(\d+)", auth)]
    country = None
    user_type = None
    selections = []
    for line in dist[dist.index("countryInformation:"):dist.index("\ncompensationTirePressure:")].splitlines():
        match = re.match(r'  - code: "([^"]+)"', line)
        if match:
            country = match[1]
        match = re.match(r'      - code: "([^"]+)"', line)
        if match:
            user_type = match[1]
        match = re.match(r'        fileName: "([^"]+)"', line)
        if match:
            selections.append({"country": country, "user_type": user_type, "file": match[1]})
    evidence.append({"id": "auth_settings.service_routing_distributor", "source": "auth_settings.DistDep_gstg",
        "kind": "decrypted-config-allowlist", "plaintext_sha256": _digest(clear),
        "locator": "basicAuthentication id/timeout and countryInformation userType code/fileName only",
        "authentication_routes": auth_rows, "settings_selection": selections,
        "finding": "Credentials are deliberately omitted; serverId chooses credential row independently of caller URL. Country/userType selects deployed service settings file,not remote entitlement."})
    clear, common = decoded["GTSPlusCommon"]
    ranges = {key: int(re.search(r"^  " + key + r":\s*(\d+)", common, re.M)[1])
              for key in ("secureServerIdMin", "secureServerIdMax", "tascalServerIdMin", "tascalServerIdMax")}
    evidence.append({"id": "auth_settings.service_routing_ranges", "source": "auth_settings.GTSPlusCommon_gstg",
        "kind": "decrypted-config-allowlist", "plaintext_sha256": _digest(clear),
        "locator": "webServiceInfo routing-range scalars only", "values": ranges,
        "finding": "Inclusive secure range adds secondResponseID; inclusive Tascal range adds X-Requested-With and ticket headers. DistDep seed contains no Tascal200..299 authentication row."})
    return {"authentication_routes": auth_rows, "settings_selection": selections, "header_ranges": ranges}


next(row for row in SECURITY_CONTRACT_MATRIX["contracts"]
     if row["id"] == "security.general-webservice-http")["tls_policy"] = {'source_sha256': '33a6f6a8a8e653aed1af4e5b48e3672b661e8d38e90e6c9b89e4e5ee28ecdfec',
 'constructor_token': '0x06000075',
 'callback_token': '0x0600007F',
 'evidence': ['security.il.33a6f6a8a8e6.06000075', 'security.il.33a6f6a8a8e6.0600007f'],
 'installation': 'Every RestClient construction reads '
                 'ServicePointManager.ServerCertificateValidationCallback, '
                 'Delegate.Combine(existing,cachedLambda), casts and stores the combined delegate back. '
                 'Lambda delegate is lazily cached in static<>9__5_0 but is appended again on every '
                 'construction; caching does not make registration one-time.',
 'callback': 'The four-argument RemoteCertificateValidationCallback ignores '
             'sender/certificate/chain/SslPolicyErrors and returns true (ldc.i4.1;ret).',
 'scope': 'Mutable process-global ServicePointManager certificate-validation policy, not scoped to this '
          'request,URL,RestClient instance or GWS. Other managed clients using that policy can observe it. '
          'Native WinHTTP/WinInet policies remain separate source-specific flows.',
 'lifetime': 'No removal/reset/disposal branch is present in this constructor or callback; repeated '
             'instances accumulate callback registrations. Getter/combine/set has no source synchronization. '
             'Standard multicast-delegate return behavior and later external changes are typed '
             'framework/process-state boundaries, not an invented irrevocable global invariant.'}


def _security_domain(
    roots: dict[str, Path], sources: list[dict[str, Any]],
    evidence: list[dict[str, Any]], materialization: dict[str, Any],
) -> dict[str, Any]:
    """Admit exact PEs and recheck shared byte/IL pins, without target execution."""
    paths: dict[str, Path] = {}
    source_ids: dict[str, str] = {}
    instance_ids: list[str] = []
    by_path = {source["path"]: source for source in sources if "path" in source}
    for spec in SECURITY_SOURCES:
        path = roots[spec["root"]] / spec["relative"]
        data = path.read_bytes()
        if _digest(data) != spec["sha256"]:
            raise ValueError(f"security source drift: {spec['id']}")
        relative = _relative(path)
        record = by_path.get(relative)
        if record is None:
            record = {"id": spec["id"], "path": relative,
                      "sha256": spec["sha256"], "size": len(data)}
            if spec["root"] == "installed":
                record["representation"] = "exact installed PE; native application or typed provider interface"
            else:
                record["recovery"] = qualify_recovered_source(
                    path, roots["installed"] / spec["protected_relative"],
                    component_root=roots[spec["root"]],
                )
                record["representation"] = "manifest-qualified recovered PE"
            if "role" in spec:
                record["role"] = spec["role"]
            sources.append(record)
            by_path[relative] = record
        elif record["sha256"] != spec["sha256"]:
            raise ValueError(f"security source alias drift: {spec['id']}")
        paths.setdefault(spec["sha256"], path)
        source_ids.setdefault(spec["sha256"], record["id"])
        instance_ids.append(record["id"])

    native_by_source: dict[str, list[tuple[Any, ...]]] = {}
    for pin in SECURITY_NATIVE:
        native_by_source.setdefault(pin[0], []).append(pin)
    for source_sha, pins in native_by_source.items():
        pe = pefile.PE(str(paths[source_sha]))
        try:
            for _, regions, expected, finding in pins:
                digest = hashlib.sha256()
                for rva, length in regions:
                    data = pe.get_data(rva, length)
                    if len(data) != length:
                        raise ValueError(f"security native region absent: {source_sha}:{rva:#x}")
                    digest.update(data)
                if digest.hexdigest() != expected:
                    raise ValueError(f"security native bytes drift: {source_sha}:{regions[0][0]:#x}")
                eid = f"security.native.{source_sha[:12]}.{regions[0][0]:x}.{expected[:12]}"
                evidence.append({
                    "id": eid, "source": source_ids[source_sha],
                    "kind": "native-byte-regions",
                    "locator": {"offset_base": "PE RVA", "regions": [
                        {"rva": rva, "length": length} for rva, length in regions],
                        "sha256": expected, "hash_order": "concatenate listed regions in order"},
                    "finding": finding,
                })
        finally:
            pe.close()

    managed_by_source: dict[str, list[tuple[Any, ...]]] = {}
    for pin in SECURITY_MANAGED:
        managed_by_source.setdefault(pin[0], []).append(pin)
    for source_sha, pins in managed_by_source.items():
        inspected = inspect_managed_bodies(paths[source_sha])
        if inspected["source_sha256"] != source_sha:
            raise ValueError(f"security managed source drift: {source_sha}")
        materialization[source_ids[source_sha]] = {key: inspected[key] for key in (
            "assembly_name", "source_sha256", "module_mvid", "classification_counts",
            "method_def_count", "method_body_rva_count", "method_body_materialized_count",
        )}
        methods = {int(row["methoddef_token"], 16): row for row in inspected["methods"]}
        for _, token, rva, size, expected, signature, finding in pins:
            row = methods[token]
            body = row.get("body")
            if row["implementation"] != "il" or body is None:
                raise ValueError(f"security expected complete IL: {source_sha}:{token:#x}")
            if (body["sha256"] != expected or
                    (rva is not None and row["rva"] != rva) or
                    (size is not None and body["size"] != size) or
                    (signature is not None and row["signature_hex"] != signature)):
                raise ValueError(f"security managed body drift: {source_sha}:{token:#x}")
            evidence.append({
                "id": f"security.il.{source_sha[:12]}.{token:08x}",
                "source": source_ids[source_sha], "kind": "managed-il",
                "locator": {"methoddef_token": row["methoddef_token"],
                    "identity": row["identity"], "owner_identity": row["owner_identity"],
                    "type": row["full_nested_name"], "method": row["name"],
                    "signature_hex": row["signature_hex"], "rva": row["rva"],
                    "body_size": body["size"], "body_sha256": expected,
                    "offset_base": "ECMA-335 method header; includes extra/EH sections"},
                "finding": finding,
            })
    matrix = copy.deepcopy(SECURITY_CONTRACT_MATRIX)
    matrix["source_instance_ids"] = instance_ids
    matrix["proof_policy"] = (
        "Shared evidence is emitted once and referenced by declared proof sets. "
        "Every source is exact-SHA pinned; recovered inputs require their existing "
        "component manifest and installed protected pair. Managed bodies require "
        "complete valid IL; native regions are rehashed directly from those PEs. "
        "No runtime analysis inventory, saved project, bridge, target invocation "
        "or private-server response is an admission dependency."
    )
    return matrix


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _relative(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(REPO_ROOT.resolve()).as_posix() if resolved.is_relative_to(REPO_ROOT.resolve()) else str(resolved)


def _sources(roots: dict[str, Path]) -> list[dict[str, Any]]:
    records = []
    inputs = {spec["id"]: spec for spec in INPUTS}
    for spec in INPUTS:
        path = roots[spec["root"]] / spec["relative"]
        data = path.read_bytes()
        record = {k: copy.deepcopy(v) for k, v in spec.items()
                  if k not in ("root", "relative", "recovery")}
        record["path"] = _relative(path)
        if spec["root"] in ("recovered", "aux"):
            parents = [inputs[sid] for sid in spec["derived_from"]]
            stub = next(parent for parent in parents if not parent["relative"].endswith("._"))
            protected = roots[stub["root"]] / stub["relative"]
            record["recovery"] = qualify_recovered_source(
                path, protected, component_root=roots[spec["root"]])
            record.update(sha256=_digest(data), size=len(data), representation="manifest-qualified recovered PE")
        elif len(data) != spec["size"] or _digest(data) != spec["sha256"]:
            raise ValueError(f"source drift: {spec['id']}")
        records.append(record)
    return records


def _section(text: str, marker: str) -> str:
    if ".prototype." not in marker:
        return text
    start = text.index(marker)
    following = re.search(
        r"[A-Za-z_$][A-Za-z0-9_$]*\.prototype\.[A-Za-z0-9_$]+\s*=\s*function",
        text[start + len(marker):],
    )
    end = start + len(marker) + following.start() if following else len(text)
    return text[start:end]


def build(
    installed_root: Path = DEFAULT_ROOT,
    recovered_root: Path = DEFAULT_MAIN,
    aux_root: Path = DEFAULT_AUX,
    cuw_root: Path = DEFAULT_CUW,
) -> dict[str, Any]:
    roots = {"installed": Path(installed_root), "recovered": Path(recovered_root),
             "aux": Path(aux_root), "cuw": Path(cuw_root)}
    sources = _sources(roots)
    evidence: list[dict[str, Any]] = copy.deepcopy(STATIC_EVIDENCE)
    proof = {}
    assemblies = {}
    try:
        for name, relative in ASSEMBLIES.items():
            path = roots["recovered"] / relative
            proof[name] = validate_managed_bodies(path)
            assemblies[name] = _open(path)
        for spec in MANAGED:
            pe = assemblies[spec["assembly"]]
            rows = _method_rows(pe, spec["type"], spec["method"])
            row = rows[spec["index"]]
            body = _body(pe, row)
            pin = _method_pin(row, body)
            if any(pin[key] != spec[key] for key in ("rva", "body_size", "body_sha256")):
                raise ValueError(f"managed body drift: {spec['id']}")
            evidence.append({
                "id": spec["id"],
                "source": "auth_settings." + spec["assembly"].replace(".", "_"),
                "kind": "managed-il",
                "locator": {
                    "type": spec["type"], "method": spec["method"], "overload": spec["index"],
                    "offset_base": "method header; includes tiny/fat header bytes", **pin,
                },
                "anchors": spec["anchors"], "finding": spec["finding"],
            })
        evidence.extend(_desktop_evidence(assemblies, roots))
        evidence.extend(_service_managed_evidence(assemblies))
    finally:
        for pe in assemblies.values():
            pe.close()
    for spec in NATIVE:
        source = next(x for x in INPUTS if x["id"] == spec["source"])
        pe = pefile.PE(str(roots[source["root"]] / source["relative"]))
        try:
            data = pe.get_data(spec["locator"]["rva"], spec["locator"]["length"])
            if _digest(data) != spec["sha256"]:
                raise ValueError(f"native byte drift: {spec['id']}")
            for instruction in spec["decisive_instructions"]:
                raw = bytes.fromhex(instruction["bytes"])
                rva = int(instruction["va"], 16) - int(pe.OPTIONAL_HEADER.ImageBase)
                if pe.get_data(rva, len(raw)) != raw:
                    raise ValueError(f"decisive instruction drift: {spec['id']}")
        finally:
            pe.close()
        evidence.append(copy.deepcopy(spec))
    aux = roots["aux"] / "ContentServer"
    assets = decode_gui(
        roots["installed"] / "GTSPlusGUI/gts.gui", aux / "GtsPlus-CM.dll",
        aux / "CryptgraphResource.dll", aux / "CryptgraphCommon.dll",
        roots["installed"] / "ContentServer/dist.crt",
    )
    asset_ids = {}
    for spec in JAVASCRIPT:
        data = assets[spec["asset"]]
        text = data.decode("utf-8")
        segment = _section(text, spec["locator"])
        if _digest(data) != spec["sha256"] or _digest(segment.encode()) != spec["segment_sha256"]:
            raise ValueError(f"signed frontend drift: {spec['id']}")
        if not all(needle in segment for needle in spec["anchors"]):
            raise ValueError(f"frontend branch anchor drift: {spec['id']}")
        if spec["asset"] not in asset_ids:
            sid = "auth_settings.asset_" + spec["asset"].split("/")[-1].replace(".", "_")
            asset_ids[spec["asset"]] = sid
            sources.append({
                "id": sid, "path": _relative(roots["installed"] / "GTSPlusGUI/gts.gui"),
                "sha256": spec["sha256"], "size": len(data),
                "representation": "authenticated decoded ZIP member", "member": spec["asset"],
                "derived_from": ["auth_settings.gts_gui", "auth_settings.gts_cpf",
                                 "auth_settings.decoder_CryptgraphResource_dll",
                                 "auth_settings.decoder_CryptgraphCommon_dll",
                                 "auth_settings.decoder_GtsPlus-CM_dll", "auth_settings.dist_crt"],
                "recovery": "gtsplus_local_crypto.decode_gui; ZIP SHA256 then RSA verification as shipped",
            })
        evidence.append({
            "id": spec["id"], "source": asset_ids[spec["asset"]], "kind": "signed-javascript",
            "locator": {"member": spec["asset"], "function": spec["locator"],
                        "segment_sha256": spec["segment_sha256"]},
            "anchors": spec["anchors"], "finding": spec["finding"],
        })
    dist = roots["installed"] / "GTSPlus/Env/DistDep.gstg"
    clear = decrypt_file(dist, roots["installed"] / "GTSPlus/Env/GTSPlus.pp", aux / "GtsPlus-CM.dll", key_type=2)
    text = clear.decode("utf-8-sig").rstrip("\x00")
    scalars = {}
    for key, expected in POLICY_SCALARS.items():
        match = re.search(r"^" + key + r":\s*([^\r\n#]*)", text, re.M)
        value = match.group(1).strip().strip('"') if match else None
        if value != expected:
            raise ValueError(f"allowlisted distributor policy drift: {key}")
        scalars[key] = value
    evidence.append({
        "id": "auth_settings.distributor_policy", "source": "auth_settings.DistDep_gstg",
        "kind": "decrypted-config-allowlist", "locator": "top-level YAML policy scalars",
        "plaintext_sha256": _digest(clear), "values": scalars,
        "finding": "Installed NA distributor policy: region1,30-day offline/profile retention,10-minute clock tolerance,7-day license refresh,60-second clock cycle; normal logout server API disabled. Empty licenseTypeValue is the actual comparison input, not a wildcard assertion.",
    })
    service_contract_matrix = _service_surface(assets, roots, sources, evidence)
    security_contract_matrix = _security_domain(roots, sources, evidence, proof)
    return {
        "schema": "gtsplus-lifecycle-domain-v1", "domain": "auth_settings",
        "sources": sources, "evidence": evidence, "states": copy.deepcopy(STATES),
        "transitions": copy.deepcopy(TRANSITIONS), "handoffs": copy.deepcopy(HANDOFFS),
        "persistence": copy.deepcopy(PERSISTENCE),
        "coverage": {
            "components": sorted(ASSEMBLIES) + ["GTSPlusSettingFileManager.dll", "GTSPlusFileCryptographic.dll", "GtsPlus-LV.dll", "signed GTS GUI login/user/PC settings and non-login service producers", "current source-qualified Security algorithms and explicitly typed native/managed providers"],
            "entrypoints": [x["type"] + "::" + x["method"] for x in MANAGED + SERVICE_MANAGED] + [x["locator"] for x in JAVASCRIPT] + [x["function"] for x in service_contract_matrix["frontend_producers"]],
            "branches": [x["guard"] for x in TRANSITIONS],
            "security_contract_ids": [row["id"] for row in security_contract_matrix["contracts"]],
        },
        "materialization": proof,
        "service_contract_matrix": service_contract_matrix,
        "security_contract_matrix": security_contract_matrix,
        "license_status": {"0": "valid", "-1": "invalid/absent offline artifacts", "-2": "expired beyond tolerance", "-3": "offline-use window expired", "-4": "local read/clock/parse/native verification error"},
        "residuals": copy.deepcopy(RESIDUALS),
        "execution_scope": "Offline parsing, signed-package/config decode and static executable evidence only; no target DLL invocation,network,vehicle,credential use.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--recovered-root", type=Path, default=DEFAULT_MAIN)
    parser.add_argument("--aux-root", type=Path, default=DEFAULT_AUX)
    parser.add_argument("--cuw-root", type=Path, default=DEFAULT_CUW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build(args.installed_root, args.recovered_root, args.aux_root, args.cuw_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{_relative(args.output)}: {len(artifact['evidence'])} evidence records")


if __name__ == "__main__":
    main()
