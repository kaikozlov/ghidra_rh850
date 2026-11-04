#!/usr/bin/env python3
"""Verify the generic CP decoder on the non-GTSPlus/non-CUWPlus host trees."""
from __future__ import annotations

import contextlib
import io
import hashlib
import json
import struct
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import dnfile
from dncil.cil.body import CilMethodBody

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream.extract_pcs_data_viewer_tss3_managed_semantics import extract as extract_pcs_semantics
from tools.techstream.inspect_dotnet_il import MethodBodyReader, format_operand, type_name
import tools.techstream.recover_cp_bodies as recovery
from tools.techstream.recover_cp_bodies import recover
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT, qualify_recovered_source
from tools.techstream.techstream_paths import resolve_gts_root


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



def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def verify_collision_schedules(diagnostics: Path, stubs: list[Path]) -> None:
    groups: dict[str, list[str]] = {}
    for stub in stubs:
        groups.setdefault(stub.name.replace(".", "_"), []).append(stub.relative_to(diagnostics).as_posix())
    collisions = {name: paths for name, paths in groups.items() if len(paths) > 1}
    check(
        "all four duplicate decoder-stem groups are qualified",
        set(collisions) == {
            "GTSPlusCommon_dll", "GTSPlusErrorReportData_dll", "GtsPlus-CM_dll", "MsgDatComm_dll",
        } and all(len(paths) == 2 for paths in collisions.values()),
    )
    selected = sorted(path for paths in collisions.values() for path in paths)
    with tempfile.TemporaryDirectory(prefix="verify-gtsplus-collisions-") as tmp:
        root = Path(tmp)
        isolated = {}
        for index, rel in enumerate(selected):
            manifest = recover(
                source=diagnostics, output=root / f"isolated-{index}", only=[rel], workers=1,
            )
            check(f"isolated recovery selects exactly {rel}", manifest["recovered_body_count"] == 1)
            isolated[rel] = manifest["entries"][0]
        for name, paths in collisions.items():
            check(
                f"{name} inputs are two distinct protected pairs",
                len({isolated[rel]["stub_sha256"] for rel in paths}) == 2
                and len({isolated[rel]["sidecar_sha256"] for rel in paths}) == 2,
            )
        for workers in (1, 8):
            manifest = recover(
                source=diagnostics, output=root / f"workers-{workers}", only=selected, workers=workers,
            )
            check(f"workers={workers} recovers all eight collision inputs", manifest["recovered_body_count"] == 8)
            artifact_paths: dict[str, set[str]] = {name: set() for name in ("metadata", "final_memory", "log")}
            for entry in manifest["entries"]:
                rel = entry["relative_path"]
                oracle = isolated[rel]
                provenance = entry["decoder_provenance"]
                check(
                    f"workers={workers} {rel} retains its exact original pair",
                    provenance["source_root"] == str(diagnostics)
                    and provenance["relative_path"] == rel
                    and provenance["stub_sha256"] == entry["stub_sha256"] == sha256(diagnostics / rel)
                    and provenance["sidecar_sha256"] == entry["sidecar_sha256"] == sha256(diagnostics / f"{rel}._"),
                )
                check(
                    f"workers={workers} {rel} consumes its own isolated decode and normalized output",
                    entry["output_sha256"] == oracle["output_sha256"]
                    == sha256(root / f"workers-{workers}" / rel)
                    and all(
                        provenance["artifacts"][name]["sha256"]
                        == oracle["decoder_provenance"]["artifacts"][name]["sha256"]
                        for name in ("metadata", "final_memory")
                    ),
                )
                for name in artifact_paths:
                    artifact_paths[name].add(provenance["artifacts"][name]["path"])
            check(
                f"workers={workers} has eight independent memory/metadata/log artifacts",
                all(len(paths) == 8 for paths in artifact_paths.values()),
            )


