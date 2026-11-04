#!/usr/bin/env python3
"""Verify coree-managed CP EXEs against same-release Toyota plaintext oracles."""
from __future__ import annotations

import argparse
import contextlib
import io
import struct
import tempfile
from pathlib import Path

import pefile

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream.recover_cp_bodies import recover as recover_cp_bodies
from tools.techstream.recover_gtsplus_bodies import _managed_admission, recover as recover_plaintext_bodies
from tools.techstream.techstream_paths import resolve_gts_root
from tools.techstream.inspect_dotnet_il import inspect_managed_bodies, validate_managed_bodies

CORE_EXES = (
    "bin/GTSPlus.exe",
    "bin/GTSPlusArbitration.exe",
    "GtsPlus-InfoCenter/GtsPlus-InfoCenter.exe",
    "GtsPlus-InfoCenter/GtsPlus-InfoCenter_Multi/GtsPlus-InfoCenter_Multi.exe",
    "GtsPlus-PcCheckerTool/GtsPlus-PcCheckerTool.exe",
)
EXPECTED_METHOD_ROWS = 2_719
EXPECTED_METHOD_BODY_RVAS = 2_637


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def method_bodies(path: Path) -> tuple[int, list[tuple[int, bytes]]]:
    result = inspect_managed_bodies(path)
    raw = path.read_bytes()
    bodies = [
        (
            method["rva"],
            raw[method["body"]["file_offset"] : method["body"]["file_offset"] + method["body"]["size"]],
        )
        for method in result["methods"] if method["implementation"] == "il"
    ]
    return result["method_def_count"], bodies


