#!/usr/bin/env python3
"""Verify the retained user-reported Camry PCS-alert timeline."""
from __future__ import annotations

import json

from tools import REPO_ROOT
from tools.targets.camry.analysis.analyze_camry_20260921_pcs_alert import request_row
ROOT = REPO_ROOT
ART = ROOT / "data/generated/camry_20260921_pcs_alert.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    data = json.loads(ART.read_text())
    census = data["corpus_census"]
    check("retained rlog census", census["rlog_count"] == 44)
    check("0x5AE census", census["native_5ae_frames"] == 12981 and census["native_5ae_byte2_bit2_asserted"] == 4)
    check("0x5AE assertion is unique to witness segment", census["asserted_files"] == ["00000043--29caa20fbc/00000043--29caa20fbc--12/rlog.zst"])
    check("PCS-associated bit occurs only in the witness run",
          census["native_08a_byte4_bit6_asserted"] == 21
          and census["byte4_bit6_asserted_files"] == census["asserted_files"])
    check("every retained native request has a valid prefix checksum",
          census["native_08a_valid_prefix_checksums"] == census["native_08a_frames"])

    event = data["event"]
    check("event identity", (event["route"], event["segment"]) == ("00000043--29caa20fbc", 12))
    check("event timing", (event["start_route_offset_s"], event["end_route_offset_s"], event["duration_s"]) == (752.436552, 752.922597, 0.486045))
    check("two-phase flag count", event["request_frame_count"] == 21 and event["byte3_bit2_phase_counts"] == {"0": 12, "1": 9})
    before, first, transition, after = (event[name] for name in ("before", "first", "phase_transition", "after"))
    check("request A remains ACC ID11", all(row["request_a"]["id"] == 11 for row in (before, first, transition, event["last"], after)))
    check("PCS-associated flag enters and clears",
          not before["byte4_bit6"] and first["byte4_bit6"] and transition["byte4_bit6"] and not after["byte4_bit6"])
    check("byte3 bit2 clears during the event", first["byte3_bit2"] and not transition["byte3_bit2"])
    check("checksum changes with the phase flag", first["byte7_checksum"] == 0x8B and transition["byte7_checksum"] == 0x87)
    check("native acceleration is already -4 m/s2 before flag entry",
          before["request_a"]["accel_mps2"] == before["request_b"]["accel_mps2"]
          == first["request_a"]["accel_mps2"] == first["request_b"]["accel_mps2"] == -4.0)
    check("request recovers toward -3.8 m/s2", event["acceleration_range_mps2"] == [-4.0, -3.8])

    payload = bytearray.fromhex(first["raw"])
    payload[0] += 4
    payload[7] += 4
    changed_header = request_row(0, bytes(payload))
    check("PCS-associated flag is independent of the former checksum-derived IDs",
          changed_header["byte4_bit6"] and changed_header["byte7_checksum_valid"])
    payload[7] ^= 1
    check("prefix checksum corruption is detected", not request_row(0, bytes(payload))["byte7_checksum_valid"])
    payload = bytearray.fromhex(first["raw"])
    payload[4] &= ~0x40
    payload[0] += 0x40
    unflagged = request_row(0, bytes(payload))
    check("the same valid checksum does not imply a PCS-associated flag",
          unflagged["byte7_checksum_valid"] and not unflagged["byte4_bit6"])
    payload = bytearray.fromhex(first["raw"])
    payload[31] ^= 1
    check("the prefix checksum excludes the security trailer", request_row(0, bytes(payload))["byte7_checksum_valid"])

    state = event["state_at_start"]
    check("event starts before driver braking", not state["car_state"]["brake_pressed"] and not state["car_state"]["gas_pressed"])
    check("openpilot was active but requested less deceleration", state["car_control"]["long_active"] and state["car_control"]["requested_accel_mps2"] == -1.5)
    check("driver brake follows native transition", event["first_driver_brake"]["after_event_start_ms"] == 16.733)
    check("openpilot disables on pedal", event["first_selfdrive_disabled"]["after_event_start_ms"] == 19.717 and event["first_selfdrive_disabled"]["alert_type"] == "pedalPressed/userDisable")
    f5ae = event["frc_5ae"]
    check("0x5AE corroborates on exact entry", len(f5ae["asserted_frames"]) == 4 and f5ae["first_assertion_offset_from_request_start_ms"] == 0.0)
    check("0x5AE asserted bit is byte2 bit2", all(row["byte2"] & 0x04 for row in f5ae["asserted_frames"]))
    check("separate 0x5AE alert carrier is forwarded immediately", f5ae["asserted_frames_forwarded_to_bus0"] == 4 and f5ae["first_forward_offset_from_request_start_ms"] == 0.0)

    relay = event["relay_timeline"]
    check("active replacement was last accepted before entry", relay["last_accepted_host_replacement_before_start"]["offset_from_request_start_ms"] == -7.941)
    check("first two native PCS-associated frames were blocked",
          relay["native_special_frames_not_forwarded"] == 2 and all(row["byte4_bit6"] for row in relay["not_forwarded"]))
    check("stock forwarding resumes after disable", relay["native_special_frames_forwarded"] == 19 and relay["first_native_forwarded"]["offset_from_request_start_ms"] == 33.508)
    check("last host replacement was rejected", relay["first_host_send_after_start"]["offset_from_request_start_ms"] == 15.685 and relay["rejected_host_replacement"]["offset_from_request_start_ms"] == 22.175)

    result = event["brake_vmm_result"]
    check("Brake/VMM longitudinal result remains ID11", result["frame_count"] == 17 and result["longitudinal_result_ids"] == [11])
    check("replacement/forward transition avoids request-loss flag", result["request_loss_supervision_asserted_frames"] == 0)
    check("closed-accelerator reference range", result["byte20_21_range_mps2"] == [-0.427, -0.401])

    print("Camry 2026-09-21 PCS-alert timeline verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
