#!/usr/bin/env python3
"""Bound unsigned FRC lateral egress over native Toyota Bus 1 (2026 Camry TSS3).

Deterministic four-tier producer for
data/generated/camry_2026_bus1_frc_egress_bounds.json, replacing the prior
invalid inference "no simple Bus-1 field correlates with protected 0x08A ->
no lateral FRC egress / private handoff" with an explicit method-bounded
negative. A downstream proxy can transform, arbitrate, multiplex, or
synthesize its protected publication from multiple FRC fields, so each tier
declares exactly what it covers and the artifact records what remains open.

Tiers (kept separate in the schema):
  1. exhaustive 541,984-field/drive contiguous 1..16-bit semantic B3..end
     +/-300 ms / 25 ms Pearson census against same-segment nearest native
     bus-2 0x08A (<=30 ms), source and shifted target both B21=11;
  2. exhaustive 898,104-spec zero-lag/state screen over every contiguous
     1..24-bit and 32-bit field (whole frame, BE/LE, unsigned/signed);
  3. stratified 450-candidate wider/nonlinear +/-1 s refinement -- this is
     NOT an exhaustive lag search; only the tier-2 zero-lag screen is
     exhaustive;
  4. reproduced activation/clear transition-edge screen.

All protected-target joins use the native Panda bus-2 0x08A DLC-32 copies
(forwarded bus-0 copies give identical ID11 intervals and edges). No runtime
or timestamp is embedded; output ordering and numeric rounding are deterministic.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
DRIVES = {
    "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}
OUT_DEFAULT = REPO / "data/generated/camry_2026_bus1_frc_egress_bounds.json"

PERIODIC_MIN = 50
# Tier 1 (exhaustive lag census)
T1_LAGS = np.arange(-300, 301, 25, dtype=int)
T1_BLOCK = 384
T1_JOIN_NS = 30_000_000
# Tier 2/3 (exhaustive zero-lag state screen + stratified refinement)
WIDTHS = list(range(1, 25)) + [32]
STATES = (0, 11, 18)
T2_JOIN_NS = 40_000_000
REFINE_CAP = 450
SCREEN_TOP = 12
T3_LAGS_MS = list(range(-1000, 1001, 25))
# Tier 4 (transition edges)
NS = 1_000_000_000
EDGE_PRE_MS, EDGE_POST_MS, EDGE_WIN_MS = 100, 100, 2_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# shared loading
# ---------------------------------------------------------------------------

def load_drive(path: Path):
    """One pass: bus-1 streams, native bus-2 0x08A targets, bus-0 0x025 angle."""
    b1 = defaultdict(lambda: defaultdict(list))
    a8 = defaultdict(list)
    angle = defaultdict(list)
    event = Counter()
    total = 0
    with gzip.open(path, "rt") as f:
        for line in f:
            seg, t, bus, addr, hx = json.loads(line)
            d = bytes.fromhex(hx)
            total += 1
            event[(seg, t)] += 1
            if bus == 1:
                b1[(addr, len(d))][seg].append((t, d))
            elif bus == 2 and addr == 0x08A and len(d) == 32:
                a8[seg].append((t, d))
            elif bus == 0 and addr == 0x025:
                angle[seg].append((t, decode_angle(d)))
    for seg in a8:
        a8[seg].sort()
    for seg in angle:
        angle[seg].sort()
    return {"b1": b1, "a8": a8, "angle": angle, "event": event, "total": total}


def decode_angle(d: bytes) -> float:
    bits = np.unpackbits(np.frombuffer(d, dtype=np.uint8), bitorder="big")
    coarse = int(bits[3:15].astype(np.uint64) @ (1 << np.arange(11, -1, -1, dtype=np.uint64)))
    fine = int(bits[39:43].astype(np.uint64) @ (1 << np.arange(3, -1, -1, dtype=np.uint64)))
    if coarse & 0x800:
        coarse -= 1 << 12
    if fine & 0x8:
        fine -= 1 << 4
    return coarse * 1.5 + fine * 0.1


def id11_intervals(a8) -> list[dict]:
    rows = sorted((t, seg, d) for seg, rr in a8.items() for t, d in rr)
    out, on = [], None
    last = None
    for t, seg, d in rows:
        if d[21] == 11 and on is None:
            on, on_seg = t, seg
        if d[21] != 11 and on is not None:
            out.append({"start_segment": int(on_seg), "end_segment": int(seg),
                        "duration_s": round((t - on) / NS, 9)})
            on = None
        last = (t, seg)
    if on is not None:
        out.append({"start_segment": int(on_seg), "end_segment": int(last[1]),
                    "duration_s": round((last[0] - on) / NS, 9)})
    return out


# ---------------------------------------------------------------------------
# tier 1: exhaustive 1..16-bit semantic-field lag census
# ---------------------------------------------------------------------------

def t1_nearest(rows, t, maxgap=T1_JOIN_NS):
    ts = [r[0] for r in rows]
    i = bisect.bisect_left(ts, t)
    js = [j for j in (i - 1, i) if 0 <= j < len(rows)]
    if not js:
        return None
    j = min(js, key=lambda j: abs(ts[j] - t))
    return rows[j] if abs(ts[j] - t) <= maxgap else None


def t1_active_frames(stream, a8):
    out = []
    for seg, rows in stream.items():
        if seg not in a8:
            continue
        for t, d in rows:
            r = t1_nearest(a8[seg], t)
            if r is not None and r[1][21] == 11:
                out.append((seg, t, d))
    if not out:
        return None
    return (np.frombuffer(b"".join(r[2] for r in out), dtype=np.uint8).reshape(-1, len(out[0][2])),
            np.array([r[1] for r in out], np.int64),
            np.array([r[0] for r in out], np.int16))


def t1_lag_targets(times, segs, a8):
    Y = np.zeros((len(times), len(T1_LAGS)))
    V = np.zeros_like(Y, dtype=bool)
    for j, lag in enumerate(T1_LAGS):
        for i, (t, seg) in enumerate(zip(times, segs)):
            r = t1_nearest(a8.get(int(seg), []), int(t) + int(lag) * 1_000_000)
            if r is not None and r[1][21] == 11:
                V[i, j] = True
                Y[i, j] = int.from_bytes(r[1][18:20], "big", signed=True)
    return Y, V


def t1_candidates(frames):
    payload = frames[:, 3:]
    for order in ("big", "little"):
        bits = np.unpackbits(payload, axis=1, bitorder=order)
        nb = bits.shape[1]
        for width in range(1, 17):
            weights = (1 << np.arange(width - 1, -1, -1, dtype=np.uint64)) if order == "big" \
                else (1 << np.arange(width, dtype=np.uint64))
            for start in range(nb - width + 1):
                u = (bits[:, start:start + width].astype(np.uint64) @ weights).astype(np.float64)
                yield f"{order}:bit{start}:u{width}", u
                if width > 1:
                    sign = 1 << (width - 1)
                    yield f"{order}:bit{start}:s{width}", np.where(u >= sign, u - (1 << width), u)


def t1_score_block(keys, X, Y, V):
    best_r = np.zeros(len(keys))
    best_lag = np.zeros(len(keys), dtype=int)
    for j, lag in enumerate(T1_LAGS):
        v = V[:, j]
        if v.sum() < 100:
            continue
        A = X[v]
        b = Y[v, j]
        bm, bs = b.mean(), b.std()
        am, astd = A.mean(0), A.std(0)
        good = astd > 0
        r = np.zeros(len(keys))
        r[good] = ((A[:, good] - am[good]).T @ (b - bm)) / (v.sum() * astd[good] * bs)
        take = np.abs(r) > np.abs(best_r)
        best_r[take] = r[take]
        best_lag[take] = lag
    return [{"field": k, "pearson_r": round(float(r), 9), "lag_ms": int(l),
             "unique": int(len(np.unique(X[:, i]))),
             "range": [float(X[:, i].min()), float(X[:, i].max())]}
            for i, (k, r, l) in enumerate(zip(keys, best_r, best_lag)) if X[:, i].std() > 0]


def tier1(loaded, streams):
    per_drive = {n: {} for n in loaded}
    for key in streams:
        sk = f"0x{key[0]:03X}/{key[1]}"
        for n, d in loaded.items():
            stream = d["b1"][key]
            af = t1_active_frames(stream, d["a8"])
            if af is None:
                per_drive[n][sk] = {"samples": 0, "candidate_fields": 0,
                                    "positive_hits_abs_r_ge_0_20": []}
                continue
            frames, times, segs = af
            Y, V = t1_lag_targets(times, segs, d["a8"])
            keys, cols, hits = [], [], []
            count = 0

            def flush():
                if not keys:
                    return
                for row in t1_score_block(keys, np.column_stack(cols), Y, V):
                    if row["lag_ms"] > 0 and abs(row["pearson_r"]) >= 0.20:
                        hits.append(row)
                keys.clear(), cols.clear()

            for k, x in t1_candidates(frames):
                count += 1
                keys.append(k)
                cols.append(x)
                if len(keys) >= T1_BLOCK:
                    flush()
            flush()
            hits.sort(key=lambda x: (-abs(x["pearson_r"]), x["field"]))
            per_drive[n][sk] = {"samples": len(frames), "candidate_fields": count,
                                "positive_hits_abs_r_ge_0_20": hits}
    reproduced = []
    for sk in [f"0x{a:03X}/{d}" for a, d in streams]:
        ma = {x["field"]: x for x in per_drive["drive_a"][sk]["positive_hits_abs_r_ge_0_20"]}
        mb = {x["field"]: x for x in per_drive["drive_b"][sk]["positive_hits_abs_r_ge_0_20"]}
        for f in ma.keys() & mb.keys():
            a, b = ma[f], mb[f]
            if a["pearson_r"] * b["pearson_r"] > 0:
                reproduced.append({"stream": sk, "field": f,
                                   "min_abs_r": round(min(abs(a["pearson_r"]), abs(b["pearson_r"])), 9),
                                   "A": a, "B": b})
    reproduced.sort(key=lambda z: (-z["min_abs_r"], z["stream"], z["field"]))
    total = sum(v["candidate_fields"] for v in per_drive["drive_a"].values())
    return {
        "scope": "all 22 shared periodic native Bus-1 streams; every contiguous 1..16-bit "
                 "BE/LE field, signed+unsigned, in semantic B3..end (B0:B1 CRC and B2 alive "
                 "counter excluded); no candidate-series deduplication",
        "candidate_fields_per_drive": total,
        "lags_ms": T1_LAGS.tolist(),
        "join": "same-segment nearest native bus2 0x08A DLC32 within 30 ms; source frame "
                "and shifted target frame both require B21=11",
        "lag_convention": "corr(field(t), target(t+lag)); positive lag means Bus-1 field "
                          "leads protected 0x08A",
        "reproduced_positive_leads_abs_r_ge_0_40": [x for x in reproduced if x["min_abs_r"] >= 0.40],
        "n_reproduced_positive_leads_abs_r_ge_0_20": len(reproduced),
        "strongest_reproduced_positive_leads": reproduced[:10],
        "per_drive_sample_counts": {n: {sk: v["samples"] for sk, v in per_drive[n].items()}
                                    for n in ("drive_a", "drive_b")},
    }


# ---------------------------------------------------------------------------
# tier 2: exhaustive zero-lag/state spec screen (all 898,104 specs)
# ---------------------------------------------------------------------------

def t2_nearest_target(rows, target, shift_ns=0, max_ns=T2_JOIN_NS):
    n = len(rows)
    st = np.full(n, -1, dtype=np.int16)
    y = np.full(n, np.nan)
    segv = np.array([r[0] for r in rows], dtype=np.int32)
    tv = np.array([r[1] for r in rows], dtype=np.int64)
    for seg in np.unique(segv):
        pos = np.flatnonzero(segv == seg)
        if int(seg) not in target:
            continue
        tt, ss, yy = target[int(seg)]
        q = tv[pos] + shift_ns
        ix = np.searchsorted(tt, q)
        i0, i1 = np.clip(ix - 1, 0, len(tt) - 1), np.clip(ix, 0, len(tt) - 1)
        choose = np.where(np.abs(tt[i1] - q) < np.abs(tt[i0] - q), i1, i0)
        dd = tt[choose] - q
        ok = np.abs(dd) <= max_ns
        pp, cc = pos[ok], choose[ok]
        st[pp], y[pp] = ss[cc], yy[cc]
    return segv, tv, st, y


def corr_cols(X, y, mask):
    mask = mask & np.isfinite(y)
    n = int(mask.sum())
    out = np.full(X.shape[1], np.nan)
    if n < 8:
        return out
    A = X[mask].astype(np.float64, copy=False)
    b = y[mask].astype(np.float64, copy=False)
    sx, sy = A.sum(0), b.sum()
    sxx, syy = np.einsum("ij,ij->j", A, A), float(np.dot(b, b))
    sxy = A.T @ b
    vx, vy = sxx - sx * sx / n, syy - sy * sy / n
    good = (vx > 1e-12) & (vy > 1e-12)
    out[good] = (sxy[good] - sx[good] * sy / n) / np.sqrt(vx[good] * vy)
    return out


def rankdata(v):
    v = np.asarray(v)
    order = np.argsort(v, kind="mergesort")
    sv = v[order]
    r = np.empty(len(v), dtype=float)
    i = 0
    while i < len(v):
        j = i + 1
        while j < len(v) and sv[j] == sv[i]:
            j += 1
        r[order[i:j]] = (i + j - 1) / 2
        i = j
    return r


def monotonic_summary(x, y, bins=10):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 20 or len(np.unique(x)) < 3 or y.std() <= 0:
        return None
    rx, ry = rankdata(x), rankdata(y)
    rho = float(np.corrcoef(rx, ry)[0, 1]) if rx.std() > 0 and ry.std() > 0 else None
    order = np.argsort(x, kind="mergesort")
    groups = np.array_split(order, min(bins, len(x) // 8))
    pred = np.empty(len(x), dtype=float)
    means = []
    for g in groups:
        m = float(y[g].mean())
        pred[g] = m
        means.append((float(x[g].mean()), m, len(g)))
    denom = float(np.sum((y - y.mean()) ** 2))
    q_r2 = None if denom <= 0 else 1.0 - float(np.sum((y - pred) ** 2) / denom)
    mx = rankdata([m[0] for m in means])
    my = rankdata([m[1] for m in means])
    mono = float(np.corrcoef(mx, my)[0, 1]) if mx.std() > 0 and my.std() > 0 else None
    return {
        "spearman": None if rho is None else round(rho, 6),
        "quantile_bin_r2": None if q_r2 is None else round(q_r2, 6),
        "bin_mean_monotonic_r": None if mono is None else round(mono, 6),
    }


def deriv_corr_cols(X, y, states, segs, times, state, kind):
    ok = ((states[:-1] == state) & (states[1:] == state) & (segs[:-1] == segs[1:])
          & np.isfinite(y[:-1]) & np.isfinite(y[1:]) & (np.diff(times) > 0)
          & (np.diff(times) <= 150_000_000))
    if ok.sum() < 8:
        return np.full(X.shape[1], np.nan)
    dy = np.diff(y)
    if kind == "dxdy":
        return corr_cols(np.diff(X.astype(np.float64), axis=0), dy, ok)
    return corr_cols(X[:-1].astype(np.float64), dy, ok)


def t2_metrics(X, join):
    seg, t, st, y, = join
    out = {}
    for s in STATES:
        out[f"angle_{s}"] = corr_cols(X, y, st == s)
    for s in (11, 18):
        out[f"delta_{s}"] = deriv_corr_cols(X, y, st, seg, t, s, "dxdy")
        out[f"rate_{s}"] = deriv_corr_cols(X, y, st, seg, t, s, "xdy")
        out[f"indicator_{s}"] = corr_cols(X, (st == s).astype(np.float64), st >= 0)
    return out


def build_values(bitmat, width, order, prev=None):
    if width == 1:
        return bitmat.astype(np.uint64, copy=False)
    if order == "be":
        return (prev[:, :-1] << np.uint64(1)) | bitmat[:, width - 1:].astype(np.uint64)
    return prev[:, :-1] | (bitmat[:, width - 1:].astype(np.uint64) << np.uint64(width - 1))


def signed_view(X, width):
    sign, mod = np.uint64(1 << (width - 1)), float(1 << width)
    return np.where((X & sign) != 0, X.astype(np.float64) - mod, X.astype(np.float64))


def spec_key(s):
    return (f"0x{s['id']:03X}/{s['dlc']}:{s['order']}:{s['start']}:"
            f"{s['width']}:{'s' if s['signed'] else 'u'}")


def decode_spec_matrix(bits, sp):
    sl = bits[:, sp["start"]:sp["start"] + sp["width"]].astype(np.uint64)
    if sp["order"] == "be":
        powers = np.uint64(1) << np.arange(sp["width"] - 1, -1, -1, dtype=np.uint64)
    else:
        powers = np.uint64(1) << np.arange(0, sp["width"], dtype=np.uint64)
    x = sl @ powers
    return signed_view(x[:, None], sp["width"])[:, 0] if sp["signed"] else x.astype(np.float64)


def tiers_2_3(loaded, streams):
    targets = {n: {seg: (np.array([r[0] for r in rr], dtype=np.int64),
                         np.array([r[1][21] for r in rr], dtype=np.int16),
                         np.array([int.from_bytes(r[1][18:20], "big", signed=True) for r in rr],
                                  dtype=np.float64))
                   for seg, rr in d["a8"].items()} for n, d in loaded.items()}
    pool = {}
    searched = 0
    by_stream = {}

    def add_top(key, specs, score, ma, mb):
        v = np.nan_to_num(np.abs(score), nan=-1.0)
        k = min(SCREEN_TOP, len(v))
        take = np.argpartition(v, -k)[-k:]
        take = take[np.argsort(v[take])[::-1]]
        for i in take:
            if v[i] < 0:
                continue
            sp = specs[int(i)]
            rec = pool.setdefault(spec_key(sp), {"spec": sp, "screen": {}})
            rec["screen"][key] = {"score": round(float(v[i]), 6),
                                  "a": None if not np.isfinite(ma[i]) else round(float(ma[i]), 6),
                                  "b": None if not np.isfinite(mb[i]) else round(float(mb[i]), 6)}

    for addr, dlc in streams:
        raw, joins, bits = {}, {}, {}
        for lab, d in loaded.items():
            rows = [(s, t, dd) for s, rr in d["b1"][(addr, dlc)].items() for t, dd in rr]
            raw[lab] = np.frombuffer(b"".join(r[2] for r in rows), dtype=np.uint8).reshape(len(rows), dlc)
            joins[lab] = t2_nearest_target(rows, targets[lab])
            bits[(lab, "be")] = np.unpackbits(raw[lab], axis=1, bitorder="big")
            bits[(lab, "le")] = np.unpackbits(raw[lab], axis=1, bitorder="little")
        n_searched = 0
        for order in ("be", "le"):
            prev = {}
            for w in range(1, 33):
                Xa = build_values(bits[("drive_a", order)], w, order, prev.get("drive_a"))
                Xb = build_values(bits[("drive_b", order)], w, order, prev.get("drive_b"))
                prev = {"drive_a": Xa, "drive_b": Xb}
                if w not in WIDTHS:
                    continue
                variants = [False] if w == 1 else [False, True]
                for sg in variants:
                    A = signed_view(Xa, w) if sg else Xa
                    B = signed_view(Xb, w) if sg else Xb
                    specs = [{"id": addr, "dlc": dlc, "order": order, "start": i,
                              "width": w, "signed": sg} for i in range(Xa.shape[1])]
                    aa, bb = t2_metrics(A, joins["drive_a"]), t2_metrics(B, joins["drive_b"])
                    n_searched += len(specs)
                    for met in aa:
                        cross = np.minimum(np.abs(aa[met]), np.abs(bb[met]))
                        add_top(f"cross_{met}", specs, cross, aa[met], bb[met])
                        add_top(f"drive_a_{met}", specs, np.abs(aa[met]), aa[met], bb[met])
                        add_top(f"drive_b_{met}", specs, np.abs(bb[met]), aa[met], bb[met])
        searched += n_searched
        by_stream[f"0x{addr:03X}/{dlc}"] = n_searched

    tier2 = {
        "candidate_specs": searched,
        "candidate_count_by_stream": by_stream,
        "scope": "all 22 periodic native bus-1 (id,dlc) streams shared by both drives; no "
                 "ID/byte prefilter",
        "candidate_fields": "every contiguous 1..24-bit and 32-bit window at every legal bit "
                            "offset, serialized MSB-first and LSB-first, unsigned and signed "
                            "(except 1-bit signed duplicate)",
        "join": "same-segment nearest 0x08A within 40 ms",
        "screens": {k: [] for k in
                    [f"angle_{s}" for s in STATES] + [f"{x}_{s}" for s in (11, 18)
                                                      for x in ("delta", "rate", "indicator")]},
        "integrity_note": "B0:B1 CRC and B2 alive counter deliberately included; interpret "
                          "their hits as E2E/time artifacts, not application fields",
    }
    for key in sorted(tier2["screens"]):
        rows = sorted((r for r in pool.values() if f"cross_{key}" in r["screen"]),
                      key=lambda r: (-r["screen"][f"cross_{key}"]["score"], spec_key(r["spec"])))
        tier2["screens"][key] = [
            {"spec": spec_key(r["spec"]), "score": r["screen"][f"cross_{key}"]["score"],
             "a": r["screen"][f"cross_{key}"]["a"], "b": r["screen"][f"cross_{key}"]["b"]}
            for r in rows[:5]]

    # --- tier 3: stratified selection + refinement ---
    def best_cross(rec):
        return max((v["score"] for k, v in rec["screen"].items() if k.startswith("cross_")), default=-1)

    def best_any(rec):
        return max((v["score"] for v in rec["screen"].values()), default=-1)

    screen_keys = sorted({k for r in pool.values() for k in r["screen"]})
    selected, selected_keys = [], set()
    for key in screen_keys:
        rows = sorted((r for r in pool.values() if key in r["screen"]),
                      key=lambda r: (-r["screen"][key]["score"], spec_key(r["spec"])))
        seen_support, per_id, taken = set(), Counter(), 0
        for r in rows:
            sp = r["spec"]
            support = (sp["id"], sp["order"], sp["start"])
            if support in seen_support or per_id[sp["id"]] >= 3:
                continue
            seen_support.add(support)
            per_id[sp["id"]] += 1
            taken += 1
            sk = spec_key(sp)
            if sk not in selected_keys:
                selected.append(r)
                selected_keys.add(sk)
            if taken >= 15:
                break
    overall = sorted(pool.values(), key=lambda r: (-best_cross(r), -best_any(r), spec_key(r["spec"])))
    for r in overall:
        if len(selected) >= REFINE_CAP:
            break
        sk = spec_key(r["spec"])
        if sk not in selected_keys:
            selected.append(r)
            selected_keys.add(sk)
    refine = selected[:REFINE_CAP]

    lag_cache = {}
    best_positive = None
    best_positive_rank = None
    best_monotonic = None
    reproduced_negative_peak = None
    for r in refine:
        sp = r["spec"]
        request_best = {}
        neg_peak = {}
        for lab in ("drive_a", "drive_b"):
            d = loaded[lab]
            rows = [(s, t, dd) for s, rr in d["b1"][(sp["id"], sp["dlc"])].items() for t, dd in rr]
            ckey = (lab, sp["id"], sp["dlc"])
            if ckey not in lag_cache:
                lag_cache[ckey] = {lag: t2_nearest_target(rows, targets[lab], lag * 1_000_000)
                                   for lag in T3_LAGS_MS}
            joins = lag_cache[ckey]
            bits = np.unpackbits(
                np.frombuffer(b"".join(x[2] for x in rows), dtype=np.uint8).reshape(len(rows), sp["dlc"]),
                axis=1, bitorder="big" if sp["order"] == "be" else "little")
            x = decode_spec_matrix(bits, sp)
            req = None
            neg_r, neg_lag = None, None
            for state in STATES:
                for lag in T3_LAGS_MS:
                    _seg, _t, st, y = joins[lag]
                    m = (st == state) & np.isfinite(y)
                    if m.sum() < 8:
                        continue
                    xx, yy = x[m], y[m]
                    if xx.std() <= 0 or yy.std() <= 0:
                        continue
                    vx, vy = xx - xx.mean(), yy - yy.mean()
                    den = np.linalg.norm(vx) * np.linalg.norm(vy)
                    if den <= 1e-12:
                        continue
                    rr_ = float(np.dot(vx, vy) / den)
                    if state == 11 and (req is None or abs(rr_) > abs(req[0])):
                        req = (rr_, lag, xx.copy(), yy.copy())
                    if neg_r is None or abs(rr_) > abs(neg_r):
                        neg_r, neg_lag = rr_, lag
            if req is None:
                request_best[lab] = None
            else:
                request_best[lab] = {
                    "pearson_r": round(req[0], 6),
                    "lag_ms": req[1],
                    "state": 11,
                    "monotonic": monotonic_summary(req[2], req[3]),
                }
            neg_peak[lab] = {"r": neg_r, "lag_ms": neg_lag}

        a, b = request_best["drive_a"], request_best["drive_b"]
        if (a and b and a["lag_ms"] > 0 and b["lag_ms"] > 0
                and a["pearson_r"] * b["pearson_r"] > 0):
            min_abs = round(min(abs(a["pearson_r"]), abs(b["pearson_r"])), 6)
            cand = {
                "stream": f"0x{sp['id']:03X}/{sp['dlc']}",
                "field": f"{sp['order']}:bit{sp['start']}:{'s' if sp['signed'] else 'u'}{sp['width']}",
                "A": {k: a[k] for k in ("pearson_r", "lag_ms", "state")},
                "B": {k: b[k] for k in ("pearson_r", "lag_ms", "state")},
                "min_abs_r": min_abs,
            }
            # Equal mathematical aliases are canonicalized to the narrowest,
            # unsigned representation so the one-bit witness is stable.
            rank = (min_abs, -sp["width"], int(not sp["signed"]), spec_key(sp))
            if best_positive_rank is None or rank > best_positive_rank:
                best_positive, best_positive_rank = cand, rank

            if a["monotonic"] and b["monotonic"]:
                ar = a["monotonic"]["spearman"]
                br = b["monotonic"]["spearman"]
                if ar is not None and br is not None and ar * br > 0:
                    mono = {
                        "stream": cand["stream"],
                        "field": cand["field"],
                        "A": a,
                        "B": b,
                        "min_abs_spearman": round(min(abs(ar), abs(br)), 6),
                    }
                    if (best_monotonic is None
                            or mono["min_abs_spearman"] > best_monotonic["min_abs_spearman"]):
                        best_monotonic = mono

        na, nb = neg_peak["drive_a"], neg_peak["drive_b"]
        if na["r"] is not None and nb["r"] is not None and na["r"] * nb["r"] > 0 and sp["id"] in (0x160, 0x1A0):
            neg = {"stream": f"0x{sp['id']:03X}/{sp['dlc']}", "field": spec_key(sp),
                   "A": {"r": round(na["r"], 6), "lag_ms": na["lag_ms"]},
                   "B": {"r": round(nb["r"], 6), "lag_ms": nb["lag_ms"]}}
            if reproduced_negative_peak is None or min(abs(na["r"]), abs(nb["r"])) > reproduced_negative_peak["min_abs_r"]:
                neg["min_abs_r"] = round(min(abs(na["r"]), abs(nb["r"])), 6)
                reproduced_negative_peak = neg

    tier3 = {
        "tier_size": len(refine),
        "selection": "stratified: per screen metric (cross/drive_a/drive_b over 9 state "
                     "screens) top-15 with (id,order,start) support dedup and per-ID cap 3, "
                     "then filled to the cap by best overall cross-drive screen score",
        "boundary": "the +/-1 s / 25 ms wider-field nonlinear sweep is a stratified subset "
                    "(strongest per screen metric), NOT an exhaustive lag search; only the "
                    "tier-2 zero-lag state screen is exhaustive over all 898,104 specs",
        "lag_sweep_ms": [T3_LAGS_MS[0], T3_LAGS_MS[-1], T3_LAGS_MS[1] - T3_LAGS_MS[0]],
        "lag_convention": "corr(field(t), target(t+lag)); positive means Bus-1 field leads downstream 0x08A",
        "strongest_positive_lag_selected_candidate": best_positive,
        "strongest_selected_monotonic_at_best_level_lag": best_monotonic,
        "strongest_reproduced_0x160_0x1A0_any_lag": reproduced_negative_peak,
        "note": "strong selected 0x160/0x1A0 correlations peak at negative lag and/or fail "
                "sign reproduction; the strongest positive-lag candidate is weak "
                "perception-shaped association, not a demonstrated request carrier",
    }
    return tier2, tier3


# ---------------------------------------------------------------------------
# tier 4: reproduced activation/clear transition-edge screen
# ---------------------------------------------------------------------------

def tier4(loaded, streams):
    intervals = {}
    windows = {}
    for name, d in loaded.items():
        ints = id11_intervals(d["a8"])
        intervals[name] = ints
        assert len(ints) == 1, ints
        on_off = ints[0]
        # recover precise on/off timestamps from the target stream
        rows = sorted((t, d[21]) for rr in d["a8"].values() for t, dd in rr for d in [dd])
        on = off = None
        for t, s in rows:
            if s == 11 and on is None:
                on = t
            if s != 11 and on is not None:
                off = t
                break
        windows[name] = {}
        for key in streams:
            addr, dlc = key
            rr = [(t, dd) for seg, rrr in d["b1"][key].items() for t, dd in rrr]

            def mat(lo, hi):
                payload = [dd for t, dd in rr if lo <= t < hi]
                if not payload:
                    return np.empty((0, dlc), dtype=np.uint8)
                return np.frombuffer(b"".join(payload), dtype=np.uint8).reshape(-1, dlc)

            mats = {
                "pre": mat(on - EDGE_WIN_MS * 1_000_000, on - EDGE_PRE_MS * 1_000_000),
                "active_start": mat(on + EDGE_PRE_MS * 1_000_000,
                                    min(off - EDGE_PRE_MS * 1_000_000,
                                        on + EDGE_WIN_MS * 1_000_000)),
                "active_end": mat(max(on + EDGE_PRE_MS * 1_000_000,
                                      off - EDGE_WIN_MS * 1_000_000),
                                  off - EDGE_PRE_MS * 1_000_000),
                "post": mat(off + EDGE_POST_MS * 1_000_000,
                            off + EDGE_WIN_MS * 1_000_000),
            }
            windows[name][key] = {k: (np.unpackbits(m, axis=1, bitorder="big").mean(axis=0)
                                      if len(m) else None, len(m)) for k, m in mats.items()}

    bits = []
    for key in streams:
        addr, dlc = key
        for k in range(24, dlc * 8):
            rec, dirs, margins, ok = {}, [], [], True
            for name in windows:
                w = windows[name][key]
                if min(w[x][1] for x in w) < 2:
                    ok = False
                    break
                p, a = float(w["pre"][0][k]), float(w["active_start"][0][k])
                e, z = float(w["active_end"][0][k]), float(w["post"][0][k])
                od, cd = a - p, z - e
                direction = 1 if od > 0 else -1
                if direction * od <= 0 or direction * cd >= 0:
                    ok = False
                    break
                dirs.append(direction)
                margins.append(min(abs(od), abs(cd)))
                rec[name] = {"pre": round(p, 4), "active_start": round(a, 4),
                             "active_end": round(e, 4), "post": round(z, 4),
                             "on_delta": round(od, 4), "off_delta": round(cd, 4),
                             "counts": [w[x][1] for x in ("pre", "active_start", "active_end", "post")]}
            if ok and len(set(dirs)) == 1:
                bits.append({"id": f"0x{addr:03X}", "dlc": dlc, "bit_be": k, "byte": k // 8,
                             "bit_in_byte_msb0": k % 8, "direction": dirs[0],
                             "min_four_edge_margin": round(min(margins), 4), "drives": rec})
    bits.sort(key=lambda x: (-x["min_four_edge_margin"], x["id"], x["bit_be"]))
    return {
        "id11_intervals": intervals,
        "windows": "1.9 s pre/start/end/post band means (100 ms guards) around the single "
                   "global-monotonic-time ID11 interval per drive; semantic bits 24.. only",
        "n_reproduced_active_edge_bits": len(bits),
        "strongest_four_edge_margin": bits[0]["min_four_edge_margin"] if bits else None,
        "top_edge_bits": [{k: b[k] for k in ("id", "bit_be", "direction",
                                             "min_four_edge_margin", "drives")} for b in bits[:8]],
        "deterministic_request_mode_bit": False,
        "note": "no deterministic request/mode bit: the strongest reproduced four-edge "
                "margin is only 0.2105 and the top fields are noisy perception/object-family "
                "bits (0x181/0x189), not stable state flags; this bounds a single stable bit "
                "synchronized to 0x08A B21, it does not prove absence of egress",
    }


# ---------------------------------------------------------------------------
# plant-feedback control (compact)
# ---------------------------------------------------------------------------

PLANT_SPECS = [(0x1A0, 48, "be", 87, 14, True), (0x160, 32, "be", 172, 11, True),
               (0x160, 32, "be", 119, 23, True), (0x160, 32, "be", 109, 8, True)]


def plant_feedback(loaded):
    def sig(d, order, start, width, signed):
        bits = np.unpackbits(np.frombuffer(d, dtype=np.uint8), bitorder=order)[start:start + width].astype(np.uint64)
        weights = (1 << np.arange(width - 1, -1, -1, dtype=np.uint64)) if order == "be" \
            else (1 << np.arange(width, dtype=np.uint64))
        v = int(bits @ weights)
        if signed and v & (1 << (width - 1)):
            v -= 1 << width
        return v

    def nearest(rows, t, gap=30_000_000):
        ts = [x[0] for x in rows]
        i = bisect.bisect_left(ts, t)
        c = [j for j in (i - 1, i) if 0 <= j < len(rows)]
        if not c:
            return None
        j = min(c, key=lambda j: abs(ts[j] - t))
        return rows[j] if abs(ts[j] - t) <= gap else None

    def corr(x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        if len(x) < 8 or x.std() == 0 or y.std() == 0:
            return None
        return float(np.corrcoef(x, y)[0, 1])

    entries = []
    for addr, dlc, order, start, width, signed in PLANT_SPECS:
        entry = {"stream": f"0x{addr:03X}/{dlc}",
                 "field": f"{order}:bit{start}:{'s' if signed else 'u'}{width}", "drives": {}}
        for name, d in loaded.items():
            rows = [(s, t, dd) for s, rr in d["b1"][(addr, dlc)].items() for t, dd in rr]
            base = []
            for seg, t, dd in rows:
                z = nearest(d["a8"].get(seg, []), t)
                if z is not None and z[1][21] == 11:
                    base.append((seg, t, sig(dd, order, start, width, signed)))
            sweeps = []
            for lag in range(-1000, 1001, 25):
                xt, yt, xa, ya = [], [], [], []
                for seg, t, x in base:
                    z = nearest(d["a8"].get(seg, []), t + lag * 1_000_000)
                    q = nearest(d["angle"].get(seg, []), t + lag * 1_000_000)
                    if z is not None and z[1][21] == 11:
                        xt.append(x)
                        yt.append(int.from_bytes(z[1][18:20], "big", signed=True))
                    if q is not None:
                        xa.append(x)
                        ya.append(q[1])
                sweeps.append((lag, corr(xt, yt), corr(xa, ya)))
            bt = max((s for s in sweeps if s[1] is not None), key=lambda s: abs(s[1]))
            ba = max((s for s in sweeps if s[2] is not None), key=lambda s: abs(s[2]))
            entry["drives"][name] = {"n_active": len(base),
                                     "target_best": {"r": round(bt[1], 6), "lag_ms": bt[0]},
                                     "measured_angle_best": {"r": round(ba[2], 6), "lag_ms": ba[0]}}
        entries.append(entry)
    return {
        "entries": entries,
        "note": "strong 0x160 candidates correlate with measured 0x025 steering angle at "
                "near-zero/negative lag while their best 0x08A target lags are more "
                "negative -- plant/feedback-shaped within the active windows, not "
                "demonstrated request commands; CORR-138 shows full-drive nonreproduction, "
                "so these are not promoted to standing field identities",
    }


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    args = ap.parse_args()

    loaded = {n: load_drive(p) for n, p in DRIVES.items()}
    common = set.intersection(*(set(d["b1"]) for d in loaded.values()))
    streams = [k for k in sorted(common)
               if min(sum(len(v) for v in loaded[n]["b1"][k].values()) for n in loaded) >= PERIODIC_MIN]
    assert len(streams) == 22, streams

    print("tier 1: exhaustive 1..16-bit lag census", flush=True)
    t1 = tier1(loaded, streams)
    print("tier 2/3: exhaustive zero-lag state screen + stratified refinement", flush=True)
    t2, t3 = tiers_2_3(loaded, streams)
    print("tier 4: transition-edge screen", flush=True)
    t4 = tier4(loaded, streams)
    print("plant-feedback control", flush=True)
    plant = plant_feedback(loaded)

    drives_meta = []
    for n, d in loaded.items():
        a8_frames = sum(len(rr) for rr in d["a8"].values())
        batching = sum(1 for seg, rr in d["a8"].items() for t, _ in rr if d["event"][(seg, t)] > 1)
        drives_meta.append({
            "label": n,
            "path": str(DRIVES[n].relative_to(REPO)),
            "sha256": sha256(DRIVES[n]),
            "total_frames": d["total"],
            "all_bus1_id_dlc_streams": len(d["b1"]),
            "periodic_bus1_streams": len(streams),
            "bus2_0x08a_frames": a8_frames,
            "batching": {
                "0x08A_timestamp_buckets_with_any_other_frame": batching,
                "boundary": "logMonoTime belongs to an rlog CAN Event publication batch; "
                            "frames sharing it have no retained within-batch wire order or "
                            "individual hardware timestamp",
            },
        })

    out = {
        "schema": "camry-2026-bus1-frc-egress-bounds-v1",
        "generated_by": "tools/analyze_camry_2026_bus1_frc_egress_bounds.py",
        "sources": {
            "drives": drives_meta,
            "periodic_stream_set": [f"0x{a:03X}/{d}" for a, d in streams],
            "periodic_threshold_frames": PERIODIC_MIN,
            "target": "native Panda bus-2 0x08A DLC 32 (protected side); forwarded bus-0 "
                      "copies give identical ID11 intervals and reproduced edges",
            "tx_ownership": "per-ID FRC-versus-radar transmitter ownership on Bus 1 is "
                            "unresolved; this census is per-stream, not per-transmitter, so "
                            "a capture-wide negative cannot be attributed specifically to FRC Tx",
        },
        "id11_intervals": {n: t4["id11_intervals"][n] for n in ("drive_a", "drive_b")},
        "tiers": {
            "exhaustive_1_16bit_lag_census": t1,
            "exhaustive_zero_lag_state_screen": t2,
            "stratified_wider_nonlinear_refinement": t3,
            "transition_edge_screen": {k: v for k, v in t4.items() if k != "id11_intervals"},
            "plant_feedback_control": plant,
        },
        "interpretation": {
            "bounded_negative": "Within the declared tiers (exhaustive 1..16-bit "
                                "semantic-field +/-300 ms Pearson census; exhaustive "
                                "898,104-spec zero-lag/state screen; stratified 450-candidate "
                                "+/-1 s wider/nonlinear refinement; reproduced four-edge "
                                "transition screen), the retained captures reveal no "
                                "reproduced direct single-field linearly or monotonically "
                                "related unsigned FRC lateral request carrier on native "
                                "Toyota Bus 1; weak positive-lag perception associations and "
                                "stronger trailing/plant-shaped fields remain.",
            "does_not_establish": [
                "absence of unsigned FRC lateral egress",
                "that the FRC->proxy/arbitration handoff is private",
                "impossibility of upstream source replacement",
            ],
            "not_excluded": [
                "multivariate encoding",
                "nonlinear/nonmonotonic transforms",
                "conditionally multiplexed or event-driven egress",
                "fields wider than 16 bits in the exhaustive lag tier",
                "source data outside periodic CAN (sparse diagnostic/event streams; drive A "
                "has 56 distinct Bus-1 ID/DLC streams vs the 22 frequent periodic ones)",
                "private Ethernet/LVDS/internal-gateway handoff",
                "diagnostic/recorder objects",
                "an FRC state vector from which the downstream ECU synthesizes the protected target",
                "effects hidden by having only one ID11 interval per drive",
            ],
            "next_primary_source": "synchronized FRC Operation FFD (5282/5631 request, "
                                   "5285/57DE arbitration, 5265 grant, 560D pinion) plus "
                                   "all-bus CAN capture",
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    print("tier1 reproduced positive >=0.40:", len(t1["reproduced_positive_leads_abs_r_ge_0_40"]),
          "tier1 candidates/drive:", t1["candidate_fields_per_drive"])
    print("tier2 specs:", t2["candidate_specs"], "tier3 size:", t3["tier_size"],
          "tier3 strongest:", json.dumps(t3["strongest_positive_lag_selected_candidate"]))
    print("tier4 edges:", t4["n_reproduced_active_edge_bits"],
          "margin:", t4["strongest_four_edge_margin"])


if __name__ == "__main__":
    main()
