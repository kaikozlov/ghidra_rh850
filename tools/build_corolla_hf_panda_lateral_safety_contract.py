#!/usr/bin/env python3
"""Build a non-enabling Panda lateral-safety candidate for Corolla H/F.

The contract intentionally separates three things:
  * the exact EPS receiver envelope recovered from H/F firmware;
  * a stricter Panda policy for a future openpilot LTA sender; and
  * unresolved/deployment inputs that keep the policy disabled today.

No Sienna constants are used.  H and F raw CodeFlash are checked directly for every
function/calibration byte used by the contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
H_CODE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
F_CODE = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
DECOMP = REPO / "data/generated/corolla_8965H1202000_panda_lateral_safety_decompiler_evidence.json"
RECEIVER = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
FULL_RECEIVER = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_contract.json"
TARGET = REPO / "data/generated/corolla_8965H1202000_b6_target_angle_ingress.json"
STATE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
CAL_DELTA = REPO / "data/generated/corolla_8965F1208000_low_calibration_delta.json"
LIMITS = REPO / "data/generated/corolla_hf_steering_limits.json"
DEFAULT_OUTPUT = REPO / "data/generated/corolla_hf_panda_lateral_safety_contract.json"

FUNCTION_WINDOWS = {
    0xC9CEA: (198, "request-profile target limit selection"),
    0xC9DB0: (164, "signed16 B6 target ingress and doubled-domain saturation"),
    0xC9E54: (124, "profile-specific target slew and absolute clamp"),
    0xCB14E: (122, "additional target/measured tracking validity gate"),
    0xCB22E: (24, "target/internal-response plausibility aggregate"),
    0xCB246: (76, "application sequence gap reconstruction"),
    0xCB2E0: (180, "measured steering-rate plausibility monitor"),
    0xCB394: (180, "internal command-derived magnitude/debounce monitor"),
    0xCB46E: (134, "request-profile target plausibility threshold selection"),
    0xCB4F4: (142, "target magnitude/delta plausibility monitor"),
    0xCB59A: (202, "internal command-derived persistent inhibit monitor"),
    0xCBD7E: (240, "measured angle/rate supervisory reconstruction"),
    0xCBE6E: (128, "Target Lateral ID request decoder"),
    0xCADE4: (52, "cooperative-control inhibit gate"),
    0xCAE18: (88, "cooperative-control inhibit gate"),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def loadj(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr)[0]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO))


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def build() -> dict[str, Any]:
    h = H_CODE.read_bytes()
    f = F_CODE.read_bytes()
    decomp = loadj(DECOMP)
    receiver = loadj(RECEIVER)
    full = loadj(FULL_RECEIVER)
    target = loadj(TARGET)
    state = loadj(STATE)
    cal_delta = loadj(CAL_DELTA)
    limits = loadj(LIMITS)

    need(decomp["software_id"] == "8965H1202000", "wrong H decompiler evidence")
    need(receiver["software_id"] == "8965H1202000", "wrong receiver contract")
    need(target["software_id"] == "8965H1202000", "wrong target-angle contract")
    need(full["applies_to"] == ["8965H1202000", "8965F1208000"] and full["cross_variant"]["h_f_application_identical"],
         "full receiver contract does not transfer to F")
    need(limits["schema"] == "corolla-hf-steering-limits-v1" and limits["applies_to"] == ["8965H1202000", "8965F1208000"],
         "wrong steering-limit ledger")
    need(not limits["status"]["production_enable_authorized"], "steering-limit ledger unexpectedly enables output")

    decomp_by_entry = {int(row["entry"], 16): row for row in decomp["functions"]}
    function_evidence: list[dict[str, Any]] = []
    for addr, (size, role) in FUNCTION_WINDOWS.items():
        row = decomp_by_entry.get(addr)
        need(row is not None, f"missing H decompiler evidence for {addr:#x}")
        need(row["body_size"] == size, f"unexpected H body size at {addr:#x}")
        h_body = h[addr:addr + size]
        f_body = f[addr:addr + size]
        need(h_body == f_body, f"H/F safety body differs at {addr:#x}")
        need(sha256_bytes(h_body) == row["body_sha256"], f"raw/decompiler body hash mismatch at {addr:#x}")
        function_evidence.append({
            "entry": f"0x{addr:08X}",
            "body_size": size,
            "body_sha256": row["body_sha256"],
            "h_f_byte_identical": True,
            "role": role,
        })

    # Both calibration banks are selected by the same firmware code.  Retained
    # runtime captures selected the low/vehicle bank, but the safety-critical LTA
    # magnitude/delta thresholds are invariant across low and high/default banks.
    low = 0x12960
    high = 0x1A960
    bank_fields = {
        "lta_abs_target_raw": 0x14,
        "lta_delta_raw_per_effective_gap": 0x16,
        "lda_abs_target_raw": 0x10,
        "lda_delta_raw_per_effective_gap": 0x12,
        "pda_abs_target_raw": 0x18,
        "pda_delta_raw_per_effective_gap": 0x1A,
        "lta_internal_slew_doubled_domain": 0x2C,
        "lda_internal_slew_doubled_domain": 0x2A,
        "hands_off_lta_internal_slew_doubled_domain": 0x2E,
        "pda_internal_slew_doubled_domain": 0x30,
        "measured_rate_lta_raw": 0x00,  # overridden below; threshold is global AFD00
    }
    low_values = {name: u16(h, low + off) for name, off in bank_fields.items() if name != "measured_rate_lta_raw"}
    high_values = {name: u16(h, high + off) for name, off in bank_fields.items() if name != "measured_rate_lta_raw"}
    for base in (low, high):
        for name, off in bank_fields.items():
            if name == "measured_rate_lta_raw":
                continue
            need(u16(h, base + off) == u16(f, base + off), f"H/F calibration differs: {name} bank {base:#x}")

    global_values = {
        "target_delta_deadband_raw": u16(h, 0xAFCE4),
        "sequence_wrap_max": u16(h, 0xAFCE8),
        "sequence_gap_cap": u16(h, 0xAFCEA),
        "measured_rate_lda_raw": u16(h, 0xAFCFE),
        "measured_rate_lta_raw": u16(h, 0xAFD00),
        "measured_rate_pda_raw": u16(h, 0xAFD02),
        "controller_error_clamp_internal": u16(h, 0xAFC34),
        "wide_target_conditioner_abs_internal": u16(h, 0xAFBAC),
        "wide_target_conditioner_step_internal": u16(h, 0xAFBAE),
    }
    for addr in (0xAFCE4, 0xAFCE8, 0xAFCEA, 0xAFCFE, 0xAFD00, 0xAFD02, 0xAFC34, 0xAFBAC, 0xAFBAE):
        need(u16(h, addr) == u16(f, addr), f"H/F global safety calibration differs at {addr:#x}")

    need(low_values["lta_abs_target_raw"] == 1745, "unexpected LTA max target")
    need(high_values["lta_abs_target_raw"] == 1745, "unexpected high-bank LTA max target")
    need(low_values["lta_delta_raw_per_effective_gap"] == high_values["lta_delta_raw_per_effective_gap"] == 78,
         "unexpected LTA delta threshold")
    need(global_values["target_delta_deadband_raw"] == 87, "unexpected target delta deadband")
    need(global_values["sequence_wrap_max"] == 63 and global_values["sequence_gap_cap"] == 8,
         "unexpected sequence geometry")
    need(global_values["measured_rate_lta_raw"] == 100, "unexpected LTA measured-rate threshold")
    need(limits["command_limits"]["b6_lta_absolute"]["raw"] == low_values["lta_abs_target_raw"], "steering-limit absolute target mismatch")
    need(limits["command_limits"]["b6_lta_delta"]["raw_per_effective_sequence_gap"] == low_values["lta_delta_raw_per_effective_gap"], "steering-limit delta mismatch")
    need(limits["command_limits"]["measured_steering_rate"]["raw_abs_threshold"] == global_values["measured_rate_lta_raw"], "steering-limit rate mismatch")

    accepted = receiver["request_contract"]["accepted_active_requests"]
    need(accepted == {"1": "PCS", "4": "LDA", "10": "Hands Off LTA", "11": "LTA/LCA", "19": "PDA"},
         "unexpected Target Lateral ID dictionary")
    seq = receiver["companion_fields"]["261"]
    loss = receiver["communication_supervision"]["deadline_expiry"]
    need(seq["modulus"] == 64 and seq["gap_cap"] == 8, "unexpected receiver sequence contract")
    need(loss["primary_cutout_after_foreground_ticks"] == 7 and loss["absolute_time_supported"] and loss["nominal_primary_cutout_ms"] == 35.0,
         "unexpected B6 loss contract")

    scale = float(target["scaling"]["controller_equivalent_deg_per_b6_count"])
    exact_scale = target["scaling"]["controller_equivalent_fraction_deg_per_b6_count"]
    need(exact_scale == {"numerator": 1024, "denominator": 17870}, "unexpected B6 physical scale")

    max_raw = low_values["lta_abs_target_raw"]
    delta_raw = low_values["lta_delta_raw_per_effective_gap"]
    deadband_raw = global_values["target_delta_deadband_raw"]

    bridge30 = state["state_bridge"]["0x030"]
    need(bridge30["driver_torque_encoding_family"]["physical_reconstruction"].startswith("Steering Wheel Torque [N.m]"),
         "driver-torque physical reconstruction not closed")
    need(state["carstate_and_panda_input_closure"]["driver_torque_validity"].startswith("closed on live 0x030"),
         "driver-torque validity gate not closed")

    cal_sem = cal_delta["low_shadow_bank"]["calibration_bank_selection"]
    need("selector 1 = programmable low/vehicle twin" in cal_sem["selector_semantics"], "calibration selector semantics drift")
    need("selected the specimen-specific low calibration bank" in cal_sem["runtime_proof"], "runtime low-bank proof drift")

    return {
        "schema": "corolla-hf-panda-lateral-safety-contract-v1",
        "status": {
            "classification": "candidate-non-enabling",
            "panda_safety_enable_authorized": False,
            "reason": (
                "The H/F receiver-side command envelope and observable steering inputs are sufficiently closed to write a candidate safety contract, "
                "but the physical driver-override threshold, extended fault policy, deliberate actuator-response policy, relay-side stock-source suppression, and sender payload/cadence/authentication integration are not yet validated. Firmware recovery found no measured-Q-current comparator in the cooperative B6 supervisor."
            ),
        },
        "sources": {
            "h_codeflash": {"path": rel(H_CODE), "sha256": sha256_file(H_CODE)},
            "f_codeflash": {"path": rel(F_CODE), "sha256": sha256_file(F_CODE)},
            "decompiler_evidence": {"path": rel(DECOMP), "sha256": sha256_file(DECOMP)},
            "receiver_contract": {"path": rel(RECEIVER), "sha256": sha256_file(RECEIVER)},
            "full_receiver_contract": {"path": rel(FULL_RECEIVER), "sha256": sha256_file(FULL_RECEIVER)},
            "target_angle_contract": {"path": rel(TARGET), "sha256": sha256_file(TARGET)},
            "state_bridge": {"path": rel(STATE), "sha256": sha256_file(STATE)},
            "steering_limits": {"path": rel(LIMITS), "sha256": sha256_file(LIMITS)},
        },
        "cross_variant": {
            "software_ids": ["8965H1202000", "8965F1208000"],
            "function_windows": function_evidence,
            "all_safety_function_windows_byte_identical": True,
            "all_cited_safety_calibration_bytes_byte_identical": True,
            "runtime_calibration_bank": "low/vehicle 0x12960 in all retained H/Span LocalRAM captures",
            "default_calibration_bank": "high/default 0x1A960",
            "critical_lta_abs_and_delta_limits_bank_invariant": True,
        },
        "wire_command": {
            "can_id": "0x0B6",
            "dlc": 32,
            "secured": True,
            "application_region": "B0..B27",
            "secoc_trailer": "B28..B31",
            "target_lateral_id": {"signal": 254, "wire": "B3[5:0]"},
            "target_angle": {
                "signal": 255,
                "wire": "B4:B5 signed16",
                "controller_equivalent_deg_per_raw_count": scale,
                "exact_scale_fraction_deg": exact_scale,
            },
            "application_sequence": {"signal": 261, "wire": "B7[5:0]", "modulus": 64},
            "secoc_boundary": (
                "Signal261 is application sequence state, not SecOC message8. SecOC authentication/freshness is a sender/transport prerequisite; this Panda contract does not claim to verify ICU-S slot4 or reconstruct CMAC itself."
            ),
        },
        "eps_hard_envelope": {
            "accepted_active_target_lateral_ids": {k: accepted[k] for k in ("1", "4", "10", "11", "19")},
            "inactive_target_lateral_id": 0,
            "inactive_label": receiver["request_contract"]["no_request"]["label"],
            "lta_lca_request_id": 11,
            "lta_target_abs_max_raw": max_raw,
            "lta_target_abs_max_deg": max_raw * scale,
            "target_delta_deadband_raw": deadband_raw,
            "target_delta_deadband_deg": deadband_raw * scale,
            "lta_target_delta_max_raw_per_effective_gap": delta_raw,
            "lta_target_delta_max_deg_per_effective_gap": delta_raw * scale,
            "sequence": {
                "raw_delta": "(current - previous) mod 64",
                "effective_gap": "1 when raw_delta <= 1, otherwise min(raw_delta, 8)",
                "effective_gap_min": 1,
                "effective_gap_max": 8,
                "strict_plus_one_required_by_eps": False,
                "plausibility_relation": "when abs(target) > 87, abs(target - prior_target) <= 78 * effective_gap",
            },
            "communication_loss": {
                "successful_receive_reload_ticks": 7,
                "primary_cutout_after_foreground_ticks": 7,
                "tick_domain": receiver["communication_supervision"]["scheduler"]["tick_source"],
                "wall_clock_duration_known": True,
                "nominal_wall_clock_ms": receiver["communication_supervision"]["deadline_expiry"]["nominal_primary_cutout_ms"],
                "effect": "B6 health goes unhealthy and cooperative request selection is disabled through the recovered health gate",
            },
            "measured_steering_rate_monitor": {
                "source_can_id": "0x025",
                "source_signal": 186,
                "wire": "signed12 B4-area field (existing TSS3 DBC STEER_RATE)",
                "lta_raw_abs_threshold": global_values["measured_rate_lta_raw"],
                "persistent_eps_debounce_cycles_low_bank": u16(h, low + 0x06),
                "persistent_eps_debounce_cycles_high_bank": u16(h, high + 0x06),
                "panda_candidate_action": "cut active command immediately when abs(raw signal186) > 100; do not wait for the EPS persistent debounce",
                "physical_unit_boundary": "Firmware proves the signed12 rate field and raw threshold 100. The current Toyota DBC uses 1 deg/s/count, but the historical DBC comment called the factor TBD; treat 100 deg/s as a prior-art physical interpretation, not a firmware-native unit proof.",
            },
            "internal_target_conditioning": {
                "runtime_low_bank_lta_slew_doubled_domain_per_steering_task": low_values["lta_internal_slew_doubled_domain"],
                "default_high_bank_lta_slew_doubled_domain_per_steering_task": high_values["lta_internal_slew_doubled_domain"],
                "runtime_low_bank_equivalent_b6_raw_counts_per_task": low_values["lta_internal_slew_doubled_domain"] / 2,
                "runtime_low_bank_equivalent_deg_per_task": (low_values["lta_internal_slew_doubled_domain"] / 2) * scale,
                "foreground_tick_nominal_ms": limits["command_limits"]["internal_lta_slew"]["foreground_tick_nominal_ms"],
                "runtime_low_bank_deg_per_second_if_once_per_foreground_tick": limits["command_limits"]["internal_lta_slew"]["selected_low_deg_per_second_if_called_each_foreground_tick"],
                "wall_clock_rate_unconditional": False,
                "reason": "TAUJ0-CH3 is now closed at nominal 5 ms. The deg/s value is still conditional on this conditioner executing exactly once per foreground cycle; enforce the per-call limit as the unconditional firmware fact.",
            },
            "internal_inhibit_chain": {
                "target_plausibility_output": "0xCB4F4 -> FEBEC269; target magnitude/delta violation or internal C268/C263 state can assert it",
                "internal_response_output": "0xCB59A -> FEBEC26B; persistent FEBEAE16 internal-command magnitude monitor, not measured motor Q-current and not directly available as a CAN measurement",
                "aggregate": "0xCB22E sets FEBEC26A = (FEBEC269 == 1) || (FEBEC26B == 1)",
                "additional_gate": "FEBEC245 from 0xCB14E is independently required clear by 0xCADE4/0xCAE18",
                "cooperative_enable_consumers": ["0x000CADE4", "0x000CAE18"],
                "panda_mapping": "Mirror the observable target/rate and 0x030 fault/validity gates now. Do not reinterpret FEBEAE16 thresholds as Q-current response limits; any Panda actuator-response policy must be validated separately from the OEM internal-command monitors.",
            },
            "controller_error_clamp": {
                "internal_abs_limit": global_values["controller_error_clamp_internal"],
                "classification": "controller error saturation, not promoted to a Panda rejection threshold",
            },
        },
        "measured_inputs": {
            "steering_angle": {
                "can_id": "0x025",
                "dlc": 32,
                "coarse_signal": 184,
                "coarse_signed_bits": 12,
                "coarse_deg_per_count": 1.5,
                "fraction_signal": 185,
                "fraction_signed_bits": 4,
                "fraction_deg_per_count": 0.1,
                "physical_relation": "angle_deg = 1.5*signal184 + 0.1*signal185",
            },
            "steering_rate": {
                "can_id": "0x025",
                "signal": 186,
                "signed_bits": 12,
                "raw_lta_abs_cutout_candidate": global_values["measured_rate_lta_raw"],
            },
            "driver_torque": {
                "can_id": "0x030",
                "dlc": 32,
                "physical_relation": "torque_Nm = signed(signal10)*0.1 + signed4(signal31)*0.01",
                "live_span_range_nm": bridge30["driver_torque_encoding_family"]["span_torque_nm"],
                "invalid_gate": "0x030 B6[0] / DRIVER_TORQUE_INVALID must be 0",
                "acquisition_clamp_raw": limits["driver_torque"]["acquisition_clamp_raw"],
                "acquisition_clamp_abs_nm": limits["driver_torque"]["acquisition_clamp_abs_nm"],
                "telemetry_saturation_abs_nm": limits["driver_torque"]["telemetry_saturation_abs_nm"],
                "override_abs_threshold_nm": None,
                "parameter_name": "driver_override_abs_nm",
                "override_policy_source": limits["driver_torque"]["policy_classification"],
                "override_boundary": "The firmware's ~8.238 N.m acquisition clamp and ±10 N.m telemetry saturation are representation limits, not driver-override thresholds. The promoted exact-H census finds no physical-driver-torque comparator in the target-to-motor control cone, so this threshold is a Panda/openpilot policy to choose conservatively and validate dynamically.",
            },
            "steering_fault_inhibit": {
                "can_id": "0x030",
                "wire": "B6[2]",
                "nominal_clear_value": 0,
                "candidate_action": "immediate controls cutout on nonzero",
                "boundary": "Selected steering fault/inhibit aggregate only; not an exhaustive temporary/permanent EPS fault class.",
            },
        },
        "candidate_panda_subset": {
            "enabled": False,
            "scope": "future lateral-only Corolla H/F safety policy; deliberately stricter than the EPS receiver where Panda controls the sender",
            "rx_requirements": [
                "Require valid 0x025 measured angle/rate before allowing an active B6 request.",
                "Require valid 0x030 additive byte-7 rule before using driver torque/fault state.",
                "Require DRIVER_TORQUE_INVALID == 0.",
                "Require STEERING_FAULT_INHIBIT_STATUS == 0.",
                "Require abs(raw 0x025 signal186) <= 100 while steering is active.",
                "Apply parameterized physical driver-override threshold once validated.",
            ],
            "tx_requirements": [
                "Permit TARGET_LATERAL_ID 11 (LTA/LCA) only while controls are allowed; permit ID 0 only as inactive/no-request.",
                "Reject all other EPS-supported request IDs (PCS/LDA/Hands-Off-LTA/PDA) from openpilot even though the EPS accepts them.",
                "Require abs(TARGET_STEERING_ANGLE raw) <= 1745 (~100 deg).",
                "After the first active frame, require application SEQUENCE to advance exactly +1 modulo 64.",
                "For every active +1 sequence step, require abs(target - previous_target) <= 78 raw counts (~4.47 deg); this is stricter than the EPS's gap-aware/deadband behavior.",
                "When controls are not allowed, require Target Lateral ID 0 and target angle 0 for the candidate sender.",
                "Do not treat application SEQUENCE as SecOC freshness; signing/freshness must be supplied by the separate authenticated sender path.",
            ],
            "secondary_b6_fields": {
                "policy": "not an unresolved Panda threshold",
                "boundary": (
                    "Signals258/260/262/263/264/265 now have an EPS-consumer-derived minimal ID11 candidate (258=1, 260=0, 262=0, 263=0, 264=0, 265=0), but cross-ECU effects and stock active-LTA values are not validated. Production TX remains disabled until the candidate/template is validated on the isolated relay-correct topology; safety should whitelist the validated result rather than permit arbitrary values."
                ),
            },
            "sender_lapse": {
                "eps_guarantee": "The EPS primary receiver-loss cutout is 7 foreground ticks.",
                "panda_state_action": "After a host/sender lapse, discard prior sequence/desired-angle history and require a fresh inactive/measurement-aligned reinitialization before permitting active steering again.",
                "milliseconds": receiver["communication_supervision"]["deadline_expiry"]["nominal_primary_cutout_ms"],
            },
        },
        "unresolved_safety_parameters": {
            "driver_override_abs_nm": {
                "value": None,
                "source_available": "live physical 0x030 Steering Wheel Torque",
                "classification": "deliberate-panda-policy-not-unrecovered-oem-comparator",
                "missing_evidence": "choose a conservative openpilot driver-override threshold and validate driver interaction/release behavior dynamically; no Toyota EPS physical-torque authority comparator remains to recover under the promoted census boundary",
            },
            "extended_fault_policy": {
                "value": None,
                "known_immediate_gate": "0x030 STEERING_FAULT_INHIBIT_STATUS != 0 => disable",
                "missing_evidence": "asserted 0x394/Ready/DTC transitions needed to map temporary/permanent or additional inhibit states",
            },
            "actuator_response_fault_threshold": {
                "value": None,
                "classification": "no-recovered-oem-measured-q-current-threshold",
                "source_available": "0x4A3 Q-current response is statically decoded as an observable",
                "static_firmware_result": "No measured-Q-current comparator is recovered in the cooperative B6 supervisor under the promoted exact-symbol census; CB394/CB59A monitor FEBEAE16 internal command state instead.",
                "policy_boundary": "A Panda/sender actuator-response limit may still be desirable, but it must be chosen and validated as a separate safety policy rather than copied from an invented OEM Q-current threshold.",
                "missing_evidence": "relay-correct dynamic command/response behavior needed to validate any future Panda/sender actuator-response policy",
            },
        },
        "deployment_integration_blockers": [
            "Physical Toyota-B CAN0/CAN1 repin and relay-side B6 producer/suppression attribution.",
            "Stock active-LTA B6 sender cadence and validated values/template for secondary application fields.",
            "SecOC sender ownership and approved slot4 MAC/freshness operation; 0x00F closes epoch semantics but does not supply the secret/MAC operation by itself.",
            "Firmware-identified active-LTA capture to validate the candidate envelope against real stock commands before enabling Panda output.",
        ],
        "not_promoted_as_safety_limits": {
            "signed16_wire_range": "too broad; LTA-specific firmware limit is ±1745 raw",
            "wide_target_conditioner": {
                "abs_internal": global_values["wide_target_conditioner_abs_internal"],
                "step_internal": global_values["wide_target_conditioner_step_internal"],
                "reason": "parallel/wider conditioning path is much looser than the LTA-specific plausibility envelope",
            },
            "controller_error_clamp_internal": global_values["controller_error_clamp_internal"],
            "driver_torque_acquisition_and_telemetry_clamps": {
                "acquisition_clamp_abs_nm": limits["driver_torque"]["acquisition_clamp_abs_nm"],
                "telemetry_saturation_abs_nm": limits["driver_torque"]["telemetry_saturation_abs_nm"],
                "reason": "representation limits, not OEM driver-override thresholds",
            },
            "measured_q_current": {
                "reason": "physical Q-current is observable, but no cooperative-supervisor measured-Q comparator is recovered; internal FEBEAE16 thresholds are not Q-current",
            },
            "legacy_toyota_lta_limits": "use only as prior art; do not transplant pre-TSS3 max angle/rate, speed-angle curves, torque, or current thresholds",
        },
        "static_conclusion": {
            "candidate_panda_contract_derived": True,
            "production_enable_authorized": False,
            "core_command_numeric_limits_closed": True,
            "request_policy_closed_for_candidate_lta": True,
            "sequence_policy_closed_for_candidate_lta": True,
            "eps_loss_cutout_closed_in_ticks": True,
            "eps_loss_cutout_nominal_wall_clock_ms": receiver["communication_supervision"]["deadline_expiry"]["nominal_primary_cutout_ms"],
            "measured_angle_input_closed": True,
            "measured_rate_raw_cutout_closed": True,
            "driver_torque_signal_closed": True,
            "driver_override_is_panda_policy_not_eps_static_recovery_blocker": True,
            "selected_fault_inhibit_gate_closed_but_extended_fault_policy_open": True,
            "measured_q_current_observable_closed_but_oem_response_threshold_not_recovered": True,
            "speed_dependent_hard_angle_reduction_not_recovered": True,
            "wall_clock_sender_cadence_open": True,
            "replacement_sender_freshness_policy_closed_independently_of_stock_cadence": True,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()
    out = args.out
    if not out.is_absolute():
        out = REPO / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
