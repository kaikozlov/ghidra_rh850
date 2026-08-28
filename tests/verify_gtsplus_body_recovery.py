#!/usr/bin/env python3
"""Verify complete recovery of the current GTS+ CP-protected PE bodies."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from recover_gtsplus_bodies import recover


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


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

    print("GTS+ body recovery verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
