#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FW = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
OUT = REPO / "data/generated/sienna_8965B4512000_techstream_did_semantics.json"

passed = failed = 0
oracle = "raw_bytes"


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


obj = json.loads(OUT.read_text())
rows = {int(x["did"], 16): x for x in obj["dids"]}
companions = {int(x["did"], 16): x for x in obj["companion_dids"]}

print("== exact Sienna DID table ==")
D = struct.Struct("<HHIII")
dids = {}
for i in range(0xF2):
    did, length, callback, arg1, arg2 = D.unpack_from(FW, 0x2941C + i * 16)
    dids[did] = (length, callback, arg1, arg2)
expect = {
    0x1151: 0x4D71C, 0x1152: 0x4D758, 0x1153: 0x4D794, 0x1154: 0x4D7D0,
    0x1155: 0x4D80C, 0x1156: 0x4D856, 0x1185: 0x4D930, 0x1C02: 0x4DB5E,
}
check("eight observer DIDs map to exact callbacks", {d: dids[d][1] for d in expect} == expect)
check("all eight are declared 2-byte RDBI values", all(dids[d][0] == 2 for d in expect))
check("0x1065 companion is one-byte callback 0x4D084", dids[0x1065][:2] == (1, 0x4D084))

print("\n== callback/supporting body identities ==")
for x in obj["dids"]:
    address = int(x["callback"], 16)
    check(f"{x['did']} callback body identity", hashlib.sha256(FW[address:address + x["size"]]).hexdigest() == x["callback_sha256"])
for x in obj["companion_dids"]:
    address = int(x["callback"], 16)
    check(f"{x['did']} companion callback identity", hashlib.sha256(FW[address:address + x["size"]]).hexdigest() == x["callback_sha256"])
for x in obj["supporting_functions"]:
    address = int(x["address"], 16)
    check(f"{x['role']} body identity", hashlib.sha256(FW[address:address + x["size"]]).hexdigest() == x["sha256"])

