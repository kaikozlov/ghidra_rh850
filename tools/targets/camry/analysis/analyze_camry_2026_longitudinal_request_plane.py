#!/usr/bin/env python3
"""Recover the Camry TSS3 0x08A request / 0x081 result layout.

Offline analysis.
"""
from __future__ import annotations
from tools.toyota_support.toyota_route_opendbc_common import be_raw, toyota_checksum

from tools.targets.camry.support import camry_f33_corpus as f33
from tools import REPO_ROOT
import argparse
import bisect
import gzip
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path

REPO = REPO_ROOT
RAW = f33.CAPTURE / "raw-20260827"
DEFAULT_OUT = REPO / "data/generated/camry_2026_longitudinal_request_plane.json"
GTS = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"
HOLD = REPO / "data/generated/camry_20260906_hands_off_warning_audit.json"
LATERAL_CENSUS = REPO / "data/generated/camry_2026_upstream_request_field_census.json"
OWNERSHIP = REPO / "data/generated/gtsplus_2026/tss3_control_ownership_surface.json"
COROLLA_SPAN = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"
DDB_ROOT = REPO / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics/GTSPlus/NA/DB/Gen"
DRIVES = {
  "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
  "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}
ANGLE_RAD_PER_COUNT = math.radians(1024 / 17870)
MAX_PAIR_NS = 60_000_000


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
      h.update(chunk)
  return h.hexdigest()


def s16be(data: bytes, offset: int) -> int:
  return int.from_bytes(data[offset:offset + 2], "big", signed=True)


def decode_wheel_speed_mps(data: bytes) -> float:
  values_kph = [be_raw(data, start, 15) * 0.01 - 67.67 for start in (6, 22, 38, 54)]
  return statistics.fmean(values_kph) / 3.6


def pearson(xs: list[float], ys: list[float]) -> float | None:
  if len(xs) < 2:
    return None
  mx, my = statistics.fmean(xs), statistics.fmean(ys)
  sx = sum((x - mx) ** 2 for x in xs)
  sy = sum((y - my) ** 2 for y in ys)
  if sx == 0 or sy == 0:
    return None
  return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sx * sy)


def regression(xs: list[float], ys: list[float]) -> dict:
  r = pearson(xs, ys)
  mx, my = statistics.fmean(xs), statistics.fmean(ys)
  denom = sum((x - mx) ** 2 for x in xs)
  slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom if denom else 0.0
  diffs = [y - x for x, y in zip(xs, ys)]
  return {
    "sample_count": len(xs),
    "pearson_r": None if r is None else round(r, 9),
    "slope": round(slope, 9),
    "intercept": round(my - slope * mx, 9),
    "median_delta": round(statistics.median(diffs), 9),
    "median_abs_delta": round(statistics.median(abs(v) for v in diffs), 9),
  }


def quantile(values: list[float], q: float) -> float:
  values = sorted(values)
  if not values:
    raise ValueError("empty quantile")
  return values[min(len(values) - 1, max(0, int(q * (len(values) - 1))))]


def load(path: Path) -> dict[int, list[tuple[int, bytes]]]:
  streams = {0x08A: [], 0x081: [], 0x0CA: [], 0x0AA: [], 0x101: [], 0x116: [], 0x127: []}
  with gzip.open(path, "rt") as f:
    for line in f:
      _seg, nanos, bus, address, payload = json.loads(line)
      data = bytes.fromhex(payload)
      if address == 0x08A and bus == 2 and len(data) == 32:
        streams[0x08A].append((int(nanos), data))
      elif address == 0x081 and bus == 0 and len(data) == 32:
        streams[0x081].append((int(nanos), data))
      elif address == 0x0CA and bus == 0 and len(data) == 32:
        streams[0x0CA].append((int(nanos), data))
      elif address in (0x0AA, 0x101, 0x116, 0x127) and bus == 2 and len(data) == 8:
        streams[address].append((int(nanos), data))
  return streams


def preceding_pairs(request: list[tuple[int, bytes]], result: list[tuple[int, bytes]]) -> list[tuple[bytes, bytes, int]]:
  ts = [t for t, _ in request]
  pairs = []
  for t, result_data in result:
    i = bisect.bisect_right(ts, t) - 1
    if i >= 0 and t - ts[i] <= MAX_PAIR_NS:
      pairs.append((request[i][1], result_data, t - ts[i]))
  return pairs


