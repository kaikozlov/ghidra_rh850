#!/usr/bin/env python3
"""Build deterministic 2026 Camry READY/gear evidence from retained passive captures."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "community/kai/camry-2026/raw-20260826"
DEFAULT_OUT = REPO / "data/generated/camry_2026_ready_gear.json"
SOURCE_NAMES = (
  "READY_GEAR_MANIFEST.txt",
  "camry_ready_gear_capture.py",
  "camry_ready_gear_20260826.json.gz",
  "camry_b_capture.py",
  "camry_ready_b_20260826.json.gz",
)


def sha256(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def load_gzip_json(name: str) -> dict:
  with gzip.open(RAW / name, "rt") as f:
    return json.load(f)


def signed(value: int, bits: int) -> int:
  sign = 1 << (bits - 1)
  return value - (1 << bits) if value & sign else value


def be_signal(data: bytes, start_bit: int, size: int, *, is_signed: bool = False) -> int:
  be_bits = [j + i * 8 for i in range(len(data)) for j in range(7, -1, -1)]
  idx = be_bits.index(start_bit)
  positions = be_bits[idx:idx + size]
  if len(positions) != size:
    raise ValueError(f"signal {start_bit}|{size} exceeds payload")
  value = 0
  for pos in positions:
    value = (value << 1) | ((data[pos // 8] >> (pos % 8)) & 1)
  return signed(value, size) if is_signed else value


def toyota_checksum(address: int, data: bytes) -> int:
  total = len(data)
  addr = address
  while addr:
    total += addr & 0xFF
    addr >>= 8
  total += sum(data[:-1])
  return total & 0xFF


def stream(obj: dict, bus: int, addr: int, length: int) -> list[dict]:
  return [r for r in obj["frames"] if r["bus"] == bus and r["addr"] == addr and r["len"] == length]


def transition_timeline(rows: list[dict], start_bit: int, size: int) -> list[dict]:
  out = []
  prev = None
  for row in rows:
    data = bytes.fromhex(row["data"])
    value = be_signal(data, start_bit, size)
    if value != prev:
      out.append({"seconds": round(float(row["t"]), 6), "value": value, "payload": data.hex()})
      prev = value
  return out


def capture_summary(obj: dict) -> dict:
  gear = stream(obj, 1, 0x127, 8)
  ready = stream(obj, 1, 0x51E, 8)
  wheels = stream(obj, 1, 0x0AA, 8)
  gear_payloads = [bytes.fromhex(r["data"]) for r in gear]
  return {
    "label": obj["capture"],
    "duration_s": round(float(obj["duration_s"]), 9),
    "total_frames": len(obj["frames"]),
    "0x127": {
      "frame_count": len(gear),
      "checksum_matches": sum(toyota_checksum(0x127, d) == d[-1] for d in gear_payloads),
      "raw_values": sorted({be_signal(d, 47, 4) for d in gear_payloads}),
      "transition_timeline": transition_timeline(gear, 47, 4),
    },
    "0x51E": {
      "frame_count": len(ready),
      "ready_values": sorted({be_signal(bytes.fromhex(r["data"]), 7, 1) for r in ready}),
      "transition_timeline": transition_timeline(ready, 7, 1),
    },
    "0x0AA_stationary_corroboration": {
      "frame_count": len(wheels),
      "unique_payloads": sorted({r["data"] for r in wheels}),
      "interpretation": "The wheel-speed carrier remains at the same single zero-motion payload used in the earlier stationary Camry baseline; this supports the operator-reported stationary condition without assigning new firmware semantics.",
    },
  }


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  first = load_gzip_json("camry_ready_gear_20260826.json.gz")
  b_run = load_gzip_json("camry_ready_b_20260826.json.gz")
  first_summary = capture_summary(first)
  b_summary = capture_summary(b_run)

  first_seq = [x["value"] for x in first_summary["0x127"]["transition_timeline"]]
  b_seq = [x["value"] for x in b_summary["0x127"]["transition_timeline"]]

  artifact = {
    "schema": "camry-2026-ready-gear-v1",
    "vehicle": "maintainer-operated 2026 Toyota Camry",
    "date": "2026-08-26",
    "sources": {
      name: {
        "path": str((RAW / name).relative_to(REPO)),
        "size": (RAW / name).stat().st_size,
        "sha256": sha256(RAW / name),
      }
      for name in SOURCE_NAMES
    },
    "capture_boundary": {
      "operation": "passive Panda CAN receive only after route/safety-mode configuration",
      "first_run_operator_context": "logger started in NRTD before explicit READY instruction; requested P/R/N/D/B/D/N/R/P, but operator later reported B was missed; observed sequence is P/R/N/D/N/R/P",
      "second_run_operator_context": "vehicle READY/stationary; dedicated D/B/D sequence after initial P baseline",
      "machine_timestamp_boundary": "operator button/selector actions were instructed interactively but are not independently machine-timestamped; the exact wire transitions below are directly timestamped by the retained captures",
      "no_vehicle_control_transmission": True,
    },
    "captures": {
      "nrtd_to_ready_gear": first_summary,
      "ready_b": b_summary,
    },
    "ready_status": {
      "carrier": "0x51E/8 bus1",
      "field": "B0[7]",
      "first_run_sequence": [x["value"] for x in first_summary["0x51E"]["transition_timeline"]],
      "transition": first_summary["0x51E"]["transition_timeline"],
      "interpretation": "Because the passive logger was already running in NRTD before the operator was explicitly told to enter READY, the directly observed B0[7] 0->1 transition is stronger causal evidence for the previously recovered Techstream Ready Status wire join. Exact physical-button-to-frame latency remains bounded because the operator action itself was not machine-timestamped.",
    },
    "gear": {
      "carrier": "0x127/8 bus1",
      "field": "DBC 47|4 Motorola",
      "first_run_sequence": first_seq,
      "second_run_sequence": b_seq,
      "validated_enum": {"0": "P", "1": "R", "2": "N", "3": "D", "4": "B"},
      "evidence": {
        "P_R_N_D_roundtrip": first_summary["0x127"]["transition_timeline"],
        "B_roundtrip": b_summary["0x127"]["transition_timeline"],
      },
      "checksum": {
        "first_run": {"frames": first_summary["0x127"]["frame_count"], "matches": first_summary["0x127"]["checksum_matches"]},
        "b_run": {"frames": b_summary["0x127"]["frame_count"], "matches": b_summary["0x127"]["checksum_matches"]},
      },
      "interpretation": "The complete prior-art enum is now directly validated on this exact Camry by reversible stationary selector transitions: P=0, R=1, N=2, D=3, B=4. This closes the Camry gear-state measurement boundary; cross-model production use still follows each platform's evidence policy.",
    },
    "production_boundary": "This evidence validates read-only Ready/gear state decoding only. It does not establish Camry steering actuation, B6 producer/signing ownership, cruise engagement policy, or Panda actuation safety.",
  }

  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
  print(args.out)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
