#!/usr/bin/env python3
"""Bound the 2026 Camry TSS3 longitudinal request/protection planes from retained CAN."""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from analyze_camry_2026_lta_state_reconciliation import secoc_shape_stats
from analyze_camry_2026_relay_capture import decode_wheel_speed

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
DEFAULT_OUT = REPO / "data/generated/camry_2026_longitudinal_request_plane.json"
DRIVES = {
  "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
  "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
      h.update(chunk)
  return h.hexdigest()


def pearson(xs: list[float], ys: list[float]) -> float | None:
  if len(xs) < 2:
    return None
  mx = statistics.fmean(xs)
  my = statistics.fmean(ys)
  sx = sum((x - mx) ** 2 for x in xs)
  sy = sum((y - my) ** 2 for y in ys)
  if sx == 0 or sy == 0:
    return None
  return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sx * sy)


def regression(xs: list[float], ys: list[float]) -> dict:
  r = pearson(xs, ys)
  mx = statistics.fmean(xs)
  my = statistics.fmean(ys)
  denom = sum((x - mx) ** 2 for x in xs)
  slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
  return {
    "sample_count": len(xs),
    "pearson_r": round(r, 9) if r is not None else None,
    "slope": round(slope, 9),
    "intercept": round(my - slope * mx, 9),
    "x_range": [min(xs), max(xs)],
    "y_range": [round(min(ys), 6), round(max(ys), 6)],
  }


def load_streams(path: Path) -> tuple[dict, int]:
  wanted = {0x00F, 0x08A, 0x0AA, 0x0CA, 0x160}
  streams = defaultdict(list)
  counts = Counter()
  frame_count = 0
  with gzip.open(path, "rt") as f:
    for line in f:
      seg, t, bus, addr, data_hex = json.loads(line)
      seg, t, bus, addr = int(seg), int(t), int(bus), int(addr)
      frame_count += 1
      if addr in wanted:
        data = bytes.fromhex(data_hex)
        streams[(bus, addr)].append((t, seg, data))
        counts[(bus, addr, len(data))] += 1
  for rows in streams.values():
    rows.sort(key=lambda x: x[0])
  return {"streams": streams, "counts": counts}, frame_count


def per_segment(rows):
  out = defaultdict(list)
  for row in rows:
    out[row[1]].append(row)
  return out


def preceding_state(rows_by_seg, seg: int, t: int, decoder) -> bool:
  rows = rows_by_seg.get(seg, [])
  if not rows:
    return False
  ts = [row[0] for row in rows]
  i = bisect.bisect_right(ts, t) - 1
  return decoder(rows[max(0, i)][2])


def nearest_row(rows_by_seg, seg: int, t: int, max_gap_ns: int):
  rows = rows_by_seg.get(seg, [])
  if not rows:
    return None
  ts = [row[0] for row in rows]
  i = bisect.bisect_left(ts, t)
  candidates = [j for j in (i - 1, i) if 0 <= j < len(rows)]
  if not candidates:
    return None
  j = min(candidates, key=lambda k: abs(rows[k][0] - t))
  return rows[j] if abs(rows[j][0] - t) <= max_gap_ns else None


def s16be(data: bytes, offset: int) -> int:
  return int.from_bytes(data[offset:offset + 2], "big", signed=True)


def signed7(raw: int) -> int:
  if raw & 0x80:
    raise ValueError("signed7 candidate has bit7 set")
  return raw if raw < 0x40 else raw - 0x80


def geometry_stats(ca_rows, a8_by_seg) -> dict:
  cruise_rows = []
  violations = Counter()
  for _t, seg, data in ca_rows:
    t = _t
    if not preceding_state(a8_by_seg, seg, t, lambda d: bool(d[3] & 0x08)):
      continue
    upper = s16be(data, 3)
    lower = s16be(data, 5)
    result = s16be(data, 7)
    cruise_rows.append((upper, lower, result))
    if not (lower <= result <= upper):
      nearest = lower if result < lower else upper
      violations[result - nearest] += 1
  in_bounds = len(cruise_rows) - sum(violations.values())
  fields = {}
  for name, idx in (("B3_B4", 0), ("B5_B6", 1), ("B7_B8", 2)):
    vals = [row[idx] * 0.001 for row in cruise_rows]
    fields[name] = {
      "scale_mps2_per_count": 0.001,
      "min_mps2": round(min(vals), 6),
      "median_mps2": round(statistics.median(vals), 6),
      "max_mps2": round(max(vals), 6),
    }
  return {
    "stock_cruise_frame_count": len(cruise_rows),
    "B5_B6_le_B7_B8_le_B3_B4": {
      "matching_frames": in_bounds,
      "matching_fraction": round(in_bounds / len(cruise_rows), 9),
      "violation_raw_delta_from_nearest_bound": {str(k): v for k, v in sorted(violations.items())},
    },
    "signed_be_words": fields,
  }


