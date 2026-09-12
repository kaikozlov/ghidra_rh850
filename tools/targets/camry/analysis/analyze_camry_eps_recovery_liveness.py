"""Offline-only census of saved EPS recovery logs; never connects to a vehicle."""

from __future__ import annotations

import argparse
import bisect
import collections
import datetime as dt
import json
import sys
import warnings
from pathlib import Path

EPS_IDS = {0x030, 0x351, 0x394, 0x4A3, 0x4C8}
DIAGNOSTIC_IDS = {0x7A1, 0x7A2, 0x7A9, 0x7AA}
WATCH_IDS = EPS_IDS | DIAGNOSTIC_IDS | {0x025, 0x0AA, 0x081, 0x08A}


def diagnostic_modes(frames, states):
    """Assign a mode only inside short, agreeing single-Panda state brackets."""
    states = sorted(states, key=lambda row: row[0])
    times = [t for t, _ in states]
    counts = collections.Counter()
    for t, event, source, address, data in frames:
        index = bisect.bisect_right(times, t) - 1
        mode = None
        if 0 <= index < len(states) - 1:
            before, after = states[index], states[index + 1]
            if before[1] == after[1] and after[0] - before[0] <= 250_000_000:
                mode = before[1]
        counts[mode, event, source, address, data] += 1
    return {
        "boundary": "Offline mode association, not electrical frame-format proof. "
        "Only agreeing adjacent single-Panda states <=250 ms apart are assigned; "
        "mode transitions, gaps, multiple Pandas, and missing states remain unassigned. "
        "Payload length does not establish per-frame FDF/BRS; audit each producer schema separately.",
        "observations": [
            {
                "mode": list(mode) if mode is not None else None,
                "event": event,
                "src": source,
                "address": f"0x{address:03X}",
                "data": data,
                "count": count,
            }
            for (mode, event, source, address, data), count in sorted(
                counts.items(), key=lambda row: repr(row[0])
            )
        ],
    }


