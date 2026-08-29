#!/usr/bin/env python3
"""Verify offline Camry TSS3 Operation-FFD EB13 parsing and OEM field decode."""
from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
from importlib import import_module
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

decoder = import_module("tools.decode_camry_tss3_operation_ffd")
decode_eb13 = decoder.decode_eb13
load_semantics = decoder.load_semantics
parse_eb13 = decoder.parse_eb13

TOOL = REPO / "tools/decode_camry_tss3_operation_ffd.py"

passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def block(data_id: int, payload: bytes) -> bytes:
    return data_id.to_bytes(2, "big") + bytes((len(payload),)) + payload


fixture = (
    bytes.fromhex("EB1328450001")
    + block(0x5282, bytes.fromhex("0BFF9C6400"))
    + block(0x5285, bytes.fromhex("0B"))
    + block(0x57DE, bytes.fromhex("FF9C"))
    + block(0x5265, bytes(13) + b"\x80")
    + block(0x560D, bytes.fromhex("00000000640000"))
    + block(0x0501, bytes.fromhex("FFFF0000000100"))
    + block(0x9999, bytes.fromhex("AABB"))
    + block(0x5230, struct.pack(">f", 12.5))
)

print("== EB13 grammar ==")
parsed = parse_eb13(fixture)
check("service/behavior/record decode", (parsed["service"], parsed["behavior"], parsed["record"]) == ("EB13", "0x2845", "0x0001"))
check("all block IDs and lengths decode", [(b["data_id"], b["length"]) for b in parsed["blocks"]] == [
    ("5282", 5), ("5285", 1), ("57DE", 2), ("5265", 14), ("560D", 7), ("0501", 7), ("9999", 2),
    ("5230", 4),
])
for name, malformed, text in (
    ("wrong service rejected", bytes.fromhex("621328450001"), "expected EB13"),
    ("short header rejected", bytes.fromhex("EB132845"), "need at least 6"),
    ("truncated block rejected", bytes.fromhex("EB1328450001528205AA"), "declares 5 bytes"),
):
    try:
        parse_eb13(malformed)
    except ValueError as exc:
        check(name, text in str(exc), str(exc))
    else:
        check(name, False, "accepted malformed PDU")

print("\n== managed-semantics decode ==")
semantics = load_semantics()
result = decode_eb13(fixture, semantics)
by_id = {row["data_id"]: row for row in result["blocks"]}
fields_5282 = {row["name"]: row for row in by_id["5282"]["fields"]}
check("5282 Target Lateral ID", fields_5282["TSS request - lateral ID"]["raw"] == 11 and fields_5282["TSS request - lateral ID"]["display"] == "11")
check("5282 signed request pinion", fields_5282["TSS request - pinion angle"]["raw"] == 0xFF9C and fields_5282["TSS request - pinion angle"]["display"] == "-0.100")
check("5282 assist/damping gains", fields_5282["Steering assist gain"]["display"] == "1.00" and fields_5282["Damping control gain"]["display"] == "0.00")
check("5285 arbitration winner ID", by_id["5285"]["fields"][0]["display"] == "11")
check("57DE arbitration winner pinion", by_id["57DE"]["fields"][0]["display"] == "-0.100")
active = next(row for row in by_id["5265"]["fields"] if row["name"] == "Active steering under-control flag")
check("5265 active-steering bit uses byte14 MSB", active["raw"] == 1 and active["display"] == "1")
eps = next(row for row in by_id["560D"]["fields"] if row["name"] == "EPS Pinion Angle")
check("560D EPS pinion signed scale", eps["raw"] == 100 and eps["display"] == "0.100")
trip = next(row for row in by_id["0501"]["fields"] if row["name"] == "Trip count [trip]")
check("invalid-value list is honored", trip["raw"] == 0xFFFF and trip["invalid"] is True)
check("IEEE-754 recorder float decodes", by_id["5230"]["fields"][0]["display"] == "12.500")
check("unknown DID is retained raw", by_id["9999"] == {
    "data_id": "9999", "length": 2, "raw": "aabb", "known": False, "fields": [], "errors": [],
})
check("decode has no field errors", all(not row["errors"] for row in result["blocks"]))

filtered = decode_eb13(fixture, semantics, {"0x5282", "57DE"})
check("DID filter is exact", [row["data_id"] for row in filtered["blocks"]] == ["5282", "57DE"])

print("\n== CLI ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "decoded.json"
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--hex", fixture.hex(), "--only", "5265", "--out", str(out)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    cli = json.loads(out.read_text()) if out.exists() else {}
    check("CLI succeeds", proc.returncode == 0, proc.stderr[-300:])
    check("CLI writes filtered deterministic JSON", [row["data_id"] for row in cli.get("blocks", [])] == ["5265"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
