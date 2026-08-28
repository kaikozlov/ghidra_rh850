#!/usr/bin/env python3
"""Reconcile Camry lateral-state carriers from retained CAN and current GTS+ data."""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
from array import array
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
SOURCES = {
  "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
  "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}
REGISTRY = REPO / "data/generated/gtsplus_2026" / "toyota_diag_registry_camry_2026.json"
F33_INGRESS = REPO / "data/generated/camry_8965F3307000_external_lateral_ingress.json"

BUTTONS = {
  "MAIN": lambda d: bool(d[7] & 0x04),
  "RES_PLUS": lambda d: bool(d[3] & 0x80) and not bool(d[6] & 0x80),
  "SET_MINUS": lambda d: bool(d[4] & 0x80) and not bool(d[7] & 0x40),
  "CANCEL": lambda d: bool(d[4] & 0x40) and not bool(d[7] & 0x20),
}
CANONICAL_CARRIER = {
  0x10: (0x10, 0),
  0x12: (0x20, 1),
  0x14: (0x30, 3),
}


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
      h.update(chunk)
  return h.hexdigest()


def rel(path: Path) -> str:
  return str(path.relative_to(REPO))


def at(t: int, seg: int, bases: dict[int, int]) -> dict:
  return {"segment": seg, "segment_s": round((t - bases[seg]) / 1e9, 6), "log_mono_time_ns": t}


def transition_rows(rows, decode, bases: dict[int, int]) -> list[dict]:
  out = []
  previous = object()
  for t, seg, data in rows:
    value = decode(data)
    if value == previous:
      continue
    row = at(t, seg, bases)
    row["value"] = value
    out.append(row)
    previous = value
  return out


def short_button_events(rows, bases: dict[int, int]) -> dict[str, list[dict]]:
  by_seg = defaultdict(list)
  for row in rows:
    by_seg[row[1]].append(row)
  result = {name: [] for name in BUTTONS}
  for name, predicate in BUTTONS.items():
    for seg, seg_rows in sorted(by_seg.items()):
      start = end = None
      count = 0
      for t, _seg, data in seg_rows:
        if predicate(data):
          start = t if start is None else start
          end = t
          count += 1
        elif start is not None:
          if count <= 30:
            result[name].append({
              **at(start, seg, bases),
              "end_segment_s": round((end - bases[seg]) / 1e9, 6),
              "frames": count,
            })
          start = end = None
          count = 0
  return result


def nearest_confusion(source, source_decode, target, target_decode, tolerance_ns: int):
  target_by_seg = defaultdict(list)
  for row in target:
    target_by_seg[row[1]].append(row)
  target_times = {seg: [row[0] for row in rows] for seg, rows in target_by_seg.items()}
  confusion = Counter()
  missed = 0
  max_delta = 0
  for t, seg, data in source:
    candidates = target_by_seg.get(seg, [])
    times = target_times.get(seg, [])
    pos = bisect.bisect_left(times, t)
    nearest = [candidates[i] for i in (pos - 1, pos) if 0 <= i < len(candidates)]
    if not nearest:
      missed += 1
      continue
    picked = min(nearest, key=lambda row: abs(row[0] - t))
    delta = abs(picked[0] - t)
    if delta > tolerance_ns:
      missed += 1
      continue
    max_delta = max(max_delta, delta)
    confusion[(source_decode(data), target_decode(picked[2]))] += 1
  return confusion, missed, max_delta


def b21_intervals(rows) -> list[dict]:
  result = []
  start = last = None
  count = 0
  for t, seg, data in rows:
    if data[21] == 11:
      if start is None:
        start = (t, seg)
      last = (t, seg)
      count += 1
    elif start is not None:
      result.append({"start": start, "last": last, "clear": (t, seg), "a8_frame_count": count})
      start = last = None
      count = 0
  if start is not None:
    result.append({"start": start, "last": last, "clear": None, "a8_frame_count": count})
  return result


def first_after(rows, t0: int, predicate):
  return next((row for row in rows if row[0] >= t0 and predicate(row[2])), None)


def counter_rows(counter: Counter, names: tuple[str, ...]) -> list[dict]:
  rows = []
  for key, count in sorted(counter.items(), key=lambda item: repr(item[0])):
    values = key if isinstance(key, tuple) else (key,)
    row = {name: value for name, value in zip(names, values)}
    row["count"] = count
    rows.append(row)
  return rows


def analyze_drive(path: Path) -> dict:
  streams = defaultdict(list)
  bases: dict[int, int] = {}
  all_times = array("Q")
  b6_times = array("Q")
  raw_hash = hashlib.sha256()
  raw_size = 0
  frame_count = 0
  with gzip.open(path, "rb") as f:
    for line in f:
      raw_hash.update(line)
      raw_size += len(line)
      seg, t, bus, addr, data_hex = json.loads(line)
      seg, t, bus, addr = int(seg), int(t), int(bus), int(addr)
      bases.setdefault(seg, t)
      all_times.append(t)
      frame_count += 1
      if addr == 0x0B6:
        b6_times.append(t)
      if bus == 0 and addr in (0x081, 0x08A, 0x0FE, 0x371, 0x412):
        streams[addr].append((t, seg, bytes.fromhex(data_hex)))

  a8 = streams[0x08A]
  a81 = streams[0x081]
  a371 = streams[0x371]
  a412 = streams[0x412]
  buttons = short_button_events(streams[0x0FE], bases)
  intervals = b21_intervals(a8)

  joint = Counter((d[3], d[21], d[23], d[24]) for _t, _s, d in a8)
  mirror, mirror_missed, mirror_max = nearest_confusion(
    a8, lambda d: d[21], a81, lambda d: d[13], 25_000_000)
  carrier, carrier_missed, carrier_max = nearest_confusion(
    a412, lambda d: d[0], a371, lambda d: (d[9], d[20] & 3), 100_000_000)

  canonical_joined = sum(
    count for (b0, state371), count in carrier.items()
    if b0 in CANONICAL_CARRIER and state371 in CANONICAL_CARRIER.values())
  canonical_matches = sum(
    count for (b0, state371), count in carrier.items()
    if CANONICAL_CARRIER.get(b0) == state371)

  interval_rows = []
  for interval in intervals:
    start_t, start_seg = interval["start"]
    last_t, last_seg = interval["last"]
    clear = interval["clear"]
    start_412 = first_after(a412, start_t, lambda d: d[0] == 0x14)
    start_371 = first_after(a371, start_t, lambda d: (d[9], d[20] & 3) == (0x30, 3))
    clear_t = clear[0] if clear else last_t
    clear_412 = first_after(a412, clear_t, lambda d: d[0] != 0x14)
    clear_371 = first_after(a371, clear_t, lambda d: (d[9], d[20] & 3) != (0x30, 3))
    canonical_clear_371 = first_after(a371, clear_t, lambda d: (d[9], d[20] & 3) in ((0x10, 0), (0x20, 1)))
    prior_cruise_rise = None
    previous = None
    for t, seg, data in a8:
      if t >= start_t:
        break
      if data[3] == 8 and previous != 8:
        prior_cruise_rise = (t, seg)
      previous = data[3]
    row = {
      "start": at(start_t, start_seg, bases),
      "last_active": at(last_t, last_seg, bases),
      "clear": at(*clear, bases) if clear else None,
      "duration_s": round((last_t - start_t) / 1e9, 6),
      "a8_frame_count": interval["a8_frame_count"],
      "incoming_frame_count_all_buses": bisect.bisect_right(all_times, last_t) - bisect.bisect_left(all_times, start_t),
      "b6_count_all_buses_any_dlc": bisect.bisect_right(b6_times, last_t) - bisect.bisect_left(b6_times, start_t),
      "prior_cruise_rise": at(*prior_cruise_rise, bases) if prior_cruise_rise else None,
      "cruise_active_before_b21_11_s": round((start_t - prior_cruise_rise[0]) / 1e9, 6) if prior_cruise_rise else None,
      "carrier_activation": {
        "0x412_b0_0x14": at(start_412[0], start_412[1], bases) | {"lag_from_b21_11_s": round((start_412[0] - start_t) / 1e9, 6)},
        "0x371_b9_0x30_b20_low2_3": at(start_371[0], start_371[1], bases) | {"lag_from_b21_11_s": round((start_371[0] - start_t) / 1e9, 6)},
      },
      "carrier_clear": {
        "0x412_first_not_0x14": at(clear_412[0], clear_412[1], bases) | {"value": clear_412[2][0], "lag_from_b21_clear_s": round((clear_412[0] - clear_t) / 1e9, 6)},
        "0x371_first_not_active": at(clear_371[0], clear_371[1], bases) | {"value": [clear_371[2][9], clear_371[2][20] & 3], "lag_from_b21_clear_s": round((clear_371[0] - clear_t) / 1e9, 6)},
        "0x371_first_canonical_nonactive": at(canonical_clear_371[0], canonical_clear_371[1], bases) | {"value": [canonical_clear_371[2][9], canonical_clear_371[2][20] & 3], "lag_from_b21_clear_s": round((canonical_clear_371[0] - clear_t) / 1e9, 6)},
      },
    }
    interval_rows.append(row)

  cancel_clear = None
  for event in buttons["CANCEL"]:
    if event["segment"] != 21:
      continue
    t0 = event["log_mono_time_ns"]
    clear_a8 = first_after(a8, t0, lambda d: d[3] == 0 and d[21] == 0)
    clear_412 = first_after(a412, t0, lambda d: d[0] != 0x14)
    clear_371 = first_after(a371, t0, lambda d: (d[9], d[20] & 3) != (0x30, 3))
    cancel_clear = {
      "cancel": event,
      "0x08A_cruise_and_b21_clear": at(clear_a8[0], clear_a8[1], bases) | {
        "b3": clear_a8[2][3], "b21": clear_a8[2][21], "lag_s": round((clear_a8[0] - t0) / 1e9, 6)},
      "0x412_b0_clear": at(clear_412[0], clear_412[1], bases) | {
        "b0": clear_412[2][0], "lag_s": round((clear_412[0] - t0) / 1e9, 6)},
      "0x371_active_clear": at(clear_371[0], clear_371[1], bases) | {
        "b9": clear_371[2][9], "b20_low2": clear_371[2][20] & 3, "lag_s": round((clear_371[0] - t0) / 1e9, 6)},
    }

  b21_counts = Counter(d[21] for _t, _s, d in a8)
  b21_11 = [d for _t, _s, d in a8 if d[21] == 11]
  b21_18 = [d for _t, _s, d in a8 if d[21] == 18]
  mirror_matches = sum(count for (a, b), count in mirror.items() if a == b)
  return {
    "source": {
      "path": rel(path),
      "compressed_size": path.stat().st_size,
      "compressed_sha256": sha256(path),
      "uncompressed_size": raw_size,
      "uncompressed_sha256": raw_hash.hexdigest(),
      "frame_count": frame_count,
      "segments": sorted(bases),
    },
    "0x08A_b21": {
      "value_set": sorted(b21_counts),
      "value_counts": {str(key): value for key, value in sorted(b21_counts.items())},
      "joint_b3_b21_b23_b24_counts": counter_rows(joint, ("b3", "b21", "b23", "b24")),
      "conditions": {
        "b21_11_only_cruise_active_b24_100": all(d[3] == 8 and d[24] == 100 for d in b21_11),
        "b21_18_only_cruise_off_b24_50": all(d[3] == 0 and d[24] == 50 for d in b21_18),
        "b21_18_b23_0x20_count": sum(d[23] == 0x20 for d in b21_18),
        "b21_18_count": len(b21_18),
      },
      "transition_timeline": transition_rows(a8, lambda d: [d[3], d[21], d[23], d[24]], bases),
      "b21_11_intervals": interval_rows,
    },
    "0x081_b13_mirror": {
      "method": "same-segment nearest 0x081/32 frame for each 0x08A/32 frame, absolute delta <=25 ms",
      "paired_count": sum(mirror.values()),
      "unpaired_0x08A_count": mirror_missed,
      "matching_count": mirror_matches,
      "matching_fraction": round(mirror_matches / sum(mirror.values()), 9),
      "max_join_delta_ms": round(mirror_max / 1e6, 6),
      "confusion": counter_rows(mirror, ("0x08A_b21", "0x081_b13")),
      "transition_timeline": transition_rows(a81, lambda d: d[13], bases),
    },
    "three_state_carrier": {
      "canonical_states": [
        {"0x412_b0": b0, "0x371_b9": state[0], "0x371_b20_low2": state[1]}
        for b0, state in CANONICAL_CARRIER.items()
      ],
      "0x412_b0_counts": {str(k): v for k, v in sorted(Counter(d[0] for _t, _s, d in a412).items())},
      "0x371_b9_b20_low2_counts": counter_rows(Counter((d[9], d[20] & 3) for _t, _s, d in a371), ("b9", "b20_low2")),
      "join_method": "same-segment nearest 0x371/32 frame for each 0x412/8 frame, absolute delta <=100 ms",
      "paired_count": sum(carrier.values()),
      "unpaired_0x412_count": carrier_missed,
      "max_join_delta_ms": round(carrier_max / 1e6, 6),
      "canonical_joined_count": canonical_joined,
      "canonical_matching_count": canonical_matches,
      "canonical_matching_fraction": round(canonical_matches / canonical_joined, 9),
      "confusion": [
        {"0x412_b0": key[0], "0x371_b9": key[1][0], "0x371_b20_low2": key[1][1], "count": count}
        for key, count in sorted(carrier.items(), key=lambda item: repr(item[0]))
      ],
      "0x412_transition_timeline": transition_rows(a412, lambda d: d[0], bases),
      "0x371_transition_timeline": transition_rows(a371, lambda d: [d[9], d[20] & 3], bases),
    },
    "known_0x0FE_cruise_button_events": {
      "counts": {name: len(events) for name, events in buttons.items()},
      "events": buttons,
      "boundary": "These exact same-car predicates recover MAIN/RES+/SET-/CANCEL only; no independent physical LTA-button carrier is decoded or claimed.",
    },
    "segment21_cancel_clear": cancel_clear,
  }


def build() -> dict:
  drives = {name: analyze_drive(path) for name, path in SOURCES.items()}
  registry = json.loads(REGISTRY.read_text())
  emps = registry["catalogs"]["405"]
  target_lateral = next(row for row in emps["dids"]["0x1CEE"] if row["name"] == "Target Lateral ID")
  frc = registry["catalogs"]["498"]
  indicator = next(row for row in frc["active_tests"] if row["name"] == "LTA Indicator 1")
  ingress = json.loads(F33_INGRESS.read_text())
  accepted = [row["can_id"] for row in ingress["normal_rx"]["accepted"]]
  combined_intervals = [
    interval
    for drive in drives.values()
    for interval in drive["0x08A_b21"]["b21_11_intervals"]
  ]
  return {
    "schema": "camry-2026-lta-state-reconciliation-v1",
    "drives": drives,
    "combined": {
      "b21_value_set_both_drives": sorted(set.intersection(*(
        set(drive["0x08A_b21"]["value_set"]) for drive in drives.values()))),
      "b21_11_duration_s": round(sum(row["duration_s"] for row in combined_intervals), 6),
      "b21_11_incoming_frame_count_all_buses": sum(row["incoming_frame_count_all_buses"] for row in combined_intervals),
      "b6_during_entire_b21_11_intervals_all_buses_any_dlc": sum(row["b6_count_all_buses_any_dlc"] for row in combined_intervals),
    },
    "current_gtsplus_join": {
      "source": {"path": rel(REGISTRY), "size": REGISTRY.stat().st_size, "sha256": sha256(REGISTRY)},
      "emps_category": emps["category"],
      "target_lateral_id": {
        "did": "0x1CEE",
        "alternate_did": f"0x{target_lateral['alternate_did']:04X}",
        "monitor_key": target_lateral["monitor_key"],
        "bit_start": target_lateral["bit_start"],
        "bit_end": target_lateral["bit_end"],
        "selected_dictionary": {key: target_lateral["patterns"][key] for key in ("0", "11", "18")},
        "dictionary": target_lateral["patterns"],
        "source_ddb_sha256": registry["source_identity"]["gtsplus/NA/DB/Gen/EMPS_P5.ddb"]["sha256"],
      },
      "frc_lta_indicator_1": {
        "category": frc["category"],
        "service": indicator["service"],
        "routine_id": indicator["routine_id"],
        "start_static": indicator["start_static"],
        "stop_static": indicator["stop_static"],
        "result_static": indicator["result_static"],
        "execution": indicator["execution"],
        "boundary": "FRC fixed RoutineControl/display active-test concept only; it is not a synchronized live-state oracle and is not used to name a captured byte.",
      },
    },
    "exact_f33_receive_boundary": {
      "source": {"path": rel(F33_INGRESS), "size": F33_INGRESS.stat().st_size, "sha256": sha256(F33_INGRESS)},
      "descriptor_count": ingress["normal_rx"]["descriptor_count"],
      "accepted_can_ids": accepted,
      "state_carriers_absent": {can_id: can_id not in accepted for can_id in ("0x08A", "0x371", "0x412")},
      "interpretation": "The three correlated messages are state/display-plane evidence, not exact-F33 EPS ingress.",
    },
    "interpretation": {
      "identification": "Bus-0 0x08A B21=11 is strongly identified as LTA/LCA active by the exact current-GTS+ numeric dictionary joined to repeated cruise-distinct dynamic state, the 0x081 mirror, and the 0x371/0x412 three-state carrier.",
      "proof_boundary": "This is a strong cross-domain numeric+dynamic join, not target-native byte-exact OEM producer-wire proof: the current 0x08A producer mapping is unavailable and exact F33 receives none of 0x08A/0x371/0x412.",
      "historical_labels": "Historical Toyota names LTA_RELATED for 0x371 and LKAS_HUD for 0x412 are corroboration only; no historical field layout is transferred.",
      "button_boundary": "No physical LTA-button carrier is recovered. The decoded 0x0FE pulses are retained only as the already-validated cruise buttons.",
      "production_output_authorized": False,
    },
  }


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--out", type=Path, default=REPO / "data/generated/camry_2026_lta_state_reconciliation.json")
  args = parser.parse_args()
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
  print(args.out)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
