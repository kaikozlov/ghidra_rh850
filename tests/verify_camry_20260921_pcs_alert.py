#!/usr/bin/env python3
"""Verify the retained user-reported Camry PCS-alert timeline."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_20260921_pcs_alert.json"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def main() -> int:
    data = json.loads(ART.read_text())
    check("schema", data["schema"] == "camry-20260921-pcs-alert-v2")
    census = data["corpus_census"]
    check("retained rlog census", census["rlog_count"] == 44)
    check("0x5AE census", census["native_5ae_frames"] == 12981 and census["native_5ae_byte2_bit2_asserted"] == 4)
    check("0x5AE assertion is unique to witness segment", census["asserted_files"] == ["00000043--29caa20fbc/00000043--29caa20fbc--12/rlog.zst"])
    check("special request IDs occur only in the witness run", census["special_08a_request_b_counts"] == {"id_33_allocation_3": 12, "id_34_allocation_3": 9})

    event = data["event"]
    check("event identity", (event["route"], event["segment"]) == ("00000043--29caa20fbc", 12))
    check("event timing", (event["start_route_offset_s"], event["end_route_offset_s"], event["duration_s"]) == (752.436552, 752.922597, 0.486045))
    check("two-phase request count", event["request_frame_count"] == 21 and event["request_b_phase_counts"] == {"id_33_allocation_3": 12, "id_34_allocation_3": 9})
    before, first, transition, after = (event[name] for name in ("before", "first", "phase_transition", "after"))
    check("request A remains ACC ID11", all(row["request_a"]["id"] == 11 for row in (before, first, transition, event["last"], after)))
    check("request B enters ID34", before["request_b"]["id"] == 17 and first["request_b"]["id"] == 34)
    check("request B changes ID34 to ID33", transition["request_b"]["id"] == 33 and after["request_b"]["id"] == 17)
    check("stage bits track ID phases", (before["byte3"], before["byte4"], first["byte3"], first["byte4"], transition["byte3"], transition["byte4"], after["byte3"], after["byte4"]) == (0x08, 0x80, 0x0C, 0xC0, 0x08, 0xC0, 0x08, 0x80))
    check("native request enters at -4 m/s2", first["request_a"]["accel_mps2"] == first["request_b"]["accel_mps2"] == -4.0)
    check("request recovers toward -3.8 m/s2", event["acceleration_range_mps2"] == [-4.0, -3.8])

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
    check("first two native PCS frames were blocked", relay["native_special_frames_not_forwarded"] == 2 and all(row["request_b"]["id"] == 34 for row in relay["not_forwarded"]))
    check("stock forwarding resumes after disable", relay["native_special_frames_forwarded"] == 19 and relay["first_native_forwarded"]["offset_from_request_start_ms"] == 33.508)
    check("last host replacement was rejected", relay["first_host_send_after_start"]["offset_from_request_start_ms"] == 15.685 and relay["rejected_host_replacement"]["offset_from_request_start_ms"] == 22.175)

    result = event["brake_vmm_result"]
    check("Brake/VMM result never selects PCS IDs", result["frame_count"] == 17 and result["longitudinal_result_ids"] == [11])
    check("replacement/forward transition avoids request-loss flag", result["request_loss_supervision_asserted_frames"] == 0)
    check("result acceleration remains far from native -4 bound", result["result_accel_range_mps2"] == [-0.427, -0.401])
    check("PCS attribution remains bounded", "does not assign a global semantic name" in data["interpretation"]["boundary"])

    print("Camry 2026-09-21 PCS-alert timeline verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
