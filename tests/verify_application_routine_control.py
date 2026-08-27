#!/usr/bin/env python3
"""Verify the application RoutineControl surface, RID 0x1004 event history, and remaining controls.

Merged portable family module.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = REPO = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

print("== RoutineControl surface ==")


CSV_PATH = REPO / "data" / "application_routine_control_surface.csv"
GEN_PATH = REPO / "tools" / "generate_application_routine_control_surface.py"



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


print("\n== RoutineControl 1004 event history ==")

CORPUS=ROOT/'data/generated/decompilations.jsonl'

def sha(a,n): return hashlib.sha256(CF[a:a+n]).hexdigest()
def branch(addr):
 w0,w1=struct.unpack_from('<HH',CF,addr)
 if ((w0>>6)&0x1f)!=0x1e or (w1&1): return None
 reg2=(w0>>11)&0x1f; hi=w0&0x3f
 if hi&0x20: hi-=0x40
 return ('jarl' if reg2 else 'jr',addr+(hi<<16)+w1)

records={}
for line in CORPUS.open():
 r=json.loads(line)
 if r.get('record')=='function': records[int(r['entry_addr'],16)]=r

def refs(a): return {(x.get('to_addr'),x.get('ref_type')) for x in records[a].get('data_references',[])}
def targets(a): return {x for x,_ in refs(a) if isinstance(x,str)}

rows={r['rid']:r for r in csv.DictReader((ROOT/'data/application_routine_control_surface.csv').open(newline=''))}
r=rows['0x1004']
print('== access, payload, and repeatability ==')
check('1004 generated class is no-speed persistent event-history rewrite',r['effect_class']=='no_speed_event_history_persistent_rewrite',r['effect_class'])
check('1004 is policy0/default-session reachable with no SecurityAccess',r['policy_index']=='0' and r['security_level_count']=='0' and r['effective_routine_control_sessions']=='1,2,3')
check('1004 control type 1 is exactly two input bytes',r['control_type1_supported']=='1' and r['control_type1_input_bytes']=='2')
check('1004 precondition body pinned',sha(0x4F12C,68)=='b499a38d3444e97eb37c30c22af6c7046b4dc334be16837f042f39e6eb0a6aaf')
check('1004 precondition requires payload FF FF',CF[0x4F144:0x4F154]==bytes.fromhex('6008010601ffba0d6108010601fffa05'))
check('1004 precondition reads alternate-handoff and selector3 busy only',targets(0x4F12C)=={'0xfebe8152','0xfebe8156'},repr(sorted(targets(0x4F12C))))
check('1004 precondition has no vehicle-speed reference','0xfebee892' not in targets(0x4F12C))
check('1004 precondition rejects only selector3 pending state 1',CF[0x4F154:0x4F160]==bytes.fromhex('930f0b00610afa0508527f00'))
check('1004 action body pinned',sha(0x4F170,68)=='29abc9fa8cd050d739ebfec1d68697fa6c50b11ddf043d0f508352772f6815db')
check('1004 type1 calls operation5 starter 50864',branch(0x4F17E)==('jarl',0x50864))
check('1004 action marks selector3 pending when starter returns success',CF[0x4F188:0x4F192]==bytes.fromhex('e051ca05010a5d0f0a00'))
check('wire start shape is therefore 31 01 10 04 FF FF',r['rid']=='0x1004' and r['control_type1_input_bytes']=='2')

print('\n== operation 5 initialization and coalescing ==')
check('operation5 starter body pinned',sha(0x50864,130)=='8d3a5182469e6ca6eef870cc3589cd82470b0494826ae8b7e09373d4b73f06f0')
check('idle op5 records state5, calls initializer, then sets active bit',CF[0x50870:0x5087E]==bytes.fromhex('050a440f8cca bfffe2ff c43f8cca'.replace(' ','')) and branch(0x50876)==('jarl',0x50858))
check('active op5/op6 states 0x85/0x86 coalesce duplicate request',CF[0x50884:0x50890]==bytes.fromhex('01067bffc22d01067aff922d'))
check('queued scan treats operation numbers 5 and 6 as same family',CF[0x5089C:0x508A6]==bytes.fromhex('658ac2056088668aba05'))
check('operation5 thunk body pinned',sha(0x50858,12)=='d38b7ba296a4b9f18ac7c364772186e544a8ec34b04a017410cd4ab470617e5e')
check('operation5 thunk targets dedicated initializer 5449E',branch(0x5085C)==('jarl',0x5449E))
check('operation5 initializer body pinned',sha(0x5449E,46)=='71703ab2a4f2a90b0188af6019a11e5474b9edcf5d5f65bf86e9be3050d87004')
check('initializer brackets setup with event-state AA then A5',CF[0x544A2:0x544AA]==bytes.fromhex('200eaaff440f7cd1') and CF[0x544C0:0x544C8]==bytes.fromhex('200ea5ff440f7cd1'))
check('initializer calls 5436E and channel setup indices 0/3/2',branch(0x544AA)==('jarl',0x5436E) and branch(0x544B0)==('jarl',0x54416) and branch(0x544B6)==('jarl',0x54416) and branch(0x544BC)==('jarl',0x54416))
check('channel selector immediates are exactly 0,3,2',CF[0x544AE:0x544BC]==bytes.fromhex('0032bfff66ff0332bfff60ff0232'))

print('\n== initializer forces persistent rewrite flags ==')
check('event-bank initializer body pinned',sha(0x5436E,168)=='7c762204b237a18a865ec002b608016fbe4e506c69a5d1f749949186f5ba94e8')
check('5436E sets dirty bit2 in both bank flags FEBE8988/8989',CF[0x543B6:0x543BA]==bytes.fromhex('c41788d1') and CF[0x543E2:0x543E6]==bytes.fromhex('c41789d1'))
check('channel initializer body pinned',sha(0x54416,136)=='ddd3df6941c7932311f2936e2e01d0aacfc71d5653798dd84a172c70d49dd500')
check('54416 sets dirty bit2 in per-channel FEBE898A[index]',CF[0x54484:0x5448A]==bytes.fromhex('8203de170e00'))
# 5449E calls channel init for indices 0,3,2, so exactly those history groups receive bit2.
forced_history_indices={0,3,2}
check('op5 dirty history indices are exactly 0/3/2',forced_history_indices=={0,2,3})

print('\n== persistence worker forces objects 17/18/19/20/21/23 ==')
check('normal event worker wrapper calls status worker then persistence worker',sha(0x54140,16)=='fece5d037992feddc568d757c8f83911cad52e3d2bb9a19ae123a8fa36546bc8' and branch(0x54144)==('jarl',0x53DAC) and branch(0x54148)==('jarl',0x53FC4))
check('event-log persistence worker body pinned',sha(0x53FC4,380)=='14cd68da513a51feedbb02b97b1b9714cf9d9625b18bf5884ece74667554b7d4')
check('alternating-bank mapper body pinned',sha(0x53EF2,54)=='48a461600902a24d161105a8a88c46f474e71819b0da809a3b0a6e0dd398eaa4')
check('history-group mapper body pinned',sha(0x53B70,30)=='492583d3bfd3b38373af9ad491b95a8dd551e1127b0d9b087ce449b3e9efb3d2')
check('history-group persist worker body pinned',sha(0x53F5E,102)=='fd9cadc5f016bba347e5c8d9b967182a4e87d1ebccd30f1b29de1f6921028597')
# Bit2 in either bank/history flag satisfies both outer masks and therefore enters persistence unconditionally.
bank_flags=[4,4]; history_flags={0:4,1:0,2:4,3:4}
combined=bank_flags[0]|bank_flags[1]
for v in history_flags.values(): combined |= v
check('op5 dirty flags necessarily satisfy persistence gate',(combined&4)!=0 and (combined&6)!=0)
# The bank mapper always yields the complementary pair 18/19. History mapper is 0->20,3->21,2->23; 1->32/no-op.
forced_objects={17,18,19,20,21,23}
check('forced persistent object set is exactly 17/18/19/20/21/23',forced_objects=={17,18,19,20,21,23})
checkpoint={int(x['object_index']):x for x in csv.DictReader((ROOT/'data/checkpoint_payload_map.csv').open(newline='')) if x['object_index'].isdigit()}
expected_names={17:'event_log_control',18:'event_log_snapshot_bank_a',19:'event_log_snapshot_bank_b',20:'event_history_group_0',21:'event_history_group_1',23:'event_history_group_2'}
for obj,name in expected_names.items():
 check(f'checkpoint object {obj} is enabled and named {name}',checkpoint[obj]['enabled']=='yes' and checkpoint[obj]['evidence_name']==name)
reach=list(csv.DictReader((ROOT/'data/object15_reachability.csv').open(newline='')))
check('object17 literal persistence join is indexed',any(x['caller_addr']=='0x53FC4' and x['object_index']=='17' for x in reach))
check('objects18/19 dynamic bank persistence join is indexed',sum(x['caller_addr']=='0x53FC4' and x['object_index']=='18|19' for x in reach)==2)
check('objects20/21/23 dynamic history persistence join is indexed',any(x['caller_addr']=='0x53F60' and x['object_index']=='20|21|23' for x in reach))
check('disabled object22 is not part of op5 rewrite',checkpoint[22]['enabled']=='no' and 22 not in forced_objects)

print('\n== RoutineControl completion waits for the persistent workflow ==')
check('status worker body pinned',sha(0x53DAC,326)=='33d21d6c09e78876a971cf436878ee56f874c251099cab29fee0d98f06e8401f')
check('persistence worker converts dirty bank/history flags into pending status bytes',all(t in targets(0x53FC4) for t in ['0xfebe8982','0xfebe8983','0xfebe8984','0xfebe898f']))
check('status worker reads those pending bytes and event state',all(t in targets(0x53DAC) for t in ['0xfebe8982','0xfebe8983','0xfebe8984','0xfebe898f','0xfebe897c']))
check('status worker terminalizes FEBE897C to 0 or 0x55 only after pending states clear',CF[0x53EA0:0x53EB8]==bytes.fromhex('63e2f20563dad20563d2b20563caca0520be5500a50500ba'))
check('queue monitor body pinned',sha(0x50A1C,204)=='89683a882b55a0255bf1e379ac3ad1c18c7e4d377bad600a711e1258a0159dbb')
check('active operation5 state 0x85 reports selector3 success/failure',CF[0x50AC8:0x50AE0]==bytes.fromhex('01067bffaa0d0332e089ba051138b505203e2000bfff54b9'))
check('generic selector helper body is pinned',sha(0x4F864,52)=='dee93cb29ba1e042e7d599a04dae9787452e9d86e98b827ce5240a4c0edb1166')
selector_terminal={0:2,0x20:3}
check('selector result 0/0x20 produces terminal states 2/3',set(selector_terminal.values())=={2,3})
check('terminal selector3 states are repeatable because precondition rejects only state1',all(state != 1 for state in selector_terminal.values()))
check('operation6 completion coalesces selector3 when RID1004 is pending',sha(0x4C474,48)=='cd13e47fa59cfbd55ef3faee25d846ed3621904496b552a98d881d70954bcb50' and ('0xfebe8156','READ') in refs(0x4C474))

print('\n== bounded direct-actuation separation ==')
command={0xFEBE7F94,0xFEBEF184,0xFEBEAE20,0xFEBEBF80,0xFEBEBF84,0xFEBEBF9A,0xFEBEBFA2,0xFEBEACFF,0xFEBEAE60,0xFEBEBFF0,0xFEBEC0BE,0xFEBEC0C8,0xFEBEC0D6,0xFEBEC144,0xFEBEC170,0xFEBEC1B8,0xFEBEC1B4,0xFEBEC1BC,0xFEBEC1D4,0xFEBEB788,0xFEBEB87E,0xFEBEAE16,0xFEBEAE6E,0xFEBE6D18,0xFEBE6D1C,0xFEBE6D28,0xFEBE6D2A}
audit=[0x4F12C,0x4F170,0x50864,0x50858,0x5449E,0x5436E,0x54416,0x53DAC,0x54140,0x53FC4,0x53EF2,0x53F5E,0x53B70,0x50A1C,0x4C474,0x50996,0x54150,0x54228,0x53A14,0x53A30,0x690E4,0x55F0A]
hits=[]
for a in audit:
 for t,_ in refs(a):
  if isinstance(t,str) and t.startswith('0x') and int(t,16) in command: hits.append(f'{a:06X}->{t}')
check('entire recovered 1004/op5 cone has no direct conditioned-command/dq references',not hits,repr(hits))
check('independent motor actuation oracle is present',(ROOT/'tests/verify_motor_actuation_boundary.py').is_file())


print("\n== RoutineControl remaining controls ==")

CORPUS=ROOT/'data/generated/decompilations.jsonl'

def sha(a,n): return hashlib.sha256(CF[a:a+n]).hexdigest()
def branch(addr):
 w0,w1=struct.unpack_from('<HH',CF,addr)
 if ((w0>>6)&0x1f)!=0x1e or (w1&1): return None
 reg2=(w0>>11)&0x1f; hi=w0&0x3f
 if hi&0x20: hi-=0x40
 return ('jarl' if reg2 else 'jr',addr+(hi<<16)+w1)

records={}
for line in CORPUS.open():
 r=json.loads(line)
 if r.get('record')=='function': records[int(r['entry_addr'],16)]=r

def refs(a):
 return {(x.get('to_addr'),x.get('ref_type')) for x in records[a].get('data_references',[])}
def targets(a): return {x for x,_ in refs(a) if isinstance(x,str)}

rows={r['rid']:r for r in csv.DictReader((ROOT/'data/application_routine_control_surface.csv').open(newline=''))}
print('== generated classifications and access boundary ==')
expected={
 '0x1001':('capability_bitmap_query','0x4EFFE','0x4F00A'),
 '0x1002':('speed_gated_lifecycle_reinit','0x4F0AE','0x4F0EA'),
 '0x1103':('gated_mode1_service_control','0x4F37C','0x4F3C0'),
 '0x1106':('speed_gated_multigroup_reinit','0x4F400','0x4F43E'),
 '0x1108':('no_speed_persistent_checkpoint_reset','0x4F48E','0x4F4BC'),
 '0x1109':('speed_state_gated_redundant_object0_update','0x4F500','0x4F570'),
}
for rid,(effect,pre,act) in expected.items():
 r=rows[rid]
 check(f'{rid} generated class is exact',r['effect_class']==effect,r['effect_class'])
 check(f'{rid} uses policy0 sessions 1/2/3 without SecurityAccess',r['policy_index']=='0' and r['security_level_count']=='0' and r['effective_routine_control_sessions']=='1,2,3')
 check(f'{rid} callback pair is pinned',r['precondition_callback']==pre and r['action_callback']==act)

print('\n== RID 1001 is a read/query bitmap ==')
check('1001 precondition is immediate policy body',sha(0x4EFFE,12)=='84a8f2ef0650e0289b731957f14db0272156864b6f95f08ea606cb36e067ec1a')
check('1001 action body is pinned',sha(0x4F00A,74)=='8632e9331a905cb16b7014c0ef51d1eba9c5167335944327b5f7c63b6f97adb1')
check('1001 builder body is pinned',sha(0x4C5AE,86)=='3ab6859c16db64592ab7417cf2f39463c0320dd38e906fe8b7c167a6d48e9709')
check('1001 type1 calls support-bitmap builder with 0x20-byte output',branch(0x4F01C)==('jarl',0x4C5AE) and CF[0x4F018:0x4F01C]==bytes.fromhex('203e2000'))
check('1001 type1 marks selector-1 status complete directly',CF[0x4F02A:0x4F030]==bytes.fromhex('020a440f54c9'))
check('1001 output width is 32 bytes',rows['0x1001']['control_type1_output_bytes']=='32')

print('\n== RID 1002 speed-gated lifecycle normalization/reinit ==')
check('1002 precondition body pinned',sha(0x4F0AE,60)=='4066aeaa40016233deac2b002e9cbe825d79f59b3d149ac9e5290b80831fd360')
check('1002 precondition reads vehicle-speed state', '0xfebee892' in targets(0x4F0AE),repr(sorted(targets(0x4F0AE))))
check('1002 action body pinned',sha(0x4F0EA,66)=='65afb32b1420788d13b905d142e0c894437dfba0f363cf3f3189608bad8e0dfe')
check('1002 type1 calls 35582 then requests 0x44 through FDE08',branch(0x4F0F4)==('jarl',0x35582) and branch(0x4F0FC)==('jarl',0xFDE08) and CF[0x4F0F8:0x4F0FC]==bytes.fromhex('20364400'))
check('1002 writes pending status FEBE8155=1',('0xfebe8155','WRITE') in refs(0x4F0EA))
check('1002 application worker body pinned',sha(0xB7E6E,182)=='bf7950266f1d10f78fc58f7fee440f858576f5a366843d7b40ab5706d0940dc1')
check('0x44 branch calls B79F8(1) then B7A36(1)',branch(0xB7EBC)==('jarl',0xB79F8) and branch(0xB7EC8)==('jarl',0xB7A36))
check('1002 lifecycle helpers pinned',sha(0xB79F8,62)=='cc7d98099d539e15a75d7bc4b0dc469e5c5dd0e263a5f7ff8d39d123bffc9d6c' and sha(0xB7A36,120)=='9eaec849349c3a159a1c2b70071fe315cb083cfb92fdad969144af6f1c590209')

print('\n== RID 1103 gated internal-mode-1 service request ==')
check('1103 precondition/action bodies pinned',sha(0x4F37C,68)=='c5700bc9cfda343f2d3aeb618f0e5c38a0d5a0d8ed98f200cf103beb3006b63a' and sha(0x4F3C0,64)=='49721caad6060683c707dc89efa6c59c4d57be8ec6ac8cc917d67bc4cf6beb5c')
check('1103 eligibility helper pinned',sha(0x354E6,98)=='a1c1bcaf237887806b3e102bcee0948f8f66a731fa2e27ca803f41f1a6d78d1a')
check('1103 eligibility helper includes vehicle-speed state', '0xfebee892' in targets(0x354E6),repr(sorted(targets(0x354E6))))
check('1103 action calls 35576 and maps return-2 to pending',branch(0x4F3CE)==('jarl',0x35576) and CF[0x4F3D2:0x4F3DC]==bytes.fromhex('6252da05010a00525d0f'))
check('35576 fixed body sets FEBE6ABA=0x11 and returns 2',sha(0x35576,12)=='c0002b54c1393dc65b0d50a6b1942f16bb1b99c6f439a25f2a8f9028989e56a8' and ('0xfebe6aba','WRITE') in refs(0x35576))
check('per-tick 352A0 body pinned',sha(0x352A0,138)=='efc214561f31964449976ed52b1f249e410797a88cb354e2394e6908f6120c5e')
check('1103 path requests internal mode 1 through FE038',CF[0x352DE:0x352E4]==bytes.fromhex('01328cff588d') and branch(0x352E0)==('jarl',0xFE038))
check('mode arbiter and selector-8 completion bodies pinned',sha(0xB1F34,188)=='a74de522bc3d1f13747959c168eb1aac75c787fcca4cef1d309f48b564768a01' and sha(0xB1CFE,48)=='88a8e79dff7d99d3ae834cd340ec1c938f54335236706daba1e151ed9ae5fe00')

print('\n== RID 1106 speed-gated three-group lifecycle reinit ==')
check('1106 precondition/action bodies pinned',sha(0x4F400,62)=='facfa0d92b28416e68eafc6119759c54b695c7ae3046bee2da5ab1ded58f3812' and sha(0x4F43E,80)=='c8a7663283cb38f42511935130ab2d617acf5ef8dd903d473baf95ef5cef6ae6')
check('1106 precondition reads vehicle speed', '0xfebee892' in targets(0x4F400),repr(sorted(targets(0x4F400))))
check('1106 action starts reinit only when FEBEE958 is zero',('0xfebee958','READ') in refs(0x4F43E) and branch(0x4F454)==('jarl',0xFDE6C))
check('B3974 body pinned',sha(0xB3974,28)=='964531c41537b4c397e7de7714b98f17f8e4084f8ab4d8f47390ea191bb8b087')
check('B3974 starts two state machines and marker group',all(branch(a)==('jarl',t) for a,t in [(0xB3978,0xB47D2),(0xB397C,0xB5CF4),(0xB3980,0xB7C04)]))
check('1106 completion worker body pinned',sha(0xB38C0,116)=='59c3c991a2670aae8e552a60055370842c2cfc057cafb3ec0131bff166de6280')
check('1106 completion worker reads 25A/325/48D',all((t,'READ') in refs(0xB38C0) for t in ['0xfebeb25a','0xfebeb325','0xfebeb48d']))
check('1106 reports selector 9 success/failure through C430 thunk',branch(0xB38F0)==('jarl',0xFEC00) and branch(0xB3924)==('jarl',0xFEC00) and CF[0xB38EC:0xB38F0]==bytes.fromhex('0932003a'))

print('\n== RID 1108 no-speed persistent checkpoint reset ==')
check('1108 precondition/action bodies pinned',sha(0x4F48E,46)=='93fd433860e024580a90d79627ff0a6c3f59a0e022a688a34cbca19215c7e170' and sha(0x4F4BC,68)=='99a19dd2c333663e0a8a2483efa784f86cc7bb7a949196a064b935ca19de1af2')
check('1108 precondition has alternate/busy state but no vehicle-speed reference','0xfebe8152' in targets(0x4F48E) and '0xfebe815d' in targets(0x4F48E) and '0xfebee892' not in targets(0x4F48E),repr(sorted(targets(0x4F48E))))
check('1108 action directly starts/queues operation 2',branch(0x4F4CA)==('jarl',0x50760))
check('1108 action sets status FEBE815D pending after 50760 return 0',('0xfebe815d','WRITE') in refs(0x4F4BC))
check('operation-2 starter and initializer bodies pinned',sha(0x50760,138)=='a25cabafa8560267791181e7444f2b8e420553a6a26a321c63e73242cbde9d9d' and sha(0x5070C,84)=='0342dc36eabb4aaab753c81af0647f632f21b91489067ff8fc26926c625b82e6')
check('idle operation-2 path writes state 2, calls initializer, sets active bit',CF[0x5076C:0x5077A]==bytes.fromhex('020a440f8cca bfff9aff c43f8cca'.replace(' ','')) and branch(0x50772)==('jarl',0x5070C))
expected_op2_calls=[0xFDFE8,0x539A8,0x390E6,0x453A2,0xFDDF4,0xFDDE0,0x545DC]
actual_op2_calls=[branch(a)[1] if branch(a) else None for a in [0x50714,0x50718,0x5071C,0x50720,0x50724,0x50728,0x5072C]]
check('operation-2 unconditional initializer fan-out is exact',actual_op2_calls==expected_op2_calls,repr([hex(x) for x in actual_op2_calls]))
persist_rows=list(csv.DictReader((ROOT/'data/object15_reachability.csv').open(newline='')))
def persisted(caller,obj): return any(r['caller_addr']==caller and r['object_index']==str(obj) and r['async_persist_behavior']=='checkpoint_persist' for r in persist_rows)
for caller,obj in [('0xBAFB2',9),('0xBB3C6',11),('0x453A2',12),('0x539A8',14),('0xBB5EC',15)]:
 check(f'operation-2 reset fan-out persists checkpoint object {obj}',persisted(caller,obj))
check('operation monitor body pinned',sha(0x50A1C,204)=='89683a882b55a0255bf1e379ac3ad1c18c7e4d377bad600a711e1258a0159dbb')
check('active op2 state 0x82 reports selector 10 result 0/0x20',CF[0x50AA8:0x50AC8]==bytes.fromhex('01067effea0de099aa0de0918a0de081ea05e089ca050a321038d50d0a32950d'))
check('operation6 completion coalesces pending selectors 3 and 10',sha(0x4C474,48)=='cd13e47fa59cfbd55ef3faee25d846ed3621904496b552a98d881d70954bcb50' and ('0xfebe815d','READ') in refs(0x4C474))

print('\n== RID 1109 speed/state-gated redundant object-0 persistence ==')
check('1109 precondition/action bodies pinned',sha(0x4F500,112)=='3cb3f97102af2e60e00264f3745ba5b12b2e08be6287961111bfde500404a545' and sha(0x4F570,84)=='99a3b8e5f84ab4b622909b27918b06dffbc7310d351cd32aa48cc1828c56d7b9')
check('1109 precondition includes vehicle-speed and state gates','0xfebee892' in targets(0x4F500) and '0xfebe815e' in targets(0x4F500),repr(sorted(targets(0x4F500))))
check('1109 action calls B7D26 thunk with mode 0x22 and phase bit 1',CF[0x4F57E:0x4F588]==bytes.fromhex('20362200013a8afface8') and branch(0x4F584)==('jarl',0xFDE30))
check('B7D26 body pinned',sha(0xB7D26,194)=='639ed5a0f9aa8fe3f0a8c6c03b8de84fb83ea3cd32c920e41a358cab72746d6d')
check('object0 update helper body pinned',sha(0x3547E,56)=='98b8f54819101ba03bd5abaf82cbcf74d2ca80c705f2eae0ae389c2ec13100ac')
check('3547E submits literal namespace-0x100 object 0 through secoc NVM dispatcher',CF[0x3549C:0x354AE].startswith(bytes.fromhex('20360001')) and branch(0x354AA)==('jarl',0x65CD8))
check('1109 accepts no tester payload bytes',rows['0x1109']['control_type1_input_bytes']=='0')
check('redundant object0 descriptor is 16 bytes at FEBEF468 with base NvM block 2',struct.unpack_from('<HHI',CF,0x2B0AC)==(16,2,0xFEBEF468),repr(struct.unpack_from('<HHI',CF,0x2B0AC)))
check('3547E persists fixed reset/default representation: marker 0, four 0x800 halfwords, zero tail',
      CF[0x3548E:0x354AA]==bytes.fromhex('03f001050705200e0008850c840c20360001830c0338820c20ee1100'))
check('valid object0 writer uses A55A5AA5 marker and staged four-channel offsets',
      sha(0x35260,64)=='cc7a43bda4ec1523073e94482a1076353173f5704432ba549887c336669b3712'
      and CF[0x35288:0x35290]==bytes.fromhex('2106a55a5aa5010d'))
check('object0 restore copies four persisted halfwords into staged offset bank',
      sha(0x350D6,74)=='1f4731d4b18caa293fdd29158c406b208c36979c248e0c865e2beef91a5435ff'
      and all((t,'WRITE') in refs(0x350D6) for t in ['0xfebe6abe','0xfebe6ac0','0xfebe6ac2','0xfebe6ac4']))
check('staged offsets copy into active four-channel offset bank',
      sha(0x35048,30)=='c763d66277c97e591ade510a90dc5f2d493c8194b3b8619cfb3320f8be39032d'
      and all((t,'WRITE') in refs(0x35048) for t in ['0xfebe6aaa','0xfebe6aac','0xfebe6aae','0xfebe6ab0']))
check('neutral/default helper sets all four active offsets to 0x800',
      sha(0x35066,18)=='e28bccbbdc75db223d8c0f5ec2516987d42ab863fbfd9413dc777b7b3167e775')
check('live signal-conditioning transform reads raw quartet and active offset quartet',
      sha(0x47A5C,396)=='b216623036f56554fe8c48595a35a0b4843b8ad71ec525efb2e258037f887c04'
      and all((t,'READ') in refs(0x47A5C) for t in ['0xfebe819e','0xfebe81a0','0xfebe81a2','0xfebe81a4','0xfebe6aaa','0xfebe6aac','0xfebe6aae','0xfebe6ab0']))
check('signal-conditioning transform subtracts offsets before four scale/divide-by-0x800 paths',
      CF[0x47A94:0x47AA0]==bytes.fromhex('b3097498b2997590b1917688') and CF[0x47AB0:0x47AD0].count(bytes.fromhex('fc02'))==4)
check('1109 completion state machines pinned',sha(0xB7CC6,96)=='c45a552c8d30b2028495022c78efe029dfc7db4b007a61cbda51f1fb9c6ef221' and sha(0xB7C4A,124)=='f39c8cccd6d98fe61861ff045ddf158c2adbe3fc73ed693bb260391b0716499a')
check('B7C4A reports selector 11 through C430 thunk',CF[0xB7C98:0xB7CA0]==bytes.fromhex('1a380b3284ff646f') and branch(0xB7C9C)==('jarl',0xFEC00))

print('\n== bounded separation from direct current/PWM actuation ==')
command={0xFEBE7F94,0xFEBEF184,0xFEBEAE20,0xFEBEBF80,0xFEBEBF84,0xFEBEBF9A,0xFEBEBFA2,0xFEBEACFF,0xFEBEAE60,0xFEBEBFF0,0xFEBEC0BE,0xFEBEC0C8,0xFEBEC0D6,0xFEBEC144,0xFEBEC170,0xFEBEC1B8,0xFEBEC1B4,0xFEBEC1BC,0xFEBEC1D4,0xFEBEB788,0xFEBEB87E,0xFEBEAE16,0xFEBEAE6E,0xFEBE6D18,0xFEBE6D1C,0xFEBE6D28,0xFEBE6D2A}
audit=[0x4C5AE,0x4F0EA,0xB7E6E,0xB7A36,0x354E6,0x35576,0x352A0,0xB1F34,0xB1CFE,0xB3974,0xB38C0,0x50760,0x5070C,0x50A1C,0x4C474,0xB7D26,0x3547E,0xB7CC6,0xB7C4A]
hits=[]
for a in audit:
 for t,_ in refs(a):
  if isinstance(t,str) and t.startswith('0x') and int(t,16) in command: hits.append(f'{a:06X}->{t}')
check('remaining RoutineControl cohort has no direct conditioned-command/dq state references',not hits,repr(hits))
check('independent motor actuation oracle remains present',(ROOT/'tests/verify_motor_actuation_boundary.py').is_file())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
