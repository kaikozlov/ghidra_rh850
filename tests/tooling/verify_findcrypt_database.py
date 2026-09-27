#!/usr/bin/env python3
"""Check firmware crypto-constant locations using the FindCrypt database."""
import json
import sys

from tools import REPO_ROOT
REPO = REPO_ROOT
DB_PATH = REPO / "ghidra" / "ghidra-findcrypt" / "data" / "database.json"
CF_PATH = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"

ok = 0
bad = 0
def check(name, cond, detail=""):
    global ok, bad
    status = "PASS" if cond else "FAIL"
    if cond: ok += 1
    else: bad += 1
    print(f"[{status}] {name}" + (f"  ({detail})" if detail else ""))

db = json.loads(DB_PATH.read_text())

# Scan the CodeFlash-only image with the signatures used by FindCrypt.
print("\n== firmware scan with findcrypt signatures ==")
cf = CF_PATH.read_bytes()

def hex_to_bytes(hex_str):
    return bytes(int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2))

def find_all(haystack, needle):
    """Find all occurrences of needle in haystack, return list of offsets."""
    results = []
    start = 0
    while True:
        idx = haystack.find(needle, start)
        if idx == -1:
            break
        results.append(idx)
        start = idx + 1
    return results

# Build name → bytes lookup
sig_bytes = {}
for entry in db:
    sig_bytes[entry["name"]] = hex_to_bytes(entry["hexBytes"])

# The CodeFlash-only file starts at VA 0, so its offsets are CodeFlash VAs.
sbox_hits = find_all(cf, sig_bytes["AES_Encryption_SBox"])
check("AES S-box found in CodeFlash", len(sbox_hits) > 0,
      f"{len(sbox_hits)} hit(s) at {[hex(h) for h in sbox_hits]}")
if sbox_hits:
    check("AES S-box at expected offset 0x8FF1",
          0x8FF1 in sbox_hits,
          f"hits at {[hex(h) for h in sbox_hits]}")

# Inverse S-box should be at VA 0x25628
inv_sbox_hits = find_all(cf, sig_bytes["AES_Decryption_SBox_Inverse"])
check("AES inverse S-box found in CodeFlash", len(inv_sbox_hits) > 0,
      f"{len(inv_sbox_hits)} hit(s) at {[hex(h) for h in inv_sbox_hits]}")
if inv_sbox_hits:
    check("AES inverse S-box at expected offset 0x25628",
          0x25628 in inv_sbox_hits,
          f"hits at {[hex(h) for h in inv_sbox_hits]}")

# Te0 should exist — but in this firmware, T-tables are stored in a different
# endianness than the database's canonical form. The database stores AES values
# as little-endian 32-bit words; the firmware stores them big-endian.
# Test both the raw pattern and the 4-byte-word-swapped variant.
te0_pattern = sig_bytes.get("Rijndael_Te0", b"")
te0_hits = find_all(cf, te0_pattern)

# Also check the byte-swapped variant (swap each 4-byte word)
if len(te0_pattern) >= 4 and len(te0_pattern) % 4 == 0:
    te0_swapped = bytearray(len(te0_pattern))
    for i in range(0, len(te0_pattern), 4):
        te0_swapped[i]     = te0_pattern[i + 3]
        te0_swapped[i + 1] = te0_pattern[i + 2]
        te0_swapped[i + 2] = te0_pattern[i + 1]
        te0_swapped[i + 3] = te0_pattern[i]
    te0_swapped = bytes(te0_swapped)
    te0_swap_hits = find_all(cf, te0_swapped)
else:
    te0_swap_hits = []

check("Rijndael Te0 found in CodeFlash (native or byte-swapped)",
      len(te0_hits) + len(te0_swap_hits) > 0,
      f"native: {len(te0_hits)} hit(s) at {[hex(h) for h in te0_hits]}, "
      f"swapped: {len(te0_swap_hits)} hit(s) at {[hex(h) for h in te0_swap_hits]}")
if te0_swap_hits:
    check("Rijndael Te0 byte-swapped at expected offset 0x23628",
          0x23628 in te0_swap_hits,
          f"hits at {[hex(h) for h in te0_swap_hits]}")

# ---- Summary ----
print(f"\n{'='*40}")
print(f"Results: {ok} passed, {bad} failed")
if bad > 0:
    print("FAILED")
    sys.exit(1)
else:
    print("ALL PASSED")
