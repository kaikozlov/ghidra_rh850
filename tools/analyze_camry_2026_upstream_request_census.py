#!/usr/bin/env python3
"""Complete field census of the retained Bus-4 (Panda bus 0) 0x08A upstream
lateral-request frames across the two relay-correct Camry drives.

Deterministic offline analysis over tracked captures; no vehicle I/O. The
census enumerates every application byte (B0..B27) partitioned by B21 Target
Lateral ID state, proves the B8:B9 == B11:B12 duplication and the constant
0x7FFF sentinel slots, closes the cruise-state mirror tuple set, records the
B24 request-level coupling, and bounds REQUEST_WORD_B8 semantics through four
negative joins (speed-derived acceleration, 0x025 steering angle, 0x030
driver torque, and the B18:B19 target-angle rate).

The GTS+ join block embeds the current generation-20 EMPS_P5 DID 0x1CEE
structured record (monitors 2069..2072) recovered through `tools/gts did
EMPS_P5 0x1CEE --json`, including the full 19-value Target Lateral ID pattern
dictionary, plus the FRC_P5 DID 0x1901 set-speed concept corroboration.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
DRIVES = {
  "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
  "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}

MAX_INLINE_VALUES = 8
NEAREST_WINDOW_MS = 50
ACCEL_DT_MIN_S = 0.5


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
      h.update(chunk)
  return h.hexdigest()


def iter_rows(path: Path):
  with gzip.open(path, "rt") as f:
    for line in f:
      seg, t, src, addr, hx = json.loads(line)
      yield seg, t, src, addr, bytes.fromhex(hx)


def collect(path: Path):
  """Return (deduped bus-0 0x08A frames, 0x0AA speeds, 0x025 angles, 0x030 torques)."""
  req, spd, ang, trq = [], [], [], []
  seen = set()
  for seg, t, src, addr, d in iter_rows(path):
    if src != 0:
      continue
    if addr == 0x08A:
      key = (seg, t)
      if key not in seen:
        seen.add(key)
        req.append((t, d))
    elif addr == 0x0AA:
      # bounded observer decode: signed16 BE *0.01 km/h (join is negative-only)
      spd.append((t, int.from_bytes(d[0:2], "big", signed=True) * 0.01))
    elif addr == 0x025:
      coarse = int.from_bytes(bytes([d[0] & 0x0F, d[1]]), "big", signed=True)
      frac = (d[2] >> 4) & 0x0F
      frac = frac - 16 if frac > 7 else frac
      ang.append((t, coarse * 1.5 + frac * 0.1))
    elif addr == 0x030:
      trq.append((t, int.from_bytes(d[8:9], "big", signed=True) * 0.1))
  return req, spd, ang, trq


def nearest(series, t):
  lo, hi = 0, len(series) - 1
  while lo < hi:
    mid = (lo + hi) // 2
    if series[mid][0] < t:
      lo = mid + 1
    else:
      hi = mid
  return series[lo]


def corr(xs, ys):
  n = len(xs)
  if n < 3:
    return None
  mx, my = sum(xs) / n, sum(ys) / n
  sxx = sum((x - mx) ** 2 for x in xs)
  syy = sum((y - my) ** 2 for y in ys)
  if sxx == 0 or syy == 0:
    return None
  sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
  return sxy / (sxx * syy) ** 0.5


def request_word(req):
  return [(t, int.from_bytes(d[8:10], "big", signed=True),
           int.from_bytes(d[18:20], "big", signed=True)) for t, d in req]


def negative_joins(req, spd, ang, trq):
  word = request_word(req)
  out = {}
  win = NEAREST_WINDOW_MS * 1e6

  pairs = []
  for t, _, _ in word:
    tt, v = nearest(spd, t)
    if abs(tt - t) < win:
      pairs.append((tt, v))
  xs, ys = [], []
  for i in range(len(pairs) - 40):
    t0, v0 = pairs[i]
    t1, v1 = pairs[i + 40]
    dt = (t1 - t0) / 1e9
    if dt > ACCEL_DT_MIN_S and v0 > 1:
      xs.append((v1 - v0) / dt)
      ys.append(word[i + 20][1])
  out["speed_accel"] = corr(xs, ys)

  for label, series in (("steer_angle_025", ang), ("driver_torque_030", trq)):
    xs, ys = [], []
    for t, w, _ in word:
      tt, v = nearest(series, t)
      if abs(tt - t) < win:
        xs.append(v)
        ys.append(w)
    out[label] = corr(xs, ys)

  xs, ys = [], []
  for i in range(1, len(word) - 1):
    t0, _, a0 = word[i - 1]
    t1, w, a1 = word[i + 1]
    dt = (t1 - t0) / 1e9
    if 0 < dt < 0.2:
      xs.append((a1 - a0) / dt)
      ys.append(w)
  out["target_angle_rate"] = corr(xs, ys)
  return {k: (round(v, 4) if v is not None else None) for k, v in out.items()}


def census_drive(req):
  by_state = {}
  for _, d in req:
    by_state.setdefault(d[21] & 0x3F, []).append(d)
  bytes_census = {}
  for st, frames in sorted(by_state.items()):
    rows = {}
    for i in range(28):
      vals = Counter(d[i] for d in frames)
      row = {"distinct": len(vals)}
      if len(vals) <= MAX_INLINE_VALUES:
        row["values"] = {str(k): v for k, v in sorted(vals.items())}
      rows[f"B{i:02d}"] = row
    bytes_census[str(st)] = {"frames": len(frames), "bytes": rows}
  return bytes_census


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--out", type=Path, default=REPO / "data/generated/camry_2026_upstream_request_field_census.json")
  args = ap.parse_args()

  artifact = {
    "schema": "camry-2026-upstream-request-field-census-v1",
    "drives": {},
    "combined": {},
    "gtsplus_join": {
      "emps_p5_did_0x1cee": {
        "monitors": [
          {"monitor_key": 2069, "name": "Target Lateral ID", "bits": "0-7",
           "mul": 1, "div": 1, "signed": False, "patterns": 19},
          {"monitor_key": 2070, "name": "Cooperative Control in Progress Flag", "bits": "8-15",
           "mul": 1, "div": 1, "signed": False, "pattern_display": {"0": "OFF", "1": "ON"}},
          {"monitor_key": 2071, "name": "Target Steering Angle After Output Compensation", "bits": "16-31",
           "mul": 15, "div": 1, "signed": True, "unit": "deg", "decimal_places": 1},
          {"monitor_key": 2072, "name": "Advanced Drive Target Steering Angle", "bits": "32-47",
           "mul": 15, "div": 1, "signed": True, "unit": "deg", "decimal_places": 1},
        ],
        "target_lateral_id_dictionary": {
          "0": "No Request (Manual Operation)", "1": "PCS", "4": "LDA", "10": "Hands Off LTA",
          "11": "LTA/LCA", "13": "DESA (Slow Deceleration Control)", "15": "DESA (Deceleration Stop Control)",
          "18": "SDG", "19": "PDA", "25": "AP", "27": "Remote Parking", "35": "AD (Lv.3)",
          "37": "EM (Lv.3)", "39": "DES (Lv.3)", "41": "AD (Lv.4)", "43": "EM (Lv.4)",
          "45": "DES (Lv.4)", "49": "Self-Propelled Transport", "63": "Driver Operation",
        },
        "recovered_via": "tools/gts did EMPS_P5 0x1CEE --json (generation-20 NA EMPS_P5.ddb)",
      },
      "frc_p5_set_speed_concept": {
        "did": "0x1901", "names": ["Current Vehicle Speed", "Memory Vehicle Speed"],
        "unit": "km/h", "bits": 32,
        "note": "corroborates the set-speed concept and km/h unit only; not a wire mapping proof",
      },
    },
    "interpretation": {
      "producer_boundary": "0x08A producer remains unidentified; GTS+ Bus-4 ECU dictionaries "
                           "(ABS_P5, Brk_Bst_P5, EPB_P5, BSCM) carry no lateral-request DID "
                           "vocabulary, so GTS+ cannot name the producer from DID semantics.",
      "field_boundary": "Structural names (CRUISE_*, REQUEST_WORD_B8, LATERAL_REQUEST_LEVEL, "
                        "COOPERATIVE_SUBSTATE_FLAG, RESERVED_16BIT_*) are census-bounded, not "
                        "OEM-joined. B21/B26 six-bit boundaries remain encoding assumptions. "
                        "The percent unit on B24 is bounded from the observed 0/50/100 value set.",
      "regression_rule": "No 0x08A-to-B6 stock-LTA transform is implied by scale or topology "
                         "(CORR-135). Passive analysis only; no output authorized.",
    },
  }

  all_req = []
  tuple_counter = Counter()
  inv = Counter()
  for name, path in DRIVES.items():
    req, spd, ang, trq = collect(path)
    all_req.extend((name, t, d) for t, d in req)
    dup8 = sum(1 for _, d in req if d[8] == d[11])
    dup9 = sum(1 for _, d in req if d[9] == d[12])
    sent13 = sum(1 for _, d in req if d[13] == 0x7F and d[14] == 0xFF)
    sent16 = sum(1 for _, d in req if d[16] == 0x7F and d[17] == 0xFF)
    zeros = {f"B{i:02d}": sum(1 for _, d in req if d[i] == 0) for i in (0, 1, 2, 5, 15, 25, 27)}
    word = [w for _, w, _ in request_word(req)]
    artifact["drives"][name] = {
      "source": str(path.relative_to(REPO)),
      "source_sha256": sha256(path),
      "bus0_frames": len(req),
      "duplication_b8_eq_b11": dup8,
      "duplication_b9_eq_b12": dup9,
      "sentinel_b13_b14_0x7fff": sent13,
      "sentinel_b16_b17_0x7fff": sent16,
      "zero_byte_frames": zeros,
      "request_word_b8_raw_range": [min(word), max(word)],
      "byte_census_by_b21_state": census_drive(req),
      "request_word_negative_joins": negative_joins(req, spd, ang, trq),
    }
    for _, d in req:
      tuple_counter[(d[3], d[6], d[7], d[20] >> 6, (d[22] >> 4) & 1,
                     d[21] & 0x3F, (d[23] >> 5) & 1, d[24])] += 1
      st = d[21] & 0x3F
      if st == 11:
        inv["b21_11_frames"] += 1
        inv["b21_11_with_cruise_latch"] += int(d[3] & 0x08 != 0)
        inv["b21_11_with_b24_100"] += int(d[24] == 100)
      elif st == 18:
        inv["b21_18_frames"] += 1
        inv["b21_18_with_b3_clear"] += int(d[3] == 0)
        inv["b21_18_with_b23_bit5"] += int((d[23] >> 5) & 1 == 1)
        inv["b21_18_with_b24_50"] += int(d[24] == 50)
      latch = (d[3] & 0x08) != 0
      mirrors = (d[20] >> 6) == 0b11 and ((d[22] >> 4) & 1) == 1
      inv["latch_frames"] += int(latch)
      inv["latch_mirror_agreement"] += int(latch == mirrors)

  artifact["combined"] = {
    "bus0_frames_total": sum(v["bus0_frames"] for v in artifact["drives"].values()),
    "duplication_total": sum(v["duplication_b8_eq_b11"] for v in artifact["drives"].values()),
    "joint_tuple_census_b3_b6_b7_b20hi_b22b4_b21_b23b5_b24": [
      {"b3": k[0], "b6": k[1], "b7": k[2], "b20_bits7_6": k[3], "b22_bit4": k[4],
       "b21": k[5], "b23_bit5": k[6], "b24": k[7], "count": v}
      for k, v in sorted(tuple_counter.items(), key=lambda kv: (-kv[1], kv[0]))
    ],
    "invariants": dict(sorted(inv.items())),
  }

  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(artifact, indent=1, sort_keys=False) + "\n")
  print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
