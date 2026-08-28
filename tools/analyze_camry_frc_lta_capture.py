#!/usr/bin/env python3
"""Summarize a synchronized Camry FRC 0x1601 + all-CAN capture.

Input is the directory emitted by :mod:`tools.camry_frc_lta_capture`.  The
analysis deliberately distinguishes Toyota's exact diagnostic state label
(``LTA Enabled``) from a stronger claim that steering torque was continuously
being produced.

CAN is attributed to an oracle state only between *two consecutive positive*
0x1601 samples that report the same four-byte state.  This avoids assigning a
transition interval to either side from one stale sample.  Gaps larger than the
selected maximum are left unclassified.
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
SELECTED_IDS = (0x00F, 0x025, 0x030, 0x0D7, 0x0B6)


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
            raw = row.get("raw")
            if not isinstance(raw, str) or len(raw) != 8:
                raise ValueError(f"oracle line {line_no}: positive response lacks 4-byte raw state")
            rows.append(row)
    rows.sort(key=lambda row: row["t_ns"])
    return rows


def stable_intervals(oracles: list[dict[str, Any]], max_gap_s: float) -> list[dict[str, Any]]:
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
            "lta_switch_condition": before["lta_switch_condition"],
            "lta_control_condition": before["lta_control_condition"],
            "hands_off_customize_condition": before["hands_off_customize_condition"],
            "hands_off_control_condition": before["hands_off_control_condition"],
            "lta_enabled_oracle": bool(before.get("lta_enabled_oracle")),
        })
    return out


def interval_index(intervals: list[dict[str, Any]]):
    # The interval count is tiny (~10 Hz oracle versus a drive), so a monotonic
    # pointer is sufficient and keeps the high-rate CAN pass O(frames+intervals).
    index = 0
    def classify(t_ns: int) -> dict[str, Any] | None:
        nonlocal index
        while index < len(intervals) and t_ns >= intervals[index]["end_ns"]:
            index += 1
        if index < len(intervals) and intervals[index]["start_ns"] <= t_ns < intervals[index]["end_ns"]:
            return intervals[index]
        return None
    return classify


def analyze(capture_dir: Path, *, max_oracle_gap_s: float = DEFAULT_MAX_ORACLE_GAP_S) -> dict[str, Any]:
    metadata = json.loads((capture_dir / "metadata.json").read_text())
    oracles = load_oracle(capture_dir / metadata["files"]["oracle"])
    intervals = stable_intervals(oracles, max_oracle_gap_s)

    state_samples = Counter(row["raw"] for row in oracles)
    state_details: dict[str, dict[str, Any]] = {}
    for row in oracles:
        state_details.setdefault(row["raw"], {
            "raw": row["raw"],
            "lta_switch_condition": row["lta_switch_condition"],
            "lta_control_condition": row["lta_control_condition"],
            "hands_off_customize_condition": row["hands_off_customize_condition"],
            "hands_off_control_condition": row["hands_off_control_condition"],
            "lta_switch_label": row.get("lta_switch_label"),
            "lta_control_label": row.get("lta_control_label"),
            "hands_off_customize_label": row.get("hands_off_customize_label"),
            "hands_off_control_label": row.get("hands_off_control_label"),
            "lta_enabled_oracle": bool(row.get("lta_enabled_oracle")),
        })

    stable_duration = Counter()
    for interval in intervals:
        stable_duration["enabled" if interval["lta_enabled_oracle"] else "other"] += interval["duration_s"]

    can_counts: dict[str, Counter] = {
        "enabled": Counter(),
        "other": Counter(),
        "unclassified": Counter(),
    }
    id_dlc_counts: dict[str, Counter] = {
        "enabled": Counter(),
        "other": Counter(),
        "unclassified": Counter(),
    }
    selected_examples: dict[str, dict[str, list[str]]] = {
        "enabled": defaultdict(list),
        "other": defaultdict(list),
        "unclassified": defaultdict(list),
    }
    classify = interval_index(intervals)
    can_path = capture_dir / metadata["files"]["can"]
    with can_path.open("rb") as stream:
        for t_ns, bus, address, data in iter_canbin_records(stream):
            interval = classify(t_ns)
            phase = "unclassified" if interval is None else ("enabled" if interval["lta_enabled_oracle"] else "other")
            can_counts[phase][str(bus)] += 1
            id_dlc_counts[phase][f"bus{bus}:0x{address:03X}/{len(data)}"] += 1
            if address in SELECTED_IDS:
                key = f"bus{bus}:0x{address:03X}/{len(data)}"
                examples = selected_examples[phase][key]
                if len(examples) < 4:
                    examples.append(data.hex())

    def selected_counts(phase: str) -> dict[str, int]:
        counts = id_dlc_counts[phase]
        return {
            key: value
            for key, value in sorted(counts.items())
            if int(key.split(":0x", 1)[1].split("/", 1)[0], 16) in SELECTED_IDS
        }

    enabled_samples = sum(
        count for raw, count in state_samples.items()
        if state_details[raw]["lta_enabled_oracle"]
    )
    b6_enabled = sum(
        value for key, value in id_dlc_counts["enabled"].items()
        if ":0x0B6/" in key
    )
    upstream_enabled = {
        key: value for key, value in sorted(id_dlc_counts["enabled"].items())
        if key.startswith("bus1:")
    }
    upstream_other = {
        key: value for key, value in sorted(id_dlc_counts["other"].items())
        if key.startswith("bus1:")
    }

    return {
        "schema": "camry-frc-lta-capture-analysis-v1",
        "source": {
            "capture_dir": str(capture_dir),
            "metadata_schema": metadata.get("schema"),
            "diag_bus": metadata.get("diag_bus"),
            "capture_duration_s": metadata.get("duration_s"),
            "max_stable_oracle_gap_s": max_oracle_gap_s,
        },
        "oracle": {
            "positive_sample_count": len(oracles),
            "state_sample_counts": dict(sorted(state_samples.items())),
            "state_details": [state_details[raw] | {"sample_count": state_samples[raw]} for raw in sorted(state_details)],
            "lta_enabled_sample_count": enabled_samples,
            "lta_enabled_observed": enabled_samples > 0,
            "stable_interval_count": len(intervals),
            "stable_lta_enabled_duration_s": stable_duration["enabled"],
            "stable_other_duration_s": stable_duration["other"],
            "interpretation": (
                "Toyota/GTS+ names DID 0x1601 switch=1 as ON and control=0 as LTA Enabled. "
                "This is an exact FRC diagnostic-state oracle; it is not by itself a claim of continuous steering-torque output."
            ),
        },
        "can": {
            "frames_by_phase_and_bus": {phase: dict(counts) for phase, counts in can_counts.items()},
            "selected_counts": {phase: selected_counts(phase) for phase in can_counts},
            "selected_examples": {
                phase: {key: values for key, values in sorted(rows.items())}
                for phase, rows in selected_examples.items()
            },
            "b6_during_stable_lta_enabled": b6_enabled,
            "bus1_id_dlc_during_stable_lta_enabled": upstream_enabled,
            "bus1_id_dlc_during_stable_other": upstream_other,
        },
        "discriminator": {
            "lta_enabled_oracle_observed": enabled_samples > 0,
            "stable_lta_enabled_interval_observed": stable_duration["enabled"] > 0,
            "b6_observed_during_stable_lta_enabled": b6_enabled > 0,
            "consequence": (
                "If a sustained stable LTA-enabled oracle interval is captured with healthy Bus-4 control traffic and zero B6, "
                "the next RE boundary is upstream FRC/Brake transformation or a non-COM/internal EPS path, not another Panda bus or arbitrary EPS CAN ID."
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
