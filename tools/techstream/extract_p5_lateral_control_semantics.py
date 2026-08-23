#!/usr/bin/env python3
"""Extract the Techstream P5 lateral-control evidence surface (schema v2).

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
)
TARGET_DLLS = (
    "KgpDataCtrl.dll",
    "GetTSS3ImageFFDP5_DT.dll",
    "GetTSS3OperationFFDP5_DT.dll",
    "GetADSDDRInfoP5_DT.dll",
    "GetADSOperationFFDP5_DT.dll",
    "CommandCommon.dll",
)
ADS_NAMES = (
    "Advanced Drive Control Target Steering Angle Speed Order Value",
    "Advanced Drive Control Target Steering Angle Order Value",
    "Lateral Control Switch Status",
)
LDA_SIGNATURES = ("X2008", "X2073", "X2081", "X2082")
EMPS_MONITORS = tuple(range(2069, 2077))
FRC_BEHAVIOR_SIGNATURES = ("X2400", "X2001", "X2082", "X2166", "XF01B")
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


def frc_pattern_values(db, strings, patdisp_key: int) -> dict[int, str]:
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
        patterns = frc_pattern_values(db, strings, patdisp_key)
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
            "an Active-Test surface (roles 6/8/99/112/173) whose actuation semantics are "
            "not recovered here and remain bounded."
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
        "schema_version": 2,
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
                "that the ADS_Eth_P5 DDR snapshot rows are live wire command fields",
                "that ADS Operation plugin DID 0x1C08 joins to ADS DDR rows 406/407",
                "any producer/bit-layout/authentication join from FRC_P5 to community NEW_MSG_8A_LAT_CONTROL (0x18A; the Reference screenshot corpus records 0x18A as one of 22 CAN-FD 64-byte IDs on buses 0 and 2, nothing more)",
                "that FRC_P5 equals the old Fr_Camera_P5 (430) or ADS_Eth_P5 (476) software domain",
                "that the Corolla-family 498+405 install sets imply EMPS2_P5 (499) vehicles use the same lateral contract",
                "the semantics of any category-498 Active-Test entry beyond its role bindings",
                "a unique 5YF-descriptor-to-VehicleId mapping (the per-pattern join is bounded, not unique)",
            ],
            "next_static_target": (
                "FRC_P5 firmware acquisition and the true-TSS3 producer contract: recover the FRC "
                "lateral-control output path and its join (if any) to EMPS/EMPS2 steering observers, "
                "using the read-only Operation FFD surface as the capture reference."
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
