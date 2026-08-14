#!/usr/bin/env python3
"""Verify the three dispatch-proven COM deadline-monitor callback tables."""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def u32(addr: int) -> int:
    return struct.unpack_from("<I", CF, addr)[0]


def sha(start: int, size: int) -> str:
    return hashlib.sha256(CF[start : start + size]).hexdigest()


def decode_long_branch(addr: int) -> tuple[str, int] | None:
    w0, w1 = struct.unpack_from("<HH", CF, addr)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1):
        return None
    reg2 = (w0 >> 11) & 0x1F
    high = w0 & 0x3F
    if high & 0x20:
        high -= 0x40
    return ("jarl" if reg2 else "jr"), addr + (high << 16) + w1


TABLES = (
    (
        "variant-D A",
        0x28524,
        1,
        52,
        tuple(range(0, 52, 4)),
        "4b98b9c52b50bad19b6df6c6c5add0aff8d5cf796282253a9d04eb6cb7ae70e0",
    ),
    (
        "simple",
        0x28558,
        28,
        12,
        (0, 4, 8),
        "ae2734c725b63086192f985acec10778ef57c87c050add9a0acf7a58b5ae0833",
    ),
    (
        "variant-D B",
        0x286D0,
        1,
        52,
        tuple(range(0, 52, 4)),
        "3806052261dd30dea4ebc010e663fcb39322901565ef354eecb4bc96d999ed7b",
    ),
)

print("== raw callback tables ==")
all_targets: list[int] = []
per_table: dict[str, list[int]] = {}
for name, base, count, stride, offsets, expected_sha in TABLES:
    check(f"{name} table hash", sha(base, count * stride) == expected_sha)
    values: list[int] = []
    for index in range(count):
        for offset in offsets:
            target = u32(base + index * stride + offset)
            if target:
                values.append(target)
                all_targets.append(target)
    per_table[name] = values
    check(f"{name} nonzero callbacks are 2-byte aligned", all((v & 1) == 0 for v in values))
    check(f"{name} callbacks all lie in CodeFlash", all(0 < v < len(CF) for v in values))

check("variant-D A has 4 nonzero slots / 3 unique callbacks", len(per_table["variant-D A"]) == 4 and len(set(per_table["variant-D A"])) == 3)
check("simple table has 83 nonzero slots / 82 unique callbacks", len(per_table["simple"]) == 83 and len(set(per_table["simple"])) == 82)
check("variant-D B has 4 nonzero slots / 3 unique callbacks", len(per_table["variant-D B"]) == 4 and len(set(per_table["variant-D B"])) == 3)
check("three tables contain 91 nonzero callback slots", len(all_targets) == 91)
check("three tables contribute exactly 88 unique callback entries", len(set(all_targets)) == 88)
check("variant-D A exact nonzero set", set(per_table["variant-D A"]) == {0x3DB78, 0x3DBC0, 0x3DBD0})
check("variant-D B exact nonzero set", set(per_table["variant-D B"]) == {0x4191C, 0x419F2, 0x41A02})
check("simple table starts at callback family 0x3DDE2", min(per_table["simple"]) == 0x3DDE2)
check("simple table ends at callback family 0x415D8", max(per_table["simple"]) == 0x415D8)
check("simple final row duplicates start callback and has null third slot", [u32(0x28558 + 27 * 12 + o) for o in (0, 4, 8)] == [0x415D8, 0x415D8, 0])

print("\n== dispatcher and setup provenance ==")
check("simple monitor dispatcher body is pinned", sha(0x6962A, 138) == "132514c473f707f4665912b443e08178f7b27e32bc58f74759956d6a66a0f579")
check("variant-D monitor dispatcher body is pinned", sha(0x6A28A, 1208) == "1854f75394c483afffd8a2355be27f8a406398065249add8d951d9a23b69b2e8")
check("variant-D A setup body is pinned", sha(0x3DB30, 72) == "ae414801f0805014edd6413eafceab63203e5fcbc3f991984e283ad85e8fc731")
check("simple-table setup body is pinned", sha(0x3DC88, 346) == "685e94c9e4ed01c480d179f74fcdb7d34184239942d30a2a0d217ad365ec23a7")
check("variant-D B setup body is pinned", sha(0x417EE, 302) == "2646214f0412b1a1b8d636506a4acc16f61895e35f94618b02d96fa245205495")

# Exact MOV-immediate sites bind each setup body to its callback table.
check("variant-D A setup loads table 0x28524", CF[0x3DB54:0x3DB5A] == bytes.fromhex("280624850200"))
check("simple setup loads table 0x28558", CF[0x3DCB4:0x3DCBA] == bytes.fromhex("3b0658850200"))
check("variant-D B setup loads table 0x286D0", CF[0x41856:0x4185C] == bytes.fromhex("3b06d0860200"))
check("variant-D A setup directly calls monitor D", decode_long_branch(0x3DB5A) == ("jarl", 0x6A28A))
check("simple setup call 1 targets simple dispatcher", decode_long_branch(0x3DD06) == ("jarl", 0x6962A))
check("simple setup call 2 targets simple dispatcher", decode_long_branch(0x3DD22) == ("jarl", 0x6962A))
check("simple setup call 3 targets simple dispatcher", decode_long_branch(0x3DD3E) == ("jarl", 0x6962A))
check("variant-D B setup call 1 targets monitor D", decode_long_branch(0x41874) == ("jarl", 0x6A28A))
check("variant-D B setup call 2 targets monitor D", decode_long_branch(0x41898) == ("jarl", 0x6A28A))
check("variant-D B setup call 3 targets monitor D", decode_long_branch(0x418BC) == ("jarl", 0x6A28A))

# The three pointer shapes match the dispatchers' recovered ABI: the simple
# monitor consumes slots 0/1/2; variant D consumes a 13-pointer row 0..12.
check("simple table stride is exactly three pointers", TABLES[1][3] == 3 * 4 and TABLES[1][4] == (0, 4, 8))
check("variant-D rows are exactly thirteen pointers", TABLES[0][3] == 13 * 4 and TABLES[0][4] == tuple(range(0, 52, 4)))
check("both variant-D rows share the exact 13-pointer shape", TABLES[0][4] == TABLES[2][4])


print("\n== promoted graph boundary ==")
candidates = ROOT / "data" / "outside_function_candidates.csv"
if candidates.is_file():
    import csv
    with candidates.open(newline="") as handle:
        outside = {int(row["target_addr"], 0) for row in csv.DictReader(handle)}
    check("none of the 88 dispatch-proven targets remain outside functions", not (set(all_targets) & outside), repr(sorted(hex(x) for x in set(all_targets) & outside)[:10]))
else:
    check("outside-function candidate artifact exists", False, str(candidates))

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
