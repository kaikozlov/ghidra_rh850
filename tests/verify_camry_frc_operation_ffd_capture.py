#!/usr/bin/env python3
"""Verify the read-only exact-Camry FRC Operation-FFD acquisition tool."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.targets.camry.live import camry_frc_operation_ffd_capture as cap

passed = failed = 0


def check(label: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][camry_frc_operation_ffd_capture] {label}" +
          (f" ({detail})" if detail else ""))


check("AB11 builder", cap.build_ab11() == bytes.fromhex("ab11"))
check("AB12 builder", cap.build_ab12(0x2845) == bytes.fromhex("ab122845"))
check("AB13 builder", cap.build_ab13(0x2845, 0x1234) == bytes.fromhex("ab1328451234"))
check("all proprietary requests fit classic CAN single frames",
      all(len(pdu) <= 7 for pdu in (cap.build_ab11(), cap.build_ab12(0x2845), cap.build_ab13(0x2845, 0x1234))))

robs = cap.parse_eb11(bytes.fromhex("eb11209d28182845240f"))
check("EB11 parser", robs == [0x209D, 0x2818, 0x2845, 0x240F])
records = cap.parse_eb12(bytes.fromhex("eb122845000100020010"), 0x2845)
check("EB12 parser + behavior echo", records == [1, 2, 0x10])

# One synthetic EB13 snapshot carrying the exact request/arbitration/state DIDs
# used by the current acquisition plan.
blocks = [
    (0x5282, bytes.fromhex("0b04d26432")),          # ID11, +1.234, gains 1.00/0.50
    (0x5631, bytes.fromhex("0bff066432")),          # ID11, -0.250
    (0x5285, bytes.fromhex("0b")),
    (0x57DE, bytes.fromhex("01f4")),                # +0.500
    (0x560D, bytes.fromhex("010002ff9c0100")),      # EPS pinion -0.100
]
stream = b"".join(did.to_bytes(2, "big") + bytes((len(data),)) + data for did, data in blocks)
pdu = bytes.fromhex("eb1328451234") + bytes((len(blocks),)) + stream
count, parsed = cap.parse_eb13(pdu, 0x2845, 0x1234)
check("EB13 declared-count parser", count == len(blocks) and [(b.data_id, b.data) for b in parsed] == blocks)

zero_count_pdu = bytes.fromhex("eb1328451234") + b"\x00" + stream
zero_count, zero_parsed = cap.parse_eb13(zero_count_pdu, 0x2845, 0x1234)
check("EB13 zero-count derives block count by scanning", zero_count == 0 and len(zero_parsed) == len(blocks))

try:
    cap.parse_eb13(bytes.fromhex("eb1328451234015282050b04"), 0x2845, 0x1234)
except cap.ProtocolError:
    malformed_rejected = True
else:
    malformed_rejected = False
check("EB13 truncated block rejected", malformed_rejected)

semantics = cap.load_recorder_semantics()
decoded = {row["data_id"]: row for row in cap.decode_blocks(parsed, semantics)}

def sig(did: str, name: str) -> dict:
    return next(row for row in decoded[did]["decoded"] if row["name"] == name)

check("5282 generic lateral ID decode", sig("0x5282", "TSS request - lateral ID")["raw"] == 11)
check("5282 generic pinion angle decode", sig("0x5282", "TSS request - pinion angle")["physical"] == "1.234")
check("5282 steering-assist gain decode", sig("0x5282", "Steering assist gain")["physical"] == "1.00")
check("5282 damping gain decode", sig("0x5282", "Damping control gain")["physical"] == "0.50")
check("5631 LTA negative pinion angle decode", sig("0x5631", "LTA Control Request Pinion Angle")["physical"] == "-0.250")
check("5285 arbitration ID decode", sig("0x5285", "Arbitration result_lateral ID")["raw"] == 11)
check("57DE arbitration pinion angle decode", sig("0x57DE", "Arbitration result Pinion angle")["physical"] == "0.500")
check("560D EPS pinion angle decode", sig("0x560D", "EPS Pinion Angle")["physical"] == "-0.100")

# MSB0 bit extraction matters for support/under-control flags.  The current
# 5265 metadata locates the seven one-bit fields at MSB positions in its payload.
flag_payload = bytearray(14)
flag_payload[1] = 0x80
flag_payload[13] = 0x80
flag_block = cap.RecorderBlock(0x5265, bytes(flag_payload))
flags = cap.decode_blocks([flag_block], semantics)[0]["decoded"]
flags_by_name = {row["name"]: row for row in flags}
check("5265 ABS under-control MSB0 decode", flags_by_name["ABS under-control"]["raw"] == 1)
check("5265 active-steering under-control MSB0 decode", flags_by_name["Active steering under-control flag"]["raw"] == 1)
check("5265 unset VSC under-control decode", flags_by_name["VSC under-control"]["raw"] == 0)

check("UDS negative parser", cap.negative_response(bytes.fromhex("7fab31")) == {
    "request_sid": "0xAB", "nrc": "0x31", "raw": "7fab31"
})

plan = cap.plan()
check("plan exact FRC route and identity guard", plan["target"] == {
    "tx": "0x792", "rx": "0x79A", "panda_bus": 0, "f181_contains": "8646F3315000"
})
check("plan uses only ordinary extended/default session around Operation FFD",
      plan["session"] == {"enter": "10 03", "leave": "10 01"})
check("plan has no SecurityAccess/RC/WDBI/flash/active-test/vehicle-control TX",
      not any(plan[key] for key in (
          "security_access", "routine_control", "write_data_by_identifier",
          "flash_write", "active_test", "vehicle_control_tx")))
check("plan includes request/arbitration/plant-state DIDs",
      {"0x5282", "0x5631", "0x5285", "0x57DE", "0x5265", "0x560D"} <= set(plan["focus_dids"]))

proc = subprocess.run(
    [sys.executable, str(REPO / "tools/targets/camry/live/camry_frc_operation_ffd_capture.py")],
    cwd=REPO, text=True, capture_output=True,
)
try:
    cli_plan = json.loads(proc.stdout)
except json.JSONDecodeError:
    cli_plan = {}
check("CLI defaults to plan-only and emits no live action", proc.returncode == 0 and cli_plan == plan,
      proc.stderr.strip())

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
