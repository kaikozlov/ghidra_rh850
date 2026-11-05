#!/usr/bin/env python3
"""Verify recovered current GTS+ TSE/GTSE procedural semantics."""
from __future__ import annotations

import json
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream.extract_gtsplus_tse_managed_semantics import COMPONENTS, extract

ART = REPO / "data/generated/gtsplus_2026/tse_managed_semantics.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    tracked = json.loads(ART.read_text(encoding="utf-8"))
    rebuilt = extract()
    check("four qualified TSE managed components selected", set(rebuilt["sources"]) == set(COMPONENTS))
    proof = tracked["recovery_proof"]
    for component in COMPONENTS:
        row = proof[component]
        check(
            f"{Path(component).name} complete IL bodies validated independently of native/bodyless methods",
            row["method_body_materialized_count"] > 0
            and row["method_body_materialized_count"] == row["classification_counts"]["il"]
            and row["method_body_materialized_count"] <= row["method_body_rva_count"]
            and row == rebuilt["recovery_proof"][component],
        )

    upgrade = tracked["legacy_upgrade"]
    check("legacy TSE is upgraded through native GTSFileController", upgrade["native_upgrade_api"] == "GFCConvertOldTSEToLatestTSE")
    check("legacy upgrade writes an intermediate NEW.TSE", upgrade["intermediate_directory"] == "_NewTSE" and upgrade["intermediate_filename"] == "{source_stem}_NEW.TSE")
    check("managed BinaryRead consumes upgraded TSE", "upgraded _NEW.TSE -> BinaryRead" in upgrade["pipeline"])

    binary = tracked["binary_read"]
    check("BinaryRead runtime position marker census", len(binary["position_markers"]) == 35)
    selected = binary["selected_position_markers"]
    check("PCS Operation FFD position marker", selected["PCS時系列作動時FFD位置情報"] == "FFFFFFFFFFFFFF27")
    check("PCS Image FFD position marker", selected["PCS画像FFD位置情報"] == "FFFFFFFFFFFFFF28")
    check("Vehicle Control History position marker", selected["VehicleControlHistory共通位置情報"] == "FFFFFFFFFFFFFF23")
    check("TMR position marker", selected["TMR位置情報"] == "FFFFFFFFFFFFFFFE")

    template = binary["template_runtime_contract"]
    check("template runtime encoding", template["template_encoding"] == "Shift_JIS")
    check(
        "template columns 15..22",
        template["columns"] == {
            "15": "Type", "16": "Size", "17": "SizeF", "18": "IsList",
            "19": "LevelF", "20": "ExistF", "21": "PositionF", "22": "PositionSkipF",
        },
    )

    traversal = binary["position_traversal"]
    check("position marker width", traversal["position_marker_width_bytes"] == 8)
    check("position sentinel grammar", traversal["sentinel_shape"] == "FF FF FF FF <selector> FF FF FF")
    check("generic position selector domain", traversal["generic_selector_acceptance"] == "0x01..0x33 or 0xFE")
    check("ECU skip position selectors", traversal["ecu_skip_selector_acceptance"] == ["0x30", "0x33", "0xFE"])
    check("position-record rewind", traversal["position_record_rewind_bytes"] == 8)

    fat = binary["fat_projection"]
    check("FAT projection depth", fat["dictionary_levels"] == 15)
    check("FAT removes header and initial vehicle roots", fat["removed_top_level_keys"] == ["ヘッダ情報", "初期車両情報"])
    check("list duplicate key format", fat["duplicate_list_key_format"] == "{name}_{index:03d}")
    check("ring bytes survive FAT projection", fat["ring_buffer_data_uses_raw_value"])

    gtse = tracked["gtse_compression"]
    check("GTSE exact salt", gtse["salt_hex"] == "e7b77797f2e62ce74b5dc58f8d15c82c574d8a4a")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
