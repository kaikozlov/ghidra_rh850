#!/usr/bin/env python3
"""Verify the CUWPlus CP decoder across every recovered PE layout."""
from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

import recover_cp_bodies
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


def main() -> int:
    gts = resolve_gts_root()
    source = gts.parent / "CUWPlus"
    sidecars = sorted([*source.rglob("*.dll._"), *source.rglob("*.exe._")])
    stubs = [Path(str(sidecar)[:-2]) for sidecar in sidecars]
    managed = [stub for stub in stubs if is_managed(stub)]
    check("current CUWPlus protected-body census is 143", len(stubs) == 143)
    check("CUWPlus native/CLR split is 127/16", len(managed) == 16 and len(stubs) - len(managed) == 127)

    selected = [
        "TCUWCanCommonPrepareWriter.dll",  # ordinary native + plaintext oracle
        "TCUWControlCommPhase.dll",       # seven-section native/.idata outlier
        "CommonLib.dll",                  # pure managed DLL
        "CUWAccessRKSWrapper.dll",         # mixed native/CLR image
        "CuwBackendServiceConsoleApp.exe", # managed EXE + phase-0x520 anti-debug path
    ]
    # Full-corpus mode is transactional and decoder failures carry useful log
    # context even when the temporary workspace is cleaned up on unwind.
    with tempfile.TemporaryDirectory(prefix="verify-cuwplus-transaction-") as tmp:
        fixture = Path(tmp)
        source_one = fixture / "source"
        source_one.mkdir()
        sample = source / "TCUWCanCommonPrepareWriter.dll"
        (source_one / sample.name).write_bytes(sample.read_bytes())
        (source_one / f"{sample.name}._").write_bytes(Path(str(sample) + "._").read_bytes())
        output_one = fixture / "output"
        output_one.mkdir()
        sentinel = output_one / "known-good.txt"
        sentinel.write_text("preserve-me")
        failing = fixture / "fail_decoder.py"
        failing.write_text("import sys\nprint('synthetic decoder failure marker')\nraise SystemExit(7)\n")
        original_decoder = recover_cp_bodies.DECODER
        recover_cp_bodies.DECODER = failing
        try:
            try:
                recover_cp_bodies.recover(source=source_one, output=output_one, workers=1)
            except RuntimeError as exc:
                message = str(exc)
            else:
                raise AssertionError("synthetic decoder failure unexpectedly succeeded")
        finally:
            recover_cp_bodies.DECODER = original_decoder
        check("failed full recovery preserves previous output", sentinel.read_text() == "preserve-me")
        check("decoder failure includes temporary log tail", "synthetic decoder failure marker" in message)

    with tempfile.TemporaryDirectory(prefix="verify-cuwplus-body-recovery-") as tmp:
        output = Path(tmp) / "recovered"
        manifest = recover(output=output, only=selected, workers=5)
        check(
            "representative recovery covers all five selected bodies",
            manifest["protected_body_count"] == 5 and manifest["recovered_body_count"] == 5,
        )
        by_path = {entry["relative_path"]: entry for entry in manifest["entries"]}
        check("all representative protectors reach success", all(entry["protector_success"] for entry in manifest["entries"]))

        ordinary = by_path["TCUWCanCommonPrepareWriter.dll"]
        check(
            "ordinary native entry/import contract recovered",
            ordinary["classification"] == "native"
            and ordinary["entrypoint_rva"] == 0x20DB
            and ordinary["import_count"] == 58,
        )
        control = by_path["TCUWControlCommPhase.dll"]
        check(
            "separate-.idata native outlier recovered",
            control["classification"] == "native"
            and control["entrypoint_rva"] == 0x131B
            and control["import_count"] == 102
            and control["section_count"] == 8,
        )
        common = by_path["CommonLib.dll"]
        check(
            "pure CLR body recovered",
            common["classification"] == "managed"
            and common["assembly_name"] == "CommonLib",
        )
        mixed = by_path["CUWAccessRKSWrapper.dll"]
        check(
            "mixed native/CLR body recovered",
            mixed["classification"] == "mixed-managed"
            and mixed["assembly_name"] == "CUWAccessRKSWrapper"
            and mixed["import_count"] == 38,
        )
        console = by_path["CuwBackendServiceConsoleApp.exe"]
        check(
            "managed EXE anti-debug/handoff path recovered",
            console["classification"] == "managed"
            and console["assembly_name"] == "CuwBackendServiceConsoleApp"
            and console["entrypoint_rva"] == 0x3AD0,
        )

        # Independent runtime-unpack oracle retained from the earlier Windows
        # experiment: the tracked decoder must reproduce the original native
        # entry and .text, not merely a parseable PE wrapper.
        oracle = REPO / "software/Techstream/gtsplus/cuwplus/CUWPlus/unpack/TCUWCanCommonPrepareWriter.unpack.dll"
        recovered = output / "TCUWCanCommonPrepareWriter.dll"
        a = pefile.PE(str(recovered), fast_load=False)
        b = pefile.PE(str(oracle), fast_load=False)
        a_text = next(sec for sec in a.sections if sec.Name.rstrip(b"\0") == b".text")
        b_text = next(sec for sec in b.sections if sec.Name.rstrip(b"\0") == b".text")
        a_image = a.get_memory_mapped_image()
        b_image = b.get_memory_mapped_image()
        n = a_text.Misc_VirtualSize
        check(
            "native fixture .text is byte-identical to independent unpack oracle",
            a.OPTIONAL_HEADER.AddressOfEntryPoint == b.OPTIONAL_HEADER.AddressOfEntryPoint
            and a_image[a_text.VirtualAddress : a_text.VirtualAddress + n]
            == b_image[b_text.VirtualAddress : b_text.VirtualAddress + n],
        )
        check("manifest persisted", (output / "manifest.json").is_file())

    print("CUWPlus body recovery verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
