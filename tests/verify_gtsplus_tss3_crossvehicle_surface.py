#!/usr/bin/env python3
"""Verify the current-GTS+ cross-vehicle TSS3/recorder evidence artifact."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_tss3_crossvehicle_surface import build

ART = REPO / "data/generated/gtsplus_2026/tss3_crossvehicle_surface.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    stored = json.loads(ART.read_text(encoding="utf-8"))
    current = build()
    check("artifact regenerates byte-semantically from pinned current GTS+", stored == current)
    check("schema/version pinned", stored["schema"] == "gtsplus-tss3-crossvehicle-surface-v1" and stored["gtsplus_version"] == "2026.03.002.02")

    fleet = stored["fleet_category_498_architecture"]
    expected = {
        "NA": (256, 51, 5),
        "EU": (460, 93, 9),
        "JP": (213, 70, 9),
    }
    for region, (rows, names, architectures) in expected.items():
        got = fleet[region]
        check(
            f"{region} FRC_P5 fleet breadth",
            (got["frc_p5_install_row_count"], got["frc_p5_model_name_count"], got["architecture_count"])
            == (rows, names, architectures),
        )
        check(
            f"{region} Steering Actuator is minority of FRC_P5 rows",
            got["selected_category_cooccurrence_counts"]["499"] < got["frc_p5_install_row_count"],
        )
        for cid in (427, 428, 429, 431, 432):
            check(
                f"{region} category {cid} is not joined to FRC_P5 by current install sets",
                got["selected_category_cooccurrence_counts"][str(cid)] == 0,
            )

    na_arch = {tuple(row["selected_category_ids"]): row["install_row_count"] for row in fleet["NA"]["architectures"]}
    check("NA dominant FRC+EMPS+Brake+Booster architecture", na_arch[(405, 435, 466, 498)] == 117)
    check("NA FRC+EMPS+Brake architecture", na_arch[(405, 435, 498)] == 98)
    check("NA FRC+EMPS architecture", na_arch[(405, 498)] == 36)
    check("NA 498+499 cooccurrence is only four MAC rows", na_arch[(405, 418, 430, 435, 466, 476, 477, 498, 499)] == 4)

    pcs = stored["pcs_data_viewer"]
    check("PCS Data Viewer version pinned", pcs["version"] == "12.00.005")
    check(
        "PCS Data Viewer has large explicit TSS3 recorder dictionary",
        pcs["tss3_resource_key_counts"]
        == {
            "FFD_TSS3_ID_": 1131,
            "FFD_TSS3_TRIGGER_ID_": 49,
            "IMGFFD_TSS3_ID_": 13,
            "IMGFFD_TSS3_TRIGGER_ID_": 18,
            "INFO_FCMIMGFFD_TSS3_": 14,
            "INFO_TSS3FFD_": 19,
        },
    )
    check("PCS viewer names lateral target report", "get_REPORT_LATERAL_POSITION_FOR_CONTROL_TARGET" in pcs["report_accessors"])
    check("PCS resources name target steering angle", "Advanced Drive Control Target Steering Angle Order Value [rad]" in pcs["english_text_witnesses"])

    tse = stored["tse_converter"]
    check("TSE converter version pinned", tse["version"] == "01.02.002")
    check("TSE converter exposes ring-buffer signal parser", "GetRingBuffData_SignalDataList" in tse["converter_symbols"] and "ParseRingBuffer" in tse["ring_buffer_symbols"])
    check("all three TSE templates retained", len(tse["sources"]["templates"]) == 3)
    check("TSE templates name PCS time-series FFD", "PCS時系列作動時FFD" in tse["template_section_translations"])

    p6 = stored["adcu_p6_successor_surface"]
    check("ADCU_P6 successor identity", p6["category"] == {"category_id": 6037, "database": "ADCU_P6.ddb", "generation": 22, "name": "ADAS Domain Controller", "short_name": ""})
    check("ADCU_P6 monitor/RoB/DDR scale", p6["selected_table_census"]["62"]["record_count"] == 1647 and p6["selected_table_census"]["164"]["record_count"] == 717 and p6["selected_table_census"]["167"]["record_count"] == 1797)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
