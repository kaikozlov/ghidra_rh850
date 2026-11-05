#!/usr/bin/env python3
"""Shared decoders for Toyota Calibration Update Wizard parameter files."""
from __future__ import annotations

import csv
import hashlib
import io
import re
from pathlib import Path
from typing import Any

from tools.techstream.cuw_attach import current_profile_int

_KEY = "ParamFileKeySystemProtocolMicon"
_DLL_FLAG = "FlagToUseCIDGetterAndFlashWriterDLL"
_SPECIAL_CONTACTS = ("P5-Unified", "Phase6", "Ethernet")
_CURRENT_VERSIONS = frozenset((2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 40, 101, 103, 104, 105, 106, 107, 206, 209, 300, 400, 500))


def decode_parameter_ini(data: bytes) -> bytes:
    """Decode the CUW parameter-INI nibble transform recovered from Techstream.

    The transform is derived from TCUWParameterForVC.dll RVA 0x10001000 and is
    shared by deterministic writer generators and the interactive GTS+ query
    surface.
    """
    if len(data) % 2:
        raise ValueError("encoded CUW parameter file has odd length")
    decoded = bytes(
        (((((a & 0xF) >> 2) + (a >> 4) * 4) * 4 + (b >> 4) + 0x1E) * 4 + ((b & 0xF) >> 2)) & 0xFF
        for a, b in zip(data[::2], data[1::2])
    )
    return decoded.rstrip(b"\xff")


def _parameter_documents(ini_root: Path, *, current: bool) -> list[dict[str, Any]]:
    documents = []
    for path in sorted(ini_root.glob("*.ini"), key=lambda p: p.name.lower()):
        document: dict[str, Any] = {"parameter_file": path.name, "readable": False}
        try:
            encoded = path.read_bytes()
        except OSError:
            if not current:
                raise
            documents.append(document)
            continue
        document.update(readable=True, encoded_sha256=hashlib.sha256(encoded).hexdigest())
        try:
            decoded = decode_parameter_ini(encoded)
            rows = list(csv.reader(io.StringIO(decoded.decode("latin1"))))
        except (ValueError, UnicodeError, csv.Error):
            documents.append(document)
            continue
        document.update(decoded_sha256=hashlib.sha256(decoded).hexdigest(), rows=rows)
        documents.append(document)
    return documents


def _declared_factory_rows(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    routes = []
    fields = {
        "cid_getter": "DLLFileNameForGetCID",
        "prepare_writer": "DLLFileNameForPrepareWrite",
        "flash_writer": "DLLFileNameForFlashWrite",
        "get_can_id_cid": "GetCANIDFunctionNameForGetCID",
        "get_can_id_prepare": "GetCANIDFunctionNameForPrepareWrite",
        "get_can_id_flash": "GetCANIDFunctionNameForFlashWrite",
        "version_contract": "EnableDLLVersionInformation",
        "prepare_retry": "PrepareRetryFlag",
    }
    for document in documents:
        rows = document.get("rows", [])
        if len(rows) < 2 or "DLLFileNameForPrepareWrite" not in rows[0]:
            continue
        for row_index, raw_row in enumerate(rows[1:], 1):
            item = dict(zip(rows[0], raw_row + [""] * (len(rows[0]) - len(raw_row))))
            routes.append({
                **{key: document[key] for key in ("parameter_file", "encoded_sha256", "decoded_sha256")},
                "row_index": row_index,
                "factory_identifier": item.get(_KEY, ""),
                **{key: item.get(column, "") for key, column in fields.items()},
                "raw": item,
            })
    routes.sort(key=lambda item: (item["factory_identifier"], item["parameter_file"], item["row_index"]))
    return routes


def _parameter_bool(value: str) -> bool | None:
    # CParameter strtol differs from the profile's catch-to-default conversion.
    first = value.split("\n", 1)[0]
    match = re.match(r"^[ \t\r\n\v\f]*([+-]?[0-9]+)", first)
    if match is None:
        return False if not first else None
    return any(character != "0" for character in match[1].lstrip("+-"))


def _master_records(documents: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    records: dict[str, list[dict[str, Any]]] = {}
    for document in documents:
        if document["parameter_file"] != "Parameter.ini":
            continue
        rows = document.get("rows", [])
        if not rows or _KEY not in rows[0]:
            continue
        for index, cells in enumerate(rows[1:], 1):
            raw = dict(zip(rows[0], cells))
            key = raw.get(_KEY, "").split("\n", 1)[0]
            records.setdefault(key, []).append({
                "parameter_file": document["parameter_file"],
                "encoded_sha256": document["encoded_sha256"],
                "decoded_sha256": document["decoded_sha256"],
                "row_index": index, "raw": raw,
                "dll_flag": _parameter_bool(raw[_DLL_FLAG]) if _DLL_FLAG in raw else None,
            })
    return records


def _current_factory_rows(
    documents: list[dict[str, Any]], routes: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if routes is None:
        routes = _declared_factory_rows(documents)
    masters = _master_records(documents)
    declared = {row["factory_identifier"] for row in routes}
    for selector in masters:
        if selector not in declared:
            routes.append({
                "factory_identifier": selector, "parameter_file": None,
                "encoded_sha256": None, "decoded_sha256": None, "row_index": None,
                "cid_getter": "", "prepare_writer": "", "flash_writer": "",
                "get_can_id_cid": "", "get_can_id_prepare": "", "get_can_id_flash": "",
                "version_contract": "", "prepare_retry": "", "raw": {},
            })
    readable = {document["parameter_file"] for document in documents if document["readable"]}
    for row in routes:
        selector = row["factory_identifier"]
        occurrences = masters.get(selector, [])
        flag = occurrences[0]["dll_flag"] if occurrences else None
        row.update(
            selector=selector,
            factory_declared=row["parameter_file"] is not None,
            master_occurrences=occurrences,
            engine_selection={
                "special_contact_types": list(_SPECIAL_CONTACTS),
                "special_contact_engine": "phase",
                "ordinary_contact_own_ini": selector + ".ini",
                "own_ini_present_and_readable_offline": selector + ".ini" in readable,
                "own_ini_open_success_engine": "phase",
                "own_ini_open_failure": "legacy" if flag is False else
                    ("CPassThruException:9999" if flag is True else "throw-int:2"),
                "master_lookup": "first exact row; consulted only after ordinary-contact open failure",
                "scope": "conditional source contract, not an observed vehicle selection",
            },
        )
    return sorted(routes, key=lambda row: (row["selector"], row["parameter_file"] or "", row["row_index"] or 0))


def factory_routes_from_ini_root(
    ini_root: Path, *, current: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Read declarations; current mode includes master-only conditional selectors.

    The default preserves V18 generator rows/statistics. Current mode preserves
    raw occurrences and exact first-master lookup, without splitting selector
    text into guessed Kind/Contact/CPU values.
    """
    documents = _parameter_documents(ini_root, current=current)
    declared = _declared_factory_rows(documents)
    statistics = {"encoded_ini_files_decoded": sum("rows" in doc for doc in documents),
                  "factory_rows": len(declared)}
    if not current:
        return declared, statistics
    routes = _current_factory_rows(documents, declared)
    statistics.update(selector_rows=len(routes),
                      master_rows=sum(len(rows) for rows in _master_records(documents).values()))
    return routes, statistics


_OLD_KINDS = {
    "ENG & ECT": "0", "HV": "1", "THS": "2", "MG": "3", "VSC/ABS/ECB": "4",
    "FC": "5", "FCHV": "6", "EPB": "7", "PRL": "8", "ENG2": "9",
    "HV Battery": "10", "DCM(Telematics)": "11", "ASG": "12", "EMPS": "13",
    "VGRS": "14", "ARS": "15", "Plug-in Control": "16", "ENG(DH)": "17",
    "ECT(DH)": "18", "ECT": "10000", "ENG": "10001",
}
_OLD_CPUS = {
    "32B 192K": "0", "32B 256K": "1", "32B 320K": "2", "32B 384K": "3",
    "32BH 384K": "4", "32BH 512K": "5", "32BH 768K": "6", "32BL 384K": "7",
    "TX2": "8", "MPC565": "10", "PG2": "11", "32BHs 384K": "12",
    "32BHs 512K": "13", "32BHs 768K": "14", "FOREST-1": "15", "FOREST-2": "16",
    "M16C/26T": "17", "M16C/29T 96K": "18", "M16C/29T 120K(Plug-in)": "19",
    "ST10F275": "20", "32BHF": "21", "B32R-V85 512K": "22", "32B-C2 256K": "23",
    "32B-C2 512K": "24", "32B-C2 768K": "25", "TC1766": "26", "PEC1 384K": "27",
    "SH72512": "28", "PIC16F877A": "29", "PEC2 512K": "30", "Denso DCM": "31",
    "Delphi DCM/HOST": "32", "Delphi DCM/DSP": "33", "Delphi DCM/PIC": "34",
    "SH72264": "35", "SH72265": "36", "SH7142": "37", "APEC0M": "38",
    "WEGA 768K": "39", "GP8": "40", "V850ES(CCP) 256K": "41", "PACE1T 384K": "42",
    "M32C/85 320K": "43", "V850E/GP2 384K": "44", "V850E/GP8 512K": "45",
    "F2171-97207 384K": "46", "M32R 512K": "47", "PRL": "48", "MPC565CAN": "10",
}


def _native_decimal_pair(value: int) -> str:
    """The native parsers write quotient/remainder bytes, not a printf width."""
    return bytes(((48 + value // 10) & 255, 48 + value % 10)).decode("latin1").split("\0", 1)[0]


def _logical_cid_scan(
    descriptor: dict[str, dict[str, str]], node_index: int, declared_count: int,
) -> tuple[list[str], int]:
    """Both native scans use the node ones digit and IDs01..32; stop after admission."""
    unique = []
    admitted = 0
    for logical_index in range(1, 33):
        section = f"LogicalBlock{(node_index + 1) % 10}{logical_index:02d}"
        cid = descriptor.get(section, {}).get("NewCID", "")
        if not cid:
            continue
        admitted += 1
        if cid not in unique:
            unique.append(cid)
        if admitted == declared_count:
            break
    return unique, admitted


def _descriptor_selector_model(descriptor: dict[str, dict[str, str]]) -> dict[str, Any]:
    """Project exact constructor states; do not sanitize native unsafe counts."""
    def boundary(detail: str, **state: Any) -> dict[str, Any]:
        return {"error": {"stage": "native-model-boundary", "native_unsafe": True,
                          "detail": detail, **state}}

    version = current_profile_int(descriptor.get("Format", {}).get("Version", ""))
    if version not in _CURRENT_VERSIONS:
        return {"error": {"stage": "descriptor-version", "native_result_code": 1001,
                          "version": version}}
    vehicle = descriptor.get("Vehicle", {})
    kind = vehicle.get("KindOfECU", "")
    contact = vehicle.get("ContactType", "")
    cpus: list[dict[str, Any]] = []
    nodes: list[dict[str, str]] = []
    try:
        if version in (2, 3):
            kind = _OLD_KINDS[kind]
        if version >= 101:
            count = current_profile_int(vehicle.get("NumberOfNode", ""))
            if count <= 0 or count * 0xF8 > 0xFFFFFFFB:
                return boundary("native node allocation/indexing has no projectable constructor state",
                                declared_nodes=count)
            prepass_total = 0
            materialized_counts = []
            for node_index in range(count):
                # d6e0 changes only the ones byte of its independent Node0n literal.
                prepass_section = f"Node0{(node_index + 1) % 10}"
                prepass = descriptor.get(prepass_section, {})
                allocated = current_profile_int(prepass.get("NumberOfCalibration", ""))
                if allocated < 0:
                    return boundary("negative CPU count is added by the native allocation prepass, not clamped",
                                    node_index=node_index, prepass_section=prepass_section,
                                    declared_cpus=allocated)
                if allocated == 0:
                    unique, _ = _logical_cid_scan(descriptor, node_index,
                        current_profile_int(prepass.get("NumberOfLogicalBlock", "")))
                    allocated = len(unique)
                prepass_total += allocated
                if prepass_total * 0x9324 > 0xFFFFFFFB:
                    return boundary("native CPU allocation size/count overflows its 32-bit representation",
                                    allocation_prepass_cpus=prepass_total)
                # 6370 writes BOTH quotient and remainder into its Node01 literal.
                section = "Node" + _native_decimal_pair(node_index + 1)
                node = descriptor.get(section, {})
                nodes.append({key: node.get(key, "") for key in
                              ("Protocol", "RequiredSpecReproVer", "DiagID", "LogicalAddress")})
                if node.get("RequiredSpecReproVer", "") in ("03", "04", "01"):
                    declared = current_profile_int(node.get("NumberOfLogicalBlock", ""))
                    if declared < 0 or declared * 0x70C > 0xFFFFFFFB:
                        return boundary("native logical-record allocation casts the signed declaration to unsigned",
                                        node_index=node_index, declared_logical_blocks=declared)
                    unique, admitted = _logical_cid_scan(descriptor, node_index, declared)
                    if declared == 0 and admitted:
                        return boundary("native logical scan writes admitted records into a zero-sized allocation",
                                        node_index=node_index, admitted_logical_blocks=admitted)
                    if admitted != declared:
                        return boundary("declared logical-record count and admitted constructor records diverge",
                                        node_index=node_index, declared_logical_blocks=declared,
                                        admitted_logical_blocks=admitted)
                    materialized = len(unique)
                else:
                    materialized = current_profile_int(node.get("NumberOfCalibration", ""))
                    if materialized < 0:
                        return boundary("negative main-node CPU count has no safe materialized selector context",
                                        node_index=node_index, node_section=section,
                                        declared_cpus=materialized)
                materialized_counts.append(materialized)
            materialized_total = sum(materialized_counts)
            if prepass_total != materialized_total:
                return boundary("allocation prepass and main-parser CPU materialization diverge",
                                allocation_prepass_cpus=prepass_total,
                                materialized_cpus=materialized_total)
            for node_index, cpu_count in enumerate(materialized_counts):
                first_cpu = len(cpus)
                cpus.extend({"cpu_index": first_cpu + index, "cpu_type": "", "node_index": node_index}
                            for index in range(cpu_count))
        else:
            count = current_profile_int(vehicle.get("NumberOfCalibration", ""))
            if count < 0 or count * 0x9324 > 0xFFFFFFFB:
                return boundary("native classic CPU allocation has an unsafe signed count/size", declared_cpus=count)
            for index in range(count):
                fields = descriptor.get("CPU" + _native_decimal_pair(index + 1), {})
                if version in (10, 12):
                    cpu_type = ""
                elif version in (2, 3):
                    cpu_type = _OLD_CPUS[fields.get("ECUType", "")]
                    if cpu_type == "10" and contact == "SIL":
                        cpu_type = "9"
                else:
                    cpu_type = fields.get("CPUType", "")
                cpus.append({"cpu_index": index, "cpu_type": cpu_type, "node_index": None})
    except KeyError as error:
        return {"error": {"stage": "legacy-descriptor-checked-map",
                          "native_exception": "std::out_of_range", "unmapped_value": error.args[0]}}
    if not cpus:
        return boundary("factory dereferences CPU0; no CPU0 was declared/materialized")
    return {"descriptor_version": version, "kind_of_ecu": kind, "contact_type": contact,
            "cpus": cpus, "nodes": nodes}


def _selected_parameter(
    documents: dict[str, dict[str, Any]], selector: str,
) -> dict[str, Any]:
    """Load the exact requested file, then first exact selected row (no alias scan)."""
    filename = selector + ".ini"
    document = documents.get(filename)
    result: dict[str, Any] = {"selector": selector, "parameter_file": filename}
    if document is None or not document["readable"]:
        return {**result, "error": {"stage": "LoadParameter", "native_error": 9999}}
    rows = document.get("rows", [])
    if (not rows or _KEY not in rows[0] or any(len(row) != len(rows[0]) for row in rows[1:])):
        return {**result, "error": {"stage": "LoadParameter", "native_error": 9999}}
    column = rows[0].index(_KEY)
    for index, cells in enumerate(rows[1:], 1):
        if cells[column].split("\n", 1)[0] == selector:
            return {**result, "row_index": index, "raw": dict(zip(rows[0], cells)),
                    "encoded_sha256": document["encoded_sha256"],
                    "decoded_sha256": document["decoded_sha256"]}
    return {**result, "error": {"stage": "SetKeys", "native_error": 9999}}


def select_factory_routes_for_descriptor(
    ini_root: Path, descriptor: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Explain current native dispatch for descriptor-derived contexts.

    No current CPU, ignition state, completed-node bitmap, successful module load,
    or live vehicle selection is synthesized. Per-CPU role contexts are conditional
    on the native worker reaching that CPU. Files are not selected by scanning for
    a matching header in a differently named INI.
    """
    model = _descriptor_selector_model(descriptor)
    result: dict[str, Any] = {
        "schema": "gts-current-cuw-selection-v1", "model": model, "routes": [], "roles": [],
        "scope": "descriptor-derived factory contexts; native admission and execution not performed",
    }
    if "error" in model:
        return result
    documents = _parameter_documents(ini_root, current=True)
    by_filename = {document["parameter_file"]: document for document in documents}
    inventory = _current_factory_rows(documents)
    kind, contact = model["kind_of_ecu"], model["contact_type"]
    cpu0 = model["cpus"][0]["cpu_type"]
    entry_selector = kind + contact + cpu0
    master = _master_records(documents).get(entry_selector, [])
    own_document = by_filename.get(entry_selector + ".ini")
    if contact in _SPECIAL_CONTACTS:
        engine, reason = "phase", "exact special ContactType; no own-file probe/master flag"
    elif own_document is not None and own_document["readable"]:
        engine, reason = "phase", "ordinary-contact own INI open succeeds; master flag ignored"
    elif master and master[0]["dll_flag"] is False:
        engine, reason = "legacy", "own INI open fails; first exact master bool is false"
    else:
        engine = "error"
        reason = "CPassThruException:9999" if master and master[0]["dll_flag"] is True else "throw-int:2"
    result["engine"] = {
        "name": engine, "reason": reason, "selector": entry_selector,
        "own_ini_file": entry_selector + ".ini", "master_occurrences": master,
        "dll": "TCUWControlCommPhase.dll" if engine == "phase" else
            ("TCUWLegacyCIDGettersAndFlashWriters.dll" if engine == "legacy" else None),
    }
    if engine != "phase":
        result["routes"] = [row for row in inventory if row["selector"] == entry_selector]
        return result

    def bind(role: str, selector: str, *, cpu_index: int | None = None,
             address_selector: str | None = None, node_index: int | None = None) -> None:
        parameter = _selected_parameter(by_filename, selector)
        binding: dict[str, Any] = {"role": role, "cpu_index": cpu_index, "node_index": node_index,
                                   "parameter": parameter}
        if address_selector is not None:
            binding["address_parameter"] = _selected_parameter(by_filename, address_selector)
        columns = {"cid": "DLLFileNameForGetCID", "prepare": "DLLFileNameForPrepareWrite",
                   "flash": "DLLFileNameForFlashWrite",
                   "gateway": "DLLFileNameForChangeToReprogGatewayMode"}
        if "raw" in parameter:
            raw = parameter["raw"]
            binding["dll"] = raw.get(columns[role], "").split("\n", 1)[0]
            binding["version_minima"] = raw.get("EnableDLLVersionInformation", "").split("\n")
            binding["version_rule"] = "exactly four entries; unsigned-byte lexical >= minimum[phase]"
            if role == "cid":
                binding["alternate_getters"] = raw.get("AlternateDLLFileNamesForGetCID", "").split("\n")
                binding["alternate_gate"] = "primary vector empty only, not primary false/nonempty"
        result["roles"].append(binding)

    protocol0 = model["nodes"][0].get("Protocol", "") if model["nodes"] else ""
    bind("cid", kind + contact + protocol0 + cpu0)
    node_route = contact in _SPECIAL_CONTACTS
    for cpu in model["cpus"]:
        index, cpu_type, node_index = cpu["cpu_index"], cpu["cpu_type"], cpu["node_index"]
        if node_route:
            if node_index is None or not 0 <= node_index < len(model["nodes"]):
                result.setdefault("role_preconditions", []).append({
                    "cpu_index": index, "roles": ["prepare", "flash"],
                    "stage": "native-node-access",
                    "detail": "CPU has no declared node index; no empty-node selector is synthesized",
                })
                continue
            node = model["nodes"][node_index]
            required = node.get("RequiredSpecReproVer", "")
            discriminator = "" if required == "02" else (
                node.get("Protocol", "") if contact == "Phase6" else required)
            selector = kind + contact + discriminator + cpu0
            bind("prepare", selector, cpu_index=index, node_index=node_index)
            bind("flash", selector, cpu_index=index, node_index=node_index)
        else:
            selector = kind + contact + cpu_type
            bind("prepare", entry_selector, cpu_index=index, address_selector=selector)
            bind("flash", selector, cpu_index=index)
    if not node_route:
        bind("gateway", entry_selector)
    requested = {binding["parameter"]["selector"] for binding in result["roles"]}
    requested.update(binding["address_parameter"]["selector"] for binding in result["roles"]
                     if "address_parameter" in binding)
    result["routes"] = [
        {**row, "selected_for": [
            {"role": binding["role"], "cpu_index": binding["cpu_index"],
             "node_index": binding["node_index"]}
            for binding in result["roles"]
            if binding["parameter"]["selector"] == row["selector"]
            and binding["parameter"].get("row_index") == row["row_index"]
            and binding["parameter"]["parameter_file"] == row["parameter_file"]
        ]}
        for row in inventory if row["selector"] in requested
        and any(binding["parameter"].get("row_index") == row["row_index"]
                and binding["parameter"]["parameter_file"] == row["parameter_file"]
                for binding in result["roles"])
    ]
    return result
