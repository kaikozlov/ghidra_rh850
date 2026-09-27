#!/usr/bin/env python3
"""Verify recovered PCS Data Viewer DDR field semantics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT
ART = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_ddr_semantics.json"
DIAG = REPO / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    data = json.loads(ART.read_text())
    for key in ("protected_exe", "protected_sidecar", "english_resources"):
        source = data["sources"][key]
        path = DIAG / source["path"]
        check(f"{key} source identity", path.stat().st_size == source["size"] and sha256(path) == source["sha256"])

    print("GTS+ PCS Data Viewer recovered DDR semantics verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