def scan(path: Path, LogReader) -> dict:
    counts = collections.Counter()
    events = collections.Counter()
    first_last = {}
    voltage = []
    ignition = collections.Counter()
    error_samples = collections.Counter()
    anchor = None
    states = []
    diagnostic_frames = []
    logger_build = None
    first = last = None
    can_first = can_last = None
    for e in LogReader(str(path), only_union_types=True):
        k = e.which()
        t = int(e.logMonoTime)
        first = t if first is None else min(first, t)
        last = t if last is None else max(last, t)
        events[k] += 1
        if k == "clocks" and e.clocks.wallTimeNanos:
            anchor = (t, int(e.clocks.wallTimeNanos))
        if k == "initData":
            if logger_build is None:
                logger_build = {
                    "git_commit": str(e.initData.gitCommit),
                    "git_branch": str(e.initData.gitBranch),
                    "dirty": bool(e.initData.dirty),
                    "version": str(e.initData.version),
                }
            if anchor is None and e.initData.wallTimeNanos:
                anchor = (t, int(e.initData.wallTimeNanos))
        if k == "pandaStates":
            mode = None
            if len(e.pandaStates) == 1:
                panda = e.pandaStates[0]
                mode = (str(panda.safetyModel), int(panda.safetyParam))
            states.append((t, mode))
            for p in e.pandaStates:
                voltage.append(int(p.voltage))
                ignition[str((bool(p.ignitionLine), bool(p.ignitionCan)))] += 1
                for b in range(3):
                    s = getattr(p, f"canState{b}")
                    if (
                        s.busOff
                        or s.errorPassive
                        or s.receiveErrorCnt
                        or s.transmitErrorCnt
                    ):
                        error_samples[f"bus{b}"] += 1
        if k not in {"can", "sendcan"}:
            continue
        if k == "can":
            can_first = t if can_first is None else min(can_first, t)
            can_last = t if can_last is None else max(can_last, t)
        for f in getattr(e, k):
            src, addr, n = int(f.src), int(f.address), len(f.dat)
            counts[k, src, addr, n] += 1
            if addr in DIAGNOSTIC_IDS:
                diagnostic_frames.append((t, k, src, addr, bytes(f.dat).hex()))
            key = (k, src, addr, n)
            if addr in WATCH_IDS:
                if key not in first_last:
                    first_last[key] = [t, t]
                else:
                    first_last[key][1] = t

    def wall(t):
        return (
            None
            if anchor is None
            else dt.datetime.fromtimestamp(
                (anchor[1] + t - anchor[0]) / 1e9, dt.UTC
            ).isoformat()
        )

    def vstats(vals):
        if not vals:
            return None
        vals = sorted(vals)
        return {
            "samples": len(vals),
            "min_mV": vals[0],
            "median_mV": vals[len(vals) // 2],
            "max_mV": vals[-1],
            "below_12000_mV": sum(v < 12000 for v in vals),
        }

    by_source = collections.Counter()
    for (k, s, a, n), c in counts.items():
        by_source[f"{k}/src{s}"] += c
    watched = []
    relative_origin = can_first if can_first is not None else first
    for (k, s, a, n), c in sorted(counts.items()):
        if a in WATCH_IDS:
            t0, t1 = first_last[k, s, a, n]
            watched.append(
                {
                    "event": k,
                    "src": s,
                    "address": f"0x{a:03X}",
                    "length": n,
                    "count": c,
                    "first_relative_s": round((t0 - relative_origin) / 1e9, 6),
                    "last_relative_s": round((t1 - relative_origin) / 1e9, 6),
                }
            )
    return {
        "path": str(path),
        "diagnostic_transport": diagnostic_modes(diagnostic_frames, states),
        "logger_build": logger_build,
        "wall_start_utc": wall(can_first) if can_first is not None else None,
        "wall_end_utc": wall(can_last) if can_last is not None else None,
        "duration_s": round((can_last - can_first) / 1e9, 6)
        if can_first is not None
        else 0,
        "panda_supply": vstats(voltage),
        "ignition_line_can": dict(ignition),
        "bus_error_samples": dict(error_samples),
        "event_counts": dict(events),
        "frame_counts_by_source": dict(by_source),
        "watched_frames": watched,
        "eps_generated_tx_native_rx": sum(
            c
            for (k, s, a, n), c in counts.items()
            if k == "can" and s < 3 and a in EPS_IDS
        ),
        "eps_diagnostic_response_native_rx": sum(
            c
            for (k, s, a, n), c in counts.items()
            if k == "can" and s < 3 and a == 0x7A9
        ),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--openpilot-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("logs", nargs="+", type=Path)
    args = ap.parse_args()
    for p in args.logs:
        if not p.is_file():
            ap.error(f"not a local file: {p}")
    sys.path.insert(0, str(args.openpilot_root))
    from openpilot.tools.lib.logreader import LogReader

    rows = []
    for path in args.logs:
        with warnings.catch_warnings(record=True) as found_warnings:
            warnings.simplefilter("always")
            row = scan(path.resolve(), LogReader)
        row["parse_warnings"] = [str(w.message) for w in found_warnings]
        rows.append(row)
        print(
            json.dumps(
                {
                    k: row[k]
                    for k in [
                        "path",
                        "wall_start_utc",
                        "duration_s",
                        "panda_supply",
                        "eps_generated_tx_native_rx",
                        "eps_diagnostic_response_native_rx",
                    ]
                }
            ),
            flush=True,
        )
    out = {
        "scope": "offline saved-log observation only; CAN spans exclude repeated initData metadata; CAN IDs are not independently authenticated source identity; no EPS supply-terminal measurement or live fault-register capture",
        "format_scope": "Address, source, payload length and timing only. Short-frame FDF/BRS are not inferred from length or from a newer reader schema. logger_build identifies the producer revision for a separate schema/plumbing audit.",
        "eps_generated_tx_ids": [f"0x{x:03X}" for x in sorted(EPS_IDS)],
        "files": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
