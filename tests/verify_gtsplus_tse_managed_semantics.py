#!/usr/bin/env python3
"""Verify recovered current GTS+ TSE/GTSE procedural semantics."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_tse_managed_semantics import COMPONENTS, extract
from recover_cp_bodies import recover
from techstream_paths import resolve_gts_root

ART = REPO / "data/generated/gtsplus_2026/tse_managed_semantics.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    diagnostics = resolve_gts_root().parent
    tracked = json.loads(ART.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="verify-gtsplus-tse-managed-") as tmp:
        recovered = Path(tmp) / "recovered"
        manifest = recover(
            source=diagnostics,
            output=recovered,
            only=list(COMPONENTS),
            workers=4,
        )
        check("four TSE managed components recover", manifest["recovered_body_count"] == 4)
        rebuilt = extract(recovered)
    check("artifact regenerates from fresh CP recovery", rebuilt == tracked)
    check("schema", tracked["schema"] == "gtsplus-tse-managed-semantics-v1")

    proof = tracked["recovery_proof"]
    for component in COMPONENTS:
        row = proof[component]
        check(
            f"{Path(component).name} every executable method body materialized",
            row["method_body_rva_count"] > 0
            and row["method_body_materialized_count"] == row["method_body_rva_count"],
        )

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

    ring = tracked["ring_buffer_parser"]
    check("ring record width", ring["record_width"] == "8-byte timestamp + 2 * sum(frame lengths)")
    check("ring engineering conversion", ring["engineering_value"] == "((raw * MUL) / DIV + OFFSET) / 10^decimal_places")

    gtse = tracked["gtse_compression"]
    check("GTSE exact salt", gtse["salt_hex"] == "e7b77797f2e62ce74b5dc58f8d15c82c574d8a4a")
    check("GTSE salted SHA-256 contract", gtse["per_file_digest"].startswith("SHA-256(file_bytes || 20-byte salt)"))
    check("GTSE Shift-JIS list manifest", "Shift-JIS" in gtse["manifest"])
    check("GTSE ZIP then rename", "ZipFile.CreateFromDirectory" in gtse["archive"] and "File.Move" in gtse["archive"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
