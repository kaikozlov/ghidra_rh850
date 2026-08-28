#!/usr/bin/env python3
"""Recover every CP-protected PE body in the pinned GTS+ diagnostics suite."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from recover_cp_bodies import recover as recover_cp_bodies
from recover_cp_bodies import recover_auxiliary
from recover_gtsplus_bodies import recover as recover_gtsplus_bodies
from techstream_paths import REPO, resolve_gts_root

DEFAULT_OUTPUT = REPO / "build/out/gts-all-unprotected"


def recover(
    *,
    gtsplus_root: Path | None = None,
    output: Path = DEFAULT_OUTPUT,
    workers: int | None = None,
) -> dict[str, Any]:
    """Recover the 54 main GTSPlus, 143 CUWPlus, and 52 auxiliary bodies."""
    gts = resolve_gts_root(gtsplus_root)
    output = output.expanduser().resolve()
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True, exist_ok=True)

    main = recover_gtsplus_bodies(output=output / "GTSPlus", installed_root=gts)
    cuw = recover_cp_bodies(
        gtsplus_root=gts,
        source=gts.parent / "CUWPlus",
        output=output / "CUWPlus",
        workers=workers,
    )
    auxiliary = recover_auxiliary(
        gtsplus_root=gts,
        output=output / "Auxiliary",
        workers=workers,
    )

    counts = {
        "gtsplus": int(main["recovered_plaintext_body_count"]),
        "cuwplus": int(cuw["recovered_body_count"]),
        "auxiliary": int(auxiliary["recovered_body_count"]),
    }
    total = sum(counts.values())
    if counts != {"gtsplus": 54, "cuwplus": 143, "auxiliary": 52} or total != 249:
        raise RuntimeError(f"unexpected protected-body census after recovery: {counts}, total={total}")

    manifest = {
        "format": "gtsplus-all-protected-body-recovery-v1",
        "gtsplus_version": main["gtsplus_version"],
        "output_root": str(output),
        "protected_body_count": 249,
        "recovered_body_count": total,
        "components": {
            "GTSPlus": {
                "method": "same-release-installer-plaintext-twin",
                "count": counts["gtsplus"],
                "manifest": str(output / "GTSPlus/manifest.json"),
            },
            "CUWPlus": {
                "method": "cp-emulation-clean-pe-rebuild",
                "count": counts["cuwplus"],
                "manifest": str(output / "CUWPlus/manifest.json"),
            },
            "Auxiliary": {
                "method": "cp-emulation-clean-pe-rebuild",
                "count": counts["auxiliary"],
                "manifest": str(output / "Auxiliary/manifest.json"),
            },
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest
