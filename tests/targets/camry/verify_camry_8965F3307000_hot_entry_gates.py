#!/usr/bin/env python3
"""Pin exact-F33 late programming/diagnostic gate evidence (offline only).

This test binds disassembled CodeFlash bytes, completed retained pseudocode, and
SID-0x23 range policy to the current image. Its value table is a pure model of
those instructions, *not* a substitute for original-byte RH850 scenario runs or
live validation of a successful PROGRAMMING transition.
"""
from __future__ import annotations

import hashlib
import json
import struct

from tools import REPO_ROOT
from tools.project.decompiler_evidence import load_function_corpus

ROOT = REPO_ROOT
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
ASSESSMENT = ROOT / "data/generated/camry_8965F3307000_application_ram_loader_assessment.json"
SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"


def check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


def main() -> None:
    image = IMAGE.read_bytes()
    rows, count = load_function_corpus(CORPUS)
    assessment = json.loads(ASSESSMENT.read_text())
    check(len(image) == 0x100000 and hashlib.sha256(image).hexdigest() == SHA256,
          "bound to exact Camry F33 CodeFlash")
    check(count == 7336 and len(rows) == count and all(row["decompile_completed"] for row in rows.values()),
          "complete 7,336-function retained corpus")
    check(assessment["target"]["codeflash_sha256"] == SHA256,
          "application loader assessment targets the same image")

    def has(entry: int, *fragments: str) -> bool:
        text = rows[entry]["decompiled_c"]
        return all(piece in text for piece in fragments)

    # Original-image RH850E3v5 instructions (also checked independently with
    # the pinned v850-elf-objdump). This avoids trusting an unrelated calibration
    # or modeling the gates from comments alone.
    check(image[0x4D5BA:0x4D5D8].hex() ==
          "8700e40f9330623a9a0d409e0300f39fb118f309b3050b527f0000527f00",
          "programming-speed precondition is byte-exact")
    check(image[0x4D5D8:0x4D5FE].hex() ==
          "a40f1f30e49fbbae84579bc90106efff920d400e0300e10fb318e199b105e051a20501527f00",
          "phase/supply/addressing precondition is byte-exact")
    check(image[0x98E84:0x98E90].hex() == "400e0300810f690de009ca2d" and image[0x30D68] == 0x5A,
          "fixed calibration disables stock application XCP commands")
    check(struct.unpack_from("<HH", image, 0x318B0) == (0x0180, 0x0A00),
          "exact speed and supply thresholds")
    check(has(0x4D5BA, "DAT_febee892", "communication_control_admission_limit", "0xb") and
          has(0x4D5D8, "DAT_febee81f", "DAT_febe66ba", "DAT_febe819a", "DAT_000318b2"),
          "gate input/source mapping matches retained pseudocode")
    check(has(0xB4214, "DAT_febeb1a4", "write_xor_encoded_u8_triplicate_d268c") and
          has(0xBF3AA, "DAT_febee81f = DAT_febeb1a4", "DAT_febee892"),
          "phase snapshot and speed snapshot have identified application producers")
    check(has(0x5D68, "puVar5[-0x6cf1] != '\\x02'", "uVar7 = 0x33"),
          "boot RequestDownload retains SecurityAccess state-2 check")

    # Distinguish gates before proposing a disruptive live 0x10 02 experiment.
    def gate(session: int, speed_raw: int, phase: int, supply: int, address_mode: int) -> tuple[int, int]:
        speed_error = 0x0B if session == 2 and speed_raw > 0x0180 else 0
        handoff_blocked = int(phase == 0x11 or supply < 0x0A00 or address_mode != 0)
        return speed_error, handoff_blocked

    cases = (
        (2, 0x180, 0x22, 0xA00, 0, (0, 0)),
        (2, 0x181, 0x22, 0xA00, 0, (0x0B, 0)),
        (3, 0x181, 0x22, 0xA00, 0, (0, 0)),
        (2, 0, 0x11, 0xA00, 0, (0, 1)),
        (2, 0, 0x22, 0x9FF, 0, (0, 1)),
        (2, 0, 0x22, 0xA00, 1, (0, 1)),
    )
    check(all(gate(*args) == expected for *args, expected in cases),
          "modeled gate truth table covers speed/phase/supply/addressing boundaries")

    read_policy = assessment["application_uds"]["read_memory_by_address"]
    check(read_policy == {"sid": "0x23", "callback": "0x000965C0", "sessions": [3]},
          "RMBA is read-only and extended-session-only on stock F33")
    check(image[0x26154] == 1 and has(0x4FC8E, "validate_febe_memory_span_against_five_exclusions_4fbe8"),
          "memory-ID-1 RMBA uses the five RAM exclusion records")
    protected = [struct.unpack_from("<II", image, 0x29254 + 8 * i) for i in range(5)]
    check(protected == [(0xFEBE0000, 0xFEBE37FF), (0xFEBE503C, 0xFEBE52A7),
                        (0xFEBF0288, 0xFEBF13CB), (0xFEBF4958, 0xFEBF4B33),
                        (0xFEBF6000, 0xFEBF6CDF)],
          "exact stock RMBA protected intervals")
    probes = {0xFEBEE892: 2, 0xFEBEE81F: 1, 0xFEBE66BA: 2, 0xFEBE819A: 1}
    check(all(0xFEBE0000 <= address and address + size <= 0xFEC00000 and
              not any(lo <= address + size - 1 and address <= hi for lo, hi in protected)
              for address, size in probes.items()),
          "all four diagnostic-gate snapshots are within readable RAM spans")

    print("All hot-entry gate invariants pass (static/offline; no machine execution).")


if __name__ == "__main__":
    main()
