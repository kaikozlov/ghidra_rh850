#!/usr/bin/env python3
"""Verify the application RoutineControl access/control surface from raw firmware bytes."""
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
CSV_PATH = REPO / "data" / "application_routine_control_surface.csv"
GEN_PATH = REPO / "tools" / "generate_application_routine_control_surface.py"

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


def row_by_rid(rows: list[dict[str, str]], rid: int) -> dict[str, str]:
    return next(row for row in rows if int(row["rid"], 16) == rid)


print("== generated RoutineControl surface artifact ==")
check("RoutineControl surface CSV exists", CSV_PATH.is_file())
with CSV_PATH.open(newline="") as fh:
    rows = list(csv.DictReader(fh))
check("surface contains exactly 19 RoutineControl rows", len(rows) == 19, str(len(rows)))
expected_rids = [
    0x1000, 0x1001, 0x1002, 0x1004, 0x1007, 0x1008, 0x1009, 0x100E, 0x100F,
    0x1010, 0x1100, 0x1103, 0x1106, 0x1108, 0x1109, 0x110A, 0x110B, 0x110C, 0x110D,
]
check("surface RID order matches firmware table",
      [int(row["rid"], 16) for row in rows] == expected_rids)
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "application_routine_control_surface.csv"
    proc = subprocess.run(
        [sys.executable, str(GEN_PATH), "-o", str(out)], cwd=REPO,
        check=True, capture_output=True, text=True,
    )
    check("RoutineControl generator rerun succeeds", proc.returncode == 0, proc.stderr)
    check("committed RoutineControl surface matches deterministic regeneration",
          out.read_bytes() == CSV_PATH.read_bytes())

print("\n== table and policy structure ==")
callback_blob = CF[0x25804:0x25804 + 19 * 12]
check("19-row RoutineControl callback table hash is pinned",
      hashlib.sha256(callback_blob).hexdigest() ==
      "bb72da6fb416c6fc47cb87cf2c060bb99f6bdb95499254bfbbfe960f1ccc979c")
check("all 19 RoutineControls are enabled", all(row["enabled"] == "1" for row in rows))
check("all 19 RoutineControls have zero configured SecurityAccess levels",
      all(row["security_level_count"] == "0" for row in rows))
policy0 = [row for row in rows if row["policy_index"] == "0"]
check("18 of 19 RoutineControls use policy index 0", len(policy0) == 18, str(len(policy0)))
check("policy-0 RoutineControls allow policy sessions 1/2/3",
      all(row["policy_sessions"] == "1,2,3" for row in policy0))
check("SID 0x31 outer gate preserves policy-0 default/programming/extended access",
      all(row["effective_routine_control_sessions"] == "1,2,3" for row in policy0))
r1010 = row_by_rid(rows, 0x1010)
check("RID 0x1010 is the sole policy-index-1 RoutineControl",
      r1010["policy_index"] == "1" and r1010["policy_sessions"] == "3"
      and r1010["effective_routine_control_sessions"] == "3")

print("\n== control type and payload shape ==")
check("every RoutineControl supports control type 1",
      all(row["control_type1_supported"] == "1" for row in rows))
control_type2 = [int(row["rid"], 16) for row in rows if row["control_type2_supported"] == "1"]
check("only RIDs 0x110A and 0x110D support control type 2",
      control_type2 == [0x110A, 0x110D], repr(control_type2))
control_type3_missing = [int(row["rid"], 16) for row in rows if row["control_type3_supported"] == "0"]
check("only crypto-test activation RIDs 0x100E/0x100F lack control type 3",
      control_type3_missing == [0x100E, 0x100F], repr(control_type3_missing))
nonzero_s1_inputs = {
    int(row["rid"], 16): int(row["control_type1_input_bytes"])
    for row in rows if int(row["control_type1_input_bytes"]) != 0
}
check("only 0x1004 and 0x1010 carry control-type-1 payload bytes",
      nonzero_s1_inputs == {0x1004: 2, 0x1010: 64}, repr(nonzero_s1_inputs))
check("RID 0x1010 selector outputs remain 49 bytes",
      r1010["control_type1_output_bytes"] == "49" and r1010["control_type3_output_bytes"] == "49")

print("\n== ungated live lifecycle reinitializers ==")
r1007 = row_by_rid(rows, 0x1007)
r1008 = row_by_rid(rows, 0x1008)
check("RIDs 0x1007/0x1008 are zero-payload policy-0 startRoutine actions",
      all(r["policy_index"] == "0" and r["effective_routine_control_sessions"] == "1,2,3"
              and r["control_type1_input_bytes"] == "0" for r in (r1007, r1008)))
