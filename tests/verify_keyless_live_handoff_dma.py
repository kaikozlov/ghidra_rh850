#!/usr/bin/env python3
"""Verify the live app->boot handoff does not create a tester-programmable DMA shortcut.

The normal programming transition is a live call into 0x9F00, not a hardware
reset.  Peripheral state therefore has to be treated as retained.  This suite
pins the relevant Sienna firmware facts: the fallback hard reset is after the
non-returning live entry, application DMAC channel descriptors come only from
fixed CodeFlash tables, and no reachable descriptor endpoint touches either
boot credential root or the tester-writable XCP shadow window.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()

passed = failed = 0

def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"[PASS] {name}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def load_functions() -> dict[int, dict]:
    out: dict[int, dict] = {}
    with (ROOT / "data/generated/decompilations.jsonl").open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") == "function":
                out[int(row["entry_addr"], 16)] = row
    return out

F = load_functions()
def code(addr: int) -> str:
    return F[addr]["decompiled_c"]

print("== KEYLESS-013: live handoff ordering ==")
handoff = code(0x64EC8)
check("programming transition calls live boot entry before hard-reset fallback",
      "FUN_00009f00" in handoff and "system_hard_reset" in handoff
      and handoff.index("FUN_00009f00") < handoff.index("system_hard_reset"))
check("0x9F00 enters boot initializer and then does not return",
      "FUN_0000148e();" in code(0x9F00) and "while( true )" in code(0x9F00))
check("boot failure init touches DMAC global control through FUN_0000121a",
      "FUN_0000121a();" in code(0x1338))
check("boot DMAC global-control helper writes fixed value 1",
      "Ramffff8000 = 1;" in code(0x121A))

print("\n== application DMAC descriptor provenance ==")
programmer = code(0x5F796)
for token in ("*(undefined4 *)(param_1 + 8)", "*(undefined4 *)(param_1 + 0xc)",
              "*(undefined4 *)(param_1 + 0x18)", "*(undefined4 *)(param_1 + 0x1c)"):
    check(f"DMAC programmer sources endpoint field {token}", token in programmer)

# Every recovered caller supplies a pointer into an immutable CodeFlash table.
caller_sources = {
    0x5EFF8: "&DAT_00031234 + iVar2",
    0x5FAE0: "&DAT_000313e8 + iVar2",
    0x5FB12: "&DAT_00031438 + iVar2",
    0x5FDC4: "&DAT_00031638",
    0x60A8C: "&DAT_000317a8 + iVar3",
}
for addr, token in caller_sources.items():
    check(f"DMAC programmer caller 0x{addr:X} uses fixed CodeFlash descriptor family",
          token in code(addr))
check("primary DMAC caller bounds selector to two banks x five records",
      "uVar2 < 2" in code(0x5F034) and all(f"FUN_0005eff8(uVar2,{i})" in code(0x5F034) for i in range(5)))

# Reachable fixed records: primary 2x5, two 2-row families, three 2-row
# secondary families, and the final 2-row family.  +8/+C and +18/+1C are the
# two endpoint pairs consumed by 0x5F796.
tables = [
    (0x31234, 10),
    (0x313E8, 2),
    (0x31438, 2),
    (0x31638, 2),
    (0x31688, 2),
    (0x316D8, 2),
    (0x317A8, 2),
]
endpoints: list[int] = []
for base, count in tables:
    for i in range(count):
        off = base + i * 0x28
        endpoints.extend(struct.unpack_from("<II", CF, off + 8))
        endpoints.extend(struct.unpack_from("<II", CF, off + 0x18))

# Some primary-table records encode disabled channel 0xFF; their fixed endpoint
# values are still safe and are included deliberately.
BOOT_ROOTS = (0xBFD8, 0xBFE8)
XCP_LO, XCP_HI = 0xFEBF7C00, 0xFEBFFBFF
check("no fixed application DMAC endpoint equals either boot credential root",
      all(v not in BOOT_ROOTS for v in endpoints))
check("no fixed application DMAC endpoint enters tester-writable XCP shadow RAM",
      all(not (XCP_LO <= v <= XCP_HI) for v in endpoints))
check("fixed DMAC descriptor tables themselves are CodeFlash-resident",
      all(0 <= base < 0x40000 and base + count * 0x28 <= len(CF) for base, count in tables))

print("\n== no direct application SFR write service ==")
# Application DCM service table has no SID 0x3D WriteMemoryByAddress.  The only
# generic tester write primitive recovered elsewhere is XCP DOWNLOAD/MODIFY_BITS,
# which is independently range-pinned to FEBF7C00..FEBFFBFF.
service_sids = [CF[0x25E28 + i * 0x18 + 0x10] for i in range(17)]
check("application DCM has no SID 0x3D WriteMemoryByAddress", 0x3D not in service_sids)
check("application service census remains the pinned 17-SID set",
      service_sids == [0x10,0x11,0x14,0x19,0x22,0x23,0x27,0x28,0x2E,0x31,0x34,0x36,0x37,0x3E,0x85,0xAB,0xBA])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
