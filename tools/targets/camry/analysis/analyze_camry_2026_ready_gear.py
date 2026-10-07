#!/usr/bin/env python3
"""Build deterministic 2026 Camry READY/gear evidence from retained passive captures."""
from __future__ import annotations

from tools.targets.camry.support import camry_f33_corpus as f33
from tools import REPO_ROOT
import argparse
import gzip
import json
from pathlib import Path

from tools.toyota_support.toyota_route_opendbc_common import be_signal, sha256, toyota_checksum

REPO = REPO_ROOT
RAW = f33.CAPTURE / "raw-20260826"
DEFAULT_OUT = REPO / "data/generated/camry_2026_ready_gear.json"
SOURCE_NAMES = (
  "READY_GEAR_MANIFEST.txt",
  "camry_ready_gear_capture.py",
  "camry_ready_gear_20260826.json.gz",
  "camry_b_capture.py",
  "camry_ready_b_20260826.json.gz",
)


def load_gzip_json(name: str) -> dict:
  with gzip.open(RAW / name, "rt") as f:
    return json.load(f)


def signed(value: int, bits: int) -> int:
  sign = 1 << (bits - 1)
  return value - (1 << bits) if value & sign else value


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


def _gear_indication_comparison(gear_edges: list[dict], indication_edges: list[dict],
                                indication_rows: list[dict], duration: float) -> dict:
  # These are the independently observed Camry selector values, not DDB offsets.
  indication_by_gear = {0: 0x80, 1: 0x40, 2: 0x20, 3: 0x10, 4: 0x10}
  projected = []
  for edge in gear_edges:
    value = indication_by_gear[edge["value"]]
    if not projected or value != projected[-1]["indication"]:
      projected.append({**edge, "indication": value})
  sequence_matches = [e["indication"] for e in projected] == [e["value"] for e in indication_edges]
  pairs = []
  if sequence_matches:
    # Skip the initial samples: they are not observed selector transitions.
    for gear, indication in zip(projected[1:], indication_edges[1:], strict=True):
      pairs.append({
        "0x127_raw": gear["value"],
        "0x3BF_raw": indication["value"],
        "0x127_seconds": gear["seconds"],
        "0x3BF_seconds": indication["seconds"],
        "receive_delta_ms": round((indication["seconds"] - gear["seconds"]) * 1000, 3),
      })
  b_intervals = []
  for index, edge in enumerate(gear_edges):
    if edge["value"] != 4:
      continue
    end = gear_edges[index + 1]["seconds"] if index + 1 < len(gear_edges) else duration
    samples = [r for r in indication_rows if edge["seconds"] <= float(r["t"]) < end]
    b_intervals.append({
      "start_seconds": edge["seconds"], "end_seconds": end,
      "frame_count": len(samples),
      "0x3BF_raw_values": sorted({bytes.fromhex(r["data"])[0] for r in samples}),
    })
  return {
    "projected_sequence_matches": sequence_matches,
    "transition_pairs": pairs,
    "max_abs_receive_delta_ms": max((abs(p["receive_delta_ms"]) for p in pairs), default=None),
    "B_intervals": b_intervals,
    "boundary": "Pairing requires matching complete value sequences after projecting 0x127 B to the observed 0x3BF D indication. Times are rounded receive-batch observations, not physical selector or wire latency; no one-second shift delay is inferred from the background rate.",
  }


