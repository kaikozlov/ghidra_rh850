#!/usr/bin/env python3
"""Extract the Techstream P5 lateral-control evidence surface (schema v5).

Directed evidence pass over the true-TSS3 Front Recognition Camera 2
(``FRC_P5``) path, its dedicated read-only Operation/Image FFD plugin DLLs,
the secondary Advanced Drive Control (``ADS_Eth_P5``) DDR snapshot domain,
and the steering-side ``EMPS_P5``/``EMPS2_P5`` observer family.

Every claim pinned here is re-derived from the raw corpus at generation time:
database/category/record identities come from the DDB files, protocol claims
carry exact machine-code byte anchors that are asserted against the pinned
plugin DLL images, and unit resolution follows the
CDbPhyData/CDbUnit lookup chain that ``GetADSDDRInfoP5_DT.dll`` performs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path

import pefile
from parse_ddb import DDBParser

REPO = Path(__file__).resolve().parents[2]
TECHROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
FACTORY = REPO / "data/generated/techstream_v18/ddb_factory_table_map.json"
H_CORR = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
DEFAULT_OUT = REPO / "data/generated/techstream_v18/p5_lateral_control_semantics.json"

REGIONS = ("NA", "EU", "JP")
TARGET_DATABASES = (
    "EMPS_P5.ddb",
    "EMPS2_P5.ddb",
    "LDA_P5.ddb",
    "Fr_Camera_P5.ddb",
    "ADS_Eth_P5.ddb",
    "ADeU_Eth_P5.ddb",
    "FRC_P5.ddb",
    "ABS_P5.ddb",
    "Brk_Bst_P5.ddb",
    "EPB_P5.ddb",
)
TARGET_DLLS = (
    "KgpDataCtrl.dll",
    "GetTSS3ImageFFDP5_DT.dll",
    "GetTSS3OperationFFDP5_DT.dll",
    "GetADSDDRInfoP5_DT.dll",
    "GetADSOperationFFDP5_DT.dll",
    "GetDatMonSignalInfoP5_DT.dll",
    "CommandCommon.dll",
    "GetRoutineActTstInitP5_DT.dll",
    "GetRoutineActTstSignalInfoP5_DT.dll",
    "SingleRoutineActTstP5_DT.dll",
)
ADS_NAMES = (
    "Advanced Drive Control Target Steering Angle Speed Order Value",
    "Advanced Drive Control Target Steering Angle Order Value",
    "Lateral Control Switch Status",
)
LDA_SIGNATURES = ("X2008", "X2073", "X2081", "X2082")
EMPS_MONITORS = tuple(range(2069, 2077))
FRC_BEHAVIOR_SIGNATURES = ("X2400", "X2001", "X2082", "X2166", "X2167", "X216E", "XF01B")
# FRC_P5 type-62 data rows pinned as the LTA/LDA lateral-control surface.
FRC_DID_ROWS = (
    (0x1202, 12, 12, "LDA Installation Availability"),
    (0x1202, 13, 13, "LTA Installation Availability"),
    (0x1202, 14, 14, "LCA Installation Availability"),
    (0x1501, 0, 7, "LDA Customize Condition Flag"),
    (0x1501, 8, 15, "LDA Control Condition"),
    (0x1601, 0, 7, "LTA Switch Condition Flag"),
    (0x1601, 8, 15, "LTA Control Condition"),
    (0x1601, 16, 23, "Hands-Off Customize Condition Flag"),
    (0x1601, 24, 31, "Hands-Off Control Condition"),
    (0x1308, 0, 7, "Steering Wheel Information"),
    (0x1806, 0, 7, "Control Target Type (For DDR)"),
    (0x1903, 0, 7, "Control Mode"),
    (0x1909, 0, 31, "Forward Vehicle Lateral Position"),
    (0x1804, 0, 31, "Control Target Vehicle Distance (DDR)"),
    (0x1805, 0, 31, "Control Target Side Position (DDR)"),
    (0x1402, 0, 7, "AHB Control ON Information"),
    (0x1401, 0, 7, "AHB/AHS Information"),
    (0x1681, 0, 7, "LCA Customize Condition Flag"),
    (0x1681, 8, 15, "LCA Control Condition"),
    (0x1705, 12, 12, "PCS AES Invalid Flag"),
)
# The four NA installing-ECU-list grouping keys where categories 498 (FRC_P5)
# and 499 (EMPS2_P5) co-occur.
FRC_COOCCURRENCE_KEYS = (0x1967, 0x1B1A, 0x1D54, 0x1E6E)

# VDS (raw Jet-format vehicle descriptor database) scan constants. The scan is
# pure Python on purpose: no external Java/JAR dependency is used or required.
VDS_PAGE_SIZE = 4096
VDS_DATA_PAGE_INDICATOR = 0x01
VDS_ROW_COUNT_OFFSET = 0x0C
VDS_ROW_OFFSET_TABLE_OFFSET = 0x0E
VDS_ROW_OFFSET_MASK = 0x0FFF
VDS_SETTING_TABLE_COLUMN_COUNT = 5
VDS_SETTING_TABLE_ROW_FIELDS_END = 0x24  # 2 + 4 + 4 + 4 + 22
# Setting_Table rows are 64 bytes, so at most ~62 fit in one 4096-byte page;
# 100 is the validated structural sanity bound used by the reproduced scan.
VDS_ROW_COUNT_SANITY_BOUND = 100
VDS_VIN_PATTERN_RE = re.compile(r"[A-Z0-9_]{11}")
VDS_TARGET_ECU_NOS = (498, 499)
VDS_EXPECTED = {
    "NA": {498: (52, 1923), 499: (0, 0)},
    "EU": {498: (9, 27), 499: (0, 0)},
    "JP": {498: (39, 4212), 499: (0, 0)},
}
VDS_PINNED_NA_5YF_PATTERNS = (
    "5YFB4MBE___",
    "5YFB4MCE___",
    "5YFB4MDE___",
    "5YFP4MCE___",
    "5YFS4MCE___",
    "5YFT4MCE___",
)
VDS_PINNED_5YF_ROW_COUNT = 60
VDS_REPRESENTATIVE = {
    "pattern": "5YFB4MBE___",
    "page_index_zero_based": 1189,
    "slot": 18,
    "setting_no": 42,
    "connection_type": 6,
}
# ECU_Setting_Table raw anchors on NA page 20 (0-based): 40-byte rows whose
# fixed tail is shared; ECUNo is u32 +0x02, Phase u32 +0x06 (=5), and the
# diagnostic request Address is the 3-byte ASCII payload after the FF FE
# compressed-Unicode marker at +0x1A.
VDS_ECU_SETTING_ANCHORS = (
    {
        "page_index_zero_based": 20,
        "slot": 8,
        "ecu_no": 405,
        "database": "EMPS_P5",
        "phase": 5,
        "address": "7A1",
        "raw_sha256": "1c4dbd01d8f2a08e387d88d8f1995f5dc558a17528da73688662f50c40995691",
    },
    {
        "page_index_zero_based": 20,
        "slot": 24,
        "ecu_no": 498,
        "database": "FRC_P5",
        "phase": 5,
        "address": "792",
        "raw_sha256": "8e0b4d4c25d6f9aa5a960d745b735a8b77f097b57ca7a3832900c8b03a10970a",
    },
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def records(section) -> list[bytes]:
    size = section.decoded_record_size
    data = section.decoded_data
    return [data[i * size : (i + 1) * size] for i in range(section.header.record_count)]


def u16(raw: bytes, off: int) -> int:
    return struct.unpack_from("<H", raw, off)[0]


def u32(raw: bytes, off: int) -> int:
    return struct.unpack_from("<I", raw, off)[0]


def did_str(value: int) -> str:
    return f"0x{value:04X}"


# ── source identities ────────────────────────────────────────────────────────


def source_identities(root: Path) -> dict:
    out: dict = {}
    for name in TARGET_DATABASES:
        out[name] = {
            region: {
                "size": (root / region / "DB" / name).stat().st_size,
                "sha256": sha256((root / region / "DB" / name).read_bytes()),
            }
            for region in REGIONS
        }
    for name in TARGET_DLLS:
        data = (root / "bin" / name).read_bytes()
        out[name] = {"size": len(data), "sha256": sha256(data)}
    for region in REGIONS:
        data = (root / f"DB/MDB/IT3Data_BDC_{region}.vds").read_bytes()
        out[f"IT3Data_BDC_{region}.vds"] = {"size": len(data), "sha256": sha256(data)}
    return out


# ── VDS Setting_Table scan (pure Python, raw Jet pages) ─────────────────────


def vds_setting_table_rows(path: Path, ecu_no: int) -> list[dict]:
    """Scan a raw Jet-format VDS file for Setting_Table rows of one ECUNo.

    Layout as reproduced from the raw pages: 4096-byte pages; data pages have
    byte 0 == 1; the row count is u16 at +0x0C; the row-offset table is u16
    entries from +0x0E (low 12 bits, descending addresses). Candidate
    Setting_Table rows start with u16 column count 5, then u32 SettingNo
    (+0x02), u32 ECUNo (+0x06), u32 ConnectionType (+0x0A), and a fixed
    11-character UTF-16LE VIN pattern at +0x0E.
    """
    data = path.read_bytes()
    out: list[dict] = []
    for page_index in range(len(data) // VDS_PAGE_SIZE):
        page = data[page_index * VDS_PAGE_SIZE : (page_index + 1) * VDS_PAGE_SIZE]
        if page[0] != VDS_DATA_PAGE_INDICATOR:
            continue
        row_count = u16(page, VDS_ROW_COUNT_OFFSET)
        if row_count == 0 or row_count > VDS_ROW_COUNT_SANITY_BOUND:
            continue
        for slot in range(row_count):
            offset = (
                u16(page, VDS_ROW_OFFSET_TABLE_OFFSET + 2 * slot) & VDS_ROW_OFFSET_MASK
            )
            if offset + VDS_SETTING_TABLE_ROW_FIELDS_END > VDS_PAGE_SIZE:
                continue
            row = page[offset:]
            if u16(row, 0x00) != VDS_SETTING_TABLE_COLUMN_COUNT:
                continue
            if u32(row, 0x06) != ecu_no:
                continue
            try:
                pattern = row[0x0E : 0x0E + 22].decode("utf-16-le")
            except UnicodeDecodeError:
                continue
            if len(pattern) != 11 or not VDS_VIN_PATTERN_RE.fullmatch(pattern):
                continue
            out.append(
                {
                    "page_index_zero_based": page_index,
                    "slot": slot,
                    "setting_no": u32(row, 0x02),
                    "ecu_no": u32(row, 0x06),
                    "connection_type": u32(row, 0x0A),
                    "vin_pattern": pattern,
                    "raw36_sha256": sha256(row[:VDS_SETTING_TABLE_ROW_FIELDS_END]),
                }
            )
    return out


def vds_ecu_setting_anchors(root: Path) -> list[dict]:
    """Re-read the pinned NA ECU_Setting_Table rows from raw page 20."""
    data = (root / "DB/MDB/IT3Data_BDC_NA.vds").read_bytes()
    out = []
    for anchor in VDS_ECU_SETTING_ANCHORS:
        page = data[
            anchor["page_index_zero_based"] * VDS_PAGE_SIZE : (
                anchor["page_index_zero_based"] + 1
            )
            * VDS_PAGE_SIZE
        ]
        if page[0] != VDS_DATA_PAGE_INDICATOR:
            raise ValueError("VDS ECU_Setting anchor page is not a data page")
        slot = anchor["slot"]
        offset = u16(page, VDS_ROW_OFFSET_TABLE_OFFSET + 2 * slot) & VDS_ROW_OFFSET_MASK
        row = page[offset : offset + 40]
        marker = row.find(b"\xff\xfe")
        if marker < 0:
            raise ValueError("VDS ECU_Setting anchor row lacks FF FE marker")
        address = row[marker + 2 : marker + 5].decode("ascii")
        checks = {
            "ecu_no": u32(row, 0x02),
            "phase": u32(row, 0x06),
            "address": address,
            "raw_sha256": sha256(row),
        }
        for field, expected in (
            ("ecu_no", anchor["ecu_no"]),
            ("phase", anchor["phase"]),
            ("address", anchor["address"]),
            ("raw_sha256", anchor["raw_sha256"]),
        ):
            if checks[field] != expected:
                raise ValueError(
                    f"VDS ECU_Setting anchor slot {slot}: {field}="
                    f"{checks[field]!r}, expected {expected!r}"
                )
        out.append(
            {
                "page_index_zero_based": anchor["page_index_zero_based"],
                "slot": slot,
                "row_offset": offset,
                "ecu_no": anchor["ecu_no"],
                "database": anchor["database"],
                "phase": anchor["phase"],
                "address": anchor["address"],
                "raw40_sha256": anchor["raw_sha256"],
                "row_layout": {
                    "column_count": "u16 +0x00",
                    "ecu_no": "u32 +0x02",
                    "phase": "u32 +0x06",
                    "address": "3-byte ASCII after FF FE marker at +0x1A",
                },
            }
        )
    return out


def vds_setting_table_evidence(root: Path) -> dict:
    regions: dict[str, dict] = {}
    representative = None
    for region in REGIONS:
        path = root / f"DB/MDB/IT3Data_BDC_{region}.vds"
        region_node: dict = {"file": path.name}
        for ecu_no in VDS_TARGET_ECU_NOS:
            rows = vds_setting_table_rows(path, ecu_no)
            pattern_counts = dict(
                sorted(Counter(r["vin_pattern"] for r in rows).items())
            )
            expected_patterns, expected_rows = VDS_EXPECTED[region][ecu_no]
            if (len(pattern_counts), len(rows)) != (expected_patterns, expected_rows):
                raise ValueError(
                    f"{region} VDS ECUNo={ecu_no}: got {len(pattern_counts)} patterns / "
                    f"{len(rows)} rows, expected {expected_patterns} / {expected_rows}"
                )
            region_node[str(ecu_no)] = {
                "setting_table_rows": len(rows),
                "vin_pattern_count": len(pattern_counts),
                "vin_pattern_row_counts": pattern_counts,
            }
            if region == "NA" and ecu_no == 498:
                for pattern in VDS_PINNED_NA_5YF_PATTERNS:
                    if pattern_counts.get(pattern) != VDS_PINNED_5YF_ROW_COUNT:
                        raise ValueError(
                            f"NA VDS pattern {pattern}: "
                            f"{pattern_counts.get(pattern)} rows, expected {VDS_PINNED_5YF_ROW_COUNT}"
                        )
                for row in rows:
                    if (
                        row["vin_pattern"] == VDS_REPRESENTATIVE["pattern"]
                        and row["page_index_zero_based"]
                        == VDS_REPRESENTATIVE["page_index_zero_based"]
                        and row["slot"] == VDS_REPRESENTATIVE["slot"]
                    ):
                        representative = row
        regions[region] = region_node
    if representative is None or (
        representative["setting_no"],
        representative["ecu_no"],
        representative["connection_type"],
    ) != (
        VDS_REPRESENTATIVE["setting_no"],
        498,
        VDS_REPRESENTATIVE["connection_type"],
    ):
        raise ValueError("NA VDS representative row did not reproduce")
    return {
        "scanner": "pure-Python raw Jet page scan (no external Java/JAR dependency)",
        "page_size": VDS_PAGE_SIZE,
        "page_layout": {
            "data_page_indicator": "byte0 == 0x01",
            "row_count": "u16 +0x0C",
            "row_offset_table": "u16 entries from +0x0E, low 12 bits, descending addresses",
            "row_count_sanity_bound": VDS_ROW_COUNT_SANITY_BOUND,
        },
        "setting_table_row_layout": {
            "column_count": "u16 +0x00 (== 5)",
            "setting_no": "u32 +0x02",
            "ecu_no": "u32 +0x06",
            "connection_type": "u32 +0x0A",
            "vin_pattern": "11-char UTF-16LE at +0x0E",
        },
        "regions": regions,
        "pinned_na_5yf_families": {
            "patterns": list(VDS_PINNED_NA_5YF_PATTERNS),
            "rows_each": VDS_PINNED_5YF_ROW_COUNT,
        },
        "representative_row": representative,
        "ecu_setting_table_anchors": vds_ecu_setting_anchors(root),
        "boundary": (
            "VDS proves ECUNo/category 498 is configured for these VIN descriptor patterns "
            "in the Techstream Setting_Table; ECUNo 499 has zero Setting_Table rows in all "
            "three regions, which is VDS Setting_Table absence, not vehicle absence. The 5YF "
            "entries are exact NA descriptor families; no repository-verified Toyota source "
            "joins them to a model name, so they are not labeled by model from VDS alone."
        ),
    }


# ── master database identities ───────────────────────────────────────────────


def master_categories(parser: DDBParser, root: Path, region: str) -> dict[str, dict]:
    master = parser.parse_master_db(root / region / "DB/Toyota.ddb")
    strings = parser.load_string_db(root / region / "DB/M_English.ddb")
    categories = parser.extract_master_ecu_categories(master.sections[16])
    out: dict[str, dict] = {}
    for target in TARGET_DATABASES:
        matches = [
            (i, row) for i, row in enumerate(categories) if row.database_name == target
        ]
        if len(matches) != 1:
            raise ValueError(
                f"{region}: expected one Toyota.ddb category for {target}, got {len(matches)}"
            )
        index, row = matches[0]
        out[target] = {
            "record_index": index,
            "category_id": row.category_id,
            "generation": row.generation,
            "resolved_ecu_name": strings.get_string(row.ecu_name_string_index),
            "raw_sha256": sha256(row.raw),
        }
    return out


def category_498_dll_roles(parser: DDBParser, root: Path, region: str) -> list[dict]:
    """All master plugin roles bound to category 498 (FRC_P5), plus the
    category-0/global ADS DDR role for contrast."""
    master = parser.parse_master_db(root / region / "DB/Toyota.ddb")
    dlls = parser.extract_master_dlls(master.sections[19])
    rows = [
        {
            "dll_name": r.dll_name,
            "category_id": r.category_id,
            "dll_role_id": r.dll_role_id,
        }
        for r in dlls
        if r.category_id == 498 or (r.dll_name == "GetADSDDRInfoP5_DT.dll")
    ]
    rows.sort(key=lambda r: (r["category_id"], r["dll_role_id"], r["dll_name"]))
    role_ids = {r["dll_role_id"] for r in rows if r["category_id"] == 498}
    # Active-Test exposure: role 6 list, role 8 init, role 112 signal info,
    # role 99 multi-act init, role 173 datamon-for-act-test.
    for required in (6, 8, 112, 99, 173):
        if required not in role_ids:
            raise ValueError(
                f"{region}: category-498 Active-Test role {required} missing"
            )
    ads = [r for r in rows if r["dll_name"] == "GetADSDDRInfoP5_DT.dll"]
    if len(ads) != 1 or ads[0]["category_id"] != 0:
        raise ValueError(
            f"{region}: ADS DDR role 229 is not the category-0/global entry"
        )
    return rows


def master_dll_roles(parser: DDBParser, root: Path, region: str) -> list[dict]:
    master = parser.parse_master_db(root / region / "DB/Toyota.ddb")
    dlls = parser.extract_master_dlls(master.sections[19])
    rows = [
        {
            "dll_name": row.dll_name,
            "category_id": row.category_id,
            "dll_role_id": row.dll_role_id,
        }
        for row in dlls
        if row.dll_name in TARGET_DLLS
    ]
    if {r["dll_name"] for r in rows} != set(TARGET_DLLS) - {
        "KgpDataCtrl.dll",
        "CommandCommon.dll",
    }:
        raise ValueError(f"{region}: incomplete TSS3/ADS plugin role table")
    return sorted(rows, key=lambda r: (r["dll_name"], r["category_id"]))


def master_table_rows(master, table_type: int) -> list[bytes]:
    return records(master.sections[table_type])


def vehicle_names(master, strings) -> dict[int, str]:
    """Type-43 CDbVehicleNameTable: VehicleId u16 +0x04 -> name string u32 +0x00."""
    out: dict[int, str] = {}
    for raw in master_table_rows(master, 43):
        out[u16(raw, 0x04)] = strings.get_string(u32(raw, 0x00))
    return out


def vehicle_install_sets(master) -> dict[int, set[int]]:
    """Type-5 CDbEcuGroupTable: VehicleId u16 +0x04 -> install-set id u16 +0x06."""
    out: dict[int, set[int]] = {}
    for raw in master_table_rows(master, 5):
        out.setdefault(u16(raw, 0x04), set()).add(u16(raw, 0x06))
    return out


def installing_ecu_list(parser: DDBParser, root: Path, region: str) -> dict:
    """Decode the master type-44 CDbInstallingEcuListTable install-set rows.

    The +0x04 field is the install-set id (the lookup key of
    ``CDbInstallingEcuListTable::FindDbItem1``); the chain
    type-5 VehicleId -> install-set id -> type-44 rows, plus the type-43
    VehicleName table, deterministically resolves each install set to model
    names. The +0x06 field is the ECU category.
    """
    master = parser.parse_master_db(root / region / "DB/Toyota.ddb")
    strings = parser.load_string_db(root / region / "DB/M_English.ddb")
    section = master.sections[44]
    if section.decoded_record_size != 24:
        raise ValueError(
            f"{region}: type-44 record size {section.decoded_record_size}, expected 24"
        )
    by_key: dict[int, dict[int, str]] = {}
    for raw in records(section):
        grouping_key = u16(raw, 0x04)
        category = u16(raw, 0x06)
        display = strings.get_string(u32(raw, 0x00))
        by_key.setdefault(grouping_key, {})[category] = display

    vnames = vehicle_names(master, strings)
    vid_sets = vehicle_install_sets(master)
    set_names: dict[int, set[str]] = {}
    for vid, sets in vid_sets.items():
        name = vnames.get(vid)
        if name is None:
            continue
        for iset in sets:
            set_names.setdefault(iset, set()).add(name)
    valid_vids = sum(1 for vid in vid_sets if vid in vnames)

    cooccur = sorted(k for k, cats in by_key.items() if 498 in cats and 499 in cats)
    return {
        "table_type": 44,
        "factory_class": "CDbInstallingEcuListTable",
        "record_size": section.decoded_record_size,
        "record_count": section.header.record_count,
        "field_offsets": {
            "display_name_string_index": "u32 +0x00",
            "install_set_id": "u16 +0x04 (FindDbItem1 lookup key)",
            "category": "u16 +0x06 (ECU category)",
        },
        "vehicle_resolution_chain": {
            "type5_class": "CDbEcuGroupTable",
            "type5_vehicle_id_offset": "u16 +0x04",
            "type5_install_set_id_offset": "u16 +0x06",
            "type43_class": "CDbVehicleNameTable",
            "type43_vehicle_id_offset": "u16 +0x04",
            "type43_name_string_offset": "u32 +0x00",
            "type5_vehicle_ids_resolving_to_type43_names": f"{valid_vids}/{len(vid_sets)}",
        },
        "cooccurrence_keys": [f"0x{k:04X}" for k in cooccur],
        "cooccurrence_sets": [
            {
                "install_set_id": f"0x{k:04X}",
                "vehicle_names": sorted(set_names.get(k, set())),
                "categories": sorted(by_key[k]),
                "displays": {str(c): by_key[k][c] for c in sorted(by_key[k])},
            }
            for k in cooccur
        ],
        "key_sets": {
            f"0x{k:04X}": {
                "categories": sorted(by_key[k]),
                "displays": {str(c): by_key[k][c] for c in sorted(by_key[k])},
            }
            for k in cooccur
        },
    }


# Exact NA model joins for Corolla-family chassis that install FRC_P5 (498).
COROLLA_MODEL_INSTALL_SETS = (
    ("Corolla", 0x30E0, 0x1D78, (405, 435, 445, 452, 498)),
    ("Corolla", 0x30E1, 0x1D7B, (405, 435, 445, 452, 498)),
    ("Corolla", 0x30E4, 0x1D84, (405, 435, 445, 452, 498)),
    ("Corolla", 0x30FE, 0x1DD2, (405, 435, 445, 452, 498)),
    ("Corolla", 0x30FF, 0x1DD5, (405, 435, 445, 452, 498)),
    ("Corolla HV", 0x30E2, 0x1D7E, (405, 435, 445, 452, 466, 498)),
    ("Corolla HV", 0x30E3, 0x1D81, (405, 435, 445, 452, 466, 498)),
    ("Corolla Cross", 0x311F, 0x1E35, (118, 405, 435, 445, 452, 498, 5005)),
    ("Corolla Cross", 0x3120, 0x1E38, (118, 405, 435, 445, 452, 498, 5005)),
    ("Corolla Cross HEV", 0x3121, 0x1E3B, (405, 435, 445, 452, 466, 498, 5005)),
    ("GR Corolla", 0x3082, 0x1C5E, (142, 435, 445, 448, 452, 498)),
)


def corolla_model_install_sets(parser: DDBParser, root: Path) -> dict:
    """NA type-43/type-5/type-44 join for Corolla-family FRC_P5 chassis."""
    master = parser.parse_master_db(root / "NA/DB/Toyota.ddb")
    strings = parser.load_string_db(root / "NA/DB/M_English.ddb")
    vnames = vehicle_names(master, strings)
    vid_sets = vehicle_install_sets(master)
    set_cats: dict[int, set[int]] = {}
    for raw in master_table_rows(master, 44):
        set_cats.setdefault(u16(raw, 0x04), set()).add(u16(raw, 0x06))
    rows = []
    for name, vid, iset, expected_cats in COROLLA_MODEL_INSTALL_SETS:
        if vnames.get(vid) != name:
            raise ValueError(
                f"NA type-43 vid 0x{vid:04X} is {vnames.get(vid)!r}, expected {name!r}"
            )
        if iset not in vid_sets.get(vid, set()):
            raise ValueError(
                f"NA type-5 vid 0x{vid:04X} does not reference set 0x{iset:04X}"
            )
        cats = set_cats.get(iset, set())
        if tuple(sorted(cats)) != expected_cats:
            raise ValueError(
                f"NA install set 0x{iset:04X} categories {sorted(cats)} != {list(expected_cats)}"
            )
        if 498 not in cats or 499 in cats:
            raise ValueError(f"NA install set 0x{iset:04X} must carry 498 without 499")
        rows.append(
            {
                "model_name": name,
                "vehicle_id": f"0x{vid:04X}",
                "install_set_id": f"0x{iset:04X}",
                "categories": list(expected_cats),
            }
        )
    return {
        "region": "NA",
        "join": "type-43 VehicleName -> type-5 VehicleId/install-set -> type-44 categories",
        "rows": rows,
        "finding": (
            "Newer Corolla-family TSS3 configurations pair FRC_P5 (498) with EMPS_P5 (405) "
            "steering; EMPS2_P5 (499) is absent from these Corolla/HV/Cross/GR install sets. "
            "GR Corolla uses category 142 (display name EMPS) instead of 405."
        ),
    }


# ── FRC_P5: the true-TSS3 front camera 2 diagnostic surface ─────────────────


def frc_did_rows(parser: DDBParser, root: Path, region: str) -> list[dict]:
    db = parser.parse_ecu_db(root / region / "DB/FRC_P5.ddb")
    strings = parser.load_string_db(root / region / "DB/M_English.ddb")
    wanted = {(did, start, end, name) for did, start, end, name in FRC_DID_ROWS}
    out = []
    for index, raw in enumerate(records(db.sections[62])):
        did = u16(raw, 0x36)
        start, end = u16(raw, 0x2C), u16(raw, 0x2E)
        name = strings.get_string(u32(raw, 0x18))
        if (did, start, end, name) in wanted:
            out.append(
                {
                    "record_index": index,
                    "data_id": did_str(did),
                    "alternate_data_id": did_str(u16(raw, 0x38)),
                    "bit_range": [start, end],
                    "monitor_key": u16(raw, 0x24),
                    "name": name,
                    "raw_sha256": sha256(raw),
                }
            )
    if len(out) != len(FRC_DID_ROWS):
        raise ValueError(
            f"{region}: matched {len(out)} FRC DID rows, expected {len(FRC_DID_ROWS)}"
        )
    return out


def frc_behavior_rows(parser: DDBParser, root: Path) -> list[dict]:
    db = parser.parse_ecu_db(root / "NA/DB/FRC_P5.ddb")
    strings = parser.load_string_db(root / "NA/DB/M_English.ddb")
    out = []
    for index, row in enumerate(parser.extract_priority_records(db.sections[87])):
        sig = row.fields.get("behavior_signature")
        if sig not in FRC_BEHAVIOR_SIGNATURES:
            continue
        out.append(
            {
                "record_index": index,
                "behavior_signature": sig,
                "name_string_index": row.fields["name_string_index"],
                "name": strings.get_string(row.fields["name_string_index"]),
                "raw_sha256": sha256(row.raw),
            }
        )
    return out


def frc_target_steering_negative(parser: DDBParser, root: Path, region: str) -> dict:
    db = parser.parse_ecu_db(root / region / "DB/FRC_P5.ddb")
    strings = parser.load_string_db(root / region / "DB/M_English.ddb")
    hits: list[dict] = []
    for table_type in (62, 88):
        for index, raw in enumerate(records(db.sections[table_type])):
            name = strings.get_string(u32(raw, 0x18)) or ""
            if "target steering" in name.lower():
                hits.append(
                    {"table_type": table_type, "record_index": index, "name": name}
                )
    return {
        "scanned_table_types": [62, 88],
        "scanned_table_classes": {
            "62": "CDbDatamonitorP5Table",
            "88": "CDbBehaviorDataRecordP5Table",
        },
        "name_substring": "target steering",
        "matches": hits,
    }


def pattern_values(db, strings, patdisp_key: int) -> dict[int, str]:
    """Resolve a type-14 CDbPatDispTable key to its value->display map.

    Verified join: the type-62 monitor record carries the pattern-display key
    at ``+0x32``; type-14 records carry the same key at ``+0x0C``, the pattern
    value at ``+0x04`` (u32), and the display string index at ``+0x00``.
    """
    out: dict[int, str] = {}
    for raw in records(db.sections[14]):
        if u16(raw, 0x0C) == patdisp_key:
            out[u32(raw, 0x04)] = strings.get_string(u32(raw, 0x00))
    return dict(sorted(out.items()))


def emps_target_lateral_id_semantics(parser: DDBParser, root: Path) -> dict:
    """Recover the OEM Target Lateral ID value dictionary used by P5 EMPS."""
    expected = {
        0: "No Request (Manual Operation)",
        1: "PCS",
        4: "LDA",
        10: "Hands Off LTA",
        11: "LTA/LCA",
        13: "DESA (Slow Deceleration Control)",
        15: "DESA (Deceleration Stop Control)",
        18: "SDG",
        19: "PDA",
        25: "AP",
        27: "Remote Parking",
        35: "AD (Lv.3)",
        37: "EM (Lv.3)",
        39: "DES (Lv.3)",
        41: "AD (Lv.4)",
        43: "EM (Lv.4)",
        45: "DES (Lv.4)",
        49: "Self-Propelled Transport",
        63: "Driver Operation",
    }
    regions: dict[str, dict] = {}
    for region in REGIONS:
        strings = parser.load_string_db(root / region / "DB/M_English.ddb")
        region_rows: dict[str, dict] = {}
        for database in ("EMPS_P5.ddb", "EMPS2_P5.ddb"):
            db = parser.parse_ecu_db(root / region / "DB" / database)
            monitors = records(db.sections[62])
            systems = {}
            for monitor_key, name, did in (
                (2069, "Target Lateral ID", 0x1CEE),
                (2073, "Target Lateral ID (System 2)", 0x1CEF),
            ):
                hits = [raw for raw in monitors if u16(raw, 0x24) == monitor_key]
                if len(hits) != 1:
                    raise ValueError(
                        f"{region} {database} monitor {monitor_key} count {len(hits)}"
                    )
                raw = hits[0]
                patdisp_key = u16(raw, 0x32)
                values = pattern_values(db, strings, patdisp_key)
                expected_patdisp_key = 39 if database == "EMPS_P5.ddb" else 29
                if not (
                    strings.get_string(u32(raw, 0x18)) == name
                    and u16(raw, 0x2A) == 1
                    and [u16(raw, 0x2C), u16(raw, 0x2E)] == [0, 7]
                    and u16(raw, 0x36) == did
                    and patdisp_key == expected_patdisp_key
                    and values == expected
                ):
                    raise ValueError(
                        f"{region} {database} {name} semantic dictionary drift"
                    )
                systems["system1" if monitor_key == 2069 else "system2"] = {
                    "monitor_key": monitor_key,
                    "name": name,
                    "primary_data_id": did_str(did),
                    "physical_data_key": u16(raw, 0x2A),
                    "bit_range": [u16(raw, 0x2C), u16(raw, 0x2E)],
                    "pattern_display_key": patdisp_key,
                    "pattern_values": values,
                    "raw_sha256": sha256(raw),
                }
            region_rows[database] = systems
        regions[region] = region_rows
    return {
        "oem_name": "Target Lateral ID",
        "value_dictionary": expected,
        "regions": regions,
        "pattern_display_join": {
            "monitor_record_pattern_display_key_offset": "u16 +0x32 (type 62)",
            "patdisp_table": "type 14 CDbPatDispTable",
            "patdisp_key_offset": "u16 +0x0C",
            "pattern_value_offset": "u32 +0x04",
            "display_string_index_offset": "u32 +0x00",
        },
        "boundary": (
            "This is the exact P5 EMPS diagnostic value dictionary. Joining any non-DID "
            "wire field to it still requires independent target-firmware/dataflow evidence."
        ),
    }


def abs_p5_active_test_surface(parser: DDBParser, root: Path) -> dict:
    """Bound the category-435 Techstream Active-Test surface.

    Type-68 direct Active-Test names/keys and type-71 routine rows are recovered
    from consumer-proven KgpDataCtrl fields.  This is a catalog-level negative:
    it proves the pinned ABS_P5 database exposes brake-actuator tests, not a
    named steering/EPS/ADS/lateral Active Test.  It does not prove those tests
    have no indirect network effects.
    """
    expected_direct = [
        (11, "Motor Relay", 30),
        (12, "Solenoid Relay", 40),
        (25, "Motor Relay", 70),
        (26, "Solenoid Relay", 80),
        (27, "Stop Lamp Relay", 90),
        (28, "EXO", 100),
        (37, "Motor Relay", 120),
        (38, "Solenoid Relay", 130),
        (41, "ECB Main Relay", 150),
        (42, "ECB Solenoid (SLR)", 160),
        (43, "ECB Solenoid (SLA)", 170),
        (44, "Brake Booster Motor", 151),
        (45, "Linear Solenoid (SLM1)", 180),
        (46, "Linear Solenoid (SLM2)", 190),
        (8502, "ABS Solenoid", 1),
        (8503, "ABS Solenoid", 2),
        (8504, "ABS Solenoid", 3),
        (8505, "VSC Solenoid", 4),
        (8506, "VSC Solenoid", 5),
        (8507, "ECB Solenoid", 6),
    ]
    expected_routines = [
        (42000, "EBS Relay", 0x110B, 0, 0, 0, 0, 1),
        (42001, "ABS Solenoid", 0xFFFF, 0, 0, 0, 0, 2),
        (42002, "VSC Solenoid", 0xFFFF, 0, 0, 0, 0, 3),
        (42003, "ECB Solenoid", 0xFFFF, 0, 0, 0, 0, 4),
    ]
    forbidden = ("steer", "eps", "ads", "lateral", "pinion")
    regions: dict[str, dict] = {}
    canonical_direct_hashes = None
    canonical_routine_hashes = None
    for region in REGIONS:
        db = parser.parse_ecu_db(root / region / "DB/ABS_P5.ddb")
        strings = parser.load_string_db(root / region / "DB/M_English.ddb")
        if not (
            db.sections[68].decoded_record_size == 64
            and db.sections[68].header.record_count == 20
            and db.sections[71].decoded_record_size == 64
            and db.sections[71].header.record_count == 4
        ):
            raise ValueError(f"{region}: ABS_P5 Active-Test table census drift")
        direct = []
        for index, raw in enumerate(records(db.sections[68])):
            direct.append(
                {
                    "record_index": index,
                    "lookup_key": u16(raw, 0x20),
                    "active_test_name_string_index": u32(raw, 0x0C),
                    "active_test_name": strings.get_string(u32(raw, 0x0C)),
                    "sort_key": u16(raw, 0x2C),
                    "exception_id": u16(raw, 0x2E),
                    "exception_flag": raw[0x3B],
                    "raw_sha256": sha256(raw),
                }
            )
        direct_tuple = [
            (row["lookup_key"], row["active_test_name"], row["sort_key"])
            for row in direct
        ]
        if direct_tuple != expected_direct:
            raise ValueError(f"{region}: ABS_P5 direct Active-Test catalog drift")

        routines = []
        for index, raw in enumerate(records(db.sections[71])):
            routines.append(
                {
                    "record_index": index,
                    "lookup_key": u16(raw, 0x1E),
                    "active_test_name_string_index": u32(raw, 0x08),
                    "active_test_name": strings.get_string(u32(raw, 0x08)),
                    "routine_id": f"0x{u16(raw, 0x1C):04X}",
                    "routine_command_variable": u16(raw, 0x28),
                    "output_mask_variable": u16(raw, 0x2A),
                    "output_mask_button_variable": u16(raw, 0x2C),
                    "routine_status_pattern_key": u16(raw, 0x2E),
                    "sort_key": u16(raw, 0x38),
                    "raw_sha256": sha256(raw),
                }
            )
        routine_tuple = [
            (
                row["lookup_key"],
                row["active_test_name"],
                int(row["routine_id"], 16),
                row["routine_command_variable"],
                row["output_mask_variable"],
                row["output_mask_button_variable"],
                row["routine_status_pattern_key"],
                row["sort_key"],
            )
            for row in routines
        ]
        if routine_tuple != expected_routines:
            raise ValueError(f"{region}: ABS_P5 routine Active-Test catalog drift")
        name_hits = [
            row["active_test_name"]
            for row in direct + routines
            if any(term in row["active_test_name"].lower() for term in forbidden)
        ]
        if name_hits:
            raise ValueError(f"{region}: ABS_P5 steering/ADS-named Active-Test rows: {name_hits}")
        direct_hashes = [row["raw_sha256"] for row in direct]
        routine_hashes = [row["raw_sha256"] for row in routines]
        if canonical_direct_hashes is None:
            canonical_direct_hashes = direct_hashes
            canonical_routine_hashes = routine_hashes
        elif direct_hashes != canonical_direct_hashes or routine_hashes != canonical_routine_hashes:
            raise ValueError(f"{region}: ABS_P5 Active-Test raw rows differ across regions")
        regions[region] = {
            "type68_direct_active_tests": direct,
            "type71_routine_active_tests": routines,
            "steering_eps_ads_lateral_name_hits": name_hits,
        }

    kgp = PE(root / "bin/KgpDataCtrl.dll")
    return {
        "database": "ABS_P5.ddb",
        "category_id": 435,
        "oem_ecu_name": "Brake/EPB",
        "factory_classes": {
            "type68": "CDbActTestP5Table",
            "type71": "CDbRoutineActTestP5Table",
        },
        "record_field_proof": {
            "type68_record_size": "64 bytes; GetRecordAddress shifts record index by 6",
            "type68_active_test_name_string_index": "u32 +0x0C loaded by CDbActTestP5ResRecords::SetRecString",
            "type68_lookup_key": "u16 +0x20 used by CDbActTestP5Table::FindDbItem1/ComparativeKey",
            "type68_sort_key": "u16 +0x2C used by CDbActTestP5ResRecords::SortInOrder",
            "type68_exception_id": "u16 +0x2E returned by CDbActTestP5Table::GetExceptahandId",
            "type68_exception_flag": "u8 +0x3B returned by CDbActTestP5Table::GetExceptahandFlag",
            "type71_fields": "same consumer-proven RoutineActTestP5 layout used by the FRC routine extraction",
            "byte_anchors": {
                "type68_name_string_index_load": kgp.check(0x100050D3, "8b 42 0c"),
                "type68_lookup_key_load": kgp.check(0x1000525B, "66 8b 42 20"),
                "type68_sort_key_load": kgp.check(0x10004FAD, "66 8b 51 2c"),
                "type68_record_stride_shift6": kgp.check(0x100052E1, "c1 e1 06"),
                "type68_exception_id_load": kgp.check(0x10005320, "66 8b 44 0a 2e"),
                "type68_exception_flag_load": kgp.check(0x1000535A, "8a 44 0a 3b"),
            },
        },
        "regions": regions,
        "conclusion": (
            "The pinned category-435 ABS_P5 Techstream Active-Test catalog is brake-actuator-only: "
            "20 direct type-68 tests and four type-71 routines resolve to relays, booster motor, "
            "linear solenoids, and ABS/VSC/ECB solenoids. No catalog row is named for steering, EPS, "
            "ADS, lateral control, or pinion angle, and all four routine rows have zero variable-backed "
            "command/mask/button payloads."
        ),
        "boundary": (
            "This is a catalog/host-schema negative, not proof that brake actuator tests have no "
            "indirect network effects. It rules out a named Techstream category-435 steering/ADS "
            "Active-Test writer in the pinned corpus; it does not resolve the normal B6 producer path."
        ),
    }


def p5_upstream_lateral_route(parser: DDBParser, root: Path) -> dict:
    """Recover the strongest Techstream-static FRC/brake/EPS topology evidence.

    This intentionally stops short of claiming that the FRC payload is forwarded
    or transformed into EPS B6.  The P5 diagnostic corpus can prove module
    installation, directed communication-health vocabulary, brake-family
    steering-target observers, and endpoint DTCs.  Producer code or synchronized
    traffic is still required for the payload/transport/authentication join.
    """
    h_corr = json.loads(H_CORR.read_text())
    h_b6 = next(
        row
        for row in h_corr["communication_monitor_dtc"]["rows"]
        if row["can_id"] == "0x0B6"
    )
    if not (
        h_b6["pdu_id"] == 42
        and h_b6["dtc"]["techstream_code"] == "U012987"
        and h_b6["dtc"]["techstream_description"]
        == "Lost Communication with Brake System Control Module"
        and h_b6["dtc"]["techstream_failure"] == "Missing Message"
    ):
        raise ValueError("H B6 Brake-System communication join drift")

    def dtc_row(db, strings, code: str, description: str) -> dict:
        hits = []
        for index, entry in enumerate(parser.extract_dtc_failure_entries(db.sections[65])):
            if entry.code != code:
                continue
            resolved = strings.get_string(entry.description_string_index) or ""
            failure = strings.get_string(entry.failure_string_index) or ""
            if resolved == description:
                hits.append((index, entry, failure))
        if len(hits) != 1:
            raise ValueError(f"{code} {description!r}: expected one DTC row, got {len(hits)}")
        index, entry, failure = hits[0]
        return {
            "record_index": index,
            "code": entry.code,
            "description": description,
            "failure": failure,
            "packed_dtc": f"0x{entry.packed_dtc:06X}",
            "raw_sha256": sha256(entry.raw),
        }

    def behavior_row(db, strings, signature: str, name: str) -> dict:
        hits = []
        for index, row in enumerate(parser.extract_priority_records(db.sections[87])):
            if row.fields.get("behavior_signature") != signature:
                continue
            resolved = strings.get_string(row.fields["name_string_index"])
            if resolved == name:
                hits.append((index, row))
        if len(hits) != 1:
            raise ValueError(f"{signature} {name!r}: expected one behavior row, got {len(hits)}")
        index, row = hits[0]
        return {
            "record_index": index,
            "behavior_signature": signature,
            "name": name,
            "raw_sha256": sha256(row.raw),
        }

    def monitor_row(db, strings, name: str) -> tuple[int, bytes]:
        hits = [
            (index, raw)
            for index, raw in enumerate(records(db.sections[62]))
            if strings.get_string(u32(raw, 0x18)) == name
        ]
        if len(hits) != 1:
            raise ValueError(f"ABS_P5 monitor {name!r}: expected one row, got {len(hits)}")
        return hits[0]

    region_rows: dict[str, dict] = {}
    for region in REGIONS:
        strings = parser.load_string_db(root / region / "DB/M_English.ddb")
        master = parser.parse_master_db(root / region / "DB/Toyota.ddb")
        categories = parser.extract_master_ecu_categories(master.sections[16])
        abs_category = [row for row in categories if row.category_id == 435]
        if len(abs_category) != 1:
            raise ValueError(f"{region}: category 435 count {len(abs_category)}")
        abs_category = abs_category[0]
        if not (
            abs_category.database_name == "ABS_P5.ddb"
            and abs_category.generation == 20
            and strings.get_string(abs_category.ecu_name_string_index) == "Brake/EPB"
        ):
            raise ValueError(f"{region}: category 435 identity drift")

        frc = parser.parse_ecu_db(root / region / "DB/FRC_P5.ddb")
        absdb = parser.parse_ecu_db(root / region / "DB/ABS_P5.ddb")
        frc_to_brk = behavior_row(
            frc,
            strings,
            "X216E",
            "Front Recognition Camera => BRK Communication Invalid",
        )
        frc_eps_key = behavior_row(
            frc,
            strings,
            "X2166",
            'Communication Error by ECU Security Key Not Registered (Power Steering Control Module "A")',
        )
        frc_vsc_key = behavior_row(
            frc,
            strings,
            "X2167",
            "Communication Error by ECU Security Key Not Registered (VSC)",
        )
        frc_brake_dtc = dtc_row(
            frc,
            strings,
            "U012987",
            'Lost Communication with Brake System Control Module "A"',
        )
        frc_eps_dtc = dtc_row(
            frc,
            strings,
            "U013187",
            'Lost Communication with Power Steering Control Module "A"',
        )
        frc_ads_dtc = dtc_row(
            frc,
            strings,
            "U015E87",
            'Lost Communication with Automated Driving System Interface Module "A"',
        )
        abs_eps_dtc = dtc_row(
            absdb,
            strings,
            "U013187",
            "Lost Communication with Power Steering Control Module",
        )
        abs_eps_ch2_dtc = dtc_row(
            absdb,
            strings,
            "U11B187",
            'Lost Communication with Power Steering Control Module "A" (ch2)',
        )
        abs_ads_dtc = dtc_row(
            absdb,
            strings,
            "U11A987",
            'Lost Communication with Automated Driving System Interface Module "A" (ch3)',
        )

        comm_index, comm_raw = monitor_row(
            absdb, strings, "EPS/Steering Control Actuator ECU Communication Open"
        )
        if not (
            u16(comm_raw, 0x24) == 500
            and u16(comm_raw, 0x2C) == 74
            and u16(comm_raw, 0x2E) == 74
            and u16(comm_raw, 0x36) == 0x102F
        ):
            raise ValueError(f"{region}: ABS EPS-communication monitor geometry drift")

        angle_index, angle_raw = monitor_row(absdb, strings, "ADS Control EPS Pinion Angle2")
        phy_key = u16(angle_raw, 0x2A)
        phy_hits = [
            (index, raw)
            for index, raw in enumerate(records(absdb.sections[13]))
            if u16(raw, 0x0C) == phy_key
        ]
        if len(phy_hits) != 1:
            raise ValueError(f"{region}: ABS ADS/EPS pinion-angle phy key {phy_key} count {len(phy_hits)}")
        phy_index, phy = phy_hits[0]
        unit_key = u16(phy, 0x0E)
        unit_hits = [
            (index, raw)
            for index, raw in enumerate(records(absdb.sections[15]))
            if u32(raw, 0x04) == unit_key
        ]
        if len(unit_hits) != 1:
            raise ValueError(f"{region}: ABS pinion-angle unit key {unit_key} count {len(unit_hits)}")
        unit_index, unit = unit_hits[0]
        angle = {
            "record_index": angle_index,
            "monitor_key": u16(angle_raw, 0x24),
            "name": "ADS Control EPS Pinion Angle2",
            "primary_data_id": did_str(u16(angle_raw, 0x36)),
            "alternate_data_id": did_str(u16(angle_raw, 0x38)),
            "bit_range": [u16(angle_raw, 0x2C), u16(angle_raw, 0x2E)],
            "physical_data_key": phy_key,
            "physical_record_index": phy_index,
            "mul": struct.unpack_from("<i", phy, 0x00)[0],
            "div": struct.unpack_from("<i", phy, 0x04)[0],
            "offset": struct.unpack_from("<i", phy, 0x08)[0],
            "signed": bool(phy[0x14]),
            "decimal_point_count": phy[0x15],
            "unit_key": unit_key,
            "unit_record_index": unit_index,
            "unit": strings.get_string(u32(unit, 0x00)),
            "data_range": [
                struct.unpack_from("<i", angle_raw, 0x10)[0],
                struct.unpack_from("<i", angle_raw, 0x0C)[0],
            ],
            "graph_range": [
                struct.unpack_from("<i", angle_raw, 0x08)[0],
                struct.unpack_from("<i", angle_raw, 0x04)[0],
            ],
            "display_scale_per_raw_count": (
                struct.unpack_from("<i", phy, 0x00)[0]
                / struct.unpack_from("<i", phy, 0x04)[0]
                / (10 ** phy[0x15])
            ),
            "monitor_raw_sha256": sha256(angle_raw),
            "physical_raw_sha256": sha256(phy),
        }
        if not (
            angle["monitor_key"] == 314
            and angle["primary_data_id"] == "0x107E"
            and angle["alternate_data_id"] == "0x307E"
            and angle["bit_range"] == [0, 23]
            and angle["physical_data_key"] == 65
            and angle["mul"] == 25
            and angle["div"] == 1
            and angle["offset"] == 0
            and angle["signed"]
            and angle["decimal_point_count"] == 5
            and angle["unit"] == "rad"
            and angle["data_range"] == [-131072, 131071]
            and angle["graph_range"] == [-3276800, 3276775]
            and abs(angle["display_scale_per_raw_count"] - 0.00025) < 1e-15
        ):
            raise ValueError(f"{region}: ABS ADS Control EPS Pinion Angle2 conversion drift")

        # A hidden copy of the EPS Target-Lateral dictionary would be significant.
        # It is absent in ABS_P5, and no type-62/88 row names Target Lateral or
        # Target Steering.  Keep that negative explicit so the route section is
        # not mistaken for a recovered B6 payload definition.
        forbidden_name_hits = []
        for table_type in (62, 88):
            for index, raw in enumerate(records(absdb.sections[table_type])):
                name = strings.get_string(u32(raw, 0x18)) or ""
                lower = name.lower()
                if "target lateral" in lower or "target steering" in lower:
                    forbidden_name_hits.append(
                        {"table_type": table_type, "record_index": index, "name": name}
                    )
        if forbidden_name_hits:
            raise ValueError(f"{region}: ABS_P5 unexpectedly has target-lateral/steering names")

        region_rows[region] = {
            "category_435": {
                "database": abs_category.database_name,
                "resolved_ecu_name": strings.get_string(abs_category.ecu_name_string_index),
                "generation": abs_category.generation,
                "raw_sha256": sha256(abs_category.raw),
            },
            "frc_behavior": {
                "frc_to_brake_invalid": frc_to_brk,
                "eps_security_key_not_registered": frc_eps_key,
                "vsc_security_key_not_registered": frc_vsc_key,
            },
            "frc_communication_dtcs": {
                "brake": frc_brake_dtc,
                "eps": frc_eps_dtc,
                "ads_interface": frc_ads_dtc,
            },
            "brake_communication_dtcs": {
                "eps": abs_eps_dtc,
                "eps_ch2": abs_eps_ch2_dtc,
                "ads_interface_ch3": abs_ads_dtc,
            },
            "brake_monitors": {
                "eps_communication_open": {
                    "record_index": comm_index,
                    "monitor_key": u16(comm_raw, 0x24),
                    "name": "EPS/Steering Control Actuator ECU Communication Open",
                    "primary_data_id": did_str(u16(comm_raw, 0x36)),
                    "bit_range": [u16(comm_raw, 0x2C), u16(comm_raw, 0x2E)],
                    "raw_sha256": sha256(comm_raw),
                },
                "ads_control_eps_pinion_angle2": angle,
            },
            "abs_target_lateral_name_negative": {
                "scanned_table_types": [62, 88],
                "matches": forbidden_name_hits,
            },
        }

    # These promoted raw records are byte-identical across the three regional DBs;
    # fail generation if a future corpus breaks that fact.
    canonical = region_rows["NA"]
    invariant_paths = (
        ("category_435", "raw_sha256"),
        ("frc_behavior", "frc_to_brake_invalid", "raw_sha256"),
        ("frc_behavior", "eps_security_key_not_registered", "raw_sha256"),
        ("frc_behavior", "vsc_security_key_not_registered", "raw_sha256"),
        ("frc_communication_dtcs", "brake", "raw_sha256"),
        ("frc_communication_dtcs", "eps", "raw_sha256"),
        ("frc_communication_dtcs", "ads_interface", "raw_sha256"),
        ("brake_communication_dtcs", "eps", "raw_sha256"),
        ("brake_communication_dtcs", "eps_ch2", "raw_sha256"),
        ("brake_communication_dtcs", "ads_interface_ch3", "raw_sha256"),
        ("brake_monitors", "eps_communication_open", "raw_sha256"),
        ("brake_monitors", "ads_control_eps_pinion_angle2", "monitor_raw_sha256"),
        ("brake_monitors", "ads_control_eps_pinion_angle2", "physical_raw_sha256"),
    )
    for region in ("EU", "JP"):
        for path in invariant_paths:
            a = canonical
            b = region_rows[region]
            for key in path:
                a = a[key]
                b = b[key]
            if a != b:
                raise ValueError(f"{region}: upstream-route regional invariant differs: {path}")

    brake_family_specs = {
        "ABS_P5.ddb": (435, "Brake/EPB"),
        "Brk_Bst_P5.ddb": (466, "Brake Booster"),
        "EPB_P5.ddb": (485, "Electric Parking Brake"),
    }
    brake_family_members: dict[str, dict] = {}
    shared_semantics = None
    for database, (category_id, ecu_name) in brake_family_specs.items():
        per_region: dict[str, dict] = {}
        for region in REGIONS:
            strings = parser.load_string_db(root / region / "DB/M_English.ddb")
            master = parser.parse_master_db(root / region / "DB/Toyota.ddb")
            categories = parser.extract_master_ecu_categories(master.sections[16])
            cat_hits = [row for row in categories if row.database_name == database]
            if len(cat_hits) != 1:
                raise ValueError(f"{region}: {database} master-category count {len(cat_hits)}")
            cat = cat_hits[0]
            if not (
                cat.category_id == category_id
                and cat.generation == 20
                and strings.get_string(cat.ecu_name_string_index) == ecu_name
            ):
                raise ValueError(f"{region}: {database} category identity drift")
            db = parser.parse_ecu_db(root / region / "DB" / database)
            monitor_hits = [
                (index, raw)
                for index, raw in enumerate(records(db.sections[62]))
                if strings.get_string(u32(raw, 0x18)) == "ADS Control EPS Pinion Angle2"
            ]
            if len(monitor_hits) != 1:
                raise ValueError(
                    f"{region}: {database} ADS Control EPS Pinion Angle2 count {len(monitor_hits)}"
                )
            monitor_index, monitor = monitor_hits[0]
            phy_key = u16(monitor, 0x2A)
            phy_hits = [
                (index, raw)
                for index, raw in enumerate(records(db.sections[13]))
                if u16(raw, 0x0C) == phy_key
            ]
            if len(phy_hits) != 1:
                raise ValueError(f"{region}: {database} PhyData key {phy_key} count {len(phy_hits)}")
            phy_index, phy = phy_hits[0]
            unit_key = u16(phy, 0x0E)
            unit_hits = [
                (index, raw)
                for index, raw in enumerate(records(db.sections[15]))
                if u32(raw, 0x04) == unit_key
            ]
            if len(unit_hits) != 1:
                raise ValueError(f"{region}: {database} unit key {unit_key} count {len(unit_hits)}")
            unit_index, unit = unit_hits[0]
            row = {
                "category_id": category_id,
                "resolved_ecu_name": ecu_name,
                "monitor_record_index": monitor_index,
                "monitor_key": u16(monitor, 0x24),
                "primary_data_id": did_str(u16(monitor, 0x36)),
                "alternate_data_id": did_str(u16(monitor, 0x38)),
                "bit_range": [u16(monitor, 0x2C), u16(monitor, 0x2E)],
                "physical_data_key": phy_key,
                "physical_record_index": phy_index,
                "mul": struct.unpack_from("<i", phy, 0x00)[0],
                "div": struct.unpack_from("<i", phy, 0x04)[0],
                "offset": struct.unpack_from("<i", phy, 0x08)[0],
                "signed": bool(phy[0x14]),
                "decimal_point_count": phy[0x15],
                "unit_key": unit_key,
                "unit_record_index": unit_index,
                "unit": strings.get_string(u32(unit, 0x00)),
                "data_range": [
                    struct.unpack_from("<i", monitor, 0x10)[0],
                    struct.unpack_from("<i", monitor, 0x0C)[0],
                ],
                "graph_range": [
                    struct.unpack_from("<i", monitor, 0x08)[0],
                    struct.unpack_from("<i", monitor, 0x04)[0],
                ],
                "display_scale_per_raw_count": (
                    struct.unpack_from("<i", phy, 0x00)[0]
                    / struct.unpack_from("<i", phy, 0x04)[0]
                    / (10 ** phy[0x15])
                ),
                "monitor_raw_sha256": sha256(monitor),
                "physical_raw_sha256": sha256(phy),
            }
            semantic_tuple = (
                row["monitor_key"],
                row["primary_data_id"],
                row["alternate_data_id"],
                tuple(row["bit_range"]),
                row["mul"],
                row["div"],
                row["offset"],
                row["signed"],
                row["decimal_point_count"],
                row["unit"],
                tuple(row["data_range"]),
                tuple(row["graph_range"]),
                row["display_scale_per_raw_count"],
            )
            expected_tuple = (
                314,
                "0x107E",
                "0x307E",
                (0, 23),
                25,
                1,
                0,
                True,
                5,
                "rad",
                (-131072, 131071),
                (-3276800, 3276775),
                0.00025,
            )
            if semantic_tuple != expected_tuple:
                raise ValueError(f"{region}: {database} 0x107E conversion drift: {semantic_tuple!r}")
            if shared_semantics is None:
                shared_semantics = semantic_tuple
            elif semantic_tuple != shared_semantics:
                raise ValueError(f"{region}: {database} brake-family 0x107E semantics differ")
            per_region[region] = row
        brake_family_members[database] = {
            "category_id": category_id,
            "resolved_ecu_name": ecu_name,
            "regions": per_region,
        }

    install_rows = corolla_model_install_sets(parser, root)["rows"]
    p5_corolla = [
        row
        for row in install_rows
        if 498 in row["categories"] and 405 in row["categories"]
    ]
    if not p5_corolla or any(435 not in row["categories"] for row in p5_corolla):
        raise ValueError("Corolla 498+405 install sets do not all contain category 435 Brake/EPB")

    return {
        "module_topology": {
            "corolla_install_sets": p5_corolla,
            "required_categories": {
                "498": "FRC_P5 / Front Recognition Camera 2",
                "435": "ABS_P5 / Brake/EPB",
                "405": "EMPS_P5 / EMPS",
            },
            "interpretation": (
                "Every Corolla-family install set in this artifact that contains FRC_P5(498) "
                "and EMPS_P5(405) also contains category 435, which Toyota.ddb resolves exactly "
                "to ABS_P5.ddb / Brake/EPB."
            ),
        },
        "regions": region_rows,
        "eps_h_endpoint": {
            "software_id": "8965H1202000",
            "can_id": h_b6["can_id"],
            "pdu_id": h_b6["pdu_id"],
            "dtc": h_b6["dtc"],
            "interpretation": (
                "Exact H maps protected B6/PDU42 loss to U012987 Lost Communication with "
                "Brake System Control Module / Missing Message, pinning the immediate monitored "
                "B6 sender relationship at the EPS endpoint."
            ),
        },
        "brake_family_angle_observer": {
            "canonical_region": "NA",
            **canonical["brake_monitors"]["ads_control_eps_pinion_angle2"],
            "conversion_formula": "display = (raw * mul / div + offset) / 10^decimal_point_count",
            "display_scale": "0.00025 rad/count",
            "family_members": brake_family_members,
            "shared_conversion": (
                "ABS_P5, Brk_Bst_P5 and EPB_P5 all expose monitor key 314 / DID 0x107E "
                "bits 0..23 as signed 0.00025 rad/count, despite using database-local PhyData keys."
            ),
            "scope": (
                "Corolla category 435 selects ABS_P5. The identical engineering conversion across "
                "the three brake-family diagnostic databases proves shared diagnostic vocabulary. "
                "It does not prove which physical ECU computes the value or that it is the B6 wire scalar."
            ),
        },
        "topology_conclusion": {
            "frc_to_brake_dependency_identified": True,
            "brake_to_eps_dependency_identified": True,
            "frc_to_eps_dependency_also_identified": True,
            "payload_forwarding_or_transform_identified": False,
            "secoc_sender_ownership_identified": False,
            "strongest_static_model": (
                "FRC_P5 has an explicit 'Front Recognition Camera => BRK Communication Invalid' "
                "behavior plus U012987 brake and U013187 EPS missing-message DTCs. Corolla's "
                "category-435 ABS_P5 brake domain monitors EPS communication and exposes an ADS "
                "Control EPS Pinion Angle2 observer. Exact H receives protected B6 from the Brake "
                "System Control Module. These facts establish a real FRC/brake/EPS communication "
                "topology and make a brake-mediated steering-target route plausible, but they do "
                "not prove that FRC target bytes are forwarded/transformed into B6; FRC also has "
                "a direct EPS communication dependency and both FRC/ABS reference an Automated "
                "Driving System Interface module."
            ),
            "next_evidence": (
                "Acquire decoded FRC_P5 and category-435 Brake/ABS firmware or a synchronized "
                "stock-LTA capture spanning FRC/Brake/EPS buses. Join the FRC lateral state to "
                "ABS_P5 0x107E (if live), protected EPS B6 signal254/255, counters/freshness and "
                "SecOC source/key state before assigning producer/forwarder ownership."
            ),
        },
        "boundary": (
            "Diagnostic module-dependency and observer evidence only. This section does not "
            "identify a CAN/CAN-FD arbitration ID for the FRC->Brake leg, a byte-level FRC->B6 "
            "transformation, category-435 transmit code, or the SecOC sender/key/freshness owner."
        ),
    }


def frc_security_state(parser: DDBParser, root: Path, region: str) -> dict:
    """Pin the FRC_P5 ECU-security-key registration-state diagnostic row."""
    db = parser.parse_ecu_db(root / region / "DB/FRC_P5.ddb")
    strings = parser.load_string_db(root / region / "DB/M_English.ddb")
    incomplete = None
    for index, raw in enumerate(records(db.sections[62])):
        if u16(raw, 0x36) != 0x10AF:
            continue
        name = strings.get_string(u32(raw, 0x18))
        if name != "ECU Security Key Registered Incomplete Flag":
            continue
        patdisp_key = u16(raw, 0x32)
        patterns = pattern_values(db, strings, patdisp_key)
        if patterns != {0: "OFF", 1: "ON", 2: "Not Fixed"}:
            raise ValueError(f"{region} 0x10AF pattern join resolved {patterns!r}")
        incomplete = {
            "record_index": index,
            "monitor_key": u16(raw, 0x24),
            "name": name,
            "primary_data_id": "0x10AF",
            "alternate_data_id": did_str(u16(raw, 0x38)),
            "bit_range": [u16(raw, 0x2C), u16(raw, 0x2E)],
            "pattern_display_key": patdisp_key,
            "pattern_values": patterns,
            "raw_sha256": sha256(raw),
        }
    if incomplete is None:
        raise ValueError(f"{region}: FRC_P5 0x10AF row not found")
    behavior = {
        row.fields["behavior_signature"]: strings.get_string(
            row.fields["name_string_index"]
        )
        for row in parser.extract_priority_records(db.sections[87])
    }
    expected_security_behavior = {
        "XF01B": "ECU Security Key Not Registered",
        "X2166": 'Communication Error by ECU Security Key Not Registered (Power Steering Control Module "A")',
    }
    for sig, name in expected_security_behavior.items():
        if behavior.get(sig) != name:
            raise ValueError(f"{region} FRC_P5 type-87 {sig}: {behavior.get(sig)!r}")
    return {
        "ecu_security_key_registered_incomplete_flag": incomplete,
        "pattern_display_join": {
            "monitor_record_pattern_display_key_offset": "u16 +0x32 (type 62)",
            "patdisp_table": "type 14 CDbPatDispTable",
            "patdisp_key_offset": "u16 +0x0C",
            "pattern_value_offset": "u32 +0x04",
            "display_string_index_offset": "u32 +0x00",
        },
        "type87_security_behavior_codes": expected_security_behavior,
        "boundary": (
            "diagnostic-state evidence only: these rows expose ECU-security-key registration "
            "state and lateral-condition monitors; they are not proof of a live authenticated "
            "lateral message or of any transport"
        ),
    }


# ── plugin DLL machine-code anchors ─────────────────────────────────────────


class PE:
    """Minimal byte-anchor oracle over a pinned 32-bit plugin DLL."""

    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        self.pe = pefile.PE(str(path), fast_load=True)
        self.base = self.pe.OPTIONAL_HEADER.ImageBase

    def check(self, va: int, expected_hex: str) -> dict:
        off = self.pe.get_offset_from_rva(va - self.base)
        expected = bytes.fromhex(expected_hex)
        actual = self.data[off : off + len(expected)]
        if actual != expected:
            raise ValueError(
                f"{self.path.name}: byte anchor at VA 0x{va:X} is {actual.hex()}, expected {expected_hex}"
            )
        return {"va": f"0x{va:X}", "file_offset": f"0x{off:X}", "bytes": expected_hex}

    def read(self, va: int, size: int) -> bytes:
        off = self.pe.get_offset_from_rva(va - self.base)
        return self.data[off : off + size]

    def imports(self) -> set[str]:
        pe = pefile.PE(str(self.path), fast_load=True)
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]]
        )
        names = set()
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            for imp in entry.imports:
                if imp.name:
                    names.add(imp.name.decode())
        return names


def tss3_operation_protocol(root: Path) -> dict:
    dll = PE(root / "bin/GetTSS3OperationFFDP5_DT.dll")
    imports = dll.imports()
    for required in (
        "?CommFrameSendReceiveExt@CCommCachePlus@@QAEKPAVCCommFrameData@@G@Z",
        "?GetCommFrmInfo@CCommCachePlus@@QAEKGPAUtagCOMMAND_DATA@@PAV?$CCmdList@VCCommFrameData@@@@K@Z",
    ):
        if required not in imports:
            raise ValueError(f"GetTSS3OperationFFDP5_DT.dll lacks import {required}")
    special_ids = [
        f"0x{v:04X}" for v in struct.unpack("<15H", dll.read(0x100091D4, 30))
    ]
    return {
        "dll": "GetTSS3OperationFFDP5_DT.dll",
        "direction": (
            "read-only proprietary Operation FFD observation; the AB/EB FFD protocol "
            "itself is read-only capture infrastructure. Category 498 separately exposes "
            "an Active-Test surface (roles 6/8/99/112/173); its steering-relevant branch is "
            "recovered separately in this artifact as fixed routine control, not a live setpoint writer."
        ),
        "transport": (
            "CCommCachePlus::CommFrameSendReceiveExt; comm-frame info selector 0x66 via "
            "CCommCachePlus::GetCommFrmInfo"
        ),
        "execute_va": "0x100032F0",
        "evidence_grading": {
            "byte_anchored": [
                "subtypes 0x11/0x12/0x13 and the AB/EB request/expected markers",
                "parser length gate (>6), data offset 6, BE16 DID shift, u8 block length",
                "special/excluded 15-entry LE-u16 table at 0x100091D4 and its scanning loop",
                "GetCommFrmInfo selector 0x66",
            ],
            "recovered_interpretation": [
                "response_layout wording (BE16 IDs after the 2-byte prefix / after offset 4)",
                "first-data-byte-as-block-count and dedup-by-DID semantics",
                "the AB31/AB33-style enumeration-vs-record roles of the subtypes",
            ],
        },
        "behavior_code_query": {
            "builder_va": "0x100010E0",
            "request": "AB 11",
            "expected_response": "EB 11",
            "response_layout": "BE16 IDs follow the 2-byte prefix",
            "response_layout_grade": "recovered",
        },
        "behavior_frame_query": {
            "builder_va": "0x100021D0",
            "request": "AB 12 <behavior_id BE16>",
            "expected_response": "EB 12",
            "response_layout": "subordinate BE16 IDs parsed after offset 4",
            "response_layout_grade": "recovered",
        },
        "data_record_query": {
            "builder_va": "0x100015A0",
            "request": "AB 13 <behavior_id BE16><record_id BE16>",
            "expected_response": "EB 13",
        },
        "data_record_parser": {
            "va": "0x10001A70",
            "data_offset": 6,
            "data_offset_grade": "byte_anchored",
            "block_layout": "[DID BE16][len u8][len bytes]",
            "first_data_byte_used_as_block_count_if_nonzero": True,
            "deduplicates_by_did": True,
            "block_semantics_grade": "recovered",
            "special_did": {
                "did": "0x0501",
                "handler_va": "0x10001F90",
            },
        },
        "special_excluded_id_list": {
            "table_va": "0x100091D4",
            "count": 15,
            "ids": special_ids,
            "scanned_by": "0x100030D0 (iterates until table end 0x100091F2)",
            "note": "operation/behavior IDs in proprietary space; not UDS DIDs unless independently resolved",
        },
        "byte_anchors": {
            "behavior_code_subtype_0x11": dll.check(0x10001188, "b1 11"),
            "behavior_code_request_marker_ab": dll.check(0x100011A4, "c6 44 24 30 ab"),
            "behavior_code_expected_marker_eb": dll.check(0x100011A9, "c6 44 24 60 eb"),
            "behavior_frame_subtype_0x12": dll.check(0x100022B0, "b1 12"),
            "behavior_frame_request_marker_ab": dll.check(0x100022C6, "c6 44 24 54 ab"),
            "behavior_frame_expected_marker_eb": dll.check(
                0x100022D3, "c6 84 24 84 00 00 00 eb"
            ),
            "data_record_subtype_0x13": dll.check(0x10001681, "b1 13"),
            "data_record_request_marker_ab": dll.check(0x100016A0, "c6 44 24 54 ab"),
            "data_record_expected_marker_eb": dll.check(
                0x100016A5, "c6 84 24 84 00 00 00 eb"
            ),
            "parser_requires_len_over_6": dll.check(0x10001ABD, "8d 43 fa"),
            "parser_data_offset_6": dll.check(0x10001ACB, "be 06 00 00 00"),
            "parser_be16_did_shift": dll.check(0x10001BC1, "c1 e5 08"),
            "parser_block_len_byte": dll.check(0x10001BCC, "8a 40 08"),
            "parser_special_did_0x0501": dll.check(0x10001FDD, "66 81 7c 24 34 01 05"),
            "getcommfrinfo_selector_0x66": dll.check(0x100031D7, "6a 66"),
            "excluded_list_table_pointer": dll.check(0x100030F7, "be d4 91 00 10"),
        },
    }


def tss3_image_fixed_reads() -> list[dict]:
    """The two re-anchored fixed spec-5 metadata pre-reads (22 11 04/22 11 07)."""
    return [
        {
            "request": "22 11 04",
            "expected_response": "62 11 04",
            "builder_va": "0x100011E0",
            "anchors": {
                "did_high_0x11": (0x1000129B, "b1 11"),
                "sid_0x22": (0x100012BE, "c6 44 24 38 22"),
                "fixed_low_0x04": (0x100012C3, "c6 44 24 50 04"),
                "expected_sid_0x62": (0x100012C8, "c6 84 24 80 00 00 00 62"),
                "expected_low_0x04": (0x100012D0, "c6 84 24 98 00 00 00 04"),
            },
            "note": "+0x50 write is the fixed request low byte (local_58=4), not a length field",
        },
        {
            "request": "22 11 07",
            "expected_response": "62 11 07",
            "builder_va": "0x100016A0",
            "anchors": {
                "did_high_0x11": (0x10001748, "b1 11"),
                "low_0x07_via_bl": (0x1000175E, "b3 07"),
                "sid_0x22": (0x1000176A, "c6 44 24 28 22"),
                "fixed_low_0x07": (0x1000176F, "88 5c 24 40"),
                "expected_sid_0x62": (0x10001773, "c6 44 24 70 62"),
                "expected_low_0x07": (0x10001778, "88 9c 24 88 00 00 00"),
            },
        },
    ]


def tss3_image_protocol(root: Path) -> dict:
    dll = PE(root / "bin/GetTSS3ImageFFDP5_DT.dll")
    imports = dll.imports()
    image_info = "?GetTSS3ImageFFDInfo@CCmdImgOpeDdr@@QAEKPAUtagCOMMAND_DATA@@PAVCCommCachePlusP5@@PAVCCommFrameData@@PAUTSS3IMAGE_FFD_MEMORIZED_INFO@@PAUTSS3IMAGE_FFD_INFO_P5@@@Z"
    for required in (
        image_info,
        "?GetDataNoEnableList@CCommDataIDData@@QAEKGPAV?$CCmdList@VCCmdByteData@@@@PAVCCommCachePlus@@PAEE@Z",
    ):
        if required not in imports:
            raise ValueError(f"GetTSS3ImageFFDP5_DT.dll lacks import {required}")

    spec5_dids = [
        0x110A,
        0x110D,
        0x1110,
        0x1113,
        0x1116,
        0x1119,
        0x111C,
        0x111F,
        0x1122,
        0x1125,
    ]
    spec5_selectors = [0x01, 0x05, 0x01, 0x05, 0x02, 0x01, 0x1E, 0x0A, 0x03, 0x0A]
    did_table = dll.read(0x100134A8, 24)
    selector_table = dll.read(0x100134C0, 12)
    # Raw bytes at 0x100134A8 (24 bytes, exact):
    #   0a 11 0d 11 10 11 13 11 16 11 19 11 1c 11 1f 11 22 11 25 11 28 11 00 00
    # <12H> unpacks to [0x110A, 0x110D, 0x1110, 0x1113, 0x1116, 0x1119,
    #                    0x111C, 0x111F, 0x1122, 0x1125, 0x1128, 0x0000];
    # the 12th entry is the 0x0000 terminator, not 0x1100.
    if did_table != bytes.fromhex("0a110d1110111311161119111c111f112211251128110000"):
        raise ValueError(f"spec DID table mismatch: {did_table.hex()}")
    read_dids = list(struct.unpack("<12H", did_table))
    read_selectors = list(selector_table)
    if (
        read_dids[:10] != spec5_dids
        or read_dids[10] != 0x1128
        or read_dids[11] != 0x0000
    ):
        raise ValueError(f"spec DID table mismatch: {[hex(d) for d in read_dids]}")
    if read_selectors != spec5_selectors + [0x03, 0x00]:
        raise ValueError(f"selector table mismatch: {[hex(s) for s in read_selectors]}")

    fixed_reads = tss3_image_fixed_reads()
    fixed_anchors = {}
    for read in fixed_reads:
        for name, (va, expected_hex) in read["anchors"].items():
            fixed_anchors[f"{read['request'].replace(' ', '_')}_{name}"] = dll.check(
                va, expected_hex
            )

    return {
        "dll": "GetTSS3ImageFFDP5_DT.dll",
        "direction": "read-only TSS3 Image FFD capture",
        "main_path": "CCmdImgOpeDdr::GetTSS3ImageFFDInfo",
        "support_probe_va": "0x10004420",
        "support_probes": [
            {"data_id": "0x1402", "selector": 1},
            {"data_id": "0x1402", "selector": 2},
            {"data_id": "0x1401", "selector": 2},
        ],
        "probe_did_names_in_FRC_P5": {
            "0x1402": "AHB Control ON Information",
            "0x1401": "AHB/AHS Information",
        },
        "fixed_metadata_reads": fixed_reads,
        "metadata_reads_via_command_common": {
            "table_va": "0x100B1780..0x100B18F0",
            "owner_dll": "CommandCommon.dll",
            "requests": ["22 11 01", "22 11 03", "22 20 81"],
            "note": "frame template table shared by CCmdGetDdrInfoP5Base-family code; each 22 xx yy entry is paired with its expected 62 xx yy response",
        },
        "security_unlock": {
            "service": "27 03 / 27 04",
            "wire_templates": {
                "27_03": "VA 0x100B17EC: 27 03 00 00 ff ff 00 00 00 00 00 00 67 03 00 00",
                "27_04": "VA 0x100B1800: 27 04 00 00 ff ff 00 00 67 04 00 00",
                "owner": "CommandCommon.dll frame-template table (shared with the 22 xx yy metadata templates)",
            },
            "seed_key_length": 6,
            "key_algorithm": "CalculateKeyDataSecLv49 @ 0x1004AC40 (CommandCommon.dll, CCmdImgOpeDdr)",
            "algorithm": (
                "for i in 0..5: x=seed[i]; j=x&7; if j>=6: j-=6; "
                "add = key[j] if j<i else seed[j]; rot=[1,2,3,3,2,1]; d=(x>>rot[i])&3; "
                "key[i] = (rol8(x, d+1) + add) & 0xFF"
            ),
            "known_vectors": [
                {"seed": "010203040506", "key": "04070a0d1a64"},
                {"seed": "123456789abc", "key": "9e6a50252409"},
                {"seed": "deadbeefcafe", "key": "cbd8b6970cba"},
                {"seed": "000000000000", "key": "000000000000"},
            ],
        },
        "spec5_dynamic_dids": {
            "did_table_va": "0x100134A8",
            "selector_table_va": "0x100134C0",
            "dids": [f"0x{d:04X}" for d in spec5_dids],
            "selectors": [f"0x{s:02X}" for s in spec5_selectors],
            "spec7_extension": {
                "did": "0x1128",
                "note": "present in the 12-entry table; its 11th selector (0x03) is bounded, not independently resolved",
            },
        },
        "proprietary_enumeration": {
            "request": "AB 31",
            "expected_response": "EB 31",
            "anchors": {
                "subtype_0x31": (0x10002E94, "b1 31"),
                "request_marker_ab": (0x10002EB3, "c6 44 24 34 ab"),
                "expected_marker_eb": (0x10002EB8, "c6 44 24 7c eb"),
            },
        },
        "proprietary_record_retrieval": {
            "request": "AB 33",
            "expected_response": "EB 33",
            "anchors": {
                "subtype_0x33": (0x10003382, "b1 33"),
                "request_marker_ab": (0x100033AE, "c6 44 24 6c ab"),
                "expected_marker_eb": (0x100033B3, "c6 84 24 b4 00 00 00 eb"),
            },
        },
        "content_boundary": (
            "the pinned Image FFD surface contains no named lateral/LTA monitor content and no "
            "write path; 22 11 04 and 22 11 07 are the only fixed metadata reads promoted, "
            "both re-anchored in the plugin"
        ),
        "not_a_did": {
            "immediate": "0x1CE4",
            "va": "0x1000A7FE",
            "meaning": "allocation size passed to the 0x1000C62E allocator; not a diagnostic data identifier",
        },
        "byte_anchors": {
            "probe_1402_selector_1": dll.check(0x100044ED, "6a 01"),
            "probe_1402_selector_1_did": dll.check(0x100044F6, "68 02 14 00 00"),
            "probe_1402_selector_2": dll.check(0x10004526, "6a 02"),
            "probe_1402_selector_2_did": dll.check(0x1000452F, "68 02 14 00 00"),
            "probe_1401_selector_2": dll.check(0x1000456E, "6a 02"),
            "probe_1401_selector_2_did": dll.check(0x10004577, "68 01 14 00 00"),
            "allocation_0x1ce4": dll.check(0x1000A7FE, "68 e4 1c 00 00"),
            "allocation_call": dll.check(0x1000A806, "e8 23 1e 00 00"),
            **fixed_anchors,
            "enum_ab31_subtype": dll.check(0x10002E94, "b1 31"),
            "enum_ab31_request": dll.check(0x10002EB3, "c6 44 24 34 ab"),
            "enum_ab31_expected": dll.check(0x10002EB8, "c6 44 24 7c eb"),
            "record_ab33_subtype": dll.check(0x10003382, "b1 33"),
            "record_ab33_request": dll.check(0x100033AE, "c6 44 24 6c ab"),
            "record_ab33_expected": dll.check(0x100033B3, "c6 84 24 b4 00 00 00 eb"),
        },
        "command_common_anchors": command_common_anchors(root),
    }


def command_common_anchors(root: Path) -> dict:
    """Byte anchors inside CommandCommon.dll for the shared FFD machinery."""
    cc = PE(root / "bin/CommandCommon.dll")
    return {
        "metadata_22_11_03_template": cc.check(
            0x100B1830, "22 11 03 00 ff ff ff 00 62 11 03 00"
        ),
        "metadata_22_11_01_template": cc.check(
            0x100B17BC, "22 11 01 00 ff ff ff 00 62 11 01 00"
        ),
        "metadata_22_20_81_template": cc.check(
            0x100B18C0, "22 20 81 00 ff ff ff 00 62 20 81 00"
        ),
        "key_rotation_table": cc.check(0x100B1910, "01 02 03 03 02 01"),
        "calculate_key_data_sec_lv49": cc.check(0x1004AC4D, "b8 10 19 0b 10"),
        "security_unlock_27_03_template": cc.check(
            0x100B17EC, "27 03 00 00 ff ff 00 00 00 00 00 00 67 03 00 00"
        ),
        "security_unlock_27_04_template": cc.check(
            0x100B1800, "27 04 00 00 ff ff 00 00 67 04 00 00"
        ),
    }


# ── ADS_Eth_P5 DDR snapshot rows (secondary evidence) ────────────────────────


def ads_ddr_tables(root: Path) -> dict:
    obj = json.loads(FACTORY.read_text())
    expected = {
        133: "CDbDDRBehaviorCodeP5Table",
        134: "CDbDDRBehaviorDataRecordP5Table",
        135: "CDbDDRBehaviorDataInvalidP5Table",
    }
    out = {}
    for table_type, class_name in expected.items():
        matches = [
            row
            for factory in obj["factories"]
            for row in factory["records"]
            if row["table_type"] == table_type
        ]
        classes = {row["class_name"] for row in matches}
        if classes != {class_name}:
            raise ValueError(f"unexpected table-{table_type} classes: {classes}")
        out[str(table_type)] = {
            "table_type": table_type,
            "class_name": class_name,
            "factory_records": matches,
        }
    out["134"].update(
        {
            "record_name_string_offset": "0x18",
            "record_name_string_consumer": (
                "CDbDDRBehaviorDataRecordP5ResRecords::SetRecString @ 0x1002A4BA "
                "loads record+0x18 at 0x1002A583 before CDbStringTable::GetString"
            ),
        }
    )
    return out


def ads_ddr_rows(parser: DDBParser, root: Path) -> dict:
    db = parser.parse_ecu_db(root / "NA/DB/ADS_Eth_P5.ddb")
    strings = parser.load_string_db(root / "NA/DB/M_English.ddb")
    phy = {
        u16(raw, 0x0C): {"unit_key": u16(raw, 0x0E), "raw_sha256": sha256(raw)}
        for raw in records(db.sections[13])
    }
    units = {
        u32(raw, 0x04): strings.get_string(u32(raw, 0x00))
        for raw in records(db.sections[15])
    }
    if len(units) != len({u32(raw, 0x04) for raw in records(db.sections[15])}):
        raise ValueError("ADS_Eth_P5 CDbUnitTable unit keys are not unique")
    rows = []
    for index, raw in enumerate(records(db.sections[134])):
        name = strings.get_string(u32(raw, 0x18))
        if name not in ADS_NAMES:
            continue
        phy_key = u16(raw, 0x28)
        unit_key = phy[phy_key]["unit_key"]
        rows.append(
            {
                "record_index": index,
                "name": name,
                "name_string_index": u32(raw, 0x18),
                "physical_data_key": phy_key,
                "bit_range": [u16(raw, 0x2A), u16(raw, 0x2C)],
                "pattern_display_key": u16(raw, 0x30),
                "unit_key": unit_key,
                "resolved_unit": units.get(unit_key),
                "raw_sha256": sha256(raw),
            }
        )
    if sorted(r["name"] for r in rows) != sorted(ADS_NAMES) or sorted(
        r["record_index"] for r in rows
    ) != [143, 406, 407]:
        raise ValueError("ADS DDR lateral rows do not resolve to records 143/406/407")
    return {
        "rows": rows,
        "row_field_consumers": {
            "physical_data_key": "u16 +0x28 (read at GetADSDDRInfoP5_DT.dll 0x100080EA)",
            "bit_start": "u16 +0x2A (subtracted at 0x10008258)",
            "bit_end": "u16 +0x2C (read at 0x10008254)",
            "pattern_display_key": "u16 +0x30 (read at 0x1000816A)",
        },
        "unit_resolution_chain": (
            "DDR row +0x28 -> CDbPhyData key (+0x0C) -> PhyData +0x0E u16 unit key -> "
            "CDbUnit key (+0x04) -> unit string index (+0x00) via CDbUnitResRecords::GetDefaultUnitStr"
        ),
    }


def emps_angle_conversion(parser: DDBParser, root: Path) -> dict:
    """Recover the P5 data-monitor numeric conversion for steering angle.

    GetDatMonSignalInfoP5_DT.dll copies CDbPhyData record +0/+4/+8 into
    CCmdConversionTbl m_lMul/m_lDiv/m_lOffset, and +0x14/+0x15 into the signed
    and decimal-point fields. The monitor's raw/graph ranges independently pin
    the conversion direction. This keeps the UI conversion separate from the
    H firmware's wire/controller proof.
    """
    names = parser.load_string_db(root / "NA/DB/M_English.ddb")

    def db_rows(region: str) -> dict:
        db = parser.parse_ecu_db(root / f"{region}/DB/EMPS_P5.ddb")
        monitors = records(db.sections[62])
        physical = records(db.sections[13])
        units = records(db.sections[15])
        phy_by_key = {u16(raw, 0x0C): (i, raw) for i, raw in enumerate(physical)}
        unit_by_key = {u16(raw, 0x04): (i, raw) for i, raw in enumerate(units)}

        def monitor_by_key(key: int) -> tuple[int, bytes]:
            found = [(i, raw) for i, raw in enumerate(monitors) if u16(raw, 0x24) == key]
            if len(found) != 1:
                raise ValueError(f"{region} EMPS_P5 monitor key {key} count {len(found)}")
            return found[0]

        def decode(key: int) -> dict:
            idx, raw = monitor_by_key(key)
            phy_key = u16(raw, 0x2A)
            phy_idx, phy = phy_by_key[phy_key]
            unit_key = u16(phy, 0x0E)
            unit_idx, unit = unit_by_key[unit_key]
            return {
                "monitor_key": key,
                "record_index": idx,
                "name": names.get_string(u32(raw, 0x18)),
                "physical_data_key": phy_key,
                "physical_record_index": phy_idx,
                "physical_raw_hex": phy.hex(),
                "mul": struct.unpack_from("<i", phy, 0x00)[0],
                "div": struct.unpack_from("<i", phy, 0x04)[0],
                "offset": struct.unpack_from("<i", phy, 0x08)[0],
                "signed": bool(phy[0x14]),
                "decimal_point_count": phy[0x15],
                "unit_key": unit_key,
                "unit_record_index": unit_idx,
                "unit": names.get_string(u32(unit, 0x00)),
                "data_range": [struct.unpack_from("<i", raw, 0x10)[0], struct.unpack_from("<i", raw, 0x0C)[0]],
                "graph_range": [struct.unpack_from("<i", raw, 0x08)[0], struct.unpack_from("<i", raw, 0x04)[0]],
                "monitor_raw_sha256": sha256(raw),
            }

        return {"steering_angle": decode(17), "vehicle_speed_sp1": decode(305)}

    regions = {region: db_rows(region) for region in REGIONS}
    canonical = regions["NA"]
    for region in ("EU", "JP"):
        for field in ("physical_data_key", "physical_raw_hex", "mul", "div", "offset", "signed", "decimal_point_count", "unit", "data_range", "graph_range"):
            if regions[region]["steering_angle"][field] != canonical["steering_angle"][field]:
                raise ValueError(f"EMPS steering-angle conversion differs in {region}: {field}")

    steer = canonical["steering_angle"]
    speed = canonical["vehicle_speed_sp1"]
    if not (
        steer["name"] == "Steering Angle"
        and steer["physical_data_key"] == 3
        and steer["mul"] == 15
        and steer["div"] == 1
        and steer["offset"] == 0
        and steer["signed"]
        and steer["decimal_point_count"] == 1
        and steer["unit"] == "deg"
        and steer["data_range"] == [-2048, 2047]
        and steer["graph_range"] == [-30720, 30705]
    ):
        raise ValueError("EMPS steering-angle conversion drift")
    if not (
        speed["name"] == "CAN Vehicle Speed (SP1)"
        and speed["mul"] == 1
        and speed["div"] == 10
        and speed["offset"] == 0
        and speed["decimal_point_count"] == 1
        and speed["data_range"] == [0, 30000]
        and speed["graph_range"] == [0, 3000]
    ):
        raise ValueError("EMPS SP1 conversion-direction witness drift")

    dll = PE(root / "bin/GetDatMonSignalInfoP5_DT.dll")
    debug_strings = {
        "mul": (0x10009344, b"[CMD]%s(%d): m_ConversionTbl.m_lMul=%ld\x00"),
        "div": (0x1000931C, b"[CMD]%s(%d): m_ConversionTbl.m_lDiv=%ld\x00"),
        "offset": (0x100092F0, b"[CMD]%s(%d): m_ConversionTbl.m_lOffset=%ld\x00"),
        "decimal_point_count": (0x1000943C, b"[CMD]%s(%d): m_lstSignalInfo:m_byDecPntCount=%d\x00"),
    }
    for field, (va, expected) in debug_strings.items():
        if dll.read(va, len(expected)) != expected:
            raise ValueError(f"GetDatMonSignalInfoP5_DT.dll debug string drift: {field}")

    return {
        "formula": "graph_integer = raw * mul / div + offset; displayed_value = graph_integer / 10^decimal_point_count",
        "direction_witness": "CAN Vehicle Speed (SP1): raw 0..30000, mul/div 1/10 -> graph 0..3000; decimal-point-count 1 -> 0.0..300.0 km/h",
        "steering_angle": steer,
        "regions": regions,
        "plugin": {
            "dll": "GetDatMonSignalInfoP5_DT.dll",
            "byte_anchors": {
                "decimal_point_read": dll.check(0x10001965, "8a5115"),
                "decimal_point_store": dll.check(0x1000196C, "88573d"),
                "mul_copy": dll.check(0x1000197A, "8b14068b0a894f58"),
                "div_copy": dll.check(0x10001982, "8b14068b4a04894f5c"),
                "offset_copy": dll.check(0x1000198B, "8b14068b4a08894f60"),
                "signed_copy": dll.check(0x10001994, "8b14068a4214884766"),
                "mul_debug_binding": dll.check(0x10001416, "8b50585268b9000000683c9500106844930010"),
                "div_debug_binding": dll.check(0x10001438, "8b405c5068ba000000683c950010681c930010"),
                "offset_debug_binding": dll.check(0x1000145A, "8b48605168bb000000683c95001068f0920010"),
            },
            "debug_strings": {field: {"va": f"0x{va:X}", "value": expected[:-1].decode()} for field, (va, expected) in debug_strings.items()},
        },
        "physical_interpretation": "EMPS_P5 steering raw count is 1.5 degrees: raw*15 produces a graph integer with one decimal place in degrees.",
    }


def ads_ddr_protocol(root: Path) -> dict:
    dll = PE(root / "bin/GetADSDDRInfoP5_DT.dll")
    imports = dll.imports()
    for required in (
        "?GetDefaultUnitStr@CDbUnitResRecords@@QAEPADF@Z",
        "?GetPatDispString@CDbPatDispResRecords@@QAEPADF@Z",
        "??0CDbPhyDataResRecords@@QAE@XZ",
    ):
        if required not in imports:
            raise ValueError(f"GetADSDDRInfoP5_DT.dll lacks import {required}")
    op = PE(root / "bin/GetADSOperationFFDP5_DT.dll")
    return {
        "info_dll": "GetADSDDRInfoP5_DT.dll",
        "byte_anchors": {
            "physical_data_key_read": dll.check(0x100080EA, "66 8b 4a 28"),
            "bit_end_read": dll.check(0x10008254, "66 8b 50 2c"),
            "bit_start_subtract": dll.check(0x10008258, "66 2b 50 2a"),
            "pattern_display_key_read": dll.check(0x1000816A, "66 8b 41 30"),
        },
        "operation_plugin_did": {
            "dll": "GetADSOperationFFDP5_DT.dll",
            "data_id": "0x1C08",
            "selectors": [1, 6],
            "note": "plugin-specific GetDataNoEnableList probes; not joined to DDR rows 406/407 without proof",
            "byte_anchors": {
                "selector_1": op.check(0x100012C7, "6a 01"),
                "did_0x1c08_selector_1": op.check(0x100012D7, "68 08 1c 00 00"),
                "selector_6": op.check(0x100012FB, "6a 06"),
                "did_0x1c08_selector_6": op.check(0x1000130B, "68 08 1c 00 00"),
            },
        },
    }


# ── LDA / EMPS domains ───────────────────────────────────────────────────────


def behavior_code_rows(parser: DDBParser, root: Path) -> list[dict]:
    db = parser.parse_ecu_db(root / "NA/DB/LDA_P5.ddb")
    strings = parser.load_string_db(root / "NA/DB/M_English.ddb")
    out = []
    for index, row in enumerate(parser.extract_priority_records(db.sections[87])):
        if row.fields.get("behavior_signature") not in LDA_SIGNATURES:
            continue
        out.append(
            {
                "record_index": index,
                "behavior_signature": row.fields["behavior_signature"],
                "name_string_index": row.fields["name_string_index"],
                "name": strings.get_string(row.fields["name_string_index"]),
                "raw_sha256": sha256(row.raw),
            }
        )
    return out


def emps_rows(parser: DDBParser, root: Path, database: str) -> list[dict]:
    db = parser.parse_ecu_db(root / "NA/DB" / database)
    strings = parser.load_string_db(root / "NA/DB/M_English.ddb")
    out = []
    for index, raw in enumerate(records(db.sections[62])):
        monitor_key = u16(raw, 0x24)
        if monitor_key not in EMPS_MONITORS:
            continue
        out.append(
            {
                "record_index": index,
                "monitor_key": monitor_key,
                "name_string_index": u32(raw, 0x18),
                "name": strings.get_string(u32(raw, 0x18)),
                "bit_range": [u16(raw, 0x2C), u16(raw, 0x2E)],
                "primary_data_id": did_str(u16(raw, 0x36)),
                "alternate_data_id": did_str(u16(raw, 0x38)),
                "raw_sha256": sha256(raw),
            }
        )
    return out


def corpus_did_scan(root: Path, data_ids: tuple[int, ...]) -> dict:
    """Scan every P5 ECU database for type-62 rows carrying the given DIDs."""
    hits: dict[tuple[str, str, int], int] = {}
    files = sorted(root.glob("*/DB/*_P5*.ddb"))
    for path in files:
        region = path.parts[-3]
        db = DDBParser().parse_ecu_db(path)
        section = db.sections.get(62)
        if not section or not section.decoded_data:
            continue
        for raw in records(section):
            did = u16(raw, 0x36)
            if did in data_ids:
                key = (region, path.name, did)
                hits[key] = hits.get(key, 0) + 1
    owners = sorted({(region, name) for region, name, _ in hits})
    return {
        "scan_scope": (
            "type-62 CDbDatamonitorP5Table primary Data-ID field (record +0x36) of the "
            "NA/EU/JP *_P5*.ddb ECU databases; alternate Data-ID fields and non-P5 or "
            "non-type-62 tables are not covered by this scan"
        ),
        "files_scanned": len(files),
        "data_ids": [did_str(d) for d in data_ids],
        "owner_databases": [
            {"region": region, "database": name} for region, name in owners
        ],
        "row_counts": [
            {"region": region, "database": name, "data_id": did_str(did), "rows": count}
            for (region, name, did), count in sorted(hits.items())
        ],
    }


# ── FRC_P5 routine Active-Test surface ──────────────────────────────────────

FRC_ROUTINE_TESTS = (
    ("LDA Steering Vibration", 0x1508, 511),
    ("LTA Steering Vibration", 0x1588, 542),
    ("LCA Steering Vibration", 0x15C8, 573),
    ("AES Automatic Steering in Control Notification", 0x160B, 609),
)


def _master_variable_blob(master, index: int) -> bytes:
    """Resolve a 1-based format-1 CDbVariableTable entry to its raw byte blob."""
    section = master.sections[0]
    count = section.header.record_count
    if index <= 0 or index > count:
        raise ValueError(f"master variable index 0x{index:X} outside 1..{count}")
    table_end = count * 6
    rel, length = struct.unpack_from("<IH", section.decoded_data, (index - 1) * 6)
    start = table_end + rel
    end = start + length
    if end > len(section.decoded_data):
        raise ValueError(f"master variable index 0x{index:X} overruns variable pool")
    return section.decoded_data[start:end]


def _master_comm_frame(
    parser: DDBParser, root: Path, region: str, selector: int
) -> dict:
    master = parser.parse_master_db(root / region / "DB/Toyota.ddb")
    section = master.sections[17]
    size = section.decoded_record_size
    matches = [raw for raw in records(section) if u16(raw, 0x00) == selector]
    if len(matches) != 1:
        raise ValueError(
            f"{region} comm-frame selector 0x{selector:02X}: {len(matches)} matches"
        )
    raw = matches[0]
    refs = {
        "send_frame": u16(raw, 0x02),
        "receive_mask": u16(raw, 0x04),
        "receive_check": u16(raw, 0x06),
    }
    return {
        "selector": f"0x{selector:02X}",
        "raw_record": raw.hex(),
        "record_size": size,
        "variable_refs": {k: f"0x{v:04X}" for k, v in refs.items()},
        "resolved": {
            k: _master_variable_blob(master, v).hex() for k, v in refs.items()
        },
        "raw_sha256": sha256(raw),
    }


def _frc_routine_rows(parser: DDBParser, root: Path, region: str) -> list[dict]:
    db = parser.parse_ecu_db(root / region / "DB/FRC_P5.ddb")
    strings = parser.load_string_db(root / region / "DB/M_English.ddb")
    section = db.sections[71]
    if section.decoded_record_size != 64:
        raise ValueError(f"{region} FRC_P5 type-71 size {section.decoded_record_size}")
    wanted = {name: (rid, sort_key) for name, rid, sort_key in FRC_ROUTINE_TESTS}
    out = []
    for index, raw in enumerate(records(section)):
        name = strings.get_string(u32(raw, 0x08))
        if name not in wanted:
            continue
        rid, sort_key = wanted[name]
        row = {
            "record_index": index,
            "name": name,
            "name_string_index": f"0x{u32(raw, 0x08):08X}",
            "lookup_key": f"0x{u16(raw, 0x1E):04X}",
            "routine_id": f"0x{u16(raw, 0x1C):04X}",
            "routine_command_variable": f"0x{u16(raw, 0x28):04X}",
            "output_mask_variable": f"0x{u16(raw, 0x2A):04X}",
            "output_mask_button_variable": f"0x{u16(raw, 0x2C):04X}",
            "routine_status_pattern_key": f"0x{u16(raw, 0x2E):04X}",
            "sort_key": u16(raw, 0x38),
            "exception_handler_id": f"0x{u16(raw, 0x3A):04X}",
            "exception_handler_flag": raw[0x3D],
            "raw_sha256": sha256(raw),
        }
        if u16(raw, 0x1C) != rid or u16(raw, 0x38) != sort_key:
            raise ValueError(f"{region} {name}: routine/sort key changed: {row}")
        if any(u16(raw, off) for off in (0x28, 0x2A, 0x2C)):
            raise ValueError(
                f"{region} {name}: unexpected variable-backed command/mask/button data"
            )
        if "Steering Vibration" in name and u16(raw, 0x2E) != 2:
            raise ValueError(f"{region} {name}: status pattern key is not 2")
        if name.startswith("AES ") and u16(raw, 0x2E) != 0:
            raise ValueError(
                f"{region} {name}: AES status pattern unexpectedly nonzero"
            )
        out.append(row)
    if {row["name"] for row in out} != set(wanted):
        raise ValueError(f"{region}: missing FRC routine test rows")
    return sorted(out, key=lambda row: row["sort_key"])


def _frc_status_pattern(parser: DDBParser, root: Path, region: str, key: int) -> dict:
    db = parser.parse_ecu_db(root / region / "DB/FRC_P5.ddb")
    section = db.sections[72]
    if section.decoded_record_size != 12:
        raise ValueError(f"{region} FRC_P5 type-72 size {section.decoded_record_size}")
    matches = [raw for raw in records(section) if u16(raw, 0x00) == key]
    if len(matches) != 1:
        raise ValueError(f"{region} FRC_P5 type-72 key {key}: {len(matches)} matches")
    raw = matches[0]
    variable = u16(raw, 0x02)
    master = parser.parse_master_db(root / region / "DB/Toyota.ddb")
    return {
        "key": f"0x{key:04X}",
        "raw_record": raw.hex(),
        "pattern_variable": f"0x{variable:04X}",
        "pattern_bytes": _master_variable_blob(master, variable).hex(),
        "raw_sha256": sha256(raw),
    }


def frc_routine_active_test_surface(parser: DDBParser, root: Path) -> dict:
    dll = PE(root / "bin/SingleRoutineActTstP5_DT.dll")
    imports = dll.imports()
    required = {
        "?GetRoutineCommand@CDbRoutineActTestP5ResRecords@@QAEPAEFPAG@Z",
        "?GetRoutineStatusPattern@CDbRoutineStatusResRecords@@QAEPAEFPAG@Z",
        "?GetCommFrmInfo@CCommCachePlus@@QAEKGPAUtagCOMMAND_DATA@@PAV?$CCmdList@VCCommFrameData@@@@K@Z",
        "?CommFrameSendReceiveExt@CCommCachePlus@@QAEKPAVCCommFrameData@@G@Z",
    }
    missing = sorted(required - imports)
    if missing:
        raise ValueError(f"SingleRoutineActTstP5_DT.dll missing imports {missing}")

    init_imports = PE(root / "bin/GetRoutineActTstInitP5_DT.dll").imports()
    signal_imports = PE(root / "bin/GetRoutineActTstSignalInfoP5_DT.dll").imports()
    auth_terms = ("Security", "Authenticate", "Seed", "KeyAccess", "Session")
    explicit_auth_imports = sorted(
        n
        for n in imports | init_imports | signal_imports
        if any(term in n for term in auth_terms)
    )

    region_tables = {}
    for region in REGIONS:
        db = parser.parse_ecu_db(root / region / "DB/FRC_P5.ddb")
        region_tables[region] = {
            "type68_direct_p5_active_test_present": 68 in db.sections,
            "type71_routine_active_test_count": db.sections[71].header.record_count,
            "type72_routine_status_count": db.sections[72].header.record_count,
            "type73_pattern_display_variable_count": db.sections[
                73
            ].header.record_count,
            "steering_related_rows": _frc_routine_rows(parser, root, region),
            "steering_vibration_status_pattern": _frc_status_pattern(
                parser, root, region, 2
            ),
            "comm_frames": {
                f"0x{selector:02X}": _master_comm_frame(parser, root, region, selector)
                for selector in (0xD5, 0xD6, 0xD7)
            },
        }
        if region_tables[region]["type68_direct_p5_active_test_present"]:
            raise ValueError(
                f"{region} FRC_P5 unexpectedly gained type-68 direct Active-Test records"
            )

    return {
        "factory_identity": {
            "type68": "CDbActTestP5Table (absent from FRC_P5 NA/EU/JP)",
            "type71": "CDbRoutineActTestP5Table",
            "type72": "CDbRoutineStatusTable",
            "type73": "CDbPatDispVariableTable",
        },
        "regions": region_tables,
        "record_field_proof": {
            "active_test_name": "type-71 u32 +0x08 -> CDbStringTable::GetString in CDbRoutineActTestP5ResRecords::SetRecString @ 0x10044D40",
            "lookup_key": "type-71 u16 +0x1E -> CDbRoutineActTestP5Table::FindDbItem1/ComparativeKey @ 0x100452C9/0x10045484",
            "routine_id": "type-71 u16 +0x1C -> SingleRoutineActTstP5_DT.dll internal state +0x08 and request items 2/3",
            "routine_command_variable": "type-71 u16 +0x28 -> CDbVariableTable::GetVariable in SetRecVariableData @ 0x10044E2B -> GetRoutineCommand",
            "output_mask_variable": "type-71 u16 +0x2A -> CDbVariableTable::GetVariable -> GetOutputMaskValue",
            "output_mask_button_variable": "type-71 u16 +0x2C -> CDbVariableTable::GetVariable -> GetOutputMaskButtonData",
            "routine_status_pattern_key": "type-71 u16 +0x2E -> SingleRoutineActTstP5_DT.dll internal state +0x0A -> type-72 CDbRoutineStatusResRecords",
            "sort_key": "type-71 u16 +0x38 -> CDbRoutineActTestP5ResRecords::SortInOrder @ 0x10044C58",
        },
        "executor": {
            "dll": "SingleRoutineActTstP5_DT.dll",
            "execute_va": "0x10001010",
            "phase_sequence": [
                {"selector": "0xD5", "helper_va": "0x10001430", "then_sleep_ms": 200},
                {
                    "selector": "0xD7",
                    "helper_va": "0x100017A0",
                    "then_sleep_ms_on_success": 5000,
                },
                {"selector": "0xD6", "helper_va": "0x10001AC0", "final_phase": True},
            ],
            "outgoing_layout": (
                "Each D5/D7/D6 comm-frame template resolves to send prefix 21 E2. "
                "The executor overwrites request items 2/3 with routine-id high/low bytes. "
                "Only D5 appends GetRoutineCommand bytes when the type-71 command variable is nonzero."
            ),
            "follow_up_status": (
                "D7 accumulates response data after the four-item header in big-endian order and "
                "compares it through type-72 CDbRoutineStatusResRecords; the steering-vibration "
                "records use status key 2, whose master variable 0x0054 resolves to byte 02."
            ),
            "explicit_auth_named_imports": explicit_auth_imports,
            "auth_boundary": (
                "No explicit SecurityAccess/authentication/session-named import is present in the "
                "SingleRoutine/Init/SignalInfo plugin chain. This does NOT prove the ECU accepts the "
                "routine without a session or authentication established by surrounding Techstream."
            ),
            "byte_anchors": {
                "call_initial_D5_helper": dll.check(0x10001125, "e8 06 03 00 00"),
                "sleep_200ms": dll.check(0x10001136, "68 c8 00 00 00"),
                "call_followup_D7_helper": dll.check(0x10001140, "e8 5b 06 00 00"),
                "sleep_5000ms": dll.check(0x1000114B, "68 88 13 00 00"),
                "call_final_D6_helper": dll.check(0x10001155, "e8 66 09 00 00"),
                "D5_selector": dll.check(0x100014C7, "68 d5 00 00 00"),
                "D7_selector": dll.check(0x10001828, "68 d7 00 00 00"),
                "D6_selector": dll.check(0x10001B48, "68 d6 00 00 00"),
                "D5_routine_high_byte": dll.check(0x100015B7, "8a 4e 09 88 48 08"),
                "D5_routine_low_byte": dll.check(0x100015C1, "8a 4e 08"),
                "D5_optional_command_length_gate": dll.check(0x100015C9, "66 39 6e 10"),
                "D5_optional_command_pointer": dll.check(0x100015CF, "8b 56 0c"),
                "D7_routine_high_byte": dll.check(0x100018B4, "8a 4d 09 88 48 08"),
                "D7_routine_low_byte": dll.check(0x100018BE, "8a 4d 08"),
                "D6_routine_high_byte": dll.check(0x10001C18, "8a 4d 09 88 48 08"),
                "D6_routine_low_byte": dll.check(0x10001C22, "8a 4d 08"),
                "status_key_load": dll.check(0x10001D37, "66 8b 56 0a"),
            },
        },
        "fixed_request_examples": {
            "LDA Steering Vibration": "21 E2 15 08",
            "LTA Steering Vibration": "21 E2 15 88",
            "LCA Steering Vibration": "21 E2 15 C8",
            "note": (
                "The same four request bytes are used by D5/D7/D6 for these vibration rows because "
                "their routine-command variable is zero; the selectors differ in receive-mask semantics, "
                "not in the resolved 21 E2 send prefix."
            ),
        },
        "conclusion": (
            "The FRC_P5 steering-related Active-Test surface is routine-only in the pinned corpus: "
            "there are no type-68 direct P5 Active-Test records, and LDA/LTA/LCA Steering Vibration "
            "are fixed routine selectors with no variable-backed command, output-mask, or button-data "
            "payload. Techstream therefore exposes no controllable steering angle, torque, amplitude, "
            "or other continuous lateral setpoint through these records. The downstream effect of FRC "
            "routines 0x1508/0x1588/0x15C8 is not visible in host software; 0x1588 is instead a concrete "
            "camera-side probe/capture trigger for identifying the FRC-to-steering transport once live "
            "capture or FRC firmware is available."
        ),
        "boundary": (
            "The fixed 21 E2 routine path is sent to the FRC diagnostic domain; it does not prove which "
            "in-vehicle message the camera emits, that the EPS is the direct downstream recipient, or "
            "that any such message is unauthenticated. It is not the missing arbitrary lateral writer."
        ),
    }


# ── assembly ─────────────────────────────────────────────────────────────────


def build(root: Path) -> dict:
    parser = DDBParser()
    h_corr = json.loads(H_CORR.read_text())
    modern = h_corr["modern_angle_domain"]
    factory = json.loads(FACTORY.read_text())
    master_factory = next(f for f in factory["factories"] if f["format_version"] == 1)
    type44 = [r for r in master_factory["records"] if r["table_type"] == 44]
    if {r["class_name"] for r in type44} != {"CDbInstallingEcuListTable"}:
        raise ValueError(
            "master factory type-44 class is not CDbInstallingEcuListTable"
        )

    installing_na = installing_ecu_list(parser, root, "NA")
    if installing_na["cooccurrence_keys"] != [
        f"0x{k:04X}" for k in FRC_COOCCURRENCE_KEYS
    ]:
        raise ValueError("NA cat498/cat499 co-occurrence keys changed")

    return {
        "schema_version": 5,
        "source": "Techstream V18.00.003",
        "sources": source_identities(root),
        "master_categories": {
            region: master_categories(parser, root, region) for region in REGIONS
        },
        "master_dll_roles": {
            region: category_498_dll_roles(parser, root, region) for region in REGIONS
        },
        "installing_ecu_list": {
            "factory_identity": {
                "factory_va": master_factory["factory_va"],
                "table_type": 44,
                "class_name": "CDbInstallingEcuListTable",
                "constructor_va": type44[0]["constructor_va"],
                "constructor_export": type44[0]["constructor_export"],
            },
            "NA": installing_na,
            "EU": installing_ecu_list(parser, root, "EU"),
            "JP": installing_ecu_list(parser, root, "JP"),
            "interpretation": (
                "Type-44 +0x04 is the install-set id (CDbInstallingEcuListTable::"
                "FindDbItem1 key). It resolves deterministically to model names through "
                "the master chain type-5 CDbEcuGroupTable (VehicleId +0x04 -> install-set "
                "id +0x06) and type-43 CDbVehicleNameTable (VehicleId +0x04 -> name "
                "+0x00). Install-set numbering is region-local: the numeric NA "
                "co-occurrence keys 0x1967/0x1B1A/0x1D54/0x1E6E also exist in the EU/JP "
                "masters but resolve different category sets there and do not carry the "
                "498+499 co-occurrence; each region carries its own distinct 498+499 keys. "
                "Sets with both FRC_P5 (498) and EMPS2_P5 (499) resolve to "
                "MAC/RZ450e/bZ4X/e-Palette-class models and are NOT Corolla evidence; "
                "Corolla-family TSS3 sets pair 498 with EMPS_P5 (405) instead."
            ),
        },
        "corolla_model_install_sets": corolla_model_install_sets(parser, root),
        "upstream_lateral_route": p5_upstream_lateral_route(parser, root),
        "brake_active_test_surface": abs_p5_active_test_surface(parser, root),
        "front_recognition_camera_2": {
            "did_rows_NA": frc_did_rows(parser, root, "NA"),
            "did_rows_region_check": {
                region: {
                    "matched_rows": len(frc_did_rows(parser, root, region)),
                    "target_steering_angle_negative": frc_target_steering_negative(
                        parser, root, region
                    ),
                }
                for region in REGIONS
            },
            "behavior_code_rows": frc_behavior_rows(parser, root),
            "security_state": {
                region: frc_security_state(parser, root, region) for region in REGIONS
            },
            "target_steering_angle_negative_note": (
                "FRC_P5 carries no named Target Steering Angle monitor in the type-62 "
                "CDbDatamonitorP5Table or the type-88 CDbBehaviorDataRecordP5Table in any region"
            ),
        },
        "vds_setting_table": vds_setting_table_evidence(root),
        "frc_routine_active_test": frc_routine_active_test_surface(parser, root),
        "tss3_operation_ffd_protocol": tss3_operation_protocol(root),
        "tss3_image_ffd": tss3_image_protocol(root),
        "advanced_drive_control": {
            "factory_semantics": {"ddb_ddr_p5_tables": ads_ddr_tables(root)},
            "ddr_behavior_data_rows": ads_ddr_rows(parser, root),
            "protocol": ads_ddr_protocol(root),
            "boundary": (
                "ADS_Eth_P5 rows 406/407 are Operation-FFD/DDR recorded snapshot fields, "
                "not proven live wire command fields"
            ),
        },
        "lane_departure_alert": {
            "behavior_code_rows": behavior_code_rows(parser, root),
        },
        "power_steering": {
            "EMPS_P5": emps_rows(parser, root, "EMPS_P5.ddb"),
            "emps_angle_conversion": emps_angle_conversion(parser, root),
            "target_lateral_id_semantics": emps_target_lateral_id_semantics(parser, root),
            "EMPS2_P5": emps_rows(parser, root, "EMPS2_P5.ddb"),
            "did_corpus_scan": corpus_did_scan(root, (0x1CEE, 0x1CEF)),
            "corolla_h_boundary": {
                "software_id": "8965H1202000",
                "modern_primary_data_ids": modern["primary_data_ids"],
                "supports_any_primary_data_id": modern["corolla_h_supports_any"],
            },
            "emps2_scope_note": (
                "EMPS2_P5 evidence here is limited to the 0x1CEE/0x1CEF monitor family "
                "and the VDS/master category identity; the steer-by-wire diagnostic "
                "vocabulary (steering-angle synchronization histories, dual-system ECU/motor "
                "overheat prevention, torque-sensor A/B calibration, reaction-force actuator "
                "angle offset) is intentionally not enumerated in this artifact and remains "
                "a separate bounded extraction if needed."
            ),
        },
        "interpretation_boundary": {
            "recovered": (
                "The true-TSS3 lateral-control diagnostic-domain holder is category 498 FRC_P5 "
                "(Front Recognition Camera 2) with dedicated master plugin roles 233/234 "
                "(GetTSS3ImageFFDP5_DT.dll / GetTSS3OperationFFDP5_DT.dll), LTA/LDA "
                "installation/customize/control/hands-off DID rows, and a read-only proprietary "
                "AB/EB Operation FFD protocol. VDS ECUNo 498 covers 52/9/39 NA/EU/JP VIN "
                "descriptor patterns including six NA 5YF families; the install-set chain joins "
                "498+499 sets to MAC/RZ450e/bZ4X/e-Palette-class models and Corolla-family "
                "TSS3 sets to 498+EMPS_P5(405). The ADS_Eth_P5 target-steering-angle order rows "
                "remain Advanced Drive snapshot evidence, and EMPS_P5/EMPS2_P5 remain the "
                "steering-side observer domain whose type-62 primary Data-ID declarations "
                "exclusively carry 0x1CEE/0x1CEF across the scanned P5 corpus. Diagnostic-domain "
                "holder means exactly that: physical control-path ownership is not asserted."
            ),
            "not_proved": [
                "the CAN/CAN-FD arbitration ID or wire encoding carrying any named target-angle value",
                "a byte-level FRC-to-Brake-to-B6 forwarding/transformation path despite the now-closed module dependency topology",
                "which ECU owns SecOC signing/freshness/key state for B6 or any upstream protected leg",
                "that the ADS_Eth_P5 DDR snapshot rows are live wire command fields",
                "that ADS Operation plugin DID 0x1C08 joins to ADS DDR rows 406/407",
                "any producer/bit-layout/authentication join from FRC_P5 to community NEW_MSG_8A_LAT_CONTROL (0x18A; the Reference screenshot corpus records 0x18A as one of 22 CAN-FD 64-byte IDs on buses 0 and 2, nothing more)",
                "that FRC_P5 equals the old Fr_Camera_P5 (430) or ADS_Eth_P5 (476) software domain",
                "that the Corolla-family 498+405 install sets imply EMPS2_P5 (499) vehicles use the same lateral contract",
                "the downstream in-vehicle FRC output caused by fixed routine-active-test IDs 0x1508/0x1588/0x15C8",
                "a unique 5YF-descriptor-to-VehicleId mapping (the per-pattern join is bounded, not unique)",
            ],
            "next_static_target": (
                "Decoded FRC_P5 plus category-435 ABS/Brake firmware acquisition (or a synchronized "
                "stock-LTA capture) to resolve the still-open payload transformation and SecOC sender "
                "ownership across the now-proved FRC/Brake/EPS communication topology. Use the "
                "read-only Operation FFD surface, ABS_P5 DID 0x107E, protected EPS B6, and fixed "
                "0x1588 LTA Steering Vibration routine as correlation references."
            ),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=TECHROOT)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    obj = build(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(obj, indent=2) + "\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
