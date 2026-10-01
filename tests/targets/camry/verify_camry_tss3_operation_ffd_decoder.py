#!/usr/bin/env python3
"""Verify shared TSS3 Operation-FFD framing and recovered viewer value rules."""
from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.techstream import tss3_operation_ffd as decoder

TOOL = REPO_ROOT / "tools/targets/camry/utilities/decode_camry_tss3_operation_ffd.py"
passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def block(data_id: int, payload: bytes) -> bytes:
    return data_id.to_bytes(2, "big") + bytes((len(payload),)) + payload


def rejects(name, callback):
    try:
        callback()
    except ValueError:
        check(name, True)
    else:
        check(name, False, "accepted malformed input")


# The seventh header byte is the count; it is not the first byte of a DID.
blocks = [
    (0x5282, bytes.fromhex("0BFF9C6400")),
    (0x5285, bytes.fromhex("0B")),
    (0x57DE, bytes.fromhex("FF9C")),
    (0x5265, bytes.fromhex("808080") + bytes(9) + bytes.fromhex("8080")),
    (0x560D, bytes.fromhex("00000000640000")),
    (0x5631, bytes.fromhex("0BFF066432")),
    (0x0501, bytes.fromhex("FFFF0000000100")),
    (0x9999, bytes.fromhex("AABB")),
    (0x5261, struct.pack(">f", -0.5)),
    (0x5A08, bytes.fromhex("E0A0")),
]
stream = b"".join(block(did, payload) for did, payload in blocks)
header = bytes.fromhex("EB1328450001")
fixture = header + bytes((len(blocks),)) + stream

print("== EB13 grammar ==")
parsed = decoder.parse_eb13(fixture, expected=(0x2845, 1))
check("behavior/record echoes and declared count", (parsed.behavior_id, parsed.record_id, parsed.declared_count) == (0x2845, 1, len(blocks)))
check("all blocks retain their boundaries and bytes", [(b.data_id, b.data) for b in parsed.blocks] == blocks)
zero = decoder.parse_eb13(header + b"\x00" + stream)
check("zero count scans the complete stream", zero.declared_count == 0 and zero.blocks == parsed.blocks)
check("empty zero-count record", decoder.parse_eb13(header + b"\x00").blocks == [])
repeated = decoder.parse_eb13(header + b"\x02" + block(0x9999, b"") + block(0x9999, b"a"))
check("repeated IDs and zero-length blocks retain order", [(b.data_id, b.data) for b in repeated.blocks] == [(0x9999, b""), (0x9999, b"a")])
for name, malformed in (
    ("wrong service rejected", b"\x62\x13" + fixture[2:]),
    ("missing count byte rejected", header),
    ("short header rejected", header[:4]),
    ("truncated block header rejected", header + bytes.fromhex("0152")),
    ("truncated block payload rejected", header + bytes.fromhex("01528205AA")),
    ("too few blocks rejected", header + b"\x02" + block(0x5285, b"\x0b")),
    ("trailing blocks rejected", header + b"\x01" + stream),
    ("zero-count trailing fragment rejected", header + b"\x00" + stream + b"\x52"),
):
    rejects(name, lambda pdu=malformed: decoder.parse_eb13(pdu))
for expected in ((0x2846, 1), (0x2845, 2)):
    rejects(f"echo mismatch {expected} rejected", lambda expected=expected: decoder.parse_eb13(fixture, expected=expected))
rejects("filter cannot hide malformed blocks", lambda: decoder.decode_eb13(header + bytes.fromhex("01999902AA"), only={0x5282}))

print("\n== managed-semantics decode ==")
semantics = decoder.load_semantics()
result = decoder.decode_eb13(fixture, semantics)
by_id = {row["data_id"]: row for row in result["blocks"]}


def signal(did, name):
    return next(row for row in by_id[did]["decoded"] if row["name"] == name)


check("5282 lateral ID", signal("0x5282", "TSS request - lateral ID")["physical"] == "11")
pinion = signal("0x5282", "TSS request - pinion angle")
check("signed pinion preserves unsigned raw bits", pinion["raw"] == 0xFF9C and pinion["physical"] == "-0.100")
check("assist/damping scales", signal("0x5282", "Steering assist gain")["physical"] == "1.00" and signal("0x5282", "Damping control gain")["physical"] == "0.00")
check("arbitration lateral ID", by_id["0x5285"]["decoded"][0]["physical"] == "11")
check("arbitration pinion", by_id["0x57DE"]["decoded"][0]["physical"] == "-0.100")
check("LTA negative pinion", signal("0x5631", "LTA Control Request Pinion Angle")["physical"] == "-0.250")
check("EPS positive pinion", signal("0x560D", "EPS Pinion Angle")["physical"] == "0.100")
check("active-steering support/value MSBs", signal("0x5265", "Active steering under-control flag")["raw"] == 1)
check("ABS support/value MSBs", signal("0x5265", "ABS under-control")["raw"] == 1)
check("supported zero differs from unsupported", signal("0x5265", "VSC under-control")["raw"] == 0 and signal("0x5265", "VSC under-control")["supported"] is True)
trip = signal("0x0501", "Trip count [trip]")
check("invalid integer has no physical value", trip["raw"] == 0xFFFF and trip["invalid"] is True and trip["physical"] is None)
check("closed-accelerator IEEE-754 value", by_id["0x5261"]["decoded"][0]["physical"] == "-0.500")
check("5A08 support bitmap qualifies separate value bits", [r["raw"] for r in by_id["0x5A08"]["decoded"]] == [1, 0, 1])
check("unknown DID retains raw bytes without invented fields", by_id["0x9999"]["data"] == "aabb" and by_id["0x9999"]["decoded"] == [])
check("complete fixture has no field errors", all("decode_error" not in field for row in result["blocks"] for field in row["decoded"]))
for payload in (bytes.fromhex("00A0"), b"\x00"):
    unsupported = decoder.decode_blocks([decoder.RecorderBlock(0x5A08, payload)], semantics)[0]["decoded"]
    check(f"absent support suppresses stale/missing values {payload.hex()}", all(r["supported"] is False and "raw" not in r and "physical" not in r for r in unsupported))
