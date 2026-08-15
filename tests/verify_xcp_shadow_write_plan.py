#!/usr/bin/env python3
"""Verify the offline-only COM-005 XCP shadow-write planner."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.followups.xcp_shadow_write_plan import (  # noqa: E402
    MAX_DOWNLOAD,
    SHADOW_END,
    SHADOW_SIZE,
    SHADOW_START,
    XcpShadowWriteError,
    build_download_plan,
    chunk_write,
    download_request,
    modify_bits_request,
    set_mta_request,
    simulate_plan,
    simulate_write,
    validate_window,
)

passed = failed = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {label}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {label}" + (f" ({detail})" if detail else ""))


def rejects(fn) -> bool:
    try:
        fn()
    except XcpShadowWriteError:
        return True
    return False


print("== exact request encoding ==")
check("shadow geometry is exact 32 KiB", SHADOW_START == 0xFEBF7C00 and SHADOW_END == 0xFEBFFBFF and SHADOW_SIZE == 0x8000)
check("SET_MTA encodes tester address little-endian", set_mta_request(SHADOW_START).hex() == "f6000000007cbffe")
check("DOWNLOAD 1 byte is padded to CTO 8", download_request(bytes.fromhex("aa")).hex() == "f001aa0000000000")
check("DOWNLOAD 6 bytes fills CTO 8", download_request(bytes.fromhex("010203040506")).hex() == "f006010203040506")
check("DOWNLOAD maximum is six data bytes", MAX_DOWNLOAD == 6 and rejects(lambda: download_request(b"1234567")))
check("MODIFY_BITS raw fields encode as EC/shift/u16le/u16le/pad", modify_bits_request(3, 0x1234, 0xABCD).hex() == "ec033412cdab0000")

print("\n== range and chunk model ==")
check("zero-length write rejected", rejects(lambda: validate_window(SHADOW_START, 0)))
check("write before shadow rejected", rejects(lambda: validate_window(SHADOW_START - 1, 1)))
check("write crossing shadow end rejected", rejects(lambda: validate_window(SHADOW_END, 2)))
chunks = chunk_write(SHADOW_START + 4, bytes(range(14)))
check("14-byte write chunks as 6/6/2", [len(chunk.data) for chunk in chunks] == [6, 6, 2])
check("chunk addresses advance by payload length", [chunk.address for chunk in chunks] == [SHADOW_START + 4, SHADOW_START + 10, SHADOW_START + 16])
check("chunk payloads reconstruct exactly", b"".join(chunk.data for chunk in chunks) == bytes(range(14)))

plan = build_download_plan(SHADOW_START + 4, bytes(range(14)))
check("plan binds COM-005", plan["finding_id"] == "COM-005")
check("planner has no live execution path", plan["live_execution_implemented"] is False)
check("plan records impact bounds: Ghidra execute=false is analysis metadata; hardware MPU grants supervisor execute; no direct consumer",
      plan["window"]["executable"] is False
      and plan["window"]["executable_basis"] == "ghidra_localram_block_metadata"
      and plan["window"]["hardware_mpu_supervisor_executable"] is True
      and plan["window"]["direct_runtime_consumer_recovered"] is False)
check("plan emits CONNECT + SET_MTA + three DOWNLOAD frames", [row["operation"] for row in plan["requests"]] == ["connect", "set_mta", "download", "download", "download"])
check("all planned frames are exactly eight bytes", all(len(bytes.fromhex(row["request"])) == 8 for row in plan["requests"]))

print("\n== deterministic local simulation ==")
shadow = bytes((index & 0xFF) for index in range(SHADOW_SIZE))
data = bytes.fromhex("deadbeef001122")
updated = simulate_write(shadow, SHADOW_START + 0x100, data)
check("simulation preserves 32 KiB geometry", len(updated) == SHADOW_SIZE)
check("simulation changes exact requested slice", updated[0x100:0x107] == data)
check("simulation preserves prefix/suffix", updated[:0x100] == shadow[:0x100] and updated[0x107:] == shadow[0x107:])
updated2, simulated = simulate_plan(shadow, SHADOW_START + 0x100, data)
check("simulation helper returns identical bytes", updated2 == updated)
check("simulation metadata reports output hash and bounded changes",
      simulated["mode"] == "simulation" and 0 < simulated["simulation"]["changed_bytes"] <= len(data))

print("\n== CLI is offline-only ==")
probe = REPO / "exploit/followups/xcp_shadow_write_plan.py"
source = probe.read_text(encoding="utf-8")
check("planner source has no Panda import", "from panda import" not in source and "import panda" not in source)
check("planner source exposes no execute flag", "--execute" not in source)
cli = subprocess.run(
    [sys.executable, str(probe), hex(SHADOW_START), "01020304050607"],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("CLI emits two DOWNLOADs for seven bytes", cli.returncode == 0 and '"download_requests": 2' in cli.stdout)
unsafe = subprocess.run(
    [sys.executable, str(probe), hex(SHADOW_START - 1), "01"],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("CLI rejects address outside shadow window", unsafe.returncode != 0)

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    source_shadow = root / "shadow.bin"
    output_shadow = root / "out.bin"
    source_shadow.write_bytes(shadow)
    simulated_cli = subprocess.run(
        [
            sys.executable,
            str(probe),
            hex(SHADOW_START + 0x100),
            data.hex(),
            "--simulate-shadow",
            str(source_shadow),
            "--simulation-output",
            str(output_shadow),
        ],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    check("CLI simulation writes exact local output only", simulated_cli.returncode == 0 and output_shadow.read_bytes() == updated)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
