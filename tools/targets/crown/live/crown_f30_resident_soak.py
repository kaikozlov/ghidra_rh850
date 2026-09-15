#!/usr/bin/env python3
"""Exercise the exact-Crown RAM resident repeatedly at the current measured angle.

This is a standalone qualification step between the one-shot signer proof and a
larger openpilot integration.  It does not install or alter the resident.  It
requires the resident/helper to be installed and armed already, keeps the target
at the fresh measured 0x025 angle, and reports how many native B6 frames were
successfully replaced/signed during the bounded run.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from exploit.ephemeral_runtime import crown_f30_b6_inline_signer as signer


class SoakError(RuntimeError):
    pass


def u32_delta(after: int, before: int) -> int:
    return (int(after) - int(before)) & 0xFFFFFFFF


def repeated_signing_qualified(*, state_after: dict[str, Any], telemetry_after: dict[str, Any],
                               signed_delta: int, attempt_delta: int) -> bool:
    # After a replacement the last computed trailer signs the modified B6, so
    # it is expected to differ from the saved native trailer. The sticky
    # native_verified byte is the retained no-mutation-oracle verdict.
    return (
        state_after["initialized"]
        and state_after["armed"]
        and state_after["last_command5_rc"] == 0
        and telemetry_after["native_verified_raw"] == 1
        and telemetry_after["last_done_flag"] == 1
        and telemetry_after["last_command_status"] == 0
        and signed_delta > 0
        and attempt_delta == signed_delta
    )


def run(*, payload: Path, helper: Path, meta: Path, duration: float, rate_hz: float) -> dict[str, Any]:
    if duration <= 0 or duration > 5.0:
        raise SoakError("duration must be in (0, 5] seconds")
    if rate_hz <= 0 or rate_hz > 100.0:
        raise SoakError("rate-hz must be in (0, 100]")

    bundle = signer.load_bundle(payload=payload, helper=helper, meta=meta)
    session = signer.InlineSignerSession(bundle, require_ready_parked=True)
    if session.vehicle_guard is None:
        raise SoakError("missing Crown READY/Park/stationary guard")

    initial_state = session.read_state()
    if not initial_state["initialized"] or not initial_state["armed"]:
        raise SoakError(f"resident must already be initialized and armed: {initial_state}")
    # native_verified is a sticky result from the resident's untouched first-B6
    # oracle. After a successful replacement, the current computed trailer signs
    # modified B6 data and is expected to differ from the saved native trailer;
    # do not re-require current trailer equality here.
    native_state = session.read_state()
    native_telemetry = signer.decode_signer_telemetry(
        signer._read_memory(session.client, session.uds_mod, signer.TELEMETRY_BASE, signer.TELEMETRY_SIZE)
    )
    if not (
        native_telemetry["native_verified_raw"] == 1
        and native_state["last_command5_rc"] == 0
        and native_telemetry["last_done_flag"] == 1
        and native_telemetry["last_command_status"] == 0
    ):
        raise SoakError(f"sticky native-MAC oracle has not been proven cleanly: state={native_state} telemetry={native_telemetry}")
    native = {"state": native_state, "telemetry": native_telemetry, "verified": True, "sticky_oracle": True}

    # Control now uses Crown's stock functional 0x777 diagnostic transport.
    # Take the counter baseline immediately before this bounded soak.
    state_before = session.read_state()
    telemetry_before = signer.decode_signer_telemetry(
        signer._read_memory(session.client, session.uds_mod, signer.TELEMETRY_BASE, signer.TELEMETRY_SIZE)
    )
    target_raw = int(session.vehicle_guard["recommended_current_target_raw"])
    target_deg = signer.target_degrees_from_raw(target_raw)

    sequence = int(telemetry_before["last_control_seq"])
    period = 1.0 / rate_hz
    sent_sequences = 0
    sent_frames = 0
    start = time.monotonic()
    next_send = start
    while True:
        now = time.monotonic()
        if now - start >= duration:
            break
        if now < next_send:
            time.sleep(min(next_send - now, 0.002))
            continue
        sequence = (sequence % 0xFF) + 1
        frame = signer.replacement_frame(sequence=sequence, target_angle_raw=target_raw)
        for _ in range(signer.WORD_REPEAT_COUNT):
            session.panda.can_send(signer.CONTROL_CAN_ID, frame, signer.CONTROL_BUS)
            sent_frames += 1
            time.sleep(signer.WORD_REPEAT_INTERVAL_SECONDS)
        sent_sequences += 1
        next_send += period

    # Give the last native carrier enough time to consume the last mailbox
    # update before observing resident counters.
    time.sleep(signer.SETTLE_SECONDS)
    telemetry_after = signer.decode_signer_telemetry(
        signer._read_memory(session.client, session.uds_mod, signer.TELEMETRY_BASE, signer.TELEMETRY_SIZE)
    )
    state_after = session.read_state()
    end_guard = signer.verify_crown_ready_stationary_on_panda(session.panda, timeout=1.0)

    signed_delta = u32_delta(state_after["signed_count"], state_before["signed_count"])
    attempt_delta = u32_delta(telemetry_after["command5_attempts"], telemetry_before["command5_attempts"])
    native_delta = u32_delta(telemetry_after["native_frame_count"], telemetry_before["native_frame_count"])
    clean = repeated_signing_qualified(
        state_after=state_after, telemetry_after=telemetry_after,
        signed_delta=signed_delta, attempt_delta=attempt_delta,
    )

    return {
        "schema": "crown-f30-b6-resident-current-angle-soak-v1",
        "target": bundle.meta["target"],
        "requested": {
            "duration_seconds": duration,
            "rate_hz": rate_hz,
            "target_raw": target_raw,
            "target_deg": target_deg,
            "intent": "repeat the proven one-shot replacement at the fresh measured steering angle; no offset target",
        },
        "control_ingress": {"can_id": "0x777", "transport": "stock functional UDS single frame"},
        "native_verification": native,
        "start_vehicle_guard": session.vehicle_guard,
        "end_vehicle_guard": end_guard,
        "state_before": state_before,
        "state_after": state_after,
        "telemetry_before": telemetry_before,
        "telemetry_after": telemetry_after,
        "sent_sequences": sent_sequences,
        "sent_can_frames": sent_frames,
        "native_frame_delta": native_delta,
        "signed_replacement_delta": signed_delta,
        "command5_attempt_delta": attempt_delta,
        "replacement_fraction_of_sequences": (signed_delta / sent_sequences) if sent_sequences else 0.0,
        "measured_angle_delta_deg": end_guard["steering_angle_deg"] - session.vehicle_guard["steering_angle_deg"],
        "verdict": "resident_repeated_signing_qualified" if clean else "resident_repeated_signing_not_qualified",
        "persistent_flash_writes": False,
        "resident_bytes_modified": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--payload", type=Path, required=True)
    ap.add_argument("--helper", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--duration", type=float, default=1.0)
    ap.add_argument("--rate-hz", type=float, default=50.0)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--parked-stationary-confirmed", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    if not args.execute:
        print(json.dumps({
            "schema": "crown-f30-b6-resident-current-angle-soak-plan-v1",
            "duration_seconds": args.duration,
            "rate_hz": args.rate_hz,
            "mutation": "none until --execute; execute sends only C7 current-angle control on the already-installed resident",
            "resident_bytes_modified": False,
            "persistent_flash_writes": False,
        }, indent=2, sort_keys=True))
        return 0
    if not args.parked_stationary_confirmed:
        print("refusing: --execute requires --parked-stationary-confirmed", file=__import__("sys").stderr)
        return 2

    try:
        result = run(
            payload=args.payload,
            helper=args.helper,
            meta=args.meta,
            duration=args.duration,
            rate_hz=args.rate_hz,
        )
    except (SoakError, signer.InlineSignerError, OSError, ValueError) as exc:
        print(f"refusing: {exc}", file=__import__("sys").stderr)
        return 2
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "resident_repeated_signing_qualified" else 3


if __name__ == "__main__":
    raise SystemExit(main())
