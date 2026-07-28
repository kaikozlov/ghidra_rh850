#!/usr/bin/env python3
"""Decode the application DID 0x1010 ICU-S key-update exchange from candump.

The application uses an OEM selector byte inside service 0x2E:

    2E 01 10 10 || M1[16] || M2[32] || M3[16]   start
    2E 03 10 10                                  read status/result

Positive replies carry the selector, DID, a one-byte status, and 48 result
bytes.  The decoder is passive: it reassembles ISO-TP and never transmits.
Package bytes are hashed by default because captures are vehicle-specific.
Use --show-package only when the output can be handled as sensitive material.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

REQUEST_ID = 0x7A1
RESPONSE_ID = 0x7A9
DID = 0x1010

STATUS_NAMES = {
    0x01: "pending",
    0x02: "complete",
    0xFF: "failed",
}

NRC_NAMES = {
    0x10: "generalReject",
    0x12: "subFunctionNotSupported",
    0x13: "incorrectMessageLengthOrInvalidFormat",
    0x14: "responseTooLong",
    0x22: "conditionsNotCorrect",
    0x24: "requestSequenceError",
    0x31: "requestOutOfRange",
    0x33: "securityAccessDenied",
    0x72: "generalProgrammingFailure",
    0x78: "requestCorrectlyReceivedResponsePending",
}

COMPACT_RE = re.compile(
    r"^\s*(?:\((?P<timestamp>[^)]+)\)\s+)?"
    r"(?P<interface>\S+)\s+(?P<can_id>[0-9A-Fa-f]+)"
    r"(?P<fd>##(?P<flags>[0-9A-Fa-f])|#)(?P<data>[0-9A-Fa-f]*)\s*$"
)
BRACKET_RE = re.compile(
    r"^\s*(?:\((?P<timestamp>[^)]+)\)\s+)?"
    r"(?P<interface>\S+)\s+(?P<can_id>[0-9A-Fa-f]+)\s+"
    r"\[(?P<dlc>\d+)\]\s+(?P<data>(?:[0-9A-Fa-f]{2}\s*)+)$"
)


@dataclass(frozen=True)
class CanFrame:
    line_number: int
    can_id: int
    data: bytes
    timestamp: str | None = None
    interface: str | None = None


@dataclass
class IsoTpAssembly:
    total_length: int
    payload: bytearray
    next_sequence: int = 1


class IsoTpReassembler:
    """Minimal normal-addressing ISO-TP reassembler for passive CAN traces."""

    def __init__(self) -> None:
        self._assemblies: dict[int, IsoTpAssembly] = {}

    def feed(self, frame: CanFrame) -> tuple[bytes | None, str | None]:
        if not frame.data:
            return None, "empty CAN payload"

        pci_type = frame.data[0] >> 4
        if pci_type == 0:
            length = frame.data[0] & 0x0F
            offset = 1
            if length == 0:
                if len(frame.data) < 2:
                    return None, "truncated extended single-frame header"
                length = frame.data[1]
                offset = 2
            if len(frame.data) - offset < length:
                return None, f"truncated single frame: need {length} payload bytes"
            self._assemblies.pop(frame.can_id, None)
            return frame.data[offset : offset + length], None

        if pci_type == 1:
            if len(frame.data) < 2:
                return None, "truncated first-frame header"
            total_length = ((frame.data[0] & 0x0F) << 8) | frame.data[1]
            offset = 2
            if total_length == 0:
                if len(frame.data) < 6:
                    return None, "truncated extended first-frame header"
                total_length = int.from_bytes(frame.data[2:6], "big")
                offset = 6
            assembly = IsoTpAssembly(total_length, bytearray(frame.data[offset:]))
            self._assemblies[frame.can_id] = assembly
            if len(assembly.payload) >= total_length:
                self._assemblies.pop(frame.can_id, None)
                return bytes(assembly.payload[:total_length]), None
            return None, None

        if pci_type == 2:
            assembly = self._assemblies.get(frame.can_id)
            if assembly is None:
                return None, "consecutive frame without an active first frame"
            sequence = frame.data[0] & 0x0F
            if sequence != assembly.next_sequence:
                self._assemblies.pop(frame.can_id, None)
                return (
                    None,
                    (
                        f"ISO-TP sequence mismatch: expected "
                        f"{assembly.next_sequence:X}, got {sequence:X}"
                    ),
                )
            assembly.next_sequence = (assembly.next_sequence + 1) & 0x0F
            assembly.payload.extend(frame.data[1:])
            if len(assembly.payload) >= assembly.total_length:
                self._assemblies.pop(frame.can_id, None)
                return bytes(assembly.payload[: assembly.total_length]), None
            return None, None

        if pci_type == 3:
            return None, None  # Flow-control frames carry no UDS payload.
        return None, f"unsupported ISO-TP PCI type 0x{pci_type:X}"


def parse_candump_line(line: str, line_number: int) -> CanFrame | None:
    """Parse compact (`can0 7A1#...`) or bracketed candump output."""
    match = COMPACT_RE.match(line)
    if match:
        data_hex = match.group("data")
    else:
        match = BRACKET_RE.match(line)
        if not match:
            return None
        data_hex = re.sub(r"\s+", "", match.group("data"))

    if len(data_hex) % 2:
        raise ValueError(f"line {line_number}: odd-length CAN payload")
    return CanFrame(
        line_number=line_number,
        can_id=int(match.group("can_id"), 16),
        data=bytes.fromhex(data_hex),
        timestamp=match.group("timestamp"),
        interface=match.group("interface"),
    )


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _component(event: dict[str, object], name: str, data: bytes, show: bool) -> None:
    event[f"{name}_sha256"] = _digest(data)
    if show:
        event[name] = data.hex()


def decode_uds(
    pdu: bytes,
    *,
    can_id: int,
    request_id: int = REQUEST_ID,
    response_id: int = RESPONSE_ID,
    show_package: bool = False,
) -> dict[str, object] | None:
    """Decode one reassembled UDS PDU relevant to the ICU-S update workflow."""
    if not pdu:
        return None

    if can_id == request_id and pdu[0] == 0x10 and len(pdu) >= 2:
        return {
            "event": "diagnostic_session_request",
            "session": pdu[1] & 0x7F,
            "suppress_positive_response": bool(pdu[1] & 0x80),
            "uds_length": len(pdu),
        }

    if can_id == response_id and pdu[0] == 0x50 and len(pdu) >= 2:
        return {
            "event": "diagnostic_session_positive",
            "session": pdu[1],
            "uds_length": len(pdu),
        }

    if can_id == response_id and len(pdu) >= 3 and pdu[:2] == b"\x7f\x2e":
        nrc = pdu[2]
        return {
            "event": "key_update_negative",
            "request_sid": 0x2E,
            "nrc": nrc,
            "nrc_name": NRC_NAMES.get(nrc, "unknown"),
            "uds_length": len(pdu),
        }

    if can_id == request_id and pdu[0] == 0x2E:
        if len(pdu) < 4 or int.from_bytes(pdu[2:4], "big") != DID:
            return None
        selector = pdu[1] & 0x7F
        common: dict[str, object] = {
            "selector": selector,
            "suppress_positive_response": bool(pdu[1] & 0x80),
            "did": f"0x{DID:04X}",
            "uds_length": len(pdu),
        }
        if selector == 1:
            event = {"event": "key_update_start", **common}
            package = pdu[4:]
            event["valid_length"] = len(package) == 64
            if len(package) == 64:
                m1, m2, m3 = package[:16], package[16:48], package[48:64]
                event["uid"] = m1[:15].hex() if show_package else "<redacted>"
                event["target_slot"] = m1[15] >> 4
                event["auth_slot"] = m1[15] & 0x0F
                _component(event, "m1", m1, show_package)
                _component(event, "m2", m2, show_package)
                _component(event, "m3", m3, show_package)
            return event
        if selector == 3:
            return {
                "event": "key_update_result_request",
                **common,
                "valid_length": len(pdu) == 4,
            }
        return {"event": "key_update_unknown_selector", **common}

    if can_id == response_id and pdu[0] == 0x6E:
        if len(pdu) < 4 or int.from_bytes(pdu[2:4], "big") != DID:
            return None
        selector = pdu[1] & 0x7F
        event = {
            "event": (
                "key_update_start_positive"
                if selector == 1
                else "key_update_result_positive"
                if selector == 3
                else "key_update_positive_unknown_selector"
            ),
            "selector": selector,
            "did": f"0x{DID:04X}",
            "uds_length": len(pdu),
            "valid_length": len(pdu) == 53,
        }
        if len(pdu) == 53:
            status = pdu[4]
            proof = pdu[5:]
            event["status"] = status
            event["status_name"] = STATUS_NAMES.get(status, "unknown")
            event["proof_present"] = status == 0x02
            _component(event, "m4", proof[:32], show_package)
            _component(event, "m5", proof[32:48], show_package)
        return event

    return None


def decode_trace(
    lines: Iterable[str],
    *,
    request_id: int = REQUEST_ID,
    response_id: int = RESPONSE_ID,
    show_package: bool = False,
) -> tuple[list[dict[str, object]], list[str]]:
    reassembler = IsoTpReassembler()
    events: list[dict[str, object]] = []
    warnings: list[str] = []

    for line_number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            frame = parse_candump_line(line, line_number)
        except ValueError as error:
            warnings.append(str(error))
            continue
        if frame is None:
            warnings.append(f"line {line_number}: unsupported candump syntax")
            continue
        if frame.can_id not in (request_id, response_id):
            continue
        pdu, warning = reassembler.feed(frame)
        if warning:
            warnings.append(f"line {line_number}: {warning}")
        if pdu is None:
            continue
        event = decode_uds(
            pdu,
            can_id=frame.can_id,
            request_id=request_id,
            response_id=response_id,
            show_package=show_package,
        )
        if event is not None:
            event["line"] = line_number
            event["can_id"] = f"0x{frame.can_id:X}"
            if frame.timestamp is not None:
                event["timestamp"] = frame.timestamp
            events.append(event)
    return events, warnings


def _parse_can_id(value: str) -> int:
    return int(value, 0)


def _human(event: dict[str, object]) -> str:
    prefix = f"line {event['line']} {event['can_id']}: {event['event']}"
    details: list[str] = []
    for key in (
        "session",
        "selector",
        "target_slot",
        "auth_slot",
        "status_name",
        "nrc_name",
        "valid_length",
    ):
        if key in event:
            details.append(f"{key}={event[key]}")
    return f"{prefix} {' '.join(details)}".rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "trace", nargs="?", default="-", help="candump file (default: stdin)"
    )
    parser.add_argument("--request-id", type=_parse_can_id, default=REQUEST_ID)
    parser.add_argument("--response-id", type=_parse_can_id, default=RESPONSE_ID)
    parser.add_argument(
        "--json", action="store_true", help="emit one JSON object per event"
    )
    parser.add_argument(
        "--show-package",
        action="store_true",
        help="include vehicle-specific M1-M5 bytes instead of hashes only",
    )
    args = parser.parse_args()

    if args.trace == "-":
        lines = sys.stdin
    else:
        lines = (
            Path(args.trace).read_text(encoding="utf-8", errors="replace").splitlines()
        )

    events, warnings = decode_trace(
        lines,
        request_id=args.request_id,
        response_id=args.response_id,
        show_package=args.show_package,
    )
    for event in events:
        if args.json:
            print(json.dumps(event, sort_keys=True))
        else:
            print(_human(event))
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
