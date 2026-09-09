#!/usr/bin/env python3
"""Re-audit the 2026-09-08 F33 monitor session as a sampling/statistics problem.

This intentionally does *not* infer causality from route44 generation residues.  It
quantifies host-read cadence, resident-snapshot cadence, modulo-counter aliasing,
and the strongest source-independent statement supported by the retained idle
control.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "targets/camry-2026/raw-20260908/runtime-monitor-session/files"
DEFAULT_OUT = ROOT / "data/generated/camry_f33_runtime_monitor_statistics.json"
RATE_RE = re.compile(
    r"bus (?P<bus>None|\d+) dt (?P<dt>[0-9.]+) sent (?P<sent>\d+) echo (?P<echo>\d+) "
    r"route_delta (?P<delta>\d+) rate (?P<rate>[0-9.]+)"
)
MARKER_RE = re.compile(
    r"(?P<name>\S+) bus (?P<bus>None|\d+) elapsed (?P<dt>[0-9.]+) sent (?P<sent>\d+) "
    r"echo (?P<echo>\d+) route_delta (?P<delta>\d+).*reads (?P<reads>\d+)"
)


def load_ndjson(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def values(row: dict) -> dict[int, bytes]:
    return {int(v["address"], 16): bytes.fromhex(v["bytes_le"]) for v in row["values"]}


def parse_segments(path: Path, rx: re.Pattern[str]) -> list[dict]:
    out = []
    for line in path.read_text().splitlines():
        m = rx.match(line)
        if not m:
            continue
        g = m.groupdict()
        dt = float(g["dt"])
        delta = int(g["delta"])
        bus = None if g["bus"] == "None" else int(g["bus"])
        row = {
            "bus": bus,
            "duration_s": dt,
            "sent": int(g["sent"]),
            "echo": int(g["echo"]),
            "route44_generation_residue_mod256": delta,
            "residue_rate_hz": delta / dt,
            "one_extra_wrap_rate_step_hz": 256.0 / dt,
            "compatible_event_counts": f"{delta} + 256*k, k>=0",
        }
        if "reads" in g:
            row["host_reads"] = int(g["reads"])
            row["host_read_rate_hz"] = int(g["reads"]) / dt
        out.append(row)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    idle = load_ndjson(RAW / "f33-idle-raw.ndjson")
    assert idle
    t = [r["t_monotonic_ns"] for r in idle]
    dt = [(b - a) / 1e9 for a, b in zip(t, t[1:])]
    capture_s = (t[-1] - t[0]) / 1e9

    # Deduplicate host reads of the same resident snapshot.  Host polls are not
    # independent observations when sample_generation is unchanged.
    distinct: list[dict] = []
    for r in idle:
        if not distinct or r["sample_generation"] != distinct[-1]["sample_generation"]:
            distinct.append(r)

    gen8 = [values(r)[0xFEBE5364][0] for r in distinct]
    gen_deltas = [(b - a) & 0xFF for a, b in zip(gen8, gen8[1:])]
    min_events = sum(gen_deltas)
    distinct_span_s = (distinct[-1]["t_monotonic_ns"] - distinct[0]["t_monotonic_ns"]) / 1e9

    # Route44 base is FEBE4BFF: watched FEBE4C00 contains B1..B4 and
    # FEBE4C04 contains B5..B8. B3 is +2 into the first watch; B7 is +2 into
    # the second. The watched tail contains B25..B31 plus one adjacent byte.
    route_rows = []
    for r in distinct:
        v = values(r)
        b1_4 = v[0xFEBE4C00]
        b5_8 = v[0xFEBE4C04]
        b25_28 = v[0xFEBE4C18]
        b29_32 = v[0xFEBE4C1C]
        route_rows.append({
            "sample_generation": r["sample_generation"],
            "t_monotonic_ns": r["t_monotonic_ns"],
            "route44_generation_u8": v[0xFEBE5364][0],
            "target_lateral_id": b1_4[2] & 0x3F,
            "target_angle_be_hex": (b1_4[3:4] + b5_8[0:1]).hex(),
            "application_sequence_mod64": b5_8[2] & 0x3F,
            "trailer_b28_b31_hex": (b25_28[3:4] + b29_32[:3]).hex(),
        })

    trailer_unique = len({r["trailer_b28_b31_hex"] for r in route_rows})
    seq = [r["application_sequence_mod64"] for r in route_rows]
    seq_min_steps = sum((b - a) & 0x3F for a, b in zip(seq, seq[1:]))

    rate = parse_segments(RAW / "f33_rate.out", RATE_RE)
    marker = parse_segments(RAW / "f33_marker.out", MARKER_RE)

    out = {
        "schema": "camry-f33-runtime-monitor-statistics-v1",
        "target": "8965F3307000",
        "retained_idle_control": {
            "host_b6_tx_echoes": 0,
            "host_reads": len(idle),
            "capture_span_s": capture_s,
            "requested_poll_interval_s": 0.03,
            "actual_host_read_interval_median_s": median(dt),
            "actual_host_read_rate_hz": (len(idle) - 1) / capture_s,
            "distinct_resident_snapshots": len(distinct),
            "distinct_snapshot_generations": [r["sample_generation"] for r in distinct],
            "resident_sample_generation_delta": idle[-1]["sample_generation"] - idle[0]["sample_generation"],
            "resident_sample_generation_rate_hz": (idle[-1]["sample_generation"] - idle[0]["sample_generation"]) / capture_s,
            "nominal_foreground_rate_hz_from_static_timer": 200.0,
            "diagnostic_read_load_boundary": "under repeated SID23 host reads, retained monitor snapshot generation advanced far below the 200-Hz nominal foreground timer and host reads frequently duplicated stale snapshots. The capture therefore cannot be modeled as independent passive 30-ms observations; this does not by itself identify which execution context was slowed or coalesced.",
            "route44_generation_u8_distinct_samples": gen8,
            "route44_generation_mod256_deltas": gen_deltas,
            "route44_minimum_publications_between_first_last_distinct_snapshot": min_events,
            "route44_distinct_span_s": distinct_span_s,
            "route44_minimum_publication_rate_hz": min_events / distinct_span_s,
            "modulo_boundary": "the u8 generation only identifies event count modulo 256; minimum_publications assumes zero additional wraps and is therefore a lower bound, not an exact rate",
            "all_sampled_target_lateral_ids_zero": all(r["target_lateral_id"] == 0 for r in route_rows),
            "distinct_trailer_values": trailer_unique,
            "application_sequence_mod64_distinct_samples": seq,
            "application_sequence_minimum_steps": seq_min_steps,
            "route44_fragment_samples": route_rows,
            "strongest_supported_statement": "with zero host B6 TX echoes, the retained control contains repeated route44 publication-counter movement plus changing route44 application-sequence/trailer content; route44 activity therefore occurred without host B6 transmission, but the source and exact cadence are not identified by this capture",
        },
        "short_window_rate_reaudit": {
            "segments": rate,
            "correction": "the printed 0-Hz/~200-Hz values are modulo-256 endpoint residues, not statistically valid publication-rate estimates. Each endpoint can also be a stale resident snapshot under diagnostic load. Preserve only the raw residue/duration/sender condition.",
        },
        "id63_postaggregate_reaudit": {
            "segments": marker,
            "correction": "11-12 host reads per ~1.1-s block are sparse post-aggregate observations, not independent opportunities to observe a short-lived ingress transaction. Zero observed ID63 at route44/generated/ADB0 does not bound queue admission without a proven observation duty cycle.",
        },
        "design_requirements_before_next_vehicle_run": [
            "Do not poll SID23 during the treatment window; latch/count internally and read once after the block.",
            "Observe the deterministic boundary after foreground receive dispatch (79EDE and its peers) and immediately before 6A410/8EFF8 SecOC consumption inside exact 7A254, rather than between foreground ticks.",
            "Record an event count, exact B3/B4:B5/B7/B8:B9/B28:B31 marker signature, and a same-scheduler positive control; do not use only an 8-bit generation residue.",
            "Use out-of-dictionary ID63 with additive contribution suppressed as the treatment marker.",
            "Jitter marker send intervals across scheduler phase instead of a frequency-locked 50/100-Hz treatment when estimating a negative detection bound.",
            "Treat Panda TX echoes as sender-side evidence only; add an F33-side receive/dispatch witness before calling a transport negative.",
            "Randomize/repeat idle, valid-segment treatment, and unrelated-bus negative-control blocks only after the observer itself has a validated positive-control detection rate.",
        ],
        "decision": {
            "vehicle_needed_now": False,
            "reason": "the retained data and exact scheduler are sufficient to redesign the observer and analysis before another ignition cycle",
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.out)


if __name__ == "__main__":
    main()