def managed_fixture(
    body: bytes,
    implementations: tuple[tuple[int, int, bool], ...] = ((0, 0x16, True), (0, 0x16, True), (3, 0x16, False)),
    *,
    nested_parent: int = 3,
) -> bytes:
    """Build a real minimal CLR PE with colliding nested names and shared RVAs."""
    strings = bytearray(b"\0")

    def string(value: str) -> int:
        index = len(strings)
        strings.extend(value.encode() + b"\0")
        return index

    module_name, assembly_name = string("Fixture.dll"), string("Fixture")
    namespace = string("Example")
    names = [string(name) for name in ("<Module>", "OuterA", "Duplicate", "OuterB", "Duplicate", "Duplicate")]
    method_name = string("Invoke")
    valid = sum(1 << table for table in (0, 2, 6, 32, 41))
    tables = bytearray(struct.pack("<IBBBBQQ", 0, 2, 0, 0, 1, valid, 0))
    tables.extend(struct.pack("<5I", 1, 6, len(implementations), 1, 3))
    tables.extend(struct.pack("<5H", 0, module_name, 1, 0, 0))
    for rid, (name, first_method) in enumerate(zip(names, (1, 1, 1, 2, 2, 3)), 1):
        nested = rid in (3, 5, 6)
        tables.extend(struct.pack("<I5H", 2 if nested else 1, name, 0 if nested else namespace, 0, 1, first_method))
    for index, (impl, flags, has_rva) in enumerate(implementations):
        signature = 1 if index != 1 else 5
        tables.extend(struct.pack("<I5H", 0x2600 if has_rva else 0, impl, flags, method_name, signature, 1))
    tables.extend(struct.pack("<I4HI3H", 0x8004, 1, 0, 0, 0, 0, 0, assembly_name, 0))
    tables.extend(struct.pack("<6H", 3, 2, 5, 4, 6, nested_parent))
    streams = [
        ("#~", bytes(tables)), ("#Strings", bytes(strings)), ("#US", b"\0"),
        ("#GUID", bytes.fromhex("1234567890abcdef1234567890abcdef")),
        ("#Blob", b"\0\x03\x00\x00\x01\x03\x20\x00\x01"),
    ]
    version = b"v4.0.30319\0\0"
    root = struct.pack("<IHHII", 0x424A5342, 1, 1, 0, len(version)) + version
    root += struct.pack("<HH", 0, len(streams))
    header_size = len(root) + sum(8 + ((len(name) + 4) & ~3) for name, _ in streams)
    headers, payload = bytearray(), bytearray()
    for name, data in streams:
        headers.extend(struct.pack("<II", header_size + len(payload), len(data)))
        encoded = name.encode() + b"\0"
        headers.extend(encoded + b"\0" * (-len(encoded) % 4))
        payload.extend(data)
        payload.extend(b"\0" * (-len(payload) % 4))
    metadata = root + headers + payload
    check("fixture metadata fits before IL", len(metadata) <= 0x400)
    raw_size = 0x600 + len(body)
    image = bytearray(0x200 + raw_size)
    image[:2] = b"MZ"
    struct.pack_into("<I", image, 0x3C, 0x80)
    image[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", image, 0x84, 0x14C, 1, 0, 0, 0, 0xE0, 0x2102)
    optional = 0x98
    struct.pack_into("<H", image, optional, 0x10B)
    struct.pack_into("<I", image, optional + 4, raw_size)
    struct.pack_into("<III", image, optional + 28, 0x400000, 0x2000, 0x200)
    struct.pack_into("<H", image, optional + 40, 4)
    struct.pack_into("<II", image, optional + 56, 0x4000, 0x200)
    struct.pack_into("<H", image, optional + 68, 3)
    struct.pack_into("<I", image, optional + 92, 16)
    struct.pack_into("<II", image, optional + 96 + 14 * 8, 0x2000, 72)
    section = optional + 0xE0
    image[section : section + 8] = b".text\0\0\0"
    struct.pack_into("<IIII", image, section + 8, raw_size, 0x2000, raw_size, 0x200)
    struct.pack_into("<I", image, section + 36, 0x60000020)
    struct.pack_into("<IHHIIII", image, 0x200, 72, 2, 5, 0x2200, len(metadata), 1, 0)
    image[0x400 : 0x400 + len(metadata)] = metadata
    image[0x800:] = body
    return bytes(image)


def verify_managed_integrity() -> None:
    """Exercise admission against real metadata and exact raw-section boundaries."""
    with tempfile.TemporaryDirectory(prefix="verify-managed-integrity-") as tmp:
        path = Path(tmp) / "Fixture.dll"

        def validate(body: bytes, *args, **kwargs) -> dict:
            path.write_bytes(managed_fixture(body, *args, **kwargs))
            with contextlib.redirect_stderr(io.StringIO()):
                return inspect_managed_bodies(path)

        def reject(label: str, body: bytes, *args, **kwargs) -> None:
            try:
                validate(body, *args, **kwargs)
            except ValueError:
                check(label, True)
            else:
                raise AssertionError(label)

        tiny = b"\x06\x2a"
        fat = struct.pack("<HHII", 0x3013, 8, 1, 0) + b"\x2a"
        extended = struct.pack("<HHII", 0x4013, 8, 1, 0) + b"\0" * 4 + b"\x2a"
        small_clause = struct.pack("<HHBHB I", 2, 0, 1, 1, 1, 0)
        small_section = b"\x01\x10\0\0" + small_clause
        eh_header = struct.pack("<HHII", 0x300B, 8, 2, 0) + b"\x00\xdc\0\0"
        small = eh_header + small_section
        chained = eh_header + b"\x81" + small_section[1:] + small_section
        fat_section = b"\x41\x1c\0\0" + struct.pack("<6I", 2, 0, 1, 1, 1, 0)
        switch = b"\x2e\x16\x45" + struct.pack("<Ii", 1, 0) + b"\x2a"
        for label, body in (
            ("tiny", tiny), ("fat", fat), ("extended fat", extended),
            ("small EH", small), ("fat EH", eh_header + fat_section), ("chained EH", chained),
            ("switch", switch),
        ):
            result = validate(body)
            check(f"complete {label} body admitted", result["method_body_materialized_count"] == 2)
            check(f"{label} full body size retained", result["methods"][0]["body"]["size"] == len(body))
        result = validate(tiny)
        compact = validate_managed_bodies(path)
        check("admission proof stays compact", set(compact) == {
            "assembly_name", "source_sha256", "module_mvid", "classification_counts",
            "method_def_count", "method_body_rva_count", "method_body_materialized_count",
        })
        check("installer admission uses the same compact managed proof", _managed_admission(path) == compact)
        types = result["type_definitions"]
        check("nested short-name collisions remain distinct", len({record["full_nested_name"] for record in types[2::2]}) == 2)
        check("complete nested owner chain", types[5]["full_nested_name"] == "Example.OuterA+Duplicate+Duplicate")
        check("nested owner tokens retained", types[5]["owner_chain"] == ["0x02000002", "0x02000003", "0x02000006"])
        methods = result["methods"]
        check("shared RVA retains distinct MethodDef identities", methods[0]["rva"] == methods[1]["rva"] and methods[0]["identity"] != methods[1]["identity"])
        check("signature ownership retained", methods[0]["signature_hex"] == "000001" and methods[1]["signature_hex"] == "200001")
        check("source/module scope retained", result["source_sha256"] in methods[0]["identity"] and result["module_mvid"] in methods[0]["identity"])
        check("assembly name retained", result["assembly_name"] == "Fixture")
        cases = (
            (0, 0x416, False), (0, 0x2016, False), (3, 0x16, False),
            (0x1000, 0x16, False), (0x10, 0x16, False),
            (1, 0x16, True), (2, 0x16, True), (4, 0x16, True),
        )
        classified = validate(b"\0" * 8 + b"BSJB", cases)
        check("legitimate RVA0 and non-IL implementations admitted without IL parsing", classified["method_body_materialized_count"] == 0)
        check("all actual implementation categories explicit", classified["classification_counts"] == {
            "abstract": 1, "pinvoke": 1, "runtime": 1, "internal_call": 1,
            "forward_ref": 1, "native": 1, "optil": 1, "unmanaged": 1,
        })
        check("non-IL RVAs remain in legacy RVA census", classified["method_body_rva_count"] == 3 and classified["method_def_count"] == 8)
        mixed = validate(tiny, ((0, 0x16, True), (1, 0x2016, True), (3, 0x16, False)))
        check("native import stubs are not IL", mixed["classification_counts"] == {"il": 1, "native": 1, "runtime": 1})
        check("mixed-module RVA and valid-IL counts differ explicitly", mixed["method_body_rva_count"] == 2 and mixed["method_body_materialized_count"] == 1)
        changed = validate(b"\x0a\x00\x2a")
        check("source bytes scope identities independently of MVID/token", changed["module_mvid"] == result["module_mvid"] and changed["methods"][0]["identity"] != methods[0]["identity"])
        reject("required IL RVA0 rejected", tiny, ((0, 0x16, True), (0, 0x16, True), (0, 0x16, False)))
        reject("cyclic NestedClass rejected", tiny, nested_parent=6)
        reject("invalid NestedClass token rejected", tiny, nested_parent=99)
        for label, body in (
            ("hollow console zero header", b"\0" * 16),
            ("hollow console zero header before BSJB", b"\0" * 8 + b"BSJB"),
            ("empty instruction stream", b"\x02"),
            ("truncated fat header", b"\x03\x30\x08"),
            ("undersized fat header", struct.pack("<HHII", 0x2013, 8, 1, 0) + b"\x2a"),
            ("reserved fat flags", struct.pack("<HHII", 0x3033, 8, 1, 0) + b"\x2a"),
            ("truncated instruction stream", b"\x12\x00\x00\x2a"),
            ("operand crossing code end", b"\x06\x20" + b"\0" * 4),
            ("truncated two-byte opcode", b"\x06\xfe"),
            ("unknown opcode", b"\x06\xff"),
            ("branch into operand", b"\x12\x2b\x01\x1f\x00"),
            ("switch into operand", b"\x2e\x16\x45" + struct.pack("<Ii", 1, -1) + b"\x2a"),
            ("switch count exceeds code", b"\x2e\x16\x45" + struct.pack("<Ii", 2, 0) + b"\x2a"),
            ("missing extra section", eh_header),
            ("truncated extra section", small[:-1]),
            ("invalid extra section size", eh_header + b"\x01\x0f\0\0" + small_clause),
            ("unknown extra section kind", eh_header + b"\x02\x10\0\0" + small_clause),
            ("missing chained extra section", chained[:-16]),
            ("EH range outside code", eh_header + b"\x01\x10\0\0" + struct.pack("<HHBHB I", 2, 0, 3, 1, 1, 0)),
            ("invalid local signature", struct.pack("<HHII", 0x3013, 8, 1, 0x11000001) + b"\x2a"),
        ):
            reject(label, body)
        overlay = bytearray(managed_fixture(tiny))
        struct.pack_into("<I", overlay, 0x178 + 16, 0x601)
        truncated_signature = bytearray(managed_fixture(tiny))
        blob = truncated_signature.index(b"\0\x03\x00\x00\x01\x03\x20\x00\x01", 0x400, 0x800)
        truncated_signature[blob + 1] = 0x3f
        for label, image in (
            ("IL cannot consume bytes beyond section raw size", bytes(overlay)),
            ("truncated metadata rejected", managed_fixture(tiny)[:0x450]),
            ("truncated MethodDef signature heap item rejected", bytes(truncated_signature)),
        ):
            path.write_bytes(image)
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    validate_managed_bodies(path)
            except ValueError:
                check(label, True)
            else:
                raise AssertionError(label)
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    _managed_admission(path)
            except RuntimeError as error:
                check(f"installer admission: {label}", "complete method validation" in str(error))
            else:
                raise AssertionError(f"installer admitted malformed declared CLR input: {label}")


def section_geometry(path: Path) -> list[tuple[str, int, int]]:
    pe = pefile.PE(str(path), fast_load=True)
    return [
        (sec.Name.rstrip(b"\0").decode("ascii", "replace"), sec.VirtualAddress, sec.Misc_VirtualSize)
        for sec in pe.sections
        if sec.Name.rstrip(b"\0") in {b".text", b".rsrc", b".reloc"}
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--integrity-only", action="store_true", help="run self-contained managed admission regressions only")
    args = parser.parse_args()
    verify_managed_integrity()
    if args.integrity_only:
        return 0
    gts = resolve_gts_root()
    with tempfile.TemporaryDirectory(prefix="verify-gtsplus-managed-exe-") as tmp:
        tmp_root = Path(tmp)
        plaintext = tmp_root / "plaintext"
        recovered = tmp_root / "recovered"
        recover_plaintext_bodies(output=plaintext, installed_root=gts)
        manifest = recover_cp_bodies(
            gtsplus_root=gts,
            source=gts,
            output=recovered,
            only=list(CORE_EXES),
            workers=5,
        )
        check("all five coree-managed oracle EXEs selected", manifest["recovered_body_count"] == 5)
        by_path = {entry["relative_path"]: entry for entry in manifest["entries"]}

        total_rows = 0
        total_bodies = 0
        total_exact = 0
        for rel in CORE_EXES:
            original = plaintext / rel
            rebuilt = recovered / rel
            original_rows, original_bodies = method_bodies(original)
            rebuilt_rows, rebuilt_bodies = method_bodies(rebuilt)
            entry = by_path[rel]
            original_pe = pefile.PE(str(original), fast_load=True)
            rebuilt_pe = pefile.PE(str(rebuilt), fast_load=True)

            check(f"{rel} MethodDef census preserved", rebuilt_rows == original_rows)
            check(
                f"{rel} MethodDef RVA sequence preserved",
                [rva for rva, _ in rebuilt_bodies] == [rva for rva, _ in original_bodies],
            )
            exact = sum(
                rebuilt_rva == original_rva and rebuilt_body == original_body
                for (rebuilt_rva, rebuilt_body), (original_rva, original_body)
                in zip(rebuilt_bodies, original_bodies)
            )
            check(f"{rel} every complete IL body matches Toyota original", exact == len(original_bodies))
            check(
                f"{rel} original entrypoint preserved",
                rebuilt_pe.OPTIONAL_HEADER.AddressOfEntryPoint
                == original_pe.OPTIONAL_HEADER.AddressOfEntryPoint,
            )
            check(
                f"{rel} application section geometry preserved",
                section_geometry(rebuilt) == section_geometry(original),
            )
            trusts = entry["synthetic_api_integrity_trusts"]
            check(
                f"{rel} uses exactly one scoped GetProcAddress integrity trust",
                len(trusts) == 1 and trusts[0]["api"] == "kernel32.dll!GetProcAddress",
            )
            check(
                f"{rel} validator proves every required IL body complete",
                entry["method_body_rva_count"] == len(original_bodies)
                and entry["method_body_materialized_count"] == len(original_bodies),
            )
            total_rows += original_rows
            total_bodies += len(original_bodies)
            total_exact += exact

        check("five-oracle MethodDef row census", total_rows == EXPECTED_METHOD_ROWS)
        check("five-oracle body-RVA census", total_bodies == EXPECTED_METHOD_BODY_RVAS)
        check("all 2,637 complete IL bodies are exact", total_exact == EXPECTED_METHOD_BODY_RVAS)

    print("GTS+ coree-managed EXE recovery verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