def nearest_pairs(a: list[tuple[int, bytes]], b: list[tuple[int, bytes]]) -> list[tuple[bytes, bytes, int]]:
  ts = [t for t, _ in b]
  pairs = []
  for t, ad in a:
    i = bisect.bisect_left(ts, t)
    choices = [j for j in (i - 1, i) if 0 <= j < len(ts)]
    if not choices:
      continue
    j = min(choices, key=lambda k: abs(ts[k] - t))
    age = ts[j] - t
    if abs(age) <= MAX_PAIR_NS:
      pairs.append((ad, b[j][1], age))
  return pairs


def preceding_value(rows: list[tuple[int, bytes]], t: int, decoder, max_age_ns: int = 100_000_000):
  ts = [x[0] for x in rows]
  i = bisect.bisect_right(ts, t) - 1
  if i < 0 or t - ts[i] > max_age_ns:
    return None
  return decoder(rows[i][1])


def b6_zero_context(streams: dict[int, list[tuple[int, bytes]]]) -> dict:
  request = streams[0x08A]
  result = streams[0x081]
  result_ts = [t for t, _ in result]
  state_ts = {addr: [t for t, _ in streams[addr]] for addr in (0x0AA, 0x101, 0x116, 0x127)}

  def state_value(addr: int, t: int, decoder, max_age_ns: int = 100_000_000):
    rows = streams[addr]
    ts = state_ts[addr]
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > max_age_ns:
      return None
    return decoder(rows[i][1])

  def b6_state(data: bytes) -> int:
    return data[6]

  stable_result_ids = Counter()
  stable_moving_result_ids = Counter()
  stable_pairs = 0
  stable_moving_pairs = 0
  stable_transition_mismatches = []

  contextual = []
  for i, (t, data) in enumerate(request):
    if b6_state(data) != 0:
      continue
    lo, hi = max(0, i - 4), min(len(request), i + 5)
    stable = hi - lo >= 5 and all(b6_state(d) == 0 for _, d in request[lo:hi])
    if not stable:
      continue

    j = bisect.bisect_left(result_ts, t)
    choices = [k for k in (j - 1, j) if 0 <= k < len(result)]
    if choices:
      k = min(choices, key=lambda x: abs(result_ts[x] - t))
      if abs(result_ts[k] - t) <= MAX_PAIR_NS:
        rid = result[k][1][6] & 0x3F
        stable_result_ids[rid] += 1
        stable_pairs += 1
        speed = state_value(0x0AA, t, decode_wheel_speed_mps)
        if speed is not None and speed > 1.0:
          stable_moving_result_ids[rid] += 1
          stable_moving_pairs += 1
        if rid != 63 and len(stable_transition_mismatches) < 16:
          stable_transition_mismatches.append({"request_time_ns": t, "result_id": rid})

    brake = state_value(0x101, t, lambda d: bool(be_raw(d, 3, 1)))
    gas = state_value(0x116, t, lambda d: be_raw(d, 15, 8) * 0.005)
    speed = state_value(0x0AA, t, decode_wheel_speed_mps)
    gear = state_value(0x127, t, lambda d: be_raw(d, 47, 4))
    if None not in (brake, gas, speed, gear):
      contextual.append({
        "t": t, "brake": bool(brake), "gas": float(gas), "speed": float(speed), "gear": int(gear),
        "lower": s16be(data, 11) * 0.001,
      })

  # Match brake-on edges against the same raw B6=0 state before and after.
  # Raw gear 3 is D on the retained Camry road captures. Limit the primary test to
  # <1 m/s, where Toyota's creep-related behavior should be most discriminating.
  brake_edges = []
  last_brake = None
  for t, data in streams[0x101]:
    brake = bool(be_raw(data, 3, 1))
    if last_brake is False and brake is True:
      gas = state_value(0x116, t, lambda d: be_raw(d, 15, 8) * 0.005)
      speed = state_value(0x0AA, t, decode_wheel_speed_mps)
      gear = state_value(0x127, t, lambda d: be_raw(d, 47, 4))
      if gas == 0.0 and gear == 3 and speed is not None and speed < 1.0:
        pre = [r["lower"] for r in contextual if t - 400_000_000 <= r["t"] <= t - 100_000_000 and r["gas"] == 0.0 and r["gear"] == 3]
        post = [r["lower"] for r in contextual if t + 100_000_000 <= r["t"] <= t + 400_000_000 and r["gas"] == 0.0 and r["gear"] == 3]
        if len(pre) >= 3 and len(post) >= 3:
          pre_median = statistics.median(pre)
          post_median = statistics.median(post)
          brake_edges.append({
            "time_ns": t,
            "speed_mps": round(float(speed), 6),
            "pre_lower_median_mps2": round(pre_median, 6),
            "post_lower_median_mps2": round(post_median, 6),
            "delta_mps2": round(post_median - pre_median, 6),
          })
    last_brake = brake

  # Speed-stratified descriptive check for the no-accelerator, D, B6=0 state.
  bins = [(0.0, 0.15), (0.15, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 5.0), (5.0, 10.0), (10.0, 20.0)]
  speed_bins = []
  for low, high in bins:
    row = {"speed_mps": [low, high]}
    for brake in (False, True):
      values = [r["lower"] for r in contextual if r["gas"] == 0.0 and r["gear"] == 3 and r["brake"] == brake and low <= r["speed"] < high]
      if values:
        row["brake_on" if brake else "brake_off"] = {
          "frames": len(values),
          "median_mps2": round(statistics.median(values), 6),
          "p10_mps2": round(quantile(values, 0.1), 6),
          "p90_mps2": round(quantile(values, 0.9), 6),
        }
    speed_bins.append(row)

  deltas = [row["delta_mps2"] for row in brake_edges]
  return {
    "request_state": "FRC-origin 0x08A raw B6=0 (request ID0 / allocation0); B7 is not a selector",
    "result_state": {
      "stable_pair_count": stable_pairs,
      "result_id_counts": {str(k): v for k, v in sorted(stable_result_ids.items())},
      "moving_over_1_mps_pair_count": stable_moving_pairs,
      "moving_over_1_mps_result_id_counts": {str(k): v for k, v in sorted(stable_moving_result_ids.items())},
      "interpretation": "Observed result B6[5:0] distribution during stable request B6=0. This is not a diagnostic identity join.",
      "non63_examples": stable_transition_mismatches,
    },
    "slot_B11_B12_brake_context": {
      "matched_brake_press_edges_under_1_mps": len(brake_edges),
      "negative_delta_edges": sum(row["delta_mps2"] < 0 for row in brake_edges),
      "positive_delta_edges": sum(row["delta_mps2"] > 0 for row in brake_edges),
      "median_delta_mps2": round(statistics.median(deltas), 6) if deltas else None,
      "mean_delta_mps2": round(statistics.fmean(deltas), 6) if deltas else None,
      "edges": brake_edges,
      "speed_bins_gas_off_drive": speed_bins,
      "boundary": "Observed acceleration-slot behavior during raw B6=0. Brake correlation does not identify a lower-slot requester or an OEM creep application.",
    },
  }


