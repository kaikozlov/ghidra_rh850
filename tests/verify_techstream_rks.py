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
absent the suite SKIPs (exit 77) so `make verify` can report the prerequisite
checkout. Run on a machine where Techstream/unpacked/ is populated.
"""
import hashlib
import struct, subprocess, sys
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
UNPACKED = REPO / "Techstream" / "unpacked" / "toyota" / "Toyota Diagnostics"
CUW = UNPACKED / "Calibration Update Wizard"
BIN = UNPACKED / "Techstream" / "bin"

RKS = CUW / "CUWAccessRKS.dll"
RKS_WRAPPER = CUW / "CUWAccessRKSWrapper.dll"
CUW_EXE = CUW / "Cuw.exe"
VFOREST = CUW / "TCUWCanSecurityVFORESTFlashWriter.dll"
UNIFIED = CUW / "TCUWCanUnifiedFlashWriter.dll"
COMMON_PREP = CUW / "TCUWCanCommonPrepareWriter.dll"

ok = 0
bad = 0
def check(name, cond, detail="", oracle_class="cfg_dataflow"):
    global ok, bad
    status = "PASS" if cond else "FAIL"
    if cond: ok += 1
    else: bad += 1
    print(f"[{status}][{oracle_class}] {name}" + (f"  ({detail})" if detail else ""))

# --- Skip if the (gitignored) Techstream tree is absent -----------------------
if not RKS.exists():
    print("SKIP: Techstream tree not present "
          f"(looked for {RKS.relative_to(REPO)}).")
    print("      This suite verifies TMS-009 only where Techstream/unpacked/ "
          "is populated; no action on a clean checkout.")
    sys.exit(77)


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
cuw_b = read(CUW_EXE)
vforest_b = read(VFOREST)
unified_b = read(UNIFIED)
commonprep_b = read(COMMON_PREP)

check("CUWAccessRKS.dll is a .NET assembly (CLR header)", is_dotnet(rks_b))
check("CUWAccessRKSWrapper.dll is a .NET assembly", is_dotnet(wrap_b))
check("Cuw.exe is pinned", hashlib.sha256(cuw_b).hexdigest()
      == "97f7b9302a6090e2715ca6c9713aecc73404d6c0f75aede2dd52f09bd201074b",
      oracle_class="identity_hash")
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

# --- Layer A: SeedValue native boundary --------------------------------------
# CUWAccessRKSWrapper maps native request-buffer +0x78 to mstrSeedValue.
il_tool = REPO / "tools/techstream/inspect_dotnet_il.py"
wrapper_il = subprocess.check_output(
    [sys.executable, str(il_tool), str(RKS_WRAPPER),
     "--type", r"<Module>", "--method", "SetDataForReproKey"],
    text=True,
)
check("wrapper maps native +0x78 to SeedValue",
      "ldc.i4.s       0x78" in wrapper_il
      and "set_mstrSeedValue" in wrapper_il)

# Native Cuw.exe builds that field from the request builder's second argument:
# it preserves EDX at [EBP-0x44], passes those 16 bytes as the fourth argument
# to FUN_0047fb24, copies exactly 16 bytes, and renders 32 uppercase hex digits
# plus NUL into request_buffer+0x78 (outer-object offset +0x28D).
pe = pefile.PE(str(CUW_EXE), fast_load=True)
image_base = pe.OPTIONAL_HEADER.ImageBase
body_pins = {
    (0x0049BCFE, 989): "0f2427fa1323a5d20f781ce0f32013f8ad77b25acf3833165d9be7205d6e0aba",
    (0x0047FB24, 565): "7e6a8d5d7d3e74bc02cbfcad07ee9f6650943bef0789c7b8285a76c6411051fd",
    (0x0041A01C, 104): "e00ded4e0bf0f3f3da6dcb7998a4ddd95f20cb6775814cefb2734b75bf40e87a",
}
for (address, size), expected in body_pins.items():
    body = pe.get_data(address - image_base, size)
    check(f"Cuw.exe RKS body {address:#x}/{size}", hashlib.sha256(body).hexdigest() == expected,
          oracle_class="identity_hash")

request_builder = pe.get_data(0x0049BCFE - image_base, 989)
request_copy = pe.get_data(0x0047FB24 - image_base, 565)
hex_encoder = pe.get_data(0x0041A01C - image_base, 104)
check("RKS builder preserves its second argument for SeedValue",
      b"\x89\x55\xbc" in request_builder and b"\x8b\x55\xbc\x52" in request_builder)
check("SeedValue consumes exactly 16 input bytes",
      b"\x6a\x10\x8b\x45\x08\x50" in request_copy)
check("SeedValue writes a 33-byte hex string at native offset +0x78",
      b"\x6a\x21\x8d\x8b\x8d\x02\x00\x00" in request_copy)
check("SeedValue encoder is uppercase hexadecimal",
      b"\x80\x04\x1e\x30" in hex_encoder
      and b"\x80\x04\x1e\x37" in hex_encoder)

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
