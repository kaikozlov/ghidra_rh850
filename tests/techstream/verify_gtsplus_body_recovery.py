#!/usr/bin/env python3
"""Verify complete recovery of the current GTS+ CP-protected PE bodies."""
from __future__ import annotations

import hashlib
import json
import tempfile
import struct
from pathlib import Path
from unittest.mock import patch

import pefile

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream import recover_gtsplus_bodies as recovery
from tools.techstream.inspect_dotnet_il import inspect_managed_bodies, validate_managed_bodies
from tools.techstream.recover_gtsplus_bodies import recover


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")

def verify_validation_transaction(output: Path) -> None:
    """Corrupt only a staged installer copy, not its PE framing or source input."""
    def snapshot() -> dict[Path, str]:
        return {
            path.relative_to(output): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in output.rglob("*") if path.is_file()
        }

    before = snapshot()
    original_copy = recovery.shutil.copy2
    corrupted = False

    def invalid_il_copy(source: Path, destination: Path) -> str | Path:
        nonlocal corrupted
        result = original_copy(source, destination)
        if destination.name == "GTSPlus.exe":
            methods = inspect_managed_bodies(destination)["methods"]
            method = next(row for row in methods if row["implementation"] == "il")
            offset = method["body"]["file_offset"]
            data = bytearray(destination.read_bytes())
            # Keep a nonzero, parseable PE while making its IL code exceed EOF.
            struct.pack_into("<HHII", data, offset, 0x3003, 8, len(data) + 1, 0)
            destination.write_bytes(data)
            check("malformed managed installer fixture retains PE .text", recovery._text_shape(destination) is not None)
            corrupted = True
        return result

    with patch.object(recovery.shutil, "copy2", invalid_il_copy):
        try:
            recover(output=output)
        except RuntimeError as error:
            check(
                "installer rejects a parseable PE with malformed IL before promotion",
                corrupted and "installer managed twin failed complete method validation" in str(error),
            )
        else:
            raise AssertionError("malformed managed installer twin was admitted")
    check("failed installer admission preserves all previous binaries and manifest", snapshot() == before)
    check("failed installer admission removes staging outputs", not list(output.parent.glob(f".{output.name}.staging-*")))



def main() -> int:
    with tempfile.TemporaryDirectory(prefix="verify-gtsplus-body-recovery-") as tmp:
        output = Path(tmp) / "recovered"
        manifest = recover(output=output)

        check("current GTS+ release pinned", manifest["gtsplus_version"] == "2026.03.002.02")
        check(
            "all installed protected GTS+ PE bodies are recovered",
            manifest["coverage_complete"]
            and manifest["installed_protected_body_count"] == 54
            and manifest["recovered_plaintext_body_count"] == 54,
        )
        counts = {row["installer"]: row["protected_body_count"] for row in manifest["installers"]}
        check("Setup_PF contributes all 45 protected bin bodies", counts == {"Setup_PF.exe": 45, "Setup_InfoCenter.exe": 9})

        by_path = {row["path"]: row for row in manifest["binaries"]}
        command = by_path["bin/CommandCommon.dll"]
        check(
            "CommandCommon original PE identity",
            command["plaintext"]["size"] == 1_280_016
            and command["plaintext"]["sha256"] == "98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3",
        )
        check(
            "CommandCommon CP image is the installed hollow representation",
            command["protected"]["stub_size"] == 356_368
            and command["protected"]["sidecar_size"] == 792_048
            and command["protected"]["text"]["raw_size"] == 0x1000
            and command["protected"]["text"]["virtual_size"] == 0xD4000,
        )
        check(
            "CommandCommon recovered native .text is materialized",
            command["plaintext"]["text"]["raw_size"] == 0xD3600
            and command["plaintext"]["native_text_expanded_vs_cp"],
        )

        info = by_path["GtsPlus-InfoCenter/GtsPlus-CM.dll"]
        checker = by_path["GtsPlus-PcCheckerTool/GtsPlus-PcCheckerTool.exe"]
        check(
            "InfoCenter and PcChecker protected bodies are included",
            info["installer"] == "Setup_InfoCenter.exe"
            and checker["installer"] == "Setup_InfoCenter.exe"
            and (output / info["path"]).is_file()
            and (output / checker["path"]).is_file(),
        )
        check(
            "every CP stub and sidecar is byte-identical to the installed pair",
            all(
                row["package_identity"]["cp_stub_matches_installed"]
                and row["package_identity"]["cp_sidecar_matches_installed"]
                for row in manifest["binaries"]
            ),
        )
        check(
            "manifest persisted with the recovered corpus",
            json.loads((output / "manifest.json").read_text(encoding="utf-8"))["coverage_complete"],
        )
        producer = manifest["producer"]
        for relative in (
            "tools/techstream/recover_gtsplus_bodies.py",
            "tools/techstream/inspect_dotnet_il.py",
        ):
            check(
                f"installer provenance pins {relative}",
                producer["sources"][relative] == hashlib.sha256((REPO / relative).read_bytes()).hexdigest(),
            )
        check(
            "installer provenance includes managed reader dependencies",
            all(producer["dependencies"][name] for name in ("dnfile", "dncil", "pefile")),
        )
        for row in manifest["binaries"]:
            path = output / row["path"]
            pe = pefile.PE(str(path), fast_load=True)
            try:
                index = pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR"]
                directories = pe.OPTIONAL_HEADER.DATA_DIRECTORY
                declared_clr = len(directories) > index and bool(
                    directories[index].VirtualAddress or directories[index].Size
                )
            finally:
                pe.close()
            plaintext = row["plaintext"]
            if declared_clr:
                proof = plaintext.get("managed_body_validation")
                check(f'{row["path"]} carries the shared complete managed admission proof', proof == validate_managed_bodies(path))
                check(f'{row["path"]} proof identifies unchanged installer bytes', proof["source_sha256"] == plaintext["sha256"])
            else:
                check(f'{row["path"]} remains a native installer twin', "managed_body_validation" not in plaintext)
        verify_validation_transaction(output)

    print("GTS+ body recovery verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