def hist(rows: list[bytes], offset: int) -> dict[str, int]:
  return {f"0x{k:02X}": v for k, v in sorted(Counter(d[offset] for d in rows).items())}


def request_summary(rows: list[tuple[int, bytes]]) -> dict:
  data = [d for _, d in rows]
  a = [s16be(d, 8) for d in data]
  b = [s16be(d, 11) for d in data]
  id_a = [d[6] >> 2 for d in data]
  alloc_a = [d[6] & 0x03 for d in data]
  checksum_expected = [toyota_checksum(0x8A, d[:8]) for d in data]
  return {
    "frame_count": len(data),
    "b6_request_state": {
      "wire": "B6[7:2] request ID + B6[1:0] allocation method (current interpretation)",
      "request_id_counts": {str(k): v for k, v in sorted(Counter(id_a).items())},
      "allocation_method_counts": {str(k): v for k, v in sorted(Counter(alloc_a).items())},
      "boundary": "B6 interpretation is retained; diagnostic/recorder geometry alone is not a CAN mapping.",
    },
    "byte7_checksum": {
      "wire": "B7",
      "formula": "(0x8A + 8 + sum(B0..B6)) & 0xFF",
      "checked_frames": len(data),
      "matching_frames": sum(d[7] == expected for d, expected in zip(data, checksum_expected)),
      "mismatch_frames": sum(d[7] != expected for d, expected in zip(data, checksum_expected)),
      "observed_counts": hist(data, 7),
      "expected_counts": {f"0x{k:02X}": v for k, v in sorted(Counter(checksum_expected).items())},
      "boundary": "Checksum over the first seven payload bytes and legacy eight-byte length; not a lower request ID or allocation field.",
    },
    "longitudinal_acceleration_words": {
      "B8_B9": {"signed16_raw_range": [min(a), max(a)], "scale_mps2_per_count": 0.001},
      "B11_B12": {"signed16_raw_range": [min(b), max(b)], "scale_mps2_per_count": 0.001},
      "equal_frames": sum(x == y for x, y in zip(a, b)),
      "equal_fraction": round(sum(x == y for x, y in zip(a, b)) / len(a), 9),
      "upper_lower_assignment": "The retained complete drives are equal-only and cannot independently order the slots. Unequal ordinary-DRCC observations elsewhere retain the current upper B8:B9 / lower B11:B12 interpretation; no lower requester ID is identified.",
    },
    "lateral_request": {
      "target_lateral_id_low6_values": sorted({d[21] & 0x3F for d in data}),
      "pinion_raw_range": [min(s16be(d, 18) for d in data), max(s16be(d, 18) for d in data)],
      "pinion_scale_rad_per_count": round(ANGLE_RAD_PER_COUNT, 12),
      "recorder_scale_comparison": {
        "pcs_5282_rad_per_count": 0.001,
        "relative_error": round((ANGLE_RAD_PER_COUNT / 0.001) - 1, 9),
      },
      "assist_gain_B24_values": sorted({d[24] for d in data}),
      "damping_gain_B25_values": sorted({d[25] for d in data}),
    },
    "longitudinal_metadata_census": {
      "B4": hist(data, 4),
      "B6": hist(data, 6),
      "B7": hist(data, 7),
      "B20": hist(data, 20),
      "B22": hist(data, 22),
      "B23": hist(data, 23),
      "B24": hist(data, 24),
      "B25": hist(data, 25),
      "boundary": ("B6 retains the current six-bit request ID / two-bit allocation interpretation; B7 is the Toyota checksum. "
                   "Shift, EPB, override-prohibition and priority fields remain unassigned. B20/B22 mirror cruise state. Do not OEM-name unresolved bytes from resemblance."),
    },
  }


