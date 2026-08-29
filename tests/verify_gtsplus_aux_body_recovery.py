#!/usr/bin/env python3
"""Verify the generic CP decoder on the non-GTSPlus/non-CUWPlus host trees."""
from __future__ import annotations

import contextlib
import io
import json
import struct
import sys
import tempfile
from pathlib import Path

import dnfile
from dncil.cil.body import CilMethodBody

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_pcs_data_viewer_tss3_managed_semantics import extract as extract_pcs_semantics
from inspect_dotnet_il import MethodBodyReader, format_operand, type_name
from recover_cp_bodies import recover
from techstream_paths import resolve_gts_root


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def is_managed(path: Path) -> bool:
    data = path.read_bytes()
    peoff = struct.unpack_from("<I", data, 0x3C)[0]
    opt = peoff + 24
    return bool(struct.unpack_from("<I", data, opt + 96 + 14 * 8)[0])


def method_lines(path: Path, qualified_type: str, method_name: str) -> list[str]:
    with contextlib.redirect_stderr(io.StringIO()):
        pe = dnfile.dnPE(str(path))
    matches = []
    for row in pe.net.mdtables.TypeDef.rows:
        if type_name(row) != qualified_type:
            continue
        matches.extend(index.row for index in row.MethodList if str(index.row.Name) == method_name)
    if len(matches) != 1:
        raise AssertionError(f"{path.name}: expected one {qualified_type}::{method_name}, got {len(matches)}")
    body = CilMethodBody(MethodBodyReader(pe, matches[0]))
    return [
        f"{str(ins.opcode)} {format_operand(pe, ins.operand)}".rstrip()
        for ins in body.instructions
    ]


def contains_ordered(lines: list[str], needles: tuple[str, ...]) -> bool:
    cursor = 0
    for needle in needles:
        while cursor < len(lines) and needle not in lines[cursor]:
            cursor += 1
        if cursor == len(lines):
            return False
        cursor += 1
    return True