print("\n== exact Techstream Data-ID vocabulary ==")
h = json.loads((REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json").read_text())
monitor_rows = h["ddb_overlap"]["emps_p5"]["monitor_rows"]
known = {int(r["primary_data_id"], 16): r for r in monitor_rows}
for did, x in rows.items():
    src = known[did]
    check(f"{x['did']} primary Data ID exact", x["techstream_primary_data_id"].lower() == f"0x{did:04x}")
    check(f"{x['did']} Techstream name exact", x["techstream_name"] == src["name"])
    check(f"{x['did']} alternate Data ID exact", x["techstream_alternate_data_id"] == src["alternate_data_id"])
    check(f"{x['did']} DDB record identity", x["techstream_record_sha256"] == src["ddb_record_sha256"] and x["techstream_record_index"] == src["ddb_record_index"])
check("all eight DDB record hashes populated", all(x["techstream_record_sha256"] for x in rows.values()))

print("\n== target-native emitted encodings and producer/control chains ==")
code = {}
for line in (REPO / "data/generated/decompilations.jsonl").open():
    record = json.loads(line)
    if record.get("entry_addr") and record.get("decompiled_c"):
        code[record["entry_addr"].lower()] = record["decompiled_c"]

callback_checks = [
    ("1151 Q actual scale", "0x0004d71c", "DAT_febe66e6 * 100", "/ 0x80", "0x7fff", "0xffff8000"),
    ("1152 Q command scale", "0x0004d758", "DAT_febe66fc * 100", "/ 0x80", "0x7fff", "0xffff8000"),
    ("1153 D actual scale", "0x0004d794", "DAT_febe66e4 * 100", "/ 0x80", "0x7fff", "0xffff8000"),
    ("1154 D command scale", "0x0004d7d0", "DAT_febe66fe * 100", "/ 0x80", "0x7fff", "0xffff8000"),
    ("1155 angle scale and invalid gate", "0x0004d80c", "FUN_00051708(0x52)", "* 0x465 >> 0xb", "0xffff"),
    ("1156 nonnegative Q limit scale", "0x0004d856", "DAT_febe6764 * 100", "/ 0x80", "0x7fff,0"),
    ("1185 protected speed cap", "0x0004d930", "DAT_febe8070", "30000"),
    ("1C02 command-torque dimensional scale", "0x0004db5e", "DAT_febe674a * (uint)DAT_febee8a6", "/ 0x2000", "* 100", "/ 0x100", "20000"),
    ("1065 limit-positive companion", "0x0004d084", "0 < DAT_febe6764", "*param_1 = auStack_9[0]"),
]
for name, address, *needles in callback_checks:
    check(name, all(n in code.get(address, "") for n in needles))

chain_checks = [
    ("Q/D feedback combine", "0x00037644", "DAT_febe6d18 =", "DAT_febe6d1a ="),
    ("Q/D base and compensated references", "0x00037712", "DAT_febe6d2c = DAT_febe6d7e", "DAT_febe6d2e = DAT_febe6d70", "DAT_febe6d28", "DAT_febe6d24"),
    ("diagnostic staging", "0x0005c0b6", "DAT_febe66e6 = DAT_febe6d1a", "DAT_febe66fc = DAT_febe6d2c", "DAT_febe66e4 = DAT_febe6d18", "DAT_febe66fe = DAT_febe6d2e"),
    ("Q command input latch", "0x00037fa2", "DAT_febe6db2 = DAT_febe6acc"),
    ("Q sign/magnitude map", "0x00037cd4", "FUN_00037b92", "DAT_febe6db2", "iVar4 = -iVar4"),
    ("motor sign junction", "0x0003572c", "DAT_febe6acc = -sVar1", "DAT_febee40c"),
    ("command torque RTE snapshot", "0x000bcace", "DAT_febee40a = DAT_febeac56", "DAT_febee40c = DAT_febeac54", "DAT_febee414 = DAT_febeac7e"),
    ("command torque state publish", "0x000cb454", "DAT_febeac56 = DAT_febec1d2"),
    ("command torque scale and limit", "0x000cadd6", "DAT_febec1d2", "DAT_febec1d6", "DAT_febeac4c"),
    ("limited command sibling", "0x000cae26", "DAT_febec1d4 = DAT_febec1d6", "0x569a"),
    ("secondary command contributor sum", "0x000cac14", "DAT_febec1b8", "DAT_febec170", "DAT_febebe2a", "DAT_febebc88", "DAT_febec19c"),
    ("Q current limit snapshot", "0x000bca88", "DAT_febee608 = DAT_febeaf40"),
    ("Q current limit selection", "0x000b8ed0", "DAT_febeb554", "0x569a"),
    ("motor angle Dem state query", "0x00051708", "param_1 & 0xffff", "uVar1 < 0x180", "DAT_febe6068", "DAT_febe6098", "DAT_febe60c8"),
    ("protected 0D7 speed unpacker", "0x0004b3aa", "DAT_febe8070"),
]
for name, address, *needles in chain_checks:
    check(name, all(n in code.get(address, "") for n in needles))

print("\n== capture-model boundaries ==")
check("1C02 remains general internal torque observer", "general internal command-value-torque" in obj["boundary"])
check("Q command distinguishes base from compensated PI state", "compensated PI reference is FEBE6D24" in rows[0x1152]["control_role"])
check("D command distinguishes base from compensated PI state", "compensated PI reference is FEBE6D28" in rows[0x1154]["control_role"])
check("1185 explicitly distinct from 0102", "distinct from DID 0x0102" in rows[0x1185]["control_role"])
check("1155 invalid marker recorded", "0xFFFF" in rows[0x1155]["emitted_encoding"])
validity = obj["motor_angle_validity"]
check("event 0x52 raw record exact", validity["event_record_address"] == "0x0003006C" and validity["event_record_raw"] == "0000000000010000" and FW[0x3006C:0x30074].hex() == validity["event_record_raw"])
check("event 0x52 carries DTC-table index zero", validity["dtc_table_index"] == 0 and FW[0x3006E] == 0)
check("1156 companion points to 1065", rows[0x1156]["companion_did"] == "0x1065" and 0x1065 in companions)
check("capture card covers nine prioritized reads", [x["did"] for x in obj["capture_card"]] == obj["observer_priority"])
check("bounded residue keeps event 0x52 producer unresolved", any("event 0x52" in x for x in obj["bounded_residues"]))
check("bounded residue keeps external 2E4 contribution unresolved", any("0x2E4" in x for x in obj["bounded_residues"]))

print("\n== regeneration ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "x.json"
    result = subprocess.run([sys.executable, str(REPO / "tools/techstream/generate_sienna_techstream_did_semantics.py"), "--output", str(out)], check=False)
    check("generator exits", result.returncode == 0)
    check("byte-identical regeneration", out.read_bytes() == OUT.read_bytes())

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
