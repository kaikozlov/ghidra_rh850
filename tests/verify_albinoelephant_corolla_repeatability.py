#!/usr/bin/env python3
"""Verify repeatability limits of the retained 2023-US-Corolla range dumps.

The range-dumper reports every file below as complete coverage.  This gate does
not assume that read-to-read differences are real NVM writes: it measures the
captured bytes, and separately asks which already-recovered NvM conclusions
survive every FF20 host-range capture.
"""
from __future__ import annotations

import itertools
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.analyze_toyota_dataflash import analyze  # noqa: E402

RAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023"
DF = sorted(RAW.glob("dump_dataflash_ff200000_ff210000_*.bin"))
P1ME = __import__("json").loads((REPO / "data/p1me_product_memory.json").read_text(encoding="utf-8"))
EXT = sorted(RAW.glob("dump_extended_codeflash_01000000_0100c000_*.bin"))
GRAM = sorted(RAW.glob("dump_global_ram_feef8000_fef08000_*.bin"))
LRAM = sorted(RAW.glob("dump_local_ram_pe1_febe0000_fec00000_*.bin"))

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def pairwise_diffs(paths: list[Path], limit: int | None = None) -> list[int]:
    blobs = [p.read_bytes() for p in paths]
    if limit is not None:
        blobs = [blob[:limit] for blob in blobs]
    return [sum(a != b for a, b in zip(left, right)) for left, right in itertools.combinations(blobs, 2)]


print("== retained multi-run corpus ==")
check("five complete 64-KiB FF20 host-range captures retained", len(DF) == 5 and all(p.stat().st_size == 0x10000 for p in DF))
check("three complete 48-KiB extended-CodeFlash captures retained", len(EXT) == 3 and all(p.stat().st_size == 0xC000 for p in EXT))
check("three complete 64-KiB global-RAM captures retained", len(GRAM) == 3 and all(p.stat().st_size == 0x10000 for p in GRAM))
check("three complete 128-KiB PE1-local-RAM captures retained", len(LRAM) == 3 and all(p.stat().st_size == 0x20000 for p in LRAM))
all_memory = sorted(RAW.glob("*.bin"))
legacy_df = REPO / "community/albinoelephant/dump_ff200000_ff208000.bin"
window_count = sum(path.stat().st_size - 15 for path in [*all_memory, legacy_df])
check("range corpus has 15 files / 3,162,112 bytes", len(all_memory) == 15 and sum(p.stat().st_size for p in all_memory) == 3_162_112)
check("16 retained memory files contain 3,194,640 sliding 16-byte windows", window_count == 3_194_640, str(window_count))
check("two-oracle full-corpus scan geometry is 6,389,280 window/oracle invocations", window_count * 2 == 6_389_280)
check("R7F701383 physical DataFlash is only the first 32 KiB", P1ME["products"]["R7F701383"]["dataflash_bytes"] == 0x8000 and P1ME["address_space"]["dataflash_1mb"]["end_exclusive"] == 0xFF208000)

print("\n== read-to-read divergence ==")
df64 = pairwise_diffs(DF)
df32 = pairwise_diffs(DF, 0x8000)
extd = pairwise_diffs(EXT)
gram = pairwise_diffs(GRAM)
lram = pairwise_diffs(LRAM)
check("full 64-KiB FF20 host-range spread is 26.2650%-27.7328%", min(df64) == 17213 and max(df64) == 18175, f"{min(df64)}..{max(df64)} / 65536")
check("physical 32-KiB DataFlash spread is 23.5077%-25.6470%", min(df32) == 7703 and max(df32) == 8404, f"{min(df32)}..{max(df32)} / 32768")
check("extended CodeFlash is byte-identical across all three reads", extd == [0, 0, 0], str(extd))
check("global RAM varies only about 1.2% pairwise", min(gram) == 782 and max(gram) == 791, f"{min(gram)}..{max(gram)} / 65536")
check("PE1 local RAM varies about 2.8%-3.2% pairwise", min(lram) == 3677 and max(lram) == 4216, f"{min(lram)}..{max(lram)} / 131072")

blobs = [p.read_bytes()[:0x8000] for p in DF]
unique_counts = [len({blob[i] for blob in blobs}) for i in range(0x8000)]
check("only 17,325/32,768 DataFlash bytes are identical in all five reads", unique_counts.count(1) == 17325, str(unique_counts.count(1)))
check("2,506 first-32-KiB byte positions show multiple nonzero identities", sum(len({blob[i] for blob in blobs if blob[i] != 0}) > 1 for i in range(0x8000)) == 2506)

print("\n== conclusions that survive every FF20 host-range read ==")
valid_counts = []
for path in DF:
    result = analyze(path)
    objects = {row["object"]: row for row in result["triplicate_objects"]}
    valid_counts.append({idx: objects[idx]["valid_copy_count"] for idx in objects})
check("objects 0, 2 and 5 have all three valid copies in every read", all(all(row[idx] == 3 for idx in (0, 2, 5)) for row in valid_counts))
check("object 15 has zero valid copy in every retained read", all(row[15] == 0 for row in valid_counts))
check("same object-validity disposition repeats across all five reads", all(row == valid_counts[0] for row in valid_counts[1:]))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
