#!/usr/bin/env python3
"""Verify the GTS+ P5 ADAS -> P6 ADCU semantic migration artifact."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))

from extract_gtsplus_p5_adas_p6_migration import DEFAULT_OUT, build  # type: ignore


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def monitor_names(section: dict) -> set[str]:
    return {row["name"] for row in section["monitors"]}


def main() -> int:
    tracked = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    rebuilt = build()
    check("artifact regenerates deterministically", rebuilt == tracked)
    check("schema", tracked["schema"] == "gtsplus-p5-adas-p6-migration-v1")

    arch = tracked["install_set_architectures"]
    check("DSSystem P5 is a three-model NA family", arch["428"]["model_count_na"] == 3)
    check("DSSystem P5 has one NA architecture", arch["428"]["architecture_count_na"] == 1)
    ds_arch = arch["428"]["architectures_na"][0]
    check("DSSystem stack models", ds_arch["model_names"] == ["LS500", "LS500h", "MIRAI"])
    check(
        "DSSystem stack includes PCS/radar/sign peers",
        {row["category_id"] for row in ds_arch["categories"]} == {427, 428, 429, 431, 432},
    )
    check("P6 ADCU has production-style NA installs", arch["6037"]["install_row_count_na"] == 24)
    check("P6F ADCU paired family", arch["6537"]["install_row_count_na"] == 20)

    frc = arch["498"]
    check("FRC generation has five NA install architectures", frc["architecture_count_na"] == 5)
    camry_arch = frc["architectures_na"][0]
    check(
        "Camry HV architecture is exactly EPS+ABS+BrakeBooster+FRC",
        {row["category_id"] for row in camry_arch["categories"]} == {405, 435, 466, 498}
        and "Camry HV" in camry_arch["model_names"]
        and camry_arch["install_row_count"] == 117,
    )
    frc_cats = {
        row["category_id"]
        for a in frc["architectures_na"]
        for row in a["categories"]
    }
    check(
        "P5 compute peers are disjoint from every FRC architecture",
        frc_cats.isdisjoint({427, 428, 429, 431, 432}),
    )
    check(
        "non-production FRC architectures are MAC and TEST only",
        [a["model_names"] for a in frc["architectures_na"][3:]] == [["MAC"], ["TEST"]],
    )

    p5 = tracked["p5_databases"]
    pcs2_names = monitor_names(p5["PCS2_P5"])
    for name in ("LPB Request", "PB Request", "PBA Request", "PCS Steering Request", "Warning Brake Request"):
        check(f"PCS2 monitor {name}", name in pcs2_names)
    radar_names = monitor_names(p5["Fr_RadSen_P5"])
    check("radar cruise dirt monitor", "Dirt Detection for Radar Cruise" in radar_names)
    lda_names = monitor_names(p5["LDA_P5"])
    check("legacy LDA hands-off torque observer", "Not Holding Steering Wheel Judgment Status (Torque Sensor)" in lda_names)

    p6 = tracked["adcu_p6_databases"]["ADCU_P6"]
    check("ADCU P6 monitor breadth", p6["monitor_count"] == 1645)
    check("ADCU P6 DTC breadth", len(p6["dtcs"]) == 183)
    check("ADCU P6 routine Active Tests", len(p6["routine_active_tests"]) == 22)
    check("ADCU P6 RoB data-ID breadth", p6["rob_surface"]["rob_data_id_counts"] == {"90": 2045, "151": 2045})
    check("ADCU P6 RoB diagnostic dictionary", len(p6["rob_surface"]["rob_diag_codes"]) == 501)
    check("ADCU P6 DDR data-ID breadth", len(p6["ddr_surface"]["ddr_data_ids"]) == 445)
    check("ADCU P6 DDR freeze-frame breadth", p6["ddr_surface"]["ddr_freeze_frame_count"] == 1797)

    continuity = {row["role"]: row for row in tracked["p6_ecosystem"]["plugin_role_continuity"]}
    check("monitor-list role continuity", continuity["0x05"]["p5_target_dlls"] == ["GetDatMonListP5_DT.dll"])
    check("RoB role continuity", continuity["0xA0"]["p5_target_dlls"] == ["GetRoBP5_DT.dll"])
    check("P6 image-FFD role is new", continuity["0xD2"]["p6_only"])
    check("P6 routine Active-Test role is new", continuity["0xAE"]["p6_only"])

    deps = tracked["module_dependency_graph"]
    for module in ("Brake System Control Module", "Power Steering Control Module", "Steering Angle Sensor Module", 'ECM/PCM "A"'):
        check(f"P5->P6 retained external dependency {module}", module in deps["retained_external_modules"])

    pcs2_join = tracked["concept_migration"]["monitor_name_joins"]["PCS2_P5"]
    renamed = {row["p5_name"]: row["adcu_names"] for row in pcs2_join["renamed_monitor_continuations"]}
    check("LPB request continues into ADCU", renamed["LPB Request"] == ["PCS LPB Request Flag"])
    check("PBA request continues into ADCU", renamed["PBA Request"] == ["PCS PBA Request Flag"])
    check("P6F database payload references P6", tracked["adcu_p6_databases"]["ADCU_P6F"]["payload_reference"] == "ADCU_P6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