def result_summary(request_rows: list[tuple[int, bytes]], result_rows: list[tuple[int, bytes]]) -> dict:
  pairs = preceding_pairs(request_rows, result_rows)
  req_acc = [s16be(q, 8) * 0.001 for q, _, _ in pairs]
  res_acc = [s16be(r, 20) * 0.001 for _, r, _ in pairs]
  ages = [age / 1e6 for _, _, age in pairs]
  id_groups: dict[int, list[tuple[float, float]]] = {}
  for q, r, _ in pairs:
    rid = r[6] & 0x3F
    id_groups.setdefault(rid, []).append((s16be(q, 8) * 0.001, s16be(r, 20) * 0.001))
  conditional = {}
  for rid, values in sorted(id_groups.items()):
    diffs = [res - req for req, res in values]
    conditional[str(rid)] = {
      "sample_count": len(values),
      "request_median_mps2": round(statistics.median(req for req, _ in values), 6),
      "result_median_mps2": round(statistics.median(res for _, res in values), 6),
      "result_minus_request": {
        "median_mps2": round(statistics.median(diffs), 6),
        "p10_mps2": round(quantile(diffs, 0.1), 6),
        "p90_mps2": round(quantile(diffs, 0.9), 6),
      },
    }

  lat_id_matches = sum((q[21] & 0x3F) == (r[13] & 0x3F) for q, r, _ in pairs)
  angle_deltas = [s16be(r, 16) - s16be(q, 18) for q, r, _ in pairs]
  selected_equals_a = sum((r[6] & 0x3F) == (q[6] >> 2) for q, r, _ in pairs)
  selected_63_not_b6 = sum((r[6] & 0x3F) == 63 and (q[6] >> 2) != 63 for q, r, _ in pairs)
  selected_11 = [(q, r) for q, r, _ in pairs if (r[6] & 0x3F) == 11]
  selected_11_equals_a = sum((q[6] >> 2) == 11 for q, _ in selected_11)
  return {
    "frame_count": len(result_rows),
    "paired_to_preceding_0x08A": len(pairs),
    "rlog_publication_age_ms": {
      "median": round(statistics.median(ages), 6),
      "p90": round(quantile(ages, 0.9), 6),
      "boundary": "rlog batch/publication timing",
    },
    "longitudinal_result_id_candidate": {
      "wire": "B6[5:0]",
      "value_counts": {str(k): v for k, v in sorted(Counter(r[6] & 0x3F for _, r, _ in pairs).items())},
      "high_bit_separate": {str(k): v for k, v in sorted(Counter((r[6] >> 7) & 1 for _, r, _ in pairs).items())},
      "candidate_for": "PCS 5284 Arbitration result_longitudinal ID",
      "grade": "strong candidate; no synchronized DID/FFD value capture",
      "relation_to_b6_request_id": {
        "selected_equals_B6_frames": selected_equals_a,
        "selected_63_absent_from_B6_frames": selected_63_not_b6,
        "selected_ID11_frames": len(selected_11),
        "selected_ID11_equals_B6_frames": selected_11_equals_a,
        "interpretation": ("Result ID11 overwhelmingly equals request B6[7:2]; result ID63 is absent from the B6 request-ID field. "
                           "No comparison with B7 is meaningful because B7 is a checksum. Numeric agreement does not establish an OEM diagnostic identity."),
      },
    },
    "longitudinal_reference_word_B20": {
      "wire": "B20:B21 signed16 big-endian",
      "scale_mps2_per_count": 0.001,
      "observation": "request-tracking acceleration-scale word on the Brake-owned result frame; not an OEM-joined diagnostic value",
      "request_vs_reference": regression(req_acc, res_acc),
      "conditional_by_result_id": conditional,
      "selection_discriminator": ("Result ID 63 tracks the request nearly exactly while result ID 11 materially diverges in the retained drives; "
                                  "this establishes result-selection behavior."),
      "retired_oem_join": {
        "former_mapping": "PCS 57DB Arbitration result Acceleration (formerly graded a strong candidate here)",
        "status": "withdrawn",
        "basis": ("The 2026-09-30 native status corpus shows B20:B21 equals B24:B25 on 1005245/1010206 closed-pedal frames. "
                  "B18:B19 has a drive-side envelope relationship, while B4:B5 is the effective/result candidate. "
                  "This retires the selected-total-acceleration interpretation of B20; exact OEM diagnostic byte/name joins remain unresolved."),
        "cross_state_artifact": "data/generated/camry_20260930_vmc_status/summary.json",
        "docs_anchor": "docs/variants/camry-2026-longitudinal-evidence.md#2026-09-30-vmc-status-corpus",
      },
    },
    "lateral_result": {
      "result_id_wire": "B13[5:0]",
      "latest_request_id_match_frames": lat_id_matches,
      "latest_request_id_match_fraction": round(lat_id_matches / len(pairs), 9),
      "result_angle_wire": "B16:B17 signed16 big-endian",
      "result_angle_scale_rad_per_count": round(ANGLE_RAD_PER_COUNT, 12),
      "angle_raw_delta_median": round(statistics.median(angle_deltas), 6),
      "angle_raw_delta_p90_abs": round(quantile([abs(v) for v in angle_deltas], 0.9), 6),
      "recorder_join": "5285 Arbitration result_lateral ID / 57DE Arbitration result Pinion angle",
    },
    "supervision": {
      "request_loss_wire": "B11[4]",
      "grade": "live FRC-suppression join proves request-loss response, but it is not OEM-joined to 57D3",
      "acceleration_valid_57D3": "unresolved",
    },
  }


