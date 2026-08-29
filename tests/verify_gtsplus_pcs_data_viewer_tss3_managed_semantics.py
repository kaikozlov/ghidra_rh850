#!/usr/bin/env python3
"""Verify recovered PCS Data Viewer TSS3 Operation-FFD semantics artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"
DIAG = REPO / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    data = json.loads(ART.read_text())
    check("schema", data["schema"] == "gtsplus-pcs-data-viewer-tss3-managed-semantics-v1")
    proof = data["recovery_proof"]
    check("PCS MethodDef census", proof["method_def_count"] == 22564)
    check("PCS executable MethodDef census", proof["method_body_rva_count"] == 22447)
    check("all PCS managed method bodies materialized", proof["method_body_materialized_count"] == 22447)
    operation = data["operation_ffd"]
    check("Operation-FFD bit-assignment row census", operation["detail_row_count"] == 1130)
    check("Operation-FFD DID census", operation["did_count"] == 623)
    check("RoB/trigger row census", data["rob_codes"]["row_count"] == 47)
    check("physical conversion formula", operation["physical_value_contract"]["formula"] == "physical = raw * Lsb + Offset")

    rows = {(row["DataID"], row["DataName"]): row for row in operation["detail_rows"]}
    expected = {
        ("5282", "TSS request - lateral ID"): (1, 7, 8, "u", "1", "0", 0),
        ("5282", "TSS request - pinion angle"): (2, 7, 16, "s", "0.001", "0", 3),
        ("5282", "Steering assist gain"): (4, 7, 8, "u", "0.01", "0", 2),
        ("5282", "Damping control gain"): (5, 7, 8, "u", "0.01", "0", 2),
        ("5285", "Arbitration result_lateral ID"): (1, 7, 8, "u", "1", "0", 0),
        ("5531", "LDA Control Request Pinion Angle"): (2, 7, 16, "s", "0.001", "0", 3),
        ("560D", "EPS Pinion Angle"): (4, 7, 16, "s", "0.001", "0", 3),
        ("5631", "LTA Control Request Pinion Angle"): (2, 7, 16, "s", "0.001", "0", 3),
        ("57DE", "Arbitration result Pinion angle"): (1, 7, 16, "s", "0.001", "0", 3),
    }
    for key, values in expected.items():
        row = rows[key]
        actual = (row["BytePosition"], row["BitPosition"], row["BitLength"], row["Type"], row["Lsb"], row["Offset"], row["Point"])
        check(f"{key[0]} {key[1]} byte/bit/scaling contract", actual == values)

    rob = {row["rob_code"]: row for row in data["rob_codes"]["rows"]}
    for code, name, sampling, pre, post in (
        ("209D", "LCS Steer Override", "0.2", 36, 8),
        ("2818", "Steering Angle Speed Threshold Exceeded", "0.4", 10, 11),
        ("2845", "LTA Hands Free Cancel", "1", 3, 7),
        ("240F", "LCA Cancel", "0.2", 20, 5),
    ):
        row = rob[code]
        check(f"RoB {code} definition", (row["DataName"], row["Sampling"], row["PreTriggerNumber"], row["PostTriggerNumber"]) == (name, sampling, pre, post))

    for key in ("protected_exe", "protected_sidecar", "english_resources"):
        src = data["sources"][key]
        path = DIAG / src["path"]
        check(f"{key} source identity", path.stat().st_size == src["size"] and sha256(path) == src["sha256"])

    print("GTS+ PCS Data Viewer recovered TSS3 semantics verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
