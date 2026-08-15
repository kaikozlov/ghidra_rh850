#!/usr/bin/env python3
"""Verify the bounded XCP DAQ observation helper against recovered firmware semantics."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.followups.xcp_daq_probe import (  # noqa: E402
    ENTRIES_PER_ODT,
    MAX_ENTRIES,
    PROFILES,
    XcpDaqError,
    build_plan,
    clear_daq_list_request,
    configure_daq,
    configuration_requests,
    decode_dto,
    layout,
    profile_or_addresses,
    set_daq_list_mode_request,
    set_daq_ptr_request,
    start_stop_daq_list_request,
    validate_addresses,
    write_daq_request,
)
from exploit.followups.xcp_read_probe import LOCALRAM_EXCLUSIONS  # noqa: E402

CF = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {label}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {label}" + (f" ({detail})" if detail else ""))


def rejects(fn) -> bool:
    try:
        fn()
    except (XcpDaqError, Exception) as exc:
        return isinstance(exc, XcpDaqError) or exc.__class__.__name__ == "XcpReadError"
    return False


print("== exact DAQ request encodings ==")
check("CLEAR_DAQ_LIST list 0", clear_daq_list_request().hex() == "e300000000000000")
check("SET_DAQ_PTR list0/odt2/entry0", set_daq_ptr_request(0, 2, 0).hex() == "e200000002000000")
check("WRITE_DAQ uses FF/01/00 plus little-endian address",
      write_daq_request(0xFEBE6D28).hex() == "e1ff0100286dbefe")
check("SET_DAQ_LIST_MODE uses event0/prescaler1/priority0",
      set_daq_list_mode_request().hex() == "e000000000000100")
check("START_DAQ_LIST list0", start_stop_daq_list_request(True).hex() == "de01000000000000")
check("STOP_DAQ_LIST list0", start_stop_daq_list_request(False).hex() == "de00000000000000")

print("\n== firmware-bound limits and profiles ==")
expected_exclusions = tuple(
    (int.from_bytes(CF[0x293F4 + i * 8:0x293F8 + i * 8], "little"),
     int.from_bytes(CF[0x293F8 + i * 8:0x293FC + i * 8], "little") + 1)
    for i in range(5)
)
check("DAQ helper inherits exact firmware LocalRAM exclusions", LOCALRAM_EXCLUSIONS == expected_exclusions,
      repr(expected_exclusions))
check("one list exposes 4x7=28 byte entries", MAX_ENTRIES == 28 and ENTRIES_PER_ODT == 7)
check("all named profile addresses pass the firmware read validator",
      all(not rejects(lambda p=p: validate_addresses(p.addresses)) for p in PROFILES.values()))
check("actuation profile is exactly one full ODT", len(PROFILES["actuation-discriminator"].addresses) == 7)
check("diagnostic-control profile maps DIAG-APP-016/017/018",
      PROFILES["diagnostic-control-state"].finding_ids == ("DIAG-APP-016", "DIAG-APP-017", "DIAG-APP-018"))
check("routine-lifecycle profile maps DIAG-APP-010/011",
      PROFILES["routine-lifecycle-state"].finding_ids == ("DIAG-APP-010", "DIAG-APP-011"))
check("routine-lifecycle profile fits exactly one ODT",
      len(PROFILES["routine-lifecycle-state"].addresses) == 7)
check("async/BA profile maps DIAG-APP-023 and SEC-APP-007",
      PROFILES["async-ba-state"].finding_ids == ("DIAG-APP-023", "SEC-APP-007"))
check("BA operational profile maps DIAG-APP-024",
      PROFILES["ba-operational-state"].finding_ids == ("DIAG-APP-024",))
check("protected XCP interval cannot be configured as a DAQ source",
      rejects(lambda: validate_addresses((0xFEBF4958,))))
check("duplicate sources rejected", rejects(lambda: validate_addresses((0xFEBE6D28, 0xFEBE6D28))))
check("more than 28 sources rejected", rejects(lambda: validate_addresses(tuple(0xFEBE6000 + i for i in range(29)))))

print("\n== deterministic layout and DTO decoding ==")
addresses = tuple(0xFEBE6000 + i for i in range(10))
groups = layout(addresses)
check("ten sources split as 7+3 across two ODTs", [len(group) for group in groups] == [7, 3])
first = decode_dto(bytes.fromhex("0001020304050607"), addresses)
second = decode_dto(bytes.fromhex("0108090a00000000"), addresses)
check("PID0 decodes first seven configured sources", first is not None and [v["value"] for v in first["values"]] == [1,2,3,4,5,6,7])
check("PID1 decodes remaining three sources", second is not None and [v["value"] for v in second["values"]] == [8,9,10])
check("command response PID FF is ignored by DTO decoder", decode_dto(bytes.fromhex("ff00000000000000"), addresses) is None)
check("unconfigured PID is ignored", decode_dto(bytes.fromhex("0300000000000000"), addresses) is None)

print("\n== configuration plan is observation-only ==")
profile = PROFILES["actuation-discriminator"]
plan = build_plan(profile.addresses, name=profile.name, description=profile.description, finding_ids=profile.finding_ids)
opcodes = [int(row["request"][:2], 16) for row in plan["configuration"]]
check("plan declares no source-memory write primitive", plan["source_memory_write_implemented"] is False)
check("plan declares DAQ configuration volatile only", plan["volatile_daq_configuration_only"] is True)
check("plan makes no wall-clock sampling-rate claim", plan["wall_clock_rate_claimed"] is False)
check("one-ODT profile uses CONNECT/CLEAR/PTR/7 WRITE_DAQ/MODE/START",
      opcodes == [0xFF, 0xE3, 0xE2] + [0xE1] * 7 + [0xE0, 0xDE], repr(opcodes))
check("plan contains no generic XCP memory-write opcode F0/EC", 0xF0 not in opcodes and 0xEC not in opcodes)
check("cleanup is explicit STOP_DAQ_LIST", plan["cleanup"]["request"] == "de00000000000000" and plan["cleanup"]["required_even_on_capture_error"])

requests = configuration_requests(profile.addresses)
check("configuration request count is 12 for seven-source profile", len(requests) == 12)
check("every DAQ request is an eight-byte CTO", all(len(request) == 8 for _, request in requests))


class InterleavedDtoPanda:
    def __init__(self):
        self.queue = []

    def can_send(self, address, data, bus):
        request = bytes(data)
        if request[:2] == bytes.fromhex("de01"):
            self.queue.append((0x7F8, 0, bytes.fromhex("0001020304050607"), bus))
        self.queue.append((0x7F8, 0, bytes.fromhex("ff00000000000000"), bus))

    def can_recv(self):
        queued, self.queue = self.queue, []
        return queued


interleaved = InterleavedDtoPanda()
try:
    configured = configure_daq(interleaved, bus=1, timeout=0.01, addresses=profile.addresses)
except Exception:
    interleaved_ok = False
else:
    interleaved_ok = configured["entry_count"] == 7
check("control exchange ignores interleaved DTO before START positive response", interleaved_ok)


class StartTimeoutPanda:
    def __init__(self):
        self.queue = []
        self.sent = []

    def can_send(self, address, data, bus):
        request = bytes(data)
        self.sent.append((int(address), request, int(bus)))
        if request[:2] == bytes.fromhex("de01"):
            return
        self.queue.append((0x7F8, 0, bytes.fromhex("ff00000000000000"), bus))

    def can_recv(self):
        queued, self.queue = self.queue, []
        return queued


cleanup_panda = StartTimeoutPanda()
check(
    "start-response timeout fails closed",
    rejects(lambda: configure_daq(cleanup_panda, bus=1, timeout=0.001, addresses=profile.addresses)),
)
check(
    "start-response timeout still sends STOP_DAQ_LIST cleanup",
    len(cleanup_panda.sent) >= 2
    and cleanup_panda.sent[-2][1][:2] == bytes.fromhex("de01")
    and cleanup_panda.sent[-1][1][:2] == bytes.fromhex("de00"),
)

print("\n== CLI guardrails ==")
probe = REPO / "exploit/followups/xcp_daq_probe.py"
plan_cli = subprocess.run(
    [sys.executable, str(probe), "--profile", "actuation-discriminator"],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("CLI defaults to non-live plan", plan_cli.returncode == 0 and '"mode": "plan"' in plan_cli.stdout)
check("CLI publishes COM-007 profile binding", '"COM-007"' in plan_cli.stdout and '"source_memory_write_implemented": false' in plan_cli.stdout)
unsafe = subprocess.run(
    [sys.executable, str(probe), "--profile", "actuation-discriminator", "--execute"],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("live DAQ refuses missing bench acknowledgement", unsafe.returncode != 0)
conflict = subprocess.run(
    [sys.executable, str(probe), "--profile", "actuation-discriminator", "--address", "0xFEBE6D28"],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("CLI rejects profile plus custom-address ambiguity", conflict.returncode != 0)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
