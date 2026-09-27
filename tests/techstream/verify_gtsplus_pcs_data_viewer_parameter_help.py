#!/usr/bin/env python3
"""Verify PCS Data Viewer FFD parameter-help extraction."""
from __future__ import annotations

import json

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream.extract_pcs_data_viewer_parameter_help import build

ART = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_parameter_help.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    tracked = json.loads(ART.read_text(encoding="utf-8"))
    rebuilt = build()
    check("artifact regenerates deterministically", rebuilt == tracked)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
