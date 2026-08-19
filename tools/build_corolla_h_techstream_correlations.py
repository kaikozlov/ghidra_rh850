#!/usr/bin/env python3
"""Join Techstream P5 steering vocabulary to Corolla 8965H1202000 diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "techstream"))
from parse_ddb import DDBParser  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
TECH = REPO / "data/generated/techstream_v18/priority_steering_ddb_semantics.json"
APP = REPO / "data/generated/techstream_v18/application_interface_correlations.json"
DIAG = REPO / "data/generated/corolla_8965H1202000_application_diagnostics_diff.json"
EVID = REPO / "data/generated/corolla_8965H1202000_techstream_steering_decompiler_evidence.json"
MASTER = REPO / "data/generated/techstream_v18/toyota_master_routes.json"
APP_RX = REPO / "data/generated/corolla_8965H1202000_application_rx_diff.json"
U023A = REPO / "data/generated/u023a87_monitor_map.json"
SIENNA = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
RAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
DEFAULT_OUT = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
TECHROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def did_map(diag: dict) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for row in diag["readable_dids"]["corolla_h_rdbi_output_audit"]["producers"]:
        for did in row["dids"]:
            out[int(did, 16)] = {
                "callback": row["callback"],
                "classification": row["classification"],
                "declared_length": row["declared_length"],
                "max_write_extent": row["max_write_extent"],
            }
    return out


def source(tech: dict, name: str) -> dict:
    return next(x for x in tech["sources"] if x["relative_path"] == name)


def section_records(db, table_type: int) -> list[bytes]:
    section = db.sections[table_type]
    size = section.record_size
    return [section.raw_data[i * size:(i + 1) * size] for i in range(section.header.record_count)]


def find_u16_record(records: list[bytes], offset: int, key: int) -> tuple[int, bytes]:
    matches = [(i, raw) for i, raw in enumerate(records) if struct.unpack_from("<H", raw, offset)[0] == key]
    if len(matches) != 1:
        raise ValueError(f"expected one key={key} at +0x{offset:x}, got {len(matches)}")
    return matches[0]


def decode_emps_monitor(parser: DDBParser, monitor_key: int) -> dict:
    db_path = TECHROOT / "NA/DB/EMPS_P5.ddb"
    db = parser.parse_ecu_db(db_path)
    strings = parser.load_string_db(TECHROOT / "NA/DB/M_English.ddb")
    monitor_index, monitor_raw = find_u16_record(section_records(db, 62), 0x24, monitor_key)
    physical_key = struct.unpack_from("<H", monitor_raw, 0x2A)[0]
    physical_index, physical_raw = find_u16_record(section_records(db, 13), 0x0C, physical_key)
    unit_key = struct.unpack_from("<H", physical_raw, 0x0E)[0]
    unit_index, unit_raw = find_u16_record(section_records(db, 15), 0x04, unit_key)
    unit_string_index = struct.unpack_from("<I", unit_raw, 0x00)[0]
    return {
        "record_index": monitor_index,
        "name": strings.get_string(struct.unpack_from("<I", monitor_raw, 0x18)[0]),
        "bit_width": struct.unpack_from("<H", monitor_raw, 0x2E)[0] - struct.unpack_from("<H", monitor_raw, 0x2C)[0] + 1,
        "physical_data_key": physical_key,
        "physical_record_index": physical_index,
        "unit_key": unit_key,
        "unit_record_index": unit_index,
        "unit": strings.get_string(unit_string_index) if unit_string_index else None,
        "raw_sha256": sha(monitor_raw),
    }


def type61_ids(src: dict) -> set[int]:
    return {x["fields"]["data_id_u16"] for x in src["sections"]["61"]["records"]}


def monitor_rows(src: dict, h_dids: dict[int, dict]) -> list[dict]:
    rows = []
    for rec in src["sections"]["62"]["records"]:
        raw = bytes.fromhex(rec["raw_hex"])
        primary = struct.unpack_from("<H", raw, 0x36)[0]
        alternate = struct.unpack_from("<H", raw, 0x38)[0]
        h = h_dids.get(primary)
        if h is None:
            continue
        rows.append({
            "monitor_key": rec["fields"]["monitor_key_u16"],
            "name": rec["fields"].get("resolved_name"),
            "primary_data_id": f"0x{primary:04X}",
            "alternate_data_id": f"0x{alternate:04X}" if alternate else None,
            "h_callback": h["callback"],
            "h_callback_classification": h["classification"],
            "h_declared_length": h["declared_length"],
            "h_max_write_extent": h["max_write_extent"],
            "ddb_record_index": rec["record_index"],
            "ddb_record_sha256": sha(raw),
        })
    return rows


def get_func(evid: dict, entry: int) -> dict:
    target = f"0x{entry:08X}"
    return next(x for x in evid["functions"] if x["entry"] == target)


def require(text: str, *needles: str) -> bool:
    return all(n in text for n in needles)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    tech, app, diag, evid, master, app_rx, u023a = map(load, (TECH, APP, DIAG, EVID, MASTER, APP_RX, U023A))
    parser = DDBParser()
    codeflash = RAW.read_bytes()
    sienna = SIENNA.read_bytes()
    h_dids = did_map(diag)
    emps = source(tech, "NA/DB/EMPS_P5.ddb")
    emps2 = source(tech, "NA/DB/EMPS2_P5.ddb")
    emps_ids, emps2_ids = type61_ids(emps), type61_ids(emps2)
    emps_rows = monitor_rows(emps, h_dids)
    emps2_rows = monitor_rows(emps2, h_dids)

    # The type-62 +0x36/+0x38 words behave as the monitor's primary/alternate
    # data-ID pair: apart from the FFFE sentinel, every nonzero +0x36 value and
    # every nonzero +0x38 value resolves in the same DDB's type-61 DataIdForDm
    # table. GetDatMonListP5_DT.dll independently filters monitor exposure via
    # the ECU support-PID/data-ID list. Keep that recovered layout claim separate
    # from the stronger exact target DID callback join below.
    def data_id_field_stats(src: dict) -> dict:
        ids = type61_ids(src)
        a, b = [], []
        for rec in src["sections"]["62"]["records"]:
            raw = bytes.fromhex(rec["raw_hex"])
            a.append(struct.unpack_from("<H", raw, 0x36)[0])
            b.append(struct.unpack_from("<H", raw, 0x38)[0])
        anz = [x for x in a if x]
        bnz = [x for x in b if x]
        return {
            "type62_record_count": len(a),
            "primary_offset": "0x36",
            "alternate_offset": "0x38",
            "primary_nonzero_count": len(anz),
            "primary_resolves_in_type61_or_fffe": sum(x in ids or x == 0xFFFE for x in anz),
            "alternate_nonzero_count": len(bnz),
            "alternate_resolves_in_type61": sum(x in ids for x in bnz),
        }

    m402 = next(x for x in emps_rows if x["monitor_key"] == 402)
    unit402 = app["monitors"]["402"][0]
    f312 = get_func(evid, 0x312F0)["decompiled_c"]
    f378 = get_func(evid, 0x378CC)["decompiled_c"]
    f379 = get_func(evid, 0x379A2)["decompiled_c"]
    f447 = get_func(evid, 0x44744)["decompiled_c"]
    f45c = get_func(evid, 0x45C8E)["decompiled_c"]
    f45e = get_func(evid, 0x45E34)["decompiled_c"]
    f463 = get_func(evid, 0x4636A)["decompiled_c"]
    f466 = get_func(evid, 0x46606)["decompiled_c"]
    f468 = get_func(evid, 0x468FA)["decompiled_c"]
    f46a = get_func(evid, 0x46A10)["decompiled_c"]
    f4c3 = get_func(evid, 0x4C338)["decompiled_c"]
    f4c9 = get_func(evid, 0x4C9B6)["decompiled_c"]
    f32934 = get_func(evid, 0x32934)["decompiled_c"]
    f32958 = get_func(evid, 0x32958)["decompiled_c"]
    f329a0 = get_func(evid, 0x329A0)["decompiled_c"]
    f331 = get_func(evid, 0x33160)["decompiled_c"]
    f332 = get_func(evid, 0x3322E)["decompiled_c"]
    f335 = get_func(evid, 0x335EE)["decompiled_c"]
    f33622 = get_func(evid, 0x33622)["decompiled_c"]
    f3364e = get_func(evid, 0x3364E)["decompiled_c"]
    f336ee = get_func(evid, 0x336EE)["decompiled_c"]
    f4915 = get_func(evid, 0x4915E)["decompiled_c"]
    f4919 = get_func(evid, 0x4919A)["decompiled_c"]
    f491d = get_func(evid, 0x491D6)["decompiled_c"]
    f4937 = get_func(evid, 0x49372)["decompiled_c"]
    f4921 = get_func(evid, 0x49212)["decompiled_c"]
    f4929 = get_func(evid, 0x49298)["decompiled_c"]
    f495 = get_func(evid, 0x495A0)["decompiled_c"]
    f568 = get_func(evid, 0x56892)["decompiled_c"]
    f572 = get_func(evid, 0x5722E)["decompiled_c"]
    f576 = get_func(evid, 0x57692)["decompiled_c"]
    fbb9 = get_func(evid, 0xBB9E8)["decompiled_c"]
    fcd55 = get_func(evid, 0xCD55A)["decompiled_c"]
    fcd5d = get_func(evid, 0xCD5DC)["decompiled_c"]
    fcd64 = get_func(evid, 0xCD644)["decompiled_c"]
    fce92 = get_func(evid, 0xCE928)["decompiled_c"]
    fce97 = get_func(evid, 0xCE974)["decompiled_c"]

    command_chain = {
        "techstream": {
            "monitor_key": 402,
            "name": m402["name"],
            "bit_width": unit402["monitor"]["bit_width"],
            "unit": unit402["unit"]["text"],
            "primary_data_id": m402["primary_data_id"],
            "alternate_data_id": m402["alternate_data_id"],
        },
        "corolla_h_rdbi": {
            "did": "0x1C02",
            "callback": "0x000495A0",
            "callback_classification": m402["h_callback_classification"],
            "declared_length": m402["h_declared_length"],
            "source": "0xFEBE65F2",
            "scale_factor": "0xFEBEE8A6",
            "formula_shape": "source * scale / 0x2000 * 100 / 0x100; clamp to +/-20000; emit signed16",
            "formula_recovered": require(f495, "sRamfebe65f2", "uRamfebee8a6", "/ 0x2000", "* 100", "20000", "FUN_0006385c"),
        },
        "target_native_producer_chain": [
            {"entry": "0x00056892", "relation": "FEBEE40A -> FEBE65F2", "recovered": require(f568, "uRamfebe65f2 = uRamfebee40a")},
            {"entry": "0x00057692", "relation": "FEBEE40A -> FEBE65F2 (alternate snapshot bank)", "recovered": require(f576, "uRamfebe65f2 = uRamfebee40a")},
            {"entry": "0x000BB9E8", "relation": "FEBEAC56 -> FEBEE40A", "recovered": require(fbb9, "uRamfebee40a = uRamfebeac56")},
            {"entry": "0x000CE928", "relation": "FEBEC3D2 -> FEBEAC56", "recovered": require(fce92, "uRamfebeac56 = uRamfebec3d2")},
            {"entry": "0x000CD5DC", "relation": "FEBEC3C0 * FEBEAC5A / 0x400 -> FEBEC3D2", "recovered": require(fcd5d, "sRamfebec3d2", "sRamfebec3c0", "uRamfebeac5a", "/ 0x400")},
            {"entry": "0x000CD55A", "relation": "compose and bound FEBEC3C0 from H-local steering terms", "recovered": require(fcd55, "FUN_000c84f2()", "FUN_000c850c()", "*(short *)(iVar3 + 0xbc0)")},
            {"entry": "0x000CE974", "relation": "active steering pipeline calls CD55A -> CD5DC -> CE928 in order", "recovered": fce97.index("FUN_000cd55a();") < fce97.index("FUN_000cd5dc();") < fce97.index("FUN_000ce928();")},
        ],
        "interpretation": (
            "8965H1202000 exposes Techstream EMPS_P5 Command Value Torque through a live "
            "target-native steering-state producer chain even though its configured CAN/SecOC "
            "ingress has no 0x2E4/0x131 records. Monitor 402 therefore names an internal "
            "commanded-torque observable; it must not be equated with one specific external CAN field."
        ),
    }

    current_monitor_keys = (251, 252, 253, 254, 255, 256)
    current_monitors = {}
    for key in current_monitor_keys:
        row = next(x for x in emps_rows if x["monitor_key"] == key)
        sem = decode_emps_monitor(parser, key)
        current_monitors[str(key)] = {
            "monitor_key": key,
            "name": sem["name"],
            "unit": sem["unit"],
            "bit_width": sem["bit_width"],
            "primary_data_id": row["primary_data_id"],
            "alternate_data_id": row["alternate_data_id"],
            "h_callback": row["h_callback"],
            "h_callback_classification": row["h_callback_classification"],
            "h_declared_length": row["h_declared_length"],
            "ddb_record_sha256": sem["raw_sha256"],
        }

    motor_current_bridge = {
        "techstream_monitors": current_monitors,
        "q_axis_command_chain": [
            {"entry": "0x000CD5DC", "relation": "FEBEC3D2 is bounded/gated into FEBEC3D6 while FEBEC3D8 records the current-limit magnitude", "recovered": require(fcd5d, "sRamfebec3d2", "uRamfebec3d6", "uRamfebec3d8")},
            {"entry": "0x000CD644", "relation": "FEBEC3D6 -> FEBEC3D4, with a bounded fault/override replacement", "recovered": require(fcd64, "uRamfebec3d4 = uRamfebec3d6", "cRamfebec418")},
            {"entry": "0x000CE928", "relation": "FEBEC3D4 -> FEBEAC54 and FEBEC3D8 -> FEBEAC7E", "recovered": require(fce92, "uRamfebeac54 = uRamfebec3d4", "uRamfebeac7e = uRamfebec3d8")},
            {"entry": "0x000BB9E8", "relation": "FEBEAC54 -> FEBEE40C and FEBEAC7E -> FEBEE414", "recovered": require(fbb9, "uRamfebee40c = uRamfebeac54", "uRamfebee414 = uRamfebeac7e")},
            {"entry": "0x000312F0", "relation": "-FEBEE40C -> FEBE6964; FEBEE40A remains the sibling command-torque observer; FEBEE414 -> FEBE696A", "recovered": require(f312, "sRamfebe6964 = -sRamfebee40c", "sRamfebe6966 = sRamfebee40a", "sRamfebe696a = sRamfebee414")},
            {"entry": "0x000336EE", "relation": "FEBE6964 -> FEBE6C1A", "recovered": require(f336ee, "uRamfebe6c1a = uRamfebe6964")},
            {"entry": "0x0003322E", "relation": "FEBE6C1A -> FEBE6BC0 Techstream-visible base Q-current command, and FEBE6BE4 + FEBE6C1A -> FEBE6BB8 compensated Q command", "recovered": require(f332, "sRamfebe6bc0 = sRamfebe6c1a", "sRamfebe6be4 + (int)sRamfebe6c1a", "uRamfebe6bb8")},
            {"entry": "0x0005722E", "relation": "FEBE6BC0 -> FEBE65A4 diagnostic snapshot", "recovered": require(f572, "uRamfebe65a4 = uRamfebe6bc0")},
            {"entry": "0x0004919A", "relation": "FEBE65A4 -> DID 0x1152 Command Value Current (Q Axis)", "recovered": require(f4919, "sRamfebe65a4", "* 100", "/ 0x80", "FUN_0006385c")},
            {"entry": "0x00033160", "relation": "motor feedback combine publishes raw Q feedback aggregate FEBE6BB4 and Techstream-visible saturated Q actual FEBE6BAE", "recovered": require(f331, "iRamfebe6bb4 = iVar2 + iVar4", "uRamfebe6bae")},
            {"entry": "0x00032934", "relation": "FEBE6BB8 compensated Q command - FEBE6BB4 raw Q feedback -> bounded Q current error", "recovered": require(f32934, "sRamfebe6bb8 - iRamfebe6bb4")},
            {"entry": "0x00032958", "relation": "Q current-error sign/gating state is derived for PI anti-windup", "recovered": require(f32958, "param_1", "uRamfebe6af4")},
            {"entry": "0x000329A0", "relation": "Q current error drives the dedicated PI/integrator state", "recovered": require(f329a0, "param_1", "iRamfebe6b08", "iRamfebe6b14", "iRamfebe6b18")},
        ],
        "q_axis_actual_chain": [
            {"entry": "0x00033160", "relation": "motor feedback combine -> FEBE6BAE q-axis actual current and FEBE6BAC d-axis actual current", "recovered": require(f331, "uRamfebe6bae", "uRamfebe6bac")},
            {"entry": "0x0005722E", "relation": "FEBE6BAE -> FEBE6592; FEBE6BAC -> FEBE6590", "recovered": require(f572, "uRamfebe6592 = uRamfebe6bae", "uRamfebe6590 = uRamfebe6bac")},
            {"entry": "0x0004915E", "relation": "FEBE6592 -> DID 0x1151 Motor Actual Current (Q Axis)", "recovered": require(f4915, "sRamfebe6592", "* 100", "/ 0x80")},
            {"entry": "0x000491D6", "relation": "FEBE6590 -> DID 0x1153 Motor Actual Current 2 (D Axis)", "recovered": require(f491d, "sRamfebe6590", "* 100", "/ 0x80")},
        ],
        "d_axis_command_chain": [
            {"entry": "0x0003364E", "relation": "internal D-axis/current auxiliary state is updated and written to FEBE6C0E (GP-0x4BF2)", "recovered": require(f3364e, "FUN_000335ee", "FUN_00033622", "*(short *)(iVar4 + -0x4bf2) = sVar6")},
            {"entry": "0x000335EE", "relation": "D-axis/current auxiliary correction is computed around prior FEBE6C0E", "recovered": require(f335, "sRamfebe6c0e", "sRamfebe6c06", "sRamfebe6c0c")},
            {"entry": "0x00033622", "relation": "auxiliary D-axis/current update is limited against calibration/state", "recovered": require(f33622, "DAT_0002d6b4", "sRamfebe6bc8")},
            {"entry": "0x0003322E", "relation": "FEBE6C0E -> FEBE6BC2 d-axis current reference", "recovered": require(f332, "sRamfebe6bc2 = sRamfebe6c0e")},
            {"entry": "0x0005722E", "relation": "FEBE6BC2 -> FEBE65A6 diagnostic snapshot", "recovered": require(f572, "uRamfebe65a6 = uRamfebe6bc2")},
            {"entry": "0x00049212", "relation": "FEBE65A6 -> DID 0x1154 Command Value Current 2 (D Axis)", "recovered": require(f4921, "sRamfebe65a6", "* 100", "/ 0x80")},
        ],
        "q_axis_limit_chain": [
            {"entry": "0x000CD5DC", "relation": "FEBEC3D8 records the selected symmetric current-limit magnitude", "recovered": require(fcd5d, "uRamfebec3d8 = (short)iVar4")},
            {"entry": "0x000CE928", "relation": "FEBEC3D8 -> FEBEAC7E", "recovered": require(fce92, "uRamfebeac7e = uRamfebec3d8")},
            {"entry": "0x000BB9E8", "relation": "FEBEAC7E -> FEBEE414", "recovered": require(fbb9, "uRamfebee414 = uRamfebeac7e")},
            {"entry": "0x00056892", "relation": "FEBEE414 -> FEBE65FC diagnostic snapshot", "recovered": require(f568, "uRamfebe65fc = uRamfebee414")},
            {"entry": "0x00049298", "relation": "FEBE65FC -> DID 0x1156 Final Motor Current Limited (Q Axis)", "recovered": require(f4929, "sRamfebe65fc", "* 100", "/ 0x80")},
        ],
        "interpretation": (
            "Techstream closes the previously missing static bridge from H's internal command-value-torque state "
            "to the motor current loop. DID 0x1C02 observes FEBEC3D2 upstream of a gating/limit stage; the gated "
            "sibling FEBEC3D4 is published through EE40C, negated into the high-rate Q-axis reference path, and "
            "appears as DID 0x1152 Command Value Current (Q Axis). DID 0x1156 independently observes the selected "
            "Q-axis current-limit magnitude. The D-axis command path is generated by a separate motor-internal "
            "auxiliary update and is not statically sourced from the 1C02 command-torque chain."
        ),
        "boundary": (
            "This proves an internal command-torque -> Q-current-reference control join. It does not identify the "
            "ultimate external/LTA source feeding the high-level FEBEC3C0/FEBEC3D2 synthesis."
        ),
    }

    cooperation = next(x for x in emps_rows if x["monitor_key"] == 60)
    emps_master_routes = [
        {"region": region["region"], "route": route}
        for region in master["regions"]
        for route in region["routes"] if route["database_name"] == "EMPS_P5.ddb"
    ]
    emps2_master_routes = [
        {"region": region["region"], "route": route}
        for region in master["regions"]
        for route in region["routes"] if route["database_name"] == "EMPS2_P5.ddb"
    ]
    emps_master_route = next(x["route"] for x in emps_master_routes if x["region"] == "NA")
    emps_section_types = sorted(int(x) for x in emps["sections"])
    emps_dlls = [x["dll_name"] for x in emps_master_route["dlls"]]
    techstream_surface = {
        "na_master_category_id": emps_master_route["category"]["category_id"],
        "na_master_generation": emps_master_route["category"]["generation"],
        "emps_p5_master_routed_regions": [x["region"] for x in emps_master_routes],
        "emps2_p5_master_route_count": len(emps2_master_routes),
        "section_types": emps_section_types,
        "classic_active_test_section_types_present": sorted(set(emps_section_types) & {11, 12}),
        "master_route_dlls": emps_dlls,
        "active_test_named_dlls": [x for x in emps_dlls if "act" in x.lower() or "test" in x.lower()],
        "routine_named_dlls": [x for x in emps_dlls if "routine" in x.lower()],
        "cooperation_control_state": {
            "monitor_key": 60,
            "name": cooperation["name"],
            "primary_data_id": cooperation["primary_data_id"],
            "h_callback": cooperation["h_callback"],
            "h_callback_classification": cooperation["h_callback_classification"],
            "h_declared_length": cooperation["h_declared_length"],
            "interpretation": "H implements the nominal Cooperation Control State DID as a success stub, so the attractive Techstream name does not expose live Corolla cooperation/LTA state in this calibration.",
        },
        "interpretation": (
            "The master-routed EMPS_P5 surface is data-monitor/DTC/support/RoB oriented. It is routed in NA/EU/JP, while EMPS2_P5 has no recovered master route in this V18 corpus. "
            "EMPS_P5's parsed section set contains no classic type-11/type-12 active-test tables, and category 405 routes no DLL whose name identifies Active Test or RoutineControl. "
            "This is a bounded Techstream-package negative, not proof that Toyota has no separate utility or server-mediated steering procedure."
        ),
    }

    # H's six-row communication-monitor family supplies a second Rosetta-stone
    # join.  The monitor scheduler selects one generated receive-status slot per
    # row; that slot's unpacker identifies the application PDU/CAN descriptor.
    # Dem event byte2 then selects H's DTC table, whose packed DTC joins exactly
    # to the P5 failure-type table.
    slot_unpackers = {
        0x00: (0x45C8E, f45c),
        0x05: (0x45E34, f45e),
        0x10: (0x4636A, f463),
        0x13: (0x46606, f466),
        0x16: (0x468FA, f468),
        0x18: (0x46A10, f46a),
    }
    signal_to_pdu = [struct.unpack_from("<H", codeflash, 0x223FC + i * 2)[0] for i in range(274)]
    descriptors = app_rx["target"]["descriptors"]
    emps_db = parser.parse_ecu_db(TECHROOT / "NA/DB/EMPS_P5.ddb")
    emps_strings = parser.load_string_db(TECHROOT / "NA/DB/M_English.ddb")
    tech_dtc_entries = parser.extract_dtc_failure_entries(emps_db.sections[65])

    def scalar_signal_ids(text: str) -> list[int]:
        return [int(m.group(1), 0) for m in re.finditer(r"FUN_0007643a\((0x[0-9a-f]+|\d+)\s*,", text, re.I)]

    communication_rows = []
    for row_index in range(6):
        rec = codeflash[0x27F68 + row_index * 8:0x27F70 + row_index * 8]
        system_event = rec[0]
        dem_event = struct.unpack_from("<H", rec, 2)[0]
        monitor_index = rec[4]
        status_slot = rec[5]
        if monitor_index != row_index or status_slot not in slot_unpackers:
            raise ValueError(f"unexpected H communication-monitor row {row_index}: {rec.hex()}")
        unpacker_entry, unpacker_c = slot_unpackers[status_slot]
        signal_ids = scalar_signal_ids(unpacker_c)
        pdus = sorted({signal_to_pdu[sig] for sig in signal_ids})
        if len(pdus) != 1 or pdus[0] < 5:
            raise ValueError(f"cannot uniquely resolve monitor row {row_index} PDU: {signal_ids} -> {pdus}")
        pdu_id = pdus[0]
        descriptor_index = pdu_id - 5
        if descriptor_index >= len(descriptors):
            raise ValueError(f"PDU {pdu_id} descriptor outside Rx table")
        descriptor = descriptors[descriptor_index]

        event_rec = codeflash[0x2B988 + dem_event * 8:0x2B990 + dem_event * 8]
        dtc_index = event_rec[2]
        dtc = None
        if dtc_index:
            dtc_raw = codeflash[0x2C588 + dtc_index * 8:0x2C590 + dtc_index * 8]
            failure_type, base_dtc, pad, enabled = struct.unpack("<BHBI", dtc_raw)
            packed = (base_dtc << 8) | failure_type
            matches = [x for x in tech_dtc_entries if x.packed_dtc == packed]
            if len(matches) != 1:
                raise ValueError(f"packed H DTC 0x{packed:06X} has {len(matches)} EMPS_P5 matches")
            te = matches[0]
            dtc = {
                "h_dtc_index": dtc_index,
                "h_record_address": f"0x{0x2C588 + dtc_index * 8:08X}",
                "h_raw_hex": dtc_raw.hex(),
                "base_dtc": f"0x{base_dtc:04X}",
                "failure_type": f"0x{failure_type:02X}",
                "packed_dtc": f"0x{packed:06X}",
                "enabled_word": enabled,
                "techstream_code": te.code,
                "techstream_description": emps_strings.get_string(te.description_string_index),
                "techstream_failure": emps_strings.get_string(te.failure_string_index),
                "techstream_raw_sha256": sha(te.raw),
            }
        communication_rows.append({
            "row_index": row_index,
            "raw_hex": rec.hex(),
            "system_event": f"0x{system_event:02X}" if system_event else None,
            "dem_event": f"0x{dem_event:04X}" if dem_event else None,
            "status_slot": f"0x{status_slot:02X}",
            "unpacker_entry": f"0x{unpacker_entry:08X}",
            "signal_ids": signal_ids,
            "pdu_id": pdu_id,
            "descriptor_index": descriptor_index,
            "can_id": descriptor["can_id"],
            "can_fd": descriptor["can_fd"],
            "length": descriptor["length"],
            "dem_event_record_address": f"0x{0x2B988 + dem_event * 8:08X}" if dem_event else None,
            "dem_event_raw_hex": event_rec.hex() if dem_event else None,
            "dtc": dtc,
        })

    communication_monitor_dtc = {
        "dispatcher": "0x000378CC",
        "scheduler": "0x000379A2",
        "monitor_table": "0x00027F68",
        "dem_event_table": "0x0002B988",
        "dtc_table": "0x0002C588",
        "row_count": 6,
        "target_native_checks": {
            "dispatcher_has_six_rows": require(f378, "param_1 < 6", "DAT_00027f68"),
            "scheduler_walks_six_rows": require(f379, "uVar5 < 6", "DAT_00027f6d", "FUN_00044744"),
            "status_reader_uses_febe7c01": require(f447, "0xfebe7c01", "param_1 & 0xff"),
            "failure_reporter_uses_event_table": require(f4c3, "DAT_0002b98c", "DAT_0002b989", "FUN_0004c9b6"),
            "dem_lifecycle_joins_event_to_dtc_table": require(f4c9, "DAT_0002b988", "DAT_0002b98a", "DAT_0002c588"),
        },
        "rows": communication_rows,
        "brake_missing_message_can_ids": [
            row["can_id"] for row in communication_rows
            if row["dtc"] is not None and row["dtc"]["techstream_code"] == "U012987"
        ],
        "b6_interpretation": (
            "H CAN 0x0B6 maps through receive-status slot 0x18 / PDU42 to Dem event 0x0143, "
            "DTC index 82, packed DTC 0xC12987, which EMPS_P5 names U012987 Lost Communication "
            "with Brake System Control Module / Missing Message. 0x0D7 and classic 0x0D5 share the same "
            "DTC. This strongly classifies B6 as brake-system-originated supervisory/control data rather than "
            "an Image Processing Module A steering-command replacement."
        ),
        "boundary": (
            "The DTC name identifies the monitored source/module relationship in Techstream's P5 diagnostic model; "
            "it does not assign every B6 field or prove that no brake-originated field can influence steering."
        ),
    }

    # The old camera/IPM-A DTC is a particularly useful cross-calibration control.
    # H still carries the DTC/event residue, but the active monitor rows that
    # Sienna used for 2E4/131/191/2FD are gone.
    h_ipm_dtc_raw = codeflash[0x2C588 + 93 * 8:0x2C590 + 93 * 8]
    h_ipm_failure, h_ipm_base, h_ipm_pad, h_ipm_enabled = struct.unpack("<BHBI", h_ipm_dtc_raw)
    h_ipm_packed = (h_ipm_base << 8) | h_ipm_failure
    ipm_matches = [x for x in tech_dtc_entries if x.packed_dtc == h_ipm_packed]
    if len(ipm_matches) != 1:
        raise ValueError(f"H IPM-A DTC 0x{h_ipm_packed:06X} has {len(ipm_matches)} Techstream matches")
    ipm_te = ipm_matches[0]
    active_h_events = {int(row["dem_event"], 16) for row in communication_rows if row["dem_event"]}
    s_ipm_rows = []
    for mapping in u023a["event_mappings"]:
        if mapping["status"] != "recovered":
            continue
        event_id = int(mapping["event_id"], 16)
        monitor_index = mapping["monitor_index"]
        s_row_raw = sienna[0x28278 + monitor_index * 8:0x28280 + monitor_index * 8]
        s_row_event = struct.unpack_from("<H", s_row_raw, 2)[0]
        h_event_raw = codeflash[0x2B988 + event_id * 8:0x2B990 + event_id * 8]
        s_ipm_rows.append({
            "event_id": mapping["event_id"],
            "sienna_monitor_index": monitor_index,
            "sienna_monitor_raw_hex": s_row_raw.hex(),
            "sienna_row_event_matches": s_row_event == event_id,
            "sienna_can_ids": mapping["can_ids"],
            "sienna_rx_state_selector": mapping["rx_state_selector"],
            "corolla_h_event_raw_hex": h_event_raw.hex(),
            "corolla_h_event_dtc_index": h_event_raw[2],
            "corolla_h_active_monitor_row_present": event_id in active_h_events,
        })
    # Field-level closure for the protected brake-originated D7 profile.  Its
    # only recovered command-sized scalar is exactly the Techstream SP1 vehicle
    # speed observable; the other two scalars are status-width fields.
    d7_row = next(row for row in communication_rows if row["can_id"] == "0x0D7")
    d7_scalar_calls = []
    for m in re.finditer(
        r"FUN_0007643a\((0x[0-9a-f]+|\d+)\s*,\s*(0x[0-9a-f]+|\d+)\s*,\s*(0x[0-9a-f]+|\d+)\s*,\s*(0x[0-9a-f]+|\d+)",
        f468, re.I,
    ):
        d7_scalar_calls.append({
            "signal_id": int(m.group(1), 0),
            "packed_bit_offset": int(m.group(2), 0),
            "bit_length": int(m.group(3), 0),
            "bit_offset_in_byte": int(m.group(4), 0),
        })
    d7_scalar_calls.sort(key=lambda x: x["signal_id"])
    sp1 = next(x for x in emps_rows if x["h_callback"].lower() == "0x49372")
    protected_brake_profile_semantics = {
        "d7": {
            "can_id": "0x0D7",
            "pdu_id": d7_row["pdu_id"],
            "techstream_source_dtc": d7_row["dtc"],
            "configured_signal_ids": list(range(240, 248)),
            "scalar_calls": d7_scalar_calls,
            "non_scalar_configured_ids": sorted(set(range(240, 248)) - {x["signal_id"] for x in d7_scalar_calls}),
            "sp1_vehicle_speed": {
                "signal_id": 243,
                "destination": "0xFEBE7D82",
                "primary_data_id": sp1["primary_data_id"],
                "monitor_key": sp1["monitor_key"],
                "name": sp1["name"],
                "h_callback": sp1["h_callback"],
                "callback_recovered": require(f4937, "uRamfebe7d82", "30000", "FUN_00063824"),
            },
            "interpretation": (
                "D7's only recovered 16-bit scalar is signal243 at FEBE7D82, exactly exposed by H DID 0x1185 and named by EMPS_P5 as CAN Vehicle Speed (SP1). "
                "Its other recovered scalars are 1-bit signal240 and 4-bit signal246 status fields. Together with the U012987 Brake System Control Module missing-message DTC, D7 does not expose a recovered steering-command magnitude."
            ),
        },
        "b6": {
            "can_id": "0x0B6",
            "techstream_source_dtc": next(row for row in communication_rows if row["can_id"] == "0x0B6")["dtc"],
            "largest_recovered_scalar_bits": 16,
            "largest_scalar_signal_id": 255,
            "largest_scalar_role": "signed16-staged-only-direct-xref-negative",
            "interpretation": "B6's sole 16-bit scalar is the already-censused staged-only signal255; all supervisor-reaching changed fields are <=8 bits, and its nonscalar/group/full-PDU surfaces are separately closed.",
        },
        "conclusion": "Both protected brake-originated profiles are inconsistent with a recovered hidden autonomous steering-magnitude replacement: D7's 16-bit field is SP1 vehicle speed and B6's 16-bit field has no runtime consumer under the complete direct-xref census.",
    }

    camera_ipm_a_residue = {
        "h_dtc_index": 93,
        "h_dtc_record_address": "0x0002C870",
        "h_dtc_raw_hex": h_ipm_dtc_raw.hex(),
        "packed_dtc": f"0x{h_ipm_packed:06X}",
        "h_enabled_word": h_ipm_enabled,
        "techstream_code": ipm_te.code,
        "techstream_description": emps_strings.get_string(ipm_te.description_string_index),
        "techstream_failure": emps_strings.get_string(ipm_te.failure_string_index),
        "sienna_active_ipm_rows": s_ipm_rows,
        "removed_sienna_can_ids": sorted({can for row in s_ipm_rows for can in row["sienna_can_ids"]}),
        "h_event_b3": {
            "event_id": "0xB3",
            "raw_hex": codeflash[0x2B988 + 0xB3 * 8:0x2B990 + 0xB3 * 8].hex(),
            "dtc_index": codeflash[0x2B988 + 0xB3 * 8 + 2],
            "note": "Sienna U023A87 map retained B3 as configured-unresolved; H disconnects it from DTC index 93 as well.",
        },
        "interpretation": (
            "H retains disabled U023A87 Image Processing Module A diagnostic residue at DTC index 93. "
            "The four Sienna active communication-monitor rows that joined this DTC to CAN 0x2E4, 0x131, 0x191, and 0x2FD are absent from H's active six-row monitor table, "
            "although their Dem event records still point to disabled DTC index 93. Together with the missing 2E4/131 SecOC/COM profiles, this is strong evidence that the classic direct camera/IPM-A steering interface was disabled/removed rather than renumbered to B6."
        ),
        "boundary": (
            "This is a calibration-specific active-monitor/DTC conclusion. It does not identify the replacement vehicle-level LTA architecture or prove another ECU cannot transform camera commands before the EPS sees them."
        ),
    }

    modern_angle = []
    for key in range(2069, 2077):
        rec = next(x for x in emps["sections"]["62"]["records"] if x["fields"]["monitor_key_u16"] == key)
        raw = bytes.fromhex(rec["raw_hex"])
        did = struct.unpack_from("<H", raw, 0x36)[0]
        modern_angle.append({
            "monitor_key": key,
            "name": rec["fields"].get("resolved_name"),
            "primary_data_id": f"0x{did:04X}",
            "corolla_h_rdbi_supported": did in h_dids,
        })

    raw = codeflash
    payload = {
        "schema": "corolla-8965H1202000-techstream-correlations-v2",
        "software_id": "8965H1202000",
        "sources": {
            "corolla_codeflash": {"path": str(RAW.relative_to(REPO)), "sha256": sha(raw), "size": len(raw)},
            "techstream_semantics": {"path": str(TECH.relative_to(REPO)), "sha256": sha(TECH.read_bytes())},
            "techstream_application_correlations": {"path": str(APP.relative_to(REPO)), "sha256": sha(APP.read_bytes())},
            "corolla_diagnostics": {"path": str(DIAG.relative_to(REPO)), "sha256": sha(DIAG.read_bytes())},
            "target_native_evidence": {"path": str(EVID.relative_to(REPO)), "sha256": sha(EVID.read_bytes())},
            "techstream_master_routes": {"path": str(MASTER.relative_to(REPO)), "sha256": sha(MASTER.read_bytes())},
            "corolla_application_rx": {"path": str(APP_RX.relative_to(REPO)), "sha256": sha(APP_RX.read_bytes())},
            "sienna_u023a87_monitor_map": {"path": str(U023A.relative_to(REPO)), "sha256": sha(U023A.read_bytes())},
            "sienna_codeflash": {"path": str(SIENNA.relative_to(REPO)), "sha256": sha(sienna), "size": len(sienna)},
            "na_emps_p5": {"relative_path": emps["relative_path"], "sha256": emps["sha256"]},
            "na_emps2_p5": {"relative_path": emps2["relative_path"], "sha256": emps2["sha256"]},
        },
        "data_id_layout_recovery": {
            "emps_p5": data_id_field_stats(emps),
            "emps2_p5": data_id_field_stats(emps2),
            "host_consumer": "GetDatMonListP5_DT.dll builds enabled/support data-ID lists and calls CheckSupportPid while enumerating CDbDatamonitorP5 records",
            "boundary": "Recovered DDB layout/support-selection semantics; exact ECU-to-DDB selection remains route/category dependent rather than inferred from overlap alone.",
        },
        "ddb_overlap": {
            "h_readable_did_count": len(h_dids),
            "emps_p5": {
                "type61_data_id_count": len(emps_ids),
                "h_type61_overlap_count": len(set(h_dids) & emps_ids),
                "h_supported_monitor_rows": len(emps_rows),
                "h_supported_monitor_primary_dids": len({x["primary_data_id"] for x in emps_rows}),
                "monitor_rows": emps_rows,
            },
            "emps2_p5": {
                "type61_data_id_count": len(emps2_ids),
                "h_type61_overlap_count": len(set(h_dids) & emps2_ids),
                "h_supported_monitor_rows": len(emps2_rows),
                "h_supported_monitor_primary_dids": len({x["primary_data_id"] for x in emps2_rows}),
                "monitor_rows": emps2_rows,
            },
            "interpretation": (
                "EMPS_P5 has the stronger static DID-vocabulary fit for this H image (124 versus 112 type61 IDs) "
                "and uniquely maps H-supported DID 0x1C02 to Command Value Torque; this is evidence for using "
                "EMPS_P5 vocabulary, not proof that a particular vehicle session selected category 405."
            ),
        },
        "techstream_surface": techstream_surface,
        "communication_monitor_dtc": communication_monitor_dtc,
        "protected_brake_profile_semantics": protected_brake_profile_semantics,
        "camera_ipm_a_residue": camera_ipm_a_residue,
        "command_value_torque": command_chain,
        "motor_current_bridge": motor_current_bridge,
        "modern_angle_domain": {
            "rows": modern_angle,
            "primary_data_ids": sorted({x["primary_data_id"] for x in modern_angle}),
            "corolla_h_supports_any": any(x["corolla_h_rdbi_supported"] for x in modern_angle),
            "interpretation": "The EMPS_P5 2069..2076 target-lateral/target-steering-angle vocabulary is grouped under DIDs 0x1CEE/0x1CEF; neither DID exists in H RDBI.",
        },
        "static_conclusion": {
            "techstream_corolla_join_previously_missing": True,
            "command_value_torque_exact_did_join": True,
            "command_value_torque_live_internal_pipeline": all(x["recovered"] for x in command_chain["target_native_producer_chain"]),
            "command_torque_to_q_current_static_bridge": all(x["recovered"] for x in motor_current_bridge["q_axis_command_chain"]),
            "q_d_actual_current_observers_recovered": all(x["recovered"] for x in motor_current_bridge["q_axis_actual_chain"]),
            "d_axis_command_path_separate": all(x["recovered"] for x in motor_current_bridge["d_axis_command_chain"]),
            "q_axis_limit_observer_recovered": all(x["recovered"] for x in motor_current_bridge["q_axis_limit_chain"]),
            "classic_active_test_surface_present": bool(techstream_surface["classic_active_test_section_types_present"] or techstream_surface["active_test_named_dlls"]),
            "live_cooperation_control_state_monitor": cooperation["h_callback_classification"] != "success_stub",
            "b6_brake_system_missing_message_dtc_join": any(
                row["can_id"] == "0x0B6" and row["dtc"] is not None and row["dtc"]["techstream_code"] == "U012987"
                for row in communication_rows
            ),
            "protected_brake_profiles_have_no_recovered_steering_magnitude": protected_brake_profile_semantics["d7"]["sp1_vehicle_speed"]["callback_recovered"] and protected_brake_profile_semantics["b6"]["largest_scalar_role"] == "signed16-staged-only-direct-xref-negative",
            "camera_ipm_a_dtc_disabled": camera_ipm_a_residue["techstream_code"] == "U023A87" and camera_ipm_a_residue["h_enabled_word"] == 0,
            "sienna_ipm_a_monitor_rows_removed_in_h": all(not row["corolla_h_active_monitor_row_present"] for row in s_ipm_rows),
            "external_can_field_equivalence": False,
            "next_use": "Use a same-vehicle stock-LTA interval plus all-bus capture and read-only RDBI/XCP to identify the autonomous contribution before it enters the general internal torque/current chain. If no EPS-local precursor moves, acquire the camera/gateway/other steering-controller firmware rather than repeating broad EPS static analysis.",
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
