#!/usr/bin/env python3
"""Verify current-release TSS3 Operation/Image FFD native acquisition semantics."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_tss3_native_recorder import build, level49

ART = REPO / "data/generated/gtsplus_2026/tss3_native_recorder_protocol.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    tracked = json.loads(ART.read_text(encoding="utf-8"))
    rebuilt = build()
    check("artifact regenerates deterministically", rebuilt == tracked)
    check("schema", tracked["schema"] == "gtsplus-tss3-native-recorder-protocol-v1")
    check("current GTS+ release", tracked["gtsplus_version"] == "2026.03.002.02")

    src = tracked["sources"]
    check(
        "current recovered CommandCommon identity",
        src["command_common"]["size"] == 1_280_016
        and src["command_common"]["sha256"] == "98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3",
    )
    check(
        "current recovered TSS3 Image plugin identity",
        src["image_plugin"]["size"] == 117_776
        and src["image_plugin"]["sha256"] == "07cfb84e1d258862f95b68a966cf34dbe8d0967e4008c59b2f16b6733a05ecd8",
    )
    check(
        "current TSS3 Operation plugin identity",
        src["operation_plugin"]["size"] == 38_928
        and src["operation_plugin"]["sha256"] == "67257cf5dfdab990adbc1bab1938ad1cb6bf52a1b307cc7fcd9b7bd33a093414",
    )

    op = tracked["operation_ffd"]
    check("Operation selector 0x66", op["selector"] == "0x66")
    check("Operation behavior enumeration", op["requests"]["enumerate_behavior_codes"]["request"] == "AB11" and op["requests"]["enumerate_behavior_codes"]["positive"] == "EB11")
    check("Operation record enumeration", op["requests"]["enumerate_behavior_records"]["request"] == "AB12 || behavior_id_be16" and op["requests"]["enumerate_behavior_records"]["positive"] == "EB12")
    check("Operation record fetch", op["requests"]["fetch_record"]["request"] == "AB13 || behavior_id_be16 || record_id_be16" and op["requests"]["fetch_record"]["positive"] == "EB13")
    check("Operation record payload offset", op["record_parser"]["data_offset"] == 6)
    check("Operation record block geometry", op["record_parser"]["block"] == "data_id_be16 || length_u8 || data[length]")
    check(
        "special behavior table",
        op["special_behavior_ids"]
        == ["0x2270", "0x2271", "0x2272", "0x2273", "0x2274", "0x2296", "0x2297", "0x2298", "0x2299", "0x227C", "0x227D", "0x229A", "0x22B0", "0x22B1", "0x22B2"],
    )

    image = tracked["image_ffd"]
    check(
        "Image FFD semantic call order",
        image["semantic_call_order"]
        == ["get spec information", "get flag/availability", "get flag/availability (spec-dependent branch)", "security unlock", "get encryption method"],
    )
    frames = image["frames"]
    check("Image spec DID 1103", frames["spec_information"]["request"] == "221103" and frames["spec_information"]["positive"] == "621103")
    check("Image availability DID 1101", frames["availability"]["request"] == "221101" and frames["availability"]["positive"] == "621101")
    check("Image encryption DID 2081", frames["encryption_method"]["request"] == "222081" and frames["encryption_method"]["positive"] == "622081")
    check("Image security seed service", frames["security_seed"]["request"] == "2703" and frames["security_seed"]["positive"] == "6703")
    check("Image security key service", frames["security_key"]["request_prefix"] == "2704" and frames["security_key"]["positive"] == "6704")
    check("Image spec 5/7 contract", image["spec_contract"]["accepted_spec_values"] == [5, 7])
    check("spec5 has ten image slots", image["spec_contract"]["spec_5_availability_slots"] == list(range(1, 11)))
    check("spec7 has eleven image slots", image["spec_contract"]["spec_7_availability_slots"] == list(range(1, 12)))
    check("availability marker is 2", image["spec_contract"]["available_value"] == 2)

    vectors = image["security"]["algorithm_vectors"]
    for seed, expected in {
        "000000000000": "000000000000",
        "010203040506": "04070a0d1a64",
        "123456789abc": "9e6a50252409",
        "deadbeefcafe": "cbd8b6970cba",
    }.items():
        check(f"current level-49 key vector {seed}", level49(bytes.fromhex(seed)).hex() == expected and vectors[seed] == expected)

    calls = [row["target"] for row in image["get_info_direct_calls"]]
    check("current GetTSS3ImageFFDInfo directly calls six-byte SecurityUnlock", any(name.startswith("?SecurityUnlock@CCmdImgOpeDdr") for name in calls))
    check("current GetTSS3ImageFFDInfo does not call SecurityUnlock16Byte", not any(name.startswith("?SecurityUnlock16Byte@CCmdImgOpeDdr") for name in calls))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
