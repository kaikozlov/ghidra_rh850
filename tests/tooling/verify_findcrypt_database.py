#!/usr/bin/env python3
"""Check Findcrypt package provenance and firmware crypto-constant locations."""
import hashlib
import io
import json
import re
import sys
import zipfile

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

# Package verification is independent of the firmware scan below.
print("== findcrypt package provenance ==")
vendor = DB_PATH.parent.parent
source_commit = "fcaa49e545b131e2cc631168c6c168c1aec862a6"
database_sha256 = "8f7bdbc5f9bbe48a4ed93792adab67fca6f103384165ed1917d883870ee6f471"
patch_path = "patches/ghidra-12.2-task-monitor.patch"
patch_sha256 = "b2e08dbb2d9f9a66fea38bc595b9d22bec775e85d5bfb3dc46d7258eb243c7b3"
try:
    provenance = json.loads((vendor / "PROVENANCE.json").read_text())
    rebuild = provenance["local_rebuild"]
    check("Findcrypt upstream v3.1.9 source pinned",
          provenance["version"] == "3.1.9"
          and provenance["upstream"]["baseline_commit"] == source_commit
          and rebuild["source_tag"] == "v3.1.9"
          and rebuild["source_commit"] == source_commit)
    check("Findcrypt requires Ghidra 12.2",
          provenance["ghidra"]["required_version"] == "12.2")
    patches = provenance["source_patches"]
    check("Findcrypt Ghidra 12.2 compatibility patch is pinned",
          len(patches) == 1
          and patches[0]["path"] == patch_path
          and patches[0]["ghidra_version"] == "12.2"
          and patches[0]["sha256"] == patch_sha256
          and hashlib.sha256((vendor / patch_path).read_bytes()).hexdigest()
          == patch_sha256)
    check("Findcrypt database matches pinned upstream",
          hashlib.sha256(DB_PATH.read_bytes()).hexdigest()
          == rebuild["database_sha256"] == database_sha256)
    check("Findcrypt database contains 130 signatures", len(db) == 130)
    archives = sorted(vendor.glob("*.zip"))
    check("Exactly one Ghidra 12.2 Findcrypt package is vendored",
          len(archives) == 1
          and re.fullmatch(r"ghidra_12\.2_PUBLIC_\d{8}_GhidraFindcrypt\.zip",
                           archives[0].name) is not None)
    if len(archives) == 1:
        archive = archives[0]
        check("Vendored package list matches actual files",
              sorted(provenance["vendored_files"])
              == sorted(["data/database.json", patch_path, archive.name]))
        check("Findcrypt package SHA-256 matches provenance",
              hashlib.sha256(archive.read_bytes()).hexdigest()
              == rebuild["artifact_sha256"])
        with zipfile.ZipFile(archive) as package:
            properties = dict(
                line.split("=", 1)
                for line in package.read("GhidraFindcrypt/extension.properties")
                .decode().splitlines()
                if "=" in line and not line.lstrip().startswith("#")
            )
            check("Packaged extension declares Ghidra 12.2",
                  properties.get("version") == "12.2"
                  and properties.get("name") == "GhidraFindcrypt")
            check("Packaged and CLI signature databases are identical",
                  package.read("GhidraFindcrypt/data/database.json")
                  == DB_PATH.read_bytes())
            jar = package.read("GhidraFindcrypt/lib/GhidraFindcrypt.jar")
            check("Findcrypt JAR SHA-256 matches provenance",
                  hashlib.sha256(jar).hexdigest() == rebuild["jar_sha256"])
            with zipfile.ZipFile(io.BytesIO(jar)) as classes:
                analyzer = classes.read("findcrypt/FindCryptAnalyzer.class")
                check("Findcrypt analyzer compiled for Java 25",
                      analyzer[:4] == b"\xca\xfe\xba\xbe"
                      and int.from_bytes(analyzer[6:8], "big") == 69)
except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
    check("Findcrypt package provenance is readable", False, str(exc))

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
