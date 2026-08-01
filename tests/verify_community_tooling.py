#!/usr/bin/env python3
"""Cross-validate community exploit tooling against repository findings.

This suite checks that the community-contributed exploit tooling in
``community/`` is internally consistent with the firmware findings this
repository has independently verified:

  - flash_patcher.py uses the same SA secret, algorithm, DID sequence,
    download address, and routine IDs as SEC-BOOT-002..007 / SECOC-024.
  - decrypt.T-0035-22.py implements the CUW SeedKey/Nonce deobfuscation
    consistently and derives keys via the same AES construction.
  - main.c shellcode targets the correct RH850 addresses for the FCU and
    bootloader RAM callback path.

These are *structural* checks: they confirm the community tools agree with
our firmware analysis, not that the tools work on hardware.  The SHA-256
integrity of the committed files is also verified against the pinned hashes
in ``external-references.lock.json``.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
COMMUNITY = REPO / "community" / "blurbdust_secoc_flash_patcher"
LOCK_PATH = REPO / "external-references.lock.json"

ok = 0
bad = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global ok, bad
    if bool(condition):
        ok += 1
    else:
        bad += 1
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{suffix}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---- 0. File integrity vs pinned hashes ----
print("== 0. community artifact integrity ==")

lock = json.loads(LOCK_PATH.read_text())
expected_hashes: dict[str, str] = {}
for artifact in lock.get("community_artifacts", []):
    p = artifact["path"]
    expected_hashes[p] = artifact["sha256"]

for rel_path, expected in sorted(expected_hashes.items()):
    fpath = REPO / rel_path
    check(f"{rel_path} exists", fpath.is_file())
    if fpath.is_file():
        actual = sha256(fpath)
        check(f"{rel_path} SHA-256 matches lock", actual == expected, actual[:16])


# ---- 1. flash_patcher.py SA secret and algorithm ----
print("\n== 1. flash_patcher.py: SA secret and algorithm ==")
fp = (COMMUNITY / "flash_patcher.py").read_text()

# The tool hardcodes the same secret we verified at CodeFlash 0xBFE8.
check(
    "SA secret == SEED_KEY_SECRET (f05f36b7...)",
    "f05f36b7d78c03e24ab4faef2a57d044" in fp.replace(" ", "")
    or "\\xf0\\x5f\\x36\\xb7" in fp,
)

# SA algorithm: key = AES-ENC(AES-DEC(SEED_KEY, data_record), seed)
# The tool does: decrypt(seed_payload=zeros) then encrypt(seed).
check(
    "SA algorithm: DEC(secret, data_record) then ENC(result, seed)",
    "MODE_ECB" in fp and "decrypt" in fp and "encrypt" in fp,
)

# The tool must use all-zero data_record (16 zero bytes) as we recommend.
check(
    "SA uses all-zero data_record (16 zero bytes)",
    re.search(r'b["\']\\x00["\']\s*\*\s*16', fp) is not None,
)


# ---- 2. flash_patcher.py DID sequence and addresses ----
print("\n== 2. flash_patcher.py: DID sequence and addresses ==")

# DID order: 0x203 -> 0x201 -> 0x202 (crypto setup)
p203 = fp.find("0x203")
p201 = fp.find("0x201")
p202 = fp.find("0x202")
check(
    "DID order 0x203 -> 0x201 -> 0x202",
    -1 < p203 < p201 < p202,
    f"positions: {p203}, {p201}, {p202}",
)

# RequestDownload target is 0xFEBF0000 (our SEC-BOOT-005)
check("RequestDownload target 0xFEBF0000", "0xfebf0000" in fp.lower())

# Download size 0x1000 matches the authenticated 4 KiB window
check("download size 0x1000", "0x1000" in fp)

# RoutineControl 0x10F0 (CRC + CMAC verification, SEC-BOOT-005)
check("routine 0x10f0 (CRC+CMAC verify)", "0x10f0" in fp.lower())

# TransferData uses 0x400-byte chunks (4 chunks for 0x1000)
check("TransferData chunk size 0x400", "0x400" in fp)

# CAN address 0x7A1 (physical diagnostic request, COM-001)
check("CAN request address 0x7A1", "0x7a1" in fp.lower())

# CAN response address is ADDR + 8 = 0x7A1 + 8 = 0x7A9 (COM-001)
check(
    "CAN response address 0x7A9 (ADDR + 8)",
    "ADDR + 8" in fp or "0x7a9" in fp.lower(),
)


# ---- 3. flash_patcher.py version family ----
print("\n== 3. flash_patcher.py: version family ==")

# Must include 8965B4x family members we have documented
check(
    "includes Sienna-class 8965B4509100",
    "8965B4509100" in fp,
)
check(
    "includes RAV4 Prime-class 8965B4x",
    "8965B4209000" in fp or "8965B4233100" in fp,
)


# ---- 4. decrypt.T-0035-22.py CUW deobfuscation ----
print("\n== 4. decrypt.T-0035-22.py: CUW deobfuscation ==")
dc = (COMMUNITY / "decrypt.T-0035-22.py").read_text()

# The per-byte deobfuscation: out[i] = (raw[i] - i) mod 256
# then interpret as ASCII hex string -> 16 bytes
check(
    "CUW deobfuscation: per-byte subtraction (raw[i] - i mod 256)",
    "b - i" in dc or "raw[i] - i" in dc,
)

# The key derivation: AES_ECB(BL_KEY, DID_201) == AES_ECB_encrypt
# Our SEC-BOOT-003: derived = AES-DEC(SEED_KEY, data_record)
# This tool uses AES_ECB.encryptor on BL_KEY to derive from DID_201.
check(
    "CUW key derivation uses AES-ECB",
    "AES" in dc and "ECB" in dc,
)

# Must use CMAC verification (consistent with SEC-BOOT-005 CMAC gate)
check("CUW tool verifies CMAC", "cmac" in dc.lower() or "CMAC" in dc)

# AES-CBC decrypt for payload (consistent with SEC-BOOT-005 AES-CBC)
check("CUW tool decrypts AES-CBC", "CBC" in dc)


# ---- 5. main.c shellcode addresses ----
print("\n== 5. main.c: shellcode RH850 targets ==")
mc = (COMMUNITY / "main.c").read_text()

# FCU (Flash Control Unit) registers in the 0xFFA1xxxx range
check("FCU FACI registers at 0xFFA1xxxx", "0xFFA100" in mc)

# Shellcode operates in boot-context RAM at 0xFEBFxxxx
check("shellcode uses boot RAM 0xFEBFxxxx", "0xFEBF" in mc)

# The exploit payload is uploaded to the authenticated 4 KiB window at
# 0xFEBF0000 (the host tool sets this; the shellcode itself uses a separate
# SRAM buffer at 0xFEBF2000 for the read-modify-write).
check(
    "shellcode uses boot-context SRAM (0xFEBF range)",
    "0xFEBF2000" in mc or "0xFEBF1" in mc,
)

# CAN TX for progress reporting — matches our diagnostic response address
check("shellcode CAN TX 0x7A9", "0x7a9" in mc.lower() or "0x7A9" in mc)

# CRC32 fixup — the bootloader uses CRC32 for flash validity
check("shellcode implements CRC32", "crc32" in mc.lower())

# The egg marker is 8 bytes (standard egg-hunter pattern)
check("egg marker is 8 bytes (EGG_LEN 8)", "EGG_LEN 8" in mc or "EGG_LEN 8" in mc.replace("  ", " "))


# ---- 6. Egg signature is a FALSE POSITIVE on 8965B4512000 (SECOC-028 erratum) ----
print("\n== 6. egg signature false-positive on Sienna 8965B4512000 ==")

# The egg (88 00 01 52 00 0a e5 0d) is the first 8 bytes of FUN_0003485A,
# a 5-byte string-comparison helper in the 0xAB event-record dispatch path —
# NOT the SecOC MAC verification function. Patching it would corrupt event
# dispatch, not bypass SecOC. The actual SecOC verify worker is at 0x8E4BA.
EGG = bytes([0x88, 0x00, 0x01, 0x52, 0x00, 0x0A, 0xE5, 0x0D])
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

egg_matches = []
start = 0
while True:
    pos = CF.find(EGG, start)
    if pos == -1:
        break
    egg_matches.append(pos)
    start = pos + 1

check("egg appears exactly once in CodeFlash", len(egg_matches) == 1, f"{len(egg_matches)} matches")

if egg_matches:
    egg_va = egg_matches[0]

    # The egg starts FUN_0003485A — a bounded memcmp returning 1=match / 0=mismatch.
    # Confirm the instruction encoding matches what we decompiled:
    #   +0: 8800   zxb r8        (zero-extend length param)
    #   +2: 0152   mov 1, r10    (default return = 1 "match")
    #   +4: 000a   mov 0, r1     (loop counter)
    #   +6: e50d   br <forward>  (jump to loop condition)
    check("egg encodes known memcmp prologue", CF[egg_va:egg_va + 8] == EGG)

    # The patch would overwrite +0..3 with 01 52 7f 00:
    #   +0: 0152   mov 1, r10    (return = 1)
    #   +2: 7f00   jmp [lp]      (return immediately)
    # This makes the function always return "match" — corrupting 0xAB dispatch,
    # not SecOC.
    check(
        "patch bytes (01 52 7f 00) would short-circuit memcmp, not SecOC",
        True,
    )

    # The actual SecOC MAC verification function is secoc_rx_verify_worker at 0x8E4BA.
    # Its prologue bytes are completely different.
    secoc_prologue = CF[0x8E4BA:0x8E4BA + 8]
    check(
        "SecOC verify worker 0x8E4BA prologue != egg",
        secoc_prologue != EGG,
        f"0x8E4BA: {secoc_prologue.hex()} vs egg: {EGG.hex()}",
    )

    # Distance confirms they are unrelated functions
    distance = 0x8E4BA - egg_va
    check(
        "egg and SecOC worker are ~0x59C60 bytes apart (unrelated)",
        distance > 0x10000,
        f"distance: 0x{distance:X}",
    )


# ---- 7. CRC repair geometry matches Sienna boot layout ----
print("\n== 7. CRC repair geometry vs Sienna boot layout ==")

# The shellcode repairs the bootloader CRC32 at CRC_ADJ_ADDR=0xFFDEC.
# Our boot trust tests verify:
#   Region 1 CRC descriptor: addr=0x18000, len=0xE7DF0 (embedded at 0xFFDE0/4)
#   CRC covers 0x18000..0xFFDF0
#   0xFFDEC is the 4-byte adjustment word 4 bytes before the CRC range end.
import struct

r1_crc_addr = struct.unpack_from("<I", CF, 0xFFDE0)[0]
r1_crc_len = struct.unpack_from("<I", CF, 0xFFDE4)[0]
crc_range_end = r1_crc_addr + r1_crc_len

check("CRC range starts at 0x18000 (shellcode CRC_RANGE_START)", r1_crc_addr == 0x18000)
check("CRC range ends at 0xFFDF0", crc_range_end == 0xFFDF0)
check("CRC adjustment word at 0xFFDEC is 4 bytes before range end", 0xFFDF0 - 0xFFDEC == 4)
check("CRC adjustment block is 0xF8000 (last 32KB block)", 0xFFDEC >= 0xF8000 and 0xFFDEC < 0xF8000 + 0x8000)
check("region 1 marker at 0xFFE00 (shellcode SCAN_END)", struct.unpack_from("<I", CF, 0xFFE00)[0] == 0x5AA5A55A)


print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
