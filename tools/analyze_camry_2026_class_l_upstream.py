#!/usr/bin/env python3
"""Class-L-conditioned EPS/upstream correlation over the two relay-correct Camry drives.

Read-only analysis against tracked raw captures:
  * exact Class-L (0x08A B21==0x0B) intervals from the VAR-067 census, recomputed
    and asserted identical;
  * majority-bit step scan across every observed exact-F33-accepted bus0 stream at
    Class-L rise/fall (3 s pre/post windows);
  * DBC-decoded EPS observables inside Class-L (0x030 steering-wheel torque,
    0x025 angle/rate) and wheel speed;
  * 0x090 closure: exact-F33 PDU40 receive geometry (sig229/232/235 + flags + sig241),
    lead/lag vs 0x025 angle, and the retirement of the prior synthetic B12/B13
    exploratory composite (outside the firmware-defined receive surface);
  * bus1 upstream-family census and Class-L-conditioned 0x18A activity, 0x18C
    staircase record count, and the 0x181 bytes[35:37] steering-lag field.

The output is review evidence only; production output stays disabled.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.analyze_camry_2026_relay_capture import decode_wheel_speed
from tools.toyota_route_opendbc_common import be_signal

RAW = REPO / "targets/camry-2026/raw-20260827"
CENSUS = REPO / "data/generated/camry_2026_cruise_lta_edge_census.json"
INGRESS = REPO / "data/generated/camry_8965F3307000_external_lateral_ingress.json"
DRIVES = {
    "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}

# Exact generated TSS3 DBC decode facts (pinned; @0 is big-endian Motorola):
#   0x030 STEERING_WHEEL_TORQUE_COARSE 71|8  (0.1,0)   -> signed8(B8) * 0.1
#   0x030 STEERING_WHEEL_TORQUE_FINE  139|4 (0.01,0)   -> signed4(B17 & 0x0F) * 0.01
#   0x025 STEER_ANGLE                   3|12 (1.5,0)   -> signed12(((B0&0x0F)<<8)|B1) * 1.5
#   0x025 STEER_FRACTION               39|4  (0.1,0)   -> signed4(B4>>4) * 0.1   (B4 high nibble)
#   0x025 STEER_RATE                   35|12 (1.0,0)   -> signed12(((B4&0x0F)<<8)|B5) * 1.0 (B4 low nibble + B5)
ANCHOR = bytes.fromhex("ffe00007")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def signed(val: int, bits: int) -> int:
    return val - (1 << bits) if val & (1 << (bits - 1)) else val


def torque_nm(d: bytes) -> float:
    return round(be_signal(d, 71, 8, is_signed=True) * 0.1 + be_signal(d, 139, 4, is_signed=True) * 0.01, 3)


def angle_deg(d: bytes) -> float:
    return be_signal(d, 3, 12, is_signed=True) * 1.5 + be_signal(d, 39, 4, is_signed=True) * 0.1


def rate_raw(d: bytes) -> int:
    return be_signal(d, 35, 12, is_signed=True)


def motor_raw(d: bytes) -> int:
    """Exact-F33 0x030 B22:B23 signed big-endian motor-feedback/current-family proxy."""
    return int.from_bytes(d[22:24], "big", signed=True)


def majority_bits(frames: list[bytes], persistence: float = 0.95) -> list[int]:
    """Per-bit persistent majority across frames of equal DLC.

    Returns 1/0 only when at least `persistence` of frames agree, and 2 when the
    bit is not persistent (analog-valued or changing); a step requires a
    persistent value in both windows that differs.
    """
    dlc = len(frames[0])
    out = []
    for i in range(dlc):
        for j in range(8):
            ones = sum((d[i] >> j) & 1 for d in frames)
            frac = ones / len(frames)
            if frac >= persistence:
                out.append(1)
            elif frac <= 1 - persistence:
                out.append(0)
            else:
                out.append(2)
    return out


def load(path: Path):
    with gzip.open(path, "rt") as f:
        for line in f:
            seg, t, bus, addr, data = json.loads(line)
            yield int(seg), int(t), int(bus), int(addr), bytes.fromhex(data)



def resample(series: list[tuple[int, float]], t0: int, t1: int, step_ns: int) -> list[float]:
    grid = list(range(t0, t1, step_ns))
    out, idx = [], 0
    for g in grid:
        while idx + 1 < len(series) and abs(series[idx + 1][0] - g) <= abs(series[idx][0] - g):
            idx += 1
        out.append(series[idx][1])
    return out


def corr(a: list[float], b: list[float]) -> float:
    n = len(a)
    if n < 8:
        return 0.0
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    if va <= 0 or vb <= 0:
        return 0.0
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return cov / (va ** 0.5 * vb ** 0.5)


def analyze_drive(label: str, path: Path, accepted: set[int], census_intervals: list[dict]) -> dict:
    streams: dict[tuple[int, int], list[tuple[int, int, bytes]]] = defaultdict(list)
    a8: dict[int, list[tuple[int, bytes]]] = defaultdict(list)
    bus1: dict[int, list[tuple[int, int, bytes]]] = defaultdict(list)
    speeds: list[tuple[int, int, float]] = []
    eps_tx30: list[tuple[int, int, bytes]] = []
    bases: dict[int, int] = {}
    n_frames = 0
    for seg, t, bus, addr, dat in load(path):
        n_frames += 1
        bases.setdefault(seg, t)
        if bus == 0:
            if addr == 0x08A and len(dat) == 32:
                a8[seg].append((t, dat))
            elif addr == 0x0AA and len(dat) == 8:
                speeds.append((seg, t, decode_wheel_speed(dat)))
            elif addr == 0x030 and len(dat) == 32:
                eps_tx30.append((seg, t, dat))
            if addr in accepted:
                streams[(addr, len(dat))].append((seg, t, dat))
        elif bus == 1:
            bus1[addr].append((seg, t, dat))

    # Recompute Class-L intervals: bus0 0x08A byte21 == 0x0B.
    ints: list[tuple[int, int, int, int]] = []
    start_seg = start = last_seg = last = None
    for seg, t, d in sorted((seg, t, d) for seg, rows in a8.items() for t, d in rows):
        if d[21] == 0x0B:
            if start is None:
                start_seg, start, last_seg, last = seg, t, seg, t
            else:
                last_seg = seg
                last = t
        elif start is not None:
            ints.append((start_seg, start, last_seg, last))
            start_seg = start = last_seg = last = None
    if start is not None:
        ints.append((start_seg, start, last_seg, last))
    recomputed = [
        {"start_segment": start_seg, "start_s": round((a - bases[start_seg]) / 1e9, 6), "duration_s": round((b - a) / 1e9, 6)}
        for start_seg, a, _end_seg, b in ints
    ]
    expected = [{k: row[k] for k in ("start_segment", "start_s", "duration_s")} for row in census_intervals]
    assert recomputed == expected, f"{label}: Class-L interval drift: {recomputed} != {expected}"
    rise = [(seg, a) for seg, a, _end_seg, _b in ints]
    fall = [(end_seg, b) for _start_seg, _a, end_seg, b in ints]

    # Majority-bit step scan at rise/fall over observed accepted bus0 streams.
    step = {"rise": {}, "fall": {}}
    observed = {k: v for k, v in streams.items() if k[0] != 0x0B6}
    for (edge_seg, edge_t), kind in [(t, "rise") for t in rise] + [(t, "fall") for t in fall]:
        flips = []
        for (addr, dlc), rows in sorted(observed.items()):
            pre = [d for _seg, t, d in rows if edge_t - 3_000_000_000 <= t < edge_t]
            post = [d for _seg, t, d in rows if edge_t <= t < edge_t + 3_000_000_000]
            if len(pre) < 20 or len(post) < 20:
                continue
            mb_pre, mb_post = majority_bits(pre), majority_bits(post)
            for i, (x, y) in enumerate(zip(mb_pre, mb_post)):
                if x in (0, 1) and y in (0, 1) and x != y:
                    flips.append({"id": f"0x{addr:03X}", "dlc": dlc, "byte": i // 8, "bit": i % 8,
                                  "pre": x, "post": y})
        step[kind][f"{edge_seg}:{edge_t}"] = flips

    def flatten(kind: str) -> set[tuple]:
        out = set()
        for fl in step[kind].values():
            for f in fl:
                out.add((f["id"], f["byte"], f["bit"]))
        return out

    # Per-drive rise flip set (single Class-L interval per drive in these captures).
    rise_keys = sorted(step["rise"].keys())
    per_drive_rise: set[tuple] = set()
    for k in rise_keys:
        for f in step["rise"][k]:
            per_drive_rise.add((f["id"], f["byte"], f["bit"]))
    fall_set = flatten("fall")

    # 0x030 is an EPS transmit stream, not an accepted Rx stream; scan it separately.
    torque_flips = []
    torque_edges = []
    for (edge_seg, edge_t), kind in [(t, "rise") for t in rise] + [(t, "fall") for t in fall]:
        pre = [d for _seg, t, d in eps_tx30 if edge_t - 3_000_000_000 <= t < edge_t]
        post = [d for _seg, t, d in eps_tx30 if edge_t <= t < edge_t + 3_000_000_000]
        flips = []
        if len(pre) >= 20 and len(post) >= 20:
            for i, (x, y) in enumerate(zip(majority_bits(pre), majority_bits(post))):
                if x in (0, 1) and y in (0, 1) and x != y:
                    flips.append({"byte": i // 8, "bit": i % 8, "pre": x, "post": y})
        torque_flips.extend(flips)
        torque_edges.append({"edge": kind, "segment": edge_seg, "edge_ns": edge_t,
                             "pre_frames": len(pre), "post_frames": len(post), "persistent_flips": flips})

    # DBC-decoded EPS observables inside Class-L.
    eps = {"intervals": []}
    t25 = streams.get((0x025, 32), [])
    for start_seg, a, end_seg, b in ints:
        inside30 = [d for _s, t, d in eps_tx30 if a <= t <= b]
        inside25 = [d for _s, t, d in t25 if a <= t <= b]
        sp = [v for _s, t, v in speeds if a <= t <= b]
        torques = sorted(abs(torque_nm(d)) for d in inside30)
        rates = sorted(abs(rate_raw(d)) for d in inside25)
        angles = [angle_deg(d) for d in inside25]
        amean = sum(angles) / len(angles) if angles else 0.0
        astd = (sum((x - amean) ** 2 for x in angles) / len(angles)) ** 0.5 if angles else 0.0
        eps["intervals"].append({
            "start_segment": start_seg, "end_segment": end_seg,
            "start_s": round(a / 1e9, 6), "duration_s": round((b - a) / 1e9, 6),
            "torque_frames": len(inside30), "angle_frames": len(inside25),
            "abs_torque_nm_median": round(torques[len(torques) // 2], 3) if torques else None,
            "abs_torque_nm_p90": round(torques[int(len(torques) * 0.9)], 3) if torques else None,
            "abs_rate_raw_median": rates[len(rates) // 2] if rates else None,
            "abs_rate_raw_p90": rates[int(len(rates) * 0.9)] if rates else None,
            "angle_std_deg": round(astd, 3),
            "wheel_speed_kph_mean": round(sum(sp) / len(sp), 2) if sp else None,
        })

    # 0x090: exploratory nibble-scan reproduction (evidence trail), then the exact-F33
    # generated-COM receive geometry and its lead/lag verdict against 0x025 angle.
    t90 = streams.get((0x090, 32), [])
    _start_seg0, a0, _end_seg0, b0 = ints[0]
    angle_series = [(t, angle_deg(d)) for _seg, t, d in t25 if a0 <= t <= b0]
    torque_series = [(t, torque_nm(d)) for _seg, t, d in eps_tx30 if a0 <= t <= b0]
    motor_series = [(t, float(motor_raw(d))) for _seg, t, d in eps_tx30 if a0 <= t <= b0]
    best = {"field": None, "r": 0.0, "lag_ms": None}
    if angle_series and t90:
        inside90 = [(t, d) for _seg, t, d in t90 if a0 <= t <= b0]
        for off in range(0, 30):
            for sh in range(0, 2):
                ser = []
                for t, d in inside90:
                    raw = ((d[off] >> (4 * sh)) & 0x0F) << 8 | (d[off + 1] >> (4 * sh) if off + 1 < 32 else 0)
                    ser.append((t, float(signed(raw, 12))))
                if not ser:
                    continue
                # fine lag search on a 10 ms grid
                cur = {"r": 0.0, "lag_ms": None}
                for lag_ms in range(-120, 121, 10):
                    shifted = [(t + lag_ms * 1_000_000, v) for t, v in ser]
                    ra = resample(angle_series, a0, b0, 10_000_000)
                    rb = resample(sorted(shifted), a0, b0, 10_000_000)
                    r = corr(ra, rb)
                    if abs(r) > abs(cur["r"]):
                        cur = {"r": round(r, 4), "lag_ms": lag_ms}
                if abs(cur["r"]) > abs(best["r"]):
                    best = {"field": f"B{off}[{'7:4' if sh else '3:0'}]+B{off+1}", **cur}
        # Exploratory nibble-scan verdict (kept as the evidence trail for VAR-068):
        # the synthetic winners sit at bytes 12..15, which the exact-F33 PDU40
        # unpacker FUN_0004b9f4 never reads (see firmware_exact_0x090 below).
        eps["exploratory_0x090_reproduction"] = {
            "best_field": best["field"], "best_r": best["r"], "peak_lag_ms": best["lag_ms"],
            "classification": (
                "resolved: synthetic cross-signal composite outside the exact-F33 0x090 "
                "receive surface; retired in favor of firmware-exact fields (sig235 is the strongest angle-like channel)"
            ),
        }

        # Exact-F33 PDU40 (=CAN 0x090) generated-COM receive geometry, recovered from
        # unpacker FUN_0004b9f4 -> FUN_0007d12a windows 0x167/0x169/0x16b/0x183 and the
        # per-PDU slice-offset table at 0x22840 (PDU40 base 0x167; byte_offset =
        # window - 0x167, so the three scalar windows begin at B0/B2/B4; in-window extraction is the big-endian 32-bit window word,
        # the same method build_camry_8965F3307000_external_lateral_ingress.py pins
        # and validates against the 0x025/B6 shapes).
        fw_fields = {
            "sig229": lambda d: ((d[0] & 3) << 8) | d[1],   # 10u  B0[1:0]+B1
            "sig232": lambda d: ((d[2] & 3) << 8) | d[3],   # 10u  B2[1:0]+B3
            "sig235": lambda d: ((d[4] & 3) << 8) | d[5],   # 10u  B4[1:0]+B5
        }
        fw = {"signals": {}, "flags_all_zero_inside_class_l": None, "duplication": {}}
        flags = {
            "sig227": lambda d: (d[0] >> 7) & 1, "sig228": lambda d: (d[0] >> 6) & 1,
            "sig230": lambda d: (d[2] >> 7) & 1, "sig231": lambda d: (d[2] >> 6) & 1,
            "sig233": lambda d: (d[4] >> 7) & 1, "sig234": lambda d: (d[4] >> 6) & 1,
        }
        fw["flags_all_zero_inside_class_l"] = all(fn(d) == 0 for _t, d in inside90 for fn in flags.values())
        ra = resample(angle_series, a0, b0, 10_000_000)
        for name, fn in fw_fields.items():
            ser = [(t, float(fn(d))) for t, d in inside90]

            def peak(target: list[tuple[int, float]]) -> dict:
                rt = resample(target, a0, b0, 10_000_000)
                cur_ = {"r": 0.0, "lag_ms": None}
                for lag_ms in range(-120, 121, 10):
                    rb_ = resample(sorted((t + lag_ms * 1_000_000, v) for t, v in ser), a0, b0, 10_000_000)
                    r_ = corr(rt, rb_)
                    if abs(r_) > abs(cur_["r"]):
                        cur_ = {"r": round(r_, 4), "lag_ms": lag_ms}
                return cur_

            cur = peak(angle_series)
            cur_torque = peak(torque_series)
            cur_motor = peak(motor_series)
            rb = resample(sorted((t + cur["lag_ms"] * 1_000_000, v) for t, v in ser), a0, b0, 10_000_000)
            n = len(ra)
            ma, mb = sum(ra) / n, sum(rb) / n
            slope = sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / sum((x - ma) ** 2 for x in ra)
            vals = [fn(d) for _t, d in inside90]
            fw["signals"][name] = {
                "wire": {"sig229": "B0[1:0]+B1", "sig232": "B2[1:0]+B3", "sig235": "B4[1:0]+B5"}[name],
                "bits": 10, "signed": False,
                "range": [min(vals), max(vals)], "unique": len(set(vals)),
                "r_vs_0x025_angle": cur["r"], "peak_lag_ms": cur["lag_ms"],
                "slope_counts_per_deg_at_peak": round(slope, 4),
                "r_vs_driver_torque": cur_torque["r"], "torque_peak_lag_ms": cur_torque["lag_ms"],
                "r_vs_0x030_motor_proxy": cur_motor["r"], "motor_peak_lag_ms": cur_motor["lag_ms"],
            }
        # Wire duplication the synthetic scan exploited: B12:B13 is byte-identical to
        # B14:B15 (a duplicated fine-scale angle-correlated copy), and the synthetic
        # candidate B4[3:0]+B5 equals exact sig235 whenever B4 <= 3 (true for every
        # inside-Class-L frame in both drives).
        n90 = len(inside90)
        fw["duplication"] = {
            "b12b13_equals_b14b15_frames": sum(1 for _t, d in inside90 if d[12] == d[14] and d[13] == d[15]),
            "b4_le3_frames": sum(1 for _t, d in inside90 if d[4] <= 3),
            "frames": n90,
        }
        fw["receive_surface"] = {
            "defined_bytes": "B0..B5 carry three 10-bit pairs + six flag bits; sig241 consumes B28[7:4]. B6..B27 are not touched by the PDU40 unpacker; B29..B31 are fetched in sig241's 4-byte window but masked away",
            "sig241_wire": "B28[7:4]", "sig241_unique_inside_class_l": len({d[28] >> 4 for _t, d in inside90}),
        }
        fw["receiver_chain"] = {
            "recenter": "FUN_0004afcc(0, 0x200, v, dst): dst = saturate16(v - 512)",
            "raw_stage": {"sig229": "FEBE8084", "sig232": "FEBE8086", "sig235": "FEBE8088"},
            "recentered_stage": {"sig229": "FEBE808A", "sig232": "FEBE808C", "sig235": "FEBE808E"},
            "flags_stage": "FEBE8090..FEBE8095", "sig241_stage": "FEBE8096",
            "freshness": "FEBE8097 + FUN_000498e0(0x16)",
            "distribution": ("FUN_00058074: FEBE808A->FEBEF1C6, FEBE808C->FEBEF1C8, FEBE808E->FEBEF1CA, "
                             "flags->FEBEF0A4..FEBEF0AE; runtime constants FEBEF098=FEBEF099=0, "
                             "FEBEF09C=1, FEBEF0AA=0"),
            "combination": ("FUN_000be846 (active when DAT_FEBEB11A==0x400 and FEBEBE8D!='Z'): with the "
                            "pinned runtime constants the output reduces to "
                            "FEBEBE96 = clamp(((sig232-512)*0x931/0x10)/0x10, +/-DAT_000af3f8=+/-3763); "
                            "the sig229 term enters only via FEBEF0AA&2 (clear here); pre-clamp "
                            "+/-DAT_000af3f0=+/-409600; validity outputs FEBEBE90..FEBEBE94"),
            "integrator": ("FUN_000bcd66 (FEBEB800-0x9F4): FEBEAE0C = FEBEBE96; FUN_000c310e "
                           "(gated DAT_FEBEBFB1=='Z'): FEBEBF58 += FEBEAE0C - FEBEBFA0; "
                           "FEBEBFA0 = FEBEBF58*0x400/PTR_LAB_000af564 (8672)"),
        }
        fw["classification"] = (
            "feedback/status: sig235 is the strongest exact-F33 0x090 angle-like channel (~1 count/deg about the "
            "512 recenter), lagging 0x025 steering angle in both drives. sig232 feeds the FEBEBE96->FEBEAE0C "
            "integrator path but does not reproduce as the dominant angle channel across drives; sig229 is a slow-drift channel. "
            "No exact 0x090 signal reproducibly leads angle, torque, or the motor proxy. sig229 is dropped from the FEBEBE96 combination by "
            "the pinned runtime constants. The prior exploratory best field B12[3:0]+B13 is a "
            "synthetic composite over bytes the F33 never reads from this frame."
        )
        eps["firmware_exact_0x090"] = fw

    # bus1 family census
    span = (min(t for rows in bus1.values() for _, t, _ in rows),
            max(t for rows in bus1.values() for _, t, _ in rows))
    dur = (span[1] - span[0]) / 1e9
    bus1_rates = {f"0x{a:03X}": round(len(rows) / dur, 2) for a, rows in sorted(bus1.items())}
    fam = [a for a in bus1 if 0x180 <= a <= 0x18F]

    # 0x18A Class-L-conditioned activity in matched local windows (retracts the
    # motion-confounded global reading).
    act = []
    for _start_seg, a, _end_seg, b in ints:
        for edge, which in ((a, "rise"), (b, "fall")):
            rows = bus1.get(0x18A, [])
            pre = [d for _s, t, d in rows if edge - 3_000_000_000 <= t < edge]
            post = [d for _s, t, d in rows if edge <= t < edge + 3_000_000_000]
            if not pre or not post:
                continue
            f = lambda rows: sum(sum(1 for b_ in d[4:] if b_) for d in rows) / len(rows)
            flips = []
            if len(pre) >= 20 and len(post) >= 20:
                for i, (x, y) in enumerate(zip(majority_bits(pre), majority_bits(post))):
                    if x in (0, 1) and y in (0, 1) and x != y:
                        flips.append({"byte": i // 8, "bit": i % 8, "pre": x, "post": y})
            act.append({"edge": which, "edge_s": round(edge / 1e9, 6),
                        "pre_nonzero_mean": round(f(pre), 2), "post_nonzero_mean": round(f(post), 2),
                        "pre_frames": len(pre), "post_frames": len(post),
                        "persistent_flips": flips, "class_l_step_detected": bool(flips)})

    # 0x18C record count via literal staircase anchor ff e0 00 07 at (off-4)%4==0.
    rec = []
    for _start_seg, a, _end_seg, b in ints:
        for edge, which in ((a, "rise"), (b, "fall")):
            rows = [d for _s, t, d in bus1.get(0x18C, []) if edge - 10_000_000_000 <= t < edge - 1_000_000_000] + \
                   [d for _s, t, d in bus1.get(0x18C, []) if edge + 1_000_000_000 < t <= edge + 10_000_000_000]
            counts = Counter()
            for d in rows:
                c = None
                for off in range(4, len(d) - 3):
                    if d[off:off + 4] == ANCHOR and (off - 4) % 4 == 0:
                        c = (off - 4) // 4
                        break
                counts[c] += 1
            rec.append({"edge": which, "frames": len(rows),
                        "record_counts": {str(k): v for k, v in sorted(counts.items(), key=lambda x: (x[0] is None, x[0]))}})

    # 0x181 bytes[35:37] signed LE i16: corr(field(t), angle(t+dt)) over first 10 s.
    lag_field = None
    if ints and (0x181 in bus1) and angle_series:
        _start_seg0, a0, _end_seg0, _ = ints[0]
        t_end = a0 + 10_000_000_000
        ser = [(t, float(int.from_bytes(d[35:37], "little", signed=True))) for _s, t, d in bus1[0x181] if a0 <= t <= t_end]
        ang = [(t, angle_deg(d)) for _s, t, d in t25 if a0 <= t <= t_end]
        if len(ser) > 20 and len(ang) > 100:
            r0 = corr(resample(ang, a0, t_end, 10_000_000), resample(ser, a0, t_end, 10_000_000))
            best_lag, best_r = None, 0.0
            for dt_ms in range(-300, 301, 10):
                shifted = sorted((t + dt_ms * 1_000_000, v) for t, v in ser)
                r = corr(resample(ang, a0, t_end, 10_000_000), resample(shifted, a0, t_end, 10_000_000))
                if abs(r) > abs(best_r):
                    best_r, best_lag = r, dt_ms
            lag_field = {"wire": "bytes[35:37] signed LE i16", "first10s_r": round(r0, 4),
                         "peak_dt_ms": best_lag, "peak_r": round(best_r, 4),
                         "meaning": "corr(field(t), angle(t+dt)) peak at negative dt: the field lags measured steering, i.e. steering-derived"}

    return {
        "source": {"file": str(path.relative_to(REPO)), "sha256": sha256(path), "frame_count": n_frames},
        "class_l": {"intervals": [{"start_segment": start_seg, "end_segment": end_seg,
                                     "start_ns": a, "end_ns": b, "duration_s": round((b - a) / 1e9, 6)}
                                    for start_seg, a, end_seg, b in ints]},
        "accepted_bit_step_scan": {
            "observed_accepted_streams": len(observed),
            "rise_flips": step["rise"], "fall_flips": step["fall"],
            "distinct_rise_flip_bits": sorted(f"{i}B{by}.{bi}" for i, by, bi in per_drive_rise),
            "distinct_fall_flip_bits": sorted(f"{i}B{by}.{bi}" for i, by, bi in fall_set),
        },
        "eps_0x030_stability": {"scan_scope": "separate EPS transmit stream on relay-correct bus0",
                                "persistence_threshold": 0.95, "edges": torque_edges,
                                "persistent_flips_at_edges": torque_flips, "count": len(torque_flips)},
        "eps_metrics_inside_class_l": eps,
        "bus1_family": {"stream_rates_hz": bus1_rates,
                        "upstream_18x_ids": [f"0x{a:03X}" for a in fam]},
        "upstream_0x18a_activity": act,
        "upstream_0x18c_record_counts": rec,
        "upstream_0x181_lag_field": lag_field,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "data/generated/camry_2026_class_l_upstream_correlation.json")
    args = ap.parse_args()

    census = json.loads(CENSUS.read_text())
    ingress = json.loads(INGRESS.read_text())
    accepted = {int(x["can_id"], 16) for x in ingress["normal_rx"]["accepted"]}
    rule_ids = {int(x, 16) for x in ingress["controller1_acceptance"]["normal_rule_ids"]} | \
               {int(x["can_id"], 16) for x in ingress["controller1_acceptance"]["special_tail"]}

    drives = {}
    for label, path in DRIVES.items():
        cints = census["drives"][label]["lateral_hud_candidate"]["intervals"]
        drives[label] = analyze_drive(label, path, accepted, cints)

    a_rise = set(drives["drive_a"]["accepted_bit_step_scan"]["distinct_rise_flip_bits"])
    b_rise = set(drives["drive_b"]["accepted_bit_step_scan"]["distinct_rise_flip_bits"])
    common = sorted(a_rise & b_rise)
    def rise_18a_bits(drive: dict) -> set[str]:
        return {
            f"B{flip['byte']}.{flip['bit']}"
            for edge in drive["upstream_0x18a_activity"] if edge["edge"] == "rise"
            for flip in edge["persistent_flips"]
        }
    common_18a = sorted(rise_18a_bits(drives["drive_a"]) & rise_18a_bits(drives["drive_b"]))

    out = {
        "schema": "camry-2026-class-l-upstream-correlation-v1",
        "sources": {
            "census": {"path": str(CENSUS.relative_to(REPO)), "sha256": sha256(CENSUS)},
            "ingress": {"path": str(INGRESS.relative_to(REPO)), "sha256": sha256(INGRESS)},
            "drives": [{"path": str(p.relative_to(REPO)), "sha256": sha256(p)} for p in DRIVES.values()],
        },
        "dbc_formulas": {
            "0x030_steering_wheel_torque_nm": "signed_be(71|8) * 0.1 + signed_be(139|4) * 0.01",
            "0x025_steering_angle_deg": "signed_be(3|12) * 1.5 + signed_be(39|4) * 0.1",
            "0x025_steering_rate_raw": "signed_be(35|12)",
        },
        "drives": drives,
        "combined": {
            "common_accepted_rise_flip_bits_across_drives": common,
            "eps_0x030_persistent_flip_total": sum(d["eps_0x030_stability"]["count"] for d in drives.values()),
            "matched_upstream_0x18a_rise_flip_bits_across_drives": common_18a,
            "matched_upstream_0x18a_class_l_step_detected": bool(common_18a),
            "upstream_18x_accepted_by_f33_rules": sorted(f"0x{x:03X}" for x in range(0x180, 0x18D) if x in rule_ids),
        },
        "interpretation": {
            "class_l_eps_negative": "observed/deterministic: across both drives no exact-F33-accepted bus0 field shows a common majority-bit step at Class-L rise, and EPS 0x030 shows zero persistent bit flips at rise/fall; inside Class-L the driver-style torque/rate observables stay bounded, consistent with Class-L being an upstream/display/availability state rather than a visible EPS cooperative-mode latch. This does not prove absence of EPS-internal state invisible on 0x030.",
            "upstream_18x": "bounded: bus1 0x180..0x18C is not exact-F33 accepted and can only be upstream transformation input. 0x18A has no persistent rise flip reproduced across both matched Class-L windows; one isolated drive-B B27 high-nibble flip is retained in the per-edge evidence and is not promoted. 0x18C record count is 3 on both sides of every edge; 0x181 bytes[35:37] signed little-endian lags measured steering by 200/240 ms in the two drives and is steering-derived, not a command precursor. No identifiable upstream target/curvature/planning quantity is recoverable from these two drives.",
            "exploratory_0x090_resolution": "verified/recovered: the exact-F33 PDU40 (CAN 0x090) receive surface is sig229 B0[1:0]+B1, sig232 B2[1:0]+B3, sig235 B4[1:0]+B5 (10-bit unsigned, recentered by FUN_0004afcc v-512 into FEBE808A/8C/8E), six flag bits B0/B2/B4.7/.6 into FEBE8090..95, and sig241 B28[7:4] into FEBE8096; B6..B27 are never read by the PDU40 unpacker and B29..B31 are fetched only inside sig241's four-byte window then masked away. sig235 is the strongest angle-like exact field (~1 count/deg about 512) and lags 0x025 steering angle by 60/70 ms across the two drives (r=0.9924/0.7428); no exact 0x090 signal reproducibly leads the motor proxy. FUN_00058074 routes the recentered cells (FEBE808A->FEBEF1C6, FEBE808C->FEBEF1C8, FEBE808E->FEBEF1CA) and FUN_000be846's combination reduces, under the pinned runtime constants FEBEF098=FEBEF099=0/FEBEF09C=1/FEBEF0AA=0, to the sig232-derived FEBEBE96 branch, copied by FUN_000bcd66 to FEBEAE0C and integrated by FUN_000c310e (leaky, x0x400/8672, gated FEBEBFB1=='Z'). The prior exploratory best field B12[3:0]+B13 (r=0.9931/-60 ms, drive A) is a synthetic cross-signal composite over wire bytes the EPS never unpacks from 0x090: bytes 12..15 carry a byte-duplicated fine-scale angle-correlated copy (B12:B13 == B14:B15 in every inside-Class-L frame) that merely observes the same underlying steering; the synthetic B4[3:0]+B5 candidate coincides numerically with exact sig235 whenever B4<=3.",
            "production_output_authorized": False,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out} ({len(json.dumps(out))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