# SID 0x31 itself permits default/programming/extended sessions, so these
# routines do not require a session transition merely to reach their policy.
# 0x1002 and 0x1106 demonstrate that this calibration does add explicit local
# speed gates to selected RoutineControls. 0x1007/0x1008 instead contain only lifecycle
# readiness + one-shot checks; pin all four callback bodies to keep that contrast exact.
check("speed-gated RoutineControl 0x1002 precondition body is pinned",
      hashlib.sha256(CF[0x4F0AE:0x4F0EA]).hexdigest() ==
      "4066aeaa40016233deac2b002e9cbe825d79f59b3d149ac9e5290b80831fd360")
check("speed-gated RoutineControl 0x1106 precondition body is pinned",
      hashlib.sha256(CF[0x4F400:0x4F43E]).hexdigest() ==
      "facfa0d92b28416e68eafc6119759c54b695c7ae3046bee2da5ab1ded58f3812")
check("RoutineControls 0x1002/0x1106 explicitly read application vehicle speed",
      CF[0x4F0C0:0x4F0C4] == bytes.fromhex("e40f9330")
      and CF[0x4F412:0x4F416] == bytes.fromhex("e40f9330"))
check("RoutineControl 0x1007 precondition body is pinned without that speed-gate shape",
      hashlib.sha256(CF[0x4F1B4:0x4F1EA]).hexdigest() ==
      "a63141ad5cced576a3efd97f1473a1804bd4be9f51bc9235ad55befb63ee9437"
      and bytes.fromhex("e40f9330") not in CF[0x4F1B4:0x4F1EA])
check("RoutineControl 0x1008 precondition body is pinned without that speed-gate shape",
      hashlib.sha256(CF[0x4F226:0x4F25C]).hexdigest() ==
      "03c50462198611b270a7497a736e0dc2a003d711c2d6c34c63dcb55894506d14"
      and bytes.fromhex("e40f9330") not in CF[0x4F226:0x4F25C])
check("0x1007/0x1008 preconditions call shared lifecycle-readiness thunk B79F8",
      CF[0xFDE80:0xFDE88] == bytes.fromhex("2c06f8790b006c00"))
check("lifecycle-readiness helper body is pinned",
      hashlib.sha256(CF[0xB79F8:0xB7A36]).hexdigest() ==
      "cc7d98099d539e15a75d7bc4b0dc469e5c5dd0e263a5f7ff8d39d123bffc9d6c")
check("0x1007 action reaches B7A36 and writes one-shot flag",
      CF[0xFDE94:0xFDE9C] == bytes.fromhex("2c06367a0b006c00")
      and CF[0x4F1FC:0x4F200] == bytes.fromhex("440f57c9"))
check("0x1008 action reaches diagnostic-only B7AAE and writes one-shot flag",
      CF[0xFDEA8:0xFDEB0] == bytes.fromhex("2c06ae7a0b006c00")
      and CF[0x4F26C:0x4F270] == bytes.fromhex("440f58c9"))
check("0x1007 reinitializer body is pinned and forces lifecycle state 0x11",
      hashlib.sha256(CF[0xB7A36:0xB7AAE]).hexdigest() ==
      "9eaec849349c3a159a1c2b70071fe315cb083cfb92fdad969144af6f1c590209"
      and CF[0xB7A72:0xB7A76] == bytes.fromhex("20ee1100"))
check("0x1008 reinitializer body is pinned and forces lifecycle state 0x11",
      hashlib.sha256(CF[0xB7AAE:0xB7AE8]).hexdigest() ==
      "d15f8d73af93ecfb3891278dbd27b34fc1670e166eaed9f1a32e5a87a788abda"
      and CF[0xB7ADC:0xB7AE0] == bytes.fromhex("209e1100"))
# B79E8 services the lifecycle workers whenever current system mode is >0x102;
# this includes the normal 0x300/0x400/0x500 operational bands.
check("normal per-tick dispatcher gates lifecycle scheduler at mode > 0x102",
      CF[0xBEDAE:0xBEDB6] == bytes.fromhex("1c06fdfee9070501"))
check("normal per-tick dispatcher calls lifecycle scheduler B79E8 on both branches",
      CF[0xBEDC0:0xBEDC4] == bytes.fromhex("bfff288c")
      and CF[0xBEE0A:0xBEE0E] == bytes.fromhex("bfffde8b"))

print("\n== state-gated live lifecycle reinitializer 0x1009 ==")
r1009 = row_by_rid(rows, 0x1009)
check("RID 0x1009 is zero-payload policy-0 control-type-1 control",
      r1009["policy_index"] == "0" and r1009["effective_routine_control_sessions"] == "1,2,3"
      and r1009["control_type1_input_bytes"] == "0")
