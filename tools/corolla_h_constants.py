#!/usr/bin/env python3
"""Shared structural constants for exact Corolla-H evidence/build pairs.

Only target identity/path and byte-table coordinates live here. Semantic proof
logic remains in the individual extractors/builders.
"""
from __future__ import annotations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOFTWARE_ID = "8965H1202000"
CODEFLASH = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
RAW_DUMP = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"

# name, base, count, stride, pointer offsets
SIENNA_DEADLINE_TABLES = (
    ("variant_d_a", 0x28524, 1, 52, tuple(range(0, 52, 4))),
    ("simple", 0x28558, 28, 12, (0, 4, 8)),
    ("variant_d_b", 0x286D0, 1, 52, tuple(range(0, 52, 4))),
)
H_DEADLINE_TABLES = (
    ("variant_d_a", 0x280B4, 1, 52, tuple(range(0, 52, 4))),
    ("simple", 0x280E8, 28, 12, (0, 4, 8)),
    ("variant_d_b", 0x28260, 1, 52, tuple(range(0, 52, 4))),
)

# Sienna entry, semantic role, H entry, XCP selector.
XCP_ROLE_MAP = (
    (0x972FA, "xcp_command_fa_handler", 0x9232A, 0xFA),
    (0x97432, "xcp_command_f5_handler", 0x92462, 0xF5),
    (0x975EE, "xcp_command_eb_handler", 0x9261E, 0xEB),
    (0x97668, "xcp_command_ea_handler", 0x92698, 0xEA),
)
