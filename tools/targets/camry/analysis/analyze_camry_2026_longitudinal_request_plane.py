#!/usr/bin/env python3
"""Recover the Camry TSS3 0x08A request / 0x081 result layout.

Offline analysis only. This intentionally distinguishes a recovered wire field
from an OEM recorder-name join: fields without a synchronized diagnostic/FFD
witness remain bounded or unresolved rather than being named by resemblance.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
RAW = REPO / "targets/camry-2026/raw-20260827"
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
  streams = {0x08A: [], 0x081: [], 0x0CA: []}
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


def hist(rows: list[bytes], offset: int) -> dict[str, int]:
  return {f"0x{k:02X}": v for k, v in sorted(Counter(d[offset] for d in rows).items())}


def request_summary(rows: list[tuple[int, bytes]]) -> dict:
  data = [d for _, d in rows]
  a = [s16be(d, 8) for d in data]
  b = [s16be(d, 11) for d in data]
  id_a = [d[6] >> 2 for d in data]
  alloc_a = [d[6] & 0x03 for d in data]
  id_b = [d[7] >> 2 for d in data]
  alloc_b = [d[7] & 0x03 for d in data]
  return {
    "frame_count": len(data),
    "longitudinal_id_allocation_packing": {
      "candidate_A": {
        "wire": "B6[7:2] request ID + B6[1:0] allocation method",
        "request_id_counts": {str(k): v for k, v in sorted(Counter(id_a).items())},
        "allocation_method_counts": {str(k): v for k, v in sorted(Counter(alloc_a).items())},
      },
      "candidate_B": {
        "wire": "B7[7:2] request ID + B7[1:0] allocation method",
        "request_id_counts": {str(k): v for k, v in sorted(Counter(id_b).items())},
        "allocation_method_counts": {str(k): v for k, v in sorted(Counter(alloc_b).items())},
      },
      "gts_geometry": ("Brake 0x10A3/0x10A4 define each TSS request ID as bits 7:2 (six bits), leaving exactly two low bits. "
                       "FRC allocation-method vocabulary is 0..3. The wire split is therefore a strong structural candidate; "
                       "upper-vs-lower A/B assignment still lacks a synchronized DID/FFD join."),
      "allocation_enum": {"0": "Engine Only", "1": "Engine and Brake 1", "2": "Engine and Brake 2", "3": "Brake Only"},
    },
    "longitudinal_acceleration_words": {
      "B8_B9": {"signed16_raw_range": [min(a), max(a)], "scale_mps2_per_count": 0.001},
      "B11_B12": {"signed16_raw_range": [min(b), max(b)], "scale_mps2_per_count": 0.001},
      "equal_frames": sum(x == y for x, y in zip(a, b)),
      "equal_fraction": round(sum(x == y for x, y in zip(a, b)) / len(a), 9),
      "upper_lower_assignment": "unresolved: both words are equal in every retained complete-drive frame",
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
      "boundary": ("B6/B7 are now structurally split into two six-bit request IDs plus two-bit allocation methods. The complete-drive census "
                   "does not establish upper-vs-lower ordering or assign the remaining shift, EPB, override-prohibition or priority fields. "
                   "B20/B22 mirror cruise state. Do not OEM-name unresolved bytes from resemblance."),
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
  selected_equals_b = sum((r[6] & 0x3F) == (q[7] >> 2) for q, r, _ in pairs)
  selected_63_not_request = sum((r[6] & 0x3F) == 63 and 63 not in (q[6] >> 2, q[7] >> 2) for q, r, _ in pairs)
  selected_11 = [(q, r) for q, r, _ in pairs if (r[6] & 0x3F) == 11]
  selected_11_equals_a = sum((q[6] >> 2) == 11 for q, _ in selected_11)
  return {
    "frame_count": len(result_rows),
    "paired_to_preceding_0x08A": len(pairs),
    "rlog_publication_age_ms": {
      "median": round(statistics.median(ages), 6),
      "p90": round(quantile(ages, 0.9), 6),
      "boundary": "rlog batch/publication timing, not physical wire latency",
    },
    "longitudinal_result_id_candidate": {
      "wire": "B6[5:0]",
      "value_counts": {str(k): v for k, v in sorted(Counter(r[6] & 0x3F for _, r, _ in pairs).items())},
      "high_bit_separate": {str(k): v for k, v in sorted(Counter((r[6] >> 7) & 1 for _, r, _ in pairs).items())},
      "candidate_for": "PCS 5284 Arbitration result_longitudinal ID",
      "grade": "strong candidate; no synchronized DID/FFD value capture",
      "relation_to_request_ids": {
        "selected_equals_candidate_A_frames": selected_equals_a,
        "selected_equals_candidate_B_frames": selected_equals_b,
        "selected_63_absent_from_A_B_frames": selected_63_not_request,
        "selected_ID11_frames": len(selected_11),
        "selected_ID11_equals_candidate_A_frames": selected_11_equals_a,
        "interpretation": ("Selected ID11 overwhelmingly names request candidate A (0x08A B6[7:2]); selected ID63 is absent from both TSS request slots and "
                           "consistent with Toyota's independently named Driver Operation ID63. This supports the packed request-ID interpretation."),
      },
    },
    "longitudinal_result_acceleration_candidate": {
      "wire": "B20:B21 signed16 big-endian",
      "scale_mps2_per_count": 0.001,
      "candidate_for": "PCS 57DB Arbitration result Acceleration",
      "grade": "strong candidate; exact synchronized DID/FFD value capture absent",
      "request_vs_result": regression(req_acc, res_acc),
      "conditional_by_result_id": conditional,
      "arbitration_discriminator": ("Result ID 63 tracks the request nearly exactly while result ID 11 materially diverges in the retained drives; "
                                    "this is result-selection behavior, not a simple request echo."),
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
    "0x081_result_accel_vs_0x0CA_words": words,
    "conclusion": ("0x0CA remains protected longitudinal/chassis state, but none of its old B3:B4/B5:B6/B7:B8 candidates reproduces "
                   "the cleaner Brake-owned 0x081 B20:B21 arbitration-result candidate. Supersede the old 0x0CA upper/lower/result triplet interpretation."),
  }


def hold_semantics() -> dict:
  report = json.loads(HOLD.read_text())
  totals = Counter()
  episode_pairs = Counter()
  episode_frames = 0
  for route in ("3b", "3c"):
    state = report["routes"][route]["stock_acc_standstill_candidate"]
    for key, count in state["cruise_substate_pair_counts"].items():
      totals[key] += count
    episode_frames += int(state["frames"])
    for episode in state["episodes"]:
      for key, count in episode["state_pair_counts"].items():
        episode_pairs[key] += count
  def decode_pair(key: str) -> dict:
    a_raw, b_raw = (int(v) for v in key.split(","))
    return {
      "raw_B6": f"0x{a_raw:02X}", "request_id_A": a_raw >> 2, "allocation_A": a_raw & 3,
      "raw_B7": f"0x{b_raw:02X}", "request_id_B": b_raw >> 2, "allocation_B": b_raw & 3,
    }
  return {
    "source": {"path": str(HOLD.relative_to(REPO)), "sha256": sha256(HOLD)},
    "route_3b_3c_pair_counts": {key: totals[key] for key in sorted(totals)},
    "hold_episode_pair_counts": {key: episode_pairs[key] for key in sorted(episode_pairs)},
    "hold_episode_frames": episode_frames,
    "structural_hold_state": {
      "wire": "0x08A B4[5]",
      "set_frames_with_cruise_latch": sum(report["routes"][route]["stock_acc_standstill_candidate"]["b4_bit5_set_frames_with_cruise_latch"] for route in ("3b", "3c")),
      "xor_violations_vs_retained_delayed_hold": sum(report["routes"][route]["stock_acc_standstill_candidate"]["b4_bit5_vs_legacy_b7_66_67_xor_violations"] for route in ("3b", "3c")),
      "grade": "exact structural delayed-hold state on complete 3b/3c routes; OEM recorder name unresolved",
    },
    "decoded_states": {
      "ordinary_active": decode_pair("45,71"),
      "ordinary_active_accelerator_override": decode_pair("44,70"),
      "delayed_hold": decode_pair("45,103"),
      "delayed_hold_accelerator_override": decode_pair("44,102"),
      "moving_ID25_counterexample": decode_pair("71,101"),
    },
    "interpretation": ("The former composite B7 0x47/0x67 state decomposes into request-B ID17/ID25 with allocation method3. "
                       "Accelerator override changes A allocation 1->0 and B allocation 3->2 while preserving both request IDs. "
                       "Delayed hold is specifically request-B ID25 with allocation2/3, not B7 bit5 alone; a moving raw B7=0x65 "
                       "(ID25/allocation1) is the retained counterexample."),
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


def requester_id_namespace(drive_reports: dict[str, dict], hold: dict) -> dict:
  """Bound Toyota's longitudinal requester-ID namespace without inventing names.

  The observed 0x08A fields are post-application-selection candidates: Toyota's
  generic movement-control architecture names longitudinal IDs as application
  identifiers, but the static P5/P6 diagnostic corpus exposes only sparse enum
  labels.  Cross-axis numeric coincidences are retained as hypotheses, not
  silently copied from the lateral Target Lateral ID dictionary.
  """
  lateral = json.loads(LATERAL_CENSUS.read_text())
  lateral_ids = lateral["gtsplus_join"]["emps_p5_did_0x1cee"]["target_lateral_id_dictionary"]

  ownership = json.loads(OWNERSHIP.read_text())
  isa_rows = ownership["longitudinal_request_surface"]["frc_output_vocabulary"]["dids"]["0x1B03"]
  isa_patterns = isa_rows[0]["patterns"]

  techstream_tools = REPO / "tools/techstream"
  if str(techstream_tools) not in sys.path:
    sys.path.insert(0, str(techstream_tools))
  from ddb_semantics import monitor_rows  # type: ignore[import-not-found]
  from ddb_strings import load_string_db  # type: ignore[import-not-found]
  from parse_ddb import DDBParser  # type: ignore[import-not-found]

  parser = DDBParser()
  strings = load_string_db(parser, DDB_ROOT / "M_English.ddb")
  requested_names = {
    "Speed Limiter Requesting Vertical ID (Upper Limit)",
    "MaaS Longitudinal Request ID of Lower Limit From IFU",
    "PDA-SA Lateral Control Request ID",
  }
  sparse_cross_generation = {}
  for database in ("ADCU_P6.ddb",):
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

  observed_a = Counter()
  observed_b = Counter()
  observed_result = Counter()
  for drive in drive_reports.values():
    req = drive["request_0x08A"]["longitudinal_id_allocation_packing"]
    observed_a.update({int(k): v for k, v in req["candidate_A"]["request_id_counts"].items()})
    observed_b.update({int(k): v for k, v in req["candidate_B"]["request_id_counts"].items()})
    observed_result.update({int(k): v for k, v in drive["result_0x081"]["longitudinal_result_id_candidate"]["value_counts"].items()})

  id25_hold_frames = hold["hold_episode_frames"]
  id36_frames = observed_b[36]

  pcs = json.loads(GTS.read_text())
  feature_id_fields = []
  for row in pcs["operation_ffd"]["detail_rows"]:
    if row.get("DataID") in {"5271", "5280", "5281", "5284", "5A04", "5B07"} and "ID" in row.get("DataName", ""):
      feature_id_fields.append({
        "data_id": row["DataID"], "name": row["DataName"],
        "bit_length": row["BitLength"], "byte_position": row["BytePosition"],
      })

  corolla = json.loads(COROLLA_SPAN.read_text())
  corolla_long = corolla["direct_reuse_evidence"]["0x08A_acc"]["request_id_allocation"]

  return {
    "source_files": {
      "lateral_dictionary": {"path": str(LATERAL_CENSUS.relative_to(REPO)), "sha256": sha256(LATERAL_CENSUS)},
      "adcu_p6_ddb": {"path": str((DDB_ROOT / "ADCU_P6.ddb").relative_to(REPO)), "sha256": sha256(DDB_ROOT / "ADCU_P6.ddb")},
      "english_strings_ddb": {"path": str((DDB_ROOT / "M_English.ddb").relative_to(REPO)), "sha256": sha256(DDB_ROOT / "M_English.ddb")},
      "control_ownership": {"path": str(OWNERSHIP.relative_to(REPO)), "sha256": sha256(OWNERSHIP)},
      "corolla_span": {"path": str(COROLLA_SPAN.relative_to(REPO)), "sha256": sha256(COROLLA_SPAN)},
    },
    "model": {
      "id_is_not_priority": "Request IDs identify FRC-submitted application sources and result IDs identify the source actually employed downstream; the numeric value is not an ordinal priority.",
      "application_id_semantics": ("Toyota's vehicle-movement architecture defines both longitudinal request IDs and the lateral request ID as identifiers of applications. "
                                   "This supports a coordinated/shared application-ID namespace model, while the static diagnostic corpus still does not expose a complete longitudinal value table."),
      "axis_boundary": ("Numeric reuse across axes is now treated as potentially intentional application identity, not an automatic coincidence. "
                        "Axis-local diagnostic labels may still describe different roles/phases of the same application, so equal numbers do not by themselves prove identical display labels."),
      "upper_lower_boundary": ("Candidate A/B are the two selected longitudinal bound-package ID/allocation slots. Archive-wide unequal ordinary-DRCC frames strongly resolve A as upper and B as lower. "
                               "The bounds are independently arbitrated and can therefore carry different application IDs."),
    },
    "camry_observed": {
      "request_candidate_A_counts": {str(k): v for k, v in sorted(observed_a.items())},
      "request_candidate_B_counts": {str(k): v for k, v in sorted(observed_b.items())},
      "result_id_counts": {str(k): v for k, v in sorted(observed_result.items())},
      "id25_delayed_hold_frames": id25_hold_frames,
      "id36_startup_frames": id36_frames,
      "id36_boundary": ("ID36 appears only in drive A request candidate B for 33 frames (~0.79 s at startup), with candidate A ID0, "
                        "zero request acceleration, and result ID63; it is not observed as active cruise authority."),
    },
    "corolla_cross_platform": {
      "request_candidate_A_counts": corolla_long["candidate_A_id_counts"],
      "request_candidate_B_counts": corolla_long["candidate_B_id_counts"],
      "result_id_counts": corolla_long["result_id_counts"],
      "boundary": corolla_long["boundary"],
    },
    "authoritative_sparse_names": {
      "p5_frc_isa_vertical_id": {"patterns": isa_patterns, "meaning": ("P5 FRC ordinary Data Monitor display surface. Its pattern table includes 63=Driver Operation, but that does not establish FRC request origination. "
                                                                                  "On the Camry wire, 63 is absent from both FRC-origin 0x08A request slots and appears on the Brake/VMC-owned 0x081 employed-result field.")},
      "cross_generation_examples": sparse_cross_generation,
      "lateral_target_id_dictionary": lateral_ids,
    },
    "feature_specific_recorder_id_fields_without_enum": feature_id_fields,
    "working_table": {
      "0": {
        "longitudinal": "No Request is OEM-named on P5 ISA vertical ID; observed as Camry candidate A idle.",
        "lateral": lateral_ids.get("0"), "grade": "named anchor / observed",
      },
      "4": {
        "longitudinal": "Observed Camry candidate B idle; no OEM longitudinal feature name recovered.",
        "lateral": lateral_ids.get("4"), "grade": "observed longitudinal; lateral comparison only",
      },
      "9": {
        "longitudinal": "P6 Speed Limiter Requesting Vertical ID explicitly names 9 = ISA; not observed in Camry 0x08A corpus.",
        "lateral": lateral_ids.get("9"), "grade": "OEM cross-generation longitudinal/vertical anchor",
      },
      "11": {
        "longitudinal": ("Observed Camry candidate A during ordinary DRCC and selected result ID11 when the application request is employed. "
                         "No static longitudinal enum row names 11."),
        "lateral": lateral_ids.get("11"),
        "grade": "strong cross-axis shared-application-ID hypothesis; not OEM-named longitudinally",
      },
      "17": {
        "longitudinal": "Observed Camry active candidate B and retained Corolla active candidate A; no OEM longitudinal label recovered.",
        "lateral": lateral_ids.get("17"), "grade": "cross-platform active-request observation",
      },
      "18": {
        "longitudinal": "No Camry longitudinal observation in the complete-drive request slots.",
        "lateral": lateral_ids.get("18"),
        "grade": "OEM lateral/PDA-SA anchor only; do not transfer to longitudinal",
      },
      "23": {
        "longitudinal": "Observed retained Corolla active candidate B; no OEM longitudinal label recovered.",
        "lateral": lateral_ids.get("23"), "grade": "cross-platform observation only",
      },
      "25": {
        "longitudinal": ("Observed Camry candidate B during delayed ACC hold; allocation method distinguishes held vs moving ID25 states. "
                         "Under the application-ID architecture this is an unresolved semantic clue, not evidence that longitudinal/lateral namespaces are unrelated."),
        "lateral": lateral_ids.get("25"),
        "grade": "observed longitudinal application ID; exact shared-application meaning unresolved",
      },
      "36": {
        "longitudinal": "Observed Camry startup-only candidate B; no active authority and no OEM label recovered.",
        "lateral": lateral_ids.get("36"), "grade": "bounded startup state",
      },
      "41": {
        "longitudinal": "P6 MaaS lower-limit longitudinal requester explicitly names 41 = Request 1 of MaaS Autonomous Driving System.",
        "lateral": lateral_ids.get("41"), "grade": "OEM cross-generation shared-application candidate",
      },
      "45": {
        "longitudinal": "P6 MaaS lower-limit longitudinal requester explicitly names 45 = Request 2 of MaaS Autonomous Driving System.",
        "lateral": lateral_ids.get("45"), "grade": "OEM cross-generation shared-application candidate",
      },
      "63": {
        "longitudinal": ("Driver Operation is OEM-named on a P5 FRC diagnostic display surface, but dynamic Camry/Corolla evidence places longitudinal ID63 on the downstream Brake/VMC result side only: "
                         "it is absent from both FRC-origin 0x08A request slots and appears in 0x081 when driver demand is the employed source."),
        "lateral": lateral_ids.get("63"), "grade": "OEM-named driver/result identity; not an observed FRC longitudinal requester",
      },
    },
    "cross_axis_assessment": {
      "supports_shared_application_namespace": [
        "Toyota's architecture explicitly defines both longitudinal and lateral request IDs as application identifiers.",
        "0 is the no-request/manual anchor on both recovered interfaces.",
        "63 is OEM-labeled Driver Operation on a P5 FRC diagnostic display surface and on the lateral Target ID dictionary, but longitudinal dynamic evidence places 63 on the downstream Brake/VMC result side rather than the FRC 0x08A request side.",
        "Camry longitudinal ID11 is the ordinary DRCC application source while lateral ID11 is OEM LTA/LCA, making 11 a strong shared TSS continuous-driving application-ID candidate.",
        "P6 longitudinal IDs 41/45 are MaaS autonomous-driving Request 1/2 while the lateral table labels 41/45 AD(Lv.4)/DES(Lv.4); these may be axis-specific views of shared automated-driving application identities rather than contradictory namespaces.",
      ],
      "unresolved_numeric_labels": [
        "The static corpus does not publish a complete longitudinal 0..63 value table.",
        "Camry longitudinal ID25 is used during delayed ACC hold while lateral ID25 is AP; this needs a feature-local recorder or firmware join before naming, and does not by itself disprove shared application identity.",
      ],
      "current_hypothesis": ("A coordinated/shared application-ID namespace is now the leading model. Longitudinal and lateral labels can describe different control roles of the same application, "
                             "so numeric identity is meaningful but exact longitudinal labels remain evidence-graded. Camry longitudinal ID11 is therefore a strong DRCC/TSS3 application-ID candidate aligned with lateral ID11 LTA/LCA."),
    },
  }


def vehicle_motion_control_did_surface() -> dict:
  """Extract the Brake diagnostic request -> Vehicle Motion Control target split."""
  techstream_tools = REPO / "tools/techstream"
  if str(techstream_tools) not in sys.path:
    sys.path.insert(0, str(techstream_tools))
  from ddb_semantics import monitor_rows  # type: ignore[import-not-found]
  from ddb_strings import load_string_db  # type: ignore[import-not-found]
  from parse_ddb import DDBParser  # type: ignore[import-not-found]

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
      "request_id": {"status": "strong structural candidate; lower-vs-upper assignment unresolved", "wire_candidates": ["0x08A B6[7:2]", "0x08A B7[7:2]"]},
      "acceleration": {"status": "mapped as one of an indistinguishable pair", "wire_candidates": ["0x08A B8:B9", "0x08A B11:B12"], "scale_mps2_per_count": 0.001},
      "force_distribution": {"status": "strong structural candidate; lower-vs-upper assignment unresolved", "wire_candidates": ["0x08A B6[1:0]", "0x08A B7[1:0]"], "enum": {"0": "Engine Only", "1": "Engine and Brake 1", "2": "Engine and Brake 2", "3": "Brake Only"}},
      "shift_range": {"status": "unresolved", "wire": None},
      "epb_request": {"status": "unresolved", "wire": None},
      "accelerator_override_prohibition": {"status": "unresolved", "wire": None},
      "low_priority": {"status": "unresolved", "wire": None},
    },
    "5281_upper_longitudinal_request": {
      "request_id": {"status": "strong structural candidate; lower-vs-upper assignment unresolved", "wire_candidates": ["0x08A B6[7:2]", "0x08A B7[7:2]"]},
      "acceleration": {"status": "mapped as one of an indistinguishable pair", "wire_candidates": ["0x08A B8:B9", "0x08A B11:B12"], "scale_mps2_per_count": 0.001},
      "force_distribution": {"status": "strong structural candidate; lower-vs-upper assignment unresolved", "wire_candidates": ["0x08A B6[1:0]", "0x08A B7[1:0]"], "enum": {"0": "Engine Only", "1": "Engine and Brake 1", "2": "Engine and Brake 2", "3": "Brake Only"}},
    },
    "5282_lateral_request": {
      "lateral_id": {"status": "recovered", "wire": "0x08A B21[5:0]"},
      "pinion_angle": {"status": "recovered", "wire": "0x08A B18:B19 signed16", "scale_rad_per_count": round(ANGLE_RAD_PER_COUNT, 12)},
      "steering_assist_gain": {"status": "strong structural join", "wire": "0x08A B24", "scale_per_count": 0.01},
      "damping_gain": {"status": "bounded structural join; zero in both complete drives", "wire": "0x08A B25", "scale_per_count": 0.01},
    },
    "5284_longitudinal_result_id": {"status": "strong candidate", "wire": "0x081 B6[5:0]"},
    "5285_lateral_result_id": {"status": "recovered", "wire": "0x081 B13[5:0]"},
    "57D3_acceleration_valid": {"status": "unresolved", "wire": None, "note": "0x081 B11[4] is request-loss supervision, not OEM-joined to this flag"},
    "57DB_result_acceleration": {"status": "strong candidate", "wire": "0x081 B20:B21 signed16", "scale_mps2_per_count": 0.001},
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
      "0x0CA_supersession_check": old_0ca_boundary(streams[0x081], streams[0x0CA]),
    }
  hold = hold_semantics()
  namespace = requester_id_namespace(drive_reports, hold)
  return {
    "schema": "camry-2026-longitudinal-request-plane-v4",
    "vehicle_access": False,
    "topology": {
      "capture_era": "temporary CAN0/CAN1 repin",
      "0x08A": "native upstream Panda bus2 -> chassis bus0 on Toyota Bus 4",
      "0x081": "native Brake/chassis Panda bus0 -> upstream bus2 on Toyota Bus 4",
      "stock_toyota_b": "Toyota Bus 4 returns to unsplit Panda bus1; compare Toyota network role, not raw Panda bus number",
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
      "request_plane": ("0x08A is the unified observed continuous TSS request-side envelope: the lateral 5282 tuple is recovered there and the duplicated "
                        "signed16 B8:B9/B11:B12 words occupy the 5280/5281 longitudinal lower/upper bound-package geometry. Exact placement before versus after internal TSS application selection remains unresolved."),
      "result_plane": ("0x081 is the unified Brake-owned employed-result/reference/supervision envelope: its lateral selected ID/reference are recovered, "
                       "B6[5:0] is the strongest 5284 longitudinal employed-source-ID candidate, and B20:B21 is the strongest 57DB result-acceleration candidate. "
                       "Toyota's architecture distinguishes the lateral arbitration winner from the longitudinal source actually employed after driver/application comparison."),
      "not_fully_mapped": ("The entire 5280/5281 recorder model is NOT yet byte-named. B6/B7 are strongly recovered structurally as the two packed "
                           "request-ID/allocation bytes (bits7:2 ID, bits1:0 allocation), including active/hold/override transitions; archive-wide unequal ordinary-DRCC frames strongly resolve A as upper and B as lower, "
                           "while shift/EPB, override-prohibition and priority remain unmapped."),
      "0x0CA": "Supersede the old upper/lower/result-triplet interpretation; 0x0CA remains other protected longitudinal/chassis state.",
      "integration": ("For Camry, do not revive 0x160 Alpha Long. The OEM-native integration target is the TSS application/request side feeding Toyota's Vehicle Movement Manager, not direct powertrain/brake actuator synthesis. "
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