def old_0ca_boundary(result_rows: list[tuple[int, bytes]], ca_rows: list[tuple[int, bytes]]) -> dict:
  pairs = nearest_pairs(result_rows, ca_rows)
  result = [s16be(a, 20) * 0.001 for a, _, _ in pairs]
  words = {}
  for offset in (3, 5, 7):
    candidate = [s16be(b, offset) * 0.001 for _, b, _ in pairs]
    words[f"B{offset}_B{offset + 1}"] = regression(result, candidate)
  return {
    "pair_count": len(pairs),
    "0x081_B20_reference_vs_0x0CA_words": words,
    "conclusion": ("0x0CA remains protected longitudinal/chassis state, but none of its old B3:B4/B5:B6/B7:B8 candidates reproduces "
                   "the Brake-owned 0x081 B20:B21 reference word. Supersede the old 0x0CA upper/lower/result triplet interpretation."),
  }


def hold_semantics() -> dict:
  report = json.loads(HOLD.read_text())
  totals = Counter()
  episode_pairs = Counter()
  episode_frames = 0
  for route in ("3b", "3c"):
    state = report["routes"][route]["stock_acc_standstill_candidate"]
    for key, count in state["raw_b6_b7_pair_counts"].items():
      totals[key] += count
    episode_frames += int(state["frames"])
    for episode in state["episodes"]:
      for key, count in episode["raw_b6_b7_pair_counts"].items():
        episode_pairs[key] += count
  def raw_pair(key: str) -> dict:
    b6, b7 = (int(v) for v in key.split(","))
    return {"raw_B6": f"0x{b6:02X}", "raw_B7_checksum": f"0x{b7:02X}",
            "B6_request_id": b6 >> 2, "B6_allocation": b6 & 3}
  return {
    "source": {"path": str(HOLD.relative_to(REPO)), "sha256": sha256(HOLD)},
    "route_3b_3c_pair_counts": {key: totals[key] for key in sorted(totals)},
    "hold_episode_pair_counts": {key: episode_pairs[key] for key in sorted(episode_pairs)},
    "hold_episode_frames": episode_frames,
    "structural_hold_state": {
      "wire": "0x08A B4[5]",
      "set_frames_with_cruise_latch": sum(report["routes"][route]["stock_acc_standstill_candidate"]["b4_bit5_set_frames_with_cruise_latch"] for route in ("3b", "3c")),
      "grade": "exact structural delayed-hold state on complete 3b/3c routes; OEM recorder name unresolved",
    },
    "raw_header_pairs": {key: raw_pair(key) for key in sorted(totals)},
    "interpretation": ("Delayed hold is measured by B4[5] with the cruise latch set. Raw B6/B7 pairs are retained observations, "
                       "not two request-ID/allocation slots: B7 is the checksum. B6 allocation changes with accelerator override; "
                       "B7 changes also reflect header flags, so its former ID17/ID25 distinction has no application-ID meaning. "
                       "The exact OEM recorder identity of B4[5] remains unknown."),
  }


