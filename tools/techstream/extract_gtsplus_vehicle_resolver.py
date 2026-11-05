#!/usr/bin/env python3
"""Extract current GTS+ vehicle/profile and P5 capability resolver semantics.

This is the Toyota decision layer above individual diagnostic commands:

* CSelectCarTypeVin10 joins live communication identity/VIN with master
  CDbVehicleDecisionTable / CDbVinVehicleDecisionTable rows;
* current main DV000004 enumerates install candidates through role 121/mode 0,
  then conditionally resolves specific ECU aliases; DV000005 checks one ECU;
* GetSupportP5 exposes Toyota's PID/DID/RID support resolver.  The current P5
  DID path uses a two-level MSB-first support bitmap rooted at 22 01 01.

The artifact retains source-qualified raw master rows separately from explicit
initial native query witnesses. It contains no executable function bodies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import pefile
from tools.techstream.ddb_semantics import (
    NativeSelectionError, UnresolvedNativeContext, native_context, records, select_for_consumer,
)
from tools.techstream.extract_gtsplus_p6_data_list import native_failure
from tools.techstream.ddb_strings import load_string_db
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT, qualify_recovered_source
from tools.techstream.techstream_paths import gts_db_root, resolve_gts_root
from tools import REPO_ROOT


DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/vehicle_resolver_semantics.json"
DEFAULT_RECOVERED = DEFAULT_OUTPUT / "GTSPlus"
REGIONS = ("NA", "EU", "JP")

# Current KgpDataCtrl master-table class ids used by SelectCarTypeVin10.
VEHICLE_DECISION_CLASS = 0x129
VIN_VEHICLE_DECISION_CLASS = 0x13B
VEHICLE_DECISION_TYPE = 41
VIN_VEHICLE_DECISION_TYPE = 59
INSTALLING_ECU_LIST_TYPE = 44
PROTOCOL_INFO_TYPE = 13
PROTOCOL_INFO_CLASS = 0x10D
COMM_FRAME_TYPE = 17
COMM_SET_TYPE = 29
COMM_FRAME_CLASS = 0x111
ECU_CATEGORY_CLASS = 0x110

# Current P5 generic DID-support root.  CCmdSupportDataIdList mutates bytes 1:3
# to each supported xx00 group for the second-level request.
P5_DID_SUPPORT_SELECTOR = 0xC8
P5_DID_SUPPORT_REQUEST = bytes.fromhex("220101")
P5_DID_SUPPORT_POSITIVE = 0x62
P5_ROUTINE_SUPPORT_SELECTOR = 0xCC
P5_ROUTINE_SUPPORT_REQUEST = bytes.fromhex("31011001")
P5_ROUTINE_SUPPORT_POSITIVE = 0x71


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source(path: Path, root: Path | None = None, *, display: str | None = None) -> dict[str, Any]:
    display_path = str(path) if display is None else display
    if root is not None and display is None:
        try:
            display_path = str(path.relative_to(root)).replace("\\", "/")
        except ValueError:
            pass
    return {"path": display_path, "size": path.stat().st_size, "sha256": sha256_file(path)}


def u16(raw: bytes, off: int) -> int:
    return struct.unpack_from("<H", raw, off)[0]


def u32(raw: bytes, off: int) -> int:
    return struct.unpack_from("<I", raw, off)[0]


def exports(path: Path) -> dict[str, int]:
    pe = pefile.PE(str(path), fast_load=False)
    base = int(pe.OPTIONAL_HEADER.ImageBase)
    return {
        (sym.name or b"").decode(errors="replace"): base + int(sym.address)
        for sym in pe.DIRECTORY_ENTRY_EXPORT.symbols
        if sym.name
    }


def export_addr(path: Path, contains: str) -> int:
    matches = [(name, addr) for name, addr in exports(path).items() if contains in name]
    if len(matches) != 1:
        raise ValueError(f"{path.name}: expected one export containing {contains!r}, got {matches!r}")
    return matches[0][1]


def va_bytes(path: Path, va: int, size: int) -> bytes:
    pe = pefile.PE(str(path), fast_load=False)
    rva = va - int(pe.OPTIONAL_HEADER.ImageBase)
    offset = pe.get_offset_from_rva(rva)
    return path.read_bytes()[offset : offset + size]


def analyze_support_bitmap(base: int, bitmap: bytes, shift: int) -> list[int]:
    """Express CCmdSupportDataIdList::AnalyzeFrameData exactly.

    Bits are consumed MSB first.  shift=8 expands the root response into xx00
    group IDs.  shift=0 expands one group into xx01..xxFF and deliberately
    skips byte31 bit7, which would alias the following group's xx00 ID.
    """
    out: list[int] = []
    for byte_index, value in enumerate(bitmap[:32]):
        for bit_index in range(8):
            mask = 0x80 >> bit_index
            if not value & mask:
                continue
            if shift:
                out.append((base + ((byte_index * 8 + bit_index) << shift)) & 0xFFFF)
            else:
                if byte_index == 31 and bit_index == 7:
                    continue
                out.append((base + 1 + byte_index * 8 + bit_index) & 0xFFFF)
    return out


def vin_decision_matches(raw: bytes, category_id: int, route_selector: int, vin11: bytes) -> bool:
    """Express current CDbVinVehicleDecisionTable::DecisionKey."""
    if len(raw) != 32:
        raise ValueError(f"VIN decision record must be 32 bytes, got {len(raw)}")
    if len(vin11) != 11:
        raise ValueError("VIN decision key requires exactly VIN[0:11]")
    if u16(raw, 0x10) != category_id or raw[0x12] != route_selector:
        return False
    flags = u32(raw, 0x00)
    return all((flags & (1 << index)) or raw[0x13 + index] == vin11[index] for index in range(11))


def vin_decision_rows(master: Any, category_id: int, route_selector: int, vin11: bytes) -> list[bytes]:
    return [raw for raw in records(master.sections[VIN_VEHICLE_DECISION_TYPE])
            if vin_decision_matches(raw, category_id, route_selector, vin11)]


def _vehicle_names(parser: DDBParser, master: Any, strings: Any) -> dict[int, str]:
    return {u16(raw, 0x04): strings.get_string(u32(raw, 0x00)) or ""
            for raw in records(master.sections[43])}


def _install_sets(master: Any) -> dict[int, list[int]]:
    out: dict[int, set[int]] = {}
    for raw in records(master.sections[5]):
        out.setdefault(u16(raw, 0x04), set()).add(u16(raw, 0x06))
    return {key: sorted(value) for key, value in out.items()}


def _set_categories(master: Any) -> dict[int, list[int]]:
    out: dict[int, set[int]] = {}
    for raw in records(master.sections[INSTALLING_ECU_LIST_TYPE]):
        out.setdefault(u16(raw, 0x04), set()).add(u16(raw, 0x06))
    return {key: sorted(value) for key, value in out.items()}


def _install_rows(master: Any, install_set_ids: set[int]) -> list[dict[str, int]]:
    """Consumer-proven GetMountEcuListNoCnfm fields from type-44 install rows."""
    out = []
    for raw in records(master.sections[INSTALLING_ECU_LIST_TYPE]):
        install_set_id = u16(raw, 0x04)
        if install_set_id not in install_set_ids:
            continue
        if len(raw) != 24:
            raise ValueError(f"install row size drift: {len(raw)}")
        out.append({
            "install_set_id": install_set_id,
            "category_id": u16(raw, 0x06),
            "connection_frame_id": u16(raw, 0x08),
            "connection_comm_set_id": u16(raw, 0x0A),
            "connection_route_selector": raw[0x13],
        })
    return sorted(out, key=lambda row: (row["install_set_id"], row["category_id"]))


def _protocol_route(master: Any, category_id: int, route_selector: int) -> dict[str, Any]:
    """Current CDbProtInfoTable route selected by CCommFrameCtrl::GetEcuAddr(category, route_selector).

    GetEcuAddr queries class 0x10D with category and the encoded route selector, then returns the u16
    record field at +0x08.  The current P5 frame builder independently consumes
    byte +0x0A from that selected row when constructing the category transport;
    for selector 0x22 Camry rows it is the logical-address extension that separates
    multiple categories sharing request CAN ID 0x750.
    """
    matches = [
        raw for raw in records(master.sections[PROTOCOL_INFO_TYPE])
        if u16(raw, 0x00) == category_id and raw[0x18] == route_selector
    ]
    if len(matches) != 1:
        raise ValueError(
            f"CDbProtInfo category {category_id} route selector 0x{route_selector:02X} resolved {len(matches)} rows"
        )
    raw = matches[0]
    if len(raw) != 28:
        raise ValueError(f"CDbProtInfo row size drift: {len(raw)}")
    return {
        "protocol_info_id": u16(raw, 0x02),
        "functional_address": u16(raw, 0x06),
        "request_address": u16(raw, 0x08),
        "address_extension": raw[0x0A],
        "request_mask": u16(raw, 0x0E),
        "response_mask": u16(raw, 0x10),
        "legislated_request_address": u16(raw, 0x14),
        "route_selector": raw[0x18],
    }


def _comm_frame_witness(context: Any, frame_id: int) -> dict[str, Any]:
    query = context.query(COMM_FRAME_TYPE, frame_id)
    witness: dict[str, Any] = {
        "query": query.as_dict(), "selected": None,
        "raw_occurrences": [row.as_dict() for row in context.raw_records(COMM_FRAME_TYPE)
                            if u16(row.raw, 0) == frame_id],
    }
    try:
        occurrence = select_for_consumer(query, "frame")
        raw = occurrence.raw
        witness["status"] = query.status
        witness["selected"] = {
            "frame_id": frame_id, "send_variable_id": u16(raw, 2),
            "receive_mask_variable_id": u16(raw, 4), "receive_check_variable_id": u16(raw, 6),
            "empty": raw == bytes(len(raw)), "occurrence": occurrence.as_dict(),
        }
    except (NativeSelectionError, UnresolvedNativeContext) as error:
        witness.update(native_failure(error))
    return witness


def _comm_set_witness(context: Any, comm_set_id: int) -> dict[str, Any]:
    query = context.query(COMM_SET_TYPE, comm_set_id)
    witness: dict[str, Any] = {
        "query": query.as_dict(), "selected": None,
        "raw_occurrences": [row.as_dict() for row in context.raw_records(COMM_SET_TYPE)
                            if u16(row.raw, 0x0A) == comm_set_id],
    }
    try:
        occurrence = select_for_consumer(query, "commset")
        raw = occurrence.raw
        witness["status"] = query.status
        witness["selected"] = {
            "comm_set_id": comm_set_id, "send_parameter": u32(raw, 0),
            "receive_timeout": u32(raw, 4), "retry_count": raw[0x0E],
            "exception_handler_id": u16(raw, 8), "exception_handler_flag": raw[0x0F],
            "occurrence": occurrence.as_dict(),
        }
    except (NativeSelectionError, UnresolvedNativeContext) as error:
        witness.update(native_failure(error))
    return witness


def _raw_master_tables(context: Any) -> dict[str, list[dict[str, Any]]]:
    """Store exact physical rows with their shared source and offset geometry."""
    tables: dict[str, list[dict[str, Any]]] = {}
    for table in (5, 13, 16, 17, 29, 41, 43, 44, 59):
        groups = []
        for family in ("Gen", "Spe"):
            rows = context.raw_records(table, family=family)
            if not rows:
                continue
            first = rows[0]
            size = len(first.raw)
            if any(row.ordinal != index or len(row.raw) != size
                   or row.source_payload_offset != first.source_payload_offset
                   or row.decoded_offset != index * size
                   for index, row in enumerate(rows)):
                raise ValueError(f"{family} table {table}: nonuniform physical record geometry")
            groups.append({
                "source": first.source.as_dict(),
                "source_payload_offset": first.source_payload_offset,
                "record_size": size,
                "records": [row.raw.hex() for row in rows],
            })
        tables[str(table)] = groups
    return tables


def master_region(parser: DDBParser, root: Path, region: str) -> dict[str, Any]:
    db_root = gts_db_root(root, region, "Gen")
    master_path = db_root / "Toyota.ddb"
    strings_path = db_root / "M_English.ddb"
    master = parser.parse_master_db(master_path)
    spe = parser.parse_master_db(gts_db_root(root, region, "Spe") / "Toyota.ddb")
    context = native_context(master, spe)
    strings = load_string_db(parser, strings_path)
    mount_query = context.query(19, 121, 0)
    mount_plugin = select_for_consumer(mount_query, "plugin")
    vehicle_names = _vehicle_names(parser, master, strings)
    install_sets = _install_sets(master)
    set_categories = _set_categories(master)

    t41 = list(records(master.sections[VEHICLE_DECISION_TYPE]))
    t59 = list(records(master.sections[VIN_VEHICLE_DECISION_TYPE]))
    if any(len(row) != 52 for row in t41):
        raise ValueError(f"{region}: CDbVehicleDecisionTable record size drift")
    if any(len(row) != 32 for row in t59):
        raise ValueError(f"{region}: CDbVinVehicleDecisionTable record size drift")

    # Camry-HV is a deterministic join witness. The generic resolver derives
    # its result independently. Vehicle type 12704 was independently pinned by
    # the current master fleet map.
    camry_type = 12704
    camry_vin_rows = [raw for raw in t59 if u16(raw, 0x0E) == camry_type]
    camry_type41_rows = [raw for raw in t41 if u16(raw, 0x32) == camry_type]
    camry_install_sets = install_sets.get(camry_type, [])
    camry_install_rows = _install_rows(master, set(camry_install_sets))
    camry_mount_candidates = []
    for row in camry_install_rows:
        query = context.query(16, row["category_id"])
        candidate: dict[str, Any] = {
            **row, "generation": None, "database": None, "name": None,
            "native_category_query": query.as_dict(),
            "transport_route": _protocol_route(master, row["category_id"], row["connection_route_selector"]),
            "transport_route_boundary": "Raw Gen type13 join; native comparator outside proved index scope.",
        }
        try:
            category = select_for_consumer(query, "category")
            candidate.update({
                "generation": category.generation, "database": category.database_name,
                "name": strings.get_string(category.ecu_name_string_index) or "",
                "category_occurrence": category.as_dict(),
            })
        except (NativeSelectionError, UnresolvedNativeContext) as error:
            candidate["native_category_failure"] = native_failure(error)
        camry_mount_candidates.append(candidate)
    connection_profiles = sorted({
        (row["connection_frame_id"], row["connection_comm_set_id"], row["connection_route_selector"])
        for row in camry_install_rows
    })

    return {
        "master": source(master_path, root),
        "strings": source(strings_path, root),
        "native_context": context.as_dict(),
        "mount_plugin": {"query": mount_query.as_dict(), "selected": mount_plugin.as_dict()},
        "context_label": "explicit_initial",
        "raw_master_tables": _raw_master_tables(context),
        "raw_master_table_encoding": "Each source group stores exact decoded records in physical order. The array index is the physical ordinal; decoded_offset is ordinal * record_size. source_payload_offset is shared by the decoded section.",
        "raw_decision_boundary": "Existing vehicle/install/VIN counts and joins describe Gen source rows, not a native Gen/Spe selection for unproved tables.",
        "tables": {
            "vehicle_decision": {
                "ddb_type": VEHICLE_DECISION_TYPE,
                "db_class_id": f"0x{VEHICLE_DECISION_CLASS:03X}",
                "record_size": 52,
                "record_count": len(t41),
            },
            "vin_vehicle_decision": {
                "ddb_type": VIN_VEHICLE_DECISION_TYPE,
                "db_class_id": f"0x{VIN_VEHICLE_DECISION_CLASS:03X}",
                "record_size": 32,
                "record_count": len(t59),
            },
            "protocol_info": {
                "ddb_type": PROTOCOL_INFO_TYPE,
                "db_class_id": f"0x{PROTOCOL_INFO_CLASS:03X}",
                "record_size": 28,
                "record_count": master.sections[PROTOCOL_INFO_TYPE].header.record_count,
            },
        },
        "vehicle_name_count": len(vehicle_names),
        "install_set_count": len(set_categories),
        "camry_hv_witness": {
            "vehicle_type": camry_type,
            "vehicle_name": vehicle_names.get(camry_type),
            "install_set_ids": camry_install_sets,
            "vin_decision_row_count": len(camry_vin_rows),
            "vehicle_decision_row_count": len(camry_type41_rows),
            "vin_rows": [raw.hex() for raw in camry_vin_rows],
            "mount_candidate_count": len(camry_mount_candidates),
            "mount_candidates": camry_mount_candidates,
            "connection_profiles": [
                {"frame_id": frame_id, "comm_set_id": comm_set_id, "route_selector": route_selector}
                for frame_id, comm_set_id, route_selector in connection_profiles
            ],
            "connection_frame_witness": _comm_frame_witness(context, 0),
            "connection_comm_set_witness": _comm_set_witness(context, 9),
        },
    }


def build(*, gtsplus_root: Path | None = None, recovered_root: Path = DEFAULT_RECOVERED) -> dict[str, Any]:
    root = resolve_gts_root(gtsplus_root)
    recovered = recovered_root.expanduser().resolve()
    parser = DDBParser()

    diag = recovered / "bin/DiagAdaptation.dll"
    command = recovered / "bin/CommandCommon.dll"
    
    kgp = root / "bin/KgpDataCtrl.dll"
    select = root / "bin/SelectCarTypVn10_DT.dll"
    mount = root / "bin/GetMntEcuLstNoCf_DT.dll"
    support = root / "bin/GetSupportP5_DT.dll"
    comm_frame_ctrl = root / "bin/KGP_CommFrameCtrl.dll"
    command_data = root / "bin/CommandDataLib.dll"
    individual_connection = root / "bin/GetEcuEchConnect_DT.dll"
    for path in (diag, command, kgp, select, mount, support, comm_frame_ctrl, command_data, individual_connection):
        if not path.is_file():
            raise FileNotFoundError(path)
    
    function_addresses = {
        "vehicle_decision": {
            "DecisionKey": export_addr(kgp, "DecisionKey@CDbVehicleDecisionTable"),
            "DecisionKeyNew": export_addr(kgp, "DecisionKeyNew@CDbVehicleDecisionTable"),
            "DecisionKeyEU": export_addr(kgp, "DecisionKeyEU@CDbVehicleDecisionTable"),
            "DecisionKeyNewEU": export_addr(kgp, "DecisionKeyNewEU@CDbVehicleDecisionTable"),
        },
        "vin_vehicle_decision": {
            "DecisionKey": export_addr(kgp, "DecisionKey@CDbVinVehicleDecisionTable"),
        },
        "mounted_ecu": {
            "CommConnectionNoBuffer": export_addr(command, "CommConnectionNoBuffer@CEcuConnectCheck"),
            "GetEcuAddr": export_addr(comm_frame_ctrl, "GetEcuAddr@CCommFrameCtrl"),
            "ProtInfo.FindDbItem1": export_addr(kgp, "FindDbItem1@CDbProtInfoTable"),
            "ProtInfo.FindDbItem2": export_addr(kgp, "FindDbItem2@CDbProtInfoTable"),
        },
        "p5_support": {
            "GetSupportP5.Execute": export_addr(support, "Execute"),
            "CheckSupportPid": export_addr(command, "CheckSupportPid@CCommCachePlusP5"),
            "CheckSupportDid": export_addr(command, "CheckSupportDid@CCommCachePlusP5"),
            "CheckSupportRid": export_addr(command, "CheckSupportRid@CCommCachePlusP5"),
            "AnalyzeFrameData": export_addr(command, "AnalyzeFrameData@CCmdSupportDataIdList@@"),
            "CreateEnableDataIdList": export_addr(command, "CreateEnableDataIdList@CCmdSupportDataIdList@@"),
            "CreateEnableRIdList": export_addr(command, "CreateEnableRIdList@CCmdSupportDataIdList@@"),
        },
    }
    
    expected = {
        "vehicle_decision": {
            "DecisionKey": 0x100D4AF0,
            "DecisionKeyNew": 0x100D54D0,
            "DecisionKeyEU": 0x100D6130,
            "DecisionKeyNewEU": 0x100D6B90,
        },
        "vin_vehicle_decision": {"DecisionKey": 0x100D91D0},
        "mounted_ecu": {
            "CommConnectionNoBuffer": 0x100829C0,
            "GetEcuAddr": 0x10035420,
            "ProtInfo.FindDbItem1": 0x100C2590,
            "ProtInfo.FindDbItem2": 0x100C2690,
        },
        "p5_support": {
            "GetSupportP5.Execute": 0x10001630,
            "CheckSupportPid": 0x10072180,
            "CheckSupportDid": 0x10070DB0,
            "CheckSupportRid": 0x10072F80,
            "AnalyzeFrameData": 0x10063660,
            "CreateEnableDataIdList": 0x10063890,
            "CreateEnableRIdList": 0x10066160,
        },
    }
    if function_addresses != expected:
        raise ValueError(f"current resolver export drift: {function_addresses!r}")
    
    phase5_vehicle_decision_va = 0x10004D80
    phase5_vehicle_decision_bytes = va_bytes(select, phase5_vehicle_decision_va, 8)
    if phase5_vehicle_decision_bytes != bytes.fromhex("b8010104c0c21400"):
        raise ValueError(f"current Phase5 vehicle-decision stub drift: {phase5_vehicle_decision_bytes.hex()}")
    
    binaries = {
        "DiagAdaptation.dll": source(diag, recovered),
        "CommandCommon.dll": source(command, recovered),
        "KgpDataCtrl.dll": source(kgp, root),
        "SelectCarTypVn10_DT.dll": source(select, root),
        "GetMntEcuLstNoCf_DT.dll": source(mount, root),
        "GetSupportP5_DT.dll": source(support, root),
        "KGP_CommFrameCtrl.dll": source(comm_frame_ctrl, root),
        "CommandDataLib.dll": source(command_data, root),
        "GetEcuEchConnect_DT.dll": source(individual_connection, root),
    }
    for name, path in (("DiagAdaptation.dll", diag), ("CommandCommon.dll", command)):
        binaries[name]["qualification"] = qualify_recovered_source(
            path, root / "bin" / name, component_root=recovered
        )

    mount_evidence = {}
    for name, path, expected_sha, pins in (
        ("DiagAdaptation.dll", diag,
         "eb4b5ffd08bfd1e18b7c5aa5b3679893fb6d3efc2c9bcd655c5e40038fe8531a", (
             ("dv4_dispatch", 0x100732B8, "c745e8f88a0910"),
             ("dv4_vtable", 0x10098AF8, "d0450010202304100046001080270410"),
             ("dv4_mode_zero", 0x10042801, "c645d800"),
             ("dv5_dispatch", 0x100732F4, "e8a720f9ff"),
         )),
        ("CommandDataLib.dll", command_data,
         "ffce12af45554a552dbf616545c4c4e02780702e4cb9e2c6f8235ff4f05c79ab", (
             ("no_comm_role", 0x1006650D, "6a79e89c28faff"),
             ("no_comm_mode_zero", 0x10066595, "c6473400"),
         )),
        ("GetMntEcuLstNoCf_DT.dll", mount,
         "711bd8965c76081df2a0a7b5a2a4abf1c3f4c94e7cb10b60266c488e8f5cdb10", (
             ("no_cf_mode_one_rejection", 0x1000FCB3,
              "80793401752d68a052011068c1000000684853011068085401106801050490ff15a4500110"),
             ("no_cf_vtable", 0x100152BC,
              "50fc00102008011020f40010e0fd001090050110f0f5001040f70010700d0110000e0110900e011020f1001070f00010d0f2001060f20010"),
             ("no_cf_row_mode_gate", 0x1000F4AD,
              "8a40343c0174043c02750484d274790fb741060fb7490c508985fcfeff"),
             ("no_cf_publish_unknown_connection", 0x1000F50B,
              "288bf885ff754a8b85fcfeffff8d8d00ffffff6aff898508ffffff8b0653518bceff50248bf885"),
         )),
        ("GetEcuEchConnect_DT.dll", individual_connection,
         "7f5fede2a4861426594fe8c62dd55d7366cfa47b8a3a9a9589abdc81d9ef6243", (
             ("individual_connection_vtable", 0x100142AC,
              "40fb001000ff001010f4001000fc001070fc001090f60010e0f7001040040110d00401106005011010f1001060f00010c0f2001050f20010"),
             ("individual_connection_cache_branch", 0x1000F581,
              "837de8018b85ecfeffff743f6683f8157439"),
         )),
    ):
        if binaries[name]["sha256"] != expected_sha:
            raise ValueError(f"current mount source drift: {name}")
        for label, address, expected_hex in pins:
            raw = va_bytes(path, address, len(bytes.fromhex(expected_hex)))
            if raw.hex() != expected_hex:
                raise ValueError(f"current mount byte drift: {name}: {label}")
            mount_evidence[label] = {
                "binary": name, "va": f"0x{address:08X}",
                "bytes": raw.hex(), "sha256": hashlib.sha256(raw).hexdigest(),
            }

    regions = {region: master_region(parser, root, region) for region in REGIONS}

    # Exact current P5 C8 frame equality is already derived in the execution
    # model/registry.  Keep its wire contract here because it is the resolver's
    # generic capability primitive consumed by Comma-side tooling.
    return {
        "schema": "gtsplus-current-vehicle-resolver-v3",
        "release": "2026.03.002.02",
        "binaries": binaries,
        "functions": {group: {name: f"0x{addr:08X}" for name, addr in rows.items()}
                      for group, rows in function_addresses.items()},
        "pipeline": [
            {
                "stage": "vehicle-resolution",
                "api": "CDAExecSelectVehicle -> CSelectCarTypeVin10",
                "semantics": (
                    "CSelectCarTypeVin10 dispatches by communication generation. P3/P4 use CDbVehicleDecisionTable; "
                    "current P5 (generation-low5 20/21) uses CDbVinVehicleDecisionTable and its Phase5 vehicle-decision "
                    "virtual returns 0xC0040101 without querying class 0x129; results feed vehicle/install resolution"
                ),
            },
            {
                "stage": "mounted-ecu-resolution",
                "api": "DV000004 -> CGetMountEcuListNoCommSnd(role 121, mode 0) -> GetMntEcuLstNoCf_DT",
                "semantics": (
                    "enumerate selected install rows with connection flag -1; only the final mutually exclusive "
                    "ECU-alias branches may probe connectivity and remove alternatives"
                ),
            },
            {
                "stage": "individual-ecu-connectivity",
                "api": "DV000005 -> CEcuEachConnectSnd/Rcv",
                "semantics": (
                    "explicit groupId/ecuId/busId request; only a one-record response emits the signed connect flag"
                ),
            },
            {
                "stage": "feature-support-resolution",
                "api": "GetSupportP5_DT",
                "semantics": (
                    "optionId 1/2/3 dispatches to CCommCachePlusP5::CheckSupportPid/Did/Rid; support requires live/cached "
                    "communication state beyond DDB presence"
                ),
            },
        ],
        "vehicle_decision": {
            "ddb_type": VEHICLE_DECISION_TYPE,
            "current_p5_boundary": {
                "generation_low5": [20, 21],
                "phase5_vehicle_decision_virtual": f"0x{phase5_vehicle_decision_va:08X}",
                "phase5_vehicle_decision_bytes": phase5_vehicle_decision_bytes.hex(),
                "return_status": "0xC0040101",
                "meaning": "current Phase5 does not query class 0x129; type-41 vehicle decision is the P3/P4 path",
            },
            "db_class_id": f"0x{VEHICLE_DECISION_CLASS:03X}",
            "record_size": 52,
            "mode_dispatch": {
                "0": "DecisionKey",
                "1": "DecisionKeyNew",
                "2": "DecisionKeyEU",
                "3": "DecisionKeyNewEU",
            },
            "base_rule": {
                "flags_offset": "0x24",
                "dont_care_bits": "bits 0..9 bypass ten decision criteria",
                "scalar_operators": {"1": "equal", "2": "not-equal", "3": "record<=key", "4": "record>=key"},
                "eu_behavior": "EU variants return a specificity score; FindDbItem retains only highest-score matches",
            },
        },
        "vin_vehicle_decision": {
            "ddb_type": VIN_VEHICLE_DECISION_TYPE,
            "db_class_id": f"0x{VIN_VEHICLE_DECISION_CLASS:03X}",
            "record_size": 32,
            "key": {
                "category_id": "u16; record +0x10",
                "route_selector": "u8; record +0x12",
                "vin_prefix": "VIN[0:11]; record +0x13..+0x1D, with per-byte wildcard bits",
            },
            "flags": "record +0x00 dword; bits 0..10 wildcard VIN-prefix positions 0..10",
            "vehicle_type": "record +0x0E u16",
            "select_car_query": "CDiagToolDb::GetDbRecord class 0x13B",
        },
        "mounted_ecu": {
            "plugin": "GetMntEcuLstNoCf_DT.dll",
            "source_name": "GetMountEcuListNoCnfm.cpp",
            "inputs": ["CDbInstallingEcuListResRecords", "CDbEcuCategoryResRecords"],
            "current_main_dv4": {
                "command": "DV000004",
                "role": 121,
                "requested_ecu_id": 0,
                "binding_scope": "main-product explicit initial Gen/Spe context; exact query retained per region",
                "mode": 0,
                "dispatch_va": "0x100730B0",
                "group_handler_va": "0x10042780",
                "plugin_entry_va": "0x1000FC50",
                "enumeration_va": "0x1000F420",
                "initial_connection_flag": -1,
                "per_candidate_connection_check": False,
                "alias_postprocessing": {
                    "va": "0x1000FEB0",
                    "groups": [[165, 361, 462], [413, 414, 463]],
                    "gate": "combined category 462/463 and at least one corresponding individual category coexist",
                    "effect": "probe an individual category; remove mutually exclusive alternatives from the result",
                },
                "evidence": mount_evidence,
            },
            "individual_connection": {
                "command": "DV000005",
                "handler_va": "0x100053A0",
                "request": {"groupId": "u16", "ecuId": "u32", "busId": "u16"},
                "response": "connect is the signed byte at CCmdEcuInfo+0x20, emitted only for exactly one record",
                "plugin_contract": {
                    "binary": "GetEcuEchConnect_DT.dll",
                    "processor_va": "0x1000F410",
                    "match": "first Installing row matching requested ECU and encoded route selector",
                    "cache_only": "CheckCarCable succeeds and (its output is 1 or route selector is 0x15): ConnectCheckNoComm",
                    "otherwise": "ConnectCheck receives route selector and Category +0x48 generation separately",
                    "missing_row": "success with no ECU output; the adapter omits connect",
                },
            },
            "install_row": {
                "ddb_type": INSTALLING_ECU_LIST_TYPE,
                "record_size": 24,
                "install_set_id": "u16 +0x04",
                "category_id": "u16 +0x06",
                "connection_frame_id": "u16 +0x08",
                "connection_comm_set_id": "u16 +0x0A",
                "connection_route_selector": "u8 +0x13; passed as CommConnectionNoBuffer arg_10h",
            },
            "transport_route": {
                "api": "CCommFrameCtrl::GetEcuAddr(category, route_selector)",
                "protocol_info_ddb_type": PROTOCOL_INFO_TYPE,
                "protocol_info_db_class_id": f"0x{PROTOCOL_INFO_CLASS:03X}",
                "key": "CDbProtInfoTable +0x00 category_id and +0x18 route_selector",
                "request_address": "u16 +0x08; returned directly by GetEcuAddr",
                "address_extension": (
                    "u8 +0x0A; consumed by the current P5 frame builder. Current selector-0x22 Camry rows use it "
                    "to distinguish logical categories that share request CAN ID 0x750"
                ),
                "legislated_request_address": (
                    "u16 +0x14; current masters contain standard 0x7E0..0x7E7 physical OBD request IDs here. "
                    "The corresponding 11-bit response is request+8; +0x14 is not itself the response ID."
                ),
            },
            "connection_algorithm": {
                "api": "CEcuConnectCheck::CommConnectionNoBuffer",
                "scope": "connection helper used by conditional alias postprocessing and explicit connection callers",
                "comm_frame_db_class_id": f"0x{COMM_FRAME_CLASS:03X}",
                "ecu_category_db_class_id": f"0x{ECU_CATEGORY_CLASS:03X}",
                "steps": [
                    "resolve connection_frame_id through CDbCommFrameTable",
                    "apply connection_comm_set_id with CCommFrameData::SetCommSet",
                    "transmit the database send frame through the common communication cache/direct sender",
                    "AND returned bytes with the database receive mask",
                    "compare the masked result byte-for-byte with the database receive-check bytes",
                    "return the connection result to the caller, which decides whether to remove an alternative",
                ],
            },
            "current_na_camry": {
                "candidate_count": regions["NA"]["camry_hv_witness"]["mount_candidate_count"],
                "connection_profiles": regions["NA"]["camry_hv_witness"]["connection_profiles"],
                "meaning": (
                    "all current Camry-HV install rows declare connection frame 0 / CommSet 9 and route-selector byte "
                    "0x12 or 0x22; all 34 candidate category+route-selector keys resolve in the raw class-0x10D route table. "
                    "Frame 0 has empty send/mask/check variables."
                ),
            },
            "output": "CCmdEcuInfo list",
        },
        "p5_support": {
            "plugin": "GetSupportP5_DT.dll",
            "options": {"1": "PID", "2": "DID", "3": "RID"},
            "did_root": {
                "selector": f"0x{P5_DID_SUPPORT_SELECTOR:02X}",
                "request": P5_DID_SUPPORT_REQUEST.hex(),
                "positive_sid": f"0x{P5_DID_SUPPORT_POSITIVE:02X}",
                "root_bitmap": "MSB-first; set bit n means group (n << 8)",
                "group_request": "replace request DID with supported xx00 group",
                "group_bitmap": "MSB-first; set bit n means xx01+n; final bit for next xx00 is skipped",
            },
            "routine_root": {
                "selector": f"0x{P5_ROUTINE_SUPPORT_SELECTOR:02X}",
                "request": P5_ROUTINE_SUPPORT_REQUEST.hex(),
                "positive_sid": f"0x{P5_ROUTINE_SUPPORT_POSITIVE:02X}",
            },
        },
        "regions": regions,
        "boundary": (
            "DDB membership supplies candidates. Current main DV000004 enumerates them and conditionally resolves "
            "ECU aliases; DV000005 performs a separately requested connectivity check. Support-plugin queries "
            "consume live/cached state. Operation execution and mutation authorization remain separate."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--gtsplus-root", type=Path)
    parser.add_argument("--recovered-root", type=Path, default=DEFAULT_RECOVERED)
    args = parser.parse_args()
    artifact = build(gtsplus_root=args.gtsplus_root, recovered_root=args.recovered_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
