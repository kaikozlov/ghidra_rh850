#!/usr/bin/env python3
"""Verify recovered PCS Data Viewer DDR field semantics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_ddr_semantics.json"
DIAG = REPO / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    data = json.loads(ART.read_text())
    check("schema", data["schema"] == "gtsplus-pcs-data-viewer-ddr-semantics-v1")
    check("full managed recovery", data["recovery_proof"] == {
        "method_body_materialized_count": 22447,
        "method_body_rva_count": 22447,
        "method_def_count": 22564,
    })
    check("DDR row census", data["legacy"]["row_count"] == 284 and data["phase5"]["row_count"] == 1788)
    check("Phase-5 resource census", data["phase5"]["resource_backed_row_count"] == 1786)
    decoder = data["decoder"]
    check("DDR decoder RVAs", (decoder["table_cctor_rva"], decoder["get_value_str_rva"], decoder["convert_detail_value_rva"]) == (0x10A098, 0x159A40, 0x159DE8))
    check("DDR raw mask contract", decoder["raw_contract"] == "read ByteCount bytes; decoded_raw = (raw & BitCount) >> RightShiftCount")
    check("DDR physical contract", decoder["physical_contract"].startswith("physical = decoded_raw * Lsb + Offset"))

    resume = data["stop_resume"]["acc_resume_trigger_signal"]
    check("two separate ACC resume definitions", [row["ResourceKey"] for row in resume] == ["DDR_ID_P5_5493", "DDR_ID_P5_5494"])
    check("ACC resume definitions share OEM name", {row["DataName"] for row in resume} == {"ACC Resume Trigger Signal"})
    check("5493 is mask 0x20 bit 5", (resume[0]["EnumValue"], resume[0]["ByteCount"], resume[0]["BitCount"], resume[0]["RightShiftCount"]) == (1738, 2, 0x20, 5))
    check("5494 is mask 0x01 bit 0", (resume[1]["EnumValue"], resume[1]["ByteCount"], resume[1]["BitCount"], resume[1]["RightShiftCount"]) == (1739, 2, 0x01, 0))
    check("resume fields are unscaled unsigned bits", all((row["Type"], row["Lsb"], row["Offset"], row["InvalidValueList"]) == ("u", "1", "0", []) for row in resume))
    check("resume policy boundary retained", "authorization policy" in data["stop_resume"]["interpretation"])

    for key in ("protected_exe", "protected_sidecar", "english_resources"):
        source = data["sources"][key]
        path = DIAG / source["path"]
        check(f"{key} source identity", path.stat().st_size == source["size"] and sha256(path) == source["sha256"])

    print("GTS+ PCS Data Viewer recovered DDR semantics verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
