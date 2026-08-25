#!/usr/bin/env python3
"""Build the firmware-derived Corolla H/F steering-limit ledger.

This artifact separates command limits that can be enforced by Panda from
controller-internal plausibility/fault thresholds and from observables that do
not have a recovered OEM cooperative-control threshold.  Verification depends
only on tracked CodeFlash/evidence artifacts; the disposable decompiler corpus
used to create the compact evidence is not opened here.
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
DECOMP = REPO / "data/generated/corolla_8965H1202000_steering_limits_decompiler_evidence.json"
CENSUS = REPO / "data/generated/corolla_8965H1202000_steering_limits_reference_census.json"
PANDA_DECOMP = REPO / "data/generated/corolla_8965H1202000_panda_lateral_safety_decompiler_evidence.json"
TARGET = REPO / "data/generated/corolla_8965H1202000_b6_target_angle_ingress.json"
STATE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
CAL_DELTA = REPO / "data/generated/corolla_8965F1208000_low_calibration_delta.json"
DEFAULT_OUTPUT = REPO / "data/generated/corolla_hf_steering_limits.json"

LOW_BANK = 0x12960
HIGH_BANK = 0x1A960
PROFILE_COMP_OFFSETS = (0x768, 0x798, 0x7C8, 0x7F8)


def loadj(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO))


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr)[0]


def s16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<h", blob, addr)[0]


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr)[0]


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def interpolation_points(blob: bytes, addr: int) -> list[dict[str, int]]:
    """Decode CE6A2-style (u16 axis, s16 value) points through 0xffff."""
    out: list[dict[str, int]] = []
    for i in range(32):
        axis = u16(blob, addr + i * 4)
        value = s16(blob, addr + i * 4 + 2)
        out.append({"axis": axis, "value": value})
        if axis == 0xFFFF:
            return out
    raise SystemExit(f"unterminated interpolation table at {addr:#x}")


def validate_decompiler_evidence(blob_h: bytes, blob_f: bytes, evidence: dict[str, Any]) -> dict[int, str]:
    need(evidence["software_id"] == "8965H1202000", "wrong steering-limit decompiler evidence")
    need(evidence["image"]["sha256"] == sha256_bytes(blob_h), "steering-limit evidence image hash drift")
    bodies: dict[int, str] = {}
    for row in evidence["functions"]:
        addr = int(row["entry"], 16)
        size = row["body_size"]
        h_body = blob_h[addr:addr + size]
        f_body = blob_f[addr:addr + size]
        need(sha256_bytes(h_body) == row["body_sha256"], f"H body hash drift at {addr:#x}")
        need(h_body == f_body, f"H/F function body differs at {addr:#x}")
        bodies[addr] = row["decompiled_c"]
    return bodies


def build() -> dict[str, Any]:
    h = H_CODE.read_bytes()
    f = F_CODE.read_bytes()
    decomp = loadj(DECOMP)
    census = loadj(CENSUS)
    panda_decomp = loadj(PANDA_DECOMP)
    target = loadj(TARGET)
    state = loadj(STATE)
    cal_delta = loadj(CAL_DELTA)

    need(len(h) == 0x100000, "unexpected H CodeFlash size")
    need(len(f) >= len(h), "unexpected F CodeFlash size")
    bodies = validate_decompiler_evidence(h, f, decomp)

    # Pin the pre-existing supervisor evidence used for the command/fault limits.
    need(panda_decomp["software_id"] == "8965H1202000", "wrong Panda decompiler evidence")
    supervisor = {int(row["entry"], 16): row for row in panda_decomp["functions"]}
    for addr in (0xC9CEA, 0xC9E54, 0xCB14E, 0xCB2E0, 0xCB394, 0xCB46E, 0xCB4F4, 0xCB59A, 0xCBD7E, 0xCAE18):
        row = supervisor[addr]
        body = h[addr:addr + row["body_size"]]
        need(sha256_bytes(body) == row["body_sha256"], f"supervisor body hash drift at {addr:#x}")
        need(body == f[addr:addr + row["body_size"]], f"H/F supervisor body differs at {addr:#x}")

    # Semantic pins from the newly promoted compact evidence.
    need("DAT_0002cb9e" in bodies[0x4332A] and "-DAT_0002cb9e" in bodies[0x4332A], "torque acquisition clamp decompile drift")
    need("uRamfebe6554 = uRamfebe7b08" in bodies[0x57692], "driver torque snapshot bridge drift")
    need("sRamfebe6554 * 100" in bodies[0x46C4C] and "1000" in bodies[0x46C4C], "driver torque telemetry saturation drift")
    need("uRamfebe6bae" in bodies[0x33160] and "0x7fff" in bodies[0x33160], "Q-current source saturation drift")
    need("uRamfebe6592 = uRamfebe6bae" in bodies[0x5722E], "Q-current snapshot bridge drift")
    need("sRamfebe6592 * -100" in bodies[0x46C4C], "Q-current 0x4A3 conversion drift")
    need("uRamfebeadf4" in bodies[0xCBFCE] and "+ 0x768" in bodies[0xCBFCE] and "+ 0x7f8" in bodies[0xCBFCE], "CBFCE ADF4 map selection drift")
    need("0xffff" in bodies[0xCE6A2] and "puVar1[1]" in bodies[0xCE6A2], "CE6A2 interpolation helper drift")

    # The compact census is promoted evidence: verification does not reopen its
    # ignored source corpus.  Its boundary is deliberately exact-symbol only.
    need(census["software_id"] == "8965H1202000", "wrong steering-limit census")
    need(census["image"]["sha256"] == sha256_bytes(h), "steering-limit census image drift")
    q_refs = census["terms"]["measured_q_current"]
    cmd_refs = census["terms"]["internal_command_state"]
    torque_refs = census["terms"]["driver_torque"]
    need([x["entry"] for x in q_refs["matches"]] == ["0x00046C4C", "0x0005722E"], "measured-Q direct-reference census drift")
    need("0x000CB394" in [x["entry"] for x in cmd_refs["matches"]] and "0x000CB59A" in [x["entry"] for x in cmd_refs["matches"]], "internal-command census drift")
    need([x["entry"] for x in torque_refs["matches"]] == ["0x00046C4C", "0x00057692"], "driver-torque direct-reference census drift")

    need(u32(h, 0xB024C) == HIGH_BANK and u32(h, 0xB0250) == LOW_BANK, "calibration bank pointer order drift")
    need(h[0xB024C:0xB0254] == f[0xB024C:0xB0254], "H/F calibration pointer table differs")
    cal_sem = cal_delta["low_shadow_bank"]["calibration_bank_selection"]
    need("selector 1 = programmable low/vehicle twin" in cal_sem["selector_semantics"], "low/high selector semantics drift")
    need("selected the specimen-specific low calibration bank" in cal_sem["runtime_proof"], "runtime selected-bank proof drift")

    scale = float(target["scaling"]["controller_equivalent_deg_per_b6_count"])
    need(target["scaling"]["controller_equivalent_fraction_deg_per_b6_count"] == {"numerator": 1024, "denominator": 17870}, "target angle scale drift")

    bank = {
        "lta_abs_target_raw": 0x14,
        "lta_delta_raw_per_effective_gap": 0x16,
        "rate_debounce": 0x06,
        "internal_command_debounce": 0x0A,
        "validity_bound_0": 0x20,
        "validity_bound_1": 0x22,
        "validity_bound_2": 0x24,
        "lta_slew_doubled_per_task": 0x2C,
    }
    low_values = {k: u16(h, LOW_BANK + off) for k, off in bank.items()}
    high_values = {k: u16(h, HIGH_BANK + off) for k, off in bank.items()}
    for base in (LOW_BANK, HIGH_BANK):
        for off in bank.values():
            need(h[base + off:base + off + 2] == f[base + off:base + off + 2], f"H/F bank value differs at {base + off:#x}")

    need(low_values["lta_abs_target_raw"] == high_values["lta_abs_target_raw"] == 1745, "LTA absolute target drift")
    need(low_values["lta_delta_raw_per_effective_gap"] == high_values["lta_delta_raw_per_effective_gap"] == 78, "LTA delta drift")
    need(low_values["rate_debounce"] == 79 and high_values["rate_debounce"] == 63, "rate debounce drift")
    need(low_values["internal_command_debounce"] == 79 and high_values["internal_command_debounce"] == 59, "internal-command debounce drift")
    need([low_values[f"validity_bound_{i}"] for i in range(3)] == [80, 90, 512], "low validity bounds drift")
    need([high_values[f"validity_bound_{i}"] for i in range(3)] == [80, 90, 512], "high validity bounds drift")
    need(low_values["lta_slew_doubled_per_task"] == 7 and high_values["lta_slew_doubled_per_task"] == 4, "LTA slew drift")

    globals_u16 = {
        "controller_error_saturation": (0xAFC34, 18000),
        "tracking_half_window": (0xAFCDC, 524),
        "tracking_debounce": (0xAFCE0, 40),
        "extended_inhibit_counter": (0xAFCD4, 15),
        "target_delta_deadband": (0xAFCE4, 87),
        "internal_command_persistent_threshold": (0xAFCEC, 1280),
        "internal_command_persistent_debounce": (0xAFCEE, 96),
        "internal_command_threshold_lta": (0xAFCFA, 512),
        "measured_rate_threshold_lta": (0xAFD00, 100),
        "target_clamp_lda": (0xAFC82, 3490),
        "target_clamp_lta": (0xAFC84, 3490),
        "target_clamp_hands_off": (0xAFC86, 3490),
        "target_clamp_pda": (0xAFC88, 3490),
        "driver_torque_acquisition_clamp_raw": (0x2CB9E, 2109),
    }
    gv: dict[str, int] = {}
    for name, (addr, expected) in globals_u16.items():
        value = u16(h, addr)
        need(value == expected, f"{name} drift: {value}")
        need(value == u16(f, addr), f"H/F {name} differs")
        gv[name] = value

    torque_fault_constants = {
        "0x0002B538": 2655,
        "0x0002B53C": 4233,
        "0x0002B546": 4091,
        "0x0002B548": 3341,
        "0x0002B54C": 1764,
    }
    for a, expected in torque_fault_constants.items():
        addr = int(a, 16)
        need(u16(h, addr) == expected == u16(f, addr), f"torque-sensor fault calibration drift at {a}")

    map_rows: list[dict[str, Any]] = []
    for off in PROFILE_COMP_OFFSETS:
        low_pts = interpolation_points(h, LOW_BANK + off)
        high_pts = interpolation_points(h, HIGH_BANK + off)
        low_len = len(low_pts) * 4
        high_len = len(high_pts) * 4
        need(h[LOW_BANK + off:LOW_BANK + off + low_len] == f[LOW_BANK + off:LOW_BANK + off + low_len], f"H/F low map differs at +{off:#x}")
        need(h[HIGH_BANK + off:HIGH_BANK + off + high_len] == f[HIGH_BANK + off:HIGH_BANK + off + high_len], f"H/F high map differs at +{off:#x}")
        low_real = [p for p in low_pts if p["axis"] != 0xFFFF]
        high_real = [p for p in high_pts if p["axis"] != 0xFFFF]
        need(all(p["value"] == 0 for p in low_real), f"selected-low compensation map +{off:#x} no longer zero")
        need(any(p["value"] != 0 for p in high_real), f"high/default compensation map +{off:#x} unexpectedly all zero")
        first_nonzero = next(p["axis"] for p in high_real if p["value"] != 0)
        need(first_nonzero == 7680, f"high/default compensation first nonzero axis drift at +{off:#x}")
        map_rows.append({
            "offset": f"0x{off:03X}",
            "index_input": "FEBEADF4",
            "selected_low_vehicle_points": low_pts,
            "high_default_points": high_pts,
            "selected_low_all_real_values_zero": True,
            "high_default_first_nonzero_axis": first_nonzero,
            "h_f_byte_identical": True,
        })

    bridge30 = state["state_bridge"]["0x030"]
    bridge4a3 = state["state_bridge"]["0x4A3"]
    need("Steering Wheel Torque [N.m]" in bridge30["driver_torque_encoding_family"]["physical_reconstruction"], "0x030 physical torque bridge drift")
    need(any(x.get("semantic") == "Motor Actual Current (Q Axis)" for x in bridge4a3["fields"]), "0x4A3 Q-current bridge drift")

    torque_clamp_raw = gv["driver_torque_acquisition_clamp_raw"]
    torque_clamp_nm = torque_clamp_raw / 256.0
    lta_abs = low_values["lta_abs_target_raw"]
    lta_delta = low_values["lta_delta_raw_per_effective_gap"]

    return {
        "schema": "corolla-hf-steering-limits-v1",
        "applies_to": ["8965H1202000", "8965F1208000"],
        "status": {
            "classification": "firmware-derived-safety-input-ledger",
            "production_enable_authorized": False,
            "boundary": "Numeric firmware limits are separated from telemetry/acquisition saturation and from unresolved policy. Nothing in this artifact authorizes Panda output.",
        },
        "sources": {
            "h_codeflash": {"path": rel(H_CODE), "sha256": sha256_file(H_CODE)},
            "f_codeflash": {"path": rel(F_CODE), "sha256": sha256_file(F_CODE)},
            "decompiler_evidence": {"path": rel(DECOMP), "sha256": sha256_file(DECOMP)},
            "reference_census": {"path": rel(CENSUS), "sha256": sha256_file(CENSUS)},
            "panda_supervisor_evidence": {"path": rel(PANDA_DECOMP), "sha256": sha256_file(PANDA_DECOMP)},
            "target_angle_contract": {"path": rel(TARGET), "sha256": sha256_file(TARGET)},
            "state_bridge": {"path": rel(STATE), "sha256": sha256_file(STATE)},
            "calibration_bank_evidence": {"path": rel(CAL_DELTA), "sha256": sha256_file(CAL_DELTA)},
        },
        "cross_variant": {
            "all_promoted_function_bodies_h_f_identical": True,
            "all_promoted_calibration_bytes_h_f_identical": True,
            "runtime_selected_bank": "low/vehicle 0x12960 (selector 1 in all retained H/Span runtime captures)",
            "compiled_default_bank": "high/default 0x1A960 (selector 0)",
        },
        "command_limits": {
            "b6_lta_absolute": {
                "raw": lta_abs,
                "deg": lta_abs * scale,
                "bank_invariant": True,
                "classification": "hard LTA/LCA target plausibility limit",
            },
            "b6_lta_delta": {
                "raw_per_effective_sequence_gap": lta_delta,
                "deg_per_effective_sequence_gap": lta_delta * scale,
                "low_angle_deadband_raw": gv["target_delta_deadband"],
                "low_angle_deadband_deg": gv["target_delta_deadband"] * scale,
                "classification": "EPS target-jump plausibility limit",
            },
            "internal_lta_slew": {
                "selected_low_doubled_domain_per_steering_task": low_values["lta_slew_doubled_per_task"],
                "selected_low_b6_counts_per_task": low_values["lta_slew_doubled_per_task"] / 2,
                "selected_low_deg_per_task": (low_values["lta_slew_doubled_per_task"] / 2) * scale,
                "high_default_doubled_domain_per_steering_task": high_values["lta_slew_doubled_per_task"],
                "high_default_b6_counts_per_task": high_values["lta_slew_doubled_per_task"] / 2,
                "high_default_deg_per_task": (high_values["lta_slew_doubled_per_task"] / 2) * scale,
                "wall_clock_deg_per_second": None,
                "boundary": "Firmware closes the per-steering-task slew, but not the exact wall-clock steering-task cadence; do not manufacture deg/s.",
            },
            "doubled_domain_absolute_clamp": {
                "raw_internal": gv["target_clamp_lta"],
                "equivalent_b6_raw": gv["target_clamp_lta"] / 2,
                "equivalent_deg": (gv["target_clamp_lta"] / 2) * scale,
                "all_profile_globals_equal": True,
            },
            "measured_steering_rate": {
                "raw_abs_threshold": gv["measured_rate_threshold_lta"],
                "violation_relation": "abs(rate_raw) > 100",
                "selected_low_persistence_cycles": low_values["rate_debounce"],
                "high_default_persistence_cycles": high_values["rate_debounce"],
                "panda_boundary": "Exactly 100 is accepted by the recovered comparison. A future Panda can cut immediately above 100 instead of waiting for EPS persistence.",
            },
        },
        "indexed_compensation": {
            "entry": "0x000CBFCE",
            "interpolator": "0x000CE6A2",
            "index_input": "FEBEADF4",
            "index_physical_identity": None,
            "maps": map_rows,
            "selected_low_vehicle_effect": "all four promoted ADF4-indexed profile compensation maps are zero at every real interpolation point",
            "high_default_effect": "the four compiled fallback maps become nonzero beginning at axis 7680 and rise thereafter",
            "safety_conclusion": "No speed-dependent reduction of the hard ±1745 B6 LTA/LCA target ceiling is recovered. These are compensation maps, not a max-angle curve. Do not transplant pre-TSS3/TSS2 speed-angle limits.",
            "boundary": "The map input is named only by its recovered RAM cell here. This artifact does not claim FEBEADF4 is SP1/vehicle speed without a separate provenance join.",
        },
        "internal_plausibility_and_fault_thresholds": {
            "tracking_consistency": {
                "entry": "0x000CB14E",
                "half_window_internal": gv["tracking_half_window"],
                "full_comparison_window_internal": gv["tracking_half_window"] * 2,
                "persistence_cycles": gv["tracking_debounce"],
                "physical_units": None,
            },
            "internal_command_instant_monitor": {
                "entry": "0x000CB394",
                "signal": "FEBEAE16 internal command-derived state",
                "lta_threshold_raw": gv["internal_command_threshold_lta"],
                "selected_low_persistence_cycles": low_values["internal_command_debounce"],
                "high_default_persistence_cycles": high_values["internal_command_debounce"],
                "not_measured_q_current": True,
            },
            "internal_command_persistent_inhibit": {
                "entry": "0x000CB59A",
                "signal": "FEBEAE16 internal command-derived state",
                "lta_threshold_raw": gv["internal_command_persistent_threshold"],
                "persistence_cycles": gv["internal_command_persistent_debounce"],
                "not_measured_q_current": True,
            },
            "reconstruction_validity_bounds": {
                "entry": "0x000CBD7E",
                "raw_bounds": [80, 90, 512],
                "physical_units": None,
                "boundary": "The three internal domains are retained as raw firmware bounds; this artifact does not invent angle/current engineering units for them.",
            },
            "extended_inhibit_counter": {
                "entry": "0x000CAE18",
                "threshold": gv["extended_inhibit_counter"],
                "wall_clock_duration": None,
            },
            "controller_error_saturation": {
                "raw_internal": gv["controller_error_saturation"],
                "classification": "controller saturation, not Panda command-rejection limit",
            },
            "torque_sensor_fault_calibration": {
                "raw_constants": torque_fault_constants,
                "classification": "bounded internal torque-sensor/plausibility calibration",
                "physical_driver_override_semantics": False,
                "boundary": "These values participate in torque-sensor fault logic, but comparison directions/domains do not justify treating them as a driver-override threshold.",
            },
        },
        "driver_torque": {
            "observable": "live physical 0x030 Steering Wheel Torque; 0x4A3 B5 is a statically closed alternate",
            "acquisition_clamp_raw": torque_clamp_raw,
            "acquisition_raw_units_per_nm": 256,
            "acquisition_clamp_abs_nm": torque_clamp_nm,
            "telemetry_saturation_abs_centi_nm": 1000,
            "telemetry_saturation_abs_nm": 10.0,
            "override_abs_threshold_nm": None,
            "supervisor_numeric_override_comparator_recovered": False,
            "safety_boundary": "The ~8.238 N.m acquisition clamp and ±10.00 N.m telemetry saturation are representation limits, not driver-override thresholds. Do not use either as Panda override policy.",
            "census_boundary": census["evidence_boundary"],
        },
        "motor_q_current": {
            "observable": "FEBE6592 Motor Actual Current (Q Axis); 0x4A3 B6:B7 is sign-inverted -0.01 A/count",
            "source_chain": "0x33160 builds/saturates FEBE6BAE; 0x5722E snapshots it to FEBE6592; 0x46C4C stages the 0x4A3 conversion",
            "cooperative_supervisor_numeric_response_threshold": None,
            "cooperative_supervisor_measured_q_comparator_recovered": False,
            "internal_monitors_are_q_current": False,
            "direct_reference_matches": [x["entry"] for x in q_refs["matches"]],
            "safety_boundary": "No measured-Q-current comparator is recovered in the cooperative B6 supervisor under the promoted exact-symbol census plus known packet bridge. CB394/CB59A monitor FEBEAE16 internal command state instead. A future Panda response limit must be a separately validated sender/live safety policy, not a fabricated OEM current threshold.",
            "census_boundary": census["evidence_boundary"],
        },
        "remaining_policy": {
            "driver_override_abs_nm": None,
            "temporary_vs_permanent_fault_mapping": None,
            "actuator_response_policy": "requires deliberate Panda/sender policy and relay-correct dynamic validation; no OEM measured-Q comparator recovered in the cooperative supervisor",
            "production_enable_authorized": False,
        },
        "static_conclusion": {
            "absolute_angle_limit_closed": True,
            "per_frame_delta_limit_closed": True,
            "per_task_slew_closed_wall_clock_rate_open": True,
            "measured_rate_limit_closed": True,
            "speed_dependent_hard_angle_reduction_recovered": False,
            "selected_vehicle_profile_compensation_maps_zero": True,
            "driver_torque_observable_closed_override_threshold_open": True,
            "measured_q_observable_closed_oem_response_threshold_not_recovered": True,
            "internal_fault_threshold_families_bounded": True,
            "production_enable_authorized": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()
    out = args.out if args.out.is_absolute() else REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
