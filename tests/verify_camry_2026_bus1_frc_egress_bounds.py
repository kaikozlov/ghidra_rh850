#!/usr/bin/env python3
"""Verify the bounded negative on unsigned FRC lateral egress over native Bus 1.

Portable deterministic guard for data/generated/camry_2026_bus1_frc_egress_bounds.json:
provenance pinning (source capture digests, method tiers, candidate counts), the
substantive method-bounded results of all four tiers, plus fast independent
recomputation of the headline numbers directly from the retained captures.

This verifier deliberately does NOT rerun the ~minutes four-tier producer; it is
not a byte-identical regeneration proof. Full deterministic regeneration of the
committed artifact is performed manually with the tracked producer:
``uv run python tools/analyze_camry_2026_bus1_frc_egress_bounds.py``. The
fast-path guards here (input hashes + schema/method/counts/key results + spot
recomputations) fail closed if the retained captures or any pinned method/result
changes without a deliberate regeneration and review.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
ART = REPO / "data/generated/camry_2026_bus1_frc_egress_bounds.json"
TOOL = REPO / "tools/analyze_camry_2026_bus1_frc_egress_bounds.py"

passed = failed = 0


def check(name: str, cond, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


EXPECTED_DRIVES = {
    "drive_a": (
        RAW / "camry_relay_route_can_20260827.ndjson.gz",
        "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5",
        1_656_656,
        56,  # distinct bus-1 ID/DLC streams in the raw capture
    ),
    "drive_b": (
        RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
        "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a",
        1_918_047,
        22,
    ),
}

PERIODIC_STREAMS = [
    "0x020/12", "0x123/16", "0x160/32", "0x180/64", "0x181/64", "0x182/64",
    "0x183/64", "0x184/64", "0x185/64", "0x186/64", "0x187/64", "0x188/64",
    "0x189/64", "0x18A/64", "0x18B/64", "0x18C/48", "0x1A0/48", "0x200/64",
    "0x201/64", "0x230/64", "0x440/32", "0x450/32",
]


def tier1_candidate_count(dlc: int) -> int:
    """Exhaustive contiguous 1..16-bit fields over semantic B3..end, BE+LE, u/s."""
    bits = (dlc - 3) * 8
    per_order = bits + 2 * sum(bits - w + 1 for w in range(2, 17))
    return 2 * per_order


def tier2_candidate_count(dlc: int) -> int:
    """Every contiguous 1..24-bit and 32-bit window at every offset, BE+LE, u/s."""
    bits = dlc * 8
    per_order = sum(
        (bits - w + 1) * (1 if w == 1 else 2) for w in list(range(1, 25)) + [32]
    )
    return 2 * per_order


TIER1_TOTAL = sum(tier1_candidate_count(int(s.split("/")[1])) for s in PERIODIC_STREAMS)
TIER2_TOTAL = sum(tier2_candidate_count(int(s.split("/")[1])) for s in PERIODIC_STREAMS)

# == load artifact (RED: missing producer/artifact) ==
if not ART.is_file():
    print(f"[FAIL] tracked artifact exists: {ART} (run the producer to generate it)")
    sys.exit(1)
if not TOOL.is_file():
    print(f"[FAIL] tracked producer exists: {TOOL}")
    sys.exit(1)
art = json.loads(ART.read_text())

print("== provenance ==")
check("schema pinned", art["schema"] == "camry-2026-bus1-frc-egress-bounds-v1")
src = art["sources"]
check("producer recorded", art.get("generated_by") == "tools/analyze_camry_2026_bus1_frc_egress_bounds.py")
for entry in src["drives"]:
    label = entry["label"]
    path, digest, frames, all_streams = EXPECTED_DRIVES[label]
    check(f"{label}: capture exists and digest pinned", path.is_file() and sha256(path) == digest)
    check(f"{label}: artifact source digest matches raw", entry["sha256"] == digest)
    check(f"{label}: total frames {frames}", entry["total_frames"] == frames)
    check(f"{label}: {all_streams} distinct bus-1 ID/DLC streams vs 22 periodic",
          entry["all_bus1_id_dlc_streams"] == all_streams
          and entry["periodic_bus1_streams"] == 22,
          f"got {entry['all_bus1_id_dlc_streams']}/{entry['periodic_bus1_streams']}")
check("periodic stream set is the 22 shared frequent streams",
      src["periodic_stream_set"] == PERIODIC_STREAMS)
check("periodic threshold is 50 frames", src["periodic_threshold_frames"] == 50)
check("Tx ownership stays unresolved (census is per-stream, not per-transmitter)",
      "unresolved" in src["tx_ownership"].lower() and "FRC" in src["tx_ownership"])

print("== ID11 protected-request intervals ==")
iv = art["id11_intervals"]
check("one continuous ID11 interval per drive (global monotonic time, not segment-local)",
      iv["drive_a"] == [{"start_segment": 5, "end_segment": 5, "duration_s": 16.14985933}]
      and iv["drive_b"] == [{"start_segment": 20, "end_segment": 21, "duration_s": 57.203824788}])

print("== tier 1: exhaustive 1..16-bit semantic-field lag census ==")
t1 = art["tiers"]["exhaustive_1_16bit_lag_census"]
check("541,984 candidate fields per drive (analytic recompute matches artifact)",
      t1["candidate_fields_per_drive"] == 541_984 == TIER1_TOTAL, str(TIER1_TOTAL))
check("lag grid -300..+300 ms in 25 ms steps",
      t1["lags_ms"][0] == -300 and t1["lags_ms"][-1] == 300
      and len(t1["lags_ms"]) == 25 and t1["lags_ms"][1] == -275)
check("join: same-segment nearest bus2 0x08A <=30 ms; source and shifted target B21=11",
      t1["join"] == "same-segment nearest native bus2 0x08A DLC32 within 30 ms; "
      "source frame and shifted target frame both require B21=11")
check("lag convention: positive lag means the field leads the protected target",
      t1["lag_convention"] == "corr(field(t), target(t+lag)); positive lag means Bus-1 field leads protected 0x08A")
check("scope is semantic B3..end, BE/LE, unsigned+signed, no dedup",
      t1["scope"] == "all 22 shared periodic native Bus-1 streams; every contiguous 1..16-bit "
      "BE/LE field, signed+unsigned, in semantic B3..end (B0:B1 CRC and B2 alive counter excluded); "
      "no candidate-series deduplication")
check("ZERO reproduced positive-lag fields with |r|>=0.40 in both drives",
      t1["reproduced_positive_leads_abs_r_ge_0_40"] == [])
strongest = t1["strongest_reproduced_positive_leads"][0]
check("strongest reproduced positive lead is 0x181/64 big:bit365:u1 "
      "(A -0.353526236 @+150ms, B -0.331393092 @+300ms)",
      strongest["stream"] == "0x181/64" and strongest["field"] == "big:bit365:u1"
      and strongest["min_abs_r"] == 0.331393092
      and strongest["A"]["pearson_r"] == -0.353526236 and strongest["A"]["lag_ms"] == 150
      and strongest["B"]["pearson_r"] == -0.331393092 and strongest["B"]["lag_ms"] == 300,
      json.dumps(strongest))
check("reproduced leads list records the >=0.20 tier size",
      isinstance(t1["n_reproduced_positive_leads_abs_r_ge_0_20"], int)
      and t1["n_reproduced_positive_leads_abs_r_ge_0_20"] > 0)

print("== tier 2: exhaustive zero-lag/state spec screen ==")
t2 = art["tiers"]["exhaustive_zero_lag_state_screen"]
check("898,104 candidate specs (analytic recompute matches artifact)",
      t2["candidate_specs"] == 898_104 == TIER2_TOTAL, str(TIER2_TOTAL))
by_stream = t2["candidate_count_by_stream"]
check("per-stream spec counts sum to the total", sum(by_stream.values()) == 898_104)
check("whole-frame scope including B0:B1 CRC and B2 alive counter is declared",
      "integrity_note" in t2 and t2["join"] == "same-segment nearest 0x08A within 40 ms")
check("state screens enumerated (level/delta/rate/indicator by Target Lateral ID 0/11/18)",
      set(t2["screens"]) >= {"angle_0", "angle_11", "angle_18", "delta_11", "delta_18",
                             "rate_11", "rate_18", "indicator_11", "indicator_18"})

print("== tier 3: stratified wider/nonlinear refinement (NOT exhaustive lag search) ==")
t3 = art["tiers"]["stratified_wider_nonlinear_refinement"]
check("tier size is the actual 450-candidate stratified subset",
      t3["tier_size"] == 450, str(t3.get("tier_size")))
boundary = t3["boundary"].lower()
check("boundary states the ±1s sweep is stratified, not exhaustive",
      "stratified" in boundary and "not" in boundary and "exhaustive" in boundary)
lead = t3["strongest_positive_lag_selected_candidate"]
check("strongest positive-lag selected candidate is 0x184/64 bit296 u1",
      lead["stream"] == "0x184/64"
      and lead["field"].endswith("bit296:u1")
      and round(lead["A"]["pearson_r"], 3) == 0.327
      and lead["A"]["lag_ms"] == 1000 and lead["A"]["state"] == 11
      and round(lead["B"]["pearson_r"], 3) == 0.223
      and lead["B"]["lag_ms"] == 300 and lead["B"]["state"] == 11,
      json.dumps(lead))
check("stratified refinement retained monotonic/Spearman diagnostics",
      isinstance(t3.get("strongest_selected_monotonic_at_best_level_lag"), dict)
      and all(
          isinstance(t3["strongest_selected_monotonic_at_best_level_lag"][drive].get("monotonic"), dict)
          for drive in ("A", "B")
      ))

print("== tier 4: transition-edge screen ==")
t4 = art["tiers"]["transition_edge_screen"]
check("no deterministic request/mode bit",
      t4["deterministic_request_mode_bit"] is False)
check("strongest four-edge margin is 0.2105 (no stable synchronized state bit)",
      t4["strongest_four_edge_margin"] == 0.2105)
check("reproduced edge bits retained compactly with top fields perception-family",
      t4["n_reproduced_active_edge_bits"] == 182
      and {b["id"] for b in t4["top_edge_bits"]} <= {"0x181", "0x189", "0x180", "0x188", "0x18B"}
      and abs(t4["top_edge_bits"][0]["min_four_edge_margin"] - 0.2105) < 1e-9)

print("== interpretation boundary ==")
interp = art["interpretation"]
check("durable conclusion is the method-bounded negative",
      interp["bounded_negative"].startswith("Within the declared tiers")
      and "no reproduced direct single-field linearly or monotonically related "
      "unsigned FRC lateral request carrier" in interp["bounded_negative"])
check("does NOT establish absence, private handoff, or impossibility of replacement",
      interp["does_not_establish"] == [
          "absence of unsigned FRC lateral egress",
          "that the FRC->proxy/arbitration handoff is private",
          "impossibility of upstream source replacement",
      ])
check("open exclusions listed (multivariate, nonlinear, multiplexed, >16-bit, non-CAN, ...)",
      any(e.startswith("multivariate") for e in interp["not_excluded"])
      and any(e.startswith("nonlinear") for e in interp["not_excluded"])
      and any("non-CAN" in e or "Ethernet" in e for e in interp["not_excluded"]))

print("== deterministic spot recomputation from raw captures (independent implementation) ==")
import bisect
from collections import defaultdict

import numpy as np

SPOT_LAG_MS = {"drive_a": 150, "drive_b": 300}
SPOT_EXPECT_R = {"drive_a": -0.353526236, "drive_b": -0.331393092}


def nearest_08a(rows, t, maxgap=30_000_000):
    ts = [r[0] for r in rows]
    i = bisect.bisect_left(ts, t)
    cand = [j for j in (i - 1, i) if 0 <= j < len(rows)]
    if not cand:
        return None
    j = min(cand, key=lambda j: abs(ts[j] - t))
    return rows[j] if abs(ts[j] - t) <= maxgap else None


spot_ok = True
for label, (path, digest, frames, all_streams) in EXPECTED_DRIVES.items():
    b1_181 = defaultdict(list)   # 0x181/64 frames by segment
    a8 = defaultdict(list)       # bus2 0x08A DLC32 frames by segment
    bus1_streams = defaultdict(int)
    n_total = 0
    with gzip.open(path, "rt") as f:
        for line in f:
            seg, t, bus, addr, hx = json.loads(line)
            d = bytes.fromhex(hx)
            n_total += 1
            if bus == 1:
                bus1_streams[(addr, len(d))] += 1
                if addr == 0x181 and len(d) == 64:
                    b1_181[seg].append((t, d))
            elif bus == 2 and addr == 0x08A and len(d) == 32:
                a8[seg].append((t, d))
    for seg in a8:
        a8[seg].sort()

    check(f"{label}: frame and stream inventory recomputed from raw",
          n_total == frames and len(bus1_streams) == all_streams
          and sum(1 for v in bus1_streams.values() if v >= 50) == 22,
          f"frames={n_total} all={len(bus1_streams)}")

    # global monotonic-time ID11 interval duration (not the segment-local split)
    rows = sorted((t, seg, d) for seg, rr in a8.items() for t, d in rr)
    on = off = on_seg = None
    for t, seg, d in rows:
        if d[21] == 11 and on is None:
            on, on_seg = t, seg
        elif d[21] != 11 and on is not None:
            off, off_seg = t, seg
            break
    dur = round((off - on) / 1e9, 9)
    want_dur = 16.14985933 if label == "drive_a" else 57.203824788
    check(f"{label}: ID11 interval duration recomputed ({want_dur}s)", dur == want_dur, str(dur))

    # Headline tier-1 statistic: big:bit365 is relative to semantic B3..end,
    # so it is full-frame byte 3+(365//8)=48, bit 5 msb0 (mask 0x04).
    # Pearson vs s16be B18:B19 at the pinned lag, both joins B21=11.
    lag = SPOT_LAG_MS[label]
    xs, ys = [], []
    for seg, rr in b1_181.items():
        if seg not in a8:
            continue
        for t, d in rr:
            src = nearest_08a(a8[seg], t)
            if src is None or src[1][21] != 11:
                continue
            tgt = nearest_08a(a8[seg], t + lag * 1_000_000)
            if tgt is None or tgt[1][21] != 11:
                continue
            xs.append((d[48] >> 2) & 1)
            ys.append(int.from_bytes(tgt[1][18:20], "big", signed=True))
    x = np.asarray(xs, dtype=np.float64)
    y = np.asarray(ys, dtype=np.float64)
    vx, vy = x - x.mean(), y - y.mean()
    r = float(np.dot(vx, vy) / (np.linalg.norm(vx) * np.linalg.norm(vy)))
    check(f"{label}: 0x181/64 big:bit365:u1 Pearson r at +{lag} ms recomputed == {SPOT_EXPECT_R[label]}",
          round(r, 9) == SPOT_EXPECT_R[label] and len(xs) >= 100,
          f"r={round(r, 9)} n={len(xs)}")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
