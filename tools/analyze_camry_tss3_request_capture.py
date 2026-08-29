#!/usr/bin/env python3
"""Summarize a synchronized Camry Brake/FRC TSS3-request capture (OQ-052).

Input is the directory emitted by :mod:`tools.camry_tss3_request_capture`:
``metadata.json``, ``oracle.ndjson`` (timestamped queries and reassembled
raw/decoded responses), and the passive all-bus ``can.bin``. The summary is a
deterministic function of those recorded bytes:

- per-ECU/per-DID query and response census, NRC histogram, raw-value
  histogram, per-signal decoded-value histograms, and sample cadence;
- nearest-sample cross-ECU joins between the brake ``... from Toyota Safety
  Sense`` observers and the FRC ISA request vocabulary (request-ID pair
  ``0x10A3``/``0x1B03`` and acceleration pairs ``0x10A1``/``0x1B04`` plus
  ``0x10A1``/``0x1B05`` signal 2), reporting pair counts, |Δt| distribution,
  and joint distinct-value tuples — observed correlation only, never a claimed
  transform;
- passive CAN context: frames by bus plus the exact-Camry ``0x0AA`` wheel-speed
  moving/stationary context reused from the LTA analyzer.

No live behavior is inferred: a DID with zero positives is reported as
unmeasured, exactly as captured. This analyzer never claims the FRC->brake
copy/transform, cadence, arbitration executor, or signer ownership that
OQ-052 still needs target-native evidence for.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.analyze_camry_frc_lta_capture import decode_wheel_speed_kph, iter_canbin_records
from tools.camry_tss3_request_capture import load_registry, build_did_table

SCHEMA = "camry-tss3-request-capture-v1"
DEFAULT_MAX_PAIR_GAP_S = 0.25
WHEEL_SPEED_MIN_KPH = 2.0
# (join name, brake DID, FRC DID, FRC signal index (0-based into decoded list))
JOINS = (
    ("request_id_upper", "0x10A3", "0x1B03", 0),
    ("request_acceleration_upper", "0x10A1", "0x1B04", 0),
    ("request_acceleration_upper_vs_variation_no_limit", "0x10A1", "0x1B05", 1),
)


def load_oracle(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as stream:
        for line in stream:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _median(values: list[int]) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) // 2


def _did_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    queries = [row for row in rows if row.get("type") == "query"]
    responses = [row for row in rows if row.get("type") == "response"]
    positives = [row for row in responses if row.get("status") == "positive"]
    negatives = [row for row in responses if row.get("status") == "negative"]
    nrc_rows = [row for row in responses if row.get("nrc") is not None]
    out: dict[str, Any] = {
        "query_count": len(queries),
        "positive_count": len(positives),
        "negative_count": len(negatives),
        "nrc_counts": dict(Counter(row["nrc"] for row in nrc_rows)),
        "response_status_counts": dict(Counter(row.get("status", "unknown") for row in responses)),
        "raw_counts": dict(Counter(row["raw"] for row in positives)),
    }
    if positives:
        out["first_positive_t_ns"] = positives[0]["t_ns"]
        out["last_positive_t_ns"] = positives[-1]["t_ns"]
        gaps = [b["t_ns"] - a["t_ns"] for a, b in zip(positives, positives[1:])]
        out["positive_interval_median_ns"] = _median(gaps)
        signal_counts: dict[str, Counter] = {}
        for row in positives:
            for signal in row.get("signals", []):
                bucket = signal_counts.setdefault(signal["name"], Counter())
                if "converted_integer" in signal:
                    bucket[str(signal["converted_integer"])] += 1
                else:
                    bucket["decode_error"] += 1
        out["signal_value_counts"] = {name: dict(counts)
                                      for name, counts in signal_counts.items()}
    out["live_support"] = "positive responses retained" if positives else (
        "unmeasured: no positive response recorded" if queries else "not polled")
    return out


def _nearest_pairs(brake_rows: list[dict[str, Any]], frc_rows: list[dict[str, Any]]):
    """Yield (brake row, frc row, |dt|) pairing each brake row to its nearest FRC row."""
    frc_times = [row["t_ns"] for row in frc_rows]
    for row in brake_rows:
        t = row["t_ns"]
        lo, hi = 0, len(frc_times)
        while lo < hi:
            mid = (lo + hi) // 2
            if frc_times[mid] < t:
                lo = mid + 1
            else:
                hi = mid
        candidates = [index for index in (lo - 1, lo) if 0 <= index < len(frc_times)]
        if not candidates:
            continue
        best = min(candidates, key=lambda index: abs(frc_times[index] - t))
        yield row, frc_rows[best], abs(frc_times[best] - t)


def _join_summary(oracle_rows: list[dict[str, Any]], max_pair_gap_s: float) -> dict[str, Any]:
    max_gap_ns = int(max_pair_gap_s * 1e9)
    joins: dict[str, Any] = {}
    for name, brake_did, frc_did, signal_index in JOINS:
        def positives(did: str) -> list[dict[str, Any]]:
            return [row for row in oracle_rows
                    if row.get("type") == "response" and row.get("status") == "positive"
                    and row.get("did") == did]

        brake_rows = positives(brake_did)
        frc_rows = positives(frc_did)
        entry: dict[str, Any] = {"brake_did": brake_did, "frc_did": frc_did,
                                 "brake_positive_count": len(brake_rows),
                                 "frc_positive_count": len(frc_rows)}
        paired = [(brake, frc, dt) for brake, frc, dt in _nearest_pairs(brake_rows, frc_rows)
                  if dt <= max_gap_ns]
        if paired:
            entry["paired_count"] = len(paired)
            entry["max_pair_gap_ns"] = max(dt for _, _, dt in paired)
            entry["median_pair_gap_ns"] = _median([dt for _, _, dt in paired])
            joint: Counter = Counter()
            for brake, frc, _dt in paired:
                brake_value = str(brake["signals"][0].get("converted_integer"))
                frc_signal = frc["signals"][signal_index] if signal_index < len(frc["signals"]) else {}
                frc_value = str(frc_signal.get("converted_integer"))
                joint[f"{brake_value}|{frc_value}"] += 1
            entry["joint_brake_frc_value_counts"] = dict(joint)
            entry["boundary"] = "nearest-sample co-observation only; not a transform proof"
        else:
            entry["paired_count"] = 0
            entry["boundary"] = "no co-observed samples inside the pair gap"
        joins[name] = entry
    return joins


def analyze(capture_dir: Path, *, max_pair_gap_s: float = DEFAULT_MAX_PAIR_GAP_S) -> dict[str, Any]:
    metadata = json.loads((capture_dir / "metadata.json").read_text())
    if metadata.get("schema") != SCHEMA:
        raise SystemExit(f"{capture_dir} is not a {SCHEMA} capture directory")
    oracle_rows = load_oracle(capture_dir / metadata.get("files", {}).get("oracle", "oracle.ndjson"))

    targets = build_did_table(load_registry())
    per_did: dict[str, Any] = {}
    for target in targets:
        did = f"0x{target.did:04X}"
        rows = [row for row in oracle_rows
                if row.get("ecu") == target.ecu
                and (row.get("did") == did or row.get("request_did") == did)
                and row.get("type") in ("query", "response")]
        per_did[target.key] = _did_summary(rows)
    per_ecu: dict[str, Any] = {}
    for ecu in dict.fromkeys(target.ecu for target in targets):
        negatives = [row for row in oracle_rows
                     if row.get("type") == "response" and row.get("ecu") == ecu
                     and row.get("status") == "negative"]
        pending_rows = [row for row in oracle_rows
                        if row.get("type") == "response" and row.get("ecu") == ecu
                        and row.get("status") == "response_pending"]
        per_ecu[ecu] = {
            "negative_count": len(negatives),
            "response_pending_count": len(pending_rows),
            "nrc_counts": dict(Counter(row["nrc"] for row in negatives + pending_rows)),
        }

    can_summary: dict[str, Any] = {"frames_by_bus": Counter()}
    wheel_speeds: list[float] = []
    with (capture_dir / metadata.get("files", {}).get("can", "can.bin")).open("rb") as stream:
        for _t_ns, bus, address, data in iter_canbin_records(stream):
            can_summary["frames_by_bus"][str(bus)] += 1
            if address == 0x0AA and len(data) == 8:
                wheel_speeds.append(decode_wheel_speed_kph(data))
    can_summary["frames_by_bus"] = dict(can_summary["frames_by_bus"])
    moving = [speed for speed in wheel_speeds if speed > WHEEL_SPEED_MIN_KPH]
    can_summary["wheel_speed_context"] = {
        "sample_count": len(wheel_speeds),
        "moving_over_2kph_sample_count": len(moving),
        "max_kph": round(max(wheel_speeds), 3) if wheel_speeds else None,
    }

    return {
        "schema": "camry-tss3-request-analysis-v1",
        "capture": {
            "schema": metadata.get("schema"),
            "diag_bus": metadata.get("diag_bus"),
            "duration_s": metadata.get("duration_s"),
            "error": metadata.get("error"),
        },
        "oracle": per_did,
        "oracle_per_ecu_negatives": per_ecu,
        "cross_ecu_joins": _join_summary(oracle_rows, max_pair_gap_s),
        "can": can_summary,
        "interpretation": {
            "summary": "deterministic summary of the retained capture bytes",
            "proof_boundary": "observed diagnostic co-occurrence and wire context only; "
                              "FRC->brake copy/transform, cadence, arbitration executor, and "
                              "SecOC/integrity ownership remain open (OQ-052)",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("capture_dir", type=Path, help="directory emitted by tools/camry_tss3_request_capture.py")
    ap.add_argument("--json", type=Path, help="optional path to write the summary JSON")
    ap.add_argument("--max-pair-gap", type=float, default=DEFAULT_MAX_PAIR_GAP_S,
                    help="maximum |dt| for cross-ECU nearest-sample pairing (default: 0.25 s)")
    args = ap.parse_args()
    summary = analyze(args.capture_dir, max_pair_gap_s=args.max_pair_gap)
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    if args.json:
        args.json.write_text(rendered + "\n")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