short = decoder.decode_eb13(header + b"\x02" + block(0x5282, b"\x0b") + block(0x9999, b"\xaa"), semantics)
check("short field reports error while preserving other data", short["blocks"][0]["decoded"][0]["raw"] == 11 and "decode_error" in short["blocks"][0]["decoded"][1] and short["blocks"][1]["data"] == "aa")

# These exercise numeric boundaries, not schema-row spelling or copied metadata.
row = dict(semantics[0x5282][1], BytePosition=1, BitPosition=7, BitLength=16, Lsb="0.001", Offset="0", Point=2)
for raw, expected in ((1239, "1.23"), (-1231, "-1.24"), (-32768, "-32.77"), (32767, "32.76")):
    value = decoder.decode_signal(raw.to_bytes(2, "big", signed=True), row)
    check(f"signed scale and floor {raw}", value["physical"] == expected)
check("Point zero floors instead of rounding", decoder.decode_signal(b"\x00\x0f", dict(row, Lsb="0.1", Point=0))["physical"] == "1")
check("packed signed field across bytes", decoder.decode_signal(bytes.fromhex("2AAA"), dict(row, BitPosition=5, BitLength=12, Lsb="1", Point=0))["physical"] == "-1366")
for kind, width, fmt in (("f", 32, ">f"), ("d", 64, ">d")):
    floating = dict(row, Type=kind, BitLength=width, Lsb="1", Point=3)
    for value, expected in ((12.5, "12.500"), (-0.5, "-0.500"), (-1.2341, "-1.235")):
        check(f"{kind} IEEE conversion and floor {value}", decoder.decode_signal(struct.pack(fmt, value), floating)["physical"] == expected)
    nan = decoder.decode_signal(struct.pack(fmt, float("nan")), floating)
    check(f"{kind} NaN is invalid without a sentinel row", nan["invalid"] is True and nan["physical"] is None)
    for value, expected in ((float("inf"), "Infinity"), (-float("inf"), "-Infinity")):
        infinite = decoder.decode_signal(struct.pack(fmt, value), floating)
        check(f"{kind} infinity stays JSON-safe", infinite["physical"] == expected and json.loads(json.dumps(infinite, allow_nan=False))["physical"] == expected)
    zero_invalid = decoder.decode_signal(struct.pack(fmt, -0.0), dict(floating, InvalidValueList=["0x" + "00" * (width // 8)]))
    check(f"{kind} invalid float compares numeric value", zero_invalid["invalid"] is True and zero_invalid["physical"] is None)

for payload, expected in (("261001123456", ["26", "10", "01", "12", "34", "56"]), ("39130024606A", [None] * 6)):
    dates = decoder.decode_blocks([decoder.RecorderBlock(0x0507, bytes.fromhex(payload))], semantics)[0]["decoded"]
    check(f"BCD timestamp components and bounds {payload}", [r["physical"] for r in dates] == expected)

filtered = decoder.decode_eb13(fixture, semantics, only={0x5282, 0x57DE})
check("filter selects output without changing record count", [row["data_id"] for row in filtered["blocks"]] == ["0x5282", "0x57DE"] and filtered["parsed_block_count"] == len(blocks))

print("\n== CLI ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "decoded.json"
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--hex", fixture.hex(), "--only", "5261", "--only", "0x5A08", "--out", str(out)],
        cwd=td, capture_output=True, text=True, check=False,
    )
    cli = json.loads(out.read_text()) if out.exists() else {}
    check("CLI loads repository schema outside repo and decodes selected values", proc.returncode == 0 and
          [r["data_id"] for r in cli.get("blocks", [])] == ["0x5261", "0x5A08"] and
          cli["blocks"][0]["decoded"][0]["physical"] == "-0.500" and
          [r["physical"] for r in cli["blocks"][1]["decoded"]] == ["1", "0", "1"], proc.stderr[-300:])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
