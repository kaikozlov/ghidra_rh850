#!/usr/bin/env python3
"""Deterministic verification of the Techstream RKS / two-layer reflash
authorization finding (TMS-009).

CUW reflash authorization is two independent layers that never exchange
material:

  Layer A — TIS portal RKS (CUWAccessRKS.dll/.NET): VIN+license-bound
            *permission* gate; embedded-IE browser automation; the returned
            "Signature" is validated only by a regex (no client-side crypto).
  Layer B — per-ECU CalcSeedKey/CollateSeedKey (native flash writers): the
            cryptographic ECU unlock with the calibration-file key
            (maps to firmware SEC-BOOT-003).

This test verifies the Layer A characterization and the Layer A/B independence
directly from the binaries. It is stdlib-only (no dnfile): .NET metadata is
checked via PE CLR-header detection and byte-level string search across both
the #Strings (ASCII identifiers) and #US (UTF-16LE literals) heaps.

The Techstream distribution tree is NOT committed (gitignored). If it is
absent the suite SKIPs (exit 0) so `make verify` stays green on a clean
checkout. Run on a machine where Techstream/unpacked/ is populated.
"""
import struct, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UNPACKED = REPO / "Techstream" / "unpacked" / "toyota" / "Toyota Diagnostics"
CUW = UNPACKED / "Calibration Update Wizard"
BIN = UNPACKED / "Techstream" / "bin"

RKS = CUW / "CUWAccessRKS.dll"
RKS_WRAPPER = CUW / "CUWAccessRKSWrapper.dll"
VFOREST = CUW / "TCUWCanSecurityVFORESTFlashWriter.dll"
UNIFIED = CUW / "TCUWCanUnifiedFlashWriter.dll"
COMMON_PREP = CUW / "TCUWCanCommonPrepareWriter.dll"

ok = 0
bad = 0
def check(name, cond, detail=""):
    global ok, bad
    status = "PASS" if cond else "FAIL"
    if cond: ok += 1
    else: bad += 1
    print(f"[{status}] {name}" + (f"  ({detail})" if detail else ""))

# --- Skip if the (gitignored) Techstream tree is absent -----------------------
if not RKS.exists():
    print("SKIP: Techstream tree not present "
          f"(looked for {RKS.relative_to(REPO)}).")
    print("      This suite verifies TMS-009 only where Techstream/unpacked/ "
          "is populated; no action on a clean checkout.")
    sys.exit(0)


def read(path):
    return path.read_bytes()

# --- .NET detection via PE CLR data directory (#14) ---------------------------
def is_dotnet(data):
    pe = data.find(b"PE\x00\x00")
    if pe < 0:
        return False
    opt = pe + 4 + 20            # COFF header is 20 bytes
    magic = struct.unpack("<H", data[opt:opt + 2])[0]
    dd = opt + (96 if magic == 0x10b else 112)   # size of optional header tables
    clr_size = struct.unpack("<I", data[dd + 14 * 8 + 4:dd + 14 * 8 + 8])[0]
    return clr_size != 0

rks_b = read(RKS)
wrap_b = read(RKS_WRAPPER)
vforest_b = read(VFOREST)
unified_b = read(UNIFIED)
commonprep_b = read(COMMON_PREP)

check("CUWAccessRKS.dll is a .NET assembly (CLR header)", is_dotnet(rks_b))
check("CUWAccessRKSWrapper.dll is a .NET assembly", is_dotnet(wrap_b))
check("TCUWCanSecurityVFORESTFlashWriter.dll is native (NOT .NET)",
      not is_dotnet(vforest_b))
check("TCUWCanCommonPrepareWriter.dll is native (NOT .NET)",
      not is_dotnet(commonprep_b))

# --- Layer A: data model + XML schema (literals live in the #US heap, UTF-16LE)
def has_u16(haystack, needle):
    return haystack.find(needle.encode("utf-16-le")) >= 0

xml_tags = ["ReproKeyRequest", "TerminalInfo", "VehicleIdentificationNumber",
            "KeypairID", "SeedValue", "Signature", "X-Version",
            "SoftwareID", "SoftwareVersion", "LicenseKey", "RequesterKind"]
for tag in xml_tags:
    check(f"RKS #US literal present: {tag!r}", has_u16(rks_b, tag))

# The format-validation regex for the returned Signature
check("RKS Signature validated by regex ^[0-9a-zA-Z]+$",
      has_u16(rks_b, "^[0-9a-zA-Z]+$"))

# --- Layer A: IE browser-automation mechanism (COM SHDocVw / mshtml) ----------
ie_markers = ["0002DF01-0000-0000-C000-000000000046",  # CLSID InternetExplorer
              "Shell.Application", "iexplore.exe",
              "getElementsByTagName", "textarea", "document"]
for m in ie_markers:
    check(f"IE-automation marker present: {m!r}", has_u16(rks_b, m))

# --- Layer A: NO client-side cryptography -------------------------------------
# Crypto API class names live in the #Strings heap as ASCII identifiers.
crypto_apis = ["RSACryptoServiceProvider", "DSACryptoServiceProvider",
               "ECDsaCng", "ECDsaOpenSsl", "RSAPKCS1SignatureDeformatter",
               "RSAPKCS1SignatureFormatter", "SignedXml", "SignatureDescription"]
for api in crypto_apis:
    idx = rks_b.find(api.encode())
    check(f"no client-side crypto API: {api!r}", idx < 0,
          f"found at {idx}" if idx >= 0 else "")
check("no VerifySignature/VerifyData call string",
      rks_b.find(b"VerifySignature") < 0 and rks_b.find(b"VerifyData") < 0)

# --- Layer A <-> Layer B independence ----------------------------------------
# The returned Signature must never reach a flash writer. Native writers store
# identifiers as ASCII; check both ASCII and UTF-16LE for robustness.
def count_both(haystack, needle):
    return haystack.count(needle.encode()) + haystack.count(needle.encode("utf-16-le"))

for w, data in [("VFOREST", vforest_b), ("Unified", unified_b),
                ("CommonPrepareWriter", commonprep_b)]:
    for tok in ["ReproKey", "tagRepro", "ImportReproKey", "SetReproKey"]:
        n = count_both(data, tok)
        check(f"{w} writer has no '{tok}' reference", n == 0, f"count={n}")

# --- Layer B present: the EPS writer uses the cal-file SA path ---------------
# CCanCommonPrepareWriter::CalcSeedKey is the writer-side key computation
# (native DLL; C++ mangled symbol is ASCII).
check("Layer B: CalcSeedKey present in CommonPrepareWriter",
      commonprep_b.find(b"CalcSeedKey@CCanCommonPrepareWriter") >= 0)
check("Layer B: CalcSeedKeyForSecurityUp variant present",
      commonprep_b.find(b"CalcSeedKeyForSecurityUp@CCanCommonPrepareWriter") >= 0)

print(f"\n{ok} passed, {bad} failed")
sys.exit(1 if bad else 0)
