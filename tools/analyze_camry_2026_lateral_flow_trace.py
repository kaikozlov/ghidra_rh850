#!/usr/bin/env python3
"""Deterministic Camry TSS3 lateral flow-trace artifact.

Recomputes, from the two retained relay-correct drives (plus the parked
censuses for the absence scope), every number claimed by the 2026-08-29
exhaustive lateral flow trace:

- absence of EPS telemetry Tx PDUs (0x351/0x394/0x4A3/0x4C8), the protected
  ingress 0x0B6, and legacy lateral IDs, with 0x030/0x081 as controls;
- the 0x081 steering-reference word: nearest-time-paired byte equality with
  the 0x08A B18:B19 request word, the B8:B9 duplicate-word negative, and the
  manual-state SAS-scale fit;
- the full 0x08A byte census: constants, latch-mirror bits, active flags,
  the B26 mod-64 freshness counter, and the damping-gain absence;
- SDG (B21=18) request content vs measured SAS;
- plant closure: request-vs-SAS lag table and gain, 30 s subinterval
  tracking, and the motor-proxy-vs-word/SAS triangle;
- the delayed-grant/ack negative across the sixteen DLC-32 bus-0 streams;
- the 0x160 "delayed SAS echo" correction (window-restricted correlation);
- the refuted 0x19C "LTA cadence flip" (phase dilution).

All pairings are nearest-neighbour/batch granular per CORR-136: logMonoTime
is the loggerd publication time, so no sub-10 ms ordering is claimed.

Output: data/generated/camry_2026_lateral_flow_trace.json (byte-stable).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data/generated/camry_2026_lateral_flow_trace.json"

DRIVES = {
    "drive_a": "targets/camry-2026/raw-20260827/camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": "targets/camry-2026/raw-20260827/camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}
PARKED = {
    "post_repin_nrtd": "targets/camry-2026/raw-20260827/camry_post_repin_nrtd_20260827.json.gz",
    "post_repin_ready": "targets/camry-2026/raw-20260827/camry_post_repin_ready_20260827.json.gz",
}

ABSENT_IDS = [0x351, 0x394, 0x4A3, 0x4C8, 0x0B6, 0x131, 0x2E4]
CONTROL_IDS = [0x030, 0x081]
DLC32_BUS0 = [0x025, 0x030, 0x081, 0x08A, 0x090, 0x0C9, 0x0CA, 0x0D7,
              0x0FE, 0x1B2, 0x1FD, 0x274, 0x371, 0x5AE, 0x5AF, 0x5B0]
KEEP_SRC0 = sorted(set(DLC32_BUS0) | {0x19C})
BUS1_KEEP = [0x160]

# 1 word-ct at the F33 B6 scale in 0x025-coarse-count units:
# 1 word-ct = 0.05730274202574147 deg; 1 SAS-ct = 1.5 deg.
SAS_CT_PER_WORD_CT = 0.05730274202574147 / 1.5


def signed(value: int, bits: int) -> int:
    return value - (1 << bits) if value >= (1 << (bits - 1)) else value


def word(data: bytes, lo: int, hi: int) -> int:
    return signed(int.from_bytes(data[lo:hi], "big"), 8 * (hi - lo))


def sas_ct(data: bytes) -> int:
    """House 0x025 decode: signed12(B0[3:0]:B1) coarse at 1.5 deg/ct."""
    return signed(((data[0] & 0x0F) << 8) | data[1], 12)


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None, None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None, None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / (sxx * syy) ** 0.5, sxy / sxx


def r6(x):
    return None if x is None else round(x, 6)


def batch(ts: float) -> int:
    return int(ts * 100)


def parse_drive(path: Path):
    counts = Counter()                       # (src, addr) over every incoming frame
    streams = {a: [] for a in KEEP_SRC0}     # src==0 only: (ts, bytes)
    b1_streams = {a: [] for a in BUS1_KEEP}  # src==1 only: (ts, bytes)
    total = 0
    uncompressed = hashlib.sha256()
    with gzip.open(path, "rb") as fh:
        for line in fh:
            uncompressed.update(line)
            row = json.loads(line)
            total += 1
            src, addr = row[2], row[3]
            counts[(src, addr)] += 1
            if src == 0 and addr in streams:
                streams[addr].append((row[1] / 1e9, bytes.fromhex(row[4])))
            elif src == 1 and addr in b1_streams:
                b1_streams[addr].append((row[1] / 1e9, bytes.fromhex(row[4])))
    for series in list(streams.values()) + list(b1_streams.values()):
        series.sort(key=lambda p: p[0])
    return total, uncompressed.hexdigest(), counts, streams, b1_streams


def id11_interval(rows_08a):
    """Single merged B21==11 interval (gap < 0.5 s) per retained drive."""
    ts = [t for t, d in rows_08a if d[21] == 11]
    assert ts, "no B21==11 frames"
    intervals = []
    start = prev = ts[0]
    for t in ts[1:]:
        if t - prev >= 0.5:
            intervals.append((start, prev))
            start = t
        prev = t
    intervals.append((start, prev))
    assert len(intervals) == 1, "expected exactly one merged ID11 interval"
    return intervals[0]


def state_intervals(rows_08a, b21, gap=0.5, min_len=0.0):
    ts = [t for t, d in rows_08a if d[21] == b21]
    out = []
    for t in ts:
        if out and t - out[-1][1] < gap:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [(a, b) for a, b in out if b - a >= min_len]


def nearest(series, t, tol):
    """Index of the nearest series frame within tol seconds, else None.

    With tol=None, returns the nearest frame regardless of distance.
    """
    lo, hi = 0, len(series) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if series[mid][0] < t:
            lo = mid + 1
        else:
            hi = mid - 1
    cands = (hi, lo) if tol is not None else (hi, lo, hi + 1)
    best = None
    for j in cands:
        if 0 <= j < len(series):
            d = abs(series[j][0] - t)
            if tol is not None and d > tol:
                continue
            if best is None or d < abs(series[best][0] - t):
                best = j
    return best


def mirror_section(rows_081, rows_08a, rows_025):
    """Nearest-in-time paired byte equality of the 0x081 B16:B17 word vs 0x08A words."""
    a_series = [(t, d) for t, d in rows_08a]

    strata = Counter()
    dup_eq = 0
    dt_hist = Counter()
    b0_pairs = []
    prev81 = None
    for t, d81 in rows_081:
        w81 = word(d81, 16, 18)
        static81 = prev81 is not None and abs(w81 - prev81) <= 2
        prev81 = w81
        j = nearest(a_series, t, None)
        if j is None:
            continue
        _, da = a_series[j]
        w_req = word(da, 18, 20)
        w_dup = word(da, 8, 10)
        state = da[21]
        active = state == 11
        dt = abs(a_series[j][0] - t)
        dt_bin = "le10ms" if dt <= 0.010 else ("le30ms" if dt <= 0.030 else "gt30ms")
        dt_hist[dt_bin] += 1
        strata[f"all_{active}"] += 1
        eq = w81 == w_req
        if eq:
            strata[f"eq_{active}"] += 1
        dup_eq += w81 == w_dup
        k = j - 1
        static_both = False
        if k >= 0:
            slew_a = abs(w_req - word(a_series[k][1], 18, 20))
            static_both = static81 and slew_a <= 2
            strata["static_both" if static_both else "moving"] += 1
            if eq:
                strata["eq_static_both" if static_both else "eq_moving"] += 1
        if not active:
            j25 = nearest(rows_025, t, 0.020)
            if j25 is not None:
                b0_pairs.append((w81, sas_ct(rows_025[j25][1])))

    def frac(num_key, den_key):
        den = strata[den_key]
        return r6(strata[num_key] / den) if den else None

    # batch-median comparison: phase-robust under CORR-136 batching
    by_batch_81 = {}
    for t, d in rows_081:
        by_batch_81.setdefault(batch(t), []).append(word(d, 16, 18))
    by_batch_a = {}
    for t, d in rows_08a:
        by_batch_a.setdefault(batch(t), []).append((word(d, 18, 20), d[21]))
    shared = sorted(set(by_batch_81) & set(by_batch_a))
    med_eq = Counter()
    for b in shared:
        m81 = statistics.median(by_batch_81[b])
        frames_a = by_batch_a[b]
        ma = statistics.median([w for w, _ in frames_a])
        states = {s for _, s in frames_a}
        med_eq["shared"] += 1
        med_eq["eq_le1"] += abs(m81 - ma) <= 1
        med_eq["eq_exact"] += m81 == ma
        if states == {11}:
            med_eq["id11_shared"] += 1
            med_eq["id11_eq_le1"] += abs(m81 - ma) <= 1
            med_eq["id11_eq_exact"] += m81 == ma

    slope = r = None
    if len(b0_pairs) >= 100:
        r, slope = pearson([p[0] for p in b0_pairs], [p[1] for p in b0_pairs])
    paired = sum(v for k, v in strata.items() if k.startswith("all_"))
    return {
        "batch_median_comparison": {
            "definition": ("per shared publication batch: |median(0x081 B16:B17) - "
                           "median(0x08A B18:B19)| <= 1 count; robust to publication phase"),
            "shared_batches": med_eq["shared"],
            "equality_le1_fraction": r6(med_eq["eq_le1"] / med_eq["shared"]) if med_eq["shared"] else None,
            "equality_exact_fraction": r6(med_eq["eq_exact"] / med_eq["shared"]) if med_eq["shared"] else None,
            "id11_shared_batches": med_eq["id11_shared"],
            "id11_equality_le1_fraction": r6(med_eq["id11_eq_le1"] / med_eq["id11_shared"]) if med_eq["id11_shared"] else None,
            "id11_equality_exact_fraction": r6(med_eq["id11_eq_exact"] / med_eq["id11_shared"]) if med_eq["id11_shared"] else None,
        },
        "definition": {
            "pairing": ("each bus-0 0x081 frame paired to the nearest-in-time bus-0 0x08A "
                        "frame; publication-granular per CORR-136"),
            "equality": "signed16 0x081 B16:B17 == signed16 0x08A B18:B19",
            "static": "both words moved <=2 counts vs their own predecessors",
        },
        "paired_frames": paired,
        "pair_dt_buckets": dict(sorted(dt_hist.items())),
        "id11_paired": strata["all_True"],
        "id11_equality_fraction": frac("eq_True", "all_True"),
        "manual_paired": strata["all_False"],
        "manual_equality_fraction": frac("eq_False", "all_False"),
        "static_both_paired": strata["static_both"],
        "static_both_equality_fraction": frac("eq_static_both", "static_both"),
        "moving_equality_fraction": frac("eq_moving", "moving"),
        "duplicate_word_B8_B9_equality_fraction": r6(dup_eq / paired) if paired else None,
        "manual_state_word_vs_sas_ct": {
            "n": len(b0_pairs),
            "pearson_r": r6(r),
            "slope_sas_ct_per_word": r6(slope),
            "implied_deg_per_word": r6(slope * 1.5) if slope else None,
            "expected_f33_b6_scale_deg_per_word": 0.05730274202574147,
        },
    }


def byte_census(rows_08a):
    per_byte = {}
    for i in range(32):
        vals = sorted({d[i] for _, d in rows_08a})
        per_byte[f"B{i}"] = {
            "distinct": len(vals),
            **({"values": vals} if len(vals) <= 6 else {"min": vals[0], "max": vals[-1]}),
        }
    n = len(rows_08a)
    latch = sum(1 for _, d in rows_08a if d[3] & 0x08)
    mirrors = {}
    for byte_i, bit in ((6, 0), (7, 0), (20, 7)):
        agree = sum(1 for _, d in rows_08a if ((d[byte_i] >> bit) & 1) == ((d[3] >> 3) & 1))
        mirrors[f"B{byte_i}[{bit}]"] = r6(agree / n)
    active = [(t, d) for t, d in rows_08a if d[21] == 11]
    flags = {}
    for byte_i, bit in ((22, 4), (23, 5), (4, 7)):
        set_active = sum(1 for _, d in active if (d[byte_i] >> bit) & 1)
        flags[f"B{byte_i}[{bit}]"] = {
            "set_fraction_b21_11": r6(set_active / len(active)) if active else None,
        }
    steps_ok = 0
    breaks = []
    prev = None
    for t, d in rows_08a:
        v = d[26]
        if prev is not None:
            if (prev + 1) % 64 == v:
                steps_ok += 1
            else:
                breaks.append({"ts_s": r6(t), "prev": prev, "next": v})
        prev = v
    damping_bytes = [i for i in range(32)
                     if i not in (3, 8, 9, 10, 11, 17, 18, 19, 21, 24, 26, 28, 29, 30, 31)]
    return {
        "frames": n,
        "per_byte": per_byte,
        "cruise_latch_B3_3_set_fraction": r6(latch / n),
        "latch_mirror_agreement": mirrors,
        "active_flags": flags,
        "B26_freshness_counter": {
            "step_fraction_plus1_mod64": r6(steps_ok / (n - 1)) if n > 1 else None,
            "break_count": len(breaks),
            "breaks_first5": breaks[:5],
        },
        "damping_gain_absence": {
            "unnamed_bytes_distinct": {f"B{i}": per_byte[f"B{i}"]["distinct"]
                                       for i in damping_bytes},
            "B24_distinct": per_byte["B24"]["distinct"],
            "conclusion": ("B24 is the only gain-shaped byte (recorder assist alphabet); no "
                           "unnamed 0x08A byte carries a {0/50/100}-style 0.01-LSB gain "
                           "alphabet, so the recorder's damping field has no wire carrier "
                           "on 0x08A"),
        },
    }


def sdg_section(rows_08a, rows_025):
    intervals = state_intervals(rows_08a, 18)
    out = []
    for a, b in intervals:
        frames = [(t, d) for t, d in rows_08a if d[21] == 18 and a <= t <= b]
        words = [word(d, 18, 20) for _, d in frames]
        entry = {
            "start_s": r6(a), "end_s": r6(b), "duration_s": r6(b - a),
            "frames": len(frames),
            "word_min": min(words), "word_max": max(words),
            "word_distinct": len(set(words)),
            "mean_abs_word": r6(sum(abs(w) for w in words) / len(words)),
        }
        if b - a >= 1.0:
            xs, ys = [], []
            for t, d in frames:
                j = nearest(rows_025, t, 0.020)
                if j is not None:
                    xs.append(word(d, 18, 20))
                    ys.append(sas_ct(rows_025[j][1]))
            r, slope = pearson(xs, ys) if len(xs) >= 20 else (None, None)
            entry["long_interval"] = True
            entry["word_vs_sas_pearson_r"] = r6(r)
            entry["word_vs_sas_slope_sas_ct_per_word"] = r6(slope)
        else:
            entry["long_interval"] = False
        out.append(entry)
    return {"interval_definition": "B21==18 runs merged at <0.5 s gaps", "intervals": out}


def plant_section(rows_08a, rows_081, rows_025, rows_030, id11):
    a, b = id11
    frames = [(t, d) for t, d in rows_08a if d[21] == 11 and a <= t <= b]
    lag_table = []
    for lag_ms in range(-50, 275, 25):
        xs, ys = [], []
        for t, d in frames:
            j = nearest(rows_025, t + lag_ms / 1000.0, 0.020)
            if j is not None:
                xs.append(word(d, 18, 20))
                ys.append(sas_ct(rows_025[j][1]))
        r, slope = pearson(xs, ys)
        lag_table.append({"lag_ms": lag_ms, "n": len(xs), "pearson_r": r6(r),
                          "slope_sas_ct_per_word": r6(slope)})
    best = max((e for e in lag_table if e["pearson_r"] is not None),
               key=lambda e: abs(e["pearson_r"]))
    gain = (r6(best["slope_sas_ct_per_word"] / SAS_CT_PER_WORD_CT)
            if best["slope_sas_ct_per_word"] else None)
    subs = []
    t0 = a
    while t0 < b:
        t1 = min(t0 + 30.0, b)
        xs, ys = [], []
        for t, d in frames:
            if t0 <= t < t1:
                j = nearest(rows_025, t, 0.020)
                if j is not None:
                    xs.append(word(d, 18, 20))
                    ys.append(sas_ct(rows_025[j][1]))
        r, _ = pearson(xs, ys) if len(xs) >= 20 else (None, None)
        subs.append({"start_s": r6(t0), "end_s": r6(t1), "n": len(xs), "pearson_r": r6(r)})
        t0 = t1
    tri = {}
    m_frames = [(t, d) for t, d in rows_030 if a <= t <= b]
    for name, series, extract in (
            ("vs_reference_word_081", rows_081, lambda d: word(d, 16, 18)),
            ("vs_sas", rows_025, lambda d: sas_ct(d))):
        by_batch = {}
        for t, d in series:
            by_batch.setdefault(batch(t), []).append((t, d))
        xs, ys = [], []
        for t, d in m_frames:
            cand = by_batch.get(batch(t))
            if not cand:
                continue
            dt, dd = min(cand, key=lambda p: abs(p[0] - t))
            if abs(dt - t) <= 0.020:
                xs.append(word(d, 22, 24))
                ys.append(extract(dd))
        r, _ = pearson(xs, ys) if len(xs) >= 20 else (None, None)
        tri[name] = {"n": len(xs), "pearson_r": r6(r)}
    return {
        "id11_word_vs_sas_lag_table": lag_table,
        "best_lag": best,
        "plant_gain_mrad_per_mrad": gain,
        "b_style_30s_subinterval_word_vs_sas_r": subs,
        "motor_proxy_triangle": {
            "definition": "0x030 B22:B23 paired to the same-batch (+/-20 ms) partner inside ID11",
            **tri,
        },
    }


def delayed_ack_section(streams, onsets):
    results = {}
    for label, onset in onsets.items():
        flips = []
        for addr in DLC32_BUS0:
            series = streams[addr]
            pre = [d for t, d in series if onset - 4.0 <= t <= onset - 1.0]
            if len(pre) < 5:
                continue
            pre_med = [statistics.median([d[i] for d in pre]) for i in range(32)]
            for k in range(1, 11):
                lo = onset + 0.5 * k
                win = [d for t, d in series if lo <= t < lo + 0.5]
                if len(win) < 5:
                    continue
                for i in range(32):
                    med = statistics.median([d[i] for d in win])
                    if med != pre_med[i]:
                        persistent = sum(1 for v in win if v == med) / len(win) >= 0.95
                        pre_persistent = sum(1 for v in pre if v == pre_med[i]) / len(pre) >= 0.95
                        if persistent and pre_persistent:
                            flips.append({"addr": f"0x{addr:03X}", "byte": i,
                                          "window_start_s": r6(lo),
                                          "before": pre_med[i], "after": med})
        results[label] = {"onset_s": r6(onset), "delayed_persistent_flips": flips,
                          "flip_count": len(flips)}
    return {
        "definition": ("per byte: >=95%-persistent value in each +0.5..+5.0 s window "
                       "(0.5 s steps) vs the [-4,-1] s pre-window; DLC-32 bus-0 streams"),
        "onsets": results,
        "classification": ("zero delayed persistent flips of any class on either clean onset; "
                           "no grant/ack announcement exists on the captured Bus-4 broadcast"),
    }


def x160_section(b1_streams, rows_025, id11):
    v160 = b1_streams[0x160]
    decodes = {
        "B22s16be": lambda d: signed(int.from_bytes(d[22:24], "big"), 16),
        "B21lo3_0_B22_12bit": lambda d: signed(((d[21] & 0x0F) << 8) | d[22], 12),
    }
    out = {}
    a, b = id11
    for wname, pred in (("full_drive", lambda t: True),
                        ("id11_window", lambda t: a <= t <= b),
                        ("outside_id11", lambda t: not (a <= t <= b))):
        sel = [(t, d) for t, d in v160 if pred(t)]
        for dn, fn in decodes.items():
            xs, ys = [], []
            for t, d in sel:
                j = nearest(rows_025, t, 0.020)
                if j is not None:
                    xs.append(fn(d))
                    ys.append(sas_ct(rows_025[j][1]))
            r, slope = pearson(xs, ys)
            out[f"{wname}/{dn}"] = {"n": len(xs), "pearson_r": r6(r),
                                    "slope_sas_ct_per_count": r6(slope)}
    return {
        "definition": "0x160 (bus 1) decodes vs 0x025 coarse SAS ct, nearest join +/-20 ms, zero lag",
        "results": out,
        "provenance_note": ("the r=+0.9963/+0.8698 echo statistics in camry_2026_bus1_field_leadlag.json "
                            "were computed inside the Class-L window only (frames_in_window 1285/2927); "
                            "the same decodes over the full drive do not reproduce an echo"),
    }


def p19c_section(streams, id11):
    series = streams[0x19C]
    if not series:
        return {"present": False}
    buckets = []
    t0 = series[0][0]
    n_buckets = int((series[-1][0] - t0) // 30) + 1
    for k in range(n_buckets):
        lo = t0 + 30 * k
        dts = [series[i + 1][0] - series[i][0] for i in range(len(series) - 1)
               if lo <= series[i][0] < lo + 30]
        if dts:
            buckets.append((lo, statistics.median(dts)))
    phases = []
    cur = None
    for lo, med in buckets:
        mode = "fast" if med < 0.055 else "slow"
        if cur and cur["mode"] == mode:
            cur["end"] = lo + 30
        else:
            if cur:
                phases.append(cur)
            cur = {"mode": mode, "start": lo, "end": lo + 30}
    if cur:
        phases.append(cur)
    a, b = id11
    contained = any(p["mode"] == "fast" and p["start"] <= a and b <= p["end"] for p in phases)
    return {
        "present": True,
        "definition": "0x19C bus-0 median inter-arrival per 30 s bucket; fast < 55 ms",
        "phases": [{"mode": p["mode"], "start_s": r6(p["start"]), "end_s": r6(p["end"])}
                   for p in phases],
        "id11_contained_in_fast_phase": contained,
    }


def main() -> int:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    drives = {}
    for name, rel in DRIVES.items():
        path = REPO / rel
        total, sha_u, counts, streams, b1_streams = parse_drive(path)
        rows_08a = streams[0x08A]
        id11 = id11_interval(rows_08a)
        absent = {}
        for aid in ABSENT_IDS:
            per_src = {f"src{s}": counts.get((s, aid), 0) for s in (0, 1, 2)}
            absent[f"0x{aid:03X}"] = {"total": sum(per_src.values()), **per_src}
        controls = {f"0x{c:03X}": {"src0": counts.get((0, c), 0), "src2": counts.get((2, c), 0)}
                    for c in CONTROL_IDS}
        drives[name] = {
            "source": rel,
            "sha256_compressed": hashlib.sha256(path.read_bytes()).hexdigest(),
            "sha256_uncompressed_ndjson": sha_u,
            "incoming_frames": total,
            "absent_carriers": absent,
            "control_carriers": controls,
            "id11_interval": {"start_s": r6(id11[0]), "end_s": r6(id11[1]),
                              "duration_s": r6(id11[1] - id11[0]),
                              "frames_bus0": sum(1 for t, d in rows_08a
                                                 if d[21] == 11 and id11[0] <= t <= id11[1])},
            "reference_word_081": mirror_section(streams[0x081], rows_08a, streams[0x025]),
            "a08A_byte_census": byte_census(rows_08a),
            "sdg_states": sdg_section(rows_08a, streams[0x025]),
            "plant_closure": plant_section(rows_08a, streams[0x081], streams[0x025],
                                           streams[0x030], id11),
            "x160_echo_correction": x160_section(b1_streams, streams[0x025], id11),
            "p19c_phase_refutation": p19c_section(streams, id11),
            "delayed_ack": delayed_ack_section(streams, {"id11_onset": id11[0]}),
        }

    parked = {}
    for name, rel in PARKED.items():
        data = json.loads(gzip.open(REPO / rel, "rb").read())
        cnt = Counter(fr["addr"] for fr in data["frames"])
        parked[name] = {
            "source": rel,
            "frames": len(data["frames"]),
            "absent_carriers": {f"0x{aid:03X}": cnt.get(aid, 0) for aid in ABSENT_IDS},
            "controls": {f"0x{c:03X}": cnt.get(c, 0) for c in CONTROL_IDS},
        }

    art = {
        "schema": "camry-2026-lateral-flow-trace-v1",
        "generated_from": ("retained relay-correct 2026-08-27 Camry drives; nearest-neighbour "
                           "and batch-granular pairings per CORR-136"),
        "production_output_authorized": False,
        "drives": drives,
        "parked_censuses": parked,
        "interpretation": {
            "conclusion": (
                "The stock-LTA actuation command never appears on any captured segment: 0x0B6, the "
                "four EPS telemetry Tx PDUs, and any B6-shaped/grant-shaped carrier are absent from "
                "every retained capture, while 0x030 and 0x081 stream throughout. The captured Bus-4 "
                "broadcast is therefore not the full EPS interface, and the wire carries request + "
                "mirrors only."
            ),
            "new_carrier": (
                "0x081 B16:B17 (s16BE) byte-equals the 0x08A B18:B19 request word at publication "
                "granularity in the LTA state and equals the measured 0x025 angle times the F33 B6 "
                "scale factor in the manual state: one mode-switching steering-reference quantity, "
                "republished at ~32 Hz beside EPS."
            ),
            "proof_boundary": (
                "Batched loggerd timestamps (CORR-136) bound all orderings; equality and correlation "
                "statistics do not establish which ECU produces 0x08A/0x081, a request-to-winner "
                "transform, or any grant. No 0x08A-to-B6 transform is established. "
                "Production output remains unauthorized."
            ),
        },
    }
    out_path.write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
    print(f"wrote {out_path} ({out_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
