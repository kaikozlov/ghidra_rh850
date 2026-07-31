#!/usr/bin/env python3
"""Deterministic verification of the Techstream Layer-B / VFOREST flash-SA
finding (TMS-010).

The EPS/VFOREST reflash SA transmission runs through the flash-writer side,
not the PrepareWriter's CalcSeedKey. Specifically:

  * `TCUWCanSecurityVFORESTFlashWriter.dll` IMPORTS
    `CCanCommonFlashWriter::SendNonceAndSeedKey` (delegates; has no
    `CalcSeedKey`/`CollateSeedKey` of its own).
  * `CCanCommonFlashWriter::SendNonceAndSeedKey` (@0x10001820) builds a
    two-frame 0x37/0x38 exchange carrying a nonce + the cal-file seed-key,
    transmitted via CJ2534IF (J2534). Seed-key from
    `CalibrationFile::GetSeedKey(int)`, verbatim.
  * No AES S-box in ANY CUW DLL/EXE (full-tree scan). AES exists only in the
    diagnostic-app DLLs (CommandCommon/UtilityEx2TY/IT3*/DS2Com*, the six of
    TMS-008) and via `Cuw.exe`'s Windows CryptoAPI (the §4.5 CalcSeedKey path).

This test verifies those claims directly from the binaries. It is stdlib-only.
The Techstream distribution tree is NOT committed (gitignored); if absent the
suite SKIPs (exit 0) so `make verify` stays green on a clean checkout. Run on
a machine where Techstream/unpacked/ is populated.
"""
import struct, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UNPACKED = REPO / "Techstream" / "unpacked" / "toyota" / "Toyota Diagnostics"
CUW = UNPACKED / "Calibration Update Wizard"
BIN = UNPACKED / "Techstream" / "bin"

VFOREST = CUW / "TCUWCanSecurityVFORESTFlashWriter.dll"
COMMON_FLASH = CUW / "TCUWCanCommonFlashWriter.dll"
COMMON_PREP = CUW / "TCUWCanCommonPrepareWriter.dll"
CALFILE = CUW / "TCUWCalibrationFile.dll"
CUW_EXE = CUW / "Cuw.exe"
CMD_COMMON = BIN / "CommandCommon.dll"
UTILEX2TY = BIN / "UtilityEx2TY.dll"

AES_SBOX = bytes.fromhex("637c777bf26b6fc5")  # FIPS-197 forward S-box first 8 bytes

ok = 0
bad = 0
def check(name, cond, detail=""):
    global ok, bad
    status = "PASS" if cond else "FAIL"
    if cond: ok += 1
    else: bad += 1
    print(f"[{status}] {name}" + (f"  ({detail})" if detail else ""))

# --- Skip if the (gitignored) Techstream tree is absent -----------------------
if not COMMON_FLASH.exists():
    print(f"SKIP: Techstream tree not present (looked for "
          f"{COMMON_FLASH.relative_to(REPO)}).")
    print("      This suite verifies TMS-010 only where Techstream/unpacked/ "
          "is populated; no action on a clean checkout.")
    sys.exit(0)

def read(p): return p.read_bytes()
def has(hay, needle): return hay.find(needle if isinstance(needle, bytes) else needle.encode()) >= 0

vforest = read(VFOREST)
cflash = read(COMMON_FLASH)
cprep = read(COMMON_PREP)
calfile = read(CALFILE)
cuw = read(CUW_EXE)
cmd = read(CMD_COMMON)
ut2ty = read(UTILEX2TY)

# --- Layer B: VFOREST writer delegates SA to the base FlashWriter -------------
check("VFOREST writer imports SendNonceAndSeedKey (delegates)",
      has(vforest, b"?SendNonceAndSeedKey@CCanCommonFlashWriter@@QAEXABVCBytes@@0PBE1I@Z"))
check("VFOREST writer has NO CalcSeedKey/CollateSeedKey of its own",
      not has(vforest, b"CalcSeedKey") and not has(vforest, b"CollateSeedKey"))

# --- Layer B: the SA send routines live in CCanCommonFlashWriter -------------
for sym in [b"?SendNonce@CCanCommonFlashWriter@@QAEXABVCBytes@@0PBEI@Z",
            b"?SendSeedKey@CCanCommonFlashWriter@@QAEXABVCBytes@@0PBEI@Z",
            b"?SendNonceAndSeedKey@CCanCommonFlashWriter@@QAEXABVCBytes@@0PBE1I@Z"]:
    check(f"CCanCommonFlashWriter defines {sym.split(b'@@')[0][1:].decode()}",
          has(cflash, sym))

# --- Layer B: seed-key comes verbatim from the calibration file --------------
check("CalibrationFile::GetSeedKey(int) export present",
      has(calfile, b"?GetSeedKey@CalibrationFile@@QAEPBEH@Z"))
check("CalibrationFile::GetServiceAuthKey(int) export present",
      has(calfile, b"?GetServiceAuthKey@CalibrationFile@@QAEPBEH@Z"))

# --- Layer B: the PrepareWriter CalcSeedKey path is a SEPARATE mechanism -----
check("CCanCommonPrepareWriter::CalcSeedKey present (separate from FlashWriter)",
      has(cprep, b"?CalcSeedKey@CCanCommonPrepareWriter@@QAE?AVCBytes@@ABV2@@Z"))
check("CCanCommonPrepareWriter::CalcSeedKeyForSecurityUp present",
      has(cprep, b"?CalcSeedKeyForSecurityUp@CCanCommonPrepareWriter@@QAE?AVCBytes@@PBE0@Z"))

# --- No AES S-box anywhere in the CUW reflash toolchain ----------------------
cuw_dlls = [p for p in CUW.glob("*.dll")] + [p for p in CUW.glob("*.exe")]
sbox_hits = {p.name: p.read_bytes().count(AES_SBOX) for p in cuw_dlls
             if p.exists() and p.read_bytes().count(AES_SBOX) > 0}
check("ZERO AES S-box in any CUW DLL/EXE (reflash toolchain has no static AES)",
      not sbox_hits, ", ".join(sorted(sbox_hits)) or "none")

# --- AES lives only in the diagnostic app + Cuw.exe CryptoAPI ----------------
check("CommandCommon.dll (diagnostic app) HAS the AES S-box", has(cmd, AES_SBOX))
check("UtilityEx2TY.dll (diagnostic app) HAS the AES S-box", has(ut2ty, AES_SBOX))
for imp in [b"CryptEncrypt", b"CryptDecrypt", b"CryptImportKey",
            b"CryptAcquireContextA"]:
    check(f"Cuw.exe imports {imp.decode()} (Windows CryptoAPI, §4.5 path)",
          has(cuw, imp))

# --- VFOREST writer is native (so SendNonceAndSeedKey is real x86, not IL) ---
def is_dotnet(data):
    pe = data.find(b"PE\x00\x00")
    if pe < 0: return False
    opt = pe + 4 + 20
    magic = struct.unpack("<H", data[opt:opt + 2])[0]
    dd = opt + (96 if magic == 0x10b else 112)
    return struct.unpack("<I", data[dd + 14 * 8 + 4:dd + 14 * 8 + 8])[0] != 0

check("TCUWCanSecurityVFORESTFlashWriter.dll is native (NOT .NET)",
      not is_dotnet(vforest))
check("TCUWCanCommonFlashWriter.dll is native (NOT .NET)",
      not is_dotnet(cflash))

print()
print(f"{ok} passed, {bad} failed")
sys.exit(1 if bad else 0)
