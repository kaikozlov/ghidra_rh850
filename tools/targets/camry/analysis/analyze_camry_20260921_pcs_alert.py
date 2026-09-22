#!/usr/bin/env python3
"""Reduce the retained 2026-09-21 user-reported Camry PCS-alert event."""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_LOGS = ROOT.parents[1] / "logs"
DEFAULT_OPENPILOT = ROOT.parent / "kai-openpilot"
DEFAULT_OUT = ROOT / "data/generated/camry_20260921_pcs_alert.json"
EVENT_ROUTE = "00000043--29caa20fbc"
EVENT_SEGMENT = 12


def load_logreader(openpilot_root: Path):
    root = openpilot_root.resolve()
    for candidate in (root, root / "openpilot"):
        if (candidate / "tools/lib/logreader.py").exists():
            base = candidate.parent if (candidate / "__init__.py").exists() else candidate
            sys.path.insert(0, str(base))
            break
    from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
    return LogReader


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def corpus_paths(logs: Path) -> list[Path]:
    patterns = (
        "0000003a--7d62f5b41f/rlog-*.zst",
        "00000041--a8c2152e46/*/rlog.zst",
        "00000042--169d4d611d/*/rlog.zst",
        "00000043--29caa20fbc/00000043--29caa20fbc--*/rlog.zst",
        "00000051--894db634a8/*/rlog.zst",
    )
    return sorted({Path(item) for pattern in patterns for item in glob.glob(str(logs / pattern))})


def signed16(data: bytes) -> float:
    return round(int.from_bytes(data, "big", signed=True) * 0.001, 3)


def request_row(t: int, data: bytes) -> dict[str, Any]:
    return {
        "log_mono_time_ns": t,
        "raw": data.hex(),
        "byte3": data[3],
        "byte4": data[4],
        "request_a": {"id": data[6] >> 2, "allocation": data[6] & 3, "accel_mps2": signed16(data[8:10])},
        "request_b": {"id": data[7] >> 2, "allocation": data[7] & 3, "accel_mps2": signed16(data[11:13])},
        "set_speed_kph": data[10],
        "lateral_id": data[21] & 0x3F,
        "request_sequence": data[26] & 0x3F,
    }


def preceding(rows: list[dict[str, Any]], t: int) -> dict[str, Any] | None:
    eligible = [row for row in rows if row["log_mono_time_ns"] <= t]
    return eligible[-1] if eligible else None


