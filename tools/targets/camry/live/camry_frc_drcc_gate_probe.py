#!/usr/bin/env python3
"""Parked discriminator for the exact-Camry FRC DRCC main-switch refusal.

The probe answers one narrow question: does restoring the missing exact-F33
``0x030/32`` stream and clearing FRC DTC U0131-87 make FRC cruise permission
return, so a normal DRCC MAIN press changes ``0x251 B0`` from ``0x80`` to
``0xA0`` instead of ``0xE0``?

``observe`` is read-only apart from ordinary FRC SID-0x22 requests. ``probe``
uses Panda allOutput only for a finite parked test because ELM327 safety cannot
transmit CAN-FD ``0x030``. It refuses to start unless every observed wheel-speed
sample is exactly Toyota's stationary raw value and native ``0x030`` is absent.
Panda is returned to silent safety in ``finally``.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

FRC_TX = 0x792
FRC_RX = 0x79A
EPS_STATUS = 0x030
WHEEL_SPEED = 0x0AA
CRUISE_DISPLAY = 0x251
STATIONARY_WHEEL_RAW = 6767

RDBI_DIDS = (0x1903, 0x1905, 0x1906)
FRC_CLEAR_DTC = bytes.fromhex("14ffffff")
FLOW_CONTROL = bytes.fromhex("3000000000000000")
SILENT_SAFETY = 0
ELM327_SAFETY = 3
ELM327_PARAM = 1
ALLOUTPUT_PASSTHROUGH_PARAM = 1


def process_cmdlines() -> list[tuple[int, str]]:
  proc = Path("/proc")
  if not proc.is_dir():
    return []
  out = []
  for child in proc.iterdir():
    if not child.name.isdigit():
      continue
    try:
      cmd = (child / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
    except (FileNotFoundError, PermissionError, ProcessLookupError):
      continue
    if cmd:
      out.append((int(child.name), cmd))
  return out


def find_pandad() -> list[tuple[int, str]]:
  return [(pid, cmd) for pid, cmd in process_cmdlines()
          if any(Path(word).name in {"pandad", "_pandad"} or Path(word).name.startswith("pandad-")
                 or word.endswith(".pandad.pandad")
                 for word in cmd.split())]


def load_panda():
  try:
    from opendbc.car.structs import CarParams  # type: ignore
    from panda import Panda  # type: ignore
    return Panda, CarParams
  except ModuleNotFoundError:
    for candidate in (Path("/data/openpilot"), Path("/data/openpilot/current")):
      if candidate.is_dir():
        sys.path.insert(0, str(candidate))
        try:
          from opendbc.car.structs import CarParams  # type: ignore
          from panda import Panda  # type: ignore
          return Panda, CarParams
        except ModuleNotFoundError:
          pass
  raise SystemExit("cannot import panda/opendbc; run on the comma from its openpilot environment")


def json_line(kind: str, **fields: Any) -> None:
  print(json.dumps({"type": kind, "t_ns": time.monotonic_ns(), **fields}, sort_keys=True), flush=True)


def single_frame(pdu: bytes) -> bytes:
  if len(pdu) > 7:
    raise ValueError("request PDU does not fit one classic-CAN ISO-TP frame")
  return bytes((len(pdu),)) + pdu + bytes(7 - len(pdu))


def decode_frc_pdu(pdu: bytes) -> dict[str, Any]:
  if pdu == bytes.fromhex("54"):
    return {"service": "clearDiagnosticInformation", "status": "positive"}
  if len(pdu) >= 3 and pdu[0] == 0x7F:
    return {"service": f"0x{pdu[1]:02X}", "status": "negative", "nrc": f"0x{pdu[2]:02X}"}
  if len(pdu) < 3 or pdu[0] != 0x62:
    return {"status": "unparsed", "pdu": pdu.hex()}
  did = int.from_bytes(pdu[1:3], "big")
  value = pdu[3:]
  row: dict[str, Any] = {"service": "readDataByIdentifier", "status": "positive",
                         "did": f"0x{did:04X}", "value": value.hex()}
  if did == 0x1903 and value:
    row["control_mode"] = value[0]
    row["control_mode_label"] = {
      1: "DRCC all speed", 2: "DRCC high speed", 3: "constant speed",
      4: "DRCC all speed without brake hold",
    }.get(value[0], "unknown")
  elif did == 0x1905 and len(value) >= 2:
    row["cruise_control_allowed"] = bool(value[1] & 0x80)
  elif did == 0x1906 and len(value) >= 6:
    row["main_switch_recognized"] = bool(value[1] & 0x80)
    row["acc_not_available_icon"] = bool(value[5] & 0x80)
  return row


def drain(panda, *, on_tick: Callable[[int], None] | None = None,
          deadline_ns: int | None = None) -> list[tuple[int, bytes, int]]:
  now = time.monotonic_ns()
  if on_tick is not None:
    on_tick(now)
  msgs = panda.can_recv() or []
  if deadline_ns is not None and time.monotonic_ns() < deadline_ns and not msgs:
    time.sleep(0.001)
  return [(int(addr), bytes(dat), int(bus)) for addr, dat, bus in msgs]


def isotp_request(panda, pdu: bytes, bus: int, *, timeout_s: float = 1.0,
                  on_tick: Callable[[int], None] | None = None) -> bytes:
  panda.can_send(FRC_TX, single_frame(pdu), bus)
  deadline = time.monotonic_ns() + int(timeout_s * 1e9)
  assembly: bytearray | None = None
  total = 0
  next_sn = 1
  while time.monotonic_ns() < deadline:
    for addr, frame, src in drain(panda, on_tick=on_tick, deadline_ns=deadline):
      if addr == CRUISE_DISPLAY and src == bus and frame:
        json_line("cruise_display", bus=src, byte0=f"0x{frame[0]:02X}", frame=frame.hex())
      if addr != FRC_RX or src != bus or not frame:
        continue
      pci = frame[0] >> 4
      if pci == 0:
        length = frame[0] & 0x0F
        return frame[1:1 + length]
      if pci == 1 and len(frame) >= 2:
        total = ((frame[0] & 0x0F) << 8) | frame[1]
        assembly = bytearray(frame[2:])
        panda.can_send(FRC_TX, FLOW_CONTROL, bus)
        if len(assembly) >= total:
          return bytes(assembly[:total])
      elif pci == 2 and assembly is not None:
        sn = frame[0] & 0x0F
        if sn != next_sn:
          raise RuntimeError(f"ISO-TP sequence mismatch: expected {next_sn}, got {sn}")
        assembly.extend(frame[1:])
        next_sn = (next_sn + 1) & 0x0F
        if len(assembly) >= total:
          return bytes(assembly[:total])
  raise TimeoutError(f"FRC 0x{FRC_TX:03X} request timed out: {pdu.hex()}")


def read_oracles(panda, bus: int, *, on_tick: Callable[[int], None] | None = None) -> None:
  for did in RDBI_DIDS:
    pdu = isotp_request(panda, bytes((0x22, did >> 8, did & 0xFF)), bus, on_tick=on_tick)
    json_line("frc_response", bus=bus, raw_pdu=pdu.hex(), decoded=decode_frc_pdu(pdu))


def preflight(panda, bus: int, duration_s: float = 1.5) -> None:
  deadline = time.monotonic_ns() + int(duration_s * 1e9)
  wheel_samples = 0
  native_030 = 0
  nonstationary: list[str] = []
  while time.monotonic_ns() < deadline:
    for addr, frame, src in drain(panda, deadline_ns=deadline):
      if src != bus:
        continue
      if addr == EPS_STATUS and len(frame) == 32:
        native_030 += 1
      elif addr == WHEEL_SPEED and len(frame) == 8:
        wheel_samples += 1
        raw = [int.from_bytes(frame[i:i + 2], "big") & 0x7FFF for i in range(0, 8, 2)]
        if raw != [STATIONARY_WHEEL_RAW] * 4:
          nonstationary.append(frame.hex())
  json_line("preflight", bus=bus, wheel_samples=wheel_samples, native_030=native_030,
            nonstationary_samples=len(nonstationary))
  if wheel_samples < 20:
    raise RuntimeError(f"stationary guard unavailable: only {wheel_samples} wheel-speed samples")
  if nonstationary:
    raise RuntimeError(f"vehicle is not exactly stationary: {nonstationary[0]}")
  if native_030:
    raise RuntimeError(f"native 0x030 is present ({native_030} frames); replay probe is not applicable")


def load_replay(path: Path) -> list[bytes]:
  obj = json.loads(path.read_text())
  frames = [bytes.fromhex(x) for x in obj["frames"]]
  if not frames or any(len(frame) != 32 for frame in frames):
    raise ValueError("replay must contain one or more 32-byte frames")
  return frames


def extract_replay(rlogs: list[Path], out: Path, source_bus: int, max_frames: int,
                   start_mono: float | None) -> None:
  sys.path.insert(0, "/Users/kai/dev/inspect/repos/kai-openpilot")
  from openpilot.tools.lib.logreader import LogReader  # type: ignore
  frames: list[str] = []
  for path in rlogs:
    for event in LogReader(str(path), sort_by_time=True):
      if start_mono is not None and event.logMonoTime / 1e9 < start_mono:
        continue
      if event.which() != "can":
        continue
      for frame in event.can:
        if int(frame.src) == source_bus and int(frame.address) == EPS_STATUS and len(frame.dat) == 32:
          frames.append(bytes(frame.dat).hex())
          if len(frames) >= max_frames:
            break
      if len(frames) >= max_frames:
        break
    if len(frames) >= max_frames:
      break
  if not frames:
    raise RuntimeError("no matching 0x030/32 frames")
  out.write_text(json.dumps({"schema": "camry-f33-030-replay-v1", "source_bus": source_bus,
                             "source_rlogs": [str(p) for p in rlogs], "period_ms": 10,
                             "frames": frames}, indent=2) + "\n")
  print(f"wrote {len(frames)} frames to {out}")


class Replay:
  def __init__(self, panda, bus: int, frames: list[bytes]) -> None:
    self.panda = panda
    self.bus = bus
    self.frames = frames
    self.index = 0
    self.next_ns = time.monotonic_ns()
    self.sent = 0

  def tick(self, now_ns: int) -> None:
    while now_ns >= self.next_ns:
      self.panda.can_send(EPS_STATUS, self.frames[self.index], self.bus, fd=True)
      self.index = (self.index + 1) % len(self.frames)
      self.next_ns += 10_000_000
      self.sent += 1


def open_panda():
  running = find_pandad()
  if running:
    detail = "; ".join(f"pid={pid} {cmd}" for pid, cmd in running)
    raise SystemExit(f"refusing Panda USB collision: stop openpilot first ({detail})")
  Panda, CarParams = load_panda()
  serials = Panda.list()
  if len(serials) != 1:
    raise SystemExit(f"expected exactly one Panda, found {len(serials)}: {serials}")
  return Panda(serials[0]), CarParams


def observe(bus: int, duration_s: float) -> None:
  panda, _ = open_panda()
  try:
    panda.set_heartbeat_disabled()
    panda.set_safety_mode(ELM327_SAFETY, ELM327_PARAM)
    read_oracles(panda, bus)
    deadline = time.monotonic_ns() + int(duration_s * 1e9)
    last_b0 = None
    while time.monotonic_ns() < deadline:
      for addr, frame, src in drain(panda, deadline_ns=deadline):
        if addr == CRUISE_DISPLAY and src == bus and frame and frame[0] != last_b0:
          last_b0 = frame[0]
          json_line("cruise_display", bus=src, byte0=f"0x{frame[0]:02X}", frame=frame.hex())
    read_oracles(panda, bus)
  finally:
    panda.set_safety_mode(SILENT_SAFETY)


def probe(bus: int, replay_path: Path, duration_s: float, arm: str) -> None:
  if arm != "PARKED_ONLY":
    raise SystemExit("probe requires --arm PARKED_ONLY")
  frames = load_replay(replay_path)
  panda, CarParams = open_panda()
  replay: Replay | None = None
  try:
    panda.set_heartbeat_disabled()
    panda.set_safety_mode(ELM327_SAFETY, ELM327_PARAM)
    preflight(panda, bus)
    read_oracles(panda, bus)

    panda.set_canfd_auto(bus, True)
    # Keep normal CAN0<->CAN2 forwarding alive while opening the finite probe
    # TX surface. The target 0x030 is on unsplit bus 1 in this harness state.
    panda.set_safety_mode(CarParams.SafetyModel.allOutput, ALLOUTPUT_PASSTHROUGH_PARAM)
    replay = Replay(panda, bus, frames)
    warmup_end = time.monotonic_ns() + 2_000_000_000
    accepted = 0
    rejected = 0
    while time.monotonic_ns() < warmup_end:
      for addr, _, src in drain(panda, on_tick=replay.tick, deadline_ns=warmup_end):
        if addr == EPS_STATUS and src == bus + 128:
          accepted += 1
        elif addr == EPS_STATUS and src == bus + 192:
          rejected += 1
    json_line("replay_warmup", sent=replay.sent, accepted=accepted, rejected=rejected)
    if accepted < 100 or rejected:
      raise RuntimeError(f"0x030 replay TX did not pass Panda: accepted={accepted}, rejected={rejected}")

    clear = isotp_request(panda, FRC_CLEAR_DTC, bus, on_tick=replay.tick)
    json_line("frc_response", bus=bus, raw_pdu=clear.hex(), decoded=decode_frc_pdu(clear))
    read_oracles(panda, bus, on_tick=replay.tick)
    json_line("instruction", message="press MAIN once now with DRCC selected")

    deadline = time.monotonic_ns() + int(duration_s * 1e9)
    last_b0 = None
    next_oracle = time.monotonic_ns() + 1_000_000_000
    while time.monotonic_ns() < deadline:
      now = time.monotonic_ns()
      if now >= next_oracle:
        read_oracles(panda, bus, on_tick=replay.tick)
        next_oracle = time.monotonic_ns() + 1_000_000_000
      for addr, frame, src in drain(panda, on_tick=replay.tick, deadline_ns=deadline):
        if addr == CRUISE_DISPLAY and src == bus and frame and frame[0] != last_b0:
          last_b0 = frame[0]
          json_line("cruise_display", bus=src, byte0=f"0x{frame[0]:02X}", frame=frame.hex())
    json_line("summary", replay_frames_sent=replay.sent)
  finally:
    try:
      panda.set_safety_mode(SILENT_SAFETY)
    finally:
      json_line("safety_restored", mode="silent", replay_frames_sent=0 if replay is None else replay.sent)


def plan() -> dict[str, Any]:
  return {
    "question": "Does 0x030 liveness plus FRC U0131 clear restore DRCC MAIN permission?",
    "oracles": ["FRC 0x1903 Control Mode", "FRC 0x1905 Cruise Control Permission",
                "FRC 0x1906 Main Switch Recognition / ACC Not Available", "CAN 0x251 B0"],
    "sequence": ["confirm exact stationary wheel speed and absent native 0x030",
                 "read FRC oracles", "replay retained stock 0x030/32 at 100 Hz",
                 "clear FRC DTCs with 14 FF FF FF", "read oracles", "press MAIN", "read oracles"],
    "positive_result": "0x1905 Allowed and 0x251 B0 0x80 -> 0xA0",
    "negative_result": "permission remains denied / 0xE0; stale protected 0x030 is insufficient",
    "scope": "finite parked development probe; not an openpilot runtime feature",
  }


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  sub = ap.add_subparsers(dest="command", required=True)
  sub.add_parser("plan")
  obs = sub.add_parser("observe")
  obs.add_argument("--bus", type=int, default=1)
  obs.add_argument("--duration", type=float, default=15.0)
  ext = sub.add_parser("extract-replay")
  ext.add_argument("rlogs", nargs="+", type=Path)
  ext.add_argument("--out", type=Path, required=True)
  ext.add_argument("--source-bus", type=int, default=0)
  ext.add_argument("--max-frames", type=int, default=512)
  ext.add_argument("--start-mono", type=float)
  pro = sub.add_parser("probe")
  pro.add_argument("--bus", type=int, default=1)
  pro.add_argument("--replay", type=Path, required=True)
  pro.add_argument("--duration", type=float, default=15.0)
  pro.add_argument("--arm", required=True)
  args = ap.parse_args()
  if args.command == "plan":
    print(json.dumps(plan(), indent=2))
  elif args.command == "observe":
    observe(args.bus, args.duration)
  elif args.command == "extract-replay":
    extract_replay(args.rlogs, args.out, args.source_bus, args.max_frames, args.start_mono)
  elif args.command == "probe":
    probe(args.bus, args.replay, args.duration, args.arm)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
