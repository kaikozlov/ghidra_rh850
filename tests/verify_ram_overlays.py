#!/usr/bin/env python3
"""Validate LocalRAM overlay inventory against mapped RAM and known landmarks."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "ram_overlay_map.csv"
CHECKPOINT_CSV = ROOT / "data" / "checkpoint_payload_map.csv"
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

LOCAL_RAM = (0xFEBE0000, 0x20000)  # start, size
APP_GP = 0xFEBEB800
BOOT_GP = 0xFEBF9800

# Landmark overlays that must remain typed for day-to-day analysis.
REQUIRED = {
    0xFEBF0FD0: ("payload_flash_callback", 4, "PayloadFlashCallback"),
    0xFEBF0FE0: ("payload_crc_trailer", 16, "PayloadCrcTrailer"),
    0xFEBF0FF0: ("payload_cmac_tag", 16, "PayloadCmacTag"),
    0xFEBF02E8: ("secoc_nvm_object15_ram_mirror", 32, "SecocNvmObject15"),
    0xFEBF0B08: ("secoc_nvm_triplicate_workbuf_root", 384, "SecocNvmWorkbufRoot"),
    0xFEBF2D08: ("payload_did_0201_key_material", 16, "PayloadDid0201KeyMaterial"),
    0xFEBF2CF8: ("payload_did_0202_iv", 16, "PayloadDid0202Iv"),
    0xFEBEB1A4: ("application_system_transition_phase_live", 1, "uint8"),
    0xFEBEE81F: ("application_system_transition_phase_snapshot", 1, "uint8"),
    0xFEBEE892: ("application_vehicle_speed_raw", 2, "uint16"),
    0xFEBE6692: ("application_supply_value_raw", 2, "uint16"),
    0xFEBE8152: ("application_alternate_handoff_flag", 1, "uint8"),
    0xFEBE8166: ("application_programming_reset_requested", 1, "uint8"),
    0xFEBF3B14: ("application_programming_handoff_value", 4, "uint32"),
    0xFEBF3B18: ("application_programming_readiness_latch", 1, "uint8"),
    0xFEBF3B19: ("application_programming_reset_latch", 1, "uint8"),
}

# Documented GP displacements that must stay honest and signed-16-bit encodable.
REQUIRED_GP = {
    "secoc_nvm_triplicate_workbuf_root": (APP_GP, 0x5308),
    "application_system_transition_phase_live": (APP_GP, -0x65C),
    "application_system_transition_phase_snapshot": (APP_GP, 0x301F),
    "application_vehicle_speed_raw": (APP_GP, 0x3092),
    "application_supply_value_raw": (APP_GP, -0x516E),
    "application_alternate_handoff_flag": (APP_GP, -0x36AE),
    "application_programming_reset_requested": (APP_GP, -0x369A),
}

# Absolute (non-GP) handoff roots proved by mov immediates.
ABSOLUTE_HANDOFF = {
    "application_programming_handoff_value",
    "application_programming_readiness_latch",
    "application_programming_reset_latch",
}

# Instruction-proved application-GP roots (mnemonic site -> signed disp).
PROVED_APP_GP_ROOTS = {
    0xFEBEE81F: (0x4C960, 0x301F, "a40f1f30"),   # ld.bu 0x301F[gp]
    0xFEBEE892: (0x4C944, 0x3092, "e40f9330"),   # ld.hu 0x3092[gp]
    0xFEBE6692: (0x4C964, -0x516E, "e49f93ae"),  # ld.hu -0x516E[gp]
    0xFEBE8152: (0x4C968, -0x36AE, "845753c9"),  # ld.bu -0x36AE[gp]
    0xFEBE8166: (0x4C986, -0x369A, "440766c9"),  # st.b r0,-0x369A[gp]
}

passed = 0
failed = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        suffix = f" ({detail})" if detail else ""
        print(f"  FAIL {name}{suffix}")


def parse_signed(text: str) -> int:
    text = text.strip()
    if not text:
        raise ValueError("empty")
    if text.startswith("-"):
        return -int(text[1:], 0)
    return int(text, 0)


def fits_s16(value: int) -> bool:
    return -0x8000 <= value <= 0x7FFF


def main() -> int:
    print("== P1M-E LocalRAM overlay CSV ==")
    check("CSV exists", CSV_PATH.is_file(), str(CSV_PATH))
    if not CSV_PATH.is_file():
        print(f"\nSummary: {passed} passed, {failed} failed")
        return 1

    rows: list[dict[str, str]] = []
    with CSV_PATH.open(newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        expected = ["address", "name", "size", "type", "gp_base", "gp_offset", "comment"]
        check("header matches schema", header == expected, repr(header))
        for line_no, parts in enumerate(reader, start=2):
            if not parts or parts[0].lstrip().startswith("#"):
                continue
            if len(parts) != 7:
                check(f"line {line_no} has seven columns", False, repr(parts))
                continue
            rows.append({
                "address": parts[0].strip(),
                "name": parts[1].strip(),
                "size": parts[2].strip(),
                "type": parts[3].strip(),
                "gp_base": parts[4].strip(),
                "gp_offset": parts[5].strip(),
                "comment": parts[6].strip(),
            })

    check("CSV has at least 40 overlays", len(rows) >= 40, str(len(rows)))

    addresses: set[int] = set()
    names: set[str] = set()
    by_addr: dict[int, tuple[str, int, str]] = {}
    ranges: list[tuple[int, int, str]] = []

    for row in rows:
        addr = int(row["address"], 0)
        size = int(row["size"], 0)
        name = row["name"]
        typ = row["type"]
        check(f"{name} size > 0", size > 0, str(size))
        check(f"{name} address unique", addr not in addresses, hex(addr))
        check(f"{name} name unique", name not in names, name)
        end = addr + size - 1
        lo, win = LOCAL_RAM
        check(f"{name} sits in LocalRAM",
              lo <= addr and end < lo + win,
              f"{addr:#x}+{size}")
        if row["gp_base"] and row["gp_offset"]:
            base = int(row["gp_base"], 0)
            off = parse_signed(row["gp_offset"])
            check(f"{name} gp_base+offset == address",
                  (base + off) & 0xFFFFFFFF == addr,
                  f"{base:#x}+{off:#x} != {addr:#x}")
            check(f"{name} gp_base is boot or app GP",
                  base in {APP_GP, BOOT_GP},
                  hex(base))
            # Handoff/phase roots are proved as ld.*/st.* disp16[gp]; enforce s16
            # there. Other overlays may use movhi/absolute forms with wider math.
            if name in REQUIRED_GP:
                check(f"{name} GP offset fits signed int16",
                      fits_s16(off),
                      f"{off:#x}")
        elif name in ABSOLUTE_HANDOFF:
            check(f"{name} is absolute (empty GP fields)",
                  not row["gp_base"] and not row["gp_offset"])
        addresses.add(addr)
        names.add(name)
        by_addr[addr] = (name, size, typ)
        ranges.append((addr, addr + size, name))

    ranges.sort()
    for (a1, e1, n1), (a2, e2, n2) in zip(ranges, ranges[1:]):
        check(f"{n1} does not overlap {n2}", a2 >= e1,
              f"[{a1:#x},{e1:#x}) vs [{a2:#x},{e2:#x})")

    for addr, (name, size, typ) in REQUIRED.items():
        actual = by_addr.get(addr)
        check(f"required {name} at {addr:#x}",
              actual == (name, size, typ),
              repr(actual))

    by_name = {r["name"]: r for r in rows}
    for name, (base, off) in REQUIRED_GP.items():
        row = by_name.get(name)
        check(f"required GP binding for {name}",
              row is not None
              and int(row["gp_base"], 0) == base
              and parse_signed(row["gp_offset"]) == off
              and fits_s16(off),
              repr(row))

    print("\n== proved application-GP handoff roots ==")
    for addr, (site, disp, insn) in PROVED_APP_GP_ROOTS.items():
        check(f"{addr:#x} instruction bytes at {site:#x}",
              CF[site:site + len(bytes.fromhex(insn))] == bytes.fromhex(insn),
              CF[site:site + 4].hex())
        check(f"{addr:#x} == APP_GP + {disp:#x}",
              (APP_GP + disp) & 0xFFFFFFFF == addr)
        check(f"{addr:#x} displacement fits signed int16", fits_s16(disp))

    # Absolute FEBF3B14/18 proved by 6-byte mov immediates.
    check("absolute mov FEBF3B18 at readiness adapter",
          CF[0x8A092:0x8A098] == bytes.fromhex("3d06183bbffe"))
    check("absolute mov FEBF3B14 at async worker",
          CF[0x8A248:0x8A24E] == bytes.fromhex("3d06143bbffe"))
    check("reset latch is FEBF3B14+5 via ld.bu/st.b 5[r29]",
          CF[0x8A24E:0x8A252] == bytes.fromhex("bde70500") and
          CF[0x8A276:0x8A27A] == bytes.fromhex("5de70500"))
    # Reject the old boot-GP/unsigned mislabels as overlay addresses.
    for bad in (0xFEBFC81F, 0xFEBFC892, 0xFEBF4692, 0xFEBF6152, 0xFEBF6166):
        check(f"old mislabel {bad:#x} is absent from overlays",
              bad not in by_addr)

    # Enabled checkpoint mirrors from the evidence CSV must appear.
    check("checkpoint CSV exists", CHECKPOINT_CSV.is_file(), str(CHECKPOINT_CSV))
    if CHECKPOINT_CSV.is_file():
        expected_checkpoints: dict[int, tuple[str, int]] = {}
        with CHECKPOINT_CSV.open(newline="") as fh:
            for crow in csv.DictReader(fh):
                if crow["enabled"] != "yes":
                    continue
                addr = int(crow["ram_mirror"], 0)
                length = int(crow["data_length"])
                ename = crow["evidence_name"]
                expected_checkpoints[addr] = (f"checkpoint_{ename}", length)
        check("at least 20 enabled checkpoint overlays expected",
              len(expected_checkpoints) >= 20,
              str(len(expected_checkpoints)))
        for addr, (name, size) in expected_checkpoints.items():
            actual = by_addr.get(addr)
            check(f"checkpoint {name} at {addr:#x}",
                  actual is not None and actual[0] == name and actual[1] == size,
                  repr(actual))

    # Workbuf root must cover the object-15 restore group addresses.
    work = by_addr.get(0xFEBF0B08)
    if work:
        start, size = 0xFEBF0B08, work[1]
        for member in (0xFEBF0C28, 0xFEBF0C48, 0xFEBF0C68):
            check(f"workbuf root covers {member:#x}",
                  start <= member < start + size)

    print(f"\nSummary: {passed} passed, {failed} failed ({len(rows)} RAM overlays)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
