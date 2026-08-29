#!/usr/bin/env python3
"""Reduce the 2026-08-27 relay-correct Camry capture to portable CAN evidence."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"


def sha256(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def be_raw(dat: bytes, start_bit: int, size: int, signed: bool = False) -> int:
  """Decode one Motorola DBC signal using opendbc bit numbering."""
  be_bits = [j + i * 8 for i in range(len(dat)) for j in range(7, -1, -1)]
  idx = be_bits.index(start_bit)
  bits = be_bits[idx:idx + size]
  if len(bits) != size:
    raise ValueError(f"signal {start_bit}|{size} exceeds payload")
  value = 0
  for bit in bits:
    byte_i, bit_i = divmod(bit, 8)
    value = (value << 1) | ((dat[byte_i] >> bit_i) & 1)
  if signed and value & (1 << (size - 1)):
    value -= 1 << size
  return value


def load_snapshot(path: Path) -> dict:
  with gzip.open(path, "rt") as f:
    return json.load(f)


def summarize_snapshot(path: Path) -> dict:
  src = load_snapshot(path)
  frames = src["frames"]
  by_bus = Counter(int(x["bus"]) for x in frames)
  ids = defaultdict(set)
  selected = defaultdict(Counter)
  seq = defaultdict(list)
  for x in frames:
    bus = int(x["bus"])
    addr = int(x["addr"])
    dat = bytes.fromhex(x["data"])
    ids[bus].add((addr, len(dat)))
    seq[bus].append((addr, dat))
    if addr in (0x00F, 0x025, 0x030, 0x0D7, 0x0B6, 0x51E, 0x351, 0x394, 0x4A3):
      selected[(addr, len(dat))][bus] += 1
  ready = []
  for x in frames:
    if int(x["addr"]) == 0x51E and int(x["bus"]) == 0:
      dat = bytes.fromhex(x["data"])
      ready.append((dat[0] >> 7) & 1)
  return {
    "duration_s": round(float(src["duration_s"]), 6),
    "frame_count": len(frames),
    "frames_by_bus": {str(k): by_bus[k] for k in sorted(by_bus)},
    "id_dlc_count_by_bus": {str(k): len(ids[k]) for k in sorted(ids)},
    "bus0_bus2_sequence_identical": seq[0] == seq[2],
    "selected_counts": {
      f"0x{addr:03X}/{dlc}": {str(b): selected[(addr, dlc)][b] for b in range(3)}
      for addr, dlc in sorted(selected)
    },
    "ready_values_bus0": sorted(set(ready)),
  }


def load_route(path: Path):
  with gzip.open(path, "rt") as f:
    for line in f:
      seg, t, bus, addr, data = json.loads(line)
      yield int(seg), int(t), int(bus), int(addr), bytes.fromhex(data)


def decode_wheel_speed(dat: bytes) -> float:
  # Existing Camry/Corolla H/F 0x0AA geometry, independently exercised on this car.
  vals = [be_raw(dat, s, 15) * 0.01 - 67.67 for s in (6, 22, 38, 54)]
  return sum(vals) / 4


def contiguous_intervals(rows: list[tuple[int, bool]]) -> list[dict]:
  out = []
  start = last = None
  count = 0
  for t, on in rows:
    if on and start is None:
      start = last = t
      count = 1
    elif on:
      last = t
      count += 1
    elif start is not None:
      out.append({"start_ns": start, "end_ns": last, "frames": count})
      start = last = None
      count = 0
  if start is not None:
    out.append({"start_ns": start, "end_ns": last, "frames": count})
  return out


def summarize_route(path: Path, segment_ids: tuple[int, ...], structural_segments: tuple[int, ...]) -> dict:
  segment_set = set(segment_ids)
  counts = {seg: Counter() for seg in segment_ids}
  tmin = {seg: None for seg in segment_ids}
  tmax = {seg: None for seg in segment_ids}
  speeds = {seg: [] for seg in segment_ids}
  gears = {seg: Counter() for seg in segment_ids}
  ready = {seg: Counter() for seg in segment_ids}
  fe_rows = {seg: [] for seg in segment_ids}
  a8_rows = {seg: [] for seg in segment_ids}
  b6_any = []
  seen_segments = set()

  for seg, t, bus, addr, dat in load_route(path):
    if seg not in segment_set:
      raise ValueError(f"unexpected segment {seg} in {path.name}; expected {segment_ids}")
    seen_segments.add(seg)
    counts[seg][(bus, addr, len(dat))] += 1
    tmin[seg] = t if tmin[seg] is None else min(tmin[seg], t)
    tmax[seg] = t if tmax[seg] is None else max(tmax[seg], t)
    if addr == 0x0B6:
      b6_any.append((seg, t, bus, len(dat), dat.hex()))
    if bus != 0:
      continue
    if addr == 0x0AA and len(dat) == 8:
      speeds[seg].append(decode_wheel_speed(dat))
    elif addr == 0x127 and len(dat) == 8:
      gears[seg][be_raw(dat, 47, 4)] += 1
    elif addr == 0x51E and len(dat) == 8:
      ready[seg][(dat[0] >> 7) & 1] += 1
    elif addr == 0x0FE and len(dat) == 32:
      fe_rows[seg].append((t, dat))
    elif addr == 0x08A and len(dat) == 32:
      a8_rows[seg].append((t, dat))

  if seen_segments != segment_set:
    raise ValueError(f"missing segments in {path.name}: {sorted(segment_set - seen_segments)}")

  segments = []
  for seg in segment_ids:
    by_bus = {str(bus): sum(n for (b, _a, _l), n in counts[seg].items() if b == bus) for bus in range(3)}
    ids = {str(bus): len({(a, l) for (b, a, l), n in counts[seg].items() if b == bus and n}) for bus in range(3)}
    sp = speeds[seg]
    segments.append({
      "segment": seg,
      "duration_s": round((tmax[seg] - tmin[seg]) / 1e9, 6) if tmin[seg] is not None else 0,
      "frames_by_bus": by_bus,
      "id_dlc_count_by_bus": ids,
      "speed_kph": {
        "min": round(min(sp), 3) if sp else None,
        "max": round(max(sp), 3) if sp else None,
        "moving_over_2kph_fraction": round(sum(x > 2 for x in sp) / len(sp), 6) if sp else None,
      },
      "gear_raw_counts": {str(k): v for k, v in sorted(gears[seg].items())},
      "ready_bit_counts": {str(k): v for k, v in sorted(ready[seg].items())},
      "protected_counts": {
        "0x00F/8": {str(b): counts[seg][(b, 0x00F, 8)] for b in range(3)},
        "0x0D7/32": {str(b): counts[seg][(b, 0x0D7, 32)] for b in range(3)},
        "0x0B6/32": {str(b): counts[seg][(b, 0x0B6, 32)] for b in range(3)},
      },
    })

  # Same-car prior diagnostic/CAN join already established these 0x0FE switch bits.
  switch_defs = {
    "MAIN": lambda d: bool(d[7] & 0x04),
    "SET_MINUS": lambda d: bool(d[4] & 0x80) and not bool(d[7] & 0x40),
  }
  switches = {}
  for name, fn in switch_defs.items():
    switches[name] = {}
    for seg in segment_ids:
      rows = [(t, fn(d)) for t, d in fe_rows[seg]]
      ints = [x for x in contiguous_intervals(rows) if x["frames"] <= 30]
      if ints:
        # Store offsets from the first 0x0FE sample, not opaque absolute monotonic time.
        base = fe_rows[seg][0][0]
        switches[name][str(seg)] = [
          {
            "start_s": round((x["start_ns"] - base) / 1e9, 6),
            "end_s": round((x["end_ns"] - base) / 1e9, 6),
            "frames": x["frames"],
          }
          for x in ints
        ]

  # This raw relay-capture artifact treats 0x08A structurally; VAR-081/CORR-134
  # subsequently recover its upstream-request semantics. Exact F33 Rx configuration does not
  # accept this ID. Its sparse tuple changes are retained as cross-ECU state markers,
  # never as lateral-command attribution.
  a8_transitions = {}
  for seg in structural_segments:
    rows = a8_rows[seg]
    if not rows:
      continue
    base = rows[0][0]
    tracked = (3, 6, 7, 10, 20, 22)
    prior = tuple(rows[0][1][i] for i in tracked)
    changes = []
    for t, d in rows[1:]:
      cur = tuple(d[i] for i in tracked)
      if cur != prior:
        changes.append({"seconds": round((t - base) / 1e9, 6), "bytes_3_6_7_10_20_22": "".join(f"{x:02x}" for x in cur)})
        prior = cur
    if changes:
      a8_transitions[str(seg)] = changes

  return {
    "frame_count": sum(sum(c.values()) for c in counts.values()),
    "segment_count": len(segment_ids),
    "segments": segments,
    "b6_any_bus_any_length_count": len(b6_any),
    "b6_examples": [list(x) for x in b6_any[:5]],
    "validated_cruise_switch_events": switches,
    "structural_0x08A_transitions": a8_transitions,
    "interpretation": (
      "The retained route proves a relay-correct moving capture with healthy protected 0x00F/0x0D7 traffic and zero 0x0B6 on every incoming bus/length. "
      "Same-car 0x0FE switch decoding and sparse 0x08A cross-ECU state changes provide timing markers, but neither machine-proves an exact factory-LTA-active interval. "
      "Accordingly this raw artifact alone treats zero B6 only as a segment-level observation; later synchronized LTA/LCA evidence plus exact F33 firmware proves that stock steering can occur through the B6-independent internal assist path, so a stock-B6 template/cadence is not required to explain these drives."
    ),
  }

def build() -> dict:
  nrtd = RAW / "camry_post_repin_nrtd_20260827.json.gz"
  ready = RAW / "camry_post_repin_ready_20260827.json.gz"
  route = RAW / "camry_relay_route_can_20260827.ndjson.gz"
  confirmation_route = RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz"
  drive = summarize_route(route, tuple(range(9)), (4, 5))
  confirmation_drive = summarize_route(confirmation_route, tuple(range(16, 26)), tuple(range(16, 26)))
  combined_frames = drive["frame_count"] + confirmation_drive["frame_count"]
  combined_segments = drive["segment_count"] + confirmation_drive["segment_count"]
  return {
    "schema": "camry-2026-relay-correct-capture-v2",
    "sources": {
      p.name: {"size": p.stat().st_size, "sha256": sha256(p)}
      for p in (nrtd, ready, route, confirmation_route)
    },
    "capture_boundary": {
      "operation": "passive incoming CAN only; openpilot/Panda production output remained disabled",
      "route_privacy": "tracked route artifacts contain only src<128 CAN frames reduced from 19 rlog segments across two drives; no GPS, video, or user-facing route metadata",
      "dedicated_logger_failure": "the separate direct-Panda logger collided with pandad and stopped on a Panda USB CHECKSUM_ERROR; all drive conclusions use normal loggerd rlogs reduced to tracked CAN-only artifacts",
      "operator_report_boundary": "the operator reported apparent factory steering assistance during the first drive and deliberately retried the experiment on the second drive; this raw relay-capture artifact alone does not semantically classify the active intervals, which are subsequently identified by VAR-081's GTS+ plus 0x08A reconciliation",
    },
    "post_repin_nrtd": summarize_snapshot(nrtd),
    "post_repin_ready": summarize_snapshot(ready),
    "drive": drive,
    "confirmation_drive": confirmation_drive,
    "combined_route_evidence": {
      "frame_count": combined_frames,
      "segment_count": combined_segments,
      "b6_any_bus_any_length_count": drive["b6_any_bus_any_length_count"] + confirmation_drive["b6_any_bus_any_length_count"],
    },
    "conclusion": {
      "relay_topology": "observed: the former bus-1 steering/state family appears on the CAN0/CAN2 pair after the physical CAN0/CAN1 repin, while the separate 22-ID FD family remains on bus1",
      "b6": f"repeated bounded negative: zero 0x0B6 at any DLC on any incoming bus across {combined_segments} retained route segments / {combined_frames} incoming CAN frames from two separate drives, while protected 0x00F/0x0D7 remain healthy",
      "semantic_upgrade": "VAR-081/CORR-134 subsequently identify complete retained LTA/LCA-active intervals and Bus-4 0x08A as the lateral-request representation; CORR-135 closes the false inference that zero B6 requires an 0x08A-to-B6 transform because exact F33 has a B6-independent internal assist path",
      "next_observation": "identify the observed Bus-4 0x08A producer and exact SecOC/security ownership, and independently trace which exact external/local state selects or drives F33's B6-independent D0218/CC60/CC50 assist path during LTA/LCA; do not assume an 0x08A-to-B6 transform",
      "production_output_authorized": False,
    },
  }

def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--out", type=Path, default=REPO / "data/generated/camry_2026_relay_correct_capture.json")
  args = ap.parse_args()
  out = build()
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
  print(args.out)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
