#!/usr/bin/env python3
"""Summarize a synchronized Camry FRC operating-state + all-CAN capture.

Input is the directory emitted by :mod:`tools.camry_frc_lta_capture`.  The
primary oracle is FRC DID 0x1601 (LTA switch/control state); DID 0x1914 adds the
independent OEM ``ACC Control in Operation`` state.  The combined discriminator
is therefore stronger than merely observing that the LTA feature is enabled,
while still deliberately stopping short of claiming continuous steering-torque
output.

CAN is attributed to an oracle state only between *two consecutive positive*
samples of the same DID that report the same raw value. Gaps larger than the
selected maximum and state transitions are left unclassified. CAN attributed to
the combined operating context must lie inside overlapping stable intervals for
both 0x1601 and 0x1914.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from itertools import pairwise
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.camry_frc_lta_capture import iter_canbin_records

DEFAULT_MAX_ORACLE_GAP_S = 0.35
SELECTED_IDS = (0x00F, 0x025, 0x030, 0x0AA, 0x0D7, 0x0B6)


def load_oracle(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("type") != "response" or row.get("status") != "positive":
                continue
            if not isinstance(row.get("t_ns"), int):
                raise TypeError(f"oracle line {line_no}: positive response lacks integer t_ns")
            # v1 captures before the ACC companion was added omitted `did` and
            # are unambiguously 0x1601 from their decoded field set.
            if row.get("did") is None and "lta_switch_condition" in row:
                row["did"] = "0x1601"
            did = row.get("did")
            if did not in {"0x1601", "0x1914"}:
                raise ValueError(f"oracle line {line_no}: unknown positive DID {did!r}")
            raw = row.get("raw")
            expected_hex_len = 8 if did == "0x1601" else 4
            if not isinstance(raw, str) or len(raw) != expected_hex_len:
                raise ValueError(f"oracle line {line_no}: malformed {did} raw state {raw!r}")
            rows.append(row)
    rows.sort(key=lambda row: row["t_ns"])

    # The closed CAN0/CAN2 relay pair can expose one FRC response on both Panda
    # RX transceivers in the same USB batch. Capture timestamps are assigned per
    # batch, so exact (DID,timestamp,raw-state) duplicates are one sample.
    deduped = []
    seen: set[tuple[str, int, str]] = set()
    for row in rows:
        key = (row["did"], row["t_ns"], row["raw"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def stable_intervals(oracles: list[dict[str, Any]], max_gap_s: float, active_key: str) -> list[dict[str, Any]]:
    max_gap_ns = int(max_gap_s * 1e9)
    out = []
    for before, after in pairwise(oracles):
        gap_ns = after["t_ns"] - before["t_ns"]
        if gap_ns <= 0 or gap_ns > max_gap_ns or before["raw"] != after["raw"]:
            continue
        out.append({
            "start_ns": before["t_ns"],
            "end_ns": after["t_ns"],
            "duration_s": gap_ns / 1e9,
            "raw": before["raw"],
            "active": bool(before.get(active_key)),
        })
    return out


def intersect_intervals(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Intersect two sorted stable-interval sets and AND their active states."""
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        start = max(left[i]["start_ns"], right[j]["start_ns"])
        end = min(left[i]["end_ns"], right[j]["end_ns"])
        if start < end:
            out.append({
                "start_ns": start,
                "end_ns": end,
                "duration_s": (end - start) / 1e9,
                "active": bool(left[i]["active"] and right[j]["active"]),
                "lta_raw": left[i]["raw"],
                "acc_raw": right[j]["raw"],
            })
        if left[i]["end_ns"] <= right[j]["end_ns"]:
            i += 1
        else:
            j += 1
    return out


def interval_index(intervals: list[dict[str, Any]]):
    index = 0

    def classify(t_ns: int) -> dict[str, Any] | None:
        nonlocal index
        while index < len(intervals) and t_ns >= intervals[index]["end_ns"]:
            index += 1
        if index < len(intervals) and intervals[index]["start_ns"] <= t_ns < intervals[index]["end_ns"]:
            return intervals[index]
        return None

    return classify


def be_raw(dat: bytes, start_bit: int, size: int) -> int:
    """Decode one Motorola DBC signal using the repo's established bit numbering."""
    be_bits = [j + i * 8 for i in range(len(dat)) for j in range(7, -1, -1)]
    idx = be_bits.index(start_bit)
    bits = be_bits[idx:idx + size]
    if len(bits) != size:
        raise ValueError(f"signal {start_bit}|{size} exceeds payload")
    value = 0
    for bit in bits:
        byte_i, bit_i = divmod(bit, 8)
        value = (value << 1) | ((dat[byte_i] >> bit_i) & 1)
    return value


