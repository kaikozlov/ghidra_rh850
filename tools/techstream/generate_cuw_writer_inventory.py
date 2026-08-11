#!/usr/bin/env python3
"""Generate the pinned Techstream V18 CUW writer/factory inventory.

The parameter INIs are an encoded CSV.  The decoder below is derived from
TCUWParameterForVC.dll RVA 0x10001000; route selection is then tied to
TCUWControlCommPhase.dll's LoadLibrary/GetProcAddress paths.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import struct
from pathlib import Path
from typing import Any

import pefile

REPO = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics"
DEFAULT_OUT = REPO / "data/generated/techstream_v18/cuw_writer_inventory.json"

ARTIFACTS = [
    "Calibration Update Wizard/Cuw.exe",
    "Calibration Update Wizard/TCUWControlCommPhase.dll",
    "Calibration Update Wizard/TCUWParameterForVC.dll",
    "Calibration Update Wizard/TCUWCalibrationFile.dll",
    "Calibration Update Wizard/TCUWCanCommonPrepareWriter.dll",
    "Calibration Update Wizard/TCUWCanCommonFlashWriter.dll",
    "Calibration Update Wizard/TCUWCanReproStdPrepareWriter.dll",
    "Calibration Update Wizard/TCUWCanReproStdFlashWriter.dll",
    "Calibration Update Wizard/TCUWCanUnifiedPrepareWriter.dll",
    "Calibration Update Wizard/TCUWCanUnifiedFlashWriter.dll",
    "Calibration Update Wizard/TCUWCanUnifiedFlashWriterEachArea.dll",
    "Calibration Update Wizard/TCUWCanSecurityVFORESTFlashWriter.dll",
    "Calibration Update Wizard/TCUWP4CanVFORESTFlashWriter.dll",
    "Calibration Update Wizard/TCUWP5CanSecurityPowerTrainPrepareWriter.dll",
]

# Sizes are function extents recovered from the pinned PE analysis.  Hashing
# those extents makes drift visible without treating the hash as semantic proof.
METHODS: dict[str, list[tuple[str, int, int, str]]] = {
    "TCUWControlCommPhase.dll": [
        ("controller_execute", 0xA8B0, 582, "state dispatcher"),
        ("load_StartGetCID", 0x1B80, 140, "LoadLibrary + GetProcAddress"),
        ("load_StartPrepareWrite", 0x1C30, 140, "LoadLibrary + GetProcAddress"),
        ("load_StartFlashWrite", 0x1D90, 270, "LoadLibrary + GetProcAddress"),
        ("prepare_factory", 0x6BC0, 2001, "parameter-keyed prepare DLL selection"),
        ("flash_factory", 0x9C90, 2417, "parameter-keyed flash DLL selection"),
    ],
    "TCUWCanCommonPrepareWriter.dll": [
        ("CalcSeedKey_key_and_seed", 0x10D0, 231, "calibration-key transform"),
        ("CalcSeedKey_seed", 0x11C0, 328, "seed transform"),
        ("CalcSeedKeyForSecurityUp", 0x1310, 234, "security-up transform"),
        ("ChangeMode", 0x1520, 271, "diagnostic mode request"),
    ],
    "TCUWCanReproStdPrepareWriter.dll": [
        ("StartPrepareWrite", 0x2A70, 152, "exported constructor/runner"),
        ("prepare_sequence", 0x2290, 1561, "standard prepare orchestration"),
        ("programming_session", 0x1400, 265, "UDS 10 02"),
        ("security_access", 0x1510, 721, "UDS 27 01/02 + service-auth key"),
    ],
    "TCUWCanUnifiedPrepareWriter.dll": [
        ("StartPrepareWrite", 0x22D0, 152, "exported constructor/runner"),
        ("prepare_sequence", 0x1D10, 1175, "unified prepare orchestration"),
        ("read_software_id", 0x1220, 404, "delegated software-ID read"),
        ("programming_session", 0x1420, 259, "UDS 10 02"),
        ("security_access", 0x1530, 741, "UDS 27 01/02 + ECU/service auth keys"),
    ],
    "TCUWCanReproStdFlashWriter.dll": [
        ("flash_sequence", 0x2A50, 2598, "standard flash orchestration"),
        ("predownload_wdbi", 0x1200, 1001, "calibration-selected UDS 2E writes"),
        ("request_download", 0x15F0, 624, "UDS 34/74"),
        ("transfer_data", 0x1870, 308, "UDS 36/76"),
        ("transfer_exit", 0x19B0, 224, "UDS 37/77"),
        ("ecu_reset", 0x1A90, 239, "UDS 11 01/51 01"),
        ("routine_control", 0x25F0, 1112, "UDS 31 01 routines"),
    ],
    "TCUWCanUnifiedFlashWriter.dll": [
        ("flash_sequence", 0x2510, 1312, "unified flash orchestration"),
        ("predownload_wdbi", 0x10F0, 816, "UDS 2E 0203/0201/0202"),
        ("request_download", 0x1420, 944, "UDS 34/74"),
        ("transfer_data", 0x17E0, 324, "UDS 36/76"),
        ("transfer_exit", 0x1930, 240, "UDS 37/77"),
        ("ecu_reset", 0x1A20, 239, "UDS 11 01/51 01"),
        ("download_area", 0x1D50, 768, "download/transfer/exit loop"),
        ("routine_control", 0x2080, 1151, "UDS 31 01 F010/F110/F210/00FF"),
    ],
}

COMMANDS = [
    {"route": "standard-prepare", "method": "programming_session", "rva": 0x1400,
     "request": "10 02", "positive_response": "50 02", "confidence": "recovered"},
    {"route": "standard-prepare", "method": "security_access", "rva": 0x1510,
     "request": "27 01; then 27 02 || CalcSeedKey(GetServiceAuthKey(node), seed[16])",
     "positive_response": "67 01 || seed[16]; then 67 02", "confidence": "recovered"},
    {"route": "unified-prepare", "method": "security_access", "rva": 0x1530,
     "request": "27 01 || GetECUAuthKey(node)[16]; then 27 02 || CalcSeedKey(GetServiceAuthKey(node), seed[16])",
     "positive_response": "67 01 || seed[16]; then 67 02", "confidence": "recovered"},
    {"route": "unified-flash", "method": "predownload_wdbi", "rva": 0x10F0,
     "request": "2E 02 03 || GetOffsetAddress(node)[5]; 2E 02 01 || GetSeedKey(node)[16]; 2E 02 02 || GetNonce(node)[16]",
     "positive_response": "6E 02 03; 6E 02 01; 6E 02 02", "confidence": "recovered"},
    {"route": "standard-flash", "method": "request_download", "rva": 0x15F0,
     "request": "34 || dataFormat || 44 || address[4] || size[4]", "positive_response": "74 || maxBlockLength",
     "response_rule": "usable payload=min(decoded maxBlockLength,0x0FFF)-2", "confidence": "recovered"},
    {"route": "unified-flash", "method": "request_download", "rva": 0x1420,
     "request": "34 || compressionFlag || areaFlag || 46 || (offset[5]+areaAddress) || areaSize",
     "positive_response": "74 || maxBlockLength", "response_rule": "usable payload=min(decoded maxBlockLength,0x0FFF)-2", "confidence": "recovered"},
    {"route": "both-flash", "method": "transfer_data", "request": "36 || blockSequenceCounter || data",
     "positive_response": "76 || blockSequenceCounter", "confidence": "recovered"},
    {"route": "both-flash", "method": "transfer_exit", "request": "37", "positive_response": "77", "confidence": "recovered"},
    {"route": "standard-flash", "method": "routine_control", "rva": 0x25F0,
     "request": "31 01 F5 10 / 31 01 00 FF / 31 01 F6 10 plus calibration-derived range/hash fields",
     "positive_response": "71 01 || routineIdentifier", "confidence": "recovered"},
    {"route": "unified-flash", "method": "routine_control", "rva": 0x2080,
     "request": "31 01 F0 10 / 31 01 00 FF / 31 01 F1 10 / 31 01 F2 10 plus offset-adjusted area/range",
     "positive_response": "71 01 || routineIdentifier", "confidence": "recovered"},
    {"route": "both-flash", "method": "ecu_reset", "request": "11 01", "positive_response": "51 01",
     "timeout_ms": 180, "confidence": "recovered"},
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_parameter_ini(data: bytes) -> bytes:
    if len(data) % 2:
        raise ValueError("encoded CUW parameter file has odd length")
    decoded = bytes(
        (((((a & 0xF) >> 2) + (a >> 4) * 4) * 4 + (b >> 4) + 0x1E) * 4 + ((b & 0xF) >> 2)) & 0xFF
        for a, b in zip(data[::2], data[1::2])
    )
    return decoded.rstrip(b"\xff")


def pe_inventory(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    pe = pefile.PE(data=data)
    exports = []
    for symbol in getattr(pe, "DIRECTORY_ENTRY_EXPORT", ()).symbols if hasattr(pe, "DIRECTORY_ENTRY_EXPORT") else ():
        exports.append({"name": symbol.name.decode("latin1") if symbol.name else None, "rva": symbol.address})
    imports = []
    iat: dict[int, str] = {}
    for library in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
        dll = library.dll.decode("latin1")
        for symbol in library.imports:
            name = symbol.name.decode("latin1") if symbol.name else f"ordinal:{symbol.ordinal}"
            imports.append({"dll": dll, "name": name, "iat_va": symbol.address})
            iat[symbol.address] = f"{dll}!{name}"
    strings = [m.group().decode("latin1") for m in re.finditer(rb"[ -~]{6,}", data)]
    classes = sorted({
        match.group(0)
        for value in strings
        for match in re.finditer(r"C[A-Za-z0-9_]*(?:PrepareWriter|FlashWriter)", value)
    })
    methods = []
    for name, rva, size, role in METHODS.get(path.name, []):
        start = pe.get_offset_from_rva(rva)
        body = data[start:start + size]
        direct = []
        imported = []
        for offset in range(max(0, len(body) - 4)):
            if body[offset] == 0xE8:
                rel = struct.unpack_from("<i", body, offset + 1)[0]
                direct.append(rva + offset + 5 + rel)
            if body[offset:offset + 2] in (b"\xff\x15", b"\xff\x25"):
                target = struct.unpack_from("<I", body, offset + 2)[0]
                if target in iat:
                    imported.append(iat[target])
        methods.append({
            "name": name, "rva": rva, "size": size, "role": role,
            "identity_sha256": digest(body),
            "direct_call_rvas": sorted(set(direct)),
            "import_call_edges": sorted(set(imported)),
        })
    return {
        "path": path.relative_to(path.parents[1]).as_posix(),
        "size": len(data), "sha256": digest(data), "image_base": pe.OPTIONAL_HEADER.ImageBase,
        "exports": sorted(exports, key=lambda item: (item["rva"], item["name"] or "")),
        "imports": sorted(imports, key=lambda item: (item["dll"].lower(), item["name"])),
        "writer_classes": classes, "methods": methods,
    }


def factory_routes(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ini_root = root / "Calibration Update Wizard/Ini"
    routes: list[dict[str, Any]] = []
    decoded_files = 0
    for path in sorted(ini_root.glob("*.ini"), key=lambda p: p.name.lower()):
        encoded = path.read_bytes()
        try:
            decoded = decode_parameter_ini(encoded)
            rows = list(csv.reader(io.StringIO(decoded.decode("latin1"))))
        except (ValueError, UnicodeError, csv.Error):
            continue
        decoded_files += 1
        if len(rows) < 2 or "DLLFileNameForPrepareWrite" not in rows[0]:
            continue
        header = rows[0]
        for row_index, row in enumerate(rows[1:], 1):
            row += [""] * (len(header) - len(row))
            item = dict(zip(header, row))
            routes.append({
                "parameter_file": path.name,
                "encoded_sha256": digest(encoded),
                "decoded_sha256": digest(decoded),
                "row_index": row_index,
                "factory_identifier": item.get("ParamFileKeySystemProtocolMicon", ""),
                "cid_getter": item.get("DLLFileNameForGetCID", ""),
                "prepare_writer": item.get("DLLFileNameForPrepareWrite", ""),
                "flash_writer": item.get("DLLFileNameForFlashWrite", ""),
                "get_can_id_prepare": item.get("GetCANIDFunctionNameForPrepareWrite", ""),
                "get_can_id_flash": item.get("GetCANIDFunctionNameForFlashWrite", ""),
                "version_contract": item.get("EnableDLLVersionInformation", ""),
            })
    routes.sort(key=lambda item: (item["factory_identifier"], item["parameter_file"], item["row_index"]))
    return routes, {"encoded_ini_files_decoded": decoded_files, "factory_rows": len(routes)}


def generate(root: Path) -> dict[str, Any]:
    artifacts = [pe_inventory(root / relative) for relative in ARTIFACTS]
    routes, route_stats = factory_routes(root)
    calibration_payloads = sorted(
        path.relative_to(root).as_posix() for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".cuw", ".cal"}
    )
    getters = sorted({
        symbol["name"]
        for artifact in artifacts for symbol in artifact["imports"]
        if "@CalibrationFile@@" in symbol["name"]
    })
    return {
        "schema_version": 1,
        "source": "external-source",
        "distribution": "Toyota Techstream V18.00.003",
        "selection_model": {
            "controller": "TCUWControlCommPhase.dll",
            "parameter_decoder": "TCUWParameterForVC.dll RVA 0x10001000",
            "resolved_edge": "decoded parameter row -> DLLFileNameForPrepareWrite/DLLFileNameForFlashWrite -> LoadLibraryA -> GetProcAddress entry point",
            "unresolved_edge": "CalibrationFile::GetContactType/GetCPUType/GetKindOfECU -> exact parameter factory_identifier for Sienna 8965B4512000",
        },
        "route_stats": route_stats,
        "factory_routes": routes,
        "artifacts": artifacts,
        "calibration_file_getters": getters,
        "commands": COMMANDS,
        "firmware_join": {
            "calibration_scope": "Sienna 8965B4512000",
            "supported_standard_uds_sids": [0x10, 0x11, 0x22, 0x27, 0x28, 0x2E, 0x31, 0x34, 0x36, 0x37, 0x3E, 0x85],
            "bootloader_dids": [0xF181, 0x0201, 0x0202, 0x0203],
            "bounded_join": "standard and unified builders use implemented SIDs; unified predownload names the same 0201/0202/0203 DIDs, but calibration selection and accepted payload semantics remain unproven",
        },
        "blockers": {
            "matching_calibration_payload_required": True,
            "searched_extensions": [".cuw", ".cal"],
            "matching_payloads_found": calibration_payloads,
            "consequence": "local V18 cannot prove the Sienna writer factory identifier, per-calibration keys/nonces, address ranges, or exact routine choices",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = generate(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
