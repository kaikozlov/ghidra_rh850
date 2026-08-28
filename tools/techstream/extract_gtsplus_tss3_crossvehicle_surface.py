"""Extract cross-vehicle TSS3 architecture and recorder/viewer evidence from current GTS+.

This intentionally records the fleet-level joins that are easy to rediscover and
forget: category-498 install-set architecture breadth, per-model/install-set
architecture classification, the v18 ECU_Setting_Table diagnostic-address join,
the Toyota CAN Bus Check topology join, category-family clustering boundaries,
the PCS Data Viewer TSS3 FFD resource surface, the TSE/GTSE parser/layout
surface, and the P6 successor boundary.  It does not infer ECU-side producer
ownership from host metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ddb_semantics import records
from ddb_strings import load_string_db
from parse_ddb import ECU_TABLE_CLASS_NAMES, DDBParser
from pe_utils import binary_strings
from techstream_paths import gts_db_root, resolve_gts_root, v18_techstream_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/tss3_crossvehicle_surface.json"
REGIONS = ("NA", "EU", "JP")

# Categories useful for distinguishing the current category-498 architecture.
SELECTED_CATEGORY_IDS = (
    142,  # legacy/P4 EMPS family seen in a few install sets
    405,  # EMPS_P5
    418,  # LDA_P5
    427,  # PCS1_P5 / Seat Belt Control
    428,  # DSSystem_P5
    429,  # Fr_RadSen_P5
    430,  # Fr_Camera_P5
    431,  # RoadSign_P5
    432,  # PCS2_P5
    435,  # ABS_P5 / Brake/EPB
    466,  # Brake Booster
    476,  # Advanced Drive Control
    477,  # Advanced Drive eXtension Control
    485,  # Electric Parking Brake
    498,  # FRC_P5 / Front Recognition Camera 2
    499,  # EMPS2_P5 / Steering Actuator
)

# Stable short tokens used to label install-set architectures in artifacts/CSVs.
ARCHITECTURE_LABEL_TOKENS = {
    142: "EPS_P4",
    405: "EMPS",
    418: "LDA",
    427: "PCS1",
    428: "DSS",
    429: "FRADSEN",
    430: "FRCAM",
    431: "RSA",
    432: "PCS2",
    435: "ABS",
    466: "BRKBST",
    476: "ADS",
    477: "ADeU",
    485: "EPB",
    498: "FRC",
    499: "EMPS2",
}

# Category-family clustering used by the census and the fleet-map report. The
# grouping is by diagnostic role, not by install-set membership; membership
# facts live in the per-region co-occurrence counts the generator emits.
CATEGORY_FAMILIES = {
    "steering_actuation": (142, 405, 499),
    "brake_domain": (435, 466, 485),
    "front_perception_compute": (430, 498),
    "radar_lateral_periphery": (418, 429),
    "pre_498_pcs_compute": (427, 428, 431, 432),
    "adas_supervision_ethernet": (476, 477),
}

FAMILY_ROLES = {
    "steering_actuation": "electric-power steering actuation generations (P4 legacy, P5 EMPS, P5 Steering Actuator)",
    "brake_domain": "hydraulic/EPB braking control (ABS_P5 skid control, Brake Booster, Electric Parking Brake)",
    "front_perception_compute": "forward camera compute generations (Fr_Camera_P5, FRC_P5/Front Recognition Camera 2)",
    "radar_lateral_periphery": "forward radar / lane-periphery sensing ECUs",
    "pre_498_pcs_compute": "pre-collision / driving-support compute of the pre-498 P5 generation",
    "adas_supervision_ethernet": "Advanced Drive supervision ECUs carried on the Ethernet diagnostic phase",
}

# CAN Bus Check topology master tables, plus the component-index focus set the
# report and verifier use to filter steering/brake/perception placements. t76
# index -> component index is index-1; the artifact retains full placements.
TOPOLOGY_TABLES = {
    55: "CDbCanBusListTable",
    75: "CDbCanBusCarIdTable",
    76: "CDbSubBusConfirmationCGWTable",
    77: "CDbCanBusOptionTable",
    78: "CDbCanBusComponentTable",
    79: "CDbCanBusNameTable",
}
TOPOLOGY_FOCUS_T76_INDEXES = (2, 16, 17, 41, 42, 45, 51, 53, 110, 111, 241)

# v18 IT3Data VDS ECU_Setting_Table layout (mirrors the pinned anchors in
# extract_p5_lateral_control_semantics; this reader is the general census join).
VDS_PAGE_SIZE = 4096
VDS_DATA_PAGE_INDICATOR = 1
VDS_ROW_COUNT_OFFSET = 0x0C
VDS_ROW_OFFSET_TABLE_OFFSET = 0x0E
VDS_ROW_OFFSET_MASK = 0xFFF
ECU_SETTING_ROW_SIZE = 40
ECU_SETTING_MARKER_OFFSET = 0x1A
ECU_SETTING_ADDRESS_LENGTH = 3

PCS_REPORT_ACCESSORS = (
    "get_REPORT_LATERAL_POSITION_FOR_CONTROL_TARGET",
    "get_REPORT_LANE_KEEPING_ASSIST",
    "get_REPORT_DYNAMIC_RADAR_CRUISE_CONTROL",
    "get_REPORT_STEERING_ANGLE",
    "get_REPORT_PRE_BRAKE_REQUEST",
    "get_REPORT_VEHICLE_CONTROL_HISTORY",
    "get_REPORT_DRIVE_DATA_RECORDER",
    "get_REPORT_EVENT_DATA_RECORDER",
    "get_TRIGGER_NAME_TSS3",
)
PCS_TEXT_WITNESSES = (
    "Target Lateral Position",
    "Advanced Drive Control Target Steering Angle Speed Order Value [rad/s]",
    "Advanced Drive Control Target Steering Angle Order Value [rad]",
    "Lateral Control Switch Status",
    "Arbitration result Lateral ID",
    "Steering angle [deg]",
    "Steering angle speed [deg/s]",
    "Control target lateral position at front right",
    "Control target lateral position at front left",
)
PCS_RESOURCE_PREFIXES = (
    "FFD_TSS3_ID_",
    "FFD_TSS3_TRIGGER_ID_",
    "IMGFFD_TSS3_ID_",
    "IMGFFD_TSS3_TRIGGER_ID_",
    "INFO_TSS3FFD_",
    "INFO_FCMIMGFFD_TSS3_",
)

TSE_CONVERTER_SYMBOLS = (
    "GetDtcDataP5",
    "GetDtcDataP5_Ffd",
    "GetPredictiveFFD_FfdSignalData",
    "GetRingBuffData_SignalDataList",
    "GetRingBuffData_SignalInfoList",
    "GetRingBuffData_StoredSignalList",
    "GetRoB_CodeListAbsoluteTime",
    "GetRoB_TimeStampInfo",
    "GetHealthCheck_EcuInfo",
    "GetSystemEcuInfoList",
)
TSE_RINGBUFFER_SYMBOLS = (
    "ParseBufferFrame",
    "ParseFrameTable",
    "ParseRingBuffer",
    "ParseSignalInfoList",
    "ConvertDataFrame",
    "frameId",
    "signalId",
    "signalName",
)
TSE_TEMPLATE_SECTIONS = (
    "タイムスタンプ先頭位置検索キーワード",
    "RecordOnBehavior共通先頭位置検索キーワード",
    "CANバス先頭位置検索キーワード",
    "VehicleControlHistory共通先頭位置検索キーワード",
    "PCS時系列作動時FFD先頭位置検索キーワード",
    "PCS画像FFD先頭位置検索キーワード",
    "DTC(Phase5)先頭位置検索キーワード",
    "PredictiveFFD先頭位置検索キーワード",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(root)).replace("\\", "/"),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def u16(raw: bytes, off: int) -> int:
    return struct.unpack_from("<H", raw, off)[0]


def u32(raw: bytes, off: int) -> int:
    return struct.unpack_from("<I", raw, off)[0]


def category_rows(parser: DDBParser, master: Any, strings: Any) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for row in parser.extract_master_ecu_categories(master.sections[16]):
        out[row.category_id] = {
            "category_id": row.category_id,
            "generation": row.generation,
            "database": row.database_name,
            "short_name": row.ecu_short_name,
            "name": strings.get_string(row.ecu_name_string_index) or "",
        }
    return out


def architecture_label(category_ids: tuple[int, ...]) -> str:
    return "+".join(ARCHITECTURE_LABEL_TOKENS[cid] for cid in category_ids if cid in ARCHITECTURE_LABEL_TOKENS)


def fleet_region(parser: DDBParser, root: Path, region: str) -> dict[str, Any]:
    db_root = gts_db_root(root, region, "Gen")
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = load_string_db(parser, db_root / "M_English.ddb")
    cats = category_rows(parser, master, strings)

    vehicle_names = {
        u16(raw, 0x04): strings.get_string(u32(raw, 0x00))
        for raw in records(master.sections[43])
    }
    vehicle_sets: dict[int, set[int]] = defaultdict(set)
    for raw in records(master.sections[5]):
        vehicle_sets[u16(raw, 0x04)].add(u16(raw, 0x06))
    set_categories: dict[int, set[int]] = defaultdict(set)
    for raw in records(master.sections[44]):
        set_categories[u16(raw, 0x04)].add(u16(raw, 0x06))

    rows: list[dict[str, Any]] = []
    for vehicle_id, install_sets in vehicle_sets.items():
        name = vehicle_names.get(vehicle_id)
        if not name:
            continue
        for install_set in sorted(install_sets):
            installed = set_categories.get(install_set, set())
            if 498 not in installed:
                continue
            architecture = tuple(cid for cid in SELECTED_CATEGORY_IDS if cid in installed)
            rows.append({
                "vehicle_id": vehicle_id,
                "vehicle_name": name,
                "install_set_id": install_set,
                "architecture": architecture,
            })
    rows.sort(key=lambda row: (row["vehicle_id"], row["install_set_id"]))

    architecture_counts = Counter(tuple(row["architecture"]) for row in rows)
    architectures = []
    for architecture, count in sorted(
        architecture_counts.items(), key=lambda item: (-item[1], item[0])
    ):
        models = sorted({row["vehicle_name"] for row in rows if tuple(row["architecture"]) == architecture})
        architectures.append({
            "selected_category_ids": list(architecture),
            "architecture_label": architecture_label(architecture),
            "selected_categories": [cats[cid] for cid in architecture if cid in cats],
            "install_row_count": count,
            "model_names": models,
        })

    cooccurrence = Counter()
    for row in rows:
        for cid in row["architecture"]:
            cooccurrence[cid] += 1

    install_rows = [
        {
            "vehicle_id": row["vehicle_id"],
            "vehicle_name": row["vehicle_name"],
            "install_set_id": row["install_set_id"],
            "architecture_label": architecture_label(row["architecture"]),
            "selected_category_ids": list(row["architecture"]),
        }
        for row in rows
    ]

    return {
        "source": {
            "master": source(db_root / "Toyota.ddb", root),
            "strings": source(db_root / "M_English.ddb", root),
        },
        "install_set_id_namespace": (
            "region-local CDbEcuGroupTable id; meaningful only inside this regional master, never transferable by number"
        ),
        "frc_p5_install_row_count": len(rows),
        "frc_p5_model_name_count": len({row["vehicle_name"] for row in rows}),
        "architecture_count": len(architectures),
        "architectures": architectures,
        "install_rows": install_rows,
        "selected_category_cooccurrence_counts": {
            str(cid): cooccurrence.get(cid, 0) for cid in SELECTED_CATEGORY_IDS
        },
    }


def v18_ecu_setting_addresses(category_ids: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """Scan v18 IT3Data_BDC VDS files for the ECU_Setting_Table address join.

    Rows are 40-byte Jet-page rows: u32 ECUNo at +0x02, u32 Phase at +0x06,
    and the diagnostic request address as exactly three ASCII bytes after the
    FF FE compressed-Unicode marker at +0x1A. Only rows whose ECUNo resolves to
    a current master category are retained; the join is recorded per region.
    """
    v18_root = v18_techstream_root()
    out: dict[str, Any] = {
        "source_product": "Techstream V18.00.003 (installer 18.00.008) IT3Data_BDC MDB VDS ECU_Setting_Table",
        "row_layout": {
            "page_size": VDS_PAGE_SIZE,
            "data_page_indicator": VDS_DATA_PAGE_INDICATOR,
            "row_count_offset": VDS_ROW_COUNT_OFFSET,
            "row_offset_table_offset": VDS_ROW_OFFSET_TABLE_OFFSET,
            "row_offset_mask": VDS_ROW_OFFSET_MASK,
            "row_size": ECU_SETTING_ROW_SIZE,
            "marker_offset": ECU_SETTING_MARKER_OFFSET,
            "marker": "FF FE",
            "address": "3 ASCII bytes at +0x1C",
            "ecu_no": "u32 +0x02",
            "phase": "u32 +0x06",
        },
        "regions": {},
    }
    for region in REGIONS:
        path = v18_root / f"DB/MDB/IT3Data_BDC_{region}.vds"
        data = path.read_bytes()
        by_ecu: dict[int, dict[str, Any]] = {}
        for page_index in range(len(data) // VDS_PAGE_SIZE):
            page = data[page_index * VDS_PAGE_SIZE : (page_index + 1) * VDS_PAGE_SIZE]
            if page[0] != VDS_DATA_PAGE_INDICATOR:
                continue
            row_count = u16(page, VDS_ROW_COUNT_OFFSET)
            if row_count == 0 or row_count > 500:
                continue
            for slot in range(row_count):
                offset = u16(page, VDS_ROW_OFFSET_TABLE_OFFSET + 2 * slot) & VDS_ROW_OFFSET_MASK
                row = page[offset : offset + ECU_SETTING_ROW_SIZE]
                if len(row) < ECU_SETTING_ROW_SIZE:
                    continue
                if row[ECU_SETTING_MARKER_OFFSET : ECU_SETTING_MARKER_OFFSET + 2] != b"\xff\xfe":
                    continue
                address = row[
                    ECU_SETTING_MARKER_OFFSET + 2 : ECU_SETTING_MARKER_OFFSET + 2 + ECU_SETTING_ADDRESS_LENGTH
                ]
                if len(address) != ECU_SETTING_ADDRESS_LENGTH or not all(0x30 <= b <= 0x7A for b in address):
                    continue
                ecu_no = u32(row, 0x02)
                if ecu_no not in category_ids:
                    continue
                entry = {
                    "ecu_no": ecu_no,
                    "phase": u32(row, 0x06),
                    "address": address.decode("ascii"),
                    "page_index_zero_based": page_index,
                    "slot": slot,
                    "row40_sha256": hashlib.sha256(row).hexdigest(),
                }
                existing = by_ecu.get(ecu_no)
                if existing is not None and existing != entry:
                    raise ValueError(
                        f"{region} ECU_Setting rows conflict for ECUNo {ecu_no}: {existing} vs {entry}"
                    )
                by_ecu[ecu_no] = entry
        out["regions"][region] = {
            "source": source(path, v18_root.parent),
            "matched_ecu_count": len(by_ecu),
            "rows": [by_ecu[ecu] for ecu in sorted(by_ecu)],
        }
    return out


def canbus_topology_region(
    parser: DDBParser,
    root: Path,
    region: str,
    frc_vehicle_types: dict[int, str],
) -> dict[str, Any]:
    """Join the regional CAN Bus Check topology for category-498 vehicle types.

    Mirrors the gts_cli canbus join: table 75 vehicle_type -> car_id, table 77
    car_id -> component group, table 78 group -> placements, names from 76/79,
    gateway identity from 55. Every group must resolve to exactly one placement
    shape; the generator asserts that invariant rather than assuming it.
    """
    db_root = gts_db_root(root, region, "Gen")
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = load_string_db(parser, db_root / "M_English.ddb")
    missing = [tid for tid in TOPOLOGY_TABLES if tid not in master.sections]
    if missing:
        raise ValueError(f"{region} master lacks CAN Bus Check tables {missing}")

    car_by_vehicle: dict[int, list[int]] = defaultdict(list)
    for raw in records(master.sections[75]):
        car_by_vehicle[u32(raw, 4)].append(u32(raw, 0))
    groups_by_car: dict[int, list[int]] = defaultdict(list)
    for raw in records(master.sections[77]):
        groups_by_car[u32(raw, 0)].append(u32(raw, 44))
    component_rows: dict[int, list[bytes]] = defaultdict(list)
    for raw in records(master.sections[78]):
        component_rows[u32(raw, 0)].append(raw)
    subbus_names = {
        u32(raw, 0): strings.get_string(u32(raw, 4))
        for raw in records(master.sections[76])
    }
    bus_names = {
        u32(raw, 8): strings.get_string(u32(raw, 4))
        for raw in records(master.sections[79])
    }
    gateway_names: dict[int, set[str]] = defaultdict(set)
    for raw in records(master.sections[55]):
        gateway_names[u16(raw, 8)].add(strings.get_string(u32(raw, 4)))

    def placements_for_group(group: int) -> list[dict[str, Any]]:
        placements = []
        for raw in sorted(
            component_rows.get(group, []),
            key=lambda item: (u16(item, 8), item[14]),
        ):
            bus_index = u16(raw, 8)
            component_index = raw[14]
            placements.append({
                "component_index": component_index,
                "component_hex": f"0x{component_index:02X}",
                "ecu_domain": subbus_names.get(component_index + 1, ""),
                "bus_index": bus_index,
                "bus_name": bus_names.get(bus_index, f"BusIndex {bus_index}"),
                "gateway_names": sorted(x for x in gateway_names.get(bus_index, set()) if x),
                "junction_name": strings.get_string(u32(raw, 4)) or "",
            })
        return placements

    def shape_digest(placements: list[dict[str, Any]]) -> str:
        canonical = json.dumps(placements, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    # Compact storage: bus identities and component domain names are stored
    # once; each shape keeps only per-bus component clusters. Cluster string
    # format: "<bus_index>|<COMP_HEX>[:<junction>][,<COMP_HEX>[:<junction>]]..."
    def encode_shape(placements: list[dict[str, Any]]) -> list[str]:
        by_bus: dict[int, list[str]] = {}
        for placement in placements:
            token = placement["component_hex"]
            junction = placement["junction_name"]
            if junction and junction != "-":
                token += f":{junction}"
            by_bus.setdefault(placement["bus_index"], []).append(token)
        return [
            f"{bus_index}|{','.join(tokens)}"
            for bus_index, tokens in sorted(by_bus.items())
        ]

    group_shape: dict[int, str] = {}
    shapes: dict[str, dict[str, Any]] = {}
    shape_groups: dict[str, set[int]] = defaultdict(set)
    shape_vehicles: dict[str, set[int]] = defaultdict(set)
    used_bus_identities: dict[int, dict[str, Any]] = {}

    vehicle_topology = []
    without_topology = []
    referenced_groups: set[int] = set()
    for vehicle_type in sorted(frc_vehicle_types):
        name = frc_vehicle_types[vehicle_type]
        car_ids = sorted(car_by_vehicle.get(vehicle_type, []))
        if not car_ids:
            without_topology.append({"vehicle_type": vehicle_type, "vehicle_name": name})
            continue
        car_rows = []
        for car_id in car_ids:
            groups = sorted(set(groups_by_car.get(car_id, [])))
            for group in groups:
                if group not in group_shape:
                    placements = placements_for_group(group)
                    digest = shape_digest(placements)
                    group_shape[group] = digest
                    existing = shapes.get(digest)
                    if existing is None:
                        shapes[digest] = {
                            "shape_sha256": digest,
                            "placement_count": len(placements),
                            "bus_clusters": encode_shape(placements),
                        }
                    elif existing["bus_clusters"] != encode_shape(placements):
                        raise ValueError(f"{region} topology shape digest collision for group {group:#x}")
                    for placement in placements:
                        bus_index = placement["bus_index"]
                        identity = used_bus_identities.setdefault(bus_index, {
                            "bus_name": placement["bus_name"],
                            "gateway_names": placement["gateway_names"],
                        })
                        if identity != {
                            "bus_name": placement["bus_name"],
                            "gateway_names": placement["gateway_names"],
                        }:
                            raise ValueError(f"{region} bus identity drift for index {bus_index}")
                shape_groups[group_shape[group]].add(group)
            car_rows.append({
                "can_bus_car_id": f"0x{car_id:08X}",
                "topology_group_keys": [f"0x{group:08X}" for group in groups],
            })
            referenced_groups.update(groups)
        vehicle_topology.append({
            "vehicle_type": vehicle_type,
            "vehicle_name": name,
            "can_bus_car_rows": car_rows,
        })
        for group in {int(k, 16) for row in car_rows for k in row["topology_group_keys"]}:
            shape_vehicles[group_shape[group]].add(vehicle_type)

    def decode_component(cluster: str) -> tuple[str, str]:
        component_hex, _, junction = cluster.partition(":")
        return component_hex, junction

    invariants = {"shapes_with_eps_and_skid": 0, "eps_skid_colocated_same_bus": 0, "camera_on_different_bus_than_eps": 0}
    for entry in shapes.values():
        component_bus = {}
        for cluster in entry["bus_clusters"]:
            bus_index_s, _, body = cluster.partition("|")
            for token in body.split(","):
                component_hex, _ = decode_component(token)
                component_bus[component_hex] = int(bus_index_s)
        if "0x32" in component_bus and "0x29" in component_bus:
            invariants["shapes_with_eps_and_skid"] += 1
            if component_bus["0x32"] == component_bus["0x29"]:
                invariants["eps_skid_colocated_same_bus"] += 1
                if component_bus.get("0x6D") not in (None, component_bus["0x32"]):
                    invariants["camera_on_different_bus_than_eps"] += 1

    for digest, entry in shapes.items():
        entry["topology_group_keys"] = sorted(f"0x{group:08X}" for group in shape_groups[digest])
        entry["frc_p5_vehicle_name_count"] = len({frc_vehicle_types[v] for v in shape_vehicles[digest]})
    shape_list = sorted(shapes.values(), key=lambda entry: (-entry["frc_p5_vehicle_name_count"], entry["shape_sha256"]))

    return {
        "source": {
            "master": source(db_root / "Toyota.ddb", root),
            "strings": source(db_root / "M_English.ddb", root),
        },
        "tables": {str(tid): name for tid, name in sorted(TOPOLOGY_TABLES.items())},
        "frc_p5_vehicle_type_count": len(frc_vehicle_types),
        "can_bus_car_row_count": sum(len(row["can_bus_car_rows"]) for row in vehicle_topology),
        "vehicle_types_without_topology_row": without_topology,
        "topology_group_count": len(referenced_groups),
        "placement_shape_count": len(shape_list),
        "placement_invariants": invariants,
        "bus_identities": {
            str(bus_index): identity for bus_index, identity in sorted(used_bus_identities.items())
        },
        "component_domains": {
            f"0x{component_index:02X}": subbus_names.get(component_index + 1, "")
            for component_index in range(256)
            if subbus_names.get(component_index + 1)
        },
        "vehicle_topology": vehicle_topology,
        "placement_shapes": shape_list,
    }


def component_versions(root: Path) -> dict[str, str]:
    manifest_path = root / "Ver/Manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    components = manifest[0]["Components"]
    versions = {row["Name"]: row["Version"] for row in components}
    versions[manifest[0]["SoftwareName"]] = manifest[0]["SoftwareVersion"]
    return versions


def pcs_data_viewer(root: Path, versions: dict[str, str]) -> dict[str, Any]:
    diagnostics = root.parent
    pcs = diagnostics / "PCS Data Viewer"
    exe = pcs / "PCS Data Viewer.exe"
    resources = pcs / "en-US/PCS Data Viewer.resources.dll"
    exe_strings = set(binary_strings(exe.read_bytes(), minimum=4))
    resource_strings = set(binary_strings(resources.read_bytes(), minimum=4))

    missing_accessors = [s for s in PCS_REPORT_ACCESSORS if s not in exe_strings]
    # .resources blobs may expose a one-byte length/type marker as a leading
    # printable character when scanned generically; require the OEM phrase as
    # a contained substring rather than pretending the scanner returns exact
    # resource-value boundaries.
    missing_text = [s for s in PCS_TEXT_WITNESSES if not any(s in value for value in resource_strings)]
    if missing_accessors or missing_text:
        raise ValueError(
            f"PCS Data Viewer witness drift: accessors={missing_accessors}, text={missing_text}"
        )
    prefix_counts = {
        prefix: len({s for s in resource_strings if s.startswith(prefix)})
        for prefix in PCS_RESOURCE_PREFIXES
    }
    expected_counts = {
        "FFD_TSS3_ID_": 1131,
        "FFD_TSS3_TRIGGER_ID_": 49,
        "IMGFFD_TSS3_ID_": 13,
        "IMGFFD_TSS3_TRIGGER_ID_": 18,
        "INFO_TSS3FFD_": 19,
        "INFO_FCMIMGFFD_TSS3_": 14,
    }
    if prefix_counts != expected_counts:
        raise ValueError(f"PCS TSS3 resource-key census drift: {prefix_counts}")

    return {
        "version": versions["PCS Data Viewer"],
        "sources": {
            "exe": source(exe, diagnostics),
            "english_resources": source(resources, diagnostics),
        },
        "tss3_resource_key_counts": prefix_counts,
        "report_accessors": list(PCS_REPORT_ACCESSORS),
        "english_text_witnesses": list(PCS_TEXT_WITNESSES),
        "interpretation": (
            "PCS Data Viewer contains a large explicit TSS3 FFD/trigger dictionary and report vocabulary "
            "for lateral, steering, cruise, recorder, and pre-brake concepts. This proves an OEM offline "
            "decoder/report surface exists; it does not yet map each resource key to an FRC AB/EB record."
        ),
    }


def tse_converter(root: Path, versions: dict[str, str]) -> dict[str, Any]:
    diagnostics = root.parent
    tse = diagnostics / "GTSPlusTSEConverter"
    converter = tse / "Converter.dll"
    ring = tse / "RingBufferParser.dll"
    converter_strings = set(binary_strings(converter.read_bytes(), minimum=4))
    ring_strings = set(binary_strings(ring.read_bytes(), minimum=4))
    missing_converter = [s for s in TSE_CONVERTER_SYMBOLS if s not in converter_strings]
    missing_ring = [s for s in TSE_RINGBUFFER_SYMBOLS if s not in ring_strings]
    if missing_converter or missing_ring:
        raise ValueError(
            f"TSE converter witness drift: converter={missing_converter}, ring={missing_ring}"
        )

    template_rows = []
    for path in sorted((tse / "TEMPLATE").glob("*_Template.csv")):
        text = path.read_bytes().decode("cp932")
        missing = [s for s in TSE_TEMPLATE_SECTIONS if s not in text]
        if missing:
            raise ValueError(f"{path.name} TSE section drift: {missing}")
        template_rows.append({
            **source(path, diagnostics),
            "encoding": "cp932",
            "required_sections": list(TSE_TEMPLATE_SECTIONS),
        })

    return {
        "version": versions["GTS+ TSEConverter"],
        "sources": {
            "converter": source(converter, diagnostics),
            "ring_buffer_parser": source(ring, diagnostics),
            "templates": template_rows,
        },
        "converter_symbols": list(TSE_CONVERTER_SYMBOLS),
        "ring_buffer_symbols": list(TSE_RINGBUFFER_SYMBOLS),
        "template_section_translations": {
            "RecordOnBehavior共通": "RecordOnBehavior common",
            "CANバス": "CAN bus",
            "VehicleControlHistory共通": "VehicleControlHistory common",
            "PCS時系列作動時FFD": "PCS time-series operation FFD",
            "PCS画像FFD": "PCS image FFD",
            "DTC(Phase5)": "Phase-5 DTC",
            "PredictiveFFD": "Predictive FFD",
            "タイムスタンプ": "timestamp",
        },
        "interpretation": (
            "The shipped TSE/GTSE converter has dedicated P5 DTC/FFD, PredictiveFFD, RoB, health-check, "
            "ring-buffer signal and ECU-map readers, and its three format templates explicitly allocate "
            "CAN, RoB, VehicleControlHistory, PCS time-series FFD and PCS image-FFD sections. This is a "
            "high-value offline capture-format decoder surface, not yet a proven direct parser for FRC AB/EB payloads."
        ),
    }


def adcu_p6(parser: DDBParser, root: Path, versions: dict[str, str]) -> dict[str, Any]:
    db_root = gts_db_root(root, "NA", "Gen")
    master = parser.parse_master_db(db_root / "Toyota.ddb")
    strings = load_string_db(parser, db_root / "M_English.ddb")
    cats = category_rows(parser, master, strings)
    cat = cats[6037]
    db_path = db_root / cat["database"]
    db = parser.parse_ecu_db(db_path)
    selected_tables = (61, 62, 65, 71, 72, 73, 77, 78, 79, 90, 157, 163, 164, 165, 166, 167, 168)
    tables = {
        str(tid): {
            "class": ECU_TABLE_CLASS_NAMES.get(tid, "unknown"),
            "record_count": db.sections[tid].header.record_count,
            "record_size": db.sections[tid].decoded_record_size,
        }
        for tid in selected_tables
        if tid in db.sections
    }
    return {
        "gtsplus_version": versions["GTS+"],
        "category": cat,
        "source": source(db_path, root),
        "selected_table_census": tables,
        "interpretation": (
            "ADCU_P6 is a generation-22 successor-domain oracle with a much larger diagnostic/RoB/DDR surface. "
            "It can be used for semantic migration comparisons, but P6 names or behavior must not be projected "
            "back onto TSS3/P5 without an independent join."
        ),
    }


def category_identity_section(parser: DDBParser, root: Path, addresses: dict[str, Any]) -> dict[str, Any]:
    """Per-region category identities joined to families and diagnostic addresses."""
    family_of = {cid: name for name, cids in CATEGORY_FAMILIES.items() for cid in cids}
    out: dict[str, Any] = {"regions": {}}
    for region in REGIONS:
        db_root = gts_db_root(root, region, "Gen")
        master = parser.parse_master_db(db_root / "Toyota.ddb")
        strings = load_string_db(parser, db_root / "M_English.ddb")
        cats = category_rows(parser, master, strings)
        address_rows = {row["ecu_no"]: row for row in addresses["regions"][region]["rows"]}
        identities = {}
        for cid in SELECTED_CATEGORY_IDS:
            if cid not in cats:
                raise ValueError(f"{region} master lacks selected category {cid}")
            address_row = address_rows.get(cid)
            identities[str(cid)] = {
                **cats[cid],
                "family": family_of.get(cid),
                "diagnostic_request_address": address_row["address"] if address_row else None,
            }
        out["regions"][region] = identities
    # The census treats cross-region identity equality as an observed fact to
    # prove, not an assumption: collapse only after comparing the joined rows.
    reference = json.dumps(out["regions"][REGIONS[0]], sort_keys=True)
    for region in REGIONS[1:]:
        if json.dumps(out["regions"][region], sort_keys=True) != reference:
            raise ValueError(f"selected-category identity drift between {REGIONS[0]} and {region}")
    out["identical_across_regions"] = True
    return out


def category_family_section(fleet: dict[str, Any]) -> dict[str, Any]:
    """Family clustering with per-region 498-cooccurrence and boundary facts."""
    families = {}
    for name, cids in CATEGORY_FAMILIES.items():
        families[name] = {
            "role": FAMILY_ROLES[name],
            "category_ids": list(cids),
            "cooccurrence_with_498_per_region": {
                region: {
                    str(cid): fleet[region]["selected_category_cooccurrence_counts"][str(cid)]
                    for cid in cids
                }
                for region in REGIONS
            },
        }
    zero_boundary = {
        str(cid): {
            region: fleet[region]["selected_category_cooccurrence_counts"][str(cid)] for region in REGIONS
        }
        for cid in SELECTED_CATEGORY_IDS
        if all(fleet[region]["selected_category_cooccurrence_counts"][str(cid)] == 0 for region in REGIONS)
    }
    region_only = {
        str(cid): {
            region: fleet[region]["selected_category_cooccurrence_counts"][str(cid)] for region in REGIONS
        }
        for cid in SELECTED_CATEGORY_IDS
        if cid not in (427, 428, 429, 431, 432)
        and sum(1 for region in REGIONS if fleet[region]["selected_category_cooccurrence_counts"][str(cid)] > 0) == 1
        and any(fleet[region]["selected_category_cooccurrence_counts"][str(cid)] > 0 for region in REGIONS)
    }
    return {
        "families": families,
        "zero_cooccurrence_with_498_all_regions": zero_boundary,
        "region_only_cooccurrence_with_498": region_only,
    }


def install_set_collision_proof(parser: DDBParser, root: Path) -> dict[str, Any]:
    """Prove install-set ids are region-local by exhibiting cross-region collisions.

    The comparison uses the full CDbInstallingEcuListTable category set of each
    498-carrying install set, not just the census selection, so an identical
    selected sub-architecture cannot mask a different real install set.
    """
    per_region_sets: dict[str, dict[int, frozenset[int]]] = {}
    for region in REGIONS:
        db_root = gts_db_root(root, region, "Gen")
        master = parser.parse_master_db(db_root / "Toyota.ddb")
        vehicle_sets: dict[int, set[int]] = defaultdict(set)
        for raw in records(master.sections[5]):
            vehicle_sets[u16(raw, 0x04)].add(u16(raw, 0x06))
        set_categories: dict[int, set[int]] = defaultdict(set)
        for raw in records(master.sections[44]):
            set_categories[u16(raw, 0x04)].add(u16(raw, 0x06))
        frc_sets = {
            install_set: frozenset(set_categories.get(install_set, set()))
            for install_sets in vehicle_sets.values()
            for install_set in install_sets
            if 498 in set_categories.get(install_set, set())
        }
        per_region_sets[region] = frc_sets
    collisions = []
    for first in range(len(REGIONS)):
        for second in range(first + 1, len(REGIONS)):
            left, right = REGIONS[first], REGIONS[second]
            shared = sorted(set(per_region_sets[left]) & set(per_region_sets[right]))
            differing = [set_id for set_id in shared if per_region_sets[left][set_id] != per_region_sets[right][set_id]]
            collisions.append({
                "regions": [left, right],
                "shared_install_set_id_count": len(shared),
                "different_full_category_set_count": len(differing),
                "example_install_set_ids": [f"0x{set_id:04X}" for set_id in differing[:5]],
            })
    if not any(row["different_full_category_set_count"] for row in collisions):
        raise ValueError("install-set id collision proof found no differing shared ids; join model changed")
    return {
        "meaning": (
            "Install-set ids are keys of the per-region CDbEcuGroupTable. The same numeric id recurs across "
            "regional masters with different full install categories, so ids must never be joined across "
            "regions without the regional master context."
        ),
        "collisions": collisions,
    }


def build() -> dict[str, Any]:
    root = resolve_gts_root()
    parser = DDBParser()
    versions = component_versions(root)
    fleet = {region: fleet_region(parser, root, region) for region in REGIONS}

    # Explicitly record the correction to a tempting but unsupported inference.
    no_frc_cooccurrence = {}
    for cid in (427, 428, 429, 431, 432):
        counts = {region: fleet[region]["selected_category_cooccurrence_counts"][str(cid)] for region in REGIONS}
        if any(counts.values()):
            raise ValueError(f"expected no FRC_P5 co-occurrence for category {cid}, got {counts}")
        no_frc_cooccurrence[str(cid)] = counts

    identity_root_categories = category_rows(
        parser,
        parser.parse_master_db(gts_db_root(root, REGIONS[0], "Gen") / "Toyota.ddb"),
        load_string_db(parser, gts_db_root(root, REGIONS[0], "Gen") / "M_English.ddb"),
    )
    addresses = v18_ecu_setting_addresses(identity_root_categories)
    identities = category_identity_section(parser, root, addresses)
    for region in REGIONS:
        for cid in (405, 435, 498):
            if identities["regions"][region][str(cid)]["diagnostic_request_address"] is None:
                raise ValueError(f"{region} lost the pinned diagnostic address for category {cid}")

    topology = {
        "identity_namespace": "toyota-gtsplus-can-bus-check",
        "focus_component_t76_indexes": list(TOPOLOGY_FOCUS_T76_INDEXES),
        "identity_note": (
            "bus_index/bus_name/gateway_names are Toyota CDbCanBusNameTable/CDbCanBusListTable identities "
            "(for example 'Bus 1' and 'Bus 4' behind 'Central Gateway'). They are network-model identities, "
            "not comma panda bus numbers and not connector cavity numbers; see "
            "docs/tooling/panda-toyota-routing.md for the separate panda naming layers."
        ),
        "component_name_join": (
            "component_index+1 -> CDbSubBusConfirmationCGWTable name ('Power Steering (EPS)' etc.) is a naming "
            "correspondence, not an ECUNo key join; only the Camry 0x6D/0x29/0x32 membership is independently "
            "pinned by repo evidence in docs/variants/camry-2026-live-baseline.md."
        ),
        "regions": {},
    }
    for region in REGIONS:
        frc_vehicle_types = {
            row["vehicle_id"]: row["vehicle_name"]
            for row in fleet[region]["install_rows"]
        }
        topology["regions"][region] = canbus_topology_region(parser, root, region, frc_vehicle_types)

    decision_tables = {}
    for region in REGIONS:
        db_root = gts_db_root(root, region, "Gen")
        master = parser.parse_master_db(db_root / "Toyota.ddb")
        decision_tables[region] = {
            "CDbVehicleDecisionTable_rows_41": len(list(records(master.sections[41]))),
            "CDbVinVehicleDecisionTable_rows_59": len(list(records(master.sections[59]))),
        }

    return {
        "schema": "gtsplus-tss3-crossvehicle-surface-v2",
        "title": "Current GTS+ cross-vehicle TSS3 architecture and topology census",
        "gtsplus_version": versions["GTS+"],
        "gtsplus_db_version": versions["GTS+ DB"],
        "fleet_category_498_architecture": fleet,
        "category_identities": identities,
        "category_families": category_family_section(fleet),
        "diagnostic_addresses": addresses,
        "can_bus_check_topology": topology,
        "region_local_boundaries": {
            "install_set_id_namespaces": install_set_collision_proof(parser, root),
            "master_vehicle_decision_tables": {
                "note": (
                    "CDbVehicleDecisionTable (41) and CDbVinVehicleDecisionTable (59) are present in every "
                    "regional master, but their row layout is not deterministically recovered. The census "
                    "joins only decoded tables (43/5/44/16 plus CAN Bus Check 75-79/55); no decision semantics "
                    "are inferred from these tables."
                ),
                "row_counts_per_region": decision_tables,
            },
        },
        "pcs_data_viewer": pcs_data_viewer(root, versions),
        "tse_converter": tse_converter(root, versions),
        "adcu_p6_successor_surface": adcu_p6(parser, root, versions),
        "generalization_boundaries": {
            "tss3_is_not_one_steering_topology": (
                "Category 498 FRC_P5 spans multiple selected install-set architectures. EMPS2_P5/Steering Actuator "
                "category 499 is present only in a minority of category-498 rows, so Steering Actuator is not an "
                "intrinsic requirement of the TSS3 diagnostic generation."
            ),
            "region_local_install_sets": (
                "Architecture is joined through vehicle/install-set/category membership per regional master. Numeric "
                "install-set IDs are region-local and must not be transferred between NA/EU/JP by number alone; "
                "region_local_boundaries.install_set_id_namespaces exhibits concrete collisions."
            ),
            "unjoined_p5_longitudinal_databases": {
                "categories": no_frc_cooccurrence,
                "meaning": (
                    "Current master install rows containing FRC_P5 category 498 have zero selected-category "
                    "co-occurrence with PCS1_P5(427), DSSystem_P5(428), Fr_RadSen_P5(429), RoadSign_P5(431), or "
                    "PCS2_P5(432) in NA/EU/JP. Those databases may still be useful Toyota vocabulary, but their P5 "
                    "generation alone is not evidence that they are members of the category-498 TSS3 architecture."
                ),
            },
            "diagnostic_address_generation_boundary": (
                "The ECUNo->diagnostic-request-address join is read from the v18 IT3Data_BDC ECU_Setting_Table "
                "because current GTS+ ships no equivalent table. Addresses are physical UDS request IDs (0x7xx "
                "range), not panda bus numbers, and cross-generation stability of each address is only observed "
                "where repo captures corroborate it (Camry 2026 FRC 0x792, EPS 0x7A1, skid 0x7B0)."
            ),
            "topology_is_gateway_identity_not_panda_bus": (
                "CAN Bus Check bus_index/bus_name/gateway_names describe Toyota's Central-Gateway network model. "
                "They must not be relabeled as panda bus numbers; the panda harness dimension is tracked "
                "separately in docs/tooling/panda-toyota-routing.md."
            ),
            "host_decoder_not_wire_owner": (
                "PCS Data Viewer/TSE parser structure proves Toyota knows how to decode saved recorder data. It does "
                "not by itself identify CAN arbitration IDs, ECU-side producer transforms, SecOC signing ownership, "
                "or a one-to-one mapping from resource keys to FRC proprietary AB/EB records."
            ),
        },
    }


def write_install_set_csv(payload: dict[str, Any], path: Path) -> None:
    import csv

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "region",
            "vehicle_id",
            "vehicle_name",
            "install_set_id",
            "install_set_id_hex",
            "architecture_label",
            "selected_category_ids",
        ])
        for region in REGIONS:
            for row in payload["fleet_category_498_architecture"][region]["install_rows"]:
                writer.writerow([
                    region,
                    row["vehicle_id"],
                    row["vehicle_name"],
                    row["install_set_id"],
                    f"0x{row['install_set_id']:04X}",
                    row["architecture_label"],
                    " ".join(str(cid) for cid in row["selected_category_ids"]),
                ])


def decode_bus_clusters(shape: dict[str, Any]) -> list[tuple[int, list[tuple[str, str]]]]:
    """Decode a compact shape into [(bus_index, [(component_hex, junction), ...])]."""
    clusters = []
    for cluster in shape["bus_clusters"]:
        bus_text, _, body = cluster.partition("|")
        components = []
        for token in body.split(","):
            component_hex, _, junction = token.partition(":")
            components.append((component_hex, junction))
        clusters.append((int(bus_text), components))
    return clusters


def write_topology_csv(payload: dict[str, Any], path: Path) -> None:
    """One row per (region, topology group, component placement).

    Group-level dedup: the vehicle -> car -> group join lives in the JSON
    (can_bus_check_topology.regions.<region>.vehicle_topology), and shapes
    store compact per-bus component clusters; this writer expands them back
    into flat placement rows using the region bus-identity and domain tables.
    """
    import csv

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "region",
            "topology_group_key",
            "shape_sha256",
            "component_hex",
            "component_index",
            "ecu_domain",
            "bus_index",
            "bus_name",
            "gateway_names",
            "junction_name",
        ])
        for region in REGIONS:
            region_topology = payload["can_bus_check_topology"]["regions"][region]
            for entry in region_topology["placement_shapes"]:
                for group_key in entry["topology_group_keys"]:
                    for bus_index, components in decode_bus_clusters(entry):
                        identity = region_topology["bus_identities"][str(bus_index)]
                        for component_hex, junction in components:
                            writer.writerow([
                                region,
                                group_key,
                                entry["shape_sha256"],
                                component_hex,
                                int(component_hex, 16),
                                region_topology["component_domains"].get(component_hex, ""),
                                bus_index,
                                identity["bus_name"],
                                "|".join(identity["gateway_names"]),
                                junction,
                            ])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_install_set_csv(payload, args.output.parent / "tss3_crossvehicle_fleet_install_sets.csv")
    write_topology_csv(payload, args.output.parent / "tss3_crossvehicle_canbus_placements.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
