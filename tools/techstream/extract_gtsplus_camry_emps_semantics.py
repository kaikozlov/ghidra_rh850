#!/usr/bin/env python3
"""Join current GTS+ EMPS semantics to the exact 2026 Camry F33 dump."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

from parse_ddb import DDBParser, ECU_TABLE_CLASS_NAMES, MASTER_TABLE_CLASS_NAMES
from ddb_semantics import extract_behavior_records, extract_monitor_records, records
from ddb_strings import load_string_db
from techstream_paths import GTSPLUS_EXTERNAL_ROOT, V18_TECHSTREAM_ROOT, resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from analysis_target import target, verified_file  # noqa: E402

DEFAULT_GTS = resolve_gts_root(GTSPLUS_EXTERNAL_ROOT)
DEFAULT_V18 = V18_TECHSTREAM_ROOT
_, F33_TARGET = target("camry-8965F3307000")
IMAGE = verified_file("camry-8965F3307000", "codeflash")
RAM = REPO / "targets/camry-2026/raw-20260826/secoc-recovery/ram/local_ram_pe1.bin"
DECOMP = REPO / "data/generated/camry_8965F3307000_gtsplus_decompiler_evidence.json"
F33_CORPUS = REPO / F33_TARGET["decompiler_corpus"]
OUT = REPO / "data/generated/gtsplus_2026/camry_8965F3307000_emps_semantics.json"
IMAGE_SHA = F33_TARGET["codeflash_sha256"]
RDBI_OFFSET = 0x2928C
RDBI_COUNT = 241


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def monitor_rows(db, strings, *, current: bool) -> list[dict]:
    # ``current`` is retained as a proof-schema input, while record layout is
    # resolved canonically from each section's actual record size.
    out = []
    for record in extract_monitor_records(db.sections[62]):
        out.append({
            "record_index": record.index,
            "monitor_key": record.monitor_key,
            "name": strings.get_string(record.name_string_index),
            "physical_data_key": record.physical_data_key,
            "bit_range": [record.bit_start, record.bit_end],
            "pattern_display_key": record.pattern_display_key,
            "primary_data_id": record.primary_did,
            "alternate_data_id": record.alternate_did,
            "raw_sha256": hashlib.sha256(record.raw).hexdigest(),
        })
    return out

def behavior_rows(db, strings) -> dict[str, dict]:
    out = {}
    for record in extract_behavior_records(db.sections[87]):
        out[record.signature] = {
            "record_index": record.index,
            "signature": record.signature,
            "name": strings.get_string(record.name_string_index),
            "comment": strings.get_string(record.comment_string_index),
            "raw_hex": record.raw.hex(),
            "raw_sha256": hashlib.sha256(record.raw).hexdigest(),
        }
    return out

def dtc_rows(parser: DDBParser, db, strings) -> dict[str, tuple]:
    out = {}
    for entry in parser.extract_dtc_failure_entries(db.sections[65]):
        out[entry.code] = (
            entry.packed_dtc,
            strings.get_string(entry.description_string_index),
            strings.get_string(entry.failure_string_index),
            entry.tail_word,
        )
    return out


def master_vehicle_names(master, strings) -> dict[int, str]:
    out = {}
    for raw in records(master.sections[43]):
        out[u32(raw, 4)] = strings.get_string(u32(raw, 0))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gtsplus-root", type=Path, default=DEFAULT_GTS)
    ap.add_argument("--v18-root", type=Path, default=DEFAULT_V18)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    parser = DDBParser()
    gdb = args.gtsplus_root / "NA/DB/Gen"
    vdb = args.v18_root / "NA/DB"
    source_paths = {
        "gts_emps": gdb / "EMPS_P5.ddb",
        "gts_strings": gdb / "M_English.ddb",
        "gts_master": gdb / "Toyota.ddb",
        "gts_kgp": args.gtsplus_root / "bin/KgpDataCtrl.dll",
        "f33_decompiler_corpus": F33_CORPUS,
        "v18_emps": vdb / "EMPS_P5.ddb",
        "v18_strings": vdb / "M_English.ddb",
        "v18_master": vdb / "Toyota.ddb",
    }
    for name, path in source_paths.items():
        if not path.is_file():
            raise SystemExit(f"missing {name}: {path}")

    image = IMAGE.read_bytes()
    if len(image) != 0x100000 or hashlib.sha256(image).hexdigest() != IMAGE_SHA:
        raise SystemExit("exact F33 image identity drift")
    if not RAM.is_file() or not DECOMP.is_file():
        raise SystemExit("missing tracked Camry RAM/decompiler evidence")

    g_emps = parser.parse_ecu_db(source_paths["gts_emps"])
    v_emps = parser.parse_ecu_db(source_paths["v18_emps"])
    g_strings = load_string_db(parser, source_paths["gts_strings"])
    v_strings = load_string_db(parser, source_paths["v18_strings"])
    g_master = parser.parse_master_db(source_paths["gts_master"])
    v_master = parser.parse_master_db(source_paths["v18_master"])

    g_mon = monitor_rows(g_emps, g_strings, current=True)
    v_mon = monitor_rows(v_emps, v_strings, current=False)
    gm = {row["monitor_key"]: row for row in g_mon}
    vm = {row["monitor_key"]: row for row in v_mon}

    # Exact F33 RDBI table: <u16 DID, u16 payload size, u32 callback, u32 aux,
    # u32 selector>. The selector distinguishes system 1/2 for shared callbacks.
    rdbi = []
    for index in range(RDBI_COUNT):
        off = RDBI_OFFSET + index * 16
        did, size, callback, aux, selector = struct.unpack_from("<HHIII", image, off)
        rdbi.append(
            {
                "record_index": index,
                "record_offset": f"0x{off:06X}",
                "data_id": did,
                "payload_size": size,
                "callback": f"0x{callback:08X}",
                "aux": f"0x{aux:08X}",
                "selector": selector,
                "raw_hex": image[off : off + 16].hex(),
            }
        )
    f33_by_did = {row["data_id"]: row for row in rdbi}

    by_did = defaultdict(list)
    for row in g_mon:
        by_did[row["primary_data_id"]].append(row)
    named = []
    for did in sorted(set(f33_by_did) & set(by_did)):
        rr = f33_by_did[did]
        named.append(
            {
                "data_id": f"0x{did:04X}",
                "payload_size": rr["payload_size"],
                "callback": rr["callback"],
                "selector": rr["selector"],
                "signals": [
                    {
                        **{k: v for k, v in row.items() if k not in ("primary_data_id", "alternate_data_id")},
                        "alternate_data_id": f"0x{row['alternate_data_id']:04X}" if row["alternate_data_id"] else "0x0000",
                    }
                    for row in by_did[did]
                ],
            }
        )

    # Current Toyota master: type-23 CDbSubSystemTable key consumers prove
    # category u16 +0x00 (FindDbItem3) and vehicle type u16 +0x10
    # (FindDbItem2). Type-43 names vehicle type at +0x04.
    cats = {entry.category_id: entry for entry in parser.extract_master_ecu_categories(g_master.sections[16])}
    cat405 = cats[405]
    if not (cat405.database_name == "EMPS_P5.ddb" and cat405.generation == 20):
        raise SystemExit("current GTS+ category 405 drift")
    g_vnames = master_vehicle_names(g_master, g_strings)
    v_vnames = master_vehicle_names(v_master, v_strings)
    g_camry = {vid: name for vid, name in g_vnames.items() if name and name.upper().startswith("CAMRY")}
    v_camry = {vid: name for vid, name in v_vnames.items() if name and name.upper().startswith("CAMRY")}
    subsystem = records(g_master.sections[23])
    p5_by_vehicle = defaultdict(list)
    for index, raw in enumerate(subsystem):
        if u16(raw, 0) == 405 and u32(raw, 0x10) in g_camry:
            p5_by_vehicle[u32(raw, 0x10)].append(
                {"record_index": index, "raw_hex": raw.hex()}
            )
    new_camry = sorted(set(g_camry) - set(v_camry))
    new_p5 = [vid for vid in new_camry if vid in p5_by_vehicle]

    # Current GTS+ contains Toyota's own CAN Bus Check topology model.  Resolve
    # the exact current-Camry family through the class-backed master tables
    # rather than inferring network membership from CAN-ID correlations.
    can_table_ids = (55, 75, 76, 77, 78, 79)
    can_table_expected = {
        55: ("CDbCanBusListTable", 52, 32),
        75: ("CDbCanBusCarIdTable", 733, 12),
        76: ("CDbSubBusConfirmationCGWTable", 256, 16),
        77: ("CDbCanBusOptionTable", 1075, 80),
        78: ("CDbCanBusComponentTable", 34365, 16),
        79: ("CDbCanBusNameTable", 47, 20),
    }
    can_table_geometry = {}
    for table_id in can_table_ids:
        sec = g_master.sections[table_id]
        expected_name, expected_count, expected_size = can_table_expected[table_id]
        if MASTER_TABLE_CLASS_NAMES.get(table_id) != expected_name:
            raise SystemExit(f"current CAN table {table_id} class-name drift")
        if (sec.header.record_count, sec.decoded_record_size) != (expected_count, expected_size):
            raise SystemExit(f"current CAN table {table_id} geometry drift")
        can_table_geometry[str(table_id)] = {
            "class_name": expected_name,
            "record_count": sec.header.record_count,
            "record_size": sec.decoded_record_size,
        }

    can_bus_car_rows = list(records(g_master.sections[75]))
    camry_topology_vehicle_types = [12704, 12862, 12984]
    if camry_topology_vehicle_types != new_p5:
        raise SystemExit(f"Camry topology vehicle-type denominator drift: {new_p5}")
    camry_car_id_rows = []
    for vehicle_type in camry_topology_vehicle_types:
        matches = [raw for raw in can_bus_car_rows if u32(raw, 4) == vehicle_type]
        if len(matches) != 1:
            raise SystemExit(f"Camry vehicle type {vehicle_type} has {len(matches)} CanBusCarId rows")
        raw = matches[0]
        camry_car_id_rows.append({
            "vehicle_type": vehicle_type,
            "vehicle_name": g_camry[vehicle_type],
            "can_bus_car_id": f"0x{u32(raw, 0):08X}",
            "raw_hex": raw.hex(),
        })
    car_ids = {row["can_bus_car_id"] for row in camry_car_id_rows}
    if car_ids != {"0x00A7D910"}:
        raise SystemExit(f"Camry CanBusCarId drift: {sorted(car_ids)}")
    camry_can_bus_car_id = 0x00A7D910

    option_rows = [raw for raw in records(g_master.sections[77]) if u32(raw, 0) == camry_can_bus_car_id]
    if len(option_rows) != 18:
        raise SystemExit(f"Camry CanBusOption variant count drift: {len(option_rows)}")
    option_groups = [u32(raw, 44) for raw in option_rows]
    if len(set(option_groups)) != 18:
        raise SystemExit("Camry CanBusOption component-group keys are no longer unique")

    # CDbCanBusComponentTable's exact current DLL API keys records by dword +0
    # (component-set), u16 +8 (bus index), and u8 +14 (component index).
    # CDbSubBusConfirmationCGWTable is one-based; component index + 1 resolves
    # the Toyota ECU-domain label.  CDbCanBusNameTable resolves the bus index.
    subbus_rows = list(records(g_master.sections[76]))
    subbus_names = {u32(raw, 0): g_strings.get_string(u32(raw, 4)) for raw in subbus_rows}
    if set(subbus_names) != set(range(1, 257)):
        raise SystemExit("current CGW sub-bus sequence is no longer 1..256")
    bus_name_rows = list(records(g_master.sections[79]))
    bus_names = {u32(raw, 8): g_strings.get_string(u32(raw, 4)) for raw in bus_name_rows}
    bus_list_rows = list(records(g_master.sections[55]))
    bus_gateway_names = defaultdict(set)
    for raw in bus_list_rows:
        bus_gateway_names[u16(raw, 8)].add(g_strings.get_string(u32(raw, 4)))

    component_rows = list(records(g_master.sections[78]))
    component_sets = {}
    for group in option_groups:
        group_rows = [raw for raw in component_rows if u32(raw, 0) == group]
        if len(group_rows) != 31:
            raise SystemExit(f"Camry component group 0x{group:08X} row-count drift: {len(group_rows)}")
        placements = []
        for raw in sorted(group_rows, key=lambda item: (u16(item, 8), item[14])):
            component = raw[14]
            bus_index = u16(raw, 8)
            placements.append({
                "component_index": f"0x{component:02X}",
                "subbus_sequence": f"0x{component + 1:02X}",
                "ecu_domain": subbus_names[component + 1],
                "bus_index": bus_index,
                "bus_name": bus_names[bus_index],
                "junction_name": g_strings.get_string(u32(raw, 4)),
                "raw_hex": raw.hex(),
            })
        component_sets[group] = placements
    placement_shapes = {
        tuple((row["component_index"], row["ecu_domain"], row["bus_index"], row["bus_name"]) for row in rows_)
        for rows_ in component_sets.values()
    }
    if len(placement_shapes) != 1:
        raise SystemExit("Camry CAN component placement differs across option variants")
    canonical_placements = next(iter(component_sets.values()))

    critical = {
        row["component_index"]: row
        for row in canonical_placements
        if row["component_index"] in {"0x6D", "0x29", "0x32"}
    }
    expected_critical = {
        "0x6D": ("Front Camera Module", 29, "Bus 1"),
        "0x29": ("Skid Control (ABS/VSC/TRAC)", 32, "Bus 4"),
        "0x32": ("Power Steering (EPS)", 32, "Bus 4"),
    }
    for component, (domain, bus_index, bus_name) in expected_critical.items():
        row = critical.get(component)
        if row is None or (row["ecu_domain"], row["bus_index"], row["bus_name"]) != (domain, bus_index, bus_name):
            raise SystemExit(f"Camry critical topology drift for {component}: {row}")
    if bus_gateway_names[29] != {"Central Gateway"} or bus_gateway_names[32] != {"Central Gateway"}:
        raise SystemExit("Camry critical bus owner/name drift")

    # Exact F33 independently collapses the EPS-side physical denominator: one
    # configured CanIf controller and channel-1-only normal Rx/Tx interrupt
    # wrappers.  B6 is rule 39 inside controller 1's normal 0..42 span.
    f33_funcs = {}
    with F33_CORPUS.open() as corpus_file:
        for line in corpus_file:
            row = json.loads(line)
            if row.get("record") == "function":
                entry = int(row["entry_addr"], 16)
                if entry in (0x83F30, 0x8583E):
                    f33_funcs[entry] = row
    if set(f33_funcs) != {0x83F30, 0x8583E}:
        raise SystemExit("F33 CAN interrupt-wrapper corpus entries missing")
    if "FUN_00083ef2(1);" not in f33_funcs[0x83F30]["decompiled_c"] or "FUN_00085800(1);" not in f33_funcs[0x8583E]["decompiled_c"]:
        raise SystemExit("F33 normal CAN interrupt wrappers no longer select controller/channel 1")
    wrapper_hex = image[0x83F30:0x83F3E].hex()
    if wrapper_hex != "800721000132bfffbcff40063f00" or image[0x8583E:0x8584C].hex() != wrapper_hex:
        raise SystemExit("F33 channel-1 interrupt wrapper raw bytes drift")
    if image[0x21970] != 1:
        raise SystemExit("F33 CanIf controller-count byte drift")
    controller1_rules = [u32(image, 0x230B8 + 0x10 * i) for i in range(47)]
    if controller1_rules[39] != 0x0B6 or controller1_rules[43:46] != [0x7A1, 0x777, 0x7A0]:
        raise SystemExit("F33 controller-1 B6/diagnostic rule placement drift")
    f33_normal_tx_ids = [u32(image, 0x21F58 + 8 * i) & 0x1FFFFFFF for i in range(5)]
    if f33_normal_tx_ids != [0x030, 0x351, 0x394, 0x4A3, 0x4C8]:
        raise SystemExit(f"F33 normal Tx table drift: {f33_normal_tx_ids}")

    # Current-only and changed monitor rows.
    current_only = [gm[key] for key in sorted(gm.keys() - vm.keys())]
    changed = []
    semantic_fields = (
        "name",
        "physical_data_key",
        "bit_range",
        "pattern_display_key",
        "primary_data_id",
        "alternate_data_id",
    )
    for key in sorted(gm.keys() & vm.keys()):
        before, after = vm[key], gm[key]
        delta = {field: [before[field], after[field]] for field in semantic_fields if before[field] != after[field]}
        if delta:
            changed.append({"monitor_key": key, "name": after["name"], "changes": delta})

    gb = behavior_rows(g_emps, g_strings)
    vb = behavior_rows(v_emps, v_strings)
    new_behavior = [gb[sig] for sig in sorted(gb.keys() - vb.keys())]
    if dtc_rows(parser, g_emps, g_strings) != dtc_rows(parser, v_emps, v_strings):
        dtc_delta = "semantic-delta-present"
    else:
        dtc_delta = "none; all 166 type-65 DTC/failure rows semantically unchanged"

    # Current mirrored table slots are consumer-proven by GTS+ KgpDataCtrl's
    # MakeTable jump table; parser names are intentionally exact class names.
    mirror_ids = [151, 153, 156, 157]
    mirrored = []
    for table_id in mirror_ids:
        sec = g_emps.sections[table_id]
        mirrored.append(
            {
                "table_id": table_id,
                "class_name": ECU_TABLE_CLASS_NAMES[table_id],
                "record_count": sec.header.record_count,
                "record_size": sec.decoded_record_size,
            }
        )

    # Type 157 is a byte-semantic subset of current type 62: same current
    # 80-byte CDbDatamonitorP5 grammar, minus time/master-sync metadata rows.
    def current_monitor_map(table_id: int) -> dict[int, tuple]:
        out = {}
        for raw in records(g_emps.sections[table_id]):
            key = u16(raw, 0x34)
            out[key] = (
                g_strings.get_string(u32(raw, 0x28)),
                u16(raw, 0x46),
                u16(raw, 0x48),
                u16(raw, 0x3C),
                u16(raw, 0x3E),
                u16(raw, 0x42),
            )
        return out

    m62, m157 = current_monitor_map(62), current_monitor_map(157)
    if any(m62[key] != val for key, val in m157.items()):
        raise SystemExit("type-157 mirror semantic mismatch")

    asic_keys = [405, 410, 1412, 1413]
    asic_rows = []
    for key in asic_keys:
        row = gm[key]
        did = row["primary_data_id"]
        rr = f33_by_did[did]
        asic_rows.append(
            {
                "monitor_key": key,
                "name": row["name"],
                "data_id": f"0x{did:04X}",
                "bit_range": row["bit_range"],
                "f33_record_offset": rr["record_offset"],
                "f33_payload_size": rr["payload_size"],
                "f33_callback": rr["callback"],
                "f33_selector": rr["selector"],
            }
        )
    if any(row["f33_payload_size"] != 8 or row["f33_callback"] != "0x0004E848" for row in asic_rows):
        raise SystemExit("F33 ASIC-state RDBI callback drift")

    decomp = json.loads(DECOMP.read_text())
    if decomp["callback"]["entry"] != "0x0004E848":
        raise SystemExit("decompiler evidence callback drift")
    ram = RAM.read_bytes()
    ram_off = 0x8298
    snapshot = ram[ram_off : ram_off + 8]

    sources = {}
    for name, path in source_paths.items():
        sources[name] = {
            "path": str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path),
            "size": path.stat().st_size,
            "sha256": sha(path),
        }

    artifact = {
        "schema": "gtsplus-2026-camry-8965f3307000-emps-semantics-v1",
        "sources": sources,
        "target": {
            "software_id": "8965F3307000",
            "codeflash_path": str(IMAGE.relative_to(REPO)),
            "codeflash_sha256": IMAGE_SHA,
            "rdbi_table_offset": f"0x{RDBI_OFFSET:06X}",
            "rdbi_record_count": RDBI_COUNT,
        },
        "current_master_join": {
            "category": {
                "category_id": 405,
                "database": cat405.database_name,
                "ecu_name": g_strings.get_string(cat405.ecu_name_string_index),
                "generation": cat405.generation,
            },
            "table_semantics": {
                "vehicle_name": "type 43 CDbVehicleNameTable: name string u32 +0x00; vehicle type u32 +0x04",
                "subsystem": "type 23 CDbSubSystemTable: category u16 +0x00; vehicle type u16/u32 +0x10",
            },
            "gtsplus_camry_vehicle_type_count": len(g_camry),
            "v18_camry_vehicle_type_count": len(v_camry),
            "v18_max_camry_vehicle_type": max(v_camry),
            "gtsplus_new_camry_vehicle_types": [
                {"vehicle_type": vid, "name": g_camry[vid], "uses_emps_p5": vid in p5_by_vehicle}
                for vid in new_camry
            ],
            "new_camry_vehicle_types_using_emps_p5": [
                {
                    "vehicle_type": vid,
                    "name": g_camry[vid],
                    "subsystem_rows": p5_by_vehicle[vid],
                }
                for vid in new_p5
            ],
            "boundary": "Current GTS+ statically binds these Camry/Camry HV vehicle-type entries to category 405 EMPS_P5. Vehicle-type numeric ordering is not itself asserted to be a model-year field, and no VIN-specific vehicle-type selection is claimed here.",
        },
        "current_camry_can_topology": {
            "table_geometry": can_table_geometry,
            "vehicle_type_to_can_bus_car_id": camry_car_id_rows,
            "can_bus_car_id": "0x00A7D910",
            "option_variant_count": len(option_rows),
            "option_variants": [
                {
                    "component_group": f"0x{u32(raw, 44):08X}",
                    "option_words": [u16(raw, 56 + 2 * i) for i in range(10)],
                    "raw_hex": raw.hex(),
                }
                for raw in option_rows
            ],
            "component_placement_variant_count": len(component_sets),
            "component_placements_identical_across_variants": len(placement_shapes) == 1,
            "canonical_component_placements": canonical_placements,
            "critical_placement": {
                "front_camera_module": critical["0x6D"],
                "skid_control_abs_vsc_trac": critical["0x29"],
                "power_steering_eps": critical["0x32"],
            },
            "critical_bus_owners": {
                "29": {"bus_name": bus_names[29], "gateway_names": sorted(bus_gateway_names[29])},
                "32": {"bus_name": bus_names[32], "gateway_names": sorted(bus_gateway_names[32])},
            },
            "exact_f33_channel_join": {
                "canif_controller_count_byte": {"address": "0x00021970", "value": image[0x21970]},
                "normal_rx_interrupt_wrapper": {
                    "entry": "0x00083F30",
                    "body_hex": wrapper_hex,
                    "decompiled_c_sha256": f33_funcs[0x83F30]["decompiled_c_sha256"],
                    "call": "FUN_00083EF2(1)",
                },
                "normal_tx_interrupt_wrapper": {
                    "entry": "0x0008583E",
                    "body_hex": wrapper_hex,
                    "decompiled_c_sha256": f33_funcs[0x8583E]["decompiled_c_sha256"],
                    "call": "FUN_00085800(1)",
                },
                "normal_tx_table": "0x00021F58",
                "normal_tx_ids": [f"0x{x:03X}" for x in f33_normal_tx_ids],
                "controller1_rule_array": "0x000230B8",
                "controller1_rule_count": 47,
                "b6_rule_index": 39,
                "b6_rule_can_id": "0x0B6",
                "diagnostic_rule_tail": ["0x7A1", "0x777", "0x7A0"],
                "interpretation": "Exact F33 normal application CAN handling is channel/controller-1-only in the recovered interrupt wrappers, and B6 is accepted inside that same controller-1 rule span. A second private F33 application CAN controller is not supported by this target-native configuration.",
            },
            "interpretation": "Toyota's current Camry CAN Bus Check model places Front Camera Module on Central Gateway Bus 1 while Skid Control (ABS/VSC/TRAC) and Power Steering (EPS) are co-resident on Central Gateway Bus 4, invariant across all 18 current Camry option variants. Combined with exact F33's controller-1-only application CAN path, this supports B6 as a Brake/Skid-to-EPS Bus-4 message rather than traffic on a hidden second EPS CAN controller.",
            "boundary": "The GTS+ Bus 1/Bus 4 labels are Toyota Central-Gateway topology identities, not Comma/Panda bus numbers or connector pin numbers. This static table alone does not prove which Toyota-B harness pair exposes Bus 4; that physical join is supplied separately by the retained pre/post-repin Camry captures and diagnostics. Front Camera Module is the GTS+ component-domain label and is not by itself a category-498 FRC identity proof.",
        },
        "emps_p5_schema_delta": {
            "v18_file_size": source_paths["v18_emps"].stat().st_size,
            "gtsplus_file_size": source_paths["gts_emps"].stat().st_size,
            "v18_type62": {"record_count": v_emps.sections[62].header.record_count, "record_size": v_emps.sections[62].decoded_record_size},
            "gtsplus_type62": {"record_count": g_emps.sections[62].header.record_count, "record_size": g_emps.sections[62].decoded_record_size},
            "mirrored_current_tables": mirrored,
            "type157_subset_of_type62": {
                "type62_key_count": len(m62),
                "type157_key_count": len(m157),
                "common_key_count": len(set(m62) & set(m157)),
                "type62_only_keys": sorted(set(m62) - set(m157)),
            },
            "current_only_monitor_rows": [
                {
                    **row,
                    "primary_data_id": f"0x{row['primary_data_id']:04X}",
                    "alternate_data_id": f"0x{row['alternate_data_id']:04X}",
                }
                for row in current_only
            ],
            "changed_monitor_rows": changed,
            "current_only_behavior_codes": new_behavior,
            "type65_dtc_delta": dtc_delta,
        },
        "f33_rdbi_join": {
            "f33_total_data_ids": len(f33_by_did),
            "gtsplus_named_f33_data_ids": len(named),
            "named_data_ids": named,
            "direct_current_improvements_on_f33_supported_dids": [
                {
                    **row,
                    "primary_data_id": f"0x{row['primary_data_id']:04X}",
                    "alternate_data_id": f"0x{row['alternate_data_id']:04X}",
                }
                for row in current_only
                if row["primary_data_id"] in f33_by_did
            ],
        },
        "asic_state_join": {
            "gtsplus_rows": asic_rows,
            "interpretation": "GTS+ splits each exact 8-byte F33 RDBI into bits 0..31 'ASIC State Information' and bits 32..63 'ASIC State Information 2'.",
            "f33_callback_evidence": {
                "path": str(DECOMP.relative_to(REPO)),
                "sha256": sha(DECOMP),
                "resolved_sources": decomp["callback"]["resolved_sources"],
                "gp": decomp["callback"]["gp_value_from_exact_f33_runtime_model"],
            },
            "ram_snapshot": {
                "path": str(RAM.relative_to(REPO)),
                "base": "0xFEBE0000",
                "address": "0xFEBE8298",
                "raw_hex": snapshot.hex(),
                "low_u32_le": f"0x{int.from_bytes(snapshot[:4], 'little'):08X}",
                "high_u32_le": f"0x{int.from_bytes(snapshot[4:], 'little'):08X}",
                "state_boundary": "Captured after application-to-boot handoff; this names an observed RAM snapshot but does not establish READY-mode bit semantics.",
            },
            "remaining_unknown": "Toyota's bit-level meanings inside the two 32-bit ASIC state words are not resolved by the current EMPS_P5 monitor database.",
        },
        "evidence_boundary": "OEM names/database membership come from pinned external Toyota GTS+/Techstream artifacts; RDBI dispatch and RAM sources are exact-target firmware-static evidence; RAM value is a tracked live snapshot. No static GTS+ row is treated as proof of CAN/CAN-FD producer ownership or SecOC signer/key/freshness semantics.",
    }

    if artifact["f33_rdbi_join"]["gtsplus_named_f33_data_ids"] != 121:
        raise SystemExit("expected 121 current GTS+ named F33 DIDs")
    if [x["monitor_key"] for x in artifact["f33_rdbi_join"]["direct_current_improvements_on_f33_supported_dids"]] != [410, 1413]:
        raise SystemExit("unexpected current-only F33 monitor join")
    if [x["vehicle_type"] for x in artifact["current_master_join"]["new_camry_vehicle_types_using_emps_p5"]] != [12704, 12862, 12984]:
        raise SystemExit("current Camry-HV -> EMPS_P5 routing drift")
    if len(new_behavior) != 1 or new_behavior[0]["signature"] != "X2436":
        raise SystemExit("current-only EMPS behavior-code delta drift")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(
        f"wrote {args.out}: {len(named)}/{len(f33_by_did)} F33 DIDs named; "
        f"current Camry-HV EMPS_P5 types={new_p5}; behavior+={[x['signature'] for x in new_behavior]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
