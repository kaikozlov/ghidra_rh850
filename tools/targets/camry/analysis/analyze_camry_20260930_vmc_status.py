#!/usr/bin/env python3
"""Analyze the retained Camry VMC corpus without assigning unproved OEM names.

Consume extract_camry_20260930_vmc_corpus and join_camry_20260930_vmc_corpus
outputs. Raw rlogs and NumPy caches remain external/ignored; this producer saves
compact evidence under data/generated/camry_20260930_vmc_status. It requires
NumPy, not an openpilot checkout or live vehicle connection. Supply --logs-root
to bind an older extraction cache to the original rlog identities.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

from tools import REPO_ROOT

DEFAULT_CORPUS = REPO_ROOT / "build/cache/camry_20260930_vmc_corpus"
DEFAULT_OUTPUT = REPO_ROOT / "data/generated/camry_20260930_vmc_status"
PHASES = {0: "unknown", 1: "driver_brake", 2: "driver_gas", 3: "standstill", 4: "op_braking",
          5: "op_accelerating", 6: "op_near_zero", 7: "native_or_stock_cruise", 8: "manual_moving"}
SAMPLES = (
  ("0000003f--36e72f5fdc", 1318.86, "stock braking ramp start"),
  ("00000086--575a5fd6a5", 253.879, "OP weak braking before pedal"),
  ("00000086--575a5fd6a5", 254.03, "driver brake after disengagement"),
  ("00000086--575a5fd6a5", 259.792, "driver accelerator"),
  ("00000086--575a5fd6a5", 272.849, "normal OP acceleration"),
  ("00000087--7e7f16f8af", 10.0, "stationary with brake held"),
)


def sha256(path: Path) -> str:
  digest = hashlib.sha256()
  with path.open("rb") as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
      digest.update(chunk)
  return digest.hexdigest()


def save_json(path: Path, value: dict | list) -> None:
  path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def save_csv(path: Path, rows: list[dict]) -> None:
  with path.open("w", newline="") as stream:
    if not rows:
      return
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    for row in rows:
      writer.writerow({key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value
                       for key, value in row.items()})


def fractions(mask: np.ndarray, relation: np.ndarray) -> dict:
  n = int(mask.sum())
  ok = int(relation[mask].sum())
  return {"n": n, "ok": ok, "fraction": ok / n if n else None}


def quants(values: np.ndarray) -> list[float] | None:
  values = values[np.isfinite(values)]
  return [float(value) for value in np.quantile(values, [.05, .5, .95])] if len(values) else None


def fit(x: np.ndarray, y: np.ndarray) -> dict:
  valid = np.isfinite(x) & np.isfinite(y)
  x, y = x[valid], y[valid]
  if len(x) < 10 or np.std(x) < .02 or np.std(y) == 0:
    return {"n": len(x), "slope": None, "intercept": None, "r": None}
  slope, intercept = np.polyfit(x, y, 1)
  return {"n": len(x), "slope": float(slope), "intercept": float(intercept),
          "r": float(np.corrcoef(x, y)[0, 1])}


def runs(mask: np.ndarray) -> list[tuple[int, int]]:
  edges = np.diff(np.r_[False, mask, False].astype(np.int8))
  return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def signed13(word: np.ndarray) -> np.ndarray:
  low = word & 8191
  return np.where(low >= 4096, low - 8192, low)


def route_report(route: dict, meta: dict, info: dict, j: dict) -> tuple[dict, list[dict], list[dict]]:
  w = j["words"]
  n = len(w)
  b4, b18, b20, b22, b24, b26 = [w[:, offset // 2] for offset in (4, 18, 20, 22, 24, 26)]
  residual = b18 - np.maximum(b4, b24)
  moving = np.isfinite(j["v"]) & (j["v"] > .5)
  closed = np.isfinite(j["age_gas"]) & (j["gas"][:, 3] == 0)
  opened = np.isfinite(j["age_gas"]) & (j["gas"][:, 3] > 0)
  brake_on = np.isfinite(j["age_brake"]) & (j["brake"][:, 4] == 1)
  native_idle = np.isfinite(j["age_native"]) & (j["native"][:, 2] == 0) & (j["native"][:, 3] == 4)
  clamped_residual = b18 - np.minimum(np.maximum(b4, b24), b22)
  bit7 = (j["result_high_bits"] & 2) != 0
  cs_standstill, cs_nonstandstill = j["cs"][:, 7] == 1, j["cs"][:, 7] == 0
  cp = meta.get("cp") or {}
  row = {
    "route": route["route"], "primary": route["primary"], "segments": len(route["files"]),
    "git": (meta.get("init") or {}).get("gitCommit"),
    "openpilotLongitudinalControl": cp.get("openpilotLongitudinalControl"),
    "n_status": n, "moving_rows": int(moving.sum()), "status_source": info["status_source"],
    "vmc_span_s": float(j["t"][-1] - j["t"][0]) if n else 0,
    "observed_vmc_seconds": float(np.minimum(np.maximum(np.diff(j["t"]), 0), .1).sum()),
    "decode_errors": meta["errors"],
    "relation_max_exact": fractions(np.ones(n, bool), residual == 0),
    "relation_max_within5": fractions(np.ones(n, bool), abs(residual) <= 5),
    "relation_max_moving": fractions(moving, residual == 0),
    "relation_max_informative": fractions(b4 != b24, residual == 0),
    "relation_clamped_envelope_exact": fractions(np.ones(n, bool), clamped_residual == 0),
    "relation_clamped_envelope_within5": fractions(np.ones(n, bool), abs(clamped_residual) <= 5),
    "b22_ceiling": fractions(np.ones(n, bool), b22 >= np.maximum.reduce((b4, b18, b20, b24))),
    "b22_ge_b18": fractions(np.ones(n, bool), b22 >= b18),
    "closed_b24_equals_b20": fractions(closed, b24 == b20),
    "closed_b24_within2_b20": fractions(closed, abs(b24 - b20) <= 2),
    "open_b24_ge_b20": fractions(opened, b24 >= b20),
    "brake_on_b26_nonzero": fractions(brake_on, b26 != 0),
    "b26_nonzero_s13_negative": fractions(b26 != 0, signed13(b26) < 0),
    "b26_high3bit_counts": dict(Counter((b26 >> 13).tolist())),
    "idle_native_upper_vs_b20": fit(j["native"][native_idle, 0], b20[native_idle] * .001),
    "idle_native_upper_minus_b20_q": quants(j["native"][native_idle, 0] - b20[native_idle] * .001),
    "result_id_counts": dict(Counter(j["result_id"].tolist())),
    "request_loss_rows": int(j["request_loss"].sum()),
    "b18_above_max_rows": int((residual > 0).sum()), "b18_below_max_rows": int((residual < 0).sum()),
    "b6_bit7": {"known_cs_standstill": int(cs_standstill.sum()),
                "known_cs_standstill_bit7": int((cs_standstill & bit7).sum()),
                "known_cs_nonstandstill_bit7": int((cs_nonstandstill & bit7).sum()),
                "moving_over_0_5_bit7": int((moving & bit7).sum())},
  }
  phases = []
  for code, label in PHASES.items():
    mask = j["phase"] == code
    if not mask.any():
      continue
    fresh = mask & np.isfinite(j["age_applied"]) & np.isfinite(j["age_cs"])
    phase = {
      "route": route["route"], "primary": route["primary"], "mode_long": cp.get("openpilotLongitudinalControl"),
      "git": row["git"], "phase": label, "n": int(mask.sum()), "n_fresh_request_cs": int(fresh.sum()),
      "result_ids": dict(Counter(j["result_id"][mask].tolist())),
      "applied_q": quants(j["applied"][fresh, 0]), "native_q": quants(j["native"][fresh, 0]),
      "wheel_aEgo_q": quants(j["cs"][fresh, 4]),
      "B4_minus_applied_q": quants(b4[fresh] * .001 - j["applied"][fresh, 0]),
      "aEgo_minus_applied_q": quants(j["cs"][fresh, 4] - j["applied"][fresh, 0]),
      "B4_vs_applied_fit": fit(j["applied"][fresh, 0], b4[fresh] * .001),
      "B4_vs_aEgo_fit": fit(j["cs"][fresh, 4], b4[fresh] * .001),
    }
    for offset in (4, 18, 20, 22, 24, 26):
      phase[f"B{offset}_q_counts"] = quants(w[mask, offset // 2])
    phases.append(phase)
  exceptions = []
  transitions = {"brake_change_0_5s": j["brake_on"], "gas_change_0_5s": j["gas_on"],
                 "op_change_0_5s": j["cc"][:, 3] == 1}
  for i in np.flatnonzero(residual != 0):
    window = slice(np.searchsorted(j["t"], j["t"][i] - .5), np.searchsorted(j["t"], j["t"][i] + .5, side="right"))
    exceptions.append({
      "route": route["route"], "t_route": float(j["t"][i]), "segment": int(j["segment"][i]),
      "residual_counts": int(residual[i]), "B4": int(b4[i]), "B18": int(b18[i]),
      "B20": int(b20[i]), "B22": int(b22[i]), "B24": int(b24[i]), "B26_signed13": int(signed13(b26[i])),
      "clamped_residual_counts": int(clamped_residual[i]),
      "gas_fraction": float(j["gas"][i, 3]) if np.isfinite(j["gas"][i, 3]) else None,
      "b6_high_bits": int(j["result_high_bits"][i]), "moving": bool(moving[i]),
      "brake_on": bool(j["brake_on"][i]), "gas_on": bool(j["gas_on"][i]),
      "result_id": int(j["result_id"][i]), "request_loss": bool(j["request_loss"][i]),
      "status_hex": j["bytes"][i].tobytes().hex(),
      **{name: bool(np.any(values[window] != values[i])) for name, values in transitions.items()},
    })
  return row, phases, exceptions


def stock_epochs(route: str, j: dict) -> list[dict]:
  """Retain the original excitation gate, then compare direct errors (not fit residuals)."""
  t, v, native = j["t"], j["v"], j["native"]
  wheel_accel = np.full(len(t), np.nan)
  idx = np.flatnonzero(np.isfinite(v) & np.isfinite(j["age_wheel"]))
  # Different status payloads can share a logger-batch timestamp. Preserve
  # those status rows, but differentiation needs distinct time knots.
  times, first, inverse = np.unique(t[idx], return_index=True, return_inverse=True)
  if len(times) > 10:
    speeds = v[idx[first]]
    # Centered median is an excitation selector, not a physical latency oracle.
    smooth = np.array([np.median(speeds[max(0, i - 5):min(len(speeds), i + 6)]) for i in range(len(speeds))])
    wheel_accel[idx] = np.gradient(smooth, times)[inverse]
  base = (np.isfinite(j["age_native"]) & (native[:, 6] == 1) & np.isfinite(j["age_cs"])
          & ~j["gas_on"] & ~j["brake_on"] & np.isfinite(v) & (v > .5))
  result = []
  for start, end in runs(base):
    duration = t[end - 1] - t[start]
    if duration < 2:
      continue
    request_range = float(np.ptp(native[start:end, 0]))
    derived = wheel_accel[start:end]
    finite = derived[np.isfinite(derived)]
    if request_range < .5 and (not len(finite) or np.ptp(finite) < .4):
      continue
    # Match the parent direct-difference check of the original rounded episode CSV.
    beginning, span = round(float(t[start]), 2), round(float(duration), 2)
    mask = base & np.isfinite(j["age_applied"]) & (t >= beginning) & (t <= beginning + span)
    if mask.sum() < 20:
      continue
    b4, request, body = j["words"][mask, 2] * .001, j["applied"][mask, 0], j["cs"][mask, 4]
    result.append({
      "route": route, "segment": int(j["segment"][start]), "t_start": beginning, "duration_s": span,
      "n": int(mask.sum()), "native_request_range_mps2": request_range,
      "request_rmse_mps2": float(np.sqrt(np.mean((b4 - request) ** 2))),
      "wheel_carstate_rmse_mps2": float(np.sqrt(np.mean((b4 - body) ** 2))),
      "median_request_error_mps2": float(np.median(b4 - request)),
      "median_wheel_carstate_error_mps2": float(np.median(b4 - body)),
      "host_origin_rows": int((j["origin"][mask] == 1).sum()),
      "max_delivered_vs_native_difference_mps2": float(np.max(abs(request - native[mask, 0]))),
    })
  return result


def braking_events(route: str, j: dict, stock: bool) -> list[dict]:
  request = j["native"][:, 0] if stock else j["applied"][:, 0]
  if stock:
    active = np.isfinite(j["age_native"]) & (j["native"][:, 6] == 1)
  else:
    active = np.isfinite(j["age_applied"]) & (j["cc"][:, 3] == 1)
  mask = active & np.isfinite(j["age_cs"]) & ~j["gas_on"] & ~j["brake_on"] & (request <= -.5) & np.isfinite(j["v"])
  events = []
  for start, end in runs(mask):
    if j["t"][end - 1] - j["t"][start] < 1:
      continue
    req = request[start:end]
    b4 = j["words"][start:end, 2] * .001
    body = j["cs"][start:end, 4]
    events.append({
      "route": route, "mode": "stock" if stock else "openpilot", "segment": int(j["segment"][start]),
      "t_start": float(j["t"][start]), "duration_s": float(j["t"][end - 1] - j["t"][start]),
      "speed_min_mps": float(np.min(j["v"][start:end])), "request_median_mps2": float(np.median(req)),
      "request_min_mps2": float(np.min(req)), "B4_median_mps2": float(np.median(b4)),
      "aEgo_median_mps2": float(np.median(body)), "B4_minus_request_median_mps2": float(np.median(b4 - req)),
      "aEgo_minus_request_median_mps2": float(np.median(body - req)),
    })
  return events


def snapshots(route: str, j: dict, raw: dict, info: dict) -> list[dict]:
  samples = []
  for sample_route, mark, label in SAMPLES:
    if sample_route != route:
      continue
    i = int(np.searchsorted(j["t"], mark, side="right") - 1)
    if i < 0 or mark - j["t"][i] > .075:
      continue
    w = j["words"][i]
    sample = {
      "label": label, "route": route, "t_route": float(j["t"][i]), "segment": int(j["segment"][i]),
      "status_hex": j["bytes"][i].tobytes().hex(),
      "delivered_upper": float(j["applied"][i, 0]), "delivered_lower": float(j["applied"][i, 1]),
      "delivered_ids": j["applied"][i, 2:4].tolist(), "allocation": j["applied"][i, 4:6].tolist(),
      "native_upper": float(j["native"][i, 0]), "confirmed_origin": int(j["origin"][i]),
      "aEgo": float(j["cs"][i, 4]), "speed_mps": float(j["v"][i]),
      "gas_fraction": float(j["gas"][i, 3]), "brake_on": bool(j["brake_on"][i]),
      "longActive": bool(j["cc"][i, 3]), "resultID": int(j["result_id"][i]),
      "requestLoss": bool(j["request_loss"][i]), "b6_high_bits": int(j["result_high_bits"][i]),
      "B26_raw": int(w[13]), "B26_signed13": int(signed13(w[13])),
      "ages_ms": {key: float(j[key][i] * 1000) for key in ("age_applied", "age_native", "age_cs", "age_gas", "age_brake")},
    }
    for offset in (4, 18, 20, 22, 24):
      sample[f"B{offset}"] = float(w[offset // 2] * .001)
    for name, source in (("vehicle_side_request_hex", info["status_source"] + 128),
                         ("native_request_hex", info["native_request_source"])):
      req = raw["req"]
      mask = ((req[:, 2] == 0) & (req[:, 3] == source) & (req[:, 0] <= j["t"][i])
              & (req[:, 0] >= j["t"][i] - .075))
      matches = np.flatnonzero(mask)
      sample[name] = raw["req_bytes"][matches[-1]].tobytes().hex() if len(matches) else None
    samples.append(sample)
  return samples


def transport_report(raw: dict) -> dict:
  req, cc = raw["req"], raw["cc"]
  host = req[:, 2] == 1
  host_t, payloads = req[host, 0], raw["req_bytes"][host]
  upper = payloads[:, 8].astype(np.int32) * 256 + payloads[:, 9]
  upper = np.where(upper >= 32768, upper - 65536, upper) * .001
  valid = np.isfinite(cc[:, 2])
  cc_t, cc_a = cc[valid, 0], cc[valid, 2]
  lows = np.searchsorted(cc_t, host_t - .101, side="right")
  highs = np.searchsorted(cc_t, host_t + 1e-6, side="right")
  lags = []
  for time, value, low, high in zip(host_t, upper, lows, highs):
    match = np.flatnonzero(abs(cc_a[low:high] - value) < .0005)
    if len(match):
      lags.append(float(time - cc_t[low + match[-1]]))
  return {"host_frames": len(host_t), "matched_preceding_cc_frames": len(lags),
          "unresolved_frames": len(host_t) - len(lags),
          "best_match_lag_s_q05_q25_q50_q75_q95": np.quantile(lags, [.05, .25, .5, .75, .95]).tolist() if lags else None,
          "method": "preceding CC window101ms, tolerance0.0005m/s2; logger batching permits1us; not ECU execution latency"}


def source_identity(meta: dict, route: dict, corpus: Path, logs_root: Path | None) -> dict:
  root = logs_root or (Path(meta["logs_root"]) if meta.get("logs_root") else None)
  files = []
  for source in meta["files"]:
    path = Path(source["path"])
    relative = source.get("relative_path")
    if relative is None and root is not None:
      relative = str(path.relative_to(root)) if path.is_absolute() else str(path)
    if relative is None:
      relative = str(Path(*path.parts[-3:]))
    actual = root / relative if root is not None else path
    if actual.exists():
      size, digest = actual.stat().st_size, sha256(actual)
    else:
      size, digest = source["size_bytes"], source["sha256"]
    files.append({"path": relative, "segment": source["segment"], "size_bytes": size, "sha256": digest})
  return {"route": route["route"], "primary": route["primary"], "files": files,
          "origin_ns": meta["origin_ns"], "init": meta.get("init"), "car_params": meta.get("cp"),
          "cache_sha256": {suffix: sha256(corpus / (route["route"] + suffix)) for suffix in (".npz", ".joined.npz")}}


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS)
  parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
  parser.add_argument("--logs-root", type=Path)
  parser.add_argument("--routes", nargs="+")
  args = parser.parse_args()
  args.output_dir.mkdir(parents=True, exist_ok=True)
  manifest = json.loads((args.corpus_dir / "manifest.json").read_text())
  selected = [route for route in manifest["routes"] if not args.routes or route["route"] in args.routes]
  reports, phases, exceptions, epochs, events, samples, identities = [], [], [], [], [], [], []
  transport, brake_model = {}, Counter()
  for route in selected:
    name = route["route"]
    meta = json.loads((args.corpus_dir / (name + ".json")).read_text())
    info = json.loads((args.corpus_dir / (name + ".joined.json")).read_text())
    with np.load(args.corpus_dir / (name + ".joined.npz")) as joined_archive, np.load(args.corpus_dir / (name + ".npz")) as raw_archive:
      j = {key: joined_archive[key] for key in joined_archive.files}
      raw = {key: raw_archive[key] for key in raw_archive.files}
      report, phase, miss = route_report(route, meta, info, j)
      reports.append(report)
      phases.extend(phase)
      exceptions.extend(miss)
      mode = report["openpilotLongitudinalControl"]
      if mode is False:
        epochs.extend(stock_epochs(name, j))
        events.extend(braking_events(name, j, stock=True))
      elif route["primary"] and mode is True:
        transport[name] = transport_report(raw)
        events.extend(braking_events(name, j, stock=False))
      samples.extend(snapshots(name, j, raw, info))
      w = j["words"]
      b4, b18, b24, s13 = w[:, 2], w[:, 9], w[:, 12], signed13(w[:, 13])
      base, alternative = b18 - np.maximum(b4, b24), b18 - np.maximum(b4 - 10 * s13, b24)
      brake_model.update({"rows": len(w), "previously_exact": int((base == 0).sum()),
                          "new_10count_model_within5": int((abs(alternative) <= 5).sum()),
                          "previously_exact_broken_gt5": int(((base == 0) & (abs(alternative) > 5)).sum()),
                          "old_misses_improved_to_within5": int(((abs(base) > 5) & (abs(alternative) <= 5)).sum())})
    identities.append(source_identity(meta, route, args.corpus_dir, args.logs_root))
    print(json.dumps({"route": name, "frames": report["n_status"], "mode_long": mode}), flush=True)

  groups = {}
  selectors = (("primary_drives", lambda r: r["primary"] and r["openpilotLongitudinalControl"] is True),
               ("historical_stock", lambda r: not r["primary"] and r["openpilotLongitudinalControl"] is False),
               ("historical_op", lambda r: not r["primary"] and r["openpilotLongitudinalControl"] is True),
               ("all_status", lambda r: True))
  relation_keys = [key for key, value in reports[0].items() if isinstance(value, dict) and "ok" in value and "n" in value]
  for name, predicate in selectors:
    rows = [row for row in reports if predicate(row)]
    group = {"routes": len(rows), "segments": sum(row["segments"] for row in rows),
             "n_status": sum(row["n_status"] for row in rows), "moving_rows": sum(row["moving_rows"] for row in rows),
             "observed_vmc_seconds": sum(row["observed_vmc_seconds"] for row in rows)}
    for key in relation_keys:
      group[key] = {"n": sum(row[key]["n"] for row in rows), "ok": sum(row[key]["ok"] for row in rows)}
    groups[name] = group
  direct = {"n_epochs": len(epochs),
            "B4_request_RMS_less_than_B4_wheel_CarState_RMS": sum(row["request_rmse_mps2"] < row["wheel_carstate_rmse_mps2"] for row in epochs),
            "median_request_RMS_mps2": float(np.median([row["request_rmse_mps2"] for row in epochs])) if epochs else None,
            "median_wheel_CarState_RMS_mps2": float(np.median([row["wheel_carstate_rmse_mps2"] for row in epochs])) if epochs else None}
  methods = {
    "words": "B4/B18/B20/B22/B24 signed16BE x0.001 nominalm/s2; B26 low13 signed, physical scale unresolved",
    "max_relation": "B18=max(B4,B24), rawcounts; informative excludes B4=B24; empirical, not proved ECU equation",
    "clamped_envelope": "B18=min(max(B4,B24),B22), raw counts; tests whether B22 explains below-max samples",
    "moving": ">0.5m/s from fresh raw wheels with CarState fallback",
    "coverage": "sum adjacent status intervals capped100ms; includes parked time, limits larger-gap contributions to100ms",
    "timing": "preceding-only joins; CS/CC60ms,request75ms,exact-payload origin100ms; logger batch timestamps, not ECU deadlines",
    "stock_epochs": "native latch1,no pedals,moving,freshCS; >=2s; request range>=0.5 or centered-median wheel-gradient range>=0.4 using unique time knots; direct RMS on original2-decimal episode boundaries, no fitted gain/offset",
    "semantics": "candidate roles only; exact synchronized OEM diagnostic/FFD joins absent",
    "segment_times": "t_route from minimum recorded monotonic event; repeated init/carParams timestamps are not segment playback anchors",
  }
  validation = {"methods": methods, "summary": groups, "routes": reports, "phases": phases}
  summary = {
    "schema": "camry-20260930-vmc-status-v1", "vehicle_access": False, "scope": groups, "methods": methods,
    "direct_stock_comparison": direct, "simple_driver_brake_correction_scale10": dict(brake_model),
    "b18_exceptions": {"above": sum(row["residual_counts"] > 0 for row in exceptions),
                       "below": sum(row["residual_counts"] < 0 for row in exceptions)},
    "b6_bit7": {key: sum(row["b6_bit7"][key] for row in reports) for key in reports[0]["b6_bit7"]},
    "transport": transport,
    "stock_braking_events": sum(row["mode"] == "stock" for row in events),
    "primary_op_braking_events": sum(row["mode"] == "openpilot" for row in events),
    "decode_errors": sum(len(row["decode_errors"]) for row in reports),
    "candidate_roles": {"B4": "effective/total-result acceleration", "B18": "drive-side result/reference",
                        "B20": "closed-accelerator reference", "B22": "upper/open-accelerator envelope",
                        "B24": "driver-accelerator demand/reference", "B26": "brake-linked signed13 quantity; scale unresolved"},
    "limits": ["Candidate roles are not confirmed OEM byte/name joins.",
               "ID11 also appears under native stock control and does not establish comma ownership.",
               "Vehicle-side TX confirmations establish publication, not execution or acceptance latency.",
               "Driver-brake onset confounds the subsequent native -4m/s2 request; it is not native-only braking proof.",
               "B4 is neither unconditional request echo nor literal stationary body acceleration.",
               "B18 envelope exceptions prohibit treating the dominant identity as universal.",
               "Cause of route86 request-to-B4 discrepancy and B26 physical scale remain unresolved."],
    "report": "docs/variants/camry-2026-longitudinal-evidence.md#2026-09-30-vmc-status-corpus",
  }
  provenance = {"schema": "camry-20260930-vmc-inputs-v1", "routes": identities,
                "excluded_paths": [{"path": str(Path(row["path"]).relative_to(args.logs_root)) if args.logs_root else row["path"],
                                    "reason": row["reason"]} for row in manifest.get("excluded_paths", [])],
                "boundary": "External rlog identities plus derived extraction/join cache hashes; large raw logs and caches are not committed."}
  for filename, value in (("summary.json", summary), ("corpus_validation.json", validation),
                          ("representative_samples.json", samples), ("braking_events.json", events),
                          ("input_manifest.json", provenance)):
    save_json(args.output_dir / filename, value)
  save_csv(args.output_dir / "phase_comparison.csv", phases)
  save_csv(args.output_dir / "stock_epochs.csv", epochs)
  save_csv(args.output_dir / "b18_exceptions.csv", exceptions)
  print(json.dumps({"output": str(args.output_dir), "scope": groups["all_status"], "stock": direct,
                    "exceptions": summary["b18_exceptions"]}), flush=True)


if __name__ == "__main__":
  main()
