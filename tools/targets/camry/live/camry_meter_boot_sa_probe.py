#!/usr/bin/env python3
"""Probe the Camry combination meter bootloader SecurityAccess path.

Run this while holding the cooperative direct-Panda lease. The probe uses the
confirmed meter diagnostic route: Panda bus 1 with ELM327 parameter 0 (OBD mux),
0x7C0 -> 0x7C8.

Sequence:
  10 01
  10 03
  10 02
  27 01 || zero16
  27 02 || derived_key

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


def load_openpilot():
  try:
    from panda import Panda  # type: ignore
    from opendbc.car.structs import CarParams  # type: ignore
    from opendbc.car.uds import (  # type: ignore
      ACCESS_TYPE,
      MessageTimeoutError,
      NegativeResponseError,
      SESSION_TYPE,
      UdsClient,
    )
    return Panda, CarParams, UdsClient, SESSION_TYPE, ACCESS_TYPE, MessageTimeoutError, NegativeResponseError
  except ModuleNotFoundError:
    for root in (Path("/data/openpilot"), Path("/data/openpilot/current")):
      if root.is_dir():
        sys.path.insert(0, str(root))
        try:
          from panda import Panda  # type: ignore
          from opendbc.car.structs import CarParams  # type: ignore
          from opendbc.car.uds import (  # type: ignore
            ACCESS_TYPE,
            MessageTimeoutError,
            NegativeResponseError,
            SESSION_TYPE,
            UdsClient,
          )
          return Panda, CarParams, UdsClient, SESSION_TYPE, ACCESS_TYPE, MessageTimeoutError, NegativeResponseError
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
  parser.add_argument("--timeout", type=float, default=0.75)
  args = parser.parse_args()

  (
    Panda, CarParams, UdsClient, SESSION_TYPE, ACCESS_TYPE,
    MessageTimeoutError, NegativeResponseError,
  ) = load_openpilot()

  serials = Panda.list()
  if len(serials) != 1:
    raise RuntimeError(f"expected one Panda, got {serials}")

  panda = Panda(serials[0], cli=False, disable_checks=False)
  try:
    panda.set_heartbeat_disabled()
    panda.set_safety_mode(CarParams.SafetyModel.elm327, 0)

    def client() -> object:
      return UdsClient(
        panda, TX_ADDR, RX_ADDR, BUS,
        timeout=args.timeout, response_pending_timeout=2.0,
      )

    c = client()
    try:
      c.diagnostic_session_control(SESSION_TYPE.DEFAULT)
      print("10 01 -> 50 01", flush=True)
    except NegativeResponseError as e:
      print(f"10 01 -> NRC 0x{int(e.error_code):02X}", flush=True)
      return 2
    except MessageTimeoutError:
      print("10 01 -> timeout", flush=True)
      return 2

    try:
      c.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)
      print("10 03 -> 50 03", flush=True)
    except NegativeResponseError as e:
      print(f"10 03 -> NRC 0x{int(e.error_code):02X}", flush=True)
      return 3
    except MessageTimeoutError:
      print("10 03 -> timeout", flush=True)
      return 3

    try:
      c.diagnostic_session_control(SESSION_TYPE.PROGRAMMING)
      print("10 02 -> 50 02", flush=True)
    except NegativeResponseError as e:
      print(f"10 02 -> NRC 0x{int(e.error_code):02X}", flush=True)
      return 4
    except MessageTimeoutError:
      print("10 02 -> timeout; trying boot SecurityAccess", flush=True)

    seed = None
    for _ in range(20):
      c = client()
      try:
        seed = bytes(c.security_access(ACCESS_TYPE.REQUEST_SEED, data_record=ZERO16))
        break
      except MessageTimeoutError:
        time.sleep(0.1)
      except NegativeResponseError as e:
        print(f"27 01 + zero16 -> NRC 0x{int(e.error_code):02X}", flush=True)
        return 5

    if seed is None:
      print("27 01 + zero16 -> timeout", flush=True)
      return 5
    if len(seed) != 16:
      print(f"27 01 + zero16 -> unexpected {len(seed)}-byte seed: {seed.hex()}", flush=True)
      return 6

    print(f"27 01 + zero16 -> 67 01 {seed.hex()}", flush=True)
    key = derive_key(seed)
    print(f"derived key = {key.hex()}", flush=True)

    c = client()
    try:
      c.security_access(ACCESS_TYPE.SEND_KEY, security_key=key)
    except NegativeResponseError as e:
      print(f"27 02 + key -> NRC 0x{int(e.error_code):02X}", flush=True)
      return 7
    except MessageTimeoutError:
      print("27 02 + key -> timeout", flush=True)
      return 7

    print("27 02 + key -> 67 02", flush=True)
    print("SUCCESS: meter boot SecurityAccess accepted", flush=True)
    return 0
  finally:
    panda.close()


if __name__ == "__main__":
  raise SystemExit(main())
