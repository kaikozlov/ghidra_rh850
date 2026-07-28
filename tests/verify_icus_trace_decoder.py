#!/usr/bin/env python3
"""Verify passive ISO-TP decoding of the DID 0x1010 key-update workflow."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.decode_icus_key_update_trace import decode_trace

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        suffix = f" ({detail})" if detail else ""
        print(f"FAIL: {name}{suffix}")


def isotp(can_id: int, pdu: bytes, timestamp: float) -> list[str]:
    frames: list[bytes] = []
    if len(pdu) <= 7:
        frames.append(bytes([len(pdu)]) + pdu)
    else:
        frames.append(bytes([0x10 | (len(pdu) >> 8), len(pdu) & 0xFF]) + pdu[:6])
        offset = 6
        sequence = 1
        while offset < len(pdu):
            frames.append(bytes([0x20 | sequence]) + pdu[offset : offset + 7])
            offset += 7
            sequence = (sequence + 1) & 0x0F
    return [
        f"({timestamp + index * 0.001:.6f}) can0 {can_id:X}#{frame.hex().upper()}"
        for index, frame in enumerate(frames)
    ]


m1 = bytes(range(15)) + bytes([0x47])
m2 = bytes(range(0x20, 0x40))
m3 = bytes(range(0x40, 0x50))
m4 = bytes(range(0x50, 0x70))
m5 = bytes(range(0x70, 0x80))

trace = []
trace += isotp(0x7A1, bytes.fromhex("1003"), 1.0)
trace += isotp(0x7A9, bytes.fromhex("5003"), 1.1)
trace += isotp(0x7A1, bytes.fromhex("2e011010") + m1 + m2 + m3, 2.0)
trace += ["(2.020000) can0 7A9#3000000000000000"]  # ECU flow control
trace += isotp(0x7A9, bytes.fromhex("6e01101001") + bytes(48), 2.1)
trace += ["(2.120000) can0 7A1#3000000000000000"]  # tester flow control
trace += isotp(0x7A1, bytes.fromhex("2e031010"), 3.0)
trace += isotp(0x7A9, bytes.fromhex("6e03101002") + m4 + m5, 3.1)
trace += ["(3.120000) can0 7A1#3000000000000000"]
trace += isotp(0x7A9, bytes.fromhex("7f2e24"), 4.0)

events, warnings = decode_trace(trace, show_package=True)
check("synthetic trace decodes without warnings", warnings == [], repr(warnings))
check(
    "session transition request/positive response are retained",
    [event["event"] for event in events[:2]]
    == ["diagnostic_session_request", "diagnostic_session_positive"],
)

start = next(event for event in events if event["event"] == "key_update_start")
check("start request requires the exact 64-byte package", start["valid_length"] is True)
check("M1 target slot is decoded from its high nibble", start["target_slot"] == 4)
check("M1 AuthID is decoded from its low nibble", start["auth_slot"] == 7)
check("M1/M2/M3 boundaries survive ISO-TP reassembly", start["m1"] == m1.hex())
check("M2 is exactly 32 bytes", start["m2"] == m2.hex())
check("M3 is exactly 16 bytes", start["m3"] == m3.hex())

accepted = next(
    event for event in events if event["event"] == "key_update_start_positive"
)
check("selector-1 response exposes pending status 0x01", accepted["status"] == 1)
check("pending response does not claim a proof", accepted["proof_present"] is False)

poll = next(event for event in events if event["event"] == "key_update_result_request")
check("selector-3 result request has no payload", poll["valid_length"] is True)

result = next(
    event for event in events if event["event"] == "key_update_result_positive"
)
check("terminal status 0x02 is named complete", result["status_name"] == "complete")
check("complete response carries a proof", result["proof_present"] is True)
check("M4/M5 result boundaries survive ISO-TP reassembly", result["m4"] == m4.hex())
check("M5 is exactly 16 bytes", result["m5"] == m5.hex())

negative = next(event for event in events if event["event"] == "key_update_negative")
check(
    "NRC 0x24 is decoded as requestSequenceError",
    negative["nrc_name"] == "requestSequenceError",
)

redacted, _ = decode_trace(trace)
redacted_start = next(
    event for event in redacted if event["event"] == "key_update_start"
)
check("package bytes are redacted by default", "m1" not in redacted_start)
check("redacted output retains component hashes", "m1_sha256" in redacted_start)

broken = isotp(0x7A1, bytes.fromhex("2e011010") + m1 + m2 + m3, 5.0)
broken[1] = broken[1].replace("#21", "#22")
_, broken_warnings = decode_trace(broken)
check(
    "ISO-TP sequence mismatch is reported",
    any("sequence mismatch" in warning for warning in broken_warnings),
    repr(broken_warnings),
)

bracketed, bracket_warnings = decode_trace(["can0 7A1 [3] 02 10 03"])
check("bracketed candump syntax decodes", bracket_warnings == [])
check(
    "bracketed single frame retains the extended-session request",
    bracketed[0]["event"] == "diagnostic_session_request"
    and bracketed[0]["session"] == 3,
)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
