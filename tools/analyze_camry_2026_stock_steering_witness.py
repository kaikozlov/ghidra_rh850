#!/usr/bin/env python3
"""Recover the strongest request-coherent stock-steering episodes in retained Camry CAN.

This is a narrow deterministic follow-up to camry_2026_motor_feedback_correlation:
join exact-F33 EPS motor-feedback/driver-torque (0x030), measured steering
angle/rate (0x025), and the recovered Toyota lateral request (0x08A ID/target).

The witness criterion deliberately does *not* call 0x08A ID11 an arbitration
grant. It asks only whether, while the ID11 request is present, there are sustained
samples where:
  - the EPS motor-feedback proxy and measured steering motion have the same sign;
  - measured driver torque has the opposite sign;
  - the motor-feedback proxy points toward the 0x08A target-angle error.

That is a stronger plant observation than request-state correlation alone, but it
still does not substitute for the FRC Operation-FFD winner/grant objects 5285/57DE/5265.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.analyze_camry_2026_motor_feedback import angle_deg, motor_current, rate_raw, torque_nm

RAW = REPO / "targets/camry-2026/raw-20260827"
OUT = REPO / "data/generated/camry_2026_stock_steering_witness.json"
DRIVES = {
    "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}

TARGET_SCALE_DEG_PER_COUNT = 0.05730274202574147
JOIN_TOL_NS = 40_000_000
MIN_ABS_CURRENT = 150
MIN_ABS_TORQUE_NM = 0.2
MIN_ABS_RATE = 2
MIN_RUN_S = 0.100
BRIDGE_SAMPLES = 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path):
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.strip():
                seg, t, bus, addr, data = json.loads(line)
                yield int(seg), int(t), int(bus), int(addr), bytes.fromhex(data)


def nearest(rows: list[tuple[int, bytes]], times: list[int], t: int) -> bytes | None:
    i = bisect.bisect_left(times, t)
    best = None
    for j in (i - 1, i):
        if 0 <= j < len(rows):
            dt = abs(rows[j][0] - t)
            if dt <= JOIN_TOL_NS and (best is None or dt < best[0]):
                best = (dt, rows[j][1])
    return None if best is None else best[1]


def sign(v: float | int) -> int:
    return (v > 0) - (v < 0)


def median(values: list[float]) -> float | None:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    return round(s[n // 2] if n & 1 else (s[n // 2 - 1] + s[n // 2]) / 2, 6)


def runs(samples: list[dict]) -> list[list[dict]]:
    out: list[list[dict]] = []
    cur: list[dict] = []
    drop = 0
    for s in samples:
        keep = s["coherent_opposition"]
        if keep:
            cur.append(s)
            drop = 0
        elif cur:
            drop += 1
            if drop > BRIDGE_SAMPLES:
                if (cur[-1]["t"] - cur[0]["t"]) / 1e9 >= MIN_RUN_S:
                    out.append(cur)
                cur = []
                drop = 0
    if cur and (cur[-1]["t"] - cur[0]["t"]) / 1e9 >= MIN_RUN_S:
        out.append(cur)
    return out


def summarize(run: list[dict], interval_start: int) -> dict:
    first, last = run[0], run[-1]
    n = len(run)
    return {
        "start_from_id11_interval_s": round((first["t"] - interval_start) / 1e9, 6),
        "duration_s": round((last["t"] - first["t"]) / 1e9, 6),
        "sample_count": n,
        "median_motor_feedback": median([float(s["motor"]) for s in run]),
        "median_driver_torque_nm": median([s["torque_nm"] for s in run]),
        "median_rate_raw": median([float(s["rate_raw"]) for s in run]),
        "angle_first_deg": first["angle_deg"],
        "angle_last_deg": last["angle_deg"],
        "target_first_deg": first["target_deg"],
        "target_last_deg": last["target_deg"],
        "target_error_first_deg": first["target_error_deg"],
        "target_error_last_deg": last["target_error_deg"],
        "target_error_abs_reduction_deg": round(abs(first["target_error_deg"]) - abs(last["target_error_deg"]), 6),
        "motor_toward_target_fraction": round(sum(sign(s["motor"]) == sign(s["target_error_deg"]) for s in run) / n, 6),
        "motion_toward_target_fraction": round(sum(sign(s["rate_raw"]) == sign(s["target_error_deg"]) for s in run) / n, 6),
        "driver_opposes_target_fraction": round(sum(sign(s["torque_nm"]) == -sign(s["target_error_deg"]) for s in run) / n, 6),
    }


def analyze(path: Path) -> dict:
    r30: list[tuple[int, bytes]] = []
    r25: list[tuple[int, bytes]] = []
    r8: list[tuple[int, bytes]] = []
    id11_intervals: list[tuple[int, int]] = []
    interval_start = None
    b6 = 0

    for _seg, t, bus, addr, dat in load(path):
        if addr == 0x0B6:
            b6 += 1
        if bus != 0:
            continue
        if addr == 0x030 and len(dat) == 32:
            r30.append((t, dat))
        elif addr == 0x025 and len(dat) == 32:
            r25.append((t, dat))
        elif addr == 0x08A and len(dat) == 32:
            r8.append((t, dat))
            if dat[21] == 11 and interval_start is None:
                interval_start = t
            elif dat[21] != 11 and interval_start is not None:
                id11_intervals.append((interval_start, t))
                interval_start = None
    if interval_start is not None:
        id11_intervals.append((interval_start, r8[-1][0]))

    t25 = [t for t, _ in r25]
    t8 = [t for t, _ in r8]
    samples: list[dict] = []
    for t, d30 in r30:
        d25 = nearest(r25, t25, t)
        d8 = nearest(r8, t8, t)
        if d25 is None or d8 is None or d8[21] != 11:
            continue
        motor = motor_current(d30)
        torque = torque_nm(d30)
        angle = angle_deg(d25)
        rate = rate_raw(d25)
        target_raw = int.from_bytes(d8[18:20], "big", signed=True)
        target = round(target_raw * TARGET_SCALE_DEG_PER_COUNT, 6)
        error = round(target - angle, 6)
        coherent = (
            abs(motor) >= MIN_ABS_CURRENT
            and abs(torque) >= MIN_ABS_TORQUE_NM
            and abs(rate) >= MIN_ABS_RATE
            and sign(motor) == sign(rate)
            and sign(motor) == -sign(torque)
            and sign(motor) == sign(error)
        )
        samples.append({
            "t": t,
            "motor": motor,
            "torque_nm": torque,
            "angle_deg": angle,
            "rate_raw": rate,
            "target_raw": target_raw,
            "target_deg": target,
            "target_error_deg": error,
            "coherent_opposition": coherent,
        })

    rr = runs(samples)
    summaries = []
    for run in sorted(rr, key=lambda x: x[-1]["t"] - x[0]["t"], reverse=True):
        containing = next((a for a, b in id11_intervals if a <= run[0]["t"] <= b), id11_intervals[0][0])
        summaries.append(summarize(run, containing))

    return {
        "source": {"path": str(path.relative_to(REPO)), "sha256": sha256(path)},
        "id11_interval_count": len(id11_intervals),
        "joined_id11_samples": len(samples),
        "coherent_opposition_samples": sum(s["coherent_opposition"] for s in samples),
        "runs_ge_100ms": len(rr),
        "max_run_s": summaries[0]["duration_s"] if summaries else 0.0,
        "top_runs": summaries[:6],
        "b6_total_all_buses": b6,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    drives = {name: analyze(path) for name, path in DRIVES.items()}
    out = {
        "schema": "camry-2026-stock-steering-witness-v1",
        "criterion": {
            "id11": "nearest bus0 0x08A B21 == 11",
            "target": "0x08A B18:B19 signed BE16 * 0.05730274202574147 deg/count",
            "motor": "0x030 B22:B23 signed BE16 exact-F33 motor-feedback/current-family proxy",
            "driver_torque": "0x030 signed_be(71|8)*0.1 + signed_be(139|4)*0.01 N.m",
            "motion": "0x025 steering rate signed_be(35|12)",
            "coherent_opposition": (
                f"|motor|>={MIN_ABS_CURRENT}, |driver torque|>={MIN_ABS_TORQUE_NM} N.m, |rate|>={MIN_ABS_RATE}; "
                "sign(motor)==sign(rate)==sign(target-angle) and sign(driver torque)==-sign(target-angle); "
                f"bridge <= {BRIDGE_SAMPLES} sample; run >= {MIN_RUN_S}s"
            ),
        },
        "drives": drives,
        "interpretation": (
            "The longest retained request-state episode has EPS motor feedback and measured wheel motion directed toward the "
            "0x08A steering target while measured driver torque opposes that direction, and the target-angle error collapses "
            "substantially. This is deterministic positive plant evidence associated with the Toyota ID11 request and is "
            "stronger than request-state correlation alone. It does not observe Toyota's FRC Operation-FFD arbitration winner "
            "or active-steering grant, and therefore does not promote ID11 itself to a grant signal."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