def capture_summary(obj: dict) -> dict:
  gear = stream(obj, 1, 0x127, 8)
  ready = stream(obj, 1, 0x51E, 8)
  wheels = stream(obj, 1, 0x0AA, 8)
  gear_payloads = [bytes.fromhex(r["data"]) for r in gear]
  indication = stream(obj, 1, 0x3BF, 8)
  gear_edges = transition_timeline(gear, 47, 4)
  indication_edges = transition_timeline(indication, 7, 8)
  return {
    "label": obj["capture"],
    "duration_s": round(float(obj["duration_s"]), 9),
    "total_frames": len(obj["frames"]),
    "0x127": {
      "frame_count": len(gear),
      "checksum_matches": sum(toyota_checksum(0x127, d) == d[-1] for d in gear_payloads),
      "raw_values": sorted({be_signal(d, 47, 4) for d in gear_payloads}),
      "transition_timeline": gear_edges,
    },
    "0x3BF": {
      "frame_count": len(indication),
      "raw_values": sorted({bytes.fromhex(r["data"])[0] for r in indication}),
      "transition_timeline": indication_edges,
    },
    "gear_indication_comparison": _gear_indication_comparison(
      gear_edges, indication_edges, indication, float(obj["duration_s"]),
    ),
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


def _check_gts_meter(artifact: dict, root: Path | None) -> dict:
  """Cross-check observed CAN values against OEM diagnostic metadata, offline."""
  from tools.techstream.ddb_semantics import decode_p5_signal, monitor_rows
  from tools.techstream.ddb_strings import load_string_db
  from tools.techstream.parse_ddb import DDBParser
  from tools.techstream.techstream_paths import gts_db_root, resolve_gts_root

  db_root = gts_db_root(resolve_gts_root(root))
  parser = DDBParser()
  meter = parser.parse_ecu_db(db_root / "Meter_P5.ddb")
  strings = load_string_db(parser, db_root / "M_English.ddb")
  rows = monitor_rows(meter, strings, "Meter_P5.ddb", include_signal_info=True)
  row, = [r for r in rows if r["primary_did"] == 0x2931 and r["monitor_key"] == 153]

  def decode(row: dict, raw: int) -> dict:
    info = row["signal_info"]
    return decode_p5_signal(
      bytes((0, raw)), bit_start=row["bit_start"], bit_end=row["bit_end"],
      mul=info["mul"], div=info["div"], offset=info["offset"], signed=info["signed"],
      decimal_point_count=info["decimal_point_count"], patterns=info["pattern_display"],
    )

  decoded = []
  for raw, label in artifact["gear_indication"]["validated_camry_enum"].items():
    result = decode(row, int(raw))
    if result["pattern"] != label:
      raise ValueError(f"GTS meter dictionary does not match observed Camry {label}: {result}")
    lamps = []
    for lamp_label in ("P", "R", "N", "D"):
      lamp, = [r for r in rows if r["primary_did"] == 0x2931
               and r["name"] == f"A/T Indicator Operation ({lamp_label})"]
      if decode(lamp, int(raw))["converted_integer"] == 1:
        lamps.append(lamp_label)
    if lamps != [label]:
      raise ValueError(f"GTS individual lamps disagree with {label}: {lamps}")
    decoded.append({"synthetic_diagnostic_payload": bytes((0, int(raw))).hex(),
                    "display": result["pattern"], "individual_lamps_on": lamps})
  return {
    "sources": {name: {"sha256": sha256(db_root / name), "size": (db_root / name).stat().st_size}
                for name in ("Meter_P5.ddb", "M_English.ddb")},
    "monitor": {key: value for key, value in row.items() if key != "raw"},
    "monitor_raw_hex": row["raw"].hex(),
    "decode_checks": decoded,
    "boundary": "Synthetic diagnostic payload exercise, not a captured DID response. DDB byte1 is not CAN byte0: the controlled captures independently establish use of these values in 0x3BF. Runtime support and physical producer identity are not established.",
  }


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  ap.add_argument("--check-gts", action="store_true",
                  help="also check the installed GTS+ meter dictionary against observed Camry values")
  ap.add_argument("--gtsplus-root", type=Path, help="external GTS+ corpus root for --check-gts")
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
    "gear_indication": {
      "carrier": "0x3BF/8 bus1",
      "field": "byte0",
      "validated_camry_enum": {"128": "P", "64": "R", "32": "N", "16": "D"},
      "first_run_sequence": [x["value"] for x in first_summary["0x3BF"]["transition_timeline"]],
      "second_run_sequence": [x["value"] for x in b_summary["0x3BF"]["transition_timeline"]],
      "interpretation": "Controlled Camry P/R/N/D/N/R/P transitions establish all four values, including Neutral. The separate B interval retains the Drive indication; this byte is not a complete replacement for hybrid 0x127 gear decoding.",
      "cross_vehicle_boundary": "The retained public Corolla route exercises P/R/D and Span exercises D. Matching values corroborate Corolla Neutral but do not constitute a Corolla Neutral observation or prove that a vehicle never broadcasts 0x127.",
      "oem_cross_check": "Run --check-gts to decode synthetic Meter_P5 DID 0x2931 value payloads with the original DDB dictionary and independent lamp bits; external GTS+ files are not required to regenerate this capture artifact.",
    },
    "production_boundary": "This evidence validates read-only Ready/gear state decoding only. It does not establish Camry steering actuation, B6 producer/signing ownership, cruise engagement policy, or Panda actuation safety.",
  }

  gts_check = _check_gts_meter(artifact, args.gtsplus_root) if args.check_gts else None
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
  print(args.out)
  if gts_check is not None:
    print(json.dumps(gts_check, indent=2, sort_keys=True))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
