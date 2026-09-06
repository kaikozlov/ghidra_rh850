#!/usr/bin/env python3
"""Verify the exact-F33 native-XCP steering-state observer contract."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from exploit.followups.xcp_daq_probe import (  # noqa: E402
    FORBIDDEN_COMMANDS,
    MAX_ENTRIES,
)
from tools.camry_f33_steering_state_capture import (  # noqa: E402
    CAN_WITNESS_IDS,
    COMMAND_FUNNEL,
    ELM327_PARAM,
    EXPECTED_F181_HEX,
    FULL_PATH,
    EventAssembler,
    PANDA_BUS,
    PROFILES,
    SCHEMA,
    SOURCE_TERMS,
    XCP_REQUEST_ID,
    XCP_RESPONSE_ID,
    camry_configuration_requests,
    decode_profile_bytes,
    plan,
    profile_list_chunks,
    profile_odt_groups,
    validate_profile,
)

passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}{suffix}")

print("== target and route ==")
check("schema is exact-F33 v1", SCHEMA == "camry-f33-steering-state-capture-v1")
check("exact F181 is pinned", EXPECTED_F181_HEX == "023839363546333330373030300000000038413331313333303331303000000000")
check("post-repin route is Panda bus0 / ELM327 param1", PANDA_BUS == 0 and ELM327_PARAM == 1)
check("XCP route IDs are exact", XCP_REQUEST_ID == 0x7F7 and XCP_RESPONSE_ID == 0x7F8)
check("CAN witness family includes request/reference/EPS state", {0x025,0x030,0x081,0x08A,0x0B6,0x371,0x412} <= CAN_WITNESS_IDS)

print("\n== exact one/two-list DAQ profile geometry ==")
check("three target profiles include one combined full path",
      set(PROFILES) == {"source-terms", "command-funnel", "full-path"})
expected_geometry = {"source-terms": (28,1,4), "command-funnel": (28,1,4), "full-path": (52,2,8)}
for profile in PROFILES.values():
    try:
        validate_profile(profile)
    except Exception as exc:
        check(f"{profile.name} passes firmware XCP read validator", False, str(exc))
    else:
        check(f"{profile.name} passes firmware XCP read validator", True)
    expected_bytes, expected_lists, expected_odts = expected_geometry[profile.name]
    check(f"{profile.name} byte/list/ODT geometry exact",
          len(profile.addresses) == expected_bytes and len(profile_list_chunks(profile)) == expected_lists and len(profile_odt_groups(profile)) == expected_odts)
    check(f"{profile.name} has no overlapping byte addresses", len(set(profile.addresses)) == len(profile.addresses))
check("one native DAQ list remains 28 bytes", MAX_ENTRIES == 28)

source_expected = (
    ("AC2B_diag_gate",0xFEBEAC2B,1,False),
    ("C7BF_b6_active",0xFEBEC7BF,1,False),
    ("C43C_assist_term",0xFEBEC43C,2,True),
    ("C4C0_assist_term",0xFEBEC4C0,4,True),
    ("C3BA_assist_term",0xFEBEC3BA,2,True),
    ("CC2C_assist_term",0xFEBECC2C,4,True),
    ("BF3C_assist_term",0xFEBEBF3C,4,True),
    ("CB38_assist_term",0xFEBECB38,2,True),
    ("C5EE_moving_term",0xFEBEC5EE,2,True),
    ("CBE8_assist_term",0xFEBECBE8,2,True),
    ("CC48_d0218_output",0xFEBECC48,4,True),
)
check("source profile pins every D0218 term/gate/output",
      tuple((f.name,f.address,f.width,f.signed) for f in SOURCE_TERMS.fields) == source_expected)

funnel_expected = (
    ("CC48_d0218_output",0xFEBECC48,4,True),
    ("CC4C_bounded",0xFEBECC4C,2,True),
    ("CC4E_slewed",0xFEBECC4E,2,True),
    ("AC52_limit",0xFEBEAC52,2,True),
    ("CC60_limited",0xFEBECC60,2,True),
    ("CC50_pre_scale",0xFEBECC50,2,True),
    ("AC5A_scale",0xFEBEAC5A,2,False),
    ("AC4C_slew_limit",0xFEBEAC4C,2,True),
    ("CC62_pre_slew",0xFEBECC62,2,True),
    ("CC66_post_slew",0xFEBECC66,2,True),
    ("CC64_selected",0xFEBECC64,2,True),
    ("AC54_motor_branch",0xFEBEAC54,2,True),
    ("AC56_diag_branch",0xFEBEAC56,2,True),
)
check("funnel profile pins recovered CC48-to-AC54/AC56 path",
      tuple((f.name,f.address,f.width,f.signed) for f in COMMAND_FUNNEL.fields) == funnel_expected)
check("full-path is exact source+funnel union with CC48 sampled once",
      FULL_PATH.fields == SOURCE_TERMS.fields + tuple(f for f in COMMAND_FUNNEL.fields if f.name != "CC48_d0218_output") and
      len(FULL_PATH.addresses) == 52)

print("\n== repository semantic joins ==")
cone = json.loads((REPO / "data/generated/camry_8965F3307000_command_cone_ingress.json").read_text())
oracles = json.loads((REPO / "data/generated/camry_8965F3307000_internal_assist_oracles.json").read_text())
source_text = cone["baseline_internal_assist_path"]["D0218_sum"]
for token in ("C43C","C4C0","C3BA","CC2C","BF3C","CB38","C5EE","CBE8","FEBECC48","AC2B","C7BF"):
    check(f"canonical D0218 evidence contains {token}", token in source_text)
chain = oracles["physical_actuation_funnel"]["chain"]
for token in ("FEBECC50","FEBECC62","FEBECC66","FEBECC64","FEBEAC54"):
    check(f"canonical physical funnel contains {token}", token in chain)
check("canonical diagnostic sibling identifies AC56 from CC62",
      cone["command_block_map"]["via_D0AAE"]["FEBEAC56"].startswith("FEBECC62"))
check("canonical motor branch identifies AC54 from CC64",
      cone["command_block_map"]["via_D0AAE"]["FEBEAC54"] == "FEBECC64")

print("\n== DAQ configuration remains observation-only ==")
for profile in PROFILES.values():
    requests = camry_configuration_requests(profile, prescaler=7)
    opcodes = [req[0] for _, req in requests]
    list_count = len(profile_list_chunks(profile))
    check(f"{profile.name} configures expected ODT pointers",
          sum(op == 0xE2 for op in opcodes) == len(profile_odt_groups(profile)))
    check(f"{profile.name} configures every byte pointer once",
          sum(op == 0xE1 for op in opcodes) == len(profile.addresses))
    check(f"{profile.name} clears/modes/starts every list",
          sum(op == 0xE3 for op in opcodes) == list_count and
          sum(op == 0xE0 for op in opcodes) == list_count and
          sum(op == 0xDE for op in opcodes) == list_count)
    check(f"{profile.name} uses only CONNECT/E3/E2/E1/E0/DE",
          set(opcodes) <= {0xFF,0xE3,0xE2,0xE1,0xE0,0xDE})
    check(f"{profile.name} contains no generic write/page-copy opcode",
          not (set(opcodes) & set(FORBIDDEN_COMMANDS)))
    modes = [req for op, req in requests if op.startswith("set_daq_list_mode_")]
    check(f"{profile.name} propagates prescaler 7 to every list",
          len(modes) == list_count and all(req[6] == 7 for req in modes))
    starts = [req for op, req in requests if op.startswith("start_daq_list_")]
    check(f"{profile.name} starts list indices in ascending order",
          [int.from_bytes(req[2:4], "little") for req in starts] == list(range(list_count)))

p = plan(SOURCE_TERMS)
check("plan defaults to conservative DAQ prescaler 10", p["daq_prescaler"] == 10)
check("plan explicitly declares no source/flash/steering/B6 writes",
      p["mutation_boundary"] == {
          "source_memory_writes": False,
          "steering_commands": False,
          "b6_transmit": False,
          "flash_writes": False,
          "ephemeral_resident": False,
          "volatile_xcp_daq_configuration": True,
      })
check("plan publishes sequential-not-atomic timing boundary", "not physical wire timestamps" in p["timing_boundary"] and "atomic CPU snapshots" in p["timing_boundary"])

print("\n== byte decoding and one/two-list event assembly ==")
# Fill each source-profile byte with a deterministic pattern, then overwrite
# multi-byte fields with values that exercise little-endian signed decoding.
values = {addr: (i * 17 + 3) & 0xFF for i, addr in enumerate(SOURCE_TERMS.addresses)}
def put(addr: int, width: int, value: int, signed: bool) -> None:
    b = int(value).to_bytes(width, "little", signed=signed)
    for i, x in enumerate(b): values[addr+i] = x
put(0xFEBEC43C,2,-1234,True)
put(0xFEBEC4C0,4,-12345678,True)
put(0xFEBECC48,4,0x12345678,True)
decoded = decode_profile_bytes(SOURCE_TERMS, values)
check("signed16 source field decodes little-endian", decoded["C43C_assist_term"] == -1234)
check("signed32 source field decodes little-endian", decoded["C4C0_assist_term"] == -12345678)
check("positive CC48 signed32 decodes exactly", decoded["CC48_d0218_output"] == 0x12345678)

assembler = EventAssembler(SOURCE_TERMS)
groups = [SOURCE_TERMS.addresses[i:i+7] for i in range(0,28,7)]
assembled = None
for pid, group in enumerate(groups):
    dto = bytes([pid]) + bytes(values[a] for a in group)
    assembled = assembler.feed(dto, 1_000_000 + pid * 1000, 100 + pid) or assembled
check("four ODTs assemble one complete sample", assembler.complete == 1 and assembled is not None)
check("assembled sample preserves decoded source values", assembled is not None and assembled["values"]["C4C0_assist_term"] == -12345678 and assembled["values"]["CC48_d0218_output"] == 0x12345678)
check("assembled sample records ODT assembly span", assembled is not None and assembled["assembly_span_ns"] == 3000)
check("assembled sample retains raw Panda busTime for each ODT", assembled is not None and assembled["panda_bus_time_raw"] == [100,101,102,103])

full_values = {addr: (i * 29 + 11) & 0xFF for i, addr in enumerate(FULL_PATH.addresses)}
# Pin both an upstream source and final motor branch in the same 52-byte event.
for addr, width, value in ((0xFEBEC4C0,4,-7654321),(0xFEBEAC54,2,-321),(0xFEBEAC56,2,654)):
    raw = int(value).to_bytes(width, "little", signed=True)
    for i, byte in enumerate(raw): full_values[addr+i] = byte
full_assembler = EventAssembler(FULL_PATH)
full_sample = None
for pid, group in enumerate(profile_odt_groups(FULL_PATH)):
    dto = bytes([pid]) + bytes(full_values[a] for a in group) + bytes(7-len(group))
    full_sample = full_assembler.feed(dto, 2_000_000 + pid * 1000, 200 + pid) or full_sample
check("eight ODTs across two lists assemble one 52-byte full-path event",
      full_assembler.complete == 1 and full_sample is not None and len(full_sample["panda_bus_time_raw"]) == 8)
check("full-path event joins source and downstream motor/diagnostic values",
      full_sample is not None and full_sample["values"]["C4C0_assist_term"] == -7654321 and
      full_sample["values"]["AC54_motor_branch"] == -321 and full_sample["values"]["AC56_diag_branch"] == 654)

bad = EventAssembler(SOURCE_TERMS)
check("out-of-order nonzero PID is rejected", bad.feed(bytes([1])+bytes(7), 1) is None and bad.out_of_order == 1)
bad.feed(bytes([0])+bytes(7), 2)
bad.feed(bytes([0])+bytes(7), 3)
check("new PID0 drops prior partial sample", bad.dropped_partial == 1)

print("\n== CLI fail-closed behavior ==")
tool = REPO / "tools/camry_f33_steering_state_capture.py"
plan_cli = subprocess.run([sys.executable, str(tool), "--profile", "full-path"], cwd=REPO, capture_output=True, text=True, check=False)
check("CLI defaults to plan mode", plan_cli.returncode == 0 and '"mode": "plan"' in plan_cli.stdout)
check("CLI exposes exact 52-byte/two-list full path", '"byte_count": 52' in plan_cli.stdout and '"daq_list_count": 2' in plan_cli.stdout and '"AC54_motor_branch"' in plan_cli.stdout)
unsafe = subprocess.run([sys.executable, str(tool), "--profile", "source-terms", "--execute"], cwd=REPO, capture_output=True, text=True, check=False)
check("live mode requires explicit stock-observation acknowledgement", unsafe.returncode != 0 and "stock-observation-confirmed" in unsafe.stderr)
ack_only = subprocess.run([sys.executable, str(tool), "--stock-observation-confirmed"], cwd=REPO, capture_output=True, text=True, check=False)
check("acknowledgement without live mode is rejected", ack_only.returncode != 0)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