def recorder_rows() -> dict:
  managed = json.loads(GTS.read_text())
  rows = managed["operation_ffd"]["detail_rows"]
  wanted = {"5252", "5253", "525D", "525E", "5261", "526A", "5280", "5281", "5282", "5284", "5285", "57D3", "57DB", "57DE"}
  out = {did: [] for did in sorted(wanted)}
  for row in rows:
    did = str(row.get("DataID", "")).upper()
    if did in wanted:
      out[did].append({k: row[k] for k in ("DataName", "BytePosition", "BitPosition", "BitLength", "Type", "Lsb", "Offset", "Point")})
  return out


def requester_id_namespace(drive_reports: dict[str, dict]) -> dict:
  """Keep diagnostic dictionaries distinct from observed CAN B6 state."""
  lateral = json.loads(LATERAL_CENSUS.read_text())
  lateral_ids = lateral["gtsplus_join"]["emps_p5_did_0x1cee"]["target_lateral_id_dictionary"]
  ownership = json.loads(OWNERSHIP.read_text())
  isa_rows = ownership["longitudinal_request_surface"]["frc_output_vocabulary"]["dids"]["0x1B03"]

  from tools.techstream.ddb_semantics import monitor_rows
  from tools.techstream.ddb_strings import load_string_db
  from tools.techstream.parse_ddb import DDBParser

  parser = DDBParser()
  strings = load_string_db(parser, DDB_ROOT / "M_English.ddb")
  requested_names = {
    "Speed Limiter Requesting Vertical ID (Upper Limit)",
    "MaaS Longitudinal Request ID of Lower Limit From IFU",
    "PDA-SA Lateral Control Request ID",
  }
  sparse_cross_generation = {}
  database = "ADCU_P6.ddb"
  db = parser.parse_ecu_db(DDB_ROOT / database)
  for row in monitor_rows(db, strings, database, deduplicate=True, include_signal_info=True):
    if row["name"] not in requested_names:
      continue
    patterns = (row.get("signal_info") or {}).get("pattern_display") or {}
    sparse_cross_generation[row["name"]] = {
      "patterns": {str(k): v for k, v in sorted(patterns.items())},
      "primary_did": f"0x{row['primary_did']:04X}",
      "alternate_did": f"0x{row['alternate_did']:04X}",
      "database": database,
    }

  observed_b6 = Counter()
  observed_result = Counter()
  for drive in drive_reports.values():
    req = drive["request_0x08A"]["b6_request_state"]
    observed_b6.update({int(k): v for k, v in req["request_id_counts"].items()})
    observed_result.update({int(k): v for k, v in drive["result_0x081"]["longitudinal_result_id_candidate"]["value_counts"].items()})
  corolla = json.loads(COROLLA_SPAN.read_text())
  corolla_request = corolla["direct_reuse_evidence"]["0x08A_acc"]["request_id_allocation"]
  pcs = json.loads(GTS.read_text())
  feature_id_fields = [{
    "data_id": row["DataID"], "name": row["DataName"],
    "bit_length": row["BitLength"], "byte_position": row["BytePosition"],
  } for row in pcs["operation_ffd"]["detail_rows"]
     if row.get("DataID") in {"5271", "5280", "5281", "5284", "5A04", "5B07"}
     and "ID" in row.get("DataName", "")]

  return {
    "source_files": {
      "lateral_dictionary": {"path": str(LATERAL_CENSUS.relative_to(REPO)), "sha256": sha256(LATERAL_CENSUS)},
      "adcu_p6_ddb": {"path": str((DDB_ROOT / database).relative_to(REPO)), "sha256": sha256(DDB_ROOT / database)},
      "english_strings_ddb": {"path": str((DDB_ROOT / "M_English.ddb").relative_to(REPO)), "sha256": sha256(DDB_ROOT / "M_English.ddb")},
      "control_ownership": {"path": str(OWNERSHIP.relative_to(REPO)), "sha256": sha256(OWNERSHIP)},
      "corolla_span": {"path": str(COROLLA_SPAN.relative_to(REPO)), "sha256": sha256(COROLLA_SPAN)},
    },
    "camry_observed": {
      "B6_request_id_counts": {str(k): v for k, v in sorted(observed_b6.items())},
      "result_id_counts": {str(k): v for k, v in sorted(observed_result.items())},
    },
    "corolla_cross_platform": {
      "B6_request_id_counts": corolla_request["candidate_A_id_counts"],
      "B6_allocation_counts": corolla_request["candidate_A_allocation_counts"],
      "result_id_counts": corolla_request["result_id_counts"],
      "boundary": "Independent raw-state observation; numeric reuse does not identify a shared OEM application.",
    },
    "diagnostic_dictionaries": {
      "p5_frc_isa_vertical_id_patterns": isa_rows[0]["patterns"],
      "cross_generation_examples": sparse_cross_generation,
      "lateral_target_id_dictionary": lateral_ids,
    },
    "feature_specific_recorder_id_fields_without_enum": feature_id_fields,
    "boundary": ("Diagnostic/recorder and CAN namespaces are distinct. Numeric coincidences across axes or platforms do not establish application identity. "
                 "B6 is the only currently interpreted request-ID/allocation byte here; the lower-slot requester ID and allocation remain unknown. "
                 "Former B7-derived ID4/17/25/36 observations and associated baseline/hold/startup application attributions are withdrawn."),
  }


