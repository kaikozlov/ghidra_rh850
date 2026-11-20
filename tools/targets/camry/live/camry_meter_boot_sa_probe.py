#!/usr/bin/env python3
"""Probe the Camry combination meter programming handoff and boot SecurityAccess.

Run this while holding the cooperative direct-Panda lease. The confirmed meter
route is the TSS3/F-CAM splice on Panda bus 1, 0x7C0 -> 0x7C8.

The programming-session request is asynchronous. Send exact physical 10 02 once
and leave it undisturbed while recording pending/final responses. If no final
response arrives, inspect F181/F186 once instead of guessing that silence means
the application stayed in its original session.

It performs no DID writes, download, transfer, RoutineControl, or ECU reset.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from Crypto.Cipher import AES

TX_ADDR = 0x7C0
RX_ADDR = 0x7C8
BUS = 1
ZERO16 = bytes(16)

# Recovered from the 2024 RAV4 Prime RH850 meter specimen.
METER_BOOT_SA_ROOT = bytes.fromhex("f579ca07326b246812a31464b123cbc6")


def _describe_frame(data: bytes) -> str:
  if not data:
    return "empty"
  frame_type = data[0] >> 4
  if frame_type == 0:
    length = data[0] & 0x0F
    return f"SF {data[1:1 + length].hex()}"
  if frame_type == 1 and len(data) >= 2:
    length = ((data[0] & 0x0F) << 8) | data[1]
    return f"FF len={length} {data[2:].hex()}"
  if frame_type == 2:
    return f"CF sn={data[0] & 0x0F} {data[1:].hex()}"
  if frame_type == 3:
    return f"FC fs={data[0] & 0x0F} bs={data[1] if len(data) > 1 else 0} stmin={data[2] if len(data) > 2 else 0}"
  return "unknown"


class TracedPanda:
  def __init__(self, panda):
    self._panda = panda

  def can_send(self, address, data, bus, *args, **kwargs):
    payload = bytes(data)
    if int(address) == TX_ADDR and int(bus) == BUS:
      print(f"CAN TX {int(address):03X} bus {int(bus)}: {payload.hex()} [{_describe_frame(payload)}]", flush=True)
    return self._panda.can_send(address, data, bus, *args, **kwargs)

  def can_recv(self):
    messages = self._panda.can_recv() or []
    for address, data, bus in messages:
      if int(address) == RX_ADDR and int(bus) == BUS:
        payload = bytes(data)
        print(f"CAN RX {int(address):03X} bus {int(bus)}: {payload.hex()} [{_describe_frame(payload)}]", flush=True)
    return messages


def _is_known_application_f181(response: bytes) -> bool:
  if not response.startswith(bytes.fromhex("62f18103")) or len(response) < 52:
    return False
  payload = response[4:52]
  slots = [payload[index * 16:(index + 1) * 16].rstrip(b"\x00") for index in range(3)]
  return slots == [b"8381GAQ02100", b"", b"8381FAQ01200"]


def load_openpilot():
  try:
    from panda import Panda  # type: ignore
    from opendbc.car.structs import CarParams  # type: ignore
    from opendbc.car.uds import CanClient, IsoTpMessage, MessageTimeoutError  # type: ignore
    return Panda, CarParams, CanClient, IsoTpMessage, MessageTimeoutError
  except ModuleNotFoundError:
    for root in (Path("/data/openpilot"), Path("/data/openpilot/current")):
      if root.is_dir():
        sys.path.insert(0, str(root))
        try:
          from panda import Panda  # type: ignore
          from opendbc.car.structs import CarParams  # type: ignore
          from opendbc.car.uds import CanClient, IsoTpMessage, MessageTimeoutError  # type: ignore
          return Panda, CarParams, CanClient, IsoTpMessage, MessageTimeoutError
        except ModuleNotFoundError:
          pass
  raise SystemExit("cannot import panda/opendbc; run this on the comma in its openpilot environment")


def derive_key(seed: bytes) -> bytes:
  if len(seed) != 16:
    raise ValueError(f"expected 16-byte seed, got {len(seed)}")
  working_key = AES.new(METER_BOOT_SA_ROOT, AES.MODE_ECB).decrypt(ZERO16)
  return AES.new(working_key, AES.MODE_ECB).encrypt(seed)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--session-wait",
    type=float,
    default=10.0,
    help="seconds to leave the 10 02 request undisturbed while awaiting its final response",
  )
  parser.add_argument(
    "--post-session-wait",
    type=float,
    default=2.0,
    help="seconds to wait after 50 02 before boot SecurityAccess, matching GTS Unified flow",
  )
  parser.add_argument("--response-slice", type=float, default=0.5)
  args = parser.parse_args()

  Panda, CarParams, CanClient, IsoTpMessage, MessageTimeoutError = load_openpilot()

  serials = Panda.list()
  if len(serials) != 1:
    raise RuntimeError(f"expected one Panda, got {serials}")

  panda = Panda(serials[0], cli=False, disable_checks=False)
  try:
    panda.set_heartbeat_disabled()
    panda.set_safety_mode(CarParams.SafetyModel.elm327, 0)
    traced_panda = TracedPanda(panda)

    def message() -> object:
      return IsoTpMessage(
        CanClient(traced_panda.can_send, traced_panda.can_recv, TX_ADDR, RX_ADDR, BUS),
        timeout=args.response_slice,
      )

    def request_once(label: str, request: bytes, timeout: float = 2.0) -> bytes | None:
      transaction = message()
      transaction.send(request)
      try:
        response, _ = transaction.recv(timeout)
      except MessageTimeoutError:
        print(f"{label} -> timeout", flush=True)
        return None
      if response is None:
        print(f"{label} -> no response", flush=True)
        return None
      response = bytes(response)
      print(f"{label} <- {response.hex()}", flush=True)
      return response

    print("10 02 -> waiting without further diagnostic traffic", flush=True)
    session = message()
    session.send(bytes.fromhex("1002"))
    deadline = time.monotonic() + args.session_wait
    final_response = None
    saw_pending = False

    while time.monotonic() < deadline:
      remaining = deadline - time.monotonic()
      try:
        response, _ = session.recv(min(args.response_slice, remaining))
      except MessageTimeoutError:
        continue
      if response is None:
        continue

      response = bytes(response)
      print(f"10 02 <- {response.hex()}", flush=True)

      if response == bytes.fromhex("7f1078"):
        saw_pending = True
        continue

      final_response = response
      break

    if final_response is None:
      pending = " after 7F 10 78" if saw_pending else ""
      print(f"10 02 -> no final response in {args.session_wait:g}s{pending}", flush=True)

      f181 = request_once("22 F181", bytes.fromhex("22f181"))
      if f181 is None or not f181.startswith(bytes.fromhex("62f181")):
        print("handoff result unresolved: neither 50 02 nor a readable meter identity", flush=True)
        return 3
      if _is_known_application_f181(f181):
        f186 = request_once("22 F186", bytes.fromhex("22f186"))
        session = f"0x{f186[3]:02X}" if f186 is not None and f186.startswith(bytes.fromhex("62f186")) and len(f186) >= 4 else "unknown"
        print(f"application remains active; reported diagnostic session {session}", flush=True)
        return 3
      print("application F181 disappeared; treating the responder as the bootloader", flush=True)
    else:
      if not final_response.startswith(bytes.fromhex("5002")):
        print(f"10 02 -> unexpected final response {final_response.hex()}", flush=True)
        return 4

      print(f"10 02 -> programming session accepted: {final_response.hex()}", flush=True)
      time.sleep(args.post_session_wait)

    seed_request = message()
    seed_request.send(bytes.fromhex("2701") + ZERO16)
    try:
      seed_response, _ = seed_request.recv(2.0)
    except MessageTimeoutError:
      print("27 01 + zero16 -> timeout", flush=True)
      return 5

    if seed_response is None:
      print("27 01 + zero16 -> no response", flush=True)
      return 5

    seed_response = bytes(seed_response)
    if seed_response.startswith(bytes.fromhex("7f27")):
      print(f"27 01 + zero16 -> {seed_response.hex()}", flush=True)
      return 5
    if not seed_response.startswith(bytes.fromhex("6701")):
      print(f"27 01 + zero16 -> unexpected response {seed_response.hex()}", flush=True)
      return 5

    seed = seed_response[2:]
    if len(seed) != 16:
      print(f"27 01 + zero16 -> unexpected {len(seed)}-byte seed: {seed.hex()}", flush=True)
      return 6

    print(f"27 01 + zero16 -> 67 01 {seed.hex()}", flush=True)
    key = derive_key(seed)
    print(f"derived key = {key.hex()}", flush=True)

    key_request = message()
    key_request.send(bytes.fromhex("2702") + key)
    try:
      key_response, _ = key_request.recv(2.0)
    except MessageTimeoutError:
      print("27 02 + key -> timeout", flush=True)
      return 7

    if key_response is None:
      print("27 02 + key -> no response", flush=True)
      return 7

    key_response = bytes(key_response)
    if key_response == bytes.fromhex("6702"):
      print("27 02 + key -> 67 02", flush=True)
      print("SUCCESS: meter boot SecurityAccess accepted", flush=True)
      return 0

    print(f"27 02 + key -> {key_response.hex()}", flush=True)
    return 7
  finally:
    panda.close()


if __name__ == "__main__":
  raise SystemExit(main())
