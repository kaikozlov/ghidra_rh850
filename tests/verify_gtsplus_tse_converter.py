#!/usr/bin/env python3
"""Verify the current GTS+ TSE/GTSE saved-session grammar artifact."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_tse_converter import build

ART = REPO / "data/generated/gtsplus_2026/tse_converter_surface.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    tracked = json.loads(ART.read_text(encoding="utf-8"))
    rebuilt = build()
    check("artifact regenerates deterministically", rebuilt == tracked)
    check("schema", tracked["schema"] == "gtsplus-tse-converter-surface-v1")
    check("converter version", tracked["tse_converter_version"] == "01.02.002")
    check("configured template", tracked["configured_template"] == "180_Template.csv")
    check("173 and 180 templates are byte-identical", tracked["template_identity"]["173_equals_180"])
    check("171 differs from 180", not tracked["template_identity"]["171_equals_180"])
    check("FAT search-key census", tracked["header_and_fat"]["fat_search_key_count"] == 38)
    check("FAT search-key width", tracked["header_and_fat"]["search_key_width_bytes"] == 12)

    sections = tracked["selected_saved_sections"]
    for name in (
        "RecordOnBehavior共通",
        "CANバス",
        "VehicleControlHistory共通",
        "PCS時系列作動時FFD",
        "PCS画像FFD",
    ):
        check(f"TSE template section {name}", bool(sections[name]))

    policy = tracked["conversion_policy"]
    check("TSE stores PCS Operation FFD", policy["pcs_operation_ffd_present_in_tse_template"])
    check("TSE stores PCS Image FFD", policy["pcs_image_ffd_present_in_tse_template"])
    check("native PCS Operation FFD API", policy["pcs_operation_ffd_native_storage_api"])
    check("native PCS Image FFD API", policy["pcs_image_ffd_native_storage_api"])
    check("current GTSE conversion skips PCS Operation FFD", policy["current_tse_to_gtse_configuration_skips_pcs_operation_ffd"])
    check("current GTSE conversion skips PCS Image FFD", policy["current_tse_to_gtse_configuration_skips_pcs_image_ffd"])

    exports = set(tracked["native_gts_file_controller"]["selected_exports"])
    for name in (
        "_GFCAddPCSMultiOperationFFDData@8",
        "_GFCGetPCSMultiOperationFFDData@12",
        "_GFCGetPCSMultiOperationFFDDataCount@4",
        "_GFCAddPCSImageFFDData@8",
        "_GFCGetPCSImageFFDData@12",
        "_GFCGetPCSImageFFDDataCount@4",
        "_GFCAddRecordOnBehaviorCommon@8",
        "_GFCAddVehicleControlHistoryData@8",
    ):
        check(f"GTSFileController export {name}", name in exports)

    ring = tracked["ring_buffer_schema"]["declared_rows"]
    by_leaf = {row["path"].split("/")[-1]: row for row in ring}
    expected = {
        "フレームテーブルサイズ(L4)": ("DWORD", "4"),
        "フレームインデックス": ("WORD*256", "2"),
        "フレーム長": ("WORD*256", "2"),
        "信号テーブルサイズ(L5)": ("DWORD", "4"),
        "信号ID": ("WORD", "2"),
        "通信フレームのID": ("BYTE", "1"),
        "通信フレームに対する先頭ビット": ("WORD", "2"),
        "通信フレームに対する終端ビット": ("WORD", "2"),
        "換算MUL": ("DWORD", "4"),
        "換算DIV": ("DWORD", "4"),
        "換算OFFSET": ("DWORD", "4"),
        "リングバッファサイズ(L6)": ("DWORD", "4"),
        "書き込み開始位置": ("LONG", "4"),
        "読み込み開始位置": ("LONG", "4"),
        "書き込み終端位置": ("LONG", "4"),
    }
    for name, pair in expected.items():
        row = by_leaf[name]
        check(f"ring field {name} type/size", (row["type"], row["size"]) == pair)

    signal = tracked["managed_metadata"]["RingBufferParser.dll"]["selected_types"]["RingBufferParser.SignalInfo"]
    for field in ("signalId", "signalName", "unitName", "signed", "mul", "div", "offset", "frameId", "startBit", "endBit"):
        check(f"RingBufferParser SignalInfo field {field}", field in signal["fields"])
    parser_methods = set(
        tracked["managed_metadata"]["RingBufferParser.dll"]["selected_types"]["RingBufferParser.Parser"]["methods"]
    )
    for method in ("ParseFrameTable", "ParseSignalInfoList", "ParseRingBuffer", "ConvertDataFrame", "ConvertNumericValue"):
        check(f"RingBufferParser method {method}", method in parser_methods)

    for component in ("Converter.dll", "RingBufferParser.dll", "TseCompression.dll", "TSEConverter.exe"):
        sample = tracked["managed_metadata"][component]["method_body_sample"]
        check(f"{component} method bodies protector-zeroed", sample["sampled"] > 0 and sample["nonzero_prefixes"] == 0)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
