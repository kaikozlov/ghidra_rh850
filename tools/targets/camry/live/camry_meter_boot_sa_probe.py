#!/usr/bin/env python3
"""Probe the Camry combination meter bootloader SecurityAccess path.

This is intentionally narrow. It:
  1. finds 0x7C0/0x7C8 with UDS 10 01 on the current Panda routing,
  2. requests programming session with 10 02,
  3. requests a boot seed with 27 01 || 16 zero bytes,
  4. derives the response with the recovered RAV4 Prime meter boot root,
  5. sends 27 02 || key and exits.

It does not write DIDs, request a download, transfer data, invoke a routine,
or reset the ECU.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from Crypto.Cipher import AES

TX_ADDR = 0x7C0
RX_ADDR = 0x7C8
BUSES = (1, 0, 2)
ZERO16 = bytes(16)

# Recovered from the 2024 RAV4 Prime RH850 meter specimen.
METER_BOOT_SA_ROOT = bytes.fromhex("f579ca07326b246812a31464b123cbc6")


def load_openpilot():
  try:
    import openpilot.cereal.messaging as messaging  # type: ignore
    from openpilot.selfdrive.car.card import can_comm_callbacks  # type: ignore
    from opendbc.car.can_definitions import CanData  # type: ignore
    from opendbc.car.uds import CanClient, IsoTpMessage, MessageTimeoutError  # type: ignore
    return messaging, can_comm_callbacks, CanData, CanClient, IsoTpMessage, MessageTimeoutError
  except ModuleNotFoundError:
    for root in (Path("/data/openpilot"), Path("/data/openpilot/current")):
      if root.is_dir():
        sys.path.insert(0, str(root))
        try:
          import openpilot.cereal.messaging as messaging  # type: ignore
          from openpilot.selfdrive.car.card import can_comm_callbacks  # type: ignore
          from opendbc.car.can_definitions import CanData  # type: ignore
          from opendbc.car.uds import CanClient, IsoTpMessage, MessageTimeoutError  # type: ignore
          return messaging, can_comm_callbacks, CanData, CanClient, IsoTpMessage, MessageTimeoutError
        except ModuleNotFoundError:
          pass
  raise SystemExit("cannot import openpilot/opendbc; run this on the comma in its openpilot environment")


def derive_key(seed: bytes) -> bytes:
  if len(seed) != 16:
    raise ValueError(f"expected 16-byte seed, got {len(seed)}")
  working_key = AES.new(METER_BOOT_SA_ROOT, AES.MODE_ECB).decrypt(ZERO16)
  return AES.new(working_key, AES.MODE_ECB).encrypt(seed)


def describe_response(pdu: bytes | None) -> str:
  if pdu is None:
    return "timeout"
  if len(pdu) >= 3 and pdu[0] == 0x7F:
    return f"{pdu.hex()}  (NRC 0x{pdu[2]:02X})"
  return pdu.hex()


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--timeout", type=float, default=0.75,
                      help="per-response ISO-TP timeout in seconds")
  args = parser.parse_args()

  (
    messaging, can_comm_callbacks, CanData, CanClient, IsoTpMessage, MessageTimeoutError,
  ) = load_openpilot()

  logcan = messaging.sub_sock("can")
  sendcan = messaging.pub_sock("sendcan")
  can_recv_packets, can_send_msgs = can_comm_callbacks(logcan, sendcan)

  def can_tx(addr: int, dat: bytes, bus: int) -> None:
    can_send_msgs([CanData(addr, dat, bus)])

  def can_rx() -> list[tuple[int, bytes, int]]:
    packets = can_recv_packets(wait_for_one=True)
    return [
      (int(msg.address), bytes(msg.dat), int(msg.src))
      for packet in packets
      for msg in packet
    ]

  def request(bus: int, pdu: bytes, timeout: float | None = None) -> bytes | None:
    client = CanClient(can_tx, can_rx, TX_ADDR, RX_ADDR, bus)
    isotp = IsoTpMessage(client, timeout=args.timeout)
    isotp.send(pdu)
    deadline = time.monotonic() + (args.timeout if timeout is None else timeout)
    while True:
      remaining = deadline - time.monotonic()
      if remaining <= 0:
        return None
      try:
        response, _ = isotp.recv(timeout=remaining)
      except MessageTimeoutError:
        return None
      if response is None:
        continue
      response = bytes(response)
      if len(response) >= 3 and response[:2] == bytes((0x7F, pdu[0])) and response[2] == 0x78:
        print(f"  <- {response.hex()}  (response pending)", flush=True)
        continue
      return response

  bus = None
  print(f"probing 0x{TX_ADDR:03X}/0x{RX_ADDR:03X} with 10 01", flush=True)
  for candidate in BUSES:
    response = request(candidate, bytes.fromhex("1001"))
    print(f"  bus {candidate}: {describe_response(response)}", flush=True)
    if response is not None and response[:2] == bytes.fromhex("5001"):
      bus = candidate
      break

  if bus is None:
    print("no 50 01 response", flush=True)
    return 2

  print(f"using bus {bus}", flush=True)

  programming = request(bus, bytes.fromhex("1002"), timeout=max(args.timeout, 1.5))
  print(f"10 02 -> {describe_response(programming)}", flush=True)
  if programming is not None and not programming.startswith(bytes.fromhex("5002")):
    return 3

  # A programming-session transition can briefly make the endpoint disappear.
  # Retry only the seed request; there is no additional setup or probing here.
  seed_response = None
  for _ in range(20):
    seed_response = request(bus, bytes.fromhex("2701") + ZERO16)
    if seed_response is not None:
      break
    time.sleep(0.1)

  print(f"27 01 + zero16 -> {describe_response(seed_response)}", flush=True)
  if seed_response is None or not seed_response.startswith(bytes.fromhex("6701")):
    return 4

  seed = seed_response[2:]
  if len(seed) != 16:
    print(f"unexpected seed length: {len(seed)}", flush=True)
    return 5

  key = derive_key(seed)
  print(f"seed = {seed.hex()}", flush=True)
  print(f"key  = {key.hex()}", flush=True)

  key_response = request(bus, bytes.fromhex("2702") + key)
  print(f"27 02 + key -> {describe_response(key_response)}", flush=True)
  if key_response is None or not key_response.startswith(bytes.fromhex("6702")):
    return 6

  print("SUCCESS: bootloader SecurityAccess 01/02 accepted", flush=True)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
