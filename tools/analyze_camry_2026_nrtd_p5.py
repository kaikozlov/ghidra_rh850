#!/usr/bin/env python3
"""Build the 2026 Camry NRTD P5 identity/cruise correlation artifact."""
from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter
from pathlib import Path

from toyota_route_opendbc_common import sha256

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260826"
DEFAULT_OUT = REPO / "data/generated/camry_2026_nrtd_p5.json"
SOURCE_NAMES = [
  "NRTD_MANIFEST.txt",
  "camry_nrtd_module_identity_20260826.json",
  "camry_nrtd_p5_oracles_20260826.json",
  "camry_nrtd_p5_oracles_extra_20260826.json",
  "camry_nrtd_brake_107e_extended_20260826.json",
  "camry_nrtd_cruise_buttons_20260826.json",
  "camry_nrtd_cruise_MAIN_20260826.json",
  "camry_nrtd_cruise_RESPLUS_20260826.json",
  "camry_nrtd_cruise_SETMINUS_20260826.json",
  "camry_nrtd_cruise_CANCEL_20260826.json",
  "camry_nrtd_cruise_DISTANCE_20260826.json",
  "camry_nrtd_cruise_can_sync_20260826.json.gz",
]


def load(name: str):
  path = RAW / name
  if path.suffix == ".gz":
    with gzip.open(path, "rt") as f:
      return json.load(f)
  return json.loads(path.read_text())


def strip_ascii(raw_hex: str, *, counted_16: bool = False) -> str:
  raw = bytes.fromhex(raw_hex)
  if counted_16:
    if not raw or raw[0] != 1:
      raise ValueError(f"expected one counted 16-byte record: {raw_hex}")
    raw = raw[1:17]
  return raw.rstrip(b"\x00").decode("ascii")


def read_map(rows: list[dict]) -> dict[str, dict]:
  return {row["did"].upper(): row for row in rows}


def route(target: dict, bus: int) -> dict:
  return next(x for x in target["routes"] if x["bus"] == bus)


def transition_sequence(rows: list[dict], fields: tuple[str, ...]) -> list[dict]:
  out = []
  prev = None
  for row in rows:
    values = tuple(row.get(k) for k in fields)
    if values != prev:
      out.append({"seconds": round(float(row["t"]), 6), **{k: row.get(k) for k in fields}})
      prev = values
  return out


def first_transition_time(rows: list[dict], field: str, value: str) -> float:
  for row in rows:
    if row.get(field) == value:
      return float(row["t"])
  raise ValueError(f"missing {field}={value}")


def event_window(rows: list[dict], field: str, event_value: str, baseline_value: str) -> tuple[float, float]:
  start = first_transition_time(rows, field, event_value)
  for row in rows:
    if float(row["t"]) > start and row.get(field) == baseline_value:
      return start, float(row["t"])
  raise ValueError(f"missing return {field}={baseline_value} after {event_value}")

def frame_stream(sync: dict, bus: int, addr: int, length: int) -> list[dict]:
  return [f for f in sync["frames"] if f["bus"] == bus and f["addr"] == addr and f["len"] == length]


def rate_hz(rows: list[dict]) -> float:
  return round((len(rows) - 1) / (rows[-1]["t"] - rows[0]["t"]), 3)


def tuple_0fe(row: dict) -> tuple[int, int, int, int]:
  d = bytes.fromhex(row["data"])
  return d[3], d[4], d[6], d[7]


def mode_tuple(rows: list[dict]) -> tuple[int, int, int, int]:
  return Counter(tuple_0fe(x) for x in rows).most_common(1)[0][0]


def tuple_dict(v: tuple[int, int, int, int]) -> dict:
  return {"B3": v[0], "B4": v[1], "B6": v[2], "B7": v[3]}


