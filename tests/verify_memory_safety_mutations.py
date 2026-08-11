#!/usr/bin/env python3
"""Sensitivity and independent boundary-model tests for memory-safety oracles."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from memory_safety_semantics import analyze  # noqa: E402

BASE = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    passed += bool(condition)
    failed += not condition
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def mutate(address: int, replacement: bytes) -> dict[str, object]:
    image = bytearray(BASE)
    image[address : address + len(replacement)] = replacement
    # Exercise the promised disposable-file path; never touch firmware/.
    with tempfile.TemporaryDirectory(prefix="memory-safety-mutant-") as directory:
        path = Path(directory) / "CodeFlash.mutant.bin"
        path.write_bytes(image)
        return analyze(path.read_bytes())


print("== baseline and unrelated-byte control ==")
check("unmodified firmware passes all claims", bool(analyze(BASE)["all_pass"]))
unrelated = mutate(0x100, bytes([BASE[0x100] ^ 0x01]))
check("unrelated mutation does not trip semantic oracle", bool(unrelated["all_pass"]))


print("\n== destructive body mutations ==")
for address, size, claims in (
    (0x6BDE, 116, ("MEM-SAFE-001",)),
    (0x7122, 78, ("MEM-SAFE-002",)),
    (0x7170, 126, ("MEM-SAFE-002",)),
    (0x6C8E, 116, ("MEM-SAFE-003",)),
    (0x86EE8, 174, ("MEM-SAFE-004",)),
    (0x32D2, 70, ("MEM-SAFE-001", "MEM-SAFE-005")),
):
    result = mutate(address, bytes(size))
    for claim in claims:
        check(f"zeroing body {address:#x} fails {claim}", not result["claims"][claim])


print("\n== focused decisive-instruction mutations ==")
for label, address, replacement, claim, proposition in (
    ("AES block shift", 0x6BFC, b"\x00\x00", "MEM-SAFE-001", "worker_caps_and_floors_blocks"),
    ("CMAC endpoint subtraction", 0x7162, b"\x00\x00", "MEM-SAFE-002", "setup_computes_start_plus_length_minus_16"),
    ("CMAC 16-byte increment", 0x717E, b"\x00\x00\x00\x00", "MEM-SAFE-002", "step_advances_exactly_16"),
    ("CMAC endpoint equality branch", 0x7184, b"\x00\x00", "MEM-SAFE-002", "finality_is_endpoint_equality"),
    ("compare mismatch NRC", 0x4F0A, b"\x00\x00\x00\x00", "MEM-SAFE-003", "response_distinguishes_equal_and_mismatch"),
    ("command-8 original length load", 0x86F50, b"\x00\x00\x00\x00", "MEM-SAFE-004", "failure_branch_loads_original_length_and_zero_fills"),
    ("range zero-length branch", 0x32D8, b"\x00\x00", "MEM-SAFE-001", "range_checker_rejects_zero_and_wrap"),
    ("range wrap branch", 0x32E2, b"\x00\x00", "MEM-SAFE-005", "range_checker_zero_and_wrap_boundary"),
):
    result = mutate(address, replacement)
    check(
        f"focused mutation fails {claim}.{proposition}",
        not result["propositions"][claim][proposition],
        label,
    )


print("\n== independent boundary model ==")
# This model does not import or call any production-verifier helper.  It states
# the arithmetic proposition independently for the plan-mandated boundary set.
START = 0xFEBF0000
expected = {
    0: (0, 0, False, False),
    1: (0, 1, True, False),
    15: (0, 15, True, False),
    16: (1, 0, True, True),
    17: (1, 1, True, False),
    0x400: (64, 0, True, True),
}
for length, wanted in expected.items():
    full_blocks, remainder, accepted, terminates = wanted
    endpoint = START + length - 16
    # The firmware compares current==endpoint and otherwise increments by 16.
    reachable = length >= 16 and endpoint >= START and (endpoint - START) % 16 == 0
    actual = (length // 16, length % 16, 1 <= length <= 0x400, reachable)
    check(
        f"length {length:#x}: blocks/remainder/admission/CMAC termination",
        actual == wanted,
        f"actual={actual} expected={wanted}",
    )

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
