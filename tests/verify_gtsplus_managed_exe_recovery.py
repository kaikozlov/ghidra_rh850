#!/usr/bin/env python3
"""Verify coree-managed CP EXEs against same-release Toyota plaintext oracles."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

import dnfile
import pefile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from recover_cp_bodies import recover as recover_cp_bodies
from recover_gtsplus_bodies import recover as recover_plaintext_bodies
from techstream_paths import resolve_gts_root

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


def method_body_prefixes(path: Path) -> tuple[int, list[tuple[int, bytes]]]:
    with contextlib.redirect_stderr(io.StringIO()):
        pe = dnfile.dnPE(str(path))
    rows = list(pe.net.mdtables.MethodDef.rows)
    raw = path.read_bytes()
    out: list[tuple[int, bytes]] = []
    for row in rows:
        rva = int(row.Rva or 0)
        if not rva:
            continue
        offset = pe.get_offset_from_rva(rva)
        if offset is None:
            raise AssertionError(f"{path.name}: unmappable MethodDef RVA 0x{rva:X}")
        out.append((rva, raw[offset : offset + 32]))
    return len(rows), out


def section_geometry(path: Path) -> list[tuple[str, int, int]]:
    pe = pefile.PE(str(path), fast_load=True)
    return [
        (sec.Name.rstrip(b"\0").decode("ascii", "replace"), sec.VirtualAddress, sec.Misc_VirtualSize)
        for sec in pe.sections
        if sec.Name.rstrip(b"\0") in {b".text", b".rsrc", b".reloc"}
    ]


def main() -> int:
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
            original_rows, original_bodies = method_body_prefixes(original)
            rebuilt_rows, rebuilt_bodies = method_body_prefixes(rebuilt)
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
            check(f"{rel} every materialized method prefix matches Toyota original", exact == len(original_bodies))
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
                f"{rel} validator proves every MethodDef body materialized",
                entry["method_body_rva_count"] == len(original_bodies)
                and entry["method_body_materialized_count"] == len(original_bodies),
            )
            total_rows += original_rows
            total_bodies += len(original_bodies)
            total_exact += exact

        check("five-oracle MethodDef row census", total_rows == EXPECTED_METHOD_ROWS)
        check("five-oracle body-RVA census", total_bodies == EXPECTED_METHOD_BODY_RVAS)
        check("all 2,637 materialized method prefixes are exact", total_exact == EXPECTED_METHOD_BODY_RVAS)

    print("GTS+ coree-managed EXE recovery verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
