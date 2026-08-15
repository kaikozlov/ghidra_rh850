#!/usr/bin/env python3
"""Verify the CONNECT-only XCP reachability discriminator and its no-write guard."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.followups.xcp_daq_probe import XcpDaqError  # noqa: E402
from exploit.followups.xcp_read_probe import CONNECT_REQUEST  # noqa: E402
from exploit.followups.xcp_reachability import (  # noqa: E402
    CONNECT_PID,
    FORBIDDEN_COMMANDS,
    SCHEMA,
    VERDICT_REACHABLE_ERROR,
    VERDICT_REACHABLE_POSITIVE,
    VERDICT_TIMEOUT,
    VERDICT_UNEXPECTED,
    XcpReachabilityError,
    assert_connect_only,
    build_plan,
    classify_response,
    forbidden_opcode_audit,
)

passed = failed = 0


def check(label: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {label}{suffix}")


print("== CONNECT-only guard ==")
check("schema pinned as v1", SCHEMA == "sienna-xcp-reachability-v1")
assert_connect_only(CONNECT_REQUEST)
check("stock CONNECT frame passes the guard", True)
for opcode in (0xE4, 0xF0, 0xEC, 0xF6, 0xF5, 0xF4, 0xE3, 0xE2, 0xE1, 0xE0, 0xDE):
    try:
        assert_connect_only(bytes([opcode]) + bytes(7))
    except XcpReachabilityError:
        check(f"opcode 0x{opcode:02X} is refused", True)
    else:
        check(f"opcode 0x{opcode:02X} is refused", False)
try:
    assert_connect_only(CONNECT_REQUEST + b"\x00")
except XcpReachabilityError:
    check("non-eight-byte request is refused", True)
else:
    check("non-eight-byte request is refused", False)
check(
    "E4 refusal names the shadow-window mutation explicitly",
    "shadow" in FORBIDDEN_COMMANDS[0xE4].lower() and "mutates" in FORBIDDEN_COMMANDS[0xE4].lower(),
)
check("generic write opcodes F0/EC are in the forbidden table", 0xF0 in FORBIDDEN_COMMANDS and 0xEC in FORBIDDEN_COMMANDS)

print("\n== plan artifact ==")
plan = build_plan()
check("plan declares the single CONNECT request", plan["single_request"] == {"operation": "connect", "request": CONNECT_REQUEST.hex()})
check("plan declares CONNECT-only with one request per run", plan["no_write_guard"]["connect_only"] is True and plan["no_write_guard"]["single_request_per_run"] is True)
check("plan declares no write commands and no page copy", plan["no_write_guard"]["write_commands_implemented"] is False and plan["no_write_guard"]["page_copy_sent"] is False)
check("plan forbids every non-CONNECT opcode it names", set(plan["no_write_guard"]["forbidden_command_opcodes"]) == {f"0x{op:02X}" for op in FORBIDDEN_COMMANDS})
check("plan binds the 0x7F7/0x7F8 route", plan["request_can_id"] == "0x7F7" and plan["response_can_id"] == "0x7F8")
check("plan requires bench isolation", plan["bench_isolated_required"] is True)
check("audit helper matches the plan guard", forbidden_opcode_audit()["forbidden_command_opcodes"] == plan["no_write_guard"]["forbidden_command_opcodes"])

print("\n== response classification ==")
positive = classify_response(bytes.fromhex("ff00000000000000"))
check("positive CONNECT response is reachable", positive["verdict"] == VERDICT_REACHABLE_POSITIVE and positive["reachable"] is True and positive["raw_response_hex"] == "ff00000000000000")
error = classify_response(bytes.fromhex("fe22000000000000"))
check(
    "XCP error response still proves physical reachability",
    error["verdict"] == VERDICT_REACHABLE_ERROR and error["reachable"] is True and error["error_code"] == "0x22",
)
unexpected = classify_response(bytes.fromhex("5500000000000000"))
check("unexpected PID is not reachable evidence", unexpected["verdict"] == VERDICT_UNEXPECTED and unexpected["reachable"] is False)
try:
    classify_response(bytes(9))
except XcpReachabilityError:
    check("non-eight-byte response is rejected", True)
else:
    check("non-eight-byte response is rejected", False)
check("timeout verdict exists and is not reachable", VERDICT_TIMEOUT == "no_response_timeout")

print("\n== source-level no-write invariants ==")
source = (REPO / "exploit/followups/xcp_reachability.py").read_text(encoding="utf-8")
can_send_calls = [line.strip() for line in source.splitlines() if ".can_send(" in line]
check("exactly one transmit call site exists", len(can_send_calls) == 1, repr(can_send_calls))
check("the only transmit sends the guarded CONNECT frame", "panda.can_send(REQUEST_ID, CONNECT_REQUEST, route.bus)" in can_send_calls[0])
check("guard runs against the literal frame before transmit", source.index("assert_connect_only(CONNECT_REQUEST)") < source.index("panda.can_send(REQUEST_ID, CONNECT_REQUEST, route.bus)"))
check(
    "no page-copy / SET_MTA / DOWNLOAD / MODIFY_BITS byte literal appears in the module",
    all(token not in source for token in ('"\\xe4', '"\\xf6', '"\\xf0\\x', '"\\xec\\x')),
)
check("module documents why E4 is excluded", "mutates" in source.lower() and "shadow" in source.lower())

print("\n== read/DAQ probes keep their intentional behavior ==")
read_source = (REPO / "exploit/followups/xcp_read_probe.py").read_text(encoding="utf-8")
check("acquisition probe still performs its E4 page copy", 'COPY_REQUEST = bytes.fromhex("e400000001000000")' in read_source)
daq_source = (REPO / "exploit/followups/xcp_daq_probe.py").read_text(encoding="utf-8")
check("DAQ probe still declares volatile-configuration-only DAQ", '"volatile_daq_configuration_only": True' in daq_source)
check("DAQ probe forbids generic write opcodes", "FORBIDDEN_COMMANDS" in daq_source)

print("\n== CLI guardrails ==")
probe = REPO / "exploit/followups/xcp_reachability.py"
plan_cli = subprocess.run([sys.executable, str(probe)], cwd=REPO, capture_output=True, text=True, check=False)
check("CLI defaults to non-live plan", plan_cli.returncode == 0 and '"mode": "plan"' in plan_cli.stdout and '"connect_only": true' in plan_cli.stdout)
unsafe = subprocess.run(
    [sys.executable, str(probe), "--execute"],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("live reachability refuses missing bench acknowledgement", unsafe.returncode != 0)
mismatch = subprocess.run(
    [sys.executable, str(probe), "--execute", "--bench-isolated"],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("live reachability refuses to run without route/identity binding", mismatch.returncode != 0)
bad_frame = subprocess.run(
    [sys.executable, str(probe), "--execute", "--bench-isolated", "--timeout", "0"],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("non-positive timeout is rejected", bad_frame.returncode != 0)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