def decode_wheel_speed_kph(dat: bytes) -> float:
    """Existing exact-Camry 0x0AA four-wheel speed geometry used by VAR-063."""
    vals = [be_raw(dat, start, 15) * 0.01 - 67.67 for start in (6, 22, 38, 54)]
    return sum(vals) / 4


def _state_summary(oracles: list[dict[str, Any]], active_key: str) -> dict[str, Any]:
    counts = Counter(row["raw"] for row in oracles)
    details: dict[str, dict[str, Any]] = {}
    for row in oracles:
        details.setdefault(row["raw"], {
            key: value for key, value in row.items()
            if key not in {"type", "status", "t_ns", "bus", "address"}
        })
    active_samples = sum(count for raw, count in counts.items() if bool(details[raw].get(active_key)))
    return {
        "positive_sample_count": len(oracles),
        "state_sample_counts": dict(sorted(counts.items())),
        "state_details": [details[raw] | {"sample_count": counts[raw]} for raw in sorted(details)],
        "active_sample_count": active_samples,
        "active_observed": active_samples > 0,
    }


def analyze(capture_dir: Path, *, max_oracle_gap_s: float = DEFAULT_MAX_ORACLE_GAP_S) -> dict[str, Any]:
    metadata = json.loads((capture_dir / "metadata.json").read_text())
    all_oracles = load_oracle(capture_dir / metadata["files"]["oracle"])
    lta_oracles = [row for row in all_oracles if row["did"] == "0x1601"]
    acc_oracles = [row for row in all_oracles if row["did"] == "0x1914"]
    lta_intervals = stable_intervals(lta_oracles, max_oracle_gap_s, "lta_enabled_oracle")
    acc_intervals = stable_intervals(acc_oracles, max_oracle_gap_s, "acc_in_operation_oracle")
    operation_intervals = intersect_intervals(lta_intervals, acc_intervals)

    lta_duration = Counter()
    for interval in lta_intervals:
        lta_duration["enabled" if interval["active"] else "other"] += interval["duration_s"]
    operation_duration = Counter()
    for interval in operation_intervals:
        operation_duration["operational" if interval["active"] else "other"] += interval["duration_s"]

    lta_can_counts = {phase: Counter() for phase in ("enabled", "other", "unclassified")}
    lta_id_dlc = {phase: Counter() for phase in ("enabled", "other", "unclassified")}
    operation_can_counts = {phase: Counter() for phase in ("operational", "other", "unclassified")}
    operation_id_dlc = {phase: Counter() for phase in ("operational", "other", "unclassified")}
    operation_examples: dict[str, dict[str, list[str]]] = {
        phase: defaultdict(list) for phase in ("operational", "other", "unclassified")
    }
    operation_wheel_speeds: list[float] = []

    classify_lta = interval_index(lta_intervals)
    classify_operation = interval_index(operation_intervals)
    can_path = capture_dir / metadata["files"]["can"]
    with can_path.open("rb") as stream:
        for t_ns, bus, address, data in iter_canbin_records(stream):
            lta_interval = classify_lta(t_ns)
            lta_phase = "unclassified" if lta_interval is None else ("enabled" if lta_interval["active"] else "other")
            lta_can_counts[lta_phase][str(bus)] += 1
            lta_id_dlc[lta_phase][f"bus{bus}:0x{address:03X}/{len(data)}"] += 1

            operation_interval = classify_operation(t_ns)
            operation_phase = (
                "unclassified" if operation_interval is None
                else ("operational" if operation_interval["active"] else "other")
            )
            operation_can_counts[operation_phase][str(bus)] += 1
            key = f"bus{bus}:0x{address:03X}/{len(data)}"
            operation_id_dlc[operation_phase][key] += 1
            if address in SELECTED_IDS:
                examples = operation_examples[operation_phase][key]
                if len(examples) < 4:
                    examples.append(data.hex())
            if operation_phase == "operational" and bus == 0 and address == 0x0AA and len(data) == 8:
                operation_wheel_speeds.append(decode_wheel_speed_kph(data))

    def selected_counts(table: dict[str, Counter], phase: str) -> dict[str, int]:
        return {
            key: value
            for key, value in sorted(table[phase].items())
            if int(key.split(":0x", 1)[1].split("/", 1)[0], 16) in SELECTED_IDS
        }

    b6_lta_enabled = sum(value for key, value in lta_id_dlc["enabled"].items() if ":0x0B6/" in key)
    b6_operational = sum(value for key, value in operation_id_dlc["operational"].items() if ":0x0B6/" in key)
    operational_selected = selected_counts(operation_id_dlc, "operational")
    protected_healthy = (
        operational_selected.get("bus0:0x00F/8", 0) > 0
        and operational_selected.get("bus0:0x0D7/32", 0) > 0
    )
    moving_samples = [speed for speed in operation_wheel_speeds if speed > 2.0]
    upstream_operational = {
        key: value for key, value in sorted(operation_id_dlc["operational"].items()) if key.startswith("bus1:")
    }
    upstream_other = {
        key: value for key, value in sorted(operation_id_dlc["other"].items()) if key.startswith("bus1:")
    }

    lta_summary = _state_summary(lta_oracles, "lta_enabled_oracle")
    acc_summary = _state_summary(acc_oracles, "acc_in_operation_oracle")
    strong_zero = (
        operation_duration["operational"] > 0
        and bool(moving_samples)
        and protected_healthy
        and b6_operational == 0
    )

    return {
        "schema": "camry-frc-lta-capture-analysis-v2",
        "source": {
            "capture_dir": str(capture_dir),
            "metadata_schema": metadata.get("schema"),
            "diag_bus": metadata.get("diag_bus"),
            "capture_duration_s": metadata.get("duration_s"),
            "max_stable_oracle_gap_s": max_oracle_gap_s,
        },
        "oracle": {
            "lta_0x1601": lta_summary | {
                "stable_interval_count": len(lta_intervals),
                "stable_lta_enabled_duration_s": lta_duration["enabled"],
                "stable_other_duration_s": lta_duration["other"],
            },
            "acc_0x1914": acc_summary | {
                "stable_interval_count": len(acc_intervals),
                "stable_acc_in_operation_duration_s": sum(
                    interval["duration_s"] for interval in acc_intervals if interval["active"]
                ),
            },
            "combined_operating_context": {
                "stable_interval_count": len(operation_intervals),
                "stable_lta_enabled_plus_acc_operating_duration_s": operation_duration["operational"],
                "stable_other_overlap_duration_s": operation_duration["other"],
                "interpretation": (
                    "0x1601 switch=1/control=0 is Toyota LTA Enabled; 0x1914 flag=1 is Toyota Cruise Control in Operation. "
                    "Their stable overlap is a machine-timestamped factory operating-context oracle, not direct steering-torque proof."
                ),
            },
        },
        "can": {
            "lta_phase_frames_by_bus": {phase: dict(counts) for phase, counts in lta_can_counts.items()},
            "lta_selected_counts": {phase: selected_counts(lta_id_dlc, phase) for phase in lta_id_dlc},
            "b6_during_stable_lta_enabled": b6_lta_enabled,
            "operating_context_frames_by_bus": {phase: dict(counts) for phase, counts in operation_can_counts.items()},
            "operating_context_selected_counts": {
                phase: selected_counts(operation_id_dlc, phase) for phase in operation_id_dlc
            },
            "operating_context_selected_examples": {
                phase: {key: values for key, values in sorted(rows.items())}
                for phase, rows in operation_examples.items()
            },
            "b6_during_stable_lta_enabled_plus_acc_operating": b6_operational,
            "protected_bus4_traffic_healthy_during_operating_context": protected_healthy,
            "wheel_speed_kph_during_operating_context": {
                "sample_count": len(operation_wheel_speeds),
                "moving_over_2kph_sample_count": len(moving_samples),
                "min": min(operation_wheel_speeds) if operation_wheel_speeds else None,
                "max": max(operation_wheel_speeds) if operation_wheel_speeds else None,
            },
            "bus1_id_dlc_during_operating_context": upstream_operational,
            "bus1_id_dlc_during_other_stable_overlap": upstream_other,
        },
        "discriminator": {
            "lta_enabled_oracle_observed": lta_summary["active_observed"],
            "acc_in_operation_oracle_observed": acc_summary["active_observed"],
            "stable_lta_enabled_plus_acc_operating_interval_observed": operation_duration["operational"] > 0,
            "moving_during_operating_context_observed": bool(moving_samples),
            "protected_bus4_traffic_healthy_during_operating_context": protected_healthy,
            "b6_observed_during_operating_context": b6_operational > 0,
            "strong_zero_b6_operating_context": strong_zero,
            "consequence": (
                "If strong_zero_b6_operating_context is true, the capture has stable Toyota LTA-Enabled + ACC-in-Operation state, motion, "
                "and healthy Bus-4 protected traffic with zero B6. The next RE boundary is then upstream FRC/Brake transformation or a "
                "non-COM/internal EPS path, not another Panda bus or arbitrary EPS CAN ID. This still does not label continuous steering torque."
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("capture_dir", type=Path)
    ap.add_argument("--max-oracle-gap", type=float, default=DEFAULT_MAX_ORACLE_GAP_S)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    if args.max_oracle_gap <= 0:
        ap.error("--max-oracle-gap must be positive")
    result = analyze(args.capture_dir, max_oracle_gap_s=args.max_oracle_gap)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
