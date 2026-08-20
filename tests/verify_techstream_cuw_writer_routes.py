#!/usr/bin/env python3
"""Independent raw-artifact checks for the CUW writer/factory inventory."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics"
CUW = ROOT / "Calibration Update Wizard"
INVENTORY = REPO / "data/generated/techstream_v18/cuw_writer_inventory.json"
passed = failed = 0
oracle = "raw_bytes"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


if not ROOT.is_dir():
    print("[SKIP] pinned Techstream V18 tree is unavailable")
    raise SystemExit(77)


def independently_decode(data: bytes) -> bytes:
    """Re-express TCUWParameterForVC RVA 0x10001000 without generator imports."""
    assert len(data) % 2 == 0
    result = bytearray()
    for index in range(0, len(data), 2):
        high, low = data[index:index + 2]
        high_quartet = ((high >> 4) * 4) + ((high & 0x0F) >> 2)
        low_quartet = ((low >> 4) * 4) + ((low & 0x0F) >> 2)
        result.append((((high_quartet * 4 + (low_quartet >> 2) + 0x1E) * 4)
                       + (low_quartet & 3)) & 0xFF)
    return bytes(result).rstrip(b"\xff")


def route(name: str) -> dict[str, str]:
    decoded = independently_decode((CUW / "Ini" / name).read_bytes()).decode("latin1")
    rows = list(csv.reader(io.StringIO(decoded)))
    check(f"{name}: encoded CSV has header plus one route", len(rows) == 2)
    return dict(zip(rows[0], rows[1]))


print("== independent factory route decode ==")
std = route("P5-Unified04.ini")
uni = route("P5-Unified10.ini")
uni_all = route("P5-Unified.ini")
vforest = route("0P5-CAN(SECURITY)302.ini")
check("P5-Unified04 selects standard prepare/flash",
      (std["DLLFileNameForPrepareWrite"], std["DLLFileNameForFlashWrite"])
      == ("TCUWCanReproStdPrepareWriter.dll", "TCUWCanReproStdFlashWriter.dll"))
check("P5-Unified10 selects unified/per-area writers",
      (uni["DLLFileNameForPrepareWrite"], uni["DLLFileNameForFlashWrite"])
      == ("TCUWCanUnifiedPrepareWriter.dll", "TCUWCanUnifiedFlashWriterEachArea.dll"))
check("P5-Unified selects unified writer pair",
      (uni_all["DLLFileNameForPrepareWrite"], uni_all["DLLFileNameForFlashWrite"])
      == ("TCUWCanUnifiedPrepareWriter.dll", "TCUWCanUnifiedFlashWriter.dll"))
check("security VFOREST is a distinct factory route",
      (vforest["DLLFileNameForPrepareWrite"], vforest["DLLFileNameForFlashWrite"])
      == ("TCUWP5CanSecurityPowerTrainPrepareWriter.dll", "TCUWCanSecurityVFORESTFlashWriter.dll"))

print("\n== controller dynamic factory anchors ==")
oracle = "cfg_dataflow"
control = (CUW / "TCUWControlCommPhase.dll").read_bytes()
for value in (b"DLLFileNameForPrepareWrite", b"DLLFileNameForFlashWrite",
              b"StartPrepareWrite", b"StartFlashWrite"):
    check(f"controller contains {value.decode()}", value in control)
control_pe = pefile.PE(data=control)
imports = {(lib.dll.decode("latin1"), symbol.name.decode("latin1"))
           for lib in control_pe.DIRECTORY_ENTRY_IMPORT for symbol in lib.imports if symbol.name}
check("controller imports LoadLibraryA", ("KERNEL32.dll", "LoadLibraryA") in imports)
check("controller imports GetProcAddress", ("KERNEL32.dll", "GetProcAddress") in imports)

# Pin the exact controller references that connect INI field names to the two
# dynamic factory entry points.  RVAs below are operand or instruction starts
# in the pinned PE, not inferred strings found elsewhere in the image.
prepare_key_va = (0x10000000 + 0x116D8).to_bytes(4, "little")
flash_key_va = (0x10000000 + 0x116F8).to_bytes(4, "little")
for rva in (0x7178, 0x98D9):
    check(f"controller code references prepare-writer field at RVA {rva:#x}",
          control_pe.get_data(rva, 4) == prepare_key_va)
for rva in (0x8B28, 0x8DC4, 0xA361):
    check(f"controller code references flash-writer field at RVA {rva:#x}",
          control_pe.get_data(rva, 4) == flash_key_va)

load_library_iat = (0x100163F8).to_bytes(4, "little")
get_proc_iat = (0x1001643C).to_bytes(4, "little")
check("prepare factory calls LoadLibraryA through pinned IAT",
      control_pe.get_data(0x1C44, 6) == b"\xff\x15" + load_library_iat)
check("prepare factory pushes StartPrepareWrite and calls GetProcAddress",
      control_pe.get_data(0x1C76, 12)
      == b"\x68" + (0x10011F8C).to_bytes(4, "little") + b"\x50\xff\x15" + get_proc_iat)
check("flash factory calls LoadLibraryA through pinned IAT",
      control_pe.get_data(0x1DA4, 6) == b"\xff\x15" + load_library_iat)
check("flash factory pushes StartFlashWrite before GetProcAddress call",
      control_pe.get_data(0x1DDD, 8)
      == b"\x68" + (0x1001205C).to_bytes(4, "little") + b"\x50\xff\xd6")

print("\n== raw writer exports, imports, and command builders ==")
required_exports = {
    "TCUWCanReproStdPrepareWriter.dll": "StartPrepareWrite",
    "TCUWCanUnifiedPrepareWriter.dll": "StartPrepareWrite",
    "TCUWCanReproStdFlashWriter.dll": "StartFlashWrite",
    "TCUWCanUnifiedFlashWriter.dll": "StartFlashWrite",
    "TCUWCanUnifiedFlashWriterEachArea.dll": "StartFlashWrite",
    "TCUWCanSecurityVFORESTFlashWriter.dll": "StartFlashWrite",
    "TCUWP4CanVFORESTFlashWriter.dll": "StartFlashWrite",
    "TCUWP5CanSecurityPowerTrainPrepareWriter.dll": "StartPrepareWrite",
}
for dll, expected in required_exports.items():
    pe = pefile.PE(str(CUW / dll))
    names = {symbol.name.decode("latin1") for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols if symbol.name}
    check(f"{dll}: exports {expected}", expected in names)


def pe_body(name: str, rva: int, size: int) -> tuple[bytes, set[str]]:
    data = (CUW / name).read_bytes()
    pe = pefile.PE(data=data)
    offset = pe.get_offset_from_rva(rva)
    imported = {symbol.name.decode("latin1") for lib in pe.DIRECTORY_ENTRY_IMPORT
                for symbol in lib.imports if symbol.name}
    return data[offset:offset + size], imported


std_session, _ = pe_body("TCUWCanReproStdPrepareWriter.dll", 0x1400, 265)
std_sa, std_prep_imports = pe_body("TCUWCanReproStdPrepareWriter.dll", 0x1510, 721)
uni_sa, uni_prep_imports = pe_body("TCUWCanUnifiedPrepareWriter.dll", 0x1530, 741)
uni_pre, uni_flash_imports = pe_body("TCUWCanUnifiedFlashWriter.dll", 0x10F0, 816)
std_rd, _ = pe_body("TCUWCanReproStdFlashWriter.dll", 0x15F0, 624)
std_td, _ = pe_body("TCUWCanReproStdFlashWriter.dll", 0x1870, 308)
std_te, _ = pe_body("TCUWCanReproStdFlashWriter.dll", 0x19B0, 224)
std_reset, _ = pe_body("TCUWCanReproStdFlashWriter.dll", 0x1A90, 239)

def imm_store(body: bytes, value: int) -> bool:
    return re.search(rb"\xc6\x84.[\s\S]{4}" + bytes([value]), body) is not None

check("standard prepare constructs SID 10 and response 50", imm_store(std_session, 0x10) and imm_store(std_session, 0x50))
check("standard prepare constructs SID 27 and response 67", imm_store(std_sa, 0x27) and imm_store(std_sa, 0x67))
check("standard prepare imports service-auth key and CalcSeedKey",
      any("GetServiceAuthKey@CalibrationFile" in name for name in std_prep_imports)
      and any("CalcSeedKey@CUnifiedUtils" in name for name in std_prep_imports))
check("unified prepare additionally imports ECU auth key",
      any("GetECUAuthKey@CalibrationFile" in name for name in uni_prep_imports)
      and imm_store(uni_sa, 0x27) and imm_store(uni_sa, 0x67))
check("unified predownload constructs 2E 0203/0201/0202 in order",
      uni_pre.find(bytes.fromhex("c68435dcefffff2e"))
      < uni_pre.find(bytes.fromhex("c68435dcefffff2e"), 200)
      < uni_pre.find(bytes.fromhex("c68435dcefffff2e"), 450))
check("unified predownload imports offset, seed-key, and nonce getters",
      all(any(token in name for name in uni_flash_imports)
          for token in ("GetOffsetAddress@CalibrationFile", "GetSeedKey@CalibrationFile", "GetNonce@CalibrationFile")))
check("standard RequestDownload constructs 34 and positive 74", imm_store(std_rd, 0x34) and imm_store(std_rd, 0x74))
check("standard RequestDownload caps max block at 0x0FFF", bytes.fromhex("81faff0f0000") in std_rd and bytes.fromhex("baff0f0000") in std_rd)
check("standard TransferData constructs 36/76", imm_store(std_td, 0x36) and imm_store(std_td, 0x76))
check("standard TransferExit constructs 37/77", imm_store(std_te, 0x37) and imm_store(std_te, 0x77))
check("standard reset constructs 11 01 / 51 01", imm_store(std_reset, 0x11) and imm_store(std_reset, 0x51))

print("\n== calibration target-integrity metadata parser ==")
# Cuw.exe contains a separate calibration-container parser for per-target
# integrity metadata.  Keep this distinct from the portal RKS "Signature": the
# static parser proves only that calibration target records carry these fields.
cuw_data = (CUW / "Cuw.exe").read_bytes()
cuw_pe = pefile.PE(data=cuw_data)
cuw_base = cuw_pe.OPTIONAL_HEADER.ImageBase
parent_va, parent_size = 0x0040B63C, 3045
helper_va, helper_size = 0x0040C224, 838
parent = cuw_pe.get_data(parent_va - cuw_base, parent_size)
helper = cuw_pe.get_data(helper_va - cuw_base, helper_size)
check("calibration logical-block parser body identity",
      hashlib.sha256(parent).hexdigest()
      == "ce3e4d43fa5539105c776684bb73b24fc9516a94768b99d044d960d8b520807d")
check("per-target integrity parser body identity",
      hashlib.sha256(helper).hexdigest()
      == "62cf1764aaa6f06169e7b0b4953cf24593490b7337d6a8a63854b190779dec8d")
target_fields = [
    ("StartAddress", 0x005D0C25),
    ("Length", 0x005D0C33),
    ("CRC", 0x005D0C3B),
    ("CMAC", 0x005D0C40),
    ("DigitalSignature", 0x005D0C46),
]
field_ref_offsets = []
for field, va in target_fields:
    encoded = struct.pack("<I", va)
    offset = helper.find(encoded)
    check(f"per-target parser references {field}",
          field.encode() + b"\x00" in cuw_data and offset >= 0,
          detail=f"helper+{offset:#x}" if offset >= 0 else "missing")
    field_ref_offsets.append(offset)
check("per-target parser visits integrity fields in declared order",
      field_ref_offsets == sorted(field_ref_offsets) and all(offset >= 0 for offset in field_ref_offsets),
      detail=", ".join(hex(offset) for offset in field_ref_offsets))
# The parent invokes the same helper once for each target-family record:
# ReproData, EraseAndReproRoutine, DeltaReproData,
# DeltaEraseAndReproRoutine, CompressionReproData, and
# CompressionEraseAndReproRoutine.
helper_calls = []
for offset in range(len(parent) - 4):
    if parent[offset] != 0xE8:
        continue
    rel = struct.unpack_from("<i", parent, offset + 1)[0]
    call_va = parent_va + offset
    if call_va + 5 + rel == helper_va:
        helper_calls.append(call_va)
check("logical-block parser invokes per-target parser six times",
      helper_calls == [0x0040BFEA, 0x0040C03E, 0x0040C092,
                       0x0040C0E6, 0x0040C13A, 0x0040C18E],
      detail=", ".join(hex(value) for value in helper_calls))
for prefix in (b"ReproData", b"EraseAndReproRoutine", b"DeltaReproData",
               b"DeltaEraseAndReproRoutine", b"CompressionReproData",
               b"CompressionEraseAndReproRoutine"):
    check(f"logical-block parser family present: {prefix.decode()}", prefix in cuw_data)

print("\n== inventory identity and live regeneration ==")
oracle = "identity_hash"
inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
check("inventory covers all 201 encoded INIs and 196 factory rows",
      inventory["route_stats"] == {"encoded_ini_files_decoded": 201, "factory_rows": 196})
check("inventory records zero local calibration payloads",
      inventory["blockers"]["matching_payloads_found"] == []
      and inventory["blockers"]["matching_calibration_payload_required"] is True)
unified_rd = next(x for x in inventory["commands"]
                  if x["route"] == "unified-flash" and x["method"] == "request_download")
check("inventory Unified RequestDownload uses corrected field order",
      unified_rd["request"]
      == "34 || dataFormatIdentifier || 46 || addressSpaceByte || (offset[5]+areaAddress) || areaLength")
for artifact in inventory["artifacts"]:
    data = (ROOT / artifact["path"]).read_bytes()
    check(f"{Path(artifact['path']).name}: artifact identity", hashlib.sha256(data).hexdigest() == artifact["sha256"])
    pe = pefile.PE(data=data)
    for method in artifact["methods"]:
        offset = pe.get_offset_from_rva(method["rva"])
        body = data[offset:offset + method["size"]]
        check(f"{Path(artifact['path']).name}:{method['name']}: body identity",
              hashlib.sha256(body).hexdigest() == method["identity_sha256"])

oracle = "raw_bytes"
firmware = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
services = {struct.unpack_from("<BBHI", firmware, 0x8E54 + index * 8)[0]
            for index in range(20)}
check("Sienna bootloader implements every direct standard-UDS writer SID",
      {0x10, 0x11, 0x27, 0x28, 0x2E, 0x31, 0x34, 0x36, 0x37} <= services)
boot_dids = [struct.unpack_from("<IHHBBBB", firmware, 0x8F14 + index * 12)[2] for index in range(4)]
check("Sienna bootloader DID table contains unified 0201/0202/0203 names",
      boot_dids == [0xF181, 0x0201, 0x0202, 0x0203])

with tempfile.TemporaryDirectory() as tmp:
    oracle = "generated_self_check"
    regenerated = Path(tmp) / "inventory.json"
    result = subprocess.run([
        sys.executable, str(REPO / "tools/techstream/generate_cuw_writer_inventory.py"),
        "--root", str(ROOT), "--output", str(regenerated),
    ], check=False)
    check("generator exits successfully", result.returncode == 0)
    check("live regeneration is byte-identical", regenerated.read_bytes() == INVENTORY.read_bytes())

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
