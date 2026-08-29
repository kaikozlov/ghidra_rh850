#!/usr/bin/env python3
"""Recover the current GTS+ PCS Vehicle Data Analysis (.vdas) persistence contract.

The installed assemblies are CP-protected.  The current installer contains exact
same-release plaintext twins, so the default build path recovers those installer
bodies into a temporary directory and extracts managed-IL semantics from them.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from extract_gtsplus_tse_managed_semantics import (
    _contains_ordered,
    _instructions,
    _lines,
    _method_pin,
    _open,
    _strings,
    sha256_file,
)
from recover_gtsplus_bodies import recover

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/vdas_semantics.json"
DIAG = "GTSPlusDiagAdaptationManager.DiagAdaptationManager"
ARCHIVER = "GTSPlusArchiver.ZipFile"

LOG_BINDINGS = (
    ("Airbag_Hinban.log", "Airbag.Hinban"),
    ("Airbag_Software.log", "Airbag.Software"),
    ("Adu_Hinban.log", "Adu.Hinban"),
    ("Adu_Software.log", "Adu.Software"),
    ("CSP_MakerId.log", "Csp.MakerId"),
    ("CSP_Hinban.log", "Csp.Hinban"),
    ("CSP_SerialNo.log", "Csp.Serial"),
    ("PCS_MakerId.log", "Pcs.MakerId"),
    ("PCS_Hinban.log", "Pcs.Hinban"),
    ("PCS_SerialNo.log", "Pcs.Serial"),
    ("FCM_MakerId.log", "Fcm.MakerId"),
    ("FCM_Hinban.log", "Fcm.Hinban"),
    ("FCM_SerialNo.log", "Fcm.Serial"),
    ("TripCount.log", "CarInfo.TripCount"),
    ("OdoMeter.log", "CarInfo.OdoMeter"),
    ("OdoUnit.log", "CarInfo.OdoUnit"),
    ("DDR.log", "Ddr.Data"),
    ("ADUDDR.log", "AduDdr.Data"),
    ("OperationFFD.log", "PcsFfd.Data"),
    ("LCSOperationFFD.log", "LcsFfd.Data"),
    ("TSS3OperationFFD.log", "Tss3Ffd.Data"),
    ("ADSOperationFFD.log", "AdsFfd.Data"),
    ("ADSOperationFFD_Eng.log", "AdsEng.Data"),
    ("ADUOperationFFD.log", "AduFfd.Data"),
    ("ImageFFD.log", "PcsImg.Data"),
    ("PVMImageFFD.log", "PvmImg.Data"),
    ("ADSImageFFD.log", "AdsImg.Data"),
    ("RCImageFFD.log", "RcImg.Data"),
    ("DMCImageFFD.log", "DmcImg.Data"),
    ("AbsoluteTimeStamp.log", "AbsoluteTime.Data"),
)

# Setter following each ReadLogFile call.  This proves each filename is assigned
# into the intended JSON model rather than merely appearing as a string literal.
LOG_SETTERS = {
    "Airbag_Hinban.log": "set_Hinban",
    "Airbag_Software.log": "set_Software",
    "Adu_Hinban.log": "set_Hinban",
    "Adu_Software.log": "set_Software",
    "CSP_MakerId.log": "set_MakerId",
    "CSP_Hinban.log": "set_Hinban",
    "CSP_SerialNo.log": "set_Serial",
    "PCS_MakerId.log": "set_MakerId",
    "PCS_Hinban.log": "set_Hinban",
    "PCS_SerialNo.log": "set_Serial",
    "FCM_MakerId.log": "set_MakerId",
    "FCM_Hinban.log": "set_Hinban",
    "FCM_SerialNo.log": "set_Serial",
    "TripCount.log": "set_TripCount",
    "OdoMeter.log": "set_OdoMeter",
    "OdoUnit.log": "set_OdoUnit",
    "DDR.log": "set_Data",
    "ADUDDR.log": "set_Data",
    "OperationFFD.log": "set_Data",
    "LCSOperationFFD.log": "set_Data",
    "TSS3OperationFFD.log": "set_Data",
    "ADSOperationFFD.log": "set_Data",
    "ADSOperationFFD_Eng.log": "set_Data",
    "ADUOperationFFD.log": "set_Data",
    "ImageFFD.log": "set_Data",
    "PVMImageFFD.log": "set_Data",
    "ADSImageFFD.log": "set_Data",
    "RCImageFFD.log": "set_Data",
    "DMCImageFFD.log": "set_Data",
    "AbsoluteTimeStamp.log": "set_Data",
}


def _source(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256_file(path)}


def _verify_log_bindings(pe: Any, instructions: list[Any]) -> list[dict[str, str]]:
    lines = _lines(pe, instructions)
    strings = _strings(pe, instructions)
    expected_files = [name for name, _ in LOG_BINDINGS]
    present = [value for value in strings if value in set(expected_files)]
    if present != expected_files:
        raise ValueError(f"VDAS log-file order drift: {present}")

    out = []
    search_from = 0
    for filename, target in LOG_BINDINGS:
        setter = LOG_SETTERS[filename]
        # Bound the proof locally: filename -> ReadLogFile -> intended setter,
        # before searching for the next filename.
        start = next(
            (idx for idx in range(search_from, len(lines)) if repr(filename) in lines[idx]),
            None,
        )
        if start is None:
            raise ValueError(f"VDAS log binding missing filename: {filename}")
        read = next((idx for idx in range(start + 1, min(start + 6, len(lines))) if "ReadLogFile" in lines[idx]), None)
        set_idx = next((idx for idx in range((read or start) + 1, min((read or start) + 6, len(lines))) if setter in lines[idx]), None)
        if read is None or set_idx is None:
            raise ValueError(f"VDAS log binding flow drift: {filename} -> {target}")
        out.append({"file": filename, "json_model_target": target})
        search_from = set_idx + 1
    return out


def _diag_contract(path: Path) -> dict[str, Any]:
    pe = _open(path)

    create_row, create, create_body = _instructions(pe, DIAG, "CreateVdasFile")
    create_lines = _lines(pe, create)
    create_strings = _strings(pe, create)
    for required in ("{0}_{1}.vdas", "yyyyMMddHHmmss", "json.log", "\\\\n", "\\n"):
        if required not in create_strings:
            raise ValueError(f"VDAS creation string drift: {required!r}")
    if not _contains_ordered(
        create_lines,
        (
            "MakeImgOpeDdrJsonData",
            "Newtonsoft.Json.JsonConvert::SerializeObject",
            "System.IO.StreamWriter::.ctor",
            "System.IO.TextWriter::Write",
            "GTSPlusArchiver.ZipFile::CompressFileToFile",
        ),
    ):
        raise ValueError("VDAS creation flow drift")
    # The call site immediately supplies literal 6 as the wrapper compression
    # argument.  ZipFile's conversion maps all values except 0/1 to enum 0.
    compress_call = next(i for i, line in enumerate(create_lines) if "GTSPlusArchiver.ZipFile::CompressFileToFile" in line)
    if "ldc.i4.6" not in create_lines[compress_call - 1]:
        raise ValueError("VDAS compression argument drift")

    json_row, json_ins, json_body = _instructions(pe, DIAG, "MakeImgOpeDdrJsonData")
    json_strings = _strings(pe, json_ins)
    if "001" not in json_strings:
        raise ValueError("VDAS JSON format version drift")
    bindings = _verify_log_bindings(pe, json_ins)

    read_row, read_ins, read_body = _instructions(pe, DIAG, "ReadLogFile")
    read_lines = _lines(pe, read_ins)
    if not _contains_ordered(read_lines, ("System.Text.UTF8Encoding::.ctor", "System.IO.StreamReader::.ctor", "System.IO.TextReader::ReadToEnd")):
        raise ValueError("VDAS source-log UTF-8/full-read flow drift")

    convert_row, convert, convert_body = _instructions(pe, DIAG, "ConvertVdastoCsvFile")
    convert_lines = _lines(pe, convert)
    convert_strings = _strings(pe, convert)
    for required in (".csv", "json.log"):
        if required not in convert_strings:
            raise ValueError(f"VDAS CSV conversion string drift: {required!r}")
    if not _contains_ordered(
        convert_lines,
        (
            "GTSPlusArchiver.ZipFile::DecompressFileToFile",
            "System.Text.UTF8Encoding::.ctor",
            "System.IO.StreamReader::.ctor",
            "System.IO.TextReader::ReadToEnd",
            "MakeImgOpeDdrCsvData",
            "System.IO.StreamWriter::.ctor",
            "System.IO.TextWriter::Write",
        ),
    ):
        raise ValueError("VDAS -> CSV flow drift")

    csv_row, csv_ins, csv_body = _instructions(pe, DIAG, "MakeImgOpeDdrCsvData")
    csv_lines = _lines(pe, csv_ins)
    if not _contains_ordered(csv_lines, ("System.String::Replace", "System.String::Replace", "CalculateImgOpeDdrHash")):
        raise ValueError("VDAS CSV presentation/hash flow drift")

    hash_rows = [row for row in pe.net.mdtables.ImplMap.rows if str(row.ImportName) == "CalculateImgOpeDdrHash"]
    if len(hash_rows) != 1 or str(hash_rows[0].ImportScope.row.Name) != "GTSPlusFileCryptographic.dll":
        raise ValueError("VDAS native hash import drift")

    return {
        "method_pins": {
            "create_vdas": _method_pin(create_row, create_body),
            "make_json": _method_pin(json_row, json_body),
            "read_log": _method_pin(read_row, read_body),
            "convert_vdas_to_csv": _method_pin(convert_row, convert_body),
            "make_csv": _method_pin(csv_row, csv_body),
        },
        "file_naming": {
            "pattern": "{sanitized_vin}_{yyyyMMddHHmmss}.vdas",
            "vin_sanitizer_regex": "[^A-Za-z0-9-]+",
            "replacement": "_",
        },
        "json_entry": {
            "archive_entry": "json.log",
            "text_encoding": "UTF-8 without BOM",
            "format_version": "001",
            "source_log_encoding": "UTF-8",
            "source_log_read": "entire file text",
            "bindings": bindings,
        },
        "csv_export": {
            "output_extension": ".csv",
            "container_entry": "json.log",
            "flow": "decompress VDAS -> read UTF-8 json.log -> MakeImgOpeDdrCsvData -> append native hash text -> write UTF-8 CSV",
            "hash_import": "GTSPlusFileCryptographic.dll!CalculateImgOpeDdrHash",
        },
    }


def _archiver_contract(path: Path) -> dict[str, Any]:
    pe = _open(path)
    comp_row, comp, comp_body = _instructions(pe, ARCHIVER, "CompressFileToFile")
    comp_lines = _lines(pe, comp)
    if not _contains_ordered(
        comp_lines,
        (
            "CompressionLevelConversion",
            "System.IO.FileStream::.ctor",
            "System.IO.Compression.ZipArchive::.ctor",
            "System.IO.Path::GetFileName",
            "System.IO.Compression.ZipFileExtensions::CreateEntryFromFile",
        ),
    ):
        raise ValueError("VDAS ZipFile compression flow drift")

    decomp_row, decomp, decomp_body = _instructions(pe, ARCHIVER, "DecompressFileToFile")
    decomp_lines = _lines(pe, decomp)
    if not _contains_ordered(
        decomp_lines,
        (
            "System.IO.Compression.ZipFile::OpenRead",
            "System.IO.Compression.ZipArchive::get_Entries",
            "System.IO.Compression.ZipFileExtensions::ExtractToFile",
        ),
    ):
        raise ValueError("VDAS ZipFile decompression flow drift")

    level_row, level, level_body = _instructions(pe, ARCHIVER, "CompressionLevelConversion")
    # IL: arg0==0 -> 2, arg0==1 -> 1, otherwise -> 0. CreateVdas supplies 6,
    # therefore the System.IO.Compression.CompressionLevel enum is 0 (Optimal).
    level_lines = _lines(pe, level)
    for token in ("ldc.i4.2", "ldc.i4.1", "ldc.i4.0"):
        if not any(token in line for line in level_lines):
            raise ValueError("VDAS compression-level mapping drift")

    return {
        "method_pins": {
            "compress_file_to_file": _method_pin(comp_row, comp_body),
            "decompress_file_to_file": _method_pin(decomp_row, decomp_body),
            "compression_level_conversion": _method_pin(level_row, level_body),
        },
        "container": "standard ZIP archive",
        "entry_name_rule": "Path.GetFileName(source_file)",
        "create_mode": "ZipArchiveMode.Create",
        "vdas_call_argument": 6,
        "vdas_effective_compression_level": "System.IO.Compression.CompressionLevel.Optimal (enum 0)",
        "read_mode": "ZipFile.OpenRead; enumerate entries; ExtractToFile(overwrite=true)",
    }


def _build_from_recovered(root: Path, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    diag = root / "bin/GTSPlusDiagAdaptMng.dll"
    archiver = root / "bin/GTSPlusArchiver.dll"
    if not diag.is_file() or not archiver.is_file():
        raise SystemExit(f"recovered root lacks required GTS+ VDAS assemblies: {root}")

    sources: dict[str, Any] = {
        "GTSPlusDiagAdaptMng.dll": _source(diag),
        "GTSPlusArchiver.dll": _source(archiver),
    }
    if manifest is not None:
        sources["installer_recovery"] = {
            "gtsplus_version": manifest["gtsplus_version"],
            "method": manifest["method"],
            "source_archive_sha256": manifest["source_archive_sha256"],
        }
        by_path = {row["path"]: row for row in manifest["binaries"]}
        for filename in ("bin/GTSPlusDiagAdaptMng.dll", "bin/GTSPlusArchiver.dll"):
            if filename not in by_path:
                raise ValueError(f"installer recovery manifest lacks {filename}")
            if by_path[filename]["plaintext"]["sha256"] != sources[Path(filename).name]["sha256"]:
                raise ValueError(f"installer manifest/source identity drift for {filename}")

    diag_contract = _diag_contract(diag)
    archiver_contract = _archiver_contract(archiver)
    tss = next(row for row in diag_contract["json_entry"]["bindings"] if row["file"] == "TSS3OperationFFD.log")
    image = next(row for row in diag_contract["json_entry"]["bindings"] if row["file"] == "ImageFFD.log")

    return {
        "schema": "gtsplus-vdas-semantics-v1",
        "title": "Current GTS+ PCS Vehicle Data Analysis (.vdas) persistence/export contract",
        "sources": sources,
        "create_and_export": diag_contract,
        "archive": archiver_contract,
        "tss3_pcs_witnesses": {
            "operation_ffd": tss,
            "image_ffd": image,
            "interpretation": (
                "VDAS is a second first-class current GTS+ persistence/export path for PCS recorder evidence. "
                "The JSON model explicitly carries TSS3OperationFFD.log as Tss3Ffd.Data and ImageFFD.log as "
                "PcsImg.Data before packaging json.log into a ZIP-backed .vdas file."
            ),
        },
        "capture_implication": (
            "A real .vdas file can be inspected with an ordinary ZIP reader and its UTF-8 json.log retained directly. "
            "For TSS3 RE this may be simpler than GTSE because the current VDAS creation path explicitly includes "
            "TSS3OperationFFD.log and ImageFFD.log rather than applying TSEConverter's PCS skip list."
        ),
        "boundary": (
            "This proves the host persistence/export format and exact source-log bindings. It does not prove that a "
            "given vehicle/session populated those logs, nor does it identify ECU-side CAN/SecOC producer ownership."
        ),
    }


def build(recovered_root: Path | None = None) -> dict[str, Any]:
    if recovered_root is not None:
        return _build_from_recovered(recovered_root.resolve())
    with tempfile.TemporaryDirectory(prefix="gtsplus-vdas-recovery-") as tmp:
        root = Path(tmp) / "plain"
        manifest = recover(output=root)
        return _build_from_recovered(root, manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recovered-root", type=Path, help="optional exact plaintext GTSPlus root; default recovers installer twins")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    payload = build(args.recovered_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