def vehicle_motion_control_did_surface() -> dict:
  """Extract the Brake diagnostic request -> Vehicle Motion Control target split."""
  from tools.techstream.ddb_semantics import monitor_rows
  from tools.techstream.ddb_strings import load_string_db
  from tools.techstream.parse_ddb import DDBParser

  parser = DDBParser()
  strings = load_string_db(parser, DDB_ROOT / "M_English.ddb")
  db = parser.parse_ecu_db(DDB_ROOT / "ABS_P5.ddb")
  wanted = set(range(0x10A1, 0x10AB))
  out = {}
  for row in monitor_rows(db, strings, "ABS_P5.ddb", deduplicate=True, include_signal_info=True):
    did = int(row["primary_did"])
    if did not in wanted:
      continue
    info = row.get("signal_info") or {}
    out[f"0x{did:04X}"] = {
      "name": row["name"],
      "bit_width": info.get("bit_width"),
      "signed": info.get("signed"),
      "unit": info.get("unit"),
      "mul": info.get("mul"),
      "decimal_point_count": info.get("decimal_point_count"),
    }
  return out


def layout_disposition() -> dict:
  return {
    "5280_lower_longitudinal_request": {
      "request_id": {"status": "unresolved; B7 is checksum", "wire": None},
      "acceleration": {"status": "strongly resolved for ordinary Camry DRCC", "wire": "0x08A B11:B12", "scale_mps2_per_count": 0.001},
      "force_distribution": {"status": "unresolved; B7 is checksum", "wire": None},
      "shift_range": {"status": "unresolved", "wire": None},
      "epb_request": {"status": "unresolved", "wire": None},
      "accelerator_override_prohibition": {"status": "unresolved", "wire": None},
      "low_priority": {"status": "unresolved", "wire": None},
    },
    "5281_upper_longitudinal_request": {
      "request_id": {"status": "current B6 interpretation; exact recorder join unresolved", "wire": "0x08A B6[7:2]"},
      "acceleration": {"status": "strongly resolved for ordinary Camry DRCC", "wire": "0x08A B8:B9", "scale_mps2_per_count": 0.001},
      "force_distribution": {"status": "current B6 interpretation; exact recorder join unresolved", "wire": "0x08A B6[1:0]"},
    },
    "5282_lateral_request": {
      "lateral_id": {"status": "recovered", "wire": "0x08A B21[5:0]"},
      "pinion_angle": {"status": "recovered", "wire": "0x08A B18:B19 signed16", "scale_rad_per_count": round(ANGLE_RAD_PER_COUNT, 12)},
      "steering_assist_gain": {"status": "strong structural join", "wire": "0x08A B24", "scale_per_count": 0.01},
      "damping_gain": {"status": "bounded structural join; zero in both complete drives", "wire": "0x08A B25", "scale_per_count": 0.01},
    },
    "5284_longitudinal_result_id": {"status": "strong candidate", "wire": "0x081 B6[5:0]"},
    "5285_lateral_result_id": {"status": "recovered", "wire": "0x081 B13[5:0]"},
    "57D3_acceleration_valid": {"status": "unresolved", "wire": None, "note": "0x081 B11[4] is request-loss supervision"},
    "57DB_result_acceleration": {"status": "unmapped", "wire": None,
                                 "note": ("the former 0x081 B20:B21 join is disproved by the 2026-09-30 cross-state corpus: B20:B21 is the "
                                          "closed-accelerator reference word, B4:B5 the effective/result candidate and B18:B19 the drive "
                                          "result/reference")},
    "57DE_result_pinion_angle": {"status": "recovered", "wire": "0x081 B16:B17 signed16", "scale_rad_per_count": round(ANGLE_RAD_PER_COUNT, 12)},
  }