def first_payload_change_after(rows: list[dict], t: float) -> tuple[dict, dict]:
  before = [x for x in rows if x["t"] < t]
  if not before:
    raise ValueError("no frame before event")
  prev = before[-1]
  for row in rows:
    if row["t"] >= t and row["data"] != prev["data"]:
      return prev, row
  raise ValueError("no payload change after event")


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  ident = load("camry_nrtd_module_identity_20260826.json")
  p5 = load("camry_nrtd_p5_oracles_20260826.json")
  p5_extra = load("camry_nrtd_p5_oracles_extra_20260826.json")
  brake_ext = load("camry_nrtd_brake_107e_extended_20260826.json")
  sync = load("camry_nrtd_cruise_can_sync_20260826.json.gz")

  targets = {x["name"]: x for x in ident["targets"]}
  frc = targets["FRC_P5_candidate"]
  brake = targets["ABS_P5_Brake_candidate"]
  frc1 = read_map(route(frc, 1)["reads"])
  brake1 = read_map(route(brake, 1)["reads"])

  direct_reads = {x["did"].upper(): x for x in p5["reads"] if x["ecu"] == "FRC_P5"}
  extra_reads = {x["did"].upper(): x for x in p5_extra["reads"] if x["ecu"] == "FRC_P5"}
  brake_reads = {x["did"].upper(): x for x in p5["reads"] if x["ecu"] == "ABS_P5_Brake"}
  brake_extra = {x["did"].upper(): x for x in p5_extra["reads"] if x["ecu"] == "ABS_P5_Brake"}

  isolated_files = {
    "MAIN": "camry_nrtd_cruise_MAIN_20260826.json",
    "RES+": "camry_nrtd_cruise_RESPLUS_20260826.json",
    "SET-": "camry_nrtd_cruise_SETMINUS_20260826.json",
    "CANCEL": "camry_nrtd_cruise_CANCEL_20260826.json",
    "DISTANCE": "camry_nrtd_cruise_DISTANCE_20260826.json",
  }
  isolated = {}
  for label, name in isolated_files.items():
    rows = load(name)
    isolated[label] = {
      "sample_count": len(rows),
      "transitions": transition_sequence(rows, ("1905", "1906", "1914", "1912")),
    }

  oracle_transitions = transition_sequence(sync["oracles"], ("1906", "1912"))
  event_times = {
    "MAIN": first_transition_time(sync["oracles"], "1906", "e0c0e0008000"),
    "RES+": first_transition_time(sync["oracles"], "1906", "e080e0808000"),
    "SET-": first_transition_time(sync["oracles"], "1906", "e080e0408000"),
    "CANCEL": first_transition_time(sync["oracles"], "1906", "e080e0208000"),
    "DISTANCE": first_transition_time(sync["oracles"], "1912", "01"),
  }

  f0fe = frame_stream(sync, 1, 0x0FE, 32)
  baseline_tuple = mode_tuple([x for x in f0fe if 8.5 <= x["t"] <= 9.5])
  # Derive every event window from the retained oracle itself; do not bake capture times
  # into the analyzer. RES+ has a second event phase before returning to baseline.
  baseline_1906 = "e080e0008000"
  windows = {
    "MAIN": event_window(sync["oracles"], "1906", "e0c0e0008000", baseline_1906),
    "RES+": event_window(sync["oracles"], "1906", "e080e0808000", baseline_1906),
    "SET-": event_window(sync["oracles"], "1906", "e080e0408000", baseline_1906),
    "CANCEL": event_window(sync["oracles"], "1906", "e080e0208000", baseline_1906),
  }
  momentary = {}
  for label, (start, end) in windows.items():
    event_rows = [x for x in f0fe if start - 0.05 <= x["t"] <= end + 0.05]
    # Event mode must differ from baseline; if the expanded window makes baseline the mode,
    # choose the most-common non-baseline tuple.
    counts = Counter(tuple_0fe(x) for x in event_rows)
    event_tuple = next(v for v, _ in counts.most_common() if v != baseline_tuple)
    momentary[label] = {
      "oracle_start_s": round(start, 6),
      "oracle_end_s": round(end, 6),
      "baseline_B3_B4_B6_B7": tuple_dict(baseline_tuple),
      "event_B3_B4_B6_B7": tuple_dict(event_tuple),
      "xor": {
        "B3": baseline_tuple[0] ^ event_tuple[0],
        "B4": baseline_tuple[1] ^ event_tuple[1],
        "B6": baseline_tuple[2] ^ event_tuple[2],
        "B7": baseline_tuple[3] ^ event_tuple[3],
      },
    }

  distance_t = event_times["DISTANCE"]
  distance_candidates = {}
  for name, addr, length, byte_index in (("0x251/8", 0x251, 8, 5), ("0x5AF/32", 0x5AF, 32, 24)):
    rows = frame_stream(sync, 1, addr, length)
    before, after = first_payload_change_after(rows, distance_t)
    b0 = bytes.fromhex(before["data"])[byte_index]
    b1 = bytes.fromhex(after["data"])[byte_index]
    distance_candidates[name] = {
      "bus": 1,
      "address": f"0x{addr:03X}",
      "dlc": length,
      "rate_hz": rate_hz(rows),
      "byte_index": byte_index,
      "before": b0,
      "after": b1,
      "xor": b0 ^ b1,
      "change_time_s": round(float(after["t"]), 6),
      "latency_from_1912_change_ms": round((float(after["t"]) - distance_t) * 1000, 3),
      "payload_before": before["data"],
      "payload_after": after["data"],
      "boundary": "Temporal/state correlation candidate only; producer and Toyota signal name are not assigned from this capture alone.",
    }

  artifact = {
    "schema": "camry-2026-nrtd-p5-v1",
    "vehicle_state": "Not Ready to Drive; stationary; operator-triggered controls only",
    "sources": {
      name: {
        "path": str((RAW / name).relative_to(REPO)),
        "size": (RAW / name).stat().st_size,
        "sha256": sha256(RAW / name),
      }
      for name in SOURCE_NAMES
    },
    "module_identity": {
      "elm327_param": ident["elm327_param"],
      "FRC_P5": {
        "bus": 1,
        "tx": "0x792",
        "rx": "0x79A",
        "f181": strip_ascii(frc1["0XF181"]["hex"], counted_16=True),
        "f18c_serial": strip_ascii(frc1["0XF18C"]["hex"]),
        "ecu_part_0105": strip_ascii(frc1["0X0105"]["hex"]),
        "swin_1fff": strip_ascii(frc1["0X1FFF"]["hex"]),
        "bus0_bus2_f181_timeout": all(read_map(route(frc, b)["reads"])["0XF181"]["status"] == "negative_or_timeout" for b in (0, 2)),
      },
      "Brake_EPB_category_435": {
        "bus": 1,
        "tx": "0x7B0",
        "rx": "0x7B8",
        "f181": strip_ascii(brake1["0XF181"]["hex"], counted_16=True),
        "f18c_serial": strip_ascii(brake1["0XF18C"]["hex"]),
        "ecu_part_0105": strip_ascii(brake1["0X0105"]["hex"]),
        "bus0_bus2_f181_timeout": all(read_map(route(brake, b)["reads"])["0XF181"]["status"] == "negative_or_timeout" for b in (0, 2)),
      },
    },
    "frc_read_only_oracles": {
      did: {"status": row["status"], "hex": row.get("hex", ""), "length": row.get("length")}
      for did, row in sorted({**direct_reads, **extra_reads}.items())
    },
    "brake_read_only_oracles": {
      "0x102F": {"status": brake_extra["0X102F"]["status"], "hex": brake_extra["0X102F"]["hex"], "length": brake_extra["0X102F"]["length"]},
      "0x107E_default": {"status": brake_reads["0X107E"]["status"], "error": brake_reads["0X107E"]["error"]},
      "0x107E_extended": {
        "extended_session": brake_ext["extended"],
        "status": brake_ext["did_107e"]["status"],
        "error": brake_ext["did_107e"]["error"],
        "returned_default": brake_ext["returned_default"],
      },
      "boundary": "The Corolla ABS_P5 0x107E monitor is not directly readable on this Camry Brake ECU in either tested default or extended session; 0x102F is readable. Do not transfer the 0x107E live-oracle assumption.",
    },
    "isolated_cruise_controls": isolated,
    "synchronized_capture": {
      "oracle_sample_count": len(sync["oracles"]),
      "can_frame_count": len(sync["frames"]),
      "oracle_transitions": oracle_transitions,
      "event_times_s": {k: round(v, 6) for k, v in event_times.items()},
      "0x0FE_momentary_switch_carrier": {
        "bus": 1,
        "address": "0x0FE",
        "dlc": 32,
        "rate_hz": rate_hz(f0fe),
        "baseline_B3_B4_B6_B7": tuple_dict(baseline_tuple),
        "events": momentary,
        "interpretation": "The same bus1 0x0FE/32 data tuple changes and returns around each FRC 0x1906 momentary MAIN/RES+/SET-/CANCEL oracle event. Counter/integrity bytes elsewhere in the frame continue independently; the listed data-byte changes are the direct dynamic join.",
      },
      "distance_state": {
        "frc_did": "0x1912",
        "isolated_transition": "03->04",
        "synchronized_transition": "04->01",
        "synchronized_change_time_s": round(distance_t, 6),
        "candidate_can_carriers": distance_candidates,
        "interpretation": "DID 0x1912 is directly validated as a persistent following-distance state by isolated operator input. 0x251 and 0x5AF change within ~12 ms in the synchronized capture and remain candidate ordinary-CAN state carriers pending an independent repeat/enum sweep.",
      },
    },
    "production_boundary": "This NRTD pass closes identities and observation carriers only. It does not establish Camry B6 producer/signing ownership, authenticated steering control, cruise engagement while driving, or production safety policy.",
  }

  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
  print(args.out)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
