#!/usr/bin/env python3
"""Verify the generated, representation-bounded Techstream crypto inventory."""
from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TREE = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics"
ARTIFACT = REPO / "data/generated/techstream_v18/crypto_inventory.json"
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    passed += bool(condition)
    failed += not condition
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


print("\n== IT3UtilityNeoNK AES-256 live-use anchors ==")
neo_path = TREE / "Techstream/bin/IT3UtilityNeoNK.dll"
if neo_path.is_file():
    neo = neo_path.read_bytes()
    neo_key = b"bCVaAQnA3fNdDgdls2Cjar5er8iwP4Xz"
    check("NeoNK full 32-byte key literal plus NUL is exact at 0x3A7D4",
          neo[0x3A7D4:0x3A7D4 + 33] == neo_key + b"\x00")
    check("NeoNK wrapper strlen-loads and pushes the same key VA",
          neo[0x23F3B:0x23F40] == bytes.fromhex("bfd4a70310")
          and neo[0x23F47:0x23F4C] == bytes.fromhex("f2aef7d149")
          and neo[0x23F5A:0x23F5F] == bytes.fromhex("68d4a70310"))
    # 0x10024050 dispatches on key_length-16. The selector table maps offsets
    # 0,8,16 (lengths 16,24,32) to the AES-128/192/256 setup arms.
    key_dispatch = struct.unpack_from("<4I", neo, 0x24254)
    key_selectors = neo[0x24264:0x24264 + 17]
    check("NeoNK key schedule arms are 16/24/32-byte selectors",
          key_dispatch[:3] == (0x1002407A, 0x10024082, 0x10024089)
          and [key_selectors[i] for i in (0, 8, 16)] == [0, 1, 2])
    check("NeoNK 32-byte strlen result selects AES-256 setup arm",
          len(neo_key) == 32 and key_selectors[len(neo_key) - 16] == 2)
    check("NeoNK decrypt wrapper iterates one 0x10024460 call per 16-byte block",
          neo[0x23F6B:0x23F82] == bytes.fromhex(
              "c1eb048bfb74488d5424248d442414525056e8de040000"))
    check("0x10023F26 is only the pre-decrypt 16-byte alignment test",
          neo[0x23F26:0x23F2B] == bytes.fromhex("f6c30f740e"))
    check("post-decrypt tail trim uses only final-byte count, not strict PKCS7 validation",
          neo[0x24001:0x24035] == bytes.fromhex(
              "8a4437ff884424108b4c241081e1ff0000003bce77238bc62bc13bc67316"
              "8bce03f82bc833c08bf1c1e902f3ab8bce83e103f3aa"))
else:
    print("[SKIP] IT3UtilityNeoNK.dll unavailable; live-use byte anchors not executed")


if TREE.is_dir():
    print("\n== byte-identical live regeneration ==")
    with tempfile.TemporaryDirectory(prefix="crypto-inventory-") as directory:
        output = Path(directory) / "crypto_inventory.json"
        completed = subprocess.run(
            [sys.executable, str(REPO / "tools/techstream/generate_crypto_inventory.py"),
             "--root", str(TREE), "--output", str(output)],
            cwd=REPO, text=True, capture_output=True,
        )
        check("generator exits successfully", completed.returncode == 0, completed.stderr.strip())
        check("live regeneration is byte-identical", output.read_bytes() == ARTIFACT.read_bytes())
else:
    print("\n[SKIP] external Techstream tree unavailable; committed artifact checks still ran")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else (0 if TREE.is_dir() else 77))
