#!/usr/bin/env python3
"""Join the extracted 2026-09-30 Camry VMC corpus to per-status-frame rows.

Reads ``manifest.json`` and each route's ``.npz``/``.json`` produced by
extract_camry_20260930_vmc_corpus.py, decodes the raw 32-byte 0x081 status and
0x08A request payloads, classifies each delivered request's origin by exact
32-byte payload match against host sendcan and native CAN traffic, and joins
preceding-only carState/carControl/carOutput/longitudinalPlan/selfdriveState/
wheel/pedal samples onto every retained status frame. Writes
``<route>.joined.npz`` and ``<route>.joined.json`` next to the corpus.

Invocation (repository root, uv environment providing numpy):

  uv run python -m tools.targets.camry.analysis.join_camry_20260930_vmc_corpus \
    --corpus-dir build/cache/camry_20260930_vmc_corpus \
    --routes 00000089--0dd1afd752

``--corpus-dir`` accepts any extraction output directory, including an
existing corpus extracted elsewhere; the default is the ignored repository
cache path. Byte decoding, origin classification, age windows, and duplicate
handling are identical to the original offline join: preceding-only samples
with request windows of 75 ms, carState/carControl/carOutput/wheel/pedal
windows of 60 ms, and plan/selfdriveState windows of 120 ms. No universal
0x081 B6 bit-7 or B26 physical semantics are asserted; decoded fields keep
their structural names.
"""
from __future__ import annotations

import argparse
import bisect
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from tools import REPO_ROOT

ROOT = REPO_ROOT
DEFAULT_CORPUS_DIR = ROOT / "build/cache/camry_20260930_vmc_corpus"
REQUEST_COLUMNS = ["upper", "lower", "id_upper", "id_lower", "allocation_upper", "allocation_lower", "latch", "hold", "sequence", "lateral_id"]
PHASES = {0: "unknown", 1: "driver_brake", 2: "driver_gas", 3: "standstill", 4: "op_braking", 5: "op_accelerating", 6: "op_near_zero", 7: "native_or_stock_cruise", 8: "manual_moving"}


def word(b, offset):
  v = b[:, offset].astype(np.int32) * 256 + b[:, offset + 1]
  return np.where(v >= 32768, v - 65536, v)


def requests(b):
  if not len(b):
    return np.empty((0, 10))
  return np.column_stack((word(b, 8) * .001, word(b, 11) * .001, b[:, 6] >> 2, b[:, 7] >> 2,
                          b[:, 6] & 3, b[:, 7] & 3, (b[:, 3] >> 3) & 1, (b[:, 4] >> 5) & 1,
                          b[:, 26] & 63, b[:, 21] & 63))


def preceding(a, t, max_age):
  result = np.full((len(t), a.shape[1]), np.nan)
  ages = np.full(len(t), np.nan)
  if len(a):
    ix = np.searchsorted(a[:, 0], t, side="right") - 1
    valid = ix >= 0
    safe = np.maximum(ix, 0)
    age = t - a[safe, 0]
    valid &= (age >= 0) & (age <= max_age)
    result[valid] = a[safe[valid]]
    ages[valid] = age[valid]
  return result, ages


def dominant(a, src_col, mask=None):
  if mask is None:
    mask = np.ones(len(a), bool)
  values = a[mask, src_col]
  if not len(values):
    return None
  return int(Counter(values.astype(int)).most_common(1)[0][0])