def verify_validation_transaction(diagnostics: Path, output: Path, managed_rel: str) -> None:
    before = {path.relative_to(output): sha256(path) for path in output.rglob("*") if path.is_file()}
    original_build = recovery._managed_build

    def invalid_il_build(stub: Path, meta: Path, memory: Path, destination: Path) -> dict:
        info = original_build(stub, meta, memory, destination)
        with contextlib.redirect_stderr(io.StringIO()):
            pe = dnfile.dnPE(str(destination))
        row = next(row for row in pe.net.mdtables.MethodDef.rows if row.Rva and row.ImplFlags.miIL)
        offset = pe.get_offset_from_rva(row.Rva)
        data = bytearray(destination.read_bytes())
        # A nonzero fat header whose declared code cannot fit in this file.
        struct.pack_into("<HHII", data, offset, 0x3003, 8, len(data) + 1, 0)
        check("invalid IL fixture retains a nonzero 16-byte prefix", any(data[offset:offset + 16]))
        destination.write_bytes(data)
        return info

    with patch.object(recovery, "_managed_build", invalid_il_build):
        try:
            recover(source=diagnostics, output=output, only=[managed_rel], workers=2)
        except RuntimeError as exc:
            check("complete-body validator rejects nonzero malformed IL", "complete method validation" in str(exc))
        else:
            raise AssertionError("malformed nonzero IL was admitted")
    check(
        "failed managed validation preserves the complete previous output and manifest",
        before == {path.relative_to(output): sha256(path) for path in output.rglob("*") if path.is_file()},
    )
    with tempfile.TemporaryDirectory(prefix="verify-gtsplus-decoder-failure-") as tmp:
        failing = Path(tmp) / "failure.py"
        failing.write_text("print('per-input decoder failure marker')\nraise SystemExit(7)\n")
        with patch.object(recovery, "DECODER", failing):
            try:
                recover(source=diagnostics, output=output, only=[managed_rel], workers=2)
            except RuntimeError as exc:
                check("decoder failure preserves its own log context", "per-input decoder failure marker" in str(exc))
            else:
                raise AssertionError("failed decoder was admitted")
    check(
        "failed decoder preserves the complete previous output and manifest",
        before == {path.relative_to(output): sha256(path) for path in output.rglob("*") if path.is_file()},
    )
    check("failed recoveries remove their staging outputs", not list(output.parent.glob(f".{output.name}.staging-*")))

    # A successful subset replaces, rather than merges with, the previous tree.
    isolated_source = output.parent / "subset-source"
    isolated_source.mkdir()
    try:
        stub = diagnostics / managed_rel
        shutil.copy2(stub, isolated_source / stub.name)
        shutil.copy2(Path(str(stub) + "._"), isolated_source / f"{stub.name}._")
        manifest = recover(source=isolated_source, output=output, workers=2)
        check(
            "successful replacement records the selected source root and exact subset",
            manifest["source_root"] == str(isolated_source.resolve())
            and manifest["recovered_body_count"] == 1
            and {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
            == {"manifest.json", stub.name},
        )
    finally:
        shutil.rmtree(isolated_source)

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
    verify_collision_schedules(diagnostics, stubs)

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
        canonical_auxiliary = DEFAULT_OUTPUT / "Auxiliary"
        for label, artifact, component_root in (
            ("fresh CP recovery", rebuilt_pcs_semantics, output),
            ("qualified aggregate", tracked_pcs_semantics, canonical_auxiliary),
        ):
            qualification = qualify_recovered_source(
                component_root / selected[2], diagnostics / selected[2], component_root=component_root
            )
            check(
                f"PCS {label} links its exact manifest, output, stub and sidecar",
                artifact["sources"]["qualification"] == qualification,
            )
        check(
            "PCS original and recovered source identities agree across selected roots",
            {key: value for key, value in rebuilt_pcs_semantics["sources"].items() if key != "qualification"}
            == {key: value for key, value in tracked_pcs_semantics["sources"].items() if key != "qualification"},
        )
        check(
            "PCS managed TSS3 semantics artifact regenerates from fresh CP recovery",
            {key: value for key, value in rebuilt_pcs_semantics.items() if key != "sources"}
            == {key: value for key, value in tracked_pcs_semantics.items() if key != "sources"},
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

        verify_validation_transaction(diagnostics, output, selected[1])

    print("GTS+ auxiliary body recovery verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
