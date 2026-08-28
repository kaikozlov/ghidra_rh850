#!/usr/bin/env python3
"""Verify the generic CP decoder on the non-GTSPlus/non-CUWPlus host trees."""
from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

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
    ]
    with tempfile.TemporaryDirectory(prefix="verify-gtsplus-aux-body-recovery-") as tmp:
        output = Path(tmp) / "recovered"
        manifest = recover(
            source=diagnostics,
            output=output,
            only=selected,
            workers=3,
        )
        check("native/managed/EXE auxiliary representatives recovered", manifest["recovered_body_count"] == 3)
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
            "PCS managed EXE movable anti-debug thunk and CLR body recovered",
            pcs["classification"] == "managed"
            and pcs["protector_success"]
            and pcs.get("assembly_name") == "PCS Data Viewer"
            and pcs["entrypoint_rva"] == 0x66FB40,
        )

    print("GTS+ auxiliary body recovery verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
