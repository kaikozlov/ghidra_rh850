#!/usr/bin/env python3
"""Independently verify the true-TSS3 FRC_P5 lateral-control evidence surface.

Re-derives every pinned identity straight from the raw Techstream corpus:
exact file hashes, master category/DLL-role identities, the type-44
installing-ECU-list join, FRC_P5 DID/behavior rows and negatives, the ADS DDR
unit chain, the 0x1CEE/0x1CEF corpus exclusivity, and the plugin-DLL
machine-code byte anchors for the read-only AB/EB Operation FFD protocol and
the fixed FRC routine Active-Test executor.
No Ghidra and no importer on the generating tool: the oracle is the pinned
external corpus itself.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
ARTIFACT = REPO / "data/generated/techstream_v18/p5_lateral_control_semantics.json"
FACTORY = REPO / "data/generated/techstream_v18/ddb_factory_table_map.json"
sys.path.insert(0, str(REPO / "tools/techstream"))
from parse_ddb import DDBParser

passed = failed = 0
oracle = "independent_external_artifact+generated_self_check"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(
        f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}"
        + (f" ({detail})" if detail else "")
    )


def u16(raw: bytes, off: int) -> int:
    return struct.unpack_from("<H", raw, off)[0]


def u32(raw: bytes, off: int) -> int:
    return struct.unpack_from("<I", raw, off)[0]


def records(section) -> list[bytes]:
    size = section.decoded_record_size
    data = section.decoded_data
    return [data[i * size : (i + 1) * size] for i in range(section.header.record_count)]


def master_variable_blob(master, index: int) -> bytes:
    sec = master.sections[0]
    count = sec.header.record_count
    table_end = count * 6
    rel, length = struct.unpack_from("<IH", sec.decoded_data, (index - 1) * 6)
    return sec.decoded_data[table_end + rel : table_end + rel + length]


if not ROOT.is_dir():
    print("[SKIP] Techstream V18 unavailable")
    raise SystemExit(77)

ev = json.loads(ARTIFACT.read_text())
p = DDBParser()

# ── schema and exact source identities ───────────────────────────────────────

check("schema version", ev["schema_version"] == 4)

EXPECTED_FRC = {
    "NA": (49806, "63307a9b8a6bcafdc5ee4b3a04f67abdc2501ba296a2779e5edc7dbff846fe42"),
    "EU": (49662, "b35ca0ac6a0c12364b670e10baffeb81c6c73f5c4d0b7d47b962c21a5384e1cc"),
    "JP": (49662, "89db9903921124475d50035cb6cd91a3f2cdf284b3990ed9b832692f487bba5e"),
}
for region, expected in EXPECTED_FRC.items():
    data = (ROOT / region / "DB/FRC_P5.ddb").read_bytes()
    actual = (len(data), hashlib.sha256(data).hexdigest())
    check(
        f"FRC_P5.ddb {region} exact identity",
        actual == expected
        and (
            ev["sources"]["FRC_P5.ddb"][region]["size"],
            ev["sources"]["FRC_P5.ddb"][region]["sha256"],
        )
        == expected,
    )

EXPECTED_SOURCES_NA = {
    "EMPS_P5.ddb": (
        49042,
        "1e5ffc4f998570458fa86dd0d563949006f9e0781f15d118d01e80656fadd199",
    ),
    "EMPS2_P5.ddb": (
        44790,
        "e80d722f3b80077e3f7bdc4b815c2035b21a51cefb6cd26dc6de3ada20939312",
    ),
    "LDA_P5.ddb": (
        11268,
        "10019b5cce2406110b5f064095f203bc1998d3997a6cf2e913512622773e3336",
    ),
    "Fr_Camera_P5.ddb": (
        14590,
        "364f792097ed3d04da534adf06f5064a316bc5420bea7ff6ac296c58fc0bc847",
    ),
    "ADS_Eth_P5.ddb": (
        94656,
        "deb8334a593efa5f98865f959c463f6803b7d72aa4d5ab86ba3de9b4cca39d70",
    ),
    "ADeU_Eth_P5.ddb": (None, None),  # identity pinned via master category only
}
for name, (size, sha) in EXPECTED_SOURCES_NA.items():
    if size is None:
        continue
    data = (ROOT / "NA/DB" / name).read_bytes()
    actual = (len(data), hashlib.sha256(data).hexdigest())
    check(
        f"{name} exact NA identity",
        actual == (size, sha)
        and (ev["sources"][name]["NA"]["size"], ev["sources"][name]["NA"]["sha256"])
        == (size, sha),
    )

EXPECTED_DLLS = {
    "KgpDataCtrl.dll": (
        721008,
        "e5235bc0c241c6a450fe461031eed0915675032b1db994bd54d98818fac88aa9",
    ),
    "GetTSS3ImageFFDP5_DT.dll": (
        135168,
        "787f88b5e14b5aa38ae676df5e8986c3d0df1de297f3ff8915579078afac63e4",
    ),
    "GetTSS3OperationFFDP5_DT.dll": (
        73728,
        "8d8461cf1b1f9b9917919fa4ea366891e0867c2f3e82d56d1a27ae2990e38f86",
    ),
    "GetADSDDRInfoP5_DT.dll": (
        106496,
        "28a4474c71344970c3e9736af1d835215d0aac02d4f31cee832101981f1246df",
    ),
    "GetADSOperationFFDP5_DT.dll": (
        77824,
        "c5549207080aabc0a7d415caa610818fd0df4ca2afc78a14b3c5a6e1861d8bce",
    ),
    "GetDatMonSignalInfoP5_DT.dll": (
        57344,
        "8f9e6149fca5e4fe6d9827f394f43019e6ee415c6f0ffc3b381ce6ca4c298f2a",
    ),
    "GetRoutineActTstInitP5_DT.dll": (
        65536,
        "1bc3fa58221a015a9f5ea70e5ddc98845994728927c034f062060dddc6213267",
    ),
    "GetRoutineActTstSignalInfoP5_DT.dll": (
        65536,
        "d3de07e1f5bf42b86fc8138147455e67310a9e116a17276bfa5b83dd759c2f9d",
    ),
    "SingleRoutineActTstP5_DT.dll": (
        57344,
        "f4be7b48751ea328f0111d8a0628d114af5391799cde43b72aa87b5b647e7adf",
    ),
}
for name, (size, sha) in EXPECTED_DLLS.items():
    data = (ROOT / "bin" / name).read_bytes()
    actual = (len(data), hashlib.sha256(data).hexdigest())
    check(
        f"{name} exact identity",
        actual == (size, sha)
        and (ev["sources"][name]["size"], ev["sources"][name]["sha256"]) == (size, sha),
        name,
    )

# ── master categories and dedicated plugin roles ────────────────────────────

EXPECTED_CATEGORIES = {
    "EMPS_P5.ddb": (405, 20, "EMPS"),
    "EMPS2_P5.ddb": (499, 20, "Steering Actuator"),
    "LDA_P5.ddb": (418, 20, "Lane Departure Alert"),
    "Fr_Camera_P5.ddb": (430, 20, "Front Recognition Camera"),
    "ADS_Eth_P5.ddb": (476, 20, "Advanced Drive Control"),
    "ADeU_Eth_P5.ddb": (477, 20, "Advanced Drive eXtension Control"),
    "FRC_P5.ddb": (498, 20, "Front Recognition Camera 2"),
}
for region in ("NA", "EU", "JP"):
    master = p.parse_master_db(ROOT / region / "DB/Toyota.ddb")
    region_strings = p.load_string_db(ROOT / region / "DB/M_English.ddb")
    cats = p.extract_master_ecu_categories(master.sections[16])
    for name, expected in EXPECTED_CATEGORIES.items():
        rows = [row for row in cats if row.database_name == name]
        check(f"{region} {name} unique master category", len(rows) == 1)
        row = rows[0]
        actual = (
            row.category_id,
            row.generation,
            region_strings.get_string(row.ecu_name_string_index),
        )
        check(
            f"{region} {name} OEM category identity",
            actual == expected
            and (
                ev["master_categories"][region][name]["category_id"],
                ev["master_categories"][region][name]["generation"],
                ev["master_categories"][region][name]["resolved_ecu_name"],
            )
            == expected,
        )
    dlls = p.extract_master_dlls(master.sections[19])
EXPECTED_498_ROLES = {
    ("GetDatMonListP5_DT.dll", 498, 5),
    ("GetActTstListP5_DT.dll", 498, 6),
    ("GetActTstInitP5_DT.dll", 498, 8),
    ("DelDiagCodeP4.dll", 498, 25),
    ("JudgeDiagStatusP5_DT.dll", 498, 41),
    ("GetDatMonSignalInfoP5_DT.dll", 498, 65),
    ("GetCID_SID22_DT.dll", 498, 82),
    ("GetMultiActInitP5_DT.dll", 498, 99),
    ("GetSupportP5_DT.dll", 498, 103),
    ("GetATSignalInfoP5_DT.dll", 498, 112),
    ("GetRoBP5_DT.dll", 498, 160),
    ("DelRoBP5_DT.dll", 498, 161),
    ("GetDatMonListP5ForActTest_DT.dll", 498, 173),
    ("GetTSS3ImageFFDP5_DT.dll", 498, 233),
    ("GetTSS3OperationFFDP5_DT.dll", 498, 234),
    ("GetADSDDRInfoP5_DT.dll", 0, 229),
}
for region in ("NA", "EU", "JP"):
    check(
        f"{region} full category-498 plugin-role table + global ADS DDR role 229 (raw master + artifact)",
        EXPECTED_498_ROLES <= {(r.dll_name, r.category_id, r.dll_role_id) for r in dlls}
        and {
            (r["dll_name"], r["category_id"], r["dll_role_id"])
            for r in ev["master_dll_roles"][region]
        }
        == EXPECTED_498_ROLES,
    )
check(
    "ADS DDR role 229 is category-0/global, not an FRC/ADS category binding",
    next(
        r
        for r in ev["master_dll_roles"]["NA"]
        if r["dll_name"] == "GetADSDDRInfoP5_DT.dll"
    )["category_id"]
    == 0,
)
check(
    "Operation FFD direction keeps read-only wording scoped to the AB/EB protocol",
    "read-only" in ev["tss3_operation_ffd_protocol"]["direction"]
    and "Active-Test" in ev["tss3_operation_ffd_protocol"]["direction"]
    and "fixed routine control" in ev["tss3_operation_ffd_protocol"]["direction"]
    and "not a live setpoint writer" in ev["tss3_operation_ffd_protocol"]["direction"],
)

# ── type-44 installing ECU list ──────────────────────────────────────────────

factory = json.loads(FACTORY.read_text())
master_factory = next(f for f in factory["factories"] if f["format_version"] == 1)
type44 = [r for r in master_factory["records"] if r["table_type"] == 44]
check(
    "master factory type-44 is CDbInstallingEcuListTable",
    {r["class_name"] for r in type44} == {"CDbInstallingEcuListTable"},
)


def type44_keys(region: str) -> dict[int, dict[int, str]]:
    master = p.parse_master_db(ROOT / region / "DB/Toyota.ddb")
    strings = p.load_string_db(ROOT / region / "DB/M_English.ddb")
    section = master.sections[44]
    check(f"{region} type-44 record size 24", section.decoded_record_size == 24)
    out: dict[int, dict[int, str]] = {}
    for raw in records(section):
        out.setdefault(u16(raw, 0x04), {})[u16(raw, 0x06)] = strings.get_string(
            u32(raw, 0x00)
        )
    return out


na_keys = type44_keys("NA")
cooccur = sorted(k for k, cats in na_keys.items() if 498 in cats and 499 in cats)
check(
    "NA cat498+cat499 co-occur at exactly the four pinned keys",
    cooccur == [0x1967, 0x1B1A, 0x1D54, 0x1E6E]
    and ev["installing_ecu_list"]["NA"]["cooccurrence_keys"]
    == ["0x1967", "0x1B1A", "0x1D54", "0x1E6E"],
)

for key in (0x1967, 0x1B1A):
    cats = na_keys[key]
    check(
        f"NA key 0x{key:04X} installation set spans the lateral stack",
        {405, 418, 430, 476, 477, 498, 499} <= set(cats)
        and ev["installing_ecu_list"]["NA"]["key_sets"][f"0x{key:04X}"]["categories"]
        == sorted(cats),
    )
check(
    "NA key 0x1967 cat418 display is Lane Control",
    na_keys[0x1967][418] == "Lane Control",
)
for key in (0x1D54, 0x1E6E):
    cats = na_keys[key]
    check(
        f"NA key 0x{key:04X} steering-trio display names",
        cats[499] == "Steering Torque Actuator"
        and cats[498] == "Front Recognition Camera"
        and cats[405] == "EMPS / Steering Control Actuator",
    )
for region in ("EU", "JP"):
    keys = type44_keys(region)
    region_cooccur = sorted(
        k for k, cats in keys.items() if 498 in cats and 499 in cats
    )
    # The four numeric NA keys DO exist in EU/JP masters, but there they
    # resolve different category sets and never carry the 498+499 pair.
    check(
        f"{region} NA numeric keys exist but none carries the 498+499 co-occurrence",
        all(
            k in keys and not (498 in keys[k] and 499 in keys[k])
            for k in (0x1967, 0x1B1A, 0x1D54, 0x1E6E)
        )
        and region_cooccur != [0x1967, 0x1B1A, 0x1D54, 0x1E6E]
        and [int(k, 16) for k in ev["installing_ecu_list"][region]["cooccurrence_keys"]]
        == region_cooccur,
    )
    check(
        f"{region} 498+499 co-occurrence keys are distinct from the NA numeric keys",
        not (set(region_cooccur) & {0x1967, 0x1B1A, 0x1D54, 0x1E6E}),
    )
    check(
        f"{region} key_sets exactly match its own co-occurrence keys",
        sorted(int(k, 16) for k in ev["installing_ecu_list"][region]["key_sets"])
        == region_cooccur
        and all(
            498 in ks["categories"] and 499 in ks["categories"]
            for ks in ev["installing_ecu_list"][region]["key_sets"].values()
        ),
    )

check(
    "NA key_sets exactly match its own co-occurrence keys",
    sorted(int(k, 16) for k in ev["installing_ecu_list"]["NA"]["key_sets"])
    == [0x1967, 0x1B1A, 0x1D54, 0x1E6E],
)
# ── FRC_P5 DID rows and negatives ────────────────────────────────────────────

EXPECTED_FRC_ROWS = [
    (0x1202, 12, 12, "LDA Installation Availability"),
    (0x1202, 13, 13, "LTA Installation Availability"),
    (0x1202, 14, 14, "LCA Installation Availability"),
    (0x1501, 0, 7, "LDA Customize Condition Flag"),
    (0x1501, 8, 15, "LDA Control Condition"),
    (0x1601, 0, 7, "LTA Switch Condition Flag"),
    (0x1601, 8, 15, "LTA Control Condition"),
    (0x1681, 0, 7, "LCA Customize Condition Flag"),
    (0x1681, 8, 15, "LCA Control Condition"),
    (0x1705, 12, 12, "PCS AES Invalid Flag"),
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
]


def frc_rows(region: str) -> list[tuple[int, int, int, str]]:
    db = p.parse_ecu_db(ROOT / region / "DB/FRC_P5.ddb")
    strings = p.load_string_db(ROOT / region / "DB/M_English.ddb")
    out = []
    for raw in records(db.sections[62]):
        key = (
            u16(raw, 0x36),
            u16(raw, 0x2C),
            u16(raw, 0x2E),
            strings.get_string(u32(raw, 0x18)),
        )
        if key in EXPECTED_FRC_ROWS:
            out.append(key)
    return sorted(out)


for region in ("NA", "EU", "JP"):
    check(
        f"{region} FRC lateral DID rows exact",
        frc_rows(region) == sorted(EXPECTED_FRC_ROWS),
    )
check(
    "artifact pins FRC DID rows",
    sorted(
        (int(r["data_id"], 16), r["bit_range"][0], r["bit_range"][1], r["name"])
        for r in ev["front_recognition_camera_2"]["did_rows_NA"]
    )
    == sorted(EXPECTED_FRC_ROWS),
)

frc_na = p.parse_ecu_db(ROOT / "NA/DB/FRC_P5.ddb")
na_strings = p.load_string_db(ROOT / "NA/DB/M_English.ddb")
frc_behavior = {
    row.fields["behavior_signature"]: na_strings.get_string(
        row.fields["name_string_index"]
    )
    for row in p.extract_priority_records(frc_na.sections[87])
    if row.fields.get("behavior_signature")
    in {"X2400", "X2001", "X2082", "X2166", "XF01B"}
}
EXPECTED_FRC_BEHAVIOR = {
    "X2400": "Lateral Control System Malfunction",
    "X2001": "Steering Angle Sensor Malfunction",
    "X2082": "Power Steering Control System for Steering Assist Steering Angle Malfunction",
    "X2166": 'Communication Error by ECU Security Key Not Registered (Power Steering Control Module "A")',
    "XF01B": "ECU Security Key Not Registered",
}
check(
    "FRC type-87 lateral/steering/security behavior codes exact",
    frc_behavior == EXPECTED_FRC_BEHAVIOR,
)
check(
    "artifact pins FRC behavior rows",
    {
        r["behavior_signature"]: r["name"]
        for r in ev["front_recognition_camera_2"]["behavior_code_rows"]
    }
    == EXPECTED_FRC_BEHAVIOR,
)

for region in ("NA", "EU", "JP"):
    db = p.parse_ecu_db(ROOT / region / "DB/FRC_P5.ddb")
    strings = p.load_string_db(ROOT / region / "DB/M_English.ddb")
    hits = [
        (t, strings.get_string(u32(raw, 0x18)) or "")
        for t in (62, 88)
        for raw in records(db.sections[t])
        if "target steering" in (strings.get_string(u32(raw, 0x18)) or "").lower()
    ]
    check(
        f"{region} FRC has no named Target Steering Angle type62/88 monitor",
        hits == []
        and ev["front_recognition_camera_2"]["did_rows_region_check"][region][
            "target_steering_angle_negative"
        ]["matches"]
        == [],
    )

# ── plugin DLL byte anchors ─────────────────────────────────────────────────


def pe_of(name: str) -> tuple[bytes, pefile.PE]:
    data = (ROOT / "bin" / name).read_bytes()
    pe = pefile.PE(str(ROOT / "bin" / name), fast_load=True)
    return data, pe


def anchor(data: bytes, pe: pefile.PE, va: int, expected_hex: str) -> bool:
    off = pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)
    expected = bytes.fromhex(expected_hex)
    return data[off : off + len(expected)] == expected


def import_names(path: Path) -> set[str]:
    pe = pefile.PE(str(path), fast_load=True)
    pe.parse_data_directories(
        directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]]
    )
    names = set()
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        for imp in entry.imports:
            if imp.name:
                names.add(imp.name.decode())
    return names


op_data, op_pe = pe_of("GetTSS3OperationFFDP5_DT.dll")
op_imports = import_names(ROOT / "bin/GetTSS3OperationFFDP5_DT.dll")
check(
    "TSS3 Operation imports CommFrameSendReceiveExt/GetCommFrmInfo",
    "?CommFrameSendReceiveExt@CCommCachePlus@@QAEKPAVCCommFrameData@@G@Z" in op_imports
    and "?GetCommFrmInfo@CCommCachePlus@@QAEKGPAUtagCOMMAND_DATA@@PAV?$CCmdList@VCCommFrameData@@@@K@Z"
    in op_imports,
)

OP_ANCHORS = {
    "behavior_code_subtype_0x11": (0x10001188, "b1 11"),
    "behavior_code_request_marker_ab": (0x100011A4, "c6 44 24 30 ab"),
    "behavior_code_expected_marker_eb": (0x100011A9, "c6 44 24 60 eb"),
    "behavior_frame_subtype_0x12": (0x100022B0, "b1 12"),
    "behavior_frame_request_marker_ab": (0x100022C6, "c6 44 24 54 ab"),
    "behavior_frame_expected_marker_eb": (0x100022D3, "c6 84 24 84 00 00 00 eb"),
    "data_record_subtype_0x13": (0x10001681, "b1 13"),
    "data_record_request_marker_ab": (0x100016A0, "c6 44 24 54 ab"),
    "data_record_expected_marker_eb": (0x100016A5, "c6 84 24 84 00 00 00 eb"),
    "parser_requires_len_over_6": (0x10001ABD, "8d 43 fa"),
    "parser_data_offset_6": (0x10001ACB, "be 06 00 00 00"),
    "parser_be16_did_shift": (0x10001BC1, "c1 e5 08"),
    "parser_block_len_byte": (0x10001BCC, "8a 40 08"),
    "parser_special_did_0x0501": (0x10001FDD, "66 81 7c 24 34 01 05"),
    "getcommfrinfo_selector_0x66": (0x100031D7, "6a 66"),
    "excluded_list_table_pointer": (0x100030F7, "be d4 91 00 10"),
}
for name, (va, expected_hex) in OP_ANCHORS.items():
    check(
        f"Operation FFD byte anchor {name}",
        anchor(op_data, op_pe, va, expected_hex)
        and ev["tss3_operation_ffd_protocol"]["byte_anchors"][name]["bytes"].replace(
            " ", ""
        )
        == expected_hex.replace(" ", ""),
    )

SPECIAL_IDS = [
    f"0x{v:04X}"
    for v in struct.unpack(
        "<15H",
        op_data[
            op_pe.get_offset_from_rva(0x100091D4 - op_pe.OPTIONAL_HEADER.ImageBase) :
        ][:30],
    )
]
check(
    "special/excluded ID list at 0x100091D4 exact",
    SPECIAL_IDS
    == [
        "0x2270",
        "0x2271",
        "0x2272",
        "0x2273",
        "0x2274",
        "0x2296",
        "0x2297",
        "0x2298",
        "0x2299",
        "0x227C",
        "0x227D",
        "0x229A",
        "0x22B0",
        "0x22B1",
        "0x22B2",
    ]
    and ev["tss3_operation_ffd_protocol"]["special_excluded_id_list"]["ids"]
    == SPECIAL_IDS,
)

img_data, img_pe = pe_of("GetTSS3ImageFFDP5_DT.dll")
img_imports = import_names(ROOT / "bin/GetTSS3ImageFFDP5_DT.dll")
check(
    "TSS3 Image main path imports CCmdImgOpeDdr::GetTSS3ImageFFDInfo",
    "?GetTSS3ImageFFDInfo@CCmdImgOpeDdr@@QAEKPAUtagCOMMAND_DATA@@PAVCCommCachePlusP5@@PAVCCommFrameData@@PAUTSS3IMAGE_FFD_MEMORIZED_INFO@@PAUTSS3IMAGE_FFD_INFO_P5@@@Z"
    in img_imports,
)
IMG_ANCHORS = {
    "probe_1402_selector_1": (0x100044ED, "6a 01"),
    "probe_1402_selector_1_did": (0x100044F6, "68 02 14 00 00"),
    "probe_1402_selector_2": (0x10004526, "6a 02"),
    "probe_1402_selector_2_did": (0x1000452F, "68 02 14 00 00"),
    "probe_1401_selector_2": (0x1000456E, "6a 02"),
    "probe_1401_selector_2_did": (0x10004577, "68 01 14 00 00"),
    "allocation_0x1ce4": (0x1000A7FE, "68 e4 1c 00 00"),
    "allocation_call": (0x1000A806, "e8 23 1e 00 00"),
}
for name, (va, expected_hex) in IMG_ANCHORS.items():
    check(
        f"TSS3 Image byte anchor {name}",
        anchor(img_data, img_pe, va, expected_hex)
        and ev["tss3_image_ffd"]["byte_anchors"][name]["bytes"].replace(" ", "")
        == expected_hex.replace(" ", ""),
    )

# ── ADS DDR rows and unit chain ──────────────────────────────────────────────

ads = p.parse_ecu_db(ROOT / "NA/DB/ADS_Eth_P5.ddb")
sec134 = ads.sections[134]
ads_rows = {}
for i, raw in enumerate(records(sec134)):
    name = na_strings.get_string(u32(raw, 0x18))
    if name in {
        "Lateral Control Switch Status",
        "Advanced Drive Control Target Steering Angle Speed Order Value",
        "Advanced Drive Control Target Steering Angle Order Value",
    }:
        ads_rows[i] = (
            name,
            u16(raw, 0x28),
            u16(raw, 0x2A),
            u16(raw, 0x2C),
            u16(raw, 0x30),
        )
check(
    "ADS DDR lateral rows exact",
    ads_rows
    == {
        143: ("Lateral Control Switch Status", 1, 7, 7, 104),
        406: (
            "Advanced Drive Control Target Steering Angle Speed Order Value",
            60,
            0,
            31,
            0,
        ),
        407: ("Advanced Drive Control Target Steering Angle Order Value", 61, 0, 31, 0),
    },
)

phy = {u16(raw, 0x0C): u16(raw, 0x0E) for raw in records(ads.sections[13])}
units = {
    u32(raw, 0x04): na_strings.get_string(u32(raw, 0x00))
    for raw in records(ads.sections[15])
}
check(
    "ADS DDR row 406 unit resolves rad/s via PhyData 60 -> unit key 452",
    units[phy[60]] == "rad/s",
)
check(
    "ADS DDR row 407 unit resolves rad via PhyData 61 -> unit key 81",
    units[phy[61]] == "rad",
)
check(
    "artifact pins ADS rows with units",
    {
        r["record_index"]: (
            r["name"],
            r["physical_data_key"],
            r["bit_range"],
            r["resolved_unit"],
        )
        for r in ev["advanced_drive_control"]["ddr_behavior_data_rows"]["rows"]
    }
    == {
        143: ("Lateral Control Switch Status", 1, [7, 7], None),
        406: (
            "Advanced Drive Control Target Steering Angle Speed Order Value",
            60,
            [0, 31],
            "rad/s",
        ),
        407: (
            "Advanced Drive Control Target Steering Angle Order Value",
            61,
            [0, 31],
            "rad",
        ),
    },
)

ddr_data, ddr_pe = pe_of("GetADSDDRInfoP5_DT.dll")
DDR_ANCHORS = {
    "physical_data_key_read": (0x100080EA, "66 8b 4a 28"),
    "bit_end_read": (0x10008254, "66 8b 50 2c"),
    "bit_start_subtract": (0x10008258, "66 2b 50 2a"),
    "pattern_display_key_read": (0x1000816A, "66 8b 41 30"),
}
for name, (va, expected_hex) in DDR_ANCHORS.items():
    check(
        f"GetADSDDRInfo byte anchor {name}",
        anchor(ddr_data, ddr_pe, va, expected_hex)
        and ev["advanced_drive_control"]["protocol"]["byte_anchors"][name][
            "bytes"
        ].replace(" ", "")
        == expected_hex.replace(" ", ""),
    )

adsop_data, adsop_pe = pe_of("GetADSOperationFFDP5_DT.dll")
ADSOP_ANCHORS = {
    "selector_1": (0x100012C7, "6a 01"),
    "did_0x1c08_selector_1": (0x100012D7, "68 08 1c 00 00"),
    "selector_6": (0x100012FB, "6a 06"),
    "did_0x1c08_selector_6": (0x1000130B, "68 08 1c 00 00"),
}
for name, (va, expected_hex) in ADSOP_ANCHORS.items():
    check(
        f"GetADSOperation byte anchor {name}",
        anchor(adsop_data, adsop_pe, va, expected_hex)
        and ev["advanced_drive_control"]["protocol"]["operation_plugin_did"][
            "byte_anchors"
        ][name]["bytes"].replace(" ", "")
        == expected_hex.replace(" ", ""),
    )

kgp_data, kgp_pe = pe_of("KgpDataCtrl.dll")
record_name_off = kgp_pe.get_offset_from_rva(0x2A583)
check(
    "DDR P5 record-name consumer loads record+0x18",
    kgp_data[record_name_off : record_name_off + 4] == bytes.fromhex("8b421850"),
)

factory = json.loads(FACTORY.read_text())
expected_ddr_classes = {
    133: "CDbDDRBehaviorCodeP5Table",
    134: "CDbDDRBehaviorDataRecordP5Table",
    135: "CDbDDRBehaviorDataInvalidP5Table",
}
for table_type, class_name in expected_ddr_classes.items():
    classes = {
        row["class_name"]
        for fac in factory["factories"]
        for row in fac["records"]
        if row["table_type"] == table_type
    }
    check(
        f"DDB table {table_type} exact DDR P5 class",
        classes == {class_name}
        and ev["advanced_drive_control"]["factory_semantics"]["ddb_ddr_p5_tables"][
            str(table_type)
        ]["class_name"]
        == class_name,
    )

# ── LDA and EMPS domains ────────────────────────────────────────────────────

EXPECTED_LDA = [
    ("X2008", "Steering Assist Request Invalid"),
    (
        "X2073",
        "Communication Error from Lane Control Module to Power Steering Control System",
    ),
    ("X2081", "Power Steering Control System for Steering Assist Invalid"),
    (
        "X2082",
        "Power Steering Control System for Steering Assist Steering Angle Malfunction",
    ),
]
lda_db = p.parse_ecu_db(ROOT / "NA/DB/LDA_P5.ddb")
lda_rows = [
    (
        row.fields["behavior_signature"],
        na_strings.get_string(row.fields["name_string_index"]),
    )
    for row in p.extract_priority_records(lda_db.sections[87])
    if row.fields.get("behavior_signature") in {"X2008", "X2073", "X2081", "X2082"}
]
check(
    "LDA steering-assist/producer diagnostics exact (raw DDB + artifact)",
    lda_rows == EXPECTED_LDA
    and [
        (x["behavior_signature"], x["name"])
        for x in ev["lane_departure_alert"]["behavior_code_rows"]
    ]
    == EXPECTED_LDA,
)

expected_names = [
    "Target Lateral ID",
    "Cooperative Control in Progress Flag",
    "Target Steering Angle After Output Compensation",
    "Advanced Drive Target Steering Angle",
    "Target Lateral ID (System 2)",
    "Cooperative Control in Progress Flag (System 2)",
    "Target Steering Angle After Output Compensation (System 2)",
    "Advanced Drive Target Steering Angle (System 2)",
]
for dbname in ("EMPS_P5", "EMPS2_P5"):
    edb = p.parse_ecu_db(ROOT / "NA/DB" / f"{dbname}.ddb")
    raw_rows = []
    for raw in records(edb.sections[62]):
        if u16(raw, 0x24) in range(2069, 2077):
            raw_rows.append(
                (
                    u16(raw, 0x24),
                    na_strings.get_string(u32(raw, 0x18)),
                    f"0x{u16(raw, 0x36):04X}",
                )
            )
    rows = ev["power_steering"][dbname]
    check(
        f"{dbname} modern angle monitor names (raw DDB + artifact)",
        [x[1] for x in raw_rows] == expected_names
        and [x["name"] for x in rows] == expected_names,
    )
    check(
        f"{dbname} modern angle monitor keys",
        [x[0] for x in raw_rows] == list(range(2069, 2077))
        and [x["monitor_key"] for x in rows] == list(range(2069, 2077)),
    )
    check(
        f"{dbname} modern angle DID split (raw DDB + artifact)",
        [x[2] for x in raw_rows] == ["0x1CEE"] * 4 + ["0x1CEF"] * 4
        and [x["primary_data_id"] for x in rows] == ["0x1CEE"] * 4 + ["0x1CEF"] * 4,
    )

# Type-62 +0x32 selects type-14 CDbPatDisp entries.  The value dictionary is
# identical across EMPS/EMPS2 and all three regions.
target_id = ev["power_steering"]["target_lateral_id_semantics"]
expected_target_ids = {
    0: "No Request (Manual Operation)", 1: "PCS", 4: "LDA", 10: "Hands Off LTA",
    11: "LTA/LCA", 13: "DESA (Slow Deceleration Control)",
    15: "DESA (Deceleration Stop Control)", 18: "SDG", 19: "PDA", 25: "AP",
    27: "Remote Parking", 35: "AD (Lv.3)", 37: "EM (Lv.3)", 39: "DES (Lv.3)",
    41: "AD (Lv.4)", 43: "EM (Lv.4)", 45: "DES (Lv.4)",
    49: "Self-Propelled Transport", 63: "Driver Operation",
}
check(
    "P5 Target Lateral ID exact OEM value dictionary",
    target_id["oem_name"] == "Target Lateral ID"
    and {int(k): v for k, v in target_id["value_dictionary"].items()} == expected_target_ids,
)
for region in ("NA", "EU", "JP"):
    region_strings = p.load_string_db(ROOT / region / "DB/M_English.ddb")
    for database in ("EMPS_P5.ddb", "EMPS2_P5.ddb"):
        edb = p.parse_ecu_db(ROOT / region / "DB" / database)
        expected_pat_key = 39 if database == "EMPS_P5.ddb" else 29
        raw_monitors = {
            u16(raw, 0x24): raw for raw in records(edb.sections[62])
            if u16(raw, 0x24) in (2069, 2073)
        }
        raw_patterns = {
            u32(raw, 0x04): region_strings.get_string(u32(raw, 0x00))
            for raw in records(edb.sections[14])
            if u16(raw, 0x0C) == expected_pat_key
        }
        check(
            f"{region} {database} Target Lateral ID raw monitor/pattern join",
            set(raw_monitors) == {2069, 2073}
            and all(
                u16(raw, 0x2A) == 1
                and (u16(raw, 0x2C), u16(raw, 0x2E)) == (0, 7)
                and u16(raw, 0x32) == expected_pat_key
                and u16(raw, 0x36) == (0x1CEE if key == 2069 else 0x1CEF)
                for key, raw in raw_monitors.items()
            )
            and raw_patterns == expected_target_ids,
        )
check(
    "P5 Target Lateral ID dictionary is identical across EMPS/EMPS2 and regions",
    all(
        row["pattern_display_key"] == (39 if database == "EMPS_P5.ddb" else 29)
        and row["physical_data_key"] == 1
        and row["bit_range"] == [0, 7]
        and {int(k): v for k, v in row["pattern_values"].items()} == expected_target_ids
        for region in ("NA", "EU", "JP")
        for database in ("EMPS_P5.ddb", "EMPS2_P5.ddb")
        for row in target_id["regions"][region][database].values()
    ),
)
check(
    "Target Lateral ID exact H-relevant OEM labels exist",
    {k: expected_target_ids[k] for k in (1, 4, 10, 11, 19, 25, 27)}
    == {1: "PCS", 4: "LDA", 10: "Hands Off LTA", 11: "LTA/LCA", 19: "PDA", 25: "AP", 27: "Remote Parking"},
)

conv = ev["power_steering"]["emps_angle_conversion"]
steer_conv = conv["steering_angle"]
check(
    "EMPS steering-angle conversion is raw 1.5 deg/count",
    steer_conv["name"] == "Steering Angle"
    and steer_conv["physical_data_key"] == 3
    and (steer_conv["mul"], steer_conv["div"], steer_conv["offset"]) == (15, 1, 0)
    and steer_conv["signed"] is True
    and steer_conv["decimal_point_count"] == 1
    and steer_conv["unit"] == "deg"
    and steer_conv["data_range"] == [-2048, 2047]
    and steer_conv["graph_range"] == [-30720, 30705]
    and "raw * mul / div + offset" in conv["formula"],
)
check(
    "EMPS conversion direction has independent SP1 witness",
    conv["regions"]["NA"]["vehicle_speed_sp1"]["monitor_key"] == 305
    and conv["regions"]["NA"]["vehicle_speed_sp1"]["data_range"] == [0, 30000]
    and conv["regions"]["NA"]["vehicle_speed_sp1"]["graph_range"] == [0, 3000]
    and (conv["regions"]["NA"]["vehicle_speed_sp1"]["mul"], conv["regions"]["NA"]["vehicle_speed_sp1"]["div"]) == (1, 10)
    and "0.0..300.0 km/h" in conv["direction_witness"],
)
check(
    "EMPS steering-angle conversion is cross-region identical",
    all(
        conv["regions"][region]["steering_angle"][field] == steer_conv[field]
        for region in ("NA", "EU", "JP")
        for field in ("physical_data_key", "physical_raw_hex", "mul", "div", "offset", "signed", "decimal_point_count", "unit", "data_range", "graph_range")
    ),
)
check(
    "GetDatMonSignalInfo P5 binds CDbPhyData to conversion fields",
    conv["plugin"]["dll"] == "GetDatMonSignalInfoP5_DT.dll"
    and set(conv["plugin"]["byte_anchors"]) == {
        "decimal_point_read", "decimal_point_store", "mul_copy", "div_copy", "offset_copy", "signed_copy",
        "mul_debug_binding", "div_debug_binding", "offset_debug_binding",
    }
    and conv["plugin"]["debug_strings"]["mul"]["value"].endswith("m_lMul=%ld")
    and conv["plugin"]["debug_strings"]["div"]["value"].endswith("m_lDiv=%ld")
    and conv["plugin"]["debug_strings"]["offset"]["value"].endswith("m_lOffset=%ld")
    and "m_byDecPntCount" in conv["plugin"]["debug_strings"]["decimal_point_count"]["value"],
)

scan_hits = {}
for path in sorted(ROOT.glob("*/DB/*_P5*.ddb")):
    region = path.parts[-3]
    db = p.parse_ecu_db(path)
    section = db.sections.get(62)
    if not section or not section.decoded_data:
        continue
    for raw in records(section):
        if u16(raw, 0x36) in (0x1CEE, 0x1CEF):
            scan_hits.setdefault((region, path.name), 0)
            scan_hits[(region, path.name)] += 1
check(
    "0x1CEE/0x1CEF type-62 primary Data-IDs occur only in EMPS_P5/EMPS2_P5 across the scanned P5 corpus",
    sorted(scan_hits)
    == sorted(
        {
            ("NA", "EMPS_P5.ddb"),
            ("NA", "EMPS2_P5.ddb"),
            ("EU", "EMPS_P5.ddb"),
            ("EU", "EMPS2_P5.ddb"),
            ("JP", "EMPS_P5.ddb"),
            ("JP", "EMPS2_P5.ddb"),
        }
    )
    and all(v == 8 for v in scan_hits.values())
    and {
        (o["region"], o["database"])
        for o in ev["power_steering"]["did_corpus_scan"]["owner_databases"]
    }
    == set(scan_hits),
)

boundary = ev["power_steering"]["corolla_h_boundary"]
check(
    "Corolla H lacks modern angle DIDs",
    boundary
    == {
        "software_id": "8965H1202000",
        "modern_primary_data_ids": ["0x1CEE", "0x1CEF"],
        "supports_any_primary_data_id": False,
    },
)

not_proved = ev["interpretation_boundary"]["not_proved"]
check(
    "interpretation keeps wire/snapshot/0x18A/Active-Test boundaries explicit",
    len(not_proved) == 8
    and "arbitration ID" in not_proved[0]
    and "snapshot" in not_proved[1]
    and "0x1C08" in not_proved[2]
    and "NEW_MSG_8A_LAT_CONTROL" in not_proved[3]
    and "screenshot corpus records 0x18A as one of 22 CAN-FD 64-byte IDs"
    in not_proved[3]
    and "Fr_Camera_P5" in not_proved[4]
    and "498+405" in not_proved[5]
    and "downstream" in not_proved[6]
    and "0x1588" in not_proved[6]
    and "not unique" in not_proved[7],
)
check(
    "recovered framing uses diagnostic-domain holder wording",
    "diagnostic-domain holder" in ev["interpretation_boundary"]["recovered"]
    and "physical control-path ownership is not asserted"
    in ev["interpretation_boundary"]["recovered"],
)
check(
    "Operation protocol grades byte-anchored vs recovered interpretation",
    set(ev["tss3_operation_ffd_protocol"]["evidence_grading"]["byte_anchored"])
    and set(
        ev["tss3_operation_ffd_protocol"]["evidence_grading"][
            "recovered_interpretation"
        ]
    )
    and ev["tss3_operation_ffd_protocol"]["behavior_code_query"][
        "response_layout_grade"
    ]
    == "recovered",
)
check(
    "EMPS2 scope records the bounded steer-by-wire vocabulary omission",
    "not enumerated" in ev["power_steering"]["emps2_scope_note"]
    and "steer-by-wire" in ev["power_steering"]["emps2_scope_note"],
)
check(
    "install-set wording states NA numeric keys exist in EU/JP without the 498+499 pair",
    "also exist in the EU/JP masters but resolve different category sets"
    in ev["installing_ecu_list"]["interpretation"]
    and "do not carry the 498+499 co-occurrence"
    in ev["installing_ecu_list"]["interpretation"]
    and "region-local" in ev["installing_ecu_list"]["interpretation"]
    and "NOT Corolla evidence" in ev["installing_ecu_list"]["interpretation"],
)

# ── install-set -> vehicle-name resolution chain (type 43/5/44) ──────────


def master_tables(region: str):
    master = p.parse_master_db(ROOT / region / "DB/Toyota.ddb")
    strings = p.load_string_db(ROOT / region / "DB/M_English.ddb")
    vnames = {}
    for raw in records(master.sections[43]):
        vnames[u16(raw, 0x04)] = strings.get_string(u32(raw, 0x00))
    vid_sets: dict[int, set[int]] = {}
    for raw in records(master.sections[5]):
        vid_sets.setdefault(u16(raw, 0x04), set()).add(u16(raw, 0x06))
    set_cats: dict[int, set[int]] = {}
    set_names: dict[int, set[str]] = {}
    for raw in records(master.sections[44]):
        set_cats.setdefault(u16(raw, 0x04), set()).add(u16(raw, 0x06))
    for vid, sets in vid_sets.items():
        name = vnames.get(vid)
        if name is None:
            continue
        for iset in sets:
            set_names.setdefault(iset, set()).add(name)
    return vnames, vid_sets, set_cats, set_names


EXPECTED_COOCCUR_NAMES = {
    "NA": {
        0x1967: {"MAC"},
        0x1B1A: {"MAC"},
        0x1D54: {"RZ450e"},
        0x1E6E: {"bZ4X"},
    },
    "EU": {
        0x2CBA: {"MAC"},
        0x31CD: {"MAC"},
        0x38C3: {"bZ4X"},
        0x38C6: {"bZ4X"},
        0x38C9: {"bZ4X"},
        0x38CC: {"bZ4X"},
        0x3A85: {"RZ450e"},
        0x3E72: {"bZ4X"},
        0x3E75: {"bZ4X"},
    },
    "JP": {
        0x1C5B: {"MAC"},
        0x1E0E: {"MAC"},
        0x1F10: {"RZ450e"},
        0x1FA0: {"e-Palette"},
    },
}
EXPECTED_VALID_RATIO = {"NA": "2480/2481", "EU": "4924/4925", "JP": "1627/1628"}
for region in ("NA", "EU", "JP"):
    vnames, vid_sets, set_cats, set_names = master_tables(region)
    ratio = sum(1 for vid in vid_sets if vid in vnames)
    check(
        f"{region} type-5 VehicleIds resolve to type-43 names (one sentinel)",
        f"{ratio}/{len(vid_sets)}" == EXPECTED_VALID_RATIO[region]
        and ev["installing_ecu_list"][region]["vehicle_resolution_chain"][
            "type5_vehicle_ids_resolving_to_type43_names"
        ]
        == EXPECTED_VALID_RATIO[region],
    )
    cooccur = sorted(k for k, cats in set_cats.items() if 498 in cats and 499 in cats)
    resolved = {k: set_names.get(k, set()) for k in cooccur}
    check(
        f"{region} 498+499 install sets resolve to exact model names",
        resolved == EXPECTED_COOCCUR_NAMES[region]
        and {
            int(s["install_set_id"], 16): set(s["vehicle_names"])
            for s in ev["installing_ecu_list"][region]["cooccurrence_sets"]
        }
        == EXPECTED_COOCCUR_NAMES[region],
    )
    check(
        f"{region} install-set field documented as FindDbItem1 key",
        ev["installing_ecu_list"][region]["field_offsets"]["install_set_id"]
        == "u16 +0x04 (FindDbItem1 lookup key)",
    )

# ── Corolla-family model install sets ─────────────────────────────────────

EXPECTED_COROLLA = [
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
]
na_vnames, na_vid_sets, na_set_cats, _ = master_tables("NA")
corolla_ok = True
for name, vid, iset, expected_cats in EXPECTED_COROLLA:
    if (
        na_vnames.get(vid) != name
        or iset not in na_vid_sets.get(vid, set())
        or tuple(sorted(na_set_cats.get(iset, set()))) != expected_cats
    ):
        corolla_ok = False
        break
check(
    "NA Corolla-family FRC_P5 install sets join exactly (498 with 405; GR uses 142)",
    corolla_ok
    and [
        (
            r["model_name"],
            int(r["vehicle_id"], 16),
            int(r["install_set_id"], 16),
            tuple(r["categories"]),
        )
        for r in ev["corolla_model_install_sets"]["rows"]
    ]
    == EXPECTED_COROLLA,
)

# ── VDS Setting_Table scan (recomputed from raw VDS) ────────────────────────

VDS_EXPECTED_REGIONS = {
    "NA": {498: (52, 1923), 499: (0, 0)},
    "EU": {498: (9, 27), 499: (0, 0)},
    "JP": {498: (39, 4212), 499: (0, 0)},
}


def vds_rows(data: bytes, ecu_no: int) -> list[tuple]:
    out = []
    for page_index in range(len(data) // 4096):
        page = data[page_index * 4096 : (page_index + 1) * 4096]
        if page[0] != 1:
            continue
        row_count = u16(page, 0x0C)
        if row_count == 0 or row_count > 100:
            continue
        for slot in range(row_count):
            offset = u16(page, 0x0E + 2 * slot) & 0x0FFF
            if offset + 36 > 4096:
                continue
            row = page[offset:]
            if u16(row, 0x00) != 5 or u32(row, 0x06) != ecu_no:
                continue
            try:
                pattern = row[0x0E : 0x0E + 22].decode("utf-16-le")
            except UnicodeDecodeError:
                continue
            if len(pattern) == 11:
                out.append((page_index, slot, u32(row, 0x02), u32(row, 0x0A), pattern))
    return out


for region in ("NA", "EU", "JP"):
    vpath = ROOT / f"DB/MDB/IT3Data_BDC_{region}.vds"
    vdata = vpath.read_bytes()
    node = ev["vds_setting_table"]["regions"][region]
    for ecu_no, (patterns, rows) in VDS_EXPECTED_REGIONS[region].items():
        got = vds_rows(vdata, ecu_no)
        check(
            f"VDS {region} ECUNo={ecu_no} Setting_Table recomputed",
            (len({r[4] for r in got}), len(got)) == (patterns, rows)
            and node[str(ecu_no)]["setting_table_rows"] == rows
            and node[str(ecu_no)]["vin_pattern_count"] == patterns,
        )

na_vds = (ROOT / "DB/MDB/IT3Data_BDC_NA.vds").read_bytes()
na_498 = vds_rows(na_vds, 498)
from collections import Counter as _Counter

na_counts = _Counter(r[4] for r in na_498)
SIX_5YF = (
    "5YFB4MBE___",
    "5YFB4MCE___",
    "5YFB4MDE___",
    "5YFP4MCE___",
    "5YFS4MCE___",
    "5YFT4MCE___",
)
check(
    "VDS NA six 5YF descriptor families each have 60 rows",
    all(na_counts.get(pat) == 60 for pat in SIX_5YF)
    and ev["vds_setting_table"]["pinned_na_5yf_families"]["patterns"] == list(SIX_5YF)
    and ev["vds_setting_table"]["pinned_na_5yf_families"]["rows_each"] == 60,
)
rep = [r for r in na_498 if r[4] == "5YFB4MBE___" and r[0] == 1189 and r[1] == 18]
check(
    "VDS NA representative row 5YFB4MBE___ page1189 slot18 recomputed",
    rep == [(1189, 18, 42, 6, "5YFB4MBE___")]
    and (
        ev["vds_setting_table"]["representative_row"]["setting_no"],
        ev["vds_setting_table"]["representative_row"]["connection_type"],
    )
    == (42, 6),
)
check(
    "VDS boundary wording: 499 is Setting_Table absence, not vehicle absence",
    "not vehicle absence" in ev["vds_setting_table"]["boundary"]
    and "Setting_Table" in ev["vds_setting_table"]["boundary"],
)

# ECU_Setting_Table raw anchors (request addresses 0x7A1 / 0x792)
page20 = na_vds[20 * 4096 : 21 * 4096]
VDS_ECU_ANCHORS = (
    (
        8,
        405,
        5,
        "7A1",
        "1c4dbd01d8f2a08e387d88d8f1995f5dc558a17528da73688662f50c40995691",
    ),
    (
        24,
        498,
        5,
        "792",
        "8e0b4d4c25d6f9aa5a960d745b735a8b77f097b57ca7a3832900c8b03a10970a",
    ),
)
for slot, ecu_no, phase, address, raw_sha in VDS_ECU_ANCHORS:
    offset = u16(page20, 0x0E + 2 * slot) & 0x0FFF
    row = page20[offset : offset + 40]
    marker = row.find(b"\xff\xfe")
    check(
        f"VDS ECU_Setting anchor slot {slot} (ECUNo {ecu_no} address {address})",
        u32(row, 0x02) == ecu_no
        and u32(row, 0x06) == phase
        and row[marker + 2 : marker + 5].decode("ascii") == address
        and hashlib.sha256(row).hexdigest() == raw_sha
        and any(
            a["ecu_no"] == ecu_no
            and a["address"] == address
            and a["raw40_sha256"] == raw_sha
            for a in ev["vds_setting_table"]["ecu_setting_table_anchors"]
        ),
    )

# ── FRC_P5 security-state rows recomputed from raw DDB ───────────────────

for region in ("NA", "EU", "JP"):
    db = p.parse_ecu_db(ROOT / region / "DB/FRC_P5.ddb")
    strings = p.load_string_db(ROOT / region / "DB/M_English.ddb")
    hit = None
    for raw in records(db.sections[62]):
        if u16(raw, 0x36) == 0x10AF and strings.get_string(u32(raw, 0x18)) == (
            "ECU Security Key Registered Incomplete Flag"
        ):
            hit = raw
            break
    check(f"{region} FRC 0x10AF security-key row present", hit is not None)
    if hit is not None:
        check(
            f"{region} FRC 0x10AF identity",
            u16(hit, 0x24) == 195
            and f"0x{u16(hit, 0x38):04X}" == "0x30AF"
            and (u16(hit, 0x2C), u16(hit, 0x2E)) == (0, 7),
        )
        pat_key = u16(hit, 0x32)
        patterns = {
            u32(raw, 0x04): strings.get_string(u32(raw, 0x00))
            for raw in records(db.sections[14])
            if u16(raw, 0x0C) == pat_key
        }
        check(
            f"{region} FRC 0x10AF pattern join 0 OFF / 1 ON / 2 Not Fixed",
            patterns == {0: "OFF", 1: "ON", 2: "Not Fixed"}
            and ev["front_recognition_camera_2"]["security_state"][region][
                "ecu_security_key_registered_incomplete_flag"
            ]["pattern_values"]
            == {"0": "OFF", "1": "ON", "2": "Not Fixed"},
        )
    behavior = {
        row.fields["behavior_signature"]: strings.get_string(
            row.fields["name_string_index"]
        )
        for row in p.extract_priority_records(db.sections[87])
    }
    check(
        f"{region} FRC type-87 X2166 + XF01B security behavior codes",
        behavior.get("XF01B") == "ECU Security Key Not Registered"
        and behavior.get("X2166")
        == 'Communication Error by ECU Security Key Not Registered (Power Steering Control Module "A")',
    )

frc_did_rowset = {
    (int(r["data_id"], 16), r["bit_range"][0], r["bit_range"][1], r["name"])
    for r in ev["front_recognition_camera_2"]["did_rows_NA"]
}
check(
    "FRC NA rows include LCA 0x1681 and PCS AES Invalid Flag 0x1705 bit12",
    (0x1681, 0, 7, "LCA Customize Condition Flag") in frc_did_rowset
    and (0x1681, 8, 15, "LCA Control Condition") in frc_did_rowset
    and (0x1705, 12, 12, "PCS AES Invalid Flag") in frc_did_rowset
    and (0x1202, 14, 14, "LCA Installation Availability") in frc_did_rowset,
)

# ── TSS3 Image FFD: raw byte tables, fixed reads, SecurityUnlock, key alg ─

check(
    "spec-5 DID table raw 24 bytes exact at 0x100134A8",
    img_data[
        img_pe.get_offset_from_rva(0x100134A8 - img_pe.OPTIONAL_HEADER.ImageBase) :
    ][:24].hex()
    == "0a110d1110111311161119111c111f112211251128110000"
    and struct.unpack(
        "<12H",
        img_data[
            img_pe.get_offset_from_rva(0x100134A8 - img_pe.OPTIONAL_HEADER.ImageBase) :
        ][:24],
    )[11]
    == 0x0000,
)
check(
    "spec-5 selector table raw 12 bytes exact at 0x100134C0",
    img_data[
        img_pe.get_offset_from_rva(0x100134C0 - img_pe.OPTIONAL_HEADER.ImageBase) :
    ][:12].hex()
    == "0105010502011e0a030a0300"
    and ev["tss3_image_ffd"]["spec5_dynamic_dids"]["spec7_extension"]["did"]
    == "0x1128",
)

FIXED_READ_ANCHORS = {
    "22_11_04_did_high_0x11": (0x1000129B, "b1 11"),
    "22_11_04_sid_0x22": (0x100012BE, "c6 44 24 38 22"),
    "22_11_04_fixed_low_0x04": (0x100012C3, "c6 44 24 50 04"),
    "22_11_04_expected_sid_0x62": (0x100012C8, "c6 84 24 80 00 00 00 62"),
    "22_11_04_expected_low_0x04": (0x100012D0, "c6 84 24 98 00 00 00 04"),
    "22_11_07_did_high_0x11": (0x10001748, "b1 11"),
    "22_11_07_low_0x07_via_bl": (0x1000175E, "b3 07"),
    "22_11_07_sid_0x22": (0x1000176A, "c6 44 24 28 22"),
    "22_11_07_expected_sid_0x62": (0x10001773, "c6 44 24 70 62"),
}
for name, (va, expected_hex) in FIXED_READ_ANCHORS.items():
    check(
        f"fixed metadata read byte anchor {name}",
        anchor(img_data, img_pe, va, expected_hex),
    )

check(
    "both fixed metadata reads promoted (22 11 04, 22 11 07)",
    [r["request"] for r in ev["tss3_image_ffd"]["fixed_metadata_reads"]]
    == ["22 11 04", "22 11 07"],
)

AB_ENUM_ANCHORS = {
    "enum_ab31_subtype": (0x10002E94, "b1 31"),
    "enum_ab31_request": (0x10002EB3, "c6 44 24 34 ab"),
    "enum_ab31_expected": (0x10002EB8, "c6 44 24 7c eb"),
    "record_ab33_subtype": (0x10003382, "b1 33"),
    "record_ab33_request": (0x100033AE, "c6 44 24 6c ab"),
    "record_ab33_expected": (0x100033B3, "c6 84 24 b4 00 00 00 eb"),
}
for name, (va, expected_hex) in AB_ENUM_ANCHORS.items():
    check(
        f"Image FFD proprietary anchor {name}",
        anchor(img_data, img_pe, va, expected_hex)
        and ev["tss3_image_ffd"]["byte_anchors"][name]["bytes"].replace(" ", "")
        == expected_hex.replace(" ", ""),
    )

cc_data, cc_pe = pe_of("CommandCommon.dll")
CC_ANCHORS = {
    "metadata_22_11_03_template": (0x100B1830, "22 11 03 00 ff ff ff 00 62 11 03 00"),
    "metadata_22_11_01_template": (0x100B17BC, "22 11 01 00 ff ff ff 00 62 11 01 00"),
    "metadata_22_20_81_template": (0x100B18C0, "22 20 81 00 ff ff ff 00 62 20 81 00"),
    "key_rotation_table": (0x100B1910, "01 02 03 03 02 01"),
    "calculate_key_data_sec_lv49": (0x1004AC4D, "b8 10 19 0b 10"),
    "security_unlock_27_03_template": (
        0x100B17EC,
        "27 03 00 00 ff ff 00 00 00 00 00 00 67 03 00 00",
    ),
    "security_unlock_27_04_template": (
        0x100B1800,
        "27 04 00 00 ff ff 00 00 67 04 00 00",
    ),
}
for name, (va, expected_hex) in CC_ANCHORS.items():
    check(
        f"CommandCommon byte anchor {name}",
        anchor(cc_data, cc_pe, va, expected_hex)
        and ev["tss3_image_ffd"]["command_common_anchors"][name]["bytes"].replace(
            " ", ""
        )
        == expected_hex.replace(" ", ""),
    )


def sec_lv49_key(seed: bytes) -> bytes:
    """Independently reimplemented CalculateKeyDataSecLv49 from the disassembly."""
    rot = (1, 2, 3, 3, 2, 1)
    key = bytearray(6)
    for i in range(6):
        x = seed[i]
        j = x & 7
        if j >= 6:
            j -= 6
        add = key[j] if j < i else seed[j]
        d = (x >> rot[i]) & 3
        r = ((x << (d + 1)) | (x >> (8 - (d + 1)))) & 0xFF
        key[i] = (r + add) & 0xFF
    return bytes(key)


KEY_VECTORS = (
    ("010203040506", "04070a0d1a64"),
    ("123456789abc", "9e6a50252409"),
    ("deadbeefcafe", "cbd8b6970cba"),
    ("000000000000", "000000000000"),
)
for seed_hex, key_hex in KEY_VECTORS:
    check(
        f"CalculateKeyDataSecLv49 vector {seed_hex} -> {key_hex}",
        sec_lv49_key(bytes.fromhex(seed_hex)).hex() == key_hex
        and {
            v["seed"]: v["key"]
            for v in ev["tss3_image_ffd"]["security_unlock"]["known_vectors"]
        }[seed_hex]
        == key_hex,
    )

check(
    "SecurityUnlock service 27 03 / 27 04 is template-anchored",
    ev["tss3_image_ffd"]["security_unlock"]["service"] == "27 03 / 27 04"
    and ev["tss3_image_ffd"]["security_unlock"]["wire_templates"]["27_03"].startswith(
        "VA 0x100B17EC"
    )
    and ev["tss3_image_ffd"]["security_unlock"]["wire_templates"]["27_04"].startswith(
        "VA 0x100B1800"
    ),
)

check(
    "Image FFD content boundary keeps no-lateral/no-write wording",
    "no write path" in ev["tss3_image_ffd"]["content_boundary"]
    and "no named lateral/LTA monitor content"
    in ev["tss3_image_ffd"]["content_boundary"],
)


# ── FRC_P5 fixed routine Active-Test surface ────────────────────────────────

EXPECTED_ROUTINES = {
    "LDA Steering Vibration": (0x1508, 511, 2),
    "LTA Steering Vibration": (0x1588, 542, 2),
    "LCA Steering Vibration": (0x15C8, 573, 2),
    "AES Automatic Steering in Control Notification": (0x160B, 609, 0),
}
EXPECTED_FRAME_RECORDS = {
    0xD5: ("d50049018302de01", 0x149, 0x283, 0x1DE, "0000000800"),
    0xD6: ("d60049018402de01", 0x149, 0x284, 0x1DE, "0000000400"),
    0xD7: ("d70049018502de01", 0x149, 0x285, 0x1DE, "0000000200"),
}
for region in ("NA", "EU", "JP"):
    db = p.parse_ecu_db(ROOT / region / "DB/FRC_P5.ddb")
    strings = p.load_string_db(ROOT / region / "DB/M_English.ddb")
    check(
        f"{region} FRC_P5 has no type-68 direct P5 Active-Test table",
        68 not in db.sections
        and ev["frc_routine_active_test"]["regions"][region][
            "type68_direct_p5_active_test_present"
        ]
        is False,
    )
    check(
        f"{region} FRC_P5 routine/status table census",
        db.sections[71].decoded_record_size == 64
        and db.sections[71].header.record_count == (70 if region == "JP" else 69)
        and db.sections[72].decoded_record_size == 12
        and db.sections[72].header.record_count == 2
        and db.sections[73].header.record_count == 192,
    )
    rows = {}
    for idx, raw in enumerate(records(db.sections[71])):
        name = strings.get_string(u32(raw, 0x08))
        if name in EXPECTED_ROUTINES:
            rows[name] = (idx, raw)
    check(
        f"{region} exact steering-related routine row set",
        set(rows) == set(EXPECTED_ROUTINES),
    )
    artifact_rows = {
        row["name"]: row
        for row in ev["frc_routine_active_test"]["regions"][region][
            "steering_related_rows"
        ]
    }
    for name, (rid, sort_key, status_key) in EXPECTED_ROUTINES.items():
        idx, raw = rows[name]
        check(
            f"{region} {name} exact type-71 fields",
            u16(raw, 0x1C) == rid
            and u16(raw, 0x38) == sort_key
            and u16(raw, 0x2E) == status_key
            and u16(raw, 0x28) == 0
            and u16(raw, 0x2A) == 0
            and u16(raw, 0x2C) == 0
            and artifact_rows[name]["record_index"] == idx
            and artifact_rows[name]["routine_id"] == f"0x{rid:04X}"
            and artifact_rows[name]["routine_command_variable"] == "0x0000"
            and artifact_rows[name]["output_mask_variable"] == "0x0000"
            and artifact_rows[name]["output_mask_button_variable"] == "0x0000",
        )

    status_rows = [raw for raw in records(db.sections[72]) if u16(raw, 0x00) == 2]
    master = p.parse_master_db(ROOT / region / "DB/Toyota.ddb")
    check(
        f"{region} vibration status key 2 resolves to byte 02",
        len(status_rows) == 1
        and status_rows[0].hex() == "020054000100000000000000"
        and u16(status_rows[0], 0x02) == 0x54
        and master_variable_blob(master, 0x54) == b"\x02"
        and ev["frc_routine_active_test"]["regions"][region][
            "steering_vibration_status_pattern"
        ]["pattern_bytes"]
        == "02",
    )

    frame_sec = master.sections[17]
    for selector, (
        raw_hex,
        send_ref,
        mask_ref,
        check_ref,
        mask_hex,
    ) in EXPECTED_FRAME_RECORDS.items():
        matches = [raw for raw in records(frame_sec) if u16(raw, 0) == selector]
        check(
            f"{region} master comm-frame 0x{selector:02X} exact raw/resolved bytes",
            len(matches) == 1
            and matches[0].hex() == raw_hex
            and u16(matches[0], 2) == send_ref
            and u16(matches[0], 4) == mask_ref
            and u16(matches[0], 6) == check_ref
            and master_variable_blob(master, send_ref) == bytes.fromhex("21e2")
            and master_variable_blob(master, mask_ref) == bytes.fromhex(mask_hex)
            and master_variable_blob(master, check_ref) == bytes.fromhex("61e2"),
        )

# The generic routine executor is byte-checked independently from the generated artifact.
single_data, single_pe = pe_of("SingleRoutineActTstP5_DT.dll")
ACTIVE_EXECUTOR_ANCHORS = {
    "call_initial_D5_helper": (0x10001125, "e8 06 03 00 00"),
    "sleep_200ms": (0x10001136, "68 c8 00 00 00"),
    "call_followup_D7_helper": (0x10001140, "e8 5b 06 00 00"),
    "sleep_5000ms": (0x1000114B, "68 88 13 00 00"),
    "call_final_D6_helper": (0x10001155, "e8 66 09 00 00"),
    "D5_selector": (0x100014C7, "68 d5 00 00 00"),
    "D7_selector": (0x10001828, "68 d7 00 00 00"),
    "D6_selector": (0x10001B48, "68 d6 00 00 00"),
    "D5_routine_high_byte": (0x100015B7, "8a 4e 09 88 48 08"),
    "D5_routine_low_byte": (0x100015C1, "8a 4e 08"),
    "D5_optional_command_length_gate": (0x100015C9, "66 39 6e 10"),
    "D5_optional_command_pointer": (0x100015CF, "8b 56 0c"),
    "D7_routine_high_byte": (0x100018B4, "8a 4d 09 88 48 08"),
    "D7_routine_low_byte": (0x100018BE, "8a 4d 08"),
    "D6_routine_high_byte": (0x10001C18, "8a 4d 09 88 48 08"),
    "D6_routine_low_byte": (0x10001C22, "8a 4d 08"),
    "status_key_load": (0x10001D37, "66 8b 56 0a"),
}
for name, (va, expected_hex) in ACTIVE_EXECUTOR_ANCHORS.items():
    check(
        f"SingleRoutine Active-Test byte anchor {name}",
        anchor(single_data, single_pe, va, expected_hex)
        and ev["frc_routine_active_test"]["executor"]["byte_anchors"][name][
            "bytes"
        ].replace(" ", "")
        == expected_hex.replace(" ", ""),
    )


# Imports prove what this plugin chain explicitly calls, while keeping the outer-session boundary.
def import_names(filename: str) -> set[str]:
    pe = pefile.PE(str(ROOT / "bin" / filename), fast_load=True)
    pe.parse_data_directories(
        directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]]
    )
    return {
        imp.name.decode()
        for entry in pe.DIRECTORY_ENTRY_IMPORT
        for imp in entry.imports
        if imp.name
    }


single_imports = import_names("SingleRoutineActTstP5_DT.dll")
init_imports = import_names("GetRoutineActTstInitP5_DT.dll")
signal_imports = import_names("GetRoutineActTstSignalInfoP5_DT.dll")
check(
    "routine executor imports exact frame/status primitives",
    "?GetRoutineCommand@CDbRoutineActTestP5ResRecords@@QAEPAEFPAG@Z" in single_imports
    and "?GetRoutineStatusPattern@CDbRoutineStatusResRecords@@QAEPAEFPAG@Z"
    in single_imports
    and "?CommFrameSendReceiveExt@CCommCachePlus@@QAEKPAVCCommFrameData@@G@Z"
    in single_imports
    and "?CheckSupportPanel@CCommCachePlusP5@@UAEKPAUtagCOMMAND_DATA@@GEPAH@Z"
    in init_imports
    and "?CheckSupportPanel@CCommCachePlusP5@@UAEKPAUtagCOMMAND_DATA@@GEPAH@Z"
    in signal_imports,
)
explicit_auth = {
    n
    for n in single_imports | init_imports | signal_imports
    if any(
        term in n
        for term in ("Security", "Authenticate", "Seed", "KeyAccess", "Session")
    )
}
check(
    "routine plugin chain has no explicit auth/session-named import and preserves boundary",
    not explicit_auth
    and ev["frc_routine_active_test"]["executor"]["explicit_auth_named_imports"] == []
    and "does NOT prove" in ev["frc_routine_active_test"]["executor"]["auth_boundary"],
)
check(
    "fixed vibration requests are 21 E2 + BE16 routine ID with no setpoint payload",
    ev["frc_routine_active_test"]["fixed_request_examples"]
    == {
        "LDA Steering Vibration": "21 E2 15 08",
        "LTA Steering Vibration": "21 E2 15 88",
        "LCA Steering Vibration": "21 E2 15 C8",
        "note": ev["frc_routine_active_test"]["fixed_request_examples"]["note"],
    }
    and "no controllable steering angle, torque, amplitude"
    in ev["frc_routine_active_test"]["conclusion"]
    and "not the missing arbitrary lateral writer"
    in ev["frc_routine_active_test"]["boundary"],
)


print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