def main() -> int:
    diagnostics = resolve_gts_root().parent
    sidecars = sorted([
        *diagnostics.rglob("*.dll._"),
        *diagnostics.rglob("*.exe._"),
    ])
    auxiliary = [
        sidecar for sidecar in sidecars
        if sidecar.relative_to(diagnostics).parts[0] not in {"GTSPlus", "CUWPlus"}
    ]
    stubs = [Path(str(sidecar)[:-2]) for sidecar in auxiliary]
    managed = [stub for stub in stubs if is_managed(stub)]
    check("full Toyota Diagnostics CP census is 249", len(sidecars) == 249)
    check("auxiliary protected-body census is 52", len(stubs) == 52)
    check("auxiliary native/CLR split is 18/34", len(stubs) - len(managed) == 18 and len(managed) == 34)

    selected = [
        "DS-4/bin/GetActTstLstP4SA_DT.dll",
        "GTSPlusCSVConverter/Constants.dll",
        "PCS Data Viewer/PCS Data Viewer.exe",
        "GTSPlusTSEConverter/TSEConverter.exe",
        "GTSPlusTSEConverter/Converter.dll",
        "GTSPlusTSEConverter/RingBufferParser.dll",
        "GTSPlusTSEConverter/TseCompression.dll",
    ]
    with tempfile.TemporaryDirectory(prefix="verify-gtsplus-aux-body-recovery-") as tmp:
        output = Path(tmp) / "recovered"
        manifest = recover(
            source=diagnostics,
            output=output,
            only=selected,
            workers=7,
        )
        check("native/managed/coree-EXE/TSE semantic representatives recovered", manifest["recovered_body_count"] == 7)
        by_path = {entry["relative_path"]: entry for entry in manifest["entries"]}
        native = by_path[selected[0]]
        clr = by_path[selected[1]]
        check(
            "DS-4 native body reaches clean PE handoff",
            native["classification"] == "native"
            and native["protector_success"]
            and native["entrypoint_rva"] != 0
            and native["section_count"] >= 5,
        )
        check(
            "CSV converter CLR body retains parseable metadata",
            clr["managed_input"]
            and clr["protector_success"]
            and clr.get("assembly_name") == "Constants",
        )

        pcs = by_path[selected[2]]
        check(
            "PCS coree-managed EXE reaches true CLR handoff with every method body",
            pcs["classification"] == "managed"
            and pcs["protector_success"]
            and pcs.get("assembly_name") == "PCS Data Viewer"
            and pcs["entrypoint_rva"] == 0x66FB8E
            and pcs["method_def_count"] == 22564
            and pcs["method_body_rva_count"] == 22447
            and pcs["method_body_materialized_count"] == 22447
            and len(pcs["synthetic_api_integrity_trusts"]) == 1
            and pcs["synthetic_api_integrity_trusts"][0]["api"] == "kernel32.dll!GetProcAddress",
        )

        tracked_pcs_semantics = json.loads(
            (REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json").read_text()
        )
        rebuilt_pcs_semantics = extract_pcs_semantics(output / selected[2])
        check(
            "PCS managed TSS3 semantics artifact regenerates from fresh CP recovery",
            rebuilt_pcs_semantics == tracked_pcs_semantics,
        )

        tse = by_path[selected[3]]
        check(
            "TSEConverter coree-managed EXE has executable IL after recovery",
            tse["classification"] == "managed"
            and tse["protector_success"]
            and tse.get("assembly_name") == "TSEConverter"
            and tse["entrypoint_rva"] == 0x6BAE
            and tse["method_def_count"] == 30
            and tse["method_body_rva_count"] == 27
            and tse["method_body_materialized_count"] == 27
            and len(tse["synthetic_api_integrity_trusts"]) == 1
            and tse["synthetic_api_integrity_trusts"][0]["api"] == "kernel32.dll!GetProcAddress",
        )

        converter = by_path[selected[4]]
        ring = by_path[selected[5]]
        compression = by_path[selected[6]]
        for label, entry in (("Converter", converter), ("RingBufferParser", ring), ("TseCompression", compression)):
            check(
                f"{label} managed body is fully materialized",
                entry["managed_input"]
                and entry["method_body_rva_count"] > 0
                and entry["method_body_materialized_count"] == entry["method_body_rva_count"],
            )

        converter_path = output / selected[4]
        read_binary = method_lines(converter_path, "Converter.BinaryRead", "ReadBinaryData")
        read_binary_text = "\n".join(read_binary)
        for type_name_token in (
            "'BYTE'", "'CHAR'", "'SHORT'", "'WORD'", "'INT'", "'UINT'",
            "'LONG'", "'ULONG'", "'DWORD'", "'DOUBLE'", "'BOOL'",
            "'SYSTEMTIME'", "'UNSIGNED CHAR'",
        ):
            check(f"Converter BinaryRead handles {type_name_token}", type_name_token in read_binary_text)

        ring_path = output / selected[5]
        parse_ring = method_lines(ring_path, "RingBufferParser.Parser", "ParseRingBuffer")
        check(
            "RingBufferParser record width is timestamp8 + 2*sum(frame lengths)",
            contains_ordered(
                parse_ring,
                (
                    "ldc.i4.8", "stfld timestampLength", "get_Values",
                    "System.Linq.Enumerable::Sum", "ldc.i4.2", "mul",
                    "ldfld timestampLength", "add",
                ),
            ),
        )
        numeric = method_lines(ring_path, "RingBufferParser.Parser", "ConvertNumericValue")
        numeric_text = "\n".join(numeric)
        for parser in ("System.SByte::Parse", "System.Int16::Parse", "System.Int32::Parse", "System.Int64::Parse"):
            check(f"RingBufferParser signed numeric path uses {parser}", parser in numeric_text)
        check(
            "RingBufferParser unsigned path masks then shifts",
            contains_ordered(numeric, ("System.UInt64::Parse", "get_bitMask", "and", "get_bitMask", "BitShift_Right")),
        )
        check(
            "RingBufferParser applies MUL/DIV/OFFSET and decimal-point scaling",
            contains_ordered(
                numeric,
                (
                    "ldfld mul", "mul", "ldfld div", "div", "ldfld offset", "add",
                    "ldc.r8 10.0", "ldfld decPntCnt", "System.Math::Pow", "div",
                ),
            ),
        )

        compression_path = output / selected[6]
        salt = bytes.fromhex("e7b77797f2e62ce74b5dc58f8d15c82c574d8a4a")
        check("TseCompression exact 20-byte salt is materialized once", compression_path.read_bytes().count(salt) == 1)
        list_info = method_lines(compression_path, "TSECompressionUtility.TSECompression", "getListFileInfo")
        check(
            "TseCompression appends salt then SHA-256 hashes each file",
            contains_ordered(
                list_info,
                ("readFile_Byte", "ldsfld saltBuf", "add", "ldsfld saltBuf", "stelem.i1",
                 "SHA256CryptoServiceProvider::.ctor", "HashAlgorithm::ComputeHash", "'{0:X2}'"),
            ),
        )
        write_list = method_lines(compression_path, "TSECompressionUtility.TSECompression", "writeListTextFile")
        check(
            "TseCompression list.txt is Shift-JIS with Target Folder header",
            contains_ordered(write_list, ("'shift_jis'", "Encoding::GetEncoding", "'Target Folder'", "TextWriter::WriteLine")),
        )
        compress_dir = method_lines(compression_path, "TSECompressionUtility.TSECompression", "compressionDir")
        check(
            "TseCompression ZIP creation preserves Shift-JIS entry encoding",
            contains_ordered(compress_dir, ("'.zip'", "'shift_jis'", "Encoding::GetEncoding", "ZipFile::CreateFromDirectory")),
        )
        rename = method_lines(compression_path, "TSECompressionUtility.TSECompression", "changeExtZipToGTSE")
        check("TseCompression finalizes GTSE via File.Move", any("System.IO.File::Move" in line for line in rename))

    print("GTS+ auxiliary body recovery verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