check("0x1009 precondition body is pinned and lacks explicit vehicle-speed read",
      hashlib.sha256(CF[0x4F296:0x4F2C2]).hexdigest() ==
      "69be616d770bd0958f8821af689778fb9300a3d622df6c5aa412b52d46e6e3e7"
      and bytes.fromhex("e40f9330") not in CF[0x4F296:0x4F2C2])
check("0x1009 feature gate is enabled in this calibration", CF[0xAEC5D] == 0x20)
check("0x1009 action body is pinned",
      hashlib.sha256(CF[0x4F2C2:0x4F322]).hexdigest() ==
      "9fc8a91c178ea9edb9adc1d3d653cc8e65744c9aae03dc0e97cd67e569540808")
check("0x1009 control type 1 requires nonzero feature and zero aggregate-health snapshot",
      CF[0x4F2D0:0x4F2E8] == bytes.fromhex(
          "8affd4ef240f593161e2ea0de051f205e009da058affcced"))
check("0x1009 diagnostic thunk reaches B55E2",
      CF[0xFE0B0:0xFE0B8] == bytes.fromhex("2c06e2550b006c00"))
check("0x1009 reinitializer body is pinned and forces FEBEB2D5 to 0x11",
      hashlib.sha256(CF[0xB55E2:0xB55FA]).hexdigest() ==
      "e9f35997e57139f2bba81867526093f65b86784fa070dff983bc173d7a68957d"
      and CF[0xB55EE:0xB55F6] == bytes.fromhex("200e1100440fd5fa"))
check("0x1009 lifecycle worker body is pinned",
      hashlib.sha256(CF[0xB5254:0xB52DA]).hexdigest() ==
      "14ec5824bf6405b24be0f4aee15f2aa11c6b5ff0232208dca2b7e633b2ce038c")
check("0x1009 worker wrapper body is pinned",
      hashlib.sha256(CF[0xB5526:0xB5546]).hexdigest() ==
      "1103b161b554a7bde0fedb5bcaa05e2ceff8a024ed014437ce6e7b51a3054a7f")
check("0x1009 control type 3 conditionally clears its diagnostic latch",
      CF[0x4F2FC:0x4F30E] == bytes.fromhex("0052e099b205e009b2055d070d00bd0f0d00"))

print("\n== stock crypto-test activation routes ==")
r100e = row_by_rid(rows, 0x100E)
r100f = row_by_rid(rows, 0x100F)
check("RID 0x100E callback row selects shared precheck and bank-0 wrapper",
      r100e["precondition_callback"] == "0x8A768" and r100e["action_callback"] == "0x8A774")
check("RID 0x100F callback row selects shared precheck and bank-1 wrapper",
      r100f["precondition_callback"] == "0x8A768" and r100f["action_callback"] == "0x8A782")
check("bank-0 wrapper directly calls activator 0x68F92",
      CF[0x8A778:0x8A77C] == bytes.fromhex("bdff1ae8"))
check("bank-1 wrapper directly calls activator 0x69018",
      CF[0x8A786:0x8A78A] == bytes.fromhex("bdff92e8"))

print("\n== RoutineControl service-mode control chain ==")
for rid, action, mode, mov_addr, call_addr in (
    (0x110A, 0x4F630, 2, 0x4F63E, 0x4F640),
    (0x110C, 0x4F702, 3, 0x4F710, 0x4F712),
    (0x110D, 0x4F7B8, 4, 0x4F7C6, 0x4F7C8),
):
    row = row_by_rid(rows, rid)
    check(f"RID 0x{rid:04X} action callback is 0x{action:X}",
          int(row["action_callback"], 16) == action)
    check(f"RID 0x{rid:04X} control type 1 loads internal mode {mode}",
          CF[mov_addr:mov_addr + 2] == bytes([mode, 0x32]))
    # All three call the same thunk at 0xFE038; instruction encoding differs by callsite.
    check(f"RID 0x{rid:04X} control type 1 calls service-mode thunk 0xFE038",
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
check("RID 0x110A control type 2 calls FE204 -> B7218",
      CF[0x4F66E:0x4F672] == bytes.fromhex("8aff96eb")
      and CF[0xFE204:0xFE20C] == bytes.fromhex("2c0618720b006c00"))
check("RID 0x110D control type 2 calls FE1F0 -> B720A",
      CF[0x4F7F6:0x4F7FA] == bytes.fromhex("8afffae9")
      and CF[0xFE1F0:0xFE1F8] == bytes.fromhex("2c060a720b006c00"))
# B720A/B7218 set service state 3; B1D2E posts event 0x2F for state 0/2/3;
# B1DAC handles 0x2F in submode 0x520 by cleanup then B0330(0x500).
check("submode-0x520 exit detector posts event 0x2F for terminal state",
      CF[0xB1D32:0xB1D4E] == bytes.fromhex("a40fe7fb620ad205630ab205e009da0520362f00bfff76e540063f00"))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
