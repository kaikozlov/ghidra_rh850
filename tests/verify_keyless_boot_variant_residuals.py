#!/usr/bin/env python3
"""Pin the 18 non-trivially-relocated boot functions in Corolla H/F.

This is a raw-byte regression for KEYLESS-011.  The broad Sienna->Corolla boot
transfer is covered elsewhere; this suite closes the residual functions that
were not simple exact bodies at the dominant -0x1C relocation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = (ROOT / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
H = (ROOT / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin").read_bytes()
F = (ROOT / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin").read_bytes()

passed = failed = 0

def check(name: str, ok: bool) -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}")

# H and F are byte-identical through the complete boot residual domain.  Their
# first divergence begins at 0xA004 in calibration/application-adjacent data.
check("Corolla H/F boot bytes are identical through 0xA003", H[:0xA004] == F[:0xA004])

# Residuals that are actually exact bodies at a non-dominant placement.
EXACT = [
    ("warm reset", 0x1B0, 0x1B0, 66),
    ("EIC init", 0x17C8, 0x17AA, 1014),
    ("TAUJ0 init", 0x1C20, 0x1C02, 64),
    ("TAUJ1 init", 0x1C60, 0x1C42, 64),
    ("TAUJ sequencer", 0x1CA0, 0x1C82, 72),
]
for name, sa, ha, size in EXACT:
    check(f"{name} body is byte-exact at residual placement", S[sa:sa+size] == H[ha:ha+size])

# Exception thunk is unchanged except for the re-linked fixed target.
check("default exception thunk target relinks 0x1E1E -> 0x1E02",
      S[0x30:0x3C] == bytes.fromhex("1f00e0061e1e000000000000") and
      H[0x30:0x3C] == bytes.fromhex("1f00e006021e000000000000"))
check("old/new default-exception targets carry the same 12-byte stub",
      S[0x1E1E:0x1E2A] == H[0x1E02:0x1E0E])

# Cold-start differences are CPU-configuration/linkage changes: TP moves by
# 0x20, PSW/EIPSW/FEPSW lose CU0 (0x18020 -> 0x8020), FPIPR is zeroed, and the
# Sienna FPU initialization sequence is absent in H/F.
check("cold-start TP immediate moves 0x869C -> 0x867C",
      S[0x1F8:0x1FE] == bytes.fromhex("25069c860000") and
      H[0x1F8:0x1FE] == bytes.fromhex("25067c860000"))
for off in (0x1FE, 0x210, 0x222):
    check(f"cold-start PSW-family immediate at 0x{off:X} clears CU0",
          S[off:off+6] == bytes.fromhex("2a0620800100") and
          H[off:off+6] == bytes.fromhex("2a0620800000"))
check("FPIPR changes from r10=0x10 to r0",
      S[0x48E:0x498] == bytes.fromhex("20561000ea3f20081c00") and
      H[0x48E:0x494] == bytes.fromhex("e03f20081c00"))
check("H cold-start body is exactly 28 bytes shorter before dominant relocation",
      S[0x684:0x742] == H[0x668:0x726])

# The CSIH generation change is an MMIO-instance remap plus one shorter address
# materialization.  It creates the temporary -0x1E island but no new parser.
check("CSIH TX base remaps by 0x2000",
      S[0x1628:0x162C] == bytes.fromhex("490840b0") and
      H[0x160C:0x1610] == bytes.fromhex("490800b0"))
check("CSIH init saves two bytes with movhi FFD8", H[0x16E6:0x16EA] == bytes.fromhex("40f6d8ff"))
check("-0x1E island closes with one zero pad before dominant -0x1C resumes",
      H[0x1CD6:0x1CD8] == b"\x00\x00" and S[0x1CF2:0x1CF4] != b"\x00\x00")

# Remaining residuals are direct re-links or a moved source table.  Pin the
# exact target-side entry bytes and the table identity, not narrative names.
for name, sa, ha in (
    ("runtime init", 0x1338, 0x131C),
    ("CSIH TX", 0x1626, 0x160A),
    ("CSIH RX", 0x169C, 0x1680),
    ("CSIH init", 0x16F2, 0x16D6),
    ("EIC mask helper", 0x1BBE, 0x1BA0),
    ("timer trampoline", 0x1CE8, 0x1CCA),
    ("TAUJ ISR", 0x1E44, 0x1E28),
    ("RAM table copier", 0x35E4, 0x35C8),
    ("EIC helper A", 0x3A9E, 0x3A82),
    ("EIC helper B", 0x3ABA, 0x3A9E),
):
    check(f"{name} retains expected instruction-family prologue",
          S[sa:sa+4] == H[ha:ha+4])
check("RAM table copier source table relocates 0x8370 -> 0x8350 with identical 0x32C bytes",
      S[0x8370:0x869C] == H[0x8350:0x867C])

# Live handoff stays at a pinned absolute VA after the FF gap.  Only PSW CU0,
# TP, and the direct callee displacement differ.
check("0x9F00 handoff stays at the same VA and same fixed-state prefix",
      S[0x9F00:0x9F22] == H[0x9F00:0x9F22])
check("0x9F00 handoff PSW clears CU0 on H/F",
      S[0x9F22:0x9F28] == bytes.fromhex("2a0620800100") and
      H[0x9F22:0x9F28] == bytes.fromhex("2a0620800000"))
check("0x9F00 handoff TP moves 0x869C -> 0x867C",
      S[0x9F50:0x9F56] == bytes.fromhex("25069c860000") and
      H[0x9F50:0x9F56] == bytes.fromhex("25067c860000"))
check("0x9F00 direct call relinks 0x148E -> 0x1472",
      S[0x9F5E:0x9F62] == bytes.fromhex("bfff3075") and
      H[0x9F5E:0x9F62] == bytes.fromhex("bfff1475"))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
