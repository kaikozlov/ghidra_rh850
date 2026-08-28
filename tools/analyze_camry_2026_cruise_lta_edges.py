#!/usr/bin/env python3
"""Recover cruise and lateral/HUD state transitions from the two relay-correct Camry drives.

This analysis uses only already-validated same-car 0x0FE button bits, exact Camry
0x0AA wheel-speed geometry, and raw state transitions. It deliberately keeps the
0x08A/0x081/0x412 lateral-looking state semantically bounded: exact F33 EPS does
not receive 0x08A and no target-native CAN-field name is asserted here.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
  sys.path.insert(0, str(REPO))

from tools.analyze_camry_2026_relay_capture import decode_wheel_speed

RAW = REPO / "targets/camry-2026/raw-20260827"
SOURCES = (
  ("drive_a", RAW / "camry_relay_route_can_20260827.ndjson.gz"),
  ("drive_b", RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz"),
)

BUTTONS: dict[str, Callable[[bytes], bool]] = {
  "MAIN": lambda d: bool(d[7] & 0x04),
  "RES_PLUS": lambda d: bool(d[3] & 0x80) and not bool(d[6] & 0x80),
  "SET_MINUS": lambda d: bool(d[4] & 0x80) and not bool(d[7] & 0x40),
  "CANCEL": lambda d: bool(d[4] & 0x40) and not bool(d[7] & 0x20),
}


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
      h.update(chunk)
  return h.hexdigest()


def load(path: Path):
  with gzip.open(path, "rt") as f:
    for line in f:
      seg, t, bus, addr, data = json.loads(line)
      yield int(seg), int(t), int(bus), int(addr), bytes.fromhex(data)


def true_intervals(rows: list[tuple[int, bool]]) -> list[tuple[int, int, int]]:
  out: list[tuple[int, int, int]] = []
  start = last = None
  count = 0
  for t, value in rows:
    if value and start is None:
      start = last = t
      count = 1
    elif value:
      last = t
      count += 1
    elif start is not None:
      out.append((start, last, count))
      start = last = None
      count = 0
  if start is not None:
    out.append((start, last, count))
  return out


def segment_offset(t: int, bases: dict[int, int], seg: int) -> float:
  return (t - bases[seg]) / 1e9


def nearest(rows: list[tuple[int, object]], t: int):
  return min(rows, key=lambda row: abs(row[0] - t)) if rows else None


def state_intervals(rows: list[tuple[int, bytes]], predicate: Callable[[bytes], bool]) -> list[tuple[int, int]]:
  ints = true_intervals([(t, predicate(d)) for t, d in rows])
  return [(a, b) for a, b, _ in ints]


def in_intervals(t: int, intervals: list[tuple[int, int]]) -> bool:
  return any(a <= t <= b for a, b in intervals)


def event_rows(name: str, rows: list[tuple[int, bytes]], bases: dict[int, int], seg: int) -> list[dict]:
  events = []
  for start, end, frames in true_intervals([(t, BUTTONS[name](d)) for t, d in rows]):
    # Restrict to human-scale button pulses; long states are not button presses.
    if frames > 30:
      continue
    events.append({
      "segment": seg,
      "start_s": round(segment_offset(start, bases, seg), 6),
      "end_s": round(segment_offset(end, bases, seg), 6),
      "frames": frames,
      "start_ns": start,
      "end_ns": end,
    })
  return events


def analyze_one(label: str, path: Path) -> dict:
  frames = list(load(path))
  segs = sorted({seg for seg, *_ in frames})
  bases: dict[int, int] = {}
  by_seg_fe: dict[int, list[tuple[int, bytes]]] = defaultdict(list)
  a8: list[tuple[int, bytes, int]] = []
  a81: list[tuple[int, bytes, int]] = []
  hud412: list[tuple[int, bytes, int]] = []
  speeds: list[tuple[int, float, int]] = []
  b6: list[tuple[int, int, int, int]] = []

  for seg, t, bus, addr, dat in frames:
    bases[seg] = min(bases.get(seg, t), t)
    if bus == 0 and addr == 0x0FE and len(dat) == 32:
      by_seg_fe[seg].append((t, dat))
    if bus == 0 and addr == 0x08A and len(dat) == 32:
      a8.append((t, dat, seg))
    elif bus == 0 and addr == 0x081 and len(dat) == 32:
      a81.append((t, dat, seg))
    elif bus == 0 and addr == 0x412 and len(dat) == 8:
      hud412.append((t, dat, seg))
    elif bus == 0 and addr == 0x0AA and len(dat) == 8:
      speeds.append((t, decode_wheel_speed(dat), seg))
    if addr == 0x0B6:
      b6.append((t, seg, bus, len(dat)))

  buttons = {name: [] for name in BUTTONS}
  for seg in segs:
    for name in BUTTONS:
      buttons[name].extend(event_rows(name, by_seg_fe[seg], bases, seg))

  a8_rows = [(t, d) for t, d, _ in a8]
  cruise_ints = state_intervals(a8_rows, lambda d: d[3] == 0x08)
  lateral_ints = state_intervals(a8_rows, lambda d: d[21] == 0x0B)

  # Every 0x08A cruise-active rising edge should follow an effective MAIN edge.
  cruise_rises = []
  prior = a8[0][1][3] if a8 else 0
  for t, d, seg in a8[1:]:
    if prior != 0x08 and d[3] == 0x08:
      candidates = [e for e in buttons["MAIN"] if e["start_ns"] <= t and 0 <= t - e["start_ns"] <= int(1e9)]
      ev = max(candidates, key=lambda e: e["start_ns"]) if candidates else None
      nspeed = nearest([(tt, v) for tt, v, _ in speeds], t)
      cruise_rises.append({
        "segment": seg,
        "seconds": round(segment_offset(t, bases, seg), 6),
        "set_speed_raw_kph": d[10],
        "wheel_speed_kph": round(float(nspeed[1]), 3) if nspeed else None,
        "set_minus_wheel_kph": round(d[10] - float(nspeed[1]), 3) if nspeed else None,
        "main_press_segment": ev["segment"] if ev else None,
        "main_press_start_s": ev["start_s"] if ev else None,
        "lag_from_main_start_s": round((t - ev["start_ns"]) / 1e9, 6) if ev else None,
      })
    prior = d[3]

  # Build state transition timeline for the cruise bit and set-speed byte.
  a8_transitions = []
  prior_state = None
  for t, d, seg in a8:
    cur = (d[3], d[10], d[20], d[21], d[23], d[24])
    if cur != prior_state:
      a8_transitions.append({
        "segment": seg,
        "seconds": round(segment_offset(t, bases, seg), 6),
        "b3": d[3], "b10": d[10], "b20": d[20], "b21": d[21], "b23": d[23], "b24": d[24],
      })
      prior_state = cur

  # The structurally distinct lateral/HUD candidate is the b21==0x0B state.
  lateral_summary = []
  for start, end in lateral_ints:
    seg = next(seg for t, _, seg in a8 if t >= start)
    matching_a8 = [d for t, d, _ in a8 if start <= t <= end]
    matching_81 = [d for t, d, _ in a81 if start <= t <= end]
    matching_hud = [d for t, d, _ in hud412 if start <= t <= end]
    modal_hud = None
    if matching_hud:
      c = Counter(d.hex() for d in matching_hud)
      modal_hud, modal_count = c.most_common(1)[0]
    else:
      modal_count = 0
    lateral_summary.append({
      "start_segment": seg,
      "start_s": round(segment_offset(start, bases, seg), 6),
      "duration_s": round((end - start) / 1e9, 6),
      "a8_frame_count": len(matching_a8),
      "a8_b21_values": sorted({d[21] for d in matching_a8}),
      "a8_b24_values": sorted({d[24] for d in matching_a8}),
      "id081_b13_match_fraction": round(sum(d[13] == 0x0B for d in matching_81) / len(matching_81), 6) if matching_81 else None,
      "hud_0x412_modal_payload": modal_hud,
      "hud_0x412_modal_fraction": round(modal_count / len(matching_hud), 6) if matching_hud else None,
      "b6_count_all_buses": sum(1 for t, *_ in b6 if start <= t <= end),
    })

  # Dynamic counts inside all 0x08A cruise-active intervals.
  active_b6 = sum(1 for t, *_ in b6 if in_intervals(t, cruise_ints))
  active_frames = sum(1 for _seg, t, _bus, _addr, _dat in frames if in_intervals(t, cruise_ints))
  lateral_frames = sum(1 for _seg, t, _bus, _addr, _dat in frames if in_intervals(t, lateral_ints))

  # RES+/SET- -> set-speed changes and CANCEL -> cruise clear are raw timing facts.
  control_edges = []
  for name in ("RES_PLUS", "SET_MINUS", "CANCEL"):
    for ev in buttons[name]:
      after = [(t, d, seg) for t, d, seg in a8 if ev["start_ns"] <= t <= ev["start_ns"] + int(0.8e9)]
      before = [(t, d, seg) for t, d, seg in a8 if t < ev["start_ns"]]
      if not after or not before:
        continue
      prev = before[-1][1]
      first_change = next(((t, d, seg) for t, d, seg in after if (d[3], d[10]) != (prev[3], prev[10])), None)
      control_edges.append({
        "button": name,
        "segment": ev["segment"],
        "button_start_s": ev["start_s"],
        "a8_before_b3": prev[3],
        "a8_before_b10": prev[10],
        "first_a8_change_s": round(segment_offset(first_change[0], bases, first_change[2]), 6) if first_change else None,
        "a8_after_b3": first_change[1][3] if first_change else None,
        "a8_after_b10": first_change[1][10] if first_change else None,
        "lag_s": round((first_change[0] - ev["start_ns"]) / 1e9, 6) if first_change else None,
      })

  return {
    "source": {"file": str(path.relative_to(REPO)), "sha256": sha256(path), "frame_count": len(frames), "segments": segs},
    "button_events": {name: [{k: v for k, v in e.items() if not k.endswith("_ns")} for e in events] for name, events in buttons.items()},
    "cruise_active": {
      "interval_count": len(cruise_ints),
      "duration_s": round(sum((b - a) / 1e9 for a, b in cruise_ints), 6),
      "incoming_frame_count_all_buses": active_frames,
      "b6_count_all_buses": active_b6,
      "rising_edges": cruise_rises,
      "control_edges": control_edges,
    },
    "lateral_hud_candidate": {
      "definition": "structural only: bus0 0x08A byte21 == 0x0B; not an OEM-named signal and not an EPS command",
      "interval_count": len(lateral_ints),
      "duration_s": round(sum((b - a) / 1e9 for a, b in lateral_ints), 6),
      "incoming_frame_count_all_buses": lateral_frames,
      "b6_count_all_buses": sum(1 for t, *_ in b6 if in_intervals(t, lateral_ints)),
      "intervals": lateral_summary,
    },
    "a8_state_transitions": a8_transitions,
  }


def build() -> dict:
  drives = {label: analyze_one(label, path) for label, path in SOURCES}
  rises = [r for d in drives.values() for r in d["cruise_active"]["rising_edges"]]
  speed_deltas = [abs(r["set_minus_wheel_kph"]) for r in rises if r["set_minus_wheel_kph"] is not None]
  return {
    "schema": "camry-2026-cruise-lta-edge-census-v1",
    "drives": drives,
    "combined": {
      "cruise_active_duration_s": round(sum(d["cruise_active"]["duration_s"] for d in drives.values()), 6),
      "cruise_active_incoming_frame_count_all_buses": sum(d["cruise_active"]["incoming_frame_count_all_buses"] for d in drives.values()),
      "b6_during_cruise_active_all_buses": sum(d["cruise_active"]["b6_count_all_buses"] for d in drives.values()),
      "lateral_hud_candidate_duration_s": round(sum(d["lateral_hud_candidate"]["duration_s"] for d in drives.values()), 6),
      "lateral_hud_candidate_incoming_frame_count_all_buses": sum(d["lateral_hud_candidate"]["incoming_frame_count_all_buses"] for d in drives.values()),
      "b6_during_lateral_hud_candidate_all_buses": sum(d["lateral_hud_candidate"]["b6_count_all_buses"] for d in drives.values()),
      "cruise_rising_edge_count": len(rises),
      "cruise_rises_with_recent_main": sum(r["main_press_start_s"] is not None for r in rises),
      "max_abs_set_speed_vs_wheel_kph_at_cruise_rise": round(max(speed_deltas), 3) if speed_deltas else None,
    },
    "interpretation": {
      "cruise": "observed/deterministic: 0x08A byte3=0x08 is a machine-visible cruise operating-state carrier. It toggles after effective MAIN/CANCEL actions and byte10 is the set-speed value in km/h: activation values track independent 0x0AA wheel speed and RES+/SET- adjust it.",
      "lateral_hud_candidate": "bounded: 0x08A byte21/byte24, mirrored 0x081 byte13, and 0x412 display-state changes form a state class distinct from the cruise-main and button-echo classes. Long intervals overlap the operator-reported steering-assistance drive, but no target-native current-Camry OEM name is yet joined, so this is not called LTA-active proof.",
      "b6": "observed/deterministic: B6 remains absent not only globally but throughout machine-recovered cruise-active intervals and throughout the bounded lateral/HUD candidate intervals.",
      "production_output_authorized": False,
    },
  }


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--out", type=Path, default=REPO / "data/generated/camry_2026_cruise_lta_edge_census.json")
  args = ap.parse_args()
  out = build()
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
  print(args.out)
  return 0

if __name__ == "__main__":
  raise SystemExit(main())
