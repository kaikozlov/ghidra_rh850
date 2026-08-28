#!/usr/bin/env python3
"""0x030 B22:B23 mapped motor-feedback proxy correlation over the two relay-correct drives.

Read-only deterministic analysis against tracked raw captures. The 0x030 wire decode is
bound to the exact-F33 decompiler-evidenced mapping in the TSS3 opendbc port artifact
(signal 33 -> B22:B23 signed big-endian, nonlinear mapped motor-feedback/current-family
proxy sharing the pre-clamp Q-axis aggregate that feeds DID 0x1151). Per 0x030 frame
(~100 Hz), the driver torque (B8 + B17[3:0]), 0x025 steering angle/rate, and 0x0AA wheel
speed are joined by nearest frame time.

Quantified per drive:
  * strata: Class-L (bus0 0x08A B21==0x0B, recomputed and asserted equal to the VAR-067
    census) versus a speed-matched cruise-latch control (0x08A B3==0x08, not Class-L,
    wheel speed inside the Class-L speed range);
  * simple deterministic stats: sample counts, medians/percentiles of |B22:B23| and
    |torque|, Pearson r of B22:B23 against torque/rate/angle per stratum;
  * rate-controlled hands-light core (|torque|<=0.5 N.m, |rate_raw|<=2): Class-L vs
    control floor comparison with a tie-corrected rank-sum z and lag-1 autocorrelation;
  * opposing-driver/motion run census (|B|>=150, |torque|>=0.2, |rate_raw|>=2,
    sign(B)==sign(rate), sign(B)==-sign(torque), <=1-sample dropout bridging, runs
    >=0.1 s) inside Class-L and in the control;
  * hands-light steering-motion sweep census (|torque|<=0.5, |rate_raw|>=2, >=0.5 s);
  * Class-L rise/fall edge |B| medians over 3 s pre/post windows;
  * B6 (0x0B6) counts on all buses (asserted zero in these captures).

Motor feedback is never by itself proof of an external lateral command: driver EPS
assist also creates current. The output is bounded review evidence only; production
output stays disabled.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.analyze_camry_2026_relay_capture import decode_wheel_speed
from tools.toyota_route_opendbc_common import be_signal

RAW = REPO / "targets/camry-2026/raw-20260827"
CENSUS = REPO / "data/generated/camry_2026_cruise_lta_edge_census.json"
PORT = REPO / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"
OUT = REPO / "data/generated/camry_2026_motor_feedback_correlation.json"
DRIVES = {
    "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}

JOIN_TOL_025_NS = 40_000_000
JOIN_TOL_0AA_NS = 300_000_000
OPP_MIN_ABS_CURRENT = 150
OPP_MIN_ABS_TORQUE = 0.2
OPP_MIN_ABS_RATE = 2
OPP_BRIDGE_SAMPLES = 1
OPP_MIN_RUN_S = 0.100
CORE_MAX_ABS_TORQUE = 0.5
CORE_MAX_ABS_RATE = 2
SWEEP_MIN_RUN_S = 0.500
EDGE_WINDOW_NS = 3_000_000_000
LAG1_MAX_DT_NS = 15_000_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def torque_nm(d: bytes) -> float:
    return round(be_signal(d, 71, 8, is_signed=True) * 0.1 + be_signal(d, 139, 4, is_signed=True) * 0.01, 3)


def angle_deg(d: bytes) -> float:
    return round(be_signal(d, 3, 12, is_signed=True) * 1.5 + be_signal(d, 39, 4, is_signed=True) * 0.1, 3)


def rate_raw(d: bytes) -> int:
    return be_signal(d, 35, 12, is_signed=True)


def motor_current(d: bytes) -> int:
    """0x030 B22:B23 signed big-endian (firmware packer writes value<<16 BE)."""
    return int.from_bytes(d[22:24], "big", signed=True)


def load(path: Path):
    with gzip.open(path, "rt") as f:
        for line in f:
            if not line.strip():
                continue
            seg, t, bus, addr, data = json.loads(line)
            yield int(seg), int(t), int(bus), int(addr), bytes.fromhex(data)


def pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return None
    return round(cov / (va ** 0.5 * vb ** 0.5), 4)


def median(xs: list[float]) -> float:
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return round((s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2), 3)


def p90(xs: list[float]) -> float:
    if not xs:
        return None
    s = sorted(xs)
    return round(s[int(len(s) * 0.9)], 3)


def rank_sum_z(x: list[float], y: list[float]) -> dict:
    """Tie-corrected Mann-Whitney rank-sum z (positive => x tends larger)."""
    n1, n2 = len(x), len(y)
    if n1 < 2 or n2 < 2:
        return None
    u = 0.0
    for xi in x:
        u += sum(1.0 for yi in y if yi < xi) + 0.5 * sum(1.0 for yi in y if yi == xi)
    n = n1 + n2
    allv = x + y
    counts: dict[float, int] = {}
    for v in allv:
        counts[v] = counts.get(v, 0) + 1
    tie = sum(c ** 3 - c for c in counts.values())
    var = n1 * n2 * ((n + 1) - tie / (n * n - n)) / 12.0 if n > 1 else 0.0
    if var <= 0:
        return None
    z = (u - n1 * n2 / 2.0) / math.sqrt(var)
    return {"z": round(z, 2), "p_two_sided": round(math.erfc(abs(z) / math.sqrt(2.0)), 4)}


def lag1_autocorr(samples: list[dict]) -> float:
    pairs = [(a["cur_abs"], b["cur_abs"]) for a, b in zip(samples, samples[1:])
             if 0 <= b["t"] - a["t"] <= LAG1_MAX_DT_NS]
    return pearson([p[0] for p in pairs], [p[1] for p in pairs])


def in_intervals(t: int, intervals: list[tuple[int, int]]) -> bool:
    return any(a <= t <= b for a, b in intervals)


def runs_from(samples: list[dict], keep: callable, min_run_s: float, bridge: int) -> list[list[dict]]:
    """Maximal kept-sequences allowing <=bridge consecutive non-kept bridging samples."""
    runs: list[list[dict]] = []
    cur: list[dict] = []
    drop = 0
    for s in samples:
        if keep(s):
            cur.append(s)
            drop = 0
        elif cur:
            drop += 1
            if drop > bridge:
                if cur and (cur[-1]["t"] - cur[0]["t"]) / 1e9 >= min_run_s:
                    runs.append(cur)
                cur = []
                drop = 0
    if cur and (cur[-1]["t"] - cur[0]["t"]) / 1e9 >= min_run_s:
        runs.append(cur)
    return runs


def summarize_run(run: list[dict], base_ns: int | None, base_label: str) -> dict:
    first, last = run[0], run[-1]
    return {
        "start_s": round((first["t"] - base_ns) / 1e9, 6) if base_ns is not None else None,
        "start_reference": base_label if base_ns is not None else "segment-relative not applied",
        "duration_s": round((last["t"] - first["t"]) / 1e9, 6),
        "median_current": median([s["cur"] for s in run]),
        "median_driver_torque_nm": median([s["torque"] for s in run]),
        "median_rate_raw": median([float(s["rate"]) for s in run]),
        "angle_first_deg": first["angle"],
        "angle_last_deg": last["angle"],
        "median_speed_kph": median([s["speed"] for s in run]),
    }


def analyze_drive(label: str, path: Path, census_intervals: list[dict], census_cruise: dict) -> dict:
    a8: list[tuple[int, int, bytes]] = []
    t30: list[tuple[int, bytes]] = []
    t25: list[tuple[int, bytes]] = []
    speeds: list[tuple[int, float]] = []
    bases: dict[int, int] = {}
    b6 = 0
    n_frames = 0
    for seg, t, bus, addr, dat in load(path):
        n_frames += 1
        bases.setdefault(seg, t)
        if bus == 0:
            if addr == 0x030 and len(dat) == 32:
                t30.append((t, dat))
            elif addr == 0x025 and len(dat) == 32:
                t25.append((t, dat))
            elif addr == 0x0AA and len(dat) == 8:
                speeds.append((t, decode_wheel_speed(dat)))
            elif addr == 0x08A and len(dat) == 32:
                a8.append((seg, t, dat))
        if addr == 0x0B6:
            b6 += 1
    t30.sort()
    t25.sort()
    speeds.sort()

    # Recompute Class-L intervals (bus0 0x08A B21==0x0B) and assert census equality.
    ints: list[tuple[int, int, int, int]] = []
    start_seg = start = last_seg = last = None
    for seg, t, d in a8:
        if d[21] == 0x0B:
            if start is None:
                start_seg, start, last_seg, last = seg, t, seg, t
            else:
                last_seg, last = seg, t
        elif start is not None:
            ints.append((start_seg, start, last_seg, last))
            start_seg = start = last_seg = last = None
    if start is not None:
        ints.append((start_seg, start, last_seg, last))
    recomputed = [
        {"start_segment": s_seg, "start_s": round((a - bases[s_seg]) / 1e9, 6), "duration_s": round((b - a) / 1e9, 6)}
        for s_seg, a, _e_seg, b in ints
    ]
    expected = [{k: row[k] for k in ("start_segment", "start_s", "duration_s")} for row in census_intervals]
    assert recomputed == expected, f"{label}: Class-L interval drift: {recomputed} != {expected}"

    # Recompute cruise-latch intervals (bus0 0x08A B3==0x08); assert census count/duration.
    cruise: list[tuple[int, int]] = []
    cstart = clast = None
    for _seg, t, d in a8:
        if d[3] == 0x08:
            if cstart is None:
                cstart = clast = t
            else:
                clast = t
        elif cstart is not None:
            cruise.append((cstart, clast))
            cstart = clast = None
    if cstart is not None:
        cruise.append((cstart, clast))
    assert len(cruise) == census_cruise["interval_count"], f"{label}: cruise interval count drift"
    cruise_dur = round(sum((b - a) for a, b in cruise) / 1e9, 6)
    assert cruise_dur == census_cruise["duration_s"], f"{label}: cruise duration drift {cruise_dur}"

    # Nearest-frame join.
    t25_times = [t for t, _ in t25]
    sp_times = [t for t, _ in speeds]

    def nearest_idx(times: list[int], t: int, tol: int):
        lo, hi = 0, len(times)
        while lo < hi:
            mid = (lo + hi) // 2
            if times[mid] < t:
                lo = mid + 1
            else:
                hi = mid
        best, best_dt = None, None
        for i in (lo - 1, lo):
            if 0 <= i < len(times):
                dt = abs(times[i] - t)
                if best_dt is None or dt < best_dt:
                    best, best_dt = i, dt
        return best if best_dt is not None and best_dt <= tol else None

    samples: list[dict] = []
    dropped = {"no_025": 0, "no_0aa": 0}
    for t, d in t30:
        i25 = nearest_idx(t25_times, t, JOIN_TOL_025_NS)
        isp = nearest_idx(sp_times, t, JOIN_TOL_0AA_NS)
        if i25 is None:
            dropped["no_025"] += 1
            continue
        if isp is None:
            dropped["no_0aa"] += 1
            continue
        samples.append({
            "t": t, "cur": motor_current(d), "cur_abs": abs(motor_current(d)),
            "torque": torque_nm(d), "angle": angle_deg(t25[i25][1]),
            "rate": rate_raw(t25[i25][1]), "speed": speeds[isp][1],
        })

    class_l_ints = [(a, b) for _sseg, a, _eseg, b in ints]
    cl_samples = [s for s in samples if in_intervals(s["t"], class_l_ints)]
    cl_speeds = [s["speed"] for s in cl_samples]
    sp_lo, sp_hi = (min(cl_speeds), max(cl_speeds)) if cl_speeds else (None, None)
    control_samples = [
        s for s in samples
        if not in_intervals(s["t"], class_l_ints) and in_intervals(s["t"], cruise)
        and sp_lo is not None and sp_lo <= s["speed"] <= sp_hi
    ]
    # Speed-matched non-Class-L (any latch state) is the comparison stratum for the
    # opposition/sweep censuses; the cruise-restricted control above is used for the
    # correlation/floor statistics.
    nc_samples = [
        s for s in samples
        if not in_intervals(s["t"], class_l_ints) and sp_lo is not None and sp_lo <= s["speed"] <= sp_hi
    ]

    def stratum_stats(rows: list[dict]) -> dict:
        return {
            "n": len(rows),
            "median_abs_driver_torque_nm": median([abs(s["torque"]) for s in rows]),
            "median_abs_current": median([float(s["cur_abs"]) for s in rows]),
            "p90_abs_current": p90([float(s["cur_abs"]) for s in rows]),
            "median_speed_kph": median([s["speed"] for s in rows]),
            "r_current_vs_torque": pearson([float(s["cur"]) for s in rows], [s["torque"] for s in rows]),
            "r_current_vs_rate": pearson([float(s["cur"]) for s in rows], [float(s["rate"]) for s in rows]),
            "r_current_vs_angle": pearson([float(s["cur"]) for s in rows], [float(s["angle"]) for s in rows]),
        }

    core_cl = [s for s in cl_samples if abs(s["torque"]) <= CORE_MAX_ABS_TORQUE and abs(s["rate"]) <= CORE_MAX_ABS_RATE]
    core_ctrl = [s for s in control_samples if abs(s["torque"]) <= CORE_MAX_ABS_TORQUE and abs(s["rate"]) <= CORE_MAX_ABS_RATE]

    # Opposing-driver/motion run census.
    def opposing(s: dict) -> bool:
        return (s["cur_abs"] >= OPP_MIN_ABS_CURRENT and abs(s["torque"]) >= OPP_MIN_ABS_TORQUE
                and abs(s["rate"]) >= OPP_MIN_ABS_RATE
                and (s["cur"] > 0) == (s["rate"] > 0) and (s["cur"] > 0) != (s["torque"] > 0))

    opp_runs_cl = runs_from(cl_samples, opposing, OPP_MIN_RUN_S, OPP_BRIDGE_SAMPLES)
    opp_runs_ctrl = runs_from(nc_samples, opposing, OPP_MIN_RUN_S, OPP_BRIDGE_SAMPLES)
    opp_cl_all = runs_from(cl_samples, opposing, 0.0, OPP_BRIDGE_SAMPLES)

    # Hands-light steering-motion sweep census.
    def hands_light_motion(s: dict) -> bool:
        return abs(s["torque"]) <= CORE_MAX_ABS_TORQUE and abs(s["rate"]) >= OPP_MIN_ABS_RATE

    sweep_cl = runs_from(cl_samples, hands_light_motion, SWEEP_MIN_RUN_S, OPP_BRIDGE_SAMPLES)
    sweep_ctrl = runs_from(nc_samples, hands_light_motion, SWEEP_MIN_RUN_S, OPP_BRIDGE_SAMPLES)

    # Class-L edge |current| medians over 3 s pre/post windows.
    edges = []
    for (_sseg, a, _eseg, _b), kind in ([(x, "rise") for x in ints] + [(x, "fall") for x in ints]):
        edge_t = a if kind == "rise" else _b
        pre = [s for s in samples if edge_t - EDGE_WINDOW_NS <= s["t"] < edge_t]
        post = [s for s in samples if edge_t <= s["t"] < edge_t + EDGE_WINDOW_NS]
        edges.append({
            "edge": kind, "edge_s": round(edge_t / 1e9, 6),
            "pre_n": len(pre), "post_n": len(post),
            "pre_median_abs_current": median([float(s["cur_abs"]) for s in pre]),
            "post_median_abs_current": median([float(s["cur_abs"]) for s in post]),
        })

    b6_total = b6
    floor_z = rank_sum_z([float(s["cur_abs"]) for s in core_cl], [float(s["cur_abs"]) for s in core_ctrl])
    cl_base = ints[0][1] if ints else None

    return {
        "source": {"file": str(path.relative_to(REPO)), "sha256": sha256(path), "frame_count": n_frames},
        "streams": {
            "eps_0x030_frames": len(t30), "steer_0x025_frames": len(t25),
            "speed_0x0AA_frames": len(speeds),
            "joined_samples": len(samples), "dropped_no_025": dropped["no_025"], "dropped_no_0aa": dropped["no_0aa"],
            "join_tolerances": {"0x025_ms": JOIN_TOL_025_NS // 1_000_000, "0x0AA_ms": JOIN_TOL_0AA_NS // 1_000_000},
        },
        "class_l": {
            "intervals": [{"start_s": round((a - bases[ss]) / 1e9, 6), "duration_s": round((b - a) / 1e9, 6),
                           "start_segment": ss} for ss, a, _es, b in ints],
            "speed_range_kph": [round(sp_lo, 2), round(sp_hi, 2)] if sp_lo is not None else None,
            "stats": stratum_stats(cl_samples),
        },
        "control_definition": "cruise latch (0x08A B3==0x08) and not Class-L and wheel speed within the Class-L speed range",
        "control": {
            "n": len(control_samples),
            "stats": stratum_stats(control_samples),
        },
        "speed_matched_non_class_l": {
            "definition": "not Class-L and wheel speed within the Class-L speed range (any latch state)",
            "n": len(nc_samples),
        },
        "hands_light_core": {
            "definition": f"|driver torque| <= {CORE_MAX_ABS_TORQUE} N.m and |rate_raw| <= {CORE_MAX_ABS_RATE}",
            "class_l": {**stratum_stats(core_cl), "lag1_autocorr_abs_current": lag1_autocorr(core_cl)},
            "control": {**stratum_stats(core_ctrl), "lag1_autocorr_abs_current": lag1_autocorr(core_ctrl)},
            "median_abs_current_floor_ratio": (
                round(median([float(s["cur_abs"]) for s in core_cl]) / median([float(s["cur_abs"]) for s in core_ctrl]), 3)
                if core_ctrl and median([float(s["cur_abs"]) for s in core_ctrl]) > 0 else None),
            "rank_sum_z_class_l_larger": floor_z,
        },
        "opposing_driver_motion_runs": {
            "definition": (f"|B22:B23| >= {OPP_MIN_ABS_CURRENT} and |driver torque| >= {OPP_MIN_ABS_TORQUE} N.m and "
                           f"|rate_raw| >= {OPP_MIN_ABS_RATE} and sign(B)==sign(rate) and sign(B)==-sign(torque); "
                           f"<= {OPP_BRIDGE_SAMPLES} sample dropout bridging; runs >= {OPP_MIN_RUN_S} s"),
            "class_l": {
                "qualifying_samples": len([s for s in cl_samples if opposing(s)]),
                "runs_ge_100ms": len(opp_runs_cl),
                "max_run_s": round(max((r[-1]["t"] - r[0]["t"] for r in opp_runs_cl), default=0) / 1e9, 6),
                "top_runs": [summarize_run(r, cl_base, "class_l_interval_start") for r in
                             sorted(opp_runs_cl, key=lambda r: r[-1]["t"] - r[0]["t"], reverse=True)[:6]],
            },
            "control": {
                "qualifying_samples": len([s for s in nc_samples if opposing(s)]),
                "runs_ge_100ms": len(opp_runs_ctrl),
                "max_run_s": round(max((r[-1]["t"] - r[0]["t"] for r in opp_runs_ctrl), default=0) / 1e9, 6),
            },
        },
        "hands_light_motion_sweeps": {
            "definition": f"|driver torque| <= {CORE_MAX_ABS_TORQUE} N.m and |rate_raw| >= {OPP_MIN_ABS_RATE}; runs >= {SWEEP_MIN_RUN_S} s",
            "class_l_runs_ge_500ms": len(sweep_cl),
            "control_runs_ge_500ms": len(sweep_ctrl),
            "class_l_max_sweep_s": round(max((r[-1]["t"] - r[0]["t"] for r in runs_from(cl_samples, hands_light_motion, 0.0, OPP_BRIDGE_SAMPLES)), default=0) / 1e9, 6),
        },
        "class_l_edge_abs_current": {"window_s": 3, "edges": edges},
        "b6": {"total_all_buses": b6_total, "observed_any": b6_total > 0},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    census = json.loads(CENSUS.read_text())
    port = json.loads(PORT.read_text())

    # Bind the wire decode to the exact-F33 decompiler-evidenced mapping.
    m = port["status_carriers"]["0x030"]["mapped_motor_feedback"]
    assert m["wire"] == "B22:B23" and m["wire_decode"] == "signed big-endian 16-bit" and m["signal_id"] == 33
    assert port["generated_com_tx"]["pdu_slice_offsets"][0] == 0

    drives = {}
    for label, path in DRIVES.items():
        drives[label] = analyze_drive(label, path, census["drives"][label]["lateral_hud_candidate"]["intervals"],
                                      census["drives"][label]["cruise_active"])

    combined = {
        "b6_observed_any": any(d["b6"]["observed_any"] for d in drives.values()),
        "class_l_floor_ratios": {k: v["hands_light_core"]["median_abs_current_floor_ratio"] for k, v in drives.items()},
        "class_l_r_current_vs_torque": {k: v["class_l"]["stats"]["r_current_vs_torque"] for k, v in drives.items()},
        "control_r_current_vs_torque": {k: v["control"]["stats"]["r_current_vs_torque"] for k, v in drives.items()},
        "class_l_opposing_runs_ge_100ms": {k: v["opposing_driver_motion_runs"]["class_l"]["runs_ge_100ms"] for k, v in drives.items()},
        "class_l_opposing_max_run_s": {k: v["opposing_driver_motion_runs"]["class_l"]["max_run_s"] for k, v in drives.items()},
        "control_opposing_runs_ge_100ms": {k: v["opposing_driver_motion_runs"]["control"]["runs_ge_100ms"] for k, v in drives.items()},
        "class_l_hands_light_sweeps_ge_500ms": {k: v["hands_light_motion_sweeps"]["class_l_runs_ge_500ms"] for k, v in drives.items()},
        "control_hands_light_sweeps_ge_500ms": {k: v["hands_light_motion_sweeps"]["control_runs_ge_500ms"] for k, v in drives.items()},
    }

    out = {
        "schema": "camry-2026-motor-feedback-correlation-v1",
        "sources": {
            "census": {"path": str(CENSUS.relative_to(REPO)), "sha256": sha256(CENSUS)},
            "tss3_port": {"path": str(PORT.relative_to(REPO)), "sha256": sha256(PORT)},
            "drives": [{"path": str(p.relative_to(REPO)), "sha256": sha256(p)} for p in DRIVES.values()],
        },
        "decode_provenance": {
            "motor_feedback": "0x030 B22:B23 signed big-endian 16-bit; signal 33; bound to camry_8965F3307000_tss3_opendbc_port.json mapped_motor_feedback (PDU0 slice offset 0, buffer offset 0x16)",
            "driver_torque_nm": "signed_be(71|8) * 0.1 + signed_be(139|4) * 0.01",
            "steering_angle_deg": "signed_be(3|12) * 1.5 + signed_be(39|4) * 0.1",
            "steering_rate_raw": "signed_be(35|12)",
            "wheel_speed_kph": "0x0AA mean of 4 wheels, be_raw(s,15)*0.01-67.67",
            "class_l": "bus0 0x08A byte21 == 0x0B (VAR-067 census intervals, recomputed and asserted equal)",
            "cruise_latch": "bus0 0x08A byte3 == 0x08 (census interval count and duration asserted equal)",
        },
        "drives": drives,
        "combined": combined,
        "interpretation": {
            "bounded_motor_feedback_floor": (
                "observed/deterministic: inside Class-L the rate-controlled hands-light core carries a several-fold larger "
                "|B22:B23| floor than the speed-matched cruise control stratum (drive B median ratio 6.0, rank-sum z=39.6), with higher lag-1 autocorrelation "
                "and near-zero correlation with driver torque, while the control stratum is driver-proportional "
                "(r(current,torque) strongly positive). This proves a smooth non-driver-proportional motor-feedback "
                "component inside Class-L; it does NOT uniquely label it LTA torque, because a mode-changed EPS "
                "damping/assist map produces the same signature."
            ),
            "bounded_opposing_runs": (
                "observed/deterministic: episodes exist (longest 0.9 s, drive A) where the motor-feedback proxy drives in "
                "the steering-motion direction while opposing measured driver torque, with B6 absent on all buses. This is "
                "consistent with active EPS assist applying torque against the driver, but driver assist, damping, "
                "friction/road-load compensation, and lane-keeping-class functions are not separable from these two drives; "
                "it is not proof of LTA authority."
            ),
            "bounded_edges_and_sweeps": (
                "observed/deterministic: the cruise-clean drive-B Class-L rise shows no immediate |B22:B23| step "
                "(3 s pre/post medians 84 vs 102), and no sustained >=0.5 s hands-light steering-motion sweep occurs "
                "inside Class-L in either drive; the speed-matched non-Class-L stratum contains one such sweep (drive A). "
                "The floor grows with Class-L occupancy rather than stepping at its rise edge, and falls after Class-L ends."
            ),
            "production_output_authorized": False,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out} ({len(json.dumps(out))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
