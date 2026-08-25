#!/usr/bin/env python3
"""Verify the firmware-derived Corolla H/F steering-limit ledger."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/corolla_hf_steering_limits.json"
BUILDER = ROOT / "tools/build_corolla_hf_steering_limits.py"
PANDA = ROOT / "data/generated/corolla_hf_panda_lateral_safety_contract.json"

passed = 0
failed = 0


def check(name: str, cond: bool) -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name}")


d = json.loads(ART.read_text())
check("schema", d["schema"] == "corolla-hf-steering-limits-v1")
check("applies to exact H/F pair", d["applies_to"] == ["8965H1202000", "8965F1208000"])
check("artifact is non-enabling", not d["status"]["production_enable_authorized"] and not d["static_conclusion"]["production_enable_authorized"])
check("promoted functions transfer exactly H/F", d["cross_variant"]["all_promoted_function_bodies_h_f_identical"])
check("promoted calibration bytes transfer exactly H/F", d["cross_variant"]["all_promoted_calibration_bytes_h_f_identical"])
check("runtime selected bank is low vehicle", "0x12960" in d["cross_variant"]["runtime_selected_bank"] and "selector 1" in d["cross_variant"]["runtime_selected_bank"])
check("compiled default bank is high", "0x1A960" in d["cross_variant"]["compiled_default_bank"])

c = d["command_limits"]
check("hard LTA absolute raw limit", c["b6_lta_absolute"]["raw"] == 1745 and c["b6_lta_absolute"]["bank_invariant"])
check("hard LTA absolute physical limit", 99.99 < c["b6_lta_absolute"]["deg"] < 100.0)
check("target delta exact", c["b6_lta_delta"]["raw_per_effective_sequence_gap"] == 78)
check("target delta physical", 4.46 < c["b6_lta_delta"]["deg_per_effective_sequence_gap"] < 4.48)
check("target low-angle deadband exact", c["b6_lta_delta"]["low_angle_deadband_raw"] == 87)
check("low selected per-task slew exact", c["internal_lta_slew"]["selected_low_doubled_domain_per_steering_task"] == 7 and c["internal_lta_slew"]["selected_low_b6_counts_per_task"] == 3.5)
check("high default per-task slew exact", c["internal_lta_slew"]["high_default_doubled_domain_per_steering_task"] == 4 and c["internal_lta_slew"]["high_default_b6_counts_per_task"] == 2.0)
check("per-task slew not fabricated into deg/s", c["internal_lta_slew"]["wall_clock_deg_per_second"] is None)
check("doubled target clamp equals B6 envelope", c["doubled_domain_absolute_clamp"]["raw_internal"] == 3490 and c["doubled_domain_absolute_clamp"]["equivalent_b6_raw"] == 1745.0)
check("measured rate violation is strictly above 100", c["measured_steering_rate"]["raw_abs_threshold"] == 100 and c["measured_steering_rate"]["violation_relation"] == "abs(rate_raw) > 100")
check("rate persistence bank split", c["measured_steering_rate"]["selected_low_persistence_cycles"] == 79 and c["measured_steering_rate"]["high_default_persistence_cycles"] == 63)

m = d["indexed_compensation"]
check("CBFCE map input remains physically unnamed", m["index_input"] == "FEBEADF4" and m["index_physical_identity"] is None)
check("four profile compensation maps recovered", len(m["maps"]) == 4 and [x["offset"] for x in m["maps"]] == ["0x768", "0x798", "0x7C8", "0x7F8"])
check("selected vehicle compensation maps all zero at real points", all(x["selected_low_all_real_values_zero"] for x in m["maps"]))
check("high default maps become nonzero at axis 7680", all(x["high_default_first_nonzero_axis"] == 7680 for x in m["maps"]))
check("speed-dependent hard angle reduction not claimed", not d["static_conclusion"]["speed_dependent_hard_angle_reduction_recovered"] and "not a max-angle curve" in m["safety_conclusion"])
check("ADF4 is not mislabeled SP1", "does not claim FEBEADF4 is SP1" in m["boundary"])

p = d["internal_plausibility_and_fault_thresholds"]
check("tracking consistency raw window", p["tracking_consistency"]["half_window_internal"] == 524 and p["tracking_consistency"]["full_comparison_window_internal"] == 1048 and p["tracking_consistency"]["persistence_cycles"] == 40)
check("tracking physical units bounded", p["tracking_consistency"]["physical_units"] is None)
check("instant internal-command threshold", p["internal_command_instant_monitor"]["lta_threshold_raw"] == 512)
check("instant internal-command persistence split", p["internal_command_instant_monitor"]["selected_low_persistence_cycles"] == 79 and p["internal_command_instant_monitor"]["high_default_persistence_cycles"] == 59)
check("instant monitor explicitly not Q current", p["internal_command_instant_monitor"]["not_measured_q_current"])
check("persistent internal-command threshold", p["internal_command_persistent_inhibit"]["lta_threshold_raw"] == 1280 and p["internal_command_persistent_inhibit"]["persistence_cycles"] == 96)
check("persistent monitor explicitly not Q current", p["internal_command_persistent_inhibit"]["not_measured_q_current"])
check("reconstruction validity bounds exact", p["reconstruction_validity_bounds"]["raw_bounds"] == [80, 90, 512] and p["reconstruction_validity_bounds"]["physical_units"] is None)
check("extended inhibit counter exact", p["extended_inhibit_counter"]["threshold"] == 15 and p["extended_inhibit_counter"]["wall_clock_duration"] is None)
check("controller error is saturation not Panda rejection", p["controller_error_saturation"]["raw_internal"] == 18000 and "not Panda" in p["controller_error_saturation"]["classification"])
check("torque sensor fault constants retained raw", p["torque_sensor_fault_calibration"]["raw_constants"] == {"0x0002B538": 2655, "0x0002B53C": 4233, "0x0002B546": 4091, "0x0002B548": 3341, "0x0002B54C": 1764})
check("torque sensor fault constants not promoted to override", not p["torque_sensor_fault_calibration"]["physical_driver_override_semantics"])

t = d["driver_torque"]
check("driver torque acquisition clamp exact", t["acquisition_clamp_raw"] == 2109 and t["acquisition_raw_units_per_nm"] == 256)
check("driver torque acquisition clamp physical", abs(t["acquisition_clamp_abs_nm"] - 8.23828125) < 1e-9)
check("driver torque telemetry saturation exact", t["telemetry_saturation_abs_centi_nm"] == 1000 and t["telemetry_saturation_abs_nm"] == 10.0)
check("driver torque override remains unset", t["override_abs_threshold_nm"] is None and not t["supervisor_numeric_override_comparator_recovered"])
check("torque clamps explicitly not override", "not driver-override thresholds" in t["safety_boundary"])

q = d["motor_q_current"]
check("Q current physical observable closed", "Motor Actual Current (Q Axis)" in q["observable"] and "-0.01 A/count" in q["observable"])
check("Q direct-reference census exact", q["direct_reference_matches"] == ["0x00046C4C", "0x0005722E"])
check("no cooperative Q-current response threshold invented", q["cooperative_supervisor_numeric_response_threshold"] is None and not q["cooperative_supervisor_measured_q_comparator_recovered"])
check("internal command monitors not Q current", not q["internal_monitors_are_q_current"] and "FEBEAE16" in q["safety_boundary"])
check("Q negative remains census-bounded", "exact-substring census" in q["census_boundary"] and "computed-pointer" in q["census_boundary"])

r = d["remaining_policy"]
check("remaining driver override policy open", r["driver_override_abs_nm"] is None)
check("temporary/permanent fault mapping open", r["temporary_vs_permanent_fault_mapping"] is None)
check("actuator response now deliberate policy, not fake OEM threshold", "no OEM measured-Q comparator recovered" in r["actuator_response_policy"])

s = d["static_conclusion"]
check("core steering limits closed", s["absolute_angle_limit_closed"] and s["per_frame_delta_limit_closed"] and s["measured_rate_limit_closed"])
check("slew closed only per task", s["per_task_slew_closed_wall_clock_rate_open"])
check("driver torque policy boundary preserved", s["driver_torque_observable_closed_override_threshold_open"])
check("Q observable/threshold boundary preserved", s["measured_q_observable_closed_oem_response_threshold_not_recovered"])

# Once the Panda contract is updated, it must remain consistent with this ledger.
if PANDA.exists():
    pd = json.loads(PANDA.read_text())
    check("Panda remains non-enabling", not pd["status"]["panda_safety_enable_authorized"])
    check("Panda hard target agrees", pd["eps_hard_envelope"]["lta_target_abs_max_raw"] == c["b6_lta_absolute"]["raw"])
    check("Panda driver override still null", pd["unresolved_safety_parameters"]["driver_override_abs_nm"]["value"] is None)
else:
    check("Panda artifact exists", False)

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td) / "limits.json"
    subprocess.run([sys.executable, str(BUILDER), "--out", str(tmp)], cwd=ROOT, check=True, capture_output=True, text=True)
    check("builder reproduces committed artifact byte-for-byte", tmp.read_bytes() == ART.read_bytes())

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
