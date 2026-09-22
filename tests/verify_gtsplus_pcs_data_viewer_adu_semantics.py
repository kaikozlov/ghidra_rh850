#!/usr/bin/env python3
"""Verify recovered PCS Data Viewer ADU recorder semantics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_adu_semantics.json"
DIAG = REPO / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry(row: dict[str, object]) -> tuple[object, ...]:
    return tuple(row[key] for key in ("BytePosition", "BitPosition", "BitLength", "Type", "Lsb", "InvalidValueList"))


def main() -> int:
    data = json.loads(ART.read_text())
    check("schema", data["schema"] == "gtsplus-pcs-data-viewer-adu-semantics-v1")
    check("full managed recovery", data["recovery_proof"] == {
        "method_body_materialized_count": 22447,
        "method_body_rva_count": 22447,
        "method_def_count": 22564,
    })
    adu = data["adu"]
    check("ADU row census", adu["row_count"] == 7851)
    check("ADU DID census", adu["did_count"] == 1369)
    check("physical conversion", adu["physical_value_contract"] == "physical = raw * Lsb + Offset")
    rows = {row["Key"]: row for row in adu["rows"]}

    expected = {
        "2A02_1": ("ADAS required longitudinal ID (lower limit)", (1, 7, 8, "u", "1", [])),
        "2A02_2": ("ADAS required acceleration (lower limit)", (2, 7, 16, "s", "0.001", ["0x7FFF"])),
        "2A02_3": ("ADAS braking/driving force distribution method instruction (lower limit)", (4, 7, 8, "u", "1", [])),
        "2A03_1": ("ADAS required longitudinal ID (upper limit)", (1, 7, 8, "u", "1", [])),
        "2A03_2": ("ADAS required acceleration (upper limit)", (2, 7, 16, "s", "0.001", ["0x7FFF"])),
        "1592_1": ("Arbitration result Longitudinal ID", (1, 7, 8, "u", "1", ["0xFF"])),
        "1592_2": ("Arbitration result Longitudinal ID(Brake)", (2, 7, 8, "u", "1", ["0xFF"])),
        "1592_3": ("Arbitration result Longitudinal ID(Powertrain)", (3, 7, 8, "u", "1", ["0xFF"])),
        "1617": ("Arbitration result_Acceleration valid flag", (1, 7, 8, "u", "1", [])),
        "161D": ("Arbitration result Acceleration", (1, 7, 16, "s", "0.001", ["0x7FFF"])),
        "1F03": ("OAA request vertical ID (upper limit)", (1, 7, 8, "u", "1", [])),
        "15EE": ("Deceleration Request Output Value [m/s^2]", (1, 7, 8, "s", "0.25", ["0x7F"])),
        "1629_9": ("Pressurization status of Automatic brake request", (2, 7, 1, "u", "1", [])),
        "1770_24": ("ACC Target Acceleration (for record)", (28, 7, 8, "s", "0.2", ["0x7F"])),
        "1770_26": ("Automatic Start DDR Detection Signal (for record)", (30, 7, 8, "u", "1", [])),
        "1770_40": ("ACC Requested Acceleration (Lower Limit) (Excluding Jerk Limit) (for record)", (45, 7, 8, "s", "0.2", ["0x7F"])),
    }
    for key, (name, expected_geometry) in expected.items():
        check(f"{key} name and geometry", rows[key]["DataName"] == name and geometry(rows[key]) == expected_geometry)

    longitudinal = data["longitudinal_arbitration"]
    check("aggregate request shapes", len(longitudinal["aggregate_lower_request"]) == 7 and len(longitudinal["aggregate_upper_request"]) == 3)
    pda_lower = {row["resource_key"]: row["name"] for row in longitudinal["pda_da_lower_request_resources"]}
    check("PDA DA is an explicit lower-limit client", pda_lower["FFD_TSS3_ID_5B07"] == "Longitudinal Request ID of Lower Limit from PDA(DA)")
    check("PDA OAA is an explicit upper-limit client", rows["1F03"]["DataName"] == "OAA request vertical ID (upper limit)")

    pcs = data["pcs_pipeline"]
    check("PCS staged surfaces retained", all(pcs[name] for name in ("scene_and_target_judgment", "request_and_output", "enable_and_prohibit", "arbitration_and_actuation")))
    resume = {row["resource_key"]: row["name"] for row in data["stop_resume"]["resume_resources"]}
    check("DDR resume trigger names", resume["DDR_ID_P5_5493"] == "ACC Resume Trigger Signal" and resume["DDR_ID_P5_5494"] == "ACC Resume Trigger Signal")
    check("resume-cancel event names", resume["ADU_TRIGGER_ID_33"] == "ACC cancel after resume" and resume["IMGFFD_TSS3_TRIGGER_ID_33_0"] == "ACC cancel after resume")

    legend = data["request_id_legend_search"]
    check("longitudinal ID field census", legend["longitudinal_or_vertical_id_field_count"] == 24)
    check("no requester-value legend claimed", legend["value_to_client_legend_found"] is False)

    for key in ("protected_exe", "protected_sidecar", "english_resources"):
        source = data["sources"][key]
        path = DIAG / source["path"]
        check(f"{key} source identity", path.stat().st_size == source["size"] and sha256(path) == source["sha256"])

    print("GTS+ PCS Data Viewer recovered ADU semantics verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
