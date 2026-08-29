#!/usr/bin/env python3
"""Extract procedural TSE/GTSE semantics from CP-recovered current GTS+ managed bodies."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dnfile  # type: ignore
from dncil.cil.body import CilMethodBody  # type: ignore

from inspect_dotnet_il import MethodBodyReader, format_operand, resolve_token, type_name
from techstream_paths import resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/tse_managed_semantics.json"
COMPONENTS = (
    "GTSPlusTSEConverter/Converter.dll",
    "GTSPlusTSEConverter/RingBufferParser.dll",
    "GTSPlusTSEConverter/TseCompression.dll",
    "GTSPlusTSEConverter/TSEConverter.exe",
)
BINARY_READ = "Converter.BinaryRead"
RING_PARSER = "RingBufferParser.Parser"
COMPRESSION = "TSECompressionUtility.TSECompression"
TSE_CONVERTER = "TSEConverter.MainForm"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _open(path: Path) -> dnfile.dnPE:
    with contextlib.redirect_stderr(io.StringIO()):
        pe = dnfile.dnPE(str(path))
    if not (pe.net and pe.net.metadata and pe.net.mdtables):
        raise ValueError(f"not a parseable recovered CLR assembly: {path}")
    return pe


def _method_rows(pe: dnfile.dnPE, full_type: str, name: str) -> list[Any]:
    for td in pe.net.mdtables.TypeDef.rows:
        if type_name(td) == full_type:
            return [item.row for item in td.MethodList if str(item.row.Name) == name]
    raise ValueError(f"type not found: {full_type}")


def _body(pe: dnfile.dnPE, row: Any) -> CilMethodBody:
    return CilMethodBody(MethodBodyReader(pe, row))


def _instructions(pe: dnfile.dnPE, full_type: str, name: str, *, index: int = 0) -> tuple[Any, list[Any], CilMethodBody]:
    rows = _method_rows(pe, full_type, name)
    if index >= len(rows):
        raise ValueError(f"{full_type}::{name}: requested overload {index}, got {len(rows)}")
    body = _body(pe, rows[index])
    return rows[index], list(body.instructions), body


def _strings(pe: dnfile.dnPE, instructions: list[Any]) -> list[str]:
    return [str(resolve_token(pe, ins.operand)) for ins in instructions if str(ins.opcode) == "ldstr"]


def _lines(pe: dnfile.dnPE, instructions: list[Any]) -> list[str]:
    return [
        f"{str(ins.opcode)} {format_operand(pe, ins.operand)}".rstrip()
        for ins in instructions
    ]


def _contains_ordered(lines: list[str], needles: tuple[str, ...]) -> bool:
    pos = 0
    for needle in needles:
        while pos < len(lines) and needle not in lines[pos]:
            pos += 1
        if pos == len(lines):
            return False
        pos += 1
    return True


def _method_pin(row: Any, body: CilMethodBody) -> dict[str, Any]:
    return {
        "rva": int(row.Rva),
        "body_size": int(body.size),
        "body_sha256": hashlib.sha256(body.raw_bytes).hexdigest(),
    }


def _recovery_proof(path: Path) -> dict[str, Any]:
    pe = _open(path)
    rows = list(pe.net.mdtables.MethodDef.rows)
    raw = path.read_bytes()
    body_rvas = [int(row.Rva or 0) for row in rows if int(row.Rva or 0)]
    materialized = 0
    for rva in body_rvas:
        off = pe.get_offset_from_rva(rva)
        if off is not None and any(raw[off : off + 16]):
            materialized += 1
    if materialized != len(body_rvas):
        raise ValueError(f"incomplete recovered body set for {path}: {materialized}/{len(body_rvas)}")
    return {
        "method_def_count": len(rows),
        "method_body_rva_count": len(body_rvas),
        "method_body_materialized_count": materialized,
    }


def _binary_read_contract(path: Path) -> dict[str, Any]:
    pe = _open(path)

    ctor_row, ctor, ctor_body = _instructions(pe, BINARY_READ, ".ctor")
    ctor_strings = _strings(pe, ctor)
    if len(ctor_strings) != 70:
        raise ValueError(f"BinaryRead ctor string census drift: {len(ctor_strings)}")
    position_markers = []
    for i in range(0, len(ctor_strings), 2):
        key, marker = ctor_strings[i : i + 2]
        if len(marker) != 16 or any(c not in "0123456789ABCDEF" for c in marker):
            raise ValueError(f"unexpected BinaryRead marker: {key!r}={marker!r}")
        position_markers.append({"key": key, "marker_hex": marker})
    if len(position_markers) != 35:
        raise ValueError("BinaryRead position-marker census drift")
    marker_map = {row["key"]: row["marker_hex"] for row in position_markers}
    expected_markers = {
        "VehicleControlHistory共通位置情報": "FFFFFFFFFFFFFF23",
        "PCS時系列作動時FFD位置情報": "FFFFFFFFFFFFFF27",
        "PCS画像FFD位置情報": "FFFFFFFFFFFFFF28",
        "TMR位置情報": "FFFFFFFFFFFFFFFE",
        "エラーレポート位置情報": "FFFFFFFFFFFFFFFF",
    }
    if any(marker_map.get(k) != v for k, v in expected_markers.items()):
        raise ValueError("BinaryRead selected position-marker drift")

    bulk_row, bulk, bulk_body = _instructions(pe, BINARY_READ, "BulkReadToList")
    bulk_strings = _strings(pe, bulk)
    bulk_lines = _lines(pe, bulk)
    if "Shift_JIS" not in bulk_strings or not _contains_ordered(
        bulk_lines,
        ("GetTemplateData", "System.IO.File::OpenRead", "System.IO.BinaryReader::.ctor", "GetBinaryData", "GetResultBinaryData"),
    ):
        raise ValueError("BinaryRead BulkReadToList flow drift")

    template_row, template, template_body = _instructions(pe, BINARY_READ, "GetTemplateData")
    template_ints = [int(ins.operand) for ins in template if str(ins.opcode) == "ldc.i4.s" and isinstance(ins.operand, int)]
    if template_ints[:8] != list(range(15, 23)):
        raise ValueError(f"BinaryRead template-column mapping drift: {template_ints[:8]}")

    next_rows = _method_rows(pe, BINARY_READ, "GetNextReadPosition")
    next_candidates = []
    for row in next_rows:
        body = _body(pe, row)
        ins = list(body.instructions)
        ss = _strings(pe, ins)
        if "xx" in ss:
            next_candidates.append((row, ins, body, ss))
    if len(next_candidates) != 1:
        raise ValueError(f"expected one sentinel-scanning GetNextReadPosition, got {len(next_candidates)}")
    next_row, next_ins, next_body, next_strings = next_candidates[0]
    expected_next_strings = ["FF", "FF", "FF", "FF", "xx", "FF", "FF", "FF", "30", "33", "FE", "FF", "ECU", "", "{0}位置情報", "X2", "X2"]
    if next_strings != expected_next_strings:
        raise ValueError(f"GetNextReadPosition sentinel grammar drift: {next_strings!r}")
    next_lines = _lines(pe, next_ins)
    if not _contains_ordered(next_lines, ("ReadUInt32", "ReadUInt32", "'{0}位置情報'", "CompareBinDataPosition", "ReadByte", "'X2'")):
        raise ValueError("GetNextReadPosition traversal flow drift")

    binary_row, binary, binary_body = _instructions(pe, BINARY_READ, "GetBinaryData")
    binary_strings = _strings(pe, binary)
    binary_lines = _lines(pe, binary)
    for required in ("System(ECU)", "＊ECU最終位置", "＊System(ECU)最終位置", "System(ECU)数"):
        if required not in binary_strings:
            raise ValueError(f"GetBinaryData missing boundary string {required}")
    if not _contains_ordered(binary_lines, ("get_PositionF", "CheckSkipDataName", "GetNextReadPosition", "set_Position")):
        raise ValueError("GetBinaryData skip-position flow drift")
    if sum("ldc.i4.8" in line for line in binary_lines) < 2:
        raise ValueError("GetBinaryData 8-byte position-record rewind drift")

    fat_row, fat, fat_body = _instructions(pe, BINARY_READ, "GetFatData")
    if _strings(pe, fat) != ["ヘッダ情報", "初期車両情報"]:
        raise ValueError("GetFatData projection drift")
    fat_lines = _lines(pe, fat)
    if not _contains_ordered(fat_lines, ("ldc.i4.s 0xf", "SetListToDic", "'ヘッダ情報'", "'初期車両情報'", "ContainsKey", "Remove")):
        raise ValueError("GetFatData dictionary flow drift")

    list_row, list_ins, list_body = _instructions(pe, BINARY_READ, "SetListToDic")
    list_strings = _strings(pe, list_ins)
    list_lines = _lines(pe, list_ins)
    if list_strings.count("{0}_{1}") != 2 or list_strings.count("000") != 2 or "リングバッファデータ" not in list_strings:
        raise ValueError("SetListToDic naming/raw-value drift")
    if not _contains_ordered(list_lines, ("'リングバッファデータ'", "get_RawValue", "Add")):
        raise ValueError("SetListToDic ring-buffer raw-value flow drift")

    compare_row, compare, compare_body = _instructions(pe, BINARY_READ, "CompareBinDataPosition")
    compare_lines = _lines(pe, compare)
    if sum("System.String::ToUpper" in line for line in compare_lines) != 2 or not any("System.String::op_Equality" in line for line in compare_lines):
        raise ValueError("CompareBinDataPosition case-insensitive comparison drift")

    read_row, read, read_body = _instructions(pe, BINARY_READ, "ReadBinaryData")
    read_strings = _strings(pe, read)
    read_lines = _lines(pe, read)
    scalar_types = [
        "BYTE", "CHAR", "SHORT", "WORD", "INT", "UINT", "LONG", "ULONG", "DWORD",
        "DOUBLE", "BOOL", "SYSTEMTIME", "UNSIGNED CHAR", "CCMDSTRING", "WCHAR_T",
    ]
    if any(name not in read_strings for name in scalar_types):
        raise ValueError("ReadBinaryData scalar type coverage drift")
    if not _contains_ordered(read_lines, ("'リングバッファデータ'", "System.IO.BinaryReader::ReadBytes", "set_RawValue")):
        raise ValueError("ReadBinaryData ring-buffer raw-byte flow drift")

    encoding_row, encoding, encoding_body = _instructions(pe, BINARY_READ, "EncodingValue")
    encoding_lines = _lines(pe, encoding)
    if not _contains_ordered(encoding_lines, ("CodePageEncoding", "System.Text.Encoding::GetString", "NullTrim")):
        raise ValueError("EncodingValue string decode drift")

    exist_row, exist, exist_body = _instructions(pe, BINARY_READ, "ChkDataExistCase")
    exist_strings = _strings(pe, exist)
    expected_features = ["ヘルスチェック", "DualDataList", "DataList", "ActiveTest", "ActiveTest(DualDataList)", "DriveRecorder", "SystemCheck", "FuelConsumption", "AF/O2SensorOperation"]
    if any(name not in exist_strings for name in expected_features):
        raise ValueError("ChkDataExistCase feature compatibility set drift")

    pins = {
        "constructor": _method_pin(ctor_row, ctor_body),
        "bulk_read_to_list": _method_pin(bulk_row, bulk_body),
        "get_template_data": _method_pin(template_row, template_body),
        "get_binary_data": _method_pin(binary_row, binary_body),
        "get_next_read_position_scan": _method_pin(next_row, next_body),
        "get_fat_data": _method_pin(fat_row, fat_body),
        "set_list_to_dic": _method_pin(list_row, list_body),
        "compare_bin_data_position": _method_pin(compare_row, compare_body),
        "read_binary_data": _method_pin(read_row, read_body),
        "encoding_value": _method_pin(encoding_row, encoding_body),
        "check_data_exist_case": _method_pin(exist_row, exist_body),
    }

    return {
        "method_pins": pins,
        "position_markers": position_markers,
        "selected_position_markers": expected_markers,
        "template_runtime_contract": {
            "template_encoding": "Shift_JIS",
            "columns": {
                "15": "Type",
                "16": "Size",
                "17": "SizeF",
                "18": "IsList",
                "19": "LevelF",
                "20": "ExistF",
                "21": "PositionF",
                "22": "PositionSkipF",
            },
        },
        "position_traversal": {
            "position_marker_width_bytes": 8,
            "sentinel_shape": "FF FF FF FF <selector> FF FF FF",
            "generic_selector_acceptance": "0x01..0x33 or 0xFE",
            "ecu_skip_selector_acceptance": ["0x30", "0x33", "0xFE"],
            "position_dictionary_compare": "case-insensitive hex-string equality",
            "position_record_rewind_bytes": 8,
            "skip_contract": "PositionF==1 sections can be skipped by scanning to the next recognized position marker; terminal/skip cases rewind one 8-byte position record before outer traversal resumes.",
        },
        "fat_projection": {
            "dictionary_levels": 15,
            "removed_top_level_keys": ["ヘッダ情報", "初期車両情報"],
            "duplicate_list_key_format": "{name}_{index:03d}",
            "ring_buffer_data_uses_raw_value": True,
            "bool_uses_raw_value": True,
            "recursive_child_lists": True,
        },
        "binary_value_decode": {
            "scalar_types": scalar_types,
            "primitive_reader": "System.IO.BinaryReader",
            "string_decode": "CodePageEncoding.GetString followed by NullTrim",
            "ring_buffer_data": "ReadBytes(Size) retained in RawValue",
            "special_time_fields": ["時系列の時間情報", "時系列範囲開始(基本的にマイナスの数値)", "時系列範囲終了"],
        },
        "version_conditioned_fields": {
            "features": expected_features,
            "frame_id_upgrade": "通信フレームのID changes to WORD/2 bytes when バージョン_L5_1(ObjectVer) > 3",
            "help_id_upgrade": "へルプID changes to DWORD/4 bytes when バージョン_L5_1(ObjectVer) > 2",
        },
    }


def _legacy_upgrade_contract(path: Path) -> dict[str, Any]:
    """Recover the current converter's old-TSE -> latest-TSE handoff.

    The configured 180 template is not applied directly to arbitrary historical TSE
    layouts. TSEConverter first asks native GTSFileController to rewrite the source to
    a ``*_NEW.TSE`` file, then gives that upgraded file to managed BinaryRead.
    """
    pe = _open(path)

    convert_row, convert, convert_body = _instructions(pe, TSE_CONVERTER, "ConvTse_ToNewTseFile")
    convert_lines = _lines(pe, convert)
    if not _contains_ordered(convert_lines, ("GFCConvertOldTSEToLatestTSE", "stloc.0", "ldloc.0", "ret")):
        raise ValueError("TSEConverter old-TSE native upgrade call drift")
    convert_strings = _strings(pe, convert)
    for required in ("* TSE/VerUP Read: Failure.", "* TSE/VerUP Write: Failure."):
        if required not in convert_strings:
            raise ValueError(f"TSEConverter legacy-upgrade status text drift: {required}")

    main_row, main, main_body = _instructions(pe, TSE_CONVERTER, "TseConvert")
    main_strings = _strings(pe, main)
    for required in ("TEMPLATE", "_NewTSE", "{0}_NEW.TSE", "> Update TSE file to the latest"):
        if required not in main_strings:
            raise ValueError(f"TSEConverter upgrade pipeline string drift: {required}")
    main_lines = _lines(pe, main)
    if not _contains_ordered(
        main_lines,
        (
            "ConvTse_ToNewTseFile",
            "System.IO.File::OpenRead",
            "Converter.BinaryRead::.ctor",
            "Converter.BinaryRead::set_FilePath_TemplateFile",
            "Converter.BinaryRead::set_FilePath_BinaryFile",
            "Converter.BinaryRead::set_BinaryDataSkipNames",
            "Converter.BinaryRead::BulkReadToList",
        ),
    ):
        raise ValueError("TSEConverter upgraded-TSE -> managed BinaryRead flow drift")

    return {
        "method_pins": {
            "tse_convert": _method_pin(main_row, main_body),
            "convert_old_tse_to_latest": _method_pin(convert_row, convert_body),
        },
        "native_upgrade_api": "GFCConvertOldTSEToLatestTSE",
        "intermediate_directory": "_NewTSE",
        "intermediate_filename": "{source_stem}_NEW.TSE",
        "pipeline": "source TSE -> native GFCConvertOldTSEToLatestTSE -> upgraded _NEW.TSE -> BinaryRead with configured template",
        "boundary": (
            "Historical TSE files are normalized by native GTSFileController before the current managed template reader. "
            "A legacy specimen can validate format lineage and the native-upgrade input boundary without being assumed "
            "byte-layout-identical to 180_Template.csv."
        ),
    }


def _ring_contract(path: Path) -> dict[str, Any]:
    pe = _open(path)
    parse_row, parse, parse_body = _instructions(pe, RING_PARSER, "ParseRingBuffer")
    parse_lines = _lines(pe, parse)
    if not _contains_ordered(parse_lines, ("ldc.i4.8", "stfld timestampLength", "get_Values", "System.Linq.Enumerable::Sum", "ldc.i4.2", "mul", "ldfld timestampLength", "add")):
        raise ValueError("RingBufferParser record-width flow drift")

    numeric_row, numeric, numeric_body = _instructions(pe, RING_PARSER, "ConvertNumericValue")
    numeric_lines = _lines(pe, numeric)
    for parser in ("System.SByte::Parse", "System.Int16::Parse", "System.Int32::Parse", "System.Int64::Parse"):
        if not any(parser in line for line in numeric_lines):
            raise ValueError(f"RingBufferParser signed parser drift: {parser}")
    if not _contains_ordered(numeric_lines, ("System.UInt64::Parse", "get_bitMask", "and", "get_bitMask", "BitShift_Right")):
        raise ValueError("RingBufferParser unsigned mask/shift drift")
    if not _contains_ordered(numeric_lines, ("ldfld mul", "mul", "ldfld div", "div", "ldfld offset", "add", "ldc.r8 10.0", "ldfld decPntCnt", "System.Math::Pow", "div")):
        raise ValueError("RingBufferParser scaling flow drift")

    return {
        "method_pins": {
            "parse_ring_buffer": _method_pin(parse_row, parse_body),
            "convert_numeric_value": _method_pin(numeric_row, numeric_body),
        },
        "record_width": "8-byte timestamp + 2 * sum(frame lengths)",
        "signed_decode": ["SByte", "Int16", "Int32", "Int64"],
        "unsigned_decode": "UInt64 parse, bit-mask, then right shift",
        "engineering_value": "((raw * MUL) / DIV + OFFSET) / 10^decimal_places",
    }


def _compression_contract(path: Path) -> dict[str, Any]:
    pe = _open(path)
    salt = bytes.fromhex("e7b77797f2e62ce74b5dc58f8d15c82c574d8a4a")
    if path.read_bytes().count(salt) != 1:
        raise ValueError("TseCompression exact salt materialization drift")

    list_row, list_ins, list_body = _instructions(pe, COMPRESSION, "getListFileInfo")
    list_lines = _lines(pe, list_ins)
    if not _contains_ordered(list_lines, ("readFile_Byte", "saltBuf", "add", "saltBuf", "stelem.i1", "SHA256CryptoServiceProvider::.ctor", "HashAlgorithm::ComputeHash", "'{0:X2}'")):
        raise ValueError("TseCompression salted-hash flow drift")

    write_row, write, write_body = _instructions(pe, COMPRESSION, "writeListTextFile")
    if not _contains_ordered(_lines(pe, write), ("'shift_jis'", "Encoding::GetEncoding", "'Target Folder'", "TextWriter::WriteLine")):
        raise ValueError("TseCompression list.txt flow drift")

    zip_row, zip_ins, zip_body = _instructions(pe, COMPRESSION, "compressionDir")
    if not _contains_ordered(_lines(pe, zip_ins), ("'.zip'", "'shift_jis'", "Encoding::GetEncoding", "ZipFile::CreateFromDirectory")):
        raise ValueError("TseCompression ZIP flow drift")

    move_row, move, move_body = _instructions(pe, COMPRESSION, "changeExtZipToGTSE")
    if not any("System.IO.File::Move" in line for line in _lines(pe, move)):
        raise ValueError("TseCompression GTSE rename drift")

    return {
        "method_pins": {
            "get_list_file_info": _method_pin(list_row, list_body),
            "write_list_text_file": _method_pin(write_row, write_body),
            "compression_dir": _method_pin(zip_row, zip_body),
            "change_ext_zip_to_gtse": _method_pin(move_row, move_body),
        },
        "salt_hex": salt.hex(),
        "per_file_digest": "SHA-256(file_bytes || 20-byte salt), rendered uppercase hex",
        "manifest": "list.txt encoded Shift-JIS with Target Folder header",
        "archive": "ZipFile.CreateFromDirectory with Shift-JIS entry encoding, then File.Move .zip to .GTSE",
    }


def extract(recovered_root: Path, *, gtsplus_root: Path | None = None) -> dict[str, Any]:
    recovered_root = recovered_root.expanduser().resolve()
    gts = resolve_gts_root(gtsplus_root)
    diagnostics = gts.parent

    sources: dict[str, Any] = {}
    proofs: dict[str, Any] = {}
    paths: dict[str, Path] = {}
    for rel in COMPONENTS:
        protected = diagnostics / rel
        sidecar = Path(str(protected) + "._")
        recovered = recovered_root / rel
        if not recovered.is_file():
            raise FileNotFoundError(f"missing recovered component: {recovered}")
        paths[rel] = recovered
        proof = _recovery_proof(recovered)
        proofs[rel] = proof
        sources[rel] = {
            "protected_stub": {"size": protected.stat().st_size, "sha256": sha256_file(protected)},
            "protected_sidecar": {"size": sidecar.stat().st_size, "sha256": sha256_file(sidecar)},
            "recovered_analysis_pe": {"size": recovered.stat().st_size, "sha256": sha256_file(recovered)},
        }

    return {
        "schema": "gtsplus-tse-managed-semantics-v2",
        "title": "GTS+ recovered TSE/GTSE managed procedural semantics",
        "sources": sources,
        "recovery_proof": proofs,
        "binary_read": _binary_read_contract(paths["GTSPlusTSEConverter/Converter.dll"]),
        "legacy_upgrade": _legacy_upgrade_contract(paths["GTSPlusTSEConverter/TSEConverter.exe"]),
        "ring_buffer_parser": _ring_contract(paths["GTSPlusTSEConverter/RingBufferParser.dll"]),
        "gtse_compression": _compression_contract(paths["GTSPlusTSEConverter/TseCompression.dll"]),
        "validation_boundary": "Procedural host semantics are recovered. Public legacy Toyota-generated TSE specimens validate the shared header/FAT/position-marker lineage, while a true-TSS3 TSE is still required to exercise current PCS Operation/Image FFD population and the complete latest-layout traversal end-to-end.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--recovered-root", type=Path, required=True)
    ap.add_argument("--gtsplus-root", type=Path)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    artifact = extract(args.recovered_root, gtsplus_root=args.gtsplus_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: markers={len(artifact['binary_read']['position_markers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
