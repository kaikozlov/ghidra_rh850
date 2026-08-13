#!/usr/bin/env python3
"""Verify the application WDBI access/control surface from raw firmware bytes."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CSV_PATH = REPO / "data" / "application_wdbi_surface.csv"
GEN_PATH = REPO / "tools" / "generate_application_wdbi_surface.py"

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS {name}")
    else:
        failed += 1
        print(f"FAIL {name}: {detail}")


def row_by_did(rows: list[dict[str, str]], did: int) -> dict[str, str]:
    return next(row for row in rows if int(row["did"], 16) == did)


print("== generated WDBI surface artifact ==")
check("WDBI surface CSV exists", CSV_PATH.is_file())
with CSV_PATH.open(newline="") as fh:
    rows = list(csv.DictReader(fh))
check("surface contains exactly 19 WDBI rows", len(rows) == 19, str(len(rows)))
expected_dids = [
    0x1000, 0x1001, 0x1002, 0x1004, 0x1007, 0x1008, 0x1009, 0x100E, 0x100F,
    0x1010, 0x1100, 0x1103, 0x1106, 0x1108, 0x1109, 0x110A, 0x110B, 0x110C, 0x110D,
]
check("surface DID order matches firmware table",
      [int(row["did"], 16) for row in rows] == expected_dids)
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "application_wdbi_surface.csv"
    proc = subprocess.run(
        [sys.executable, str(GEN_PATH), "-o", str(out)], cwd=REPO,
        check=True, capture_output=True, text=True,
    )
    check("WDBI generator rerun succeeds", proc.returncode == 0, proc.stderr)
    check("committed WDBI surface matches deterministic regeneration",
          out.read_bytes() == CSV_PATH.read_bytes())

print("\n== table and policy structure ==")
callback_blob = CF[0x25804:0x25804 + 19 * 12]
check("19-row WDBI callback table hash is pinned",
      hashlib.sha256(callback_blob).hexdigest() ==
      "bb72da6fb416c6fc47cb87cf2c060bb99f6bdb95499254bfbbfe960f1ccc979c")
check("all 19 WDBIs are enabled", all(row["enabled"] == "1" for row in rows))
check("all 19 WDBIs have zero configured SecurityAccess levels",
      all(row["security_level_count"] == "0" for row in rows))
policy0 = [row for row in rows if row["policy_index"] == "0"]
check("18 of 19 WDBIs use policy index 0", len(policy0) == 18, str(len(policy0)))
check("policy-0 WDBIs allow policy sessions 1/2/3",
      all(row["policy_sessions"] == "1,2,3" for row in policy0))
check("SID 0x2E outer gate reduces policy-0 WDBIs to programming/extended",
      all(row["effective_wdbi_sessions"] == "2,3" for row in policy0))
r1010 = row_by_did(rows, 0x1010)
check("DID 0x1010 is the sole policy-index-1 WDBI",
      r1010["policy_index"] == "1" and r1010["policy_sessions"] == "3"
      and r1010["effective_wdbi_sessions"] == "3")

print("\n== selector and payload shape ==")
check("every WDBI supports selector 1",
      all(row["selector1_supported"] == "1" for row in rows))
selector2 = [int(row["did"], 16) for row in rows if row["selector2_supported"] == "1"]
check("only DIDs 0x110A and 0x110D support selector 2",
      selector2 == [0x110A, 0x110D], repr(selector2))
selector3_missing = [int(row["did"], 16) for row in rows if row["selector3_supported"] == "0"]
check("only crypto-test activation DIDs 0x100E/0x100F lack selector 3",
      selector3_missing == [0x100E, 0x100F], repr(selector3_missing))
nonzero_s1_inputs = {
    int(row["did"], 16): int(row["selector1_input_bytes"])
    for row in rows if int(row["selector1_input_bytes"]) != 0
}
check("only 0x1004 and 0x1010 carry selector-1 payload bytes",
      nonzero_s1_inputs == {0x1004: 2, 0x1010: 64}, repr(nonzero_s1_inputs))
check("DID 0x1010 selector outputs remain 49 bytes",
      r1010["selector1_output_bytes"] == "49" and r1010["selector3_output_bytes"] == "49")

print("\n== stock crypto-test activation routes ==")
r100e = row_by_did(rows, 0x100E)
r100f = row_by_did(rows, 0x100F)
check("DID 0x100E callback row selects shared precheck and bank-0 wrapper",
      r100e["precondition_callback"] == "0x8A768" and r100e["action_callback"] == "0x8A774")
check("DID 0x100F callback row selects shared precheck and bank-1 wrapper",
      r100f["precondition_callback"] == "0x8A768" and r100f["action_callback"] == "0x8A782")
check("bank-0 wrapper directly calls activator 0x68F92",
      CF[0x8A778:0x8A77C] == bytes.fromhex("bdff1ae8"))
check("bank-1 wrapper directly calls activator 0x69018",
      CF[0x8A786:0x8A78A] == bytes.fromhex("bdff92e8"))

print("\n== WDBI service-mode control chain ==")
for did, action, mode, mov_addr, call_addr in (
    (0x110A, 0x4F630, 2, 0x4F63E, 0x4F640),
    (0x110C, 0x4F702, 3, 0x4F710, 0x4F712),
    (0x110D, 0x4F7B8, 4, 0x4F7C6, 0x4F7C8),
):
    row = row_by_did(rows, did)
    check(f"DID 0x{did:04X} action callback is 0x{action:X}",
          int(row["action_callback"], 16) == action)
    check(f"DID 0x{did:04X} selector 1 loads internal mode {mode}",
          CF[mov_addr:mov_addr + 2] == bytes([mode, 0x32]))
    # All three call the same thunk at 0xFE038; instruction encoding differs by callsite.
    check(f"DID 0x{did:04X} selector 1 calls service-mode thunk 0xFE038",
          CF[call_addr:call_addr + 2] == bytes.fromhex("8aff"))
check("service-mode thunk reaches dispatcher FUN_B1F34",
      CF[0xFE038:0xFE040] == bytes.fromhex("2c06341f0b006c00"))
# B1F34 accepts modes 2/3/4, sets an activity bit, and posts event 6 when the
# current system-mode high byte is not already 0x500.
check("service-mode dispatcher contains mode-2/3/4 comparisons",
      CF[0xB1F86:0xB1F92] == bytes.fromhex("62eaf20563ead20564ea820d"))
check("service-mode dispatcher posts system-mode event 6",
      CF[0xB1FE4:0xB1FEA] == bytes.fromhex("0632bfffd6e2"))
# In high mode 0x500, B1BF6 maps activity bits 2/3/4 to event 0x2E. B1DAC then
# calls B1C6E and commits submode 0x520 through system_mode_event_set helper B0330.
check("0x500 coordinator recognizes service event 0x2E",
      CF[0xB1E1A:0xB1E2A] == bytes.fromhex("20362e00bfffaee56152fa05bfff48fe"))
check("0x500 coordinator commits system submode 0x520",
      CF[0xB1E2A:0xB1E32] == bytes.fromhex("20362005bfff02e5"))
# B1C6E selects service subtype 1/2/3 and B7054 persists it; B7054 also zeroes
# paired subsystem command slots through thunk 0xFED2C.
check("service submode initializer calls B7054",
      CF[0xB1C92:0xB1C98] == bytes.fromhex("1d3080ffc053"))
check("B7054 clears command slots 0 and 1 through thunk 0xFED2C",
      CF[0xB70BC:0xB70CC] == bytes.fromhex("0032063884ff6c7c0132003a84ff647c"))
check("thunk 0xFED2C reaches fixed command-slot writer 0x562C8",
      CF[0xFED2C:0xFED34] == bytes.fromhex("2c06c86205006c00"))

print("\n== explicit service-mode termination ==")
check("DID 0x110A selector 2 calls FE204 -> B7218",
      CF[0x4F66E:0x4F672] == bytes.fromhex("8aff96eb")
      and CF[0xFE204:0xFE20C] == bytes.fromhex("2c0618720b006c00"))
check("DID 0x110D selector 2 calls FE1F0 -> B720A",
      CF[0x4F7F6:0x4F7FA] == bytes.fromhex("8afffae9")
      and CF[0xFE1F0:0xFE1F8] == bytes.fromhex("2c060a720b006c00"))
# B720A/B7218 set service state 3; B1D2E posts event 0x2F for state 0/2/3;
# B1DAC handles 0x2F in submode 0x520 by cleanup then B0330(0x500).
check("submode-0x520 exit detector posts event 0x2F for terminal state",
      CF[0xB1D32:0xB1D4E] == bytes.fromhex("a40fe7fb620ad205630ab205e009da0520362f00bfff76e540063f00"))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
