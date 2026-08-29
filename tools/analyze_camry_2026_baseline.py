#!/usr/bin/env python3
"""Build the compact 2026 Camry TSK/CAN baseline from tracked field evidence."""
from __future__ import annotations

import argparse
import gzip
import json
from collections import defaultdict
from pathlib import Path

from toyota_route_opendbc_common import be_signal, sha256, toyota_checksum

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260826"
DEFAULT_OUT = REPO / "data/generated/camry_2026_tsk_baseline.json"
BASELINE_SOURCE_NAMES = ("MANIFEST.txt", "can_oracle.ndjson.gz", "identity.json", "programming_probe.json", "xcp_probe.json")


def load_json(name: str) -> dict:
  return json.loads((RAW / name).read_text())


def parse_f181(raw_hex: str) -> list[str]:
  raw = bytes.fromhex(raw_hex)
  count = raw[0]
  body = raw[1:]
  records = []
  for i in range(count):
    record = body[i * 16:(i + 1) * 16].rstrip(b"\x00")
    records.append(record.decode("ascii"))
  return records


def stat(values: list[float | int]) -> dict:
  return {
    "count": len(values),
    "min": min(values),
    "max": max(values),
    "unique_count": len(set(values)),
  }


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  identity = load_json("identity.json")
  programming = load_json("programming_probe.json")
  xcp = load_json("xcp_probe.json")
  can_path = RAW / "can_oracle.ndjson.gz"

  rows: list[dict] = []
  run_start: dict | None = None
  with gzip.open(can_path, "rt") as f:
    for line in f:
      row = json.loads(line)
      if row.get("event") == "run_start":
        run_start = row
      elif row.get("event") == "can":
        rows.append(row)
  if run_start is None or not rows:
    raise RuntimeError("tracked CAN oracle is missing run_start/CAN rows")

  streams: dict[tuple[int, int, int], list[dict]] = defaultdict(list)
  for row in rows:
    streams[(row["bus"], row["addr"], row["len"])].append(row)

  def stream(bus: int, addr: int, length: int) -> list[dict]:
    return streams.get((bus, addr, length), [])

  def rate_hz(rs: list[dict]) -> float | None:
    if len(rs) < 2:
      return None
    dt = (rs[-1]["t_mono_ns"] - rs[0]["t_mono_ns"]) / 1e9
    return round((len(rs) - 1) / dt, 3) if dt > 0 else None

  selected_ids = [
    (1, 0x00F, 8), (1, 0x025, 32), (1, 0x030, 32), (1, 0x090, 32),
    (1, 0x0AA, 8), (1, 0x0B6, 32), (1, 0x0D7, 32), (1, 0x101, 8),
    (1, 0x116, 8), (1, 0x127, 8), (1, 0x176, 8), (1, 0x24D, 8),
    (1, 0x351, 4), (1, 0x394, 3), (1, 0x4A3, 8), (1, 0x4C8, 8),
    (1, 0x51E, 8),
  ]
  selected = {}
  for bus, addr, length in selected_ids:
    rs = stream(bus, addr, length)
    selected[f"0x{addr:03X}/{length}"] = {
      "bus": bus,
      "count": len(rs),
      "rate_hz": rate_hz(rs),
      "unique_payloads": len({r["data"] for r in rs}),
    }

  # H/F-derived 0x030 field family, decoded directly from the tracked wire bytes.
  f030 = stream(1, 0x030, 32)
  payload030 = [bytes.fromhex(r["data"]) for r in f030]
  additive_matches = sum(((sum(d[:7]) + 0x38) & 0xFF) == d[7] for d in payload030)
  torque = [be_signal(d, 71, 8, is_signed=True) * 0.1 + be_signal(d, 139, 4, is_signed=True) * 0.01 for d in payload030]
  torque_trunc = [be_signal(d, 7, 8, is_signed=True) * 0.1 for d in payload030]
  status_bits = {f"b6_bit{i}": sorted({(d[6] >> i) & 1 for d in payload030}) for i in range(4)}
  bit_transitions = {}
  for bit in range(4):
    prev = None
    events = []
    for row, d in zip(f030, payload030):
      value = (d[6] >> bit) & 1
      if value != prev:
        events.append({"seconds": round(row["ts_ms"] / 1000, 6), "value": value})
        prev = value
    bit_transitions[f"b6_bit{bit}"] = events

  # H/F-derived 0x025 steering-sensor layout.
  f025 = [bytes.fromhex(r["data"]) for r in stream(1, 0x025, 32)]
  angle = [be_signal(d, 3, 12, is_signed=True) * 1.5 for d in f025]
  fraction = [be_signal(d, 39, 4, is_signed=True) * 0.1 for d in f025]
  steering_rate = [be_signal(d, 35, 12, is_signed=True) for d in f025]

  # Legacy Toyota checksum/carrier reuse candidates.
  checksum_contracts = {}
  for addr in (0x101, 0x127, 0x176):
    rs = stream(1, addr, 8)
    ds = [bytes.fromhex(r["data"]) for r in rs]
    checksum_contracts[f"0x{addr:03X}"] = {
      "frames": len(ds),
      "checksum_matches": sum(toyota_checksum(addr, d) == d[-1] for d in ds),
    }

  gear_frames = [bytes.fromhex(r["data"]) for r in stream(1, 0x127, 8)]
  gear_raw = sorted({be_signal(d, 47, 4) for d in gear_frames})
  ready_rows = stream(1, 0x51E, 8)
  ready_events = []
  last_ready: tuple[int, str] | None = None
  for row in ready_rows:
    d = bytes.fromhex(row["data"])
    value = be_signal(d, 7, 1)
    state = (value, d.hex())
    if state != last_ready:
      ready_events.append({"seconds": round(row["ts_ms"] / 1000, 6), "value": value, "payload": d.hex()})
      last_ready = state

  # Bus 0/2 TSS3 FD topology comparison.
  bus0_keys = {(addr, length) for bus, addr, length in streams if bus == 0}
  bus2_keys = {(addr, length) for bus, addr, length in streams if bus == 2}
  unequal_sequences = []
  for addr, length in sorted(bus0_keys & bus2_keys):
    seq0 = [r["data"] for r in stream(0, addr, length)]
    seq2 = [r["data"] for r in stream(2, addr, length)]
    if seq0 != seq2:
      unequal_sequences.append(f"0x{addr:03X}/{length}")

  app_row = next(r for r in identity["identity"] if r["name"] == "app_sw_id")
  serial_row = next(r for r in identity["identity"] if r["name"] == "ecu_serial")
  app_records = parse_f181(app_row["hex"])
  boot_raw = programming["bootloader_f181"]["hex"]

  artifact = {
    "schema": "camry-2026-tsk-baseline-v1",
    "vehicle_attribution": {
      "vehicle": "2026 Toyota Camry",
      "source": "maintainer-operated vehicle session",
      "date": "2026-08-26",
      "boundary": "Vehicle/model attribution is operator context; F181, route, CAN, programming, and XCP facts below are direct tracked observations.",
    },
    "sources": {
      name: {
        "path": str((RAW / name).relative_to(REPO)),
        "size": (RAW / name).stat().st_size,
        "sha256": sha256(RAW / name),
      }
      for name in BASELINE_SOURCE_NAMES
    },
    "identity": {
      "f181_records": app_records,
      "primary_software_id": app_records[0],
      "secondary_software_id": app_records[1],
      "ecu_serial": bytes.fromhex(serial_row["hex"]).decode("ascii"),
      "route": identity["route"],
      "services_answering_probe": [r["name"] for r in identity["services"] if r["supported"]],
      "exact_f181_known_in_prior_repo_corpus": False,
    },
    "programming": {
      "status": programming["status"],
      "handoff_switched": programming["did_it_take"]["switched"],
      "programming_response_timeout": programming["did_it_take"]["response_timeout"],
      "route_preserved": programming["programming_handoff"]["route_before"] == programming["programming_handoff"]["route_after"],
      "bootloader_f181_hex": boot_raw,
      "bootloader_f181_is_two_bang_placeholders": bytes.fromhex(boot_raw) == b"\x02" + b"!" * 32,
      "functional_0x777": programming["functional_0x777"],
      "boundary": "PROGRAMMING handoff and bootloader-family behavior are observed. Boot SecurityAccess, RequestDownload, 0x10F0, RAM-exec geometry, and ciphertext portability were not established and must not be inferred from H/F or Sienna.",
    },
    "xcp": {
      "status": xcp["status"],
      "request_id": xcp["xcp_request_id"],
      "response_id": xcp["xcp_response_id"],
      "connect_response": xcp["connect_response"],
      "message": xcp["message"],
      "boundary": "No usable 0x7F8 CONNECT response was observed on the tested EPS normal-harness route; this is a route/session observation, not a universal physical absence proof.",
    },
    "can_capture": {
      "run_id": run_start["run_id"],
      "start_utc": run_start["time_utc"],
      "duration_s": round((max(r["t_mono_ns"] for r in rows) - min(r["t_mono_ns"] for r in rows)) / 1e9, 6),
      "total_can_rows": len(rows),
      "stream_count_by_bus": {str(bus): sum(1 for k in streams if k[0] == bus) for bus in (0, 1, 2)},
      "selected_streams": selected,
      "b6_absent_in_stationary_ready_segment": selected["0x0B6/32"]["count"] == 0,
      "b6_absence_boundary": "This early stationary READY segment did not exercise an LTA off->active->off transition, so its zero-B6 count is only a segment-level fact. Later relay-correct captures machine-identify 73.303384 s of LTA/LCA with zero B6 and exact F33 proves a B6-independent internal assist path; do not use this early artifact to resurrect a stock-B6 prerequisite.",
      "bus0_bus2_same_id_dlc_set": bus0_keys == bus2_keys,
      "bus0_bus2_stream_count": len(bus0_keys),
      "bus0_bus2_payload_sequence_unequal": unequal_sequences,
    },
    "hf_transfer_observations": {
      "classification": "strong wire-format transfer evidence; exact Camry firmware semantics remain unproved without CodeFlash",
      "0x025": {
        "frame_count": len(f025),
        "steering_angle_deg": stat(angle),
        "steering_fraction_deg": stat(fraction),
        "steering_rate_raw_or_prior_art_deg_s": stat(steering_rate),
        "boundary": "Bit layout/scale is the existing H/F-derived TSS3 DBC interpretation and decodes coherently on this stationary Camry segment; Camry firmware-static confirmation remains open.",
      },
      "0x030": {
        "frame_count": len(payload030),
        "additive_rule": "B7 = low8(sum(B0..B6) + 0x38)",
        "additive_rule_matches": additive_matches,
        "steering_wheel_torque_nm": stat(torque),
        "steering_wheel_torque_trunc_nm": stat(torque_trunc),
        "b6_status_values": status_bits,
        "b6_status_transitions": bit_transitions,
        "boundary": "The exact H/F additive rule transfers perfectly and the H/F torque encoding is physically plausible/dynamic. B6 status meanings remain H/F-derived candidates until Camry firmware or independent diagnostics join them.",
      },
      "legacy_checksum_carriers": checksum_contracts,
      "0x127": {
        "frame_count": len(gear_frames),
        "gear_raw_values": gear_raw,
        "prior_art_candidate_decode": {"0": "P", "1": "R", "2": "N", "3": "D", "4": "B"},
        "interpretation": "Raw 0 is directly observed while the vehicle is stationary in the operator-described READY baseline and is prior-art-compatible with P. P/R/N/D/B transition validation remains required before production use.",
      },
      "0x51E": {
        "frame_count": len(ready_rows),
        "ready_values": sorted({be_signal(bytes.fromhex(r["data"]), 7, 1) for r in ready_rows}),
        "transition_timeline": ready_events,
        "interpretation": "B0[7] transitions 0->1 during the captured READY startup, strongly corroborating the H/F + Techstream Ready Status wire join on this Camry family. Exact causal timing relative to the vehicle's physical READY action is not independently recorded.",
      },
    },
    "next_evidence": [
      "Read the Camry Brake/EPB and FRC software identities through their target diagnostic routes before assuming Corolla producer ownership/addressing transfers.",
      "Use the later relay-correct LTA/LCA captures and exact F33 control graph to identify which external/local state selects or modulates the B6-independent D0218/CC60/CC50 assist path; independently identify 0x08A producer/SecOC ownership without assuming translation into B6.",
      "Capture stationary P/R/N/D transitions to validate 0x127 enums on this target; B remains optional if the vehicle/trim exposes it.",
      "Synchronize cruise main/engage/cancel with target-native diagnostic oracles rather than promoting inactive 0x176 fields by prior art.",
      "Acquire exact 8965F3307000 CodeFlash before transferring H/F boot-RAM, SecOC receiver, steering-limit, command-5 carrier, or safety conclusions as firmware facts.",
    ],
  }

  # Add explicit absent steering IDs without making selected_stream lookup awkward.
  artifact["can_capture"]["legacy_steering_counts"] = {
    "0x131/8": len(stream(1, 0x131, 8)),
    "0x2E4/8": len(stream(1, 0x2E4, 8)),
  }
  artifact["can_capture"]["legacy_steering_commands_absent"] = all(v == 0 for v in artifact["can_capture"]["legacy_steering_counts"].values())

  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
  print(args.out)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
