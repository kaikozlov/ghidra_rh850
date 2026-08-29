#!/usr/bin/env python3
"""Verify the privacy-minimized public Toyota TSE lineage observations."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OBS = REPO / "data/external/public_techstream_tse_lineage.json"
SURFACE = REPO / "data/generated/gtsplus_2026/tse_converter_surface.json"
MANAGED = REPO / "data/generated/gtsplus_2026/tse_managed_semantics.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    obs = json.loads(OBS.read_text(encoding="utf-8"))
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    managed = json.loads(MANAGED.read_text(encoding="utf-8"))

    check("public TSE lineage schema", obs["schema"] == "public-techstream-tse-lineage-v1")
    check("raw third-party sessions are intentionally not tracked", "Raw third-party diagnostic sessions" in obs["privacy_boundary"])
    check("three public archive identities retained", sorted(int(k) for k in obs["source"]["attachments"]) == [2573, 2594, 2615])
    check("four distinct Toyota TSE specimens", len(obs["samples"]) == 4 and len({x["tse_sha256"] for x in obs["samples"]}) == 4)
    check("legacy specimen scope is explicitly pre-TSS3", obs["specimen_scope"]["generation"] == "legacy pre-TSS3")

    expected_fat = [
        "IniCarInfo", "ConfCarInfo", "MultiPID", "FuncName", "HealthCheck", "TimeStamp",
        "ROBCommon", "MILMessage", "CanBus", "DualData", "DDRData", "OpeFFD", "ImgFFD", "ECUInfo",
    ]
    check("legacy top-level FAT key order", obs["common_legacy_top_level_fat_keys"] == expected_fat)

    for sample in obs["samples"]:
        header = sample["header"]
        check(f"{sample['sample_id']} TSE signature", header["signature_hex"] == "9a53db1254534500")
        check(f"{sample['sample_id']} legacy header version", header["version"] == "0x102A" and header["header_size"] == 0x2E)
        check(f"{sample['sample_id']} Techstream identity", header["gts_version"] == "11.30.137" and header["user_type_code"] == "EU_CORP")
        fat = sample["legacy_top_level_fat"]
        check(f"{sample['sample_id']} FAT row count/order", [x["key"] for x in fat] == expected_fat)
        check(f"{sample['sample_id']} FAT targets in bounds", all(0 <= x["position"] <= sample["tse_size"] - 8 for x in fat))
        check(f"{sample['sample_id']} FAT targets use current scan shape", all(x["target_matches_current_scan_shape"] for x in fat))
        check(
            f"{sample['sample_id']} first three section selectors",
            [x["target_selector"] for x in fat[:3]] == [0x01, 0x02, 0x17],
        )

    # Current Toyota template begins with the same field grammar observed in the
    # public historical samples; later/current fields are not projected backward.
    header_rows = {x["path"]: x for x in surface["header_and_fat"]["declared_header_rows"]}
    check("current template keeps 8-byte file-extension/signature field", header_rows["File extention"]["type"] == "BYTE" and header_rows["File extention"]["size"] == "8")
    check("current template keeps DWORD/WORD/WORD file header", header_rows["ID"]["type"] == "DWORD" and header_rows["Ver"]["type"] == "WORD" and header_rows["予備"]["type"] == "WORD")
    check("current template keeps 12-byte FAT keys", header_rows["初期車両情報先頭位置検索キーワード"]["type"] == "CHAR" and header_rows["初期車両情報先頭位置検索キーワード"]["size"] == "12")
    check("current template keeps DWORD FAT positions", header_rows["初期車両情報先頭位置"]["type"] == "DWORD" and header_rows["初期車両情報先頭位置"]["size"] == "4")

    traversal = managed["binary_read"]["position_traversal"]
    check("public FAT targets match recovered current scan grammar", traversal["sentinel_shape"] == "FF FF FF FF <selector> FF FF FF")
    upgrade = managed["legacy_upgrade"]
    check("current converter explicitly upgrades old TSE before BinaryRead", upgrade["native_upgrade_api"] == "GFCConvertOldTSEToLatestTSE" and "upgraded _NEW.TSE -> BinaryRead" in upgrade["pipeline"])
    check("true-TSS3 PCS specimen remains separate", "true-TSS3" in obs["specimen_scope"]["boundary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
