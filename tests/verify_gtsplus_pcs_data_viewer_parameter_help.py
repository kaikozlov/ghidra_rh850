#!/usr/bin/env python3
"""Verify PCS Data Viewer FFD parameter-help extraction."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_pcs_data_viewer_parameter_help import build

ART = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_parameter_help.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    tracked = json.loads(ART.read_text(encoding="utf-8"))
    rebuilt = build()
    check("artifact regenerates deterministically", rebuilt == tracked)
    check("schema", tracked["schema"] == "gtsplus-pcs-data-viewer-parameter-help-v1")
    check("28 English FFD help parameters", len(tracked["english_ffd_parameters"]) == 28)
    check("28 Japanese-help FFD parameters", len(tracked["japanese_help_ffd_parameters"]) == 28)
    check("exact help/resource joins", tracked["exact_join_count"] >= 12)

    by_idx = {x["index"]: x for x in tracked["english_ffd_parameters"]}
    check("PCS operation state semantics", "3:PCS operation" in by_idx[9]["description"] and "0:PCS non-operation" in by_idx[9]["description"])
    check("deceleration request definition", by_idx[10]["description"] == "PCS deceleration request")
    check("target object definition", by_idx[11]["description"] == "Object number of PCS control target")
    check("lateral target definition", by_idx[19]["description"] == "Lateral position of PCS control target")
    check("steering angle definition", by_idx[28]["description"] == "Steering angle")

    joins = {x["help_name"]: {m["key"] for m in x["matches"]} for x in tracked["exact_normalized_dictionary_joins"]}
    check("PBA status joins TSS3 ID 5792", "FFD_TSS3_ID_5792" in joins["PBA Request Status"])
    check("target object joins TSS3 ID 573E", "FFD_TSS3_ID_573E" in joins["Target Object Number"])
    check("steering angle joins TSS3 ID 523D", "FFD_TSS3_ID_523D" in joins["Steering angle"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
