#!/usr/bin/env python3
"""Reduce the first FDF-preserving, exact-F33-timing Camry road capture.

This is a source-derived audit of route 00000045--805b7ca6ab.  It answers
three questions that historical rlogs could not answer:

* Are Toyota's native 8-byte 0x412 and 0x101 PDUs Classical CAN or CAN FD?
* Does production pandad's legacy canfd_auto change the format of replacements?
* Does exact 70% F33 data timing reveal any recurrent native address/DLC shape
  absent from the previous long 80%-timing route?

Full rlogs are maintainer-local external inputs.  The generated JSON is the
portable compact evidence artifact; tests pin its decisive counts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_NEW = Path("/Users/kai/dev/inspect/logs/camry-2026/2026-09-07/00000045--805b7ca6ab")
DEFAULT_BASELINE = Path("/Users/kai/dev/inspect/logs/camry-2026/2026-09-06/0000003f--36e72f5fdc")
DEFAULT_OPENPILOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
DEFAULT_OUT = Path("data/generated/camry_20260907_canfd_transport.json")
SPECIAL = (0x0B6, 0x412, 0x101, 0x08A, 0x025, 0x030, 0x090, 0x0D7, 0x00F, 0x251, 0x371)


def load_logreader(root: Path):
  sys.path.insert(0, str(root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
      h.update(chunk)
  return h.hexdigest()


def segment_files(route: Path) -> list[tuple[int, Path]]:
  rows: list[tuple[int, Path]] = []
  # Current local archive convention: ROUTE/ROUTE--SEG/rlog.zst.
  for p in route.glob("*/rlog.zst"):
    try:
      rows.append((int(p.parent.name.rsplit("--", 1)[1]), p))
    except (IndexError, ValueError):
      pass
  # Older flat convention is accepted too.
  for p in route.glob("rlog-*.zst"):
    try:
      rows.append((int(p.name[5:-4]), p))
    except ValueError:
      pass
  return sorted(dict(rows).items())


def keyrow(k: tuple[int, int, int], count: int | None = None) -> dict[str, Any]:
  row: dict[str, Any] = {"bus": k[0], "address": f"0x{k[1]:03X}", "length": k[2]}
  if count is not None:
    row["count"] = count
  return row


def scan_native_keys(LogReader, route: Path) -> Counter[tuple[int, int, int]]:
  out: Counter[tuple[int, int, int]] = Counter()
  for _, p in segment_files(route):
    for e in LogReader(str(p), sort_by_time=False, only_union_types=True):
      if e.which() != "can":
        continue
      for m in e.can:
        src = int(m.src)
        if src < 3:
          out[(src, int(m.address), len(m.dat))] += 1
  return out


def scan_new(LogReader, route: Path) -> dict[str, Any]:
  native_format: Counter[tuple[int, int, int, bool]] = Counter()
  sendcan: Counter[tuple[int, int, int, bool]] = Counter()
  returned: Counter[tuple[int, int, int, bool]] = Counter()
  rejected: Counter[tuple[int, int, int, bool]] = Counter()
  special: dict[int, Counter[tuple[int, int, bool]]] = defaultdict(Counter)
  init: dict[str, Any] = {}
  harness: Counter[str] = Counter()
  ps_first: list[dict[str, Any] | None] = [None, None, None]
  ps_last: list[dict[str, Any] | None] = [None, None, None]
  ps_max: list[dict[str, int]] = [defaultdict(int), defaultdict(int), defaultdict(int)]
  first_ns: int | None = None
  last_ns: int | None = None
  segments = segment_files(route)

  def health(cs) -> dict[str, Any]:
    return {
      "busOffCnt": int(cs.busOffCnt), "receiveErrorCnt": int(cs.receiveErrorCnt),
      "transmitErrorCnt": int(cs.transmitErrorCnt), "totalErrorCnt": int(cs.totalErrorCnt),
      "totalTxLostCnt": int(cs.totalTxLostCnt), "totalRxLostCnt": int(cs.totalRxLostCnt),
      "canCoreResetCnt": int(cs.canCoreResetCnt), "lastStoredError": str(cs.lastStoredError),
      "lastDataStoredError": str(cs.lastDataStoredError), "canfdEnabled": bool(cs.canfdEnabled),
      "brsEnabled": bool(cs.brsEnabled), "canSpeed": int(cs.canSpeed),
      "canDataSpeed": int(cs.canDataSpeed),
    }

  for seg, p in segments:
    for e in LogReader(str(p), sort_by_time=True, only_union_types=True):
      t = int(e.logMonoTime)
      first_ns = t if first_ns is None else min(first_ns, t)
      last_ns = t if last_ns is None else max(last_ns, t)
      which = e.which()
      if which == "initData" and not init:
        x = e.initData
        init = {"gitCommit": str(x.gitCommit), "gitBranch": str(x.gitBranch),
                "dirty": bool(x.dirty), "version": str(x.version)}
      elif which == "can":
        for m in e.can:
          src, addr, length, fd = int(m.src), int(m.address), len(m.dat), bool(m.fd)
          if src < 3:
            native_format[(src, addr, length, fd)] += 1
          elif 128 <= src < 131:
            returned[(src - 128, addr, length, fd)] += 1
          elif 192 <= src < 195:
            rejected[(src - 192, addr, length, fd)] += 1
          if addr in SPECIAL:
            special[addr][(src, length, fd)] += 1
      elif which == "sendcan":
        for m in e.sendcan:
          sendcan[(int(m.src), int(m.address), len(m.dat), bool(m.fd))] += 1
      elif which == "pandaStates":
        for ps in e.pandaStates:
          harness[str(ps.harnessStatus)] += 1
          for i in range(3):
            d = health(getattr(ps, f"canState{i}"))
            if ps_first[i] is None:
              ps_first[i] = d.copy()
            ps_last[i] = d.copy()
            for field in ("busOffCnt", "receiveErrorCnt", "transmitErrorCnt", "totalErrorCnt",
                          "totalTxLostCnt", "totalRxLostCnt", "canCoreResetCnt"):
              ps_max[i][field] = max(ps_max[i][field], int(d[field]))

  by_bus: dict[str, Any] = {}
  for bus in range(3):
    rows = [(k, n) for k, n in native_format.items() if k[0] == bus]
    by_bus[str(bus)] = {
      "frames": sum(n for _, n in rows),
      "classical": sum(n for k, n in rows if not k[3]),
      "can_fd": sum(n for k, n in rows if k[3]),
      "address_length_keys": len({(k[1], k[2]) for k, _ in rows}),
    }

  specials = {
    f"0x{addr:03X}": [
      {"src": src, "length": length, "fd": fd, "count": n}
      for (src, length, fd), n in sorted(counter.items())
    ] for addr, counter in special.items()
  }

  host = {}
  for addr in (0x0B6, 0x412, 0x101):
    host[f"0x{addr:03X}"] = {
      "sendcan": [
        {"bus": b, "length": l, "fd": fd, "count": n}
        for (b, a, l, fd), n in sorted(sendcan.items()) if a == addr
      ],
      "returned": [
        {"bus": b, "length": l, "fd": fd, "count": n}
        for (b, a, l, fd), n in sorted(returned.items()) if a == addr
      ],
      "rejected": [
        {"bus": b, "length": l, "fd": fd, "count": n}
        for (b, a, l, fd), n in sorted(rejected.items()) if a == addr
      ],
    }

  health_rows = []
  for i in range(3):
    first = ps_first[i] or {}
    last = ps_last[i] or {}
    health_rows.append({
      "physical_can": i,
      "first": first,
      "last": last,
      "max": dict(ps_max[i]),
      "total_error_growth": int(last.get("totalErrorCnt", 0)) - int(first.get("totalErrorCnt", 0)),
      "bus_off_growth": int(last.get("busOffCnt", 0)) - int(first.get("busOffCnt", 0)),
      "rx_lost_growth": int(last.get("totalRxLostCnt", 0)) - int(first.get("totalRxLostCnt", 0)),
      "tx_lost_growth": int(last.get("totalTxLostCnt", 0)) - int(first.get("totalTxLostCnt", 0)),
    })

  return {
    "segments": [{"segment": seg, "bytes": p.stat().st_size, "sha256": sha256(p)} for seg, p in segments],
    "duration_s": round(((last_ns or 0) - (first_ns or 0)) / 1e9, 6),
    "init_data": init,
    "harness_status_counts": dict(harness),
    "native_by_bus": by_bus,
    "special_frame_formats": specials,
    "host_tx": host,
    "panda_health": health_rows,
    "native_keys": Counter((b, a, l) for (b, a, l, _fd) in native_format.elements()),
  }


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--new-route", type=Path, default=DEFAULT_NEW)
  ap.add_argument("--baseline-route", type=Path, default=DEFAULT_BASELINE)
  ap.add_argument("--openpilot-root", type=Path, default=DEFAULT_OPENPILOT)
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  LogReader = load_logreader(args.openpilot_root)
  new = scan_new(LogReader, args.new_route)
  new_keys: Counter[tuple[int, int, int]] = new.pop("native_keys")
  old_keys = scan_native_keys(LogReader, args.baseline_route)

  comparison = {}
  for bus in range(3):
    a = {k for k in old_keys if k[0] == bus}
    b = {k for k in new_keys if k[0] == bus}
    comparison[str(bus)] = {
      "baseline_key_count": len(a), "matched_timing_key_count": len(b),
      "new_only": [keyrow(k, new_keys[k]) for k in sorted(b - a)],
      "baseline_only": [keyrow(k, old_keys[k]) for k in sorted(a - b)],
    }

  def special_count(addr: str, *, native: bool, fd: bool) -> int:
    return sum(r["count"] for r in new["special_frame_formats"].get(addr, [])
               if (r["src"] < 3) == native and r["fd"] == fd)

  def tx_count(addr: str, group: str, *, fd: bool) -> int:
    return sum(r["count"] for r in new["host_tx"][addr][group] if r["fd"] == fd)

  native_412_classic = special_count("0x412", native=True, fd=False)
  native_412_fd = special_count("0x412", native=True, fd=True)
  native_101_classic = special_count("0x101", native=True, fd=False)
  native_101_fd = special_count("0x101", native=True, fd=True)
  native_b6 = special_count("0x0B6", native=True, fd=False) + special_count("0x0B6", native=True, fd=True)
  send_412_classic = tx_count("0x412", "sendcan", fd=False)
  sent_412_fd = tx_count("0x412", "returned", fd=True)
  send_101_classic = tx_count("0x101", "sendcan", fd=False)
  sent_101_fd = tx_count("0x101", "returned", fd=True)

  result = {
    "schema_version": 1,
    "scope": {
      "matched_timing_route": args.new_route.name,
      "baseline_route": args.baseline_route.name,
      "matched_openpilot_commit": new["init_data"].get("gitCommit"),
      "boundary": "FDF is recorded; BRS is not represented by CanData and remains outside this artifact.",
    },
    "matched_timing": new,
    "native_address_length_comparison": comparison,
    "conclusions": {
      "native_0x412_is_classical": native_412_classic > 0 and native_412_fd == 0,
      "native_0x101_is_classical": native_101_classic > 0 and native_101_fd == 0,
      "host_0x412_was_promoted_to_fd_by_canfd_auto": send_412_classic > 0 and sent_412_fd > 0,
      "host_0x101_was_promoted_to_fd_by_canfd_auto": send_101_classic > 0 and sent_101_fd > 0,
      "native_b6_frames": native_b6,
      "matched_timing_new_native_address_length_signatures": sum(len(v["new_only"]) for v in comparison.values()),
    },
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
  print(args.out)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