def build() -> dict:
  drive_reports = {}
  for label, path in DRIVES.items():
    streams = load(path)
    drive_reports[label] = {
      "source": {"path": str(path.relative_to(REPO)), "sha256": sha256(path)},
      "request_0x08A": request_summary(streams[0x08A]),
      "result_0x081": result_summary(streams[0x08A], streams[0x081]),
      "b6_zero_context": b6_zero_context(streams),
      "0x0CA_supersession_check": old_0ca_boundary(streams[0x081], streams[0x0CA]),
    }
  hold = hold_semantics()
  namespace = requester_id_namespace(drive_reports)
  return {
    "schema": "camry-2026-longitudinal-request-plane-v6",
    "vehicle_access": False,
    "topology": {
      "capture_era": "temporary CAN0/CAN1 repin",
      "0x08A": "native upstream Panda bus2 -> chassis bus0 on Toyota Bus 4",
      "0x081": "native Brake/chassis Panda bus0 -> upstream bus2 on Toyota Bus 4",
      "stock_toyota_b": "Toyota Bus 4 returns to unsplit Panda bus1; compare by Toyota network role across Panda bus-number changes",
    },
    "gts_recorder_schema": {"source": str(GTS.relative_to(REPO)), "sha256": sha256(GTS), "rows": recorder_rows()},
    "gts_vehicle_motion_control_surface": {
      "source": str((DDB_ROOT / "ABS_P5.ddb").relative_to(REPO)),
      "sha256": sha256(DDB_ROOT / "ABS_P5.ddb"),
      "dids": vehicle_motion_control_did_surface(),
      "interpretation": ("0x10A1..0x10A4 are Toyota-Safety-Sense request acceleration/IDs; 0x10A5..0x10AA are Vehicle-Motion-Control target acceleration/IDs/driving force. "
                         "This preserves the request -> post-arbitration request-generation boundary in Toyota diagnostics."),
    },
    "hold_request_semantics": hold,
    "requester_id_namespace": namespace,
    "layout": layout_disposition(),
    "drives": drive_reports,
    "conclusion": {
      "request_plane": ("0x08A is the observed continuous TSS request-side envelope. Signed16 B8:B9/B11:B12 acceleration slots and B6 request-ID/allocation interpretation are retained. "
                        "B7 is the Toyota checksum, not a second request-ID/allocation byte. Recorder geometry does not prove a CAN mapping; exact internal application-selection placement remains unresolved."),
      "result_plane": ("0x081 is the unified Brake-owned employed-result/reference/supervision envelope: its lateral selected ID/reference are recovered, "
                       "B6[5:0] is the strongest 5284 longitudinal employed-source-ID candidate, and B20:B21 is observed as the closed-accelerator "
                       "reference word with its former 57DB result-acceleration join retired by the 2026-09-30 cross-state corpus. In that corpus "
                       "B4:B5 is the effective/result acceleration candidate and B18:B19 the drive result/reference, with no confirmed OEM diagnostic "
                       "join for either. Current status and evidence: docs/variants/camry-2026-longitudinal-evidence.md#2026-09-30-vmc-status-corpus "
                       "and data/generated/camry_20260930_vmc_status/."),
      "not_fully_mapped": ("The 5280/5281 recorder model is not fully byte-mapped. B6 retains the current ID/allocation interpretation, while the lower requester ID/allocation, "
                           "shift/EPB, override-prohibition and priority remain unknown. B7-derived active/hold/override application-ID conclusions are withdrawn."),
      "0x0CA": "Supersede the old upper/lower/result-triplet interpretation; 0x0CA remains other protected longitudinal/chassis state.",
      "integration": ("For Camry, do not revive 0x160 Alpha Long. The OEM-native integration target is the TSS application/request side feeding Toyota's Vehicle Movement Manager. "
                      "0x08A is the strongest observed request-side carrier, while the downstream Vehicle Motion Control target interface and source-suppression/security path remain to be recovered."),
    },
  }


def main() -> None:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()
  report = build()
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
  print(args.output)


if __name__ == "__main__":
  main()
