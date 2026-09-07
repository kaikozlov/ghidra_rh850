#!/usr/bin/env python3
"""Extract current GTS+ vehicle/profile and P5 capability resolver semantics.

This is the Toyota decision layer above individual diagnostic commands:

* CSelectCarTypeVin10 joins live communication identity/VIN with master
  CDbVehicleDecisionTable / CDbVinVehicleDecisionTable rows;
* GetMountEcuListNoCnfm starts from the selected install set and performs live
  ECU connection filtering; and
* GetSupportP5 exposes Toyota's PID/DID/RID support resolver.  The current P5
  DID path uses a two-level MSB-first support bitmap rooted at 22 01 01.

The artifact is clean derived metadata.  It contains no Toyota executable or
DDB body bytes beyond short instruction/data anchors used to detect drift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any

import pefile

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ddb_semantics import records
from ddb_strings import load_string_db
from parse_ddb import DDBParser
from recover_gtsplus_bodies import recover
from techstream_paths import gts_db_root, resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/vehicle_resolver_semantics.json"
REGIONS = ("NA", "EU", "JP")

# Current KgpDataCtrl master-table class ids used by SelectCarTypeVin10.
VEHICLE_DECISION_CLASS = 0x129
VIN_VEHICLE_DECISION_CLASS = 0x13B
VEHICLE_DECISION_TYPE = 41
VIN_VEHICLE_DECISION_TYPE = 59
INSTALLING_ECU_LIST_TYPE = 44
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


def vin_decision_matches(raw: bytes, category_id: int, phase_type: int, vin11: bytes) -> bool:
    """Express current CDbVinVehicleDecisionTable::DecisionKey."""
    if len(raw) != 32:
        raise ValueError(f"VIN decision record must be 32 bytes, got {len(raw)}")
    if len(vin11) != 11:
        raise ValueError("VIN decision key requires exactly VIN[0:11]")
    if u16(raw, 0x10) != category_id or raw[0x12] != phase_type:
        return False
    flags = u32(raw, 0x00)
    return all((flags & (1 << index)) or raw[0x13 + index] == vin11[index] for index in range(11))


def vin_decision_rows(master: Any, category_id: int, phase_type: int, vin11: bytes) -> list[bytes]:
    return [raw for raw in records(master.sections[VIN_VEHICLE_DECISION_TYPE])
            if vin_decision_matches(raw, category_id, phase_type, vin11)]


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
            "connection_phase_type": raw[0x13],
        })
    return sorted(out, key=lambda row: (row["install_set_id"], row["category_id"]))


def _comm_frame_witness(master: Any, frame_id: int) -> dict[str, Any]:
    matches = [raw for raw in records(master.sections[COMM_FRAME_TYPE]) if u16(raw, 0x00) == frame_id]
    if len(matches) != 1:
        raise ValueError(f"CommFrame {frame_id} resolved {len(matches)} rows")
    raw = matches[0]
    return {
        "frame_id": frame_id,
        "send_variable_id": u16(raw, 0x02),
        "receive_mask_variable_id": u16(raw, 0x04),
        "receive_check_variable_id": u16(raw, 0x06),
        "empty": raw == bytes(len(raw)),
    }


def _comm_set_witness(parser: DDBParser, master: Any, comm_set_id: int) -> dict[str, Any]:
    matches = [row for row in parser.extract_master_comm_sets(master.sections[COMM_SET_TYPE])
               if row.comm_set_id == comm_set_id]
    if len(matches) != 1:
        raise ValueError(f"CommSet {comm_set_id} resolved {len(matches)} rows")
    row = matches[0]
    return {
        "comm_set_id": row.comm_set_id,
        "send_parameter": row.send_parameter,
        "receive_timeout": row.receive_timeout,
        "retry_count": row.retry_count,
        "exception_handler_id": row.exception_handler_id,
        "exception_handler_flag": row.exception_handler_flag,
    }


def master_region(parser: DDBParser, root: Path, region: str) -> dict[str, Any]:
    db_root = gts_db_root(root, region, "Gen")
    master_path = db_root / "Toyota.ddb"
    strings_path = db_root / "M_English.ddb"
    master = parser.parse_master_db(master_path)
    strings = load_string_db(parser, strings_path)
    vehicle_names = _vehicle_names(parser, master, strings)
    install_sets = _install_sets(master)
    set_categories = _set_categories(master)

    t41 = list(records(master.sections[VEHICLE_DECISION_TYPE]))
    t59 = list(records(master.sections[VIN_VEHICLE_DECISION_TYPE]))
    if any(len(row) != 52 for row in t41):
        raise ValueError(f"{region}: CDbVehicleDecisionTable record size drift")
    if any(len(row) != 32 for row in t59):
        raise ValueError(f"{region}: CDbVinVehicleDecisionTable record size drift")

    # Camry-HV is a useful deterministic join witness, not an assumption in the
    # generic resolver.  Vehicle type 12704 was independently pinned by the
    # current master fleet map.
    camry_type = 12704
    camry_vin_rows = [raw for raw in t59 if u16(raw, 0x0E) == camry_type]
    camry_type41_rows = [raw for raw in t41 if u16(raw, 0x32) == camry_type]
    camry_install_sets = install_sets.get(camry_type, [])
    camry_install_rows = _install_rows(master, set(camry_install_sets))
    categories = {
        row.category_id: row
        for row in parser.extract_master_ecu_categories(master.sections[16])
    }
    camry_mount_candidates = [
        {
            **row,
            "generation": categories[row["category_id"]].generation,
            "database": categories[row["category_id"]].database_name,
            "name": strings.get_string(categories[row["category_id"]].ecu_name_string_index) or "",
        }
        for row in camry_install_rows
    ]
    connection_profiles = sorted({
        (row["connection_frame_id"], row["connection_comm_set_id"], row["connection_phase_type"])
        for row in camry_install_rows
    })

    return {
        "master": source(master_path, root),
        "strings": source(strings_path, root),
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
                {"frame_id": frame_id, "comm_set_id": comm_set_id, "phase_type": phase_type}
                for frame_id, comm_set_id, phase_type in connection_profiles
            ],
            "connection_frame_witness": _comm_frame_witness(master, 0),
            "connection_comm_set_witness": _comm_set_witness(parser, master, 9),
        },
    }


def build() -> dict[str, Any]:
    root = resolve_gts_root()
    parser = DDBParser()

    # Main GTS+ CP binaries are recovered from the same-release installers so
    # generation does not trust build/ workspace state.
    with tempfile.TemporaryDirectory(prefix="gtsplus-vehicle-resolver-") as td:
        recovered = Path(td) / "recovered"
        recover(output=recovered)
        diag = recovered / "bin/DiagAdaptation.dll"
        command = recovered / "bin/CommandCommon.dll"

        kgp = root / "bin/KgpDataCtrl.dll"
        select = root / "bin/SelectCarTypVn10_DT.dll"
        mount = root / "bin/GetMntEcuLstNoCf_DT.dll"
        support = root / "bin/GetSupportP5_DT.dll"
        for path in (diag, command, kgp, select, mount, support):
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
            "mounted_ecu": {"CommConnectionNoBuffer": 0x100829C0},
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

        binaries = {
            "DiagAdaptation.dll": source(diag, display="installer-recovered/bin/DiagAdaptation.dll"),
            "CommandCommon.dll": source(command, display="installer-recovered/bin/CommandCommon.dll"),
            "KgpDataCtrl.dll": source(kgp, root),
            "SelectCarTypVn10_DT.dll": source(select, root),
            "GetMntEcuLstNoCf_DT.dll": source(mount, root),
            "GetSupportP5_DT.dll": source(support, root),
        }

    regions = {region: master_region(parser, root, region) for region in REGIONS}

    # Exact current P5 C8 frame equality is already derived in the execution
    # model/registry.  Keep its wire contract here because it is the resolver's
    # generic capability primitive consumed by Comma-side tooling.
    return {
        "schema": "gtsplus-current-vehicle-resolver-v1",
        "release": "2026.03.002.02",
        "binaries": binaries,
        "functions": {group: {name: f"0x{addr:08X}" for name, addr in rows.items()}
                      for group, rows in function_addresses.items()},
        "pipeline": [
            {
                "stage": "vehicle-resolution",
                "api": "CDAExecSelectVehicle -> CSelectCarTypeVin10",
                "semantics": (
                    "live communication/protocol identity plus VIN and user/option selections are resolved through "
                    "CDbVehicleDecisionTable and CDbVinVehicleDecisionTable; results include vehicleId, decisionVin, "
                    "parentPhaseType, carInfoList and optionInfoList"
                ),
            },
            {
                "stage": "mounted-ecu-resolution",
                "api": "CDAExecGetMountEcuList -> GetMountEcuListNoCnfm",
                "semantics": (
                    "selected CDbInstallingEcuListTable candidates are passed through CEcuConnectCheck/" 
                    "CommConnectionNoBuffer and returned as CCmdEcuInfo mounted ECUs"
                ),
            },
            {
                "stage": "feature-support-resolution",
                "api": "GetSupportP5_DT",
                "semantics": (
                    "optionId 1/2/3 dispatches to CCommCachePlusP5::CheckSupportPid/Did/Rid; support is live/cached "
                    "communication state, not DDB presence alone"
                ),
            },
        ],
        "vehicle_decision": {
            "ddb_type": VEHICLE_DECISION_TYPE,
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
                "phase_type": "u8; record +0x12",
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
            "install_row": {
                "ddb_type": INSTALLING_ECU_LIST_TYPE,
                "record_size": 24,
                "install_set_id": "u16 +0x04",
                "category_id": "u16 +0x06",
                "connection_frame_id": "u16 +0x08",
                "connection_comm_set_id": "u16 +0x0A",
                "connection_phase_type": "u8 +0x13; passed as CommConnectionNoBuffer arg_10h",
            },
            "connection_algorithm": {
                "api": "CEcuConnectCheck::CommConnectionNoBuffer",
                "comm_frame_db_class_id": f"0x{COMM_FRAME_CLASS:03X}",
                "ecu_category_db_class_id": f"0x{ECU_CATEGORY_CLASS:03X}",
                "steps": [
                    "resolve connection_frame_id through CDbCommFrameTable",
                    "apply connection_comm_set_id with CCommFrameData::SetCommSet",
                    "transmit the database send frame through the common communication cache/direct sender",
                    "AND returned bytes with the database receive mask",
                    "compare the masked result byte-for-byte with the database receive-check bytes",
                    "set the candidate mounted flag only when the communication succeeds and the check matches",
                ],
            },
            "current_na_camry": {
                "candidate_count": regions["NA"]["camry_hv_witness"]["mount_candidate_count"],
                "connection_profiles": regions["NA"]["camry_hv_witness"]["connection_profiles"],
                "meaning": (
                    "all current Camry-HV install rows use connection frame 0 / CommSet 9 and phase-type byte "
                    "0x12 or 0x22; frame 0 has empty send/mask/check variables, so this is category-scoped "
                    "transport-connectivity resolution, not an identity-DID probe"
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
            "This recovers Toyota's current host-side resolver. DDB membership is candidate metadata; GetMountEcuList "
            "and GetSupportP5 are the live/cached filters. It does not imply that every listed operation is safe to "
            "execute or that mutation authorization can be skipped."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