def build(logs: Path = DEFAULT_LOGS, openpilot_root: Path = DEFAULT_OPENPILOT) -> dict[str, Any]:
    LogReader = load_logreader(openpilot_root)
    files = corpus_paths(logs)
    if len(files) != 44:
        raise ValueError(f"expected 44 retained 2026-09-21 rlogs, found {len(files)}")

    event_path = logs / EVENT_ROUTE / f"{EVENT_ROUTE}--{EVENT_SEGMENT}/rlog.zst"
    segment0 = logs / EVENT_ROUTE / f"{EVENT_ROUTE}--0/rlog.zst"
    route_start_ns = min(int(event.logMonoTime) for event in LogReader(str(segment0), sort_by_time=False, only_union_types=True))

    sources = []
    asserted_5ae: list[dict[str, Any]] = []
    special_08a_census: Counter[tuple[int, int]] = Counter()
    total_5ae = 0
    for path in files:
        file_5ae = file_asserted = 0
        for event in LogReader(str(path), sort_by_time=False, only_union_types=True):
            if event.which() != "can":
                continue
            for frame in event.can:
                if frame.src != 2 or len(frame.dat) != 32:
                    continue
                data = bytes(frame.dat)
                if frame.address == 0x5AE:
                    total_5ae += 1
                    file_5ae += 1
                    if data[2] & 0x04:
                        file_asserted += 1
                        asserted_5ae.append({
                            "source": relative(path, logs),
                            "log_mono_time_ns": int(event.logMonoTime),
                            "raw": data.hex(),
                        })
                elif frame.address == 0x08A and (data[7] >> 2) in (33, 34):
                    special_08a_census[(data[7] >> 2, data[7] & 3)] += 1
        sources.append({
            "path": relative(path, logs),
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "native_5ae_frames": file_5ae,
            "native_5ae_byte2_bit2_asserted": file_asserted,
        })

    request_frames: list[dict[str, Any]] = []
    f5ae: list[dict[str, Any]] = []
    car_states: list[dict[str, Any]] = []
    car_controls: list[dict[str, Any]] = []
    selfdrive_states: list[dict[str, Any]] = []
    for event in LogReader(str(event_path), sort_by_time=True, only_union_types=True):
        t = int(event.logMonoTime)
        which = event.which()
        if which == "can":
            for frame in event.can:
                if frame.src != 2 or len(frame.dat) != 32:
                    continue
                data = bytes(frame.dat)
                if frame.address == 0x08A:
                    request_frames.append(request_row(t, data))
                elif frame.address == 0x5AE:
                    f5ae.append({"log_mono_time_ns": t, "raw": data.hex(), "byte0": data[0], "byte2": data[2]})
        elif which == "carState":
            state = event.carState
            car_states.append({
                "log_mono_time_ns": t,
                "v_ego_mps": float(state.vEgo),
                "gas_pressed": bool(state.gasPressed),
                "brake_pressed": bool(state.brakePressed),
                "cruise_enabled": bool(state.cruiseState.enabled),
                "cruise_standstill": bool(state.cruiseState.standstill),
            })
        elif which == "carControl":
            control = event.carControl
            car_controls.append({
                "log_mono_time_ns": t,
                "enabled": bool(control.enabled),
                "long_active": bool(control.longActive),
                "requested_accel_mps2": float(control.actuators.accel),
            })
        elif which == "selfdriveState":
            state = event.selfdriveState
            selfdrive_states.append({
                "log_mono_time_ns": t,
                "enabled": bool(state.enabled),
                "active": bool(state.active),
                "alert_type": str(state.alertType),
            })

    special_indices = [index for index, row in enumerate(request_frames) if row["request_b"]["id"] in (33, 34)]
    if len(special_indices) != 21 or special_indices != list(range(special_indices[0], special_indices[-1] + 1)):
        raise ValueError("PCS-alert request-ID run is absent or no longer contiguous")
    first_index, last_index = special_indices[0], special_indices[-1]
    special = request_frames[first_index : last_index + 1]
    before, after = request_frames[first_index - 1], request_frames[last_index + 1]
    start_ns, end_ns = special[0]["log_mono_time_ns"], special[-1]["log_mono_time_ns"]
    phase_counts = Counter((row["request_b"]["id"], row["request_b"]["allocation"]) for row in special)
    first_brake = next(row for row in car_states if row["log_mono_time_ns"] >= start_ns and row["brake_pressed"])
    first_disabled = next(row for row in selfdrive_states if row["log_mono_time_ns"] >= start_ns and not row["enabled"])
    asserted_in_segment = [row for row in f5ae if row["byte2"] & 0x04]
    next_5ae_clear = next(row for row in f5ae if row["log_mono_time_ns"] > asserted_in_segment[-1]["log_mono_time_ns"] and not row["byte2"] & 0x04)

    return {
        "schema": "camry-20260921-pcs-alert-v1",
        "title": "Retained Camry user-reported PCS-alert request-plane timeline",
        "annotation": "The driver reported visible/audible PCS alerting in this window; that attribution is external to the logged openpilot fields.",
        "sources": sources,
        "corpus_census": {
            "rlog_count": len(files),
            "native_5ae_frames": total_5ae,
            "native_5ae_byte2_bit2_asserted": len(asserted_5ae),
            "asserted_files": sorted({row["source"] for row in asserted_5ae}),
            "special_08a_request_b_counts": {f"id_{key[0]}_allocation_{key[1]}": count for key, count in sorted(special_08a_census.items())},
        },
        "event": {
            "route": EVENT_ROUTE,
            "segment": EVENT_SEGMENT,
            "start_route_offset_s": round((start_ns - route_start_ns) / 1e9, 6),
            "end_route_offset_s": round((end_ns - route_start_ns) / 1e9, 6),
            "duration_s": round((end_ns - start_ns) / 1e9, 6),
            "request_frame_count": len(special),
            "request_b_phase_counts": {f"id_{key[0]}_allocation_{key[1]}": count for key, count in sorted(phase_counts.items())},
            "before": before,
            "first": special[0],
            "phase_transition": next(row for row in special if row["request_b"]["id"] == 33),
            "last": special[-1],
            "after": after,
            "acceleration_range_mps2": [min(row["request_b"]["accel_mps2"] for row in special), max(row["request_b"]["accel_mps2"] for row in special)],
            "state_at_start": {
                "car_state": preceding(car_states, start_ns),
                "car_control": preceding(car_controls, start_ns),
                "selfdrive_state": preceding(selfdrive_states, start_ns),
            },
            "first_driver_brake": {**first_brake, "after_event_start_ms": round((first_brake["log_mono_time_ns"] - start_ns) / 1e6, 3)},
            "first_selfdrive_disabled": {**first_disabled, "after_event_start_ms": round((first_disabled["log_mono_time_ns"] - start_ns) / 1e6, 3)},
            "frc_5ae": {
                "asserted_frames": asserted_in_segment,
                "first_assertion_offset_from_request_start_ms": round((asserted_in_segment[0]["log_mono_time_ns"] - start_ns) / 1e6, 3),
                "next_clear": next_5ae_clear,
            },
        },
        "interpretation": {
            "bounded_result": (
                "The native FRC request plane enters a two-phase ID34->ID33 state while request A remains ID11. "
                "Both acceleration slots are -4.000 m/s^2 at entry. FRC-side 0x5AE byte2 bit2 asserts on the exact "
                "entry timestamp and is unique in the retained 44-rlog corpus."
            ),
            "relay_consequence": (
                "Blocking native FRC 0x08A prevents this native request from reaching VMC. A replacement path must "
                "preserve stock emergency requests through normal upstream safety/controller ownership."
            ),
            "boundary": (
                "The user report plus temporal join identifies this as the PCS-alert witness, but does not assign a "
                "global semantic name to requester IDs 33/34 or prove which braking substage each ID represents."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--logs", type=Path, default=DEFAULT_LOGS)
    parser.add_argument("--openpilot-root", type=Path, default=DEFAULT_OPENPILOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    report = build(args.logs, args.openpilot_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")
    print(f"event_frames={report['event']['request_frame_count']} corpus_rlogs={report['corpus_census']['rlog_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
