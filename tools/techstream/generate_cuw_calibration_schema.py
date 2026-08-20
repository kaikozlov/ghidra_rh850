#!/usr/bin/env python3
"""Generate the byte-pinned V18 CUW calibration metadata/object schema.

This describes the metadata parser and TCUWCalibrationFile in-memory model.
It deliberately does not invent the outer .cuw archive framing: the installed
V18 tree contains no calibration specimen against which such an extractor can
be validated.  `parse_cuw_attach.py` consumes the recovered `attach.att`
descriptor once extracted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import collections
import sys
from pathlib import Path
from typing import Any

import pefile

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from tools.techstream.generate_cuw_writer_inventory import factory_routes  # noqa: E402
from tools.techstream.generate_cuw_writer_protocol_grammar import route_verdict  # noqa: E402
ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard"
OUT = REPO / "data/generated/techstream_v18/cuw_calibration_schema.json"

FUNCTIONS = {
    "Cuw.exe": [
        (0x00403480, 448, "attached_information_object_init"),
        (0x00404708, 25389, "attached_information_parser"),
        (0x0040B63C, 3045, "logical_block_parser"),
        (0x0040C224, 838, "target_integrity_parser"),
    ],
    "TCUWCanReproStdFlashWriter.dll": [
        (0x100025F0, 1112, "standard_target_integrity_routine_control"),
        (0x10002A50, 2598, "standard_flash_orchestration"),
    ],
    "TCUWCanUnifiedFlashWriterEachArea.dll": [
        (0x10001420, 855, "unified_each_area_request_download"),
        (0x10001F80, 832, "unified_each_area_routine_control"),
    ],
    "TCUWCalibrationFile.dll": [
        (0x100015F0, 60, "logical_block_area_default_ctor"),
        (0x10001630, 158, "logical_block_area_dtor"),
        (0x100016D0, 20, "target_data_default_ctor"),
        (0x100018C0, 582, "logical_block_default_ctor"),
        (0x10001FF0, 51, "target_data_copy_ctor"),
        (0x100021F0, 214, "logical_block_area_copy_ctor"),
        (0x10002520, 34, "target_data_assign"),
        (0x10002810, 92, "logical_block_area_assign"),
        (0x100032E0, 53, "import_calib_archived_file"),
        (0x10003BC0, 174, "import_file_header_info"),
        (0x10003C70, 163, "import_logical_block_area_info"),
        (0x10003D20, 1526, "import_logical_block"),
        (0x10004320, 2880, "import_calibration_file"),
    ],
}

EXPECTED_HASHES = {
    ("Cuw.exe", 0x00403480): "8693436e2efd94928b402c111df5ab049e18dab7fca04e1f92bcf3a4462319d3",
    ("Cuw.exe", 0x00404708): "249e7ac1c90725f27e8e92bd9a787fc2c01fda3753c8e8383acaeec2f2a255ad",
    ("Cuw.exe", 0x0040B63C): "ce3e4d43fa5539105c776684bb73b24fc9516a94768b99d044d960d8b520807d",
    ("Cuw.exe", 0x0040C224): "62cf1764aaa6f06169e7b0b4953cf24593490b7337d6a8a63854b190779dec8d",
    ("TCUWCanReproStdFlashWriter.dll", 0x100025F0): "6aa2bd0d44347d588386f57ce6fda737f44504460d032644f10ad75261692652",
    ("TCUWCanReproStdFlashWriter.dll", 0x10002A50): "3f0955be8af3615fe82696445623041cb7ed5196860a6a820d495b20414df017",
    ("TCUWCanUnifiedFlashWriterEachArea.dll", 0x10001420): "c14089dd3cb7777838a9b2ebf6c24b88eaf86c5cdd5567952f68a2436483efec",
    ("TCUWCanUnifiedFlashWriterEachArea.dll", 0x10001F80): "61fb7c16743a2313a4a082a284cfe241e2102998fb3f68d02d8072e502d8a1d9",
    ("TCUWCalibrationFile.dll", 0x100015F0): "bd46b15bcdfbc0d86c469f323dfae90fa70cc0f1a338dc94addad87841350771",
    ("TCUWCalibrationFile.dll", 0x10001630): "02f3a95fab81edff83c4bbd0ae44509bda64d78c49c1d2bb9d76fafb40689e3a",
    ("TCUWCalibrationFile.dll", 0x100016D0): "6f172a820cd37c8dcdb9473f45ec706ef02bc6aa08f27831545c0c353ee6d009",
    ("TCUWCalibrationFile.dll", 0x100018C0): "f02459d873fb345e708d6e2150f23ad3e08d28b0c56f4d9a54aa5f0af0d09b85",
    ("TCUWCalibrationFile.dll", 0x10001FF0): "7e01c0b658802fa5c51bc2a72266b88a0ec86a41f338538542bf1fdb39fa7e0b",
    ("TCUWCalibrationFile.dll", 0x100021F0): "bc71d320bed2c30c1e7725a8fcef130982d5daee377160b5f13343f591756257",
    ("TCUWCalibrationFile.dll", 0x10002520): "4250f1b01bd4f1b6d0caba4164c853a433567b4ed9fd2943218864617fd5bbe6",
    ("TCUWCalibrationFile.dll", 0x10002810): "3a2cede5b45dfda8a0a62589a69488131ceb8c2daec9d0cf1a539e52b2d24ca1",
    ("TCUWCalibrationFile.dll", 0x100032E0): "97175eecffbbb1431f60660f3f9297e8686a7cdc0e5cb21e965b45a57610417e",
    ("TCUWCalibrationFile.dll", 0x10003BC0): "800567b49cc5318b1d450a1dd580a091b7f28d22ed6422095cd72afd997878d3",
    ("TCUWCalibrationFile.dll", 0x10003C70): "54736e7ab774c35e15206c2a9201db75c77d480020f9a62e5037dd57a8918874",
    ("TCUWCalibrationFile.dll", 0x10003D20): "e1631b79f6f6c1aef405314bc73689ba9c772445085c2c60bf86e233cf51aec1",
    ("TCUWCalibrationFile.dll", 0x10004320): "6fdb177b88013a4bb9c7265f14ced1523622991b31358a2b00e632dd97346043",
}

TARGET_FIELDS = [
    {"name": "StartAddress", "source_offset": 0x00, "object_offset": 0x00, "size": 0x1C, "kind": "msvc_string"},
    {"name": "Length", "source_offset": 0x04, "object_offset": 0x1C, "size": 0x1C, "kind": "msvc_string"},
    {"name": "CRC", "source_offset": 0x08, "object_offset": 0x38, "size": 0x1C, "kind": "msvc_string"},
    {"name": "CMAC", "source_offset": 0x0C, "object_offset": 0x54, "size": 0x1C, "kind": "msvc_string"},
    {"name": "DigitalSignature", "source_offset": 0x10, "object_offset": 0x70, "size": 0x1C, "kind": "msvc_string"},
]

TARGET_FAMILIES = [
    {"name": "ReproData", "logical_block_object_offset": 0x008, "source_offset": 0x08, "call_va": 0x0040BFEA},
    {"name": "EraseAndReproRoutine", "logical_block_object_offset": 0x094, "source_offset": 0x1C, "call_va": 0x0040C03E},
    {"name": "DeltaReproData", "logical_block_object_offset": 0x120, "source_offset": 0x30, "call_va": 0x0040C092},
    {"name": "DeltaEraseAndReproRoutine", "logical_block_object_offset": 0x1AC, "source_offset": 0x44, "call_va": 0x0040C0E6},
    {"name": "CompressionReproData", "logical_block_object_offset": 0x238, "source_offset": 0x58, "call_va": 0x0040C13A},
    {"name": "CompressionEraseAndReproRoutine", "logical_block_object_offset": 0x2C4, "source_offset": 0x6C, "call_va": 0x0040C18E},
]

ATTACH_KEYS = [
    "Format", "Version", "NumberOfNode", "NumberOfCalibration", "Number", "DateOfIssue",
    "VehicleType", "VehicleName", "ECUType", "ContactType", "KindOfECU", "ModelYear",
    "ECUAuthKey", "ServiceAuthKey", "RequiredSpecReproVer", "WakeUpTimeAfterReset",
    "IntervalTimeBetweenFrame", "DiagID", "LogicalAddress", "NumberOfGateway",
    "EmissionsRelatedSystem", "ChargeLocalBusEcuReprogrammingFlow",
    "ChargeLocalBusPowerOnControllingEcuDiagID", "ChargeLocalBusEcuStartTimeAfterPowerOn",
    "NumberOfLogicalBlock", "CPUImageName", "NewCID", "CompressionAlgorithm",
    "SecurityProperty2", "SeedKey", "Nonce", "ReproMethod", "OffsetAddress",
    "P4ServerMaxTime", "NumberOfTargets", "NumberOfAreaSettings", "FlashCodeName",
    "LocationID", "CPUType", "NumberOfTargetHardwares", "DataFormatID", "NumberOfFiles",
    "FileName", "DataFormat", "EraseBlock", "ALFID", "DownloadAddress", "DownloadMemsize",
    "System", "EngineType", "KindOfCal", "IsControlledBySCC", "IsBlankECU", "IsNonFieldFix",
    "StartAddress", "Length", "CRC", "CMAC", "DigitalSignature", "VehicleForNA", "VehicleForEUOT",
]


def body_hash(path: Path, va: int, size: int) -> str:
    pe = pefile.PE(str(path)); base = pe.OPTIONAL_HEADER.ImageBase
    return hashlib.sha256(pe.get_data(va - base, size)).hexdigest()


def generate(root: Path) -> dict[str, Any]:
    funcs = []
    for filename, rows in FUNCTIONS.items():
        path = root / filename
        for va, size, role in rows:
            digest = body_hash(path, va, size)
            funcs.append({"artifact": filename, "va": va, "size": size, "role": role,
                          "sha256": digest, "expected_sha256": EXPECTED_HASHES[(filename, va)]})

    routes, _ = factory_routes(root.parent)
    pairs = collections.Counter((row["prepare_writer"], row["flash_writer"]) for row in routes)
    route_relevance = []
    for (prepare, flash), count in sorted(pairs.items()):
        verdict, reason = route_verdict(prepare, flash)
        if prepare == "TCUWCanReproStdPrepareWriter.dll" and flash == "TCUWCanReproStdFlashWriter.dll":
            integrity_path = "standard-CLogicalBlockAreaInfo"
            field_flow = {
                "StartAddress": "copied into 31 01 routine request",
                "Length": "copied into 31 01 routine request",
                "CRC": "conditionally copied with CRC selector/length",
                "CMAC": "conditionally copied for RequiredSpecReproVer03",
                "DigitalSignature": "conditionally copied on alternate required-spec path",
            }
        elif prepare == "TCUWCanUnifiedPrepareWriter.dll" and flash in {"TCUWCanUnifiedFlashWriter.dll", "TCUWCanUnifiedFlashWriterEachArea.dll"}:
            integrity_path = "unified-CFileHeaderInfo-area"
            field_flow = {
                "StartAddress": "area start used with OffsetAddress in RequestDownload/RoutineControl",
                "Length": "area length used in RequestDownload/RoutineControl",
                "CRC": "not consumed through the standard CLogicalBlockAreaInfo routine builder",
                "CMAC": "not consumed through the standard CLogicalBlockAreaInfo routine builder",
                "DigitalSignature": "not consumed through the standard CLogicalBlockAreaInfo routine builder",
            }
        else:
            integrity_path = "target-incompatible-route"
            field_flow = {
                key: "route rejected by an earlier exact boot-grammar mismatch; no Sienna/H target-integrity semantic is promoted"
                for key in ("StartAddress", "Length", "CRC", "CMAC", "DigitalSignature")
            }
        route_relevance.append({
            "prepare_writer": prepare,
            "flash_writer": flash,
            "factory_rows": count,
            "target_verdict": verdict,
            "target_reason": reason,
            "integrity_path": integrity_path,
            "field_flow": field_flow,
        })

    return {
        "schema_version": 2,
        "distribution": "Toyota Techstream V18.00.003",
        "descriptor": {
            "embedded_name": "attach.att",
            "grammar": "Windows-profile/INI-like key-value descriptor",
            "evidence": [
                "Cuw.exe initializer 0x00403480 stores literal attach.att",
                "Cuw.exe imports GetPrivateProfileIntA/GetPrivateProfileStringA",
                "Cuw.exe 0x00404708 reads recovered section/key vocabulary through the descriptor object",
            ],
            "key_vocabulary": ATTACH_KEYS,
            "section_templates": [
                "Vehicle", "CPUImage00", "LogicalBlocknxx", "xx_TargetCalibration",
                "ReproDatanxx", "EraseAndReproRoutinenxx", "DeltaReproDatanxx",
                "DeltaEraseAndReproRoutinenxx", "CompressionReproDatanxx",
                "CompressionEraseAndReproRoutinenxx", "00_TargetHardware", "File0000",
            ],
        },
        "objects": {
            "CLogicalBlockAreaInfo": {"size": 0x8C, "fields": TARGET_FIELDS},
            "TargetData": {
                "size": 0x20,
                "fields": [
                    {"offset": 0x00, "size": 0x1C, "kind": "msvc_string"},
                    {"offset": 0x1C, "size": 4, "kind": "scalar"},
                ],
            },
            "CLogicalBlockInfo": {
                "size": 0x39C,
                "target_array_pointer_offset": 0x00,
                "target_count_offset": 0x04,
                "area_records": TARGET_FAMILIES,
                "tail": [
                    {"offset": 0x350, "kind": "scalar"}, {"offset": 0x354, "kind": "msvc_string", "size": 0x1C},
                    {"offset": 0x370, "kind": "scalar"}, {"offset": 0x374, "kind": "msvc_string", "size": 0x1C},
                    {"offset": 0x390, "kind": "scalar"}, {"offset": 0x394, "kind": "pointer"}, {"offset": 0x398, "kind": "scalar"},
                ],
                "source_record_size": 0x98,
            },
            "CalibArchivedFile": {
                "known_output_offsets": [0x00, 0x1C, 0x20, 0x24, 0x58, 0x5C, 0x60],
                "known_source_offsets": [0x00, 0x04, 0x08, 0x0C, 0x1C, 0x20, 0x24],
                "boundary": "field roles are only promoted where an exported getter or copy operation names them",
            },
        },
        "target_integrity": {
            "record_size": 0x14,
            "fields": [{"name": f["name"], "source_offset": f["source_offset"]} for f in TARGET_FIELDS],
            "families": TARGET_FAMILIES,
            "standard_writer_consumer": {
                "function_va": 0x100025F0,
                "request": "31 01 || routine_id || 44 || StartAddress || Length || integrity_selector || integrity_value",
                "routine_ids": {"0": "10F5", "1": "FF00", "2": "10F6"},
                "field_offsets": {"StartAddress": 0x00, "Length": 0x1C, "CRC": 0x38, "CMAC": 0x54, "DigitalSignature": 0x70},
                "integrity_selection": {
                    "crc": "if CRC is nonempty, an explicit length/selector 4 precedes the CRC bytes",
                    "required_spec_repro_ver_03": "prefix 00 10 then CMAC bytes; request length becomes transport_prefix+0x24",
                    "other_required_spec": "prefix 01 00 then DigitalSignature bytes; request length becomes transport_prefix+0x114",
                },
                "positive_response": "71 01 || routine_id",
                "target_family_callers": {
                    "whole": ["ReproData", "EraseAndReproRoutine"],
                    "delta": ["DeltaReproData", "DeltaEraseAndReproRoutine"],
                    "compression": ["CompressionReproData", "CompressionEraseAndReproRoutine"],
                },
                "evidence": "exact target-object offsets from TCUWCalibrationFile plus direct field loads/copies in the byte-pinned standard RoutineControl builder and orchestration",
            },
            "unified_writer_boundary": "both recovered Unified flash variants use CFileHeaderInfo-shape area start/length plus OffsetAddress in RIDs 10F0/10F1/10F2/FF00; they do not consume CLogicalBlockAreaInfo CRC/CMAC/DigitalSignature through the standard target-record builder",
            "route_relevance": route_relevance,
            "boundary": "all 32 V18 route pairs are classified for Sienna/H target relevance. Standard transmits the signature-bearing target record but is target-incompatible; both compatible Unified routes use the separate area start/length path. Signer/private-key provenance and actual package values remain artifact/server questions.",
        },
        "top_level_import": {
            "function_va": 0x10004320,
            "source_geometry": {
                "node_array_pointer": 0x08, "node_count": 0x0C, "node_source_stride": 0x60, "node_output_stride": 0xBC,
                "calibration_array_pointer": 0x18, "calibration_count": 0x1C, "calibration_source_stride": 0xB8,
                "calibration_output_stride": 0xAE9C,
                "binary_material_source_start": 0x38, "binary_material_source_stride": 0x10, "binary_material_count": 8,
            },
            "boundary": "geometry is exact from ImportData; semantic labels for every anonymous slot require the parser call-site join",
        },
        "function_identities": funcs,
        "outer_container_boundary": {
            "status": "artifact-blocked-for-parser-validation",
            "reason": "the V18 installation contains no .cuw/.cal specimen; static code proves an embedded attach.att metadata descriptor but a byte-accurate outer-package extractor cannot be fixture-validated locally",
            "ready_path": "tools/techstream/parse_cuw_attach.py parses the recovered descriptor once extracted; preserve the first acquired raw package before attempting extraction",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--root", type=Path, default=ROOT); ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args(); result = generate(args.root.resolve()); args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__": raise SystemExit(main())
