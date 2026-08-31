#!/usr/bin/env python3
"""Verify the offline Camry FRC-style 0x160 request PoC against retained wire frames."""
from __future__ import annotations

import gzip
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.camry_frc_request_poc import (
    build_0x160_request,
    decode_signed7,
    encode_signed7,
)
from tools.toyota_e2e_p05 import (
    crc16_ccitt,
    e2e_p05_check,
    e2e_p05_protect,
    e2e_p05_recover_data_id,
)

RAW = REPO / "targets/camry-2026/raw-20260827"
DRIVES = (
    RAW / "camry_relay_route_can_20260827.ndjson.gz",
    RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
)

passed = failed = 0


def check(name: str, condition, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


print("== exact Profile-5 primitive ==")
check("CRC-16/CCITT-FALSE standard check vector", crc16_ccitt(b"123456789") == 0x29B1)

print("== signed7 codec ==")
check("signed7 endpoints", encode_signed7(-64) == 0x40 and encode_signed7(63) == 0x3F)
check("signed7 roundtrip", all(decode_signed7(encode_signed7(v)) == v for v in range(-64, 64)))

print("== fixed retained witnesses ==")
a = bytes.fromhex("f13bf182800040034de80b0000a80080012f80c0000000140000000000000000")
b = bytes.fromhex("8420b582800040034de80b007fa80080012f80c0000000140000000000000000")
check("retained 0x160 independently recovers implicit DataID 0x0160", e2e_p05_recover_data_id(a) == 0x160)
r = build_0x160_request(a, request_signed7=-1, counter=0xB5)
check("combined counter+B12 mutation reproduces retained frame byte-exact", r.frame == b)
check("only header/counter/request changed", r.frame[3:12] == a[3:12] and r.frame[13:] == a[13:])

base = bytes.fromhex("5a1c03f8000000034de000000000000000000000000000000000000000000000")
expected_counter4 = bytes.fromhex("a98204f8000000034de000000000000000000000000000000000000000000000")
check("counter-only +1 mutation reproduces retained frame", build_0x160_request(base, 0, counter=4).frame == expected_counter4)
check("default replacement preserves intercepted counter", build_0x160_request(base, 0).new_counter == 3)
check("explicit next-frame mode advances modulo 256", build_0x160_request(base, 0, advance_counter=True).new_counter == 4)

print("== full retained pair validation ==")
rows: list[bytes] = []
for path in DRIVES:
    with gzip.open(path, "rt") as f:
        for line in f:
            _seg, _t, src, addr, hx = json.loads(line)
            if src == 1 and addr == 0x160:
                rows.append(bytes.fromhex(hx))

# Group frames whose visible payload is identical except B2 and B12.  Every
# pair in a group is therefore a direct oracle for the two recovered delta maps.
by_rest: dict[bytes, list[bytes]] = defaultdict(list)
for frame in rows:
    by_rest[frame[3:12] + frame[13:]].append(frame)

pairs = mismatches = request_change_pairs = 0
for group in by_rest.values():
    if len(group) < 2:
        continue
    anchor = group[0]
    for target in group[1:]:
        if anchor[2] == target[2] and anchor[12] == target[12]:
            continue
        pairs += 1
        request_change_pairs += anchor[12] != target[12]
        built = build_0x160_request(anchor, decode_signed7(target[12]), counter=target[2]).frame
        mismatches += built != target

check("retained oracle covers >20k direct B2/B12 pairs", pairs > 20_000, str(pairs))
check("retained oracle includes request-field changes", request_change_pairs > 0, str(request_change_pairs))
check("all retained B2/B12 pair reconstructions are byte-exact", mismatches == 0, str(mismatches))

print("== CLI is offline-only and deterministic ==")
proc = subprocess.run(
    [
        sys.executable,
        str(REPO / "tools/camry_frc_request_poc.py"),
        "--template-hex",
        a.hex(),
        "--request",
        "-1",
        "--counter",
        "0xB5",
        "--json",
    ],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
)
check("CLI succeeds", proc.returncode == 0, proc.stderr[-200:])
if proc.returncode == 0:
    obj = json.loads(proc.stdout)
    check("CLI emits retained witness", obj["frame_hex"] == b.hex())
    check("CLI explicitly has no transmit path", obj["transmits_can"] is False)

print("== fail-closed bounds ==")
for bad in (-65, 64):
    try:
        build_0x160_request(base, bad)
        ok = False
    except ValueError:
        ok = True
    check(f"request {bad} rejected", ok)

corrupt = bytearray(base)
corrupt[8] ^= 0x01
try:
    build_0x160_request(bytes(corrupt), 0)
    ok = False
except ValueError:
    ok = True
check("invalid Profile-5 template rejected", ok)

bit7_template = bytearray(base)
bit7_template[12] = 0x80
bit7_template = bytearray(e2e_p05_protect(bytes(bit7_template), 0x160))
check("exact Profile-5 recovery covers formerly-unrecovered B12 bit7", e2e_p05_check(bit7_template, 0x160))
check("PoC can repair from a valid bit7 template", e2e_p05_check(build_0x160_request(bytes(bit7_template), 0).frame, 0x160))

try:
    build_0x160_request(base, 0, counter=4, advance_counter=True)
    ok = False
except ValueError:
    ok = True
check("explicit counter and advance mode cannot conflict", ok)

print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
