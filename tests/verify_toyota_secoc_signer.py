#!/usr/bin/env python3
"""Verify the independent Toyota classic-CAN SecOC signer."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_secoc_signer import (
    build_normal_authenticated_input,
    build_sync_authenticated_input,
    pack_normal_freshness,
    sign_classic_frame,
    sign_sync_frame,
)

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        suffix = f" ({detail})" if detail else ""
        print(f"[FAIL] {name}{suffix}")


def rejects(name: str, callback, exception=ValueError) -> None:
    try:
        callback()
    except exception:
        check(name, True)
    except Exception as error:  # noqa: BLE001 - verification reports the wrong type.
        check(name, False, f"wrong exception {type(error).__name__}: {error}")
    else:
        check(name, False, "accepted invalid input")


KEY = bytes(range(16))
TRIP = 0x1234
RESET = 0x56789
MESSAGE = 0xAB
PAYLOAD = bytes.fromhex("11223344")

print("== normal protected frame ==")
freshness = pack_normal_freshness(TRIP, RESET, MESSAGE)
check("freshness packing matches firmware-derived reference", freshness.hex() == "123456789ab4", freshness.hex())
check("freshness is six bytes", len(freshness) == 6)
check("freshness leaves two low padding bits clear", freshness[-1] & 0x03 == 0)

authenticated = build_normal_authenticated_input(0x2E4, PAYLOAD, TRIP, RESET, MESSAGE)
check(
    "normal authenticated input is DataID_be16 || payload4 || freshness48",
    authenticated.hex() == "02e411223344123456789ab4",
    authenticated.hex(),
)
frame = sign_classic_frame(KEY, 0x2E4, PAYLOAD, TRIP, RESET, MESSAGE)
check("normal known-answer frame", frame.hex() == "11223344d7bd232c", frame.hex())
check("normal frame is exact classic DLC 8", len(frame) == 8)
check("authentic payload is unchanged", frame[:4] == PAYLOAD)
check("transmitted freshness nibble is message-low2 || reset-low2", frame[4] >> 4 == 0xD)
check(
    "known-answer transmitted tag is the first 28 CMAC bits",
    int.from_bytes(frame[4:], "big") & 0x0FFFFFFF == 0x07BD232C,
)

print("\n== synchronization frame ==")
sync_authenticated = build_sync_authenticated_input(TRIP, RESET)
check(
    "sync authenticated input is DataID_be16 || trip16 || reset20 || pad4",
    sync_authenticated.hex() == "000f1234567890",
    sync_authenticated.hex(),
)
sync_frame = sign_sync_frame(KEY, TRIP, RESET)
check("sync known-answer frame", sync_frame.hex() == "12345678957bc857", sync_frame.hex())
check("sync frame is exact classic DLC 8", len(sync_frame) == 8)
check("sync frame carries trip16 and reset20 verbatim", sync_frame.hex().startswith("123456789"))
check("sync known-answer transmitted tag", int.from_bytes(sync_frame, "big") & 0x0FFFFFFF == 0x057BC857)

print("\n== boundaries and validation ==")
check(
    "maximum counters pack without overflow",
    pack_normal_freshness(0xFFFF, 0xFFFFF, 0xFF).hex() == "fffffffffffc",
)
check(
    "signer is DataID-generic within standard CAN",
    len(sign_classic_frame(KEY, 0x183, bytes(4), 0, 0, 0)) == 8,
)
rejects("AES key must be exactly 16 bytes", lambda: sign_classic_frame(bytes(15), 0x2E4, PAYLOAD, 0, 0, 0))
rejects("authentic payload must be exactly four bytes", lambda: sign_classic_frame(KEY, 0x2E4, bytes(5), 0, 0, 0))
rejects("extended CAN IDs are outside this profile", lambda: sign_classic_frame(KEY, 0x1234, PAYLOAD, 0, 0, 0))
rejects("trip counter is unsigned 16-bit", lambda: sign_classic_frame(KEY, 0x2E4, PAYLOAD, 0x10000, 0, 0))
rejects("reset counter is unsigned 20-bit", lambda: sign_classic_frame(KEY, 0x2E4, PAYLOAD, 0, 0x100000, 0))
rejects("message counter is unsigned 8-bit", lambda: sign_classic_frame(KEY, 0x2E4, PAYLOAD, 0, 0, 0x100))

print("\n== command-line interface ==")
environment = os.environ.copy()
environment["TOYOTA_SECOC_KEY"] = KEY.hex()
signer = REPO / "tools" / "toyota_secoc_signer.py"
normal_cli = subprocess.run(
    [
        sys.executable,
        str(signer),
        "sign",
        "--can-id", "0x2e4",
        "--payload", PAYLOAD.hex(),
        "--trip", hex(TRIP),
        "--reset", hex(RESET),
        "--message", hex(MESSAGE),
    ],
    check=False,
    capture_output=True,
    text=True,
    env=environment,
)
check("CLI normal invocation exits successfully", normal_cli.returncode == 0, normal_cli.stderr.strip())
check(
    "CLI emits candump-compatible normal output",
    normal_cli.stdout.strip() == "2E4#11223344D7BD232C",
    normal_cli.stdout.strip(),
)

sync_cli = subprocess.run(
    [sys.executable, str(signer), "sync", "--trip", hex(TRIP), "--reset", hex(RESET)],
    check=False,
    capture_output=True,
    text=True,
    env=environment,
)
check("CLI sync invocation exits successfully", sync_cli.returncode == 0, sync_cli.stderr.strip())
check(
    "CLI emits candump-compatible sync output",
    sync_cli.stdout.strip() == "00F#12345678957BC857",
    sync_cli.stdout.strip(),
)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
