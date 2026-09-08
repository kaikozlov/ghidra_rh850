#!/usr/bin/env python3
"""Verify exact-F33 RS-CANFD mode and bit timing (VAR-142)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "data/generated/camry-8965F3307000/decompilations.jsonl"


def check(name: str, cond: bool) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"[PASS] {name}")


def load_function(entry: str) -> dict:
    with CORPUS.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("record") == "function" and rec.get("entry_addr") == entry:
                return rec
    raise AssertionError(f"missing exact-F33 function {entry}")


mode = load_function("0x00003908")
gcfg = load_function("0x0000396c")
timing = load_function("0x00003978")
fdcfg = load_function("0x00003a8e")

check(
    "CAN-FD interface-mode selector is written",
    "DAT_ffd204fc = 1" in mode["decompiled_c"]
    and any(r["to_addr"] == "0xffd204fc" and r["ref_type"] == "WRITE" for r in mode["data_references"]),
)
check(
    "global configuration constant exact",
    "DAT_ffd20084 = 0xffff0000" in gcfg["decompiled_c"]
    and any(r["to_addr"] == "0xffd20084" and r["ref_type"] == "WRITE" for r in gcfg["data_references"]),
)
check(
    "per-channel nominal/data timing constants exact",
    "0xf3e7800" in timing["decompiled_c"]
    and "0x55c0000" in timing["decompiled_c"]
    and {r["to_addr"] for r in timing["data_references"]} == {"0xffd20000", "0xffd20500"},
)
check(
    "per-channel CAN-FD configuration constant exact",
    "0x20000000" in fdcfg["decompiled_c"]
    and any(r["to_addr"] == "0xffd20504" and r["ref_type"] in {"DATA", "WRITE"} for r in fdcfg["data_references"]),
)

# RH850/P1M-E User's Manual R01UH0585EJ0120 Rev.1.20, RS-CANFD sections
# 17.4.3/17.4.4/17.11.1: DCS=0 selects clkc (40 MHz); each encoded TSEG/SJW
# field is one less than its Tq count; NBRP/DBRP divide fCAN by field+1.
GCFG = 0xFFFF0000
NCFG = 0x0F3E7800
DCFG = 0x055C0000
FDCFG = 0x20000000
FCAN_HZ = 40_000_000

check("DCS selects 40-MHz clkc", ((GCFG >> 4) & 1) == 0)

nbrp = (NCFG & 0x3FF) + 1
ntseg1 = ((NCFG >> 16) & 0x7F) + 1
ntseg2 = ((NCFG >> 24) & 0x1F) + 1
nsjw = ((NCFG >> 11) & 0x1F) + 1
nominal_tq = 1 + ntseg1 + ntseg2
nominal_bps = FCAN_HZ // (nbrp * nominal_tq)
nominal_sp = (1 + ntseg1) / nominal_tq
check(
    "nominal timing is 500 kbit/s at 80% sample point",
    (nbrp, ntseg1, ntseg2, nsjw, nominal_tq, nominal_bps) == (1, 63, 16, 16, 80, 500_000)
    and nominal_sp == 0.8,
)

dbrp = (DCFG & 0xFF) + 1
dtseg1 = ((DCFG >> 16) & 0xF) + 1
dtseg2 = ((DCFG >> 20) & 0x7) + 1
dsjw = ((DCFG >> 24) & 0x7) + 1
data_tq = 1 + dtseg1 + dtseg2
data_bps = FCAN_HZ // (dbrp * data_tq)
data_sp = (1 + dtseg1) / data_tq
check(
    "data timing is 2 Mbit/s at 70% sample point",
    (dbrp, dtseg1, dtseg2, dsjw, data_tq, data_bps) == (1, 13, 6, 6, 20, 2_000_000)
    and data_sp == 0.7,
)

check(
    "FD-only mode is disabled and receive edge filter is enabled",
    ((FDCFG >> 28) & 1) == 0 and ((FDCFG >> 29) & 1) == 1,
)
