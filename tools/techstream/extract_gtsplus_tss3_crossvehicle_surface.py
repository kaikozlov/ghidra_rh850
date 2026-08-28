#!/usr/bin/env python3
"""Extract cross-vehicle TSS3 architecture and recorder/viewer evidence from current GTS+.

This intentionally records the fleet-level joins that are easy to rediscover and
forget: category-498 install-set architecture breadth, the PCS Data Viewer TSS3
FFD resource surface, the TSE/GTSE parser/layout surface, and the P6 successor
boundary.  It does not infer ECU-side producer ownership from host metadata.
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
from parse_ddb import DDBParser, ECU_TABLE_CLASS_NAMES
from pe_utils import binary_strings
from techstream_paths import gts_db_root, resolve_gts_root

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

    architecture_counts = Counter(tuple(row["architecture"]) for row in rows)
    architectures = []
    for architecture, count in sorted(
        architecture_counts.items(), key=lambda item: (-item[1], item[0])
    ):
        models = sorted({row["vehicle_name"] for row in rows if tuple(row["architecture"]) == architecture})
        architectures.append({
            "selected_category_ids": list(architecture),
            "selected_categories": [cats[cid] for cid in architecture if cid in cats],
            "install_row_count": count,
            "model_names": models,
        })

    cooccurrence = Counter()
    for row in rows:
        for cid in row["architecture"]:
            cooccurrence[cid] += 1

    return {
        "source": {
            "master": source(db_root / "Toyota.ddb", root),
            "strings": source(db_root / "M_English.ddb", root),
        },
        "frc_p5_install_row_count": len(rows),
        "frc_p5_model_name_count": len({row["vehicle_name"] for row in rows}),
        "architecture_count": len(architectures),
        "architectures": architectures,
        "selected_category_cooccurrence_counts": {
            str(cid): cooccurrence.get(cid, 0) for cid in SELECTED_CATEGORY_IDS
        },
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

    return {
        "schema": "gtsplus-tss3-crossvehicle-surface-v1",
        "title": "Current GTS+ cross-vehicle TSS3 architecture and recorder surface",
        "gtsplus_version": versions["GTS+"],
        "gtsplus_db_version": versions["GTS+ DB"],
        "fleet_category_498_architecture": fleet,
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
                "install-set IDs are region-local and must not be transferred between NA/EU/JP by number alone."
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
            "host_decoder_not_wire_owner": (
                "PCS Data Viewer/TSE parser structure proves Toyota knows how to decode saved recorder data. It does "
                "not by itself identify CAN arbitration IDs, ECU-side producer transforms, SecOC signing ownership, "
                "or a one-to-one mapping from resource keys to FRC proprietary AB/EB records."
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