def cross_plane_stats(x160_rows, ca_by_seg, a8_by_seg) -> dict:
  joined = []
  unsaturated = []
  for t, seg, data in x160_rows:
    if not preceding_state(a8_by_seg, seg, t, lambda d: bool(d[3] & 0x08)):
      continue
    ca = nearest_row(ca_by_seg, seg, t, 30_000_000)
    if ca is None:
      continue
    cdata = ca[2]
    x = signed7(data[12])
    upper = s16be(cdata, 3) * 0.001
    lower = s16be(cdata, 5) * 0.001
    result = s16be(cdata, 7) * 0.001
    joined.append((x, result))
    if result > lower + 0.05 and result < upper - 0.05:
      unsaturated.append((x, result))
  xs = [x for x, _ in joined]
  ys = [y for _, y in joined]
  uxs = [x for x, _ in unsaturated]
  uys = [y for _, y in unsaturated]
  return {
    "join": "native bus1 0x160 B12 signed7 to nearest protected bus0 0x0CA B7:B8 within 30 ms while stock cruise latch is set",
    "all": regression(xs, ys),
    "unsaturated_result": {
      "filter": "B7:B8 > B5:B6 + 0.05 m/s^2 and B7:B8 < B3:B4 - 0.05 m/s^2",
      **regression(uxs, uys),
    },
  }


def interp(ts: list[float], vals: list[float], t: float) -> float:
  i = bisect.bisect_left(ts, t)
  if i <= 0:
    return vals[0]
  if i >= len(ts):
    return vals[-1]
  t0, v0 = ts[i - 1], vals[i - 1]
  t1, v1 = ts[i], vals[i]
  if t1 == t0:
    return v0
  f = (t - t0) / (t1 - t0)
  return v0 + f * (v1 - v0)


def accel_correlation(ca_rows, wheel_rows, a8_by_seg) -> dict:
  wheel_pairs = defaultdict(list)
  for t, seg, data in wheel_rows:
    wheel_pairs[seg].append((t / 1e9, decode_wheel_speed(data) / 3.6))
  wheels_by_seg = {
    seg: ([t for t, _v in rows], [v for _t, v in rows])
    for seg, rows in wheel_pairs.items()
  }
  ca_by_seg = defaultdict(list)
  for t, seg, data in ca_rows:
    if preceding_state(a8_by_seg, seg, t, lambda d: bool(d[3] & 0x08)):
      ca_by_seg[seg].append((t / 1e9, s16be(data, 7) * 0.001))

  sweep = []
  for lag_tenths in range(-20, 31):
    lag = lag_tenths / 10.0
    xs = []
    ys = []
    for seg, ca in ca_by_seg.items():
      wheel_series = wheels_by_seg.get(seg)
      if wheel_series is None or len(wheel_series[0]) < 2:
        continue
      ts, vals = wheel_series
      lo = ts[0] + 0.5 - lag
      hi = ts[-1] - 0.5 - lag
      for t, result in ca:
        if not (lo <= t <= hi):
          continue
        accel = interp(ts, vals, t + lag + 0.5) - interp(ts, vals, t + lag - 0.5)
        xs.append(result)
        ys.append(accel)
    r = pearson(xs, ys)
    if r is not None:
      sweep.append((abs(r), r, lag, len(xs)))
  _abs_r, r, lag, n = max(sweep)
  return {
    "method": "1.0 s centered derivative of decoded 0x0AA mean wheel speed; lag is a correlation shift only",
    "best_shift_s": lag,
    "pearson_r": round(r, 9),
    "sample_count": n,
  }


