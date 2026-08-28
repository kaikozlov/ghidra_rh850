#!/usr/bin/env python3
"""Verify the generated PCS Data Viewer TSS3 recorder dictionary."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_pcs_data_viewer_tss3_dictionary import (
    DEFAULT_OUT,
    ORACLE_ENTRIES_EN,
    ORACLE_ENTRIES_JA,
    build,
)


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    tracked = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    rebuilt = build()
    check("generated artifact is deterministic", rebuilt == tracked)
    check("schema", tracked["schema"] == "gtsplus-pcs-data-viewer-tss3-dictionary-v1")
    check("PCS Data Viewer version", tracked["pcs_data_viewer_version"] == "12.00.005")

    counts = {name: value["count"] for name, value in tracked["dictionaries"]["families"].items()}
    check("1,131 TSS3 recorder signal resources", counts["ffd_tss3_signals"] == 1131)
    check("49 TSS3 trigger resources", counts["ffd_tss3_triggers"] == 49)
    check("13 TSS3 image signal resources", counts["imgffd_tss3_signals"] == 13)
    check("18 TSS3 image trigger resources", counts["imgffd_tss3_triggers"] == 18)

    english = tracked["oracles"]["english"]
    japanese = tracked["oracles"]["japanese"]
    for key, value in ORACLE_ENTRIES_EN.items():
        check(f"English oracle {key}", english[key] == value)
    for key, value in ORACLE_ENTRIES_JA.items():
        check(f"Japanese oracle {key}", japanese[key] == value)

    protection = tracked["net_assembly"]["protection"]
    check("managed bodies are protected/zeroed", protection["method_bodies_sampled"] == 512 and protection["method_bodies_with_nonzero_bytes"] == 0)
    types = tracked["net_assembly"]["tss3_types"]
    detail = types[
        "PCSDataViewer.Extractor.OperationFFD.TSS3.Define.DetailBitAssignInfo"
    ]["fields"]
    for field in ("DataID", "DataSize", "BytePosition", "BitPosition", "BitLength", "Lsb", "Offset", "Point"):
        check(f"bit-assignment schema has {field}", field in detail)

    join = tracked["image_ffd_family_did_join"]
    check("FCM image enum selected exactly", join["enum"].endswith("FCMImageFFDTSS3.DataTable.FCMDataTableDIDData.DataID"))
    check("FCM image recorder IDs", join["enum_ids"] == ["0501", "0502", "0507", "0511", "5101", "6001"])
    check("raw image DID 6001 is unnamed", join["enum_ids_without_display_name"] == ["6001"])

    tokens = tracked["protocol_surface"]["distinct_service_tokens"]
    for token in ("SID$AB$12", "SID$AB$13", "SID$EB$23", "SID$EB$33", "DID$6001"):
        check(f"protocol resource token {token}", token in tokens)

    check("Operation FFD native plugin Execute export", tracked["role_plugins"]["operation_ffd_role_plugin"]["exports"] == ["Execute"])
    check("Image FFD native plugin Execute export", tracked["role_plugins"]["image_ffd_role_plugin"]["exports"] == ["Execute"])
    check("recorder IDs explicitly separated from SID22", "not ordinary FRC_P5" in tracked["identity_boundaries"]["recorder_ids_are_not_sid22_dids"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
