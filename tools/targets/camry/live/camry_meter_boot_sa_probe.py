"""Reproduce the non-gateway GTS+ P5-Unified meter preparation and boot SA.

Run this while holding the cooperative direct-Panda lease. The confirmed meter
route is the TSS3/F-CAM splice on Panda bus 1, 0x7C0 -> 0x7C8.

The wire sequence follows TCUWCanUnifiedPrepareWriter.dll: functional session
and TesterPresent traffic, DTC suppression, diagnostic masking, communication
control, software-ID read, physical 10 02, the fixed two-second handoff delay,
and boot SecurityAccess. Central-gateway discovery, automatic-IG-off handling,
gateway SecurityAccess, and gateway routines are intentionally omitted.

It performs no DID writes, download, transfer, RoutineControl, or ECU reset SID.
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
from pathlib import Path

from Crypto.Cipher import AES

TX_ADDR = 0x7C0
RX_ADDR = 0x7C8
BUS = 1

STANDARD_FUNCTIONAL_ADDR = 0x777
EXTENDED_FUNCTIONAL_ADDR = 0x77F
EXTENDED_FUNCTIONAL_SUBADDR = 0xFE
DIAGNOSTIC_MASK_ADDR = 0x720
PHASE6_FUNCTIONAL_ADDR = 0x18DBEFE0
TRACE_TX_ADDRS = {
  TX_ADDR,
  STANDARD_FUNCTIONAL_ADDR,
  EXTENDED_FUNCTIONAL_ADDR,
  DIAGNOSTIC_MASK_ADDR,
  PHASE6_FUNCTIONAL_ADDR,
}

ALLOUTPUT_PASSTHROUGH_PARAM = 1
PREPARATION_FRAME_COUNT = 26
TX_ACCEPTED_BUS = BUS + 128
TX_REJECTED_BUS = BUS + 192
TESTER_PRESENT_PERIOD = 2.0
TESTER_PRESENT_INTERMESSAGE = 0.1
ZERO16 = bytes(16)

# Recovered from the 2024 RAV4 Prime RH850 meter specimen.
METER_BOOT_SA_ROOT = bytes.fromhex("f579ca07326b246812a31464b123cbc6")


def _address_text(address: int) -> str:
  return f"{address:08X}" if address > 0x7FF else f"{address:03X}"


def _describe_frame(address: int, data: bytes) -> str:
  if not data:
    return "empty"
  if address == DIAGNOSTIC_MASK_ADDR:
    return "raw diagnostic mask"

  prefix = ""
  if address == EXTENDED_FUNCTIONAL_ADDR and data[0] == EXTENDED_FUNCTIONAL_SUBADDR:
    prefix = "EA FE "
    data = data[1:]
    if not data:
      return prefix + "empty"

  frame_type = data[0] >> 4
  if frame_type == 0:
    length = data[0] & 0x0F
    return prefix + f"SF {data[1:1 + length].hex()}"
  if frame_type == 1 and len(data) >= 2:
    length = ((data[0] & 0x0F) << 8) | data[1]
    return prefix + f"FF len={length} {data[2:].hex()}"
  if frame_type == 2:
    return prefix + f"CF sn={data[0] & 0x0F} {data[1:].hex()}"
  if frame_type == 3:
    return (
      prefix
      + f"FC fs={data[0] & 0x0F} bs={data[1] if len(data) > 1 else 0} "
      + f"stmin={data[2] if len(data) > 2 else 0}"
    )
  return prefix + "unknown"


class TracedPanda:
  def __init__(self, panda):
    self._panda = panda
    self._io_lock = threading.Lock()
    self._accepted_tx = 0
    self._rejected_tx = 0

  def can_send(self, address, data, bus, *args, **kwargs):
    address = int(address)
    bus = int(bus)
    payload = bytes(data)
    if address in TRACE_TX_ADDRS and bus == BUS:
      print(
        f"CAN TX {_address_text(address)} bus {bus}: {payload.hex()} "
        f"[{_describe_frame(address, payload)}]",
        flush=True,
      )
    with self._io_lock:
      return self._panda.can_send(address, data, bus, *args, **kwargs)

  def can_recv(self):
    with self._io_lock:
      messages = self._panda.can_recv() or []
    for address, data, bus in messages:
      address = int(address)
      source = int(bus)
      payload = bytes(data)
      if address in TRACE_TX_ADDRS and source in {TX_ACCEPTED_BUS, TX_REJECTED_BUS}:
        accepted = source == TX_ACCEPTED_BUS
        if accepted:
          self._accepted_tx += 1
        else:
          self._rejected_tx += 1
        status = "accepted" if accepted else "REJECTED"
        print(
          f"CAN TX {status} {_address_text(address)} bus {BUS}: {payload.hex()}",
          flush=True,
        )
      elif address == RX_ADDR and source == BUS:
        print(
          f"CAN RX {_address_text(address)} bus {source}: {payload.hex()} "
          f"[{_describe_frame(address, payload)}]",
          flush=True,
        )
    return messages

  def verify_tx_receipts(self, expected: int, timeout: float = 0.5) -> None:
    deadline = time.monotonic() + timeout
    while self._accepted_tx + self._rejected_tx < expected and time.monotonic() < deadline:
      self.can_recv()
      time.sleep(0.005)
    if self._rejected_tx or self._accepted_tx != expected:
      raise RuntimeError(
        f"Panda preparation receipts: accepted={self._accepted_tx}, "
        f"rejected={self._rejected_tx}, expected={expected}"
      )
    print(f"Panda preparation receipts: {self._accepted_tx}/{expected} accepted", flush=True)


def _single_frame(payload: bytes, subaddress: int | None = None) -> bytes:
  maximum = 6 if subaddress is not None else 7
  if not payload or len(payload) > maximum:
    raise ValueError(f"functional payload must contain 1..{maximum} bytes")
  frame = bytes([len(payload)]) + payload
  if subaddress is not None:
    frame = bytes([subaddress]) + frame
  return frame.ljust(8, b"\x00")


def _send_functional(
  panda: TracedPanda,
  address: int,
  payload: bytes,
  *,
  subaddress: int | None = None,
) -> None:
  panda.can_send(address, _single_frame(payload, subaddress), BUS)


def _send_tester_present_group(
  panda: TracedPanda,
  *,
  intermessage: float = 0.0,
  stop_event: threading.Event | None = None,
) -> None:
  messages = (
    (STANDARD_FUNCTIONAL_ADDR, None),
    (EXTENDED_FUNCTIONAL_ADDR, EXTENDED_FUNCTIONAL_SUBADDR),
    (PHASE6_FUNCTIONAL_ADDR, None),
  )
  for index, (address, subaddress) in enumerate(messages):
    if stop_event is not None and stop_event.is_set():
      return
    if index and intermessage:
      if stop_event is not None:
        if stop_event.wait(intermessage):
          return
      else:
        time.sleep(intermessage)
    _send_functional(panda, address, bytes.fromhex("3e80"), subaddress=subaddress)


class PeriodicTesterPresent:
  def __init__(self, panda: TracedPanda):
    self._panda = panda
    self._thread: threading.Thread | None = None
    self._stop_event: threading.Event | None = None
    self._error: Exception | None = None

  def start(self, initial_delay: float) -> None:
    self.stop()
    stop_event = threading.Event()
    self._stop_event = stop_event
    self._error = None
    self._thread = threading.Thread(
      target=self._run,
      args=(stop_event, initial_delay),
      name="meter-gts-periodic-tester-present",
      daemon=True,
    )
    self._thread.start()

  def stop(self) -> None:
    if self._thread is None:
      return
    assert self._stop_event is not None
    self._stop_event.set()
    self._thread.join()
    self._thread = None
    self._stop_event = None
    if self._error is not None:
      error = self._error
      self._error = None
      raise RuntimeError("periodic TesterPresent sender failed") from error

  def _run(self, stop_event: threading.Event, initial_delay: float) -> None:
    try:
      if stop_event.wait(initial_delay):
        return
      next_group = time.monotonic()
      while not stop_event.is_set():
        _send_tester_present_group(
          self._panda,
          intermessage=TESTER_PRESENT_INTERMESSAGE,
          stop_event=stop_event,
        )
        next_group += TESTER_PRESENT_PERIOD
        if stop_event.wait(max(0.0, next_group - time.monotonic())):
          return
    except Exception as error:  # noqa: BLE001 - propagate transport failures to the owner thread
      self._error = error


def _parse_hex16(value: str) -> bytes:
  try:
    result = bytes.fromhex(value)
  except ValueError as error:
    raise argparse.ArgumentTypeError("expected 32 hexadecimal digits") from error
  if len(result) != 16:
    raise argparse.ArgumentTypeError("expected 32 hexadecimal digits")
  return result


def _is_known_application_f181(response: bytes) -> bool:
  if not response.startswith(bytes.fromhex("62f18103")) or len(response) < 52:
    return False
  payload = response[4:52]
  slots = [payload[index * 16:(index + 1) * 16].rstrip(b"\x00") for index in range(3)]
  return slots == [b"8381GAQ02100", b"", b"8381FAQ01200"]


def load_openpilot():
  try:
    from opendbc.car.structs import CarParams  # type: ignore
    from opendbc.car.uds import CanClient, IsoTpMessage, MessageTimeoutError  # type: ignore
    from panda import Panda  # type: ignore
    return Panda, CarParams, CanClient, IsoTpMessage, MessageTimeoutError
  except ModuleNotFoundError:
    for root in (Path("/data/openpilot"), Path("/data/openpilot/current")):
      if root.is_dir():
        sys.path.insert(0, str(root))
        try:
          from opendbc.car.structs import CarParams  # type: ignore
          from opendbc.car.uds import CanClient, IsoTpMessage, MessageTimeoutError  # type: ignore
          from panda import Panda  # type: ignore
          return Panda, CarParams, CanClient, IsoTpMessage, MessageTimeoutError
        except ModuleNotFoundError:
          pass
  raise SystemExit("cannot import panda/opendbc; run this on the comma in its openpilot environment")


def derive_key(seed: bytes, boot_root: bytes, ecu_auth_key: bytes) -> bytes:
  if len(seed) != 16:
    raise ValueError(f"expected 16-byte seed, got {len(seed)}")
  working_key = AES.new(boot_root, AES.MODE_ECB).decrypt(ecu_auth_key)
  return AES.new(working_key, AES.MODE_ECB).encrypt(seed)


def _wait_while_draining(panda: TracedPanda, duration: float) -> None:
  deadline = time.monotonic() + duration
  while time.monotonic() < deadline:
    panda.can_recv()


def _prepare_non_gateway(
  panda: TracedPanda,
  periodic: PeriodicTesterPresent,
  *,
  wake_wait: float,
  diagnostic_mask_wait: float,
) -> None:
  if wake_wait:
    print(f"GTS prepare: package wake-up delay {wake_wait:g}s", flush=True)
    _wait_while_draining(panda, wake_wait)

  print("GTS prepare: functional 10 83 and one-shot TesterPresent group", flush=True)
  _send_functional(panda, STANDARD_FUNCTIONAL_ADDR, bytes.fromhex("1083"))
  _wait_while_draining(panda, 1.0)
  _send_tester_present_group(panda)
  _wait_while_draining(panda, 1.0)
  _send_functional(
    panda,
    EXTENDED_FUNCTIONAL_ADDR,
    bytes.fromhex("1083"),
    subaddress=EXTENDED_FUNCTIONAL_SUBADDR,
  )
  _send_functional(panda, PHASE6_FUNCTIONAL_ADDR, bytes.fromhex("1083"))
  _wait_while_draining(panda, 1.0)

  periodic.start(1.0)
  print("GTS prepare: omitting central-gateway and automatic-IG-off branches", flush=True)
  periodic.stop()

  print("GTS prepare: functional 85 82 and diagnostic mask", flush=True)
  _send_functional(panda, STANDARD_FUNCTIONAL_ADDR, bytes.fromhex("8582"))
  _wait_while_draining(panda, 1.0)
  _send_tester_present_group(panda)
  _wait_while_draining(panda, 1.0)
  _send_functional(
    panda,
    EXTENDED_FUNCTIONAL_ADDR,
    bytes.fromhex("8582"),
    subaddress=EXTENDED_FUNCTIONAL_SUBADDR,
  )
  _wait_while_draining(panda, 1.0)
  _send_tester_present_group(panda)
  _wait_while_draining(panda, 1.0)
  for _ in range(3):
    panda.can_send(DIAGNOSTIC_MASK_ADDR, bytes.fromhex("a027"), BUS)
    _wait_while_draining(panda, diagnostic_mask_wait)
  _wait_while_draining(panda, 0.9)

  print("GTS prepare: non-emissions functional 28 81/83 01", flush=True)
  _send_tester_present_group(panda)
  _wait_while_draining(panda, 1.0)
  _send_functional(panda, STANDARD_FUNCTIONAL_ADDR, bytes.fromhex("288101"))
  _wait_while_draining(panda, 1.0)
  _send_tester_present_group(panda)
  _wait_while_draining(panda, 1.0)
  _send_functional(
    panda,
    EXTENDED_FUNCTIONAL_ADDR,
    bytes.fromhex("288101"),
    subaddress=EXTENDED_FUNCTIONAL_SUBADDR,
  )
  _send_functional(panda, PHASE6_FUNCTIONAL_ADDR, bytes.fromhex("288301"))
  _wait_while_draining(panda, 1.0)
  periodic.start(1.0)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--wake-wait",
    type=float,
    default=0.0,
    help="package WakeUpTimeAfterReset delay before preparation; exact meter CUW value is unavailable",
  )
  parser.add_argument(
    "--diagnostic-mask-wait",
    type=float,
    default=0.1,
    help="seconds after each raw 0x720:A027 frame; P5-Unified base calibration is 0.1",
  )
  parser.add_argument(
    "--session-wait",
    type=float,
    default=10.0,
    help="P4ServerMaxTime budget for a final 10 02 response",
  )
  parser.add_argument(
    "--post-session-wait",
    type=float,
    default=2.0,
    help="seconds after 50 02 before boot SecurityAccess; GTS Unified uses 2.0",
  )
  parser.add_argument("--response-slice", type=float, default=0.5)
  parser.add_argument("--ecu-auth-key", type=_parse_hex16, default=ZERO16)
  parser.add_argument("--boot-root", type=_parse_hex16, default=METER_BOOT_SA_ROOT)
  args = parser.parse_args()

  if min(
    args.wake_wait,
    args.diagnostic_mask_wait,
    args.session_wait,
    args.post_session_wait,
    args.response_slice,
  ) < 0:
    parser.error("timings must be non-negative")
  if args.session_wait == 0 or args.response_slice == 0:
    parser.error("--session-wait and --response-slice must be greater than zero")

  Panda, CarParams, CanClient, IsoTpMessage, MessageTimeoutError = load_openpilot()

  serials = Panda.list()
  if len(serials) != 1:
    raise RuntimeError(f"expected one Panda, got {serials}")

  panda = Panda(serials[0], cli=False, disable_checks=False)
  periodic: PeriodicTesterPresent | None = None
  try:
    panda.set_heartbeat_disabled()
    panda.set_obd(True)
    panda.set_safety_mode(CarParams.SafetyModel.allOutput, ALLOUTPUT_PASSTHROUGH_PARAM)
    traced_panda = TracedPanda(panda)
    periodic = PeriodicTesterPresent(traced_panda)

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

    _prepare_non_gateway(
      traced_panda,
      periodic,
      wake_wait=args.wake_wait,
      diagnostic_mask_wait=args.diagnostic_mask_wait,
    )
    traced_panda.verify_tx_receipts(PREPARATION_FRAME_COUNT)

    request_once("GTS ReadSoftwareID 22 F181", bytes.fromhex("22f181"))
    periodic.stop()
    periodic.start(1.0)
    periodic.stop()
    periodic.start(1.0)

    print("GTS target session: physical 10 02 with network TesterPresent active", flush=True)
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
      if saw_pending:
        request_once("pending-budget 3E 00", bytes.fromhex("3e00"))
      periodic.stop()

      f181 = request_once("postmortem 22 F181", bytes.fromhex("22f181"))
      if f181 is None or not f181.startswith(bytes.fromhex("62f181")):
        print("handoff unresolved: no 50 02 and no readable meter identity", flush=True)
        return 3
      if _is_known_application_f181(f181):
        f186 = request_once("postmortem 22 F186", bytes.fromhex("22f186"))
        diagnostic_session = (
          f"0x{f186[3]:02X}"
          if f186 is not None and f186.startswith(bytes.fromhex("62f186")) and len(f186) >= 4
          else "unknown"
        )
        print(f"application remains active; reported diagnostic session {diagnostic_session}", flush=True)
      else:
        print(f"unexpected F181 responder after failed 10 02: {f181.hex()}", flush=True)
      return 3

    if not final_response.startswith(bytes.fromhex("5002")) or len(final_response) < 6:
      print(
        f"10 02 -> unexpected final response; GTS requires 50 02 plus four timing bytes: "
        f"{final_response.hex()}",
        flush=True,
      )
      return 4

    p2_ms = int.from_bytes(final_response[2:4], "big")
    p2_star_ms = int.from_bytes(final_response[4:6], "big") * 10
    print(
      f"10 02 -> accepted; P2={p2_ms}ms P2*={p2_star_ms}ms: {final_response.hex()}",
      flush=True,
    )
    periodic.stop()
    periodic.start(0.0)
    time.sleep(args.post_session_wait)

    seed_request = message()
    seed_request.send(bytes.fromhex("2701") + args.ecu_auth_key)
    try:
      seed_response, _ = seed_request.recv(2.0)
    except MessageTimeoutError:
      print("27 01 + ECUAuthKey -> timeout", flush=True)
      return 5

    if seed_response is None:
      print("27 01 + ECUAuthKey -> no response", flush=True)
      return 5

    seed_response = bytes(seed_response)
    if seed_response.startswith(bytes.fromhex("7f27")):
      print(f"27 01 + ECUAuthKey -> {seed_response.hex()}", flush=True)
      return 5
    if not seed_response.startswith(bytes.fromhex("6701")):
      print(f"27 01 + ECUAuthKey -> unexpected response {seed_response.hex()}", flush=True)
      return 5

    seed = seed_response[2:]
    if len(seed) != 16:
      print(f"27 01 + ECUAuthKey -> unexpected {len(seed)}-byte seed: {seed.hex()}", flush=True)
      return 6

    print(f"27 01 + ECUAuthKey -> 67 01 {seed.hex()}", flush=True)
    key = derive_key(seed, args.boot_root, args.ecu_auth_key)
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
    if periodic is not None:
      try:
        periodic.stop()
      except RuntimeError as error:
        print(f"warning: {error}", file=sys.stderr, flush=True)
    try:
      panda.set_safety_mode(0)
      panda.set_obd(False)
    finally:
      panda.close()


if __name__ == "__main__":
  raise SystemExit(main())
