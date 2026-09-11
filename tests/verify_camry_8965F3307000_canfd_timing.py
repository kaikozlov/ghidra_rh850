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


# Bootloader and application carry separate RS-CANFD initializers.  The old
# 0x39xx fixed writers are boot-only (0x1398 -> 0x1338 -> 0x3B3C).  The live
# application initializes RSCFD through 0x7A132 -> 0x79DFA -> 0x83F3E ->
# 0x84652 -> 0x84570 using the configuration table at 0x22E80/0x233B8.
boot_init = load_function("0x00001338")
boot_mode = load_function("0x00003908")
boot_gcfg = load_function("0x0000396c")
app_root = load_function("0x0007a132")
app_comm_init = load_function("0x00079dfa")
app_rscfd_init = load_function("0x00083f3e")
app_driver_init = load_function("0x00084652")
app_apply = load_function("0x00084570")

IMAGE = REPO / "firmware/camry-8965F3307000/CodeFlash.bin"
image = IMAGE.read_bytes()

check(
    "boot CAN-FD initializer is separate and writes legacy GCFG",
    "FUN_00003b3c()" in boot_init["decompiled_c"]
    and "DAT_ffd204fc = 1" in boot_mode["decompiled_c"]
    and "DAT_ffd20084 = 0xffff0000" in boot_gcfg["decompiled_c"],
)
check(
    "application RS-CANFD init chain exact",
    "FUN_00079dfa()" in app_root["decompiled_c"]
    and "FUN_00083f3e(0)" in app_comm_init["decompiled_c"]
    and "FUN_00084652()" in app_rscfd_init["decompiled_c"]
    and "FUN_00084570()" in app_driver_init["decompiled_c"],
)
check(
    "application global configuration source reaches GCFG",
    "PTR_DAT_0002303c = DAT_00022e80" in app_apply["decompiled_c"]
    and any(r["to_addr"] == "0x00022e80" and r["ref_type"] == "READ" for r in app_apply["data_references"])
    and any(r["to_addr"] == "0xffd20084" and r["ref_type"] == "WRITE" for r in app_apply["data_references"]),
)

# Exact live-application configuration table.  Channel 1 is the external EPS
# CAN-FD channel used by the target; its timing matches the boot constants while
# the application FDCFG carries additional configured bits.
GCFG = int.from_bytes(image[0x22E80:0x22E84], "little")
NCFG = int.from_bytes(image[0x233F8:0x233FC], "little")
DCFG = int.from_bytes(image[0x23410:0x23414], "little")
FDCFG = int.from_bytes(image[0x23414:0x23418], "little")
check("application GCFG exact", GCFG == 0xFFFF0020)
check("application channel-1 NCFG exact", NCFG == 0x0F3E7800)
check("application channel-1 DCFG exact", DCFG == 0x055C0000)
check("application channel-1 FDCFG exact", FDCFG == 0x280D0200)

# RH850/P1M-E User's Manual R01UH0585EJ0120 Rev.1.20, RS-CANFD sections
# 17.4.3/17.4.4/17.11.1: DCS=0 selects clkc (40 MHz); each encoded TSEG/SJW
# field is one less than its Tq count; NBRP/DBRP divide fCAN by field+1.
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
