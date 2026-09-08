#!/usr/bin/env python3
"""Reconcile exact-F33 B6 SecOC freshness semantics with the complete Camry rlog corpus.

The reducer treats exact 8965F3307000 receiver behavior as the authority and uses
rlogs only to characterize what native protected 0x0D7 and comma B6 actually put
on the wire.  It does not infer receiver acceptance from a Panda TX echo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_LOG_ROOT = Path("/Users/kai/dev/inspect/logs/camry-2026")
DEFAULT_OPENPILOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
DEFAULT_OUT = Path(__file__).resolve().parents[1] / "data/generated/camry_b6_freshness_contract.json"


def load_logreader(openpilot_root: Path):
  sys.path.insert(0, str(openpilot_root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
      h.update(chunk)
  return h.hexdigest()


def decode_sync(dat: bytes) -> tuple[int, int]:
  return int.from_bytes(dat[0:2], "big"), (dat[2] << 12) | (dat[3] << 4) | (dat[4] >> 4)


def decode_fv4(dat: bytes) -> tuple[int, int]:
  return dat[28] >> 6, (dat[28] >> 4) & 0x3


def epoch_newer(a: tuple[int, int], b: tuple[int, int]) -> bool:
  """Ordinary non-wrap ordering used by this road corpus (no trip/reset wrap occurs)."""
  return a > b


def reconstruct_reset_candidate(current_reset: int, received_low2: int) -> tuple[int | None, int | None]:
  """Exact F33 0x909CA candidate order, excluding the 20-bit wrap corner absent from these logs."""
  for offset in (0, -1, 1, -2, 2):
    candidate = current_reset + offset
    if 0 <= candidate < (1 << 20) and (candidate & 0x3) == received_low2:
      return candidate, offset
  return None, None


def reconstruct_same_epoch_message(committed: int, received_low2: int) -> int | None:
  candidate = (committed & ~0x3) | received_low2
  if candidate <= committed:
    candidate += 4
  return candidate if candidate <= 0xFF else None


@dataclass
class SimState:
  epoch: tuple[int, int] = (0, 0)
  message: int = 0
  initialized: bool = False

  def accept(self, epoch: tuple[int, int], message_low2: int) -> tuple[bool, str, int | None]:
    """Model the normal F33 ordinary-freshness path once reset reconstruction chose `epoch`.

    This intentionally models only the no-wrap road domain.  Exact 0x90A48 behavior
    is: newer epoch seeds message8 directly from the received low bits; same epoch
    reconstructs the next strictly-forward congruent message; older/stale epoch
    returns retry/failure upstream.
    """
    if not self.initialized:
      # EPS SecOC init zeros the ordinary slots.  All observed road epochs are newer
      # than (0,0), so keep the real initialized values rather than inventing a
      # first-frame special case.
      self.initialized = True
    if epoch_newer(epoch, self.epoch):
      self.epoch = epoch
      self.message = message_low2
      return True, "newer_epoch_seed_from_wire_low2", self.message
    if epoch == self.epoch:
      candidate = reconstruct_same_epoch_message(self.message, message_low2)
      if candidate is None:
        return False, "same_epoch_message8_overflow", None
      self.message = candidate
      return True, "same_epoch_strict_forward", candidate
    return False, "older_epoch", None


def discover_routes(root: Path) -> list[tuple[Path, list[tuple[int, Path]]]]:
  grouped: dict[Path, list[tuple[int, Path]]] = defaultdict(list)
  for p in root.rglob("*.zst"):
    if "rlog" not in p.name: continue
    if p.name == "rlog.zst":
      try:
        seg = int(p.parent.name.rsplit("--", 1)[1])
      except (IndexError, ValueError):
        continue
      route = p.parent.parent
    elif p.name.startswith("rlog-"):
      try:
        seg = int(p.stem.split("-", 1)[1])
      except (IndexError, ValueError):
        continue
      route = p.parent
    elif p.name.endswith(".rlog.zst"):
      try:
        seg = int(p.name.removesuffix(".rlog.zst").rsplit("--", 1)[1])
      except (IndexError, ValueError):
        continue
      route = p.parent
    else:
      continue
    if "--" not in route.name:
      continue
    grouped[route].append((seg, p))
  return [(route, sorted(files)) for route, files in sorted(grouped.items())]


def counter_json(c: Counter[int] | Counter[str]) -> dict[str, int]:
  return {str(k): int(v) for k, v in sorted(c.items(), key=lambda x: str(x[0]))}


def scan_route(LogReader, route: Path, segments: list[tuple[int, Path]]) -> dict[str, Any]:
  latest_sync: dict[int, tuple[int, int, int]] = {}
  last_d7: dict[int, tuple[tuple[int, int], int, int]] = {}
  last_d7_epoch: dict[int, tuple[int, int]] = {}
  last_b6: dict[int, tuple[tuple[int, int], int, int]] = {}
  last_b6_epoch: dict[int, tuple[int, int]] = {}
  b6_sim: dict[int, SimState] = defaultdict(SimState)

  sync_counts: Counter[int] = Counter()
  d7_counts: Counter[int] = Counter()
  native_b6_counts: Counter[int] = Counter()
  incoming_b6_payloads: dict[int, Counter[bytes]] = defaultdict(Counter)
  send_b6_payloads: dict[int, set[bytes]] = defaultdict(set)
  d7_reset_match: Counter[int] = Counter()
  d7_reset_candidate_found: Counter[int] = Counter()
  d7_reset_candidate_offsets: dict[int, Counter[int]] = defaultdict(Counter)
  d7_mapped: Counter[int] = Counter()
  d7_first_low2: dict[int, Counter[int]] = defaultdict(Counter)
  d7_same_epoch_delta: dict[int, Counter[int]] = defaultdict(Counter)
  d7_same_epoch_pairs: Counter[int] = Counter()
  d7_epoch_count: Counter[int] = Counter()
  sync_epoch_changes: Counter[int] = Counter()
  sync_reset_deltas: dict[int, Counter[int]] = defaultdict(Counter)
  sync_trip_changes: Counter[int] = Counter()
  first_sync: dict[int, tuple[int, int]] = {}
  last_sync_value: dict[int, tuple[int, int]] = {}

  send_b6_counts: Counter[int] = Counter()
  send_b6_mapped: Counter[int] = Counter()
  send_b6_reset_match: Counter[int] = Counter()
  send_b6_reset_candidate_found: Counter[int] = Counter()
  send_b6_reset_candidate_offsets: dict[int, Counter[int]] = defaultdict(Counter)
  send_b6_first_low2: dict[int, Counter[int]] = defaultdict(Counter)
  send_b6_same_epoch_delta: dict[int, Counter[int]] = defaultdict(Counter)
  send_b6_same_epoch_pairs: Counter[int] = Counter()
  send_b6_sim_accept: Counter[int] = Counter()
  send_b6_sim_reasons: dict[int, Counter[str]] = defaultdict(Counter)
  send_b6_sim_unmapped: Counter[int] = Counter()
  send_b6_max_gap_ns: Counter[int] = Counter()
  send_b6_zero_mac28: Counter[int] = Counter()
  tx_b6_echo_counts: Counter[int] = Counter()
  tx_b6_reject_counts: Counter[int] = Counter()
  tx_b6_echo_mapped: Counter[int] = Counter()
  tx_b6_echo_reset_offsets: dict[int, Counter[int]] = defaultdict(Counter)
  tx_b6_echo_same_epoch_delta: dict[int, Counter[int]] = defaultdict(Counter)
  tx_b6_echo_same_epoch_pairs: Counter[int] = Counter()
  tx_b6_echo_model_accept: Counter[int] = Counter()
  tx_b6_echo_model_reasons: dict[int, Counter[str]] = defaultdict(Counter)
  tx_b6_echo_last: dict[int, tuple[tuple[int, int], int, int]] = {}
  tx_b6_echo_sim: dict[int, SimState] = defaultdict(SimState)
  init_data: dict[str, Any] = {}

  inventory = []
  for segment, path in segments:
    inventory.append({"segment": segment, "bytes": path.stat().st_size, "sha256": sha256(path)})
    for e in LogReader(str(path), sort_by_time=True, only_union_types=True):
      t = int(e.logMonoTime)
      which = e.which()
      if which == "initData" and not init_data:
        x = e.initData
        init_data = {
          "gitCommit": str(x.gitCommit), "gitBranch": str(x.gitBranch),
          "dirty": bool(x.dirty), "version": str(x.version),
        }
      elif which == "can":
        for fr in e.can:
          src = int(fr.src)
          addr, dat = int(fr.address), bytes(fr.dat)
          if addr == 0x0B6 and len(dat) == 32 and 128 <= src < 131:
            bus = src - 128
            tx_b6_echo_counts[bus] += 1
            sync = latest_sync.get(bus)
            if sync is not None:
              mlow, rlow = decode_fv4(dat)
              reconstructed_reset, reset_offset = reconstruct_reset_candidate(sync[1], rlow)
              if reconstructed_reset is not None:
                epoch = (sync[0], reconstructed_reset)
                tx_b6_echo_mapped[bus] += 1
                tx_b6_echo_reset_offsets[bus][int(reset_offset)] += 1
                prev = tx_b6_echo_last.get(bus)
                if prev is not None and prev[0] == epoch:
                  tx_b6_echo_same_epoch_pairs[bus] += 1
                  tx_b6_echo_same_epoch_delta[bus][(mlow - prev[1]) & 3] += 1
                tx_b6_echo_last[bus] = (epoch, mlow, t)
                accepted, reason, _ = tx_b6_echo_sim[bus].accept(epoch, mlow)
                tx_b6_echo_model_accept[bus] += int(accepted)
                tx_b6_echo_model_reasons[bus][reason] += 1
            continue
          if addr == 0x0B6 and len(dat) == 32 and 192 <= src < 195:
            tx_b6_reject_counts[src - 192] += 1
            continue
          if src not in (0, 1, 2):
            continue
          if addr == 0x00F and len(dat) == 8:
            trip, reset = decode_sync(dat)
            sync_counts[src] += 1
            first_sync.setdefault(src, (trip, reset))
            last_sync_value[src] = (trip, reset)
            prev = latest_sync.get(src)
            if prev is not None and (trip, reset) != (prev[0], prev[1]):
              sync_epoch_changes[src] += 1
              if trip != prev[0]:
                sync_trip_changes[src] += 1
              if trip == prev[0]:
                sync_reset_deltas[src][reset - prev[1]] += 1
            latest_sync[src] = (trip, reset, t)
          elif addr == 0x0D7 and len(dat) == 32:
            d7_counts[src] += 1
            mlow, rlow = decode_fv4(dat)
            sync = latest_sync.get(src)
            if sync is None:
              continue
            reconstructed_reset, reset_offset = reconstruct_reset_candidate(sync[1], rlow)
            if reconstructed_reset is None:
              continue
            epoch = (sync[0], reconstructed_reset)
            d7_mapped[src] += 1
            d7_reset_candidate_found[src] += 1
            d7_reset_candidate_offsets[src][int(reset_offset)] += 1
            d7_reset_match[src] += int(reset_offset == 0)
            if last_d7_epoch.get(src) != epoch:
              d7_epoch_count[src] += 1
              d7_first_low2[src][mlow] += 1
              last_d7_epoch[src] = epoch
            prev = last_d7.get(src)
            if prev is not None and prev[0] == epoch:
              d7_same_epoch_pairs[src] += 1
              d7_same_epoch_delta[src][(mlow - prev[1]) & 3] += 1
            last_d7[src] = (epoch, mlow, t)
          elif addr == 0x0B6 and len(dat) == 32:
            native_b6_counts[src] += 1
            incoming_b6_payloads[src][dat] += 1
      elif which == "sendcan":
        for fr in e.sendcan:
          if int(fr.address) != 0x0B6 or len(fr.dat) != 32:
            continue
          bus, dat = int(fr.src), bytes(fr.dat)
          send_b6_counts[bus] += 1
          send_b6_payloads[bus].add(dat)
          send_b6_zero_mac28[bus] += int((int.from_bytes(dat[28:32], "big") & 0x0FFFFFFF) == 0)
          mlow, rlow = decode_fv4(dat)
          # CarState's TSS3 parser and the B6 sender use the same logical bus as
          # the outgoing B6 in the current Camry port.  Historical routes are
          # recorded per bus rather than silently projecting bus 0.
          sync = latest_sync.get(bus)
          if sync is None:
            send_b6_sim_unmapped[bus] += 1
            continue
          reconstructed_reset, reset_offset = reconstruct_reset_candidate(sync[1], rlow)
          if reconstructed_reset is None:
            send_b6_sim_unmapped[bus] += 1
            continue
          epoch = (sync[0], reconstructed_reset)
          send_b6_mapped[bus] += 1
          send_b6_reset_candidate_found[bus] += 1
          send_b6_reset_candidate_offsets[bus][int(reset_offset)] += 1
          send_b6_reset_match[bus] += int(reset_offset == 0)
          if last_b6_epoch.get(bus) != epoch:
            send_b6_first_low2[bus][mlow] += 1
            last_b6_epoch[bus] = epoch
          prev = last_b6.get(bus)
          if prev is not None:
            gap = t - prev[2]
            send_b6_max_gap_ns[bus] = max(send_b6_max_gap_ns[bus], gap)
            if prev[0] == epoch:
              send_b6_same_epoch_pairs[bus] += 1
              send_b6_same_epoch_delta[bus][(mlow - prev[1]) & 3] += 1
          last_b6[bus] = (epoch, mlow, t)
          accepted, reason, _ = b6_sim[bus].accept(epoch, mlow)
          send_b6_sim_accept[bus] += int(accepted)
          send_b6_sim_reasons[bus][reason] += 1

  sources = sorted(set(sync_counts) | set(d7_counts) | set(native_b6_counts))
  buses = sorted(send_b6_counts)
  all_send_payloads = set().union(*send_b6_payloads.values()) if send_b6_payloads else set()
  incoming_b6_matches_send = {
    src: sum(count for payload, count in incoming_b6_payloads[src].items() if payload in all_send_payloads)
    for src in sources
  }
  incoming_b6_non_send_unique = {
    src: sum(count for payload, count in incoming_b6_payloads[src].items() if payload not in all_send_payloads)
    for src in sources
  }
  return {
    "route": str(route),
    "route_name": route.name,
    "initData": init_data,
    "inventory": inventory,
    "total_rlog_bytes": sum(x["bytes"] for x in inventory),
    "native": {
      str(src): {
        "sync_00f": sync_counts[src],
        "d7": d7_counts[src],
        "incoming_b6": native_b6_counts[src],
        "incoming_b6_exact_payload_matches_route_sendcan": incoming_b6_matches_send[src],
        "incoming_b6_payload_not_in_route_sendcan": incoming_b6_non_send_unique[src],
        "sync_epoch_changes": sync_epoch_changes[src],
        "sync_trip_changes": sync_trip_changes[src],
        "first_sync_trip_reset": list(first_sync[src]) if src in first_sync else None,
        "last_sync_trip_reset": list(last_sync_value[src]) if src in last_sync_value else None,
        "sync_same_trip_reset_deltas": counter_json(sync_reset_deltas[src]),
        "d7_mapped_to_prior_sync": d7_mapped[src],
        "d7_reset_candidate_found": d7_reset_candidate_found[src],
        "d7_reset_candidate_offsets": counter_json(d7_reset_candidate_offsets[src]),
        "d7_reset_low2_matches_latest_sync": d7_reset_match[src],
        "d7_epoch_count": d7_epoch_count[src],
        "d7_first_message_low2": counter_json(d7_first_low2[src]),
        "d7_same_epoch_pairs": d7_same_epoch_pairs[src],
        "d7_same_epoch_message_low2_delta_mod4": counter_json(d7_same_epoch_delta[src]),
      } for src in sources
    },
    "panda_b6_tx": {
      str(bus): {
        "successful_echoes": tx_b6_echo_counts[bus],
        "rejected_returns": tx_b6_reject_counts[bus],
        "mapped_successful_echoes": tx_b6_echo_mapped[bus],
        "reset_candidate_offsets": counter_json(tx_b6_echo_reset_offsets[bus]),
        "same_epoch_pairs": tx_b6_echo_same_epoch_pairs[bus],
        "same_epoch_message_low2_delta_mod4": counter_json(tx_b6_echo_same_epoch_delta[bus]),
        "receiver_model_accept_count": tx_b6_echo_model_accept[bus],
        "receiver_model_reasons": counter_json(tx_b6_echo_model_reasons[bus]),
      } for bus in sorted(set(tx_b6_echo_counts) | set(tx_b6_reject_counts))
    },
    "comma_b6": {
      str(bus): {
        "send_count": send_b6_counts[bus],
        "zero_mac28_count": send_b6_zero_mac28[bus],
        "mapped_to_prior_same_bus_sync": send_b6_mapped[bus],
        "unmapped_before_same_bus_sync": send_b6_sim_unmapped[bus],
        "reset_candidate_found": send_b6_reset_candidate_found[bus],
        "reset_candidate_offsets": counter_json(send_b6_reset_candidate_offsets[bus]),
        "reset_low2_matches_latest_sync": send_b6_reset_match[bus],
        "first_message_low2_by_observed_epoch": counter_json(send_b6_first_low2[bus]),
        "same_epoch_pairs": send_b6_same_epoch_pairs[bus],
        "same_epoch_message_low2_delta_mod4": counter_json(send_b6_same_epoch_delta[bus]),
        "max_gap_ms": round(send_b6_max_gap_ns[bus] / 1e6, 6),
        "receiver_model_accept_count": send_b6_sim_accept[bus],
        "receiver_model_reasons": counter_json(send_b6_sim_reasons[bus]),
      } for bus in buses
    },
  }


def aggregate(routes: list[dict[str, Any]]) -> dict[str, Any]:
  native_d7_first: Counter[int] = Counter()
  native_d7_delta: Counter[int] = Counter()
  native_d7_epochs = 0
  native_d7_pairs = 0
  native_d7_mapped = 0
  native_d7_reset_match = 0
  native_d7_reset_offsets: Counter[int] = Counter()
  native_b6 = 0
  incoming_b6_send_match = 0
  incoming_b6_not_send = 0
  b6_first: Counter[int] = Counter()
  b6_delta: Counter[int] = Counter()
  b6_send = 0
  b6_mapped = 0
  b6_reset_match = 0
  b6_reset_offsets: Counter[int] = Counter()
  b6_pairs = 0
  b6_accept = 0
  b6_unmapped = 0
  b6_reasons: Counter[str] = Counter()
  b6_zero_mac = 0
  tx_echoes = 0
  tx_rejects = 0
  tx_echo_mapped = 0
  tx_echo_accept = 0
  tx_echo_pairs = 0
  tx_echo_delta: Counter[int] = Counter()
  tx_echo_reset_offsets: Counter[int] = Counter()
  tx_echo_reasons: Counter[str] = Counter()
  total_bytes = 0

  for route in routes:
    total_bytes += int(route["total_rlog_bytes"])
    for x in route["native"].values():
      # Count each physical/native plane.  The artifact also publishes per-plane
      # data so relay duplicates are visible rather than silently deduplicated.
      native_b6 += int(x["incoming_b6"])
      incoming_b6_send_match += int(x["incoming_b6_exact_payload_matches_route_sendcan"])
      incoming_b6_not_send += int(x["incoming_b6_payload_not_in_route_sendcan"])
      native_d7_epochs += int(x["d7_epoch_count"])
      native_d7_pairs += int(x["d7_same_epoch_pairs"])
      native_d7_mapped += int(x["d7_mapped_to_prior_sync"])
      native_d7_reset_match += int(x["d7_reset_low2_matches_latest_sync"])
      native_d7_reset_offsets.update({int(k): int(v) for k, v in x["d7_reset_candidate_offsets"].items()})
      native_d7_first.update({int(k): int(v) for k, v in x["d7_first_message_low2"].items()})
      native_d7_delta.update({int(k): int(v) for k, v in x["d7_same_epoch_message_low2_delta_mod4"].items()})
    for x in route["panda_b6_tx"].values():
      tx_echoes += int(x["successful_echoes"])
      tx_rejects += int(x["rejected_returns"])
      tx_echo_mapped += int(x["mapped_successful_echoes"])
      tx_echo_accept += int(x["receiver_model_accept_count"])
      tx_echo_pairs += int(x["same_epoch_pairs"])
      tx_echo_reset_offsets.update({int(k): int(v) for k, v in x["reset_candidate_offsets"].items()})
      tx_echo_delta.update({int(k): int(v) for k, v in x["same_epoch_message_low2_delta_mod4"].items()})
      tx_echo_reasons.update({str(k): int(v) for k, v in x["receiver_model_reasons"].items()})
    for x in route["comma_b6"].values():
      b6_send += int(x["send_count"])
      b6_zero_mac += int(x["zero_mac28_count"])
      b6_mapped += int(x["mapped_to_prior_same_bus_sync"])
      b6_unmapped += int(x["unmapped_before_same_bus_sync"])
      b6_reset_match += int(x["reset_low2_matches_latest_sync"])
      b6_reset_offsets.update({int(k): int(v) for k, v in x["reset_candidate_offsets"].items()})
      b6_pairs += int(x["same_epoch_pairs"])
      b6_accept += int(x["receiver_model_accept_count"])
      b6_first.update({int(k): int(v) for k, v in x["first_message_low2_by_observed_epoch"].items()})
      b6_delta.update({int(k): int(v) for k, v in x["same_epoch_message_low2_delta_mod4"].items()})
      b6_reasons.update({str(k): int(v) for k, v in x["receiver_model_reasons"].items()})

  return {
    "routes": len(routes),
    "rlog_bytes": total_bytes,
    "incoming_b6_frames_all_native_planes": native_b6,
    "incoming_b6_exact_payload_matches_route_sendcan": incoming_b6_send_match,
    "incoming_b6_payload_not_in_route_sendcan": incoming_b6_not_send,
    "native_d7": {
      "mapped_frames_all_native_planes": native_d7_mapped,
      "reset_low2_matches_latest_sync": native_d7_reset_match,
      "reset_candidate_offsets": counter_json(native_d7_reset_offsets),
      "observed_epochs_all_native_planes": native_d7_epochs,
      "first_message_low2": counter_json(native_d7_first),
      "same_epoch_pairs": native_d7_pairs,
      "same_epoch_delta_mod4": counter_json(native_d7_delta),
    },
    "panda_b6_tx": {
      "successful_echoes": tx_echoes,
      "rejected_returns": tx_rejects,
      "mapped_successful_echoes": tx_echo_mapped,
      "receiver_model_accept_count": tx_echo_accept,
      "reset_candidate_offsets": counter_json(tx_echo_reset_offsets),
      "same_epoch_pairs": tx_echo_pairs,
      "same_epoch_delta_mod4": counter_json(tx_echo_delta),
      "receiver_model_reasons": counter_json(tx_echo_reasons),
    },
    "comma_b6": {
      "send_frames": b6_send,
      "zero_mac28_frames_historical_corpus": b6_zero_mac,
      "mapped_frames": b6_mapped,
      "unmapped_before_same_bus_sync": b6_unmapped,
      "reset_low2_matches_latest_sync": b6_reset_match,
      "reset_candidate_offsets": counter_json(b6_reset_offsets),
      "observed_epochs": sum(b6_first.values()),
      "first_message_low2": counter_json(b6_first),
      "same_epoch_pairs": b6_pairs,
      "same_epoch_delta_mod4": counter_json(b6_delta),
      "receiver_model_accept_count": b6_accept,
      "receiver_model_reasons": counter_json(b6_reasons),
    },
  }


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
  ap.add_argument("--openpilot", type=Path, default=DEFAULT_OPENPILOT)
  ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  LogReader = load_logreader(args.openpilot)
  discovered = discover_routes(args.log_root)
  if not discovered:
    raise SystemExit(f"no rlogs under {args.log_root}")

  routes = []
  for i, (route, segments) in enumerate(discovered, 1):
    print(f"[{i}/{len(discovered)}] {route} ({len(segments)} segments)", file=sys.stderr, flush=True)
    routes.append(scan_route(LogReader, route, segments))

  out = {
    "schema": "camry-b6-freshness-contract-v1",
    "scope": {
      "vehicle": "2026 Toyota Camry Hybrid",
      "eps": "8965F3307000",
      "log_root": str(args.log_root),
      "openpilot_root": str(args.openpilot),
    },
    "exact_f33_receiver_contract": {
      "freshness_before_mac": True,
      "freshness_dispatch": "0x8F746 -> profile callback 0x903A0 before 0x8F676/0x8F906 MAC processing",
      "fv4_parse": "0x90736: message_low2=B28>>6; reset_low2=(B28>>4)&3",
      "reset_reconstruction": "0x909CA: authenticated-global reset candidates current,-1,+1,-2,+2 filtered by transmitted reset_low2",
      "normal_slot": "0x90248 selects B6 freshness ID2 -> ordinary slot1; committed FEBE55E8, pending FEBE5600",
      "newer_epoch_rule": "0x90A48 seeds pending message8 directly from received message_low2; no fixed 0/1/2/3 starting phase is required",
      "same_epoch_rule": "0x90A48 reconstructs the next strictly-forward message8 congruent with message_low2; ordinary accepted gap is 1..4",
      "commit": "0x90448 -> 0x90D6A copies pending ordinary freshness to committed on success",
      "current_maintainer_patch": "cumulative stage5 includes stage4 0x8F7E6 0AD8->00DA (freshness callback result forced zero) and stage5 0x8F890 E051->E001 (ICU-S result compare neutralized)",
    },
    "phase_exhaustive_check": {
      "new_epoch_start_low2_accepted": {str(low2): SimState().accept((1, 1), low2)[0] for low2 in range(4)},
      "reset_candidate_from_current_100": {str(low2): reconstruct_reset_candidate(100, low2) for low2 in range(4)},
      "same_epoch_next_from_message_0": {str(low2): reconstruct_same_epoch_message(0, low2) for low2 in range(4)},
      "interpretation": "The observed native D7 preference for first low2=1 is sender policy/timing, not an F33 B6 receiver requirement.",
    },
    "routes": routes,
  }
  out["aggregate"] = aggregate(routes)
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
  print(json.dumps(out["aggregate"], indent=2, sort_keys=True))


if __name__ == "__main__":
  main()