def analyze_drive(path: Path) -> dict:
  loaded, frame_count = load_streams(path)
  streams = loaded["streams"]
  counts = loaded["counts"]
  ca = streams[(0, 0x0CA)]
  sync = streams[(0, 0x00F)]
  a8 = streams[(0, 0x08A)]
  x160 = streams[(1, 0x160)]
  wheels = streams[(0, 0x0AA)]
  a8_by_seg = per_segment(a8)
  ca_by_seg = per_segment(ca)

  secoc = secoc_shape_stats(ca, sync, app_sequence_byte=2)
  secoc["auth28_unique_fraction"] = round(secoc["auth28_unique_count"] / secoc["frame_count"], 9)

  bus_counts = {
    str(bus): counts.get((bus, 0x0CA, 32), 0)
    for bus in range(3)
  }
  x160_counts = {
    str(bus): counts.get((bus, 0x160, 32), 0)
    for bus in range(3)
  }
  last4 = Counter(data[-4:].hex() for _t, _seg, data in x160)
  high_bit = Counter((data[12] >> 7) & 1 for _t, _seg, data in x160)

  return {
    "source": {
      "path": str(path.relative_to(REPO)),
      "sha256": sha256(path),
      "frame_count": frame_count,
    },
    "protected_0x0CA": {
      "dlc": 32,
      "panda_bus_counts": bus_counts,
      "secoc_shape_bus0": secoc,
      "longitudinal_geometry": geometry_stats(ca, a8_by_seg),
      "measured_acceleration_join": accel_correlation(ca, wheels, a8_by_seg),
    },
    "plaintext_candidate_0x160": {
      "dlc": 32,
      "panda_bus_counts": x160_counts,
      "native_bus1_frame_count": len(x160),
      "last4_histogram": dict(sorted(last4.items())),
      "B12_high_bit_histogram": {str(k): v for k, v in sorted(high_bit.items())},
      "B12_signed7_to_0x0CA_result": cross_plane_stats(x160, ca_by_seg, a8_by_seg),
    },
  }


def build() -> dict:
  return {
    "schema": "camry-2026-longitudinal-request-plane-v1",
    "vehicle": "2026 Toyota Camry Hybrid / exact maintainer vehicle",
    "drives": {name: analyze_drive(path) for name, path in DRIVES.items()},
    "gtsplus_semantic_bridge": {
      "frc": {
        "0x1B03..0x1B07": "FRC_P5 longitudinal request/permission Data Monitor surface, including ISA upper-limit ID/acceleration, allocation/shift/response, and brake/stop permissions",
        "PCS_5280": "TSS required longitudinal ID + lower-limit acceleration + force/shift/EPB/override/priority fields",
        "PCS_5281": "TSS request longitudinal ID + upper-limit acceleration + force-distribution field",
        "PCS_5284_57DB": "arbitration-result longitudinal ID / arbitration-result acceleration",
      },
      "brake": {
        "0x10A1": "Request Acceleration of Upper Limit from Toyota Safety Sense (signed16, 0.001 m/s^2)",
        "0x10A2": "Request Acceleration of Lower Limit from Toyota Safety Sense (signed16, 0.001 m/s^2)",
        "0x10A3": "Request Acceleration and Deceleration ID of Upper Limit from Toyota Safety Sense",
        "0x10A4": "Request Acceleration and Deceleration ID of Lower Limit from Toyota Safety Sense",
      },
    },
    "interpretation": {
      "0x0CA": "Already-protected/downstream-looking Toyota-P5 longitudinal PDU. Its FV4||MAC28 structural match rejects treating 0x0CA itself as the unsigned FRC-to-signer request.",
      "0x0CA_words": "B3:B4, B5:B6, and B7:B8 form a strong upper/lower/result-like signed16 x0.001 m/s^2 triplet, but exact byte-to-OEM-name assignment awaits synchronized diagnostic/FFD capture.",
      "0x160_B12": "High-value non-SecOC cross-plane candidate. Signed7 B12 maps tightly to protected 0x0CA B7:B8 during stock cruise, but producer, direction, and OEM request identity are not yet proved.",
      "next_discriminator": "Run tools/camry_tss3_request_capture.py during stock DRCC and join FRC 0x792 DIDs 1B03..1B07 plus Brake 0x7B0 DIDs 10A1..10A4 to native bus1 0x160 and protected bus0/bus2 0x0CA.",
    },
  }


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()
  result = build()
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
  print(args.output)


if __name__ == "__main__":
  main()
