#!/usr/bin/env python3
"""Verify the non-enabling Corolla H/F candidate Panda lateral-safety contract."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/corolla_hf_panda_lateral_safety_contract.json"
BUILDER = ROOT / "tools/build_corolla_hf_panda_lateral_safety_contract.py"

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


def candidate_tx_ok(*, controls_allowed: bool, request_id: int, target_raw: int, seq: int,
                    previous_target: int | None, previous_seq: int | None,
                    steer_rate_raw: int, driver_torque_invalid: int = 0,
                    fault_inhibit: int = 0, driver_torque_nm: float = 0.0,
                    driver_override_abs_nm: float | None = None) -> bool:
    """Reference implementation of the deliberately strict policy encoded by the artifact."""
    if driver_torque_invalid != 0 or fault_inhibit != 0:
        return False
    if driver_override_abs_nm is not None and abs(driver_torque_nm) > driver_override_abs_nm:
        return False
    if controls_allowed:
        if request_id != 11 or abs(target_raw) > 1745 or abs(steer_rate_raw) > 100:
            return False
        if previous_seq is not None and seq != ((previous_seq + 1) & 0x3F):
            return False
        if previous_target is not None and abs(target_raw - previous_target) > 78:
            return False
        return True
    return request_id == 0 and target_raw == 0


d = json.loads(ART.read_text())

check("candidate remains explicitly non-enabling", d["status"]["classification"] == "candidate-non-enabling" and not d["status"]["panda_safety_enable_authorized"])
check("production enable remains false", not d["static_conclusion"]["production_enable_authorized"])
check("H/F exact software IDs", d["cross_variant"]["software_ids"] == ["8965H1202000", "8965F1208000"])
check("all cited H/F safety functions byte-identical", d["cross_variant"]["all_safety_function_windows_byte_identical"] and len(d["cross_variant"]["function_windows"]) == 15)
check("all cited H/F safety calibration bytes byte-identical", d["cross_variant"]["all_cited_safety_calibration_bytes_byte_identical"])
check("critical LTA limits bank-invariant", d["cross_variant"]["critical_lta_abs_and_delta_limits_bank_invariant"])

wire = d["wire_command"]
check("B6 wire geometry", wire["can_id"] == "0x0B6" and wire["dlc"] == 32 and wire["secured"])
check("Target Lateral ID geometry", wire["target_lateral_id"] == {"signal": 254, "wire": "B3[5:0]"})
check("target-angle signal geometry", wire["target_angle"]["signal"] == 255 and wire["target_angle"]["wire"] == "B4:B5 signed16")
check("target-angle exact scale", wire["target_angle"]["exact_scale_fraction_deg"] == {"numerator": 1024, "denominator": 17870})
check("application sequence geometry", wire["application_sequence"] == {"signal": 261, "wire": "B7[5:0]", "modulus": 64})
check("application sequence explicitly separate from SecOC", "not SecOC message8" in wire["secoc_boundary"])

e = d["eps_hard_envelope"]
check("EPS accepted request IDs exact", e["accepted_active_target_lateral_ids"] == {"1": "PCS", "4": "LDA", "10": "Hands Off LTA", "11": "LTA/LCA", "19": "PDA"})
check("manual/no-request ID is zero", e["inactive_target_lateral_id"] == 0 and e["lta_lca_request_id"] == 11)
check("LTA absolute raw target limit", e["lta_target_abs_max_raw"] == 1745)
check("LTA absolute physical target is approximately 100 deg", 99.99 < e["lta_target_abs_max_deg"] < 100.0)
check("target delta deadband exact", e["target_delta_deadband_raw"] == 87)
check("target delta threshold exact", e["lta_target_delta_max_raw_per_effective_gap"] == 78)
check("target delta physical threshold approximately 4.47 deg", 4.46 < e["lta_target_delta_max_deg_per_effective_gap"] < 4.48)
check("EPS sequence gap formula and cap", e["sequence"]["effective_gap_min"] == 1 and e["sequence"]["effective_gap_max"] == 8 and not e["sequence"]["strict_plus_one_required_by_eps"])
check("seven-tick B6 receiver cutout", e["communication_loss"]["successful_receive_reload_ticks"] == 7 and e["communication_loss"]["primary_cutout_after_foreground_ticks"] == 7)
check("seven-tick wall clock closed at nominal 35 ms", e["communication_loss"]["wall_clock_duration_known"] and e["communication_loss"]["nominal_wall_clock_ms"] == 35.0)
check("LTA measured steering-rate raw threshold", e["measured_steering_rate_monitor"]["lta_raw_abs_threshold"] == 100)
check("measured-rate persistent debounce remains bank-specific", e["measured_steering_rate_monitor"]["persistent_eps_debounce_cycles_low_bank"] == 79 and e["measured_steering_rate_monitor"]["persistent_eps_debounce_cycles_high_bank"] == 63)
check("per-task target slew retained with conditional 5ms rate", e["internal_target_conditioning"]["runtime_low_bank_lta_slew_doubled_domain_per_steering_task"] == 7 and e["internal_target_conditioning"]["default_high_bank_lta_slew_doubled_domain_per_steering_task"] == 4 and e["internal_target_conditioning"]["foreground_tick_nominal_ms"] == 5.0 and not e["internal_target_conditioning"]["wall_clock_rate_unconditional"] and 40.0 < e["internal_target_conditioning"]["runtime_low_bank_deg_per_second_if_once_per_foreground_tick"] < 40.2)
check("internal target/response inhibit aggregation exact", "FEBEC269" in e["internal_inhibit_chain"]["aggregate"] and "FEBEC26B" in e["internal_inhibit_chain"]["aggregate"] and "FEBEC26A" in e["internal_inhibit_chain"]["aggregate"])
check("additional C245 cooperative gate retained", "FEBEC245" in e["internal_inhibit_chain"]["additional_gate"])
check("controller error saturation not promoted as rejection", e["controller_error_clamp"]["classification"] == "controller error saturation, not promoted to a Panda rejection threshold")

m = d["measured_inputs"]
check("measured angle comes from 0x025 coarse+fraction", m["steering_angle"]["can_id"] == "0x025" and m["steering_angle"]["coarse_signal"] == 184 and m["steering_angle"]["fraction_signal"] == 185)
check("measured angle scales exact", m["steering_angle"]["coarse_deg_per_count"] == 1.5 and m["steering_angle"]["fraction_deg_per_count"] == 0.1)
check("measured rate is signal186", m["steering_rate"]["signal"] == 186 and m["steering_rate"]["signed_bits"] == 12)
check("driver torque source physical and live", m["driver_torque"]["can_id"] == "0x030" and m["driver_torque"]["live_span_range_nm"]["count"] == 6000)
check("driver torque invalid gate is required clear", "must be 0" in m["driver_torque"]["invalid_gate"])
check("driver override numeric threshold deliberately open as Panda policy", m["driver_torque"]["override_abs_threshold_nm"] is None and "Panda/openpilot" in m["driver_torque"]["override_policy_source"])
check("driver torque acquisition clamp is not override", abs(m["driver_torque"]["acquisition_clamp_abs_nm"] - 8.23828125) < 1e-9 and "not driver-override thresholds" in m["driver_torque"]["override_boundary"])
check("driver torque telemetry saturation is not override", m["driver_torque"]["telemetry_saturation_abs_nm"] == 10.0 and "not driver-override thresholds" in m["driver_torque"]["override_boundary"])
check("selected fault/inhibit is immediate cutout candidate", m["steering_fault_inhibit"]["nominal_clear_value"] == 0 and "immediate controls cutout" in m["steering_fault_inhibit"]["candidate_action"])

p = d["candidate_panda_subset"]
check("candidate Panda subset still disabled", not p["enabled"])
check("candidate restricts active request to LTA/LCA", any("ID 11" in x for x in p["tx_requirements"]))
check("candidate rejects other EPS request profiles", any("Reject all other" in x for x in p["tx_requirements"]))
check("candidate requires strict +1 sequence", any("exactly +1 modulo 64" in x for x in p["tx_requirements"]))
check("candidate applies single-step 78-count delta", any("<= 78 raw counts" in x for x in p["tx_requirements"]))
check("candidate inactive command is ID0/target0", any("ID 0 and target angle 0" in x for x in p["tx_requirements"]))
check("secondary B6 values have bounded minimal candidate but still require validation", p["secondary_b6_fields"]["policy"] == "not an unresolved Panda threshold" and "258=1" in p["secondary_b6_fields"]["boundary"] and "cross-ECU" in p["secondary_b6_fields"]["boundary"] and "whitelist" in p["secondary_b6_fields"]["boundary"])
check("sender lapse now records nominal 35 ms EPS cutout", p["sender_lapse"]["milliseconds"] == 35.0)

u = d["unresolved_safety_parameters"]
check("only three bounded safety-policy parameter classes remain", set(u) == {"driver_override_abs_nm", "extended_fault_policy", "actuator_response_fault_threshold"})
check("driver override parameter is intentionally unset policy not OEM recovery", u["driver_override_abs_nm"]["value"] is None and u["driver_override_abs_nm"]["classification"] == "deliberate-panda-policy-not-unrecovered-oem-comparator" and "no Toyota EPS" in u["driver_override_abs_nm"]["missing_evidence"])
check("extended fault policy is intentionally unset with immediate gate known", u["extended_fault_policy"]["value"] is None and "disable" in u["extended_fault_policy"]["known_immediate_gate"])
check("actuator response threshold intentionally unset", u["actuator_response_fault_threshold"]["value"] is None)
check("actuator response is reclassified as no recovered OEM measured-Q threshold", u["actuator_response_fault_threshold"]["classification"] == "no-recovered-oem-measured-q-current-threshold" and "FEBEAE16" in u["actuator_response_fault_threshold"]["static_firmware_result"])
check("future actuator response remains deliberate Panda/sender policy", "separate safety policy" in u["actuator_response_fault_threshold"]["policy_boundary"])
check("deployment blockers remain outside safety math", len(d["deployment_integration_blockers"]) == 4 and any("repin" in x for x in d["deployment_integration_blockers"]))

# Edge behavior for the stricter future Panda subset.
check("reference policy accepts nominal first active LTA", candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=7, previous_target=None, previous_seq=None, steer_rate_raw=20))
check("reference policy accepts wrap +1", candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=110, seq=0, previous_target=100, previous_seq=63, steer_rate_raw=20))
check("reference policy accepts exact max angle", candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=1745, seq=2, previous_target=1700, previous_seq=1, steer_rate_raw=100))
check("reference policy rejects above max angle", not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=1746, seq=2, previous_target=1700, previous_seq=1, steer_rate_raw=20))
check("reference policy rejects non-LTA request", not candidate_tx_ok(controls_allowed=True, request_id=4, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20))
check("reference policy rejects sequence gap tolerated by EPS", not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=110, seq=3, previous_target=100, previous_seq=1, steer_rate_raw=20))
check("reference policy accepts 78-count delta", candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=178, seq=2, previous_target=100, previous_seq=1, steer_rate_raw=20))
check("reference policy rejects 79-count delta", not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=179, seq=2, previous_target=100, previous_seq=1, steer_rate_raw=20))
check("reference policy rejects measured rate 101", not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=101))
check("reference policy rejects torque-invalid gate", not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20, driver_torque_invalid=1))
check("reference policy rejects selected fault gate", not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20, fault_inhibit=1))
check("reference policy supports future driver threshold parameter", not candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20, driver_torque_nm=3.1, driver_override_abs_nm=3.0))
check("reference policy permits exact future driver threshold", candidate_tx_ok(controls_allowed=True, request_id=11, target_raw=100, seq=2, previous_target=90, previous_seq=1, steer_rate_raw=20, driver_torque_nm=-3.0, driver_override_abs_nm=3.0))
check("inactive candidate accepts only zero request/target", candidate_tx_ok(controls_allowed=False, request_id=0, target_raw=0, seq=0, previous_target=None, previous_seq=None, steer_rate_raw=0))
check("inactive candidate rejects stale target", not candidate_tx_ok(controls_allowed=False, request_id=0, target_raw=1, seq=0, previous_target=None, previous_seq=None, steer_rate_raw=0))
check("steering-limit ledger is a tracked Panda input", "steering_limits" in d["sources"] and d["sources"]["steering_limits"]["path"] == "data/generated/corolla_hf_steering_limits.json")
check("Panda does not transplant TSS2 speed-angle/current limits", "speed-angle curves" in d["not_promoted_as_safety_limits"]["legacy_toyota_lta_limits"] and "measured_q_current" in d["not_promoted_as_safety_limits"])
check("static conclusion keeps Q-current OEM threshold negative", d["static_conclusion"]["measured_q_current_observable_closed_but_oem_response_threshold_not_recovered"])
check("static conclusion keeps speed-dependent hard reduction negative", d["static_conclusion"]["speed_dependent_hard_angle_reduction_not_recovered"])
check("static conclusion closes nominal 35ms loss cutout", d["static_conclusion"]["eps_loss_cutout_nominal_wall_clock_ms"] == 35.0)
check("static conclusion reclassifies driver override as Panda policy", d["static_conclusion"]["driver_torque_signal_closed"] and d["static_conclusion"]["driver_override_is_panda_policy_not_eps_static_recovery_blocker"])
check("static conclusion separates stock cadence from replacement freshness", d["static_conclusion"]["wall_clock_sender_cadence_open"] and d["static_conclusion"]["replacement_sender_freshness_policy_closed_independently_of_stock_cadence"])

# The builder must reproduce the committed artifact exactly from tracked evidence.
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td) / "safety.json"
    subprocess.run([sys.executable, str(BUILDER), "--out", str(tmp)], cwd=ROOT, check=True, capture_output=True, text=True)
    check("builder reproduces committed artifact byte-for-byte", tmp.read_bytes() == ART.read_bytes())

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
