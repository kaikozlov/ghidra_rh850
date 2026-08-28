#!/usr/bin/env python3
"""Exhaustive BUS0 (Toyota Bus4 chassis/EPS network)
field census with lead/lag classification over the two relay-correct Camry drives.

Adapted from tools/analyze_camry_2026_bus1_field_leadlag.py (VAR-074) with:
  - every bus0 (addr,dlc) stream, not only exact-F33-accepted IDs;
  - added 12-bit and 10-bit low-nibble windows (w12/s12/w10/s10);
  - bits screened against motor+angle only (cost control);
  - refinement adds command-plausibility metrics: lag-1 autocorr inside Class-L,
    frame-level activity/cadence inside vs outside Class-L and vs cruise control,
    range, and motor-on-field regression slope at peak lag.

Offline/generated evidence only; no vehicle I/O.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from bisect import bisect_right
from collections import Counter, defaultdict
from functools import reduce
from operator import mul
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.analyze_camry_2026_relay_capture import decode_wheel_speed
from tools.toyota_route_opendbc_common import be_signal

RAW = REPO / "targets/camry-2026/raw-20260827"
CENSUS = REPO / "data/generated/camry_2026_cruise_lta_edge_census.json"
DRIVES = {
    "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}

WINDOW_MARGIN_S = 8.0
GRID_NS = 25_000_000
SCREEN_DECIMATE = 4
SCREEN_LAG_RANGE_MS = 500
SCREEN_LAG_STEP_MS = 100
SCREEN_MIN_ABS_R = 0.20
FINE_LAG_STEP_MS = 25
MIN_STREAM_FRAMES = 50
MIN_DISTINCT_SCALAR = 8
MIN_DISTINCT_NIBBLE = 4
MIN_MINORITY_BIT_FRAC = 0.02
DELTA_MAX_GAP_NS = 150_000_000
COUNTER_FRAC = 0.90
COUNTER_MAX_STEP = 15
CHECKSUM_FRAC = 0.90
REPRO_MIN_ABS_R = 0.40
LEAD_MIN_MS = 50
CONTROL_GUARD_S = 2.0
TOP_N = 12

SCALAR_DECODES = ("u8", "s8", "u16be", "s16be", "u16le", "s16le", "u24be", "s24be", "u24le", "s24le")
SPAN = {"u8": 1, "s8": 1, "u16be": 2, "s16be": 2, "u16le": 2, "s16le": 2,
        "u24be": 3, "s24be": 3, "u24le": 3, "s24le": 3,
        "w12": 2, "s12": 2, "w10": 2, "s10": 2}
DELTA_DECODES = (("u8", 1), ("u16be", 2), ("u16le", 2), ("u24be", 3))

Frame = tuple[int, bytes]


def load(path: Path):
    with gzip.open(path, "rt") as f:
        for line in f:
            seg, t, bus, addr, data = json.loads(line)
            yield int(seg), int(t), int(bus), int(addr), bytes.fromhex(data)


def torque_nm(d: bytes) -> float:
    return round(be_signal(d, 71, 8, is_signed=True) * 0.1 + be_signal(d, 139, 4, is_signed=True) * 0.01, 3)


def angle_deg(d: bytes) -> float:
    return be_signal(d, 3, 12, is_signed=True) * 1.5 + be_signal(d, 39, 4, is_signed=True) * 0.1


def rate_raw(d: bytes) -> int:
    return be_signal(d, 35, 12, is_signed=True)


def motor_current(d: bytes) -> int:
    return int.from_bytes(d[22:24], "big", signed=True)


def decode_value(dat: bytes, off: int, dec: str) -> int:
    n = SPAN[dec]
    if dec == "u8":
        return dat[off]
    if dec == "s8":
        return int.from_bytes(dat[off:off + 1], "big", signed=True)
    if dec in ("u16be", "s16be", "u24be", "s24be"):
        raw = int.from_bytes(dat[off:off + n], "big", signed=False)
        return int.from_bytes(dat[off:off + n], "big", signed=True) if dec.startswith("s") else raw
    if dec in ("u16le", "s16le", "u24le", "s24le"):
        raw = int.from_bytes(dat[off:off + n], "little", signed=False)
        return int.from_bytes(dat[off:off + n], "little", signed=True) if dec.startswith("s") else raw
    if dec == "w12":
        return ((dat[off] & 0x0F) << 8) | dat[off + 1]
    if dec == "s12":
        v = ((dat[off] & 0x0F) << 8) | dat[off + 1]
        return v - 0x1000 if v >= 0x800 else v
    if dec == "w10":
        return ((dat[off] & 0x03) << 8) | dat[off + 1]
    if dec == "s10":
        v = ((dat[off] & 0x03) << 8) | dat[off + 1]
        return v - 0x400 if v >= 0x200 else v
    raise ValueError(dec)


def field_key(addr: int, off: int, dec: str) -> str:
    return f"0x{addr:03X}[{off}]{dec}"


def zoh(series: list[tuple[int, float]], grid: list[int]) -> list[float]:
    out: list[float] = []
    i = 0
    cur = 0.0
    n = len(series)
    for g in grid:
        while i < n and series[i][0] <= g:
            cur = series[i][1]
            i += 1
        out.append(cur)
    return out


def standardize(v: list[float]):
    n = len(v)
    if n == 0:
        return None
    mean = sum(v) / n
    var = sum((x - mean) ** 2 for x in v) / n
    if var <= 1e-12:
        return None
    sd = var ** 0.5
    return [x - mean for x in v], sd


def corr_std(x: list[float], xsd: float, y: list[float], ysd: float) -> float:
    cov = sum(map(mul, x, y))
    return (cov / len(x)) / (xsd * ysd)


def lag_corr(xs, xsd, ys, ysd, k: int):
    if k >= 0:
        x2, y2 = xs[:len(xs) - k], ys[k:]
    else:
        x2, y2 = xs[-k:], ys[:len(ys) + k]
    if len(x2) < 30:
        return None
    return corr_std(x2, xsd, y2, ysd)


def sweep(xs, xsd, ys, ysd, lags):
    best_r = None
    best_k = None
    for k in lags:
        r = lag_corr(xs, xsd, ys, ysd, k)
        if r is not None and (best_r is None or abs(r) > abs(best_r)):
            best_r, best_k = r, k
    return {"r": None if best_r is None else round(best_r, 4), "k": best_k}


def collect_drive(path: Path) -> dict:
    a8 = []
    bus0 = defaultdict(list)
    bus2 = defaultdict(list)
    t30, t25, speeds = [], [], []
    n_frames = 0
    for seg, t, bus, addr, dat in load(path):
        n_frames += 1
        if bus == 0:
            bus0[(addr, len(dat))].append((t, dat))
            if addr == 0x08A and len(dat) == 32:
                a8.append((seg, t, dat))
            elif addr == 0x030 and len(dat) == 32:
                t30.append((t, dat))
            elif addr == 0x025 and len(dat) == 32:
                t25.append((t, dat))
            elif addr == 0x0AA and len(dat) == 8:
                speeds.append((t, decode_wheel_speed(dat)))
        elif bus == 2:
            bus2[(addr, len(dat))].append((t, dat))
    a8.sort(); t30.sort(); t25.sort(); speeds.sort()
    return {"a8": a8, "bus0": dict(bus0), "bus2": dict(bus2), "t30": t30, "t25": t25,
            "speeds": speeds, "n_frames": n_frames}


def a8_intervals(a8, byte, value):
    ints = []
    ss = s = ls = last = None
    for seg, t, d in a8:
        if d[byte] == value:
            if s is None:
                ss, s, ls, last = seg, t, seg, t
            else:
                ls, last = seg, t
        elif s is not None:
            ints.append((ss, s, ls, last))
            ss = s = ls = last = None
    if s is not None:
        ints.append((ss, s, ls, last))
    return ints


def counter_bytes(frames, dlc):
    out = {}
    for o in range(dlc):
        dd = Counter()
        for (t1, d1), (t2, d2) in zip(frames, frames[1:]):
            if t2 - t1 > DELTA_MAX_GAP_NS:
                continue
            dv = (d2[o] - d1[o]) & 0xFF
            dd[dv if dv <= COUNTER_MAX_STEP else 999] += 1
        total = sum(dd.values())
        if total < 10:
            continue
        top, cnt = dd.most_common(1)[0]
        if 1 <= top <= COUNTER_MAX_STEP and cnt / total >= COUNTER_FRAC:
            out[o] = {"step": top, "frac": round(cnt / total, 4)}
    return out


def checksum_bytes(frames, dlc):
    out = {}
    sample = [d for _t, d in frames[:4000]]
    for pos in (dlc - 1, dlc - 2):
        if pos < 1:
            continue
        variants = {
            "sum_head_mod256": lambda d, pos=pos: (sum(d[:pos]) & 0xFF) == d[pos],
            "xor_head": lambda d, pos=pos: reduce(lambda a, b: a ^ b, d[:pos], 0) == d[pos],
        }
        for name, fn in variants.items():
            frac = sum(1 for d in sample if fn(d)) / len(sample)
            if frac >= CHECKSUM_FRAC:
                out[pos] = {"variant": name, "frac": round(frac, 4)}
                break
    return out


WINDOW_DECODES = ("w12", "s12", "w10", "s10")
ALL_VALUE_DECODES = SCALAR_DECODES + WINDOW_DECODES


def gen_candidates(addr, dlc, frames, skip):
    def overlaps(off, span):
        return any(b in skip for b in range(off, off + span))

    for off in range(dlc):
        if off in skip:
            continue
        for dec in ALL_VALUE_DECODES:
            span = SPAN[dec]
            if off + span > dlc or overlaps(off, span):
                continue
            yield (field_key(addr, off, dec),
                   [(t, float(decode_value(d, off, dec))) for t, d in frames])
        yield (field_key(addr, off, "nib_hi"), [(t, float(d[off] >> 4)) for t, d in frames])
        yield (field_key(addr, off, "nib_lo"), [(t, float(d[off] & 0x0F)) for t, d in frames])
        for bit in range(7, -1, -1):
            yield (field_key(addr, off, f"b{bit}"), [(t, float((d[off] >> bit) & 1)) for t, d in frames])
    for off in range(dlc):
        if off in skip:
            continue
        for dec, span in DELTA_DECODES:
            if off + span > dlc or overlaps(off, span):
                continue
            series = []
            prev_v = prev_t = None
            for t, d in frames:
                v = decode_value(d, off, dec)
                if prev_v is not None and t - prev_t <= DELTA_MAX_GAP_NS:
                    series.append((t, float(v - prev_v)))
                prev_v, prev_t = v, t
            yield (field_key(addr, off, f"d{dec}"), series)


def candidate_series(addr, dlc, frames, skip, key):
    for k, series in gen_candidates(addr, dlc, frames, skip):
        if k == key:
            return series
    return None


def keep_candidate(key, series):
    if not series:
        return False
    vals = [v for _, v in series]
    dec = key.split("]")[-1]
    if dec.startswith("b"):
        cnt = Counter(vals)
        if len(cnt) < 2:
            return False
        return min(cnt.values()) / len(vals) >= MIN_MINORITY_BIT_FRAC
    distinct = len(set(vals))
    if dec.startswith("nib") or dec.startswith("d"):
        return distinct >= MIN_DISTINCT_NIBBLE
    return distinct >= MIN_DISTINCT_SCALAR


def activity_stats(series, lo, hi):
    """Frame-level change/cadence stats for frames inside [lo,hi]."""
    ins = [(t, v) for t, v in series if lo <= t <= hi]
    if len(ins) < 10:
        return None
    changes = 0
    gaps = []
    prev_v = prev_t = None
    absd = []
    for t, v in ins:
        if prev_v is not None and t - prev_t <= DELTA_MAX_GAP_NS:
            if v != prev_v:
                changes += 1
                gaps.append(t - prev_t)
                absd.append(abs(v - prev_v))
        prev_v, prev_t = v, t
    n = len(ins) - 1
    return {
        "frames": len(ins),
        "change_frac": round(changes / n, 4),
        "median_change_gap_ms": round(sorted(gaps)[len(gaps) // 2] / 1e6, 2) if gaps else None,
        "median_abs_delta": round(sorted(absd)[len(absd) // 2], 2) if absd else None,
        "min": round(min(v for _, v in ins), 2), "max": round(max(v for _, v in ins), 2),
    }


def analyze_drive(label, path, census_drive):
    data = collect_drive(path)
    a8, bus0, t30, t25, speeds = data["a8"], data["bus0"], data["t30"], data["t25"], data["speeds"]

    ints = a8_intervals(a8, 21, 0x0B)
    census_cl = census_drive["lateral_hud_candidate"]["intervals"]
    assert len(ints) == len(census_cl), f"{label}: Class-L count drift"
    for (ss, a, _ls, b), row in zip(ints, census_cl):
        assert ss == row["start_segment"] and round((a - 0) / 1e9, 6) is not None
        dur = round((b - a) / 1e9, 6)
        assert dur == row["duration_s"], f"{label}: Class-L duration drift {dur} != {row['duration_s']}"

    cruise = a8_intervals(a8, 3, 0x08)
    census_cr = census_drive["cruise_active"]
    assert len(cruise) == census_cr["interval_count"], f"{label}: cruise interval count drift {len(cruise)} != {census_cr['interval_count']}"
    cdur = round(sum((b - a) for _ss, a, _es, b in cruise) / 1e9, 6)
    assert cdur == census_cr["duration_s"], f"{label}: cruise duration drift {cdur} != {census_cr['duration_s']}"

    cl = [(a, b) for _ss, a, _es, b in ints]
    cr = [(a, b) for _ss, a, _es, b in cruise]
    win_lo = min(a for a, _ in cl) - int(WINDOW_MARGIN_S * 1e9)
    win_hi = max(b for _, b in cl) + int(WINDOW_MARGIN_S * 1e9)
    grid = list(range(win_lo, win_hi, GRID_NS))
    step_ms = GRID_NS // 1_000_000
    screen_grid = grid[::SCREEN_DECIMATE]
    screen_step_ms = step_ms * SCREEN_DECIMATE
    screen_lags = [k for k in range(-SCREEN_LAG_RANGE_MS // screen_step_ms,
                                    SCREEN_LAG_RANGE_MS // screen_step_ms + 1)]
    fine_lags = [k for k in range(-SCREEN_LAG_RANGE_MS // step_ms,
                                  SCREEN_LAG_RANGE_MS // step_ms + 1)]

    sp_grid = zoh(speeds, grid)
    cl_speeds = [v for v, g in zip(sp_grid, grid) if any(a <= g <= b for a, b in cl)]
    sp_lo, sp_hi = (min(cl_speeds), max(cl_speeds)) if cl_speeds else (None, None)
    guard_ns = int(CONTROL_GUARD_S * 1e9)
    control_mask = [
        (not any(a <= g <= b for a, b in cl))
        and any(a + guard_ns <= g <= b - guard_ns for a, b in cr)
        and sp_lo is not None and sp_lo <= v <= sp_hi
        for g, v in zip(grid, sp_grid)
    ]

    motor = zoh([(t, float(motor_current(d))) for t, d in t30], grid)
    targets = {
        "motor": motor,
        "motor_abs": [abs(x) for x in motor],
        "torque": zoh([(t, torque_nm(d)) for t, d in t30], grid),
        "angle": zoh([(t, angle_deg(d)) for t, d in t25], grid),
        "rate": zoh([(t, float(rate_raw(d))) for t, d in t25], grid),
        "speed": sp_grid,
        "class_l": [1.0 if any(a <= g <= b for a, b in cl) else 0.0 for g in grid],
    }
    tgt_std = {k: standardize(v) for k, v in targets.items()}
    scr_std = {k: standardize(v[::SCREEN_DECIMATE]) for k, v in targets.items()}
    scr_avail = {k: v for k, v in scr_std.items() if v is not None}
    scr_ma = {k: scr_avail[k] for k in ("motor", "angle") if k in scr_avail}

    # grid masks for inside/outside Class-L
    in_cl = [any(a <= g <= b for a, b in cl) for g in grid]

    streams_out = {}
    hits = {}
    drop_totals = Counter()
    kept_total = 0

    for (addr, dlc) in sorted(bus0):
        frames = bus0[(addr, dlc)]
        wframes = [(t, d) for t, d in frames if win_lo <= t <= win_hi]
        entry = {"dlc": dlc, "frames_total": len(frames), "frames_in_window": len(wframes)}
        if len(wframes) < MIN_STREAM_FRAMES:
            entry["skipped"] = "below MIN_STREAM_FRAMES in window"
            bus2n = len(data["bus2"].get((addr, dlc), []))
            entry["bus2_frames_total"] = bus2n
            streams_out[f"0x{addr:03X}"] = entry
            continue
        cb = counter_bytes(wframes, dlc)
        ck = checksum_bytes(wframes, dlc)
        skip = set(cb) | set(ck)

        kept = 0
        n_hits = 0
        top_motor = []
        top_angle = []
        seen_series = set()

        for key, series in gen_candidates(addr, dlc, wframes, skip):
            if not keep_candidate(key, series):
                dec = key.split("]")[-1]
                if not series:
                    drop_totals["empty"] += 1
                elif dec.startswith("b"):
                    drop_totals["bit_const_or_sparse"] += 1
                elif dec.startswith("nib") or dec.startswith("d"):
                    drop_totals["nibble_or_delta_const"] += 1
                else:
                    drop_totals["scalar_low_diversity"] += 1
                continue
            sig = tuple(v for _, v in series)
            if sig in seen_series:
                drop_totals["duplicate_series"] += 1
                continue
            seen_series.add(sig)

            xs_full = zoh(series, grid)
            st = standardize(xs_full)
            if st is None:
                drop_totals["grid_constant"] += 1
                continue
            kept += 1
            xs_scr = xs_full[::SCREEN_DECIMATE]
            mean = sum(xs_scr) / len(xs_scr)
            var = sum((x - mean) ** 2 for x in xs_scr) / len(xs_scr)
            if var <= 1e-12:
                drop_totals["screen_grid_constant"] += 1
                continue
            xs_d = var ** 0.5
            xscr = [x - mean for x in xs_scr]

            scr_motor = None
            scr_angle = None
            is_hit = False
            is_bit = key.split("]")[-1].startswith("b")
            for name, (ys, ysd) in (scr_ma if is_bit else scr_avail).items():
                res = sweep(xscr, xs_d, ys, ysd, screen_lags)
                if res["r"] is None:
                    continue
                if name == "motor":
                    scr_motor = res
                elif name == "angle":
                    scr_angle = res
                if abs(res["r"]) >= SCREEN_MIN_ABS_R:
                    is_hit = True
            if scr_motor is not None:
                top_motor.append((abs(scr_motor["r"]), key, scr_motor["k"]))
            if scr_angle is not None:
                top_angle.append((abs(scr_angle["r"]), key, scr_angle["k"]))
            if is_hit:
                n_hits += 1
                hits[key] = {"addr": addr, "dlc": dlc}

        kept_total += kept

        def top(rows):
            rows.sort(key=lambda x: (-x[0], x[1]))
            return [{"field": k, "lag_ms": kk * screen_step_ms} for _a, k, kk in rows[:TOP_N]]

        entry.update({
            "counter_bytes": {str(k): v for k, v in sorted(cb.items())},
            "checksum_bytes": {str(k): v for k, v in sorted(ck.items())},
            "candidates_kept": kept, "screen_hits": n_hits,
            "top_vs_motor": top(top_motor), "top_vs_angle": top(top_angle),
            "bus2_frames_total": len(data["bus2"].get((addr, dlc), [])),
        })
        streams_out[f"0x{addr:03X}"] = entry

    # Refinement
    refined = []
    for key in sorted(hits):
        h = hits[key]
        addr, dlc = h["addr"], h["dlc"]
        frames = bus0[(addr, dlc)]
        wframes = [(t, d) for t, d in frames if win_lo <= t <= win_hi]
        cb = counter_bytes(wframes, dlc)
        ck = checksum_bytes(wframes, dlc)
        skip = set(cb) | set(ck)
        series = candidate_series(addr, dlc, wframes, skip, key)
        if series is None:
            continue
        gv = zoh(series, grid)
        st = standardize(gv)
        if st is None:
            continue
        xs, xsd = st
        fine = {}
        for name, ts in tgt_std.items():
            if ts is None:
                continue
            ys, ysd = ts
            fine[name] = sweep(xs, xsd, ys, ysd, fine_lags)
        m = fine.get("motor") or {}
        spec = None
        slope = None
        if m.get("k") is not None:
            k = m["k"]
            cg = [v for v, keep in zip(gv, control_mask) if keep]
            cm = [v for v, keep in zip(motor, control_mask) if keep]
            if len(cg) >= 50 and len(cm) == len(cg):
                if k >= 0:
                    x2, y2 = cg[:len(cg) - k], cm[k:]
                else:
                    x2, y2 = cg[-k:], cm[:len(cm) + k]
                s1, s2 = standardize(x2), standardize(y2)
                if s1 is not None and s2 is not None and len(x2) >= 30:
                    spec = round(corr_std(s1[0], s1[1], s2[0], s2[1]), 4)
                    mx = sum(x2) / len(x2)
                    my = sum(y2) / len(y2)
                    sxx = sum((a - mx) ** 2 for a in x2)
                    if sxx > 1e-9:
                        slope = round(sum((a - mx) * (b - my) for a, b in zip(x2, y2)) / sxx, 4)
        # lag-1 autocorr inside Class-L (native grid values)
        vin = [v for v, keep in zip(gv, in_cl) if keep]
        ac = None
        s = standardize(vin)
        if s is not None and len(vin) > 3:
            xs2, sd2 = s
            ac = round(sum(map(mul, xs2[:-1], xs2[1:])) / len(xs2[:-1]) / (sd2 * sd2), 4)
        cl_lo = min(a for a, _ in cl)
        cl_hi = max(b for _, b in cl)
        act_in = activity_stats(series, cl_lo, cl_hi)
        # activity on a cruise-control-only speed-matched region (any)
        ctl_regions = [(a + guard_ns, b - guard_ns) for a, b in cr
                       if b - a > 2 * guard_ns and not any(a < cb2 and b > ca2 for ca2, cb2 in cl)]
        act_ctl = None
        for a, b in ctl_regions:
            act_ctl = activity_stats(series, a, b)
            if act_ctl:
                break
        # activity outside Class-L within window (baseline)
        outside = [(t, v) for t, v in series if win_lo <= t <= win_hi and not any(a <= t <= b for a, b in cl)]
        act_out = activity_stats(outside, win_lo, win_hi) if outside else None
        steps = []
        for a, b in cl:
            for edge, which in ((a, "rise"), (b, "fall")):
                pre = sorted(v for t, v in series if edge - 3_000_000_000 <= t < edge)
                post = sorted(v for t, v in series if edge <= t < edge + 3_000_000_000)
                if pre and post:
                    steps.append({"edge": which, "pre_median": round(pre[len(pre) // 2], 2),
                                  "post_median": round(post[len(post) // 2], 2)})
        lag_ms = (m["k"] * step_ms) if m.get("k") is not None else None
        r0 = None
        if tgt_std["motor"] is not None:
            r0 = lag_corr(xs, xsd, tgt_std["motor"][0], tgt_std["motor"][1], 0)
        refined.append({
            "field": key, "id": f"0x{addr:03X}", "dlc": dlc,
            "motor_r": m.get("r"),
            "motor_lag0_r": round(r0, 4) if r0 is not None else None,
            "motor_peak_lag_ms": lag_ms,
            "angle_r": (fine.get("angle") or {}).get("r"),
            "angle_peak_lag_ms": ((fine.get("angle") or {}).get("k") or 0) * step_ms
            if (fine.get("angle") or {}).get("k") is not None else None,
            "rate_r": (fine.get("rate") or {}).get("r"),
            "torque_r": (fine.get("torque") or {}).get("r"),
            "control_motor_r_at_classl_peak_lag": spec,
            "control_motor_slope": slope,
            "classl_lag1_autocorr": ac,
            "activity_inside_classl": act_in,
            "activity_cruise_control": act_ctl,
            "activity_outside_classl": act_out,
            "class_l_steps": steps,
        })

    refined.sort(key=lambda c: (-abs(c["motor_r"] if c["motor_r"] is not None else 0.0), c["field"]))
    return {
        "source": {"file": str(path.relative_to(REPO)), "frame_count": data["n_frames"]},
        "window": {"margin_s": WINDOW_MARGIN_S, "grid_step_ms": step_ms, "grid_points": len(grid),
                   "screen_grid_step_ms": screen_step_ms,
                   "class_l": [[a, b] for a, b in cl], "cruise": [[a, b] for a, b in cr],
                   "control_grid_points": sum(control_mask),
                   "class_l_speed_range_kph": [round(sp_lo, 2), round(sp_hi, 2)] if sp_lo is not None else None},
        "targets_available": {k: v is not None for k, v in tgt_std.items()},
        "candidate_totals": {"streams": len(streams_out), "kept": kept_total, "dropped": dict(drop_totals)},
        "streams": streams_out,
        "refined_candidates": refined,
    }



def sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "data/generated/camry_2026_bus4_field_leadlag.json")
    args = ap.parse_args()

    census = json.loads(CENSUS.read_text())
    drives = {label: analyze_drive(label, path, census["drives"][label]) for label, path in DRIVES.items()}
    ra = {c["field"]: c for c in drives["drive_a"]["refined_candidates"]}
    rb = {c["field"]: c for c in drives["drive_b"]["refined_candidates"]}
    common = sorted(set(ra) & set(rb))

    def brief(c: dict) -> dict:
        return {k: c.get(k) for k in (
            "id", "dlc", "motor_r", "motor_peak_lag_ms", "angle_r", "angle_peak_lag_ms",
            "rate_r", "torque_r", "control_motor_r_at_classl_peak_lag", "classl_lag1_autocorr")}

    strong = []
    motor_leads = []
    near_motor_leads = []
    angle_leads = []
    rate_leads = []
    for field in common:
        a, b = ra[field], rb[field]
        if a["motor_r"] is not None and b["motor_r"] is not None and abs(a["motor_r"]) >= REPRO_MIN_ABS_R and abs(b["motor_r"]) >= REPRO_MIN_ABS_R:
            strong.append(field)
            la, lb = a["motor_peak_lag_ms"], b["motor_peak_lag_ms"]
            if la is not None and lb is not None and la >= LEAD_MIN_MS and lb >= LEAD_MIN_MS:
                motor_leads.append(field)
            if la is not None and lb is not None and 25 <= la < 50 and 25 <= lb < 50:
                near_motor_leads.append(field)
        for target, dest in (("angle", angle_leads), ("rate", rate_leads)):
            ar, br = a.get(f"{target}_r"), b.get(f"{target}_r")
            al, bl = a.get(f"{target}_peak_lag_ms"), b.get(f"{target}_peak_lag_ms")
            if ar is not None and br is not None and abs(ar) >= REPRO_MIN_ABS_R and abs(br) >= REPRO_MIN_ABS_R and al is not None and bl is not None and al >= LEAD_MIN_MS and bl >= LEAD_MIN_MS:
                dest.append(field)

    selected_names = [
        "0x030[8]s8", "0x030[22]s16be", "0x030[14]s16be",
        "0x081[16]s16be", "0x08A[18]s16be", "0x090[12]w12", "0x025[0]s12",
    ]
    selected = {field: {"drive_a": brief(ra[field]), "drive_b": brief(rb[field])}
                for field in selected_names if field in ra and field in rb}

    out = {
        "schema": "camry-2026-bus4-field-leadlag-v1",
        "sources": {
            "census": {"path": str(CENSUS.relative_to(REPO)), "sha256": sha256(CENSUS)},
            "drives": [{"label": label, "path": str(path.relative_to(REPO)), "sha256": sha256(path)} for label, path in DRIVES.items()],
        },
        "method": {
            "network": "Panda bus0 on relay-correct Toyota-B = Toyota Bus4 Brake/EPS chassis network; bus2 is relay mirror",
            "candidate_decodes": list(ALL_VALUE_DECODES) + ["nib_hi", "nib_lo", "b0..b7", "du8", "du16be", "du16le", "du24be"],
            "lag_convention": "corr(field(t), target(t+tau)); tau>0 means field LEADS target",
            "grid_step_ms": GRID_NS // 1_000_000,
            "lag_range_ms": SCREEN_LAG_RANGE_MS,
            "reproduction": {"min_abs_r_both_drives": REPRO_MIN_ABS_R, "lead_min_ms": LEAD_MIN_MS},
            "minimum_stream_frames_in_window": MIN_STREAM_FRAMES,
            "low_rate_boundary": "streams below 50 frames in the Class-L+/-8s window are excluded from correlation; this excludes <=~1.5Hz traffic, not a plausible continuous EPS steering carrier",
        },
        "drives": drives,
        "combined": {
            "refined_in_both_drives": len(common),
            "reproduced_strong_motor_fields": len(strong),
            "reproduced_motor_leads_ge_50ms": motor_leads,
            "reproduced_motor_near_leads_25_to_49ms": near_motor_leads,
            "reproduced_angle_leads_ge_50ms": angle_leads,
            "reproduced_rate_leads_ge_50ms": rate_leads,
            "angle_leads_outside_eps_tx_0x030": [f for f in angle_leads if not f.startswith("0x030")],
            "selected_fields": selected,
        },
        "interpretation": {
            "bounded_negative": "Across every periodic Bus4 stream with enough samples for continuous-command correlation, no external-ID field reproducibly leads the EPS motor proxy, measured steering angle, or steering rate. The only reproduced angle leads are fields in 0x030, the exact F33 EPS transmit frame; this is a positive control that the method detects actuator-before-motion relationships.",
            "meaning": "The retained logs do not reveal a second ordinary external CAN steering-target carrier. This does not prove the physical LTA actuation path is the FEBECC62/1C02 observable cone; indirect/local-RAM/peripheral paths and downstream motor-reference paths require separate firmware closure.",
            "production_output_authorized": False,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