def join(route: str, corpus_dir: Path):
  data = np.load(corpus_dir / (route + ".npz"))
  meta = json.loads((corpus_dir / (route + ".json")).read_text())
  s, sb = data["status"], data["status_bytes"]
  source = dominant(s, 2, s[:, 2] < 4)
  if source is None:
    return None
  keep = s[:, 2] == source
  s, sb = s[keep], sb[keep]
  t = s[:, 0]
  q, qb = data["req"], data["req_bytes"]
  native_source = dominant(q, 3, (q[:, 2] == 0) & (q[:, 3] < 4))
  native_mask = (q[:, 2] == 0) & (q[:, 3] == native_source) if native_source is not None else np.zeros(len(q), bool)
  host_mask = (q[:, 2] == 1) & (q[:, 3] == source)
  delivered_mask = (q[:, 2] == 0) & (q[:, 3] == source + 128)
  native_map = defaultdict(list)
  host_map = defaultdict(list)
  for i in np.flatnonzero(native_mask):
    native_map[qb[i].tobytes()].append(float(q[i, 0]))
  for i in np.flatnonzero(host_mask):
    host_map[qb[i].tobytes()].append(float(q[i, 0]))
  delivered_q = q[delivered_mask]
  delivered_b = qb[delivered_mask]
  origins = []
  host_match_ages = []
  native_match_ages = []
  for qi, b in zip(delivered_q, delivered_b):
    time = qi[0]
    payload = b.tobytes()
    ages = []
    for mapping in (host_map, native_map):
      stamps = mapping.get(payload, ())
      ix = bisect.bisect_right(stamps, time + .000001) - 1
      age = time - stamps[ix] if ix >= 0 else float("nan")
      ages.append(age if -.000001 <= age <= .1 else float("nan"))
    h, n = np.isfinite(ages)
    origins.append(3 if h and n else 1 if h else 2 if n else 0)
    host_match_ages.append(ages[0])
    native_match_ages.append(ages[1])
  delivered_all = np.column_stack((delivered_q[:, 0], requests(delivered_b), np.asarray(origins))) if len(delivered_q) else np.empty((0, 12))
  native_all = np.column_stack((q[native_mask, 0], requests(qb[native_mask])))
  host_all = np.column_stack((q[host_mask, 0], requests(qb[host_mask])))
  applied, a_age = preceding(delivered_all, t, .075)
  native, n_age = preceding(native_all, t, .075)
  host, h_age = preceding(host_all, t, .075)
  cs, cs_age = preceding(data["cs"], t, .06)
  cc, cc_age = preceding(data["cc"], t, .06)
  out, out_age = preceding(data["out"], t, .06)
  plan, plan_age = preceding(data["plan"], t, .12)
  sd, sd_age = preceding(data["sd"], t, .12)
  wheel = data["wheel"]
  wheel_source = dominant(wheel, 2)
  wheel_rows = wheel[wheel[:, 2] == wheel_source] if wheel_source is not None else wheel
  wh, wh_age = preceding(wheel_rows, t, .06)
  pedal = data["pedal"]
  gas_source = dominant(pedal, 2, np.isfinite(pedal[:, 3]))
  brake_source = dominant(pedal, 2, np.isfinite(pedal[:, 4]))
  gas_rows = pedal[(pedal[:, 2] == gas_source) & np.isfinite(pedal[:, 3])] if gas_source is not None else np.empty((0, 5))
  brake_rows = pedal[(pedal[:, 2] == brake_source) & np.isfinite(pedal[:, 4])] if brake_source is not None else np.empty((0, 5))
  gas, gas_age = preceding(gas_rows, t, .06)
  brake, brake_age = preceding(brake_rows, t, .06)
  gas_on = np.where(np.isfinite(gas[:, 3]), gas[:, 3] > 0, cs[:, 5] > 0)
  brake_on = np.where(np.isfinite(brake[:, 4]), brake[:, 4] > 0, cs[:, 6] > 0)
  v = np.where(np.isfinite(wh[:, 3]) & (wh[:, 4] == 0), wh[:, 3], cs[:, 2])
  standing = np.isfinite(v) & (abs(v) < .03)
  mode_long = meta["cp"].get("openpilotLongitudinalControl") if meta["cp"] else None
  op = np.isfinite(cc[:, 0]) & (cc[:, 3] == 1) & (mode_long is True)
  native_active = ((applied[:, 7] == 1) | (native[:, 7] == 1))
  phase = np.zeros(len(t), np.int8)
  phase[np.isfinite(v) & ~standing] = 8
  phase[native_active & ~standing] = 7
  phase[op & (cc[:, 2] < -.3) & ~standing] = 4
  phase[op & (cc[:, 2] > .3) & ~standing] = 5
  phase[op & (abs(cc[:, 2]) <= .3) & ~standing] = 6
  phase[standing] = 3
  phase[gas_on] = 2
  phase[brake_on] = 1
  joined = {
    "t": t, "segment": s[:, 1], "bytes": sb,
    "words": np.column_stack([word(sb, i) for i in range(0, 28, 2)]),
    "result_id": sb[:, 6] & 63, "result_high_bits": sb[:, 6] >> 6,
    "request_loss": ((sb[:, 11] >> 4) & 1), "lateral_id": sb[:, 13] & 63,
    "cs": cs, "cc": cc, "out": out, "plan": plan, "sd": sd,
    "wheel": wh, "gas": gas, "brake": brake, "v": v, "gas_on": gas_on, "brake_on": brake_on,
    "applied": applied[:, 1:11], "origin": applied[:, 11], "native": native[:, 1:], "host": host[:, 1:],
    "phase": phase,
    "age_applied": a_age, "age_native": n_age, "age_host": h_age, "age_cs": cs_age, "age_cc": cc_age,
    "age_out": out_age, "age_plan": plan_age, "age_sd": sd_age, "age_wheel": wh_age,
    "age_gas": gas_age, "age_brake": brake_age,
  }
  np.savez(corpus_dir / (route + ".joined.npz"), **joined)
  ages = np.asarray(host_match_ages)
  finite = ages[np.isfinite(ages)]
  info = {"route": route, "status_source": source, "native_request_source": native_source,
          "wheel_source": wheel_source, "gas_source": gas_source, "brake_source": brake_source,
          "rows": len(t), "phase_counts": {PHASES[int(k)]: int(v) for k, v in Counter(phase).items()},
          "request_columns": REQUEST_COLUMNS, "word_offsets": list(range(0, 28, 2)),
          "delivered_origin_counts": {str(k): v for k, v in Counter(origins).items()},
          "host_confirmation_age_ms_median": float(np.median(finite) * 1000) if len(finite) else None,
          "host_confirmation_age_ms_p95": float(np.quantile(finite, .95) * 1000) if len(finite) else None,
          "unknown_applied_rows": int(np.isnan(applied[:, 0]).sum()),
          "missing_cs_rows": int(np.isnan(cs[:, 0]).sum()), "missing_cc_rows": int(np.isnan(cc[:, 0]).sum()),
          "bounds": {"status_native_only": True, "join": "preceding only; status native source chosen by dominant count; CS/CC 60ms; request 75ms",
                     "origin": "exact 32-byte match to host send or native FRC receive <=100ms, simultaneous logger batch allowed; 1 host,2 native,3 both,0 unknown",
                     "timing": "CAN log batch timestamps, not physical wire timestamps",
                     "phase": "pedal states override standstill/control classes; native_or_stock_cruise is observed request latch, not proven ECU execution"}}
  (corpus_dir / (route + ".joined.json")).write_text(json.dumps(info, indent=2))
  print(json.dumps(info), flush=True)
  return joined


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS_DIR, help=f"extraction output directory to read (default {DEFAULT_CORPUS_DIR}, ignored by git)")
  parser.add_argument("--routes", nargs="*", help="restrict to these route ids")
  parser.add_argument("--primary", action="store_true", help="restrict to the five primary routes")
  parser.add_argument("--missing", action="store_true", help="skip routes whose .joined.npz and .joined.json outputs already exist")
  args = parser.parse_args()
  manifest = json.loads((args.corpus_dir / "manifest.json").read_text())
  for r in manifest["routes"]:
    if args.primary and not r["primary"]:
      continue
    if args.routes and r["route"] not in args.routes:
      continue
    if args.missing and (args.corpus_dir / (r["route"] + ".joined.npz")).exists() and (args.corpus_dir / (r["route"] + ".joined.json")).exists():
      continue
    if (args.corpus_dir / (r["route"] + ".npz")).exists():
      join(r["route"], args.corpus_dir)


if __name__ == "__main__":
  main()
