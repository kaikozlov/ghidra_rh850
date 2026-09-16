#!/usr/bin/env python3
"""Verify the exact cross-variant TSS3 resident-control ingress matrix."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/variants/analyze_tss3_resident_control_ingress.py"
ARTIFACT = ROOT / "data/generated/tss3_resident_control_ingress_matrix.json"


def check(label: str, condition: object) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[PASS] {label}")


with tempfile.TemporaryDirectory(prefix="verify-tss3-ingress-") as td:
    regen = Path(td) / "matrix.json"
    subprocess.run(
        [sys.executable, str(ANALYZER), "--output", str(regen)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    check("ingress matrix regenerates byte-exact", regen.read_bytes() == ARTIFACT.read_bytes())
    data = json.loads(regen.read_text(encoding="utf-8"))

check("matrix schema", data["schema"] == "toyota-tss3-resident-control-ingress-matrix-v1")
expected = {
    "camry-8965F3307000": ("0xFEBE5751", True, "0xFEBE4C34"),
    "corolla-8965H1202000": ("0xFEBE563D", True, "0xFEBE4B20"),
    "corolla-8965F1208000": ("0xFEBE563D", True, "0xFEBE4B20"),
    "crown-8965F3012000": ("0xFEBE527D", False, None),
}
for name, (functional_buffer, xcp_enabled, xcp_staging) in expected.items():
    target = data["targets"][name]
    functional = target["functional_diagnostic_ingress"]
    xcp = target["dedicated_xcp_ingress"]
    check(f"{name}: stock functional diagnostic route",
          functional["can_id"] == "0x777" and
          functional["cantp_rx_pdu"] == "0x0805" and functional["pdur_rx_pdu"] == "0x0803" and
          functional["functional_dcm_buffer"] == functional_buffer and
          functional["dcm_upper_pdu_ids"] == [2, 3, 4] and functional["dcm_request_types"] == [0, 1, 0])
    check(f"{name}: C6/C7 use unsupported-functional-service behavior",
          functional["functional_service_ids"] == ["0x10", "0x14", "0x28", "0x31", "0x3E", "0x85"] and
          functional["c6_configured"] is False and functional["c7_configured"] is False and
          functional["unsupported_service_nrc"] == "0x11" and functional["functional_nrc11_suppressed"] is True and
          functional["wire"]["loader"] == "07 C6 C6 index word_le32" and
          functional["wire"]["runtime"] == "07 C7 C7 seq target_hi target_lo 00 00" and
          "durable tail" in functional["wire"]["tag_policy"])
    check(f"{name}: dedicated family5 disposition",
          xcp["enabled"] is xcp_enabled and xcp["staging"] == xcp_staging)
    if xcp_enabled:
        check(f"{name}: dedicated XCP/C7 config exact",
              xcp["family_routes"] == [0, 255, 2, 255, 255, 4] and
              xcp["family_counts"] == [5, 0, 4, 0, 0, 1] and
              xcp["request"] == "0x1FDC0002" and xcp["response"] == "0x1FE00002" and
              xcp["request_word_occurrences"] == 2 and xcp["response_word_occurrences"] == 1)
    else:
        check(f"{name}: dedicated XCP/C7 config absent",
              xcp["family_routes"] == [0, 255, 2, 255, 255, 255] and
              xcp["family_counts"] == [5, 0, 4, 0, 0, 0] and
              xcp["request_word_occurrences"] == 0 and xcp["response_word_occurrences"] == 0)

cross = data["cross_variant"]
check("functional 0x777 fallback is common to all four exact targets",
      cross["functional_0x777_present_all"] is True and
      cross["functional_service_set_identical"] is True and
      cross["c6_c7_unconfigured_all"] is True and cross["functional_nrc11_suppressed_all"] is True)
check("only Crown lacks the dedicated family5 carrier",
      cross["dedicated_xcp_disabled"] == ["crown-8965F3012000"] and
      set(cross["dedicated_xcp_enabled"]) == {
          "camry-8965F3307000", "corolla-8965H1202000", "corolla-8965F1208000"
      })
check("Corolla H/F diagnostic transport implementation remains byte-identical",
      all(row["identical"] for row in cross["corolla_hf_diagnostic_functions_byte_identical"]))

print("TSS3 resident-control ingress matrix verification passed.")
